"""Galeria das Sementes, sob a ponte do Taquaral."""
import pygame

from . import nicho_taquaral as nicho
from .combate import segmento_bloqueado
from .fases import CHAO, Objeto, Terreno
from .taticas import Habitante, RECEITAS
from .vento_taquaral import Corrente

TITULO = "Galeria das Sementes"
PEDIDO = "bercos_vento"
NOME_PEDIDO = "Os berços de vento"
MOTIVO = "Risca quer voltar a secar as sementes nos berços sob a ponte."
PREMIO = "Globo de vaga-lume e uma corrente de volta à superfície."
ALTURA = 1080
FUNDO = 968
ESQUERDA, DIREITA = 1640, 2496
ENTRADA = (2130, 2238)
SAIDA = (2336, 2464)
BOCA_VENEZIANA = pygame.Rect(2320, 562, 152, 17)
CHAMINE = Corrente(2348, 2453, 320, 950, 0, -187)
DURACAO_VENEZIANA = .92
ABERTA = "veneziana_sementes_aberta"
CONHECIDA = "bercos_vento_conhecidos"
CIPO = Objeto("cipo_sementes", "galeria_sementes", 2180, FUNDO, "Subir pelo cipó da galeria")
PLACA = Objeto("placa_sementes", "galeria_sementes", 2184, CHAO, "Ler a placa de Risca")
CAVILHA = Objeto("cavilha_sementes", "galeria_sementes", 1725, FUNDO, "Recolher a cavilha de casca")
VENEZIANA = Objeto("veneziana_sementes", "galeria_sementes", 2390, FUNDO, "Reparar a veneziana")
POLEIROS = ((1948, 875), (2087, 871))
ORIGEM_ARANHA = (1910, FUNDO)
MEMBROS = (POLEIROS[1][0], ORIGEM_ARANHA[0])
PRIMEIRAS_FAMILIAS = tuple(next(p for p in c.passos if isinstance(p, int)) for c in RECEITAS)


class VespaDaFenda(Habitante):
    @property
    def no_poleiro(self):
        x, y = self.rect.midbottom
        return any(abs(x-px) <= 6 and abs(y-py) <= 3 for px, py in POLEIROS)

    @property
    def duracao_aviso(self):
        return super().duracao_aviso + (.12 if self.tecnica == "ferrao" else 0.)

    def viavel(self, indice, lume, terrenos):
        return (indice not in (1, 2) or self.no_poleiro) and super().viavel(indice, lume, terrenos)

    def pesos_combos(self, lume, terrenos):
        base = super().pesos_combos(lume, terrenos)
        return [peso * (3.0 if familia in (1, 2) else 1.0)
                for peso, familia in zip(base, PRIMEIRAS_FAMILIAS)]

    def poleiro(self, lume):
        return min(POLEIROS, key=lambda p: abs(abs(lume.rect.centerx-p[0])-148))

    def preparar(self, lume, terrenos=()):
        px, py = self.poleiro(lume)
        if (not self.no_poleiro and 820 < lume.rect.bottom <= FUNDO+4
                and 68 < abs(lume.rect.centerx-px) < 270
                and (not self.plano or self.plano[0] in (1, 2))
                and not segmento_bloqueado(self.rect.center, (px, py-self.rect.h/2), terrenos)):
            self.t = .12
            return ""
        return super().preparar(lume, terrenos)

    def patrulhar(self, lume, distancia, dt, terrenos):
        px, py = self.origem
        if lume.rect.bottom > 780 and distancia < 320:
            px, py = self.poleiro(lume)
        self.seguir((px, py-self.rect.h/2), 155, dt, terrenos)


def povoar(j):
    for classe, especie, (x, y) in ((VespaDaFenda, "vespa", POLEIROS[1]),
                                   (Habitante, "aranha", ORIGEM_ARANHA)):
        if f"inimigo_{x}" not in j.flags:
            j.inimigos.append(classe(especie, x, y, j.dificuldade))
    nicho.povoar(j)


def ativo(j):
    return j.etapa == 2 and not j.em_vertical and not hasattr(j, "sala_id")


