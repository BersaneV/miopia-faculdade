"""
mundo.py — geração do labirinto, colisão e desenho do cenário.

Cada bioma é um labirinto gerado por semente (recursive backtracker) com
algumas paredes derrubadas para criar atalhos e duas clareiras. O cenário
inteiro é desenhado uma vez numa superfície estática; por frame só
entram os bichos, o orvalho e a luz.
"""

from __future__ import annotations

import random
from collections import deque

import pygame

from . import config
from . import utils


class Mundo:
    def __init__(self, bioma: int, semente: int, dados: dict | None = None) -> None:
        self.bioma = bioma            # estilo de decoração (0 a 3)
        self.semente = semente
        # no modo infinito o chamador passa um descritor gerado na hora
        self.dados = dados if dados is not None else config.BIOMAS[bioma]
        self.colunas = config.COLUNAS
        self.linhas = config.LINHAS
        self.sorteio = random.Random(semente)

        self.grade: list[list[int]] = []
        self.inicio: tuple[float, float] = (0.0, 0.0)
        self.saida: tuple[float, float] = (0.0, 0.0)
        self.celula_saida = (0, 0)
        self.orvalhos: list[dict] = []
        self.inimigos: list[dict] = []
        self.decoracoes: list[dict] = []
        self.superficie: pygame.Surface | None = None
        self._distancias: dict[tuple[int, int], int] = {}

        self._gerar_labirinto()
        self._escolher_inicio_saida()
        self._distribuir_orvalho()
        self._distribuir_inimigos()
        self._distribuir_decoracoes()
        self.desenhar_estatico()

    # ================================================================== #
    # Geração
    # ================================================================== #
    def _gerar_labirinto(self) -> None:
        """
        Mata aberta com moitas (blocos de vegetação/pedra), não um labirinto de
        corredor único. Motivos:
          - perseguição precisa de espaço para desviar e dar volta;
          - a escuridão já cria o "labirinto" na cabeça do jogador;
          - blocos irregulares parecem mata, não tabuleiro.
        Cada bloco só entra se o mapa continuar todo conectado (BFS barato).
        """
        colunas, linhas = self.colunas, self.linhas
        grade = [[0] * colunas for _ in range(linhas)]

        # Borda fechada
        for x in range(colunas):
            grade[0][x] = grade[linhas - 1][x] = 1
        for y in range(linhas):
            grade[y][0] = grade[y][colunas - 1] = 1

        # Zona de início: canto inferior esquerdo sempre livre
        for y in range(linhas - 3, linhas - 1):
            for x in range(1, 4):
                grade[y][x] = 0

        inicio = (1, linhas - 2)

        def conectado(teste: list[list[int]]) -> bool:
            """True se todas as células livres são alcançáveis a partir do início."""
            if teste[inicio[1]][inicio[0]] != 0:
                return False
            vistos = {inicio}
            fila = deque([inicio])
            total_livre = sum(1 for linha in teste for c in linha if c == 0)
            while fila:
                x, y = fila.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in vistos and teste[ny][nx] == 0:
                        vistos.add((nx, ny))
                        fila.append((nx, ny))
            return len(vistos) == total_livre

        def sobrepoe(x0, y0, w, h, folga=1) -> bool:
            for y in range(max(0, y0 - folga), min(linhas, y0 + h + folga)):
                for x in range(max(0, x0 - folga), min(colunas, x0 + w + folga)):
                    if grade[y][x] == 1:
                        return True
            return False

        alvo = 20
        colocados = 0
        tentativas = 0
        while colocados < alvo and tentativas < 500:
            tentativas += 1
            largura = self.sorteio.choice((1, 1, 1, 2, 2, 3, 4))
            altura = self.sorteio.choice((1, 1, 2, 2, 3))
            x0 = self.sorteio.randrange(1, colunas - 1 - largura)
            y0 = self.sorteio.randrange(1, linhas - 1 - altura)

            # não encostar em outra moita (deixa corredor de 1 célula)
            if sobrepoe(x0, y0, largura, altura):
                continue

            for y in range(y0, y0 + altura):
                for x in range(x0, x0 + largura):
                    grade[y][x] = 1

            if conectado(grade):
                colocados += 1
            else:
                for y in range(y0, y0 + altura):
                    for x in range(x0, x0 + largura):
                        grade[y][x] = 0

        # Alguns pilares soltos, que dão quebra de linha de visão
        for _ in range(10):
            x = self.sorteio.randrange(2, colunas - 2)
            y = self.sorteio.randrange(2, linhas - 2)
            if grade[y][x] == 0 and not sobrepoe(x, y, 1, 1, folga=1):
                grade[y][x] = 1
                if not conectado(grade):
                    grade[y][x] = 0

        self.grade = grade

        # Clareira de respiro no meio (garante espaço para escapar do bando)
        meio_x = self.sorteio.randrange(colunas // 3, 2 * colunas // 3)
        meio_y = self.sorteio.randrange(linhas // 3, 2 * linhas // 3)
        for y in range(max(1, meio_y - 1), min(linhas - 1, meio_y + 2)):
            for x in range(max(1, meio_x - 1), min(colunas - 1, meio_x + 2)):
                self.grade[y][x] = 0

    def _celulas_livres(self) -> list[tuple[int, int]]:
        livres = []
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.grade[y][x] == 0:
                    livres.append((x, y))
        return livres

    def _bfs(self, inicio: tuple[int, int]) -> dict[tuple[int, int], int]:
        distancias = {inicio: 0}
        fila = deque([inicio])
        while fila:
            x, y = fila.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.colunas and 0 <= ny < self.linhas and self.grade[ny][nx] == 0:
                    if (nx, ny) not in distancias:
                        distancias[(nx, ny)] = distancias[(x, y)] + 1
                        fila.append((nx, ny))
        return distancias

    def _escolher_inicio_saida(self) -> None:
        livres = self._celulas_livres()

        # Início: a célula livre mais próxima do canto inferior esquerdo
        # (a geração já garante que essa região está limpa)
        canto = (1, self.linhas - 2)
        self.inicio_celula = min(
            livres, key=lambda c: abs(c[0] - canto[0]) * 1.0 + abs(c[1] - canto[1]) * 1.0
        )
        self._distancias = self._bfs(self.inicio_celula)

        # Saída: sorteada entre as células mais distantes do início.
        # Sortear evita que a saída caia sempre no mesmo canto.
        ordenadas = sorted(self._distancias.items(), key=lambda item: -item[1])
        limite = ordenadas[0][1] * 0.86
        candidatas = [c for c, d in ordenadas if d >= limite]
        self.celula_saida = self.sorteio.choice(candidatas[: max(4, len(candidatas) // 3)])

        self.inicio = self._centro(self.inicio_celula)
        self.saida = self._centro(self.celula_saida)

    def _centro(self, celula: tuple[int, int]) -> tuple[float, float]:
        return (
            celula[0] * config.TILE + config.TILE / 2,
            celula[1] * config.TILE + config.TILE / 2,
        )

    def _celula_de(self, pos: tuple[float, float]) -> tuple[int, int]:
        return int(pos[0] // config.TILE), int(pos[1] // config.TILE)

    # ------------------------------------------------------------------ #
    def _distribuir_orvalho(self) -> None:
        """
        Espalha o orvalho pelo mapa INTEIRO.

        Antes, as células eram ordenadas por distância ao início e o código
        pegava as mais distantes primeiro. Como as mais distantes ficam todas
        grudadas perto da saída (um canto do mapa), o orvalho inteiro acabava
        concentrado naquele canto. Agora o mapa é dividido em setores e as
        escolhas são feitas em rodízio, um item por setor a cada rodada.
        """
        necessario = self.dados["necessario"]
        alvo = necessario + 7

        candidatas = [
            c for c, d in self._distancias.items()
            if d >= 3 and c != self.inicio_celula and c != self.celula_saida
        ]
        if not candidatas:
            self.orvalhos = []
            return

        # ---- setores (4 x 2 = 8 regiões do mapa) ----
        colunas_setor, linhas_setor = 4, 2
        setores: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for celula in candidatas:
            cx = min(colunas_setor - 1, celula[0] * colunas_setor // self.colunas)
            cy = min(linhas_setor - 1, celula[1] * linhas_setor // self.linhas)
            setores.setdefault((cx, cy), []).append(celula)

        for lista in setores.values():
            lista.sort(key=lambda c: self._distancias.get(c, 0))
            # embaralha dentro da faixa para não criar padrão de grade
            for i in range(len(lista) - 1, 0, -1):
                j = self.sorteio.randrange(i + 1)
                lista[i], lista[j] = lista[j], lista[i]

        # ---- rodízio entre os setores ----
        ordem = list(setores)
        self.sorteio.shuffle(ordem)
        escolhidas: list[tuple[int, int]] = []
        while len(escolhidas) < alvo and ordem:
            progresso = False
            for chave in list(ordem):
                lista = setores[chave]
                while lista:
                    celula = lista.pop()
                    # espaçamento mínimo: dois orvalhos nunca ficam colados
                    if all(abs(celula[0] - e[0]) + abs(celula[1] - e[1]) >= 2
                           for e in escolhidas):
                        escolhidas.append(celula)
                        progresso = True
                        break
                if len(escolhidas) >= alvo:
                    break
            if not progresso:
                break

        self.orvalhos = [
            {"pos": self._centro(c), "raro": False, "fase": self.sorteio.random() * 6.28}
            for c in escolhidas
        ]

        # ---- dois raros: longe do início, mas separados dos demais ----
        livres = [c for c in candidatas if c not in set(escolhidas)]
        self.sorteio.shuffle(livres)
        dist_max = max(self._distancias.get(c, 0) for c in candidatas) or 1
        raros: list[tuple[int, int]] = []
        for celula in sorted(livres, key=lambda c: -self._distancias.get(c, 0)):
            if len(raros) >= 2 or self._distancias.get(celula, 0) < 0.55 * dist_max:
                break
            if all(abs(celula[0] - e[0]) + abs(celula[1] - e[1]) >= 4
                   for e in escolhidas + raros):
                raros.append(celula)

        for celula in raros:
            self.orvalhos.append({
                "pos": self._centro(celula), "raro": True,
                "fase": self.sorteio.random() * 6.28,
            })

    # ------------------------------------------------------------------ #
    def _distribuir_inimigos(self) -> None:
        self.inimigos = []
        ocupados: list[tuple[int, int]] = []
        # mapas com muitos inimigos (modo infinito) aceitam espaçamento menor,
        # senão o mapa "recusa" os bichos e a fase fica mais fácil que a anterior
        total = sum(self.dados["inimigos"].values())
        espaco = 2 if total >= 12 else 3
        distancia_min = 6 if total >= 12 else 7
        for tipo, quantidade in self.dados["inimigos"].items():
            for _ in range(quantidade):
                opcoes = [
                    c for c, d in self._distancias.items()
                    if d >= distancia_min
                    and c != self.celula_saida
                    and all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= espaco
                            for o in ocupados)
                ]
                if not opcoes:
                    continue
                celula = self.sorteio.choice(opcoes)
                ocupados.append(celula)
                self.inimigos.append({
                    "tipo": tipo,
                    "pos": self._centro(celula),
                    "semente": self.sorteio.randrange(1, 99999),
                })

        # chefe do último bioma: a Coruja começa longe do jogador
        if self.dados.get("coruja"):
            candidatas = [
                c for c, d in self._distancias.items()
                if d >= 10 and c != self.celula_saida
            ]
            if candidatas:
                celula = max(candidatas, key=lambda c: self._distancias[c])
                self.inimigos.append({
                    "tipo": "coruja",
                    "pos": self._centro(celula),
                    "semente": self.sorteio.randrange(1, 99999),
                })

    # ------------------------------------------------------------------ #
    def _distribuir_decoracoes(self) -> None:
        tipos = {
            0: ["grama", "grama", "cogumelo", "pedra", "raiz"],
            1: ["grama", "pedra", "poca", "cogumelo", "folha"],
            2: ["bambu", "grama", "folha", "pedra", "cogumelo"],
            3: ["cristal", "pedra", "raiz", "cogumelo", "folha"],
        }[self.bioma]
        self.decoracoes = []
        for celula in self._celulas_livres():
            if celula == self.inicio_celula or celula == self.celula_saida:
                continue
            if self.sorteio.random() < 0.42:
                x, y = self._centro(celula)
                self.decoracoes.append({
                    "tipo": self.sorteio.choice(tipos),
                    "pos": (x + self.sorteio.uniform(-12, 12), y + self.sorteio.uniform(-12, 12)),
                    "tamanho": self.sorteio.uniform(0.7, 1.4),
                    "giro": self.sorteio.uniform(0, 6.28),
                })

    # ================================================================== #
    # Consultas de colisão
    # ================================================================== #
    def parede(self, coluna: int, linha: int) -> bool:
        if coluna < 0 or linha < 0 or coluna >= self.colunas or linha >= self.linhas:
            return True
        return self.grade[linha][coluna] == 1

    def colide(self, x: float, y: float, raio: float) -> bool:
        esquerda = int((x - raio) // config.TILE)
        direita = int((x + raio) // config.TILE)
        topo = int((y - raio) // config.TILE)
        base = int((y + raio) // config.TILE)
        for linha in range(topo, base + 1):
            for coluna in range(esquerda, direita + 1):
                if self.parede(coluna, linha):
                    return True
        return False

    def mover(self, x: float, y: float, dx: float, dy: float, raio: float):
        """Move resolvendo um eixo por vez (evita travar em quinas)."""
        bateu_x = bateu_y = False
        novo_x = x + dx
        if not self.colide(novo_x, y, raio):
            x = novo_x
            if dx:
                if self.colide(x + (raio if dx > 0 else -raio) * 0.1, y, raio - 0.5):
                    pass
        else:
            bateu_x = True

        novo_y = y + dy
        if not self.colide(x, novo_y, raio):
            y = novo_y
        else:
            bateu_y = True
        return x, y, bateu_x, bateu_y

    def visao(self, a: tuple[float, float], b: tuple[float, float]) -> bool:
        """Linha de visão simples por amostragem: True se não há parede no meio."""
        distancia = utils.distancia(a, b)
        passos = max(2, int(distancia // 14))
        for i in range(1, passos):
            t = i / passos
            x = utils.lerp(a[0], b[0], t)
            y = utils.lerp(a[1], b[1], t)
            if self.parede(int(x // config.TILE), int(y // config.TILE)):
                return False
        return True

    def direcao_saida(self, pos: tuple[float, float]) -> tuple[float, float]:
        """Aponta para a célula vizinha que está mais perto da saída (usado na dica)."""
        celula = self._celula_de(pos)
        melhor = None
        melhor_dist = self._distancias.get(celula, 999)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vizinha = (celula[0] + dx, celula[1] + dy)
            if vizinha in self._distancias and self._distancias[vizinha] <= melhor_dist:
                melhor_dist = self._distancias[vizinha]
                melhor = vizinha
        if melhor is None:
            return 0.0, 0.0
        alvo = self._centro(melhor)
        return utils.normalizar(alvo[0] - pos[0], alvo[1] - pos[1])

    # ================================================================== #
    # Desenho estático (chão + paredes + decoração)
    # ================================================================== #
    def desenhar_estatico(self) -> None:
        dados = self.dados
        surf = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA))
        surf.fill(dados["chao"])

        # xadrez bem sutil no chão (só para não ficar chapado)
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.grade[y][x] == 0 and (x + y) % 2 == 0:
                    pygame.draw.rect(
                        surf, utils.clarear(dados["chao"], 0.015),
                        (x * config.TILE, y * config.TILE, config.TILE, config.TILE),
                    )

        surf.blit(self._textura(), (0, 0))
        self._desenhar_decoracoes(surf)
        self._desenhar_paredes(surf)

        # sombra interna nas bordas da área
        borda = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for i in range(10):
            alpha = int(60 * (1 - i / 10))
            pygame.draw.rect(borda, (0, 0, 0, alpha), (i, i, surf.get_width() - i * 2,
                                                       surf.get_height() - i * 2), 1)
        surf.blit(borda, (0, 0))

        self.superficie = surf

    def _textura(self) -> pygame.Surface:
        sorteio = random.Random(self.semente + 77)
        surf = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA), pygame.SRCALPHA)
        for _ in range(900):
            x = sorteio.randrange(config.AREA_LARGURA)
            y = sorteio.randrange(config.AREA_ALTURA_USADA)
            tom = sorteio.choice(((255, 255, 255, 10), (0, 0, 0, 18), (200, 230, 255, 8)))
            pygame.draw.circle(surf, tom, (x, y), sorteio.choice((1, 1, 2)))
        return surf

    # ------------------------------------------------------------------ #
    def _desenhar_decoracoes(self, surf: pygame.Surface) -> None:
        for deco in self.decoracoes:
            x, y = deco["pos"]
            t = deco["tamanho"]
            tipo = deco["tipo"]
            ambiente = self.dados["ambiente"]

            if tipo == "grama":
                for i in range(3):
                    dx = (i - 1) * 4 * t
                    altura = (7 + i * 2) * t
                    pygame.draw.line(surf, utils.escurecer(ambiente, 0.55),
                                     (x + dx, y + 3), (x + dx + (i - 1) * 2, y + 3 - altura), 2)
            elif tipo == "cogumelo":
                pygame.draw.rect(surf, (210, 200, 190), (x - 1.5, y - 3, 3, 6))
                pygame.draw.circle(surf, utils.escurecer(ambiente, 0.8), (int(x), int(y - 5)),
                                   int(5 * t))
                pygame.draw.circle(surf, (255, 240, 210), (int(x - 1), int(y - 6)), 1)
            elif tipo == "pedra":
                pygame.draw.ellipse(surf, utils.escurecer(ambiente, 0.45),
                                    (x - 6 * t, y - 3 * t, 12 * t, 7 * t))
                pygame.draw.ellipse(surf, utils.escurecer(ambiente, 0.7),
                                    (x - 5 * t, y - 3 * t, 9 * t, 4 * t))
            elif tipo == "raiz":
                pygame.draw.lines(
                    surf, utils.escurecer(ambiente, 0.35), False,
                    [(x - 10, y - 4), (x - 3, y), (x + 2, y - 3), (x + 9, y + 2)], 2,
                )
            elif tipo == "poca":
                pygame.draw.ellipse(surf, utils.escurecer(ambiente, 0.35),
                                    (x - 12, y - 5, 24, 10))
                pygame.draw.ellipse(surf, utils.clarear(ambiente, 0.15),
                                    (x - 9, y - 4, 14, 5))
            elif tipo == "folha":
                pygame.draw.ellipse(surf, utils.escurecer(ambiente, 0.5),
                                    (x - 5, y - 2, 10, 4))
                pygame.draw.line(surf, utils.escurecer(ambiente, 0.3), (x - 4, y), (x + 4, y), 1)
            elif tipo == "bambu":
                for i in range(2):
                    bx = x + i * 5
                    pygame.draw.line(surf, utils.escurecer(ambiente, 0.45),
                                     (bx, y + 6), (bx + (i - 0.5) * 3, y - 16 * t), 3)
            elif tipo == "cristal":
                pontos = [(x, y - 9 * t), (x + 4 * t, y), (x, y + 4), (x - 4 * t, y)]
                pygame.draw.polygon(surf, utils.escurecer(ambiente, 0.5), pontos)
                pygame.draw.lines(surf, utils.clarear(ambiente, 0.2), True, pontos, 1)

    # ------------------------------------------------------------------ #
    def _desenhar_paredes(self, surf: pygame.Surface) -> None:
        dados = self.dados
        tile = config.TILE

        # sombra projetada: primeiro passa nas paredes, desenhando embaixo
        sombra = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.grade[y][x] == 1 and not self.parede(x, y + 1):
                    pygame.draw.rect(sombra, (0, 0, 0, 90),
                                     (x * tile + 4, y * tile + tile - 6, tile - 8, 14))
        surf.blit(sombra, (0, 0))

        for y in range(self.linhas):
            for x in range(self.colunas):
                if self.grade[y][x] != 1:
                    continue
                ret = pygame.Rect(x * tile, y * tile, tile, tile)
                cor = dados["parede"]
                if not self.parede(x, y - 1):
                    cor = dados["parede_topo"]
                pygame.draw.rect(surf, cor, ret)
                pygame.draw.rect(surf, utils.escurecer(cor, 0.72), ret, 2)

                # brilho no topo da parede quando ela tem chão acima
                if not self.parede(x, y - 1):
                    pygame.draw.line(surf, utils.clarear(dados["parede_topo"], 0.18),
                                     (ret.left + 2, ret.top + 2), (ret.right - 3, ret.top + 2), 2)
                # musgo / textura na base
                if not self.parede(x, y + 1):
                    for i in range(3):
                        px = ret.left + 6 + i * 11
                        pygame.draw.circle(surf, utils.escurecer(dados["ambiente"], 0.35),
                                           (px, ret.bottom - 4), 2)

    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface) -> None:
        if self.superficie:
            tela.blit(self.superficie, (0, 0))
