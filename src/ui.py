"""
ui.py — sistema de interface do Miopia ("skill" de front end de jogo aplicada).

Por que este arquivo existe: antes, cada tela posicionava texto "na mão", e o
resultado era texto socado no rodapé das caixas (alinhamento pelo TOPO em vez
do centro) e botões com foco confuso. Aqui ficam as regras do design system,
num só lugar:

  1. ESCALA DE ESPAÇO   — múltiplos de 4: 4 · 8 · 12 · 16 · 24 · 32 · 48
  2. ESCALA DE TIPO     — display 96 · h1 56 · h2 34 · h3 24 · corpo 19 · micro 15
  3. CENTRO VERTICAL REAL — o texto é centrado pelos METRICS do glifo
     (ascent/descender), não pela altura da caixa de linha.
  4. FOCO VISÍVEL       — anel de 3 px FORA do botão + barra de acento;
     o preenchimento não muda de forma brusca.
  5. CONTRASTE          — todo texto sobre painel/scrim; nunca direto sobre
     cena clara ou escura. Paleta auditada por tools/checar_contraste.py.
  6. COR NUNCA SOZINHA  — estado crítico sempre tem forma/palavra junto.
  7. FEEDBACK < 100 ms  — hover/click respondem no mesmo quadro.

Regras de composição usadas nas telas:
  - margem segura de 48 px nas bordas;
  - coluna de leitura de no máximo ~72 caracteres;
  - botão com 52 px de altura e 24 px de padding lateral;
  - painel com 24–28 px de padding interno e cantos de 14 px.
"""

from __future__ import annotations

import pygame

from . import config
from . import utils

# --------------------------------------------------------------------------
# Tokens
# --------------------------------------------------------------------------
ESP = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32, "3xl": 48}
RAIO = {"sm": 8, "md": 12, "lg": 16, "pill": 999}
MARGEM = 48
ALTURA_BOTAO = 52
PADDING_PAINEL = 26
ENTRELINHA = 1.55

# cores de interface (todas validadas contra os fundos usados no jogo)
FUNDO_PAINEL = (12, 17, 28)
BORDA_PAINEL = (44, 60, 88)
BORDA_SUAVE = (30, 41, 60)
FUNDO_BOTAO = (17, 24, 39)
FUNDO_BOTAO_HOVER = (24, 34, 54)
FUNDO_BOTAO_FOCO = (26, 38, 62)
FUNDO_BOTAO_PRESSIONADO = (12, 18, 30)
ACENTO = config.AGUA
FOCO = config.LUZ_QUENTE
TEXTO = config.TEXTO
TEXTO_MEDIO = (170, 184, 210)
TEXTO_FRACO = (134, 149, 178)      # ≥ 4.5:1 sobre FUNDO_PAINEL
TEXTO_APAGADO = (110, 124, 152)    # só para legendas/botões desabilitados


# --------------------------------------------------------------------------
# Medidas de texto (a base de todo alinhamento correto)
# --------------------------------------------------------------------------
def altura_visual(fonte: pygame.font.Font, conteudo: str) -> tuple[int, int]:
    """
    Devolve (topo, base) do desenho do texto relativo ao topo da linha.
    Usa os metrics reais do glifo: 'Miopia' e 'ação' têm alturas diferentes.
    """
    if not conteudo:
        return 0, fonte.get_height()
    metrics = fonte.metrics(conteudo)
    validos = [m for m in metrics if m]
    if not validos:
        return 0, fonte.get_height()
    ascent = fonte.get_ascent()
    maxy = max(m[3] for m in validos)
    miny = min(m[2] for m in validos)
    return ascent - maxy, ascent - miny


def y_para_centro(fonte: pygame.font.Font, conteudo: str, centro_y: float) -> int:
    """Y ideal para que o TEXTO (não a caixa) fique centrado em centro_y."""
    topo, base = altura_visual(fonte, conteudo)
    return int(round(centro_y - (topo + base) / 2))


def largura(fonte: pygame.font.Font, conteudo: str) -> int:
    return fonte.size(conteudo)[0]


