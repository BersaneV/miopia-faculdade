"""Três salas sob o Bosque, no mesmo espaço físico da trilha principal."""
import math
import pygame
from .fases import CHAO, Objeto, Terreno
from .taticas import Habitante

ALTURA=1400
ENTRADA=(1580,1720)
SAIDA=(2164,2264)
FUNDO=1282
CIPO_X=2180
SALAS=(('galeria','Galeria das Cascas',pygame.Rect(1474,510,636,350)),
       ('poco','Poço dos Cipós',pygame.Rect(2110,570,430,740)),
       ('camara','Câmara do Caruncho',pygame.Rect(1474,1048,606,260)))


def ativo(j):
    return (j.modo=='historia' and j.etapa==0 and not j.em_vertical
            and not hasattr(j,'sala_id') and not getattr(j,'ensaio_armas',False))


def setor(j):
    if not ativo(j) or j.lume.rect.bottom<510:return ''
    return next((nome for _,nome,r in SALAS if r.collidepoint(j.lume.rect.center)), 'Raízes do Bosque')


def terrenos(superficie, flags):
    out=[]
    for t in superficie:
        if t.tipo!='chao' or t.rect.top!=CHAO:
            out.append(t);continue
        segmentos=[(t.rect.left,t.rect.right)]
        for a,b in (ENTRADA,SAIDA):
            novos=[]
            for l,r in segmentos:
                if l<=a and r>=b:
                    if l<a:novos.append((l,a))
                    if b<r:novos.append((b,r))
                    out.append(Terreno(pygame.Rect(a,CHAO,b-a,14),'grade'))
                else:novos.append((l,r))
            segmentos=novos
        out.extend(Terreno(pygame.Rect(l,CHAO,r-l,t.rect.h),'chao') for l,r in segmentos)
    def add(x,y,w,h,tipo):out.append(Terreno(pygame.Rect(x,y,w,h),tipo))
    for x,y,w in ((1580,542,140),(1560,642,340),(1570,742,210),
                  (1860,742,165),(1830,642,130)):
        add(x,y,w,16,'plataforma')
    add(1474,842,636,60,'chao')
    add(2120,842,120,16,'plataforma')
    add(1450,570,24,712,'raiz_lisa')
    add(2080,902,30,152,'raiz_lisa')
    add(1474,FUNDO,1066,118,'chao')
    add(2510,570,30,712,'raiz_lisa')
    add(1474,1030,636,24,'chao')
    if 'porta_ninho' not in flags:add(2080,1054,30,228,'ninho_tranca')
    if 'cipo_estendido' not in flags:add(2164,620,100,28,'ninho_tranca')
    # A saída superior tem grade; a espessura do chão não atravessa o eixo.
    return out


def objetos(j):
    pontos=[Objeto('placa_raizes','raizes',1538,CHAO,'Ler as marcas de Mimo'),
            Objeto('pista_pino','raizes',1880,842,'Ler o risco que aponta ao pino'),
            Objeto('cipos_baixo','raizes',CIPO_X,FUNDO,'Subir pelo cipó'),
            Objeto('porta_ninho','raizes',2148,FUNDO,'Erguer a raiz do viveiro')]
    if 'pino_ninho' not in j.flags:pontos.append(Objeto('pino_ninho','raizes',1940,642,'Recolher o pino de casca'))
    if 'caruncho_vencido' in j.flags:
        if 'ambar_ninho' not in j.flags:pontos.append(Objeto('ambar_ninho','raizes',1580,FUNDO,'Recolher o âmbar do berçário'))
        pontos.append(Objeto('trava_cipo','raizes',1510,FUNDO,'Estender o cipó até a forquilha'))
    return pontos


class Caruncho(Habitante):
    nome='Caruncho do Viveiro'
    def repor(self):
        super().repor()
        self.max_vida=self.vida=22
        self.ativo=True
        self.rect.size=(76,48);self.rect.midbottom=self.origem
        self.ritmo=1.12
        self.fase=1
        self.reacao_defesa=0.
        self.pos_manobra=pygame.Vector2(self.rect.center)

    def update(self,dt,lume,raio,restaurado,terrenos):
        self.reacao_defesa=max(0.,self.reacao_defesa-dt)
        if self.vida<=self.max_vida/2 and self.fase==1:
            self.fase=2;self.ritmo=1.26
            self.plano=[]
            # Troca visível de fase; não inicia dano sem outro aviso.
            self.estado,self.t='recuo',.65
        return super().update(dt,lume,raio,restaurado,terrenos)

    def acertar(self,arma,area,clarao,lume):
        estado,tempo,plano=self.estado,self.t,list(self.plano)
        resultado=super().acertar(arma,area,clarao,lume)
        if resultado=='acerto' and self.ativo and self.estado=='atordoado':
            pesado=arma.tipo in ('corte3','queda','avanco')
            if not pesado or self.reacao_defesa>0:
                self.estado,self.t,self.plano=estado,tempo,plano
            else:self.reacao_defesa=1.2
        return resultado


