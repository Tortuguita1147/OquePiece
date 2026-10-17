import os
import random

from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, session, url_for)

import jogos
from fontes import (PERSONAGENS, JOLLY_ROGERS, COMPLETOS, COM_EPISODIO,
                    META, ORIGEM_DADOS)

app = Flask(__name__)
app.secret_key = "quepedaco_chave_secreta_do_mestre_dos_mares"

# índice nome -> personagem (também usado nas buscas)
INDICE = {p["nome"]: p for p in PERSONAGENS}

LISTA_JOGOS = [
    {"nome": "Adivinhar Personagem", "rota": "personagens", "emoji": "🎯",
     "desc": "Descubra o personagem do dia com dicas de cor."},
    {"nome": "Wordle", "rota": "wordle", "emoji": "🔤",
     "desc": "Adivinhe o nome em 6 tentativas."},
    {"nome": "Pirâmide", "rota": "piramide", "emoji": "🔺",
     "desc": "Ordene 10 personagens do maior para o menor."},
    {"nome": "Grid", "rota": "grid", "emoji": "🧩",
     "desc": "Ache o personagem que cumpre linha e coluna."},
    {"nome": "Maior ou Menor", "rota": "higher_lower", "emoji": "💰",
     "desc": "Compare recompensas em 20 rodadas."},
    {"nome": "Connections", "rota": "connections", "emoji": "🔗",
     "desc": "Encontre os 4 grupos escondidos."},
    {"nome": "Bingo", "rota": "bingo", "emoji": "🎟️",
     "desc": "Complete a cartela de condições."},
    {"nome": "Wanted", "rota": "wanted", "emoji": "🪧",
     "desc": "Reconheça o cartaz embaçado."},
    {"nome": "Adivinhar Fruta", "rota": "fruta", "emoji": "🍎",
     "desc": "Descubra de quem é a Fruta do Diabo."},
    {"nome": "Jolly Roger", "rota": "jolly_roger", "emoji": "🏴‍☠️",
     "desc": "De quem é essa bandeira pirata?"},
    {"nome": "Impostor", "rota": "impostor", "emoji": "🕵️",
     "desc": "Ache quem não pertence ao grupo."},
    {"nome": "Identidade", "rota": "identidade", "emoji": "❓",
     "desc": "Perguntas de sim ou não até descobrir."},
    {"nome": "Adivinhar a Risa", "rota": "risa", "emoji": "😆",
     "desc": "De quem é essa risada?"},
    {"nome": "Sopa de Letras", "rota": "sopa", "emoji": "🔎",
     "desc": "Encontre os nomes escondidos na grade."},
    {"nome": "Adivinhar Episódio", "rota": "episodio", "emoji": "📺",
     "desc": "Em que episódio esse personagem estreou?"},
    {"nome": "Nakama Draft", "rota": "draft", "emoji": "⛵",
     "desc": "Monte sua tripulação com orçamento."},
]


# ------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------
def sem_acento(texto):
    trocas = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
              "é": "e", "ê": "e", "è": "e", "í": "i", "î": "i",
              "ó": "o", "ô": "o", "õ": "o", "ö": "o", "ú": "u",
              "û": "u", "ü": "u", "ç": "c"}
    return "".join(trocas.get(c, c) for c in texto.lower().strip())


def achar_personagem(texto):
    if not texto:
        return None
    alvo = sem_acento(texto)
    for nome, p in INDICE.items():
        if sem_acento(nome) == alvo:
            return p
    # aceita só o primeiro nome também (ex.: "luffy")
    for nome, p in INDICE.items():
        if sem_acento(nome).split()[0] == alvo:
            return p
    return None


def modo(jogo):
    """Devolve a seed do modo treino, ou None pro desafio do dia.

    O botão "Treino" chama a rota com ?treino=1, que gera uma seed nova.
    """
    if request.args.get("treino"):
        session[f"{jogo}_seed"] = random.randrange(1, 10 ** 9)
    return session.get(f"{jogo}_seed")


