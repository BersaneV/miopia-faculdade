"""Sobreviventes originais, trabalhos escolhidos e luzes persistentes do mundo."""
from dataclasses import dataclass
import math
from .fases import CHAO, Objeto


@dataclass(frozen=True)
class Sobrevivente:
    id: str
    nome: str
    etapa: int
    ponto: tuple
    abrigo: tuple
    cor: tuple
    item: str
    encontro: str
    trilha: str
    casa: str


PESSOAS=(
    Sobrevivente('tila','Tila',0,(1635,1282),(470,CHAO),(224,183,106),'pavio',
        'Eu disse que não tinha medo. Depois comecei a contar as gotas para não ouvir o Caruncho. Você abriu a raiz? Então levo os casulos que sobraram. Diga onde minha luz ajuda mais.',
        'Vou marcar a grade e a forquilha. Se alguém chamar, respondo primeiro e conto as gotas depois.',
        'Mimo precisa de pavios. Fiz um para você; agora vou aquecer os casulos. Eu também posso ficar com medo aqui.'),
    Sobrevivente('bento','Bento',1,(3060,1102),(730,CHAO),(139,195,179),'polen',
        'Eu medi a subida três vezes e não subi nenhuma. A cheia levou minha régua. Se a água voltou a correr, posso seguir a margem. Você prefere que eu marque a volta ou prepare pólen no abrigo?',
        'Duas marcas de luz na margem, uma nos galhos de baixo. Não apagam quando alguém se atrasa. Medi isso também.',
        'Fiz um envelope de pólen para prender asas e desfazer projéteis. Só este lote ficou seco. O próximo precisa crescer.'),
    Sobrevivente('aru','Aru',1,(2300,790),(1060,CHAO),(180,163,221),'casulo',
        'Estas sementes lembram a chuva, mesmo secas. Eu queria salvar todas e fiquei para trás. Com Tila e Bento de volta, conseguimos abrir a estufa a leste. Antes, diga onde devo ajudar.',
        'Vou marcar a oficina e o caminho do jardim. A água não encontra uma semente que ninguém consegue alcançar.',
        'Costurei um casulo que segura um golpe. É o último tecido seco da oficina. Vou guardar o resto para quem ainda voltar.'),
)
POR_ID={p.id:p for p in PESSOAS}


def disponivel(j,p):
    if p.id in j.sobreviventes:return False
    if p.id=='tila':return not j.em_vertical and j.etapa==0 and 'caruncho_vencido' in j.flags
    if p.id=='bento':return not j.em_vertical and j.etapa==1 and 'ralo' in j.flags
    return j.em_vertical and {'tila','bento'}<=j.sobreviventes.keys()


def objetos(j):
    if j.modo!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False):return ()
    out=[]
    for p in PESSOAS:
        if disponivel(j,p):out.append(Objeto('resgate_'+p.id,'sobrevivente',*p.ponto,'Libertar '+p.nome))
        elif p.id in j.sobreviventes and not j.em_vertical and j.etapa==0:
            out.append(Objeto('casa_'+p.id,'sobrevivente',*p.abrigo,'Conversar com '+p.nome))
    return tuple(out)


def conversar(j,o):
    ident=o.id.split('_',1)[1];p=POR_ID[ident]
    if ident not in j.sobreviventes:
        if not disponivel(j,p):return
        j.sobreviventes[ident]={'oficio':'aguardando','premio':False}
        j.flags.add('ouviu_resgates')
        j.eventos.append('resgate')
        j.memorizar(p.nome+' voltou',p.encontro)
        texto=p.encontro
    else:
        oficio=j.sobreviventes[ident]['oficio']
        texto=p.trilha if oficio=='trilha' else p.casa if oficio=='abrigo' else p.encontro
    j.escolha_resgate=ident
    j.dialogo=(p.nome,texto+' Escolha: luz permanente em pontos da trilha, ou um mantimento único preparado no abrigo. Você pode mudar o trabalho depois; o mantimento não se repete.')
    j.eventos.append('pagina')


def escolher(j,indice):
    ident=j.escolha_resgate
    if ident not in j.sobreviventes or indice not in (0,1):return False
    p=POR_ID[ident];estado=j.sobreviventes[ident]
    estado['oficio']='trilha' if indice==0 else 'abrigo'
    if indice==1 and not estado['premio']:
        j.bolsa.receber(p.item,1);estado['premio']=True
        j.eventos.append('coleta')
    j.memorizar('Escolha de '+p.nome,p.trilha if indice==0 else p.casa)
    j.fechar_dialogo()
    j.notificar(p.nome+(': trilha marcada com luz.' if indice==0 else ': mantimento preparado; não se repete ao trocar o trabalho.'),6.)
    return True


def carregar(dados):
    if dados is None:return {}
    if not isinstance(dados,dict) or not set(dados)<=POR_ID.keys():raise ValueError('Sobreviventes inválidos')
    out={}
    for ident,estado in dados.items():
        if (not isinstance(estado,dict) or estado.get('oficio') not in ('aguardando','trilha','abrigo')
                or type(estado.get('premio')) is not bool):raise ValueError('Trabalho de sobrevivente inválido')
        out[ident]={'oficio':estado['oficio'],'premio':estado['premio']}
    return out