def povoar(j):
    criaturas=[('cobra',1985,842),('morcego',1875,717)]
    for tipo,x,y in criaturas:
        if f'inimigo_{x}' not in j.flags:j.inimigos.append(Habitante(tipo,x,y,dificuldade=j.dificuldade))
    if 'caruncho_vencido' not in j.flags and 'inimigo_1800' not in j.flags:
        j.inimigos.append(Caruncho('carabideo',1800,FUNDO,dificuldade=j.dificuldade))


def interagir(j,o):
    ident=o.id
    if ident=='placa_raizes':
        j.flags.add('pedido_raizes')
        j.missao='pedido_raizes'
        j.dialogo=('A reserva do berçário',
            'Mimo desenhou três níveis: galeria, poço e viveiro. O pino de casca ficou no galho alto da galeria. '
            'Ele abre a raiz presa à esquerda do fundo do poço. O Caruncho guarda o âmbar de que Mimo precisa '
            'para ampliar sua bolsa de bálsamos. S + Espaço na grade desce; o cipó no fundo sempre permite voltar.')
        j.memorizar(*j.dialogo);j.eventos.append('pagina')
    elif ident=='pino_ninho':
        j.flags.add(ident);j.eventos.append('coleta')
        j.notificar('Pino de casca recolhido. Ele levanta a porta no fundo do poço, à esquerda.',6.)
    elif ident=='pista_pino':
        j.dialogo=('Dois galhos acima',
                   'Mimo riscou um pino e duas setas para cima. O sulco sobe pelo galho à direita e termina no apoio seguinte. Salte até o primeiro galho e salte outra vez; recolha o pino com E.')
        j.memorizar(*j.dialogo);j.eventos.append('pagina')
    elif ident=='porta_ninho':
        if 'porta_ninho' in j.flags:
            j.notificar('A raiz está erguida. O viveiro continua à esquerda.');return
        if 'pino_ninho' not in j.flags:
            j.notificar('Falta o pino de casca. Ele está no galho alto da galeria, acima e à esquerda.',6.);return
        j.flags.add(ident);j.eventos.extend(('madeira','porta'))
        j.notificar('A raiz sobe com o pino. O Caruncho guarda a reserva adiante.',6.)
    elif ident=='cipos_baixo':
        l=j.lume
        l.em_corda=True;l.corda_destino=CHAO if 'cipo_estendido' in j.flags else 842
        l.rect.centerx=CIPO_X;l.vx=l.vy=0.;l.chao=False
        j.eventos.append('corda')
        j.notificar('O cipó sobe até a forquilha.' if 'cipo_estendido' in j.flags else
                    'O cipó leva à galeria. Após o Caruncho, abra o nó por dentro para chegar à superfície.')
    elif ident=='ambar_ninho':
        j.flags.update(('pedido_raizes','ambar_ninho'));j.missao='pedido_raizes'
        j.eventos.append('coleta');j.notificar('Âmbar do berçário recolhido. Leve a Mimo no abrigo; antes, solte o nó à esquerda.',7.)
    elif ident=='trava_cipo':
        if 'cipo_estendido' not in j.flags:
            j.flags.add('cipo_estendido');j.eventos.extend(('corda','porta'))
        j.notificar('Atalho aberto. E no cipó do poço sobe fisicamente até a forquilha.',6.)


def atualizar(j,dt):
    for ident,_,r in SALAS:
        if r.collidepoint(j.lume.rect.center):j.flags.add('viu_raizes_'+ident)
    if 'inimigo_1800' in j.flags and 'caruncho_vencido' not in j.flags:
        j.flags.add('caruncho_vencido')
        j.notificar('O Caruncho recua. Recolha o âmbar à esquerda e solte o nó do cipó.',7.)
        j.eventos.append('vencer')
    from .sinalizacao import camera_vertical
    camera_vertical(j,ALTURA,dt)


def camera(j):
    from .sinalizacao import camera_vertical
    camera_vertical(j,ALTURA)


def limite_queda(j):
    return ALTURA+28 if 1480<=j.lume.rect.centerx<=2540 else 550


