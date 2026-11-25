"""Cenas isoladas da campanha para as rodadas de avaliação com o jogador."""
from dataclasses import dataclass
from .fases import ARENA, CHAO, FASES, MEIO
from .sala_aranha import ABRIGO, DueloAranha, SALA_ARANHA, SEMENTE_ARANHA
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
    Ensaio("Estaleiro das Folhas",1,(1944,CHAO),("dreno","lingueta","ponte","meio"),
           "E na fenda leva à oficina. Desça pelas grades do viveiro e abra o retorno à cisterna. Para saltar de novo, solte Espaço e aperte no ar."),
    Ensaio("Asa Fendida",0,(ARENA-20,CHAO),("meio","marco","peca",FASES[0].preparo),
           "Entre pela direita. Observe a altura da asa antes de escolher entre agachar e saltar. A raiz riscada expõe o dorso."),
    Ensaio("Tecelã do Vão",1,(ARENA-20,CHAO),("meio","marco","dreno","lingueta","ponte",FASES[1].preparo),
           "Entre pela direita. Observe as duas trajetórias de seda depois do primeiro corte. A roda a oeste abre a cortina de água."),
    Ensaio("Raízes do Córrego",1,(2600,CHAO),("meio","dreno","lingueta","ponte","ralo"),
           "S + Espaço na grade desce sem trocar de mapa. Explore até a membrana de libélula e suba pelos galhos a leste."),
    Ensaio("Patrulha em dupla",0,(1510,CHAO),(),
           "Morcego e aranha usam vinte sequências por espécie. Q/F usa ferramentas; o pólen retarda asas e o tanino rompe carapaça."),
    Ensaio('Casco Oco',2,(ARENA-20,CHAO),('meio','marco','no','brasa','vagem'),
           'Salte o chifre, saia da aterrissagem e observe o segundo aviso na fase II. E empurra a seiva até o aro; E na brasa abre a carapaça.'),
    Ensaio('A Coruja',3,(ARENA-20,CHAO),('meio','marco','roldana','contrapeso','eco_antigo'),
           'Garras, rasantes e penas têm avisos próprios. E duas vezes na roda chama a Coruja à raiz direita. Suba nos apoios e use K perto da face exposta.'),
    Ensaio('Oficina dos Espinhos',0,(160,CHAO),(),
           'V alterna espinho rápido e agulha longa, que custa 2 de luz por corte. Compare em dois alvos imóveis. E no abrigo restaura luz e alvos. Protótipo isolado.'),
    Ensaio('Raízes do Bosque',0,(1538,CHAO),('pedido_raizes','inimigo_1548','inimigo_1660','inimigo_1978'),
           'Leia a marca com E. S + Espaço na grade à direita desce por três salas no mesmo mapa. O pino da galeria abre o viveiro; o cipó do poço sempre permite voltar.'),
    Ensaio('Caruncho do Viveiro',0,(2230,1282),('pedido_raizes','pino_ninho','porta_ninho'),
           'Siga à esquerda. Carapaça frontal: terceiro corte, ataque por cima ou pelas costas. Pule as ondas e leia o segundo golpe. Recolha o âmbar e solte o nó ao fundo após vencer.'),
    Ensaio('Resgate no berçário',0,(1635,1282),('pino_ninho','porta_ninho','caruncho_vencido'),
           'E conversa com Tila. Leia as páginas e escolha entre marcar a trilha com luz ou preparar um pavio único. Esc deixa a escolha para depois.'),
    Ensaio('Jardim do Último Sinal',1,(2510,790),(),
           'Os três sobreviventes abriram a estufa. Suba aos galhos, busque orvalho, mova o contrapeso e recupere as sementes. A grade desce às calhas; cipós retornam sem portal.'),
    Ensaio('Último chamado',3,(ARENA+75,CHAO),('meio','marco','roldana','contrapeso','eco_antigo'),
           'Última fase isolada: E recolhe uma gota por ninho, K devolve o sinal. Cruze a arena entre os três ninhos, saltando os rasantes anunciados.'),
    Ensaio('Floresta reacesa',0,(450,CHAO),(),
           'Pós-jogo isolado. Explore as luzes locais dos sobreviventes e use M: a cartografia continua exigindo visão real. O save da História é preservado.'),
    Ensaio('Escuta dos ataques',0,(160,CHAO),(),
           'J escolhe a família; K escolhe a espécie; E toca o aviso à direita. Trinta avisos próprios. Compare por ouvido antes de avaliar no combate.'),
    Ensaio("Duelo da aranha",0,ABRIGO,(),
           "Referência S02 de fio e salto, com replay. Os vinte combos novos estão em Patrulha em dupla e na História. E recupera luz no abrigo."),
)
INDICE_ARANHA = len(ENSAIOS) - 1


def preparar_ensaio(indice, dificuldade, semente=SEMENTE_ARANHA):
    if indice == INDICE_ARANHA:
        return DueloAranha(dificuldade, semente)
    cena=ENSAIOS[indice]
    if cena.nome=='Escuta dos ataques':
        from .escuta import Escuta
        return Escuta(dificuldade)
    if cena.nome=='Oficina dos Espinhos':
        from .oficina_armas import Oficina
        jogo=Oficina(dificuldade)
        jogo.notificar(cena.pista,8)
        return jogo
    jogo=Jornada("historia",dificuldade,cena.etapa)
    jogo.flags.update(cena.flags)
    jogo.entrar(cena.etapa)
    jogo.checkpoint=cena.pos
    jogo.reiniciar()
    if cena.nome in ('Jardim do Último Sinal','Último chamado','Floresta reacesa'):
        jogo.sobreviventes={i:{'oficio':'trilha','premio':False} for i in ('tila','bento','aru')}
    if cena.nome=='Jardim do Último Sinal':
        from .corte_vertical import entrar
        jogo.cartografia.add('jardim_aberto');jogo.missao='jardim'
        entrar(jogo,'jardim');jogo.bolsa.receber('balsamo',2)
    elif cena.nome=='Último chamado':
        from .chefes import Encontro
        from .ultimo_chamado import iniciar
        jogo.boss=Encontro(3,ARENA,CHAO,despertar=True,aliados=3)
        iniciar(jogo.boss,jogo.eventos)
    elif cena.nome=='Floresta reacesa':
        jogo.concluida=True
        for n in range(4):
            jogo.historico.setdefault((0,n),set()).update(('raiz','chefe','meio','marco',FASES[n].preparo,*FASES[n].mecanismos))
        jogo.restauradas=4
    if cena.nome=="Patrulha em dupla":
        jogo.ensaio_tatico=True
        jogo.bolsa.receber("polen",2)
        jogo.bolsa.receber("tanino",2)
    if cena.nome in ('Raízes do Bosque','Caruncho do Viveiro'):
        jogo.missao='pedido_raizes'
        jogo.bolsa.receber('balsamo',1)
    jogo.lume.iframes=0.
    jogo.notificar(cena.pista,8)
    return jogo
