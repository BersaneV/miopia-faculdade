# A3 · Jogo Original — 26 temas para escolher

**UC:** Usabilidade, desenvolvimento web, mobile e jogos (0011109) · **Prof.:** Elzo Brito dos Santos Filho
**Enunciado lido em:** `usabilidade-web-mobile-jogos/2026-2/atividades/a3-jogo/README.md`
**Valor:** 10,0 · **Grupo:** até 6 · **Rubrica:** 2,0 por critério (Gráfico, Jogabilidade, Som, Documentação, História)

> Este documento é o passo anterior ao código: primeiro o tema e o escopo, depois o projeto.
> O ambiente já está preparado (pygame-ce 2.5.8, captura headless para prints/GIF e síntese de áudio original).

---

## Índice — os 26 temas

**Leva 1 (1 a 8):** temas de arcade, exploração e puzzle, pensados para o menor risco de implementação.
**Leva 2 (9 a 16):** temas com identidade brasileira, esporte de mesa, stealth folclórico, gestão e simulação — inclusive opções boas para **2 jogadores no mesmo teclado**.
**Leva 3 (17 a 26):** gêneros que ainda não apareceram — defesa de base, escavação, pesca, dedução, empilhamento, escalada, memória, resgate, roguelike e dublagem.

| # | Tema | Gênero | Mecânica em uma linha | Esforço | Leva |
|---|---|---|---|---|---|
| 1 | **A Última Mariposa** | Arcade de voo | Voar com inércia, ser atraída/fugir da luz, polinizar flores | ★★☆ | 1 |
| 2 | **Miopia** | Exploração | Você só enxerga um raio de luz em volta do vaga-lume | ★★☆ | 1 |
| 3 | **Curto-Circuito** | Puzzle de conexão | Girar peças e levar energia ao hospital antes do tempo | ★☆☆ | 1 |
| 4 | **Cozinha de Guerra** | Gestão sob pressão | Coletar, montar e entregar pedidos antes do cliente desistir | ★★☆ | 1 |
| 5 | **Faxina Orbital** | Arcade com gravidade | Atrair/repelir lixo espacial usando a gravidade dos planetas | ★★☆ | 1 |
| 6 | **Batida do Bairro** | Ritmo | Acertar 4 teclas no tempo de uma trilha original | ★★★ | 1 |
| 7 | **Porteiro do Infinito** | Triagem | Aprovar ou barrar documentos com regras que mudam | ★☆☆ | 1 |
| 8 | **Corda Bamba** | Cooperação 2P | Dois rebocadores presos por uma corda levam a carga à saída | ★★★ | 1 |
| 9 | **Batalha de Pipas** | Duelo aéreo | Linha tensionada, manobra e vento até derrubar a pipa rival | ★★☆ | 2 |
| 10 | **Futebol de Botão** | Esporte de mesa | Mirar, medir a força e palhetar; torneio em turnos | ★☆☆ | 2 |
| 11 | **Queimada** | Arena de recreio | Carregar, quicar, pegar no ar e reviver os colegas | ★★☆ | 2 |
| 12 | **Guardião do Acervo** | Gestão/ordenação | Devolver livros na prateleira certa antes de fechar a biblioteca | ★☆☆ | 2 |
| 13 | **Curupira: Passos ao Contrário** | Stealth folclórico | Plantar pistas falsas e assustar caçadores sem combate | ★★★ | 2 |
| 14 | **Semáforo Humano** | Puzzle de fluxo | Alternar fases do cruzamento e priorizar a ambulância | ★☆☆ | 2 |
| 15 | **Temporada de Chuvas** | Arcade de resistência | Vencer o vento com o guarda-chuva e chegar seco | ★★☆ | 2 |
| 16 | **Mata Viva** | Simulação ecológica | Plantar, proteger e ver a Mata Atlântica voltar em 5 anos | ★★☆ | 2 |
| 17 | **Horta Defensiva** | Tower defense | Plantar defesas com sinergia e resistir às pragas até a colheita | ★★☆ | 3 |
| 18 | **Poço Fundo** | Escavação com risco | Cavar atrás de água, voltar antes de a lamparina apagar | ★★☆ | 3 |
| 19 | **Rio de Peixes Perdidos** | Pesca e diário | Fisgar, controlar a tensão da linha e completar o diário do avô | ★★☆ | 3 |
| 20 | **O Caso do Elevador** | Dedução narrativa | Entrevistar vizinhos, cruzar depoimentos e achar a contradição | ★☆☆ | 3 |
| 21 | **Mudança** | Puzzle de empilhamento | Fazer tudo caber no caminhão sem a pilha tombar na curva | ★★☆ | 3 |
| 22 | **Andaime** | Escalada de precisão | Subir o prédio em obras com o andaime balançando no vento | ★★☆ | 3 |
| 23 | **Arraiá** | Memória rítmica | Decorar e repetir os passos da quadrilha no tempo da sanfona | ★★☆ | 3 |
| 24 | **Brigada** | Resgate com fumaça | Achar moradores no prédio em chamas e carregá-los para fora | ★★★ | 3 |
| 25 | **Porão 13** | Roguelike | Salas geradas a cada noite, itens, morte permanente e segredos | ★★★ | 3 |
| 26 | **Legenda Viva** | Dublagem/digitação | Dublar as falas do filme digitando no tempo e na emoção certa | ★★☆ | 3 |

⭐ = esforço de implementação (mais estrelas = mais trabalho). **Nenhum dos 26 é "o jogo da aula com outra cor".**

---

## 1. O que o enunciado realmente cobra (e que muda a escolha do tema)

| Critério | Peso | Tradução prática | O que o tema precisa ter |
|---|---|---|---|
| **Gráfico** | 2,0 | Identidade, contraste, HUD legível, **ao menos 1 animação** e feedback visual (partículas, tremor) | Paleta fechada, sprites/forma própria, menu/pausa/fim no mesmo estilo |
| **Jogabilidade** | 2,0 | Mecânica clara, dificuldade crescente, colisão certa, **pausa (P/ESC) e reinício** | Loop curto e viciante + progressão por fases/ondas |
| **Som** | 2,0 | Efeitos nas ações principais + **música em loop**, volume e **silenciar (M)** | Sons para: pulo/tiro/colisão/coleta/dano/vitória/derrota |
| **Documentação** | 2,0 | README com os **10 itens obrigatórios**, pastas `src/` e `assets/`, `requirements.txt`, prints/GIF | Código comentado e nomeado em PT-BR |
| **História** | 2,0 | Premissa, conflito e desfecho **dentro do jogo** (intro, textos entre fases, finais) | Narrativa curta que case com a mecânica |

**Bônus que contam a favor:** 2 jogadores, IA adversária, power-ups, **recorde salvo em arquivo**, opções de volume/dificuldade.

### Linhas vermelhas (do enunciado)

1. **Não vale** Snake, Pong, Breakout ou Space Invaders "da aula" com mudança mínima — e não vale jogo copiado de tutorial/repositório/vídeo. Partir de um gênero conhecido sim, desde que a identidade seja do grupo.
2. **Tecnologia sugerida é Python + pygame-ce.** Outra é aceita, mas precisa justificar no README **e o professor precisa conseguir rodar**. Pygame elimina esse risco.
3. **História tem de aparecer no jogo**, não só no README.
4. **Asset de terceiro exige arquivo, autor, link e licença** nos créditos. Asset sem fonte = tratado como não autorizado.
5. **IA só vale se declarada** no README: ferramenta, finalidade e arquivos.

### Restrições técnicas que valem para qualquer tema

