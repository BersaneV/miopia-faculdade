"""Simulação do caminho de Lume. Coordenadas e colisões ficam no espaço do mundo."""
from __future__ import annotations

from dataclasses import dataclass
import math
import pygame
from .visao import DURACAO, Vestigio
from .combate import Arma, Inimigo
from .taticas import Habitante
from .fases import VIGIA_X, TRANCA_X
from .fases import (ARENA, CHAO, FIM_ARENA, FALAS, FASES, MEIO, RAIZ, SAIDA,
                    RAMAIS, Objeto, Terreno, montar_infinito, terrenos)


from . import narrativa, corte_vertical, subsolo


@dataclass(frozen=True)
class Comando:
    mover: int = 0
    baixo: bool = False
    salto: bool = False
    segurar_salto: bool = False
    deslize: bool = False
    golpe: bool = False
    clarao: bool = False
    interagir: bool = False


def aproximar(valor, alvo, passo):
    return valor + max(-passo, min(alvo - valor, passo))


class Lume:
    ALTURA = 42
    BAIXO = 20
    # Compatibilidade com ferramentas que inspecionam esta reserva. A asa agora
    # sustenta a queda enquanto Espaço estiver pressionado, sem cronômetro.
    PLANEIO = 1.

    def __init__(self, x, y, vidas=3):
        self.rect = pygame.FRect(0, 0, 24, self.ALTURA)
        self.rect.midbottom = x, y
        self.vx = self.vy = 0.
        self.face = 1
        self.chao = True
        self.coyote = self.buffer = self.slide = self.slide_cd = 0.
        self.golpe = self.golpe_cd = self.pulso = self.pulso_cd = 0.
        self.iframes = self.impacto = self.planeio = 0.
        self.energia = 100.
        self.vidas = vidas
        self.em_corda = False
        self.bateu = False
        self.na_parede = self.planando = self.impulso_parede = False
        self.ultimo_impulso = self.lado_parede = 0
        self.trava_lateral = self.graca_parede = 0.
        self.ignorar_topo = None
        self.planeio = self.PLANEIO
        self.asa_disponivel = False
        self.batida_asa = 0.
        self.arma = Arma()
        self.bonus_dano = self.bonus_velocidade = 1.

    @property
    def pose(self):
        if self.impacto > 0: return "dano"
        if self.em_corda: return "corda"
        if self.pulso > 0: return "clarao"
        if self.golpe > 0: return "golpe"
        if self.slide > 0: return "deslize"
        if self.rect.height < self.ALTURA: return "agachar"
        if self.planando: return "planar"
        if not self.chao and self.na_parede and self.vy>=0: return "parede"
        if not self.chao: return "pulo" if self.vy < 0 else "queda"
        if abs(self.vx) > 196: return "correr"
        return "andar" if abs(self.vx) > 10 else "parado"

    def altura(self, baixo, solidos):
        altura = self.BAIXO if baixo else self.ALTURA
        if self.rect.height == altura:
            return
        novo = self.rect.copy()
        novo.height = altura
        novo.bottom = self.rect.bottom
        if baixo or not any(not t.atravessavel and novo.colliderect(t.rect) for t in solidos):
            self.rect = novo

    def movimento(self, dt, cmd, solidos, corrente, asas):
        self.bateu = self.planando = self.impulso_parede = False
        saltou = False
        for timer in ("buffer", "slide", "slide_cd", "golpe", "golpe_cd", "pulso",
                      "pulso_cd", "iframes", "impacto", "trava_lateral", "graca_parede", "batida_asa"):
            setattr(self, timer, max(0., getattr(self, timer) - dt))
        if self.chao:
            self.asa_disponivel = True
        self.coyote = .105 if self.chao else max(0., self.coyote - dt)
        self.altura(cmd.baixo or self.slide > 0, solidos)
        r = self.rect

        # O pé identifica a peça que de fato sustenta a personagem. Solos e
        # pontes continuam bloqueando para baixo mesmo encostados numa grade.
        apoio = [t for t in solidos if r.right > t.rect.left and r.left < t.rect.right
                 and abs(r.bottom - t.rect.top) < 1.2]
        desceu = (cmd.baixo and cmd.salto and self.chao and apoio
                  and all(t.descida for t in apoio))
        if desceu:
            self.ignorar_topo = r.bottom
            self.buffer = self.coyote = self.slide = 0.
            self.chao = False
            self.vy = max(125., self.vy)
            r.y += 2
        elif cmd.salto and not cmd.baixo:
            self.buffer = .125

        contato = 0
        if not self.chao:
            for t in solidos:
                if t.tipo != "parede" or r.bottom <= t.rect.top + 3 or r.top >= t.rect.bottom - 1:
                    continue
                if abs(r.right - t.rect.left) <= 2.5:
                    contato = 1
                elif abs(r.left - t.rect.right) <= 2.5:
                    contato = -1
                if contato:
                    self.lado_parede = contato
                    self.graca_parede = .11
                    break
        self.na_parede = bool(contato)
        if cmd.mover and self.trava_lateral <= 0 and self.slide <= 0:
            self.face = 1 if cmd.mover > 0 else -1
        if cmd.deslize and cmd.mover and self.chao and self.slide_cd <= 0:
            self.slide, self.slide_cd = .62, 1.04
            self.altura(True, solidos)
            r = self.rect
        if self.buffer > 0 and self.slide <= 0 and r.h == self.ALTURA:
            if self.coyote > 0:
                self.vy = -502.
                self.buffer = self.coyote = 0.
                self.chao = False
                saltou = True
            elif self.graca_parede > 0 and self.lado_parede != self.ultimo_impulso:
                # A distância entre os troncos permite alternar paredes. Uma
                # mesma face só volta a dar impulso depois de outro apoio.
                self.ultimo_impulso = self.lado_parede
                self.face = -self.lado_parede
                self.vx, self.vy = self.face * 345., -523.
                self.trava_lateral = .15
                self.buffer = self.graca_parede = 0.
                self.impulso_parede = True
                saltou = True
            elif asas and self.asa_disponivel:
                self.vy = -440.
                self.asa_disponivel = False
                self.batida_asa = .18
                self.buffer = 0.
                saltou = True
        if not cmd.segurar_salto and self.vy < -233 and self.arma.rebote <= 0:
            self.vy = -233.
        if self.slide > 0:
            self.vx = self.face * 530.
        elif self.trava_lateral <= 0:
            limite = (94 if r.h < self.ALTURA else 247) * self.bonus_velocidade
            self.vx = aproximar(self.vx, cmd.mover * limite, (1750 if self.chao else 950) * dt)
        old = r.copy()
        dx = (self.vx + corrente) * dt
        r.x += dx
        for t in solidos:
            if not t.atravessavel and r.colliderect(t.rect):
                if t.tipo != "parede":
                    self.bateu = self.bateu or abs(self.vx) > 185
                if dx > 0: r.right = t.rect.left
                elif dx < 0: r.left = t.rect.right
                self.vx = self.slide = 0.

        self.planando = bool(asas and cmd.segurar_salto and not cmd.baixo
                             and self.vy > 48
                             and not (contato and cmd.mover == contato))
        if self.planando:
            self.vy = aproximar(self.vy, 76., dt * 840)
        elif contato and cmd.mover == contato and self.vy > 0:
            self.vy = min(self.vy + 240 * dt, 78.)
        else:
            self.vy = min(self.vy + 1190 * dt, 710.)
        self.chao = False
        r.y += self.vy * dt
        for t in solidos:
            if not r.colliderect(t.rect):
                continue
            if self.ignorar_topo is not None and t.descida and abs(t.rect.top-self.ignorar_topo)<1.2:
                continue
            if self.vy >= 0 and old.bottom <= t.rect.top + .5:
                r.bottom = t.rect.top
                self.vy = 0.
                self.chao = True
                self.planando = False
                self.planeio = self.PLANEIO
                self.asa_disponivel = True
                self.batida_asa = 0.
                self.ultimo_impulso = self.lado_parede = 0
                self.graca_parede = 0.
            elif self.vy < 0 and not t.atravessavel and old.top >= t.rect.bottom - .5:
                r.top = t.rect.bottom
                self.vy = 0.
        if self.ignorar_topo is not None and (r.top > self.ignorar_topo or r.bottom < self.ignorar_topo):
            self.ignorar_topo = None
        return saltou

    def atacar(self, cmd):
        if cmd.golpe:
            self.arma.pedir(cmd.baixo and not self.chao, cmd.deslize and bool(cmd.mover))
        if cmd.clarao and self.pulso_cd <= 0 and self.energia >= getattr(self,"custo_clarao",22.):
            self.energia -= getattr(self,"custo_clarao",22.)
            self.pulso, self.pulso_cd = .55, 2.50
            return True
        return False


