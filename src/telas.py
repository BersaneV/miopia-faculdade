"""Menus e páginas desenhados em 960 × 540. As áreas clicáveis são as linhas visíveis."""
import math
import pygame
from .ensaios import ENSAIOS, INDICE_ARANHA
from . import ambiental
from .narrativa import RAIZES
from .ilustracao import (AMBAR, OSSO, PALIDO, TEAL, ROMANOS, brilho, imagem, linhas,
                         losango, painel, paragrafo, placa, texto)
from .paisagem import NPC_TAM, slug
from .roteiro import CONTROLES, ENTRADAS, FINAL, PROLOGO, epilogo

SEMENTE_ANTERIOR=pygame.Rect(466,321,38,32)
SEMENTE_SEGUINTE=pygame.Rect(643,321,38,32)
VER_TENTATIVA=pygame.Rect(466,370,317,36)

def fundo(s,a):
    s.blit(imagem("capa.jpg",960,540),(0,0))
    for n in range(14):
        x=365+n*47+math.sin(a.relogio*.28+n)*10
        y=(147+n*33-a.relogio*(2+n%3))%480
        pygame.draw.circle(s,(169+n%4*14,152,102),(int(x),int(y)),1)
    brilho(s,(774,278),45)


def opcoes(a,s,nomes,x,y,w,passo=34,tam=18):
    a.alvos=[]
    for i,nome in enumerate(nomes):
        r=pygame.Rect(x,y+i*passo,w,passo-2)
        ativo=a.selecao==i
        if ativo:
            s.blit(placa(r.w,r.h,199),r)
            pygame.draw.line(s,(129,124,94),r.bottomleft,r.bottomright)
            losango(s,r.x+12,r.centery,4)
        texto(s,nome,r.x+26,r.y+(r.h-tam)//2-3,tam,AMBAR if ativo else OSSO,"forte" if ativo else "normal")
        a.alvos.append(r)


def menu(a,s):
    fundo(s,a)
    texto(s,"Miopia",53,39,96,OSSO,"titulo")
    texto(s,"A ÚLTIMA LUZ DA MATA",62,147,17,AMBAR,"forte")
    pygame.draw.line(s,TEAL,(62,183),(282,183))
    losango(s,289,183,3)
    opcoes(a,s,a.menu_nomes(),55,203,270,32,18)
    texto(s,"Setas  escolher     Enter  confirmar",60,501,14,PALIDO)
    if a.mem.aviso: texto(s,a.mem.aviso,340,504,13,AMBAR)


def livro(a,s,titulo,supra=""):
    fundo(s,a)
    s.blit(placa(960,540,147),(0,0))
    painel(s,(52,35,856,470))
    if supra: texto(s,supra,81,54,13,AMBAR,"forte")
    texto(s,titulo,80,74,39,OSSO,"titulo")


def ensaios(a,s):
    livro(a,s,"Campo de testes","MIOPIA")
    texto(s,"Entre direto no trecho. Sua campanha fica salva à parte.",83,130,17,PALIDO)
    nomes=[c.nome for c in ENSAIOS]+["Voltar"]
    opcoes(a,s,nomes,78,160,355,min(36,288//len(nomes)),17)
    if a.selecao<len(ENSAIOS):
        c=ENSAIOS[a.selecao]
        texto(s,c.nome,467,196,24,AMBAR,"titulo")
        paragrafo(s,c.pista,467,242,386,18)
        if a.selecao==INDICE_ARANHA:
            for botao,sinal in ((SEMENTE_ANTERIOR,"‹"),(SEMENTE_SEGUINTE,"›")):
                painel(s,botao,False)
                texto(s,sinal,botao.centerx,botao.y+1,22,AMBAR,"forte","centerx")
            texto(s,f"Semente {a.semente_aranha}",573,328,16,OSSO,"forte","centerx")
            if a.ultimo_replay is not None:
                painel(s,VER_TENTATIVA,False)
                texto(s,"V   Assistir à última tentativa",480,379,16,AMBAR,"forte")
                paragrafo(s,a.aviso_replay,467,412,380,14,PALIDO)
    texto(s,"Enter   abrir trecho      Esc   voltar",82,459,15,PALIDO)


def ajuda(a,s):
    livro(a,s,"Controles","CADERNO DE CAMPO")
    for i,(key,acao) in enumerate(CONTROLES):
        texto(s,key,86,130+i*25,16,AMBAR,"forte")
        texto(s,acao,302,130+i*25,16,OSSO)
    texto(s,"Esc ou Enter   ·   voltar",84,461,15,PALIDO)


def opcoes_ajustes(a,s):
    livro(a,s,"Ajustes","MIOPIA")
    p=a.mem.prefs
    labels=[f"Dificuldade  ·  {p['dificuldade'].capitalize()}",
            f"Ambiência  ·  {round(p['musica']*100)}%",f"Efeitos  ·  {round(p['efeitos']*100)}%",
            "Brilho da mata  ·  "+("Mínimo","Noturno","Médio","Alto")[p["brilho"]],
            "Som  ·  "+("silenciado" if p["mudo"] else "ligado"),"Voltar"]
    opcoes(a,s,labels,77,134,390,41,19)
    from .paisagem import SOMBRAS, mascara_luz
    # A amostra mostra exatamente a máscara aplicada na partida.
    amostra = imagem("fundo_0.jpg",340,188).copy()
    mascara = pygame.Surface(amostra.get_size())
    mascara.fill(SOMBRAS[p["brilho"]])
    mascara.blit(mascara_luz(66,p["brilho"]),(104,30),special_flags=pygame.BLEND_RGB_MAX)
    amostra.blit(mascara,(0,0),special_flags=pygame.BLEND_RGB_MULT)
    s.blit(amostra,(517,146))
    texto(s,"Visibilidade na mata",517,344,15,PALIDO)
    texto(s,"Esquerda / direita  ajustar     Enter ou clique  avançar",82,410,16,PALIDO)
    texto(s,"A dificuldade se aplica à próxima jornada.",82,448,16,PALIDO)


def creditos(a,s):
    livro(a,s,"Créditos","MIOPIA")
    texto(s,"Projeto A3  ·  Universidade São Judas Tadeu",84,135,19,AMBAR,"forte")
    paragrafo(s,"Otávio Araújo Aredes Guedes, Caio Vidotte Vrech Sousa, Tiago Ribeiro Gomes, Thierry Henry Rocha da Silva, Victor Bersane Jasaitis e Iago Robert da Silva Andrade.",84,171,785,18)
    texto(s,"Arte e implementação",84,248,19,AMBAR,"forte")
    paragrafo(s,"Reformulação com Codex, ImageGen e pygame-ce. Tipografia Nunito e Liberation Serif, sob a licença SIL Open Font License.",84,279,780,17)
    texto(s,"Paisagem sonora",84,345,19,AMBAR,"forte")
    paragrafo(s,a.credito_audio,84,376,785,16)
    texto(s,"Esc ou Enter   ·   voltar",84,465,15,PALIDO)


def pausa(a,s):
    s.blit(placa(960,540,120),(0,0))
    painel(s,(294,91,372,361))
    texto(s,"Pausa",480,106,44,OSSO,"titulo","centerx")
    nomes=a.pausa_nomes.copy()
    if a.ensaio is not None:
        nomes[-1]="Voltar ao campo de testes"
    opcoes(a,s,nomes,315,176,330,39)
    dica=(f"Semente {a.jogo.semente}   ·   R para repetir" if a.ensaio==INDICE_ARANHA
          else "O tempo da mata está suspenso.")
    texto(s,dica,480,414,15,PALIDO,"normal","centerx")


def morte(a,s):
    j=a.jogo
    s.blit(placa(960,540,174),(0,0))
    painel(s,(177,102,606,338))
    texto(s,"Você morreu",480,135,58,OSSO,"titulo","centerx")
    terminal=j.estado=="derrota"
    if terminal and j.modo=="historia":
        detalhe=FINAL["derrota"][1]
    else:
        detalhe=("Lume caiu no vão." if j.motivo_morte=="queda" else "A luz de Lume se apagou.")
        detalhe += (" Resta uma fagulha." if j.lume.vidas==1 else
                    f" Restam {j.lume.vidas} fagulhas." if j.lume.vidas else " A última fagulha se apagou.")
    paragrafo(s,detalhe,212,222,536,18,PALIDO)
    nome="Tentar outra noite" if terminal and j.modo=="infinito" else "Voltar ao último marco"
    if a.ensaio is not None:
        nome="Repetir o ensaio"
    voltar="Voltar ao campo de testes" if a.ensaio==INDICE_ARANHA else "Voltar ao menu"
    opcoes(a,s,[nome,voltar],209,328,540,40,19)


def replay(a,s):
    if a.reproducao is None:
        painel(s,(202,106,556,94))
        paragrafo(s,a.aviso_replay,223,118,512,17,OSSO)
        texto(s,"Esc   voltar ao campo",223,165,15,AMBAR)
    else:
        painel(s,(246,18,421,64),False)
        nome="Reprodução pausada" if a.replay_pausado else "Reprodução"
        texto(s,f"{nome}   ·   {a.jogo.tempo:.1f} s",456,24,17,AMBAR,"forte","centerx")
        texto(s,"Espaço   pausar / continuar      Esc   voltar",456,52,15,OSSO,"normal","centerx")


def confirmar(a,s):
    livro(a,s,a.conf_titulo,"MIOPIA")
    paragrafo(s,a.conf_msg,84,163,741,20)
    opcoes(a,s,["Voltar",a.conf_acao],77,278,410,46)


def dialogo(a,s):
    j=a.jogo
    nome,msg=j.dialogo
    painel(s,(73,344,814,139))
    x=97
    if nome in NPC_TAM:
        img=imagem("npc_"+slug(nome)+".png",76,70)
        s.blit(img,(88,379)); x=179
    texto(s,nome,x,355,20,AMBAR,"titulo")
    paragrafo(s,a.fala_visivel,x,384,825-x,17,OSSO)
    texto(s,"E / Enter   ·   avançar",866,456,12,PALIDO,"normal","right")


def cena(a,s):
    titulo,msg,i=PROLOGO[a.quadro]
    img=imagem(f"fundo_{i}.jpg",1030,580)
    s.blit(img,(-30,-28))
    s.blit(placa(960,540,94),(0,0))
    painel(s,(0,302,960,238),False)
    texto(s,"PRÓLOGO     "+ROMANOS[a.quadro],65,323,14,AMBAR,"forte")
    texto(s,titulo,62,347,39,OSSO,"titulo")
    paragrafo(s,a.fala_visivel,65,411,810,19)
    texto(s,"Enter  avançar     Esc  pular prólogo",894,504,14,PALIDO,"normal","right")


def diario(a,s):
    j=a.jogo
    if a.ensaio==INDICE_ARANHA:
        livro(a,s,j.fase.name,"CADERNO DE ENSAIO")
        texto(s,f"Semente {j.semente}   ·   {j.dificuldade}",85,148,20,AMBAR,"titulo")
        texto(s,"Lume em âmbar. A pedra entre o abrigo e a aranha bloqueia a visão.",85,186,17,PALIDO)
        for tr in j.solidos:
            r=tr.rect
            x=86+round(r.x/j.fase.width*780)
            y=234+round(r.y*.23)
            pygame.draw.rect(s,TEAL,(x,y,max(2,round(r.w/j.fase.width*780)),max(2,round(r.h*.23))),1)
        for corpo,cor in ((j.lume.rect,AMBAR),(j.inimigos[0].rect,OSSO)):
            losango(s,86+round(corpo.centerx/j.fase.width*780),234+round(corpo.centery*.23),5,cor)
        texto(s,"Abrigo",115,379,16,PALIDO)
        texto(s,"Tab / Esc   fechar",84,465,15,PALIDO)
        return
    livro(a,s,"Diário de Lume","CADERNO DE CAMPO")
    tem_corte=bool(j.cartografia)
    total=len(j.diario)+2+tem_corte
    texto(s,f"{a.pagina+1} / {total}",873,77,20,PALIDO,"titulo","right")
    if a.pagina==0:
        from .cartografia import alvo_local, mapa_local, texto_curto
        texto(s,"Corte da Figueira" if j.em_vertical else j.fase.name,85,135,23,AMBAR,"titulo")
        texto(s,"Âmbar · Lume     Alvo verde · próximo passo     Círculo · marco",85,168,14,PALIDO)
        mapa_local(s,j,(85,197,780,153))
        alvo=alvo_local(j)
        texto(s,texto_curto(j.objetivo,780,17,"forte"),85,362,17,OSSO,"forte")
        if alvo:
            # O relato completo fica no diário; a faixa ao vivo mantém uma ação.
            for n,linha in enumerate(linhas(alvo.detalhe,780,15)[:2]):
                texto(s,linha,85,390+n*19,15,PALIDO)
        reliquias=getattr(j.bolsa,"reliquias",())
        if reliquias:
            bonus=[]
            if j.bolsa.bonus_dano>1: bonus.append(f"dano +{round((j.bolsa.bonus_dano-1)*100)}%")
            if j.bolsa.bonus_velocidade>1: bonus.append(f"movimento +{round((j.bolsa.bonus_velocidade-1)*100)}%")
            if j.bolsa.fator_dreno<1: bonus.append(f"gasto de luz −{round((1-j.bolsa.fator_dreno)*100)}%")
            texto(s,texto_curto("Relíquias ativas · "+" · ".join(bonus),780,13),85,436,13,AMBAR)
        else:
            texto(s,"K   um clarão revela o rumo do objetivo por alguns instantes",85,436,13,TEAL)
    
    elif a.pagina==1:
        texto(s,"As quatro raízes da figueira",85,143,23,AMBAR,"titulo")
        texto(s,"Reacenda as raízes para levar orvalho de volta às margens.",85,177,17,PALIDO)
        for n,nome in enumerate(("Bosque","Córrego","Taquaral","Gruta")):
            x=173+n*200
            if n<3: pygame.draw.line(s,TEAL,(x+8,260),(x+192,260),1)
            feito="raiz" in j.historico.get((j.volta,n),())
            losango(s,x,260,10,AMBAR if n==j.etapa or feito else TEAL,feito)
            if n==j.etapa: pygame.draw.circle(s,OSSO,(x,260),18,1)
            texto(s,nome if (j.volta,n) in j.historico else "···",x,295,19,OSSO,"titulo","centerx")
        texto(s,"Pedidos dos moradores",85,350,16,AMBAR,"forte")
        paragrafo(s,j.pedido_local or "Converse com os moradores para descobrir pedidos e recompensas.",85,379,765,16,PALIDO)
    elif a.pagina==2 and tem_corte:
        from .corte_vertical import desenhar_mapa
        texto(s,"Corte da Figueira",85,130,25,AMBAR,"titulo")
        desenhar_mapa(s,j,pygame.Rect(84,173,780,264))
    else:
        nome,msg=j.diario[a.pagina-2-int(tem_corte)]
        texto(s,nome,84,161,30,AMBAR,"titulo")
        paragrafo(s,msg,84,221,750,22)
    texto(s,"Esquerda / direita   mudar página     Tab / Esc   fechar",84,465,15,PALIDO)


def registro(a,s):
    m=ambiental.MENSAGENS[a.registro_etapa]
    livro(a,s,m["bioma"],"REGISTRO DA RAIZ   "+ROMANOS[a.registro_etapa])
    titulo, trecho = RAIZES[a.registro_etapa]
    texto(s,titulo,83,137,21,AMBAR,"titulo")
    paragrafo(s,trecho,83,170,369,16)
    texto(s,"No caderno de campo",481,137,21,AMBAR,"titulo")
    paragrafo(s,m["mensagem"],481,170,389,16)
    texto(s,m["pergunta"],83,271,18,OSSO,"forte")
    if a.resposta is None:
        opcoes(a,s,m["opcoes"],77,303,795,38,16)
    else:
        certo=m["correta"]==a.resposta
        texto(s,"A folha confirma sua leitura." if certo else "A folha guarda outra pista.",83,309,20,AMBAR,"titulo")
        paragrafo(s,m["explicacao"],83,346,755,17)
    texto(s,"Enter   confirmar     Esc   seguir viagem",83,460,15,PALIDO)


def capitulo(a,s):
    j=a.jogo
    s.blit(imagem(f"fundo_{j.etapa}.jpg",960,540),(0,0))
    s.blit(placa(960,540,116),(0,0))
    painel(s,(60,288,840,183))
    texto(s,"TRAVESSIA   "+ROMANOS[j.etapa],83,304,14,AMBAR,"forte")
    texto(s,j.fase.name,81,330,37,OSSO,"titulo")
    paragrafo(s,ENTRADAS[j.etapa],83,389,780,18)
    texto(s,"Enter   ·   continuar",873,443,14,PALIDO,"normal","right")


def fim(a,s):
    j=a.jogo
    if a.ensaio==INDICE_ARANHA:
        livro(a,s,"Duelo concluído","GALERIA DA SEDA")
        texto(s,f"Semente {j.semente}   ·   {j.tempo:.1f} s",84,162,23,AMBAR,"titulo")
        texto(s,f"Avisos da aranha: {j.inimigos[0].sequencia}",84,219,18,OSSO)
        texto(s,a.aviso_replay,84,256,16,PALIDO)
        opcoes(a,s,a.fim_nomes(),77,346,470,40)
        return
    chave=j.estado if j.modo=="historia" else "infinito"
    titulo,msg=FINAL[chave]
    livro(a,s,titulo,"DESFECHO")
    y = paragrafo(s,msg,82,146,770,20)
    desdobramento = epilogo(j) if chave == "vitoria" else ""
    if desdobramento:
        y = paragrafo(s,desdobramento,82,y+14,765,17,PALIDO)
    texto(s,f"{j.restauradas} raízes acesas    ·    {j.pontuacao} pontos    ·    {int(j.tempo//60)} min {int(j.tempo%60):02d} s",83,y+20,17,AMBAR,"forte")
    opcoes(a,s,a.fim_nomes(),77,max(342,y+73),400,40)


def recordes(a,s):
    livro(a,s,"Recordes","CADERNO DE CAMPO")
    rows=a.mem.recordes()
    if not rows: paragrafo(s,"Conclua uma jornada para gravar o primeiro resultado.",85,168,724,20)
    for i,(modo,n,p,fase) in enumerate(rows):
        y=159+102*i
        texto(s,"História" if modo=="historia" else "Infinito",84,y,27,AMBAR,"titulo")
        texto(s,f"{n} jornada(s) encerrada(s)     ·     {p} pontos de recorde     ·     trecho {fase}",85,y+44,17)
    texto(s,"Esc ou Enter   ·   voltar",84,462,15,PALIDO)
