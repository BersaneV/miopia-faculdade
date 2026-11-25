"""
audio_kit.py — efeitos e trilha ORIGINAIS, sintetizados em Python.

Motivo: o critério de Som da A3 pede fonte e licença de cada áudio de
terceiros. Sintetizando aqui, o áudio é do grupo (CC0 / autoral) e não
tem risco de crédito faltando.

Gera WAV 16 bits, mono, 44.1 kHz — formato que pygame.mixer.Sound e
pygame.mixer.music carregam sem dependência extra (sem ffmpeg, sem ogg).

Demonstração (cria a pasta de sons com efeitos e uma trilha de 8 s):

    python tools/audio_kit.py --demo

Uso no jogo:

    som_moeda = pygame.mixer.Sound("assets/sons/moeda.wav")
"""

from __future__ import annotations

import argparse
import math
import os
import wave

import numpy as np

SR = 44100
NOTAS = {
    "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
    "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
    "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
    "C5": 523.25, "C#5": 554.37, "D5": 587.33, "D#5": 622.25,
    "E5": 659.25, "F5": 698.46, "F#5": 739.99, "G5": 783.99,
    "G#5": 830.61, "A5": 880.00, "A#5": 932.33, "B5": 987.77,
    "C6": 1046.50, "E6": 1318.51, "G6": 1567.98,
}


# --------------------------------------------------------------------- #
# Blocos de síntese
# --------------------------------------------------------------------- #
def tempo(segundos: float) -> np.ndarray:
    return np.arange(int(SR * segundos)) / SR


def onda(freq: float, segundos: float, tipo: str = "square", fase: float = 0.0) -> np.ndarray:
    """Onda simples: square, triangle, saw ou sine."""
    t = tempo(segundos)
    x = 2 * math.pi * freq * t + fase
    if tipo == "square":
        return np.sign(np.sin(x))
    if tipo == "triangle":
        return 2 / math.pi * np.arcsin(np.sin(x))
    if tipo == "saw":
        return 2 * ((freq * t + fase / (2 * math.pi)) % 1.0) - 1
    return np.sin(x)


def envelope(n: int, ataque: float = 0.005, decaimento: float = 0.15,
             sustain: float = 0.6, liberacao: float = 0.1) -> np.ndarray:
    """Envelope ADSR simples por amostra."""
    a = max(1, int(ataque * SR))
    d = max(1, int(decaimento * SR))
    r = max(1, int(liberacao * SR))
    s = max(0, n - a - d - r)
    env = np.concatenate([
        np.linspace(0, 1, a),
        np.linspace(1, sustain, d),
        np.full(s, sustain),
        np.linspace(sustain, 0, r),
    ])
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def nota(nome: str, segundos: float, tipo: str = "square", vol: float = 0.3,
         adsr: tuple[float, float, float, float] = (0.005, 0.12, 0.7, 0.08)) -> np.ndarray:
    """Uma nota musical com envelope."""
    sinal = onda(NOTAS[nome] if isinstance(nome, str) else nome, segundos, tipo)
    sinal = sinal * envelope(len(sinal), *adsr) * vol
    # pequena suavização para tirar o "click" do square
    return np.convolve(sinal, np.ones(5) / 5, mode="same")


def ruido(segundos: float, vol: float = 0.3) -> np.ndarray:
    n = int(SR * segundos)
    return np.random.uniform(-1, 1, n) * vol


def glissando(f0: float, f1: float, segundos: float, tipo: str = "square", vol: float = 0.3) -> np.ndarray:
    """Sweep de frequência — bom para pulo, dano, coleta."""
    n = int(SR * segundos)
    freq = np.linspace(f0, f1, n)
    fase = np.cumsum(2 * math.pi * freq / SR)
    x = np.sin(fase)
    if tipo == "square":
        x = np.sign(x)
    return x * envelope(n, 0.003, 0.1, 0.5, 0.08) * vol


def silencio(segundos: float) -> np.ndarray:
    return np.zeros(int(SR * segundos))


# --------------------------------------------------------------------- #
# Efeitos prontos (mude à vontade — são só pontos de partida)
# --------------------------------------------------------------------- #
def sfx_pulo(vol: float = 0.35) -> np.ndarray:
    return glissando(320, 720, 0.16, "square", vol)


def sfx_moeda(vol: float = 0.32) -> np.ndarray:
    return np.concatenate([nota("E5", 0.06, "square", vol), nota("B5", 0.12, "square", vol)])


def sfx_coleta(vol: float = 0.32) -> np.ndarray:
    return np.concatenate([nota("C5", 0.05, "triangle", vol), nota("G5", 0.09, "triangle", vol)])


def sfx_dano(vol: float = 0.4) -> np.ndarray:
    tom = glissando(300, 90, 0.28, "saw", vol)
    batida = ruido(0.28, vol * 0.5) * np.exp(-np.linspace(0, 8, len(tom)))
    return tom + batida


def sfx_erro(vol: float = 0.35) -> np.ndarray:
    return np.concatenate([nota("A#4", 0.12, "square", vol), nota("E4", 0.18, "square", vol)])


def sfx_explosao(vol: float = 0.45, segundos: float = 0.5) -> np.ndarray:
    n = int(SR * segundos)
    return ruido(segundos, vol) * np.exp(-np.linspace(0, 6, n))