def cabe(fonte: pygame.font.Font, conteudo: str, largura_max: float) -> bool:
    return largura(fonte, conteudo) <= largura_max


def encolher_para_caber(fontes: list[pygame.font.Font], conteudo: str,
                        largura_max: float) -> pygame.font.Font:
    """Se o texto não cabe, usa a primeira fonte da lista que caiba."""
    for fonte in fontes:
        if cabe(fonte, conteudo, largura_max):
            return fonte
    return fontes[-1]


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------
def texto(tela, fonte, conteudo, cor, x, y, *, alinhamento="esq",
          vertical="topo", largura_max=None, sombra=None, alpha=255):
    """
    Desenha texto de uma linha com alinhamento explícito nos dois eixos.

    alinhamento: "esq" | "centro" | "dir"
    vertical:    "topo" | "meio" | "base"
    """
    if largura_max is not None:
        conteudo = encurtar(fonte, conteudo, largura_max)

    larg = largura(fonte, conteudo)
    if alinhamento == "centro":
        px = x - larg / 2
    elif alinhamento == "dir":
        px = x - larg
    else:
        px = x

    if vertical == "meio":
        py = y_para_centro(fonte, conteudo, y)
    elif vertical == "base":
        topo, base = altura_visual(fonte, conteudo)
        py = y - base
    else:
        py = y

    px, py = int(round(px)), int(round(py))

    if sombra is not None:
        imagem_sombra = utils.texto(fonte, conteudo, sombra)
        if alpha < 255:
            imagem_sombra = imagem_sombra.copy()
            imagem_sombra.set_alpha(alpha)
        tela.blit(imagem_sombra, (px + 2, py + 2))

    imagem = utils.texto(fonte, conteudo, cor)
    if alpha < 255:
        imagem = imagem.copy()
        imagem.set_alpha(alpha)
    tela.blit(imagem, (px, py))
    return pygame.Rect(px, py, larg, fonte.get_height())


def encurtar(fonte, conteudo: str, largura_max: float) -> str:
    """Corta com reticências se não couber (evita texto invadindo a caixa)."""
    if largura(fonte, conteudo) <= largura_max:
        return conteudo
    reticencias = "…"
    corte = conteudo
    while corte and largura(fonte, corte + reticencias) > largura_max:
        corte = corte[:-1]
    return corte.rstrip() + reticencias


def bloco(tela, fonte, texto_longo: str, caixa: pygame.Rect, cor,
          *, alinhamento="esq", entrelinha=ENTRELINHA, centralizar_vertical=True,
          sombra=None):
    """
    Desenha um parágrafo com quebra automática DENTRO de uma caixa,
    com entrelinha e (por padrão) centragem vertical ótima.

    Retorna a altura usada. É essa função que corrige o "texto socado
    no rodapé": o bloco inteiro é medido antes de ser posicionado.
    """
    linhas = utils.quebrar_texto(fonte, texto_longo, caixa.width)
    linha_altura = int(fonte.get_linesize() * entrelinha)
    altura_total = linha_altura * len(linhas)

    if centralizar_vertical:
        y = caixa.y + (caixa.height - altura_total) // 2
    else:
        y = caixa.y

    for linha in linhas:
        if alinhamento == "centro":
            x = caixa.centerx
        elif alinhamento == "dir":
            x = caixa.right
        else:
            x = caixa.x
        texto(tela, fonte, linha, cor, x, y, alinhamento=alinhamento, sombra=sombra)
        y += linha_altura

    return altura_total


# --------------------------------------------------------------------------
# Superfícies
# --------------------------------------------------------------------------
def painel(tela, caixa: pygame.Rect, *, fundo=FUNDO_PAINEL, borda=BORDA_PAINEL,
           raio=RAIO["lg"], alpha=242, espessura=1, brilho_topo=False):
    """Retângulo arredondado com borda — a base de toda caixa do jogo."""
    superficie = pygame.Surface(caixa.size, pygame.SRCALPHA)
    pygame.draw.rect(superficie, (*fundo, alpha), superficie.get_rect(), border_radius=raio)
    if brilho_topo:
        pygame.draw.rect(superficie, (*utils.clarear(fundo, 0.06), alpha),
                         (0, 0, caixa.width, 1), border_radius=raio)
    pygame.draw.rect(superficie, (*borda, min(255, alpha + 10)), superficie.get_rect(),
                     width=espessura, border_radius=raio)
    tela.blit(superficie, caixa.topleft)


