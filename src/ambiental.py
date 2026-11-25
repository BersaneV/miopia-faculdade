"""
ambiental.py — conteúdo educativo do Miopia (RF15, RN12 do documento de
Modelagem).

Regra do documento: cada fase concluída entrega **uma mensagem ambiental**
e o conteúdo é apoiado nos ODS 15 (meta 15.5) e ODS 4 (meta 4.7). O texto é
curto, em linguagem simples, e cada fase tem uma **pergunta de compreensão**
avaliada separadamente da habilidade de vencer — errar não custa vida, ponto
nem progresso, só mostra a resposta certa com a explicação.

Nomenclatura (alinhada ao PDF, versão 1.2):
    Fase 1 · Clareira            → Bosque das Samambaias
    Fase 2 · Trilha interrompida → Córrego Fundo
    Fase 3 · Borda da floresta   → Taquaral
    Fase 4 · Último refúgio      → Gruta da Figueira
"""

from __future__ import annotations

FONTE = "ODS 15 · Vida terrestre (meta 15.5) · ODS 4 · Educação de qualidade (meta 4.7)"

MENSAGENS = [
    {
        "fase": "Clareira",
        "bioma": "Bosque das Samambaias",
        "mensagem": (
            "A clareira não é vazia: samambaias, musgo e vaga-lumes dividem o "
            "mesmo canto de mata. Floresta em pé é casa de muita vida pequena."
        ),
        "pergunta": "O que mantém a clareira viva?",
        "opcoes": [
            "Só as árvores grandes.",
            "Várias espécies vivendo juntas no mesmo lugar.",
            "A luz que a lua empresta toda noite.",
        ],
        "correta": 1,
        "explicacao": (
            "Biodiversidade é isso: muitos seres dividindo o mesmo habitat. "
            "Proteger um pedaço de mata é proteger todos eles de uma vez."
        ),
    },
    {
        "fase": "Trilha interrompida",
        "bioma": "Córrego Fundo",
        "mensagem": (
            "A trilha acabou e o córrego virou caminho. Um trecho cortado separa "
            "a mata em dois lados; o corredor verde é a ponte que religa os pedaços."
        ),
        "pergunta": "Para que serve um corredor de floresta?",
        "opcoes": [
            "Para a mata ficar mais bonita nas fotos.",
            "Para ligar pedaços de mata e deixar os bichos passarem.",
            "Para o vento entrar mais forte.",
        ],
        "correta": 1,
        "explicacao": (
            "Corredor verde une habitats separados. Sem ele, cada pedaço de mata "
            "fica ilhado e perde espécies com o tempo."
        ),
    },
    {
        "fase": "Borda da floresta",
        "bioma": "Taquaral",
        "mensagem": (
            "Aqui o vento bate e o sol chega direto: esta é a borda. Quem precisa "
            "de mata fechada fica sem lugar quando a floresta vira pedaços pequenos."
        ),
        "pergunta": "O que acontece quando a mata fica só em pedaços pequenos?",
        "opcoes": [
            "Sobra muita borda e pouca mata fechada.",
            "Os bichos ficam maiores para caber no pedaço.",
            "Nada muda, porque a borda é igual ao meio.",
        ],
        "correta": 0,
        "explicacao": (
            "Pedaço pequeno demais não tem miolo. As espécies que precisam de mata "
            "fechada somem: é o efeito de borda."
        ),
    },
    {
        "fase": "Último refúgio",
        "bioma": "Gruta da Figueira",
        "mensagem": (
            "Este é o último refúgio: o canto de mata que ainda está inteiro. É por "
            "isso que a colônia resistiu. Área protegida é a casa de quem não tem "
            "para onde ir."
        ),
        "pergunta": "Por que a colônia resistiu à noite?",
        "opcoes": [
            "Porque tinha um refúgio inteiro para se esconder e se salvar.",
            "Porque a tempestade parou sozinha.",
            "Porque o Breu gostava dos vaga-lumes.",
        ],
        "correta": 0,
        "explicacao": (
            "Habitat preservado segura a biodiversidade em crise. É a meta 15.5: "
            "reduzir a perda de habitat e proteger a vida que vive nele."
        ),
    },
]
