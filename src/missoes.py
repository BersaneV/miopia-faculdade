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
    local: str = ""


def conhecidas(j):
    out=[Missao("principal","O caminho dos sobreviventes","Colônia da Figueira",
                "Quatro raízes",j.etapa,"Concluída" if j.concluida else "Em curso",
                "As raízes estão acesas. Procure os sobreviventes e explore a estufa que ficou para trás." if j.concluida else
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
                          'Ampola para três bálsamos, uma carga e a Agulha de taquara.',alvo,
                          'O âmbar do viveiro permite vedar outra ampola de viagem.'))
    if any('ouviu_resgates' in f for f in j.historico.values()) or j.sobreviventes:
        from .resgates import PESSOAS
        falta=next((p for p in PESSOAS if p.id not in j.sobreviventes),None)
        pistas={'tila':'Procure Tila na câmara sob a galeria do Bosque. O Caruncho guarda a passagem.',
                'bento':'Procure Bento nos galhos inferiores do Córrego, depois do ralo.',
                'aru':'Procure Aru na oficina do Corte. Tila e Bento precisam voltar primeiro.'}
        out.append(Missao('resgates','As três vozes da colônia','Mimo','Colônia',falta.etapa if falta else 0,
                          'Em curso' if falta else 'Concluída',pistas[falta.id] if falta else 'Os três sobreviventes voltaram.',
                          'Companheiros no abrigo: escolha luz na trilha ou um mantimento único.',
                          'resgate_'+falta.id if falta else '', 'A colônia precisa de quem cuida, transporta água e planta.'))
    if 'jardim_aberto' in j.cartografia or len(j.sobreviventes)==3:
        from .jardim import objetivo
        ident,passo=objetivo(j)
        out.append(Missao('jardim','A primeira muda','Aru','Nascente do Jardim',0,
                          'Concluída' if 'jardim_plantado' in j.cartografia else 'Em curso',passo,
                          'Retorno ao viveiro e dois pavios; dois segredos na rota.',ident,
                          'Água e sementes precisam chegar ao mesmo canteiro.'))
    from . import fio_corte
    if fio_corte.CONHECIDA in j.cartografia:
        estado, passo, alvo = fio_corte.passo(j)
        out.append(Missao(fio_corte.ID, fio_corte.TITULO, "Fio", "Margens da cisterna", 1,
                          estado, passo, fio_corte.RECOMPENSA, alvo, fio_corte.MOTIVO,
                          local="Corte da Figueira"))
    from . import galeria_taquaral as galeria
    flags_taquaral = j.historico.get((j.volta, 2), set())
    if galeria.CONHECIDA in flags_taquaral:
        estado, passo, alvo = galeria.passo_pedido(flags_taquaral)
        out.append(Missao(galeria.PEDIDO, galeria.NOME_PEDIDO, "Risca", "Veneziana", 2,
                          estado, passo, galeria.PREMIO, alvo, galeria.MOTIVO, local=galeria.TITULO))
    from . import resgates, rotas_borda
    for ident, trabalho in rotas_borda.POSTOS.items():
        finalizado = trabalho.corda.id in j.historico.get((j.volta, trabalho.etapa), ())
        if finalizado or rotas_borda.posto(j, ident) is not None:
            nome = resgates.POR_ID[ident].nome
            posto = rotas_borda.PREFIXO + ident
            out.append(Missao(posto, trabalho.titulo, nome, FASES[trabalho.etapa].name, trabalho.etapa,
                              "Concluída" if finalizado else "Em curso",
                              trabalho.registro if finalizado else trabalho.pista,
                              trabalho.corda.nome + ".", "" if finalizado else posto))
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
