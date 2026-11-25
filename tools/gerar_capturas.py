"""
gerar_capturas.py — roda o Miopia SEM MONITOR e salva as imagens do README.

    python tools/gerar_capturas.py

Produz em capturas/:
    01_menu.png        menu principal (com registro e dificuldade)
    02_intro.png       cutscene de abertura (modo história)
    03_partida.png     partida em andamento (com clarão)
    03b_clarao.png     clarão em uso
    03c_coleta.png     coleta de orvalho
    04_bioma3.png      bioma diferente, mostrando a paleta
    05_briefing.png    cartão entre biomas (modo rápido)
    06_fim.png         tela de fim de jogo
    07_ajuda.png       como jogar
    08_pausa.png       menu de pausa
    09_coruja.png      bioma 4, com a Coruja e aviso de luz baixa
    10_historia.png    cutscene de bioma (modo história)
    11_final.png       cutscene de desfecho
    12_creditos.png    créditos
    13_infinito.png    cutscene de abertura do modo infinito
    14_infinito_jogo.png  modo infinito: bioma 9, volta 3
    15_volta.png       cartão de checkpoint entre voltas (modo infinito)
    16_chefe.png       boss fight: a Coruja na fase 4
    17_ambiental.png   mensagem ambiental + pergunta de compreensão (fim de fase)
    partida.gif        ~9 segundos de jogo

Como funciona: usa os drivers "dummy" do SDL (sem janela) e chama o mesmo
laço de atualização/desenho do jogo. O teclado é simulado por um dicionário.
"""

from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import pygame  # noqa: E402

from src.main import App  # noqa: E402

SAIDA = os.path.join(RAIZ, "capturas")
DT = 1 / 60


class TecladoFalso(dict):
    """Substitui pygame.key.get_pressed() para simular teclas pressionadas."""

    def __missing__(self, chave):
        return False

    def marcar(self, *teclas) -> None:
        self.clear()
        for tecla in teclas:
            self[tecla] = True


def salvar(tela, nome: str) -> str:
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    pygame.image.save(tela, caminho)
    print(f"  · {nome}")
    return caminho


def passos(app, quantidade: int, teclado=None, capturar_gif=None) -> None:
    for _ in range(quantidade):
        app._atualizar(DT)
        app._desenhar()
        if capturar_gif is not None:
            capturar_gif.quadro(app.tela)