- **Tela 960×540** (16:9) com `pygame.SCALED|RESIZABLE` — funciona em telão e em notebook de laboratório.
- **Rodar offline.** Nada de fonte/imagem por URL na apresentação.
- **Acentos**: fonte que renderize "ação", "você", "pântano". `SysFont("arial")` **não** garante a mesma cara em Linux; nosso padrão é uma TTF empacotada em `assets/fontes/` ou `SysFont` com fallback testado.
- **Som sem ffmpeg**: WAV 44,1 kHz mono gerado em Python (`tools/audio_kit.py`) — `pygame.mixer` carrega nativo, som é do grupo (CC0/autoral), sem risco de crédito.
- **Assets procedurais**: arte desenhada por código (`pygame.draw` + `Surface`), o que dispensa caçar sprites na internet e evita o item 7 (créditos) da rubrica virar problema.

---

## 2. Onde cada tema pontua (e por que não parece cópia)

| # | Tema | Onde pontua mais | Por que não parece cópia da aula |
|---|---|---|---|
| 1 | **A Última Mariposa** | Gráfico + Som | Física suave de aceleração e luz que puxa; nada de colisão de eixo |
| 2 | **Miopia** | Gráfico + História | Fog-of-war **é** a mecânica, não um efeito |
| 3 | **Curto-Circuito** | Jogabilidade + Documentação | Puzzle de grade, gênero que a turma não viu |
| 4 | **Cozinha de Guerra** | Jogabilidade + HUD | Fila, tempo, economia e combos — não é Snake com outra cor |
| 5 | **Faxina Orbital** | Gráfico + Jogabilidade | Campos gravitacionais e combos por órbita |
| 6 | **Batida do Bairro** | Som | Único jogo de ritmo da turma, com trilha autoral |
| 7 | **Porteiro do Infinito** | História + Usabilidade | Decisão por leitura e carimbo; ninguém faz isso |
| 8 | **Corda Bamba** | Jogabilidade (2P) + originalidade | Física de corda + cooperação local |
| 9 | **Batalha de Pipas** | Gráfico + Jogabilidade (2P) | Linha tensionada e vento como sistema, tema brasileiro |
| 10 | **Futebol de Botão** | Documentação + Jogabilidade | Esporte de mesa em turnos, com mira e força |
| 11 | **Queimada** | Jogabilidade (2P) + Som | Arremesso em arco, quique e ressurreição |
| 12 | **Guardião do Acervo** | Usabilidade + Documentação | Ordenação e memória, sem tiro nem reflexo |
| 13 | **Curupira: Passos ao Contrário** | História + Gráfico | Stealth sem combate, com folclore brasileiro |
| 14 | **Semáforo Humano** | Jogabilidade + Documentação | Fluxo e prioridade; erro custa fila, não vida |
| 15 | **Temporada de Chuvas** | Som + Gráfico | Vento como adversário, física de guarda-chuva |
| 16 | **Mata Viva** | História + Gráfico | Simulação com progresso visível ao longo das fases |
| 17 | **Horta Defensiva** | Jogabilidade + Documentação | Tower defense com sinergia entre plantas; ondas em arquivo |
| 18 | **Poço Fundo** | Jogabilidade + Gráfico | Risco × retorno e iluminação por lamparina |
| 19 | **Rio de Peixes Perdidos** | Som + História | Pesca com tensão de linha e diário que vira narrativa |
| 20 | **O Caso do Elevador** | História + Documentação | Dedução: depoimentos, contradições e acusação com provas |
| 21 | **Mudança** | Gráfico + Jogabilidade | Empilhamento físico com teste do caminhão em movimento |
| 22 | **Andaime** | Jogabilidade + Som | Plataforma de precisão com andaime que balança |
| 23 | **Arraiá** | Som + Gráfico | Memória de sequência antes de ritmo; quadrilha brasileira |
| 24 | **Brigada** | História + Som | Fumaça como limite de visão e resgate com peso |
| 25 | **Porão 13** | Jogabilidade + Documentação | Roguelike com salas procedurais por semente |
| 26 | **Legenda Viva** | Som + Jogabilidade | Digitar a fala no tempo e escolher a emoção da dublagem |

⭐ = esforço de implementação (mais estrelas = mais trabalho). **Nenhum dos 16 é "o jogo da aula com outra cor".**

---

## 3. Os temas em detalhe

### 1) A Última Mariposa — *arcade de voo e luz*

> Uma mariposa acorda num jardim onde as flores pararam de abrir. A luz artificial que a guia também a queima. Ela tem cinco noites para polinizar o último jardim antes de o sol não voltar.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Voo com inércia (acelera/derrapa). A luz atrai: perto dela você ganha impulso, mas perde vida. Flores de lua só abrem se você passar por elas; morcegos caçam pelo som. |
| **Loop de 30 s** | Desviar de lâmpadas → coletar néctar (combo) → acordar flores → fugir de morcego → terminar a noite |
| **Progressão** | 5 noites com padrões de luz diferentes (postes, letreiro piscando, estufa). Noite 5 = chefe: holofote que varre a tela e divide o espaço. |
| **História no jogo** | Intro desenhada + 2 falas entre noites; dois finais: jardim salvo (vitória) ou apagão (derrota) |
| **Gráfico** | Fundo noturno (azul-tinta) + peças em âmbar/ciano; rastro de partículas, asas em 3 quadros, tremor + flash no dano, HUD em tarja inferior |
| **Som** | Zumbido de asa por velocidade (SFX), coleta em escala, trilha em loop; M silencia |
| **Controles** | Setas/WASD (voar), Espaço (impulso de asa), P/ESC (pausa), M (som) |
| **Extras** | Recorde em `recorde.txt`, power-up "pólen" (luz própria por 5 s), dificuldade 1–3 |
| **Escopo** | ~700–1.000 linhas; **18–26 pessoas-dia**; sem assets externos |
| **Risco** | Física "escorregadia" demais — calibrar aceleração e atrito cedo, testar com 3 pessoas |

**Encaixe na rubrica:** Gráfico e Som saem quase de graça (partículas, rastro, zumbido); história é naturalmente poética; jogabilidade exige tuning, mas o loop é curto e claro.

---

### 2) Miopia — *exploração com luz*

> Um vaga-lume míope perdeu a colônia na noite da tempestade. Ele só enxerga o que a própria luz alcança — e o que se mexe no escuro não é sempre amigo.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | O mundo é escuro; um círculo de luz acompanha o jogador. Bater nas paredes apaga luz (energia), coletar orvalho reacende. Inimigos andam no escuro e só aparecem quando entram no raio. |
| **Loop de 30 s** | Explorar → achar orvalho → mapear a saída → fugir quando a luz começa a piscar |
| **Progressão** | Labirintos maiores (gerados por semente, para a apresentação não repetir), 4 biomas, chefe cego que caça pelo som |
| **História no jogo** | Intro em texto curto, cartões entre biomas, dois finais (reencontro com a colônia / apagão) |
| **Gráfico** | Preto-azulado + halo de luz com gradiente; mascará de escuridão via `BLEND_MULT`; brilho pulsando (energia), pegadas luminosas |
| **Som** | Batimento cardíaco quando a energia cai, ecos ao andar, trilha ambiente em loop |
| **Controles** | WASD/setas, Shift (piscar = clarão que gasta energia), P/ESC, M |
| **Extras** | Mapa do bioma como item, recorde de tempo, energia salva em arquivo |
| **Escopo** | ~650–950 linhas; **16–24 pessoas-dia** |
| **Risco** | Ficar "escuro demais" e virar frustração — regra de ouro: o raio mínimo nunca é menor que 90 px |

**Encaixe na rubrica:** é o tema com maior potencial de "uau" na apresentação, porque a mecânica **é** o visual. Excelente para Gráfico e História; cuidado com a legibilidade (que é justamente o conteúdo da disciplina).

---

### 3) Curto-Circuito — *puzzle de conexão*