def dentro(j):
    x, y = j.lume.rect.midbottom
    return ativo(j) and (ESQUERDA <= x < DIREITA and CHAO + 42 < y <= ALTURA or nicho.dentro(j))


def abertura(j):
    if ABERTA not in j.flags:
        return 0.
    if j.veneziana_inicio is None:
        return 1.
    return min(1., (j.tempo-j.veneziana_inicio)/DURACAO_VENEZIANA)


def painel(j):
    r = BOCA_VENEZIANA
    largura = round(r.w * (1.-abertura(j)))
    return pygame.Rect(r.right-largura, r.y, largura, r.h)


def vento(j):
    # O impulso vem da abertura embaixo; os espaços abrigados mantêm o ar parado.
    if CHAMINE.contem(*j.lume.rect.midbottom) and abertura(j) == 1.:
        return CHAMINE
    return None


def zonas(j):
    if not ativo(j):
        return ()
    zonas = []
    if abertura(j) == 1.:
        zonas.append(pygame.Rect(2324, 430, 148, 538))
    if nicho.ACESO in j.flags:
        zonas.append(pygame.Rect(nicho.OESTE, 808, nicho.LESTE-nicho.OESTE+30, FUNDO+40-808))
    return zonas


def terrenos(superficie, abertas, nicho_aberto=False):
    for terreno in superficie:
        r = terreno.rect
        if terreno.tipo != "chao" or r.top != CHAO or not r.left <= ENTRADA[0] < SAIDA[1] <= r.right:
            yield terreno
            continue
        inicio = r.left
        for esquerda, direita in (ENTRADA, SAIDA):
            yield Terreno(pygame.Rect(inicio, CHAO, esquerda-inicio, r.h), "chao")
            forma = "ponte" if esquerda == SAIDA[0] and not abertas else "grade"
            yield Terreno(pygame.Rect(esquerda, CHAO, direita-esquerda, 16), forma)
            inicio = direita
        yield Terreno(pygame.Rect(inicio, CHAO, r.right-inicio, r.h), "chao")
    for x, y, w in ((2060, 590, 192), (1942, 685, 180), (2088, 775, 164),
                    (1742, 875, 234), (1672, 792, 151), (2050, 871, 73)):
        yield Terreno(pygame.Rect(x, y, w, 16), "plataforma")
    oeste = nicho.SOLEIRA if abertas else FUNDO
    yield Terreno(pygame.Rect(ESQUERDA, 570, 30, oeste-570), "colmos_galeria")
    if abertas:
        yield from nicho.terrenos(nicho_aberto)
    yield Terreno(pygame.Rect(2472, 570, 28, FUNDO-570), "colmos_galeria")
    yield Terreno(pygame.Rect(ESQUERDA, FUNDO, DIREITA-ESQUERDA+4, ALTURA-FUNDO), "chao")
    yield Terreno(pygame.Rect(2254, 747, 70, 182), "colmos_galeria")
    yield Terreno(pygame.Rect(2122, 791, 30, 125), "colmos_galeria")
    if not abertas:
        yield Terreno(BOCA_VENEZIANA, "veneziana_sementes")


def camera(j, dt=None):
    from .sinalizacao import camera_vertical
    camera_vertical(j, ALTURA, dt)


def atualizar(j, dt):
    camera(j, dt)
    if j.veneziana_inicio is not None and abertura(j) == 1.:
        j.veneziana_inicio = None
        j.eventos.append("madeira")


def objetos(j):
    base = (PLACA, CIPO, VENEZIANA)
    if ABERTA in j.flags:
        base += (nicho.TRANCA,)
    if nicho.ABERTO in j.flags:
        base += (nicho.LAMPADA_ACESA if nicho.ACESO in j.flags else nicho.LAMPADA,)
    return base if CAVILHA.id in j.flags else (*base, CAVILHA)


def passo_pedido(flags):
    if ABERTA in flags:
        return "Concluída", "A luz volta aos berços e as sementes sobem pela chaminé.", ""
    if CAVILHA.id in flags:
        return "Entregar", "Use S ou direção + Shift sob a raiz baixa a leste. Depois, E na veneziana.", VENEZIANA.id
    return "Em curso", "Desça pela grade depois da Sentinela. A cavilha está na ponta oeste da galeria.", CAVILHA.id


