"""Repertórios de combate com compromisso por golpe, memória e manobras físicas.

Vinte sequências por espécie combinam cinco famílias de ataque. A escolha
pondera contexto; cada golpe seguinte precisa perceber e avisar novamente.
"""
from dataclasses import dataclass
import math
import pygame
from .combate import Inimigo, Vetor, direcao, segmento_bloqueado, AEREOS


FAMILIAS={
    "morcego":("mergulho","rasante","eco","rasante_baixo","queda"),
    "aranha":("salto","fio","leque_fio","mordida","pique"),
    "sombra":("fenda","rasteira","orbe","fenda_dupla","pique"),
    "vespa":("mergulho","ferrao","leque_ferrao","rasante","queda"),
    "carabideo":("carga","onda","onda_dupla","varredura","salto"),
    "cobra":("rasteira","salto","veneno","mordida","pique"),
}


@dataclass(frozen=True)
class Combo:
    nome: str
    passos: tuple


RECEITAS=(
    Combo("Aproximação",(0,)), Combo("Controle de espaço",(1,)),
    Combo("Dispersão",(2,)), Combo("Ataque rente",(3,)), Combo("Ataque de cima",(4,)),
    Combo("Duas entradas",(0,0)), Combo("Duas pressões",(1,1)),
    Combo("Entrar e afastar",(0,"recuar",1)), Combo("Atrair e entrar",(1,"recuar",0)),
    Combo("Cobertura e avanço",(2,0)), Combo("Rente e distância",(3,1)),
    Combo("Recuo coberto",("recuar",2)), Combo("Entrada pelo flanco",("flanco",0)),
    Combo("Pressão pelo flanco",("flanco",1)), Combo("Cruzar e responder",(0,"flanco",1)),
    Combo("Atrair e cruzar",(1,"flanco",0)), Combo("Alto e dispersão",(4,2)),
    Combo("Três alturas",(3,4,1)), Combo("Entrada e queda",(0,"recuar",4)),
    Combo("Pinça",(2,"flanco",3)),
)


