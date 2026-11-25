"""Encontros laterais. Toda geometria de combate usa coordenadas do mundo."""
from dataclasses import dataclass
from functools import lru_cache
from math import hypot, sin
from pathlib import Path

import pygame


@dataclass(frozen=True)
class Ficha:
    nome: str
    folha: str
    pista: str
    janela: str
    desfecho: str


FICHAS = (
    Ficha("Asa Fendida", "asa-fendida", "Atraia a asa até uma raiz marcada. Abaixe-se.",
          "Dorso exposto. Suba no patamar e golpeie com J.", "Asa Fendida recolhe as asas."),
    Ficha("Tecelã do Vão", "tecela", "Gire a válvula à esquerda para romper os fios.",
          "O ventre tocou o leito. Aproxime-se e golpeie com J.", "A teia solta a margem."),
    Ficha("Casco Oco", "casco-oco", "Leve a seiva ao entalhe. Depois, acione a brasa.",
          "A casca se abriu. Salte até a marca e golpeie com J.", "O guardião baixa a carapaça."),
    Ficha("A Coruja", "coruja", "Mova o sino pela válvula e toque a corda com E.",
          "Ela escuta. Suba perto da face e lance um clarão (K).", "A Coruja reconhece Lume."),
)

FERRUGEM = (222, 132, 99)
OURO = (252, 206, 132)
TEAL = (118, 176, 167)
FIO = (183, 211, 197)
ESCURO = (31, 44, 48)
PELE = (75, 95, 88)


@dataclass
class Fio:
    x: float
    y: float
    vx: float
    vy: float


@dataclass
class Trama:
    faixa: pygame.FRect
    tempo: float = 2.8
    tocada: bool = False


def aproximar(a, b, passo):
    return a + max(-passo, min(passo, b-a))


@lru_cache(maxsize=4)
def _quadros(nome):
    """Folhas compartilhadas; o espelhamento acontece uma vez por pose/quadro."""
    raiz = Path(__file__).resolve().parent.parent
    folha = pygame.image.load(str(raiz / "assets" / "chefes" / (nome + ".png")))
    w, h = folha.get_width() // 4, folha.get_height() // 4
    quadros = {}
    for pose in range(4):
        for frame in range(4):
            quadro = folha.subsurface((frame*w, pose*h, w, h))
            quadros[(pose, frame, 1)] = quadro
            quadros[(pose, frame, -1)] = pygame.transform.flip(quadro, True, False)
    return quadros


