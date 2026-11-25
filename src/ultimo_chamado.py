"""Clímax da Coruja: devolver três sinais entre ataques anunciados."""
from math import hypot

import pygame


QUEDA = .38
MEIA_FAIXA = 25


def iniciar(e, eventos):
    e.coro_iniciado = True
    e.fase = 3
    e.vida = 0.
    e.coro_sinais = e.coro_turno = 0
    e.coro_gota = True
    e.coro_faixas = ()
    e.penas.clear()
    e.fios.clear()
    e.atingiu = False
    e._mudar("coro_inicio", 1.1)
    eventos.append("chamado_final")


def ninhos(e):
    return tuple((x, e.chao-30) for x in (e.esq+75, e.dir-75, (e.esq+e.dir)/2))


def alvo(e):
    return ninhos(e)[min(e.coro_sinais, 2)]


def perto(e, corpo):
    return hypot(corpo.centerx-alvo(e)[0], corpo.centery-alvo(e)[1]) < 98+6*e.aliados


def avisar(e, corpo, eventos):
    x, _ = alvo(e)
    e.coro_turno += 1
    e.atingiu = False
    e.frente = 1 if x >= e.x else -1
    e.destino = max(e.esq, min(e.dir, x+e.frente*120))
    e.alvo_y = e.chao-(13 if e.coro_turno % 2 else 32)
    if e.coro_sinais and e.coro_turno % 2:
        centro = max(e.inicio+MEIA_FAIXA, min(e.inicio+e.largura-MEIA_FAIXA, round(corpo.centerx)))
        e.coro_faixas = (centro,)
        if e.coro_sinais == 2:
            lado = 1 if x > centro else -1
            e.coro_faixas += (centro+lado*105,)
    e._mudar("coro_aviso", .50 + .28*e.ritmo.janela + .04*e.aliados)
    eventos.append("aviso")


def altura_das_penas(e):
    progresso = max(0., min(1., 1-e.tempo/QUEDA))
    return e.chao-212+223*progresso


def atualizar(e, dt, corpo, clarao, interagir, eventos):
    from .chefes import aproximar

    if interagir and e.coro_gota and perto(e, corpo):
        e.coro_gota = False
        eventos.append("gota_final")
    if clarao and perto(e, corpo):
        e.coro_sinais += 1
        e.coro_turno = 0
        e.coro_faixas = ()
        e.atingiu = False
        e.coro_gota = True
        eventos.append("harmonia")
        if e.coro_sinais == 3:
            e.vencido = True
            e.estado = "repouso"
            eventos.append("chefe_resolvido")
        else:
            e._mudar("coro_resposta", .69)
        return
    if e.estado in ("coro_inicio", "coro_resposta", "coro_busca"):
        x, _ = alvo(e)
        outro = e.dir if x < (e.esq+e.dir)/2 else e.esq
        e.x = aproximar(e.x, outro, dt*420)
        e.y = aproximar(e.y, e.chao-145, dt*240)
        if e.tempo <= 0:
            avisar(e, corpo, eventos)
    elif e.estado == "coro_aviso":
        altura = e.chao-158 if e.coro_faixas else e.alvo_y
        e.y = aproximar(e.y, altura, dt*230)
        if e.tempo <= 0:
            if e.coro_faixas:
                e._mudar("coro_queda", QUEDA)
            else:
                e._mudar("coro_investida", 2.)
    elif e.estado == "coro_queda":
        y = altura_das_penas(e)
        for x in e.coro_faixas:
            e._colisao(corpo, pygame.FRect(x-MEIA_FAIXA, y-24, 2*MEIA_FAIXA, 27), eventos)
        if e.tempo <= 0:
            e.coro_faixas = ()
            e._mudar("coro_busca", .60)
    elif e.estado == "coro_investida":
        e.x = aproximar(e.x, e.destino, dt*610)
        e.y = e.alvo_y
        e._colisao(corpo, pygame.FRect(e.x-34, e.y-12, 68, 20), eventos)
        if abs(e.x-e.destino) < .01 or e.tempo <= 0:
            e._mudar("coro_busca", .60)