> A tempestade derrubou a rede elétrica e o hospital está no escuro. Você é a equipe de manutenção: gire as peças certas e leve a energia até a tomada crítica antes que o gerador morra.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Grade de peças (reta, curva, T, cruzamento, interruptor). Clique/arrastar gira a peça; energia flui da fonte; se chegar ao hospital, a fase fecha. Tempo e movimentos limitados. |
| **Loop de 30 s** | Ler o tabuleiro → girar 3–5 peças → ver a corrente acender → fase resolvida |
| **Progressão** | 8 fases curtas; entram peça quebrada (precisa de conserto), fusível (limite de carga) e fase noturna com energia piscando |
| **História no jogo** | Intro, falas do rádio entre fases, final: hospital salvo ou cidade às escuras |
| **Gráfico** | Estética de placa de circuito (verde-escuro, trilhas douradas, LED ciano); animação de corrente percorrendo as trilhas, faísca ao errar |
| **Som** | Clique seco ao girar, zumbido crescente da corrente, sirene quando o tempo acaba |
| **Controles** | Mouse (clique esquerdo gira 90°, direito gira ao contrário), R reinicia fase, P/ESC, M |
| **Extras** | Contador de movimentos, estrelas por eficiência, "modo engenheiro" (sem tempo), fases salvas em arquivo |
| **Escopo** | ~600–850 linhas; **14–20 pessoas-dia** (a mais barata de executar bem) |
| **Risco** | Puzzle mal balanceado; mitigação: fases desenhadas à mão em arquivo de texto e testadas por outra pessoa |

**Encaixe na rubrica:** o mais seguro para **Jogabilidade + Documentação**: regras claras, dificuldade crescente, pausa e reinício triviais de provar. Bom para grupos com pouco tempo de código e mais gente para testar/polir.

---

### 4) Cozinha de Guerra — *gestão sob pressão*

> O último food truck de uma cidade sitiada precisa alimentar os moradores durante o toque de recolher. Cada pedido errado custa uma vida; cada combo enche o caixa.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Fila de clientes com paciência. Você anda pelo balcão, pega ingrediente, monta o prato na ordem certa e entrega. Cliente impaciente vai embora. |
| **Loop de 30 s** | Ler pedido → pegar 3 itens → montar → entregar → receber gorjeta |
| **Progressão** | 6 dias (fases) com receitas novas, fila maior, cozinha quebrada; chefe: inspeção sanitária (tempo curto) |
| **História no jogo** | Diálogos dos clientes contam a cidade; final: banquete coletivo (vitória) ou truck fechado (derrota) |
| **Gráfico** | Vista de cima, formas chapadas e sombra dura; sprites de personagem em 4 direções; ícones de pedido no balão; prato montado aparece em camadas |
| **Som** | Sizzle, tábua, caixa registradora, sino do cliente, música por dia |
| **Controles** | WASD/setas (andar), Espaço (interagir), E (entregar), P/ESC, M |
| **Extras** | Gorjeta/combo, upgrade de bancada entre dias, 2P cooperativo local (modo extra) |
| **Escopo** | ~900–1.300 linhas; **22–32 pessoas-dia** (conteúdo: receitas e falas) |
| **Risco** | Escopo de conteúdo cresce fácil — **congelar 6 dias e 8 receitas desde o início** |

**Encaixe na rubrica:** diversão imediata e HUD é fácil de mostrar; história aparece sozinha nos pedidos e falas. Exige mais conteúdo escrito do que código, o que é bom para grupo grande.

---

### 5) Faxina Orbital — *arcade com gravidade*

> A órbita da Terra virou um ferro-velho. Você pilota o coletor "Vassoura-1" e tem quatro órbitas para limpar o corredor antes que o lixo derrube a estação.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Nave com inércia no espaço; ao apertar um botão, o planeta mais próximo atrai (ou repele) a nave e o lixo. Junte detritos numa rede e leve ao contêiner. |
| **Loop de 30 s** | Mirar → puxar detritos com gravidade → agrupar em combo → descarregar no contêiner |
| **Progressão** | 4 órbitas com planetas/luas diferentes; chefe: tempestade solar que desliga a gravidade |
| **História no jogo** | Rádio da estação comentando cada órbita; final: órbita limpa ou colisão |
| **Gráfico** | Paralaxe de estrelas, planetas em camadas, rastro de sucata, explosões particuladas, HUD de combustível |
| **Som** | Motor por aceleração, aviso de proximidade, impacto metálico, trilha espacial em loop |
| **Controles** | Setas (girar/impulsionar), Espaço (campo gravitacional), P/ESC, M |
| **Extras** | Combos por quantidade, recorde de kg em arquivo, escudo limitado |
| **Escopo** | ~800–1.100 linhas; **20–28 pessoas-dia** |
| **Risco** | Gravidade é difícil de "sentir" — protótipo de 1 hora antes de investir em arte |

**Encaixe na rubrica:** visual é o ponto mais forte (paralaxe + partículas); a história "radiofônica" é barata e integrada. Cuidado com o tempo gasto em tuning de física.

---

### 6) Batida do Bairro — *ritmo*

> Os postes de som da cidade foram desligados. Você é o DJ da rua e tem três noites para religar cada quarteirão — no tempo exato da batida.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Quatro pistas (D, F, J, K). Notas descem; acertar na janela soma; erro quebra combo e tira vida. Notas longas exigem segurar. |
| **Loop de 30 s** | Tocar um trecho → combo subir → refrão → fechar a música |
| **Progressão** | 3 músicas originais com dificuldade crescente (BPM e densidade); bônus: dueto com a cidade (2 jogadores no mesmo teclado) |
| **História no jogo** | Cartões entre músicas; final: cidade dançando ou silêncio |
| **Gráfico** | Neon sobre escuro, equalizador reativo, fundo pulsando no BPM, letras de impacto ("PERFEITO!", "COMBO x12") |
| **Som** | **É o jogo** — trilha autoral sintetizada (já temos `tools/audio_kit.py`), SFX de acerto/erro/perfect |
| **Controles** | D F J K, P/ESC, M; opção de offset de latência no menu |
| **Extras** | 2 jogadores no mesmo teclado, ranking em arquivo, calibração de áudio |
| **Escopo** | ~750–1.050 linhas + 3 músicas; **22–30 pessoas-dia** |
| **Risco** | **Sincronia e latência** — se o áudio atrasar, o jogo parece quebrado. Mitigação: mapa de notas em arquivo, offset calibrável e teste em 2 computadores diferentes **antes** de caprichar no visual |

**Encaixe na rubrica:** Som 2,0 praticamente garantido e muita identidade; porém é o tema em que um bug de timing derruba a nota de Jogabilidade. Só escolher se alguém do grupo gostar de música/áudio.

---

### 7) Porteiro do Infinito — *triagem e decisão rápida*

> A estação-portão entre os mundos contratou você como porteiro. Cada viajante traz documentos; as regras mudam a cada turno. Um erro deixa passar algo que não devia — ou barra quem precisava entrar.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Ler o passaporte (nome, planeta, selo, validade), comparar com o **livro de regras do turno** e apertar APROVAR ou BARRAR antes do relógio. |
| **Loop de 30 s** | Puxar documento → conferir 2–3 regras → decidir → carimbo e próximo viajante |
| **Progressão** | Turnos com 1, 2 e 3 regras ativas, regras conflitantes, viajantes que mentem; chefe: auditoria com 5 regras |
| **História no jogo** | Bilhetes dos viajantes contam o mistério da estação; 3 finais (promovido, demitido, ou a verdade) |
| **Gráfico** | Estética de guichê: papel, carimbos, carimbo animado ao apertar; retratos procedurais (olhos, chifres, chapéus); HUD de erros e relógio |
| **Som** | Carimbo, papel, tique-taque, rádio da chefia, trilha burocrática em loop |
| **Controles** | A/← aprovar, D/→ barrar, S (abrir regras), P/ESC, M |
| **Extras** | Regras e viajantes em arquivo de texto (fácil de expandir), recorde de turnos, modo "sem tempo" |
| **Escopo** | ~700–1.000 linhas + tabela de conteúdo; **18–26 pessoas-dia** |
| **Risco** | Sem tempo e sem combo, vira leitura chata — o relógio é o que faz o jogo |