class Habitante(Inimigo):
    def __init__(self, tipo, x, y, dificuldade="normal", *, semente=None, ouve_pousos=False):
        self.ouve_pousos = ouve_pousos
        super().__init__(tipo, x, y, dificuldade, semente=semente)

    def repor(self):
        super().repor()
        self.alvo_escuta = None
        self.plano=[]
        self.combo_id=-1
        self.memoria_combos=[]
        self.acao_atual=""
        self.familia_atual=0
        self.companhia=None
        self.grupo=None;self.papel='';self.colegas=[];self.cego=0.
        self.ataque_iluminado = False
        self.pos_manobra=Vetor(self.rect.center)

    def viavel(self,indice,lume,terrenos):
        dx=abs(lume.rect.centerx-self.rect.centerx)
        if dx>330 or segmento_bloqueado(self.rect.center,lume.rect.center,terrenos):return False
        acao=FAMILIAS[self.tipo][indice]
        if self.carabideo_com_alvo_acima(lume):
            return acao == "salto" and self.salto_alto_viavel(lume, terrenos)
        if acao in ("salto","pique"):
            return dx<=155 and abs(lume.rect.centery-self.rect.centery)<85 and self.salto_livre(self.alvo_observado(lume),terrenos)
        if acao in ("mordida","varredura","rasteira"):return dx<160
        if acao in ("fio","ferrao","eco","orbe","veneno","leque_fio","leque_ferrao"):return 50<dx<310
        if acao in ("onda","onda_dupla"):return abs(lume.rect.bottom-self.rect.bottom)<90
        return True

    def pesos_combos(self,lume,terrenos):
        d=abs(lume.rect.centerx-self.rect.centerx)
        centros=(100,185,210,85,115)
        pesos=[]
        for ident,combo in enumerate(RECEITAS):
            primeira=next(p for p in combo.passos if isinstance(p,int))
            if not self.viavel(primeira,lume,terrenos):pesos.append(0.);continue
            afinidade=math.exp(-.5*((d-centros[primeira])/110)**2)
            movimento=1.35 if "flanco" in combo.passos and (abs(lume.vx)>70 or self.companhia is not None) else 1.
            memoria=.18 if self.memoria_combos and ident==self.memoria_combos[-1] else .55 if ident in self.memoria_combos else 1.
            pressao=1.15 if len(combo.passos)>1 and lume.vida<50 else 1.
            papel=3.4 if self.papel=='flanco' and 'flanco' in combo.passos else 2.8 if self.papel=='cobertura' and primeira in (1,2) else 1.
            pesos.append(afinidade*movimento*memoria*pressao*papel)
        return pesos

    def escolher_combo(self,lume,terrenos):
        pesos=self.pesos_combos(lume,terrenos)
        total=sum(pesos)
        if total<=0:return -1
        sorteio=self.sorte.random()*total
        for ident,peso in enumerate(pesos):
            sorteio-=peso
            if peso>0 and sorteio<0:return ident
        return max(i for i,p in enumerate(pesos) if p>0)

    @property
    def duracao_aviso(self):
        return max(.36, self.ficha.aviso/self.ritmo*.88)

    def vaga_de_ataque(self):
        ativos = [e for e in self.colegas if e is not self and e.ativo and e.estado in ("aviso", "investida")]
        if len(ativos) != 1:
            return not ativos
        outro = ativos[0]
        return (self.ataque_iluminado and outro.ataque_iluminado
                and (outro.estado != "aviso" or outro.t <= outro.duracao_aviso-.18))

    def preparar(self,lume,terrenos=()):
        if self.cego>0:self.t=.12;return ''
        if not self.plano:
            self.combo_id=self.escolher_combo(lume,terrenos)
            if self.combo_id<0:self.t=.18;return ""
            self.memoria_combos=(self.memoria_combos+[self.combo_id])[-3:]
            self.plano=list(RECEITAS[self.combo_id].passos)
        passo=self.plano[0]
        if isinstance(passo,str):
            self.plano.pop(0)
            lado=1 if lume.rect.centerx>=self.rect.centerx else -1
            alvo=lume.rect.centerx+lado*90 if passo=="flanco" else self.rect.centerx-lado*115
            self.pos_manobra=Vetor(max(25,self.origem[0]-280,min(self.origem[0]+280,alvo)),self.origem[1]-self.rect.h/2)
            self.estado="manobra";self.acao_atual=passo;self.t=.62
            return "patas_perto" if self.tipo=="aranha" else self.ficha.som
        if not self.viavel(passo,lume,terrenos):
            self.plano=[];self.t=.18;return ""
        if self.grupo and not self.vaga_de_ataque():
            self.t = .12
            return ""
        self.plano.pop(0)
        self.familia_atual=passo
        acao=FAMILIAS[self.tipo][passo];self.acao_atual=acao
        self.tecnica={"eco":"eco","orbe":"eco","veneno":"ferrao","leque_fio":"fio","leque_ferrao":"ferrao",
            "onda_dupla":"onda","mordida":"rasteira","varredura":"rasteira",
            "fenda_dupla":"fenda","pique":"salto","queda":"mergulho","rasante_baixo":"rasante"}.get(acao,acao)
        if acao == "salto" and self.carabideo_com_alvo_acima(lume):
            self.tecnica = "salto_alto"
        self.sequencia+=1
        self.frente=1 if lume.rect.centerx>=self.rect.centerx else -1
        self.alvo=self.alvo_observado(lume);self.inicio=Vetor(self.rect.center)
        self.destino_recuo=Vetor(self.rect.centerx-self.frente*45,self.origem[1]-self.rect.h/2)
        if self.tecnica=="rasante":self.alvo.y=lume.rect.bottom-(9 if acao=="rasante_baixo" else 42)
        if self.tecnica=="fenda":self.alvo.y=self.origem[1]
        self.estado="aviso"
        self.t = self.duracao_aviso
        return f'aviso_{self.tipo}_{passo}'

    def lancar(self):
        if self.tecnica=="eco":
            self.estado="investida";self.inicio=Vetor(self.rect.center)
            self.disparar("eco",self.inicio,direcao(self.inicio,self.alvo)*280*self.ritmo,1.5)
            self.duracao=self.t=.22
            return
        super().lancar()
        if self.acao_atual=="veneno":self.projeteis[-1].tipo="veneno"
        if self.acao_atual.startswith("leque_"):
            proj=self.projeteis[-1]
            for angulo in (-22,22):self.disparar(proj.tipo,proj.pos,proj.vel.rotate(angulo),1.45)
        elif self.acao_atual=="onda_dupla":
            self.disparar("onda",(self.rect.centerx-18*self.frente,self.rect.bottom-9),(-242*self.frente*self.ritmo,0),1.25)
        if self.tecnica in ("mergulho","rasante","carga","rasteira"):
            self.vetor*=1.18
            if self.acao_atual in ("mordida","varredura"):self.duracao=self.t=.24

    def executar_ataque(self,dt,lume,terrenos):
        if self.acao_atual=="fenda_dupla":
            contato=any(pygame.FRect(self.alvo.x+dx-20,self.alvo.y-39,40,39).colliderect(lume.rect) for dx in (-48,48))
            if contato or self.t<=0:self.estado,self.t="recuo",.34
            return contato
        return super().executar_ataque(dt,lume,terrenos)

    def ouvir_pouso(self, posicao):
        """Fixa uma pista no chão. Outro ruído não redireciona a busca atual."""
        if not self.ouve_pousos or self.estado != "patrulha":
            return False
        x, piso = posicao
        if abs(piso - self.origem[1]) > 24 or abs(x - self.rect.centerx) > 300:
            return False
        self.alvo_escuta = x
        self.plano.clear()
        self.chamada = 2.6
        self.estado, self.t = "investigar", 2.4
        return True

    def alcance(self, lume, raio, restaurado):
        if self.ouve_pousos:
            return min(154., 86. + .28 * raio)
        return super().alcance(lume, raio, restaurado)

    def encerrar_busca(self):
        self.alvo_escuta = None
        self.estado, self.t = "patrulha", .14

    def update(self,dt,lume,raio,restaurado,terrenos):
        if self.estado == "investigar":
            centro = self.rect.center
            if (self.cego <= 0 and math.dist(centro, lume.rect.center) < self.alcance(lume, raio, restaurado)
                    and not segmento_bloqueado(centro, lume.rect.center, terrenos)):
                self.encerrar_busca()
            else:
                velocidade = 145 * (.6 if self.lentidao > 0 else 1)
                sons, dano = super().update(dt, lume, raio, restaurado, terrenos)
                destino = (self.alvo_escuta, self.origem[1]-self.rect.h/2)
                if abs(destino[0] - self.rect.centerx) > 5:
                    self.frente = 1 if destino[0] > self.rect.centerx else -1
                    self.seguir(destino, velocidade, dt, terrenos)
                else:
                    self.t = min(self.t, .44)
                if self.t <= 0:
                    self.encerrar_busca()
                return sons, dano
        if self.estado=="manobra":
            self.cego=max(0.,self.cego-dt)
            self.relogio+=dt;self.t-=dt
            self.flash=max(0,self.flash-dt);self.lentidao=max(0,self.lentidao-dt)
            self.seguir(self.pos_manobra,305*(.6 if self.lentidao>0 else 1),dt,terrenos)
            if self.t<=0 or self.pos_manobra.distance_to(self.rect.center)<8:
                self.estado,self.t="patrulha",.08
            return [],False
        if self.estado=="aviso" and self.acao_atual=="queda":
            dy=max(-240*dt,min(240*dt,self.alvo.y-115-self.rect.centery))
            self.mover(0,dy,terrenos)
        antes=self.estado
        sons,dano=super().update(dt,lume,raio,restaurado,terrenos)
        if antes=="investida" and self.estado=="recuo":self.t=.34
        if abs(lume.rect.centerx-self.rect.centerx)>400:self.plano=[]
        return sons,dano

    def patrulhar(self,lume,distancia,dt,terrenos):
        if self.grupo and distancia<600 and abs(lume.rect.centery-self.rect.centery)<180:
            lado=1 if self.rect.centerx>=lume.rect.centerx else -1
            deslocamento=-lado*85 if self.papel=='flanco' else lado*(170 if self.papel=='cobertura' else 75)
            destino=Vetor(lume.rect.centerx+deslocamento,self.origem[1]-self.rect.h/2)
            self.seguir(destino,195,dt,terrenos)
        else:
            # A aranha do Córrego mantém a ronda até ouvir ou avistar Lume.
            super().patrulhar(lume, math.inf if self.ouve_pousos else distancia, dt, terrenos)

    def acertar(self,arma,area,clarao,lume):
        antes,tempo=self.estado,self.t
        resultado=super().acertar(arma,area,clarao,lume)
        if antes == "investigar" and (self.estado != antes or not self.ativo):
            self.alvo_escuta = None
        if resultado=="acerto" and self.ativo:
            if self.grupo and self.grupo != "ninhada" and antes == "aviso" and arma.luminoso and not clarao:
                self.estado, self.t = "atordoado", .32
                self.plano.clear()
                return resultado
            if self.grupo and antes in ('aviso','investida'):
                self.estado,self.t=antes,tempo
                return resultado
            if not clarao and arma.tipo in ("corte1","corte2") and antes in ("aviso","investida"):
                self.estado,self.t=antes,tempo
            elif self.estado=="atordoado":self.plano=[]
        return resultado
