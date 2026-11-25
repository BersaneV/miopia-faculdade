"""
audio.py — gerenciador de som do Miopia.

Tudo é WAV gerado por `gerar_assets.py` (síntese própria, sem asset de
terceiro). O gerenciador cuida de:
  - efeitos curtos em canais separados;
  - música em loop com fade suave entre telas;
  - volume geral e mudo (tecla M), salvos junto do recorde.

Se a placa de som não existir (laboratório, servidor, CI), o jogo continua
funcionando em silêncio, sem erro.
"""

from __future__ import annotations

import os

import pygame

from . import config


class Audio:
    def __init__(self, pasta: str = config.SONS) -> None:
        self.disponivel = False
        self.mudo = False
        self.volume = 0.8
        self.musica_volume = 0.55
        self.sfx_volume = 0.75

        self._sons: dict = {}
        self._musicas: dict = {}
        self._musica_atual: str | None = None
        self._canal_musica = None
        self._fade_alvo = 0.0
        self._fade_atual = 1.0

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            self._canal_musica = pygame.mixer.Channel(0)
            self.disponivel = True
        except pygame.error:
            self.disponivel = False
            return

        self._carregar(pasta)

    # ------------------------------------------------------------------ #
    def _carregar(self, pasta: str) -> None:
        if not os.path.isdir(pasta):
            return
        for arquivo in sorted(os.listdir(pasta)):
            if not arquivo.endswith(".wav"):
                continue
            nome = arquivo[:-4]
            caminho = os.path.join(pasta, arquivo)
            try:
                som = pygame.mixer.Sound(caminho)
            except pygame.error:
                continue
            if nome.startswith("trilha_"):
                self._musicas[nome[7:]] = som
            else:
                self._sons[nome] = som

    # ------------------------------------------------------------------ #
    # Volume / mudo
    # ------------------------------------------------------------------ #
    def aplicar_volumes(self) -> None:
        if not self.disponivel:
            return
        volume_sfx = 0.0 if self.mudo else self.volume * self.sfx_volume
        for som in self._sons.values():
            som.set_volume(volume_sfx)
        if self._canal_musica:
            self._canal_musica.set_volume(0.0 if self.mudo else self.volume * self.musica_volume)

    def alternar_mudo(self) -> bool:
        self.mudo = not self.mudo
        self.aplicar_volumes()
        return self.mudo

    def ajustar_volume(self, delta: float) -> None:
        self.volume = max(0.0, min(1.0, self.volume + delta))
        self.aplicar_volumes()

    # ------------------------------------------------------------------ #
    # Efeitos
    # ------------------------------------------------------------------ #
    def tocar(self, nome: str, volume: float = 1.0, canal: int | None = None) -> None:
        if not self.disponivel or self.mudo:
            return
        som = self._sons.get(nome)
        if not som:
            return
        som.set_volume(volume * self.volume * self.sfx_volume)
        if canal is None:
            som.play()
        else:
            pygame.mixer.Channel(canal).play(som)

    # ------------------------------------------------------------------ #
    # Música
    # ------------------------------------------------------------------ #
    def tocar_musica(self, nome: str, fade: float = 1.0) -> None:
        if not self.disponivel:
            return
        if nome == self._musica_atual:
            return
        musica = self._musicas.get(nome)
        if not musica:
            return
        self._musica_atual = nome
        self._fade_atual = 0.0
        self._fade_alvo = 1.0
        try:
            self._canal_musica.play(musica, loops=-1, fade_ms=int(fade * 1000))
        except pygame.error:
            pass
        self.aplicar_volumes()

    def parar_musica(self) -> None:
        if not self.disponivel or not self._canal_musica:
            return
        self._canal_musica.fadeout(600)
        self._musica_atual = None

    def atualizar(self, dt: float) -> None:
        """Fade manual de volume — deixa a troca de trilha menos brusca."""
        if not self.disponivel or not self._canal_musica:
            return
        alvo = 0.0 if self.mudo else self.volume * self.musica_volume
        self._fade_atual += (1.0 if self._fade_atual < alvo else -1.0) * dt * 2.0
        self._fade_atual = max(0.0, min(1.0, self._fade_atual))
        if self._canal_musica.get_busy():
            self._canal_musica.set_volume(alvo * self._fade_atual)

    # ------------------------------------------------------------------ #
    def parar_tudo(self) -> None:
        if not self.disponivel:
            return
        pygame.mixer.stop()
