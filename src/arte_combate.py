"""Silhuetas, rastros e avisos. Os sinais são desenhados no ponto usado pela colisão."""
import math
import pygame
from .ilustracao import AMBAR, OSSO, PALIDO, PERIGO, alto_contraste, brilho, imagem, losango, sprite, texto
from .combate import CORTES
from .fauna_jardim import TEMPO_CACA

CORES = {"fio": (159, 209, 211), "ferrao": (253, 185, 100), "onda": (226, 151, 118), "eco": (153,175,216),"veneno":(163,197,104)}
MEDIDAS = {"morcego": (65, 44), "aranha": (65, 39), "vespa": (61, 42),
           "sombra": (55, 47), "carabideo": (73, 46), "cobra":(74,36)}
def efeito(s, nome, centro, dimensoes, espelho=False):
    if nome=="avanco": nome="corte3"
    if nome in ('pesado','quebra','retorno','aurora'):nome='corte3' if nome!='retorno' else 'corte2'
    asset = "efeito_" + nome
    textura = imagem(asset + ".png", *dimensoes, espelho)
    s.blit(textura, textura.get_rect(center=centro))


def golpe_lume(s, lume, cx):
    ataque = lume.arma
    if not ataque.tipo:
        return
    perfil = ataque.perfil
    if ataque.tempo < perfil.espera:
        losango(s, lume.rect.centerx-cx+ataque.face*18, lume.rect.centery-8, 3, OSSO)
        return
    x, y = lume.rect.centerx-cx, lume.rect.centery
    if ataque.equipamento == 'agulha':
        # Haste e ponta próprias; nenhum sprite de arma externa foi importado.
        ponta = x + ataque.face * perfil.alcance
        pygame.draw.line(s, (157,177,138), (x,y+5), (ponta,y-4), 3)
        pygame.draw.lines(s, OSSO, False, [(ponta-ataque.face*12,y-10),(ponta,y-4),(ponta-ataque.face*10,y+2)],2)
    progresso = min(1., (ataque.tempo-perfil.espera)/perfil.ativo)
    restante = 1 - max(0., ataque.tempo - perfil.espera - perfil.ativo) / .12
    if restante <= 0:
        return
    tinta = tuple(int(v * (.53 + .47*min(1., restante))) for v in AMBAR)
    if ataque.luminoso:
        tinta=(159,226,214)
        brilho(s,(round(x+ataque.face*25),round(y)),28)
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


def corpo_cobra(s, e, x, y, t):
    aviso = e.estado in ("aviso", "aviso_caca")
    bote = e.estado in ("investida", "bote_caca")
    recuo = e.estado in ("recuo", "recuo_caca")
    if aviso:
        duracao = TEMPO_CACA if e.estado == "aviso_caca" else getattr(e, "duracao_aviso", e.ficha.aviso/e.ritmo)
        comprime = 1.-max(0., min(1., e.t/duracao))
        comprimento, altura, ponta = 41-8*comprime, 16+8*comprime, 14
    elif bote:
        comprimento, altura, ponta = 68, 3, 31
    elif recuo:
        comprimento, altura, ponta = 50, 8, 21
    else:
        comprimento, altura, ponta = 54, 10, 24
    escala = getattr(e, "escala", 1.)
    cauda = [
        (x+escala*e.frente*(ponta-comprimento+n*comprimento/12),
         y-6-escala*altura*(n/12)**2+math.sin(t*7+n*.8)*(1 if bote else 3))
        for n in range(13)
    ]
    pygame.draw.lines(s, (40, 56, 33), False, cauda, round(12*escala))
    cor = (151, 130, 75) if escala > 1 else (110, 137, 71)
    pygame.draw.lines(s, cor, False, cauda, round(7*escala))
    for px, py in cauda[::2]:
        pygame.draw.circle(s, (170, 166, 92), (round(px), round(py-1)), 2)
    hx, hy = map(round, cauda[-1])
    cabeca = (hx-11*escala, hy-7*escala, 22*escala, 14*escala)
    pygame.draw.ellipse(s, cor if escala > 1 else (125, 145, 78), cabeca)
    pygame.draw.ellipse(s, (45, 61, 34), cabeca, 1)
    pygame.draw.circle(s, AMBAR, (hx+e.frente*5, hy-2), 2)
    if aviso:
        face = e.frente
        pygame.draw.lines(s, OSSO, False, [(hx+face*6,hy+2),(hx+face*13,hy+3),(hx+face*11,hy+9)], 2)
    elif bote:
        pygame.draw.line(s, PERIGO, (hx+e.frente*10, hy+2), (hx+e.frente*24, hy+2), 2)


