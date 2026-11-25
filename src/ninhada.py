"""Reforços temporários da Tecelã, delimitados pela arena."""
from .taticas import Habitante

AVISO = .94
RECUO = 2.2


def pontos(arena):
    return (round(arena.inicio+arena.largura*.61), round(arena.inicio+arena.largura*.86))


class Cria(Habitante):
    def __init__(self, x, arena):
        self.arena = arena
        super().__init__("aranha", x, arena.chao, arena.dificuldade)
        self.rect.size = self.rect.w*.76, self.rect.h*.78
        self.rect.midbottom = self.origem
        self.max_vida = self.vida = 4 if arena.dificuldade in ("difícil", "dificil") else 3
        self.t = .45
        self.grupo = "ninhada"

    def vaga_de_ataque(self):
        return (self.arena.relogio < self.arena.ninhada.expira-RECUO
                and self.arena.estado == "busca" and not self.arena.fios and not any(
            e is not self and e.ativo and (e.estado in ("aviso", "investida") or e.projeteis)
            for e in self.colegas))

    def patrulhar(self, lume, distancia, dt, terrenos):
        lado = -1 if self.rect.centerx < lume.rect.centerx else 1
        faixa = 109 if any(c.ativo and c.origem[0] < self.origem[0] for c in self.colegas) else 77
        x = max(self.arena.esq, min(self.arena.dir, lume.rect.centerx+lado*faixa))
        self.seguir((x, self.origem[1]-self.rect.h/2), 142, dt, terrenos)

    def update(self, dt, lume, raio, restaurado, terrenos):
        if (self.arena.relogio >= self.arena.ninhada.expira-RECUO
                and self.estado not in ("aviso", "investida") and not self.projeteis):
            self.estado = "retira_ninhada"
            self.seguir((self.origem[0], self.origem[1]-self.rect.h/2), 245, dt, terrenos)
            if abs(self.rect.centerx-self.origem[0]) < 8 and not self.projeteis:
                self.ativo = False
            return [], False
        if self.arena.agua > 0 and abs(self.rect.centerx-self.arena.cortina) < 110:
            if self.estado in ("aviso", "investida", "manobra"):
                self.estado, self.t = "recuo", .38
                self.plano.clear()
            self.cego = max(self.cego, .20)
            self.lentidao = max(self.lentidao, .25)
        sons, dano = super().update(dt, lume, raio, restaurado, terrenos)
        self.rect.centerx = max(self.arena.esq, min(self.arena.dir, self.rect.centerx))
        return sons, dano


class Ninhada:
    def __init__(self, arena):
        self.arena = arena
        self.vivos = []
        self.cascas = ()
        self.levas = 0
        self.expira = 0.
        self.ultimo_turno = -1

    def limpar(self):
        self.vivos.clear()
        self.cascas = ()

    def atacando(self):
        return any(e.ativo and (e.estado in ("aviso", "investida") or e.projeteis) for e in self.vivos)

    def ceder_turno(self, corpo):
        e = self.arena
        if self.ultimo_turno == e.turno or e.fios or e.relogio >= self.expira-RECUO:
            return False
        if not any(c.ativo and c.cego <= 0 and abs(c.rect.centerx-corpo.centerx) < 154
                   and abs(c.rect.centery-corpo.centery) < 88
                   for c in self.vivos):
            return False
        self.ultimo_turno = e.turno
        e.tempo = .72
        return True

    def atualizar(self, corpo, eventos):
        """Retorna se o chamado usa este passo da Tecelã."""
        e = self.arena
        if self.vivos and e.relogio >= self.expira:
            self.vivos.clear()
        if e.estado == "chama_ninhada":
            if e.tempo <= 0:
                self.vivos[:] = [Cria(x, e) for x in self.cascas]
                for cria in self.vivos:
                    cria.colegas = self.vivos
                self.cascas = ()
                self.expira = e.relogio + 14.
                e._mudar("busca", .52)
            return True
        if (e.estado != "busca" or self.levas >= e.meta-1 or any(cria.ativo for cria in self.vivos)
                or e.vida > e.vida_max*(.68 if not self.levas else .34)):
            return False
        qtd = 2 if self.levas or e.dificuldade in ("difícil", "dificil") else 1
        self.cascas = tuple(sorted(pontos(e), key=lambda x: abs(corpo.centerx-x), reverse=True)[:qtd])
        self.levas += 1
        e._mudar("chama_ninhada", AVISO)
        eventos.append("aviso")
        return True
