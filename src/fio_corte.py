"""A rotina de Fio e o pedido que liga o Viveiro à cisterna."""
from .fases import CHAO, Objeto

ID = "pedido_fio"
TITULO = "O fio da cheia"
CONHECIDA = "fio_cheia_conhecida"
CARRETEL = "carretel_fio"
REPARADA = "passarela_fio"
MARCA = "leu_placa_viveiro"
MOTIVO = "Fio quer comparar as alturas da água e recuperar seu carretel de medir."
RECOMPENSA = "Uma passarela na cisterna e um Globo de vaga-lume para fixar luz."
OFICINA = (1834, 790)
MARGEM = (1310, 1828)
PASSARELA = (930, 1828, 67, 14)
PECA = Objeto(CARRETEL, "carretel_fio", 1176, 1576, "Recolher o carretel de Fio")


def moradora(j):
    na_margem = "viveiro_aberto" in j.cartografia and j.comporta_inicio is None
    return Objeto("fio_corte", "fio_corte", *(MARGEM if na_margem else OFICINA), "Conversar com Fio")


def objetos(j):
    fio = moradora(j)
    return (fio,) if CARRETEL in j.cartografia else (fio, PECA)


def luzes(j):
    x, y, largura, _ = PASSARELA
    if REPARADA in j.cartografia and j.camera-76 <= x <= j.camera+1036 and j.camera_y+616 >= y:
        return ((x+largura//2, y-32, 76),)
    return ()


def passo(j):
    memoria = j.cartografia
    if REPARADA in memoria:
        return "Concluída", "A passarela de Fio une as margens da cisterna.", ""
    if MARCA not in memoria:
        return "Em curso", "Leia os riscos nos berços. Da oficina, desça pela grade. Do fundo do viveiro, suba pelos apoios a leste.", "placa_viveiro"
    if "viveiro_aberto" not in memoria:
        return "Em curso", "Use E na roda no fundo do Viveiro para abrir a passagem oeste.", "comporta_viveiro"
    if CARRETEL not in memoria:
        return "Em curso", "Suba pelos três apoios acima da saída da cisterna até o carretel de Fio.", CARRETEL
    return "Entregar", "Desça dos apoios e leve o carretel a Fio, na margem junto à comporta.", "fio_corte"


def interagir(j, o):
    memoria = j.cartografia
    primeiro_encontro = CONHECIDA not in memoria
    memoria.add(CONHECIDA)
    if o.tipo == "carretel_fio":
        if CARRETEL in memoria:
            return
        memoria.add(CARRETEL)
        j.memorizar("As duas voltas do carretel",
                    "A seda velha está manchada de barro seco. A volta nova tem um nó e cheiro de chuva. "
                    "Fio anotou o nível da água em duas noites diferentes.")
        dica = "Entregue-o a Fio na margem." if j.missao == ID else "M abre os pedidos."
        j.notificar("Carretel guardado. " + dica, 4.)
        j.eventos.append("coleta")
        return

    if primeiro_encontro:
        j.notificar("O fio da cheia entrou nos pedidos do mapa (M).", 4.)
    posicao = moradora(j).y
    estado, pista, _ = passo(j)
    if estado == "Concluída":
        texto = ("A seda esticou um pouco depois da primeira travessia. Já fiz outro nó. "
                 "Passe por ali quando quiser. Vou esperar para ver se a água respeita a minha marca desta vez.")
    elif posicao == OFICINA[1]:
        texto = ("Medi a água em voltas de seda. Na noite do raio, já havia barro seco nos berços de baixo. "
                 "Leia os riscos onde guardei os casulos. Se abrir a comporta, eu vou medir de novo na cisterna.")
    elif estado == "Entregar":
        memoria.add(REPARADA)
        j.bolsa.receber("globo", 1)
        texto = ("O barro é da noite em que Casca virou a água. O nó é da noite em que tirei os casulos por causa da chuva. "
                 "Guardei as duas medidas no mesmo carretel. Com esta seda, amarro a passarela sobre a fenda. "
                 "Leve também um Globo de vaga-lume. Q escolhe e F fixa a luz no lugar em que você estiver.")
        j.memorizar(TITULO, "As marcas de Fio separam o desvio antigo da retirada durante a tempestade. "
                             "A passarela da cisterna foi reparada. Fio entregou um Globo de vaga-lume.")
        j.eventos.extend(("coleta", "madeira"))
        if j.missao == ID:
            j.missao = "principal"
    else:
        texto = "Daqui da margem eu ouço a água bater nas duas paredes. " + pista
    j.dialogo = ("Fio", texto)


def orientar(j):
    if j.missao != ID or CONHECIDA not in j.cartografia or REPARADA in j.cartografia:
        return None
    from dataclasses import replace
    from .orientacao import _alvo, _superficie

    if not j.em_vertical:
        if j.etapa > 1:
            return _alvo(j, "voltar", TITULO, "Volte ao Córrego", 34, CHAO,
                         "Use E na saída à esquerda desta região para retornar ao Córrego.", opcional=True)
        entrada = "corte_bosque" if j.etapa == 0 else "corte_estaleiro"
        o = next((o for o in j.objetos if o.id == entrada), None)
        if o is None:
            return replace(_superficie(j), motivo="Abra a ponte do Córrego para chegar ao Estaleiro por este lado.")
        return _alvo(j, o.id, TITULO, "Entre no Corte da Figueira", o.x, o.y,
                     "Use E na fenda. Da galeria, salte duas vezes no beiral à direita para subir à oficina.", opcional=True)

    from . import corte_vertical as corte

    _, pista, ident = passo(j)
    x, y = j.lume.rect.midbottom
    setor = corte.setor(j.lume.rect.centery, x)[0]
    if setor == "estaleiro":
        return _alvo(j, "grade_viveiro", TITULO, "Desça pela grade do estaleiro", 2240, 790,
                     "Use S + Espaço na grade acima dos berços. A roda do Viveiro fica no fundo a oeste.", opcional=True)
    if ("viveiro_aberto" not in j.cartografia and x < corte.COMPORTA.left and y > 1600):
        ralo_aberto = "ralo_aberto" in j.cartografia
        ident = "carro_baixo" if ralo_aberto else "ralo_cisterna"
        pista = ("Use o contrapeso para subir. Da copa, desça pelos galhos à direita até a galeria e suba à oficina."
                 if ralo_aberto else "Use K e E no ralo a oeste para liberar o contrapeso que leva à copa.")
    o = next((o for o in j.objetos if o.id == ident), None)
    if o is None:
        return None
    acao = {"placa_viveiro": "Leia os riscos nos berços", "comporta_viveiro": "Abra a comporta",
            CARRETEL: "Busque o carretel nos apoios", "fio_corte": "Entregue o carretel a Fio",
            "ralo_cisterna": "Abra o ralo para subir", "carro_baixo": "Suba no contrapeso"}[ident]
    return replace(_alvo(j, o.id, TITULO, acao, o.x, o.y, pista, opcional=True), motivo=MOTIVO)
