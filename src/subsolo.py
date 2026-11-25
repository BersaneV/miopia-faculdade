"""Desvio do Córrego no mesmo espaço físico, alcançado ao atravessar uma grade."""
import math
import pygame
from .fases import CHAO, Objeto, Terreno

ALTURA = 1220
ENTRADA = (2520, 2680)
SAIDA = (2980, 3095)


def ativo(j):
    return j.modo == "historia" and j.etapa == 1 and not j.em_vertical and not hasattr(j, "sala_id")


def terrenos(superficie):
    out = []
    for t in superficie:
        r = t.rect
        abertura = next((v for v in (ENTRADA, SAIDA) if r.left <= v[0] and r.right >= v[1]), None)
        if t.tipo == "chao" and r.y == CHAO and abertura:
            for a, b in ((r.left, abertura[0]), (abertura[1], r.right)):
                if b > a:
                    out.append(Terreno(pygame.Rect(a, r.y, b-a, r.h), "chao"))
            out.append(Terreno(pygame.Rect(abertura[0], CHAO, abertura[1]-abertura[0], 16), "grade"))
        else:
            out.append(t)
    # Patamares alternados a 90–100 px. Todos atravessam por baixo e aceitam
    # descida intencional, permitindo refazer a subida com controles normais.
    for x, y, w in ((2505,532,190), (2570,622,220), (2505,712,190),
                    (2570,802,220), (2505,892,190), (2570,982,220),
                    (2790,982,200), (2940,892,190), (2790,802,190),
                    (2940,712,190), (2790,622,340), (2940,532,190)):
        out.append(Terreno(pygame.Rect(x,y,w,18), "plataforma"))
    out.extend((Terreno(pygame.Rect(2462,570,30,532), "parede"),
                Terreno(pygame.Rect(3140,570,30,532), "parede"),
                Terreno(pygame.Rect(2462,1102,708,118), "chao")))
    return out


def objetos(j):
    return (() if j.bolsa.estoque.get("asa") else
            (Objeto("reliquia_asa", "reliquia", 2940,1102,"Recolher a membrana de libélula"),))


def limite_queda(j):
    # Os demais vãos continuam perigosos; só a câmara escavada contém terreno.
    if ativo(j) and 2440 <= j.lume.rect.centerx <= 3190:
        return ALTURA + 28
    return 550


def camera(j, dt=None):
    alvo = max(0., min(ALTURA-540., j.lume.rect.centery-(CHAO-21.)))
    if dt is None:
        j.camera_y = alvo
    else:
        j.camera_y += (alvo-j.camera_y) * (1.-math.exp(-8.5*dt))
