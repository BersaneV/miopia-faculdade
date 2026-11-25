"""
config.py — constantes, cores e balanceamento do Miopia.

Tudo o que o grupo vai querer ajustar (velocidade, energia, tempo, inimigos)
está aqui, separado da lógica. Assim dá para equilibrar o jogo sem tocar
no código das telas.
"""

from __future__ import annotations

import os

# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
FONTES = os.path.join(ASSETS, "fontes")
SONS = os.path.join(ASSETS, "sons")
DADOS = os.path.join(RAIZ, "dados")
RECORDE = os.path.join(DADOS, "recorde.json")

# --------------------------------------------------------------------------
# Tela e grade
# --------------------------------------------------------------------------
TITULO = "Miopia — a última luz da mata"
LARGURA = 960
ALTURA = 600
HUD_ALTURA = 84
RODAPE_ALTURA = 36
AREA_ALTURA = ALTURA - HUD_ALTURA - RODAPE_ALTURA   # 480
FPS = 60

TILE = 40
COLUNAS = 24
LINHAS = 12
AREA_LARGURA = COLUNAS * TILE              # 960
AREA_ALTURA_USADA = LINHAS * TILE          # 480

assert AREA_LARGURA == LARGURA

# --------------------------------------------------------------------------
# Paleta (uma noite de mata atlântica: azul-tinta + luz de vaga-lume)
# --------------------------------------------------------------------------
NOITE = (6, 9, 16)
NOITE_SUAVE = (11, 16, 27)
CHAO = (15, 21, 34)
CHAO_ALT = (18, 25, 40)
PAREDE = (27, 36, 55)
PAREDE_TOPO = (40, 53, 78)
PAREDE_BORDA = (52, 68, 98)

LUZ = (255, 235, 170)
LUZ_QUENTE = (255, 208, 110)
AGUA = (127, 231, 255)
VERDE = (126, 222, 176)
PERIGO = (255, 108, 108)
ROXO = (167, 142, 240)
TEXTO = (232, 238, 250)
TEXTO_FRACO = (146, 160, 190)
TEXTO_APAGADO = (98, 110, 138)
OURO = (255, 204, 102)
PRETO = (0, 0, 0)

# --------------------------------------------------------------------------
# Fonte
# --------------------------------------------------------------------------
FONTE_TITULO = os.path.join(FONTES, "FredokaOne-Regular.ttf")
FONTE_NEGRITO = os.path.join(FONTES, "Nunito-Bold.ttf")
FONTE_TEXTO = os.path.join(FONTES, "Nunito-Regular.ttf")

# --------------------------------------------------------------------------
# Balanceamento do jogador
# --------------------------------------------------------------------------
VEL_MAX = 168.0           # px/s andando
VEL_CORRER = 258.0        # px/s com Shift
ACELERACAO = 2200.0
ATRITO = 12.0
RAIO_JOGADOR = 9

ENERGIA_MAX = 100.0
DRENO_BASE = 1.6          # energia por segundo (a luz consome)
DRENO_CORRER = 6.0        # energia por segundo correndo
ORVALHO_ENERGIA = 16.0
ORVALHO_RARO_ENERGIA = 45.0

CUSTO_PULSO = 27.0
COOLDOWN_PULSO = 1.6
DURACAO_PULSO = 0.75

RAIO_LUZ_MIN = 122.0       # regra de ouro: nunca menos que isso (legibilidade)
RAIO_LUZ_MAX = 262.0
ENERGIA_RAIO_MIN = 16.0   # abaixo disso a luz começa a fechar

VIDAS_INICIAIS = 3
INVULNERAVEL = 1.8        # segundos piscando após levar dano
APAGAO_DANO_INTERVALO = 6.0   # energia zerada: perde 1 vida a cada X s

# --------------------------------------------------------------------------
# Partida
# --------------------------------------------------------------------------
TEMPO_TOTAL = 270.0       # 4:00 até o amanhecer (mais o bônus por bioma)
BONUS_TEMPO_BIOMA = 35.0  # segundos ganhos ao começar um bioma novo

PONTOS_ORVALHO = 10
PONTOS_RARO = 50
PONTOS_CHEFE = 500       # recompensa por acalmar a Coruja
PONTOS_BIOMA = 150
PONTOS_SEGUNDO = 4        # multiplica o tempo restante no fim
PONTOS_VIDA = 100

# --------------------------------------------------------------------------
# Biomas: cada um muda paleta, inimigos e quantidade de orvalho exigida
# --------------------------------------------------------------------------
BIOMAS = [
    {
        "fase": "Clareira",
        "nome": "Bosque das Samambaias",
        "curto": "Bosque",
        "trilha": "bosque",
        "dica": "Sua luz é curta. Colete orvalho para mantê-la viva.",
        "chao": (15, 23, 32),
        "parede": (24, 38, 46),
        "parede_topo": (35, 54, 62),
        "ambiente": (120, 200, 160),
        "necessario": 6,
        "inimigos": {"morcego": 1, "aranha": 1},
        "coruja": False,
        "semente_extra": 0,
    },
    {
        "fase": "Trilha interrompida",
        "nome": "Córrego Fundo",
        "curto": "Córrego",
        "trilha": "corrego",
        "dica": "Aranhas sentem a luz chegando. Passe longe das teias.",
        "chao": (13, 22, 36),
        "parede": (22, 34, 56),
        "parede_topo": (33, 50, 78),
        "ambiente": (110, 190, 255),
        "necessario": 9,
        "inimigos": {"morcego": 2, "aranha": 2},
        "coruja": False,
        "semente_extra": 1,
    },
    {
        "fase": "Borda da floresta",
        "nome": "Taquaral",
        "curto": "Taquaral",
        "trilha": "taquaral",
        "dica": "Sombras congelam quando você está bem iluminado.",
        "chao": (18, 24, 28),
        "parede": (36, 48, 42),
        "parede_topo": (52, 68, 56),
        "ambiente": (200, 220, 130),
        "necessario": 11,
        "inimigos": {"morcego": 3, "aranha": 2, "sombra": 2},
        "coruja": False,
        "semente_extra": 2,
    },
    {
        "fase": "Último refúgio",
        "nome": "Gruta da Figueira",
        "curto": "Gruta",
        "trilha": "gruta",
        "dica": "A Coruja te ouve: ande devagar. 3 clarões perto dela e ela se acalma.",
        "chao": (16, 16, 30),
        "parede": (32, 28, 52),
        "parede_topo": (46, 40, 74),
        "ambiente": (170, 140, 255),
        "necessario": 13,
        "inimigos": {"morcego": 3, "aranha": 2, "sombra": 2},
        "coruja": True,
        "semente_extra": 3,
    },
]
