"""Jardim do Último Sinal, circuito contínuo a leste da oficina do Corte."""
import pygame
from .fases import Objeto,Terreno

LARGURA=4608
INICIO=2432
FLAGS=frozenset(('jardim_aberto','jardim_comporta','jardim_calha','jardim_plantado'))
SALAS=(('jardim_ponte','Ponte das Lanternas',pygame.Rect(2432,650,650,220)),
       ('jardim_copa','Jardim Suspenso',pygame.Rect(2640,200,1120,450)),
       ('jardim_estufa','Estufa Seca',pygame.Rect(3760,500,810,380)),
       ('jardim_calhas','Calhas da Memória',pygame.Rect(3600,880,970,700)),
       ('jardim_chuva','Câmara da Chuva',pygame.Rect(2432,1580,2138,328)))
CRIATURAS=(('cobra',2720,790),('vespa',2870,680),('sombra',3500,316),
           ('aranha',3710,790),('carabideo',4350,790),('vespa',4240,680),
           ('cobra',4020,1828),('sombra',3270,1828))


def setor(y,x):
    return next(((i,n) for i,n,r in SALAS if r.collidepoint(x,y)),('jardim','Jardim do Último Sinal'))


def terrenos(flags):
    out=[]
    def t(x,y,w,h,tipo):out.append(Terreno(pygame.Rect(x,y,w,h),tipo))
    # A antiga parede da oficina agora tem duas bocas, ambas com propósito.
    t(2394,0,38,680,'parede');t(2394,850,38,820,'parede')
    if 'jardim_aberto' not in flags:t(2394,680,38,170,'ninho_tranca')
    if 'jardim_plantado' not in flags:t(2394,1670,38,158,'ninho_tranca')
    for x,w in ((2427,373),(2950,420),(3490,450),(4260,310)):
        t(x,790,w,24,'ponte')
    t(4100,790,160,14,'grade')
    for x,y,w in ((2680,694,140),(2860,598,165),(3060,502,175),(3260,406,175),(3460,316,240),
                  (3060,316,160),(4060,886,180),(3920,982,180),(4080,1078,180),
                  (3900,1174,210),(3720,1270,210),(3890,1366,180),(3800,1462,480),(2670,1710,190)):
        t(x,y,w,17,'plataforma')
    # O primeiro apoio precisa de largura livre para pousar antes da raiz alta.
    t(3190,466,28,324,'parede')
    if 'jardim_comporta' not in flags:t(3960,0,30,790,'ninho_tranca')
    t(3870,1366,210,72,'teto')  # Vão de 24 px até o apoio de baixo: deslize.
    if 'jardim_calha' not in flags:t(3520,1492,34,336,'ninho_tranca')
    t(2432,1828,2138,80,'chao');t(4570,0,38,1908,'raiz_lisa')
    return out


def objetos(j):
    pts=[Objeto('jardim_entrada','jardim',2360,790,'Abrir a estufa dos três sinais'),
         Objeto('jardim_marco','jardim',2510,790,'Guardar retorno na ponte'),
         Objeto('jardim_polia','jardim',3900,790,'Encher o contrapeso da estufa'),
         Objeto('jardim_calha','jardim',3830,1462,'Soltar o tampão da calha'),
         Objeto('jardim_plantar','jardim',3020,1828,'Plantar a nascente'),
         Objeto('jardim_cipo_oeste','jardim',2520,1828,'Subir ao início do jardim'),
         Objeto('jardim_cipo_leste','jardim',4440,1828,'Subir à estufa')]
    if 'jardim_orvalho' not in j.cartografia:pts.append(Objeto('jardim_orvalho','jardim',3520,316,'Recolher orvalho da copa'))
    if 'jardim_brotos' not in j.cartografia:pts.append(Objeto('jardim_brotos','jardim',4500,790,'Recolher as sementes do viveiro'))
    if not j.bolsa.estoque['lente']:pts.append(Objeto('jardim_lente','jardim',3120,316,'Recolher a lente de casca'))
    pts.append(Objeto('jardim_memoria','jardim',2760,1710,'Ler a folha guardada sob a ponte'))
    for n,(x,y) in enumerate(((2770,770),(3470,385),(4070,1430))):
        if f'jardim_gota_{n}' not in j.cartografia:pts.append(Objeto(f'jardim_gota_{n}','orvalho_jardim',x,y,'Orvalho da estufa'))
    return tuple(pts)


