"""Mistura local de trilha, combate, batimento, vida da mata e ações em primeiro plano."""
from pathlib import Path
import math
import pygame

PASTA=Path(__file__).resolve().parents[1]/"assets"/"sons"
# Os sinais de perigo, dano e mecanismo têm canais distintos para não se encobrirem.
ALIASES={"etapa":"abertura","selo":"seiva","chefe_exposto":"vulneravel","chefe_acerto":"acerto",
         "chefe_vencido":"vencer","chefe_resolvido":"vencer","investida":"deslize","parede":"impacto","brasa":"seiva",
         "vulneravel":"vulneravel","exposto":"vulneravel","madeira":"impacto","barril":"valvula"}
ALERTAS={"aviso":5,"dano":6,"acerto":7,"sino":8,"impacto":9,"vulneravel":8,
         "raiz":9,"porta":8,"seiva":8}


def panoramica(delta, alcance=550):
    """Distância lateral de uma fonte relativa a Lume, em pixels do mundo."""
    distancia = abs(delta)
    if distancia >= alcance:
        return 0., 0.
    desvio = max(-1., min(1., delta/215))
    ganho = 1 - .82 * distancia / alcance
    return (ganho * math.sqrt((1 - .83*desvio) / 2),
            ganho * math.sqrt((1 + .83*desvio) / 2))


class Audio:
    def __init__(self,pasta=PASTA):
        self.disponivel=False
        self.mudo=False
        self.volume_musica=.65
        self.volume_efeitos=.85
        self.atual=None
        self.ativos=(0.,0.,0.)
        self.niveis=[0.,0.,0.]
        self.silencio=0.
        self.grave=0.
        self.pasta=Path(pasta)
        self.fx={}
        self.camadas=[]
        self.trilhas={}
        try:
            if not pygame.mixer.get_init(): pygame.mixer.init(44100,-16,2,512)
            pygame.mixer.set_num_channels(28)
            pygame.mixer.set_reserved(16)
            for p in self.pasta.glob("*.wav"):
                nome=p.stem
                if nome.startswith("trilha_"): self.trilhas[nome[7:]]=p
                else: self.fx[nome]=pygame.mixer.Sound(str(p))
            for n,nome in enumerate(("camada_combate","camada_pulso","camada_vida")):
                canal=pygame.mixer.Channel(n)
                canal.set_volume(0.)
                if nome in self.fx: canal.play(self.fx[nome],loops=-1)
                self.camadas.append(canal)
            self.disponivel=True
        except (pygame.error,OSError):
            return

    def tocar_musica(self,nome):
        if nome==self.atual or not self.disponivel: return
        caminho=self.trilhas.get(nome)
        if not caminho: return
        try:
            pygame.mixer.music.load(str(caminho))
            pygame.mixer.music.play(-1,fade_ms=560)
            self.atual=nome
            self.aplicar_volumes()
        except (pygame.error,OSError):
            pass

    def tocar(self,nome):
        if not self.disponivel or self.mudo: return
        nome=ALIASES.get(nome,nome)
        som=self.fx.get(nome)
        if not som: return
        n=ALERTAS.get(nome)
        canal=pygame.mixer.Channel(n) if n is not None else next((pygame.mixer.Channel(i) for i in range(16,28) if not pygame.mixer.Channel(i).get_busy()),None)
        if not canal: return
        volume=self.volume_efeitos*(.32 if nome=="passo" else (.50 if nome in ("clique","navegar") else .82))
        canal.set_volume(volume)
        canal.play(som)
        if nome in ("aviso","sino","dano"): self.silencio=.47

    def tocar_local(self, nome, fonte_x, ouvinte_x):
        if not self.disponivel or self.mudo:
            return
        som = self.fx.get(nome)
        if som is None:
            return
        esq, dire = panoramica(fonte_x-ouvinte_x)
        if esq + dire == 0:
            return
        # Seis vozes posicionais, independentes da música, impacto e interface.
        canais = [pygame.mixer.Channel(n) for n in range(10,16)]
        livre = next((c for c in canais if not c.get_busy()), None)
        if livre is None:
            return
        livre.set_volume(esq*self.volume_efeitos, dire*self.volume_efeitos)
        livre.play(som)
        self.silencio = .38

    def ambiente(self,*,combate,energia,raizes,suspenso=False):
        self.grave=max(0.,min(1.,(31.-energia)/21.))
        self.ativos=(.44 if combate else 0.,self.grave*.64,
                     0. if suspenso else min(.48,.12*raizes))

    def aplicar_volumes(self):
        if not self.disponivel: return
        musica=0 if self.mudo else self.volume_musica
        fx=0 if self.mudo else self.volume_efeitos
        corte=(1-.40*self.grave)*(.37 if self.silencio>0 else 1)
        pygame.mixer.music.set_volume(musica*corte*.79)
        for i,canal in enumerate(self.camadas):
            canal.set_volume(self.niveis[i]*(fx if i==1 else musica))
        if self.mudo:
            for n in range(5,pygame.mixer.get_num_channels()): pygame.mixer.Channel(n).stop()

    def atualizar(self,dt):
        if not self.disponivel: return
        self.silencio=max(0.,self.silencio-dt)
        for i,destino in enumerate(self.ativos):
            self.niveis[i]+=(destino-self.niveis[i])*min(1,dt*5)
        self.aplicar_volumes()
