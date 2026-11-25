"""
historia.py — roteiro e arte das cutscenes do Miopia.

A história foi escrita para amarrar a MECÂNICA à ficção:

  · a colônia vive na figueira velha e cada vaga-lume carrega uma luz dela;
  · o "clarão" da tempestade apagou as luzes e acordou o **Breu**, uma sombra
    antiga que dorme na gruta e se alimenta de luz;
  · Lume, o mais míope, escapou por ser fraco: o Breu não o notou;
  · os inimigos são consequência disso (morcegos caçam o brilho, aranhas tecem
    teias que apagam, sombras são pedaços do Breu, a Coruja é a guardiã cega);
  · o clarão do jogador atordoa a Coruja porque foi o mesmo clarão que a cegou.

Toda a arte é desenhada em código (pygame.draw) — nenhum asset de terceiro.
Cada cena recebe (superfície, tempo) e desenha em 960x600.
"""

from __future__ import annotations

import math
import random

import pygame

from . import config
from . import utils

# ========================================================================= #
# Roteiro (linguagem simples, com falante em cada fala)
#
# Regras do mundo — curtas o bastante para caber na cabeça de quem joga:
#   1. A figueira velha é a casa dos vaga-lumes (a Colônia da Figueira).
#   2. De noite eles bebem orvalho e levam luz para a raiz. É essa luz que
#      mantém a figueira acesa.
#   3. Embaixo da raiz dorme o BREU: uma sombra antiga que come luz.
#   4. Um raio caiu na figueira e o Breu acordou. Ele bebeu a luz da colônia.
#   5. O Breu não sai de baixo da raiz. Ele manda sombras e escuro.
#   6. Ele só pega quem brilha muito. Lume é o menor e o mais fraco: sobrou.
#   7. Lume tem três fagulhas da colônia. São as três vidas.
#   8. O caminho de volta segue a raiz. Cada trecho tem uma porteira de
#      raízes, que só abre quando sente orvalho.
#   9. Quando o sol nasce, o orvalho seca. Se a raiz não receber orvalho até
#      lá, a figueira não acende mais.
#  10. Morcegos bebiam das lâmpadas; aranhas sentem a luz nas teias; sombras
#      são pedaços do Breu e só têm coragem no escuro. A Coruja era a guardiã
#      da figueira: o raio cegou os olhos dela, e agora ela caça pelo som.
#      O clarão ainda dói nos olhos dela — por isso ela recua.
# ========================================================================= #
INTRO = [
    {
        "arte": "tempestade",
        "trilha": "historia",
        "local": "Mata Atlântica · a noite da tempestade",
        "falas": [
            ("Narrador", "Esta é a noite da tempestade."),
            ("Narrador", "Um raio caiu na figueira velha e apagou as luzes da colônia."),
            ("Narrador", "Debaixo da raiz, alguma coisa acordou."),
        ],
    },
    {
        "arte": "colonia",
        "trilha": "historia",
        "local": "Colônia da Figueira · antes do raio",
        "falas": [
            ("Narrador", "A figueira velha é a casa dos vaga-lumes."),
            ("Narrador", "Toda noite eles bebem orvalho e levam luz para a raiz. É isso que mantém a árvore acesa."),
            ("Breu", "A luz é minha."),
            ("Narrador", "O Breu, a sombra que dormia sob a raiz, bebeu a luz toda."),
        ],
    },
    {
        "arte": "acordar",
        "trilha": "historia",
        "local": "Bosque das Samambaias · longe de casa",
        "falas": [
            ("Lume", "Oi? Cadê todo mundo?"),
            ("Narrador", "Este é o Lume. Ele é o menor vaga-lume da colônia — e o mais míope: só enxerga o que a própria luz alcança."),
            ("Narrador", "O Breu não o viu. Sobraram três fagulhas: as três vidas dele."),
            ("Lume", "Preciso chegar na figueira antes do sol nascer. Quando o sol nasce, o orvalho seca — e a árvore não acende mais."),
            ("Narrador", "Ande com WASD. Aperte Espaço para dar um clarão: ele gasta luz, mas afasta o escuro."),
        ],
    },
]

