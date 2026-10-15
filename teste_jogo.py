# -*- coding: utf-8 -*-
"""Testa a jogabilidade de verdade (POSTs + sessao) usando o test client do Flask."""
import sys
sys.path.insert(0, "/home/user/workspaces/732db4c0-b54e-45f4-9dee-4b4e0b61e684/oquepiece")
from app import app
from dados import PERSONAGENS

app.config["TESTING"] = True
falhas = []

def check(cond, msg):
    if not cond:
        falhas.append(msg)
        print("  FALHA:", msg)

# ---- Guess Character (/palpite) ----
with app.test_client() as c:
    c.get("/personagens?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("secreto")
    check(alvo is not None, "alvo do guess character nao definido")
    r = c.post("/palpite", data={"nome_busca": alvo}, follow_redirects=True)
    check(r.status_code == 200, "palpite status")
    with c.session_transaction() as s:
        hist = s.get("historico") or []
    check(bool(hist) and hist[0].get("venceu") is True,
          "guess character nao detectou acerto")

# ---- Wordle ----
with app.test_client() as c:
    c.get("/wordle?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("wordle_alvo")
    check(alvo is not None, "alvo do wordle nao definido")
    if alvo:
        r = c.post("/wordle", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "wordle POST status")
        with c.session_transaction() as s:
            tent = s.get("wordle_tentativas") or []
        check(any(t["palpite"].upper() == alvo.upper() for t in tent), "wordle nao registrou o palpite")

# ---- Higher or Lower ----
with app.test_client() as c:
    c.get("/maior-menor?treino=1")
    with c.session_transaction() as s:
        proximo = s.get("hl_proximo")
    if proximo:
        # responde sempre "maior" e confere que nao quebra
        r = c.post("/maior-menor", data={"escolha": "maior"}, follow_redirects=True)
        check(r.status_code == 200, "higher lower POST status")

# ---- Grid ----
with app.test_client() as c:
    c.get("/grid?treino=1")
    with c.session_transaction() as s:
        dados = s.get("grid_dados")
    if dados:
        sol = dados["solucao"]
        r = c.post("/grid", data={f"c{i}": n for i, n in enumerate(sol)}, follow_redirects=True)
        check(r.status_code == 200, "grid POST status")

# ---- Connections ----
with app.test_client() as c:
    c.get("/connections?treino=1")
    with c.session_transaction() as s:
        grupos = s.get("conn_grupos")
    if grupos:
        g = grupos[0]["membros"]
        r = c.post("/connections", data={f"sel{i}": n for i, n in enumerate(g)}, follow_redirects=True)
        check(r.status_code == 200, "connections POST status")

# ---- Impostor ----
with app.test_client() as c:
    c.get("/impostor?treino=1")
    with c.session_transaction() as s:
        desafios = s.get("imp_desafios")
    if desafios:
        r = c.post("/impostor", data={"escolha": desafios[0]["intruso"]}, follow_redirects=True)
        check(r.status_code == 200, "impostor POST status")

# ---- Bingo ----
with app.test_client() as c:
    c.get("/bingo?treino=1")
    r = c.post("/bingo", data={}, follow_redirects=True)
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
        alvo = s.get("fruta_alvo")
    if alvo:
        r = c.post("/fruta", data={"palpite": alvo.get("usuario") if isinstance(alvo, dict) else alvo}, follow_redirects=True)
        check(r.status_code == 200, "fruta POST status")

# ---- Jolly Roger ----
with app.test_client() as c:
    c.get("/jolly-roger?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("jr_alvo")
    if alvo:
        r = c.post("/jolly-roger", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "jolly roger POST status")

# ---- Identidade ----
with app.test_client() as c:
    c.get("/identidade?treino=1")
    r = c.post("/identidade", data={"pergunta": "0"}, follow_redirects=True)
    check(r.status_code == 200, "identidade POST status")

# ---- Risa ----
with app.test_client() as c:
    c.get("/risa?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("risa_alvo")
    if alvo:
        r = c.post("/risa", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "risa POST status")

# ---- Episodio ----
with app.test_client() as c:
    c.get("/episodio?treino=1")
    with c.session_transaction() as s:
        alvo = s.get("ep_alvo")
    if alvo:
        r = c.post("/episodio", data={"palpite": alvo}, follow_redirects=True)
        check(r.status_code == 200, "episodio POST status")

# ---- Draft ----
with app.test_client() as c:
    c.get("/draft?treino=1")
    r = c.post("/draft", data={}, follow_redirects=True)
    check(r.status_code == 200, "draft POST status")

print()
print(f"{len(falhas)} falha(s) de jogabilidade" if falhas else "Jogabilidade OK em todos os jogos.")