@app.context_processor
def injetar_ajudantes():
    def retrato_url(p):
        if p["foto"]:
            if p["foto"].startswith("http"):
                return p["foto"]
            return url_for("static", filename="img/" + p["foto"])
        return url_for("retrato", nome=p["nome"])

    return {
        "retrato_url": retrato_url,
        "personagem": lambda n: INDICE.get(n),
        "todos_personagens": [p["nome"] for p in PERSONAGENS],
        "lista_jogos": LISTA_JOGOS,
        "meta_dados": META,
        "origem_dados": ORIGEM_DADOS,
    }


app.jinja_env.filters["formato_berries"] = jogos.formatar_berries


# ------------------------------------------------------------------
# Início
# ------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/personagens")
def api_personagens():
    return jsonify([p["nome"] for p in PERSONAGENS])


@app.route("/retrato/<path:nome>")
def retrato(nome):
    svg = jogos.retrato_svg(nome)
    return Response(svg, mimetype="image/svg+xml")


# ------------------------------------------------------------------
# 1) Adivinhar Personagem
# ------------------------------------------------------------------
@app.route("/personagens")
def personagens():
    seed = modo("personagens")
    if "secreto" not in session:
        session["secreto"] = jogos.do_dia(COMPLETOS, "personagem", seed)["nome"]
    if "historico" not in session:
        session["historico"] = []
    return render_template("personagens.html", historico=session["historico"])


@app.route("/palpite", methods=["POST"])
def processar_palpite():
    chute = achar_personagem(request.form.get("nome_busca", ""))
    if not chute:
        return redirect(url_for("personagens"))
    secreto = INDICE.get(session.get("secreto"))
    if not secreto:
        return redirect(url_for("reiniciar"))

    comparacao = jogos.comparar(chute, secreto)
    historico = session.get("historico", [])
    historico.insert(0, comparacao)
    session["historico"] = historico
    return redirect(url_for("personagens"))


@app.route("/reiniciar")
def reiniciar():
    for chave in ("secreto", "historico"):
        session.pop(chave, None)
    return redirect(url_for("personagens"))


# ------------------------------------------------------------------
# 2) Wordle
# ------------------------------------------------------------------
@app.route("/wordle", methods=["GET", "POST"])
def wordle():
    seed = modo("wordle")
    if "wordle_alvo" not in session:
        session["wordle_alvo"] = jogos.gerar_wordle(seed)
        session["wordle_tentativas"] = []

    erro = None
    if request.method == "POST":
        palpite = request.form.get("palpite", "").strip()
        if not achar_personagem(palpite):
            erro = "Esse nome não está cadastrado. Tente outro personagem."
        else:
            tentativas = session["wordle_tentativas"]
            resultado = jogos.avaliar_wordle(palpite, session["wordle_alvo"])
            tentativas.append({"palpite": palpite, "resultado": resultado})
            session["wordle_tentativas"] = tentativas

    alvo = session["wordle_alvo"]
    tentativas = session["wordle_tentativas"]
    venceu = any(t["palpite"].upper() == alvo.upper() for t in tentativas)
    acabou = len(tentativas) >= 6 and not venceu
    return render_template("wordle.html", alvo=alvo, tentativas=tentativas,
                           venceu=venceu, acabou=acabou, erro=erro)


@app.route("/wordle/reiniciar")
def wordle_reiniciar():
    for c in ("wordle_alvo", "wordle_tentativas", "wordle_seed"):
        session.pop(c, None)
    return redirect(url_for("wordle"))


# ------------------------------------------------------------------
# 3) Pirâmide
# ------------------------------------------------------------------
@app.route("/piramide", methods=["GET", "POST"])
def piramide():
    seed = modo("piramide")
    if "pir_ordem" not in session:
        dados = jogos.gerar_piramide(seed)
        session["pir_ordem"] = dados["ordem"]
        session["pir_categoria"] = dados["categoria"]
        session["pir_chave"] = dados["chave"]

    ordem = session["pir_ordem"]
    resultado = None
    if request.method == "POST":
        enviado = request.form.get("ordem", "").split("|")
        acertos = sum(1 for a, b in zip(enviado, ordem) if a == b)
        resultado = {"acertos": acertos, "total": len(ordem),
                     "perfeito": acertos == len(ordem)}

    embaralhada = list(ordem)
    random.Random(session.get("pir_seed", 7)).shuffle(embaralhada)
    return render_template("piramide.html", ordem=ordem, categoria=session["pir_categoria"],
                           chave=session["pir_chave"], embaralhada=embaralhada,
                           resultado=resultado)


