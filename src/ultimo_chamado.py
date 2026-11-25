"""Clímax da Coruja: cruzar a arena e devolver três sinais, com ataques anunciados."""
from math import hypot
import pygame


def iniciar(e,eventos):
    e.coro_iniciado=True;e.fase=3;e.vida=0.
    e.coro_sinais=0;e.coro_gota=True;e.penas.clear();e.fios.clear()
    e.atingiu=False;e._mudar('coro_inicio',1.1)
    eventos.append('chamado_final')


def alvo(e):
    xs=(e.esq+75,e.dir-75,(e.esq+e.dir)/2)
    return xs[min(e.coro_sinais,2)],e.chao-30


def perto(e,corpo):
    return hypot(corpo.centerx-alvo(e)[0],corpo.centery-alvo(e)[1])<(115 if e.aliados==3 else 98)


def avisar(e,eventos):
    x,y=alvo(e)
    e.frente=1 if x>=e.x else -1
    e.destino=max(e.esq,min(e.dir,x+e.frente*120))
    e.alvo_y=e.chao-(13 if e.turno%2 else 32)
    e.atingiu=False
    e._mudar('coro_aviso',.78 if e.aliados<3 else .92)
    eventos.append('aviso')


def atualizar(e,dt,corpo,clarao,interagir,eventos):
    from .chefes import aproximar
    if interagir and e.coro_gota and perto(e,corpo):
        e.coro_gota=False
        eventos.append('gota_final')
    if clarao and perto(e,corpo):
        e.coro_sinais+=1
        e.atingiu=False;e.coro_gota=True
        eventos.append('harmonia')
        if e.coro_sinais==3:
            e.vencido=True;e.estado='repouso'
            eventos.append('chefe_resolvido')
            return
        e._mudar('coro_resposta',.9)
    if e.estado in ('coro_inicio','coro_resposta','coro_busca'):
        x,_=alvo(e)
        outro=e.dir if x<(e.esq+e.dir)/2 else e.esq
        e.x=aproximar(e.x,outro,dt*420)
        e.y=aproximar(e.y,e.chao-145,dt*240)
        if e.tempo<=0:
            e.turno+=1;avisar(e,eventos)
    elif e.estado=='coro_aviso':
        e.y=aproximar(e.y,e.alvo_y,dt*230)
        if e.tempo<=0:e._mudar('coro_investida',2.)
    elif e.estado=='coro_investida':
        e.x=aproximar(e.x,e.destino,dt*610);e.y=e.alvo_y
        e._colisao(corpo,pygame.FRect(e.x-34,e.y-12,68,20),eventos)
        if abs(e.x-e.destino)<.01 or e.tempo<=0:e._mudar('coro_busca',.6)