BIOMAS = {
    0: {
        "arte": "bosque",
        "trilha": "bosque",
        "local": "Fase 1 · Clareira — Bosque das Samambaias",
        "falas": [
            ("Narrador", "O bosque é o berçário da colônia. As samambaias estão cheias de orvalho."),
            ("Lume", "Morcegos! Eles bebiam das lâmpadas. Agora vêm atrás da minha luz."),
            ("Narrador", "Junte orvalho para abrir a porteira de raízes e siga a raiz até a figueira."),
        ],
    },
    1: {
        "arte": "corrego",
        "trilha": "corrego",
        "local": "Fase 2 · Trilha interrompida — Córrego Fundo",
        "falas": [
            ("Narrador", "O córrego é a água da colônia. Agora as aranhas tecem teias de margem a margem."),
            ("Lume", "Elas não enxergam. Sentem a luz tremendo na teia."),
            ("Narrador", "Elas correm em linha reta. Desvie das teias — não precisa apagar a luz."),
        ],
    },
    2: {
        "arte": "taquaral",
        "trilha": "taquaral",
        "local": "Fase 3 · Borda da floresta — Taquaral",
        "falas": [
            ("Narrador", "O Breu não sai de baixo da raiz. Mas manda pedaços de si: as sombras."),
            ("Lume", "Quanto mais escuro, mais elas crescem."),
            ("Narrador", "Fique com a luz alta e elas recuam. Siga os bambus até a gruta."),
        ],
    },
    3: {
        "arte": "gruta",
        "trilha": "gruta",
        "local": "Fase 4 · Último refúgio — Gruta da Figueira",
        "falas": [
            ("Narrador", "A raiz da figueira desce até aqui. O Breu está no fundo, com a luz que roubou."),
            ("Lume", "Tem alguém na entrada... É a Coruja! Ela tomava conta da colônia."),
            ("Narrador", "O raio cegou os olhos dela. Ela caça pelo som: correr faz barulho, andar devagar não."),
            ("Coruja", "Quem está aí? Eu ouço você."),
            ("Narrador", "O clarão dói nos olhos dela. Use perto dela para assustar e recuar — e para acalmá-la de vez."),
        ],
    },
}

FINAIS = {
    "vitoria": {
        "arte": "amanhecer",
        "trilha": "vitoria",
        "local": "Amanhecer · Colônia da Figueira",
        "falas": [
            ("Narrador", "O orvalho desceu pela raiz. O tronco rachado acendeu por dentro."),
            ("Coruja", "A luz voltou."),
            ("Lume", "Eu consegui. A colônia está acesa."),
            ("Narrador", "O Breu voltou para baixo da raiz, com fome. Mas a figueira está viva outra vez."),
            ("Narrador", "O Lume continua míope. Agora, porém, enxerga a colônia inteira ao redor dele."),
        ],
    },
    "derrota": {
        "arte": "noite_eterna",
        "trilha": "derrota",
        "local": "Amanhecer · mata sem colônia",
        "falas": [
            ("Narrador", "O sol nasceu e o orvalho secou antes de chegar à raiz."),
            ("Narrador", "A figueira não acendeu. A mata ficou sem o caminho de volta."),
            ("Lume", "Amanhã eu tento de novo."),
        ],
    },
}

# Modo infinito: o Breu sonha, e enquanto ele sonha a noite não acaba.
INFINITO = [
    {
        "arte": "sonho",
        "trilha": "gruta",
        "local": "A noite que não acaba",
        "falas": [
            ("Narrador", "O Breu dormiu com a luz que roubou. E sonhou."),
            ("Breu", "Fica. A noite é minha."),
            ("Narrador", "No sonho, a mata se refaz a cada fase e o sol nunca nasce."),
            ("Narrador", "Vá o quanto aguentar. A cada fase o sonho aperta: mais bicho, menos fôlego."),
        ],
    },
]


# ========================================================================= #
# Ferramentas de desenho
# ========================================================================= #
def _gradiente(surf: pygame.Surface, topo, base, altura: int | None = None) -> None:
    altura = altura or surf.get_height()
    for y in range(altura):
        t = y / max(1, altura - 1)
        cor = tuple(int(utils.lerp(a, b, t)) for a, b in zip(topo, base))
        pygame.draw.line(surf, cor, (0, y), (surf.get_width(), y))


