"""Pedidos dos moradores, ferramentas de viagem e testemunhos das raízes."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Item:
    id: str
    nome: str
    descricao: str
    permanente: bool = False


ITENS = (
    Item("balsamo", "Bálsamo de Mimo", "Recupera 35 de luz. Guarde para depois de um golpe ou clarão."),
    Item("pavio", "Pavio de pólen", "Ilumina o caminho ao seu redor por 12 segundos."),
    Item("casulo", "Casulo de seda", "Absorve o próximo ataque de uma criatura."),
    Item("concha", "Concha de escuta", "Localiza a criatura mais próxima. Aguarde cinco segundos entre escutas.", True),
)
POR_ID = {item.id: item for item in ITENS}


class Bolsa:
    def __init__(self):
        self.estoque = {i.id: int(i.id == "balsamo") for i in ITENS}
        self.equipado = "balsamo"
        self.escudo = False
        self.luz_ate = 0.
        self.escuta_ate = 0.
        self.revisao = 0

    @property
    def item(self):
        return POR_ID[self.equipado]

    @property
    def quantidade(self):
        return self.estoque[self.equipado]

    def receber(self, item, quantidade):
        # Cada bolsa de trilha e cada presente têm um registro de coleta próprio.
        if POR_ID[item].permanente:
            self.estoque[item] = 1
        else:
            self.estoque[item] += quantidade
        if not self.quantidade:
            self.equipado = item
        self.revisao += 1

    def trocar(self):
        disponiveis = [i.id for i in ITENS if self.estoque[i.id]]
        if not disponiveis:
            return "A bolsa está vazia. Procure mantimentos nos desvios."
        if self.equipado in disponiveis:
            indice = (disponiveis.index(self.equipado) + 1) % len(disponiveis)
            self.equipado = disponiveis[indice]
        else:
            self.equipado = disponiveis[0]
        self.revisao += 1
        return f"{self.item.nome} · {self.item.descricao}"

    def absorver(self):
        if not self.escudo:
            return False
        self.escudo = False
        self.revisao += 1
        return True

    def usar(self, j):
        if not self.quantidade:
            j.notificar("Sem carga neste bolso. Q escolhe outro item.")
            return None
        item = self.equipado
        if item == "balsamo":
            if j.lume.energia >= 99.99:
                j.notificar("Sua luz está cheia. O bálsamo continua na bolsa.")
                return None
            antes = j.lume.energia
            j.lume.energia = min(100., antes + 35.)
            mensagem = f"Bálsamo · +{round(j.lume.energia - antes)} de luz."
            som = "coleta"
        elif item == "pavio":
            if self.luz_ate > j.tempo:
                j.notificar("O pavio anterior ainda está aceso.")
                return None
            self.luz_ate = j.tempo + 12.
            mensagem = "Pavio aceso · 12 segundos de luz ampliada."
            som = "abertura"
        elif item == "casulo":
            if self.escudo:
                j.notificar("O casulo já cobre as suas asas.")
                return None
            self.escudo = True
            mensagem = "Casulo vestido · absorve o próximo ataque."
            som = "corda"
        else:
            if self.escuta_ate > j.tempo:
                j.notificar("O eco anterior ainda vibra na concha.")
                return None
            self.escuta_ate = j.tempo + 5.
            mensagem = self.escutar(j)
            som = "sino"
        if not self.item.permanente:
            self.estoque[item] -= 1
        self.revisao += 1
        j.notificar(mensagem)
        return som

    @staticmethod
    def escutar(j):
        x, y = j.lume.rect.center
        alvos = [(e.rect.centerx, e.rect.centery) for e in j.inimigos if e.ativo]
        if j.boss and not j.boss.vencido:
            alvos.append((j.boss.x, j.boss.y))
        if alvos:
            ax, ay = min(alvos, key=lambda p: math.dist((x, y), p))
            distancia = math.dist((x, y), (ax, ay))
            if distancia < 700:
                direcao = "à esquerda" if ax < x else "à direita"
                altura = ", acima" if ay < y - 55 else ", abaixo" if ay > y + 55 else ""
                perto = "muito perto" if distancia < 120 else "ao longe" if distancia > 330 else "à frente"
                return f"Eco {direcao}{altura} · {perto}."
        return "A concha só devolve o som de Lume. Nenhuma criatura por perto."

    def salvar(self, tempo):
        return {
            "estoque": dict(self.estoque),
            "equipado": self.equipado,
            "escudo": self.escudo,
            "pavio_restante": max(0., self.luz_ate - tempo),
            "concha_restante": max(0., self.escuta_ate - tempo),
        }

    @classmethod
    def carregar(cls, dados, tempo):
        bolsa = cls()
        if not isinstance(dados, dict):
            return bolsa
        estoque = dados.get("estoque")
        if isinstance(estoque, dict):
            for item in ITENS:
                n = estoque.get(item.id, 0)
                if type(n) is int:
                    bolsa.estoque[item.id] = max(0, min(1 if item.permanente else 9999, n))
        if isinstance(dados.get("equipado"), str) and dados["equipado"] in POR_ID:
            bolsa.equipado = dados["equipado"]
        bolsa.escudo = dados.get("escudo") is True
        for campo, atributo, limite in (
            ("pavio_restante", "luz_ate", 12.),
            ("concha_restante", "escuta_ate", 5.),
        ):
            valor = dados.get(campo, 0.)
            if isinstance(valor, (int, float)) and math.isfinite(valor):
                setattr(bolsa, atributo, tempo + max(0., min(limite, valor)))
        return bolsa


@dataclass(frozen=True)
class Pedido:
    titulo: str
    origem: str
    destino: str
    # A cada ação corresponde a pista que o diário oferece enquanto ela falta.
    passos: tuple[tuple[str, str], ...]
    entregar: str
    convite: str
    cobrar: str
    entrega: str
    depois: str
    itens: tuple[tuple[str, int], ...]


PEDIDOS = (
    Pedido(
        "Os nomes nas cascas", "Nira", "Véspera",
        (("registro", "Leia o mapa enrolado no galho do berçário."),),
        "Leve a data do mapa a Véspera, junto dos ninhos altos.",
        "Véspera tirou os pequenos dali antes do raio. No galho do berçário ficou um mapa enrolado. Leia a data para ela.",
        "Deixei um pavio junto às cascas. Primeiro preciso saber quando saímos. Leia a data no mapa deste galho.",
        "Duas luas antes do raio. Eu tinha razão em levar os pequenos. Leve meus pavios de pólen para enxergar o caminho.",
        "Agora canto só quando alguém responde. Os que eu tirei daqui foram com Mimo.",
        (("pavio", 2),),
    ),
    Pedido(
        "A marca da cheia", "Casca", "Fio",
        (("registro", "Examine a marca d'água no galho acima do canal."),
         ("ponte", "Drene o canal e solte a ponte com a lingueta.")),
        "Conte a Fio, na cabeceira da ponte, para onde a corrente vira.",
        "Fio remendou três teias contra a corrente. Veja a marca no galho de cima e abra a ponte. Preciso que ela saiba quem fechou a água.",
        "A ponte precisa abrir. Procure também o sulco alto na casca. O limo mostra para que lado a água corria antes.",
        "O limo ficou do lado de fora. Foi Casca quem virou a água para o tronco. Leve esta concha. Ela devolve o lado de onde vêm os passos.",
        "Casca desceu para abrir o canal comigo. Hoje a seda aguenta a corrente sem partir.",
        (("concha", 1),),
    ),
    Pedido(
        "Luz de chamada", "Eco", "Risca",
        (("no", "Acenda o nó lateral na borda do vão."),
         ("chamado_eco", "Use K junto ao nó aceso para responder ao sinal de Eco.")),
        "Diga a Risca que o clarão na taquara veio de Eco.",
        "Risca tapou a trilha porque viu dois olhos. Eu estava chamando da borda. Acenda o nó na borda e dê um clarão junto dele. Vou responder do outro lado.",
        "Vi duas luzes. Acenda o nó da borda e dê um clarão junto dele. Se alguém responder, eu tiro a palha da passagem.",
        "Uma luz, intervalo, outra luz. Era Eco batendo as asas. Vou abrir a trilha. Vista este casulo. A seda segura um golpe.",
        "Catei a palha que eu tinha posto na passagem. Eco pode chamar sem que alguém tape o caminho de novo.",
        (("casulo", 2),),
    ),
    Pedido(
        "O toque interrompido", "Nó", "Pingo",
        (("registro", "Leia a cicatriz na face interna da raiz, sobre o primeiro estrado."),
         ("eco_antigo", "Desça pela grade da câmara e toque o sino soterrado.")),
        "Encontre Pingo no primeiro estrado para levar o recado a Brasa.",
        "O sino tocava na distribuição de água. Procure o talho antigo no alto e toque o sino soterrado na câmara. Pingo pode levar o que ouvirmos.",
        "Nó só guarda um som quando ele passa na raiz. Leia o talho lá em cima e toque o sino soterrado. Seus pés vão sentir a resposta.",
        "O talho é antigo. A guardiã batia o sino enquanto a borda secava. Vou contar a Brasa. Leve este pavio para chegar até ela.",
        "Carreguei a notícia pelo caminho curto. Pela primeira vez Brasa veio ouvir a raiz deste lado.",
        (("pavio", 2), ("balsamo", 1)),
    ),
)


def pedido_local(j):
    if j.modo != "historia" or "pedido_aceito" not in j.flags or "pedido_entregue" in j.flags:
        return ""
    pedido = PEDIDOS[j.etapa]
    for flag, pista in pedido.passos:
        if flag not in j.flags:
            return pista
    return pedido.entregar


def _presentes(j, itens):
    for item, quantidade in itens:
        j.bolsa.receber(item, quantidade)
    return ", ".join(f"{quantidade} × {POR_ID[item].nome}" for item, quantidade in itens)


def ajuda_do_refugio(j, nome, texto):
    # A marca pertence à área e não reaparece ao reentrar ou carregar o marco.
    if nome == "Mimo" and "mantimento_mimo" not in j.flags:
        j.flags.add("mantimento_mimo")
        _presentes(j, (("balsamo", 1),))
        return "Este bálsamo é dos casulos vazios. Use F quando sua luz baixar. As crianças do berçário dormem aqui. Pergunte a Nira quem as trouxe."
    if nome == "Brasa":
        if j.etapa == 3 and "pedido_entregue" in j.historico.get((j.volta, 1), set()) and "oferta_brasa" not in j.flags:
            j.flags.add("oferta_brasa")
            _presentes(j, (("casulo", 1),))
            return "Fio me contou que você ouviu Casca. Fiamos esta manta juntos. Ela aguenta um golpe. Leve-a à Coruja."
        if j.etapa == 1:
            if "registro" in j.historico.get((j.volta, 0), set()):
                return "Reconheço a data no mapa de Nira. Nessa noite pedi a Casca que fechasse a comporta. Queria encher o poço do berçário."
            return "Fui eu que pedi a Casca que fechasse a comporta. O poço central ia secar. Eu não via as teias de Fio desde a outra margem."
        if "contrapeso" in j.flags:
            return "Reconheço o sino. Ouvi isso do tronco tantas noites e achei que a Coruja guardava a entrada. Ela pedia água para fora."
        return "A comporta desviou a água para cá. Eu esperava encontrar o tronco cheio. Encoste na raiz e ouça o que ficou para trás."
    if nome == "Candeia" and "mantimento_candeia" not in j.flags:
        j.flags.add("mantimento_candeia")
        _presentes(j, (("pavio", 1),))
        return "Eco me ensinou a chamar com dois sinais curtos. Tome um pavio. Acenda com F depois de escolher com Q, e veja os apoios na borda."
    if nome == "Coruja":
        return "Eu ouvia as comportas fecharem. Bati o sino, mas ninguém saía do tronco. Agora escuto as quatro raízes correndo ao mesmo tempo."
    return texto


def conversar(j, nome, texto_base):
    pedido = PEDIDOS[j.etapa]
    texto = texto_base
    if j.modo == "historia" and nome in (pedido.origem, pedido.destino):
        if "pedido_entregue" in j.flags:
            texto = pedido.depois if nome == pedido.destino else texto_base
        else:
            j.flags.add("pedido_aceito")
            texto = pedido.convite if nome == pedido.origem else pedido.cobrar
            if nome == pedido.destino and all(flag in j.flags for flag, _ in pedido.passos):
                j.flags.add("pedido_entregue")
                if j.etapa == 2:
                    # Risca tira a palha que fechava o acesso rápido ao abrigo.
                    j.flags.add("atalho")
                recibo = _presentes(j, pedido.itens)
                j.memorizar(pedido.titulo + " · entregue", f"{pedido.entrega} Na bolsa: {recibo}.")
                j.eventos.append("coleta")
                texto = pedido.entrega
            else:
                j.memorizar("Pedido · " + pedido.titulo, pedido.convite + " " + pedido.entregar)
                if nome == pedido.origem and all(flag in j.flags for flag, _ in pedido.passos):
                    texto = pedido.entregar
    else:
        texto = ajuda_do_refugio(j, nome, texto)
    j.dialogo = (nome, texto)
    j.memorizar(nome, texto)
    j.eventos.append("pagina")


def responder_chamado(j):
    if j.modo != "historia" or j.etapa != 2 or "no" not in j.flags or "chamado_eco" in j.flags:
        return
    no = next(o for o in j.fase.objetos if o.id == "no")
    if math.dist(j.lume.rect.midbottom, (no.x, no.y)) > 115:
        return
    j.flags.add("chamado_eco")
    j.memorizar("A resposta de Eco", "Lume acendeu o nó e lançou um clarão ao lado dele. Do outro lado do vão, alguém respondeu com dois lampejos.")
    j.notificar("Dois lampejos respondem. Conte a Risca o que viu.")
    j.eventos.extend(("coleta", "resposta_eco"))


RESERVAS = (
    ("A trouxa de Véspera", "Entre dois casulos há um embrulho de seda. Véspera deixou mantimentos na rota de evacuação.", (("casulo", 1), ("balsamo", 1))),
    ("O bolso da comporta", "Fio prendeu a reserva acima da marca da cheia. Uma lata de bálsamo ficou seca lá dentro.", (("balsamo", 2),)),
    ("Reserva da borda", "Um pavio envolto em palha tinha duas marcas de asa. Eco guardava luz para o caminho de volta.", (("pavio", 2),)),
    ("A vigia da raiz", "Sob o velho apoio do sino, restam duas mantas de seda dobradas. A guardiã fazia vigílias longas aqui.", (("casulo", 2),)),
)


def abrir_reserva(j):
    if "reserva" in j.flags:
        return
    titulo, historia, itens = RESERVAS[j.etapa]
    j.flags.add("reserva")
    recibo = _presentes(j, itens)
    j.memorizar(titulo, historia + " Encontrado: " + recibo + ".")
    j.notificar("Bolsa de trilha · " + recibo)
    j.eventos.append("coleta")


# Os quatro fatos decisivos também chegam a quem segue apenas a rota principal.
VESTIGIOS = (
    ("A peça do berçário", "A peça da porteira traz a marca de Véspera. Ela carregou os casulos por aqui antes de a tempestade chegar."),
    ("O segundo leito", "A ponte se estende sobre o sulco seco. A marca de Casca na comporta fica do lado do tronco: a água foi desviada."),
    ("Sinais na borda", "No reflexo da brasa, Lume vê dois sinais de asa vindos do vão. Há sobreviventes esperando uma trilha de volta."),
    ("Por que o sino batia", "A primeira badalada corre pela raiz até a borda. A Coruja responde do escuro: conhecia o caminho dos que ficaram sem água."),
)
RAIZES = (
    ("Primeira resposta", "Uma gota corre para fora do tronco. Véspera responde do berçário. A mancha escura segue adiante, junto ao córrego."),
    ("A comporta aberta", "A água volta a entrar nos dois braços da bifurcação. Fio deixa uma teia sobre a margem molhada. Um fio de luz alcança as taquaras."),
    ("Um caminho até Eco", "Eco atravessa a faixa de terra que secava ao vento. Lume segue os dois sinais de suas asas até a boca da figueira."),
    ("As quatro correntes", "A Coruja acompanha os quatro cursos com a cabeça. A sombra continua entre as raízes secas, mas agora há água junto delas."),
)


RAMAIS = (
    ("A cunha arranhada", "No alto do poço, a cunha tem a mesma marca do mapa de Nira. Foi por estas paredes que Véspera levou os casulos."),
    ("A grelha de Fio", "Quando o ralo abre, passam folhas e fios de seda pela grelha. Fio tinha tentado levar a água para fora sozinha."),
    ("O cheiro da vagem", "Lume traz da outra margem a vagem de uma taquara. Seu cheiro alcança Eco, que muda o chamado de lugar."),
    ("O sino soterrado", "O badalo de baixo tremia mesmo antes do raio. Nó guardou esse som. A Coruja ouvia as raízes secando."),
)


def guardar_virada(j, eventos):
    if j.modo == "historia":
        titulo, texto = eventos[j.etapa]
        j.memorizar(titulo, texto)
        if eventos is not RAIZES:
            j.notificar(texto, 6.)
