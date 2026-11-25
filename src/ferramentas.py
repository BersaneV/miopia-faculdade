"""Ferramentas de combate locais. Sem alvo, um uso não desperdiça a carga."""
from .combate import AEREOS, segmento_bloqueado


def espalhar_polen(j):
    l=j.lume
    terrenos=j.solidos
    def alcance(p):
        dx,dy=p[0]-l.rect.centerx,p[1]-l.rect.centery
        return -15<=dx*l.face<=190 and abs(dy)<125 and not segmento_bloqueado(l.rect.center,p,terrenos)
    afetados=0
    for e in j.inimigos:
        if not e.ativo:continue
        if e.tipo in AEREOS and alcance(e.rect.center):
            e.lentidao=6.
            afetados+=1
        vivos=[p for p in e.projeteis if not alcance(p.pos)]
        afetados+=len(e.projeteis)-len(vivos)
        e.projeteis=vivos
    if afetados:
        j.eventos.append("polen")
    return afetados
