"""
recursos.py — fontes, superfícies cacheadas e áudio.

Superfícies caras (escuridão, brilho, vinheta, textura do chão) são
construídas uma vez e reaproveitadas. Isso é o que garante 60 FPS mesmo
com a máscara de escuridão em tela cheia.
"""

from __future__ import annotations

import math
import os

import pygame

from . import config
from .audio import Audio


class Recursos:
    def __init__(self) -> None:
        self.fontes: dict[str, pygame.font.Font] = {}
        self._carregar_fontes()

        self.audio = Audio()

        self._cache_escuro: dict[tuple[int, int], pygame.Surface] = {}
        self._cache_brilho: dict[tuple[int, tuple], pygame.Surface] = {}
        self._cache_chao: dict[int, pygame.Surface] = {}
        self._vinheta: pygame.Surface | None = None
        self._quadrado: pygame.Surface | None = None

    # ------------------------------------------------------------------ #
    # Fontes
    # ------------------------------------------------------------------ #
    def _carregar_fontes(self) -> None:
        def abrir(caminho: str, tamanho: int) -> pygame.font.Font:
            try:
                return pygame.font.Font(caminho, tamanho)
            except (OSError, pygame.error):
                return pygame.font.SysFont("dejavusans", tamanho, bold=True)

        # Escala tipográfica (ui.py): display 92 · h1 56 · h2 34 · h3 24 ·
        # corpo 19 · pequena 15. Chaves fixas para não quebrar as telas.
        self.fontes = {
            "titulo_grande": abrir(config.FONTE_TITULO, 92),
            "titulo": abrir(config.FONTE_TITULO, 56),
            "titulo_medio": abrir(config.FONTE_TITULO, 34),
            "h2": abrir(config.FONTE_TEXTO, 24),
            "h2_forte": abrir(config.FONTE_NEGRITO, 24),
            "corpo": abrir(config.FONTE_TEXTO, 19),
            "corpo_forte": abrir(config.FONTE_NEGRITO, 19),
            "pequena": abrir(config.FONTE_TEXTO, 15),
            "pequena_forte": abrir(config.FONTE_NEGRITO, 15),
            "hud": abrir(config.FONTE_NEGRITO, 18),
            "hud_num": abrir(config.FONTE_NEGRITO, 24),
            "botao": abrir(config.FONTE_NEGRITO, 21),
            "enorme": abrir(config.FONTE_TITULO, 76),
        }

    def fonte(self, nome: str) -> pygame.font.Font:
        return self.fontes[nome]

    # ------------------------------------------------------------------ #
    # Escuridão: gradiente usado como "buraco" na máscara preta
    # ------------------------------------------------------------------ #
    def escuro(self, raio: float) -> pygame.Surface:
        chave = (int(raio) // 4, 0)
        cache = self._cache_escuro.get(chave)
        if cache is not None:
            return cache

        raio_int = max(8, int(raio))
        tamanho = raio_int * 2
        surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        passos = max(14, min(120, raio_int // 2))
        for i in range(passos, 0, -1):
            t = i / passos
            # alpha alto no centro (apaga a escuridão) e zero na borda,
            # com curva suave para a luz não terminar em "bolha"
            alpha = int(255 * (1.0 - t ** 1.05))
            if alpha <= 0:
                continue
            pygame.draw.circle(surf, (255, 255, 255, alpha), (raio_int, raio_int),
                               max(1, int(raio_int * t)))
        self._cache_escuro[chave] = surf
        return surf

    def escuro_quadro(self, raio: float) -> pygame.Surface:
        """
        Máscara de escuridão completa da área do jogo (preta, com buraco).
        Chamada uma vez por frame; o gradiente vem do cache.
        """
        quadro = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA),
                                pygame.SRCALPHA)
        quadro.fill((0, 0, 0, 255))
        return quadro

    # ------------------------------------------------------------------ #
    # Brilho aditivo (luz do vaga-lume)
    # ------------------------------------------------------------------ #
    def brilho(self, raio: float, cor: tuple[int, int, int]) -> pygame.Surface:
        chave = (int(raio) // 6, tuple(cor))
        cache = self._cache_brilho.get(chave)
        if cache is not None:
            return cache

        raio_int = max(8, int(raio))
        tamanho = raio_int * 2
        surf = pygame.Surface((tamanho, tamanho))
        surf.fill((0, 0, 0))
        passos = max(10, min(80, raio_int // 3))
        for i in range(passos, 0, -1):
            t = i / passos
            intensidade = (1.0 - t) ** 2.2
            tom = tuple(int(clamp_cor(c * intensidade)) for c in cor)
            if tom == (0, 0, 0):
                continue
            pygame.draw.circle(surf, tom, (raio_int, raio_int), max(1, int(raio_int * t)))
        self._cache_brilho[chave] = surf
        return surf

    # ------------------------------------------------------------------ #
    # Vinheta e textura
    # ------------------------------------------------------------------ #
    def vinheta(self) -> pygame.Surface:
        if self._vinheta is None:
            surf = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
            centro = (config.LARGURA // 2, config.ALTURA // 2)
            maior = int(math.hypot(*centro))
            passos = 60
            for i in range(passos):
                t = i / passos
                alpha = int(95 * (t ** 2.6))
                if alpha <= 0:
                    continue
                pygame.draw.circle(surf, (0, 0, 0, alpha), centro,
                                   int(maior * (1 - t)), 0)
            self._vinheta = surf
        return self._vinheta

    def textura_chao(self, bioma: int) -> pygame.Surface:
        if bioma not in self._cache_chao:
            import random

            sorteio = random.Random(1000 + bioma)
            surf = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA),
                                  pygame.SRCALPHA)
            for _ in range(1400):
                x = sorteio.randrange(config.AREA_LARGURA)
                y = sorteio.randrange(config.AREA_ALTURA_USADA)
                cor = sorteio.choice(((255, 255, 255, 8), (255, 255, 255, 12),
                                      (140, 200, 255, 10)))
                pygame.draw.circle(surf, cor, (x, y), sorteio.choice((1, 1, 2)))
            self._cache_chao[bioma] = surf
        return self._cache_chao[bioma]

    # ------------------------------------------------------------------ #
    def quadrado(self) -> pygame.Surface:
        """Superfície 1x1 branca, útil para desenhar retângulos com alpha."""
        if self._quadrado is None:
            self._quadrado = pygame.Surface((1, 1))
            self._quadrado.fill((255, 255, 255))
        return self._quadrado


def clamp_cor(valor: float) -> float:
    return max(0.0, min(255.0, valor))


def pasta_existe(caminho: str) -> bool:
    return os.path.isdir(caminho)