**Encaixe na rubrica:** o mais original da lista e o que mais conversa com a disciplina (hierarquia de informação, contraste, feedback de erro). História é o forte; gráfico simples precisa de carinho nos retratos.

---

### 8) Corda Bamba — *cooperação local*

> Dois rebocadores teimosos estão presos pela mesma corda e precisam levar a carga da estação até a saída. Puxar cada um para seu lado só atrapalha: a corda não perdoa.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Dois rebocadores com propulsão própria, ligados por uma corda com física (mola + amortecimento). A carga fica entre eles. Obstáculos, vento e portões exigem coordenação. |
| **Loop de 30 s** | Combinar direções → passar por um portão → reposicionar a carga → checkpoint |
| **Progressão** | 6 fases com ventos, portões e espinhos; modo solo com IA no segundo rebocador |
| **História no jogo** | Rádio entre os dois pilotos (falas), final: entrega feita ou carga perdida |
| **Gráfico** | Industrial colorido (amarelo-concreto), corda desenhada como polilinha com tensão visível, poeira e faíscas; HUD com dois medidores |
| **Som** | Estalo de corda esticada, motor, impacto, sirene de checkpoint |
| **Controles** | P1: WASD · P2: setas; ESPAÇO freia; P/ESC; M |
| **Extras** | **2 jogadores (bônus explícito)** + IA + medalhas por tempo |
| **Escopo** | ~1.000–1.400 linhas; **26–36 pessoas-dia** (o mais ambicioso da lista) |
| **Risco** | Física da corda e sincronia de teclado no mesmo computador; **só indicar se o grupo tiver um programador confortável com vetores** |

**Encaixe na rubrica:** entrega o bônus de 2 jogadores e uma demonstração ótima de "jogo bom de jogar", mas é o que tem maior chance de bug na apresentação.

---

## 3b. Leva 2 — temas 9 a 16

### 9) Batalha de Pipas — *duelo aéreo (2 jogadores ou IA)*

> No fim da tarde, a laje vira arena: a pipa da sua rua precisa dominar o céu antes da chuva. Sem cerol — aqui a vitória vem de colar a linha na do rival e puxar até derrubar.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | A pipa se move com o vento e com o quanto você solta ou recolhe a linha. Vento muda de direção a cada ~20 s. Encostar a linha na do adversário e **puxar** derruba a pipa dele; a sua perde altitude se recolher demais. |
| **Loop de 30 s** | Ganhar altura → ler o vento → aproximar → colar e puxar → recolher rabiola |
| **Progressão** | Melhor de 3 rounds (manhã, tarde, tempestade); 3 adversários com IA de estilos diferentes (agressivo, paciente, errático) |
| **História no jogo** | Intro dos personagens, provocações entre rounds, dois finais (pipa campeã / linha estourada) |
| **Gráfico** | Céu em gradiente por horário, silhueta de lajes e antenas, pipa com rabiola animada (2 quadros), partículas de vento, HUD de altitude e linha |
| **Som** | Vento em loop com intensidade variável, estalo de linha tensionada, "vruum" do lançamento, trilha de percussão |
| **Controles** | P1: setas + Z (soltar) e X (puxar) · P2: WASD + Q/E (ou IA); P/ESC, M |
| **Extras** | **2 jogadores no mesmo teclado** + IA, melhor de 3, recorde em arquivo |
| **Escopo** | ~800–1.100 linhas; **20–28 pessoas-dia** |
| **Risco** | Física da linha: simplificar como mola entre a mão e a pipa (não simular corda real) |

**Encaixe na rubrica:** tema com identidade brasileira forte e demonstração divertida em 2 jogadores; gráfico do céu rende muito com pouco código. É a melhor opção se o grupo quer o bônus de 2P **sem** a complexidade da corda do tema 8.

---

### 10) Futebol de Botão — *esporte de mesa em turnos*

> O campeonato de botão do bairro vale a mesa do bar no domingo. O seu time é o azarão — e o adversário tem um botão de chumbo.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Turnos alternados: escolhe o botão, mira a seta, mede a força e palheta. Colisão elástica entre botões transfere movimento; bola entra no gol. |
| **Loop de 30 s** | Escolher peça → mirar → dosar força → ver a jogada → reposicionar |
| **Progressão** | 4 times adversários com IA de mira e força diferentes; campos com obstáculos e "regra do bar" (mesa inclinada, toalha) |
| **História no jogo** | Provocações antes de cada time, troféu no final, derrota com o botão quebrado |
| **Gráfico** | Mesa de madeira vista de cima, botões pintados com cores de time, sombras, giz, placar de verdade |
| **Som** | Botão deslizando, "toc" seco do choque, apito, torcida pequena, samba de fundo |
| **Controles** | Mouse (mirar e arrastar a força) + Espaço; alternativa só teclado |
| **Extras** | IA, 2P em turnos no mesmo teclado, torneio salvo em arquivo |
| **Escopo** | ~600–900 linhas; **14–20 pessoas-dia** (turnos eliminam tempo real) |
| **Risco** | Pouco: colisão entre círculos com atrito é simples; a IA é só mirar com erro |

**Encaixe na rubrica:** o **mais seguro de todos** para jogabilidade sem bugs, e a documentação fica fácil (regras de turno explicam-se sozinhas). Gráfico precisa de capricho na mesa e nos botões; história é leve, então capriche nos diálogos.

---

### 11) Queimada — *arena de recreio*

> Último recreio antes da prova. A turma do 2º ano desafiou a sua: quem ficar de pé leva a quadra até o fim do ano.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Arremesso em arco (força + mira), quique na quadra, desvio (rolamento) e **pegar no ar** para reviver um colega. Dois times; quem sai vai para a área dos eliminados. |
| **Loop de 30 s** | Esquivar → pegar a bola → mirar → queimar alguém → reviver um colega |
| **Progressão** | 3 partidas com regras extras: uma bola, duas bolas, quadra dividida; IA de time com funções |
| **História no jogo** | Intro com o sino do recreio, falas curtas entre partidas, final de campeonato |
| **Gráfico** | Quadra colorida vista de cima, personagens em 4 direções (3 quadros), poeira no rolamento, HUD com vivos de cada time |
| **Som** | Apito, impacto, torcida de criança, música animada |
| **Controles** | P1: A/D + Espaço · P2: setas + Enter; IA nos demais; P/ESC, M |
| **Extras** | **2 jogadores**, IA de time, campeonato, tempo de partida configurável |
| **Escopo** | ~800–1.100 linhas; **20–28 pessoas-dia** |
| **Risco** | Janela do "pegar no ar" (timing) e colisão bola-corpo; testar com tolerância generosa |

**Encaixe na rubrica:** jogo que todo mundo entende em 5 segundos — ótimo para demonstrar usabilidade. Som e energia da torcida vendem bem; cuidado para o time da IA não parecer injusto.

---

### 12) Guardião do Acervo — *gestão e ordenação*