def corpo_vespa(s, e, x, y, w, h, pose):
    estado = e.estado
    ancorada = getattr(e, "no_poleiro", False)
    if estado == "aviso":
        duracao = getattr(e, "duracao_aviso", e.ficha.aviso/e.ritmo)
        w -= 10
        h -= 3 + round(6*(1.-max(0., min(1., e.t/duracao))))
    elif estado == "investida":
        w += 7
        h -= 8
    elif estado == "recuo":
        w += 11
        h += 5
        pose = 0
    if ancorada:
        # Abdômen baixo e patas apoiadas distinguem o disparo da vespa de fenda.
        w -= 6
        h -= 5
        pose = int(estado == "aviso")
    sprite(s, f"inimigo_vespa_{pose}", x, y+2, w, h, e.frente<0)
    if ancorada:
        for lado in (-1, 1):
            pygame.draw.lines(s, PALIDO, False, [(x+lado*8,y-9),(x+lado*15,y-3),(x+lado*20,y-3)], 2)
    if estado == "aviso":
        espora = x-e.frente*18
        if e.tecnica == "ferrao":
            pygame.draw.lines(s, OSSO, False, [(espora,y-15),(espora-e.frente*9,y-5),(espora,y-8)], 2)
        else:
            pygame.draw.lines(s, OSSO, False, [(x-e.frente*19,y-h),(x,y-16),(x+e.frente*6,y-26)], 2)
    elif estado == "isca":
        pygame.draw.arc(s, PALIDO, (x-27,y-h-6,54,22), .65, 2.49, 1)


def corpo(s,e,cx,t):
    x, y = e.rect.centerx-cx, e.rect.bottom
    if getattr(e,'cego',0)>0:
        for n in range(3):
            ang=t*7+n*2.1
            losango(s,round(x+math.cos(ang)*14),round(e.rect.top-9+math.sin(ang)*4),2,OSSO)
    pose = int(e.estado in ("aviso", "investida", "atordoado") or
               (e.tipo in ("morcego", "vespa") and int(t*6)%2==1))
    w,h = MEDIDAS[e.tipo]
    if getattr(e, "grupo", None) == "ninhada":
        w, h = round(w*.76), round(h*.78)
    if hasattr(e,'nome'):w,h=88,58
    if e.estado == "aviso":
        w += 4
        h -= 4
    elif e.estado == "investida":
        w += 8
        h -= 2
    asset = f"inimigo_{e.tipo}_{pose}"
    if e.tipo == "cobra":
        corpo_cobra(s, e, x, y, t)
    elif e.tipo == "vespa":
        corpo_vespa(s, e, x, y, w, h, pose)
    else:
        sprite(s, asset, x, y+2, w, h, e.frente<0)
    if e.estado == "investigar":
        # Duas marcas claras junto às patas dianteiras acompanham a escuta.
        cor = (153, 195, 186)
        for n in (0, 1):
            px = x + e.frente * (17 + 5*n)
            py = y - h + 3*n
            pygame.draw.aaline(s, cor, (px, py), (px + e.frente*5, py-4))
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
    if getattr(e,"lentidao",0)>0:
        for n in range(5):
            pygame.draw.circle(s,AMBAR,(round(x+math.sin(t*2+n*1.7)*28),round(y-h/2+math.cos(t*2+n)*19)),2)
    if hasattr(e,'nome'):
        texto(s,e.nome+(' · II' if getattr(e,'fase',1)==2 else ''),x,y-h-43,13,AMBAR,'forte','centerx')
        pygame.draw.line(s,(78,79,52),(x-48,y-h-21),(x+48,y-h-21),4)
        pygame.draw.line(s,AMBAR,(x-48,y-h-21),(x-48+96*max(0,e.vida/e.max_vida),y-h-21),3)
        if getattr(e,'fase',1)==2:
            for n in range(3):
                px=x-14+n*11
                pygame.draw.lines(s,AMBAR,False,[(px-3,y-36),(px+2,y-30),(px-2,y-24)],2)
        if hasattr(e, "exposta") and not e.exposta:
            texto(s,"Escamas fechadas",x,y-h-15,11,PALIDO,"forte","centerx")
    if e.guarda:
        losango(s,x,y-h-17,5,PERIGO,False)
        pygame.draw.line(s,AMBAR,(x-8,y-h-17),(x-4,y-h-17),1)
        pygame.draw.line(s,AMBAR,(x+4,y-h-17),(x+8,y-h-17),1)
    if 0<e.vida<e.max_vida and not hasattr(e,'nome'):
        for n in range(e.max_vida):
            losango(s, x+7*n-(e.max_vida-1)*3.5,y-h-6,2,AMBAR if n<e.vida else (92,96,96))