def sfx_vitoria(vol: float = 0.35) -> np.ndarray:
    melodia = [("C5", 0.12), ("E5", 0.12), ("G5", 0.12), ("C6", 0.32)]
    return np.concatenate([nota(n_, d, "square", vol) for n_, d in melodia])


def sfx_derrota(vol: float = 0.35) -> np.ndarray:
    melodia = [("G4", 0.18), ("E4", 0.18), ("C4", 0.4)]
    return np.concatenate([nota(n_, d, "triangle", vol) for n_, d in melodia])


SFX = {
    "pulo": sfx_pulo,
    "moeda": sfx_moeda,
    "coleta": sfx_coleta,
    "dano": sfx_dano,
    "erro": sfx_erro,
    "explosao": sfx_explosao,
    "vitoria": sfx_vitoria,
    "derrota": sfx_derrota,
}


# --------------------------------------------------------------------- #
# Trilha em loop
# --------------------------------------------------------------------- #
def trilha(bpm: int = 116, compassos: int = 4, escala_raiz: str = "C4",
           menor: bool = False, vol: float = 0.22) -> np.ndarray:
    """
    Loop de chiptune: baixo + arpejo + bumbo/caixa de ruído.
    Retorna um array que pode ser salvo como WAV e tocado em loop.
    """
    intervalo = {
        False: [0, 2, 4, 5, 7, 9, 11, 12],   # maior
        True:  [0, 2, 3, 5, 7, 8, 10, 12],   # menor
    }[menor]
    raiz = NOTAS[escala_raiz] if isinstance(escala_raiz, str) else escala_raiz
    frequencias = [raiz * 2 ** (s / 12) for s in intervalo]

    base = 60 / bpm
    colcheia = base / 2
    total = int(SR * colcheia * 4 * compassos)
    mix = np.zeros(total)

    padrao_arpejo = [0, 2, 4, 2, 1, 3, 5, 3]
    padrao_baixo = [0, 0, 3, 4]

    step = int(SR * colcheia)
    for i in range(compassos * 4):
        pos = i * step
        if pos + step > total:
            break
        idx = padrao_arpejo[i % len(padrao_arpejo)]
        arp = onda(frequencias[idx] * 2, colcheia, "square")
        arp *= envelope(len(arp), 0.002, 0.04, 0.35, 0.03) * vol
        mix[pos:pos + len(arp)] += arp

        if i % 2 == 0:
            f_baixo = frequencias[padrao_baixo[(i // 2) % 4]] / 2
            baixo = onda(f_baixo, base, "triangle")
            baixo *= envelope(len(baixo), 0.005, 0.08, 0.5, 0.05) * vol * 1.1
            fim = min(total, pos + len(baixo))
            mix[pos:fim] += baixo[:fim - pos]

        # bateria: bumbo no 1 e 3, caixa no 2 e 4
        if i % 4 in (0, 2):
            bumbo = onda(70, 0.09, "sine") * envelope(int(SR * 0.09), 0.001, 0.02, 0.2, 0.05)
            fim = min(total, pos + len(bumbo))
            mix[pos:fim] += bumbo[:fim - pos] * 0.9
        if i % 4 in (1, 3):
            caixa = ruido(0.07, vol * 0.8) * envelope(int(SR * 0.07), 0.001, 0.01, 0.1, 0.04)
            fim = min(total, pos + len(caixa))
            mix[pos:fim] += caixa[:fim - pos]

    return normalizar(mix, pico=0.85)


def normalizar(sinal: np.ndarray, pico: float = 0.9) -> np.ndarray:
    maior = float(np.max(np.abs(sinal))) or 1.0
    return sinal / maior * pico


def salvar_wav(caminho: str, sinal: np.ndarray, taxa: int = SR) -> None:
    """
    Grava WAV mono 16 bits.

    `taxa` permite reduzir a amostragem (ex.: 22050 Hz) para o repositório
    não ficar gigante. Antes de reduzir, aplica um passa-baixa curto para
    evitar aliasing.
    """
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)

    if taxa < SR:
        fator = int(round(SR / taxa))
        kernel = np.ones(fator) / fator
        sinal = np.convolve(sinal, kernel, mode="same")[::fator]
        taxa = SR // fator

    dados = (np.clip(sinal, -1, 1) * 32767).astype("<i2")
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(dados.tobytes())
    print(f"[audio] {os.path.basename(caminho):22s} {len(dados) / taxa:5.2f}s  "
          f"{os.path.getsize(caminho) // 1024:5d} KB")


# --------------------------------------------------------------------- #
def demo(pasta: str = "assets/sons") -> None:
    for nome, funcao in SFX.items():
        salvar_wav(os.path.join(pasta, f"{nome}.wav"), funcao())
    salvar_wav(os.path.join(pasta, "trilha_menu.wav"),
               trilha(bpm=100, compassos=4, escala_raiz="C4", menor=False))
    salvar_wav(os.path.join(pasta, "trilha_jogo.wav"),
               trilha(bpm=128, compassos=4, escala_raiz="A4", menor=True))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Síntese de efeitos e trilha (CC0, autoral).")
    ap.add_argument("--demo", action="store_true", help="gera a pasta de sons de exemplo")
    ap.add_argument("--pasta", default="assets/sons")
    args = ap.parse_args()
    if args.demo:
        demo(args.pasta)
    else:
        ap.print_help()
