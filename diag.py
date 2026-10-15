# -*- coding: utf-8 -*-
import sys, signal
sys.path.insert(0, "/home/user/workspaces/732db4c0-b54e-45f4-9dee-4b4e0b61e684/oquepiece")
import jogos

class T(Exception): pass
def h(s, f): raise T()
signal.signal(signal.SIGALRM, h)

gens = ["gerar_grid","gerar_connections","gerar_sopa","gerar_impostor","gerar_piramide",
        "gerar_higher_lower","gerar_bingo","gerar_draft","gerar_wordle","gerar_risa",
        "gerar_identidade","gerar_wanted","gerar_episodio","gerar_fruta","gerar_jolly_roger"]
for g in gens:
    fn = getattr(jogos, g, None)
    if not fn:
        print(g, "AUSENTE"); continue
    travados = []
    for s in range(400):
        signal.alarm(3)
        try:
            fn(s)
        except T:
            travados.append(s)
        except Exception as e:
            print(g, "ERRO seed", s, type(e).__name__, e)
        finally:
            signal.alarm(0)
    print(f"{g}: travou em {len(travados)} seeds {travados[:10]}")
