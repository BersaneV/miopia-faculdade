"""
jogo.py — a partida: estados, regras, luz, HUD e desenho.

Fluxo de uma fase:
  1. acordar com pouca luz no canto da mata;
  2. coletar o orvalho espalhado (a luz é o combustível e a arma);
  3. abrir a saída e chegar até ela antes do amanhecer;
  4. modo história: quatro fases, a última com a Coruja (chefe);
     modo infinito: fases geradas na hora, cada uma com mais bicho e
     sem chefe — não é a história repetida em rodízio.

Regras de vida: energia zerada não mata na hora — a luz pisca e, a cada
APAGAO_DANO_INTERVALO segundos, perde-se uma vida. Assim o jogador tem
tempo de reagir, o que é mais justo do que morte instantânea.
"""

from __future__ import annotations

import math
import random

import pygame

from . import config
from . import ui
from . import utils
from .atores import Inimigo, Jogador, Orvalho, Particula, explodir
from .mundo import Mundo


class Jogo:
    def __init__(self, app) -> None:
        self.app = app
        self.recursos = app.recursos
        self.audio = app.recursos.audio
        self.dados = app.dados

        self.cena = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA))
        self.mascara = pygame.Surface((config.AREA_LARGURA, config.AREA_ALTURA_USADA),
                                      pygame.SRCALPHA)

        self.pausado = False
        self.ativo = False
        self.fim: str | None = None
        self.modo = "historia"      # "historia" (4 biomas) | "infinito" (sem fim)
        self.numero_bioma = 1       # contagem absoluta (no infinito, 5, 6, 7…)

        self.bioma_index = 0
        self.dados_fase = config.BIOMAS[0]   # descritor da fase em curso
        self.mundo: Mundo | None = None
        self.jogador: Jogador | None = None
        self.orvalhos: list[Orvalho] = []
        self.inimigos: list[Inimigo] = []
        self.particulas: list[Particula] = []
        self.textos_flutuantes: list[dict] = []

        self.pontos = 0
        self.tempo = config.TEMPO_TOTAL
        self.necessario = 0
        self.coletados = 0

        self.tremor = 0.0
        self.flash = 0.0
        self.flash_cor = config.PERIGO
        self.banner_timer = 0.0
        self.dica_timer = 0.0
        self.sem_coleta = 0.0
        self._ciclos_apagao = 0
        self.saida_aberta = False
        self.abertura_timer = 0.0
        self.tempo_total_partida = 0.0

        # ---- chefe do bioma 4 (Coruja) ----
        self.chefe: Inimigo | None = None
        self.estado_chefe = "inativo"   # inativo · ativo · vencido
        self.aviso_chefe = 0.0          # "A CORUJA TE OUVIU"
        self.chefe_visor = 0.0          # quanto tempo o status fica no rodapé depois

        # menu de pausa: botões de verdade (mesmo componente do menu principal)
        self._indice_pausa = 0
        self._botoes_pausa = [
            ui.Botao("Continuar", self._despausar, largura_min=268, centralizar=True),
            ui.Botao("Reiniciar", self.reiniciar_partida, largura_min=268, centralizar=True),
            ui.Botao("Voltar ao menu", self._ir_para_menu, largura_min=268, centralizar=True),
        ]

    # ================================================================== #
    # Início / reinício
    # ================================================================== #
    def iniciar(self, modo: str = "historia") -> None:
        self.modo = modo if modo in ("historia", "infinito") else "historia"
        self.pontos = 0
        self.tempo = config.TEMPO_TOTAL
        self.tempo_total_partida = 0.0

        # ---- chefe do bioma 4 (Coruja) ----
        self.chefe: Inimigo | None = None
        self.estado_chefe = "inativo"   # inativo · ativo · vencido
        self.aviso_chefe = 0.0          # "A CORUJA TE OUVIU"
        self.chefe_visor = 0.0          # quanto tempo o status fica no rodapé depois
        self.fim = None
        self.pausado = False
        self.bioma_index = 0
        self.numero_bioma = 1
        self.dados_fase = config.BIOMAS[0]
        self._indice_pausa = 0
        self._carregar_bioma(0, bonus=False)
        self.ativo = True
        if self.modo == "infinito":
            self.banner_timer = 4.0
            self.dica_timer = 7.0

    def reiniciar_partida(self) -> None:
        self.iniciar(self.modo)

    # ------------------------------------------------------------------ #
    @property
    def infinito(self) -> bool:
        return self.modo == "infinito"

    @property
    def nivel(self) -> int:
        """Fase atual do modo infinito (1, 2, 3, …). Na história, a fase 1–4."""
        return self.numero_bioma

    def _carregar_bioma(self, indice: int, bonus: bool = True,
                        dados: dict | None = None) -> None:
        """
        Carrega uma fase. Na história o `indice` escolhe tudo (paleta,
        inimigos, texto). No infinito a fase é GERADA a partir do número:
        `indice` só decide o estilo de decoração do cenário.
        """
        self.bioma_index = indice
        if not self.infinito:
            self.numero_bioma = indice + 1
            dados = config.BIOMAS[indice]
        else:
            dados = dados or config.fase_infinita(self.numero_bioma)
        self.dados_fase = dados
        semente = random.randrange(1, 10**6)
        self.mundo = Mundo(indice, semente, dados)

        self.jogador = Jogador(*self.mundo.inicio)
        self.orvalhos = [Orvalho(*o["pos"], raro=o["raro"]) for o in self.mundo.orvalhos]
        self.inimigos = [
            Inimigo(i["tipo"], *i["pos"]) for i in self.mundo.inimigos
        ]
        tipos = list(self.mundo.dados["inimigos"].keys())

        # (a) inimigos extra da dificuldade escolhida — mesmo critério de antes
        extra = int(self.dados.get("dificuldade", 1)) * self.mundo.dados["semente_extra"]
        for _ in range(extra):
            celulas = list(self.mundo._distancias.keys())
            if not celulas or not tipos:
                break
            celula = random.choice(celulas)
            if self.mundo._distancias[celula] < 6:
                continue
            x, y = self.mundo._centro(celula)
            self.inimigos.append(Inimigo(random.choice(tipos), x, y))

        # (b) modo infinito: garante o número anunciado da fase. O mapa às
        # vezes recusa posição (espaçamento), e sem esse reforço a fase 7
        # podia sair com menos bichos que a 6 — o contrário do combinado.
        if self.infinito:
            alvo = min(config.LIMITE_INIMIGOS_INFINITO, dados.get("total_inimigos", 0))
            tentativas = 0
            while len(self.inimigos) < alvo and tentativas < 240:
                tentativas += 1
                if not tipos:
                    break
                livres = [c for c, d in self.mundo._distancias.items()
                          if d >= 5 and c != self.mundo.celula_saida]
                if not livres:
                    break
                x, y = self.mundo._centro(random.choice(livres))
                if any(abs(i.x - x) + abs(i.y - y) < 56 for i in self.inimigos):
                    continue
                self.inimigos.append(Inimigo(random.choice(tipos), x, y))
            self.inimigos = self.inimigos[:config.LIMITE_INIMIGOS_INFINITO]

        self.total_inimigos = len(self.inimigos)

        self.chefe = next((i for i in self.inimigos if getattr(i, "chefe", False)), None)
        self.estado_chefe = "inativo"
        self.aviso_chefe = 0.0
        self.chefe_visor = 0.0

        self.particulas.clear()
        self.textos_flutuantes.clear()
        # o pedido da fase nunca passa do que o mapa tem para dar
        self.necessario = min(dados["necessario"],
                              max(1, len(self.orvalhos) - 2))
        self.coletados = 0
        self.saida_aberta = False
        self.abertura_timer = 0.0
        self._ciclos_apagao = 0
        self.sem_coleta = 0.0
        self.banner_timer = 3.0
        # no infinito a dica só aparece na primeira fase; depois vira ruído
        self.dica_timer = 5.5 if (not self.infinito or self.numero_bioma == 1) else 0.0
        # cada bioma tem a sua trilha (o modo infinito passa por todas)
        self.audio.tocar_musica(dados.get("trilha", "jogo"))
        self.tremor = 0.0
        self.flash = 0.0
        # bônus de tempo ao entrar em um bioma novo
        if bonus:
            if self.infinito:
                # a noite não acaba: o relógio não tem teto e cada fase dá
                # menos fôlego que a anterior
                bonus_tempo = max(18.0,
                                  config.BONUS_TEMPO_BIOMA - 1.5 * (self.nivel - 1))
                self.tempo += bonus_tempo
            else:
                self.tempo = min(config.TEMPO_TOTAL,
                                 self.tempo + config.BONUS_TEMPO_BIOMA)

    def proximo_bioma(self) -> bool:
        """Avança de bioma. False se era o último (vitória na história)."""
        self.pontos += config.PONTOS_BIOMA
        if self.infinito:
            self.numero_bioma += 1
            # o índice só escolhe o estilo de decoração; a fase é gerada
            self._carregar_bioma((self.numero_bioma - 1) % len(config.BIOMAS))
            return True
        if self.bioma_index + 1 >= len(config.BIOMAS):
            return False
        self._carregar_bioma(self.bioma_index + 1)
        return True

    # ================================================================== #
    # Eventos
    # ================================================================== #
    def tratar_evento(self, evento) -> bool:
        """Retorna True se o evento foi consumido pelo jogo."""
        if self.pausado:
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                    self._navegar_pausa(1)
                    return True
                if evento.key in (pygame.K_UP, pygame.K_w):
                    self._navegar_pausa(-1)
                    return True
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._acionar_pausa()
                    return True
            elif evento.type == pygame.MOUSEMOTION:
                for i, botao in enumerate(self._botoes_pausa):
                    if botao.tratar_mouse(evento.pos):
                        self._indice_pausa = i
                        self._sincronizar_pausa()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for botao in self._botoes_pausa:
                    if botao.tratar_mouse(evento.pos, clicou=True):
                        self.audio.tocar("clique")
                        botao.acao()
                        return True

        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_p, pygame.K_ESCAPE):
                if self.fim is None:
                    self.pausado = not self.pausado
                    self._indice_pausa = 0
                    self._sincronizar_pausa()
                    self.audio.tocar("clique")
                return True
            if evento.key == pygame.K_m:
                mudo = self.audio.alternar_mudo()
                self.dados["mudo"] = mudo
                self._salvar_preferencias()
                return True
            if self.pausado:
                if evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.audio.ajustar_volume(-0.1)
                    self.dados["volume"] = self.audio.volume
                    self._salvar_preferencias()
                    return True
                if evento.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.audio.ajustar_volume(0.1)
                    self.dados["volume"] = self.audio.volume
                    self._salvar_preferencias()
                    return True
                if evento.key == pygame.K_r:
                    self.reiniciar_partida()
                    return True
                if evento.key == pygame.K_v:
                    self.ativo = False
                    self.app.ir_para_menu()
                    return True
            return False
        return False

    def _despausar(self) -> None:
        self.pausado = False

    def _ir_para_menu(self) -> None:
        self.ativo = False
        self.pausado = False
        self.app.ir_para_menu()

    def _salvar_preferencias(self) -> None:
        from . import persistencia
        persistencia.salvar(self.dados)

    # ================================================================== #
    # Atualização
    # ================================================================== #
    def atualizar(self, dt: float) -> None:
        if not self.ativo or self.fim is not None:
            return
        self.banner_timer = max(0.0, self.banner_timer - dt)
        self.dica_timer = max(0.0, self.dica_timer - dt)
        self.tremor = max(0.0, self.tremor - dt * 34)
        self.flash = max(0.0, self.flash - dt * 2.6)
        self.abertura_timer += dt

        if self.pausado:
            for botao in self._botoes_pausa:
                botao.atualizar(dt)
            return

        self.tempo_total_partida += dt
        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = 0
            self._terminar("derrota")
            return

        teclas = pygame.key.get_pressed()
        self.jogador.atualizar(dt, self.mundo, teclas, self.particulas)

        # ---- pulso (clarão) ----
        if teclas[pygame.K_SPACE] and self.jogador.pode_pulsar():
            # o cooldown evita repetir enquanto a tecla está pressionada
            if self.jogador.pulsar(self.particulas):
                self.audio.tocar("pulso")
                self.tremor = max(self.tremor, 5)
                self._aplicar_pulso()

        # ---- coleta de orvalho ----
        self.sem_coleta += dt
        for orvalho in self.orvalhos:
            orvalho.atualizar(dt, self.tempo_total_partida)
            if orvalho.coletado:
                continue
            if utils.distancia((orvalho.x, orvalho.y), self.jogador.pos()) < 16 + (6 if orvalho.raro else 0):
                orvalho.coletado = True
                self.coletados += 1
                self.pontos += orvalho.valor
                self.jogador.beber(
                    config.ORVALHO_RARO_ENERGIA if orvalho.raro else config.ORVALHO_ENERGIA,
                    self.particulas,
                )
                self.audio.tocar("raro" if orvalho.raro else "coleta")
                self.sem_coleta = 0.0
                cor = config.OURO if orvalho.raro else config.AGUA
                explodir(self.particulas, orvalho.x, orvalho.y, cor, quantidade=10,
                         forca=80 if not orvalho.raro else 130, vida=0.6)
                self._texto_flutuante(
                    orvalho.x, orvalho.y - 14,
                    f"+{orvalho.valor}", cor,
                )
                if orvalho.raro:
                    self.tremor = 3
                if self.coletados >= self.necessario and not self.saida_aberta:
                    self.saida_aberta = True
                    self.audio.tocar("abertura")
                    self.flash_cor = config.VERDE
                    self.flash = 0.6
                    self._texto_flutuante(
                        self.jogador.x, self.jogador.y - 40,
                        "A COLÔNIA SE ABRIU!", config.VERDE,
                    )

        # ---- chefe: a Coruja se acalma depois de apanhar de clarão ----
        if self.chefe and self.estado_chefe != "vencido":
            if self.estado_chefe == "inativo" and \
                    utils.distancia((self.chefe.x, self.chefe.y), self.jogador.pos()) < 260:
                self.estado_chefe = "ativo"
                self.aviso_chefe = 2.0
                self.audio.tocar("dano", volume=0.45)
            if self.chefe.exposicao >= 0.99:
                self._acalmar_coruja()
        self.aviso_chefe = max(0.0, self.aviso_chefe - dt)
        if self.estado_chefe == "vencido":
            self.chefe_visor = max(0.0, self.chefe_visor - dt)

        # ---- inimigos ----
        dificuldade = self.dados.get("dificuldade", 1)
        for inimigo in self.inimigos:
            inimigo.atualizar(dt, self.mundo, self.jogador, dificuldade)
            inimigo.separar(self.inimigos, dt)
            if self.jogador.intangivel <= 0 and inimigo.colide_com(self.jogador):
                if self.jogador.levar_dano(inimigo.pos()):
                    inimigo.acertou(self.jogador)
                    self.audio.tocar("dano")
                    self.tremor = 9
                    self.flash_cor = config.PERIGO
                    self.flash = 0.75
                    explodir(self.particulas, self.jogador.x, self.jogador.y,
                             config.PERIGO, quantidade=14, forca=120, vida=0.7)
                    self._texto_flutuante(self.jogador.x, self.jogador.y - 26, "-1 vida",
                                          config.PERIGO)
                    if self.jogador.morto:
                        self._terminar("derrota")
                        return

        # ---- apagão: perder vida por ficar no escuro ----
        if self.jogador.tempo_apagado > 0:
            ciclos = int(self.jogador.tempo_apagado // config.APAGAO_DANO_INTERVALO)
            if ciclos > 0 and getattr(self, "_ciclos_apagao", 0) < ciclos:
                self._ciclos_apagao = ciclos
                if self.jogador.levar_dano():
                    # sobrevivência: quem apaga recebe um resto de luz para reagir
                    self.jogador.energia = max(self.jogador.energia, 55.0)
                    self._ciclos_apagao = 0
                    self.sem_coleta = 0.0
                    self.audio.tocar("dano")
                    self.tremor = 8
                    self.flash_cor = config.PERIGO
                    self.flash = 0.8
                    self._texto_flutuante(self.jogador.x, self.jogador.y - 26,
                                          "a luz apagou!", config.PERIGO)
                    if self.jogador.morto:
                        self._terminar("derrota")
                        return
        else:
            self._ciclos_apagao = 0

        # ---- saída aberta: chegar até ela fecha o bioma ----
        if self.saida_aberta:
            if utils.distancia(self.jogador.pos(), self.mundo.saida) < 26:
                self._fechar_bioma()
                return

        # ---- partículas e textos ----
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]
        for t in self.textos_flutuantes:
            t["vida"] -= dt
            t["y"] -= 26 * dt
        self.textos_flutuantes = [t for t in self.textos_flutuantes if t["vida"] > 0]

    # ------------------------------------------------------------------ #
    def _aplicar_pulso(self) -> None:
        pulso = self.jogador.pulso
        if not pulso:
            return
        for inimigo in self.inimigos:
            dist = utils.distancia((inimigo.x, inimigo.y), (pulso.x, pulso.y))
            if dist <= pulso.raio_max * 1.15:
                inimigo.assustar(2.6)
                explodir(self.particulas, inimigo.x, inimigo.y, config.LUZ,
                         quantidade=6, forca=60, vida=0.5)

    def _acalmar_coruja(self) -> None:
        """Terceiro clarão: a Coruja se acalma (convence, não mata)."""
        coruja = self.chefe
        if not coruja:
            return
        self.estado_chefe = "vencido"
        self.chefe_visor = 6.0
        coruja.calma = 1.0
        coruja.exposicao = 1.0
        coruja.estado = "patrulha"
        coruja.vx = coruja.vy = 0.0
        coruja.atordoado = 0.0
        self.pontos += config.PONTOS_CHEFE
        self.audio.tocar("vitoria", volume=0.8)
        self.flash_cor = config.OURO
        self.flash = 0.7
        self.tremor = 6
        explodir(self.particulas, coruja.x, coruja.y, config.OURO, quantidade=26,
                 forca=150, vida=1.0, tamanho=3)
        self._texto_flutuante(coruja.x, coruja.y - 42, f"+{config.PONTOS_CHEFE}",
                              config.OURO)
        self._texto_flutuante(self.jogador.x, self.jogador.y - 46,
                              "A CORUJA SE ACALMOU", config.VERDE)

    def _texto_flutuante(self, x, y, conteudo, cor) -> None:
        self.textos_flutuantes.append({"x": x, "y": y, "texto": conteudo,
                                       "cor": cor, "vida": 1.1})

    def _fechar_bioma(self) -> None:
        self.audio.tocar("vitoria")
        self.flash_cor = config.VERDE
        self.flash = 1.0
        explodir(self.particulas, self.jogador.x, self.jogador.y, config.VERDE,
                 quantidade=30, forca=180, vida=1.2, tamanho=4)
        fase_concluida = self.bioma_index      # a fase que ACABOU de ser fechada
        ultimo = self.proximo_bioma()
        if not ultimo:
            self._terminar("vitoria")
            return
        if self.infinito:
            # sem tela no meio: um aviso curto no topo e a fase emenda
            self.banner_timer = 2.6
            return
        self.app.mostrar_intervalo(fase_concluida, ao_voltar=self._retomar_do_briefing)

    def _retomar_do_briefing(self) -> None:
        self.ativo = True
        self.banner_timer = 4.0

    def _terminar(self, motivo: str) -> None:
        self.fim = motivo
        if motivo == "vitoria":
            self.pontos += int(self.tempo) * config.PONTOS_SEGUNDO
            self.pontos += self.jogador.vidas * config.PONTOS_VIDA
            self.audio.tocar("vitoria_final")
            self.audio.tocar_musica("vitoria")
        else:
            self.audio.tocar("derrota")
            self.audio.tocar_musica("derrota")
        self.tremor = 12
        self.app.mostrar_fim(self)

    # ================================================================== #
    # Desenho
    # ================================================================== #
    def desenhar(self, tela: pygame.Surface) -> None:
        if not self.mundo or not self.jogador:
            return

        cena = self.cena
        cena.fill(config.NOITE)
        self.mundo.desenhar(cena)

        # saída
        self._desenhar_saida(cena)

        # entidades ordenadas por y (profundidade simples)
        desenhaveis = [*self.orvalhos, *self.inimigos, self.jogador]
        desenhaveis.sort(key=lambda e: getattr(e, "y", 0))
        for entidade in desenhaveis:
            if isinstance(entidade, Orvalho):
                entidade.desenhar(cena, self.recursos)
            elif isinstance(entidade, Jogador):
                entidade.desenhar(cena, self.recursos)
            else:
                entidade.desenhar(cena)

        for particula in self.particulas:
            particula.desenhar(cena)

        # escuridão + luz
        self._aplicar_escuridao(cena)

        # pulso desenhado por cima da escuridão (é luz)
        if self.jogador.pulso:
            self.jogador.pulso.desenhar(cena, self.recursos)

        # textos flutuantes
        for t in self.textos_flutuantes:
            alpha = int(255 * min(1.0, t["vida"] / 0.5))
            img = utils.texto(self.recursos.fonte("pequena_forte"), t["texto"], t["cor"],
                              sombra=(0, 0, 0))
            img = img.copy()
            img.set_alpha(alpha)
            cena.blit(img, (t["x"] - img.get_width() / 2, t["y"]))

        # tremor de tela
        tremor_x = tremor_y = 0
        if self.tremor > 0.3:
            tremor_x = random.uniform(-self.tremor, self.tremor)
            tremor_y = random.uniform(-self.tremor, self.tremor)

        tela.fill(config.NOITE)
        tela.blit(cena, (int(tremor_x), config.HUD_ALTURA + int(tremor_y)))

        # vinheta (dá profundidade de noite)
        tela.blit(self.recursos.vinheta(), (0, 0))

        # flash de dano / vitória
        if self.flash > 0:
            camada = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
            camada.fill((*self.flash_cor, int(90 * self.flash)))
            tela.blit(camada, (0, 0))

        self._desenhar_hud(tela)

        if self.banner_timer > 0 and not self.pausado:
            self._desenhar_banner(tela)

        if self.dica_timer > 0 and not self.pausado:
            self._desenhar_dica(tela)

        if self.jogador.energia < 22 and not self.pausado and self.fim is None:
            self._desenhar_aviso_luz(tela)

        if self.sem_coleta > 9 and not self.saida_aberta and not self.pausado:
            self._desenhar_seta_ajuda(tela)

        if self.chefe and self.aviso_chefe > 0 and not self.pausado:
            self._desenhar_aviso_chefe(tela)

        if self.pausado:
            self._desenhar_pausa(tela)

    # ------------------------------------------------------------------ #
    def _desenhar_saida(self, cena: pygame.Surface) -> None:
        x, y = int(self.mundo.saida[0]), int(self.mundo.saida[1])
        pulso = 0.5 + 0.5 * math.sin(self.abertura_timer * 2.4)
        aberta = self.saida_aberta

        cor = config.VERDE if aberta else (60, 78, 96)
        alpha = 60 + int(60 * pulso) if aberta else 30
        aura = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*cor, alpha), (60, 60), 40 + int(8 * pulso))
        pygame.draw.circle(aura, (*cor, min(255, alpha + 40)), (60, 60), 22, 2)
        cena.blit(aura, (x - 60, y - 60))

        # pequenas luzes ao redor (colônia de vaga-lumes)
        for i in range(5):
            ang = self.abertura_timer * 0.9 + i * math.tau / 5
            raio = 26 + math.sin(self.abertura_timer * 1.6 + i) * 5
            px = x + math.cos(ang) * raio
            py = y + math.sin(ang) * raio
            cor_p = config.LUZ if aberta else (90, 104, 124)
            pygame.draw.circle(cena, cor_p, (int(px), int(py)), 2)

    # ------------------------------------------------------------------ #
    def _aplicar_escuridao(self, cena: pygame.Surface) -> None:
        jogador = self.jogador
        mascara = self.mascara
        mascara.fill((0, 0, 0, 248))

        raio = jogador.raio_luz
        if jogador.luz_fraca:
            # piscada de luz fraca (feedback de perigo)
            raio *= 0.95 + random.uniform(-0.04, 0.04)

        def abrir(x: float, y: float, r: float, intensidade: float = 1.0) -> None:
            if r < 8:
                return
            # penumbra: um círculo maior e fraco por baixo suaviza a borda
            if intensidade >= 0.9:
                penumbra = self.recursos.escuro(r * 1.55)
                copia_pen = penumbra.copy()
                copia_pen.set_alpha(70)
                mascara.blit(copia_pen, (int(x) - penumbra.get_width() // 2,
                                         int(y) - penumbra.get_height() // 2),
                             special_flags=pygame.BLEND_RGBA_SUB)
            grad = self.recursos.escuro(r)
            copia = grad
            if intensidade < 1.0:
                copia = grad.copy()
                copia.set_alpha(int(255 * intensidade))
            mascara.blit(copia, (int(x) - grad.get_width() // 2,
                                 int(y) - grad.get_height() // 2),
                         special_flags=pygame.BLEND_RGBA_SUB)

        # luz principal
        abrir(jogador.x, jogador.y, raio)

        for orvalho in self.orvalhos:
            if orvalho.coletado:
                continue
            abrir(orvalho.x, orvalho.y, 74 if orvalho.raro else 52, 0.6)

        if self.saida_aberta:
            abrir(*self.mundo.saida, 96)
        else:
            abrir(*self.mundo.saida, 44, 0.6)

        if jogador.pulso:
            abrir(jogador.pulso.x, jogador.pulso.y, jogador.pulso.raio + 30)

        for particula in self.particulas:
            abrir(particula.x, particula.y, 26, 0.35)

        cena.blit(mascara, (0, 0))

        # ---- luzes distantes visíveis no escuro ----
        # É o coração do jogo: o vaga-lume não vê o mundo, vê as luzes.
        # Orvalho, saída e (de leve) inimigos brilham por cima da escuridão.
        for orvalho in self.orvalhos:
            if orvalho.coletado:
                continue
            distancia_jogador = utils.distancia((orvalho.x, orvalho.y), jogador.pos())
            if distancia_jogador > 720:
                continue
            cor = config.OURO if orvalho.raro else config.AGUA
            raio_brilho = (26 if orvalho.raro else 15) * (1.0 + 0.08 * math.sin(orvalho.fase * 2))
            brilho = self.recursos.brilho(raio_brilho, cor)
            copia = brilho.copy()
            copia.set_alpha(int(utils.clamp(1.2 - distancia_jogador / 720, 0.18, 1.0) * 115))
            cena.blit(copia, (int(orvalho.x) - brilho.get_width() // 2,
                              int(orvalho.y + math.sin(orvalho.fase) * 3) - brilho.get_height() // 2),
                      special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(cena, cor, (int(orvalho.x), int(orvalho.y + math.sin(orvalho.fase) * 3)),
                               2 if not orvalho.raro else 3)

        # farol da colônia
        dist_saida = utils.distancia(self.mundo.saida, jogador.pos())
        if dist_saida < 900:
            cor_saida = config.VERDE if self.saida_aberta else (74, 96, 120)
            alcance = 74 if self.saida_aberta else 42
            farol = self.recursos.brilho(alcance, cor_saida)
            copia = farol.copy()
            copia.set_alpha(int(utils.clamp(1.15 - dist_saida / 900, 0.3, 1.0) * (190 if self.saida_aberta else 120)))
            cena.blit(copia, (int(self.mundo.saida[0]) - farol.get_width() // 2,
                              int(self.mundo.saida[1]) - farol.get_height() // 2),
                      special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(cena, cor_saida, (int(self.mundo.saida[0]), int(self.mundo.saida[1])),
                               4 if self.saida_aberta else 3)

        # olhos dos inimigos (só os próximos, para dar tensão sem entregar tudo)
        for inimigo in self.inimigos:
            dist = utils.distancia((inimigo.x, inimigo.y), jogador.pos())
            if dist > 300 or inimigo.tipo == "sombra":
                continue
            cor_olho = config.PERIGO if inimigo.estado in ("cacar", "atacar") else (196, 176, 255)
            if inimigo.atordoado > 0:
                cor_olho = config.AGUA
            for lado in (-3, 3):
                pygame.draw.circle(cena, cor_olho, (int(inimigo.x + lado), int(inimigo.y - 2)), 1)

        # o vaga-lume é a fonte da luz: ele mesmo nunca fica no escuro
        jogador.desenhar(cena, self.recursos)

        # brilho aditivo do vaga-lume (bem mais discreto que a área iluminada)
        intensidade = 1.0 if not jogador.luz_fraca else 0.72 + random.uniform(-0.08, 0.08)
        halo = self.recursos.brilho(min(64, raio * 0.34), config.LUZ_QUENTE)
        halo_copia = halo.copy()
        halo_copia.set_alpha(int(62 * intensidade))
        cena.blit(halo_copia, (int(jogador.x) - halo.get_width() // 2,
                               int(jogador.y) - halo.get_height() // 2),
                  special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.circle(cena, config.LUZ, (int(jogador.x), int(jogador.y + 6)), 4)

    # ------------------------------------------------------------------ #
    def _desenhar_hud(self, tela: pygame.Surface) -> None:
        """HUD em colunas, com rótulo e valor centrados pela métrica do glifo."""
        r = self.recursos
        f_rot = r.fonte("pequena_forte")
        f_num = r.fonte("hud_num")
        f_val = r.fonte("hud")
        meio = 52          # centro vertical da faixa de valores
        topo_rotulo = 9

        pygame.draw.rect(tela, config.NOITE_SUAVE, (0, 0, config.LARGURA, config.HUD_ALTURA))

        # ---------------- vidas ----------------
        ui.texto(tela, f_rot, "VIDAS", ui.TEXTO_FRACO, 24, topo_rotulo)
        for i in range(config.VIDAS_INICIAIS):
            x = 30 + i * 24
            cheia = i < self.jogador.vidas
            cor = config.LUZ_QUENTE if cheia else (40, 48, 64)
            pygame.draw.circle(tela, utils.escurecer(cor, 0.55), (x, meio), 8)
            pygame.draw.circle(tela, cor, (x, meio), 5)
            if cheia:
                pygame.draw.circle(tela, (255, 255, 255), (x - 2, meio - 2), 1)

        # ---------------- luz ----------------
        x_luz = 128
        ui.texto(tela, f_rot, "LUZ", ui.TEXTO_FRACO, x_luz, topo_rotulo)
        proporcao = utils.clamp(self.jogador.energia / config.ENERGIA_MAX, 0, 1)
        cor_barra = config.LUZ_QUENTE
        if proporcao < 0.25:
            cor_barra = config.PERIGO
        elif proporcao < 0.5:
            cor_barra = (255, 168, 96)
        caixa_barra = pygame.Rect(x_luz, meio - 7, 158, 14)
        ui.barra_progresso(tela, caixa_barra, proporcao, cor=cor_barra)
        ui.texto(tela, f_val, f"{int(self.jogador.energia):3d}", ui.TEXTO,
                 caixa_barra.right + 10, meio, vertical="meio")

        # ---------------- orvalho ----------------
        x_orv = 356
        ui.texto(tela, f_rot, "ORVALHO", ui.TEXTO_FRACO, x_orv, topo_rotulo)
        pygame.draw.circle(tela, config.AGUA, (x_orv + 9, meio), 8)
        pygame.draw.circle(tela, (255, 255, 255), (x_orv + 7, meio - 3), 2)
        ui.texto(tela, f_num, f"{self.coletados}/{self.necessario}", config.AGUA,
                 x_orv + 26, meio, vertical="meio")

        # ---------------- amanhecer ----------------
        centro = 588
        pouco_tempo = self.tempo <= 60
        if self.infinito:
            # sem amanhecer, o relógio é o fôlego de Lume dentro do sonho
            rotulo_tempo = "CORRE" if pouco_tempo else "FÔLEGO"
        else:
            rotulo_tempo = "CORRE" if pouco_tempo else "AMANHECER"
        ui.texto(tela, f_rot, rotulo_tempo,
                 config.PERIGO if pouco_tempo else ui.TEXTO_FRACO, centro, topo_rotulo,
                 alinhamento="centro")
        ui.texto(tela, f_num, utils.formatar_tempo(self.tempo),
                 config.PERIGO if pouco_tempo else ui.TEXTO,
                 centro, meio, alinhamento="centro", vertical="meio")

        # ---------------- pontos ----------------
        ui.texto(tela, f_rot, "PONTOS", ui.TEXTO_FRACO, config.LARGURA - 24,
                 topo_rotulo, alinhamento="dir")
        ui.texto(tela, f_num, f"{self.pontos:05d}", ui.TEXTO, config.LARGURA - 24, meio,
                 alinhamento="dir", vertical="meio")

        # ---------------- progresso do bioma ----------------
        pygame.draw.rect(tela, (18, 25, 38), (0, config.HUD_ALTURA - 5, config.LARGURA, 5))
        progresso = int(config.LARGURA * min(1.0, self.coletados / max(1, self.necessario)))
        if progresso:
            pygame.draw.rect(tela, config.VERDE if self.saida_aberta else config.AGUA,
                             (0, config.HUD_ALTURA - 5, progresso, 5))
        pygame.draw.line(tela, (26, 36, 54), (0, config.HUD_ALTURA - 1),
                         (config.LARGURA, config.HUD_ALTURA - 1), 1)

        # ---------------- rodapé ----------------
        rodape = pygame.Rect(0, config.ALTURA - config.RODAPE_ALTURA,
                             config.LARGURA, config.RODAPE_ALTURA)
        pygame.draw.rect(tela, config.NOITE_SUAVE, rodape)
        pygame.draw.line(tela, (24, 33, 50), rodape.topleft, rodape.topright, 1)

        dados = self.dados_fase
        if self.infinito:
            nome = f"Infinito · Fase {self.numero_bioma} · {dados['fase']}"
        else:
            nome = (f"Fase {self.numero_bioma}/{len(config.BIOMAS)} · "
                    f"{dados['fase']} — {dados['nome']}")
        ui.texto(tela, f_rot, nome, dados["ambiente"], 24, rodape.centery, vertical="meio")

        if self._chefe_no_rodape():
            self._desenhar_chefe_rodape(tela, rodape)
        else:
            lembrete = "WASD mover · Shift correr · ESPAÇO clarão · P pausa · M som"
            ui.texto(tela, r.fonte("pequena"), lembrete, ui.TEXTO_APAGADO,
                     config.LARGURA - 24, rodape.centery, alinhamento="dir", vertical="meio")

    def _desenhar_banner(self, tela: pygame.Surface) -> None:
        if self.banner_timer <= 0:
            return
        dados = self.dados_fase
        t = min(1.0, self.banner_timer / 0.6) if self.banner_timer < 0.6 else 1.0
        alpha = int(255 * utils.suavizar(t))
        painel = pygame.Surface((config.LARGURA, 84), pygame.SRCALPHA)
        pygame.draw.rect(painel, (5, 8, 14, int(140 * t)), painel.get_rect())
        pygame.draw.line(painel, (*dados["ambiente"], int(120 * t)), (0, 83),
                         (config.LARGURA, 83), 1)
        titulo = f"FASE {self.numero_bioma} · {dados['fase'].upper()}"
        utils.texto_centrado(painel, self.recursos.fonte("h2_forte"), titulo,
                             dados["ambiente"], config.LARGURA // 2, 30)
        painel.set_alpha(alpha)
        tela.blit(painel, (0, config.HUD_ALTURA))

    def _desenhar_dica(self, tela: pygame.Surface) -> None:
        dados = self.dados_fase
        img = utils.texto(self.recursos.fonte("corpo"), dados["dica"], config.TEXTO,
                          sombra=(0, 0, 0))
        caixa = pygame.Rect(0, 0, img.get_width() + 32, img.get_height() + 18)
        caixa.center = (config.LARGURA // 2, config.ALTURA - 96)
        alpha = int(255 * min(1.0, self.dica_timer / 1.0))
        painel = pygame.Surface(caixa.size, pygame.SRCALPHA)
        pygame.draw.rect(painel, (8, 12, 20, min(230, alpha)), painel.get_rect(),
                         border_radius=10)
        pygame.draw.rect(painel, (*config.AGUA, min(160, alpha)), painel.get_rect(),
                         width=1, border_radius=10)
        painel.blit(img, (16, 9))
        painel.set_alpha(alpha)
        tela.blit(painel, caixa.topleft)

    def _desenhar_aviso_luz(self, tela: pygame.Surface) -> None:
        """Aviso pulsante quando a energia está no fim — feedback antes do dano."""
        intensidade = 0.35 + 0.65 * abs(math.sin(self.abertura_timer * 4.0))
        alpha = int(200 * intensidade)
        mensagem = "SUA LUZ ESTÁ ACABANDO — PROCURE ORVALHO"
        imagem = utils.texto(self.recursos.fonte("corpo_forte"), mensagem, config.PERIGO,
                             sombra=(0, 0, 0))
        caixa = pygame.Rect(0, 0, imagem.get_width() + 28, imagem.get_height() + 14)
        caixa.center = (config.LARGURA // 2, config.HUD_ALTURA + 40)
        painel = pygame.Surface(caixa.size, pygame.SRCALPHA)
        pygame.draw.rect(painel, (30, 8, 10, alpha), painel.get_rect(), border_radius=8)
        pygame.draw.rect(painel, (*config.PERIGO, alpha), painel.get_rect(), width=1,
                         border_radius=8)
        painel.blit(imagem, (14, 7))
        tela.blit(painel, caixa.topleft)

    def _desenhar_seta_ajuda(self, tela: pygame.Surface) -> None:
        """Depois de 9 s sem coletar, uma seta aponta o orvalho mais próximo."""
        alvo = self.mundo.saida if self.saida_aberta else None
        if alvo is None:
            restantes = [o for o in self.orvalhos if not o.coletado]
            if not restantes:
                return
            alvo = min(restantes, key=lambda o: utils.distancia((o.x, o.y), self.jogador.pos()))
            alvo = (alvo.x, alvo.y)

        dx, dy = utils.normalizar(alvo[0] - self.jogador.x, alvo[1] - self.jogador.y)
        pulso = 0.5 + 0.5 * math.sin(self.abertura_timer * 5)
        px = self.jogador.x + dx * (34 + pulso * 6)
        py = self.jogador.y + dy * (34 + pulso * 6) + config.HUD_ALTURA
        angulo = math.atan2(dy, dx)
        pontas = [
            (px + math.cos(angulo) * 10, py + math.sin(angulo) * 10),
            (px + math.cos(angulo + 2.5) * 8, py + math.sin(angulo + 2.5) * 8),
            (px + math.cos(angulo - 2.5) * 8, py + math.sin(angulo - 2.5) * 8),
        ]
        pygame.draw.polygon(tela, config.AGUA, pontas)

    # ------------------------------------------------------------------ #
    def _chefe_no_rodape(self) -> bool:
        """O status da batalha mora no rodapé — nunca em cima do mapa."""
        if not self.chefe or self.estado_chefe == "inativo":
            return False
        if self.estado_chefe == "vencido":
            return self.chefe_visor > 0
        return True

    def _desenhar_chefe_rodape(self, tela: pygame.Surface, rodape: pygame.Rect) -> None:
        """
        A Coruja em uma linha: nome, 3 marcas de clarão e a dica do momento.

        Antes era um painel flutuante no meio da área de jogo e escondia o
        caminho (e a própria coruja). No rodapé o estado continua legível sem
        tapar nada; a barra virou uma linha fina na borda do rodapé, no canto
        do olho em vez do centro da tela.
        """
        r = self.recursos
        f_tit = r.fonte("pequena_forte")
        f_txt = r.fonte("pequena")
        coruja = self.chefe
        vencido = self.estado_chefe == "vencido"
        cor = config.VERDE if vencido else config.OURO

        if vencido:
            titulo, dica = "CORUJA ACALMADA", "o caminho está livre"
        elif coruja.atordoado > 0:
            titulo, dica = "A CORUJA — atordoada", "aproveite e passe"
        elif coruja.reacao_golpe > 0:
            titulo, dica = "A CORUJA — vai investir!", "desvie agora"
        else:
            titulo, dica = "A CORUJA", "3 clarões perto dela a acalmam"

        # medidor periférico na borda de cima do rodapé
        pygame.draw.line(tela, (24, 33, 50), rodape.topleft, rodape.topright, 1)
        progresso = 1.0 if vencido else coruja.exposicao
        largura = int(config.LARGURA * utils.clamp(progresso, 0, 1))
        if largura > 0:
            pygame.draw.rect(tela, cor, (0, rodape.y, largura, 3))
            if not vencido:
                pygame.draw.circle(tela, (255, 255, 255), (largura, rodape.y + 1), 1)

        # da direita para a esquerda: dica · contagem · marcas · nome
        x = rodape.right - 24
        ui.texto(tela, f_txt, dica, ui.TEXTO_FRACO, x, rodape.centery,
                 alinhamento="dir", vertical="meio")
        x -= ui.largura(f_txt, dica) + 18

        cheias = 3 if vencido else sum(
            1 for i in range(3) if coruja.exposicao >= (i + 1) / 3 - 0.02)
        rotulo = f"{cheias}/3"
        ui.texto(tela, f_txt, rotulo, cor, x, rodape.centery,
                 alinhamento="dir", vertical="meio")
        x -= ui.largura(f_txt, rotulo) + 12

        for i in reversed(range(3)):
            cheia = i < cheias
            pygame.draw.circle(tela, cor if cheia else (74, 88, 116),
                               (x - 6, rodape.centery), 5)
            if cheia:
                pygame.draw.circle(tela, (12, 16, 24), (x - 6, rodape.centery), 2)
            x -= 15

        ui.texto(tela, f_tit, titulo, cor, x - 6, rodape.centery,
                 alinhamento="dir", vertical="meio")

    def _desenhar_aviso_chefe(self, tela: pygame.Surface) -> None:
        """Anúncio curto de entrada na batalha (some sozinho)."""
        alpha = int(255 * min(1.0, self.aviso_chefe / 0.8))
        titulo = "A CORUJA TE OUVIU"
        f_tit = self.recursos.fonte("h2_forte")

        caixa = pygame.Rect(0, 0, ui.largura(f_tit, titulo) + 52, 48)
        caixa.midtop = (config.LARGURA // 2, config.HUD_ALTURA + 12)

        camada = pygame.Surface(caixa.size, pygame.SRCALPHA)
        ui.painel(camada, camada.get_rect(), raio=ui.RAIO["md"], alpha=234, brilho_topo=True)
        ui.texto(camada, f_tit, titulo, config.OURO, caixa.width // 2,
                 caixa.height // 2, alinhamento="centro", vertical="meio")
        camada.set_alpha(alpha)
        tela.blit(camada, caixa.topleft)

    def _desenhar_pausa(self, tela: pygame.Surface) -> None:
        ui.scrim(tela, 205)

        caixa = pygame.Rect(0, 0, 640, 452)
        caixa.center = (config.LARGURA // 2, config.ALTURA // 2)
        ui.painel(tela, caixa, raio=ui.RAIO["lg"], alpha=250, brilho_topo=True)

        ui.texto(tela, self.recursos.fonte("titulo_medio"), "Pausa", ui.TEXTO,
                 caixa.centerx, caixa.y + 24, alinhamento="centro", sombra=(0, 0, 0))
        ui.divisor(tela, caixa.x + 32, caixa.y + 76, caixa.width - 64)

        # coluna esquerda: controles com chips de tecla (cor + forma)
        f_tecla = self.recursos.fonte("pequena_forte")
        f_acao = self.recursos.fonte("pequena")
        controles = [
            ("WASD", "voar"), ("SHIFT", "correr (gasta luz)"),
            ("ESPAÇO", "clarão"), ("P", "continuar"),
            ("R", "reiniciar"), ("V", "menu"),
            ("M", "som"), ("- / +", "volume"),
        ]
        y = caixa.y + 100
        for rotulo, acao in controles:
            chip_tecla = ui.tecla(tela, f_tecla, rotulo, caixa.x + 34, y)
            ui.texto(tela, f_acao, acao, ui.TEXTO_FRACO, chip_tecla.right + 12,
                     chip_tecla.centery, vertical="meio")
            y += 38

        # coluna direita: status + botões
        x_dir = caixa.x + 336
        som = "mudo" if self.audio.mudo else f"{int(self.audio.volume * 100)}%"
        ui.texto(tela, f_tecla, "STATUS", ui.TEXTO_FRACO, x_dir, caixa.y + 100)
        linhas = [
            ("Fase", str(self.numero_bioma) if self.infinito
             else f"{self.bioma_index + 1}/{len(config.BIOMAS)}"),
            ("Orvalho", f"{self.coletados}/{self.necessario}"),
            ("Pontos", f"{self.pontos:05d}"),
            ("Som", som),
        ]
        y = caixa.y + 128
        for rotulo, valor in linhas:
            ui.texto(tela, f_acao, rotulo, ui.TEXTO_FRACO, x_dir, y, vertical="meio")
            ui.texto(tela, self.recursos.fonte("pequena_forte"), valor, ui.TEXTO,
                     caixa.right - 34, y, alinhamento="dir", vertical="meio")
            y += 26

        ui.divisor(tela, x_dir, y + 4, caixa.right - 34 - x_dir)

        self._sincronizar_pausa()
        y = y + 20
        for botao in self._botoes_pausa:
            botao.desenhar(tela, self.recursos.fonte("botao"), x=x_dir, y=y)
            y += botao.ret.height + 8

    # ------------------------------------------------------------------ #
    def _sincronizar_pausa(self) -> None:
        for i, botao in enumerate(self._botoes_pausa):
            botao.foco = i == self._indice_pausa
            botao.desabilitado = False

    def _navegar_pausa(self, passo: int) -> None:
        self._indice_pausa = (self._indice_pausa + passo) % len(self._botoes_pausa)
        self._sincronizar_pausa()
        self.audio.tocar("navegar", volume=0.55)

    def _acionar_pausa(self) -> None:
        self.audio.tocar("clique")
        self._botoes_pausa[self._indice_pausa].acao()
