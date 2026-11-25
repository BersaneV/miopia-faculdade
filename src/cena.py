"""
cena.py — reprodutor de cutscene (modo história).

O que este arquivo garante:
  1. O texto NUNCA escapa da caixa. O painel é medido pelo conteúdo, as falas
     são divididas em páginas que cabem e, como rede de segurança, o desenho
     é recortado (clip) na área interna do painel.
  2. Cada fala tem um falante (Narrador, Lume, Breu, Coruja) — isso ajuda o
     público a entender quem está falando.
  3. O texto é revelado aos poucos (máquina de escrever). ESPAÇO/clique
     completa a página; de novo, avança. ESC pula a sequência.

As falas chegam como (quem, texto). Falas seguidas do MESMO falante viram um
parágrafo só (o nome aparece uma vez, não a cada linha); o nome volta a
aparecer quando OUTRO personagem começa a falar — e também no topo de uma
página nova, para nunca perder quem está falando. Falas longas são quebradas
em blocos maiores que uma página, então cada página mostra poucas linhas por
vez: leitura confortável em vez de parede de texto.
"""

from __future__ import annotations

import math

import pygame

from . import config
from . import ui
from . import utils

VELOCIDADE_TEXTO = 52      # caracteres por segundo
TEMPO_ENTRE_CENAS = 0.35
BARRA = 54                 # letterbox de cima e de baixo
LARGURA_PAINEL = 720
ALTURA_MAX_TEXTO = 258     # área de texto disponível dentro do painel
ENTRELINHA = 1.42          # respiro entre linhas da MESMA fala
ESPACO_BLOCO = 18          # respiro entre falas (troca de falante)


def _normalizar(falas) -> list[tuple[str | None, str]]:
    """Aceita ("quem", "texto") ou só "texto" (falante = None)."""
    saida = []
    for fala in falas:
        if isinstance(fala, (tuple, list)) and len(fala) == 2:
            saida.append((str(fala[0]), str(fala[1])))
        else:
            saida.append((None, str(fala)))
    return saida


def _agrupar_falas(falas) -> list[tuple[str | None, str]]:
    """
    Junta falas seguidas do mesmo falante num parágrafo só.

    Era o que o público reclamava: três frases do narrador viravam três
    blocos com "NARRADOR" repetido em cima de cada um. Agora o nome aparece
    uma vez por fala contínua — e só muda de bloco quando muda quem fala.
    """
    grupos: list[tuple[str | None, str]] = []
    for quem, texto in falas:
        texto = texto.strip()
        if not texto:
            continue
        if grupos and quem and grupos[-1][0] == quem:
            anterior_quem, anterior_texto = grupos[-1]
            grupos[-1] = (anterior_quem, anterior_texto + " " + texto)
        else:
            grupos.append((quem, texto))
    return grupos


def _quebrar_em_blocos(falas, fonte, largura, limite: int) -> list[tuple[str | None, str]]:
    """
    Divide falas longas em blocos que caibam sozinhos numa página.
    Corta em fim de frase (., !, ?) — nunca no meio de uma palavra.
    Só o primeiro pedaço leva o nome do falante; os seguintes são a
    continuação da mesma fala.
    """
    blocos: list[tuple[str | None, str]] = []
    for quem, texto in falas:
        if len(utils.quebrar_texto(fonte, texto, largura)) * fonte.get_linesize() <= limite:
            blocos.append((quem, texto))
            continue

        partes, atual = [], ""
        for pedaco in texto.replace("!", "!|").replace("?", "?|").replace(".", ".|").split("|"):
            pedaco = pedaco.strip()
            if not pedaco:
                continue
            teste = (atual + " " + pedaco).strip()
            if atual and len(utils.quebrar_texto(fonte, teste, largura)) * fonte.get_linesize() > limite:
                partes.append(atual)
                atual = pedaco
            else:
                atual = teste
        if atual:
            partes.append(atual)
        for i, parte in enumerate(partes):
            blocos.append((quem if i == 0 else None, parte))
    return blocos


