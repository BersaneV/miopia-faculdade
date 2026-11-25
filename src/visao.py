"""Luz portátil de Lume e clarões que permanecem nas coordenadas do mundo."""
from dataclasses import dataclass
import math

DURACAO = 6.5
ALCANCE = 1200

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
