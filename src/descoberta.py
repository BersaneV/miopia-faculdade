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
    assinatura=(j.em_vertical,j.etapa,j.volta,int(j.camera/24),int(j.camera_y/24),tuple((round(x/12),round(y/12),int(r/24)) for x,y,r in luzes),
                frozenset(j.flags),frozenset(j.cartografia),frozenset(j.tochas))
    if getattr(j,"_ultima_descoberta",None)!=assinatura:
        j._ultima_descoberta=assinatura
        candidatas=set()
        for x,y,raio in luzes:
            if raio<=0:continue
            for col in range(max(0,int((x-raio)//TAMANHO)),int((x+raio)//TAMANHO)+1):
                for lin in range(max(0,int((y-raio)//TAMANHO)),int((y+raio)//TAMANHO)+1):
                    px,py=col*TAMANHO,lin*TAMANHO
                    if px+22<j.camera or px>j.camera+960 or py+22<j.camera_y or py>j.camera_y+540:continue
                    if chave(j,px,py) not in j.explorado:candidatas.add((px,py))
        from .luzes_mundo import zonas
        for z in zonas(j):
            for col in range(max(0,z.left//TAMANHO,int(j.camera)//TAMANHO),min(z.right//TAMANHO+1,int(j.camera+960)//TAMANHO+1)):
                for lin in range(max(0,z.top//TAMANHO,int(j.camera_y)//TAMANHO),min(z.bottom//TAMANHO+1,int(j.camera_y+540)//TAMANHO+1)):
                    p=col*TAMANHO,lin*TAMANHO
                    if chave(j,*p) not in j.explorado:candidatas.add(p)
        # Preserva trabalho ainda visível: mover a câmera não pode reiniciar
        # sempre pelo centro e impedir que a borda iluminada entre no mapa.
        pendentes=[p for p in getattr(j,'_descoberta_fila',()) if p in candidatas]
        candidatas.difference_update(pendentes)
        j._descoberta_fila=deque(pendentes+sorted(candidatas,key=lambda p:(p[0]-j.lume.rect.centerx)**2+(p[1]-j.lume.rect.centery)**2))
    fila=getattr(j,"_descoberta_fila",deque())
    for _ in range(min(24,len(fila))):
        px,py=fila.popleft()
        if any(ponto_visivel(j,(px+dx,py+dy))
               for dx,dy in ((12,12),(2,2),(22,22))):
            j.explorado.add(chave(j,px,py))
