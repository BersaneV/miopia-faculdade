"""
atores.py — vaga-lume, inimigos, orvalho, partículas e o clarão (pulso).

Cada inimigo tem uma regra própria, e todas conversam com a história:

  morcego  — caça a luz. Persegue, mas foge do clarão.
  aranha   — sente a luz de longe e corre em linha reta. Fica atordoada no clarão.
  sombra   — só se mexe quando a sua luz está fraca. Luz forte a faz recuar.
  coruja   — caça pelo SOM (chefe). Correr atrai; parar engana; o clarão a cega.

Todos os sprites são desenhados com pygame.draw (arte do grupo, sem asset
de terceiro). Cada um anima por tempo, não por frames de imagem.
"""

from __future__ import annotations

import math
import random

import pygame

from . import config
from . import utils


# ========================================================================= #
# Partículas
# ========================================================================= #
class Particula:
    __slots__ = ("x", "y", "vx", "vy", "vida", "vida_max", "cor", "tamanho", "arrasto")

    def __init__(self, x, y, vx, vy, vida, cor, tamanho, arrasto=2.5):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.vida = self.vida_max = vida
        self.cor = cor
        self.tamanho = tamanho
        self.arrasto = arrasto

    def atualizar(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx -= self.vx * self.arrasto * dt
        self.vy -= self.vy * self.arrasto * dt
        self.vy += 22 * dt
        self.vida -= dt
        return self.vida > 0

    def desenhar(self, tela: pygame.Surface) -> None:
        t = max(0.0, self.vida / self.vida_max)
        raio = max(1, int(self.tamanho * t))
        cor = (*self.cor, int(255 * t))
        ponto = pygame.Surface((raio * 2 + 2, raio * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(ponto, cor, (raio + 1, raio + 1), raio)
        tela.blit(ponto, (int(self.x) - raio, int(self.y) - raio))


def explodir(particulas: list, x, y, cor, quantidade=12, forca=90, vida=0.7, tamanho=3):
    for _ in range(quantidade):
        angulo = random.uniform(0, math.tau)
        velocidade = random.uniform(forca * 0.3, forca)
        particulas.append(Particula(
            x, y,
            math.cos(angulo) * velocidade,
            math.sin(angulo) * velocidade,
            random.uniform(vida * 0.6, vida),
            cor, random.uniform(1.5, tamanho),
        ))


# ========================================================================= #
# Orvalho (item de coleta)
# ========================================================================= #
class Orvalho:
    def __init__(self, x: float, y: float, raro: bool = False) -> None:
        self.x, self.y = x, y
        self.raro = raro
        self.fase = random.uniform(0, math.tau)
        self.coletado = False
        self.brilho = 0.0

    @property
    def valor(self) -> int:
        return config.PONTOS_RARO if self.raro else config.PONTOS_ORVALHO

    def atualizar(self, dt: float, tempo: float) -> None:
        self.fase += dt * (2.2 if self.raro else 1.6)
        self.brilho = 0.55 + 0.45 * math.sin(self.fase * 2.0)

    def desenhar(self, tela: pygame.Surface, recursos) -> None:
        if self.coletado:
            return
        flutua = math.sin(self.fase) * 3.0
        x, y = int(self.x), int(self.y + flutua)
        raio = 12 if self.raro else 7

        # halo aditivo
        halo = recursos.brilho(raio * 3.6, config.AGUA if not self.raro else config.OURO)
        tela.blit(halo, (x - halo.get_width() // 2, y - halo.get_height() // 2),
                  special_flags=pygame.BLEND_RGB_ADD)

        # gota
        cor = config.OURO if self.raro else config.AGUA
        pygame.draw.circle(tela, utils.escurecer(cor, 0.55), (x, y), raio)
        pygame.draw.circle(tela, cor, (x, y), max(2, int(raio * 0.72)))
        pygame.draw.circle(tela, (255, 255, 255), (x - raio // 3, y - raio // 3),
                           max(1, raio // 3))

        # raios do raro
        if self.raro:
            for i in range(4):
                ang = self.fase * 0.8 + i * math.tau / 4
                px = x + math.cos(ang) * (raio + 7)
                py = y + math.sin(ang) * (raio + 7)
                pygame.draw.circle(tela, cor, (int(px), int(py)), 2)


# ========================================================================= #
# Clarão (pulso de luz)
# ========================================================================= #
class Pulso:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y
        self.t = 0.0
        self.duracao = config.DURACAO_PULSO
        self.raio_max = 168.0

    @property
    def ativo(self) -> bool:
        return self.t < self.duracao

    @property
    def raio(self) -> float:
        return self.raio_max * utils.suavizar(self.t / self.duracao)

    @property
    def alcance_dano(self) -> float:
        return self.raio if self.ativo else 0.0

    def atualizar(self, dt: float) -> None:
        self.t += dt

    def desenhar(self, tela: pygame.Surface, recursos) -> None:
        if not self.ativo:
            return
        t = self.t / self.duracao
        raio = max(4, int(self.raio))
        alpha = int(150 * (1 - t))

        # miolo do clarão (soma de luz)
        halo = recursos.brilho(min(200, raio + 30), config.LUZ)
        tela.blit(halo, (int(self.x) - halo.get_width() // 2,
                         int(self.y) - halo.get_height() // 2),
                  special_flags=pygame.BLEND_RGB_ADD)

        anel = pygame.Surface((raio * 2 + 8, raio * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(anel, (*config.LUZ, alpha), (raio + 4, raio + 4), raio, 3)
        pygame.draw.circle(anel, (*config.LUZ_QUENTE, alpha // 2), (raio + 4, raio + 4),
                           max(1, raio - 6), 1)
        tela.blit(anel, (int(self.x) - raio - 4, int(self.y) - raio - 4))


# ========================================================================= #
# Jogador
# ========================================================================= #
class Jogador:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.raio = config.RAIO_JOGADOR

        self.energia = config.ENERGIA_MAX
        self.vidas = config.VIDAS_INICIAIS
        self.invulneravel = 2.0
        self.intangivel = 0.0
        self.correndo = False
        self.olhando = 1

        self.pulso: Pulso | None = None
        self.cooldown_pulso = 0.0
        self.ruido = 0.0          # o quanto está fazendo barulho (coruja)
        self.tempo_apagado = 0.0
        self.morto = False

        self._historico: list[tuple[float, float]] = [(x, y)] * 8
        self._tempo = 0.0
        self._passo = 0.0
        self._flash_dano = 0.0
        self._brilho_extra = 0.0

    # ------------------------------------------------------------------ #
    @property
    def raio_luz(self) -> float:
        proporcao = utils.clamp(self.energia / config.ENERGIA_MAX, 0.0, 1.0)
        raio = config.RAIO_LUZ_MIN + (config.RAIO_LUZ_MAX - config.RAIO_LUZ_MIN) * (proporcao ** 0.5)
        # clarão empurra a luz para fora por um instante
        if self.pulso and self.pulso.ativo:
            raio += 60 * (1 - self.pulso.t / self.pulso.duracao)
        return raio + self._brilho_extra

    @property
    def luz_fraca(self) -> bool:
        return self.energia / config.ENERGIA_MAX < 0.4

    @property
    def velocidade(self) -> float:
        return math.hypot(self.vx, self.vy)

    # ------------------------------------------------------------------ #
    def acertou(self, jogador: "Jogador") -> None:
        """Chamado quando este inimigo acerta o jogador."""
        self.cooldown_dano = 2.4
        self.esfriando = 2.2
        self.perseguindo = 0.0
        self.reacao = 0.0        # tem de te notar de novo antes de voltar
        self.estado = "patrulha"
        dx, dy = utils.normalizar(self.x - jogador.x, self.y - jogador.y)
        self.vx = dx * 300
        self.vy = dy * 300

    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def atualizar(self, dt: float, mundo, teclas, partículas) -> None:
        self._tempo += dt
        self.invulneravel = max(0.0, self.invulneravel - dt)
        self.intangivel = max(0.0, self.intangivel - dt)
        self.cooldown_pulso = max(0.0, self.cooldown_pulso - dt)
        self._flash_dano = max(0.0, self._flash_dano - dt * 2.2)
        self._brilho_extra = max(0.0, self._brilho_extra - dt * 90)

        # ---------------- entrada ---------------- #
        eixo_x = (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a])
        eixo_y = (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - (teclas[pygame.K_UP] or teclas[pygame.K_w])
        eixo_x, eixo_y = utils.normalizar(eixo_x, eixo_y)

        quer_correr = teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]
        self.correndo = bool(quer_correr and (eixo_x or eixo_y) and self.energia > 4)

        velocidade_alvo = config.VEL_CORRER if self.correndo else config.VEL_MAX
        alvo_x = eixo_x * velocidade_alvo
        alvo_y = eixo_y * velocidade_alvo

        if eixo_x or eixo_y:
            self.vx = utils.aproximar(self.vx, alvo_x, config.ACELERACAO * dt)
            self.vy = utils.aproximar(self.vy, alvo_y, config.ACELERACAO * dt)
            self.olhando = 1 if eixo_x >= 0 else -1
        else:
            self.vx -= self.vx * config.ATRITO * dt
            self.vy -= self.vy * config.ATRITO * dt

        # ---------------- movimento ---------------- #
        self.x, self.y, bateu_x, bateu_y = mundo.mover(self.x, self.y, self.vx * dt, self.vy * dt, self.raio)
        if bateu_x:
            self.vx *= -0.15
        if bateu_y:
            self.vy *= -0.15

        # poeirinha ao andar
        self._passo += dt
        if self.velocidade > 40 and self._passo > 0.12:
            self._passo = 0.0
            partículas.append(Particula(
                self.x + random.uniform(-3, 3), self.y + 6,
                random.uniform(-12, 12), random.uniform(-18, -6),
                0.45, utils.escurecer(config.LUZ, 0.8), 2,
            ))

        # ---------------- energia ---------------- #
        dreno = config.DRENO_BASE + (config.DRENO_CORRER if self.correndo else 0.0)
        # parado no escuro, a luz respira um pouco menos
        if self.velocidade < 20:
            dreno *= 0.82
        self.energia = max(0.0, self.energia - dreno * dt)

        if self.energia <= 0.0:
            self.tempo_apagado += dt
        else:
            self.tempo_apagado = 0.0

        # ---------------- histórico da luz ---------------- #
        self._historico.insert(0, (self.x, self.y))
        if len(self._historico) > 9:
            self._historico.pop()

        # ---------------- ruído (coruja) ---------------- #
        alvo_ruido = 0.0
        if self.velocidade > 30:
            alvo_ruido = 0.35 + 0.65 * (self.velocidade / config.VEL_CORRER)
        self.ruido = utils.lerp(self.ruido, alvo_ruido, min(1.0, dt * 6))

        # ---------------- pulso ---------------- #
        if self.pulso:
            self.pulso.atualizar(dt)
            if not self.pulso.ativo:
                self.pulso = None

    # ------------------------------------------------------------------ #
    def pode_pulsar(self) -> bool:
        return self.cooldown_pulso <= 0 and self.energia >= config.CUSTO_PULSO

    def pulsar(self, partículas) -> bool:
        if not self.pode_pulsar():
            return False
        self.energia -= config.CUSTO_PULSO
        self.pulso = Pulso(self.x, self.y)
        self.cooldown_pulso = config.COOLDOWN_PULSO
        self._brilho_extra = 26
        explodir(partículas, self.x, self.y, config.LUZ, quantidade=18, forca=150, vida=0.8)
        return True

    def levar_dano(self, origem: tuple[float, float] | None = None) -> bool:
        if self.invulneravel > 0 or self.morto:
            return False
        self.vidas -= 1
        self.invulneravel = config.INVULNERAVEL
        self._flash_dano = 1.0
        self.energia = max(0.0, self.energia - 18.0)
        if origem:
            # empurrão forte para longe do inimigo + instante de "intangibilidade"
            dx, dy = utils.normalizar(self.x - origem[0], self.y - origem[1])
            self.vx += dx * 380
            self.vy += dy * 380
            self.intangivel = 0.45
        if self.vidas <= 0:
            self.morto = True
        return True

    def beber(self, valor: float, partículas) -> None:
        self.energia = min(config.ENERGIA_MAX, self.energia + valor)
        self._brilho_extra = 18
        explodir(partículas, self.x, self.y, config.AGUA, quantidade=10, forca=70, vida=0.6)

    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface, recursos) -> None:
        # pisca quando invulnerável
        if self.invulneravel > 0 and int(self.invulneravel * 12) % 2 == 0:
            return

        x, y = int(self.x), int(self.y)
        batida = math.sin(self._tempo * 26)
        inclinacao = math.sin(self._tempo * 1.8) * 0.12

        corpo = utils.misturar(config.LUZ_QUENTE, (255, 255, 255), 0.15)
        if self._flash_dano > 0:
            corpo = utils.misturar(corpo, config.PERIGO, self._flash_dano)

        # ---- rastro luminoso (histórico) ----
        for i, (hx, hy) in enumerate(self._historico[2:], start=2):
            t = 1 - i / len(self._historico)
            if t <= 0:
                continue
            raio = max(1, int(4 * t))
            cor = (*utils.escurecer(config.LUZ, 0.35), int(90 * t))
            ponto = pygame.Surface((raio * 2 + 2, raio * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ponto, cor, (raio + 1, raio + 1), raio)
            tela.blit(ponto, (int(hx) - raio, int(hy) - raio))

        # ---- asas ----
        asa_cor = (*utils.escurecer(config.LUZ, 0.72), 120)
        largura_asa = 11 + abs(batida) * 5
        for lado in (-1, 1):
            asa = pygame.Surface((largura_asa * 2, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(asa, asa_cor, (0, 0, largura_asa * 2, 22))
            pygame.draw.ellipse(asa, (*config.LUZ, 70), (2, 3, largura_asa * 2 - 4, 12))
            girada = pygame.transform.rotate(asa, lado * (18 + batida * 22) + inclinacao * 30)
            tela.blit(girada, (x - girada.get_width() // 2,
                               y - girada.get_height() // 2 + 2))

        # ---- abdômen luminoso ----
        luz_abdomem = 5 + int(2 * (0.5 + 0.5 * math.sin(self._tempo * 4)))
        pygame.draw.circle(tela, utils.escurecer(corpo, 0.5), (x, y + 6), luz_abdomem + 2)
        pygame.draw.circle(tela, config.LUZ, (x, y + 6), luz_abdomem)

        # ---- corpo ----
        pygame.draw.ellipse(tela, utils.escurecer(corpo, 0.45), (x - 7, y - 8, 14, 18))
        pygame.draw.ellipse(tela, corpo, (x - 5, y - 7, 10, 14))

        # ---- cabeça ----
        pygame.draw.circle(tela, utils.escurecer(corpo, 0.35), (x, y - 7), 7)
        pygame.draw.circle(tela, corpo, (x, y - 8), 6)

        # ---- óculos (a piada visual do jogo) ----
        lente = (18, 26, 40)
        pygame.draw.circle(tela, (230, 240, 255), (x - 3, y - 9), 3)
        pygame.draw.circle(tela, (230, 240, 255), (x + 3, y - 9), 3)
        pygame.draw.circle(tela, lente, (x - 3 + self.olhando, y - 9), 1)
        pygame.draw.circle(tela, lente, (x + 3 + self.olhando, y - 9), 1)
        pygame.draw.line(tela, (200, 215, 235), (x - 1, y - 10), (x + 1, y - 9), 1)

        # ---- antenas ----
        for lado in (-1, 1):
            pygame.draw.line(tela, utils.escurecer(corpo, 0.5),
                             (x + lado * 2, y - 13), (x + lado * 5, y - 18), 1)
            pygame.draw.circle(tela, config.LUZ, (x + lado * 5, y - 18), 1)


# ========================================================================= #
# Inimigos
# ========================================================================= #
class Inimigo:
    VELOCIDADES = {
        "morcego": 90.0,
        "aranha": 96.0,
        "sombra": 72.0,
        "coruja": 132.0,
    }
    DETECCAO = {
        "morcego": 165.0,
        "aranha": 240.0,
        "sombra": 200.0,
        "coruja": 215.0,
    }

    def __init__(self, tipo: str, x: float, y: float) -> None:
        self.tipo = tipo
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.raio = 15 if tipo == "coruja" else 10
        self.estado = "patrulha"
        self.timer_estado = random.uniform(0.5, 1.6)
        self.alvo = (x, y)
        self.atordoado = 0.0
        self.fase = random.uniform(0, math.tau)
        self.velocidade_base = self.VELOCIDADES[tipo]
        self.assustado = 0.0
        self._tempo = 0.0
        self.lento = 0.0
        self.perseguindo = 0.0    # segundos perseguindo sem pausa
        self.esfriando = 0.0      # segundos em que ignora o jogador
        self.reacao = 0.0         # tempo dentro do raio antes de partir para cima
        self.cooldown_dano = 0.0  # após acertar o jogador, recua um instante
        self.limite_perseguicao = {"morcego": 4.2, "aranha": 3.0,
                                   "sombra": 4.5, "coruja": 5.0}[tipo]

        # ---- chefe (só a Coruja): 3 clarões e ela se acalma ----
        self.chefe = tipo == "coruja"
        self.calma = 0.0          # 0 = alterada · 1 = acalmada
        self.exposicao = 0.0      # quanto já somou de clarão (0 a 1)
        self.reacao_golpe = 0.0   # "!" antes de investir (telegrafia)

    # ------------------------------------------------------------------ #
    def assustar(self, duracao: float) -> None:
        """Efeito do clarão, muda por inimigo."""
        if self.tipo == "morcego":
            self.assustado = duracao
            self.estado = "fugir"
        elif self.tipo == "aranha":
            self.atordoado = max(self.atordoado, duracao)
        elif self.tipo == "sombra":
            self.assustado = duracao * 1.4
            self.estado = "recuar"
        else:  # coruja (chefe)
            self.atordoado = max(self.atordoado, duracao * 1.7)
            self.estado = "cega"
            if self.chefe and self.calma <= 0:
                self.exposicao = min(1.0, self.exposicao + 0.34)

    # ------------------------------------------------------------------ #
    def separar(self, outros: list["Inimigo"], dt: float) -> None:
        """Empurra inimigos que estão quase no mesmo ponto (evita enxame)."""
        for outro in outros:
            if outro is self:
                continue
            dx, dy = self.x - outro.x, self.y - outro.y
            dist = math.hypot(dx, dy)
            if dist < 26 and dist > 0.01:
                forca = (26 - dist) * 6 * dt
                dx, dy = dx / dist, dy / dist
                self.x += dx * forca
                self.y += dy * forca
                outro.x -= dx * forca
                outro.y -= dy * forca

    def atualizar(self, dt: float, mundo, jogador: Jogador, dificuldade: float) -> None:
        self._tempo += dt
        self.fase += dt * 3.0
        self.atordoado = max(0.0, self.atordoado - dt)
        self.assustado = max(0.0, self.assustado - dt)
        self.lento = max(0.0, self.lento - dt)
        self.esfriando = max(0.0, self.esfriando - dt)
        self.cooldown_dano = max(0.0, self.cooldown_dano - dt)

        # coleira: depois de perseguir por muito tempo, o inimigo desiste por
        # alguns segundos. Isso dá janelas de respiro e evita enxame injusto.
        if self.estado == "cacar" and self.atordoado <= 0 and self.assustado <= 0:
            self.perseguindo += dt
            if self.perseguindo > self.limite_perseguicao:
                self.perseguindo = 0.0
                self.esfriando = 3.6 - 0.6 * dificuldade
                self.estado = "patrulha"
                self.timer_estado = 0.0
        elif self.estado != "cacar":
            self.perseguindo = max(0.0, self.perseguindo - dt * 0.7)

        deteccao = self.DETECCAO[self.tipo] * (0.82 + 0.24 * dificuldade)
        distancia = utils.distancia((self.x, self.y), (jogador.x, jogador.y))

        if self.atordoado > 0:
            self.vx -= self.vx * 8 * dt
            self.vy -= self.vy * 8 * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            self._colidir(mundo)
            return

        # chefe: telegrafa a investida antes de vir
        if self.chefe and self.calma <= 0:
            self.reacao_golpe = max(0.0, self.reacao_golpe - dt)
            if self.estado == "cacar" and distancia < 190 and self.reacao_golpe <= 0:
                self.reacao_golpe = 0.9      # janela de aviso

        alvo = self._escolher_alvo(dt, mundo, jogador, distancia, deteccao)
        dx, dy = utils.normalizar(alvo[0] - self.x, alvo[1] - self.y)
        velocidade = self.velocidade_base * (1.0 + 0.22 * dificuldade)
        if self.chefe and self.estado == "cacar":
            velocidade *= 0.8         # investida forte, mas legível
        if self.lento > 0:
            velocidade *= 0.55
        if self.tipo == "sombra" and not jogador.luz_fraca:
            velocidade *= 0.35

        alvo_vx, alvo_vy = dx * velocidade, dy * velocidade
        self.vx = utils.aproximar(self.vx, alvo_vx, velocidade * 6 * dt)
        self.vy = utils.aproximar(self.vy, alvo_vy, velocidade * 6 * dt)

        antigo = (self.x, self.y)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._colidir(mundo, antigo)

    # ------------------------------------------------------------------ #
    def _colidir(self, mundo, antigo=None) -> None:
        if mundo.colide(self.x, self.y, self.raio - 1):
            if antigo:
                self.x, self.y = antigo
            self.vx *= -0.4
            self.vy *= -0.4
            self.timer_estado = min(self.timer_estado, 0.15)

    # ------------------------------------------------------------------ #
    def _escolher_alvo(self, dt, mundo, jogador, distancia, deteccao):
        self.timer_estado -= dt

        # recuo depois de acertar: dá ao jogador uma janela para escapar
        if self.cooldown_dano > 0 and self.assustado <= 0:
            return (self.x * 2 - jogador.x, self.y * 2 - jogador.y)

        if self.esfriando > 0 and self.assustado <= 0:
            return self._patrulha(dt, alcance=70)

        # tempo de reação: o inimigo precisa te "notar" antes de correr
        if distancia < deteccao:
            self.reacao = min(1.0, self.reacao + dt * 2.5)
        else:
            self.reacao = max(0.0, self.reacao - dt * 2.0)

        if self.tipo == "morcego":
            if self.assustado > 0:
                return (self.x * 2 - jogador.x, self.y * 2 - jogador.y)
            if (self.reacao >= 0.35 and distancia < deteccao
                    and mundo.visao((self.x, self.y), jogador.pos())):
                self.estado = "cacar"
                return jogador.pos()
            return self._patrulha(dt)

        if self.tipo == "aranha":
            if self.reacao >= 0.35 and distancia < deteccao:
                self.estado = "atacar"
                return jogador.pos()
            return self._patrulha(dt, alcance=90)

        if self.tipo == "sombra":
            if self.assustado > 0:
                return (self.x * 2 - jogador.x, self.y * 2 - jogador.y)
            if self.reacao >= 0.35 and distancia < deteccao and jogador.luz_fraca:
                self.estado = "cacar"
                return jogador.pos()
            if distancia < 120 and not jogador.luz_fraca:
                return (self.x * 2 - jogador.x, self.y * 2 - jogador.y)
            return self._patrulha(dt, alcance=120)

        # coruja: caça pelo som
        if self.estado == "cega":
            if self.atordoado <= 0:
                self.estado = "patrulha"
            return self._patrulha(dt, alcance=60)

        ruido = jogador.ruido
        if self.reacao >= 0.35 and ruido > 0.45 and distancia < deteccao * 2:
            self.estado = "cacar"
            return jogador.pos()
        if self.reacao >= 0.35 and ruido > 0.15 and distancia < deteccao:
            self.estado = "cacar"
            return jogador.pos()
        return self._patrulha(dt, alcance=110)

    # ------------------------------------------------------------------ #
    def _patrulha(self, dt, alcance: float = 120):
        if self.timer_estado <= 0 or utils.distancia((self.x, self.y), self.alvo) < 12:
            self.estado = "patrulha"
            angulo = random.uniform(0, math.tau)
            self.alvo = (
                utils.clamp(self.x + math.cos(angulo) * alcance, 24, config.AREA_LARGURA - 24),
                utils.clamp(self.y + math.sin(angulo) * alcance, 24, config.AREA_ALTURA_USADA - 24),
            )
            self.timer_estado = random.uniform(1.0, 2.6)
        return self.alvo

    # ------------------------------------------------------------------ #
    def acertou(self, jogador: "Jogador") -> None:
        """Chamado quando este inimigo acerta o jogador."""
        self.cooldown_dano = 2.4
        self.esfriando = 2.2
        self.perseguindo = 0.0
        self.reacao = 0.0        # tem de te notar de novo antes de voltar
        self.estado = "patrulha"
        dx, dy = utils.normalizar(self.x - jogador.x, self.y - jogador.y)
        self.vx = dx * 300
        self.vy = dy * 300

    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def colide_com(self, jogador: Jogador) -> bool:
        if self.calma > 0:
            return False
        if self.atordoado > 0 and self.tipo != "coruja":
            return False
        return utils.distancia((self.x, self.y), (jogador.x, jogador.y)) < self.raio + jogador.raio - 2

    # ------------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface) -> None:
        if self.tipo == "morcego":
            self._desenhar_morcego(tela)
        elif self.tipo == "aranha":
            self._desenhar_aranha(tela)
        elif self.tipo == "sombra":
            self._desenhar_sombra(tela)
        else:
            self._desenhar_coruja(tela)

    def _desenhar_morcego(self, tela) -> None:
        x, y = int(self.x), int(self.y)
        b = math.sin(self.fase * 2.4)
        cor = config.ROXO if self.assustado <= 0 else utils.clarear(config.ROXO, 0.25)

        for lado in (-1, 1):
            pontos = [(x, y), (x + lado * 16, y - 9 - b * 4), (x + lado * 12, y + 3),
                      (x + lado * 7, y + 1)]
            pygame.draw.polygon(tela, utils.escurecer(cor, 0.55), pontos)

        pygame.draw.circle(tela, utils.escurecer(cor, 0.35), (x, y), 8)
        pygame.draw.circle(tela, cor, (x, y - 1), 6)

        for lado in (-1, 1):
            pygame.draw.polygon(tela, utils.escurecer(cor, 0.3),
                                [(x + lado * 3, y - 6), (x + lado * 6, y - 12), (x + lado * 7, y - 5)])
        # olhos
        cor_olho = config.PERIGO if self.estado == "cacar" else (255, 180, 120)
        pygame.draw.circle(tela, cor_olho, (x - 2, y - 1), 1)
        pygame.draw.circle(tela, cor_olho, (x + 2, y - 1), 1)

    def _desenhar_aranha(self, tela) -> None:
        x, y = int(self.x), int(self.y)
        atordoada = self.atordoado > 0
        cor = (58, 40, 70) if not atordoada else (90, 80, 110)

        for i in range(4):
            for lado in (-1, 1):
                passo = math.sin(self.fase * 3 + i * 0.9) * 4
                base_x = x + lado * 4
                base_y = y - 2 + i * 2
                joelho = (base_x + lado * (9 + i), base_y - 6 + passo)
                ponta = (base_x + lado * (13 + i * 0.7), base_y + 5 + passo * 0.6)
                pygame.draw.line(tela, cor, (base_x, base_y), joelho, 2)
                pygame.draw.line(tela, cor, joelho, ponta, 2)

        pygame.draw.circle(tela, utils.escurecer(cor, 0.7), (x, y + 2), 8)
        pygame.draw.circle(tela, utils.clarear(cor, 0.12), (x, y), 6)

        if atordoada:
            # estrelinhas de atordoamento
            for i in range(3):
                ang = self.fase * 0.8 + i * math.tau / 3
                px = x + math.cos(ang) * 12
                py = y - 12 + math.sin(ang) * 3
                pygame.draw.circle(tela, config.LUZ, (int(px), int(py)), 1)
        else:
            cor_olho = config.AGUA if self.estado != "atacar" else config.PERIGO
            pygame.draw.circle(tela, cor_olho, (x - 2, y - 2), 1)
            pygame.draw.circle(tela, cor_olho, (x + 2, y - 2), 1)

    def _desenhar_sombra(self, tela) -> None:
        x, y = int(self.x), int(self.y)
        forte = self.assustado <= 0 and (self._tempo * 3) % 2 < 1.4
        alpha = 190 if forte else 110

        blob = pygame.Surface((44, 46), pygame.SRCALPHA)
        for i in range(7):
            ang = self.fase * 0.7 + i * math.tau / 7
            px = 22 + math.cos(ang) * 9
            py = 24 + math.sin(ang) * 9
            pygame.draw.circle(blob, (24, 16, 40, alpha), (int(px), int(py)), 8)
        pygame.draw.circle(blob, (30, 20, 50, alpha), (22, 24), 10)
        tela.blit(blob, (x - 22, y - 24))

        if self.assustado <= 0:
            cor_olho = (240, 240, 255) if not self.assustado else (150, 150, 170)
            pygame.draw.circle(tela, cor_olho, (x - 4, y - 2), 2)
            pygame.draw.circle(tela, cor_olho, (x + 4, y - 2), 2)

    def _desenhar_coruja(self, tela) -> None:
        x, y = int(self.x), int(self.y)
        b = math.sin(self.fase * 1.6)
        cega = self.atordoado > 0

        # fase: muda de cor conforme os clarões recebidos (cor + número, não só cor)
        if self.chefe:
            if self.calma > 0:
                cor_fase = (98, 126, 150)
            elif self.exposicao > 0.68:
                cor_fase = (255, 138, 110)
            elif self.exposicao > 0.34:
                cor_fase = (236, 176, 120)
            else:
                cor_fase = (150, 128, 200)
            pulso = 0.5 + 0.5 * math.sin(self._tempo * 3)
            raio = int(34 + 6 * pulso)
            aura = pygame.Surface((raio * 2 + 8, raio * 2 + 8), pygame.SRCALPHA)
            for i in range(6, 0, -1):
                alpha = int(26 * (1 - i / 6) * (1.2 if self.reacao_golpe > 0 else 1))
                pygame.draw.circle(aura, (*cor_fase, alpha), (raio + 4, raio + 4),
                                   raio * i // 6)
            tela.blit(aura, (x - raio - 4, y - raio - 4), special_flags=pygame.BLEND_RGB_ADD)
        cor = (86, 74, 120) if not cega else (110, 104, 130)

        for lado in (-1, 1):
            pontos = [(x + lado * 6, y - 2), (x + lado * 26, y - 14 - b * 5),
                      (x + lado * 24, y + 6), (x + lado * 10, y + 6)]
            pygame.draw.polygon(tela, utils.escurecer(cor, 0.6), pontos)

        pygame.draw.ellipse(tela, utils.escurecer(cor, 0.45), (x - 14, y - 12, 28, 30))
        pygame.draw.ellipse(tela, cor, (x - 11, y - 10, 22, 24))
        # penas do peito
        for i in range(3):
            pygame.draw.arc(tela, utils.escurecer(cor, 0.3), (x - 8 + i * 5, y - 1, 8, 8), 0, math.pi, 1)

        # tufos de orelha
        for lado in (-1, 1):
            pygame.draw.polygon(tela, utils.escurecer(cor, 0.35),
                                [(x + lado * 4, y - 10), (x + lado * 10, y - 18), (x + lado * 9, y - 8)])

        if cega:
            for lado in (-1, 1):
                pygame.draw.line(tela, (230, 230, 240), (x + lado * 5 - 2, y - 4),
                                 (x + lado * 5 + 2, y), 1)
                pygame.draw.line(tela, (230, 230, 240), (x + lado * 5 - 2, y),
                                 (x + lado * 5 + 2, y - 4), 1)
        else:
            for lado in (-1, 1):
                pygame.draw.circle(tela, (255, 236, 150), (x + lado * 5, y - 3), 4)
                pygame.draw.circle(tela, (20, 14, 30), (x + lado * 5, y - 3), 2)

        # aviso de investida: "!" acima dela (forma, não só cor)
        if self.chefe and self.reacao_golpe > 0 and self.calma <= 0:
            cor_aviso = (255, 220, 150) if int(self._tempo * 8) % 2 else (255, 120, 110)
            pygame.draw.rect(tela, cor_aviso, (x - 2, y - 34, 4, 10), border_radius=2)
            pygame.draw.rect(tela, cor_aviso, (x - 2, y - 21, 4, 4), border_radius=1)

        # acalmada: "zZ" flutuando
        if self.calma > 0:
            for i, (dx, dy) in enumerate(((14, -26), (22, -34))):
                tamanho = 4 + i * 2
                cor_z = utils.misturar((150, 176, 200), (230, 240, 255),
                                       (math.sin(self._tempo * 2 + i) + 1) / 2)
                pygame.draw.line(tela, cor_z, (x + dx, y + dy),
                                 (x + dx + tamanho, y + dy), 2)
                pygame.draw.line(tela, cor_z, (x + dx + tamanho, y + dy),
                                 (x + dx, y + dy + tamanho), 2)
                pygame.draw.line(tela, cor_z, (x + dx, y + dy + tamanho),
                                 (x + dx + tamanho, y + dy + tamanho), 2)
