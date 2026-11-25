"""Tipografia, imagens e pequenos sinais compartilhados pelas telas."""
from functools import lru_cache
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import pygame

RAIZ = Path(__file__).resolve().parents[1]
ARTE = RAIZ / "assets" / "arte"
OSSO = (232, 231, 210)
PALIDO = (176, 197, 184)
AMBAR = (241, 183, 101)
TINTA = (10, 18, 23)
TEAL = (104, 139, 132)
PERIGO = (245, 154, 122)
ROMANOS = ("I", "II", "III", "IV")
_leitura = ContextVar("leitura", default=(100, False, False, None))


@contextmanager
def estilo(preferencias, controles=None):
    estado = (preferencias.get("texto",100), preferencias.get("contraste",False),
              preferencias.get("claroes_suaves",False), controles)
    anterior = _leitura.set(estado)
    try:
        yield
    finally:
        _leitura.reset(anterior)


def tamanho_texto(tam):
    return round(tam*_leitura.get()[0]/100) if tam <= 22 else tam


def alto_contraste():
    return _leitura.get()[1]


def claroes_suaves():
    return _leitura.get()[2]


def dica_teclado(msg):
    controles = _leitura.get()[3]
    return controles.dicas(msg) if controles is not None else msg


@lru_cache(maxsize=48)
def fonte(tamanho, estilo="normal"):
    arquivo = {"titulo":"LiberationSerif-Regular.ttf", "forte":"Nunito-Bold.ttf",
               "normal":"Nunito-Regular.ttf"}[estilo]
    return pygame.font.Font(RAIZ / "assets" / "fontes" / arquivo, tamanho)


@lru_cache(maxsize=384)
def tinta(msg, tamanho, cor, estilo):
    return fonte(tamanho, estilo).render(msg, True, cor)


def texto(surf, msg, x, y, tam=17, cor=OSSO, estilo="normal", alinhar="left"):
    if alto_contraste():
        cor = tuple(round(c*.76 + 61) for c in cor)
    im = tinta(str(msg), tamanho_texto(tam), cor, estilo)
    rect = im.get_rect(top=y)
    setattr(rect, alinhar, x)
    surf.blit(im, rect)
    return rect


def linhas(msg, largura, tam=17, estilo="normal"):
    f = fonte(tamanho_texto(tam), estilo)
    linha = ""
    out = []
    for palavra in msg.split():
        tentativa = (linha + " " + palavra).strip()
        if linha and f.size(tentativa)[0] > largura:
            out.append(linha)
            linha = palavra
        else:
            linha = tentativa
    if linha:
        out.append(linha)
    return out


def paragrafo(surf, msg, x, y, largura, tam=17, cor=OSSO, estilo="normal", entre=None):
    for linha in linhas(msg, largura, tam, estilo):
        texto(surf, linha, x, y, tam, cor, estilo)
        y += entre or (tamanho_texto(tam) + 5)
    return y


@lru_cache(maxsize=150)
def original(nome):
    path = ARTE / nome
    im = pygame.image.load(str(path))
    return im.convert_alpha() if path.suffix == ".png" else im.convert()


@lru_cache(maxsize=600)
def imagem(nome, largura, altura, espelho=False):
    im = pygame.transform.smoothscale(original(nome), (max(1, largura), max(1, altura)))
    return pygame.transform.flip(im, True, False) if espelho else im


def sprite(surf, nome, x, pe, largura, altura, espelho=False):
    im = imagem(nome + ".png", int(largura), int(altura), espelho)
    r = im.get_rect(midbottom=(round(x), round(pe)))
    surf.blit(im, r)
    return r


def manivela(surf, x, pe, largura, altura, girada):
    sprite(surf, "obj_valvula", x, pe, largura, altura)
    eixo = round(x), round(pe - altura * .61)
    lado = 1 if girada else -1
    pino = eixo[0] + lado * round(largura * .27), eixo[1] + lado * round(altura * .17)
    pygame.draw.line(surf, TINTA, eixo, pino, 5)
    pygame.draw.line(surf, AMBAR, eixo, pino, 2)
    pygame.draw.circle(surf, OSSO, pino, 3)


def losango(surf, x, y, r=4, cor=AMBAR, cheio=True):
    pts = ((x,y-r),(x+r,y),(x,y+r),(x-r,y))
    pygame.draw.polygon(surf, cor, pts, 0 if cheio else 1 + int(alto_contraste()))


@lru_cache(maxsize=90)
def placa(w, h, opacidade=213):
    out = pygame.Surface((w,h), pygame.SRCALPHA)
    out.fill((*TINTA,opacidade))
    return out


def painel(surf, r, friso=True):
    r = pygame.Rect(r)
    surf.blit(placa(r.w,r.h,249 if alto_contraste() else 213),r)
    if friso:
        pygame.draw.line(surf, TEAL, r.topleft,(r.right-1,r.top))
        pygame.draw.line(surf, (53,72,70), r.bottomleft,(r.right-1,r.bottom))
        losango(surf,r.left+2,r.top,3)


@lru_cache(maxsize=40)
def halo(raio):
    im = pygame.Surface((raio*2,raio*2), pygame.SRCALPHA)
    for r in range(raio,0,-2):
        f = 1-r/raio
        pygame.draw.circle(im,(250,177,88,int(65*f*f)),(raio,raio),r)
    return im


def brilho(surf, xy, raio):
    surf.blit(halo(raio),(int(xy[0])-raio,int(xy[1])-raio))
