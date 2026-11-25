"""Galeria da Seda: recorte isolado do Bosque para repetir o encontro com uma aranha."""
from random import Random

import pygame

from .combate import Inimigo
from .fases import CHAO, Fase, Objeto, Terreno
from .narrativa import Bolsa
from .travessia import Jornada, Lume

SALA_ARANHA = "bosque.galeria_da_seda.v1"
SEMENTE_ARANHA = 1701
ABRIGO = (160, CHAO)
LARGURA = 1104
GALERIA = Fase(
    name="Galeria da Seda", width=LARGURA, pisos=((0, LARGURA),),
    plataformas=((448, CHAO-118, 152),), tetos=(),
    objetos=(Objeto("abrigo", "refugio", *ABRIGO, "Descansar sob a casca"),),
    mecanismos={}, preparo="", passos=(), inimigos=(), orvalhos=(),
    registro=("", ""), fonte="",
)


class AranhaObservada(Inimigo):
    """O seletor e os ataques são os da campanha. Só o ensaio anota a decisão."""
    def repor(self):
        super().repor()
        self.observacao = None
        self.instante_aviso = None

    def preparar(self, lume, terrenos=()):
        self.observacao = tuple(lume.rect.center)
        self.instante_aviso = self.relogio
        return super().preparar(lume, terrenos)


class DueloAranha(Jornada):
    sala_id = SALA_ARANHA

    def __init__(self, dificuldade, semente):
        if type(semente) is not int:
            raise ValueError("A semente do duelo deve ser um número inteiro.")
        self.semente = semente
        sorte = Random(f"{self.sala_id}/{semente}")
        self.poleiro = sorte.randint(560, 620)
        galho_x, galho_y, largura = GALERIA.plataformas[0]
        self._terrenos = (
            Terreno(pygame.Rect(0, CHAO, LARGURA, 128), "chao"),
            Terreno(pygame.Rect(0, 0, 34, CHAO), "parede"),
            Terreno(pygame.Rect(LARGURA-34, 0, 34, CHAO), "parede"),
            Terreno(pygame.Rect(335, CHAO-72, 70, 72), "parede"),
            Terreno(pygame.Rect(galho_x, galho_y, largura, 16), "plataforma"),
        )
        super().__init__("historia", dificuldade)

    def entrar(self, indice, retorno=False):
        if indice != 0:
            raise ValueError("O duelo acontece no Bosque.")
        self.etapa = 0
        self.fase = GALERIA
        self.flags = self.historico.setdefault((0, 0), set())
        self.boss = None
        self.gotas = ()
        self.checkpoint = ABRIGO
        self.reiniciar()

    def reiniciar(self):
        self.tempo = 0.
        self.estado = "jogando"
        self.pontuacao = 0
        self.flags.clear()
        self.eventos.clear()
        self.sons_espaciais.clear()
        self.bolsa = Bolsa()
        self.bolsa.estoque["balsamo"] = 0
        self.lume = Lume(*ABRIGO, self.vidas_iniciais)
        self.inimigos = [AranhaObservada("aranha", self.poleiro, CHAO, self.dificuldade, semente=self.semente)]
        super().reiniciar()
        self.lume.iframes = 0.
        self.notificar("O abrigo fica a oeste. A aranha patrulha além da pedra.")

    @property
    def solidos(self):
        return self._terrenos

    @property
    def objetos(self):
        return GALERIA.objetos

    @property
    def objetivo(self):
        return "Vença a aranha da galeria"

    @property
    def dica_local(self):
        return "A pedra intercepta a seda. O galho permite atacar de cima."

    def passo(self, dt, cmd, clarao):
        super().passo(dt, cmd, clarao)
        if self.estado == "jogando" and not self.inimigos[0].ativo:
            self.estado = "vitoria"
            self.eventos.append("vitoria")
