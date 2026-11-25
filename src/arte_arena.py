"""Camada de cenário e sinais das arenas. Posições mecânicas vêm de Encontro."""
from functools import lru_cache
from math import cos, sin, tau
from pathlib import Path
import pygame

from .chefes import ESCURO, FERRUGEM, FIO, OURO, PELE, TEAL, _quadros


ARTES = Path(__file__).resolve().parent.parent / "assets" / "arte"


@lru_cache(maxsize=16)
def _peca(nome, largura, altura):
    arte = pygame.image.load(str(ARTES / ("obj_" + nome + ".png")))
    return pygame.transform.smoothscale(arte, (largura, altura))


@lru_cache(maxsize=8)
def _retrato(indice, postura):
    return pygame.image.load(str(ARTES / f"chefe_{indice}_{postura}.png"))


@lru_cache(maxsize=512)
def _corpo(indice, pose, quadro, face):
    # Variações pequenas mantêm os pontos de contato estáveis entre quadros.
    postura = ((0, 0, 1, 1), (0, 0, 1, 1), (0, 0, 0, 1), (0, 1, 1, 0))[indice][pose]
    arte = _retrato(indice, postura)
    largura = [(103, 147), (131, 125), (112, 117), (107, 159)][indice][postura]
    altura = largura * arte.get_height() / arte.get_width()
    ciclo = (0, 1, 0, -1)[quadro]
    folego = (1.3, 2.0, 2.8, 0.8)[pose]
    w, h = round(largura + ciclo*folego), round(altura - ciclo*folego)
    corpo = pygame.transform.smoothscale(arte, (w,h))
    if face > 0:
        corpo = pygame.transform.flip(corpo, True, False)
    if pose == 2 and indice in (0,3):
        corpo = pygame.transform.rotate(corpo, face * (4 + ciclo * 1.5))
    return corpo


@lru_cache(maxsize=4)
def _gravura(nome):
    # Uma imagem gravada no marco de entrada conserva a silhueta dos guardiões.
    quadro = _quadros(nome)[0,0,1]
    pigmento = pygame.mask.from_surface(quadro).to_surface(
        setcolor=(124,147,132,120), unsetcolor=(0,0,0,0))
    return pygame.transform.smoothscale(pigmento, (53,43))


def _roda(surf, centro, t):
    x, y = centro
    pygame.draw.rect(surf, ESCURO, (x-7, y+9, 14, 24), border_radius=3)
    pygame.draw.line(surf, PELE, (x-12,y+31), (x+13,y+31), 4)
    pygame.draw.circle(surf, (40,55,53), centro, 18)
    pygame.draw.circle(surf, FIO, centro, 17, 2)
    pygame.draw.circle(surf, PELE, centro, 13, 2)
    for i in range(5):
        a = t + i*tau/5
        tip = (x+round(19*cos(a)), y+round(19*sin(a)))
        pygame.draw.line(surf, TEAL, centro, tip, 2)
        pygame.draw.circle(surf, OURO, tip, 2)
    imagem = _peca("valvula", 44, 43)
    surf.blit(imagem, imagem.get_rect(center=centro))
    pygame.draw.circle(surf, OURO, centro, 3)


@lru_cache(maxsize=2)
def _tronco(espelho):
    casca = _peca("galho",139,43)
    return pygame.transform.rotate(casca,88*espelho)


def _parede(surf, x, y, espelho):
    # Feixe de raiz gasto, com cicatrizes atravessando o veio.
    casca = _tronco(espelho)
    surf.blit(casca, casca.get_rect(midbottom=(x,y+3)))
    for h in range(3):
        sy = y - 39 - h*13
        pygame.draw.lines(surf, (215,173,109), False,
                          [(x-7,sy+4),(x+2,sy-2),(x+9,sy-6)], 2)


def _apoio(surf, rect, indice):
    x,y,w,h = rect
    nome = ("galho", "galho", "bambu", "pedra")[indice]
    corpo = _peca(nome,w,h+17)
    surf.blit(corpo,(x,y-2))
    pygame.draw.line(surf, (166,173,140), (x+2,y+1),(x+w-3,y+1),1)