def interagir(j,o):
    ident=o.id;c=j.cartografia
    if ident=='jardim_entrada':
        if len(j.sobreviventes)<3:
            faltam=', '.join(p for i,p in (('tila','Tila'),('bento','Bento'),('aru','Aru')) if i not in j.sobreviventes)
            j.notificar('A estufa tem três amarras: faltam '+faltam+'. M acompanha os sinais dos sobreviventes.',7.)
            return
        c.add('jardim_aberto');j.missao='jardim'
        j.memorizar('O jardim aberto','Tila corta a seda, Bento segura o peso e Aru solta as sementes presas. A oficina volta a alcançar a estufa.')
        j.notificar('Estufa aberta. Suba pelos galhos até o orvalho da copa; ele move o contrapeso a leste.',7.)
        j.eventos.extend(('porta','resgate'))
    elif ident=='jardim_marco':
        j.marco_vertical='jardim';j.checkpoint=(2510,790)
        j.notificar('Retorno guardado na ponte. O marco não cura.')
    elif ident.startswith('jardim_cipo_'):
        j.lume.em_corda=True;j.lume.corda_destino=790
        j.lume.rect.centerx=o.x;j.lume.vx=j.lume.vy=0.
        j.eventos.append('corda')
        j.notificar('O cipó sobe de volta à ponte da estufa.')
    elif ident=='jardim_orvalho':
        c.add(ident);j.eventos.append('coleta')
        j.notificar('Orvalho da copa guardado. Encha o contrapeso na ponte a leste.',7.)
    elif ident=='jardim_polia':
        if 'jardim_orvalho' not in c:
            j.notificar('O balde está vazio. Suba pelos galhos da ponte até a copa e recolha orvalho.',7.);return
        c.add('jardim_comporta');j.eventos.extend(('agua','porta'))
        j.notificar('O peso da água levanta a raiz. O vigia prende as sementes na estufa à direita.',7.)
    elif ident=='jardim_brotos':
        if 'vigia_4350' not in c:
            j.notificar('A trama do vigia prende o embrulho. Afaste o besouro para soltar as sementes.',6.);return
        c.add(ident);j.eventos.append('coleta')
        j.notificar('Sementes guardadas. Desça pela grade da estufa e solte o tampão da calha.',7.)
    elif ident=='jardim_calha':
        c.add(ident);j.eventos.extend(('agua','porta'))
        j.notificar('A calha corre para oeste. No fundo, plante as sementes na nascente.',7.)
    elif ident=='jardim_plantar':
        if not {'jardim_calha','jardim_brotos','jardim_orvalho'}<=c:
            j.notificar('A nascente precisa das sementes da estufa, do orvalho da copa e da calha aberta.',7.);return
        if 'jardim_plantado' not in c:
            c.add('jardim_plantado');j.bolsa.receber('pavio',2)
            j.eventos.extend(('raiz','resgate'))
            j.memorizar('A primeira muda','Aru guardou sementes enquanto a colônia discutia a água. Tila marca o canteiro e Bento divide o fluxo: nenhuma muda precisa da água toda.')
        j.notificar('Nascente plantada. A água abriu o retorno a oeste, junto ao viveiro antigo.',7.)
    elif ident=='jardim_lente':
        j.bolsa.receber('lente',1);j.aplicar_reliquias();j.eventos.append('coleta')
        j.memorizar('Lente de casca','Uma gota endurecida na casca concentra a luz de Lume. A visão portátil cresce 18 px. Luz atravessa terreno; o mapa registra somente o alcance iluminado dentro da tela.')
        j.notificar('Lente de casca: visão portátil +18. Só registra áreas iluminadas dentro da tela.',6.)
    elif ident=='jardim_memoria':
        if ident not in c:
            c.add(ident);j.bolsa.receber('balsamo',1);j.bolsa.receber('pavio',1)
        j.dialogo=('A folha que Aru não enviou',
                   '“Brasa pediu toda a água para o tronco. Eu vi as sementes secarem do outro lado e não disse nada. Guardei três. Se você encontrar esta folha, não deixe ninguém escolher sozinho para onde a água corre.” Ao lado há um pavio e um bálsamo, guardados uma única vez.')
        j.memorizar(*j.dialogo);j.eventos.append('pagina')


def atualizar(j):
    for o in objetos(j):
        if o.id.startswith('jardim_gota_') and j.lume.rect.inflate(14,16).collidepoint(o.x,o.y):
            j.cartografia.add(o.id);j.lume.energia=min(100.,j.lume.energia+20)
            j.eventos.append('coleta')


def objetivo(j):
    c=j.cartografia
    if 'jardim_plantado' in c:return 'comporta_viveiro','Volte ao viveiro pela passagem a oeste'
    if 'jardim_aberto' not in c:return 'jardim_entrada','Peça aos três sobreviventes para abrir a estufa'
    if 'jardim_orvalho' not in c:return 'jardim_orvalho','Suba à copa e recolha orvalho para o contrapeso'
    if 'jardim_comporta' not in c and 'jardim_brotos' not in c:return 'jardim_polia','Encha o contrapeso na ponte da estufa'
    if 'jardim_brotos' not in c:return 'jardim_brotos','Afaste o vigia e recolha as sementes da estufa'
    if 'jardim_calha' not in c:return 'jardim_calha','Desça pela grade e solte o tampão da calha'
    if 'jardim_plantado' not in c:return 'jardim_plantar','Plante as sementes na nascente do fundo'
    return 'comporta_viveiro','Volte ao viveiro pela passagem a oeste'


def orientar(j):
    from .orientacao import _alvo
    if 'jardim_plantado' in j.cartografia:return None
    if j.modo!='historia' or not (j.missao=='jardim' or j.concluida and j.missao=='principal' and len(j.sobreviventes)==3):return None
    if not j.em_vertical:
        x=630 if j.etapa==0 else 1944 if j.etapa==1 else 34
        return _alvo(j,'entrada_jardim','Jardim do Último Sinal','Volte ao Corte da Figueira',x,442,
                     'A estufa fica a leste da oficina. Os três sobreviventes ajudam a soltar a entrada.',opcional=True)
    ident,acao=objetivo(j)
    o=next((o for o in j.objetos if o.id==ident),None)
    if o is None:return None
    return _alvo(j,ident,'Jardim do Último Sinal',acao,o.x,o.y,
                 acao+'. A copa fica acima da ponte; a grade da estufa desce às calhas. Os cipós do fundo permitem retornar.',opcional=True)