class Encontro:
    """Um encontro novo restaura a geometria e todos os objetos essenciais."""
    meta = 2

    def __init__(self, indice: int, inicio: int, chao: int, largura: int = 760):
        self.indice, self.inicio, self.chao, self.largura = indice, inicio, chao, largura
        self.ficha = FICHAS[indice]
        self.nome = self.ficha.nome
        self.esq = inicio + 62
        self.dir = inicio + largura - 62
        self.x, self.y = self.dir - 40., chao - 110.
        self.frente = -1
        self.estado = "busca"
        self.tempo, self.relogio = 1.65, 0.
        self.progresso = 0
        self.vencido = False
        self.turno = 0
        self.destino = self.esq
        self.alvo_y = chao - 28.
        self.impacta = False
        self.atingiu = False
        self.fios = []
        self.tramas = []
        self.agua = self.onda = 0.
        self.barrel_x = self.inicio + 102.
        self.engatado = self.assentado = self.tabua_quebrada = False
        self.sino_movido = self.sino_soou = False
        self.x_ouvido = None
        if indice == 1:
            self.x, self.y = self.cortina, chao-203.
        if indice == 2:
            self.x, self.y = self.inicio + largura * .77, chao-35.

    @property
    def valvula(self):
        return self.inicio + 180

    @property
    def cortina(self):
        return self.inicio + self.largura * .39

    @property
    def brasa(self):
        return self.inicio + self.largura * .60

    @property
    def entalhe(self):
        return self.inicio + self.largura * (.46 if self.progresso == 0 else .69)

    @property
    def dica(self):
        if self.vencido:
            return self.ficha.desfecho
        if self.estado == "aberto":
            return self.ficha.janela
        if self.indice == 2:
            if self.estado in ("rastro", "investida_seiva", "flor"):
                return "O guardião segue a seiva. Salte sobre o casco."
            if self.assentado:
                return "A seiva encaixou. Toque a fonte de brasa (E)."
            if self.engatado:
                return "Caminhe com a seiva até o aro âmbar no chão."
        if self.indice == 3 and self.sino_movido:
            return "Toque a corda na válvula. Siga o som até a parede."
        return self.ficha.pista

    def apoios(self):
        """Apoios de mão única; os degraus junto às marcas sempre ficam disponíveis."""
        base = self.chao
        apoios = [
            pygame.Rect(self.inicio+16, base-66, 147, 12),
            pygame.Rect(self.inicio+self.largura-163, base-66, 147, 12),
            pygame.Rect(self.inicio+186, base-120, 116, 11),
            pygame.Rect(self.inicio+self.largura-302, base-120, 116, 11),
        ]
        if self.indice == 2 and not self.tabua_quebrada:
            apoios.append(pygame.Rect(self.inicio+self.largura//2-46, base-45, 92, 10))
        return apoios

    def _perto(self, corpo, x, alcance=59):
        return abs(corpo.centerx-x) <= alcance and self.chao-86 <= corpo.bottom <= self.chao+24

    def interacao(self, corpo):
        if self.vencido or self.estado in ("aberto","desce","flor","rastro","investida_seiva"):
            return ""
        if self.indice == 1 and self.agua <= 0 and self._perto(corpo, self.valvula):
            return "Abrir cortina de água"
        if self.indice == 2:
            if self.assentado and self._perto(corpo, self.brasa):
                return "Despertar brasa"
            if not self.assentado and self._perto(corpo, self.barrel_x):
                return "Soltar seiva" if self.engatado else "Empurrar seiva"
        if self.indice == 3 and self._perto(corpo, self.valvula):
            return "Tanger sino" if self.sino_movido else "Mover sino"
        return ""

    def _mudar(self, estado, tempo):
        self.estado, self.tempo = estado, tempo

    def _usar(self, corpo, eventos):
        acao = self.interacao(corpo)
        if acao == "Abrir cortina de água":
            self.agua = 4.
            self.tramas.clear()
            eventos.extend(("valvula", "agua"))
        elif acao == "Despertar brasa":
            self.engatado = False
            self.destino = self.entalhe
            self.alvo_y = self.chao - 35
            self.frente = 1 if self.destino > self.x else -1
            self.atingiu = False
            self._mudar("rastro", .75)
            eventos.extend(("seiva", "aviso"))
        elif acao in ("Soltar seiva", "Empurrar seiva"):
            self.engatado = not self.engatado
            eventos.append("valvula")
        elif acao == "Mover sino":
            self.sino_movido = True
            eventos.append("valvula")
        elif acao == "Tanger sino":
            self.sino_soou = True
            self.onda = 1.
            eventos.append("sino")
            # O som aciona a busca mesmo quando Lume fica inteiramente imóvel.
            if self.estado == "busca":
                self.tempo = min(self.tempo, .15)

    def _abrir(self, duracao, eventos):
        self._mudar("aberto", duracao)
        self.onda = .7
        eventos.append("impacto")

    def _marca(self):
        if self.indice == 0:
            return self.x - self.frente * 27, self.chao - 80
        if self.indice == 1:
            return self.x, self.chao - 30
        if self.indice == 2:
            return self.x - 12, self.chao - (71 if self.progresso == 0 else 97)
        return self.x - 16, self.chao - 94

    def _acertou(self, corpo, golpe, clarao):
        mx, my = self._marca()
        ponto = pygame.Rect(round(mx)-18, round(my)-19, 36, 38)
        if self.indice == 3:
            return (clarao and corpo.bottom <= self.chao - 32
                    and hypot(corpo.centerx-mx, corpo.centery-my) < 130)
        altura = self.indice == 1 or corpo.bottom <= self.chao - 30
        return altura and golpe is not None and ponto.colliderect(golpe)

    def _fechar(self):
        self.fios.clear()
        self.agua = 0.
        self.sino_soou = False
        self.engatado = self.assentado = False
        self.barrel_x = self.inicio + 102
        self._mudar("busca", 1.6)

    def _atualizar_aberto(self, corpo, golpe, clarao, eventos):
        if self._acertou(corpo, golpe, clarao):
            self.progresso += 1
            self.onda = 1.
            eventos.append("acerto")
            if self.progresso == self.meta:
                self.vencido = True
                self.estado = "repouso"
                eventos.append("chefe_resolvido")
                return
            self._fechar()
        elif self.tempo <= 0:
            self._fechar()

    def _colisao(self, corpo, area, eventos):
        if not self.atingiu and area.colliderect(corpo):
            self.atingiu = True
            eventos.append("dano_jogador")

    def _aviso_investida(self, destino, y, duracao, impacta, eventos):
        self.destino = max(self.esq, min(self.dir, destino))
        self.alvo_y = y
        self.frente = 1 if self.destino > self.x else -1
        self.impacta, self.atingiu = impacta, False
        self._mudar("aviso", duracao)
        eventos.append("aviso")

    def _voar(self, dt, corpo, eventos, velocidade):
        self.y = self.alvo_y
        self.x = aproximar(self.x, self.destino, velocidade*dt)
        # A linha alta passa pelo jogador em pé mas sobre a caixa agachada.
        faixa = pygame.FRect(self.x-32, self.y-12, 64, 19)
        self._colisao(corpo, faixa, eventos)
        if abs(self.x-self.destino) < .01:
            if self.impacta:
                self.y = self.chao - (57 if self.indice == 0 else 72)
                self._abrir(5.6 if self.indice == 0 else 7.1, eventos)
            else:
                self._mudar("busca", .95)

    def _asa(self, dt, corpo, eventos):
        if self.estado == "busca":
            self.y = aproximar(self.y, self.chao-93+sin(self.relogio*3)*5, dt*120)
            if self.tempo <= 0:
                esquerda = corpo.centerx <= self.esq+133
                direita = corpo.centerx >= self.dir-133
                impacta = esquerda or direita
                destino = self.esq if esquerda else self.dir if direita else corpo.centerx
                # Reposiciona a aproximação do lado oposto quando a vítima está atrás.
                if abs(self.x-destino) < 105:
                    self._mudar("contorna", .65)
                    self.destino = self.dir if destino < (self.esq+self.dir)/2 else self.esq
                else:
                    self._aviso_investida(destino, self.chao-31, .95, impacta, eventos)
        elif self.estado == "contorna":
            self.x = aproximar(self.x, self.destino, 330*dt)
            self.frente = 1 if self.destino >= self.x else -1
            self.y = self.chao-135
            if self.tempo <= 0:
                self._mudar("busca", .35)
        elif self.estado == "aviso":
            self.y = aproximar(self.y, self.alvo_y, dt*170)
            if self.tempo <= 0:
                self._mudar("investida", 2.)
        elif self.estado == "investida":
            self._voar(dt, corpo, eventos, 498)

    def _tecela(self, dt, corpo, eventos):
        # A roda abre a água imediatamente. A aranha cai quando um fio tenso
        # encontra a cortina, o que também funciona para quem abriu antes do aviso.
        if self.agua > 0 and (self.estado == "aviso" or self.fios):
            self.fios.clear()
            self._mudar("desce", 1.0)
        if self.estado == "desce":
            self.x = aproximar(self.x, self.cortina, dt*260)
            self.y = aproximar(self.y, self.chao-31, dt*215)
            if self.tempo <= 0:
                self.y = self.chao-31
                self._abrir(4.8, eventos)
            return
        if self.estado == "busca":
            self.y = aproximar(self.y, self.chao-208, dt*172)
            self.x = aproximar(self.x, self.cortina+sin(self.relogio*.8)*65, dt*125)
            if self.tempo <= 0:
                self.destino = corpo.centerx
                self.alvo_y = corpo.centery
                self.frente = 1 if self.destino > self.x else -1
                self._mudar("aviso", .92)
                eventos.append("aviso")
        elif self.estado == "aviso" and self.tempo <= 0:
            vx, vy = self.destino-self.x, self.alvo_y-self.y
            n = max(1., hypot(vx, vy))
            self.fios.append(Fio(self.x, self.y, vx*265/n, vy*265/n))
            self.turno += 1
            self._mudar("busca", .98)
            eventos.append("teia")
        vivos = []
        for fio in self.fios:
            fio.x += fio.vx*dt
            fio.y += fio.vy*dt
            if pygame.FRect(fio.x-6,fio.y-6,12,12).colliderect(corpo):
                eventos.append("dano_jogador")
            elif self.esq-28 <= fio.x <= self.dir+28 and fio.y >= self.chao-4:
                # Um tiro desviado forma uma trama alta ou baixa no leito.
                # Cada faixa tem uma passagem livre e se desfaz após um contato.
                topo = self.chao - (57 if self.turno % 2 else 20)
                self.tramas.append(Trama(pygame.FRect(fio.x-28, topo, 56, 18)))
            elif self.inicio <= fio.x <= self.inicio+self.largura and self.chao-340 <= fio.y <= self.chao+3:
                vivos.append(fio)
        self.fios = vivos
        for trama in self.tramas:
            trama.tempo -= dt
            if not trama.tocada and trama.faixa.colliderect(corpo):
                trama.tocada = True
                eventos.append("dano_jogador")
        self.tramas = [t for t in self.tramas if t.tempo > 0 and not t.tocada]

    def _casco(self, dt, corpo, direcao, eventos):
        if self.engatado:
            if self._perto(corpo, self.barrel_x, 95):
                # A peça acompanha o besouro somente quando Lume a empurra.
                if direcao:
                    desejado = corpo.centerx + direcao*27
                    self.barrel_x = max(self.esq, min(self.dir, aproximar(self.barrel_x, desejado, dt*295)))
            else:
                self.engatado = False
            if abs(self.barrel_x-self.entalhe) < 24:
                self.barrel_x = self.entalhe
                self.assentado, self.engatado = True, False
                eventos.append("impacto")
        if self.estado == "rastro":
            if self.tempo <= 0:
                self._mudar("investida_seiva", 5.)
            return
        if self.estado == "investida_seiva":
            self.x = aproximar(self.x, self.entalhe, dt*247)
            self._colisao(corpo, pygame.FRect(self.x-36,self.chao-52,72,52), eventos)
            if not self.tabua_quebrada and abs(self.x-self.inicio-self.largura/2)<70:
                self.tabua_quebrada = True
                eventos.append("impacto")
            if self.x == self.entalhe:
                self.onda = 1.
                self._mudar("flor", .65)
                eventos.append("impacto")
            return
        if self.estado == "flor":
            self.y = aproximar(self.y,self.chao-(45 if self.progresso==0 else 70),dt*150)
            if self.tempo <= 0:
                self.x = self.entalhe
                self._abrir(5., eventos)
            return
        if self.estado == "busca":
            self.y = aproximar(self.y, self.chao-35, dt*72)
            self.frente = 1 if corpo.centerx>self.x else -1
            if self.tempo <= 0:
                self._aviso_investida(corpo.centerx + 64*self.frente, self.chao-35, 1.1, False, eventos)
        elif self.estado == "aviso" and self.tempo <= 0:
            self._mudar("investida", 2.)
        elif self.estado == "investida":
            self.x = aproximar(self.x, self.destino, dt*167)
            if not self.tabua_quebrada and abs(self.x-self.inicio-self.largura/2)<70:
                self.tabua_quebrada = True
                eventos.append("impacto")
            self._colisao(corpo, pygame.FRect(self.x-42,self.chao-55,84,54), eventos)
            if self.tempo <= 0 or self.x == self.destino:
                self._mudar("busca", 1.75)

    def _coruja(self, dt, corpo, ruido, eventos):
        if ruido > .05:
            self.x_ouvido = corpo.centerx
        if self.estado == "busca":
            self.y = aproximar(self.y,self.chao-103+sin(self.relogio*2.3)*5,dt*116)
            if self.tempo <= 0:
                self.turno += 1
                if self.sino_soou:
                    self.sino_soou = False
                    # Afasta-se primeiro, se uma investida anterior terminou sob o sino.
                    if abs(self.dir-self.x)<130:
                        self._mudar("contorna", .95)
                        self.sino_soou = True
                        return
                    alvo, alto, parede = self.dir, True, True
                else:
                    patrulha = self.esq if self.x > (self.esq+self.dir)/2 else self.dir
                    alvo = self.x_ouvido if self.x_ouvido is not None else patrulha
                    self.x_ouvido = None
                    alto, parede = self.turno % 2 == 1, False
                self._aviso_investida(alvo, self.chao-(32 if alto else 13), 1.05, parede, eventos)
        elif self.estado == "contorna":
            self.x = aproximar(self.x, self.esq, dt*310)
            self.frente, self.y = -1, self.chao-145
            if self.tempo <= 0:
                self._mudar("busca", .22)
        elif self.estado == "aviso":
            self.y = aproximar(self.y, self.alvo_y, dt*160)
            if self.tempo <= 0:
                self._mudar("investida", 2.)
        elif self.estado == "investida":
            self._voar(dt, corpo, eventos, 415)

    def update(self, dt, corpo, *, ruido=0., golpe=None, clarao=False, interagir=False, direcao=0):
        """Recebe bordas de comando (golpe, clarão e E); retorna eventos desta atualização."""
        eventos = []
        self.relogio += dt
        self.onda = max(0., self.onda-dt)
        self.agua = max(0., self.agua-dt)
        if self.vencido:
            return eventos
        self.tempo -= dt
        if interagir:
            self._usar(corpo, eventos)
        if self.estado == "aberto":
            self._atualizar_aberto(corpo, golpe, clarao, eventos)
        elif self.indice == 0:
            self._asa(dt, corpo, eventos)
        elif self.indice == 1:
            self._tecela(dt, corpo, eventos)
        elif self.indice == 2:
            self._casco(dt, corpo, direcao, eventos)
        else:
            self._coruja(dt, corpo, ruido, eventos)
        return eventos

    def desenhar(self, tela, camera_x, camera_y=0):
        from .arte_arena import desenhar_encontro
        desenhar_encontro(tela, self, camera_x, camera_y)
