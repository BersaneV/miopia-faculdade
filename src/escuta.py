"""Ensaio de ouvido isolado: não grava progresso nem altera o combate da História."""
from .travessia import Jornada
from .taticas import FAMILIAS
from .fases import CHAO


class Escuta(Jornada):
    def __init__(self,dificuldade):
        super().__init__('historia',dificuldade)
        self.checkpoint=(160,CHAO);self.recolocar(self.checkpoint)
        self.especies=tuple(FAMILIAS);self.especie=0;self.familia=0
        self.inimigos=[];self.ensaio_escuta=True
        self.mostrar()

    def mostrar(self):
        e=self.especies[self.especie];f=FAMILIAS[e][self.familia]
        self.notificar(f'{e.title()} · {f} — J muda o golpe; K muda a espécie; E escuta. Fones ajudam a avaliar.',3600)

    @property
    def interacao(self):return 'E: ouvir o aviso à direita'

    def update(self,dt,cmd=None):
        self.eventos.clear();self.sons_espaciais.clear()
        self.tempo+=dt
        if cmd:
            if cmd.golpe:self.familia=(self.familia+1)%5;self.mostrar()
            if cmd.clarao:self.especie=(self.especie+1)%len(self.especies);self.mostrar()
            if cmd.interagir:self.sons_espaciais.append((f'aviso_{self.especies[self.especie]}_{self.familia}',self.lume.rect.centerx+130))
