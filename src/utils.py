"""utils.py — funções pequenas usadas em todo o jogo (matemática, texto, desenho)."""

from __future__ import annotations

import math
import random

import pygame


# --------------------------------------------------------------------------
# Matemática
# --------------------------------------------------------------------------
def clamp(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp(t, 0.0, 1.0)


def suavizar(t: float) -> float:
    """Curva suave (smoothstep) para animações de entrada e saída."""
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def aproximar(valor: float, alvo: float, passo: float) -> float:
    """Move 'valor' em direção a 'alvo' sem passar dele."""
    if valor < alvo:
        return min(valor + passo, alvo)
    return max(valor - passo, alvo)


def distancia(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def normalizar(x: float, y: float) -> tuple[float, float]:
    comprimento = math.hypot(x, y)
    if comprimento < 1e-6:
        return 0.0, 0.0
    return x / comprimento, y / comprimento


def formatar_tempo(segundos: float) -> str:
    """450 -> '07:30'."""
    segundos = max(0, int(segundos))
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


def chance(probabilidade: float) -> bool:
    return random.random() < probabilidade


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------
_cache_texto: dict = {}


def texto(fonte, conteudo: str, cor, *, sombra=None, sombra_offset=2):
    """
    Renderiza texto com cache. Repetir a mesma frase todo frame é caro;
    aqui cada combinação é renderizada uma vez só.
    """
    chave = (id(fonte), conteudo, tuple(cor), tuple(sombra) if sombra else None)
    if chave in _cache_texto:
        return _cache_texto[chave]

    imagem = fonte.render(conteudo, True, cor)
    if sombra:
        fundo = fonte.render(conteudo, True, sombra)
        juntar = pygame.Surface(
            (imagem.get_width() + sombra_offset, imagem.get_height() + sombra_offset),
            pygame.SRCALPHA,
        )
        juntar.blit(fundo, (sombra_offset, sombra_offset))
        juntar.blit(imagem, (0, 0))
        imagem = juntar

    # limite simples para não crescer sem fim (ex.: pontuação mudando)
    if len(_cache_texto) > 600:
        _cache_texto.clear()
    _cache_texto[chave] = imagem
    return imagem


def desenhar_texto(tela, fonte, conteudo, cor, pos, *, centralizar=False,
                   direita=False, sombra=None, sombra_offset=2):
    imagem = texto(fonte, conteudo, cor, sombra=sombra, sombra_offset=sombra_offset)
    ret = imagem.get_rect()
    ret.topleft = pos
    if centralizar:
        ret.midtop = pos
    if direita:
        ret.topright = pos
    tela.blit(imagem, ret)
    return ret


def texto_centrado(tela, fonte, conteudo: str, cor, centro_x: int, y: int,
                   sombra=None, offset: int = 2, alpha: int = 255):
    """
    Texto centralizado usando a largura REAL do glifo.
    (render() inclui o avanço do último caractere, o que desloca o centro.)
    """
    largura, _altura = fonte.size(conteudo)
    x = int(centro_x - largura / 2)
    if sombra:
        imagem_sombra = fonte.render(conteudo, True, sombra)
        if alpha < 255:
            imagem_sombra.set_alpha(alpha)
        tela.blit(imagem_sombra, (x + offset, y + offset))
    imagem = texto(fonte, conteudo, cor)
    if alpha < 255:
        imagem = imagem.copy()
        imagem.set_alpha(alpha)
    tela.blit(imagem, (x, y))
    return pygame.Rect(x, y, largura, _altura)


def texto_direita(tela, fonte, conteudo: str, cor, direita_x: int, y: int,
                  sombra=None, offset: int = 2):
    """Texto alinhado à direita pela borda real do glifo."""
    largura, _altura = fonte.size(conteudo)
    x = int(direita_x - largura)
    if sombra:
        tela.blit(fonte.render(conteudo, True, sombra), (x + offset, y + offset))
    tela.blit(texto(fonte, conteudo, cor), (x, y))
    return pygame.Rect(x, y, largura, _altura)


def quebrar_texto(fonte, conteudo: str, largura_max: int) -> list[str]:
    """Quebra um parágrafo em linhas que cabem em 'largura_max' pixels."""
    linhas: list[str] = []
    for paragrafo in conteudo.split("\n"):
        atual = ""
        for palavra in paragrafo.split(" "):
            teste = f"{atual} {palavra}".strip()
            if fonte.size(teste)[0] <= largura_max or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


# --------------------------------------------------------------------------
# Superfícies
# --------------------------------------------------------------------------
def gradiente_radial(raio: int, cor, alpha_centro: int, alpha_borda: int,
                     potencia: float = 2.0) -> pygame.Surface:
    """
    Círculo com alpha decrescente do centro para a borda.
    Usado para a máscara de escuridão e para o brilho do vaga-lume.
    """
    raio = max(1, int(raio))
    tam = raio * 2
    surf = pygame.Surface((tam, tam), pygame.SRCALPHA)
    passos = max(8, raio // 3)
    for i in range(passos, 0, -1):
        t = i / passos
        alpha = int(lerp(alpha_centro, alpha_borda, t ** potencia))
        r = max(1, int(raio * t))
        pygame.draw.circle(surf, (*cor, alpha), (raio, raio), r)
    return surf


def superficie_ruido(tamanho: tuple[int, int], cor, alpha: int,
                     quantidade: int, semente: int = 1) -> pygame.Surface:
    """Textura leve de pontos, para o chão não ficar chapado."""
    sorteio = random.Random(semente)
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    for _ in range(quantidade):
        x = sorteio.randrange(tamanho[0])
        y = sorteio.randrange(tamanho[1])
        a = sorteio.randint(alpha // 3, alpha)
        pygame.draw.circle(surf, (*cor, a), (x, y), sorteio.choice((1, 1, 1, 2)))
    return surf


def escurecer(cor, fator: float):
    return tuple(int(clamp(c * fator, 0, 255)) for c in cor)


def clarear(cor, quanto: float):
    return tuple(int(clamp(c + (255 - c) * quanto, 0, 255)) for c in cor)


def misturar(cor_a, cor_b, t: float):
    return tuple(int(lerp(a, b, t)) for a, b in zip(cor_a, cor_b))


def desenhar_painel(tela, ret: pygame.Rect, cor_fundo, cor_borda,
                    raio: int = 14, alpha: int = 235, borda: int = 2):
    """Retângulo arredondado translúcido — base de menus e HUD."""
    painel = pygame.Surface(ret.size, pygame.SRCALPHA)
    pygame.draw.rect(painel, (*cor_fundo, alpha), painel.get_rect(), border_radius=raio)
    pygame.draw.rect(painel, (*cor_borda, min(255, alpha + 20)), painel.get_rect(),
                     width=borda, border_radius=raio)
    tela.blit(painel, ret.topleft)


def barra(tela, ret: pygame.Rect, valor: float, cor, cor_fundo,
          raio: int = 6, brilho=None):
    """Barra de progresso com valor de 0 a 1."""
    pygame.draw.rect(tela, cor_fundo, ret, border_radius=raio)
    largura = int(ret.width * clamp(valor, 0, 1))
    if largura > 2:
        cheia = pygame.Rect(ret.x, ret.y, largura, ret.height)
        pygame.draw.rect(tela, cor, cheia, border_radius=raio)
        if brilho:
            topo = pygame.Rect(ret.x, ret.y + 1, largura, max(2, ret.height // 3))
            pygame.draw.rect(tela, brilho, topo, border_radius=raio)
    pygame.draw.rect(tela, (*cor_fundo, 200), ret, width=1, border_radius=raio)
