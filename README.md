# QuePedaço ☠️

Paródia do [WhatPiece](https://whatpiece.com). Um site com **16 minijogos**
de One Piece, desafio novo todo dia e modo treino livre.

> O projeto não tem fins comerciais nem busca violar direitos autorais.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Depois abre `http://127.0.0.1:5000` no navegador.

Opcional: para expor na internet com ngrok, defina o token antes de rodar
(não deixe o token no código):

```bash
export NGROK_AUTHTOKEN="seu_token_aqui"
python app.py
```

## De onde vêm os dados

A base **não é mais um dicionário fixo**. Ela é montada por `fontes.py`:

| Fonte | O que traz |
|-------|------------|
| **API One Piece** — `https://api.api-onepiece.com/v2` | Fonte principal: ~786 personagens, 213 frutas e 149 tripulações (nome, altura, idade, recompensa, tripulação, fruta, status) |
| **OnePieceQL** — `https://onepieceql.up.railway.app/graphql` | Enriquecimento: origem (Blue), estreia no anime e afiliações de ~1.345 personagens |
| **`dados.py`** (dicionário local) | Complemento: gênero, raça, haki, risada, arco, frases, grupos (Connections/Impostor) e Jolly Rogers — campos que as APIs públicas não oferecem |

O resultado é gravado em `cache/personagens.json` e reaproveitado. O primeiro
build baixa tudo da rede; depois o site funciona **sem internet**. Para atualizar:

```bash
python fontes.py --atualizar
```

Se a rede falhar e não houver cache, o site cai de volta no dicionário local
(a home avisa que está em "modo offline").

## Os jogos

| Jogo | Rota | O que é |
|------|------|---------|
| Adivinhar Personagem | `/personagens` | Descubra o personagem do dia com dicas de cor |
| Wordle | `/wordle` | Adivinhe o nome em 6 tentativas |
| Pirâmide | `/piramide` | Ordene 10 personagens (altura, recompensa, idade...) |
| Grid | `/grid` | Ache quem cumpre a linha **e** a coluna |
| Maior ou Menor | `/maior-menor` | Compare recompensas em 20 rodadas |
| Connections | `/connections` | Encontre os 4 grupos escondidos |
| Bingo | `/bingo` | Complete a cartela de condições |
| Wanted | `/wanted` | Reconheça o cartaz embaçado |
| Adivinhar Fruta | `/fruta` | De quem é essa Fruta do Diabo? |
| Jolly Roger | `/jolly-roger` | De quem é essa bandeira? |
| Impostor | `/impostor` | Ache quem não pertence ao grupo |
| Identidade | `/identidade` | Perguntas de sim/não até descobrir |
| Adivinhar a Risa | `/risa` | De quem é essa risada? |
| Sopa de Letras | `/sopa` | Encontre os nomes escondidos |
| Adivinhar Episódio | `/episodio` | Em que episódio o personagem estreou? |
| Nakama Draft | `/draft` | Monte a tripulação com orçamento |

## Como está organizado

```
OquePiece/
├── app.py          # rotas Flask e regras de sessão
├── jogos.py        # a lógica de cada jogo (dá pra testar sem subir servidor)
├── fontes.py       # camada de dados: API + OnePieceQL + dicionário
├── dados.py        # complemento local: gênero, haki, grupos, frases, risadas
├── cache/          # JSON baixado das APIs (gerado por fontes.py)
├── testes.py       # integridade da base + geradores em várias seeds
├── teste_jogo.py   # testa a jogabilidade (POSTs) com o test client do Flask
├── smoke.sh        # sobe o servidor e bate em todas as rotas
├── templates/      # um HTML por jogo + base + home
└── static/
    ├── css/estilo.css
    └── img/        # fotos opcionais (o resto vira retrato SVG na hora)
```

### Desafio do dia x treino

Cada gerador aceita uma `seed`. Sem seed, a semente vem da data (`_semente`), então
todo mundo joga o mesmo desafio no mesmo dia. Com `?treino=1`, a seed é sorteada e o
jogo vira modo livre.

## Testes

```bash
python testes.py       # integridade da base + geradores
python teste_jogo.py   # jogabilidade (POSTs, sessão, vitória)
bash smoke.sh          # todas as rotas respondem 200 sem traceback
```

## Retratos

Quase todos os personagens usam um retrato SVG desenhado na hora (`retrato_svg` em
`jogos.py`): caveirinha com as iniciais e cores estáveis por nome. O dicionário
local ainda pode apontar pra uma foto em `static/img`.