def fala_mimo(j):
    if 'ambar_ninho' in j.flags and 'pedido_raizes_entregue' not in j.flags:
        j.flags.update(('pedido_raizes','pedido_raizes_entregue'))
        j.bolsa.receber('frasco',1);j.bolsa.receber('balsamo',1)
        j.memorizar('A reserva do berçário · entregue',
                    'Mimo recebeu o âmbar do Caruncho. A bolsa comporta três bálsamos e recebeu uma carga. V alterna o Espinho e a Agulha de taquara.')
        j.eventos.append('coleta')
        return ('Com esse âmbar vedei outra ampola. Cabem três bálsamos na bolsa, e deixei uma carga. '
                'Leve também a Agulha de taquara. Ela alcança mais longe, mas demora a voltar à guarda. '
                'Use V para alternar entre a agulha e o espinho.')
    if ('pedido_raizes' in j.flags and 'pedido_raizes_entregue' not in j.flags
            and 'encomenda_entregue' in j.flags):
        return 'Falta o âmbar no viveiro sob o Bosque. Meus riscos estão junto à grade antes do marco do ramal. O pino no galho alto da galeria abre a porta no fundo do poço. O cipó permite voltar mesmo se o Caruncho resistir.'
    return None


def passo_pedido(j):
    flags=j.historico.get((j.volta,0),set())
    if 'pedido_raizes_entregue' in flags:return 'Concluída','A bolsa comporta três bálsamos. V alterna as armas.',''
    if 'ambar_ninho' in flags:return 'Entregar','Leve o âmbar do berçário a Mimo, no abrigo do Bosque.','npc:Mimo'
    if 'caruncho_vencido' in flags:return 'Em curso','Recolha o âmbar atrás do viveiro e solte o nó do cipó.','ambar_ninho'
    if 'porta_ninho' in flags:return 'Em curso','Afaste o Caruncho do Viveiro, atrás da raiz erguida.','caruncho_alvo'
    if 'pino_ninho' in flags:return 'Em curso','Desça ao fundo do poço e use o pino na porta à esquerda.','porta_ninho'
    return 'Em curso','Desça pela grade; os riscos no chão da galeria apontam dois galhos acima até o pino.','pino_ninho'


def orientar(j):
    from .orientacao import _alvo
    if not ativo(j):return None
    rastreando=j.missao=='pedido_raizes' and 'pedido_raizes_entregue' not in j.flags
    fundo=j.lume.rect.bottom
    if rastreando:
        estado,texto,ident=passo_pedido(j)
        if ident=='caruncho_alvo':
            e=next((e for e in j.inimigos if isinstance(e,Caruncho) and e.ativo),None)
            return _alvo(j,ident,'Caruncho do Viveiro','Afaste o Caruncho',e.rect.centerx if e else 1800,FUNDO,
                         'A carapaça resiste de frente. Use o terceiro corte, ataque por cima ou alcance as costas; pule as ondas.',opcional=True)
        if ident=='npc:Mimo' and fundo>500:
            if j.lume.em_corda:
                return _alvo(j,'subida_cipo','Subida ao Bosque','Continue pelo cipó',CIPO_X,CHAO,texto,opcional=True)
            if fundo>850:
                return _alvo(j,'cipos_baixo','Cipó de retorno','Suba pelo cipó',CIPO_X,FUNDO,
                             'E no cipó do poço sobe. Se ainda não estendeu o cipó, ele para na galeria; siga os galhos à grade.',opcional=True)
            return _alvo(j,'grade_raizes','Retorno à trilha','Suba pelos galhos até a grade',1640,CHAO,texto,opcional=True)
        if fundo<500 and ident!='npc:Mimo':
            return _alvo(j,'grade_raizes','Grade das raízes','Desça pela grade com S + Espaço',1640,CHAO,
                         'A grade fica junto das marcas de Mimo, antes do marco do ramal. A descida e o retorno são pelo mesmo mundo.',opcional=True)
        o=next((o for o in j.objetos if o.id==ident or ident=='npc:'+o.nome),None)
        if o:return _alvo(j,o.id,'A reserva do berçário',texto,o.x,o.y,texto,opcional=True)
    if fundo>500:
        x,y=(CIPO_X,FUNDO) if fundo>850 else (1640,CHAO)
        return _alvo(j,'retorno_raizes','Retorno ao Bosque','Retorne à trilha principal',x,y,
                     'Desvio opcional. No fundo, E no cipó leva à galeria; os galhos voltam à grade. A missão principal segue pela forquilha.',opcional=True)
    return None
