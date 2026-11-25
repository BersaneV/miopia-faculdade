"""Cenas isoladas da campanha para as rodadas de avaliação com o jogador."""
from dataclasses import dataclass
from .fases import CHAO, MEIO
from .travessia import Jornada


@dataclass(frozen=True)
class Ensaio:
    nome: str
    etapa: int
    pos: tuple[int, int]
    flags: tuple[str, ...]
    pista: str


ENSAIOS = (
    Ensaio("Combate no Bosque",0,(796,CHAO),(),
           "Escute o morcego antes de avançar. Experimente J em sequência e S + J no ar."),
    Ensaio("Túnel do Córrego",1,(804,CHAO),("dreno",),
           "K deixa o trecho iluminado. Use Shift + direita para atravessar a corrente e E junto à lingueta."),
    Ensaio("Pulo entre paredes",0,(2200,CHAO),("meio","valvula","peca"),
           "Salte encostando na face riscada à direita. Pressione Espaço de novo e alterne entre as duas faces."),
    Ensaio("Descida pela grade",1,(2316,315),("meio","dreno","lingueta","ponte"),
           "Segure S ou seta para baixo e aperte Espaço. No fundo, E destrava a comporta."),
    Ensaio("Planeio no Taquaral",2,(2442,298),("meio","no","brasa","inimigo_1980"),
           "Corra até a ponta. Salte à direita e continue segurando Espaço enquanto cai."),
    Ensaio("Sentinela do Taquaral",2,(MEIO,CHAO),("meio","no","brasa"),
           "Escute o casco. Golpeie por trás ou de cima para abrir a trama que protege o bambuzal."),
    Ensaio("Mundo vertical",0,(630,CHAO),(),
           "Pressione E na fenda. Suba até a copa ou desça à cisterna. Tab abre o mapa das regiões visitadas."),

)


def preparar_ensaio(indice, dificuldade):
    cena=ENSAIOS[indice]
    jogo=Jornada("historia",dificuldade,cena.etapa)
    jogo.flags.update(cena.flags)
    jogo.entrar(cena.etapa)
    jogo.checkpoint=cena.pos
    jogo.reiniciar()
    jogo.lume.iframes=0.
    jogo.notificar(cena.pista,8)
    return jogo
