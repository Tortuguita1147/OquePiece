# -*- coding: utf-8 -*-
"""
Testes rapidos do O Que Piece.
Roda com:  python3 testes.py
Serve pra conferir que os geradores nunca quebram em nenhuma seed e que
todo dado cadastrado aponta pra personagem que existe de verdade.
"""
from collections import Counter

import jogos
from dados import PERSONAGENS, GRUPOS, FRUTAS, JOLLY_ROGERS, FRASES

nomes = {p["nome"] for p in PERSONAGENS}
problemas = []

# --- 1. integridade dos dados ---------------------------------------------
for grupo, membros in GRUPOS.items():
    for m in membros:
        if m not in nomes:
            problemas.append(f"grupo '{grupo}' cita '{m}', que nao existe")

for fruta, tipo, usuario, traducao in FRUTAS:
    if usuario not in nomes:
        problemas.append(f"fruta '{fruta}' aponta pra '{usuario}', que nao existe")

for frase, autor in FRASES:
    if autor not in nomes:
        problemas.append(f"frase de '{autor}' nao bate com ninguem")

duplicados = [n for n, c in Counter(p["nome"] for p in PERSONAGENS).items() if c > 1]
if duplicados:
    problemas.append(f"personagens duplicados: {duplicados}")

campos = ["nome", "genero", "raca", "afiliacao", "status", "fruta",
          "fruta_tipo", "haki", "recompensa", "altura", "idade",
          "origem", "arco", "episodio"]
for p in PERSONAGENS:
    for c in campos:
        if p.get(c) in (None, ""):
            problemas.append(f"'{p['nome']}' esta sem o campo '{c}'")
            break

# --- 2. geradores em varias seeds -----------------------------------------
SEEDS = 400


def conta_falhas(nome, fn, valida):
    ruins = 0
    for s in range(SEEDS):
        try:
            if not valida(fn(s)):
                ruins += 1
        except Exception as e:  # noqa: BLE001
            problemas.append(f"{nome}(seed={s}) estourou: {e!r}")
            ruins += 1
    print(f"  {nome:<14} {SEEDS - ruins}/{SEEDS} ok")


print("Dados:")
print(f"  {len(PERSONAGENS)} personagens, {len(GRUPOS)} grupos, "
      f"{len(FRUTAS)} frutas, {len(FRASES)} frases, "
      f"{len(JOLLY_ROGERS)} jolly rogers")

print("Geradores:")
conta_falhas("grid", jogos.gerar_grid, lambda r: r and len(r["solucao"]) == 9)
conta_falhas("connections", jogos.gerar_connections, lambda r: r and len(r) == 4)
conta_falhas("sopa", jogos.gerar_sopa, lambda r: r and len(r["palavras"]) >= 4)
conta_falhas("impostor", jogos.gerar_impostor, lambda r: bool(r))
conta_falhas("impostores", lambda s: jogos.gerar_impostores(10, s), lambda r: r and len(r) == 10)
conta_falhas("piramide", jogos.gerar_piramide, lambda r: bool(r))
conta_falhas("higher_lower", jogos.gerar_higher_lower, lambda r: bool(r))
conta_falhas("bingo", jogos.gerar_bingo, lambda r: bool(r))
conta_falhas("draft", jogos.gerar_draft, lambda r: bool(r))
conta_falhas("wordle", jogos.gerar_wordle, lambda r: bool(r))
conta_falhas("wanted", jogos.gerar_wanted, lambda r: bool(r))
conta_falhas("fruta", jogos.gerar_fruta, lambda r: bool(r))
conta_falhas("risa", jogos.gerar_risa, lambda r: bool(r))
conta_falhas("episodio", jogos.gerar_episodio, lambda r: bool(r))
conta_falhas("jolly_roger", jogos.gerar_jolly_roger, lambda r: bool(r))
conta_falhas("frase", jogos.gerar_frase, lambda r: bool(r))

print()
if problemas:
    print(f"{len(problemas)} problema(s):")
    for p in problemas[:40]:
        print("  -", p)
else:
    print("Tudo certo, nenhum problema encontrado.")
