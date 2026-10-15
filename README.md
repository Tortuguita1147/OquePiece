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
oquepiece/
├── app.py          # rotas Flask e regras de sessão
├── jogos.py        # a lógica de cada jogo (dá pra testar sem subir servidor)
├── dados.py        # a base: personagens, grupos, frutas, frases, jolly rogers
├── testes.py       # integridade dos dados + geradores em 400 seeds
├── teste_jogo.py   # testa a jogabilidade (POSTs) com o test client do Flask
├── smoke.sh        # sobe o servidor e bate em todas as rotas
├── templates/      # um HTML por jogo + base + home
└── static/
    ├── css/estilo.css
    └── img/        # fotos opcionais (o resto vira retrato SVG na hora)
```

### Banco de dados

Tudo fica em `dados.py`, em dicionários simples — sem banco de verdade, de propósito,
pra ficar fácil de aumentar. Pra cadastrar um personagem novo, só copiar uma linha:

```python
_p("Nome", "Masculino", "Humano", "Piratas do Chapéu de Palha", "Vivo",
   "Nenhuma", "Nenhuma", NADA,
   0, 1.80, 25, "East Blue", "Romance Dawn", 1, ""),
```

A ordem dos campos está comentada no topo do arquivo.

### Desafio do dia x treino

Cada gerador aceita uma `seed`. Sem seed, a semente vem da data (`_semente`), então
todo mundo joga o mesmo desafio no mesmo dia. Com `?treino=1`, a seed é sorteada e o
jogo vira modo livre.

## Testes

```bash
python testes.py       # dados + 400 seeds por gerador
python teste_jogo.py   # jogabilidade (POSTs, sessão, vitória)
bash smoke.sh          # todas as rotas respondem 200 sem traceback
```

## Números do projeto

- **192 personagens** cadastrados (pretende mais até o fim do ano)
- **25 grupos** pra Connections/Impostor
- **70 Frutas do Diabo**
- **40 frases** pro jogo de quem disse
- **15 Jolly Rogers**
- **16 jogos**

## Retratos

Quase todos os personagens usam um retrato SVG desenhado na hora (`retrato_svg` em
`jogos.py`): caveirinha com as iniciais e cores estáveis por nome.
