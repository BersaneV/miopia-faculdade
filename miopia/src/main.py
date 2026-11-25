"""
main.py — ponto de entrada do Miopia.

    python src/main.py

Responsabilidades deste arquivo:
  - abrir a janela e manter o laço principal (entrada → atualização → desenho);
  - trocar de tela (menu, cutscene, briefing, partida, fim, ajuda, créditos);
  - carregar e salvar recorde/preferências;
  - transição suave entre telas.

Dois modos:
  · HISTÓRIA (principal) — a partida emoldurada por cutscenes: prólogo em
      3 cenas, uma cena ao entrar em cada bioma e o desfecho (vitória/derrota);
  · INFINITO — a noite que não acaba: biomas emendados sem cutscene, cada
      volta pelos quatro biomas fica mais escura, mais cheia e mais faminta.
      Não há amanhecer: a partida termina quando as fagulhas acabam.

O jogo em si (regras da partida) fica em jogo.py.
"""

from __future__ import annotations

import os
import sys

# garante que "src" seja importável quando o script é rodado direto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src import config
from src import historia
from src import persistencia
from src.cena import Cutscene
from src.jogo import Jogo
from src.recursos import Recursos
from src.telas import Ajuda, Ambiental, Briefing, Creditos, Fim, Menu


class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.TITULO)
        try:
            self.tela = pygame.display.set_mode(
                (config.LARGURA, config.ALTURA), pygame.SCALED | pygame.RESIZABLE
            )
        except pygame.error:
            self.tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
        pygame.display.set_icon(self._criar_icone())

        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.deixar_espaco_livre = False

        self.recursos = Recursos()
        self.dados = persistencia.carregar()
        self.audio = self.recursos.audio
        self.audio.volume = float(self.dados.get("volume", 0.8))
        self.audio.mudo = bool(self.dados.get("mudo", False))
        self.audio.aplicar_volumes()

        self.jogo = Jogo(self)
        self.modo_historia = False
        self._novo_recorde = False
        self._final_mostrado = False

        self.estado = "menu"
        self.tela_atual = Menu(self)
        self.tela_atual.entrar()

        self.fade = 0.0          # 1 = preto total (transição)
        self.fade_dir = -1
        self.quadros = 0

    # ------------------------------------------------------------------ #
    def _criar_icone(self) -> pygame.Surface:
        icone = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icone, (*config.LUZ_QUENTE, 90), (16, 16), 14)
        pygame.draw.circle(icone, config.LUZ, (16, 16), 8)
        pygame.draw.circle(icone, (255, 255, 255), (13, 13), 2)
        return icone

    # ================================================================== #
    # Navegação entre telas
    # ================================================================== #
    def _trocar(self, estado: str, tela) -> None:
        self.estado = estado
        self.tela_atual = tela
        tela.entrar()
        self.fade = 1.0
        self.fade_dir = -1

    # ---------------------------- modos ------------------------------- #
    def abrir_historia(self) -> None:
        """Modo principal: cutscene de abertura e depois a partida."""
        self.modo_historia = True
        self._novo_recorde = False
        self._final_mostrado = False

        def comecar() -> None:
            self._trocar("jogo", _TelaVazia(self))
            self.jogo.iniciar("historia")

        self._trocar("cutscene", Cutscene(self, historia.INTRO, comecar,
                                          rotulo="PRÓLOGO"))

    def abrir_infinito(self) -> None:
        """Modo infinito: o sonho do Breu — cutscene curta e partida sem fim."""
        self.modo_historia = False
        self._novo_recorde = False
        self._final_mostrado = False

        def comecar() -> None:
            self._trocar("jogo", _TelaVazia(self))
            self.jogo.iniciar("infinito")

        self._trocar("cutscene", Cutscene(self, historia.INFINITO, comecar,
                                          rotulo="INFINITO"))

    def ir_para_jogo(self) -> None:
        modo = self.jogo.modo if self.jogo.modo in ("historia", "infinito") else "historia"
        self.jogo.iniciar(modo)
        self._trocar("jogo", _TelaVazia(self))

    def ir_para_menu(self) -> None:
        self.jogo.ativo = False
        self.jogo.pausado = False
        self.modo_historia = False
        self._trocar("menu", Menu(self))

    def abrir_ajuda(self) -> None:
        self._trocar("ajuda", Ajuda(self, self.ir_para_menu))

    def abrir_creditos(self) -> None:
        self._trocar("creditos", Creditos(self, self.ir_para_menu))

    # ------------------------- intervalos ----------------------------- #
    def mostrar_briefing(self, bioma: int, ao_voltar) -> None:
        def continuar() -> None:
            self._trocar("jogo", _TelaVazia(self))
            ao_voltar()

        self._trocar("briefing", Briefing(self, bioma, continuar))

    def mostrar_volta(self, numero_bioma: int, ao_voltar) -> None:
        """Checkpoint a cada volta completa do modo infinito."""
        jogo = self.jogo
        volta = jogo.volta

        def continuar() -> None:
            self._trocar("jogo", _TelaVazia(self))
            ao_voltar()

        self._trocar("briefing", Briefing(
            self, jogo.bioma_index, continuar,
            chip_texto=f"VOLTA {volta + 1}",
            titulo="A mata se refez",
            texto=("O sonho do Breu recomeça: a mata se refaz igual e mais escura. "
                   "Mais bichos, menos orvalho por canto e menos fôlego a cada volta."),
            meta=f"fase {numero_bioma} · junte {jogo.necessario} orvalhos para seguir",
            rotulo_botao="Continuar o sonho",
        ))

    def mostrar_intervalo(self, bioma: int, ao_voltar) -> None:
        """Chamado ao terminar um bioma (só no modo história)."""
        if not self.modo_historia:
            self.mostrar_briefing(bioma, ao_voltar)
            return

        def continuar() -> None:
            self._trocar("jogo", _TelaVazia(self))
            ao_voltar()

        # 1) mensagem ambiental + pergunta de compreensão (RF15)
        # 2) cutscene da fase
        def depois_da_mensagem() -> None:
            cena = historia.BIOMAS.get(bioma, historia.BIOMAS[0])
            self._trocar("cutscene", Cutscene(self, [cena], continuar,
                                              rotulo=f"FASE {bioma + 1}"))

        self._trocar("ambiental", Ambiental(self, bioma, depois_da_mensagem))

    # ---------------------------- finais ------------------------------ #
    def mostrar_fim(self, jogo) -> None:
        self.jogo.ativo = False
        self.jogo.pausado = False
        self._novo_recorde = self.registrar_fim(jogo)

        if jogo.infinito:
            # sem cutscene de desfecho: o sonho simplesmente acaba
            self._abrir_fim(jogo)
            return

        if self.modo_historia and not self._final_mostrado:
            self._final_mostrado = True
            self.dados["historias"] = int(self.dados.get("historias", 0)) + 1
            persistencia.salvar(self.dados)
            cena = historia.FINAIS["vitoria" if jogo.fim == "vitoria" else "derrota"]

            def abrir_final() -> None:
                self._trocar("cutscene", Cutscene(self, [cena],
                                                  lambda: self._abrir_fim(jogo),
                                                  rotulo="FINAL"))

            # vitória: a fase 4 também entrega a sua mensagem ambiental
            # (RF15: "uma mensagem ambiental por fase concluída")
            if jogo.fim == "vitoria":
                self._trocar("ambiental",
                             Ambiental(self, len(config.BIOMAS) - 1, abrir_final))
            else:
                abrir_final()
            return

        self._abrir_fim(jogo)

    def _abrir_fim(self, jogo) -> None:
        self._trocar("fim", Fim(self, jogo, self._novo_recorde))

    def registrar_fim(self, jogo) -> bool:
        if jogo.infinito:
            bioma = jogo.numero_bioma
            infinito = True
        else:
            bioma = jogo.bioma_index + 1
            infinito = False
        return persistencia.registrar_partida(
            self.dados,
            pontos=jogo.pontos,
            tempo_restante=jogo.tempo,
            bioma=bioma,
            vitoria=(jogo.fim == "vitoria"),
            infinito=infinito,
        )

    # ================================================================== #
    # Laço principal
    # ================================================================== #
    def executar(self) -> None:
        while self.rodando:
            dt = min(self.relogio.tick(config.FPS) / 1000.0, 1 / 20)
            self.quadros += 1
            self._eventos()
            self._atualizar(dt)
            self._desenhar()
            pygame.display.flip()
        pygame.quit()

    def _eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                continue
            if self.estado == "jogo":
                if self.jogo.tratar_evento(evento):
                    continue
            else:
                self.tela_atual.tratar_evento(evento)

    def _atualizar(self, dt: float) -> None:
        self.audio.atualizar(dt)

        if self.estado == "jogo":
            self.jogo.atualizar(dt)
        else:
            self.tela_atual.atualizar(dt)

        if self.fade_dir < 0:
            self.fade = max(0.0, self.fade - dt * 4.0)

    def _desenhar(self) -> None:
        if self.estado == "jogo":
            self.jogo.desenhar(self.tela)
        else:
            self.tela_atual.desenhar(self.tela)

        if self.fade > 0.01:
            veu = pygame.Surface((config.LARGURA, config.ALTURA))
            veu.fill((3, 5, 10))
            veu.set_alpha(int(255 * self.fade))
            self.tela.blit(veu, (0, 0))


class _TelaVazia:
    """Usada enquanto o estado é 'jogo' (o Jogo desenha por conta própria)."""

    def __init__(self, app) -> None:
        self.app = app

    def entrar(self) -> None:
        pass

    def tratar_evento(self, evento) -> None:
        pass

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, tela) -> None:
        pass


def principal() -> None:
    App().executar()


if __name__ == "__main__":
    principal()
