"""Ferramentas de combate locais. Sem alvo, um uso não desperdiça a carga."""
from .combate import AEREOS, segmento_bloqueado

DURACAO_POLEN = 6.


def espalhar_polen(j):
    l=j.lume
    terrenos=j.solidos
    def alcance(p):
        dx,dy=p[0]-l.rect.centerx,p[1]-l.rect.centery
        return -15<=dx*l.face<=190 and abs(dy)<125 and not segmento_bloqueado(l.rect.center,p,terrenos)
    asas = projeteis = 0
    for e in j.inimigos:
        if not e.ativo:continue
        if e.tipo in AEREOS and e.lentidao <= 0 and alcance(e.rect.center):
            e.lentidao = DURACAO_POLEN
            asas += 1
        vivos=[p for p in e.projeteis if not alcance(p.pos)]
        projeteis += len(e.projeteis)-len(vivos)
        e.projeteis=vivos
    if asas or projeteis:
        j.eventos.append("polen")
    return asas, projeteis