NIVEIS = {
    "facil": (.32, 12, 4), "fácil": (.32, 12, 4), "sereno": (.32, 12, 4),
    "normal": (.5, 19, 3), "dificil": (.74, 25, 2), "difícil": (.74, 25, 2),
}

# O pino da roda fica nesta posição quando a alteração no mundo já foi feita.
MANIVELAS = {
    "valvula": ("valvula", "Examinar a corda baixada"),
    "dreno": ("dreno", "Examinar o canal drenado"),
    "ponte": ("ponte", "Examinar a ponte estendida"),
    "ralo": ("ralo", "Examinar a comporta aberta"),
    "roldana": ("roldana", "Examinar a roldana destravada"),
    "selo_copa": ("atalho_copa", "Examinar a janela aberta"),
    "ralo_cisterna": ("ralo_aberto", "Examinar o ralo aberto"),
    "comporta_viveiro": ("viveiro_aberto", "Examinar a comporta aberta"),
}


class Jornada:
    def __init__(self, modo="historia", dificuldade="normal", etapa=0):
        self.modo = modo.lower()
        self.dificuldade = dificuldade.lower()
        self.dreno, self.dano, self.vidas_iniciais = NIVEIS.get(self.dificuldade, NIVEIS["normal"])
        self.dreno *= .36
        self.vestigios = []
        self.em_vertical = False
        self.camera_y = 0.
        self.cartografia = set()
        self.explorado = set()
        self.missao = "principal"
        self.marco_vertical = "bosque"
        self.destino_vertical = None
        self.motivo_morte = ""
        self.tempo = 0.
        self.tempo_restante = 120.
        self.pontuacao = 0
        self.restauradas = 0
        self.volta = 0
        self.historico = {}
        self.diario = []
        self.bolsa = narrativa.Bolsa()
        self.estado = "jogando"
        self.dialogo = None
        self.eventos = []
        self.sons_espaciais = []
        self.aviso = ""
        self.aviso_t = 0.
        self.lume = Lume(95, CHAO, self.vidas_iniciais)
        self.entrar(etapa)

    def entrar(self, indice, retorno=False):
        self.em_vertical = False
        self.destino_vertical = None
        self.camera_y = 0.
        self.vestigios.clear()
        self.etapa = indice
        self.fase = FASES[indice]
        self.flags = self.historico.setdefault((self.volta, indice), set())
        self.boss = None
        inimigos = self.fase.inimigos
        self.gotas = self.fase.orvalhos
        self.gota_minuto = None
        self.variante = ""
        if self.modo == "infinito":
            self.variante, inimigos, self.gotas, self.gota_minuto = montar_infinito(indice, self.volta)
        self.inimigos = [Habitante(*e, dificuldade=self.dificuldade) for e in inimigos if "inimigo_" + str(e[1]) not in self.flags]
        if subsolo.ativo(self) and "inimigo_2860" not in self.flags:
            self.inimigos.append(Habitante("aranha",2860,1102,dificuldade=self.dificuldade))
        for e in self.inimigos:
            e.guarda = self.tranca_fechada and e.origem[0] == VIGIA_X and e.tipo == "carabideo"
        # No Bosque, a primeira silhueta a aparecer precisa ser a de Lume.
        # Nos demais biomas ele chega entre o abrigo e o primeiro morador.
        entrada = 42 if indice == 0 else 139
        marco = ARENA-20 if "marco" in self.flags else (MEIO if "meio" in self.flags else entrada)
        self.checkpoint = (marco, CHAO)
        pos = (RAIZ+42, CHAO) if retorno else (entrada, CHAO)
        self.recolocar(pos)
        self.camera = max(0, min(self.fase.width - 960, pos[0] - 340))
        self.eventos.append("etapa")
        self.notificar(f"Noite {self.volta + 1} · {self.variante}. Orvalho dourado: +8 s."
                       if self.variante else self.fase.name)

    def salvar(self):
        """Salva o progresso assentado. Objetos transitórios da arena renascem no marco."""
        return {
            "versao": 3, "mapa_grade": 24, "explorado": sorted(self.explorado), "missao": self.missao,
            "corte": {"ativo": self.em_vertical, "marco": self.marco_vertical,
                      "memoria": sorted(self.cartografia)}, "modo": self.modo, "dificuldade": self.dificuldade,
            "etapa": self.etapa, "volta": self.volta, "vidas": self.lume.vidas,
            "tempo": self.tempo, "tempo_restante": self.tempo_restante,
            "pontuacao": self.pontuacao, "diario": list(self.diario),
            "bolsa": self.bolsa.salvar(self.tempo),
            "fases": [{ "volta": volta, "etapa": etapa, "flags": sorted(flags)}
                      for (volta, etapa), flags in sorted(self.historico.items())],
        }

    @classmethod
    def carregar(cls, dados):
        """Carrega campanha local. Um arquivo inválido é recusado pelo chamador."""
        if not isinstance(dados, dict) or dados.get("versao") not in (1, 2, 3):
            raise ValueError("Formato de campanha desconhecido")
        etapa = int(dados["etapa"])
        if not 0 <= etapa < len(FASES):
            raise ValueError("Bioma desconhecido")
        jogo = cls(dados["modo"], dados["dificuldade"], etapa)
        jogo.volta = max(0, int(dados["volta"]))
        memoria = dados.get("explorado", [])
        if not isinstance(memoria,list) or len(memoria)>60000 or not all(isinstance(v,str) and len(v)<80 for v in memoria):
            raise ValueError("Mapa descoberto inválido")
        jogo.explorado = set(memoria) if dados.get("mapa_grade")==24 else set()
        escolha=dados.get("missao")
        jogo.missao = escolha if escolha in ("principal","secundaria","entrega_mimo",*(f"pedido_{i}" for i in range(4))) else "principal"
        for visita in dados["fases"]:
            nivel = int(visita["etapa"])
            if not 0 <= nivel < len(FASES):
                raise ValueError("Bioma desconhecido")
            flags = visita["flags"]
            if not isinstance(flags, list) or not all(isinstance(f, str) for f in flags):
                raise ValueError("Estado de bioma inválido")
            marcos = set(flags)
            if dados["versao"] == 1 and marcos.intersection(("marco","chefe","raiz")):
                # V1 terminava diretamente na arena após o primeiro mecanismo.
                marcos.update(("meio", FASES[nivel].preparo))
            jogo.historico[int(visita["volta"]), nivel] = marcos
        jogo.restauradas = sum("raiz" in flags for flags in jogo.historico.values())
        jogo.diario = [(str(titulo), str(texto)) for titulo, texto in dados["diario"]]
        jogo.tempo = max(0., float(dados["tempo"]))
        jogo.bolsa = narrativa.Bolsa.carregar(dados.get("bolsa"), jogo.tempo)
        jogo.tempo_restante = max(1., float(dados["tempo_restante"]))
        jogo.pontuacao = max(0, int(dados["pontuacao"]))
        jogo.lume.vidas = min(jogo.vidas_iniciais, max(1, int(dados["vidas"])))
        jogo.entrar(etapa)
        if dados.get("versao")==3:
            corte=dados.get("corte",{})
            if not isinstance(corte,dict):
                raise ValueError("Cartografia do corte inválida")
            marco=corte.get("marco","bosque")
            memoria=corte.get("memoria",[])
            if marco not in corte_vertical.MARCOS or not isinstance(memoria,list) or not all(isinstance(v,str) for v in memoria):
                raise ValueError("Cartografia do corte inválida")
            jogo.marco_vertical=marco
            jogo.cartografia=set(memoria)
            if corte.get("ativo") and jogo.modo=="historia":
                corte_vertical.entrar(jogo,marco)
        jogo.reiniciar()
        return jogo

    @property
    def setor_vertical(self):
        return corte_vertical.setor(self.lume.rect.centery,self.lume.rect.centerx)[1] if self.em_vertical else ""

    @property
    def altura_mundo(self):
        return corte_vertical.ALTURA if self.em_vertical else (subsolo.ALTURA if subsolo.ativo(self) else 540)

    @property
    def orvalhos(self):
        return sum(1 for k in self.flags if k.startswith("gota_"))

    @property
    def raio(self):
        portatil = 90 + .38 * max(0., min(100., self.lume.energia))
        if self.bolsa.luz_ate > self.tempo:
            portatil += 65
        if self.boss and not self.boss.vencido:
            portatil += 22
        return portatil

    def visivel(self, centro, margem=0):
        from .visao import ponto_visivel
        return ponto_visivel(self,centro,margem)

    @property
    def combate(self):
        return bool(self.boss and not self.boss.vencido) or any(
            e.estado in ("aviso", "investida") for e in self.inimigos if e.ativo)

    @property
    def tranca_fechada(self):
        # Um marco de arena obtido em versão anterior já comprova a passagem.
        liberada = (f"inimigo_{VIGIA_X}" in self.flags or "marco" in self.flags
                    or "vagem" in self.flags or "chefe" in self.flags)
        return self.modo == "historia" and self.etapa == 2 and not liberada

    @property
    def solidos(self):
        if self.em_vertical:
            return corte_vertical.terrenos("viveiro_aberto" in self.cartografia)
        geometria=frozenset(self.flags.intersection(("dreno","ponte","no","contrapeso",self.fase.preparo,"chefe")))
        ident=(self.etapa,geometria,subsolo.ativo(self))
        if getattr(self,"_geometria_id",None)!=ident:
            base=terrenos(self.etapa,geometria)
            self._geometria_base=tuple(subsolo.terrenos(base) if subsolo.ativo(self) else base)
            self._geometria_id=ident
        out=list(self._geometria_base)
        if self.tranca_fechada:
            out.append(Terreno(pygame.Rect(TRANCA_X, 223, 36, CHAO-223), "tranca"))
        if self.boss:
            out.extend(Terreno(rect, "arena") for rect in self.boss.apoios())
        return out

    @property
    def objetos(self):
        if self.em_vertical:
            return corte_vertical.objetos(self)
        out = [o for o in self.fase.objetos if (not o.requer or o.requer in self.flags)
               and not (o.id in self.flags and o.tipo in ("peca", "registro", "brasa", "reserva"))]
        if "encomenda_recolhida" in self.flags:
            out=[o for o in out if o.id!="encomenda_mimo"]
        deslocados = {}
        if self.etapa == 1 and "ponte" in self.flags:
            deslocados["fio"] = (1567, CHAO)
        if self.etapa == 2 and "raiz" in self.flags:
            deslocados["eco"] = (RAIZ-74, CHAO)
        if self.etapa == 3 and "contrapeso" in self.flags:
            deslocados["pingo"] = (366, 377)
        out = [Objeto(o.id, o.tipo, *deslocados[o.id], o.nome, o.requer) if o.id in deslocados else o for o in out]
        out.extend(Objeto(f"gota_{n}", "orvalho", x, y, "Orvalho") for n, (x, y) in
                   enumerate(self.gotas) if f"gota_{n}" not in self.flags)
        if self.gota_minuto and "gota_minuto" not in self.flags:
            out.append(Objeto("gota_minuto", "orvalho", *self.gota_minuto, "Orvalho da madrugada"))
        out.extend((
            Objeto("abrigo", "refugio", 114 if self.etapa == 0 else 82, CHAO, "Descansar sob a casca"),
            Objeto("abrigo_npc", "npc", 163, CHAO, ("Mimo", "Brasa", "Candeia", "Brasa")[self.etapa]),
            Objeto("atalho", "atalho", 1756, CHAO, "Abrir atalho ao abrigo" if "atalho" not in self.flags else "Voltar ao abrigo"),
            Objeto("meio", "refugio", MEIO, CHAO, "Descansar no marco do ramal"),
            Objeto("marco", "refugio", ARENA-24, CHAO, "Descansar no marco da arena"),
            Objeto("raiz", "raiz", RAIZ, CHAO, "Devolver orvalho" if "raiz" not in self.flags else "Ouvir a raiz"),
            Objeto("saida", "saida", SAIDA, CHAO, "Seguir a raiz"),
        ))
        if "atalho" in self.flags:
            out.append(Objeto("via", "atalho", 303, CHAO, "Voltar ao marco"))
        if self.etapa > 0:
            out.append(Objeto("voltar", "voltar", 34, CHAO, "Voltar ao bioma anterior"))
        if self.etapa == 3 and "chefe" in self.flags:
            out.append(Objeto("coruja_calma", "npc", FIM_ARENA+43, CHAO, "Coruja"))
        out.extend(corte_vertical.entradas(self))
        if subsolo.ativo(self):
            out.extend(subsolo.objetos(self))
        return out

    def proximo(self):
        if self.destino_vertical is not None:
            return None
        p = self.lume.rect
        candidatos = []
        for o in self.objetos:
            if o.tipo == "orvalho":
                continue
            dx = abs(o.x - p.centerx)
            if o.tipo == "corda" and dx < 50 and 216 <= p.bottom <= CHAO + 3:
                candidatos.append((dx, o))
            elif o.tipo == "valvula":
                # O desenho é apoiado no piso, mas Lume alcança seu aro acima da base.
                eixo = o.x, o.y - 35
                if dx <= 51 and p.top - 25 <= eixo[1] <= p.bottom + 25 and not any(
                    not t.atravessavel and t.rect.clipline(p.center, eixo) for t in self.solidos
                ):
                    candidatos.append((math.dist(p.center, eixo), o))
            elif dx <= 51 and abs(o.y - p.bottom) <= 48:
                candidatos.append((math.hypot(dx, o.y - p.bottom), o))
        return min(candidatos, key=lambda par: par[0])[1] if candidatos else None

    def manivela_girada(self, o):
        memoria = self.cartografia if self.em_vertical else self.flags
        return o.id in MANIVELAS and MANIVELAS[o.id][0] in memoria

    @property
    def interacao(self):
        if self.boss and not self.boss.vencido:
            return self.boss.interacao(self.lume.rect) or ""
        o = self.proximo()
        if not o:
            return ""
        if o.tipo == "npc":
            return "Ouvir " + o.nome
        if o.tipo == "valvula":
            if self.manivela_girada(o):
                return MANIVELAS[o.id][1]
            if o.id == "ralo_cisterna":
                return "Destravar o ralo" if corte_vertical.ralo_iluminado(self, o) else "Examinar a trava (precisa de K)"
            if o.id == "ponte" and "lingueta" not in self.flags:
                return "Examinar encaixe sem lingueta"
            if o.id == "ralo" and "ponte" not in self.flags:
                return "Examinar ralo preso à ponte"
        if o.id in self.fase.mecanismos and o.id in self.flags:
            return "Examinar o mecanismo"
        return o.nome

    @property
    def objetivo(self):
        if getattr(self,"ensaio_tatico",False):
            vivos=sum(e.ativo for e in self.inimigos if e.origem[0] in (1548,1660))
            return f"Afaste a patrulha da margem · {vivos} inimigo(s)" if vivos else "Patrulha vencida · Esc volta ao Campo de testes"
        from .orientacao import objetivo_atual
        alvo = objetivo_atual(self)
        if alvo:
            return alvo.texto
        return "Observe o fio e o salto. Enfrente a aranha e volte ao abrigo para tentar de novo."

    @property
    def dica_local(self):
        if self.em_vertical:
            return "Tab  mapa do corte   ·   S + Espaço  descer por uma grade"
        x = self.lume.rect.centerx
        if subsolo.ativo(self) and 2480 < x < 3200:
            return "Raízes inferiores · S + Espaço desce. Salte pelos galhos para voltar."
        if self.tranca_fechada and 1700 < x < TRANCA_X:
            return "A casca bloqueia de frente. O 3º J ou S + J no ar rompe a guarda."
        if self.etapa == 0:
            if x < 295: return "A D  mover     Espaço  saltar     E  interagir"
            if x < 580: return "No ar, solte e aperte Espaço de novo para alcançar o galho de orvalho."
            if 622 < x < 1100: return "J, J, J: três cortes. No ar, S + J rebate sobre o alvo."
            if 1135 < x < 1285: return "S  agachar     Shift + direção  deslizar"
            if 1415 < x < 1720: return "J  golpe curto     K  clarão (22 de luz)"
        if self.etapa == 1 and 750 < x < 1120:
            return "A marca de Casca mostra a peça da ponte. Siga o sulco sob a raiz; direção + Shift vence a corrente."
        if MEIO-50 < x < MEIO+100: return RAMAIS[self.etapa].nome + " · marco do ramal"
        if self.etapa == 0 and 1970 < x < 2495:
            return "Troncos riscados: salte encostado, depois aperte Espaço a cada troca de parede."
        if self.etapa in (1,3) and 1980 < x < 2720:
            return "Na grade de casca, segure baixo e aperte Espaço para descer."
        if self.etapa == 2 and 1990 < x < 2930:
            return "Salte da beira do bambu. Segure Espaço ao cair para planar."
        if ARENA-95 < x < ARENA: return self.fase.fonte
        return ""

    def recolocar(self, pos):
        self.lume.rect.size = (24, self.lume.ALTURA)
        self.lume.rect.midbottom = pos
        self.retorno_queda = tuple(pos)
        self.lume.vx = self.lume.vy = 0.
        self.lume.coyote = self.lume.buffer = self.lume.slide = self.lume.slide_cd = 0.
        self.lume.golpe = self.lume.pulso = self.lume.impacto = 0.
        self.lume.chao = True
        self.lume.em_corda = self.lume.na_parede = self.lume.planando = False
        self.lume.trava_lateral = self.lume.graca_parede = 0.
        self.lume.ultimo_impulso = self.lume.lado_parede = 0
        self.lume.ignorar_topo = None
        self.lume.planeio = self.lume.PLANEIO
        self.lume.asa_disponivel = True
        self.lume.batida_asa = 0.
        self.lume.arma = Arma()
        self.aplicar_reliquias()

    def aplicar_reliquias(self):
        self.lume.bonus_dano = self.bolsa.bonus_dano
        self.lume.bonus_velocidade = self.bolsa.bonus_velocidade
        self.lume.custo_clarao = 18. if self.bolsa.estoque["resina"] else 22.
        self.lume.tanino = self.bolsa.tanino_ate>self.tempo

    def notificar(self, texto, segundos=3.8):
        self.aviso, self.aviso_t = texto, segundos

    def memorizar(self, titulo, texto):
        if (titulo, texto) not in self.diario:
            self.diario.append((titulo, texto))

    @property
    def pedido_local(self):
        return narrativa.pedido_local(self)

    def trocar_item(self):
        if self.estado == "jogando" and not self.dialogo:
            self.notificar(self.bolsa.trocar())
        return self.bolsa.item.nome

    def usar_item(self):
        if self.estado == "jogando" and not self.dialogo:
            return self.bolsa.usar(self)
        return None

    def trocar_arma(self):
        if not getattr(self, 'ensaio_armas', False) or self.estado != 'jogando' or self.dialogo:
            return False
        if self.lume.impacto > 0 or not self.lume.arma.trocar():
            self.notificar('Conclua o golpe antes de trocar a arma.')
            return False
        agulha = self.lume.arma.equipamento == 'agulha'
        self.notificar('Agulha de taquara: alcance longo, golpe mais lento, 2 de luz por corte.' if agulha
                       else 'Espinho: cortes rápidos e curtos, sem custo de luz.')
        return True

    def fechar_dialogo(self):
        self.dialogo = None

    def reiniciar(self):
        self.motivo_morte=""
        self.destino_vertical=None
        self.vestigios.clear()
        if self.estado == "caido":
            self.estado = "jogando"
        self.boss = None
        self.dialogo = None
        for inimigo in self.inimigos:
            if inimigo.ativo:
                inimigo.repor()
        self.recolocar(self.checkpoint)
        self.lume.energia = 100.
        self.lume.iframes = 1.35
        self.lume.golpe_cd = self.lume.pulso_cd = 0.
        self.camera = max(0, min(self.fase.width - 960, self.checkpoint[0] - 340))
        if self.em_vertical:
            corte_vertical.camera(self)
        elif subsolo.ativo(self):
            subsolo.camera(self)
        self.notificar("Lume reencontra a luz do marco.")
        self.eventos.append("retorno")

    def ferir(self, forcar=False):
        if self.lume.iframes > 0 and not forcar:
            return
        if not forcar and self.bolsa.absorver():
            self.lume.iframes = 1.0
            self.notificar("O casulo se rompeu e amorteceu o ataque.")
            self.eventos.append("corda")
            return
        self.lume.iframes, self.lume.impacto = 1.25, .25
        self.lume.arma.cancelar()
        self.lume.golpe = 0.
        self.lume.energia = max(0., self.lume.energia - self.dano)
        self.eventos.append("dano")

    def recuperar_queda(self):
        energia=self.lume.energia-25.
        if energia<=0:
            self.perder_fagulha(motivo="queda")
            return
        destino=getattr(self,"retorno_queda",self.checkpoint)
        self.recolocar(destino)
        self.lume.energia=energia
        self.lume.iframes=1.5
        self.eventos.append("dano")
        self.notificar("A queda custou 25 de luz. Lume voltou à última borda segura.")
        if self.em_vertical:
            corte_vertical.camera(self)
        elif subsolo.ativo(self):
            subsolo.camera(self)

    def perder_fagulha(self, motivo="energia"):
        if self.estado != "jogando":
            return
        self.lume.vidas = max(0, self.lume.vidas - 1)
        self.lume.energia = 0.
        self.motivo_morte = motivo
        self.estado = "caido" if self.lume.vidas else "derrota"
        self.eventos.append("morte")

    def interagir(self, o):
        if o.tipo == "reliquia":
            item = o.id.removeprefix("reliquia_")
            if not self.bolsa.estoque.get(item):
                self.bolsa.receber(item, 1)
                self.aplicar_reliquias()
                ficha = narrativa.POR_ID[item]
                self.memorizar(ficha.nome, ficha.descricao)
                self.notificar(ficha.nome + " · " + ficha.descricao, 7.)
                self.eventos.append("coleta")
            return
        if self.em_vertical or o.tipo=="fenda":
            corte_vertical.interagir(self,o)
            return
        l = self.lume
        if o.tipo == "npc":
            estado = 2 if "raiz" in self.flags or self.restauradas >= 3 else int(
                self.fase.passos[0][0] in self.flags or (o.id == "abrigo_npc" and self.restauradas > 0))
            narrativa.conversar(self, o.nome, FALAS[o.nome][estado])
        elif o.tipo == "reserva":
            narrativa.abrir_reserva(self)
        elif o.tipo == "encomenda":
            if "encomenda_recolhida" not in self.flags:
                self.flags.update(("encomenda_aceita","encomenda_recolhida"))
                self.missao="entrega_mimo"
                self.notificar("Pacote de Mimo na bolsa de missão. Leve-o a Mimo no abrigo da entrada.",7.)
                self.memorizar("A mochila dos casulos","Um pacote de tanino ficou na varanda alta. Mimo prometeu preparar a lâmina para atravessar carapaças.")
                self.eventos.append("coleta")
        elif o.id == "placa_canal":
            self.flags.add("pista_canal")
            self.dialogo=("A peça levada pela cheia",
                "Casca desenhou a roda sem pino e uma peça de três dentes. Um sulco de metal segue sob a raiz baixa. "
                "Drene a água na roda acima de Casca. Depois, direção + Shift atravessa a corrente. "
                "Use E junto ao metal para recolher a lingueta e encaixá-la na roda da ponte.")
            self.memorizar(*self.dialogo)
            self.eventos.append("pagina")
        elif o.tipo == "registro":
            self.flags.add(o.id)
            self.dialogo = self.fase.registro
            self.memorizar(*self.dialogo)
            mapas = ("A válvula dos galhos solta a corda da peça. Além do marco, as paredes do poço levam à cunha.",
                     "Drene o canal e busque a lingueta no túnel. Depois da ponte, desça pela grade e solte o ralo.",
                     "O nó revela três apoios para alcançar a brasa. A vagem fica do outro lado da ponte quebrada.",
                     "A roldana solta a corda do contrapeso. Além do marco, o sino fica sob a grade da câmara.")
            self.memorizar("Mapa parcial · " + self.fase.name, mapas[self.etapa])
            self.eventos.append("pagina")
        elif o.id in self.fase.mecanismos:
            m = self.fase.mecanismos[o.id]
            if m.requer and m.requer not in self.flags:
                from .orientacao import pista_mecanismo
                self.notificar(pista_mecanismo(self, o), 7.)
            elif o.id in self.flags:
                self.notificar(m.efeito)
            else:
                self.flags.add(o.id)
                self.notificar(m.efeito)
                self.eventos.extend(m.audio)
                self.pontuacao += 25
                if o.id in ("peca", "ponte", "brasa", "contrapeso"):
                    narrativa.guardar_virada(self, narrativa.VESTIGIOS)
                if o.id == self.fase.preparo:
                    narrativa.guardar_virada(self, narrativa.RAMAIS)
        elif o.tipo == "corda":
            if l.rect.bottom < CHAO - 120:
                self.recolocar((o.x - 40, CHAO))
            else:
                l.em_corda = True
                l.rect.centerx = o.x + 10
                l.vx = l.vy = 0.
                self.eventos.append("corda")
        elif o.tipo == "refugio":
            l.energia = 100.
            self.eventos.append("coleta")
            self.notificar("Luz restaurada. " + self.objetivo, 7.)
        elif o.tipo == "atalho":
            self.flags.add("atalho")
            self.recolocar((1728 if o.id == "via" else 320, CHAO))
            self.notificar("Os dois lados da casca agora se comunicam.")
            self.eventos.append("porta")
        elif o.tipo == "raiz":
            if "chefe" not in self.flags:
                self.notificar("A guardiã ainda guarda o caminho.")
            elif self.orvalhos < 3:
                self.notificar(f"A raiz precisa de três gotas. Você encontrou {self.orvalhos}.")
            elif "raiz" not in self.flags:
                self.flags.add("raiz")
                self.restauradas += 1
                self.pontuacao += 180
                self.lume.energia = 100.
                if self.modo == "infinito":
                    premio = 51 - min(5, self.volta) * 4
                    self.tempo_restante = min(150., self.tempo_restante + premio)
                self.eventos.append("raiz")
                self.notificar("O orvalho corre pelas raízes de fora. O caminho responde.")
                narrativa.guardar_virada(self, narrativa.RAIZES)
            else:
                self.notificar("Há insetos cantando no galho molhado.")
        elif o.tipo == "saida":
            if "raiz" not in self.flags:
                self.notificar("A trilha se abre quando a raiz recebe o orvalho.")
            elif self.etapa == 3 and self.modo != "infinito":
                self.estado = "vitoria"
                self.eventos.append("vitoria")
            else:
                if self.etapa == 3:
                    self.volta += 1
                    self.tempo_restante = min(self.tempo_restante, max(85., 155. - self.volta * 8))
                self.entrar((self.etapa + 1) % 4)
        elif o.tipo == "voltar":
            self.entrar(self.etapa - 1, retorno=True)

    def update(self, dt, cmd=None):
        self.eventos = []
        self.sons_espaciais = []
        if self.estado != "jogando" or self.dialogo or dt <= 0:
            return
        cmd = cmd or Comando()
        # E e os ataques são bordas de tecla, mesmo quando um frame precisa
        # de vários passos de física. Conversa congela até o último relógio.
        o = self.proximo() if cmd.interagir and not (self.boss and not self.boss.vencido) else None
        # Na cisterna, K e E podem chegar no mesmo quadro. Teste o clarão já lançado.
        examinar_apos_clarao = o is not None and o.id == "ralo_cisterna" and cmd.clarao
        if o and not examinar_apos_clarao:
            origem = self.etapa, self.em_vertical
            self.interagir(o)
            if self.dialogo or self.estado != "jogando" or origem != (self.etapa, self.em_vertical):
                return
        clarao = self.lume.atacar(cmd)
        if clarao:
            self.vestigios.append(Vestigio(*self.lume.rect.center, self.tempo, 9. if self.bolsa.luz_ate>self.tempo else DURACAO))
            self.eventos.append("pulso")
            if not self.em_vertical:
                narrativa.responder_chamado(self)
        if examinar_apos_clarao:
            self.interagir(o)
            if self.dialogo:
                return
        dt = min(.1, dt)
        passos = max(1, math.ceil(dt * 120 - 1e-7))
        retido = Comando(mover=cmd.mover, baixo=cmd.baixo, segurar_salto=cmd.segurar_salto)
        for i in range(passos):
            self.passo(dt / passos, cmd if i == 0 else retido, clarao and i == 0)
            if self.estado != "jogando":
                break
        from .descoberta import revelar
        revelar(self)

    def passo(self, dt, cmd, clarao):
        l = self.lume
        if l.chao and not l.em_corda and l.energia>0 and any(
                abs(l.rect.bottom-t.rect.top)<1.5 and l.rect.right>t.rect.left
                and l.rect.left<t.rect.right for t in self.solidos):
            self.retorno_queda = tuple(l.rect.midbottom)
        self.tempo += dt
        while self.vestigios and self.tempo - self.vestigios[0].inicio >= self.vestigios[0].duracao:
            self.vestigios.pop(0)
        self.aviso_t = max(0., self.aviso_t - dt)
        if self.aviso_t <= 0: self.aviso = ""
        self.aplicar_reliquias()
        l.energia -= dt * (self.dreno + (.28 + min(5, self.volta) * .08 if self.modo == "infinito" else 0)) * self.bolsa.fator_dreno
        if self.modo == "infinito":
            self.tempo_restante -= dt
            if self.tempo_restante <= 0:
                self.estado = "derrota"
                self.eventos.append("derrota")
                return
        if self.em_vertical:
            corte_vertical.passo(self,dt,cmd,clarao)
            return
        estava_chao = l.chao
        if l.em_corda:
            alvo = 240 if self.etapa == 0 else 242
            l.rect.bottom = max(alvo, l.rect.bottom - 265 * dt)
            if l.rect.bottom <= alvo:
                l.em_corda = False
                l.chao = True
            else:
                l.chao = False
        else:
            corrente = -128 if self.etapa == 1 and 855 < l.rect.centerx < 1032 and l.rect.bottom > 406 else 0
            if l.movimento(dt, cmd, self.solidos, corrente, True):
                self.eventos.append("pulo")
            if l.bateu:
                l.energia = max(0., l.energia - 3.)
                self.eventos.append("impacto")
        l.rect.left = max(0, min(l.rect.left, self.fase.width - l.rect.w))
        pouso = not estava_chao and l.chao
        if pouso: self.eventos.append("pouso")
        if cmd.deslize and l.slide >= .60: self.eventos.append("deslize")
        if l.rect.top > subsolo.limite_queda(self):
            self.recuperar_queda()
            return
        for o in self.objetos:
            if o.tipo == "orvalho" and l.rect.inflate(16, 18).collidepoint(o.x, o.y):
                self.flags.add(o.id)
                if o.id == "gota_minuto":
                    self.tempo_restante += 8
                    self.notificar("Orvalho da madrugada · +8 segundos")
                l.energia = min(100., l.energia + 20)
                self.pontuacao += 10
                self.eventos.append("coleta")
        if self.tranca_fechada and l.rect.centerx > MEIO+20 and "viu_vigia" not in self.flags:
            self.flags.add("viu_vigia")
            self.notificar("O vigia aperta a trança. Ataque pelas costas ou quebre a guarda com o terceiro corte.", 5.)
        if l.rect.centerx >= MEIO-36 and "meio" not in self.flags:
            self.flags.add("meio")
            self.checkpoint = (MEIO, CHAO)
            l.energia = 100.
            self.notificar("Marco do ramal aceso · " + RAMAIS[self.etapa].nome)
            self.eventos.append("coleta")
        if l.rect.centerx >= ARENA-52 and self.fase.preparo in self.flags and "marco" not in self.flags:
            self.flags.add("marco")
            self.checkpoint = (ARENA-20, CHAO)
            l.energia = 100.
            self.notificar("Marco aceso. O musgo guardará sua volta.")
            self.eventos.append("coleta")
        if l.rect.left >= ARENA + 5 and self.fase.preparo in self.flags and "chefe" not in self.flags and self.boss is None:
            from .chefes import Encontro
            self.boss = Encontro(self.etapa, ARENA, CHAO, FIM_ARENA - ARENA)
            self.eventos.append("arena")
        if l.arma.avancar(dt, l):
            self.eventos.append("golpe")
        golpe = l.arma.area(l)
        if self.boss and not self.boss.vencido:
            l.rect.left = max(l.rect.left, ARENA)
            ruido = 1.0 if l.slide > 0 or pouso else min(.66, abs(l.vx) / 360) if l.chao else .08
            eventos = self.boss.update(dt, l.rect, ruido=ruido, golpe=golpe, clarao=clarao,
                                       interagir=cmd.interagir, direcao=cmd.mover,
                                       serie=l.arma.serie,bonus_dano=l.bonus_dano,
                                       dano_corte=2*l.arma.perfil.dano if l.arma.perfil else 2.)
            self.eventos.extend(e for e in eventos if e != "dano_jogador")
            if "dano_jogador" in eventos: self.ferir()
            if self.boss.vencido:
                self.flags.add("chefe")
                self.notificar("A guardiã encontra a calma." if self.etapa == 3 else "A raiz libera a saída da arena.")
                self.pontuacao += 120
                self.eventos.append("porta")
        else:
            self.combater_inimigos(dt, golpe, clarao)
        if l.energia <= 0:
            self.perder_fagulha()
        alvo = l.rect.centerx - (410 if l.face < 0 else 340)
        if self.boss and not self.boss.vencido:
            alvo = ARENA - (960 - (FIM_ARENA - ARENA)) / 2
        alvo = max(0., min(self.fase.width - 960, alvo))
        self.camera += (alvo - self.camera) * (1. - math.exp(-7.5 * dt))
        if subsolo.ativo(self):
            subsolo.camera(self, dt)

    def combater_inimigos(self, dt, golpe, clarao):
        lume = self.lume
        terrenos = self.solidos
        for e in self.inimigos:
            if not e.ativo:
                continue
            golpe = lume.arma.area(lume)
            e.companhia=next((outro.rect.centerx for outro in self.inimigos if outro is not e
                and outro.ativo and abs(outro.rect.centerx-e.rect.centerx)<350),None)
            resultado = e.acertar(lume.arma, golpe, clarao, lume)
            if resultado:
                self.eventos.append(resultado)
                if (lume.arma.tipo == "queda" and golpe and lume.arma.serie == e.ultimo_corte
                        and resultado != "bloqueio"):
                    lume.arma.rebote = .16
                    lume.vy = -344.
                    lume.chao = False
                    self.eventos.append("rebote")
                if not e.ativo:
                    if self.em_vertical:
                        self.cartografia.add("vigia_"+str(e.origem[0]))
                    else:
                        self.flags.add("inimigo_" + str(e.origem[0]))
                    self.pontuacao += 18
                    if e.guarda:
                        self.eventos.append("porta")
                        self.notificar("O vigia recua. A trança cai e a ponte das sementes está livre.", 5.)
                    continue
            dentro_do_clarao = any(math.dist(e.rect.center, (v.x, v.y)) <= v.raio(self.tempo)
                                   for v in self.vestigios)
            raio_isca = max(self.raio, 225) if dentro_do_clarao else self.raio
            avisos, atingiu = e.update(dt, lume, raio_isca, "no" in self.flags or dentro_do_clarao, terrenos)
            self.sons_espaciais.extend(avisos)
            vivos = []
            for p in e.projeteis:
                contato = p.avancar(dt, lume, terrenos, golpe, clarao)
                if contato == "corte":
                    self.eventos.append("acerto")
                elif contato == "dano":
                    atingiu = True
                elif not contato:
                    vivos.append(p)
            e.projeteis = vivos
            if atingiu and lume.iframes <= 0:
                energia = lume.energia
                self.ferir()
                if lume.energia < energia:
                    lume.vx += 143 if lume.rect.centerx >= e.rect.centerx else -143