> A biblioteca fecha em dez minutos, o carrinho está cheio e o bibliotecário foi ao banheiro. Devolva cada livro na prateleira certa — e ainda atenda quem pede ajuda.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Cada livro tem etiqueta (ex.: `500-C`, `800-B`) e existe uma prateleira correspondente. Carregue até 4, ande pelo corredor, devolva. Errado = livro volta e desconta pontos. Ler o código certo é a habilidade. |
| **Loop de 30 s** | Pegar livro → ler etiqueta → achar prateleira → devolver → atender cliente |
| **Progressão** | 8 dias: mais livros, corredores em U, cliente apressado, livro fora de ordem |
| **História no jogo** | Bilhetes esquecidos dentro dos livros contam a história da biblioteca; dois finais |
| **Gráfico** | Biblioteca vista de cima, paleta quente de madeira, etiquetas grandes e legíveis, marcador de prateleira |
| **Som** | Página virando, bip do leitor, silêncio com trilha suave, "shh" ao correr |
| **Controles** | WASD/setas + E (pegar/devolver), Tab (lista do carrinho), P/ESC, M |
| **Extras** | Recorde em arquivo, modo sem tempo, ordenação alfabética × numérica |
| **Escopo** | ~600–900 linhas; **14–20 pessoas-dia** |
| **Risco** | Ficar monótono — o cliente pedindo livro é o que cria pressão; coloque um já na segunda fase |

**Encaixe na rubrica:** é o tema mais alinhado ao conteúdo de **usabilidade** (hierarquia, leitura, prevenção de erro) e o mais fácil de documentar. Não espere adrenalina: espere nota alta e demonstração tranquila.

---

### 13) Curupira: Passos ao Contrário — *stealth folclórico*

> Os caçadores entraram na mata. O Curupira não quer sangue: quer que eles se percam e voltem para casa. Você assusta, confunde e protege — sem tocar em ninguém.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Sem combate. Você planta **pegadas invertidas** (ilusão), assobia para desviar, apaga tochas e usa o mato. Caçadores têm cone de visão e audição; se te veem, perdem o "mistério". |
| **Loop de 30 s** | Observar patrulha → plantar pista falsa → assustar → sumir no mato |
| **Progressão** | 5 noites com mais caçadores, cães e lanternas; chefe: o caçador cético que exige 3 tipos diferentes de susto |
| **História no jogo** | Intro narrada, diálogos dos caçadores, dois finais: eles desistem (vitória) ou a mata queima (derrota) |
| **Gráfico** | Silhuetas em camadas de neblina, vaga-lumes, paleta verde-noite, animação de passos invertidos e do assobio |
| **Som** | Assobio (a assinatura do jogo), passos, coração acelerado, tambores nas noites |
| **Controles** | WASD (andar), Espaço (assobiar), E (plantar pegada), Shift (esconder), P/ESC, M |
| **Extras** | Medalha "invisível", caderno de folclore no menu, recorde de sustos |
| **Escopo** | ~1.000–1.400 linhas; **26–36 pessoas-dia** |
| **Risco** | IA de patrulha e cones de visão são o coração do jogo — protótipo antes de qualquer arte |

**Encaixe na rubrica:** o tema com a **história mais forte** e o mais original de todos; cultura brasileira com potencial de destaque na banca. Exige grupo com alguém confortável em IA de patrulha. Trate o folclore com respeito e cite as fontes da pesquisa no README.

---

### 14) Semáforo Humano — *puzzle de fluxo*

> Rush da tarde no cruzamento da avenida e o guarda de trânsito faltou. Você assume o apito — e a ambulância já vem vindo.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Controlar as fases do cruzamento (ou os sinais de mão) para escoar filas. Prioridades: ambulância > ônibus > carros. Deixar o cruzamento "fechar a caixa" trava tudo e custa pontos. |
| **Loop de 30 s** | Ler as 4 filas → liberar a via mais cheia → abrir passagem de emergência |
| **Progressão** | 8 turnos com mais faixas, eventos (acidente, passeata, obra) e trânsito noturno |
| **História no jogo** | Rádio da central comentando o caos; final: rush resolvido ou cidade parada |
| **Gráfico** | Diagrama limpo visto de cima, carros como peças coloridas com setas, medidores de fila, contraste alto |
| **Som** | Buzina (medidor de paciência), sirene, apito, trilha calma |
| **Controles** | 1–4 (fases), Espaço (segura tudo), E (emergência), P/ESC, M |
| **Extras** | Modo engenheiro (sandbox), recorde de fluxo, dificuldade |
| **Escopo** | ~600–900 linhas; **14–20 pessoas-dia** |
| **Risco** | Regras confusas quebram o jogo — tutorial sobreposto na primeira fase e **cores + formas** (daltonismo) |

**Encaixe na rubrica:** tema "de adulto" que mostra domínio de regras e feedback — excelente para Jogabilidade. Gráfico simples, mas o HUD precisa ser impecável; a história vem pelo rádio.

---

### 15) Temporada de Chuvas — *arcade de resistência*

> A enchente subiu, o ônibus não passa e você precisa voltar para casa com um guarda-chuva que já foi melhor. Chegue seco — ou chegue.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Andar para a direita com o guarda-chuva como física: incline contra a rajada, e o vento muda de força e direção. Molhar-se enche o medidor de umidade (vida); poças, respingos de carro e granizo tiram mais. |
| **Loop de 30 s** | Ler a rajada que vem → inclinar → passar pela poça → correr no ponto de ônibus |
| **Progressão** | 5 trechos da cidade, rajadas mais fortes, noite, granizo |
| **História no jogo** | Bilhete no bolso explicando por que voltar; final seco × final encharcado, com bilhete diferente |
| **Gráfico** | Silhueta de cidade com camadas de chuva, guarda-chuva deformando (polígono), reflexos nas poças, relâmpagos que iluminam a cena |
| **Som** | Chuva em camadas, trovão, pano batendo no vento, respingo — trilha melancólica em loop |
| **Controles** | ←/→ andar, ↑/↓ inclinar, Espaço correr (gasta mais), P/ESC, M |
| **Extras** | Recorde de "secura" (0–100), fitas e remendos que melhoram o guarda-chuva, dificuldade |
| **Escopo** | ~700–1.000 linhas; **18–24 pessoas-dia** |
| **Risco** | Monotonia: agende um evento a cada 20 s (carro passando, raio, vento forte) |

**Encaixe na rubrica:** o **som** é o protagonista e a história cabe em duas linhas — bom para o critério de Som e para a atmosfera. Ideal para grupo que quer algo bonito e emocional sem muita lógica.

---

### 16) Mata Viva — *simulação ecológica*

> A Mata Atlântica virou pasto. Com cinco anos e uma mochila de sementes, você vai fazer a floresta voltar — uma árvore por vez.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Terreno em grade: escolher espécie nativa conforme solo e água, plantar, regar e proteger de gado e fogo. O medidor de biodiversidade cresce e os bichos voltam em marcos. |
| **Loop de 30 s** | Analisar o solo → plantar 3 mudas → regar → espantar o gado |
| **Progressão** | 5 "anos" (fases) com seca, queimada, gado solto e chuva forte; chefe: incêndio grande |
| **História no jogo** | Caderno de campo com entradas entre fases; dois finais: mata restaurada × terra seca |
| **Gráfico** | Paleta que **muda de marrom a verde** conforme o progresso (payoff visual), camadas de parallax, bichos chegando |
| **Som** | Paisagem sonora que ganha pássaros e insetos a cada fase — o som conta a história junto |
| **Controles** | Mouse (plantar/regar) + atalhos de teclado, P/ESC, M |
| **Extras** | Progresso salvo em arquivo, códice de espécies, modo livre |
| **Escopo** | ~900–1.300 linhas; **22–32 pessoas-dia** |
| **Risco** | Balanceamento dos sistemas e conteúdo de espécies; garanta algo satisfatório nos primeiros 2 minutos |

**Encaixe na rubrica:** melhor tema para **História + Som reforçando a mecânica** (a floresta "soa" e "parece" melhor conforme você joga). O mais "de projeto" da lista; combina com grupos que gostam de pesquisa e conteúdo.

