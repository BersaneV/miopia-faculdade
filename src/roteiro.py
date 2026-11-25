PROLOGO = (
    ("Os quatro caminhos",
     "Toda noite a colônia levava orvalho para a figueira. Lume contava quatro sulcos na casca. Ultimamente, só um deles chegava molhado.", 3),
    ("A noite do raio",
     "O raio abriu o tronco. O Breu seguiu as lanternas fortes até o centro. A de Lume mal iluminava as próprias asas. Foi assim que ele escapou.", 0),
    ("O último turno",
     "O sino da guardiã bateu três vezes. Mimo chamou do abrigo: “Se encontrar um casulo inteiro, traga para mim. Os que eu recolhi estão frios.”", 0),
    ("O berçário vazio",
     "O orvalho seca ao amanhecer. As asas rasgadas ainda seguram uma queda. Lume procura os pequenos e leva a primeira gota pelo sulco que secou.", 0),
)
ENTRADAS = (
    "As cascas dos casulos estão cortadas por dentro. Quem tirou os pequenos daqui conhecia a passagem. Nira ainda guarda o mapa.",
    "O riacho corre para o tronco. Do outro lado, Fio prende a seda a pedras que já estiveram debaixo d'água. Casca guarda a chave do desvio.",
    "A água voltou ao canal, mas as taquaras secas estalam ao vento. Da outra margem vem um sinal curto, depois outro. Alguém está chamando.",
    "A raiz entra na figueira pela ferida do raio. No fundo há um sino com marcas antigas de garra. Os fungos de Nó guardaram a última badalada.",
)
FINAL = {
    "vitoria": ("O turno da borda",
        "Ao amanhecer, Brasa chega ao berçário com uma gota, e não passa direto. Casca abre os dois canais. Da borda vem a resposta de Eco. Ainda há ninhos vazios. A Coruja ouve passar, um por um, os que voltam."),
    "derrota": ("Quando a raiz silencia",
        "Lume deixa de ver o próximo sulco. O orvalho seca nas folhas. No abrigo, Mimo levanta a casca para o último grupo passar. Cada um parte por um caminho."),
    "infinito": ("O fim desta noite",
        "A última luz se recolhe. Na casca ficam as marcas dos trechos que Lume conseguiu atravessar."),
}
def epilogo(jogo):
    entregues = [i for i in range(4) if "pedido_entregue" in jogo.historico.get((0, i), ())]
    cenas = (
        "Mimo deixa Véspera ler, ao lado dos casulos, os nomes que Nira conseguiu salvar.",
        "Casca segura a roda enquanto Fio faz na madeira uma marca nova para a água desta manhã.",
        "Risca abre a trilha antes de Eco piscar duas vezes. Agora conhece o chamado.",
        "Pingo volta com Brasa. Os dois escutam juntos a última vibração do sino.",
    )
    if len(entregues) == 4:
        return "Véspera traz o mapa. Fio anota a cheia. Risca deixa a trilha aberta para Eco. E Pingo espera Brasa na ponta da fila."
    return cenas[entregues[-1]] if entregues else ""


CONTROLES = (
    ("A / D   ou   setas", "Andar. Encoste numa parede e salte para a oposta."),
    ("Espaço", "Saltar. Segure no ar para planar durante a queda."),
    ("S   /   S + Espaço", "Agachar / descer de uma plataforma vazada."),
    ("Shift + direção", "Deslizar. A corrente do córrego exige impulso."),
    ("E", "Conversar, operar mecanismos e abrir bolsas de trilha."),
    ("J   /   S + J no ar", "Até três cortes em sequência / golpe para baixo com rebote."),
    ("K", "Clarão de 22 de luz. O local fica iluminado por 6,5 segundos."),
    ("Q   /   F", "Escolher item na bolsa / usar o item escolhido."),
    ("Tab", "Diário, mapa e pistas dos pedidos dos moradores."),
    ("Esc   ou   P", "Pausar. Na pausa, R retorna ao marco."),
    ("M   /   F11", "Silenciar / alternar tela cheia."),
)
