"""Silhuetas, rastros e avisos. Os sinais são desenhados no ponto usado pela colisão."""
import math
import pygame
from .ilustracao import AMBAR, OSSO, PALIDO, PERIGO, brilho, imagem, losango, sprite
from .combate import CORTES

CORES = {"fio": (159, 209, 211), "ferrao": (253, 185, 100), "onda": (226, 151, 118)}
MEDIDAS = {"morcego": (65, 44), "aranha": (65, 39), "vespa": (61, 42),
           "sombra": (55, 47), "carabideo": (73, 46)}
def efeito(s, nome, centro, dimensoes, espelho=False):
    if nome=="avanco": nome="corte3"
    asset = "efeito_" + nome
    textura = imagem(asset + ".png", *dimensoes, espelho)
    s.blit(textura, textura.get_rect(center=centro))


def golpe_lume(s, lume, cx):
    ataque = lume.arma
    if not ataque.tipo:
        return
    perfil = CORTES[ataque.tipo]
    if ataque.tempo < perfil.espera:
        losango(s, lume.rect.centerx-cx+ataque.face*18, lume.rect.centery-8, 3, OSSO)
        return
    x, y = lume.rect.centerx-cx, lume.rect.centery
    progresso = min(1., (ataque.tempo-perfil.espera)/perfil.ativo)
    restante = 1 - max(0., ataque.tempo - perfil.espera - perfil.ativo) / .12
    if restante <= 0:
        return
    tinta = tuple(int(v * (.53 + .47*min(1., restante))) for v in AMBAR)
    if ataque.tipo == "queda":
        y = lume.rect.bottom-4
        maior = int(18 + progresso*perfil.alcance)
        efeito(s, "queda", (round(x),round(y+maior/2)), (56,maior+15))
        pygame.draw.lines(s, tinta, False, [(x-12,y+3),(x-2,y+maior),(x+10,y+7)], 2)
    else:
        face = ataque.face
        alcance = int(perfil.alcance*(.58 + .42*progresso))
        seno = -1 if ataque.tipo == "corte2" else 1
        centro = (round(x+face*alcance*.52), round(y))
        efeito(s, ataque.tipo, centro, (alcance+12, 63 if ataque.tipo != "corte3" else 77), face<0)
        # Um filete sobre a pintura dá a direção e o limite real do contato.
        angulo = -1.25 + progresso*2.28
        arco = []
        for n in range(12):
            a = angulo - (11-n)*.095
            arco.append((x+face*alcance*(.16+.84*math.cos(a)), y+seno*30*math.sin(a)))
        pygame.draw.lines(s, tinta, False, arco, 2 if ataque.tipo != "corte3" else 3)


def corpo(s,e,cx,t):
    x, y = e.rect.centerx-cx, e.rect.bottom
    pose = int(e.estado in ("aviso", "investida", "atordoado") or
               (e.tipo in ("morcego", "vespa") and int(t*6)%2==1))
    w,h = MEDIDAS[e.tipo]
    if e.estado == "aviso":
        w += 4
        h -= 4
    elif e.estado == "investida":
        w += 8
        h -= 2
    asset = f"inimigo_{e.tipo}_{pose}"
    sprite(s, asset, x, y+2, w, h, e.frente<0)
    if e.tipo == "sombra":
        for i in range(4):
            ponta = x-e.frente*(22+i*5)
            pygame.draw.aaline(s, (111,118,159), (x-7*e.frente,y-13+i),
                               (ponta,y-11+i+math.sin(t*5+i)*6))
    if e.flash>0:
        raio = max(4,round(18*e.flash/.20))
        for i in range(4):
            a=i*math.pi/2+.48
            pygame.draw.line(s, OSSO, (x+math.cos(a)*raio,y-h/2+math.sin(a)*raio),
                             (x+math.cos(a)*(raio+5),y-h/2+math.sin(a)*(raio+5)),2)
    if e.guarda:
        losango(s,x,y-h-17,5,PERIGO,False)
        pygame.draw.line(s,AMBAR,(x-8,y-h-17),(x-4,y-h-17),1)
        pygame.draw.line(s,AMBAR,(x+4,y-h-17),(x+8,y-h-17),1)
    if 0<e.vida<e.max_vida:
        for n in range(e.max_vida):
            losango(s, x+7*n-(e.max_vida-1)*3.5,y-h-6,2,AMBAR if n<e.vida else (92,96,96))


