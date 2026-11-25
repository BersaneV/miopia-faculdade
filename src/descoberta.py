"""Cartografia por células visitadas. Não consulta o desenho para mudar o save."""
from collections import deque
TAMANHO = 24

def chave(j,x,y):
    regiao = "corte" if j.em_vertical else f"{j.volta}:{j.etapa}"
    return f"{regiao}/{int(x)//TAMANHO}/{int(y)//TAMANHO}"

def conhecida(j,x,y):
    return chave(j,x,y) in j.explorado

def revelar(j):
    # Só registra o entorno efetivamente percorrido. Um clarão não desenha
    # automaticamente a planta de salas que ainda não foram visitadas.
    from .visao import fontes,ponto_visivel
    luzes=fontes(j)
    assinatura=(j.em_vertical,j.etapa,j.volta,tuple((round(x/12),round(y/12),int(r/24)) for x,y,r in luzes),
                frozenset(j.flags),frozenset(j.cartografia))
    if getattr(j,"_ultima_descoberta",None)!=assinatura:
        j._ultima_descoberta=assinatura
        candidatas=set()
        for x,y,raio in luzes:
            if raio<=0:continue
            for col in range(max(0,int((x-raio)//TAMANHO)),int((x+raio)//TAMANHO)+1):
                for lin in range(max(0,int((y-raio)//TAMANHO)),int((y+raio)//TAMANHO)+1):
                    px,py=col*TAMANHO,lin*TAMANHO
                    if chave(j,px,py) not in j.explorado:candidatas.add((px,py))
        j._descoberta_fila=deque(sorted(candidatas,key=lambda p:min((p[0]-x)**2+(p[1]-y)**2 for x,y,r in luzes)))
    terrenos=j.solidos
    fila=getattr(j,"_descoberta_fila",deque())
    for _ in range(min(24,len(fila))):
        px,py=fila.popleft()
        if any(ponto_visivel(j,(px+dx,py+dy),terrenos=terrenos)
               for dx,dy in ((12,12),(2,2),(22,22))):
            j.explorado.add(chave(j,px,py))
