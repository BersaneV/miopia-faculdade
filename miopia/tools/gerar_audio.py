"""
gerar_audio.py — cria todos os sons do Miopia em assets/sons/.

    python tools/gerar_audio.py

Nada aqui vem da internet: tudo é sintetizado com numpy (onda quadrada,
triangular e ruído filtrado). Por isso o áudio é do grupo — os créditos
no README dizem "autoral, gerado por este script".

Se quiser trocar a trilha, mexa nas listas de padrões no fim do arquivo.
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_kit import (  # noqa: E402  (import depois do sys.path)
    NOTAS,
    SR,
    envelope,
    normalizar,
    onda,
    salvar_wav,
    silencio,
)

DESTINO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "sons")

# 22050 Hz mono: metade do tamanho, e para chiptune não se perde nada audível.
TAXA_SAIDA = 22050


# ---------------------------------------------------------------------- #
# Utilidades de composição
# ---------------------------------------------------------------------- #
SEMITONS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
            "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10,
            "Bb": 10, "B": 11}


def frequencia(nome: str) -> float:
    """Converte 'A3', 'C#5'... em Hz (A4 = 440). Cobre todas as oitavas."""
    if nome in NOTAS:
        return NOTAS[nome]
    oitava = int(nome[-1])
    base = nome[:-1]
    semitons = SEMITONS[base] + (oitava - 4) * 12 - 9
    return 440.0 * 2 ** (semitons / 12)


def nota(nome: str, dur: float, tipo: str = "triangle", vol: float = 0.3,
         adsr=(0.004, 0.09, 0.62, 0.06), desafinar: float = 0.0) -> np.ndarray:
    f = frequencia(nome) * (1 + desafinar)
    sinal = onda(f, dur, tipo)
    sinal = sinal * envelope(len(sinal), *adsr) * vol
    return np.convolve(sinal, np.ones(4) / 4, mode="same")


def ruido_filtrado(dur: float, vol: float = 0.2, corte: float = 0.5) -> np.ndarray:
    n = int(SR * dur)
    bruto = np.random.uniform(-1, 1, n)
    # média móvel = passa-baixa simples; 'corte' controla o brilho
    janela = max(2, int(SR * 0.0008 * (1 / max(0.02, corte))))
    kernel = np.ones(janela) / janela
    return np.convolve(bruto, kernel, mode="same") * vol


def mixar(*camadas) -> np.ndarray:
    """Soma arrays de tamanhos diferentes (alinha pelo início)."""
    total = max(len(c) for c in camadas)
    saida = np.zeros(total)
    for camada in camadas:
        saida[: len(camada)] += camada
    return saida


def juntar(*partes) -> np.ndarray:
    """Concatena arrays em sequência (um som depois do outro)."""
    return np.concatenate([np.asarray(p, dtype=float) for p in partes])


def eco(sinal: np.ndarray, atraso: float, repeticoes: int = 2,
        decaimento: float = 0.4) -> np.ndarray:
    atraso_n = int(SR * atraso)
    total = len(sinal) + atraso_n * repeticoes
    saida = np.zeros(total)
    saida[: len(sinal)] += sinal
    for i in range(1, repeticoes + 1):
        inicio = atraso_n * i
        saida[inicio: inicio + len(sinal)] += sinal * (decaimento ** i)
    return saida


# ---------------------------------------------------------------------- #
# Efeitos
# ---------------------------------------------------------------------- #
def sfx_clique() -> np.ndarray:
    return mixar(
        nota("C6", 0.05, "square", 0.20, (0.001, 0.02, 0.2, 0.02)),
        ruido_filtrado(0.03, 0.05, 0.8),
    )


def sfx_navegar() -> np.ndarray:
    return nota("A5", 0.055, "square", 0.16, (0.001, 0.03, 0.3, 0.03))


def sfx_pagina() -> np.ndarray:
    """Papel virando: ruído curto com envelope rápido e um 'toc' de madeira."""
    papel = ruido_filtrado(0.16, 0.16, 0.75) * envelope(int(SR * 0.16), 0.002, 0.03, 0.2, 0.09)
    toc = nota("D5", 0.05, "triangle", 0.10, (0.001, 0.02, 0.2, 0.02))
    return mixar(papel, juntar(silencio(0.02), toc))


def sfx_coleta() -> np.ndarray:
    a = nota("E5", 0.055, "triangle", 0.30)
    b = nota("B5", 0.11, "triangle", 0.28)
    return eco(juntar(a, silencio(0.035), b), 0.02, 1, 0.25)


def sfx_raro() -> np.ndarray:
    melodia = [("C5", 0.06), ("E5", 0.06), ("G5", 0.06), ("C6", 0.22)]
    partes = [nota(n, d, "triangle", 0.30) for n, d in melodia]
    brilho = juntar(*partes)
    return eco(brilho, 0.05, 2, 0.3)


def sfx_pulso() -> np.ndarray:
    # varredura ascendente + acorde aberto = "clarão"
    n = int(SR * 0.55)
    freq = np.linspace(420, 1500, n)
    fase = np.cumsum(2 * math.pi * freq / SR)
    varredura = np.sin(fase) * np.exp(-np.linspace(0, 3.2, n)) * 0.28
    acorde = mixar(
        nota("C5", 0.5, "triangle", 0.16, (0.01, 0.2, 0.4, 0.2)),
        nota("G5", 0.5, "triangle", 0.13, (0.01, 0.2, 0.4, 0.2)),
        nota("E6", 0.5, "triangle", 0.10, (0.01, 0.2, 0.4, 0.2)),
    )
    return mixar(varredura, acorde)


def sfx_dano() -> np.ndarray:
    tom = nota("E4", 0.10, "saw", 0.22) 
    queda = np.concatenate([nota("E4", 0.10, "saw", 0.26), nota("C4", 0.12, "saw", 0.24),
                            nota("A3", 0.20, "square", 0.20)])
    batida = ruido_filtrado(0.16, 0.30, 0.35)
    return mixar(queda, batida, tom * 0.3)


def sfx_abertura() -> np.ndarray:
    acorde = mixar(
        nota("C4", 1.0, "triangle", 0.18, (0.05, 0.3, 0.5, 0.4)),
        nota("E4", 1.0, "triangle", 0.15, (0.05, 0.3, 0.5, 0.4)),
        nota("G4", 1.0, "triangle", 0.14, (0.05, 0.3, 0.5, 0.4)),
        nota("C5", 1.0, "triangle", 0.12, (0.05, 0.3, 0.5, 0.4)),
    )
    sino = eco(nota("G5", 0.35, "triangle", 0.16), 0.12, 3, 0.35)
    return mixar(acorde, sino)


def sfx_vitoria() -> np.ndarray:
    melodia = [("C5", 0.10), ("E5", 0.10), ("G5", 0.10), ("C6", 0.30)]
    return eco(juntar(*[nota(n, d, "triangle", 0.26) for n, d in melodia]), 0.04, 2, 0.28)


def sfx_vitoria_final() -> np.ndarray:
    parte1 = juntar(*[nota(n, d, "triangle", 0.24) for n, d in
                     [("C5", 0.16), ("E5", 0.16), ("G5", 0.16), ("C6", 0.30)]])
    acorde = mixar(
        nota("C4", 1.6, "triangle", 0.14, (0.02, 0.4, 0.4, 0.6)),
        nota("E4", 1.6, "triangle", 0.12, (0.02, 0.4, 0.4, 0.6)),
        nota("G4", 1.6, "triangle", 0.12, (0.02, 0.4, 0.4, 0.6)),
        nota("C5", 1.6, "triangle", 0.10, (0.02, 0.4, 0.4, 0.6)),
    )
    sino = eco(nota("C6", 0.4, "triangle", 0.12), 0.15, 3, 0.3)
    return mixar(parte1, juntar(silencio(0.66), acorde), juntar(silencio(0.66), sino))


def sfx_derrota() -> np.ndarray:
    melodia = [("G4", 0.24), ("E4", 0.24), ("C4", 0.30), ("A3", 0.7)]
    return eco(juntar(*[nota(n, d, "saw", 0.16) for n, d in melodia]), 0.08, 2, 0.3)


# ---------------------------------------------------------------------- #
# Trilhas (loop)
# ---------------------------------------------------------------------- #
def compor(
    bpm: int,
    escala: list[str],
    acordes: list[list[int]],
    arpejo: list[int],
    baixo: list[int],
    compassos: int,
    *,
    bateria: bool = True,
    pad: bool = True,
    brilho: float = 1.0,
    instrumento: str = "square",
) -> np.ndarray:
    """
    Compositor simples de 4/4:
      - arpejo em colcheias (uma nota por metade de tempo);
      - baixo em mínimas;
      - pad (acorde sustentado) por compasso;
      - bumbo/caixa/hats opcionais.
    `escala` é uma lista de nomes de nota; os índices em `acordes`,
    `arpejo` e `baixo` apontam para ela.
    """
    base = 60.0 / bpm
    colcheia = base / 2
    passos_por_compasso = 8
    total = int(SR * base * 4 * compassos)
    mix = np.zeros(total + SR)

    def idx(i: int) -> str:
        return escala[i % len(escala)]

    # ---- pad + arpejo + baixo ----
    for compasso in range(compassos):
        inicio = int(SR * base * 4 * compasso)
        acorde = acordes[compasso % len(acordes)]

        if pad:
            vozes = [nota(escala[(acorde[0] + 12) % len(escala)], base * 4,
                          "triangle", 0.075, (0.35, 0.4, 0.75, 0.5), 0.001 * i)
                     for i in range(3)]
            pad_comp = mixar(*vozes)
            fim = min(len(mix), inicio + len(pad_comp))
            mix[inicio:fim] += pad_comp[: fim - inicio]

        for passo in range(passos_por_compasso):
            pos = int(SR * colcheia * (compasso * passos_por_compasso + passo))
            grau = acorde[passo % len(acorde)] if passo % 2 == 0 else acorde[0]
            f = nota(idx(grau + arpejo[passo % len(arpejo)]), colcheia * 0.95,
                     instrumento, 0.085 * brilho, (0.002, 0.05, 0.35, 0.04))
            fim = min(len(mix), pos + len(f))
            mix[pos:fim] += f[: fim - pos]

        pos_baixo = int(SR * base * 4 * compasso)
        f_baixo = nota(escala[baixo[compasso % len(baixo)] % len(escala)],
                       base * 1.9, "triangle", 0.20, (0.01, 0.15, 0.6, 0.15))
        fim = min(len(mix), pos_baixo + len(f_baixo))
        mix[pos_baixo:fim] += f_baixo[: fim - pos_baixo]

        if bateria:
            for tempo in range(4):
                p = int(SR * base * (compasso * 4 + tempo))
                if tempo in (0, 2):
                    bumbo = onda(58, 0.12, "sine") * envelope(int(SR * 0.12), 0.001, 0.03, 0.2, 0.07)
                    fim = min(len(mix), p + len(bumbo))
                    mix[p:fim] += bumbo[: fim - p] * 0.55
                if tempo in (1, 3):
                    caixa = ruido_filtrado(0.09, 0.16, 0.6) * envelope(int(SR * 0.09), 0.001, 0.02, 0.1, 0.05)
                    fim = min(len(mix), p + len(caixa))
                    mix[p:fim] += caixa[: fim - p]
                hat = ruido_filtrado(0.04, 0.05, 0.9) * envelope(int(SR * 0.04), 0.001, 0.01, 0.05, 0.02)
                fim = min(len(mix), p + int(SR * base / 2) + len(hat))
                mix[p + int(SR * base / 2):fim] += hat[: max(0, fim - (p + int(SR * base / 2)))]

    return normalizar(mix[:total], pico=0.82)


def trilha_menu() -> np.ndarray:
    escala = ["A3", "C4", "D4", "E4", "G4", "A4", "C5", "E5", "G5", "A5"]
    return compor(
        bpm=84, escala=escala,
        acordes=[[0, 2, 4], [3, 5, 7], [5, 7, 9], [1, 3, 5]],
        arpejo=[0, 2, 4, 2], baixo=[0, 3, 5, 1], compassos=4,
        bateria=False, pad=True, brilho=0.8,
    )


def trilha_jogo() -> np.ndarray:
    escala = ["D3", "F3", "G3", "A3", "C4", "D4", "F4", "G4", "A4", "C5"]
    return compor(
        bpm=126, escala=escala,
        acordes=[[0, 2, 4], [4, 6, 8], [2, 4, 6], [3, 5, 7]],
        arpejo=[0, 3, 5, 7, 4, 2, 6, 4], baixo=[0, 4, 2, 3], compassos=8,
        bateria=True, pad=True, brilho=1.0,
    )


# ---------------------------------------------------------------------- #
# Uma trilha por bioma (o modo infinito também usa estas)
# ---------------------------------------------------------------------- #
def trilha_bosque() -> np.ndarray:
    """Bosque: o berçário. Doce, curioso, flauta de bambu (triângulo)."""
    escala = ["G3", "A3", "B3", "D4", "E4", "G4", "A4", "B4", "D5"]
    return compor(
        bpm=112, escala=escala,
        acordes=[[0, 2, 4], [5, 7, 8], [3, 5, 7], [4, 6, 8]],
        arpejo=[0, 2, 4, 6, 5, 3, 1, 3], baixo=[0, 5, 3, 4], compassos=8,
        bateria=True, pad=True, brilho=0.95, instrumento="triangle",
    )


def trilha_corrego() -> np.ndarray:
    """Córrego: água corrente. Sinos e arpejo rápido, quase sem batida."""
    escala = ["D3", "E3", "F3", "A3", "B3", "D4", "E4", "F4", "A4", "B4"]
    return compor(
        bpm=104, escala=escala,
        acordes=[[2, 4, 6], [4, 6, 8], [0, 2, 4], [3, 5, 7]],
        arpejo=[0, 3, 5, 7, 9, 7, 5, 3], baixo=[2, 4, 0, 3], compassos=8,
        bateria=False, pad=True, brilho=0.85, instrumento="sine",
    )


def trilha_taquaral() -> np.ndarray:
    """Taquaral: bambus no vento. Madeira (square), batida seca e tensa."""
    escala = ["E3", "F3", "G3", "A3", "B3", "C4", "E4", "F4", "G4"]
    return compor(
        bpm=132, escala=escala,
        acordes=[[0, 2, 4], [1, 3, 5], [0, 2, 4], [4, 6, 8]],
        arpejo=[0, 2, 3, 2, 5, 3, 2, 1], baixo=[0, 1, 0, 4], compassos=8,
        bateria=True, pad=True, brilho=1.0, instrumento="square",
    )


def trilha_gruta() -> np.ndarray:
    """Gruta: o Breu e a Coruja. Grave, lenta, com eco de pedra."""
    escala = ["C3", "D3", "Eb3", "G3", "Ab3", "C4", "D4", "Eb4", "G4"]
    return compor(
        bpm=78, escala=escala,
        acordes=[[0, 2, 4], [2, 4, 6], [0, 2, 4], [3, 5, 7]],
        arpejo=[0, 4, 2, 6, 4, 2, 3, 5], baixo=[0, 2, 0, 3], compassos=8,
        bateria=True, pad=True, brilho=0.7, instrumento="triangle",
    )


def trilha_historia() -> np.ndarray:
    escala = ["F3", "G3", "A3", "C4", "D4", "F4", "G4", "A4", "C5"]
    return compor(
        bpm=70, escala=escala,
        acordes=[[0, 2, 4], [3, 5, 7], [1, 3, 5], [4, 6, 8]],
        arpejo=[0, 4, 2, 6], baixo=[0, 3, 1, 4], compassos=4,
        bateria=False, pad=True, brilho=0.65,
    )


def trilha_vitoria() -> np.ndarray:
    escala = ["C4", "D4", "E4", "G4", "A4", "C5", "E5", "G5", "C6"]
    return compor(
        bpm=120, escala=escala,
        acordes=[[0, 2, 4], [3, 5, 7], [5, 7, 8], [0, 2, 4]],
        arpejo=[0, 2, 4, 6], baixo=[0, 3, 5, 0], compassos=3,
        bateria=True, pad=True, brilho=1.05,
    )


def trilha_derrota() -> np.ndarray:
    escala = ["A3", "B3", "C4", "E4", "F4", "A4", "C5", "E5"]
    return compor(
        bpm=62, escala=escala,
        acordes=[[0, 2, 4], [3, 5, 7], [1, 3, 5], [0, 2, 4]],
        arpejo=[0, 2, 4, 1], baixo=[0, 3, 1, 0], compassos=3,
        bateria=False, pad=True, brilho=0.6,
    )


EFEITOS = {
    "clique": sfx_clique,
    "navegar": sfx_navegar,
    "pagina": sfx_pagina,
    "coleta": sfx_coleta,
    "raro": sfx_raro,
    "pulso": sfx_pulso,
    "dano": sfx_dano,
    "abertura": sfx_abertura,
    "vitoria": sfx_vitoria,
    "vitoria_final": sfx_vitoria_final,
    "derrota": sfx_derrota,
}

TRILHAS = {
    "trilha_menu": trilha_menu,
    "trilha_jogo": trilha_jogo,
    "trilha_bosque": trilha_bosque,
    "trilha_corrego": trilha_corrego,
    "trilha_taquaral": trilha_taquaral,
    "trilha_gruta": trilha_gruta,
    "trilha_historia": trilha_historia,
    "trilha_vitoria": trilha_vitoria,
    "trilha_derrota": trilha_derrota,
}


def main() -> None:
    os.makedirs(DESTINO, exist_ok=True)
    print(f"Gerando áudio em {DESTINO}")
    for nome, funcao in EFEITOS.items():
        salvar_wav(os.path.join(DESTINO, f"{nome}.wav"), funcao())
    for nome, funcao in TRILHAS.items():
        salvar_wav(os.path.join(DESTINO, f"{nome}.wav"), funcao(), taxa=TAXA_SAIDA)
    print("Pronto.")


if __name__ == "__main__":
    main()