def inimigo(s,e,cx,lume,t):
    if e.ativo and -105 < e.rect.centerx-cx < 1065:
        corpo(s,e,cx,t)


def aviso(s,e,cx,lume,t):
    x,y=e.rect.centerx-cx,e.rect.centery
    tx,ty=e.alvo.x-cx,e.alvo.y
    pct = min(1., 1-e.t/(e.ficha.aviso/e.ritmo)) if e.estado=="aviso" else 1.
    cor = PERIGO if e.estado=="investida" else (196,142,116)
    if e.tecnica=="fenda":
        largura=round(54*pct)
        pygame.draw.line(s,cor,(tx-largura*.5,ty-3),(tx+largura*.5,ty-3),2)
        for a in (-1,1):
            pygame.draw.lines(s,cor,False,[(tx+a*28,ty-2),(tx+a*26,ty-10),(tx+a*22,ty-14)],2)
        if e.estado=="investida":
            efeito(s,"fenda",(round(tx),round(ty-20)),(70,48))
            pygame.draw.lines(s, (216,191,209), False, [(tx-17,ty-4),(tx-7,ty-33),(tx-2,ty-18),(tx+13,ty-35)],2)
        return
    if e.estado!="aviso":
        return
    # Mira pontilhada para fio/ferrão e marca curta para investidas. A mira trava.
    direcao=pygame.Vector2(tx-x,ty-y)
    if direcao.length_squared()<=1:
        return
    limite = min(direcao.length(), 240 if e.tecnica in ("fio","ferrao") else 125)
    direcao= direcao.normalize()
    for n in range(12, int(limite), 15):
        p=pygame.Vector2(x,y)+direcao*n
        pygame.draw.line(s, cor, p, p+direcao*4,1)
    losango(s,x,y-e.rect.h*.65-4,round(3+pct*3),cor,False)


def projeteis(s,e,cx,lume,raio,visivel=None):
    if not e.ativo:
        return
    if e.estado in ("aviso","investida") and abs(e.rect.centerx-lume.rect.centerx)<350:
        aviso(s,e,cx,lume,e.relogio)
    for p in e.projeteis:
        x,y=p.pos.x-cx,p.pos.y
        perto = p.pos.distance_to(lume.rect.center)<max(raio+70,164)
        if -30<x<990 and (perto or visivel and visivel(p.pos,8)):
            cor=CORES[p.tipo]
            if p.tipo=="onda":
                efeito(s,"onda",(round(x),round(y)),(55,25),p.vel.x<0)
                pygame.draw.lines(s,cor,False,[(x-17,y+5),(x-7,y-5),(x,y+3),(x+7,y-6),(x+16,y+5)],2)
            else:
                nome="fio" if p.tipo=="fio" else "ferrao"
                efeito(s,nome,(round(x),round(y)),(37,16),p.vel.x<0)
                d=p.vel.normalize()
                pygame.draw.line(s,cor,(x-d.x*13,y-d.y*13),(x+d.x*4,y+d.y*4),2)
                losango(s,x,y,3,PALIDO if p.tipo=="fio" else AMBAR)

def tranca(s, r):
    """Duas taquaras se curvam a partir do chão; a trança fecha o vão entre elas."""
    terra = r.bottom
    for lado in (-1, 1):
        origem = r.centerx + lado*(r.width//2)
        for n in range(3):
            ramo = [(origem + lado*(10+n*3), terra+3),
                    (origem - lado*3+n, terra-28),
                    (origem - lado*7+n, r.y+85),
                    (r.centerx + lado*(7+n), r.y+15),
                    (r.centerx + lado*11, r.y+2)]
            pygame.draw.lines(s,(45+10*n,47+6*n,38+4*n),False,ramo,8-2*n)
            pygame.draw.lines(s,(126,116,79),False,ramo,1)
    for n in range(7):
        y=terra-13-n*26
        metade=min(15,6+(y-r.top)//10)
        for lado in (-1,1):
            pts=[(r.centerx+lado*metade,y),(r.centerx,y-8),(r.centerx-lado*metade,y-19)]
            pygame.draw.lines(s,(119,91,65),False,pts,3)
            pygame.draw.lines(s,(177,139,91),False,pts,1)
    losango(s,r.centerx,terra-47,9,PERIGO,False)
    losango(s,r.centerx,terra-47,4,AMBAR)