def _teia(surf, x, y, espelho):
    for i in range(4):
        dx = (15+i*21)*espelho
        pygame.draw.line(surf,(82,110,108),(x,y),(x+dx,y+97-i*20),1)
    for i in range(1,5):
        r = i/5
        pygame.draw.lines(surf,(69,90,90),False,
                          [(x+(15+j*21)*espelho*r,y+(97-j*20)*r) for j in range(4)],1)


def _semente(surf,x,y,t):
    # Fruto resinoso preso a um berço de bambu sobre rodinhas de casca.
    pygame.draw.ellipse(surf,(69,59,44),(x-17,y-27,34,25))
    pygame.draw.ellipse(surf,(180,151,103),(x-17,y-27,34,25),1)
    imagem = _peca("barril",43,34)
    surf.blit(imagem,imagem.get_rect(midbottom=(x,y-2)))
    for offset in [-9,6]:
        pygame.draw.arc(surf,(156,136,94),(x+offset-5,y-27,10,24),0,tau,2)
    pygame.draw.line(surf,OURO,(x-5,y-15),(x+6,y-19),2)
    pygame.draw.line(surf,(156,145,103),(x-20,y-3),(x+19,y-3),3)
    for dx in [-12,12]:
        pygame.draw.circle(surf,ESCURO,(x+dx,y),4)
        pygame.draw.circle(surf,PELE,(x+dx,y),4,1)


def _braseiro(surf,x,y,t):
    pygame.draw.polygon(surf,(65,63,55),[(x-13,y),(x-9,y-25),(x+10,y-25),(x+16,y)])
    for i in range(3):
        dx = (i-1)*5
        h = 9 + 5*sin(t*4+i)
        pygame.draw.polygon(surf,[FERRUGEM,OURO,FERRUGEM][i],[(x+dx-3,y-25),(x+dx,y-26-h),(x+dx+4,y-25)])
    pygame.draw.line(surf,TEAL,(x-12,y-25),(x+12,y-25),2)


def _sino(surf,x,y,t,onda):
    p = round(sin(t*14)*onda*6)
    pygame.draw.line(surf,PELE,(x,y-18),(x+p,y),2)
    pygame.draw.polygon(surf,(95,110,96),[(x+p-3,y),(x+p+3,y),(x+p+7,y+13),
                        (x+p+12,y+18),(x+p+12,y+20),(x+p-12,y+20),(x+p-12,y+18),(x+p-7,y+13)])
    imagem = _peca("sino",34,39)
    surf.blit(imagem,imagem.get_rect(midbottom=(x+p,y+22)))
    pygame.draw.line(surf,OURO,(x+p-11,y+18),(x+p+11,y+18),2)
    pygame.draw.circle(surf,FIO,(x+p,y+22),2)
    if onda>0:
        pygame.draw.circle(surf,FIO,(x+p,y+14),round(17+48*(1-onda)),1)


