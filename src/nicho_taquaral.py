"""Antigo depósito abaixo da margem oeste do Taquaral."""
import pygame

from .combate import Vetor, direcao
from .fases import Objeto, Terreno
from .taticas import Habitante


TITULO = "Nicho dos Berços"
ABERTO = "nicho_bercos_aberto"
ACESO = "nicho_bercos_aceso"
FUNDO = 968
OESTE, LESTE = 1200, 1640
SOLEIRA = 862
TRANCA = Objeto("tranca_bercos", "galeria_sementes", 1700, FUNDO,
                "Erguer a tranca dos berços")
LAMPADA = Objeto("lampada_bercos", "galeria_sementes", 1274, FUNDO,
                 "Acender a luz sobre o cofre")
LAMPADA_ACESA = Objeto(LAMPADA.id, LAMPADA.tipo, LAMPADA.x, LAMPADA.y,
                      "Observar a luz do depósito")
ORIGEM = (1388, FUNDO)
DERROTADA = f"inimigo_{ORIGEM[0]}"


class CobraDosBercos(Habitante):
    nome = "Cobra dos Berços"
    escala = 1.28

    def __init__(self, dificuldade):
        super().__init__("cobra", *ORIGEM, dificuldade)
        self.max_vida += 13
        self.vida = self.max_vida

    def repor(self):
        super().repor()
        self.rect.size = 76, 33
        self.rect.midbottom = self.origem
        self.fase = 1
        self.primeiro_leque = False
        self.brecha = 0.

    @property
    def exposta(self):
        return self.brecha > 0 and self.estado in ("recuo", "atordoado")

    @property
    def duracao_aviso(self):
        base = super().duracao_aviso
        if self.fase == 2 and self.acao_atual != "veneno":
            return max(.38, base*.86)
        return base

    @property
    def angulo_veneno(self):
        return -17*self.frente if self.fase == 2 and self.acao_atual == "veneno" else 0

    def preparar(self, lume, terrenos=()):
        if self.primeiro_leque and self.cego <= 0 and self.viavel(2, lume, terrenos):
            self.plano[:] = [2]
            self.primeiro_leque = False
        return super().preparar(lume, terrenos)

    def lancar(self):
        if self.acao_atual != "veneno":
            super().lancar()
            return
        # Os disparos saem nas mesmas direções desenhadas no aviso.
        self.estado = "investida"
        self.inicio = Vetor(self.rect.center)
        self.duracao = self.t = .18
        velocidade = direcao(self.inicio, self.alvo)*304*self.ritmo
        self.disparar("veneno", self.inicio, velocidade, 1.45)
        if self.angulo_veneno:
            self.disparar("veneno", self.inicio, velocidade.rotate(self.angulo_veneno), 1.45)

    def dano_corte(self, arma, lume):
        dano = super().dano_corte(arma, lume)
        if self.exposta:
            return dano*2.
        return dano if arma.luminoso else dano*.5

    def acertar(self, arma, area, clarao, lume):
        estado, tempo, plano = self.estado, self.t, self.plano
        resultado = super().acertar(arma, area, clarao, lume)
        if resultado == "acerto" and self.estado == "atordoado" and not clarao:
            comprometida = estado in ("aviso", "investida") and not arma.luminoso
            leve = arma.tipo in ("corte1", "corte2") and not arma.luminoso
            if comprometida or leve and self.resistencia_leve > 0:
                self.estado, self.t, self.plano = estado, tempo, plano
            elif leve:
                self.resistencia_leve = .95
        return resultado

    def update(self, dt, lume, raio, restaurado, terrenos):
        if not OESTE <= lume.rect.centerx < LESTE or lume.rect.bottom < 810:
            self.estado, self.t = "patrulha", .18
            self.projeteis.clear()
            self.plano.clear()
            self.brecha = 0.
            if self.rect.midbottom != self.origem:
                self.seguir((self.origem[0], FUNDO-self.rect.h/2), 175, dt, terrenos)
            return [], False
        if self.vida <= self.max_vida/2 and self.fase == 1:
            self.fase = 2
            self.primeiro_leque = True
            self.estado, self.t = "recuo", .64
            self.brecha = 0.
            self.plano.clear()
        self.brecha = max(0., self.brecha-dt)
        entrou_atacando = self.estado == "investida"
        sons, atingiu = super().update(dt, lume, raio, restaurado, terrenos)
        if entrou_atacando and self.estado == "recuo" and self.acao_atual != "veneno" and not atingiu:
            self.brecha = self.t = .94/self.ritmo
            self.plano.clear()
            sons.append(("vulneravel", self.rect.centerx))
        return sons, atingiu


def dentro(j):
    x, y = j.lume.rect.midbottom
    return ABERTO in j.flags and OESTE <= x < LESTE and 800 < y <= 1080


def terrenos(aberto):
    formas = [
        (OESTE, FUNDO, LESTE-OESTE, 112, "chao"),
        (OESTE, 795, LESTE-OESTE+30, 24, "teto"),
        (OESTE, 819, 24, FUNDO-819, "colmos_galeria"),
        (1280, 895, 108, 15, "plataforma"),
        (1484, 877, 108, 15, "plataforma"),
    ]
    if not aberto:
        formas.append((LESTE, SOLEIRA, 30, FUNDO-SOLEIRA, "colmos_galeria"))
    return tuple(Terreno(pygame.Rect(x,y,w,h), tipo) for x,y,w,h,tipo in formas)


def povoar(j):
    if ABERTO in j.flags and DERROTADA not in j.flags:
        j.inimigos.append(CobraDosBercos(j.dificuldade))


def destrancar(j):
    if ABERTO in j.flags:
        j.notificar("A tranca está erguida. O piso leva ao cipó da galeria.")
        return
    j.flags.add(ABERTO)
    povoar(j)
    j.memorizar("O depósito de Risca",
                "Risca guardava as sementes no oeste quando não havia vento. "
                "A veneziana reparada secou o feixe que prendia a tranca. "
                "O cofre de seda e a velha luz ficaram na sala de baixo.")
    j.notificar("Tranca erguida. O depósito fica à esquerda.", 6.)
    j.eventos.extend(("madeira", "porta"))


def acender(j):
    if DERROTADA not in j.flags:
        j.notificar("A cobra guarda o cofre junto à luz apagada.")
    elif ACESO not in j.flags:
        j.flags.add(ACESO)
        j.bolsa.receber("casulo", 2)
        j.memorizar("A luz do depósito", "A cobra recuou. Lume acendeu a luz de Risca e recolheu dois Casulos de seda.")
        j.notificar("Luz permanente acesa. Dois Casulos de seda na bolsa.", 6.)
        j.eventos.extend(("raiz", "coleta"))
    else:
        j.notificar("A luz de Risca ainda está acesa. O cofre já foi recolhido.")