def main() -> None:
    app = App()
    teclado = TecladoFalso()
    pygame.key.get_pressed = lambda: teclado

    print("Gerando capturas em", SAIDA)

    # ---------- 1. menu ----------
    app.estado = "menu"
    from src.telas import Menu
    app.tela_atual = Menu(app)
    app.tela_atual.entrar()
    app.fade = 0.0
    for _ in range(90):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "01_menu.png")

    # ---------- 2. cutscene de abertura (modo história) ----------
    from src import historia
    from src.cena import Cutscene
    app._trocar("cutscene", Cutscene(app, historia.INTRO, lambda: None, rotulo="PRÓLOGO"))
    app.fade = 0.0
    for _ in range(210):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "02_intro.png")

    # ---------- 3. ajuda ----------
    app.abrir_ajuda()
    app.fade = 0.0
    for _ in range(30):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "07_ajuda.png")

    # ---------- 4. partida ----------
    from src.main import _TelaVazia
    app._trocar("jogo", _TelaVazia(app))
    app.jogo.iniciar()
    app.fade = 0.0

    # posiciona o jogador perto de um orvalho para a foto ficar boa
    jogo = app.jogo
    orvalho = min(jogo.orvalhos, key=lambda o: abs(o.y - jogo.jogador.y))
    jogo.jogador.x, jogo.jogador.y = orvalho.x - 70, orvalho.y + 30

    from PIL import Image

    quadros_gif: list = []
    fps_gif = 12
    acumular = 0.0

    def gif_quadro(superficie) -> None:
        nonlocal acumular
        acumular += DT
        if acumular >= 1 / fps_gif:
            acumular = 0.0
            dados = pygame.image.tobytes(superficie, "RGB")
            imagem = Image.frombytes("RGB", superficie.get_size(), dados)
            quadros_gif.append(imagem.resize((560, 350), Image.LANCZOS))

    # ---------- gravação do GIF com movimento real ----------
    jogo.banner_timer = 0.0
    jogo.dica_timer = 0.0
    quadros_gif.clear()

    from collections import deque

    def proximo_no(caminho_ini, caminho_fim):
        """Primeira célula do caminho mais curto no mapa (BFS)."""
        mundo = jogo.mundo
        ini = (int(caminho_ini[0] // 40), int(caminho_ini[1] // 40))
        fim = (int(caminho_fim[0] // 40), int(caminho_fim[1] // 40))
        if ini == fim:
            return caminho_fim
        veio = {ini: None}
        fila = deque([ini])
        while fila:
            atual = fila.popleft()
            if atual == fim:
                break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                viz = (atual[0] + dx, atual[1] + dy)
                if viz in veio or mundo.parede(*viz):
                    continue
                veio[viz] = atual
                fila.append(viz)
        if fim not in veio:
            return caminho_fim
        no = fim
        while veio[no] is not None and veio[no] != ini:
            no = veio[no]
        return (no[0] * 40 + 20, no[1] * 40 + 20)

    def dirigir(alvo, correr=False):
        no = proximo_no((jogo.jogador.x, jogo.jogador.y), alvo)
        teclado.clear()
        dx, dy = no[0] - jogo.jogador.x, no[1] - jogo.jogador.y
        if dx > 3:
            teclado[pygame.K_RIGHT] = True
        elif dx < -3:
            teclado[pygame.K_LEFT] = True
        if dy > 3:
            teclado[pygame.K_DOWN] = True
        elif dy < -3:
            teclado[pygame.K_UP] = True
        if correr:
            teclado[pygame.K_LSHIFT] = True

    def garantir_partida() -> None:
        """O bot pode fechar o bioma no meio da captura; volta para a partida."""
        if app.estado != "jogo":
            from src.main import _TelaVazia
            app._trocar("jogo", _TelaVazia(app))
            jogo.ativo = True
            jogo.pausado = False
            app.fade = 0.0

    def gravar(frames: int, alvo_fn) -> None:
        for i in range(frames):
            alvo = alvo_fn()
            if alvo:
                dirigir(alvo, correr=(jogo.jogador.energia > 40 and i % 60 > 35))
            else:
                teclado.clear()
            app._atualizar(DT)
            app._desenhar()
            gif_quadro(app.tela)

    def alvo_orvalho():
        restantes = [o for o in jogo.orvalhos if not o.coletado]
        if jogo.saida_aberta:
            return jogo.mundo.saida
        if not restantes:
            return None
        o = min(restantes, key=lambda o: (o.x - jogo.jogador.x) ** 2 + (o.y - jogo.jogador.y) ** 2)
        return (o.x, o.y)

    gravar(150, alvo_orvalho)          # anda e coleta
    salvar(app.tela, "03_partida.png")

    teclado.clear()
    teclado[pygame.K_SPACE] = True      # clarão
    for _ in range(16):
        app._atualizar(DT)
        app._desenhar()
        gif_quadro(app.tela)
    salvar(app.tela, "03b_clarao.png")
    teclado.clear()

    gravar(80, alvo_orvalho)           # segue coletando
    garantir_partida()
    # segura o bioma aberto e monta uma cena clara de "pontuação subindo"
    jogo.saida_aberta = False
    jogo.coletados = min(jogo.coletados, max(1, jogo.necessario - 4))
    jogo.pontos = max(jogo.pontos, 240)
    jogo.dica_timer = 0.0
    teclado.clear()
    restantes = [o for o in jogo.orvalhos if not o.coletado]
    # coleta de verdade: passa por cima de dois orvalhos (o HUD sobe junto)
    for orvalho in restantes[:2]:
        jogo.jogador.x, jogo.jogador.y = orvalho.x, orvalho.y
        for _ in range(3):
            app._atualizar(DT)
            app._desenhar()
    if len(restantes) > 2:
        alvo = restantes[2]
        jogo.jogador.x, jogo.jogador.y = alvo.x - 46, alvo.y + 22
    for _ in range(18):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "03c_coleta.png")

    # ---------- 4b. pausa (com o jogo rodando) ----------
    garantir_partida()
    jogo.pausado = True
    jogo._indice_pausa = 0
    jogo._sincronizar_pausa()
    for _ in range(20):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "08_pausa.png")
    jogo.pausado = False

    # ---------- 5. bioma 3 (paleta diferente) ----------
    garantir_partida()
    jogo._carregar_bioma(2)
    jogo.jogador.invulneravel = 0
    jogo.jogador.energia = 78
    for _ in range(80):
        app._atualizar(DT)
        app._desenhar()
        gif_quadro(app.tela)
    salvar(app.tela, "04_bioma3.png")

    # ---------- 5b. bioma 4 com a Coruja e aviso de luz baixa ----------
    jogo._carregar_bioma(3)
    jogo.jogador.invulneravel = 0
    jogo.jogador.energia = 18
    jogo.banner_timer = 0
    jogo.dica_timer = 0
    coruja = next((i for i in jogo.inimigos if i.tipo == "coruja"), None)
    if coruja:
        jogo.jogador.x = max(40, coruja.x - 140)
        jogo.jogador.y = coruja.y + 60
        while jogo.mundo.colide(jogo.jogador.x, jogo.jogador.y, 9) and jogo.jogador.x > 60:
            jogo.jogador.x -= 20
    for _ in range(50):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "09_coruja.png")

    # ---------- 5c. boss fight (Coruja) ----------
    jogo._carregar_bioma(3)
    jogo.banner_timer = 0
    jogo.dica_timer = 0
    coruja = jogo.chefe
    jogo.jogador.x = max(50, coruja.x - 150)
    jogo.jogador.y = coruja.y + 40
    while jogo.mundo.colide(jogo.jogador.x, jogo.jogador.y, 9) and jogo.jogador.x > 50:
        jogo.jogador.x -= 20
    for _ in range(30):
        app._atualizar(DT)
        app._desenhar()
    coruja.assustar(2.6)
    for _ in range(8):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "16_chefe.png")

    # ---------- 5d. mensagem ambiental + pergunta ----------
    from src.telas import Ambiental
    mensagem = Ambiental(app, 0, lambda: None)
    app._trocar("ambiental", mensagem)
    for _ in range(20):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "17_ambiental.png")

    # ---------- 6. briefing ----------
    app.mostrar_briefing(3, lambda: None)
    app.fade = 0.0
    for _ in range(40):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "05_briefing.png")

    # ---------- 6b. cutscene de bioma (modo história) ----------
    app.modo_historia = True
    app.mostrar_intervalo(1, lambda: None)
    app.fade = 0.0
    for _ in range(200):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "10_historia.png")

    # ---------- 6c. cutscene de desfecho ----------
    from src import historia as _historia
    from src.cena import Cutscene as _Cutscene
    app._trocar("cutscene", _Cutscene(app, [_historia.FINAIS["vitoria"]],
                                      lambda: None, rotulo="FINAL"))
    app.fade = 0.0
    for _ in range(240):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "11_final.png")

    # ---------- 6c2. modo infinito ----------
    from src import historia as _historia2
    from src.cena import Cutscene as _Cutscene2
    app._trocar("cutscene", _Cutscene2(app, _historia2.INFINITO, lambda: None,
                                       rotulo="INFINITO"))
    app.fade = 0.0
    for _ in range(200):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "13_infinito.png")

    from src.main import _TelaVazia as _Vazia
    app._trocar("jogo", _Vazia(app))
    app.jogo.iniciar("infinito")
    app.fade = 0.0
    jogo = app.jogo
    for _ in range(8):                      # chega à volta 3
        jogo._fechar_bioma()
    jogo.banner_timer = 4.0
    for _ in range(90):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "14_infinito_jogo.png")

    app.mostrar_volta(jogo.numero_bioma, lambda: None)
    app.fade = 0.0
    for _ in range(40):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "15_volta.png")

    # ---------- 6d. créditos ----------
    app.modo_historia = False
    app.abrir_creditos()
    app.fade = 0.0
    for _ in range(30):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "12_creditos.png")

    # ---------- 7. fim de jogo ----------
    jogo.fim = "derrota"
    jogo.pontos = 1234
    app.mostrar_fim(jogo)
    app.fade = 0.0
    for _ in range(45):
        app._atualizar(DT)
        app._desenhar()
    salvar(app.tela, "06_fim.png")

    # ---------- GIF ----------
    if quadros_gif:
        caminho = os.path.join(SAIDA, "partida.gif")
        # paleta compartilhada em 128 cores: mesma leitura, arquivo 60% menor
        base = quadros_gif[0].quantize(colors=128, method=Image.MEDIANCUT)
        paleta = [q.quantize(palette=base, dither=Image.NONE) for q in quadros_gif]
        paleta[0].save(caminho, save_all=True, append_images=paleta[1:],
                       duration=int(1000 / fps_gif), loop=0, optimize=True)
        tamanho = os.path.getsize(caminho) / 1e6
        print(f"  · partida.gif ({len(quadros_gif)} quadros, {tamanho:.1f} MB)")

    print("Pronto.")


if __name__ == "__main__":
    main()
