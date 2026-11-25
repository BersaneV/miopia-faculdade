"""Luz portátil de Lume e clarões que permanecem nas coordenadas do mundo."""
from dataclasses import dataclass
import math

DURACAO = 5.5
ALCANCE = 340

@dataclass(frozen=True)
class Vestigio:
    x: float
    y: float
    inicio: float
    duracao: float = DURACAO

    def raio(self, agora):
        idade = max(0., agora - self.inicio)
        if idade >= self.duracao:
            return 0
        if idade < .22:
            return round(92 + (ALCANCE - 92) * math.sin(idade / .22 * math.pi / 2))
        if idade <= 2.0:
            return ALCANCE
        u = (idade - 2.) / (self.duracao - 2.)
        return round(ALCANCE * (1. - u*u*(3.-2.*u)))


def fontes(j):
    return [(*j.lume.rect.center,j.raio),*((v.x,v.y,v.raio(j.tempo)) for v in j.vestigios)]


def ponto_visivel(j,ponto,margem=0,terrenos=None):
    """Luz com oclusão. Paredes e patamares impedem descobrir o outro lado."""
    terrenos=j.solidos if terrenos is None else terrenos
    for x,y,raio in fontes(j):
        if math.dist(ponto,(x,y))>raio+margem:continue
        if not any(t.rect.clipline((x,y),ponto) for t in terrenos):return True
    return False