def _altura_blocos(blocos, fonte, fonte_nome, largura, espaco=ESPACO_BLOCO) -> int:
    altura = 0
    for i, (quem, texto) in enumerate(blocos):
        if quem:
            altura += fonte_nome.get_linesize()
        altura += len(utils.quebrar_texto(fonte, texto, largura)) * int(fonte.get_linesize() * ENTRELINHA)
        if i < len(blocos) - 1:
            altura += espaco
    return altura


class Cutscene:
    def __init__(self, app, cenas: list[dict], ao_terminar, *, pular_permitido=True,
                 rotulo: str = "HISTÓRIA") -> None:
        self.app = app
        self.recursos = app.recursos
        self.audio = app.recursos.audio
        self.cenas = cenas
        self.ao_terminar = ao_terminar
        self.pular_permitido = pular_permitido
        self.rotulo = rotulo

        self.fonte = self.recursos.fonte("corpo")
        self.fonte_nome = self.recursos.fonte("pequena_forte")

        self.indice = 0            # cena atual
        self.pagina = 0            # página dentro da cena
        self.tempo = 0.0
        self.tempo_cena = 0.0
        self.revelado = 0.0
        self.saindo = False
        self.pausa_saida = 0.0
        self.concluida = False

        self.arte = pygame.Surface((config.LARGURA, config.ALTURA))
        self.paginas_cena: list[list[tuple[str | None, str]]] = [[]]
        self.total_paginas = 1
        self.pagina_global = 0

    # ------------------------------------------------------------------ #
    # Montagem das páginas
    # ------------------------------------------------------------------ #
    def _montar(self) -> None:
        largura_texto = LARGURA_PAINEL - 76
        self.paginas_por_cena: list[list[list[tuple[str | None, str]]]] = []
        for cena in self.cenas:
            blocos = _quebrar_em_blocos(_agrupar_falas(_normalizar(cena.get("falas", []))),
                                        self.fonte, largura_texto, ALTURA_MAX_TEXTO)
            paginas: list[list[tuple[str | None, str]]] = []
            atual: list[tuple[str | None, str]] = []
            for bloco in blocos:
                teste = atual + [bloco]
                if atual and _altura_blocos(teste, self.fonte, self.fonte_nome,
                                            largura_texto) > ALTURA_MAX_TEXTO:
                    paginas.append(atual)
                    atual = [bloco]
                else:
                    atual = teste
            if atual:
                paginas.append(atual)

            # continuou a fala numa página nova? o nome volta, para o leitor
            # não ficar sem saber quem está falando
            falante = None
            for pagina in paginas:
                if pagina and pagina[0][0] is None and falante:
                    pagina[0] = (falante, pagina[0][1])
                falante = next((quem for quem, _ in pagina if quem), falante)

            self.paginas_por_cena.append(paginas or [[(None, "")]])

        self.total_paginas = sum(len(p) for p in self.paginas_por_cena)

    @property
    def cena(self) -> dict:
        return self.cenas[min(self.indice, len(self.cenas) - 1)]

    @property
    def blocos(self) -> list[tuple[str | None, str]]:
        paginas = self.paginas_por_cena[min(self.indice, len(self.paginas_por_cena) - 1)]
        return paginas[min(self.pagina, len(paginas) - 1)]

    def _posicao_global(self) -> int:
        return sum(len(p) for p in self.paginas_por_cena[: self.indice]) + self.pagina

    def _texto_da_pagina(self) -> str:
        return "".join(texto for _, texto in self.blocos)

    # ------------------------------------------------------------------ #
    def entrar(self) -> None:
        self._montar()
        self.indice = 0
        self.pagina = 0
        self.tempo = 0.0
        self.pagina_global = 0
        self._iniciar_pagina()
        self._trocar_trilha()

    def _iniciar_pagina(self) -> None:
        self.revelado = 0.0
        self.tempo_cena = 0.0
        self.concluida = False

    def _trocar_trilha(self) -> None:
        """Cada cena pode ter a sua trilha (a cena do bioma toca a trilha dele)."""
        if not self.audio:
            return
        trilha = self.cena.get("trilha")
        if trilha:
            self.audio.tocar_musica(trilha)

    # ------------------------------------------------------------------ #
    def tratar_evento(self, evento) -> None:
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.pular_permitido:
                    self._sair()
                return
            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self._avancar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self._avancar()

    def _avancar(self) -> None:
        if self.saindo:
            return
        total = len(self._texto_da_pagina())
        if not self.concluida:
            self.revelado = total
            self.concluida = True
            if self.audio:
                self.audio.tocar("clique")
            return

        paginas = self.paginas_por_cena[self.indice]
        if self.pagina + 1 < len(paginas):
            self.pagina += 1
            self.pagina_global += 1
            self._iniciar_pagina()
            if self.audio:
                self.audio.tocar("pagina")
            return

        if self.indice + 1 < len(self.cenas):
            self.indice += 1
            self.pagina = 0
            self.pagina_global += 1
            self._iniciar_pagina()
            self._trocar_trilha()
            if self.audio:
                self.audio.tocar("pagina")
            return

        self._sair()

    def _sair(self) -> None:
        if self.saindo:
            return
        self.saindo = True
        self.pausa_saida = TEMPO_ENTRE_CENAS
        if self.audio:
            self.audio.tocar("clique")

    # ------------------------------------------------------------------ #
    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        self.tempo_cena += dt

        if not self.concluida:
            self.revelado += VELOCIDADE_TEXTO * dt
            if self.revelado >= len(self._texto_da_pagina()):
                self.revelado = len(self._texto_da_pagina())
                self.concluida = True

        if self.saindo:
            self.pausa_saida -= dt
            if self.pausa_saida <= 0:
                self.ao_terminar()

    # ------------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------------ #
    def desenhar(self, tela: pygame.Surface) -> None:
        # ---------------- arte ----------------
        from . import historia
        historia.desenhar_cena(self.cena.get("arte", ""), self.arte, self.tempo_cena)

        zoom = 1.0 + 0.012 * math.sin(self.tempo_cena * 0.35)
        largura = int(config.LARGURA * zoom)
        altura = int(config.ALTURA * zoom)
        if largura != config.LARGURA:
            ampliada = pygame.transform.smoothscale(self.arte, (largura, altura))
            tela.blit(ampliada, ((config.LARGURA - largura) // 2,
                                 (config.ALTURA - altura) // 2))
        else:
            tela.blit(self.arte, (0, 0))

        # ---------------- letterbox ----------------
        pygame.draw.rect(tela, (3, 4, 8), (0, 0, config.LARGURA, BARRA))
        pygame.draw.rect(tela, (3, 4, 8), (0, config.ALTURA - BARRA, config.LARGURA, BARRA))

        # ---------------- topo ----------------
        ui.chip(tela, self.fonte_nome, self.rotulo, ui.MARGEM, 16, icone="livro",
                cor_texto=ui.ACENTO)

        local = self.cena.get("local", "")
        if local:
            ui.texto(tela, self.fonte, local, ui.TEXTO_MEDIO,
                     config.LARGURA - ui.MARGEM, BARRA / 2 + 2,
                     alinhamento="dir", vertical="meio")

        # ---------------- painel da legenda (medido pelo conteúdo) ----------------
        largura_texto = LARGURA_PAINEL - 76
        altura_conteudo = _altura_blocos(self.blocos, self.fonte, self.fonte_nome,
                                         largura_texto)
        altura_painel = int(utils.clamp(altura_conteudo + 52, 118, 320))

        caixa = pygame.Rect((config.LARGURA - LARGURA_PAINEL) // 2,
                            config.ALTURA - BARRA - altura_painel - 22,
                            LARGURA_PAINEL, altura_painel)

        # gradiente escuro atrás do painel (contraste em qualquer arte)
        altura_veu = caixa.height + 90
        veu = pygame.Surface((config.LARGURA, altura_veu), pygame.SRCALPHA)
        for i in range(altura_veu):
            t = i / altura_veu
            pygame.draw.line(veu, (4, 6, 11, int(196 * t ** 1.5)), (0, i),
                             (config.LARGURA, i))
        tela.blit(veu, (0, caixa.bottom - altura_veu))

        ui.painel(tela, caixa, raio=ui.RAIO["lg"], alpha=246, brilho_topo=True)
        pygame.draw.rect(tela, (*ui.ACENTO, 200), (caixa.x + 22, caixa.y + 22, 3,
                                                   caixa.height - 44), border_radius=2)

        # ---------------- texto (com recorte de segurança) ----------------
        area = pygame.Rect(caixa.x + 44, caixa.y + 24, largura_texto, caixa.height - 46)
        recorte_anterior = tela.get_clip()
        tela.set_clip(area)

        restante = int(self.revelado)
        y = area.y
        for quem, texto in self.blocos:
            if restante <= 0:
                break
            parcial = texto[:restante]
            restante -= len(texto)

            if quem:
                cor_nome = self._cor_do_falante(quem)
                ui.texto(tela, self.fonte_nome, quem.upper(), cor_nome, area.x, y)
                y += self.fonte_nome.get_linesize()

            for linha in utils.quebrar_texto(self.fonte, parcial, area.width):
                ui.texto(tela, self.fonte, linha, ui.TEXTO, area.x, y)
                y += int(self.fonte.get_linesize() * ENTRELINHA)
            y += ESPACO_BLOCO

        tela.set_clip(recorte_anterior)

        # ---------------- rodapé da barra ----------------
        if self.concluida:
            ultimo = (self._posicao_global() >= self.total_paginas - 1)
            if ultimo:
                dica = "ver o resultado" if self.rotulo == "FINAL" else "começar"
            else:
                dica = "continuar"
            pulso = 0.6 + 0.4 * math.sin(self.tempo * 4)
            cor_dica = utils.misturar(ui.TEXTO_MEDIO, (255, 255, 255), pulso)
            larg = ui.largura(self.fonte_nome, dica)
            x_dica = config.LARGURA - ui.MARGEM - larg
            ui.texto(tela, self.fonte_nome, dica, cor_dica, x_dica,
                     config.ALTURA - BARRA / 2, vertical="meio")
            chip = ui.tecla(tela, self.fonte_nome, "ESPAÇO",
                            x_dica - 96, config.ALTURA - BARRA / 2 - 13)
            ui.seta(tela, (chip.x - 16, config.ALTURA - BARRA / 2), "dir", cor_dica, 5)
        else:
            ui.texto(tela, self.fonte, "ESPAÇO completa o texto",
                     ui.TEXTO_APAGADO, config.LARGURA - ui.MARGEM,
                     config.ALTURA - BARRA / 2, alinhamento="dir", vertical="meio")

        # progresso (uma bolinha por página, não por cena)
        total = min(self.total_paginas, 12)
        for i in range(total):
            cor = ui.ACENTO if i <= self._posicao_global() else (54, 66, 90)
            pygame.draw.circle(tela, cor, (ui.MARGEM + i * 13, config.ALTURA - BARRA / 2),
                               4 if i == self._posicao_global() else 3)
        if self.total_paginas > 12:
            ui.texto(tela, self.fonte, f"{self._posicao_global() + 1}/{self.total_paginas}",
                     ui.TEXTO_APAGADO,
                     ui.MARGEM + total * 13 + 6, config.ALTURA - BARRA / 2, vertical="meio")

        if self.pular_permitido:
            ui.texto(tela, self.fonte, "Esc pula a cena", ui.TEXTO_APAGADO,
                     config.LARGURA // 2, config.ALTURA - BARRA / 2,
                     alinhamento="centro", vertical="meio")

        # ---------------- fade de saída ----------------
        if self.saindo:
            progresso = 1 - max(0.0, self.pausa_saida) / TEMPO_ENTRE_CENAS
            veu_saida = pygame.Surface((config.LARGURA, config.ALTURA))
            veu_saida.fill((3, 5, 10))
            veu_saida.set_alpha(int(255 * utils.clamp(progresso, 0, 1)))
            tela.blit(veu_saida, (0, 0))

    # ------------------------------------------------------------------ #
    @staticmethod
    def _cor_do_falante(quem: str):
        return {
            "NARRADOR": (150, 164, 192),
            "LUME": config.LUZ_QUENTE,
            "BREU": (176, 148, 232),
            "CORUJA": config.OURO,
        }.get(quem.upper(), ui.ACENTO)
