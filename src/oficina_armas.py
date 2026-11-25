"""Oficina isolada para comparar alcance, cadência e custo sem alterar a campanha."""
import pygame
from .combate import Inimigo
from .fases import CHAO, Fase, Objeto, Terreno
from .travessia import Jornada

ABRIGO = (160, CHAO)
OFICINA = Fase(name='Oficina dos Espinhos', width=1400, pisos=((0,1400),),
               plataformas=((680,CHAO-115,150),), tetos=(),
               objetos=(Objeto('abrigo','refugio',*ABRIGO,'Restaurar luz e alvos'),),
               mecanismos={}, preparo='', passos=(), inimigos=(), orvalhos=(),
               registro=('',''), fonte='')


class AlvoDeCasca(Inimigo):
    def repor(self):
        super().repor()
        self.max_vida = self.vida = 20
        self.ativo = True
        self.frente = 1

    def update(self, dt, lume, raio, iluminado, terrenos):
        self.flash=max(0.,self.flash-dt)
        self.relogio+=dt
        return [], False


class Oficina(Jornada):
    ensaio_armas = True

    def __init__(self, dificuldade='normal'):
        self._terrenos=(Terreno(pygame.Rect(0,CHAO,1400,128),'chao'),
                        Terreno(pygame.Rect(680,CHAO-115,150,12),'plataforma'))
        super().__init__('historia', dificuldade)

    def entrar(self, indice, retorno=False):
        self.etapa=0
        self.fase=OFICINA
        self.flags=self.historico.setdefault((0,0),set())
        self.boss=None
        self.gotas=()
        self.checkpoint=ABRIGO
        self.reiniciar()

    def reiniciar(self):
        self.flags.clear()
        self.inimigos=[AlvoDeCasca('carabideo',520,CHAO),AlvoDeCasca('aranha',760,CHAO-115)]
        super().reiniciar()

    @property
    def solidos(self):
        return self._terrenos

    @property
    def objetos(self):
        return OFICINA.objetos

    @property
    def objetivo(self):
        if getattr(self,'ensaio_combos',False):return 'Combine J, L e K · Ctrl + ataque usa brilho · acerte sem sofrer dano'
        return 'Compare espinho e agulha · V troca a arma fora do golpe'

    @property
    def dica_local(self):
        return 'J/J/J encadeia cortes; S+J no ar rebate; direção+Shift+J avança. E no abrigo repõe os alvos.'

    def interagir(self, objeto):
        if objeto.id=='abrigo':
            for e in self.inimigos:
                e.repor()
            self.flags.clear()
        super().interagir(objeto)
