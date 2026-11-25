"""Ensino contextual durante a partida. Não pausa e não exige abrir um menu."""
from .narrativa import ITENS

CURTAS={
    'primeiros_passos':'A / D move. Espaço salta. S agacha. E interage perto de pessoas e mecanismos.',
    'reservas':'Vida recebe dano. K e Ctrl usam brilho; se faltar, usam vida. Brilho não drena sozinho.',
    'salto_duplo':'Solte Espaço e aperte de novo no ar. Segure na queda para planar.',
    'combate':'J rápido, L pesado. Alterne J/L/J. S + J no ar rebate; Shift + direção + J avança.',
    'deslize':'S agacha. Shift + direção desliza sob raízes. Solte S para saltar.',
    'luz_combate':'K clareia. Ctrl + J / L carrega luz. No escuro, K atrapalha a visão dos inimigos.',
    'menus':'M / Tab abre o mapa. Esc / P pausa. F10 silencia; F11 alterna tela cheia.',
    'grade':'S + Espaço desce de grades e galhos. Terra firme não deixa passar.',
    'corda':'E na base sobe pelo cipó. Marcos guardam retorno, sem curar.',
    'parede':'Toque o tronco e salte para a parede oposta. Alterne as faces para subir.',
    'planagem':'Segure Espaço ao cair para planar. Solte ou aperte S para descer mais rápido.',
    'combos_luz':'Acertos devolvem brilho. Sem sofrer dano, o retorno cresce até 8×; um golpe ou queda zera.',
    'tochas':'Vença os guardas, recolha o núcleo com E e acenda a tocha. O globo Q/F ilumina outro local.'}


def atualizar(j,cmd):
    if (j.modo!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False) or
            getattr(j,'campo_testes',False) or j.dialogo or j.boss and not j.boss.vencido):return
    x,y=j.lume.rect.midbottom
    candidatos=[];condicoes=set()
    def dica(ident,cond,titulo,texto):
        if cond:condicoes.add(ident)
        if cond and ident not in j.tutorial:
            curto=CURTAS.get(ident,texto.split('.')[0]+'.')
            candidatos.append((ident,titulo,curto,texto))
    dica('primeiros_passos',j.etapa==0 and x<220,'O primeiro caminho','A / D ou setas movem Lume. Espaço salta. Seta para baixo ou S agacha. Continue pela direita; E conversa quando aparecer uma indicação.')
    dica('reservas',j.etapa==0 and x>=290,'Vida e brilho','Vida recebe dano. Brilho só gasta no K e nos ataques de luz. Ao zerar, o halo apaga; insistir numa habilidade usa vida. Derrotar inimigos recupera um pouco das duas barras.')
    dica('salto_duplo',j.etapa==0 and 220<x<600,'Outra batida de asas','Solte Espaço depois do salto e aperte novamente no ar: é o salto duplo. Segure Espaço durante a queda para planar sem limite de tempo.')
    dica('combate',j.etapa==0 and 620<x<900,'Cortes e respostas','J faz cortes rápidos. L faz um golpe pesado. Alterne J, L, J; use S + J no ar para atacar para baixo e rebater. Shift + direção + J avança. Observe o aviso antes de se aproximar.')
    dica('deslize',j.etapa==0 and 1090<x<1350,'Por baixo das raízes','S agacha. Shift + direção desliza pelos vãos baixos. Solte S antes de tentar saltar. Terra firme não permite descer; grades e galhos elevados permitem.')
    dica('luz_combate',j.etapa==0 and 1390<x<1530,'Luz contra a emboscada','K ilumina uma área ampla e atrapalha por instantes a visão dos inimigos no escuro. Ctrl + J / L executa golpes de luz, mais fortes e com custo de brilho. Ataques normais são gratuitos.')
    dica('menus',j.etapa==0 and 1840<x<2080,'Leve o caminho com você','M / Tab: mapa. + / - amplia; WASD ou arrasto move; botão direito marca e V muda o tipo. C centraliza no mapa. Esc / P pausa; R na pausa retorna ao marco. F10 silencia; F11 alterna tela cheia.')
    dica('grade',j.etapa==0 and 1530<x<1720 and y<500,'A floresta continua abaixo','Sobre uma grade ou galho elevado, segure S e aperte Espaço para descer. Pule por baixo de galhos para subir. M abre o mapa; ele guarda o que você já iluminou dentro da tela.')
    dica('corda',any(o.tipo=='corda' and abs(o.x-x)<100 for o in j.objetos),'Cipós e cordas','E junto à base faz Lume subir. Os cipós dos poços permitem retornar mesmo antes de vencer o guardião. O marco guarda seu retorno e não cura.')
    dica('parede',j.etapa==0 and 2110<x<2380,'Entre dois troncos','Salte encostado numa face de impulso e aperte Espaço novamente: Lume salta para a parede oposta. Alterne as duas faces e direcione a saída para o galho do alto.')
    dica('planagem',j.etapa==0 and 2700<x<3200,'Sustente as asas','Salte da borda e segure Espaço enquanto cai para planar continuamente. Soltar Espaço acelera a descida; S também encerra o planeio.')
    dica('combos_luz',j.lume.combo_acertos>=3,'Uma sequência sem ferimentos','Acertar golpes recupera um pouco de brilho. A cada três acertos sem sofrer dano, o retorno cresce exponencialmente, até 8×. Um golpe recebido ou uma queda zera o multiplicador.')
    dica('tochas',any(o.tipo=='lanterna' and abs(o.x-x)<100 and abs(o.y-y)<100 for o in j.objetos),'Conquiste a clareira','Derrote os guardas, recolha o núcleo com E e use E na tocha. A região fica nítida para sempre. O globo recebido pode ser fixado em outro caminho usando Q / F.')
    for item in ITENS:
        dica('item_'+item.id,j.bolsa.estoque[item.id]>0 and (item.id!='balsamo' or j.lume.vida<90 or j.etapa==0 and x>380),'Na sua bolsa: '+item.nome,item.descricao+(' Use E na tocha da clareira.' if item.id=='semente_luz' else ' Q escolhe; F usa uma carga. Sem efeito, a carga é guardada.' if not item.passivo else ' A melhoria já está ativa; não precisa equipar.'))
    genericas=lambda ident:ident in ('reservas','primeiros_passos','combos_luz') or ident.startswith('item_')
    locais=[c for c in candidatos if not genericas(c[0])]
    atual=getattr(j,'ensino_id','')
    if getattr(j,'ensino_ate',0)>j.tempo:
        if not locais or atual in condicoes and not genericas(atual):return
        candidatos=locais
    elif locais:candidatos=locais
    if candidatos:
        ident,titulo,texto,detalhe=candidatos[0];j.tutorial.add(ident)
        j.ensino_id=ident
        j.ensino_titulo=titulo;j.ensino_texto=texto;j.ensino_detalhe=detalhe;j.ensino_ate=j.tempo+6.


def desenhar(s,j):
    from .avisos import desenhar as aviso
    aviso(s,j)
