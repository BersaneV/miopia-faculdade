# Miopia · A última luz da mata

## Jogar

Instale Python 3.10 a 3.14. No Linux ou macOS, rode `sh ./rodar.sh`. No Windows, abra `rodar.bat`. O atalho prepara as dependências na primeira abertura.

## O jogo

Um raio parte a figueira e apaga o berçário. Lume, o menor dos vaga-lumes, escapa porque seu brilho é fraco demais para o Breu perceber. Com as asas feridas, precisa seguir as raízes a pé. A volta atravessa quatro trechos de Mata Atlântica. Em cada um, a luz revela só o que está perto e o orvalho devolve o fôlego necessário para avançar.

Cada um dos quatro mapas do **modo História** passou de 2.920 para 4.720 px. Há marcos no meio da fase e antes da arena, câmaras inferiores, rotas opcionais, pedidos de moradores e dois desfechos. Em cada bioma, recolha três gotas, opere os mecanismos, passe pela guardiã e devolva a luz à raiz. O **modo Infinito** emenda os biomas sob um relógio contínuo. Patrulhas e posições de orvalho mudam a cada volta. Uma gota dourada devolve oito segundos e as raízes restauradas estendem o relógio.

| Trecho | Descoberta | Guardião |
|---|---|---|
| Bosque das Samambaias | Uma corda alta e a peça da porteira no antigo berçário. | Asa Fendida se prende na raiz marcada após uma investida. |
| Córrego Fundo | Drenar o canal revela a passagem baixa. Uma segunda válvula estende a ponte. | Uma cortina de água interrompe os fios da Tecelã do Vão. |
| Taquaral | Reacender um nó revela apoios de bambu entre dois fragmentos de mata. | Um barril de seiva e a brasa fictícia expõem a armadura do Casco Oco. |
| Gruta da Figueira | A roldana e o contrapeso restabelecem a travessia. | O sino desvia a Coruja cega. Um clarão no instante certo a acalma. |

Ver a travessia em movimento.

## Controles

| Comando | Ação |
|---|---|
| A / D ou setas esquerda e direita | Mover |
| Espaço | Saltar. Solte e aperte outra vez no ar para o salto duplo. Segure durante a queda para planar continuamente. Encostado ao tronco de impulso, o novo toque lança Lume para o lado oposto. |
| S ou seta para baixo | Agachar. Segure para baixo e aperte Espaço sobre grade, galho elevado ou apoio para passar ao nível inferior. Terra e pontes firmes sustentam Lume. |
| Shift + direção | Deslizar |
| E | Usar mecanismos, subir cordas, descansar e conversar |
| J / S + J no ar | Até três cortes em sequência; ataque para baixo com rebote ao acertar. Cortes também interceptam fios e ferrões. |
| K | Clarão fixo no mundo, ao custo de 22 de luz. |
| Q / F | Alternar item / usar o item escolhido (bálsamo, pavio, casulo ou concha). |
| Tab / M / C | Mapa por descoberta / mapa / caderno opcional das raízes restauradas. No mapa, direita abre pedidos; cima/baixo e Enter escolhem o rastreio. |
| P ou Esc | Pausar ou continuar. R na pausa pede confirmação para retornar ao marco. |
| M / F11 | Silenciar ou reativar som / alternar tela cheia |
| Setas e Enter, ou mouse | Escolher nos menus. Enter completa a fala e avança. Esc pula o prólogo. |

A luz pessoal varia de 90 a 128 px e o gasto passivo no modo História caiu 64%. O clarão abre uma clareira de até 296 px, permanece aceso onde foi lançado e se fecha gradualmente ao longo de 6,5 s. O brilho da mata pode ser ajustado em quatro níveis. Volte ao abrigo para recuperar energia. A tela **Você morreu** mostra quando Lume cai ou perde a luz e espera sua confirmação para voltar ao último marco. Portas e itens já conquistados ficam registrados. As conversas, o diário e as perguntas ambientais pausam a simulação. Uma resposta errada apenas revela a explicação.

O morcego segue o brilho. A aranha pode disparar seda, a vespa mira ferrões, a sombra explora a penumbra e o carabídeo protege a frente do corpo. No Taquaral, derrotar a sentinela solta a trama que bloqueia o caminho. Os cinco inimigos anunciam o ataque por som e postura. Os quatro guardiões têm soluções ambientais próprias.

## Dados locais e dificuldade

Ajustes de ambiência, efeitos, brilho, mudo e dificuldade ficam em SQLite, junto do marco de História, dos registros do diário e do histórico de partidas encerradas. Na reabertura, **Continuar história** recupera a campanha no último marco. É possível iniciar um desafio Infinito sem sobrescrever essa campanha. A dificuldade escolhida vale para a próxima jornada. Os níveis ajustam fagulhas, dano e consumo de luz.

No Linux, os dados vão para `$XDG_DATA_HOME/miopia` ou `~/.local/share/miopia`. No Windows, o código usa `%LOCALAPPDATA%/Miopia`. A pasta do jogo pode ser somente leitura.

## Créditos

Projeto A3 da Universidade São Judas Tadeu. Otávio Araújo Aredes Guedes, Caio Vidotte Vrech Sousa, Tiago Ribeiro Gomes, Thierry Henry Rocha da Silva, Victor Bersane Jasaitis e Iago Robert da Silva Andrade.

Ilustrações produzidas com auxílio de OpenAI ImageGen. Os avisos das fontes acompanham os [arquivos de fonte](assets/fontes).