def _cenario(surf,e,cx,cy):
    base = round(e.chao-cy)
    l, r = round(e.inicio-cx), round(e.inicio+e.largura-cx)
    _parede(surf,l+28,base,1)
    _parede(surf,r-28,base,-1)
    marco = _gravura(e.ficha.folha)
    surf.blit(marco,marco.get_rect(center=(l+31,base-98)))
    for apoio in e.apoios():
        _apoio(surf, apoio.move(-int(cx),-int(cy)), e.indice)
    if e.indice == 1:
        from .ninhada import pontos as abrigos_da_ninhada
        x = round(e.cortina-cx)
        _teia(surf,l+80,base-225,1)
        _teia(surf,r-90,base-210,-1)
        _roda(surf,(round(e.valvula-cx),base-30), .5 + e.agua*.8)
        pygame.draw.lines(surf,PELE,False,[(e.valvula-cx,base-48),(e.valvula-cx,base-215),
                                            (x,base-216)],2)
        pygame.draw.line(surf,(82,121,119),(x-18,base-217),(x+20,base-217),4)
        for abrigo in abrigos_da_ninhada(e):
            px = round(abrigo-cx)
            pygame.draw.lines(surf, PELE, False, [(px-18,base),(px,base-23),(px+14,base)], 2)
            pygame.draw.ellipse(surf, (85, 99, 81), (px-13,base-23,26,23))
            for n in range(3):
                pygame.draw.aaline(surf, FIO, (px-8,base-18+n*5), (px+9,base-16+n*5))
        if e.agua>0:
            for i in range(12):
                sx = x - 20 + i*3
                offset = int((e.relogio*(165+i*3)+i*31) % 153)
                pygame.draw.line(surf,TEAL,(sx,base-210+offset),(sx+1,base-184+offset),1)
            pygame.draw.ellipse(surf,TEAL,(x-32,base-6,64,7),1)
    elif e.indice == 2:
        _braseiro(surf,round(e.brasa-cx),base,e.relogio)
        mx = round(e.entalhe-cx)
        pygame.draw.ellipse(surf,OURO,(mx-22,base-9,44,8),2)
        pygame.draw.line(surf,OURO,(mx-16,base-14),(mx-19,base-19),1)
        pygame.draw.line(surf,OURO,(mx+16,base-14),(mx+19,base-19),1)
        if not e.vencido and e.estado not in ("flor","aberto"):
            _semente(surf,round(e.barrel_x-cx),base-3,e.relogio)
        if e.estado == "flor":
            raio = round(12+(1-e.onda)*105)
            for i in range(11):
                a = i*tau/11
                pygame.draw.line(surf,OURO,(mx+cos(a)*raio*.7,base-20+sin(a)*raio*.7),
                                 (mx+cos(a)*raio,base-20+sin(a)*raio),2)
    elif e.indice == 3:
        vx = round(e.valvula-cx)
        _roda(surf,(vx,base-30),1.3 if e.sino_movido else 0.)
        bx = round((e.dir if e.sino_movido else e.inicio+e.largura*.5)-cx)
        by = base-148
        pygame.draw.lines(surf,PELE,False,[(vx,base-48),(vx,base-220),(bx,base-226),(bx,by-18)],2)
        for pos in [(vx,base-220),(bx,base-226)]:
            pygame.draw.circle(surf,FIO,pos,5,1)
        _sino(surf,bx,by,e.relogio,e.onda if e.sino_soou or e.impacta else 0)
        from .aula_sino import marca as marca_do_sino
        marca_do_sino(surf,round(e.dir-cx),base-118,e.sino_soou or e.tecnica=="sino")


def _linha_de_aviso(surf, inicio, fim):
    dx,dy = fim[0]-inicio[0],fim[1]-inicio[1]
    pontos = max(1,round((dx*dx+dy*dy)**.5/16))
    for i in range(pontos):
        a,b = i/pontos,(i+.46)/pontos
        pygame.draw.line(surf,FERRUGEM,(inicio[0]+dx*a,inicio[1]+dy*a),
                         (inicio[0]+dx*b,inicio[1]+dy*b),2)
    pygame.draw.circle(surf,FERRUGEM,tuple(round(v) for v in fim),7,1)
    return pontos


def _sinais_do_chamado(surf, e, cx, cy):
    from .arte_resgates import vagalume
    from .ultimo_chamado import MEIA_FAIXA, altura_das_penas, ninhos

    for indice, (tx, ty) in enumerate(ninhos(e)):
        x, y = round(tx-cx), round(ty-cy)
        if indice < e.coro_sinais:
            pygame.draw.circle(surf, TEAL, (x,y), 14, 2)
            pygame.draw.lines(surf, FIO, False, [(x-6,y), (x-2,y+4), (x+7,y-5)], 2)
        elif indice == e.coro_sinais:
            pygame.draw.circle(surf, OURO, (x,y), 23, 2)
            pygame.draw.lines(surf, OURO, False, [(x-9,y+6), (x,y-7), (x+9,y+6)], 2)
            for n in range(e.aliados):
                desloc = (n-(e.aliados-1)/2)*31
                vagalume(surf,x+desloc,y-45,e.relogio+n,OURO,'tila',.5)
        else:
            pygame.draw.ellipse(surf, PELE, (x-11,y+16,22,6), 1)
    base = round(e.chao-cy)
    if e.coro_faixas:
        for centro in e.coro_faixas:
            x = round(centro-cx)
            bordas = x-MEIA_FAIXA, x+MEIA_FAIXA
            pygame.draw.line(surf, FERRUGEM, (bordas[0],base-3), (bordas[1],base-3), 3)
            if e.estado == 'coro_aviso':
                for borda in bordas:
                    for y in range(base-194, base-18, 23):
                        pygame.draw.line(surf, FERRUGEM, (borda,y), (borda,y+10), 2)
                for y in (base-180, base-108, base-37):
                    pygame.draw.lines(surf, OURO, False, [(x-7,y-5), (x,y+3), (x+7,y-5)], 2)
            else:
                y = round(altura_das_penas(e)-cy)
                for dx, dy in ((-15,-6), (0,0), (15,-13)):
                    pygame.draw.polygon(surf, FIO, [(x+dx-3,y+dy-26), (x+dx+5,y+dy-15),
                                                    (x+dx,y+dy), (x+dx-6,y+dy-11)])
                    pygame.draw.line(surf, OURO, (x+dx,y+dy-14), (x+dx,y+dy+2), 2)
    elif e.estado == 'coro_aviso':
        _linha_de_aviso(surf, (e.x-cx,e.alvo_y-cy), (e.destino-cx,e.alvo_y-cy))


