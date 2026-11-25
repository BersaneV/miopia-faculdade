"""Pedidos conhecidos e rastreio persistente. Consultar a lista não muda a jornada."""
from dataclasses import dataclass
from .fases import FASES
from .narrativa import PEDIDOS, POR_ID


@dataclass(frozen=True)
class Missao:
    id: str
    titulo: str
    origem: str
    destino: str
    etapa: int
    estado: str
    passo: str
    recompensa: str
    alvo_id: str = ""
    motivo: str = ""


def conhecidas(j):
    out=[Missao("principal","O caminho dos sobreviventes","Colônia da Figueira",
                "Quatro raízes",j.etapa,"Em curso",
                "Recolha orvalho, reabra as passagens e enfrente a guardiã de cada raiz.",
                "Água e passagem para quem ficou nas bordas.",motivo="Os sobreviventes precisam voltar à figueira antes de o orvalho secar.")]
    if j.modo!="historia" or hasattr(j,"sala_id"):
        return tuple(out)
    for etapa,pedido in enumerate(PEDIDOS):
        flags=j.historico.get((j.volta,etapa),set())
        if "pedido_aceito" not in flags:continue
        faltando=next(((flag,texto) for flag,texto in pedido.passos if flag not in flags),None)
        if "pedido_entregue" in flags:
            estado,passo,alvo="Concluída",pedido.depois,""
        elif faltando:
            flag,passo=faltando;estado="Em curso";alvo="no" if flag=="chamado_eco" else flag
            # Um pedido pode depender de um mecanismo ainda sem a sua peça.
            visitados=set()
            while alvo in FASES[etapa].mecanismos and alvo not in visitados:
                visitados.add(alvo)
                requer=FASES[etapa].mecanismos[alvo].requer
                if not requer or requer in flags:break
                alvo=requer
        else:
            estado,passo,alvo="Entregar",pedido.entregar,"npc:"+pedido.destino
        premio=", ".join(f"{n} × {POR_ID[item].nome}" for item,n in pedido.itens)
        out.append(Missao(f"pedido_{etapa}",pedido.titulo,pedido.origem,pedido.destino,
                          etapa,estado,passo,premio,alvo,pedido.convite))
    flags=j.historico.get((j.volta,0),set())
    if "encomenda_aceita" in flags:
        pronta="encomenda_recolhida" in flags
        feita="encomenda_entregue" in flags
        out.append(Missao("entrega_mimo","A mochila dos casulos","Mimo","Mimo",0,
            "Concluída" if feita else "Entregar" if pronta else "Em curso",
            "Pacote entregue a Mimo." if feita else "Leve o pacote a Mimo, no abrigo da entrada." if pronta else
            "Suba à varanda acima de Nira com dois saltos e recolha o pacote com E.",
            "3 × Tanino de casca: cortes atravessam carapaças por 18 s.",
            "npc:Mimo" if pronta else "encomenda_mimo",
            "Mimo precisa da mochila para preparar proteção para os casulos."))
    if 'pedido_raizes' in flags:
        from .raizes_bosque import passo_pedido
        estado,passo,alvo=passo_pedido(j)
        out.append(Missao('pedido_raizes','A reserva do berçário','Mimo','Mimo',0,estado,passo,
                          'Ampola do berçário: capacidade de 3 bálsamos e uma carga.',alvo,
                          'O âmbar do viveiro permite vedar outra ampola de viagem.'))
    return tuple(out)


def rastreada(j):
    lista=conhecidas(j)
    ident=j.missao
    if ident=="secundaria":ident=f"pedido_{j.etapa}"
    return next((m for m in lista if m.id==ident and m.estado!="Concluída"),lista[0])


def selecionar(j,ident):
    missao=next((m for m in conhecidas(j) if m.id==ident),None)
    if missao is None or missao.estado=="Concluída":
        j.notificar("Este pedido já foi concluído ou ainda não foi conhecido.")
        return False
    j.missao=ident
    j.notificar("Acompanhando: "+missao.titulo)
    return True