---

## 3c. Leva 3 — temas 17 a 26

> Esta leva troca de gênero de propósito: nada de arcade de reflexo nem de jogo de grade.
> Se o que faltou foi **ação**, olhe 22 e 24. **Cérebro**, 20 e 25. **Calma e beleza**, 19 e 23. **Algo grande e rejogável**, 25. **Humor e originalidade**, 21 e 26.

### 17) Horta Defensiva — *tower defense botânico*

> O concreto tomou o quintal. Sobrou a última horta comunitária do bairro — e as pragas descobriram primeiro. Resista até a colheita.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Plantar defesas nos canteiros ao longo do caminho das pragas. Cada planta tem alcance e cadência, e **sinergia**: manjericão espanta pulgão, cravo-de-defunto atrai predadores, capim-limão deixa a praga lenta. Água de chuva alimenta os aspersores. |
| **Loop de 30 s** | Ler a próxima onda → gastar sementes → posicionar/upar → colher → próxima onda |
| **Progressão** | 3 estações × 10 ondas, com pragas novas (pulgão, lagarta, formiga cortadeira) e chefe de estação: **geada** — exige cobrir os canteiros |
| **História no jogo** | Intro dos vizinhos, bilhetes entre estações, dois finais: festa da colheita ou quintal morto |
| **Gráfico** | Horta vista de cima, plantas em 3 estágios de crescimento, pragas animadas, partículas de pólen e água; HUD de sementes/água/onda |
| **Som** | Pássaros, regador, zumbido de inseto, sino na colheita, trilha calma que acelera nas ondas |
| **Controles** | Mouse (escolher e posicionar), 1–3 (tipo de planta), Espaço (começar onda), P/ESC, M |
| **Extras** | Melhor onda salva em arquivo, 3 dificuldades, enciclopédia de plantas |
| **Escopo** | ~900–1.300 linhas; **22–32 pessoas-dia** |
| **Risco** | Balancear ondas é o trabalho de verdade — coloque as ondas num arquivo de configuração e teste em planilha |

**Encaixe na rubrica:** gênero que todo mundo reconhece, mas com tema e sinergias próprias. **Jogabilidade** e **Documentação** saem fortes (ondas em arquivo = fácil de explicar e ajustar).

---

### 18) Poço Fundo — *escavação com risco e retorno*

> A seca levou o rio. Seu avô dizia que havia água no fundo do poço velho — e também dizia que havia outra coisa.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Cavar para baixo, esquerda e direita numa grade subterrânea. A lamparina é o tempo: quando o óleo acaba, você perde tudo o que está na mochila. Quanto mais fundo, melhor o achado — e maior o perigo (bolsões de gás, pedra dura, água). |
| **Loop de 30 s** | Descer → cavar → encher a mochila → decidir se volta agora ou "só mais um pouco" |
| **Progressão** | 5 poços cada vez mais fundos; loja com 4 melhorias (corda, lamparina, picareta, mochila); meta final: achar o aquífero |
| **História no jogo** | Cartas do avô entre poços; dois finais: água encontrada ou perdido no escuro |
| **Gráfico** | Paleta subterrânea em camadas, luz da lamparina com gradiente, poeira e partículas, HUD de óleo/mochila/profundidade |
| **Som** | Pingos, escavação, madeira estalando, batimento cardíaco com pouco óleo, drone grave |
| **Controles** | Setas (cavar/mover), E (usar corda), P/ESC, M |
| **Extras** | Melhorias e recorde salvos em arquivo, poço com semente, dificuldade |
| **Escopo** | ~800–1.100 linhas; **20–28 pessoas-dia** |
| **Risco** | Economia das melhorias desbalanceada; mantenha **só 4** e ajuste os preços cedo |

**Encaixe na rubrica:** o laço "só mais um pouco" é viciante e fácil de mostrar em 30 s. Iluminação limitada dá **gráfico** bonito com pouco código e o som ambiente segura a tensão.

---

### 19) Rio de Peixes Perdidos — *pesca e diário*

> Você herdou o barco do avô, a vara dele e um diário com 40 peixes que talvez não existam. O primeiro é o que ele nunca conseguiu pescar.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Arremessar (força + direção), esperar a fisgada, e o núcleo: **controlar a tensão da linha** — puxar demais estoura, de menos o peixe foge. Cada captura entra no diário; algumas "capturas" não são peixes (bota, aliança, bilhete) e movem a história. |
| **Loop de 30 s** | Arremessar → fisgar → tensão → registrar → decidir soltar ou vender |
| **Progressão** | 3 rios × 5 pontos, cada um com tabela de peixes própria; equipamento melhora; pesca noturna com lanterna |
| **História no jogo** | O diário se completa conforme você pesca; três finais, incluindo o "peixe que não existe" |
| **Gráfico** | Superfície da água em parallax com ondulações, silhuetas de peixe, barco, caderno desenhado à mão; clima muda por período |
| **Som** | Água batendo no casco, catraca do molinete, pássaros, silêncio — trilha tranquila com violão sintetizado |
| **Controles** | Mouse (arremessar), Espaço (puxar/soltar), Tab (diário), P/ESC, M |
| **Extras** | Diário salvo em arquivo, modo relax (sem tempo), 40 espécies |
| **Escopo** | ~800–1.100 linhas + texto das 40 fichas; **20–28 pessoas-dia** |
| **Risco** | Esperar é chato: fisgadas frequentes e **a tensão é o jogo**, não a espera |
| **Cuidado** | É o tema mais calmo da lista — ótimo contraponto, mas não espere adrenalina |

**Encaixe na rubrica:** o **som** e a **história** carregam sozinhos (o diário é narrativa pura). Gráfico bonito com poucas formas; a mecânica de tensão é simples de explicar.

---

### 20) O Caso do Elevador — *dedução narrativa*

> O elevador parou entre o 7º e o 8º por quarenta minutos. Quando abriu, faltava um quadro — e todos os moradores têm álibi.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Entrevistar 6 vizinhos, ouvir depoimentos e **fixar as falas num mural**, ligando com linha. Quando duas falas se contradizem, você aponta a contradição e ganha uma pergunta nova. No fim, acusa um vizinho com a lista de provas. |
| **Loop de 30 s** | Puxar conversa → escolher pergunta → anotar → ligar duas falas → abrir nova pista |
| **Progressão** | 3 atos: mais depoimentos, um vizinho mente duas vezes e um objeto muda de lugar |
| **História no jogo** | É o jogo inteiro: 6 personagens com motivo e humor, três finais (culpado certo, culpado errado, caso arquivado) |
| **Gráfico** | Corte do prédio com os andares acesos, retratos de formas simples com personalidade, mural de cortiça com barbante; HUD de caderno |
| **Som** | "Ding" do elevador, passos, chuva na janela, trilha noir leve; tema diferente por suspeito |
| **Controles** | Mouse (tudo), 1–4 (opções de fala), Tab (caderno), P/ESC, M |
| **Extras** | Sistema de 3 dicas, modo "sem acusar" (só investigar), final secreto |
| **Escopo** | ~700–1.000 linhas + **muita escrita**; **18–26 pessoas-dia** |
| **Risco** | Consistência do texto: faça uma planilha de fatos (quem, onde, quando) antes de programar |

**Encaixe na rubrica:** o mais forte em **História** e o mais fácil de documentar. Serve para grupo que escreve bem e tem pouco tempo de código — mas o "gráfico" depende dos retratos terem carisma.

---

### 21) Mudança — *puzzle de empilhamento físico*

