"""Néctar, caça e distração na Ponte das Lanternas."""
import math

from .combate import Vetor, segmento_bloqueado
from .taticas import Habitante


PAR = (("cobra", 2720, 790), ("vespa", 2870, 680))
FLOR = (2740, 758)
TEMPO_CACA = .56
PLACA = "jardim_placa_nectar"
ESTADOS_COBRA = ("espreita", "aviso_caca", "bote_caca", "recuo_caca")
ESTADOS_VESPA = ("nectar", "fuga", "isca")
ROTINAS = ESTADOS_COBRA + ESTADOS_VESPA


def margem_da_isca(x, y):
    return 2440 <= x < 2660 and 640 <= y <= 810


class MoradorDaPonte(Habitante):
    def __init__(self, tipo, x, y, dificuldade):
        super().__init__(tipo, x, y, dificuldade=dificuldade)
        self.presa = None

    def repor(self):
        super().repor()
        self.estado = "espreita" if self.tipo == "cobra" else "nectar"
        self.alvo_isca = None
        self.ultima_isca = None

    def percebe(self, lume, terrenos, alcance):
        return (self.cego <= 0 and math.dist(self.rect.center, lume.rect.center) < alcance
                and not segmento_bloqueado(self.rect.center, lume.rect.center, terrenos))

    def acertar(self, arma, area, clarao, lume):
        # À distância de observação, o clarão chama a vespa em rotina.
        # De perto ou em combate, o pulso segue a regra comum de acerto.
        if self.tipo == "vespa" and self.estado in ESTADOS_VESPA and margem_da_isca(*lume.rect.center):
            clarao = False
        return super().acertar(arma, area, clarao, lume)

    def seguir_rotina(self, destino, velocidade, dt, terrenos):
        dx = destino[0]-self.rect.centerx
        if abs(dx) > 4:
            self.frente = 1 if dx > 0 else -1
        self.seguir(destino, velocidade, dt, terrenos)

    def atualizar_vespa(self, dt, lume, terrenos):
        if self.estado == "isca":
            self.seguir_rotina(self.alvo_isca, 270, dt, terrenos)
            if self.t <= 0:
                self.alvo_isca = None
                self.estado = "nectar"
        elif self.estado == "fuga":
            self.seguir_rotina((self.origem[0]-15, self.origem[1]-38), 320, dt, terrenos)
            if self.t <= 0:
                self.estado = "nectar"
        elif self.percebe(lume, terrenos, 105):
            self.estado, self.t = "patrulha", .10
        else:
            x, y = FLOR
            self.seguir_rotina((x+math.sin(self.relogio*3)*9, y-21+math.sin(self.relogio*5)*5),
                               165, dt, terrenos)
        return [], False

    def atualizar_cobra(self, dt, lume, terrenos):
        chao = self.origem[1]-self.rect.h/2
        presa = self.presa
        if self.estado == "aviso_caca":
            if presa and presa.ativo and presa.estado == "nectar" and self.t <= .21:
                presa.estado, presa.t = "fuga", 1.00
            if self.t <= 0:
                self.estado, self.t = "bote_caca", .31
        elif self.estado == "bote_caca":
            self.seguir((self.alvo.x, chao), 415*self.ritmo, dt, terrenos)
            contato = self.rect.colliderect(lume.rect)
            if contato or self.t <= 0:
                self.estado, self.t = "recuo_caca", .74
            return [], contato
        elif self.percebe(lume, terrenos, 81):
            self.estado, self.t = "patrulha", .10
        elif self.estado == "recuo_caca":
            self.seguir_rotina((FLOR[0]-69, chao), 108, dt, terrenos)
            if self.t <= 0:
                self.estado = "espreita"
        else:
            self.seguir_rotina((FLOR[0]-69, chao), 94, dt, terrenos)
            if (presa and presa.ativo and presa.estado == "nectar" and self.cego <= 0
                    and abs(self.rect.centerx-(FLOR[0]-69)) < 9
                    and math.dist(presa.rect.center, FLOR) < 31
                    and not segmento_bloqueado(self.rect.center, presa.rect.center, terrenos)):
                self.alvo = Vetor(presa.rect.center)
                self.frente = 1
                self.estado, self.t = "aviso_caca", TEMPO_CACA
                return [("silvo_perto", self.rect.centerx)], False
        return [], False

    def update(self, dt, lume, raio, restaurado, terrenos):
        if self.estado in ROTINAS:
            lento = self.lentidao > 0
            self.lentidao = max(0., self.lentidao-dt)
            self.cego = max(0., self.cego-dt)
            if lento:
                dt *= .6
            self.relogio += dt
            self.t -= dt
            self.flash = max(0., self.flash-dt)
            self.resistencia_leve = max(0., self.resistencia_leve-dt)
            if self.tipo == "cobra":
                return self.atualizar_cobra(dt, lume, terrenos)
            return self.atualizar_vespa(dt, lume, terrenos)
        if self.estado == "patrulha" and not self.projeteis and math.dist(self.rect.center, lume.rect.center) > 320:
            self.plano.clear()
            self.estado = "espreita" if self.tipo == "cobra" else "nectar"
            self.alvo_isca = None
            return [], False
        return super().update(dt, lume, raio, restaurado, terrenos)


def aproximar_isca(j):
    if not j.vestigios or "jardim_aberto" not in j.cartografia:
        return
    vestigio = j.vestigios[-1]
    if not margem_da_isca(vestigio.x, vestigio.y):
        return
    vespa = next((e for e in j.inimigos if e.ativo and isinstance(e, MoradorDaPonte)
                  and e.tipo == "vespa"), None)
    if (vespa is None or vespa.estado not in ESTADOS_VESPA or vespa.ultima_isca == vestigio.inicio
            or math.dist(vespa.rect.center, (vestigio.x, vestigio.y)) > vestigio.raio(j.tempo)):
        return
    vespa.ultima_isca = vestigio.inicio
    vespa.alvo_isca = (vestigio.x, max(620, vestigio.y-114))
    vespa.estado, vespa.t = "isca", 2.30
    j.sons_espaciais.append(("zurro_perto", vespa.rect.centerx))


def luzes(j):
    x, y = FLOR
    alcance = 108
    if ("jardim_aberto" in j.cartografia
            and j.camera-alcance <= x <= j.camera+960+alcance
            and j.camera_y-alcance <= y <= j.camera_y+540+alcance):
        return ((x, y, alcance),)
    return ()
