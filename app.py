import random
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "chave_secreta_muito_inteligente"

personagens_base = [
    {
        "nome": "Monkey D. Luffy",
        "foto": "luffymose.jpeg",
        "gênero": "Masculino",
        "raça": "Humano",
        "afiliação": "Piratas do Chapéu de Palha",
        "status": "Vivo",
        "fruta": "Zoan mitica",
        "haki": "👑, 💪🏿, 👁️",
        "recompensa": "3.000.000.000 Berries",
        "altura": "1,74 m",
        "idade": "19 anos",
        "arco": "Romance Dawn",
        "epsodio": "1",
        "origem": "East Blue",
    },
    {
        "nome": "Roronoa Zoro",
        "foto": "zoro_gucci.jpeg",
        "gênero": "Masculino",
        "raça": "Humano",
        "afiliação": "Piratas do Chapéu de Palha",
        "status": "Vivo",
        "fruta": "Nenhuma",
        "haki": "👑, 💪🏿, 👁️",
        "recompensa": "1.111.000.000 Berries",
        "altura": "1,81 m",
        "idade": "21 anos",
        "arco": "Romance Dawn",
        "epsodio": "2",
        "origem": "East Blue",
    },
    {
        "nome": "Nico Robin",
        "foto": "robin_testuda.jpg",
        "gênero": "Feminino",
        "raça": "Humano",
        "afiliação": "Piratas do Chapéu de Palha",
        "status": "Vivo",
        "fruta": "Paramecia",
        "haki": False,
        "recompensa": "930.000.000 Berries",
        "altura": "1,88 m",
        "idade": "30",
        "arco": "Alabasta",
        "epsodio": "67",
        "origem": "West Blue",
    },
]


def limpar_recompensa(valor_str):
    try:
        return int(
            valor_str.replace("Berries", "").replace(".", "").strip()
        )
    except:
        return 0


def limpar_altura(valor_str):
    try:
        return float(valor_str.replace("m", "").replace(",", ".").strip())
    except:
        return 0.0


def limpar_idade(valor_str):
    try:
        return int(valor_str.replace("anos", "").strip())
    except:
        return 0
    
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/personagens")
def personagens():
    if "secreto" not in session:
        session["secreto"] = random.choice(personagens_base)["nome"]
    if "historico" not in session:
        session["historico"] = []
    return render_template("personagens.html", historico=session["historico"])


@app.route("/palpite", methods=["POST"])
def processar_palpite():
    nome_palpite = request.form.get("nome_busca", "").strip().lower()

    chute = next(
        (p for p in personagens_base if p["nome"].lower() == nome_palpite), None
    )
    if not chute:
        return redirect(url_for("home"))

    secreto = next(
        (p for p in personagens_base if p["nome"] == session["secreto"]), None
    )

    chute_rec = limpar_recompensa(chute["recompensa"])
    sec_rec = limpar_recompensa(secreto["recompensa"])

    chute_alt = limpar_altura(chute["altura"])
    sec_alt = limpar_altura(secreto["altura"])

    chute_id = limpar_idade(chute["idade"])
    sec_id = limpar_idade(secreto["idade"])

    comparacao = {
        "nome": chute["nome"],
        "foto": chute["foto"],
        "genero": {
            "valor": chute["gênero"],
            "classe": "correto" if chute["gênero"] == secreto["gênero"] else "errado",
        },
        "raca": {
            "valor": chute["raça"],
            "classe": "correto" if chute["raça"] == secreto["raça"] else "errado",
        },
        "afiliacao": {
            "valor": chute["afiliação"],
            "classe": "correto"
            if chute["afiliação"] == secreto["afiliação"]
            else "errado",
        },
        "status": {
            "valor": chute["status"],
            "classe": "correto" if chute["status"] == secreto["status"] else "errado",
        },
        "fruta": {
            "valor": chute["fruta"],
            "classe": "correto" if chute["fruta"] == secreto["fruta"] else "errado",
        },
        "haki": {
            "valor": "Sim" if chute["haki"] else "Não",
            "classe": "correto"
            if bool(chute["haki"]) == bool(secreto["haki"])
            else "errado",
        },
        "origem": {
            "valor": chute["origem"],
            "classe": "correto" if chute["origem"] == secreto["origem"] else "errado",
        },
        "arco": {
            "valor": chute["arco"],
            "classe": "correto" if chute["arco"] == secreto["arco"] else "errado",
        },
        "recompensa": {
            "valor": chute["recompensa"],
            "classe": "correto" if chute_rec == sec_rec else "errado",
            "seta": "⬆️" if chute_rec < sec_rec else ("⬇️" if chute_rec > sec_rec else ""),
        },
        "altura": {
            "valor": chute["altura"],
            "classe": "correto" if chute_alt == sec_alt else "errado",
            "seta": "⬆️" if chute_alt < sec_alt else ("⬇️" if chute_alt > sec_alt else ""),
        },
        "idade": {
            "valor": chute["idade"]
            if "anos" in str(chute["idade"])
            else f"{chute['idade']} anos",
            "classe": "correto" if chute_id == sec_id else "errado",
            "seta": "⬆️" if chute_id < sec_id else ("⬇️" if chute_id > sec_id else ""),
        },
    }

    if chute["nome"] == secreto["nome"]:
        comparacao["venceu"] = True

    historico = session["historico"]
    historico.insert(0, comparacao)
    session["historico"] = historico

    return redirect(url_for("personagens"))


@app.route("/reiniciar")
def reiniciar():
    session.pop("secreto", None)
    session.pop("historico", None)
    return redirect(url_for("personagens"))


if __name__ == "__main__":
    app.run(debug=True)
