# -*- coding: utf-8 -*-
"""Testa a jogabilidade de verdade (POSTs + sessão) com o test client do Flask.

Roda com:  python3 teste_jogo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app  # noqa: E402

app.config["TESTING"] = True
falhas = []


def check(cond, msg):
    if not cond:
        falhas.append(msg)
        print("  FALHA:", msg)


# ---- Adivinhar Personagem (/palpite) ----
with app.test_client() as c:
    c.get("/personagens?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("secreto")
    check(alvo is not None, "alvo do adivinhar personagem não definido")
    r = c.post("/palpite", data={"nome_busca": alvo}, follow_redirects=True)
    check(r.status_code == 200, "palpite status")
    with c.session_transaction() as s:
        hist = s.get("historico") or []
    check(bool(hist) and hist[0].get("venceu") is True,
          "adivinhar personagem não detectou acerto")

# ---- Wordle ----
with app.test_client() as c:
    c.get("/wordle?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("wordle_alvo")
    check(alvo is not None, "alvo do wordle não definido")
    if alvo:
        r = c.post("/wordle", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "wordle POST status")
        with c.session_transaction() as s:
            tent = s.get("wordle_tentativas") or []
        check(any(t["palpite"].upper() == alvo.upper() for t in tent),
              "wordle não registrou o palpite")

# ---- Pirâmide ----
with app.test_client() as c:
    c.get("/piramide?treino=1")
    with c.session_transaction() as s:
        ordem = s.get("pir_ordem")
    if ordem:
        r = c.post("/piramide", data={"ordem": "|".join(ordem)}, follow_redirects=True)
        check(r.status_code == 200, "pirâmide POST status")

# ---- Grid ----
with app.test_client() as c:
    c.get("/grid?treino=1")
    with c.session_transaction() as s:
        dados = s.get("grid_dados")
    if dados:
        sol = dados["solucao"]
        r = c.post("/grid", data={f"casa{i}": n for i, n in enumerate(sol)},
                   follow_redirects=True)
        check(r.status_code == 200, "grid POST status")

# ---- Maior ou Menor ----
with app.test_client() as c:
    c.get("/maior-menor?treino=1")
    r = c.post("/maior-menor", data={"escolha": "maior"}, follow_redirects=True)
    check(r.status_code == 200, "maior-menor POST status")

# ---- Connections ----
with app.test_client() as c:
    c.get("/connections?treino=1")
    with c.session_transaction() as s:
        grupos = s.get("conn_grupos")
    if grupos:
        g = grupos[0]["membros"]
        r = c.post("/connections", data={"escolhido": g}, follow_redirects=True)
        check(r.status_code == 200, "connections POST status")

# ---- Bingo ----
with app.test_client() as c:
    c.get("/bingo?treino=1")
    r = c.post("/bingo", data={"acao": "pular"}, follow_redirects=True)
    check(r.status_code == 200, "bingo POST status")

# ---- Wanted ----
with app.test_client() as c:
    c.get("/wanted?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("wanted_alvo")
    if alvo:
        r = c.post("/wanted", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "wanted POST status")

# ---- Fruta ----
with app.test_client() as c:
    c.get("/fruta?treino=1")
    with c.session_transaction() as s:
        usuario = s.get("fruta_usuario")
    if usuario:
        r = c.post("/fruta", data={"palpite": usuario}, follow_redirects=True)
        check(r.status_code == 200, "fruta POST status")

# ---- Jolly Roger ----
with app.test_client() as c:
    c.get("/jolly-roger?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("jr_alvo")
    if alvo:
        r = c.post("/jolly-roger", data={"escolha": alvo}, follow_redirects=True)
        check(r.status_code == 200, "jolly roger POST status")

# ---- Impostor ----
with app.test_client() as c:
    c.get("/impostor?treino=1")
    with c.session_transaction() as s:
        desafios = s.get("imp_desafios")
    if desafios:
        r = c.post("/impostor", data={"escolha": desafios[0]["intruso"]},
                   follow_redirects=True)
        check(r.status_code == 200, "impostor POST status")

# ---- Identidade ----
with app.test_client() as c:
    c.get("/identidade?treino=1")
    r = c.post("/identidade", data={"acao": "perguntar", "pergunta": "0"},
               follow_redirects=True)
    check(r.status_code == 200, "identidade POST status")

# ---- Risa ----
with app.test_client() as c:
    c.get("/risa?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("risa_alvo")
    if alvo:
        r = c.post("/risa", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "risa POST status")

# ---- Episódio ----
with app.test_client() as c:
    c.get("/episodio?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("ep_alvo")
        opcoes = s.get("ep_opcoes") or []
    if alvo and opcoes:
        r = c.post("/episodio", data={"escolha": opcoes[0]}, follow_redirects=True)
        check(r.status_code == 200, "episódio POST status")

# ---- Draft ----
with app.test_client() as c:
    c.get("/draft?treino=1")
    r = c.post("/draft", data={}, follow_redirects=True)
    check(r.status_code == 200, "draft POST status")

print()
print(f"{len(falhas)} falha(s) de jogabilidade" if falhas
      else "Jogabilidade OK em todos os jogos.")
