"""Vaga-lumes originais desenhados com formas, sem folhas de terceiros."""
import math
import pygame
from .resgates import POR_ID,fontes


def vagalume(s,x,y,t,cor,tipo='tila',escala=1.):
    x,y=round(x),round(y)
    asa=(.5+.5*math.sin(t*14))*9*escala
    for lado in (-1,1):
        pts=[(x,y-24*escala),(x+lado*(13*escala+asa),y-37*escala),(x+lado*17*escala,y-13*escala)]
        pygame.draw.polygon(s,(126,151,133),pts,1)
    pygame.draw.ellipse(s,(51,70,58),(x-7*escala,y-30*escala,14*escala,28*escala))
    pygame.draw.ellipse(s,cor,(x-6*escala,y-16*escala,12*escala,13*escala))
    pygame.draw.circle(s,(172,184,141),(x,y-round(32*escala)),max(1,round(6*escala)))
    pygame.draw.line(s,(36,49,42),(x-3*escala,y-34*escala),(x+3*escala,y-34*escala),2)
    if tipo=='bento':
        pygame.draw.rect(s,(101,154,160),(x+7*escala,y-21*escala,7*escala,12*escala),1)
    elif tipo=='aru':
        pygame.draw.polygon(s,(116,147,81),[(x-9*escala,y-20*escala),(x-20*escala,y-25*escala),(x-14*escala,y-6*escala)])
    else:
        pygame.draw.line(s,(215,162,91),(x-8*escala,y-23*escala),(x+8*escala,y-20*escala),3)


def pessoa(s,o,j,cx,t):
    p=POR_ID[o.id.split('_',1)[1]]
    vagalume(s,o.x-cx,o.y+math.sin(t*2+o.x)*2,t,p.cor,p.id)


def luzes(s,j,cx,t):
    for n,(x,y,r) in enumerate(fontes(j)):
        vagalume(s,x-cx+math.sin(t*.8+n)*8,y+math.cos(t*.7+n)*4,t+n,(216,209,126),'tila',.35)
