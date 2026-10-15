# -*- coding: utf-8 -*-
"""Funções dos jogos do QuePedaço.

A ideia é deixar a regra de cada jogo aqui e o app.py só chamar.
Assim dá pra testar cada jogo sem subir o servidor.

Cada gerador aceita um "seed" opcional:
  - sem seed  -> desafio do dia (igual pra todo mundo naquele dia)
  - com seed  -> modo treino (aleatório a cada partida)
"""

import hashlib
import random
from datetime import date

from dados import PERSONAGENS, FRUTAS, GRUPOS, JOLLY_ROGERS, FRASES

# índice por nome pra busca rápida
POR_NOME = {p["nome"]: p for p in PERSONAGENS}


def pegar(nome):
    return POR_NOME.get(nome)


# ------------------------------------------------------------------
# Sorteio "do dia": mesma coisa pra todo mundo no mesmo dia.
# ------------------------------------------------------------------
def _semente(sal, seed=None):
    if seed is not None:
        return seed
    hoje = date.today().isoformat()
    bruto = f"{hoje}|{sal}".encode("utf-8")
    return int(hashlib.sha256(bruto).hexdigest(), 16)


def do_dia(lista, sal, seed=None):
    if not lista:
        return None
    r = random.Random(_semente(sal, seed))
    return lista[r.randrange(len(lista))]


# ------------------------------------------------------------------
# Retrato em SVG (não precisa de imagem pronta)
# ------------------------------------------------------------------
PALETA = [
    ("#ff9000", "#7a3d00"), ("#26d07c", "#0d5c37"), ("#3d8bfd", "#123a75"),
    ("#e8433f", "#6e1512"), ("#9b5de5", "#3f1c68"), ("#f2c14e", "#7a5b0a"),
    ("#2ec4b6", "#0d5a52"), ("#ff6b9d", "#7a2247"),
]


def cor_do_nome(nome):
    h = sum(ord(c) for c in nome)
    return PALETA[h % len(PALETA)]


def iniciais(nome):
    partes = [p for p in nome.replace(".", " ").split() if p]
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def retrato_svg(nome, largura=200, altura=200):
    """Caveirinha com iniciais, cores estáveis por nome."""
    claro, escuro = cor_do_nome(nome)
    letras = iniciais(nome)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{claro}"/>
      <stop offset="1" stop-color="{escuro}"/>
    </linearGradient>
  </defs>
  <rect width="{largura}" height="{altura}" fill="url(#g)"/>
  <circle cx="{largura/2}" cy="{altura*0.42}" r="{altura*0.24}" fill="rgba(0,0,0,0.28)"/>
  <circle cx="{largura*0.42}" cy="{altura*0.40}" r="{altura*0.045}" fill="#fff"/>
  <circle cx="{largura*0.58}" cy="{altura*0.40}" r="{altura*0.045}" fill="#fff"/>
  <rect x="{largura*0.47}" y="{altura*0.47}" width="{largura*0.06}" height="{altura*0.07}" fill="#fff"/>
  <text x="50%" y="{altura*0.90}" text-anchor="middle" font-family="Verdana, sans-serif"
        font-size="{altura*0.13}" font-weight="bold" fill="#fff">{letras}</text>