def fontes(j):
    if getattr(j,'modo',None)!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False):return []
    pontos=[]
    if j.concluida:
        if j.em_vertical:
            pontos=[(x,y,165) for x,y in ((260,950),(510,600),(1100,600),(660,1460),(1070,1740),(1890,760),(1850,1450),(2550,760),(3280,500),(4220,760),(4000,1450),(3000,1790))]
        else:
            pontos=[(x,CHAO-50,190) for x in range(180,j.fase.width,300)]
            if j.etapa==0:pontos.extend((x,y,170) for x,y in ((1700,620),(1960,810),(2300,1180),(1700,1230)))
            if j.etapa==1:pontos.extend((x,y,170) for x,y in ((2600,600),(2620,900),(2940,1070)))
    else:
        for ident,estado in j.sobreviventes.items():
            p=POR_ID[ident]
            if not j.em_vertical and j.etapa==0:pontos.append((p.abrigo[0],p.abrigo[1]-35,82))
            if estado['oficio']!='trilha':continue
            if ident=='tila' and not j.em_vertical and j.etapa==0:pontos.extend((x,y,150) for x,y in ((1640,415),(2190,410),(3350,230)))
            if ident=='bento' and not j.em_vertical and j.etapa==1:pontos.extend((x,y,150) for x,y in ((1290,407),(2600,900),(3020,1070)))
            if ident=='aru' and j.em_vertical:pontos.extend((x,y,150) for x,y in ((2280,755),(2700,755),(3270,370)))
    if j.em_vertical and 'jardim_plantado' in j.cartografia:pontos.append((3020,1790,180))
    cx,cy=j.camera,j.camera_y
    visiveis=[p for p in pontos if cx-p[2]<=p[0]<=cx+960+p[2] and cy-p[2]<=p[1]<=cy+540+p[2]]
    return sorted(visiveis,key=lambda p:math.dist(p[:2],j.lume.rect.center))[:4]


def mensagem_final(j):
    n=len(j.sobreviventes)
    if n==3:return 'Tila marca a primeira curva. Bento conta três luzes e ri da própria conta. Aru planta a semente onde antes só havia fuligem. A colônia voltou por caminhos que agora consegue ver.'
    if n:return f'{n} sobrevivente(s) responderam ao chamado. As raízes voltaram a correr, mas faltam vozes no abrigo. Lume pode retornar aos desvios e buscar quem ficou.'
    return 'As quatro raízes voltaram a correr. No abrigo ainda há três lugares vazios. A floresta reacesa permite procurar os sinais que Lume deixou para depois.'


def orientar(j):
    from .orientacao import _alvo,_superficie
    if j.modo!='historia' or not (j.missao=='resgates' or j.concluida and j.missao=='principal'):return None
    p=next((p for p in PESSOAS if p.id not in j.sobreviventes),None)
    if p is None:return None
    if j.em_vertical:
        if p.id=='aru':return _alvo(j,'resgate_aru','Aru na oficina','Encontre Aru na oficina',*p.ponto,p.encontro,opcional=True)
        return _alvo(j,'volta_bosque' if p.id=='tila' else 'volta_estaleiro','Volta à superfície',
                     'Volte ao Bosque' if p.id=='tila' else 'Volte ao Córrego',183 if p.id=='tila' else 2018,988 if p.id=='tila' else 790,
                     'O sobrevivente espera no desvio inferior da superfície. Use uma saída do Corte para retornar.',opcional=True)
    if j.etapa!=p.etapa and p.id!='aru':
        return _alvo(j,'rota_resgate',p.nome,'Siga até '+('o Bosque' if p.etapa==0 else 'o Córrego'),34 if j.etapa>p.etapa else 4670,CHAO,
                     'Os sinais de '+p.nome+' ficaram em '+('câmaras sob o Bosque.' if p.id=='tila' else 'galhos sob o Córrego.'),opcional=True)
    if p.id=='tila':
        from .raizes_bosque import passo_pedido
        if j.lume.rect.bottom<500:return _alvo(j,'grade_raizes','Sinal de Tila','Desça na grade do berçário',1640,CHAO,
                     'A marca de Mimo fica antes do marco do ramal. O pino da galeria abre a câmara de Tila.',opcional=True)
        if 'caruncho_vencido' not in j.flags:
            _,texto,ident=passo_pedido(j)
            o=next((o for o in j.objetos if o.id==ident),None)
            return _alvo(j,ident,'Caminho de Tila',texto,o.x if o else 1800,o.y if o else 1282,
                         texto+' Tila espera atrás da passagem guardada.',opcional=True)
    elif p.id=='bento':
        if 'ralo' not in j.flags:return _superficie(j)
        if j.lume.rect.bottom<500:return _alvo(j,'grade_bento','Sinal de Bento','Desça na grade das raízes',2600,CHAO,
                     'Após o ralo, S + Espaço na grade leva aos galhos inferiores. Bento está no fundo, à direita.',opcional=True)
    elif p.id=='aru':
        if j.etapa>1:return _alvo(j,'rota_aru','Aru na oficina','Volte ao Córrego',34,CHAO,'A oficina tem acesso pela ponte do Córrego ou pelo Corte do Bosque.',opcional=True)
        if j.etapa==1 and 'ponte' not in j.flags:return _superficie(j)
        x=630 if j.etapa==0 else 1944
        return _alvo(j,'entrada_aru','Aru na oficina','Entre no Corte da Figueira',x,CHAO,'Na oficina, siga à direita até a caixa de sementes de Aru.',opcional=True)
    return _alvo(j,'resgate_'+p.id,p.nome,'Libere '+p.nome,*p.ponto,p.encontro,opcional=True)