def _brilho(surf, x, y, raio: float, cor, intensidade: float = 1.0) -> None:
    """
    Halo radial suave.

    Atenção: BLEND_RGB_ADD ignora o canal alpha — quem define a intensidade é
    a própria COR. Antes as camadas eram desenhadas com (*cor, alpha), então
    todas somavam a cor cheia e o halo virava um disco chapado (a "lua" que
    aparecia no lugar da colônia). Aqui a cor já vai multiplicada pela queda.
    """
    raio = max(2, int(raio))
    halo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    camadas = 16
    for i in range(camadas, 0, -1):
        t = i / camadas
        queda = (1 - t) ** 2.4 * intensidade * 0.62
        if queda <= 0.004:
            continue
        cor_camada = tuple(min(255, int(canal * queda)) for canal in cor)
        pygame.draw.circle(halo, cor_camada, (raio, raio), max(1, int(raio * t)))
    surf.blit(halo, (x - raio, y - raio), special_flags=pygame.BLEND_RGB_ADD)


def _arvores(surf, base_y: int, cor, semente: int, escala: float = 1.0,
             balanco: float = 0.0) -> None:
    sorteio = random.Random(semente)
    x = -60
    while x < surf.get_width() + 80:
        altura = sorteio.randint(120, 260) * escala
        largura = sorteio.randint(90, 190) * escala
        inclina = math.sin(balanco + x * 0.01) * 8 * escala
        pygame.draw.rect(surf, utils.escurecer(cor, 0.85),
                         (x + largura * 0.42 + inclina, base_y - altura * 0.55,
                          max(6, int(10 * escala)), altura * 0.6))
        for i in range(3):
            raio = largura * (0.55 - i * 0.1)
            pygame.draw.ellipse(
                surf, cor,
                (x + inclina - raio * 0.2, base_y - altura + i * altura * 0.14,
                 raio * 1.9, raio * 1.2),
            )
        x += largura * 0.85


def _capim(surf, base_y: int, cor, semente: int, altura: float = 90,
           balanco: float = 0.0) -> None:
    sorteio = random.Random(semente)
    for _ in range(46):
        x = sorteio.randrange(-20, surf.get_width() + 20)
        h = sorteio.uniform(altura * 0.45, altura)
        curva = math.sin(balanco * 1.6 + x * 0.02) * h * 0.35
        pygame.draw.line(surf, cor, (x, base_y), (x + curva, base_y - h),
                         max(2, int(3 + h / 60)))


def _chuva(surf, tempo: float, quantidade: int = 130, cor=(150, 190, 255)) -> None:
    sorteio = random.Random(11)
    for _ in range(quantidade):
        x = sorteio.randrange(-40, surf.get_width() + 40)
        fase = sorteio.uniform(0, 1)
        velocidade = sorteio.uniform(700, 1100)
        y = (fase * surf.get_height() + tempo * velocidade) % (surf.get_height() + 80) - 40
        comprimento = sorteio.uniform(10, 22)
        pygame.draw.line(surf, (*cor, 60), (x, y), (x - 3, y + comprimento), 1)


def _estrelas(surf, semente: int, brilho: float = 1.0, quantidade: int = 90) -> None:
    sorteio = random.Random(semente)
    for _ in range(quantidade):
        x = sorteio.randrange(0, surf.get_width())
        y = sorteio.randrange(0, int(surf.get_height() * 0.6))
        raio = sorteio.choice((1, 1, 1, 2))
        alpha = int(sorteio.uniform(40, 170) * brilho)
        ponto = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(ponto, (220, 235, 255, alpha), (raio, raio), raio)
        surf.blit(ponto, (x, y))


def _luzes_colonia(surf, x: float, y: float, tempo: float, apagando: float = 0.0,
                   raio_espalhado: float = 90, quantidade: int = 26) -> None:
    """Pequenas luzes de vaga-lume agrupadas. 'apagando' vai de 0 a 1."""
    sorteio = random.Random(4)
    for i in range(quantidade):
        ang = sorteio.uniform(0, math.tau)
        dist = sorteio.uniform(0, raio_espalhado)
        px = x + math.cos(ang) * dist
        py = y + math.sin(ang) * dist * 0.6
        ordem = i / quantidade
        if apagando > ordem:
            continue
        pisca = 0.55 + 0.45 * math.sin(tempo * sorteio.uniform(1.5, 3.2) + i)
        _brilho(surf, px, py, sorteio.uniform(9, 18), config.LUZ, pisca * 0.9)
        pygame.draw.circle(surf, config.LUZ, (int(px), int(py)), 2)


