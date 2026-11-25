"""
persistencia.py — recorde e preferências em arquivo (JSON).

O enunciado conta a favor "recorde salvo em arquivo". Aqui gravamos:
  - maior pontuação e melhor tempo;
  - último bioma alcançado e quantas partidas já foram jogadas;
  - volume, mudo e dificuldade escolhidos no menu.

Se o arquivo não existir, estiver corrompido ou a pasta não puder ser
criada, o jogo usa valores padrão e continua rodando.
"""

from __future__ import annotations

import json
import os

from . import config

PADRAO = {
    "recorde": 0,
    "melhor_tempo": 0.0,      # segundos restantes no melhor final
    "bioma_max": 1,           # 1 a 4
    "partidas": 0,
    "vitorias": 0,
    "volume": 0.8,
    "mudo": False,
    "dificuldade": 1,         # 0 fácil · 1 normal · 2 difícil
    "historias": 0,           # vezes que o modo História foi concluído
    "melhor_infinito": 0,     # maior número de biomas no modo infinito
    "pontos_infinito": 0,     # melhor pontuação no modo infinito
}


def carregar() -> dict:
    dados = dict(PADRAO)
    try:
        with open(config.RECORDE, "r", encoding="utf-8") as arquivo:
            salvos = json.load(arquivo)
        if isinstance(salvos, dict):
            for chave, valor in salvos.items():
                if chave in dados:
                    dados[chave] = valor
    except (OSError, ValueError):
        pass
    return dados


def salvar(dados: dict) -> None:
    try:
        os.makedirs(config.DADOS, exist_ok=True)
        temporario = config.RECORDE + ".tmp"
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=2, ensure_ascii=False)
        os.replace(temporario, config.RECORDE)
    except OSError:
        pass


def registrar_partida(dados: dict, pontos: int, tempo_restante: float,
                      bioma: int, vitoria: bool, infinito: bool = False) -> bool:
    """
    Atualiza os recordes. Retorna True se a pontuação virou novo recorde.

    No modo infinito, 'bioma' é a contagem absoluta (pode passar de 4) e a
    vitória nunca acontece — o que importa é até onde o jogador chegou.
    """
    novo_recorde = pontos > int(dados.get("recorde", 0))

    dados["partidas"] = int(dados.get("partidas", 0)) + 1
    if novo_recorde:
        dados["recorde"] = pontos

    if infinito:
        dados["melhor_infinito"] = max(int(dados.get("melhor_infinito", 0)), bioma)
        dados["pontos_infinito"] = max(int(dados.get("pontos_infinito", 0)), pontos)
        salvar(dados)
        return novo_recorde

    dados["bioma_max"] = max(int(dados.get("bioma_max", 1)), bioma)
    if vitoria:
        dados["vitorias"] = int(dados.get("vitorias", 0)) + 1

    if tempo_restante > float(dados.get("melhor_tempo", 0.0)):
        dados["melhor_tempo"] = round(tempo_restante, 1)

    salvar(dados)
    return novo_recorde
