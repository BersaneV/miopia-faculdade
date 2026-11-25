"""Entrada de Miopia. A simulação só avança na tela de jogo, fora de conversas."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import sys
if __package__ in ("",None):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY","1")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1")
import pygame
from src import telas, ambiental
from src.audio import Audio
from src.ensaios import ENSAIOS, preparar_ensaio
from src.ilustracao import fonte, original, tinta
from src.memoria import Memoria
from src.paisagem import Paisagem, hud
from src.roteiro import PROLOGO
from src.travessia import Comando, Jornada

ACEITAR = (pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE)
CORES_AUDIO = ("bosque","corrego","taquaral","gruta")

class App:
    pausa_nomes=["Continuar","Diário","Ajustes","Reiniciar no marco","Salvar e voltar ao menu"]
    def __init__(self, temporaria=False):
        pygame.mixer.pre_init(44100,-16,2,512)
        pygame.init()
        fonte.cache_clear()
        tinta.cache_clear()
        self.cheia=False
        self.tela=self.janela()
        pygame.display.set_caption("Miopia · A última luz da mata")
        pygame.display.set_icon(original("lume_4.png"))
        self.mem=Memoria(temporaria)
        self.audio=Audio()
        self.ajustar_som()
        self.credito_audio=("Vento, água, taquaras e ecos sintetizados para Miopia. As cinco criaturas têm avisos próprios, posicionados em estéreo conforme a distância e o lado de Lume.")
        self.paisagem=Paisagem()
        self.paisagem.brilho_mata=self.mem.prefs["brilho"]
        self.morte_desde=0.
        self.impacto_restante=0.
        self.ensaio=None
        self.rodando=True
        self.relogio=0.
        self.jogo=None
        self.selecao=0
        self.estado="menu"
        self.alvos=[]
        self.bordas=set()
        self.anterior="menu"
        self.pagina=0
        self.quadro=0
        self.fala=""
        self.letras=0
        self.espera=0.
        self.passo_som=0.
        self.ultimo_save=None
        self.proximo_save=0.
        self.mem_camp=self.mem.ler("campanha")
        self.conf_acao=self.conf_msg=self.conf_titulo=self.confirmacao=""
        self.registro_etapa=0
        self.resposta=None
        self.musica("menu")

    def janela(self):
        flags=pygame.SCALED | (pygame.FULLSCREEN if self.cheia else pygame.RESIZABLE)
        try:
            return pygame.display.set_mode((960,540),flags)
        except pygame.error:
            return pygame.display.set_mode((960,540))

    def musica(self,cena):
        self.audio.tocar_musica(cena)

    def ajustar_som(self):
        self.audio.volume_musica=self.mem.prefs["musica"]
        self.audio.volume_efeitos=self.mem.prefs["efeitos"]
        self.audio.mudo=self.mem.prefs["mudo"]
        self.audio.aplicar_volumes()

    def som(self,nome):
        self.audio.tocar(nome)

    def mudar(self,nome):
        self.estado=nome
        self.impacto_restante=0.
        self.selecao=0
        self.alvos=[]
        self.bordas.clear()

    def menu(self):
        self.salvar_campanha()
        self.jogo=None
        self.ensaio=None
        self.mem_camp=self.mem.ler("campanha")
        self.mudar("menu")
        self.musica("menu")

    def menu_nomes(self):
        itens=["Continuar história","Nova história"] if self.mem_camp else ["Jogar história"]
        return itens+["Modo infinito","Campo de testes","Como jogar","Ajustes","Recordes","Créditos","Sair"]

    def fim_nomes(self):
        j=self.jogo
        if j.estado=="derrota":
            return [("Retomar do marco" if j.modo=="historia" else "Tentar outra noite"),"Voltar ao menu"]
        return ["Voltar ao menu"]

    def salvar_campanha(self,forcar=True):
        j=self.jogo
        if self.ensaio is not None or not j or j.modo!="historia" or j.estado not in ("jogando","caido"): return
        assinatura=(j.etapa,j.pontuacao,j.lume.vidas,j.checkpoint,len(j.diario),
                    tuple(sorted(j.flags)),j.bolsa.revisao,j.em_vertical,j.marco_vertical,frozenset(j.cartografia))
        if forcar or self.relogio>=self.proximo_save and assinatura!=self.ultimo_save:
            self.mem_camp=j.salvar()
            self.mem.guardar("campanha",self.mem_camp)
            self.ultimo_save=assinatura
            self.proximo_save=self.relogio+.65

    def iniciar(self,modo,continuar=False):
        self.ensaio=None
        if continuar:
            try: self.jogo=Jornada.carregar(self.mem_camp)
            except (ValueError,KeyError,TypeError,AttributeError,OverflowError):
                self.mem.aviso="O marco salvo está ilegível. Comece uma nova história."
                self.mem_camp=None
                self.mudar("menu")
                return
        else:
            self.jogo=Jornada(modo,self.mem.prefs["dificuldade"])
        self.ultimo_save=None
        self.salvar_campanha()
        if modo=="historia" and not continuar:
            self.quadro=0
            self.mudar("prologo")
            self.nova_fala(PROLOGO[0][1])
            self.musica("historia")
        else:
            self.jogar()

    def jogar(self):
        self.mudar("jogo")
        self.musica(CORES_AUDIO[self.jogo.etapa])

    def nova_fala(self,msg):
        self.fala=msg
        self.letras=0
        self.espera=.02

    @property
    def fala_visivel(self):
        return self.fala[:self.letras]

    def escrever(self,dt):
        self.espera-=dt
        while self.espera<=0 and self.letras<len(self.fala):
            ch=self.fala[self.letras]
            self.letras+=1
            self.espera+=.17 if ch in ".!?…" else (.09 if ch in ",;" else .021)

    def avancar_fala(self):
        if self.letras<len(self.fala):
            self.letras=len(self.fala)
            return
        if self.estado=="prologo":
            self.quadro+=1
            if self.quadro==len(PROLOGO): self.jogar()
            else: self.nova_fala(PROLOGO[self.quadro][1])
        else:
            self.jogo.fechar_dialogo()
            self.bordas.clear()

    def confirmar(self,motivo,titulo,msg,acao):
        self.confirmacao=motivo
        self.conf_titulo,self.conf_msg,self.conf_acao=titulo,msg,acao
        self.mudar("confirmar")

    def ajustar(self,delta):
        if self.selecao==5:
            self.mudar(self.anterior)
            return
        p=self.mem.prefs
        if self.selecao==0:
            niveis=("fácil","normal","difícil")
            p["dificuldade"]=niveis[(niveis.index(p["dificuldade"])+delta)%3]
        elif self.selecao in (1,2):
            k=("musica","efeitos")[self.selecao-1]
            p[k]=max(0,min(1,round(p[k]+delta*.1,2)))
        elif self.selecao==3:
            p["brilho"]=(p["brilho"]+delta)%4
            self.paisagem.brilho_mata=p["brilho"]
        else: p["mudo"]=not p["mudo"]
        self.ajustar_som()
        self.mem.guardar("preferencias",p)
        self.som("clique")

    def ativar(self):
        estado=self.estado
        i=self.selecao
        self.som("clique")
        if estado=="menu":
            nome=self.menu_nomes()[i]
            if nome=="Jogar história": self.iniciar("historia")
            elif nome=="Nova história":
                self.confirmar("nova","Começar outra história?","O novo percurso ocupará o marco salvo desta campanha.","Começar de novo")
            elif nome=="Continuar história": self.iniciar("historia",True)
            elif nome=="Modo infinito": self.iniciar("infinito")
            elif nome=="Sair": self.rodando=False
            elif nome=="Campo de testes": self.mudar("ensaios")
            else:
                self.anterior="menu"
                if nome=="Créditos": self.musica("creditos")
                self.mudar({"Como jogar":"ajuda","Ajustes":"ajustes","Recordes":"recordes","Créditos":"creditos"}[nome])
        elif estado=="ensaios":
            if i==len(ENSAIOS):
                self.menu()
                return
            self.ensaio=i
            self.jogo=preparar_ensaio(i,self.mem.prefs["dificuldade"])
            self.jogar()
        elif estado=="pausa":
            if i==0: self.jogar()
            elif i==1: self.abrir_diario("pausa")
            elif i==2:
                self.anterior="pausa"
                self.mudar("ajustes")
            elif i==3: self.perguntar_reinicio()
            elif self.ensaio is not None:
                self.jogo=None
                self.ensaio=None
                self.mudar("ensaios")
                self.musica("menu")
            else: self.menu()
        elif estado=="morte":
            if self.relogio-self.morte_desde < .35:
                return
            if i==0:
                if self.ensaio is not None:
                    self.jogo=preparar_ensaio(self.ensaio,self.mem.prefs["dificuldade"])
                    self.jogar()
                elif self.jogo.estado=="derrota" and self.jogo.modo=="infinito":
                    self.iniciar("infinito")
                else:
                    if self.jogo.estado=="derrota":
                        self.jogo.lume.vidas=self.jogo.vidas_iniciais
                        self.jogo.estado="caido"
                    self.jogo.reiniciar()
                    self.salvar_campanha()
                    self.jogar()
            else:
                self.menu()
        elif estado=="confirmar":
            if i==0: self.mudar("menu" if self.confirmacao=="nova" else "pausa")
            elif self.confirmacao=="nova": self.iniciar("historia")
            else:
                self.jogo.reiniciar()
                self.jogar()
        elif estado=="ajustes": self.ajustar(1)
        elif estado=="fim":
            if i==0 and self.jogo.estado=="derrota":
                self.iniciar(self.jogo.modo,self.jogo.modo=="historia" and bool(self.mem_camp))
            else: self.menu()
        elif estado=="registro":
            if self.resposta is None: self.resposta=i
            else: self.jogar()
        elif estado=="capitulo": self.jogar()
        elif estado in ("ajuda","creditos","recordes"): self.menu()

    def perguntar_reinicio(self):
        self.confirmar("marco","Voltar ao marco?","Lume recupera a luz. As portas abertas, as gotas e os registros continuam na jornada.","Voltar ao marco")

    def abrir_diario(self,origem):
        self.anterior=origem
        self.pagina=2 if self.jogo.em_vertical else 0
        self.mudar("diario")
        self.som("pagina")

    def evento(self,e):
        if e.type==pygame.QUIT:
            self.rodando=False
            return
        if e.type==pygame.WINDOWFOCUSLOST and self.estado=="jogo" and not self.jogo.dialogo:
            self.mudar("pausa")
            return
        if e.type in (pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN):
            if e.type==pygame.MOUSEBUTTONDOWN and e.button!=1: return
            for i,r in enumerate(self.alvos):
                if r.collidepoint(e.pos):
                    self.selecao=i
                    if e.type==pygame.MOUSEBUTTONDOWN: self.ativar()
                    return
            if e.type==pygame.MOUSEBUTTONDOWN:
                if self.estado=="prologo" or (self.estado=="jogo" and self.jogo.dialogo): self.avancar_fala()
                elif self.estado in ("capitulo","ajuda","creditos","recordes") or self.estado=="registro" and self.resposta is not None:
                    self.ativar()
            return
        if e.type!=pygame.KEYDOWN or getattr(e,"repeat",False): return
        k=e.key
        if k==pygame.K_F11:
            self.cheia=not self.cheia
            self.tela=self.janela()
            return
        if k==pygame.K_m:
            self.mem.prefs["mudo"]=not self.mem.prefs["mudo"]
            self.ajustar_som()
            self.mem.guardar("preferencias",self.mem.prefs)
            return
        est=self.estado
        if est=="prologo":
            if k==pygame.K_ESCAPE: self.jogar()
            elif k in ACEITAR: self.avancar_fala()
        elif est=="jogo":
            if self.jogo.dialogo:
                if k in (*ACEITAR,pygame.K_e,pygame.K_ESCAPE): self.avancar_fala()
            elif k in (pygame.K_ESCAPE,pygame.K_p): self.mudar("pausa")
            elif k==pygame.K_TAB: self.abrir_diario("jogo")
            elif k==pygame.K_q:
                self.jogo.trocar_item()
                self.som("pagina")
            elif k==pygame.K_f:
                self.som(self.jogo.usar_item() or "navegar")
            else: self.bordas.add(k)
        elif est=="diario":
            if k in (pygame.K_ESCAPE,pygame.K_TAB): self.mudar(self.anterior)
            elif k in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_a,pygame.K_d):
                self.pagina=(self.pagina+(-1 if k in (pygame.K_LEFT,pygame.K_a) else 1))%(len(self.jogo.diario)+2+bool(self.jogo.cartografia))
                self.som("pagina")
        elif est=="pausa" and k in (pygame.K_ESCAPE,pygame.K_p): self.jogar()
        elif est=="pausa" and k==pygame.K_r: self.perguntar_reinicio()
        elif k==pygame.K_ESCAPE:
            if est in ("registro","capitulo"): self.jogar()
            elif est=="ajustes": self.mudar(self.anterior)
            elif est=="confirmar": self.mudar("menu" if self.confirmacao=="nova" else "pausa")
            elif est=="morte": return
            elif est=="menu": self.rodando=False
            else: self.menu()
        elif est=="ajustes" and k in (pygame.K_LEFT,pygame.K_RIGHT): self.ajustar(1 if k==pygame.K_RIGHT else -1)
        elif k in ACEITAR: self.ativar()
        elif k in (pygame.K_UP,pygame.K_DOWN,pygame.K_w,pygame.K_s):
            quant={"menu":len(self.menu_nomes()),"pausa":5,"ajustes":6,"confirmar":2,"morte":2,"ensaios":len(ENSAIOS)+1,
                   "fim":len(self.fim_nomes()) if est=="fim" else 0,"registro":3}.get(est,0)
            if quant:
                self.selecao=(self.selecao+(-1 if k in (pygame.K_UP,pygame.K_w) else 1))%quant
                self.som("navegar")

    def atualizar(self,dt,presso=None):
        self.relogio+=dt
        if self.estado=="prologo" or self.estado=="jogo" and self.jogo.dialogo:
            self.escrever(dt)
        if self.estado=="jogo" and self.impacto_restante>0:
            # A fila de KEYDOWN permanece intacta durante o breve impacto.
            self.impacto_restante=max(0.,self.impacto_restante-dt)
            self.mix(dt)
            return
        if self.estado=="jogo" and not self.jogo.dialogo:
            teclas=pygame.key.get_pressed() if presso is None else presso
            mover=int(bool(teclas[pygame.K_RIGHT] or teclas[pygame.K_d]))-int(bool(teclas[pygame.K_LEFT] or teclas[pygame.K_a]))
            shift=(pygame.K_LSHIFT,pygame.K_RSHIFT)
            direcoes=(pygame.K_LEFT,pygame.K_RIGHT,pygame.K_a,pygame.K_d)
            pedir_deslize=bool(self.bordas.intersection(shift)) or (
                any(teclas[k] for k in shift) and bool(self.bordas.intersection(direcoes)))
            cmd=Comando(mover,teclas[pygame.K_s] or teclas[pygame.K_DOWN],pygame.K_SPACE in self.bordas,
                        teclas[pygame.K_SPACE],pedir_deslize,
                        pygame.K_j in self.bordas,pygame.K_k in self.bordas,pygame.K_e in self.bordas)
            self.bordas.clear()
            j=self.jogo
            etapa,raizes=j.etapa,j.restauradas
            j.update(dt,cmd)
            if "acerto" in j.eventos or "abatido" in j.eventos or "rebote" in j.eventos:
                self.impacto_restante=.045
            for ev in dict.fromkeys(j.eventos): self.som(ev)
            for nome,x in j.sons_espaciais:
                self.audio.tocar_local(nome,x,j.lume.rect.centerx)
            if j.boss and "aviso" in j.eventos:
                self.audio.tocar_local(("asa_perto","patas_perto","casco_perto","asa_perto")[j.etapa],
                                       j.boss.x,j.lume.rect.centerx)
            self.passo_som-=dt
            if j.lume.pose in ("andar","correr") and self.passo_som<=0:
                self.som("passo")
                self.passo_som=.34
            if j.dialogo: self.nova_fala(j.dialogo[1])
            if j.estado in ("caido","derrota") and j.motivo_morte:
                self.morte_desde=self.relogio
                if j.estado=="derrota" and self.ensaio is None:
                    self.mem.terminar(j)
                    if j.modo=="historia":
                        self.mem_camp=j.salvar()
                        self.mem_camp["vidas"]=j.vidas_iniciais
                        self.mem.guardar("campanha",self.mem_camp)
                else: self.salvar_campanha()
                self.mudar("morte")
                self.musica("derrota")
            elif j.estado!="jogando":
                if self.ensaio is None:
                    self.mem.terminar(j)
                self.mudar("fim")
                self.musica(j.estado)
            elif raizes<j.restauradas and j.modo=="historia":
                self.registro_etapa=j.etapa
                m=ambiental.MENSAGENS[j.etapa]
                j.memorizar(m["fase"],m["mensagem"])
                self.resposta=None
                self.mudar("registro")
                self.salvar_campanha()
            elif j.etapa!=etapa:
                self.musica(CORES_AUDIO[j.etapa])
                if j.modo=="historia": self.mudar("capitulo")
                self.salvar_campanha()
            else: self.salvar_campanha(False)
        self.mix(dt)

    def mix(self,dt):
        j=self.jogo
        ativo=self.estado=="jogo" and j and not j.dialogo
        self.audio.ambiente(combate=bool(ativo and j.combate),
                           energia=j.lume.energia if ativo else 100,
                           raizes=j.restauradas if j else 0,suspenso=not ativo)
        self.audio.atualizar(dt)

    def desenhar(self):
        s=self.tela
        if self.estado in ("jogo","pausa","morte"):
            j=self.jogo
            self.paisagem.desenhar(s,j,j.tempo)
            if self.estado=="morte":
                telas.morte(self,s)
                return
            hud(s,j)
            if j.dialogo: telas.dialogo(self,s)
            if self.estado=="pausa": telas.pausa(self,s)
            return
        renderer={"menu":telas.menu,"prologo":telas.cena,"ajuda":telas.ajuda,"creditos":telas.creditos,
                  "ensaios":telas.ensaios,"confirmar":telas.confirmar,"ajustes":telas.opcoes_ajustes,"capitulo":telas.capitulo,
                  "registro":telas.registro,"fim":telas.fim,"recordes":telas.recordes,"diario":telas.diario}
        renderer[self.estado](self,s)

    def rodar(self):
        clock=pygame.time.Clock()
        try:
            while self.rodando:
                dt=min(.07,clock.tick(60)/1000)
                for e in pygame.event.get(): self.evento(e)
                if not self.rodando: break
                self.atualizar(dt)
                self.desenhar()
                pygame.display.flip()
        finally:
            self.salvar_campanha()
            self.mem.db.close()
            pygame.quit()

def principal():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true",help="Verifica menu, início e desenho do jogo e encerra.")
    parser.add_argument("--captura",type=Path)
    args=parser.parse_args()
    app=App(temporaria=args.smoke)
    if not args.smoke:
        app.rodar()
        return
    app.desenhar()
    app.iniciar("historia")
    app.jogar()
    for n in range(15):
        app.atualizar(1/60)
        app.desenhar()
        pygame.display.flip()
    if args.captura: pygame.image.save(app.tela,str(args.captura))
    print("Miopia OK · menu, recursos e Bosque em 960 × 540")
    app.mem.db.close()
    pygame.quit()

if __name__=="__main__":
    principal()