def scrim(tela, alpha=170, cor=(5, 8, 14)):
    """Véu sobre a cena: garante contraste do texto sobre qualquer fundo."""
    veu = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
    veu.fill((*cor, alpha))
    tela.blit(veu, (0, 0))


def barra_progresso(tela, caixa: pygame.Rect, valor: float, *, cor,
                    fundo=(28, 36, 52), raio=RAIO["sm"], marcas=0):
    pygame.draw.rect(tela, fundo, caixa, border_radius=raio)
    largura_cheia = int(caixa.width * utils.clamp(valor, 0, 1))
    if largura_cheia > 2:
        pygame.draw.rect(tela, cor, (caixa.x, caixa.y, largura_cheia, caixa.height),
                         border_radius=raio)
        pygame.draw.rect(tela, utils.clarear(cor, 0.3),
                         (caixa.x + 1, caixa.y + 1, max(0, largura_cheia - 2),
                          max(2, caixa.height // 3)), border_radius=raio)
    if marcas:
        for i in range(1, marcas):
            x = caixa.x + caixa.width * i / marcas
            pygame.draw.line(tela, (*fundo, 255), (x, caixa.y + 3), (x, caixa.bottom - 4), 2)
    pygame.draw.rect(tela, utils.escurecer(fundo, 0.7), caixa, width=1, border_radius=raio)


# --------------------------------------------------------------------------
# Botão
# --------------------------------------------------------------------------
class Botao:
    """
    Botão com os quatro estados desenhados de propósito:
      normal · hover (mouse) · foco (teclado) · pressionado

    O foco é um ANEL EXTERNO + barra de acento à esquerda: o preenchimento
    não "acende" inteiro, o que antes deixava o botão parecendo selecionado
    para sempre. Teclado e mouse compartilham o mesmo estado visual.
    """

    def __init__(self, rotulo: str, acao, largura_min: int = 280,
                 icone: str | None = None, centralizar: bool = False) -> None:
        self.rotulo = rotulo
        self.centralizar = centralizar
        self.acao = acao
        self.icone = icone
        self.largura_min = largura_min
        self.ret = pygame.Rect(0, 0, largura_min, ALTURA_BOTAO)
        self.foco = False
        self.hover = False
        self.pressionado = False
        self.desabilitado = False
        self._pulso = 0.0

    # ------------------------------------------------------------------ #
    def atualizar(self, dt: float) -> None:
        alvo = 1.0 if (self.foco or self.hover) else 0.0
        self._pulso = utils.aproximar(self._pulso, alvo, dt * 8)

    def medir(self, fonte) -> None:
        """Ajusta a largura ao conteúdo (com folga para o anel de foco)."""
        self.ret.width = max(self.largura_min, largura(fonte, self.rotulo) + 96)

    # ------------------------------------------------------------------ #
    def tratar_mouse(self, pos, clicou=False) -> bool:
        self.hover = self.ret.collidepoint(pos)
        if clicou and self.hover and not self.desabilitado:
            return True
        return False

    def desenhar(self, tela, fonte, *, x=None, y=None) -> None:
        if x is not None:
            self.ret.x = x
        if y is not None:
            self.ret.y = y

        base = FUNDO_BOTAO
        if self.desabilitado:
            base = (14, 19, 30)
        elif self.pressionado:
            base = FUNDO_BOTAO_PRESSIONADO
        elif self.foco:
            base = FUNDO_BOTAO_FOCO
        elif self.hover:
            base = FUNDO_BOTAO_HOVER

        # sombra curta (profundidade sem sujar)
        sombra = pygame.Surface(self.ret.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 90), sombra.get_rect(), border_radius=RAIO["md"])
        tela.blit(sombra, (self.ret.x, self.ret.y + 3))

        borda = BORDA_SUAVE if not (self.foco or self.hover) else ACENTO
        painel(tela, self.ret, fundo=base, borda=borda,
               raio=RAIO["md"], alpha=250, espessura=1)

        # barra de acento à esquerda quando em foco/hover
        if self.foco or self.hover:
            altura_barra = max(10, int((self.ret.height - 18) * (0.45 + 0.55 * self._pulso)))
            barra = pygame.Rect(self.ret.x + 6,
                                self.ret.centery - altura_barra // 2, 3, altura_barra)
            pygame.draw.rect(tela, ACENTO, barra, border_radius=2)

        # anel de foco FORA da caixa (não muda o preenchimento)
        if self.foco:
            anel = self.ret.inflate(8, 8)
            pygame.draw.rect(tela, (*FOCO, 200), anel, width=2, border_radius=RAIO["md"] + 4)

        cor_texto = TEXTO_APAGADO if self.desabilitado else (
            TEXTO if not (self.foco or self.hover) else (255, 255, 255))
        deslocamento = 1 if self.pressionado else 0
        # menu: rótulo à esquerda (alinha com os ícones). Ação única: centralizado.
        if self.centralizar:
            alvo_x = self.ret.centerx
            alinhamento = "centro"
        else:
            alvo_x = self.ret.x + (58 if self.icone else 26)
            alinhamento = "esq"
        texto(tela, fonte, self.rotulo, cor_texto, alvo_x,
              self.ret.centery + deslocamento, alinhamento=alinhamento, vertical="meio")

        if self.icone:
            icone_x = self.ret.x + 26
            desenhar_icone(tela, self.icone, icone_x, self.ret.centery + deslocamento,
                           cor_texto, 8)


# --------------------------------------------------------------------------
# Ícones desenhados (a paleta não depende de fonte com símbolo)
# --------------------------------------------------------------------------
def desenhar_icone(tela, nome: str, x: float, y: float, cor, tamanho: float = 8) -> None:
    if nome == "play":
        pygame.draw.polygon(tela, cor, [(x - tamanho * 0.5, y - tamanho),
                                        (x - tamanho * 0.5, y + tamanho),
                                        (x + tamanho * 0.9, y)])
    elif nome == "livro":
        pygame.draw.rect(tela, cor, (x - tamanho, y - tamanho * 0.8,
                                     tamanho * 2, tamanho * 1.6), 2, border_radius=2)
        pygame.draw.line(tela, cor, (x, y - tamanho * 0.8), (x, y + tamanho * 0.8), 2)
    elif nome == "som":
        pygame.draw.polygon(tela, cor, [(x - tamanho, y - tamanho * 0.5),
                                        (x - tamanho * 0.3, y - tamanho * 0.5),
                                        (x + tamanho * 0.3, y - tamanho),
                                        (x + tamanho * 0.3, y + tamanho),
                                        (x - tamanho * 0.3, y + tamanho * 0.5),
                                        (x - tamanho, y + tamanho * 0.5)])
        pygame.draw.arc(tela, cor, (x - tamanho * 0.2, y - tamanho * 0.8,
                                    tamanho * 1.6, tamanho * 1.6), -0.9, 0.9, 2)
    elif nome == "sair":
        pygame.draw.rect(tela, cor, (x - tamanho, y - tamanho * 0.9,
                                     tamanho * 1.2, tamanho * 1.8), 2, border_radius=2)
        pygame.draw.line(tela, cor, (x - tamanho * 0.2, y), (x + tamanho, y), 2)
        pygame.draw.polygon(tela, cor, [(x + tamanho, y), (x + tamanho * 0.5, y - 4),
                                        (x + tamanho * 0.5, y + 4)])


# --------------------------------------------------------------------------
# Componentes auxiliares
# --------------------------------------------------------------------------
def chip(tela, fonte, conteudo, x, y, *, cor_texto=TEXTO_MEDIO, fundo=FUNDO_PAINEL,
         borda=BORDA_SUAVE, icone=None, alinhamento="esq"):
    """Etiqueta pequena (tecla, tag, status) com altura fixa e texto centrado."""
    largura_texto = largura(fonte, conteudo)
    altura = 26
    larg = largura_texto + (34 if icone else 24)
    caixa = pygame.Rect(0, 0, larg, altura)
    if alinhamento == "centro":
        caixa.centerx = x
    elif alinhamento == "dir":
        caixa.right = x
    else:
        caixa.x = x
    caixa.y = y
    painel(tela, caixa, fundo=fundo, borda=borda, raio=RAIO["sm"], alpha=225)
    if icone:
        desenhar_icone(tela, icone, caixa.x + 15, caixa.centery, cor_texto, 6)
    texto(tela, fonte, conteudo, cor_texto, caixa.x + (30 if icone else 12),
          caixa.centery, vertical="meio")
    return caixa


def tecla(tela, fonte, rotulo: str, x, y) -> pygame.Rect:
    """Chip de tecla (ex.: 'ESPAÇO') — cor + forma, nunca cor sozinha."""
    largura_texto = largura(fonte, rotulo)
    caixa = pygame.Rect(x, y, largura_texto + 20, 26)
    pygame.draw.rect(tela, (30, 41, 60), caixa, border_radius=6)
    pygame.draw.rect(tela, (58, 76, 106), caixa, width=1, border_radius=6)
    pygame.draw.rect(tela, (255, 255, 255), (caixa.x + 4, caixa.y + 4, caixa.width - 8, 1))
    texto(tela, fonte, rotulo, (226, 236, 250), caixa.centerx, caixa.centery,
          alinhamento="centro", vertical="meio")
    return caixa


def titulo(tela, fonte, conteudo, centro_x, y, *, cor=config.TEXTO, sombra=(0, 0, 0),
           espacamento_letras: int = 0):
    """Título com sombra curta para garantir contraste sobre a cena."""
    if espacamento_letras:
        conteudo = (" " * 0).join(conteudo)  # fallback simples
    return texto(tela, fonte, conteudo, cor, centro_x, y, alinhamento="centro",
                 sombra=sombra)


def divisor(tela, x, y, largura_linha, cor=BORDA_SUAVE):
    pygame.draw.rect(tela, cor, (x, y, largura_linha, 1))


def seta(tela, centro, direcao: str, cor, tamanho: float = 5) -> None:
    x, y = centro
    if direcao == "dir":
        pontos = [(x - tamanho, y - tamanho), (x - tamanho, y + tamanho), (x + tamanho, y)]
    elif direcao == "esq":
        pontos = [(x + tamanho, y - tamanho), (x + tamanho, y + tamanho), (x - tamanho, y)]
    elif direcao == "cima":
        pontos = [(x - tamanho, y + tamanho), (x + tamanho, y + tamanho), (x, y - tamanho)]
    else:
        pontos = [(x - tamanho, y - tamanho), (x + tamanho, y - tamanho), (x, y + tamanho)]
    pygame.draw.polygon(tela, cor, pontos)


# --------------------------------------------------------------------------
# Contraste (auditoria — usada por tools/checar_contraste.py)
# --------------------------------------------------------------------------
def luminancia(cor) -> float:
    def canal(valor: float) -> float:
        valor = valor / 255
        return valor / 12.92 if valor <= 0.03928 else ((valor + 0.055) / 1.055) ** 2.4

    r, g, b = cor[:3]
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def contraste(cor_a, cor_b) -> float:
    """Razão de contraste WCAG entre duas cores (1 a 21)."""
    la, lb = luminancia(cor_a), luminancia(cor_b)
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def rotulo_valido(cor_texto, cor_fundo, tamanho_pt: float = 19) -> bool:
    """Texto normal precisa 4.5:1; texto grande (>= 24 pt) precisa 3:1."""
    minimo = 3.0 if tamanho_pt >= 24 else 4.5
    return contraste(cor_texto, cor_fundo) >= minimo