def _mira(surf, e, cx, cy):
    x, y = e.x-cx, e.y-cy
    if e.estado.startswith('coro_'):
        _sinais_do_chamado(surf, e, cx, cy)
        return
    if e.indice == 2 and e.estado == 'aviso' and e.tecnica == 'salto':
        from .casco import ponto_salto
        # Mesmo arco parabólico e mesma aterrissagem usados pela simulação.
        for n in range(0, 24, 2):
            pontos = []
            for p in (n/24, (n+1)/24):
                px,py=ponto_salto((e.x,e.y),e.destino,e.alvo_y,p)
                pontos.append((px-cx,py-cy))
            pygame.draw.line(surf, FERRUGEM, *pontos, 2)
        pygame.draw.ellipse(surf, FERRUGEM, (e.destino-cx-34,e.chao-cy-11,68,10),2)
        return
    if e.indice == 2 and e.estado in ('aviso', 'varrida_casco') and e.tecnica == 'varrida':
        l = x if e.frente > 0 else x-113
        pygame.draw.rect(surf, FERRUGEM, (l,e.chao-cy-72,113,71), 1, border_radius=8)
        for n in range(3):
            px = x+e.frente*(27+n*27)
            pygame.draw.lines(surf, OURO, False, [(px-e.frente*6,e.chao-cy-32),(px,e.chao-cy-38),(px-e.frente*6,e.chao-cy-44)],2)
        return
    if e.indice == 3 and e.estado == 'aviso' and e.tecnica == 'penas':
        dx, dy = e.destino-e.x, e.alvo_y-e.y
        for fator in (-.16, .16):
            _linha_de_aviso(surf, (x,y), (x+dx-dy*fator,y+dy+dx*fator))
        return
    if e.estado in ("aviso", "rastro"):
        # A indicação desenha o plano de ataque, inclusive por cima da penumbra.
        if e.indice==1:
            fim = (e.destino-cx, e.alvo_y-cy)
            inicio = (x,y)
        else:
            fim = (e.destino-cx, e.alvo_y-cy)
            inicio = (x,e.alvo_y-cy)
        pontos = _linha_de_aviso(surf,inicio,fim)
        if e.indice==1 and e.segundo_fio is not None:
            x2,y2 = e.segundo_fio
            _linha_de_aviso(surf,inicio,(x2-cx,y2-cy))
        if e.indice==0 and e.asa_rasteira:
            # Folhas levantando da linha de voo; forma legível também em mudo.
            for i in range(1,pontos,3):
                px = inicio[0]+(fim[0]-inicio[0])*i/pontos
                pygame.draw.lines(surf,FIO,False,[(px-4,fim[1]+3),(px,fim[1]-2),(px+4,fim[1]+3)],2)
        for j in [-1,0,1]:
            pygame.draw.line(surf,FERRUGEM,(x+j*6,y-43),(x+j*9,y-50),2)
    if e.estado == "aberto":
        ax,ay = e._marca()
        mx,my = round(ax-cx),round(ay-cy)
        r = 12+round(2*sin(e.relogio*6))
        pygame.draw.circle(surf,OURO,(mx,my),r,1)
        pygame.draw.lines(surf,OURO,True,[(mx-4,my),(mx,my-5),(mx+4,my),(mx,my+5)],2)