> O caminhão chega às 18h e o contrato acaba hoje. Tudo o que couber, vai. Tudo o que sobrar, fica — e cada objeto tem uma história.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Arrastar e girar móveis dentro da caçamba. A pilha precisa sobreviver ao **teste do caminhão**, que sacode e freia: se tombar, os frágeis quebram. Pontuação pelo valor e pela quantidade que chega inteira. |
| **Loop de 30 s** | Escolher objetos → empilhar → amarrar → apertar "partir" → ver o estrago |
| **Progressão** | 6 mudanças com caçamba menor, prazo mais curto e itens frágeis; metas opcionais |
| **História no jogo** | Cada objeto tem uma legenda curta; **o que você deixa para trás muda o final** |
| **Gráfico** | Corte lateral da caçamba, móveis com formas e texturas de madeira/tecido, poeira, balanço da pilha; HUD de peso e valor |
| **Som** | Madeira estalando, fita adesiva, motor do caminhão, barulho de queda |
| **Controles** | Mouse (arrastar/girar), Espaço (confirmar), Z (desfazer), P/ESC, M |
| **Extras** | Desfazer infinito, três finais por escolha, recorde de valor salvo em arquivo |
| **Escopo** | ~700–1.000 linhas; **18–24 pessoas-dia** |
| **Risco** | Física de pilha é traiçoeira: use **retângulos rígidos com resolução simples** e teste o "partir" desde o primeiro dia |

**Encaixe na rubrica:** original, engraçado e com um final emocional barato de produzir. **Gráfico** e **Jogabilidade** se destacam; história vem nas legendas dos objetos.

---

### 22) Andaime — *escalada de precisão*

> O prédio em obras não vai se pintar sozinho — e o andaime balança mais do que devia.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Subir com pulo e agarre, com **estamina** que acaba se você segurar muito tempo. O andaime oscila com o vento, então a distância entre as plataformas muda: é preciso esperar o momento certo. Latas de tinta derramam se você pular com força. |
| **Loop de 30 s** | Ler o próximo apoio → esperar o balanço → pular/agarrar → recuperar estamina → checkpoint do andar |
| **Progressão** | 12 andares com pombos, cabos elétricos e rajadas; andares noturnos; chefe final: telhado na tempestade |
| **História no jogo** | Bilhetes dos outros operários; final no letreiro do topo |
| **Gráfico** | Parallax vertical da cidade, vigas e tábuas conectadas, cordas balançando, poeira; HUD de estamina e altura |
| **Som** | Batida de metal, vento em camadas, asas de pombo, ritmo de obra em loop |
| **Controles** | ←/→ + Espaço (pular) + Shift (agarrar), P/ESC, M |
| **Extras** | Recorde de tempo, medalha "sem queda", checkpoint salvo |
| **Escopo** | ~700–1.000 linhas; **18–24 pessoas-dia** |
| **Risco** | Controle precisa ser generoso: **coyote time** e buffer de pulo desde a primeira versão |

**Encaixe na rubrica:** precisão + tensão = **jogabilidade** fácil de demonstrar; o vertical dá um visual que ninguém mais vai ter. Bom para quem quer ação sem física complexa.

---

### 23) Arraiá — *memória rítmica*

> A quadrilha do bairro perdeu o puxador. Agora a dança depende de você lembrar a sequência — e o noivo está atrasado.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Primeiro **decorar**, depois **repetir no tempo**: a dupla mostra 4 passos (olhar, anavan, balancê, passeio) e você repete. A sequência cresce; errar no tempo quebra o combo e espanta a plateia. |
| **Loop de 30 s** | Assistir a sequência → repetir → sequência maior → fechar a música |
| **Progressão** | 6 músicas com BPM e tamanho de sequência crescentes; entram parceiro e plateia |
| **História no jogo** | Noiva atrasada, sanfoneiro e o puxador sumido; dois finais (casamento sai ou festa acaba) |
| **Gráfico** | Bandeirinhas animadas, quadrilha em 3 quadros, confete em partículas, HUD de combo |
| **Som** | Trilha de forró sintetizada (sanfona em onda triangular), passos, palmas, multidão |
| **Controles** | D F J K (ou setas), P/ESC, M; calibração de offset no menu |
| **Extras** | 2 jogadores dividindo os passos, recorde em arquivo, dificuldade |
| **Escopo** | ~700–1.000 linhas + 6 músicas; **18–24 pessoas-dia** |
| **Risco** | Latência: a janela de acerto precisa ser generosa porque **memória** vem antes de **ritmo** |

**Encaixe na rubrica:** **Som** e **Gráfico** com identidade brasileira imediata, e a memória é fácil de explicar em 10 segundos. Diferente do tema 6: aqui o erro é lembrar, não sincronizar.

---

### 24) Brigada — *resgate com fumaça*

> O alarme tocou às 3h. O corredor está cheio de fumaça e ainda tem gente no 5º andar.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Andar em planta baixa com **fumaça que tira visão e ar** (o cilindro é o tempo). Você carrega **uma pessoa por vez**, e ela te deixa mais lento. Portas quentes precisam ser testadas com a mão antes de abrir. Elevador não funciona: é pela escada. |
| **Loop de 30 s** | Entrar → localizar → verificar porta → carregar → descer a escada → entregar/recarregar |
| **Progressão** | 5 prédios com mais moradores, fogo se espalhando e correntes de ar que reacendem focos |
| **História no jogo** | Rádio da central, falas dos moradores; finais variam conforme quantos você salvou |
| **Gráfico** | Planta baixa com camadas de fumaça (blend), fogo tremulando, cone de lanterna, sprite carregando alguém; HUD de ar/resgatados/tempo |
| **Som** | Alarme, respiração ofegante, rugido do fogo, rádio com ruído, música de tensão |
| **Controles** | WASD, E (porta/pegar), Shift (correr, gasta ar), P/ESC, M |
| **Extras** | Medalha por número de resgates, dificuldade, recorde em arquivo |
| **Escopo** | ~1.000–1.400 linhas; **26–36 pessoas-dia** |
| **Risco** | Escopo e legibilidade: prédios feitos **à mão** (não gerados) para não criar labirinto injusto |

**Encaixe na rubrica:** atmosfera e **som** muito fortes; história aparece nas escolhas de quem salvar. Exige equipe disciplinada com o mapa — mas é o tema mais "cinematográfico" da lista.

---

### 25) Porão 13 — *roguelike*

> O elevador desce até um andar que não existe na planta. Cada porta é uma sala diferente, o prédio se refaz toda noite — e alguém já desceu antes de você.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Salas geradas por semente, combate corpo a corpo simples (golpe + esquiva), itens com efeito imediato e morte permanente. Progresso permanente só de conhecimento e chaves. Cada porta oferece uma escolha: tesouro, santuário ou risco. |
| **Loop de 30 s** | Limpar sala → escolher porta → pegar item → sobreviver |
| **Progressão** | 5 noites com inimigos novos; chefe no 13º andar; desbloqueios entre noites |
| **História no jogo** | Bilhetes encontrados revelam o segredo do prédio; três finais |
| **Gráfico** | Monocromático com **uma cor de acento**, salas em tiles, luz piscando, partículas; identidade visual muito forte por pouco custo |
| **Som** | Rangidos, sussurros, batimento, drone que intensifica conforme a vida cai |
| **Controles** | WASD, setas/Espaço (atacar), Shift (esquiva), P/ESC, M |
| **Extras** | Geração por semente (mostrada na tela), desbloqueios salvos, recorde de andares |
| **Escopo** | ~1.200–1.600 linhas; **30–40 pessoas-dia** — o maior da lista |
| **Risco** | Geração e balanceamento: **só escolha se houver um programador forte** e o grupo aceitar cortar escopo |

**Encaixe na rubrica:** rejogabilidade e arquitetura impressionam a banca; **documentação** rende muito (explicar geração procedural no README). É o tema com maior teto e maior chance de atraso.

---

### 26) Legenda Viva — *dublagem e digitação*