def inimigo(s,e,cx,lume,t):
    if e.ativo and -105 < e.rect.centerx-cx < 1065:
        corpo(s,e,cx,t)


def aviso(s,e,cx,lume,t):
    x,y=e.rect.centerx-cx,e.rect.centery
    tx,ty=e.alvo.x-cx,e.alvo.y
    duracao = getattr(e, "duracao_aviso", e.ficha.aviso/e.ritmo)
    pct = max(0., min(1., 1-e.t/duracao)) if e.estado=="aviso" else 1.
    cor = PERIGO if e.estado=="investida" else (196,142,116)
    realce=int(alto_contraste())
    if realce:
        cor=(255,197,157)
    if getattr(e,"acao_atual","")=="fenda_dupla":
        for dx in (-48,48):
            pygame.draw.line(s,cor,(tx+dx-20,ty-3),(tx+dx+20,ty-3),2+realce)
        return
    if e.tecnica=="fenda":
        largura=round(54*pct)
        pygame.draw.line(s,cor,(tx-largura*.5,ty-3),(tx+largura*.5,ty-3),2+realce)
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
    angulo = getattr(e, "angulo_veneno", 0)
    linhas = (direcao, direcao.rotate(angulo)) if angulo else (direcao,)
    for rota in linhas:
        for n in range(12, int(limite), 15):
            p=pygame.Vector2(x,y)+rota*n
            pygame.draw.line(s, CORES["veneno"] if angulo else cor, p, p+rota*(6 if angulo else 4), (2 if angulo else 1)+realce)
    losango(s,x,y-e.rect.h*.65-4,round(3+pct*3),cor,False)


def projeteis(s,e,cx,lume,raio,visivel=None):
    if not e.ativo:
        return
    if getattr(e, "exposta", False) and pygame.Vector2(e.rect.center).distance_to(lume.rect.center) < 260:
        # Como a mira, a brecha atravessa o borrão sem revelar o cenário.
        x,y = round(e.rect.centerx-cx),round(e.rect.top-22)
        cor = (168, 231, 192)
        losango(s,x,y,5,cor,False)
        texto(s,"Brecha",x,y-22,12,cor,"forte","centerx")
    if e.estado in ("aviso","investida") and abs(e.rect.centerx-lume.rect.centerx)<350:
        aviso(s,e,cx,lume,e.relogio)
    for p in e.projeteis:
        x,y=p.pos.x-cx,p.pos.y
        perto = p.pos.distance_to(lume.rect.center)<max(raio+70,164)
        if -30<x<990 and (perto or visivel and visivel(p.pos,8)):
            cor=CORES[p.tipo]
            if p.tipo in ("eco","veneno"):
                pygame.draw.circle(s,cor,(round(x),round(y)),8,2)
                pygame.draw.circle(s,PALIDO,(round(x),round(y)),3,1)
            elif p.tipo=="onda":
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