def desenhar_encontro(surf,e,cx,cy=0):
    if e.inicio + e.largura < cx-120 or e.inicio > cx+surf.get_width()+120:
        return
    _cenario(surf,e,cx,cy)
    if e.indice == 3 and e.vencido:
        return  # A Coruja acalmada já aparece junto à raiz de fora.
    x,y = round(e.x-cx),round(e.y-cy)
    if e.indice == 1 and not e.vencido:
        pygame.draw.line(surf,TEAL,(x,round(e.chao-cy-260)),(x,y),1)
    if e.indice == 3 and e.estado == "busca":
        r = 29+int(e.relogio*36)%27
        face = x+e.frente*25
        pygame.draw.arc(surf,TEAL,(face-r,y-14-r,2*r,2*r),-.8 if e.frente>0 else 2.35,
                        .8 if e.frente>0 else 3.95,1)
    pose = {"aviso":1,"rastro":1,"investida_seiva":2,"investida":2,"desce":2,"flor":2,"aberto":3,"repouso":3,
            'salto_casco':2,'varrida_casco':2,'muda_casco':3,'muda_coruja':1,'recolhe_coruja':0}.get(e.estado,0)
    if e.indice==0 and e.estado=="aviso" and e.asa_rasteira:
        pose = 2  # abre as asas horizontalmente já na preparação do rasante
    if e.estado=='coro_aviso':pose=1
    if e.estado in ('coro_investida', 'coro_queda'):pose=2
    imagem = _corpo(e.indice,pose,int(e.relogio*(5 if pose==0 else 8))%4,e.frente)
    caixa = imagem.get_rect(center=(x,y))
    caixa.bottom = min(caixa.bottom, round(e.chao-cy+2))
    surf.blit(imagem,caixa)
    if e.indice in (2,3) and getattr(e,'fase',1)==2 and not e.vencido:
        # Cicatrizes e penas destacadas conservam a leitura da fase em mudo.
        for n in range(3):
            px=x-20+n*17
            pygame.draw.lines(surf,OURO,False,[(px-4,y-27),(px+3,y-20),(px-2,y-11)],2)
    if e.estado in ('muda_casco','muda_coruja'):
        pygame.draw.circle(surf, OURO,(x,y),round(48+16*sin(e.relogio*8)),2)



def sinais_encontro(surf,e,cx,cy=0):
    """Fios e marcas de ataque continuam visíveis além do alcance pessoal."""
    if e.ninhada is not None and e.ninhada.cascas:
        for origem in e.ninhada.cascas:
            x, y = round(origem-cx), round(e.chao-cy)
            pygame.draw.ellipse(surf, OURO, (x-26,y-12,52,12), 2)
            for f in (-1,1):
                pygame.draw.lines(surf, FIO, False, [(x+f*4,y-14),(x+f*14,y-29),(x+f*20,y-25)], 2)
            pygame.draw.lines(surf, FERRUGEM, False, [(x-6,y-32),(x,y-39),(x+6,y-32)], 2)
    for f in e.fios:
        x,y = f.x-cx, f.y-cy
        pygame.draw.line(surf,TEAL,(x-f.vx*.07,y-f.vy*.07),(x,y),2)
        pygame.draw.circle(surf,FIO,(round(x),round(y)),4)
    for o in getattr(e, 'ondas', ()):
        x,y=round(o.x-cx),round(o.y-cy)
        pygame.draw.lines(surf,FERRUGEM,False,[(x-17,y-2),(x-7,y-16),(x,y-6),(x+8,y-14),(x+17,y-2)],3)
    for p in getattr(e, 'penas', ()):
        x,y=p.x-cx,p.y-cy
        pygame.draw.line(surf,FIO,(x-p.vx*.035,y-p.vy*.035),(x,y),3)
        pygame.draw.line(surf,OURO,(x-3,y-4),(x+4,y+4),1)
    for trama in e.tramas:
        faixa = trama.faixa.move(-cx,-cy)
        tom = FIO if trama.tempo > .55 else TEAL
        for n in range(4):
            x = faixa.left + n*14
            pygame.draw.line(surf,tom,(x,faixa.top),(x+14,faixa.bottom),1)
            pygame.draw.line(surf,tom,(x,faixa.bottom),(x+14,faixa.top),1)
        pygame.draw.line(surf,tom,faixa.topleft,faixa.topright,1)
        pygame.draw.line(surf,tom,faixa.bottomleft,faixa.bottomright,1)
    _mira(surf,e,cx,cy)
