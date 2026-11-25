"""Cartografia por células visitadas. Não consulta o desenho para mudar o save."""
TAMANHO = 160

def chave(j,x,y):
    regiao = "corte" if j.em_vertical else f"{j.volta}:{j.etapa}"
    return f"{regiao}/{int(x)//TAMANHO}/{int(y)//TAMANHO}"

def conhecida(j,x,y):
    return chave(j,x,y) in j.explorado

def revelar(j):
    # Só registra o entorno efetivamente percorrido. Um clarão não desenha
    # automaticamente a planta de salas que ainda não foram visitadas.
    x,y = j.lume.rect.center
    for dx,dy in ((0,0),(-65,0),(65,0),(0,-65),(0,65)):
        if x+dx>=0 and y+dy>=0:
            j.explorado.add(chave(j,x+dx,y+dy))