> O estúdio perdeu o áudio do filme às 2h da manhã. Você é o dublador de plantão, a sessão começa em dez minutos e o filme é um melodrama péssimo.

| Campo | Definição |
|---|---|
| **Mecânica núcleo** | Digitar a fala **dentro da janela de tempo** da cena e escolher a **emoção** certa (alegre, triste, raiva) para o contexto. Acertar tudo mantém a "sincronia"; errar faz o filme sair do tom e a plateia rir. |
| **Loop de 30 s** | Ler a legenda → digitar no tempo → escolher emoção → cena seguinte |
| **Progressão** | 5 cenas com textos mais longos e mais rápidos; no fim, três personagens para dublar na mesma cena |
| **História no jogo** | O filme dentro do jogo é a história: elenco, diretor nervoso e um final alternativo se você dublar mal de propósito |
| **Gráfico** | Cabine de dublagem com forma de onda reagindo à digitação, personagens atuando no monitor, legenda destacando a próxima palavra; humor no traço |
| **Som** | Sua "voz" vira bipe com tom por emoção, ambiência de estúdio, claquete, risada da plateia |
| **Controles** | Teclado (digitar), 1–3 (emoção), P/ESC, M |
| **Extras** | Modo sem tempo, recorde de precisão em arquivo, "modo livre" com falas aleatórias |
| **Escopo** | ~600–900 linhas + roteiro; **16–24 pessoas-dia** |
| **Risco** | Barreira de digitação: ofereça dificuldade fácil e uma alternativa de escolher entre 3 falas |

**Encaixe na rubrica:** é o mais original da lista e o **som** é o próprio jogo; **jogabilidade** é fácil de entender e de demonstrar em 20 segundos. Ótimo para grupo com pouco tempo de código e muito texto.

---

## 4. Recomendação para este grupo

A rubrica é equilibrada: **não adianta um jogo difícil de mostrar nem um bonito sem regra**. Olhando esforço × impacto:

| Se o grupo... | Escolha | Por quê |
|---|---|---|
| quer a maior nota com risco controlado | **1. A Última Mariposa** | Gráfico e som saem do próprio código (partículas, rastro, zumbido); história curta e coerente; física simples de tunar |
| tem pouco tempo e muita gente para testar/polir | **3. Curto-Circuito** ou **10. Futebol de Botão** | Menos código, mais polimento; jogabilidade e documentação impecáveis são fáceis de demonstrar |
| quer impressionar na apresentação | **2. Miopia**, **5. Faxina Orbital** ou **13. Curupira** | Conceito visual que ninguém da turma vai ter; mecânica = visual |
| quer o bônus de 2 jogadores sem risco alto | **9. Batalha de Pipas** ou **11. Queimada** | Jogo local divertido no telão; física bem mais simples que a corda do tema 8 |
| tem alguém de música/áudio | **6. Batida do Bairro** | Som vale 2,0 e vira o diferencial; exige calibração de latência |
| é um grupo grande, com gente de escrita | **4. Cozinha de Guerra**, **7. Porteiro do Infinito** ou **16. Mata Viva** | Conteúdo (receitas, falas, regras, espécies) distribui bem entre 5–6 pessoas |
| quer algo com identidade brasileira | **9. Batalha de Pipas**, **11. Queimada**, **13. Curupira** ou **23. Arraiá** | Tema cultural reconhecível e com pouca concorrência na turma |
| tem um programador forte e quer ousar | **8. Corda Bamba**, **13. Curupira** ou **25. Porão 13** | Física própria, IA de patrulha ou geração procedural; se der certo, é o mais "uau" |
| quer ação e tensão | **22. Andaime** ou **24. Brigada** | Precisão e resgate; adrenalina sem física complicada (Andaime) ou com atmosfera forte (Brigada) |
| quer um jogo calmo e bonito | **19. Rio de Peixes Perdidos** ou **23. Arraiá** | Som e clima no centro; bom para grupo com gente de arte/música |
| quer algo de "cabeça", com enredo | **20. O Caso do Elevador** | Dedução pura: o código é pequeno e a história é o jogo |
| quer humor e originalidade barata | **21. Mudança** ou **26. Legenda Viva** | Conceito que ninguém espera e execução enxuta |

**Minha escolha padrão: 1. A Última Mariposa** — é a melhor relação entre identidade visual (critério mais subjetivo da banca) e custo de implementação, e a história cabe na mecânica sem texto gigante.

**Se o grupo quiser fugir de "arcade com bichinho/nave":** **18. Poço Fundo** (o laço mais viciante), **20. O Caso do Elevador** (o mais original em história) ou **21. Mudança** (o mais engraçado).

**Pódio por critério da rubrica** (para escolher pelo que o grupo quer garantir):

| Critério | Temas que mais rendem nota |
|---|---|
| Gráfico | 2 Miopia · 1 Mariposa · 9 Pipas · 16 Mata Viva · 21 Mudança |
| Jogabilidade | 3 Curto-Circuito · 10 Futebol de Botão · 17 Horta Defensiva · 18 Poço Fundo · 22 Andaime |
| Som | 6 Batida do Bairro · 19 Rio de Peixes · 23 Arraiá · 24 Brigada |
| Documentação | 3 Curto-Circuito · 12 Guardião do Acervo · 17 Horta · 20 O Caso do Elevador |
| História | 13 Curupira · 16 Mata Viva · 20 O Caso do Elevador · 24 Brigada · 26 Legenda Viva |

---

## 5. Kit de produção já preparado

| Arquivo | O que faz | Status |
|---|---|---|
| `tools/audio_kit.py` | Sintetiza 8 efeitos + trilhas em loop (WAV 44,1 kHz), 100% autoral | ✅ testado |
| `tools/captura.py` | Grava PNGs e GIF **sem monitor**, gerando os prints obrigatórios do README | ✅ testado |
| pygame-ce 2.5.8 | Motor do jogo, mesmo das aulas | ✅ instalado |
| Pillow, numpy, scipy | Suporte a GIF e síntese | ✅ instalados |

**O que eu entrego assim que o tema for escolhido:**

1. `src/main.py` jogável com máquina de estados (menu → jogo → pausa → fim), HUD, recorde em arquivo e volume.
2. Arte procedural própria + paleta fechada, com animação e feedback (partículas, tremor, flash).
3. Efeitos e trilha sintetizados, tecla M e ajuste de volume no menu.
4. `README.md` com os **10 itens obrigatórios** da seção 5, incluindo créditos e declaração de IA.
5. `requirements.txt`, capturas/GIF gerados e roteiro de apresentação.

> Sobre IA: o enunciado permite **desde que declarada**. O README trará a seção dizendo ferramenta, finalidade e arquivos — o grupo deve saber explicar cada trecho.

---

## 6. Checklist do enunciado (referência rápida)

- [ ] Até 6 integrantes, nome e RA no README
- [ ] Jogo original (não é o da aula com mudanças mínimas)
- [ ] Abre, roda do início ao fim e não trava
- [ ] Tela inicial, partida e fim, com jogar de novo / voltar ao menu
- [ ] Vitória ou derrota + pontos, vidas, tempo ou progresso
- [ ] Controles explicados **no jogo** e no README
- [ ] Pausa (P/ESC) e reinício funcionando
- [ ] Gráfico coerente, HUD legível, ao menos 1 animação
- [ ] Música e efeitos equilibrados, opção de silenciar
- [ ] História dentro do jogo (intro + final)
- [ ] README: como rodar, controles, regras, divisão de tarefas, créditos, tecnologia, IA
- [ ] Assets de terceiros com autor, link e licença
- [ ] Tecnologia justificada se não for pygame
- [ ] Instruções testadas em **outro** computador
- [ ] Link entregue com acesso ao professor
- [ ] Apresentação ensaiada, todos sabem explicar o código
