"""
telas.py — menu, ajuda, créditos e fim de jogo.

Todas as telas usam o design system de ui.py:
  · texto centrado pelos metrics do glifo (nunca pelo topo da caixa);
  · botões com foco/hover/pressionado desenhados de propósito;
  · painéis com padding fixo (26 px) e margem segura de 48 px;
  · blocos de texto com entrelinha 1.5 e largura de leitura controlada.

O modo história (cutscenes) fica em cena.py + historia.py.
"""

from __future__ import annotations

import math
import random

import pygame

from . import ambiental
from . import config
from . import utils
from .ui import (ACENTO, BORDA_SUAVE, FOCO, FUNDO_BOTAO, FUNDO_BOTAO_FOCO,
                 FUNDO_BOTAO_HOVER, MARGEM, RAIO, TEXTO, TEXTO_APAGADO,
                 TEXTO_FRACO, TEXTO_MEDIO, Botao, bloco, chip, divisor, largura as medir,
                 painel, scrim, seta, tecla, texto)


# ========================================================================= #
# Fundo vivo (vaga-lumes soltos)
# ========================================================================= #
class Fundo:
    def __init__(self, quantidade: int = 24) -> None:
        self.vagalumes = []
        for _ in range(quantidade):
            self.vagalumes.append({
                "x": random.uniform(0, config.LARGURA),
                "y": random.uniform(0, config.ALTURA),
                "vx": random.uniform(-12, 12),
                "vy": random.uniform(-9, 9),
                "fase": random.uniform(0, math.tau),
                "tamanho": random.uniform(0.9, 1.8),
                "velocidade": random.uniform(0.7, 1.6),
            })
        self.tempo = 0.0

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        for v in self.vagalumes:
            v["fase"] += dt * v["velocidade"]
            v["x"] += (v["vx"] + math.sin(v["fase"]) * 8) * dt
            v["y"] += (v["vy"] + math.cos(v["fase"] * 0.8) * 6) * dt
            if v["x"] < -20:
                v["x"] = config.LARGURA + 20
            elif v["x"] > config.LARGURA + 20:
                v["x"] = -20
            if v["y"] < -20:
                v["y"] = config.ALTURA + 20
            elif v["y"] > config.ALTURA + 20:
                v["y"] = -20

    def desenhar(self, tela: pygame.Surface) -> None:
        tela.fill(config.NOITE)
        for i in range(28):
            t = i / 28
            cor = utils.misturar((11, 16, 27), (6, 9, 16), t)
            pygame.draw.rect(tela, cor, (0, int(config.ALTURA * t),
                                         config.LARGURA, config.ALTURA // 28 + 1))

        # silhueta de mata na base
        sorteio = random.Random(7)
        linha_base = config.ALTURA - 46
        x = -20
        while x < config.LARGURA + 40:
            altura = sorteio.randint(30, 110)
            largura = sorteio.randint(30, 70)
            cor = sorteio.choice(((9, 13, 21), (8, 11, 19), (11, 16, 25)))
            pygame.draw.ellipse(tela, cor, (x, linha_base - altura, largura, altura * 2))
            x += largura - 12

        for v in self.vagalumes:
            brilho = 0.5 + 0.5 * math.sin(v["fase"] * 1.7)
            raio = max(2, int(v["tamanho"] * (1.6 + brilho * 1.4)))
            tamanho = raio * 6 + 2
            ponto = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
            centro = tamanho // 2
            camadas = 8
            for i in range(camadas, 0, -1):
                t = i / camadas
                r = max(1, int(raio * 2.2 * t))
                # BLEND_RGB_ADD ignora alpha: quem controla a intensidade é a cor
                k = (1 - t) ** 2.6 * (0.25 + 0.75 * brilho)
                cor = tuple(int(canal * k * 0.9) for canal in config.LUZ)
                pygame.draw.circle(ponto, cor, (centro, centro), r)
            nucleo = tuple(int(canal * (0.55 + 0.45 * brilho)) for canal in config.LUZ)
            pygame.draw.circle(ponto, nucleo, (centro, centro), max(1, raio // 2))
            pygame.draw.circle(ponto, (255, 255, 255), (centro, centro), max(1, raio // 4))
            tela.blit(ponto, (v["x"] - centro, v["y"] - centro),
                      special_flags=pygame.BLEND_RGB_ADD)


# ========================================================================= #
# Tela base
# ========================================================================= #
class Tela:
    def __init__(self, app) -> None:
        self.app = app
        self.recursos = app.recursos
        self.audio = app.recursos.audio
        self.dados = app.dados
        self.indice = 0
        self.botoes: list[Botao] = []
        self.fundo = Fundo()
        self.modo_teclado = False   # foco visível só depois que o teclado é usado

    # ------------------------------------------------------------------ #
    def entrar(self) -> None:
        self.indice = 0
        self.modo_teclado = False
        for botao in self.botoes:
            botao.medir(self.recursos.fonte("botao"))

    def _sincronizar(self) -> None:
        for i, botao in enumerate(self.botoes):
            botao.foco = self.modo_teclado and i == self.indice
            botao.desabilitado = False

    def navegar(self, passo: int) -> None:
        if not self.botoes:
            return
        self.modo_teclado = True
        self.indice = (self.indice + passo) % len(self.botoes)
        self._sincronizar()
        self.audio.tocar("navegar", volume=0.55)

    def confirmar(self) -> None:
        if self.botoes:
            self.audio.tocar("clique")
            self.botoes[self.indice].acao()

    # ------------------------------------------------------------------ #
    def tratar_evento(self, evento) -> None:
        if evento.type in (pygame.KEYDOWN,):
            if evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                self.navegar(1)
            elif evento.key in (pygame.K_UP, pygame.K_w):
                self.navegar(-1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirmar()
            elif evento.key == pygame.K_ESCAPE:
                self.app.ir_para_menu()
        elif evento.type == pygame.MOUSEMOTION:
            # o mouse assume: o foco do teclado some (nada de botão "preso" aceso)
            self.modo_teclado = False
            self._sincronizar()
            for i, botao in enumerate(self.botoes):
                if botao.tratar_mouse(evento.pos):
                    self.indice = i
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for botao in self.botoes:
                if botao.tratar_mouse(evento.pos, clicou=True):
                    self.audio.tocar("clique")
                    botao.acao()
                    return

    def atualizar(self, dt: float) -> None:
        self.fundo.atualizar(dt)
        for botao in self.botoes:
            botao.atualizar(dt)

    def desenhar(self, tela: pygame.Surface) -> None:
        self.fundo.desenhar(tela)

    # ------------------------------------------------------------------ #
    # Peças reutilizadas
    # ------------------------------------------------------------------ #
    def cabecalho(self, tela, rotulo: str, titulo_texto: str,
                  subtitulo: str | None = None) -> int:
        """Cabeçalho padrão: chip + título + subtítulo. Devolve o y seguinte."""
        chip(tela, self.recursos.fonte("pequena_forte"), rotulo, MARGEM, 40,
             cor_texto=ACENTO)
        y = 84
        texto(tela, self.recursos.fonte("titulo"), titulo_texto, TEXTO,
              config.LARGURA // 2, y, alinhamento="centro", sombra=(0, 0, 0))
        if subtitulo:
            y += 74
            texto(tela, self.recursos.fonte("corpo"), subtitulo, TEXTO_MEDIO,
                  config.LARGURA // 2, y, alinhamento="centro")
        return y

    def rodape(self, tela, dica: str, nota: str | None = None) -> None:
        """Faixa de rodapé própria: o texto nunca encosta no conteúdo acima."""
        faixa = pygame.Rect(0, config.ALTURA - 34, config.LARGURA, 34)
        pygame.draw.rect(tela, (8, 12, 20), faixa)
        pygame.draw.line(tela, BORDA_SUAVE, faixa.topleft, faixa.topright, 1)
        texto(tela, self.recursos.fonte("pequena"), dica, TEXTO_APAGADO,
              MARGEM, faixa.centery, vertical="meio")
        if nota:
            texto(tela, self.recursos.fonte("pequena"), nota, TEXTO_APAGADO,
                  config.LARGURA - MARGEM, faixa.centery, alinhamento="dir",
                  vertical="meio")


# ========================================================================= #
# MENU
# ========================================================================= #
class Menu(Tela):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.botoes = [
            Botao("História", self._historia, largura_min=272, icone="livro"),
            Botao("Infinito", self._infinito, largura_min=272, icone="play"),
            Botao("Como jogar", self._como_jogar, largura_min=272),
            Botao("Créditos", self._creditos, largura_min=272),
            Botao("Sair", self._sair, largura_min=272),
        ]
        self.app.deixar_espaco_livre = False
        self._posicionar()

    # ------------------------------------------------------------------ #
    def _posicionar(self) -> None:
        x = 88
        y = 282
        for botao in self.botoes:
            botao.ret.topleft = (x, y)
            y += botao.ret.height + 3

    def _historia(self) -> None:
        self.app.abrir_historia()

    def _infinito(self) -> None:
        self.app.abrir_infinito()

    def _como_jogar(self) -> None:
        self.app.abrir_ajuda()

    def _creditos(self) -> None:
        self.app.abrir_creditos()

    def _sair(self) -> None:
        self.app.rodando = False

    def entrar(self) -> None:
        super().entrar()
        self._posicionar()
        self._sincronizar()
        self.audio.tocar_musica("menu")

    # ------------------------------------------------------------------ #
    def tratar_evento(self, evento) -> None:
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
                passo = -1 if evento.key == pygame.K_LEFT else 1
                self.dados["dificuldade"] = (int(self.dados.get("dificuldade", 1)) + passo) % 3
                self._salvar()
                self.audio.tocar("navegar")
                return
            if evento.key == pygame.K_m:
                self.dados["mudo"] = self.audio.alternar_mudo()
                self._salvar()
                return
            if evento.key == pygame.K_ESCAPE:
                self.app.rodando = False
                return
        super().tratar_evento(evento)

    def _salvar(self) -> None:
        from . import persistencia
        persistencia.salvar(self.dados)

    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface) -> None:
        super().desenhar(tela)
        scrim(tela, 120)

        # ---------------- coluna esquerda: identidade ----------------
        texto(tela, self.recursos.fonte("titulo_grande"), "MIOPIA", config.LUZ,
              88, 40, sombra=(0, 0, 0))
        texto(tela, self.recursos.fonte("h2"), "a última luz da mata", TEXTO,
              90, 142)
        divisor(tela, 90, 184, 300)

        premissa = ("Um vaga-lume míope perdeu a colônia na noite da tempestade — "
                    "só enxerga o que a própria luz alcança.")
        bloco(tela, self.recursos.fonte("pequena"), premissa,
              pygame.Rect(90, 190, 384, 62), TEXTO_FRACO, entrelinha=1.4,
              centralizar_vertical=False)
        texto(tela, self.recursos.fonte("pequena"),
              "História: 4 fases · Infinito: fases que não acabam", ACENTO, 90, 256)

        # ---------------- botões ----------------
        self._posicionar()
        for botao in self.botoes:
            botao.desenhar(tela, self.recursos.fonte("botao"))

        # ---------------- painel de registro ----------------
        caixa = pygame.Rect(596, 150, 316, 244)
        painel(tela, caixa, raio=RAIO["lg"], brilho_topo=True)

        texto(tela, self.recursos.fonte("pequena_forte"), "REGISTRO DA MATA",
              TEXTO_FRACO, caixa.centerx, caixa.y + 20, alinhamento="centro")

        recorde = int(self.dados.get("recorde", 0))
        texto(tela, self.recursos.fonte("titulo_medio"), f"{recorde:05d}", config.OURO,
              caixa.centerx, caixa.y + 58, alinhamento="centro")
        texto(tela, self.recursos.fonte("pequena"), "melhor pontuação", TEXTO_APAGADO,
              caixa.centerx, caixa.y + 102, alinhamento="centro")

        divisor(tela, caixa.x + 26, caixa.y + 130, caixa.width - 52, BORDA_SUAVE)

        linhas = [
            ("Fase alcançada", f"{int(self.dados.get('bioma_max', 1))} de {len(config.BIOMAS)}"),
            ("Vitórias", str(int(self.dados.get("vitorias", 0)))),
            ("Infinito", f"{int(self.dados.get('melhor_infinito', 0))} fases"),
            ("Partidas", str(int(self.dados.get("partidas", 0)))),
        ]
        y = caixa.y + 146
        for rotulo, valor in linhas:
            texto(tela, self.recursos.fonte("pequena"), rotulo, TEXTO_FRACO,
                  caixa.x + 26, y, vertical="meio")
            texto(tela, self.recursos.fonte("pequena_forte"), valor, TEXTO,
                  caixa.right - 26, y, alinhamento="dir", vertical="meio")
            y += 24

        # ---------------- dificuldade ----------------
        dificuldade_caixa = pygame.Rect(596, 412, 316, 46)
        painel(tela, dificuldade_caixa, raio=RAIO["md"], alpha=230)
        texto(tela, self.recursos.fonte("pequena"), "Dificuldade", TEXTO_FRACO,
              dificuldade_caixa.x + 18, dificuldade_caixa.centery, vertical="meio")
        nomes = ["Fácil", "Normal", "Difícil"]
        valor = nomes[int(self.dados.get("dificuldade", 1))]
        texto(tela, self.recursos.fonte("pequena_forte"), valor, ACENTO,
              dificuldade_caixa.right - 74, dificuldade_caixa.centery,
              alinhamento="centro", vertical="meio")
        seta(tela, (dificuldade_caixa.right - 24, dificuldade_caixa.centery), "dir",
             TEXTO_FRACO, 6)
        seta(tela, (dificuldade_caixa.right - 128, dificuldade_caixa.centery), "esq",
             TEXTO_FRACO, 6)

        # ---------------- mascote (Lume) ----------------
        self._desenhar_lume(tela, 754, 492)

        # ---------------- rodapé ----------------
        som = "mudo" if self.audio.mudo else f"{int(self.audio.volume * 100)}%"
        self.rodape(
            tela,
            f"setas navegar · Enter escolher · A/D dificuldade · M som ({som}) · F11 tela cheia",
            "A3 · USJT",
        )

    # ------------------------------------------------------------------ #
    def _desenhar_lume(self, tela, x: float, y: float) -> None:
        """Mascote do menu: o Lume grande, respirando. Reforça a identidade."""
        t = self.fundo.tempo
        flutua = math.sin(t * 1.4) * 6
        y += flutua

        brilho = pygame.Surface((108, 108), pygame.SRCALPHA)
        for i in range(12, 0, -1):
            t = i / 12
            k = (1 - t) ** 2.2 * 0.22
            cor = tuple(int(canal * k) for canal in config.LUZ)
            pygame.draw.circle(brilho, cor, (54, 54), int(52 * t))
        tela.blit(brilho, (x - 54, y - 54), special_flags=pygame.BLEND_RGB_ADD)

        batida = math.sin(t * 22)
        for lado in (-1, 1):
            asa = pygame.Surface((46, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(asa, (*config.LUZ, 60), (0, 0, 46, 22))
            girada = pygame.transform.rotate(asa, lado * (20 + batida * 18))
            tela.blit(girada, (x - girada.get_width() / 2,
                               y - girada.get_height() / 2 - 6))

        corpo = config.LUZ_QUENTE
        pygame.draw.ellipse(tela, utils.escurecer(corpo, 0.45), (x - 12, y - 16, 24, 32))
        pygame.draw.circle(tela, corpo, (x, y - 18), 11)
        pygame.draw.circle(tela, (250, 252, 255), (x - 4, y - 20), 4)
        pygame.draw.circle(tela, (250, 252, 255), (x + 4, y - 20), 4)
        pygame.draw.circle(tela, (30, 38, 54), (x - 3, y - 20), 2)
        pygame.draw.circle(tela, (30, 38, 54), (x + 5, y - 20), 2)
        pygame.draw.circle(tela, config.LUZ, (x, y + 12), 6)

        texto(tela, self.recursos.fonte("pequena"), "Lume, o míope", TEXTO_APAGADO,
              x, max(y + 40, 534), alinhamento="centro")


# ========================================================================= #
# AJUDA
# ========================================================================= #
class Ajuda(Tela):
    def __init__(self, app, voltar) -> None:
        super().__init__(app)
        self.voltar = voltar
        self.botoes = [Botao("Voltar", self.voltar, largura_min=220, centralizar=True)]

    def entrar(self) -> None:
        super().entrar()
        self._sincronizar()

    def desenhar(self, tela: pygame.Surface) -> None:
        super().desenhar(tela)
        scrim(tela, 205)

        itens = [
            ("Objetivo", "coletar o orvalho da fase e voar até a colônia antes do amanhecer"),
            ("Modos", "História: 4 fases e dois desfechos · "
                      "Infinito: fases cada vez mais cheias, sem chefe"),
            ("Luz", "cada segundo gasta energia; sem energia a visão fecha e você perde vidas"),
            ("Orvalho", "recupera a luz — o orvalho dourado recupera muito mais"),
            ("Clarão", "Espaço: afasta morcegos, atordoa aranhas e cega a Coruja"),
            ("Inimigos", "morcego caça a luz · aranha corre reto · sombra age no escuro"),
            ("Coruja (chefe)", "ela caça pelo som: ande devagar e dê 3 clarões perto dela"),
            ("Dica", "depois de 9 s sem coletar, uma seta aponta o próximo orvalho"),
            ("Ambiental", "no fim de cada fase: mensagem e pergunta sobre ODS 15/4"),
        ]
        controles = (("WASD", "mover"), ("SHIFT", "correr"), ("ESPAÇO", "clarão"),
                     ("P", "pausa"), ("M", "som"), ("- / +", "volume"))

        f_rotulo = self.recursos.fonte("corpo_forte")
        f_desc = self.recursos.fonte("corpo")
        f_peq = self.recursos.fonte("pequena")
        f_peq_forte = self.recursos.fonte("pequena_forte")
        fonte_botao = self.recursos.fonte("botao")
        self.botoes[0].medir(fonte_botao)

        largura_painel = 840
        x_rotulo_off = 34
        x_desc_off = 176
        largura_desc = largura_painel - x_desc_off - 34
        altura_linha = f_desc.get_linesize()

        # ---- 1. mede tudo antes de desenhar (nada encosta em nada) ----
        altura_itens = 0
        for _, descricao in itens:
            linhas = utils.quebrar_texto(f_desc, descricao, largura_desc)
            altura_itens += max(28, len(linhas) * altura_linha) + 2

        topo_itens = 90
        altura_controles = 44 + 28            # rótulo + linha de teclas
        altura_botao = self.botoes[0].ret.height

        altura_painel = (topo_itens + altura_itens + 20 + altura_controles
                         + 14 + altura_botao + 18)
        painel_ret = pygame.Rect(0, 0, largura_painel, altura_painel)
        painel_ret.center = (config.LARGURA // 2, config.ALTURA // 2)
        if painel_ret.bottom > config.ALTURA - 12:
            painel_ret.bottom = config.ALTURA - 12
        if painel_ret.top < 12:
            painel_ret.top = 12

        painel(tela, painel_ret, raio=RAIO["lg"], alpha=250, brilho_topo=True)
        texto(tela, self.recursos.fonte("titulo_medio"), "Como jogar", TEXTO,
              painel_ret.centerx, painel_ret.y + 20, alinhamento="centro", sombra=(0, 0, 0))
        divisor(tela, painel_ret.x + 32, painel_ret.y + 72, painel_ret.width - 64,
                BORDA_SUAVE)

        x_rotulo = painel_ret.x + x_rotulo_off
        x_desc = painel_ret.x + x_desc_off

        y = painel_ret.y + topo_itens
        for rotulo, descricao in itens:
            texto(tela, f_rotulo, rotulo, ACENTO, x_rotulo, y)
            linhas = utils.quebrar_texto(f_desc, descricao, largura_desc)
            for i, linha in enumerate(linhas):
                texto(tela, f_desc, linha, TEXTO_FRACO, x_desc, y + i * altura_linha)
            y += max(28, len(linhas) * altura_linha) + 2

        # ---- 2. controles ----
        y += 20
        divisor(tela, painel_ret.x + 32, y, painel_ret.width - 64, BORDA_SUAVE)
        texto(tela, f_peq_forte, "CONTROLES", TEXTO_FRACO, x_rotulo, y + 16)

        x = x_rotulo
        y_teclas = y + 44
        for rotulo, acao in controles:
            caixa_tecla = tecla(tela, f_peq_forte, rotulo, x, y_teclas)
            texto(tela, f_peq, acao, TEXTO_APAGADO,
                  caixa_tecla.right + 8, caixa_tecla.centery, vertical="meio")
            x = caixa_tecla.right + 8 + medir(f_peq, acao) + 24

        # ---- 3. botão dentro do painel ----
        self.botoes[0].desenhar(tela, fonte_botao,
                                x=painel_ret.centerx - self.botoes[0].ret.width // 2,
                                y=painel_ret.bottom - altura_botao - 24)


# ========================================================================= #
# CRÉDITOS
# ========================================================================= #
class Creditos(Tela):
    def __init__(self, app, voltar) -> None:
        super().__init__(app)
        self.voltar = voltar
        self.botoes = [Botao("Voltar", self.voltar, largura_min=220, centralizar=True)]

    def entrar(self) -> None:
        super().entrar()
        self._sincronizar()

    def desenhar(self, tela: pygame.Surface) -> None:
        super().desenhar(tela)
        scrim(tela, 205)

        painel_ret = pygame.Rect(0, 0, 820, 510)
        painel_ret.center = (config.LARGURA // 2, config.ALTURA // 2 - 8)
        painel(tela, painel_ret, raio=RAIO["lg"], alpha=250, brilho_topo=True)

        texto(tela, self.recursos.fonte("titulo_medio"), "Créditos", TEXTO,
              painel_ret.centerx, painel_ret.y + 22, alinhamento="centro", sombra=(0, 0, 0))
        divisor(tela, painel_ret.x + 30, painel_ret.y + 74, painel_ret.width - 60, BORDA_SUAVE)

        blocos = [
            ("Arte", "desenhada em código com pygame.draw pelo grupo (sem asset de terceiro)"),
            ("Som", "efeitos e trilhas sintetizados por tools/gerar_audio.py — autoral / CC0"),
            ("Fontes", "Fredoka One e Nunito · SIL Open Font License 1.1 · google/fonts"),
            ("Motor", "Python 3 + pygame-ce"),
            ("História", "roteiro e personagens criados pela equipe"),
            ("Educação", "conteúdo ambiental apoiado nos ODS 15 (meta 15.5) e ODS 4 (meta 4.7)"),
            ("Projeto", "A3 integrada de Modelagem e de Usabilidade/Jogos — USJT, 2026"),
        ]
        y = painel_ret.y + 92
        for rotulo, descricao in blocos:
            linhas = len(utils.quebrar_texto(self.recursos.fonte("corpo"), descricao,
                                             painel_ret.width - 202))
            altura_linha = int(self.recursos.fonte("corpo").get_linesize() * 1.35)
            texto(tela, self.recursos.fonte("corpo_forte"), rotulo, ACENTO,
                  painel_ret.x + 34, y)
            bloco(tela, self.recursos.fonte("corpo"), descricao,
                  pygame.Rect(painel_ret.x + 168, y - 2,
                              painel_ret.width - 202, linhas * altura_linha),
                  TEXTO_FRACO, entrelinha=1.35, centralizar_vertical=False)
            y += max(24, linhas * altura_linha + 10)

        self.botoes[0].desenhar(tela, self.recursos.fonte("botao"),
                                x=painel_ret.centerx - self.botoes[0].ret.width // 2,
                                y=painel_ret.bottom - 70)


# ========================================================================= #
# FIM DE JOGO
# ========================================================================= #
class Fim(Tela):
    def __init__(self, app, jogo, novo_recorde: bool = False) -> None:
        super().__init__(app)
        self.jogo = jogo
        self.vitoria = jogo.fim == "vitoria"
        self.infinito = getattr(jogo, "infinito", False)
        self.novo_recorde = novo_recorde
        self.app.deixar_espaco_livre = True
        self.botoes = [
            Botao("Jogar de novo", self._denovo, largura_min=280, centralizar=True),
            Botao("Voltar ao menu", self._menu, largura_min=280, centralizar=True),
        ]
        self.tempo = 0.0

    def _denovo(self) -> None:
        self.app.ir_para_jogo()

    def _menu(self) -> None:
        self.app.ir_para_menu()

    def entrar(self) -> None:
        super().entrar()
        self._sincronizar()
        self.audio.tocar_musica("vitoria" if self.vitoria else "derrota")

    def atualizar(self, dt: float) -> None:
        super().atualizar(dt)
        self.tempo += dt

    def desenhar(self, tela: pygame.Surface) -> None:
        super().desenhar(tela)
        scrim(tela, 185)

        if self.infinito:
            titulo_final = "FIM DO SONHO"
            cor_titulo = config.PERIGO
        else:
            titulo_final = "REENCONTRO" if self.vitoria else "A NOITE ACABOU"
            cor_titulo = config.VERDE if self.vitoria else config.PERIGO
        texto(tela, self.recursos.fonte("titulo"), titulo_final, cor_titulo,
              config.LARGURA // 2, 76, alinhamento="centro", sombra=(0, 0, 0))

        if self.infinito:
            resumo = ("O Breu sonhou até onde você aguentou. Cada fase veio com mais "
                      "bichos que a anterior — e o amanhecer continua do outro lado "
                      "do sonho.")
        elif self.vitoria:
            resumo = ("O sol nasce e a colônia acende. Você ainda não enxerga longe, mas "
                      "reconhece cada ponto de luz.")
        else:
            resumo = ("A sua luz se apagou antes do amanhecer. A mata fica sem o caminho de "
                      "volta — e a colônia espera por outra noite.")
        bloco(tela, self.recursos.fonte("corpo"), resumo,
              pygame.Rect(180, 168, config.LARGURA - 360, 64), TEXTO_MEDIO,
              alinhamento="centro", entrelinha=1.5)

        # ---------------- cartão de resultados ----------------
        cartao = pygame.Rect(0, 0, 660, 132)
        cartao.center = (config.LARGURA // 2, 320)
        painel(tela, cartao, raio=RAIO["lg"], alpha=248, brilho_topo=True)

        if self.infinito:
            colunas = [
                ("PONTOS", f"{self.jogo.pontos:05d}", TEXTO),
                ("FASES", str(max(0, self.jogo.numero_bioma - 1)), ACENTO),
                ("MELHOR", str(int(self.dados.get("melhor_infinito", 0))), config.OURO),
            ]
        else:
            colunas = [
                ("PONTOS", f"{self.jogo.pontos:05d}", TEXTO),
                ("FASE", f"{self.jogo.bioma_index + 1}/{len(config.BIOMAS)}", ACENTO),
                ("RECORDE", f"{int(self.dados.get('recorde', 0)):05d}", config.OURO),
            ]
        largura_col = cartao.width // len(colunas)
        for i, (rotulo, valor, cor) in enumerate(colunas):
            centro_x = cartao.x + largura_col * i + largura_col // 2
            texto(tela, self.recursos.fonte("pequena_forte"), rotulo, TEXTO_FRACO,
                  centro_x, cartao.y + 26, alinhamento="centro")
            texto(tela, self.recursos.fonte("titulo_medio"), valor, cor,
                  centro_x, cartao.y + 62, alinhamento="centro")
            if i:
                x_sep = cartao.x + largura_col * i
                pygame.draw.line(tela, BORDA_SUAVE, (x_sep, cartao.y + 26),
                                 (x_sep, cartao.bottom - 26))

        if self.novo_recorde and self.tempo > 0.35:
            chip(tela, self.recursos.fonte("pequena_forte"), "NOVO RECORDE",
                 cartao.centerx, cartao.bottom + 10, cor_texto=config.OURO,
                 alinhamento="centro")

        # ---------------- botões ----------------
        y = 440
        for botao in self.botoes:
            botao.desenhar(tela, self.recursos.fonte("botao"),
                           x=config.LARGURA // 2 - botao.ret.width // 2, y=y)
            y += botao.ret.height + 10


# ========================================================================= #
# BRIEFING entre biomas (modo rápido — no modo História quem conta é a cutscene)
# ========================================================================= #
TEXTO_BIOMA = {
    0: "Asas molhadas, olhos embaçados. O orvalho ainda brilha nas folhas — "
       "beba antes que a noite engula o caminho.",
    1: "O córrego subiu com a tempestade. Do outro lado, aranhas tecem teias "
       "exatamente onde a sua luz passa.",
    2: "Os bambus estalam com o vento. Tem algo vivo morando nas sombras — e as "
       "sombras só criam coragem quando a sua luz fraqueja.",
    3: "A colônia está perto: você já ouve os assobios. Mas a Coruja também ouve. "
       "Voe baixo, respire fundo e só corra se for preciso.",
}


class Briefing(Tela):
    def __init__(self, app, bioma: int, ao_continuar, *, titulo: str | None = None,
                 chip_texto: str | None = None, texto: str | None = None,
                 meta: str | None = None, rotulo_botao: str = "Começar a fase",
                 dados_alt: dict | None = None) -> None:
        super().__init__(app)
        self.bioma = bioma
        self.ao_continuar = ao_continuar
        self.titulo_alt = titulo
        self.chip_alt = chip_texto
        self.texto_alt = texto
        self.meta_alt = meta
        self.dados_alt = dados_alt
        self.botoes = [Botao(rotulo_botao, self._continuar, largura_min=280,
                             centralizar=True)]
        self.app.deixar_espaco_livre = False

    def _continuar(self) -> None:
        self.ao_continuar()

    def entrar(self) -> None:
        super().entrar()
        self._sincronizar()
        self.audio.tocar_musica("historia")

    def desenhar(self, tela: pygame.Surface) -> None:
        super().desenhar(tela)
        scrim(tela, 150)
        dados = self.dados_alt or config.BIOMAS[self.bioma]
        cor_ambiente = dados["ambiente"]

        self.cabecalho(tela,
                       self.chip_alt or f"FASE {self.bioma + 1} DE {len(config.BIOMAS)}",
                       self.titulo_alt or dados.get("fase", dados["nome"]),
                       None if self.titulo_alt else dados["nome"])

        # painel medido pelo texto: nada de parágrafo encostando na borda
        fonte_texto = self.recursos.fonte("h2")
        largura_painel = 700
        largura_texto = largura_painel - 88
        corpo = self.texto_alt if self.texto_alt is not None \
            else TEXTO_BIOMA.get(self.bioma, "")
        linhas = utils.quebrar_texto(fonte_texto, corpo, largura_texto)
        altura_linha = int(fonte_texto.get_linesize() * 1.45)
        altura_texto = len(linhas) * altura_linha
        altura_painel = altura_texto + 24 + 24 + 96

        topo = 214 if not self.titulo_alt else 198
        # se o botão não couber abaixo do painel, o painel sobe
        espaco_baixo = config.ALTURA - 34 - 18 - 52 - 18
        if topo + altura_painel > espaco_baixo:
            topo = max(160, espaco_baixo - altura_painel)
        caixa = pygame.Rect((config.LARGURA - largura_painel) // 2, topo,
                            largura_painel, altura_painel)
        painel(tela, caixa, raio=RAIO["lg"], alpha=250, brilho_topo=True)

        # barrinha de ambiente: identifica o bioma também por forma/cor de apoio
        pygame.draw.rect(tela, cor_ambiente, (caixa.x + 28, caixa.y + 26, 3,
                                             altura_texto + 4), border_radius=2)

        bloco(tela, fonte_texto, corpo,
              pygame.Rect(caixa.x + 52, caixa.y + 24, largura_texto, altura_texto),
              TEXTO, entrelinha=1.45)

        # bloco da meta, com rótulo e valor em linhas separadas
        y = caixa.y + 24 + altura_texto + 22
        divisor(tela, caixa.x + 28, y, caixa.width - 56)
        texto(tela, self.recursos.fonte("pequena_forte"),
              "META" if self.meta_alt else "META DA FASE", TEXTO_FRACO,
              caixa.x + 52, y + 16)
        texto(tela, self.recursos.fonte("corpo"),
              self.meta_alt or
              f"coletar {dados['necessario']} orvalhos e alcançar a colônia antes do amanhecer",
              ACENTO, caixa.x + 52, y + 40)

        # o botão nunca encosta no painel nem no rodapé: se o texto for
        # longo, o painel sobe e o botão desce, os dois com folga de 16 px
        altura_botao = self.botoes[0].ret.height
        limite_baixo = config.ALTURA - 34 - 18 - altura_botao
        y_botao = min(limite_baixo, max(caixa.bottom + 18, limite_baixo))
        self.botoes[0].desenhar(tela, self.recursos.fonte("botao"),
                                x=config.LARGURA // 2 - self.botoes[0].ret.width // 2,
                                y=y_botao)
        self.rodape(tela, "Enter começar", "Esc volta ao menu")

    def tratar_evento(self, evento) -> None:
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.app.ir_para_menu()
            return
        super().tratar_evento(evento)


# ========================================================================= #
# MENSAGEM AMBIENTAL + PERGUNTA DE COMPREENSÃO (RF15 do PDF de Modelagem)
# ========================================================================= #
class Ambiental(Tela):
    """
    Aparece quando uma fase é concluída, antes da cutscene seguinte.

    Duas partes, como o documento pede:
      1. a mensagem ambiental da fase (ODS 15 · meta 15.5 / ODS 4 · meta 4.7);
      2. uma pergunta de compreensão, avaliada separada da habilidade de vencer:
         errar não tira vida, ponto nem progresso — mostra a resposta certa e
         explica. O avanço só acontece depois da resposta.
    """

    LARGURA_PAINEL = 760
    Y_PAINEL = 150
    ALTURA_OPCAO = 40
    ESPACO_OPCAO = 5

    def __init__(self, app, bioma: int, ao_continuar) -> None:
        super().__init__(app)
        self.bioma = bioma
        self.conteudo = ambiental.MENSAGENS[min(bioma, len(ambiental.MENSAGENS) - 1)]
        self.ao_continuar = ao_continuar
        self.resposta = -1           # -1 = ainda não respondeu
        self.hover = -1
        self.continuar = Botao("Seguir viagem", self._seguir, largura_min=300,
                               centralizar=True)
        self.botoes = []
        self.tempo = 0.0
        self.app.deixar_espaco_livre = False

    # ------------------------------------------------------------------ #
    @property
    def respondida(self) -> bool:
        return self.resposta >= 0

    @property
    def acertou(self) -> bool:
        return self.resposta == self.conteudo["correta"]

    # ---- geometria (tudo medido, nada de altura chutada) --------------- #
    def _fonte_corpo(self):
        return self.recursos.fonte("corpo")

    def _painel(self) -> pygame.Rect:
        """Painel da mensagem: altura = texto medido + rótulo + respiro."""
        fonte = self._fonte_corpo()
        largura_texto = self.LARGURA_PAINEL - 88
        linhas = utils.quebrar_texto(fonte, self.conteudo["mensagem"], largura_texto)
        altura_texto = len(linhas) * int(fonte.get_linesize() * 1.42)
        altura = 14 + 18 + 8 + altura_texto + 18
        return pygame.Rect((config.LARGURA - self.LARGURA_PAINEL) // 2,
                           self.Y_PAINEL, self.LARGURA_PAINEL, altura)

    def _y_conteudo(self) -> int:
        """Primeiro y livre abaixo da mensagem (e da linha de fonte)."""
        return self._painel().bottom + 32

    def _y_opcoes(self) -> int:
        if self.respondida:
            return self._y_conteudo() + 110
        return self._y_conteudo() + 62

    def _opcoes_ret(self) -> list[pygame.Rect]:
        caixas = []
        x = (config.LARGURA - self.LARGURA_PAINEL) // 2
        for i in range(len(self.conteudo["opcoes"])):
            y = self._y_opcoes() + i * (self.ALTURA_OPCAO + self.ESPACO_OPCAO)
            caixas.append(pygame.Rect(x, y, self.LARGURA_PAINEL, self.ALTURA_OPCAO))
        return caixas

    # ------------------------------------------------------------------ #
    def entrar(self) -> None:
        super().entrar()
        self.indice = 0
        self.continuar.medir(self.recursos.fonte("botao"))
        self.audio.tocar_musica("historia")

    def _responder(self, indice: int) -> None:
        if self.respondida:
            return
        self.resposta = indice
        if self.acertou:
            self.audio.tocar("vitoria", volume=0.55)
        else:
            self.audio.tocar("dano", volume=0.35)
        self.modo_teclado = True

    def _seguir(self) -> None:
        if not self.respondida:
            return
        self.audio.tocar("clique")
        self.ao_continuar()

    # ------------------------------------------------------------------ #
    def tratar_evento(self, evento) -> None:
        if evento.type == pygame.KEYDOWN:
            if not self.respondida:
                if evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                    self.modo_teclado = True
                    self.indice = (self.indice + 1) % len(self.conteudo["opcoes"])
                    self.audio.tocar("navegar", volume=0.5)
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    self.modo_teclado = True
                    self.indice = (self.indice - 1) % len(self.conteudo["opcoes"])
                    self.audio.tocar("navegar", volume=0.5)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                    pygame.K_SPACE, pygame.K_1, pygame.K_2, pygame.K_3):
                    if evento.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.indice = evento.key - pygame.K_1
                    self._responder(self.indice)
                return
            # já respondeu: qualquer confirmação segue
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,
                              pygame.K_ESCAPE):
                self._seguir()
            return

        if evento.type == pygame.MOUSEMOTION:
            self.modo_teclado = False
            self.hover = -1
            if not self.respondida:
                for i, caixa in enumerate(self._opcoes_ret()):
                    if caixa.collidepoint(evento.pos):
                        self.hover = i
            self.continuar.tratar_mouse(evento.pos)
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not self.respondida:
                for i, caixa in enumerate(self._opcoes_ret()):
                    if caixa.collidepoint(evento.pos):
                        self.indice = i
                        self._responder(i)
                        return
            elif self.continuar.tratar_mouse(evento.pos, clicou=True):
                self._seguir()

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        self.fundo.atualizar(dt)
        self.continuar.atualizar(dt)

    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface) -> None:
        self.fundo.desenhar(tela)
        scrim(tela, 182)

        d = self.conteudo
        chip(tela, self.recursos.fonte("pequena_forte"),
             f"FASE {self.bioma + 1} CONCLUÍDA", MARGEM, 26, cor_texto=config.VERDE)
        texto(tela, self.recursos.fonte("titulo_medio"), d["fase"], TEXTO,
              config.LARGURA // 2, 52, alinhamento="centro", sombra=(0, 0, 0))
        texto(tela, self.recursos.fonte("corpo"), d["bioma"], TEXTO_MEDIO,
              config.LARGURA // 2, 100, alinhamento="centro")

        # ---------------- mensagem ambiental (painel medido) ----------------
        caixa = self._painel()
        painel(tela, caixa, raio=RAIO["lg"], alpha=248, brilho_topo=True)
        pygame.draw.rect(tela, config.VERDE, (caixa.x + 22, caixa.y + 16, 3,
                                             caixa.height - 32), border_radius=2)
        texto(tela, self.recursos.fonte("pequena_forte"), "MENSAGEM AMBIENTAL",
              config.VERDE, caixa.x + 40, caixa.y + 12)
        bloco(tela, self._fonte_corpo(), d["mensagem"],
              pygame.Rect(caixa.x + 40, caixa.y + 36, caixa.width - 80,
                          caixa.height - 50),
              TEXTO, entrelinha=1.42, centralizar_vertical=False)
        texto(tela, self.recursos.fonte("pequena"), ambiental.FONTE, TEXTO_APAGADO,
              config.LARGURA // 2, caixa.bottom + 8, alinhamento="centro")

        if self.respondida:
            self._desenhar_resultado(tela)
        else:
            self._desenhar_pergunta(tela)

        self.rodape(tela,
                    "Setas escolhem · Enter responde · 1, 2 ou 3"
                    if not self.respondida else "Enter segue viagem",
                    "errar não custa vida nem ponto")

    # ------------------------------------------------------------------ #
    def _desenhar_pergunta(self, tela) -> None:
        d = self.conteudo
        x = (config.LARGURA - self.LARGURA_PAINEL) // 2
        y = self._y_conteudo()
        texto(tela, self.recursos.fonte("pequena_forte"), "PERGUNTA DE COMPREENSÃO",
              config.OURO, x, y)
        texto(tela, self.recursos.fonte("h2_forte"), d["pergunta"], TEXTO,
              x, y + 20)

        fonte = self.recursos.fonte("corpo")
        for i, (rotulo, ret) in enumerate(zip(d["opcoes"], self._opcoes_ret())):
            foco = self.modo_teclado and i == self.indice
            ativo = foco or i == self.hover
            fundo = FUNDO_BOTAO_FOCO if foco else (
                FUNDO_BOTAO_HOVER if i == self.hover else FUNDO_BOTAO)
            painel(tela, ret, fundo=fundo, borda=ACENTO if ativo else BORDA_SUAVE,
                   raio=RAIO["md"], alpha=248, espessura=1)
            if foco:
                pygame.draw.rect(tela, (*FOCO, 200), ret.inflate(8, 8), width=2,
                                 border_radius=RAIO["md"] + 4)
            # marcador A/B/C: a escolha não depende só de cor
            marca = pygame.Rect(ret.x + 12, ret.centery - 10, 20, 20)
            pygame.draw.rect(tela, ACENTO if ativo else FUNDO_BOTAO, marca,
                             border_radius=6)
            pygame.draw.rect(tela, ACENTO if ativo else BORDA_SUAVE, marca, width=1,
                             border_radius=6)
            texto(tela, self.recursos.fonte("pequena_forte"), "ABC"[i],
                  config.NOITE if ativo else TEXTO_FRACO, marca.centerx,
                  marca.centery, alinhamento="centro", vertical="meio")
            texto(tela, fonte, rotulo, TEXTO if ativo else TEXTO_MEDIO,
                  ret.x + 44, ret.centery, vertical="meio")

    # ------------------------------------------------------------------ #
    def _desenhar_resultado(self, tela) -> None:
        d = self.conteudo
        acertou = self.acertou
        cor = config.VERDE if acertou else config.PERIGO
        x = (config.LARGURA - self.LARGURA_PAINEL) // 2
        y = self._y_conteudo()

        titulo_fb = "Isso mesmo!" if acertou else "Quase: a resposta certa é a " \
            + "ABC"[d["correta"]] + "."
        texto(tela, self.recursos.fonte("h2_forte"), titulo_fb, cor, x, y)
        texto(tela, self.recursos.fonte("corpo"),
              ("sua resposta: " if acertou else "certa: ") + d["opcoes"][d["correta"]],
              TEXTO, x, y + 34)
        bloco(tela, self.recursos.fonte("corpo"), d["explicacao"],
              pygame.Rect(x, y + 66, self.LARGURA_PAINEL, 60), TEXTO_MEDIO,
              entrelinha=1.42, centralizar_vertical=False)

        self.continuar.desenhar(tela, self.recursos.fonte("botao"),
                                x=config.LARGURA // 2 - self.continuar.ret.width // 2,
                                y=config.ALTURA - 34 - 16 - self.continuar.ret.height)
