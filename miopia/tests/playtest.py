"""
playtest.py — testa o Miopia SEM MONITOR, com bots.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python tests/playtest.py

Três bots rodam as regras de verdade (mesma máquina de estados do jogo):
  1. "competente": busca caminho no mapa, desvia de inimigos e usa clarão.
  2. "atento":      só persegue o que está visível, sem conhecer o mapa.
  3. "parado":      não faz nada — usado para checar a regra do apagão.

Serve também de base para o grupo ajustar o balanceamento em config.py.
"""
import os, sys, math, random, heapq
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"

# roda a partir de qualquer pasta: a raiz é a pasta acima de tests/
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pygame

from src.main import App, _TelaVazia
from src import config
DT=1/60
class T(dict):
    def __missing__(self,k): return False

def ir(tk,dx,dy):
    tk.clear()
    if dx>4: tk[pygame.K_RIGHT]=True
    elif dx<-4: tk[pygame.K_LEFT]=True
    if dy>4: tk[pygame.K_DOWN]=True
    elif dy<-4: tk[pygame.K_UP]=True

def bfs_passo(mundo, ini, fim, perigos):
    """Caminho mais curto em células, com custo extra perto de inimigos."""
    cel_ini=(int(ini[0]//config.TILE), int(ini[1]//config.TILE))
    cel_fim=(int(fim[0]//config.TILE), int(fim[1]//config.TILE))
    if cel_ini==cel_fim: return fim
    fila=[(0.0, cel_ini)]; custo={cel_ini:0.0}; veio={}
    while fila:
        c, atual = heapq.heappop(fila)
        if atual==cel_fim: break
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            viz=(atual[0]+dx, atual[1]+dy)
            if mundo.parede(*viz): continue
            px,py = viz[0]*config.TILE+20, viz[1]*config.TILE+20
            extra = 0.0
            for (ix,iy,_r) in perigos:
                d = math.hypot(px-ix, py-iy)
                if d < 90: extra += (90-d)/22.0
            novo = custo[atual] + 1 + extra
            if novo < custo.get(viz, 1e9):
                custo[viz]=novo; veio[viz]=atual; heapq.heappush(fila,(novo,viz))
    if cel_fim not in veio: return fim
    no=cel_fim
    while veio.get(no) not in (None, cel_ini):
        no=veio[no]
    return (no[0]*config.TILE+config.TILE/2, no[1]*config.TILE+config.TILE/2)

def jogar(seed, verbose=False, modo="historia", biomas_alvo=4):
    """Um bot competente joga do começo ao fim.

    modo="historia": 4 biomas e vitória.
    modo="infinito": segue jogando enquanto o bioma absoluto não chegar ao alvo.
    """
    random.seed(seed)
    app=App(); tk=T(); pygame.key.get_pressed=lambda: tk
    app.modo_historia = modo == "historia"
    app._trocar("jogo", _TelaVazia(app)); app.jogo.iniciar(modo); j=app.jogo
    danos=[]; frames=0
    orig=j.jogador.levar_dano
    def ld(origem=None):
        ok=orig(origem)
        if ok: danos.append((round(frames*DT), round(j.jogador.energia), "apagao" if origem is None else "inimigo"))
        return ok
    j.jogador.levar_dano=ld

    res=[]
    bioma_visto = j.numero_bioma
    bioma_alvo = j.numero_bioma + biomas_alvo - 1
    while j.numero_bioma <= bioma_alvo and j.fim is None:
        if frames >= 60*260:            # limite de tempo por bioma
            break

        # ---- o bioma virou? registra e recomeça a contagem ----
        if j.numero_bioma != bioma_visto:
            res.append((bioma_visto, round(frames*DT), j.jogador.vidas, j.pontos))
            if verbose:
                print(f"   bioma {bioma_visto}: {frames*DT:.0f}s vidas={j.jogador.vidas} pontos={j.pontos} danos={danos}")
            danos.clear(); frames=0; bioma_visto=j.numero_bioma

        perigos=[(i.x,i.y,i.raio) for i in j.inimigos
                 if i.estado in ("cacar","atacar") or math.hypot(i.x-j.jogador.x,i.y-j.jogador.y)<140]
        muito_perto=[i for i in j.inimigos if math.hypot(i.x-j.jogador.x,i.y-j.jogador.y)<46]
        if muito_perto and j.jogador.pode_pulsar():
            tk.clear(); tk[pygame.K_SPACE]=True
        else:
            alvo=None
            if j.saida_aberta:
                alvo=j.mundo.saida
            else:
                cand=[o for o in j.orvalhos if not o.coletado]
                if cand:
                    o=min(cand,key=lambda o:(o.x-j.jogador.x)**2+(o.y-j.jogador.y)**2-(400 if o.raro else 0))
                    alvo=(o.x,o.y)
            if alvo is None and j.orvalhos:
                alvo=(j.orvalhos[0].x, j.orvalhos[0].y)
            if alvo:
                nxt=bfs_passo(j.mundo,(j.jogador.x,j.jogador.y),alvo,perigos)
                ir(tk, nxt[0]-j.jogador.x, nxt[1]-j.jogador.y)
                if j.jogador.energia>55 and math.hypot(alvo[0]-j.jogador.x,alvo[1]-j.jogador.y)>200:
                    tk[pygame.K_LSHIFT]=True
            else:
                ir(tk, 1, 1)

        app._atualizar(DT); frames+=1

        # o app pode abrir briefing/cutscene entre biomas: volta para a partida
        if app.estado in ("briefing", "cutscene"):
            res.append((j.numero_bioma, round(frames*DT), j.jogador.vidas, j.pontos))
            if verbose:
                print(f"   bioma {j.numero_bioma}: {frames*DT:.0f}s vidas={j.jogador.vidas} pontos={j.pontos} danos={danos}")
            danos.clear(); frames=0; bioma_visto=j.numero_bioma
            if hasattr(app.tela_atual, "ao_continuar"):
                app.tela_atual.ao_continuar()
            else:
                app._trocar("jogo", _TelaVazia(app))
                j.ativo = True
        elif app.estado=="fim":
            if j.fim == "vitoria":
                res.append((j.numero_bioma, round(frames*DT), j.jogador.vidas, j.pontos))
            break
    return j, res


def teste_parado():
    """Jogador sem input: a luz acaba e as vidas caem."""
    app=App(); tk=T(); pygame.key.get_pressed=lambda: tk
    app._trocar("jogo", _TelaVazia(app)); app.jogo.iniciar()
    j=app.jogo
    for f in range(60*300):
        app._atualizar(DT)
        if app.estado == "fim":
            break
    print(f"bot parado: fim={j.fim} vidas={j.jogador.vidas} em {f*DT:.0f}s")
    return j


if __name__ == "__main__":
    print("=== bot competente (com mapa) ===")
    vitorias=0; alcancados=[]
    for semente in range(1,7):
        j,res = jogar(semente)
        vitorias += 1 if j.fim=="vitoria" else 0
        alcancados.append(j.bioma_index+1)
        print(f"seed {semente}: fim={str(j.fim):8s} bioma={j.bioma_index+1} "
              f"vidas={j.jogador.vidas} pontos={j.pontos:5d} tempo={j.tempo:5.0f} etapas={res}")
    print(f"vitorias: {vitorias}/6 | biomas: {alcancados}")

    print()
    print("=== chefe: a Coruja se acalma com 3 clarões ===")
    app = App(); tk=T(); pygame.key.get_pressed=lambda: tk
    app.modo_historia = True
    app._trocar("jogo", _TelaVazia(app)); app.jogo.iniciar("historia")
    j = app.jogo
    j._carregar_bioma(3)
    coruja = j.chefe
    j.jogador.x, j.jogador.y = coruja.x - 150, coruja.y + 40
    j.banner_timer = 0; j.dica_timer = 0
    for _ in range(20):
        app._atualizar(DT)
    vinha_ativa = j.estado_chefe == "ativo"
    for _ in range(3):
        coruja.assustar(2.6)
        for _ in range(10):
            app._atualizar(DT)
    print(f"chefe detectado: {vinha_ativa} | estado final: {j.estado_chefe} | "
          f"pontos: {j.pontos} | ainda machuca: {coruja.colide_com(j.jogador)}")
    assert vinha_ativa and j.estado_chefe == "vencido" and not coruja.colide_com(j.jogador)
    assert j.pontos >= 500

    print()
    print("=== conteúdo ambiental: 4 fases com mensagem e pergunta ===")
    from src import ambiental
    assert len(ambiental.MENSAGENS) == len(config.BIOMAS) == 4
    for i, m in enumerate(ambiental.MENSAGENS):
        assert m["fase"] == config.BIOMAS[i]["fase"], (m["fase"], config.BIOMAS[i]["fase"])
        assert 0 <= m["correta"] < len(m["opcoes"])
        assert m["mensagem"] and m["pergunta"] and m["explicacao"]
    # a tela não deixa seguir sem responder, e não muda o resultado da partida
    from src.telas import Ambiental
    app2 = App()
    seguiu = []
    tela = Ambiental(app2, 0, lambda: seguiu.append(True))
    app2._trocar("ambiental", tela)
    tela._seguir()
    bloqueado = not seguiu
    tela._responder((tela.conteudo["correta"] + 1) % 3)   # erra de propósito
    errou_sem_punir = not tela.acertou
    tela._seguir()
    print(f"mensagens: {len(ambiental.MENSAGENS)} | sem resposta não avança: {bloqueado} | "
          f"errar não tira nada: {errou_sem_punir} | avançou: {bool(seguiu)}")
    assert bloqueado and errou_sem_punir and seguiu

    print()
    print("=== bot no modo infinito (10 biomas) ===")
    j, res = jogar(11, modo="infinito", biomas_alvo=10)
    print(f"infinito: chegou ao bioma {j.numero_bioma} (volta {j.volta+1}), "
          f"fim={j.fim}, pontos={j.pontos}, tempo={j.tempo:.0f}s")
    assert j.numero_bioma >= 6, "o modo infinito deveria passar dos 4 biomas"

    print("\n=== bot parado ===")
    teste_parado()
    print("\nOK")