</svg>"""


# ------------------------------------------------------------------
# Comparação do "Adivinhar Personagem"
# ------------------------------------------------------------------
def _classe_exata(a, b):
    return "correto" if a == b else "errado"


def _classe_haki(a, b):
    ca, cb = set(a.split()), set(b.split())
    if ca == cb:
        return "correto"
    if ca & cb:
        return "parcial"
    return "errado"


def _seta(a, b):
    if a < b:
        return "⬆️"
    if a > b:
        return "⬇️"
    return ""


def comparar(chute, secreto):
    """Devolve o quadro de comparação de um palpite."""
    return {
        "nome": chute["nome"],
        "foto": chute["foto"],
        "genero": {"valor": chute["genero"], "classe": _classe_exata(chute["genero"], secreto["genero"])},
        "raca": {"valor": chute["raca"], "classe": _classe_exata(chute["raca"], secreto["raca"])},
        "afiliacao": {"valor": chute["afiliacao"], "classe": _classe_exata(chute["afiliacao"], secreto["afiliacao"])},
        "status": {"valor": chute["status"], "classe": _classe_exata(chute["status"], secreto["status"])},
        "fruta": {"valor": chute["fruta"], "classe": _classe_exata(chute["fruta"], secreto["fruta"])},
        "haki": {"valor": chute["haki"], "classe": _classe_haki(chute["haki"], secreto["haki"])},
        "origem": {"valor": chute["origem"], "classe": _classe_exata(chute["origem"], secreto["origem"])},
        "arco": {"valor": chute["arco"], "classe": _classe_exata(chute["arco"], secreto["arco"])},
        "recompensa": {
            "valor": formatar_berries(chute["recompensa"]),
            "classe": _classe_exata(chute["recompensa"], secreto["recompensa"]),
            "seta": _seta(chute["recompensa"], secreto["recompensa"]),
        },
        "altura": {
            "valor": f"{chute['altura']:.2f} m".replace(".", ","),
            "classe": _classe_exata(chute["altura"], secreto["altura"]),
            "seta": _seta(chute["altura"], secreto["altura"]),
        },
        "idade": {
            "valor": f"{chute['idade']} anos",
            "classe": _classe_exata(chute["idade"], secreto["idade"]),
            "seta": _seta(chute["idade"], secreto["idade"]),
        },
        "episodio": {
            "valor": f"Ep. {chute['episodio']}",
            "classe": _classe_exata(chute["episodio"], secreto["episodio"]),
            "seta": _seta(chute["episodio"], secreto["episodio"]),
        },
        "venceu": chute["nome"] == secreto["nome"],
    }


def formatar_berries(valor):
    if not valor:
        return "Sem recompensa"
    return f"{valor:,}".replace(",", ".") + " Berries"


# ------------------------------------------------------------------
# Wordle
# ------------------------------------------------------------------
def avaliar_wordle(palpite, alvo):
    """Devolve lista de 'certo' / 'parcial' / 'errado' por letra."""
    palpite = palpite.upper()
    alvo = alvo.upper()
    resultado = ["errado"] * len(palpite)
    restante = list(alvo)
    for i, letra in enumerate(palpite):
        if i < len(alvo) and letra == alvo[i]:
            resultado[i] = "certo"
            restante[i] = None
    for i, letra in enumerate(palpite):
        if resultado[i] == "certo":
            continue
        if letra in restante:
            resultado[i] = "parcial"
            restante[restante.index(letra)] = None
    return resultado


# ------------------------------------------------------------------
# Condições pros jogos de Grid / Bingo / Impostor
# ------------------------------------------------------------------
def _e_pirata(p):
    return p["afiliacao"].startswith("Piratas") or p["afiliacao"] in ("Cross Guild", "Barto Club")


def _e_marinha(p):
    return p["afiliacao"] == "Marinha"


def _tem_fruta(p):
    return p["fruta"] != "Nenhuma"


def _tem_haki(p):
    return p["haki"] != "Nenhum"


def _e_logia(p):
    return p["fruta_tipo"] == "Logia"


def _e_zoan(p):
    return p["fruta_tipo"].startswith("Zoan")


def _e_paramecia(p):
    return p["fruta_tipo"].startswith("Paramecia")


def _tem_recompensa(p):
    return p["recompensa"] > 0


def _e_mulher(p):
    return p["genero"] == "Feminino"


def _e_homem(p):
    return p["genero"] == "Masculino"


def _recompensa_1b(p):
    return p["recompensa"] >= 1000000000


def _altura_2m(p):
    return p["altura"] >= 2.0


def _idade_40(p):
    return p["idade"] >= 40


def _e_espada(p):
    return p["nome"] in ("Roronoa Zoro", "Dracule Mihawk", "Tashigi", "Brook",
                         "Cavendish", "Killer", "Shimotsuki Koushirou", "Kuina")


CONDICOES = [
    {"texto": "Usa Fruta do Diabo", "teste": _tem_fruta},
    {"texto": "Não usa Fruta", "teste": lambda p: not _tem_fruta(p)},
    {"texto": "Usa Haki", "teste": _tem_haki},
    {"texto": "Fruta do tipo Logia", "teste": _e_logia},
    {"texto": "Fruta do tipo Zoan", "teste": _e_zoan},
    {"texto": "Fruta do tipo Paramecia", "teste": _e_paramecia},
    {"texto": "É pirata", "teste": _e_pirata},
    {"texto": "É da Marinha", "teste": _e_marinha},
    {"texto": "É mulher", "teste": _e_mulher},
    {"texto": "É homem", "teste": _e_homem},
    {"texto": "Recompensa ≥ 1 bilhão", "teste": _recompensa_1b},
    {"texto": "Tem recompensa", "teste": _tem_recompensa},
    {"texto": "Sem recompensa", "teste": lambda p: not _tem_recompensa(p)},
    {"texto": "Altura ≥ 2 m", "teste": _altura_2m},
    {"texto": "Idade ≥ 40 anos", "teste": _idade_40},
    {"texto": "Nasceu no East Blue", "teste": lambda p: p["origem"] == "East Blue"},
    {"texto": "Nasceu no North Blue", "teste": lambda p: p["origem"] == "North Blue"},
    {"texto": "Nasceu no Grand Line", "teste": lambda p: p["origem"] == "Grand Line"},
    {"texto": "Está morto", "teste": lambda p: p["status"] == "Morto"},
    {"texto": "Lutou com espada", "teste": _e_espada},
    {"texto": "Capitão ou líder", "teste": lambda p: any(
        p["afiliacao"].startswith(x) for x in ("Piratas", "Cross Guild", "Barto Club", "Exército")
    )},
    {"texto": "Apareceu antes do ep. 100", "teste": lambda p: p["episodio"] < 100},
]


def casa_condicao(cond, pessoa):
    try:
        return bool(cond["teste"](pessoa))
    except Exception:
        return False


def gerar_grid(seed=None):
    """Monta um 3x3 com condições de linha e coluna que tenha solução."""
    r = random.Random(_semente("grid", seed))
    condicoes = r.sample(CONDICOES, len(CONDICOES))
    for _ in range(300):
        linhas = r.sample(condicoes, 3)
        colunas = r.sample(condicoes, 3)
        solucao = _resolver_grid(linhas, colunas, r)
        if solucao:
            return {
                "linhas": [c["texto"] for c in linhas],
                "colunas": [c["texto"] for c in colunas],
                "solucao": [p["nome"] for p in solucao],
            }
    return None


def _resolver_grid(linhas, colunas, r, orcamento=8000):
    """Acha 9 personagens distintos (um por casa). None se não der.

    Usa a heurística da variável mais restrita (MRV): a cada passo resolve a
    casa com menos candidatos disponíveis. Sem isso o backtracking puro explode
    quando a combinação de condições é insolúvel.
    """
    celulas = []
    for i in range(3):
        for j in range(3):
            candidatos = [p for p in PERSONAGENS
                          if casa_condicao(linhas[i], p) and casa_condicao(colunas[j], p)]
            if not candidatos:
                return None
            r.shuffle(candidatos)
            celulas.append({"i": i, "j": j, "cands": candidatos})

    usado = set()
    resultado = [None] * 9
    passos = [0]

    def backtrack(restantes):
        if not restantes:
            return True
        passos[0] += 1
        if passos[0] > orcamento:
            return False
        # escolhe a casa com menos candidatos ainda livres
        escolhida = None
        for cel in restantes:
            livres = [p for p in cel["cands"] if p["nome"] not in usado]
            if escolhida is None or len(livres) < len(escolhida[1]):
                escolhida = (cel, livres)
        cel, livres = escolhida
        if not livres:
            return False
        sobrou = [c for c in restantes if c is not cel]
        pos = cel["i"] * 3 + cel["j"]
        for p in livres:
            usado.add(p["nome"])
            resultado[pos] = p
            if backtrack(sobrou):
                return True
            usado.discard(p["nome"])
            resultado[pos] = None
        return False

    if backtrack(celulas):
        return resultado
    return None


# ------------------------------------------------------------------
# Connections / Impostor
# ------------------------------------------------------------------
def gerar_connections(seed=None):
    """4 grupos de 4 personagens sem repetir ninguém."""
    r = random.Random(_semente("connections", seed))
    validos = [g for g, membros in GRUPOS.items() if len(membros) >= 4]
    r.shuffle(validos)
    escolhidos = []
    usados = set()
    for grupo in validos:
        membros = [m for m in GRUPOS[grupo] if m in POR_NOME]
        r.shuffle(membros)
        quatro = membros[:4]
        if len(quatro) < 4:
            continue
        if any(m in usados for m in quatro):
            continue
        usados.update(quatro)
        escolhidos.append({"grupo": grupo, "membros": quatro})
        if len(escolhidos) == 4:
            break
    if len(escolhidos) < 4:
        return None
    return escolhidos


def gerar_impostor(seed=None):
    """Um grupo e um intruso que NÃO pertence a ele."""
    r = random.Random(_semente("impostor", seed))
    validos = [g for g, m in GRUPOS.items() if len(m) >= 4]
    grupo = r.choice(validos)
    membros = [m for m in GRUPOS[grupo] if m in POR_NOME]
    trio = r.sample(membros, 3)
    fora = [p["nome"] for p in PERSONAGENS if p["nome"] not in GRUPOS[grupo]]
    intruso = r.choice(fora)
    opcoes = trio + [intruso]
    r.shuffle(opcoes)
    return {"grupo": grupo, "opcoes": opcoes, "intruso": intruso}


def gerar_impostores(quantidade, seed=None):
    """Vários desafios de impostor de uma vez (pro jogo de 10 rodadas)."""
    r = random.Random(_semente("impostor-lote", seed))
    validos = [g for g, m in GRUPOS.items() if len(m) >= 4]
    desafios = []
    for _ in range(quantidade):
        grupo = r.choice(validos)
        membros = [m for m in GRUPOS[grupo] if m in POR_NOME]
        trio = r.sample(membros, 3)
        fora = [p["nome"] for p in PERSONAGENS if p["nome"] not in GRUPOS[grupo]]
        intruso = r.choice(fora)
        opcoes = trio + [intruso]
        r.shuffle(opcoes)
        desafios.append({"grupo": grupo, "opcoes": opcoes, "intruso": intruso})
    return desafios


# ------------------------------------------------------------------
# Pirâmide
# ------------------------------------------------------------------
CATEGORIAS_PIRAMIDE = [
    {"chave": "altura", "texto": "Altura"},
    {"chave": "recompensa", "texto": "Recompensa"},
    {"chave": "idade", "texto": "Idade"},
    {"chave": "episodio", "texto": "Estreia no anime"},
]


def gerar_piramide(seed=None):
    r = random.Random(_semente("piramide", seed))
    categoria = r.choice(CATEGORIAS_PIRAMIDE)
    if categoria["chave"] == "recompensa":
        pool = [p for p in PERSONAGENS if p["recompensa"] > 0]
    else:
        pool = list(PERSONAGENS)
    escolhidos = r.sample(pool, 10)
    escolhidos.sort(key=lambda p: p[categoria["chave"]], reverse=True)
    return {
        "categoria": categoria["texto"],
        "chave": categoria["chave"],
        "ordem": [p["nome"] for p in escolhidos],
    }


# ------------------------------------------------------------------
# Higher or Lower
# ------------------------------------------------------------------
def gerar_higher_lower(seed=None):
    r = random.Random(_semente("higher-lower", seed))
    pool = [p for p in PERSONAGENS if p["recompensa"] > 0]
    return r.sample(pool, 21)


# ------------------------------------------------------------------
# Bingo
# ------------------------------------------------------------------
def gerar_bingo(seed=None):
    r = random.Random(_semente("bingo", seed))
    celulas = r.sample(CONDICOES, 9)
    return {"celulas": [c["texto"] for c in celulas]}


def cond_por_texto(texto):
    for c in CONDICOES:
        if c["texto"] == texto:
            return c
    return None


def bingo_escolher(celulas, travadas, seed=None):
    """Sorteia um personagem que bate com UMA única casa ainda aberta.

    Assim a partida sempre pode ser completada, sem depender de sorte.
    """
    abertas = [i for i in range(len(celulas)) if i not in travadas]
    if not abertas:
        return None
    r = random.Random(_semente("bingo-escolha", seed) + len(travadas))
    r.shuffle(abertas)
    for i in abertas:
        cond = cond_por_texto(celulas[i])
        if not cond:
            continue
        candidatos = [p for p in PERSONAGENS if casa_condicao(cond, p)]
        r.shuffle(candidatos)
        for p in candidatos:
            outras = [j for j in abertas if j != i
                      and casa_condicao(cond_por_texto(celulas[j]), p)]
            if not outras:
                return p["nome"]
    # plano B: qualquer um que bata com alguma casa aberta
    for i in abertas:
        cond = cond_por_texto(celulas[i])
        for p in PERSONAGENS:
            if cond and casa_condicao(cond, p):
                return p["nome"]
    return None


# ------------------------------------------------------------------
# Wanted / Fruta / Risa / Episódio
# ------------------------------------------------------------------
def gerar_wanted(seed=None):
    return do_dia(PERSONAGENS, "wanted", seed)


def gerar_fruta(seed=None):
    return do_dia(FRUTAS, "fruta", seed)


def gerar_risa(seed=None):
    com_risada = [p for p in PERSONAGENS if p["risada"]]
    return do_dia(com_risada, "risa", seed)


def gerar_episodio(seed=None):
    return do_dia(PERSONAGENS, "episodio", seed)


def gerar_jolly_roger(seed=None):
    return do_dia(JOLLY_ROGERS, "jolly-roger", seed)


def gerar_wordle(seed=None):
    candidatos = [p["nome"] for p in PERSONAGENS if len(p["nome"]) <= 14]
    return do_dia(candidatos, "wordle", seed)


def gerar_frase(seed=None):
    return do_dia(FRASES, "frase", seed)


# ------------------------------------------------------------------
# Sopa de letras
# ------------------------------------------------------------------
TAMANHO_SOPA = 12
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gerar_sopa(seed=None):
    r = random.Random(_semente("sopa", seed))
    nomes = [p["nome"] for p in PERSONAGENS]
    alvos = []
    for nome in r.sample(nomes, len(nomes)):
        chave = nome.split()[-1].upper()
        if 4 <= len(chave) <= 8 and chave.isalpha() and chave not in alvos:
            alvos.append(chave)
        if len(alvos) == 8:
            break

    grade = [[r.choice(LETRAS) for _ in range(TAMANHO_SOPA)] for _ in range(TAMANHO_SOPA)]
    posicoes = {}
    for palavra in alvos:
        if _encaixar(grade, palavra, r):
            posicoes[palavra] = True
    return {"grade": ["".join(linha) for linha in grade],
            "palavras": list(posicoes.keys())}


def _encaixar(grade, palavra, r):
    direcoes = [(0, 1), (1, 0), (1, 1)]
    for _ in range(300):
        dr, dc = r.choice(direcoes)
        L = len(palavra)
        if dr == 0:
            lin = r.randrange(TAMANHO_SOPA)
            col = r.randrange(TAMANHO_SOPA - L + 1)
        elif dc == 0:
            lin = r.randrange(TAMANHO_SOPA - L + 1)
            col = r.randrange(TAMANHO_SOPA)
        else:
            lin = r.randrange(TAMANHO_SOPA - L + 1)
            col = r.randrange(TAMANHO_SOPA - L + 1)
        ok = True
        for k, letra in enumerate(palavra):
            l, c = lin + dr * k, col + dc * k
            atual = grade[l][c]
            if atual != letra and atual in palavra:
                ok = False
                break
        if not ok:
            continue
        for k, letra in enumerate(palavra):
            grade[lin + dr * k][col + dc * k] = letra
        return True
    return False


# ------------------------------------------------------------------
# Nakama Draft
# ------------------------------------------------------------------
def gerar_draft(seed=None):
    r = random.Random(_semente("draft", seed))
    pool = [p for p in PERSONAGENS if p["recompensa"] > 0]
    return r.sample(pool, 12)