@app.route("/piramide/reiniciar")
def piramide_reiniciar():
    for c in ("pir_ordem", "pir_categoria", "pir_chave", "pir_seed"):
        session.pop(c, None)
    return redirect(url_for("piramide"))


# ------------------------------------------------------------------
# 4) Grid
# ------------------------------------------------------------------
@app.route("/grid", methods=["GET", "POST"])
def grid():
    seed = modo("grid")
    if "grid_dados" not in session:
        dados = jogos.gerar_grid(seed)
        session["grid_dados"] = dados

    dados = session["grid_dados"]
    if not dados:
        return render_template("grid.html", dados=None)

    avaliacao = None
    if request.method == "POST":
        if request.form.get("acao") == "revelar":
            avaliacao = {"revelado": True}
        else:
            nomes = [request.form.get(f"casa{i}", "") for i in range(9)]
            marcacao = []
            usados = set()
            acertos = 0
            for i, nome in enumerate(nomes):
                p = achar_personagem(nome)
                if not p:
                    marcacao.append("vazio")
                    continue
                if p["nome"] in usados:
                    marcacao.append("repetido")
                    continue
                ok = _bate(p, dados["linhas"][i // 3]) and _bate(p, dados["colunas"][i % 3])
                if ok:
                    marcacao.append("certo")
                    usados.add(p["nome"])
                    acertos += 1
                else:
                    marcacao.append("errado")
            avaliacao = {"marcacao": marcacao, "acertos": acertos,
                         "venceu": acertos == 9}

    return render_template("grid.html", dados=dados, avaliacao=avaliacao)


def _bate(pessoa, texto_condicao):
    for c in jogos.CONDICOES:
        if c["texto"] == texto_condicao:
            return jogos.casa_condicao(c, pessoa)
    return False


@app.route("/grid/reiniciar")
def grid_reiniciar():
    for c in ("grid_dados", "grid_seed"):
        session.pop(c, None)
    return redirect(url_for("grid"))


# ------------------------------------------------------------------
# 5) Maior ou Menor
# ------------------------------------------------------------------
@app.route("/maior-menor", methods=["GET", "POST"])
def higher_lower():
    seed = modo("higher_lower")
    if "hl_fila" not in session:
        session["hl_fila"] = [p["nome"] for p in jogos.gerar_higher_lower(seed)]
        session["hl_indice"] = 0
        session["hl_placar"] = 0
        session["hl_vidas"] = 3
        session["hl_fim"] = False

    fila = session["hl_fila"]
    i = session["hl_indice"]
    mensagem = None

    if request.method == "POST" and not session["hl_fim"]:
        escolha = request.form.get("escolha")
        atual = INDICE[fila[i]]
        proximo = INDICE[fila[i + 1]]
        maior = proximo["recompensa"] >= atual["recompensa"]
        acertou = (escolha == "maior" and maior) or (escolha == "menor" and not maior)
        if acertou:
            session["hl_placar"] += 1
            session["hl_indice"] += 1
            if session["hl_indice"] >= len(fila) - 1:
                session["hl_fim"] = True
        else:
            session["hl_vidas"] -= 1
            if session["hl_vidas"] <= 0:
                session["hl_fim"] = True
            else:
                session["hl_indice"] += 1
                mensagem = f"Errou! O certo era {'maior' if maior else 'menor'}. Ainda restam {session['hl_vidas']} vidas."
        i = session["hl_indice"]

    acabou = session["hl_fim"]
    atual = INDICE[fila[min(i, len(fila) - 1)]]
    proximo = None
    if i + 1 < len(fila):
        proximo = INDICE[fila[i + 1]]
    return render_template("higher_lower.html", atual=atual, proximo=proximo,
                           placar=session["hl_placar"], vidas=session["hl_vidas"],
                           rodada=i + 1, total=len(fila) - 1, acabou=acabou,
                           mensagem=mensagem)


@app.route("/maior-menor/reiniciar")
def hl_reiniciar():
    for c in ("hl_fila", "hl_indice", "hl_placar", "hl_vidas", "hl_fim", "higher_lower_seed"):
        session.pop(c, None)
    return redirect(url_for("higher_lower"))


# ------------------------------------------------------------------
# 6) Connections
# ------------------------------------------------------------------
@app.route("/connections", methods=["GET", "POST"])
def connections():
    seed = modo("connections")
    if "conn_grupos" not in session:
        session["conn_grupos"] = jogos.gerar_connections(seed)
        session["conn_resolvidos"] = []
        session["conn_vidas"] = 5
        session["conn_erros"] = []

    grupos = session["conn_grupos"]
    if not grupos:
        return render_template("connections.html", grupos=None)

    nomes = []
    for g in grupos:
        nomes.extend(g["membros"])
    nomes.sort(key=lambda n: sum(ord(c) for c in n))
    random.Random(session.get("conn_seed", 3)).shuffle(nomes)

    aviso = None
    if request.method == "POST":
        escolhidos = request.form.getlist("escolhido")
        if len(escolhidos) == 4:
            resolvidos = session["conn_resolvidos"]
            achou = None
            for g in grupos:
                if set(g["membros"]) == set(escolhidos) and g["grupo"] not in resolvidos:
                    achou = g
                    break
            if achou:
                resolvidos.append(achou["grupo"])
                session["conn_resolvidos"] = resolvidos
            else:
                session["conn_vidas"] -= 1
                for g in grupos:
                    if len(set(g["membros"]) & set(escolhidos)) == 3 and g["grupo"] not in resolvidos:
                        aviso = "Quase! Três desses formam um grupo."
                if not aviso:
                    aviso = "Esses quatro não formam um grupo."
        else:
            aviso = "Escolha exatamente 4 personagens."

    resolvidos = session["conn_resolvidos"]
    membros_resolvidos = set()
    for g in grupos:
        if g["grupo"] in resolvidos:
            membros_resolvidos.update(g["membros"])
    restantes = [n for n in nomes if n not in membros_resolvidos]
    venceu = len(resolvidos) == len(grupos)
    return render_template("connections.html", grupos=grupos, nomes=nomes,
                           restantes=restantes, resolvidos=resolvidos,
                           vidas=session["conn_vidas"], aviso=aviso, venceu=venceu)


@app.route("/connections/reiniciar")
def connections_reiniciar():
    for c in ("conn_grupos", "conn_resolvidos", "conn_vidas", "conn_erros", "connections_seed"):
        session.pop(c, None)
    return redirect(url_for("connections"))


# ------------------------------------------------------------------
# 7) Bingo
# ------------------------------------------------------------------
@app.route("/bingo", methods=["GET", "POST"])
def bingo():
    seed = modo("bingo")
    if "bingo_celulas" not in session:
        session["bingo_celulas"] = jogos.gerar_bingo(seed)["celulas"]
        session["bingo_travadas"] = []
        session["bingo_erros"] = 0
        session["bingo_atual"] = jogos.bingo_escolher(session["bingo_celulas"], [], seed)

    celulas = session["bingo_celulas"]
    aviso = None

    if request.method == "POST":
        if request.form.get("acao") == "pular":
            session["bingo_atual"] = jogos.bingo_escolher(celulas, session["bingo_travadas"], seed)
        else:
            casa = int(request.form.get("casa", -1))
            p = INDICE.get(session.get("bingo_atual"))
            cond = jogos.cond_por_texto(celulas[casa]) if 0 <= casa < len(celulas) else None
            if casa in session["bingo_travadas"]:
                aviso = "Essa casa já está marcada."
            elif p and cond and jogos.casa_condicao(cond, p):
                travadas = session["bingo_travadas"]
                travadas.append(casa)
                session["bingo_travadas"] = travadas
                session["bingo_atual"] = jogos.bingo_escolher(celulas, travadas, seed)
            else:
                session["bingo_erros"] += 1
                aviso = "Essa condição não bate com o personagem."

    travadas = session["bingo_travadas"]
    venceu = len(travadas) == 9
    atual = None if venceu else INDICE.get(session.get("bingo_atual"))
    return render_template("bingo.html", celulas=celulas, travadas=travadas,
                           atual=atual, erros=session["bingo_erros"], aviso=aviso,
                           venceu=venceu, acabou=False)


@app.route("/bingo/reiniciar")
def bingo_reiniciar():
    for c in ("bingo_celulas", "bingo_travadas", "bingo_erros", "bingo_atual", "bingo_seed"):
        session.pop(c, None)
    return redirect(url_for("bingo"))


# ------------------------------------------------------------------
# 8) Wanted
# ------------------------------------------------------------------
@app.route("/wanted", methods=["GET", "POST"])
def wanted():
    seed = modo("wanted")
    if "wanted_alvo" not in session:
        session["wanted_alvo"] = jogos.gerar_wanted(seed)["nome"]
        session["wanted_erros"] = 0

    alvo = INDICE[session["wanted_alvo"]]
    dica = False
    erro = None
    if request.method == "POST":
        if request.form.get("acao") == "dica":
            dica = True
        else:
            chute = achar_personagem(request.form.get("palpite", ""))
            if not chute:
                erro = "Personagem não cadastrado."
            elif chute["nome"] == alvo["nome"]:
                session["wanted_venceu"] = True
            else:
                session["wanted_erros"] += 1

    venceu = session.get("wanted_venceu", False)
    erros = session["wanted_erros"]
    # cada erro diminui o desfoque
    borrao = max(0, 14 - erros * 2)
    return render_template("wanted.html", alvo=alvo, erros=erros, borrao=borrao,
                           dica=dica, erro=erro, venceu=venceu)


@app.route("/wanted/reiniciar")
def wanted_reiniciar():
    for c in ("wanted_alvo", "wanted_erros", "wanted_venceu", "wanted_seed"):
        session.pop(c, None)
    return redirect(url_for("wanted"))


# ------------------------------------------------------------------
# 9) Adivinhar Fruta
# ------------------------------------------------------------------
@app.route("/fruta", methods=["GET", "POST"])
def fruta():
    seed = modo("fruta")
    if "fruta_alvo" not in session:
        fruta_dia = jogos.gerar_fruta(seed)
        session["fruta_alvo"] = fruta_dia[0]
        session["fruta_tipo"] = fruta_dia[1]
        session["fruta_usuario"] = fruta_dia[2]
        session["fruta_traducao"] = fruta_dia[3]
        session["fruta_erros"] = 0

    erro = None
    if request.method == "POST":
        chute = achar_personagem(request.form.get("palpite", ""))
        if not chute:
            erro = "Personagem não cadastrado."
        elif chute["nome"] == session["fruta_usuario"]:
            session["fruta_venceu"] = True
        else:
            session["fruta_erros"] += 1

    erros = session["fruta_erros"]
    return render_template("fruta.html", fruta=session["fruta_alvo"],
                           tipo=session["fruta_tipo"], traducao=session["fruta_traducao"],
                           usuario=session["fruta_usuario"],
                           erros=erros, venceu=session.get("fruta_venceu", False),
                           erro=erro)


@app.route("/fruta/reiniciar")
def fruta_reiniciar():
    for c in ("fruta_alvo", "fruta_tipo", "fruta_usuario", "fruta_traducao",
              "fruta_erros", "fruta_venceu", "fruta_seed"):
        session.pop(c, None)
    return redirect(url_for("fruta"))


# ------------------------------------------------------------------
# 10) Jolly Roger
# ------------------------------------------------------------------
@app.route("/jolly-roger", methods=["GET", "POST"])
def jolly_roger():
    seed = modo("jolly_roger")
    if "jr_alvo" not in session:
        alvo = jogos.gerar_jolly_roger(seed)
        session["jr_alvo"] = alvo["tripulacao"]
        session["jr_dica"] = alvo["dica"]
        session["jr_emoji"] = alvo["emoji"]

    opcoes = [j["tripulacao"] for j in JOLLY_ROGERS]
    random.Random(session.get("jr_seed", 11)).shuffle(opcoes)
    resultado = None
    if request.method == "POST":
        escolha = request.form.get("escolha")
        resultado = {"acertou": escolha == session["jr_alvo"],
                     "escolha": escolha, "certo": session["jr_alvo"]}
    return render_template("jolly_roger.html", dica=session["jr_dica"],
                           emoji=session["jr_emoji"], opcoes=opcoes, resultado=resultado)


@app.route("/jolly-roger/reiniciar")
def jr_reiniciar():
    for c in ("jr_alvo", "jr_dica", "jr_emoji", "jr_seed", "jolly_roger_seed"):
        session.pop(c, None)
    return redirect(url_for("jolly_roger"))


# ------------------------------------------------------------------
# 11) Impostor
# ------------------------------------------------------------------
@app.route("/impostor", methods=["GET", "POST"])
def impostor():
    seed = modo("impostor")
    if "imp_desafios" not in session:
        session["imp_desafios"] = jogos.gerar_impostores(10, seed)
        session["imp_indice"] = 0
        session["imp_placar"] = 0

    desafios = session["imp_desafios"]
    i = session["imp_indice"]
    resultado = None
    if request.method == "POST" and i < len(desafios):
        escolha = request.form.get("escolha")
        certo = desafios[i]["intruso"]
        acertou = escolha == certo
        if acertou:
            session["imp_placar"] += 1
        session["imp_indice"] += 1
        resultado = {"acertou": acertou, "certo": certo,
                     "grupo": desafios[i]["grupo"]}
        i = session["imp_indice"]

    acabou = i >= len(desafios)
    atual = None if acabou else desafios[i]
    return render_template("impostor.html", atual=atual, resultado=resultado,
                           placar=session["imp_placar"], rodada=i + 1,
                           total=len(desafios), acabou=acabou)


@app.route("/impostor/reiniciar")
def impostor_reiniciar():
    for c in ("imp_desafios", "imp_indice", "imp_placar", "impostor_seed"):
        session.pop(c, None)
    return redirect(url_for("impostor"))


# ------------------------------------------------------------------
# 12) Identidade (sim ou não)
# ------------------------------------------------------------------
PERGUNTAS = [
    {"texto": "É mulher?", "teste": lambda p: p["genero"] == "Feminino"},
    {"texto": "Usa Fruta do Diabo?", "teste": lambda p: p["fruta"] != "Nenhuma"},
    {"texto": "É pirata?", "teste": lambda p: p["afiliacao"].startswith("Piratas")},
    {"texto": "É da Marinha?", "teste": lambda p: p["afiliacao"] == "Marinha"},
    {"texto": "Nasceu no East Blue?", "teste": lambda p: p["origem"] == "East Blue"},
    {"texto": "Tem recompensa ≥ 1 bilhão?", "teste": lambda p: p["recompensa"] >= 1000000000},
    {"texto": "Tem mais de 2 m de altura?", "teste": lambda p: p["altura"] >= 2.0},
    {"texto": "Tem 40 anos ou mais?", "teste": lambda p: p["idade"] >= 40},
    {"texto": "Usa Haki?", "teste": lambda p: p["haki"] != "Nenhum"},
    {"texto": "Apareceu antes do episódio 100?", "teste": lambda p: p["episodio"] < 100},
]


@app.route("/identidade", methods=["GET", "POST"])
def identidade():
    seed = modo("identidade")
    if "id_alvo" not in session:
        session["id_alvo"] = jogos.do_dia(COMPLETOS, "identidade", seed)["nome"]
        session["id_feitas"] = []
        session["id_vidas"] = 5

    alvo = INDICE[session["id_alvo"]]
    erro = None
    if request.method == "POST":
        if request.form.get("acao") == "perguntar":
            idx = int(request.form.get("pergunta", -1))
            feitas = session["id_feitas"]
            if idx >= 0 and idx not in [f["idx"] for f in feitas]:
                feitas.append({"idx": idx, "resposta": PERGUNTAS[idx]["teste"](alvo)})
                session["id_feitas"] = feitas
                session["id_vidas"] -= 1
        else:
            chute = achar_personagem(request.form.get("palpite", ""))
            if chute and chute["nome"] == alvo["nome"]:
                session["id_venceu"] = True
            else:
                erro = "Não é esse. Tente de novo."

    return render_template("identidade.html", perguntas=PERGUNTAS,
                           feitas=session["id_feitas"], vidas=session["id_vidas"],
                           venceu=session.get("id_venceu", False), erro=erro,
                           acabou=session["id_vidas"] <= 0)


@app.route("/identidade/reiniciar")
def identidade_reiniciar():
    for c in ("id_alvo", "id_feitas", "id_vidas", "id_venceu", "identidade_seed"):
        session.pop(c, None)
    return redirect(url_for("identidade"))


# ------------------------------------------------------------------
# 13) Adivinhar a Risa
# ------------------------------------------------------------------
@app.route("/risa", methods=["GET", "POST"])
def risa():
    seed = modo("risa")
    if "risa_alvo" not in session:
        session["risa_alvo"] = jogos.gerar_risa(seed)["nome"]

    erro = None
    if request.method == "POST":
        chute = achar_personagem(request.form.get("palpite", ""))
        if not chute:
            erro = "Personagem não cadastrado."
        elif chute["nome"] == session["risa_alvo"]:
            session["risa_venceu"] = True

    alvo = INDICE[session["risa_alvo"]]
    return render_template("risa.html", risada=alvo["risada"],
                           venceu=session.get("risa_venceu", False), erro=erro)


@app.route("/risa/reiniciar")
def risa_reiniciar():
    for c in ("risa_alvo", "risa_venceu", "risa_seed"):
        session.pop(c, None)
    return redirect(url_for("risa"))


# ------------------------------------------------------------------
# 14) Sopa de Letras
# ------------------------------------------------------------------
@app.route("/sopa")
def sopa():
    seed = modo("sopa")
    dados = jogos.gerar_sopa(seed)
    return render_template("sopa.html", grade=dados["grade"], palavras=dados["palavras"])


# ------------------------------------------------------------------
# 15) Adivinhar Episódio
# ------------------------------------------------------------------
@app.route("/episodio", methods=["GET", "POST"])
def episodio():
    seed = modo("episodio")
    if "ep_alvo" not in session:
        alvo = jogos.gerar_episodio(seed)
        session["ep_alvo"] = alvo["nome"]
        r = random.Random(jogos._semente("ep-opcoes", seed))
        outros = [p for p in COM_EPISODIO if p["nome"] != alvo["nome"]]
        opcoes = [alvo["episodio"]] + [p["episodio"] for p in r.sample(outros, 3)]
        opcoes = sorted(set(opcoes))
        session["ep_opcoes"] = opcoes

    alvo = INDICE[session["ep_alvo"]]
    resultado = None
    if request.method == "POST":
        escolha = int(request.form.get("escolha", -1))
        resultado = {"acertou": escolha == alvo["episodio"], "certo": alvo["episodio"]}
    return render_template("episodio.html", alvo=alvo, opcoes=session["ep_opcoes"],
                           resultado=resultado)


@app.route("/episodio/reiniciar")
def episodio_reiniciar():
    for c in ("ep_alvo", "ep_opcoes", "episodio_seed"):
        session.pop(c, None)
    return redirect(url_for("episodio"))


# ------------------------------------------------------------------
# 16) Nakama Draft
# ------------------------------------------------------------------
ORCAMENTO = 8000000000


@app.route("/draft", methods=["GET", "POST"])
def draft():
    seed = modo("draft")
    if "draft_pool" not in session:
        session["draft_pool"] = [p["nome"] for p in jogos.gerar_draft(seed)]

    pool = [INDICE[n] for n in session["draft_pool"]]
    resultado = None
    if request.method == "POST":
        escolhidos = [INDICE[n] for n in request.form.getlist("escolhido") if n in INDICE]
        if len(escolhidos) != 8:
            resultado = {"erro": "Escolha exatamente 8 nakamas."}
        else:
            total = sum(p["recompensa"] for p in escolhidos)
            if total > ORCAMENTO:
                resultado = {"erro": f"Estourou o orçamento! {jogos.formatar_berries(total)}.",
                             "total": total}
            else:
                resultado = {"escolhidos": escolhidos, "total": total}
    return render_template("draft.html", pool=pool, orcamento=ORCAMENTO,
                           resultado=resultado)


@app.route("/draft/reiniciar")
def draft_reiniciar():
    for c in ("draft_pool", "draft_seed"):
        session.pop(c, None)
    return redirect(url_for("draft"))



if __name__ == '__main__':
    # link público opcional: defina NGROK_AUTHTOKEN pra expor na internet
    token = os.environ.get("NGROK_AUTHTOKEN")
    if token:
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(token)
            print(f" * Link público: {ngrok.connect(5000)}")
        except Exception as e:
            print(" (ngrok indisponível: %s)" % e)
    app.run(port=5000)