def _vaga_lume(surf, x: float, y: float, escala: float, tempo: float,
               olhando: int = 1, alpha: int = 255) -> None:
    """O Lume em close (mesmo desenho do jogo, ampliado)."""
    camada = pygame.Surface((int(120 * escala), int(120 * escala)), pygame.SRCALPHA)
    cx, cy = camada.get_width() // 2, camada.get_height() // 2
    batida = math.sin(tempo * 24)

    cor = config.LUZ_QUENTE
    for lado in (-1, 1):
        largura = (16 + abs(batida) * 8) * escala
        asa = pygame.Surface((int(largura * 2), int(34 * escala)), pygame.SRCALPHA)
        pygame.draw.ellipse(asa, (*utils.escurecer(cor, 0.7), 150),
                            (0, 0, int(largura * 2), int(30 * escala)))
        girada = pygame.transform.rotate(asa, lado * (18 + batida * 20))
        camada.blit(girada, (cx - girada.get_width() // 2,
                             cy - girada.get_height() // 2 + 4))

    pygame.draw.ellipse(camada, utils.escurecer(cor, 0.4),
                        (cx - 9 * escala, cy - 10 * escala, 18 * escala, 24 * escala))
    pygame.draw.circle(camada, cor, (cx, cy - 10 * escala), int(8 * escala))
    pygame.draw.circle(camada, (250, 252, 255), (cx - 3 * escala, cy - 11 * escala),
                       max(2, int(3 * escala)))
    pygame.draw.circle(camada, (250, 252, 255), (cx + 3 * escala, cy - 11 * escala),
                       max(2, int(3 * escala)))
    pygame.draw.circle(camada, (30, 38, 54), (int(cx - 3 * escala + 1 * olhando),
                                              int(cy - 11 * escala)), max(1, int(escala)))
    pygame.draw.circle(camada, (30, 38, 54), (int(cx + 3 * escala + 1 * olhando),
                                              int(cy - 11 * escala)), max(1, int(escala)))
    _brilho(camada, cx, cy + int(8 * escala), 16 * escala, config.LUZ, 0.85)

    if alpha < 255:
        camada.set_alpha(alpha)
    surf.blit(camada, (x - camada.get_width() // 2, y - camada.get_height() // 2))


def _figueira(surf, x: float, base_y: float, escala: float, tempo: float,
              cor=(9, 13, 22)) -> None:
    """Figueira velha: tronco largo, raízes e copa redonda."""
    tronco = pygame.Rect(x - 26 * escala, base_y - 300 * escala,
                         52 * escala, 300 * escala)
    pygame.draw.rect(surf, cor, tronco, border_radius=int(12 * escala))
    for i, lado in enumerate((-1, 1)):
        pygame.draw.polygon(surf, cor, [
            (x + lado * 18 * escala, base_y - 6),
            (x + lado * 90 * escala, base_y + 14),
            (x + lado * 64 * escala, base_y - 30 * escala),
        ])
    # raízes aéreas
    for i in range(5):
        rx = x - 40 * escala + i * 20 * escala
        pygame.draw.line(surf, utils.escurecer(cor, 0.8),
                         (rx, base_y - 200 * escala),
                         (rx + math.sin(tempo + i) * 4, base_y - 60 * escala), 2)
    # copa
    for i in range(9):
        ang = i / 9 * math.tau
        cx = x + math.cos(ang) * 90 * escala
        cy = base_y - 300 * escala + math.sin(ang) * 40 * escala
        pygame.draw.ellipse(surf, cor, (cx - 90 * escala, cy - 60 * escala,
                                        180 * escala, 120 * escala))


def _coruja_silhueta(surf, x, y, escala, tempo, olhos: bool = True) -> None:
    cor = (16, 14, 26)
    pygame.draw.ellipse(surf, cor, (x - 22 * escala, y - 26 * escala,
                                    44 * escala, 54 * escala))
    for lado in (-1, 1):
        pygame.draw.polygon(surf, cor, [
            (x + lado * 8 * escala, y - 24 * escala),
            (x + lado * 20 * escala, y - 40 * escala),
            (x + lado * 18 * escala, y - 16 * escala),
        ])
        if olhos:
            brilho = 0.6 + 0.4 * math.sin(tempo * 2)
            pygame.draw.circle(surf, (*config.OURO, int(200 * brilho)),
                               (int(x + lado * 8 * escala), int(y - 12 * escala)),
                               max(2, int(4 * escala)))
    for lado in (-1, 1):
        pygame.draw.polygon(surf, utils.escurecer(cor, 0.85), [
            (x + lado * 6 * escala, y - 4 * escala),
            (x + lado * 34 * escala, y - 22 * escala),
            (x + lado * 30 * escala, y + 14 * escala),
            (x + lado * 12 * escala, y + 10 * escala),
        ])


# ========================================================================= #
# Cenas
# ========================================================================= #
def _vinheta(surf: pygame.Surface, forca: float = 0.75, raio_min: int = 150) -> None:
    """Escurece as bordas de verdade: anéis finos, alpha crescendo para fora."""
    vinheta = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    centro = (surf.get_width() // 2, surf.get_height() // 2)
    raio_max = int(math.hypot(*centro)) + 10
    passo = 10
    for raio in range(raio_max, raio_min, -passo):
        t = raio / raio_max
        alpha = int(190 * forca * max(0.0, (t - 0.45) / 0.55) ** 1.8)
        if alpha <= 0:
            continue
        pygame.draw.circle(vinheta, (0, 0, 0, alpha), centro, raio, width=passo + 1)
    surf.blit(vinheta, (0, 0))


def _teia(surf, cx: float, cy: float, raio: float, t: float) -> None:
    """
    Teia setorial (não uma mira): fios abertos em leque + arcos curtos,
    pendurada num galho. O leque é o que faz o olho ler "teia" e não "relógio".
    """
    cor = (78, 100, 120)
    inicio, fim = 0.38, 2.76            # leque apontando para BAIXO (y cresce)
    # galho de onde a teia pende
    pygame.draw.line(surf, (26, 34, 30), (cx - raio * 1.1, cy - raio * 0.22),
                     (cx + raio * 1.1, cy - raio * 0.16), 3)

    passos = 6
    for k in range(passos):
        ang = inicio + (fim - inicio) * k / (passos - 1)
        comp = raio * (0.82 + 0.18 * math.sin(t * 0.6 + k))
        pygame.draw.line(surf, cor, (cx, cy),
                         (cx + math.cos(ang) * comp, cy + math.sin(ang) * comp), 1)

    # draw.arc mede o ângulo no sentido anti-horário da tela (y para cima):
    # o leque de baixo corresponde a ângulos negativos.
    for fracao in (0.45, 0.72, 0.96):
        r = int(raio * fracao)
        caixa = pygame.Rect(int(cx - r), int(cy - r), r * 2, r * 2)
        pygame.draw.arc(surf, cor, caixa, -fim + 0.10, -inicio - 0.10, 1)

    # orvalho preso nos fios
    for ang in (0.9, 1.55, 2.2):
        px = cx + math.cos(ang) * raio * 0.86
        py = cy + math.sin(ang) * raio * 0.86
        _brilho(surf, px, py, 8, config.AGUA, 0.45)
        pygame.draw.circle(surf, config.AGUA, (int(px), int(py)), 1)


def cena_tempestade(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (8, 12, 24), (18, 26, 40))
    _estrelas(surf, 3, brilho=0.35, quantidade=40)

    # relâmpago a cada ~3,5 s
    ciclo = t % 3.5
    flash = 0.0
    if ciclo < 0.18:
        flash = 1 - ciclo / 0.18
    elif 0.3 < ciclo < 0.42:
        flash = 0.5
    if flash > 0:
        clarão = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        clarão.fill((180, 205, 255, int(120 * flash)))
        surf.blit(clarão, (0, 0))
        if ciclo < 0.18:
            pontos = [(620, 0), (600, 90), (640, 120), (590, 230), (630, 260), (560, 400)]
            pygame.draw.lines(surf, (225, 238, 255), False, pontos, 3)

    _arvores(surf, 470, (12, 18, 30), 21, escala=1.25, balanco=t)
    _arvores(surf, 520, (8, 13, 22), 8, escala=0.9, balanco=t * 1.4)

    # a colônia apagando ao fundo (a última luz some no fim da cena)
    apagando = utils.clamp((t - 2.5) / 3.5, 0.0, 0.95)
    _luzes_colonia(surf, 760, 300, t, apagando=apagando, raio_espalhado=64, quantidade=18)
    if apagando < 0.9:
        _brilho(surf, 760, 300, 90, config.LUZ, 0.25 * (1 - apagando))

    _chuva(surf, t, quantidade=150)
    _capim(surf, 600, (7, 11, 18), 5, altura=130, balanco=t)


def cena_colonia(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (10, 14, 28), (24, 22, 38))
    _estrelas(surf, 9, brilho=0.7, quantidade=70)

    _figueira(surf, 480, 520, 1.0, t, cor=(10, 13, 24))
    _brilho(surf, 480, 300, 220, config.LUZ, 0.35)
    _luzes_colonia(surf, 480, 300, t, apagando=0.0, raio_espalhado=120, quantidade=34)

    # Lume pequeno, no canto, olhando a colônia
    _vaga_lume(surf, 190, 430, 0.85, t, olhando=1)
    _brilho(surf, 190, 440, 60, config.LUZ, 0.5)

    _capim(surf, 600, (8, 12, 20), 12, altura=110, balanco=t * 0.8)


def cena_acordar(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (7, 10, 18), (14, 20, 30))

    # chão em close: folhas gigantes
    for i in range(7):
        x = 90 + i * 150
        balanco = math.sin(t * 0.9 + i) * 10
        pygame.draw.ellipse(surf, (10, 18, 24),
                            (x - 120 + balanco, 300 + i % 3 * 30, 260, 420))
    _capim(surf, 620, (9, 16, 22), 31, altura=220, balanco=t * 1.2)

    # gotas de orvalho brilhando (o tutorial visual do jogo)
    for i, (x, y) in enumerate(((250, 420), (420, 360), (640, 430), (760, 330))):
        pisca = 0.5 + 0.5 * math.sin(t * 2 + i)
        _brilho(surf, x, y, 26, config.AGUA, 0.55 + 0.4 * pisca)
        pygame.draw.circle(surf, config.AGUA, (x, y), 4)
        pygame.draw.circle(surf, (255, 255, 255), (x - 1, y - 1), 1)

    # Lume no chão, óculos tortos
    flutua = math.sin(t * 2.2) * 4
    _vaga_lume(surf, 480, 470 + flutua, 1.5, t, olhando=1)
    _brilho(surf, 480, 480 + flutua, 190, config.LUZ, 0.55)

    # penumbra nas bordas (é assim que ele vê o mundo)
    _vinheta(surf, forca=0.92)


def cena_bosque(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (8, 14, 20), (13, 24, 26))
    _arvores(surf, 460, (11, 22, 24), 4, escala=1.1, balanco=t * 0.7)
    _arvores(surf, 520, (8, 17, 20), 77, escala=0.8, balanco=t)
    for i in range(5):
        x = 140 + i * 170
        _brilho(surf, x, 330 + math.sin(t + i) * 8, 34, config.AGUA, 0.5)
        pygame.draw.circle(surf, config.AGUA, (x, int(330 + math.sin(t + i) * 8)), 3)
    _vaga_lume(surf, 380 + math.sin(t * 0.7) * 60, 380, 0.7, t, olhando=1)
    _capim(surf, 610, (8, 15, 15), 61, altura=120, balanco=t)


def cena_corrego(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (8, 12, 26), (12, 22, 34))
    _estrelas(surf, 17, brilho=0.5, quantidade=55)

    # lua cheia refletida na água: dá verticalidade à cena
    _brilho(surf, 764, 132, 150, (198, 214, 244), 0.45)
    pygame.draw.circle(surf, (222, 231, 248), (764, 132), 34)
    pygame.draw.circle(surf, (204, 216, 238), (754, 124), 7)

    # água
    pygame.draw.rect(surf, (9, 20, 32), (0, 400, surf.get_width(), 200))
    for i in range(26):
        y = 408 + i * 7
        deslocamento = math.sin(t * 0.8 + i * 0.4) * 12
        pygame.draw.line(surf, (20, 44, 62), (0 + deslocamento, y),
                         (surf.get_width(), y), 1)
    # reflexos
    for i in range(6):
        x = 120 + i * 150
        alpha = 0.25 + 0.15 * math.sin(t * 1.4 + i)
        _brilho(surf, x, 470 + math.sin(t + i) * 4, 40, config.AGUA, alpha)

    # margem: juncos e pedras
    _capim(surf, 402, (14, 24, 28), 9, altura=78, balanco=t * 0.8)
    for i, (px, py, r) in enumerate(((180, 396, 16), (205, 400, 11), (560, 398, 14))):
        pygame.draw.ellipse(surf, (18, 26, 34), (px, py - r, r * 2.2, r * 1.5))

    # teias penduradas entre os galhos (arcos parciais + orvalho)
    _teia(surf, 286, 300, 62, t)
    _teia(surf, 694, 268, 48, t * 0.8)

    _vaga_lume(surf, 480, 330 + math.sin(t) * 6, 0.75, t, olhando=1)


def cena_taquaral(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (10, 16, 18), (16, 22, 20))
    sorteio = random.Random(15)
    for camada in range(3):
        # camadas de trás para a frente: névoa no fundo, colmos escuros na frente
        escuro = 10 + camada * 5
        for _ in range(13):
            x = sorteio.randrange(-30, surf.get_width() + 30)
            h = sorteio.uniform(240, 520) * (0.8 + camada * 0.15)
            balanco = math.sin(t * 1.2 + x * 0.02) * (10 + camada * 4)
            grossura = 2 + camada
            cor = (escuro + 4, escuro + 12, escuro + 8)
            pontos = [(x, 600), (x + balanco * 0.5, 600 - h * 0.55), (x + balanco, 600 - h)]
            pygame.draw.lines(surf, cor, False, pontos, grossura)
            # nós do bambu
            for k in range(1, 5):
                yy = 600 - h * k / 5
                xx = x + balanco * (k / 5) ** 1.5
                pygame.draw.line(surf, (cor[0] + 8, cor[1] + 12, cor[2] + 8),
                                 (xx - 4, yy), (xx + 4, yy), 2)
            # folhas
            for k in range(2):
                yy = 600 - h * (0.55 + k * 0.18)
                xx = x + balanco * 0.7
                pygame.draw.polygon(surf, (cor[0] + 6, cor[1] + 16, cor[2] + 10), [
                    (xx, yy), (xx + 30, yy - 14), (xx + 22, yy - 2)])

    # sombras no chão
    for i in range(5):
        x = 90 + i * 200
        alpha = int(40 + 30 * math.sin(t * 2 + i))
        mancha = pygame.Surface((160, 70), pygame.SRCALPHA)
        pygame.draw.ellipse(mancha, (10, 6, 16, alpha), mancha.get_rect())
        surf.blit(mancha, (x, 470))
        for lado in (-1, 1):
            pygame.draw.circle(surf, (235, 235, 255), (x + 70 + lado * 6, 500), 1)

    _vaga_lume(surf, 480, 350 + math.sin(t * 0.9) * 8, 0.7, t, olhando=1)


def cena_gruta(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (6, 8, 16), (16, 12, 26))

    # estalactites e paredes
    sorteio = random.Random(23)
    for i in range(12):
        x = sorteio.randrange(-40, surf.get_width() + 40)
        altura = sorteio.randint(60, 190)
        pygame.draw.polygon(surf, (10, 9, 20), [(x, 0), (x + 60, 0), (x + 30, altura)])
    pygame.draw.rect(surf, (10, 9, 20), (0, 520, surf.get_width(), 80))

    # cristais
    for (x, y, s) in ((240, 470, 1.0), (700, 450, 0.8), (520, 500, 0.6)):
        pisca = 0.5 + 0.5 * math.sin(t * 1.7 + x)
        _brilho(surf, x, y, 44 * s, (150, 120, 255), 0.3 + 0.3 * pisca)
        pygame.draw.polygon(surf, (60, 46, 104), [
            (x, y - 26 * s), (x + 10 * s, y), (x, y + 12), (x - 10 * s, y)])

    # raízes da figueira descendo
    for i in range(6):
        rx = 120 + i * 130
        pygame.draw.line(surf, (14, 12, 24), (rx, 0), (rx + 30, 520), 5)

    # a Coruja no fundo, olhos acesos
    _coruja_silhueta(surf, 780, 250, 1.6, t)
    _brilho(surf, 780, 240, 70, config.OURO, 0.28)

    _vaga_lume(surf, 330, 400 + math.sin(t) * 6, 0.9, t, olhando=1)
    _brilho(surf, 330, 410, 120, config.LUZ, 0.45)


def cena_amanhecer(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (30, 30, 58), (206, 150, 120))
    # sol nascendo
    progresso = utils.clamp(t / 6, 0, 1)
    sol_y = 520 - progresso * 180
    _brilho(surf, 480, sol_y, 240, (255, 214, 160), 0.55)
    pygame.draw.circle(surf, (255, 226, 176), (480, int(sol_y)), 46)

    _arvores(surf, 500, (18, 20, 30), 5, escala=1.0, balanco=t * 0.4)
    _figueira(surf, 480, 520, 0.9, t, cor=(16, 18, 28))
    _luzes_colonia(surf, 480, 320, t, apagando=0.0, raio_espalhado=110, quantidade=30)
    _brilho(surf, 480, 320, 200, config.LUZ, 0.4)

    # Lume subindo até a colônia
    subida = utils.suavizar(utils.clamp(t / 5, 0, 1))
    _vaga_lume(surf, 480, 520 - subida * 170, 0.8, t, olhando=1)

    _capim(surf, 600, (22, 26, 30), 71, altura=100, balanco=t * 0.6)


def cena_noite_eterna(surf: pygame.Surface, t: float) -> None:
    _gradiente(surf, (6, 8, 14), (12, 14, 22))
    _estrelas(surf, 41, brilho=0.8, quantidade=110)
    _arvores(surf, 500, (8, 10, 16), 5, escala=1.0, balanco=t * 0.3)
    _figueira(surf, 480, 520, 0.9, t, cor=(9, 10, 18))

    # a colônia apagada: só um resto de luz pulsando
    resto = 0.25 * (0.5 + 0.5 * math.sin(t * 1.2))
    _luzes_colonia(surf, 480, 320, t, apagando=0.92, raio_espalhado=100, quantidade=26)
    _brilho(surf, 480, 320, 120, config.LUZ, resto)

    # Lume no chão, quase apagado
    _vaga_lume(surf, 480, 470, 0.6, t, olhando=1,
               alpha=int(120 + 90 * (0.5 + 0.5 * math.sin(t * 1.6))))
    _capim(surf, 610, (8, 10, 16), 71, altura=120, balanco=t * 0.4)
    _chuva(surf, t, quantidade=60, cor=(120, 150, 200))


def cena_sonho(surf: pygame.Surface, t: float) -> None:
    """O sonho do Breu: a mata se repetindo, sem amanhecer."""
    _gradiente(surf, (7, 6, 16), (16, 10, 24))
    _estrelas(surf, 63, brilho=0.45, quantidade=70)

    # várias figueiras iguais, cada vez menores: o sonho se repetindo
    for i, escala in enumerate((0.9, 0.62, 0.42, 0.28)):
        _figueira(surf, 480, 610 - i * 20, escala, t * (0.6 + i * 0.2),
                  cor=(10 + i * 3, 9 + i * 3, 20 + i * 3))

    # olhos do Breu abrindo devagar no fundo
    abertura = 0.55 + 0.45 * math.sin(t * 0.7)
    for lado in (-1, 1):
        ex, ey = 480 + lado * 74, 250
        _brilho(surf, ex, ey, 46, (150, 96, 210), 0.35 * abertura)
        pygame.draw.ellipse(surf, (196, 158, 255),
                            (ex - 16, ey - int(9 * abertura), 32, int(18 * abertura)))
        pygame.draw.ellipse(surf, (24, 12, 36),
                            (ex - 4, ey - int(7 * abertura), 9, int(14 * abertura)))

    # vaga-lumes presos no sonho, subindo e sumindo
    for i in range(9):
        fase = (t * (0.12 + i * 0.01) + i * 0.11) % 1.0
        px = 90 + (i * 97) % 780 + math.sin(t * 0.6 + i) * 22
        py = 560 - fase * 380
        alpha = int(200 * (1 - fase))
        _brilho(surf, px, py, 16, config.LUZ, 0.35 * (1 - fase))
        pygame.draw.circle(surf, (*config.LUZ, alpha), (int(px), int(py)), 2)

    _capim(surf, 600, (9, 8, 16), 44, altura=110, balanco=t * 0.5)


CENAS = {
    "sonho": cena_sonho,
    "tempestade": cena_tempestade,
    "colonia": cena_colonia,
    "acordar": cena_acordar,
    "bosque": cena_bosque,
    "corrego": cena_corrego,
    "taquaral": cena_taquaral,
    "gruta": cena_gruta,
    "amanhecer": cena_amanhecer,
    "noite_eterna": cena_noite_eterna,
}


def desenhar_cena(nome: str, surf: pygame.Surface, tempo: float) -> None:
    funcao = CENAS.get(nome)
    if funcao:
        funcao(surf, tempo)
    else:
        surf.fill(config.NOITE)