def orientar(j):
    if not ativo(j):
        return None
    from .orientacao import _alvo
    if j.missao == PEDIDO and CONHECIDA in j.flags and ABERTA not in j.flags:
        _, pista, ident = passo_pedido(j.flags)
        if not dentro(j):
            return _alvo(j, "entrada_sementes", NOME_PEDIDO, "Desça pela grade de Risca",
                         PLACA.x, CHAO, "Depois da Sentinela, use S + Espaço na grade e nos patamares.",
                         opcional=True)
        o = CAVILHA if ident == CAVILHA.id else VENEZIANA
        return _alvo(j, ident, NOME_PEDIDO, o.nome, o.x, o.y, pista, opcional=True)
    if dentro(j):
        if nicho.dentro(j) and nicho.ACESO not in j.flags:
            vencida = nicho.DERROTADA in j.flags
            return _alvo(j, nicho.LAMPADA.id if vencida else "cobra_bercos", nicho.TITULO,
                         "Acenda a luz do depósito" if vencida else "Afaste a Cobra dos Berços",
                         nicho.LAMPADA.x if vencida else nicho.ORIGEM[0], FUNDO,
                         "E junto ao cofre acende a luz após a luta." if vencida else
                         "Salte o bote e ataque na brecha. Ctrl + J atravessa as escamas.", opcional=True)
        if j.lume.rect.centerx > CHAMINE.esquerda and abertura(j) == 1.:
            return _alvo(j, "chamine_sementes", TITULO, "Plane pela chaminé",
                         VENEZIANA.x, VENEZIANA.y,
                         "Salte onde as sementes sobem e segure Espaço. Acima da grade, solte para pousar.",
                         opcional=True)
        return _alvo(j, CIPO.id, TITULO, "Suba pelo cipó central",
                     CIPO.x, CIPO.y, "Use E na base. Volte à trilha principal por cima da galeria.", opcional=True)
    return None


def interagir(j, o):
    if o.id == nicho.TRANCA.id and ABERTA in j.flags:
        nicho.destrancar(j)
    elif o.id == nicho.LAMPADA.id and nicho.ABERTO in j.flags:
        nicho.acender(j)
    elif o.id == CIPO.id:
        l = j.lume
        l.em_corda, l.corda_destino = True, CHAO
        l.rect.centerx = CIPO.x
        l.vx = l.vy = 0.
        j.eventos.append("corda")
    elif o.id == PLACA.id:
        j.flags.add(CONHECIDA)
        j.dialogo = ("Os berços de vento",
                     "Risca escreveu: “As sementes secavam aqui mesmo em noite de garoa. "
                     "A enchente levou a cavilha para a ponta oeste. Guardei um globo junto à roda, "
                     "para quem devolver o ar aos berços.”")
        j.memorizar(*j.dialogo)
        j.eventos.append("pagina")
    elif o.id == CAVILHA.id and o.id not in j.flags:
        j.flags.update((CONHECIDA, o.id))
        j.notificar("Cavilha de Risca guardada. A veneziana está depois da raiz baixa, a leste.", 6.)
        j.eventos.append("coleta")
    elif o.id == VENEZIANA.id:
        if ABERTA in j.flags:
            j.notificar("A veneziana deixa o ar circular até a grade leste.")
        elif CAVILHA.id not in j.flags:
            j.flags.add(CONHECIDA)
            j.notificar("Falta a cavilha. Procure no piso da ponta oeste, depois da patrulha.", 6.)
        else:
            j.flags.add(ABERTA)
            j.veneziana_inicio = j.tempo
            j.bolsa.receber("globo", 1)
            if j.missao == PEDIDO:
                j.missao = "principal"
            j.memorizar(NOME_PEDIDO, "A veneziana voltou a se mover. Risca deixou na roda um Globo de vaga-lume.")
            j.notificar("Veneziana reparada. Globo na bolsa. Salte na chaminé e segure Espaço ao cair.", 7.)
            j.eventos.extend(("valvula", "coleta"))


