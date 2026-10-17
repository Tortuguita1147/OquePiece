import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

from traducao import CREWS_PT

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE, "cache")
ARQ_FINAL = os.path.join(CACHE, "personagens.json")

API = "https://api.api-onepiece.com/v2"
QL = "https://onepieceql.up.railway.app/graphql"
QL_PAGINAS = 34

RUIDO = {"viz", "odex", "funimation", "4kids", "dub", "subs", "sub", "wt100",
         "opcg", "uncut", "edited", "formerly", "media", "d", "the", "de",
         "dr", "la", "le", "les", "os", "as", "and"}

ALIASES = {
    "marshall d teach": ["marchall d teach", "marshall d teech"],
    "buggy": ["baggy", "buggy le clown"],
    "donquixote doflamingo": ["don quijote doflamingo", "don quixote doflamingo"],
    "edward weevil": ["edward weeble"],
    "eustass kid": ["eustass kidd"],
    "chiffon": ["charlotte chiffon"],
    "nekomamushi": ["cat viper nekomamushi", "nekomamushi cat viper"],
    "inuarashi": ["dogstorm inuarashi", "inuarashi dogstorm", "dogstorm dogupine inuarashi"],
    "caesar clown": ["cesar clown"],
    "daz bones": ["das bones", "daz bonez"],
    "fisher tiger": ["ficher tiger"],
    "gan fall": ["gan forr", "ganfor"],
    "trafalgar lami": ["trafalgar lammy"],
    "shimotsuki koushirou": ["koushirou", "koshiro"],
    "lucky roux": ["lucky roo"],
    "shiryu": ["shiryu shiliew"],
    "kanjuro": ["kanjuro kurozumi", "kurozumi kanjuro"],
    "who's who": ["whos who", "who s who"],
    "riku doldo iii": ["riku dold iii"],
    "ryuma": ["ryuma shimotsuki", "shimotsuki ryuma"],
    "dr hiriluk": ["hiriluk hiruruku", "hiriluk"],
    "dracule mihawk": ["dracule mihawk diego mihawk"],
    "don krieg": ["krieg"],
    "kuina": ["shimotsuki kuina"],
    "sham": ["siam sham"],
    "buchi": ["butchie buchi"],
    "baby 5": ["baby five", "baby 5 baby five"],
    "gin": ["ghin"],
    "mohji": ["morji"],
}


# --- Utilidades de texto e número ---
def _norm(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9 ]", " ", texto.lower())
    return re.sub(r"\s+", " ", texto).strip()


def _candidatos(nome):
    if not nome:
        return []
    nome = re.sub(r"\(.*?\)", " ", nome)
    saida = []
    for parte in re.split(r"[/;,]", nome):
        toks = [t for t in _norm(parte).split() if t not in RUIDO]
        if toks:
            limpo = " ".join(toks)
            if limpo not in saida:
                saida.append(limpo)
    return saida


def _chave(nome):
    return {" ".join(sorted(c.split())) for c in _candidatos(nome)}


def _chaves(nome, alias_local=False):
    ks = set(_chave(nome))
    if alias_local:
        for extra in ALIASES.get(_norm(nome), []):
            ks |= _chave(extra)
    return ks


def _so_digitos(texto):
    if texto is None:
        return None
    d = re.sub(r"\D", "", str(texto))
    return int(d) if d else None


def _parse_recompensa(valor):
    return _so_digitos(valor) or 0


def _parse_altura(valor):
    if valor is None:
        return None
    m = re.search(r"(\d+[.,]?\d*)", str(valor).replace(",", "."))
    if not m:
        return None
    v = float(m.group(1))
    if v > 10:
        v = v / 100.0
    return round(v, 2) if 0.1 <= v <= 30 else None


def _parse_idade(valor):
    if valor is None:
        return None
    m = re.search(r"(\d{1,3})", str(valor))
    if not m:
        return None
    n = int(m.group(1))
    return n if 0 < n < 200 else None


def _parse_episodio(debut):
    if not debut:
        return 0
    m = re.search(r"(?:episode|epis[oó]dio|ep\.?)\s*(\d{1,4})", str(debut), re.I)
    return int(m.group(1)) if m else 0


def _tipo_fruta(tipo):
    if not tipo:
        return "Nenhuma"
    t = _norm(tipo)
    if "logia" in t:
        return "Logia"
    if "mythique" in t or "mythical" in t or "mitica" in t:
        return "Zoan Mítica"
    if "antique" in t or "ancient" in t or "antiga" in t:
        return "Zoan Antiga"
    if "zoan" in t:
        return "Zoan"
    if "paramecia" in t:
        return "Paramecia Especial" if ("special" in t or "especial" in t) else "Paramecia"
    return "Nenhuma"


def _status(s):
    if not s:
        return "Desconhecido"
    n = _norm(s)
    if n in ("vivant", "alive", "vivo", "viva"):
        return "Vivo"
    if n in ("mort", "morto", "morta", "deceased", "dead"):
        return "Morto"
    return "Desconhecido"


def _afiliacao(crew):
    if not crew:
        return "Desconhecida"
    if isinstance(crew, dict):
        cid = crew.get("id")
        if cid in CREWS_PT:
            return CREWS_PT[cid]
        crew = crew.get("name") or ""
    n = _norm(crew)
    mapa = [
        (("marine", "marinha"), "Marinha"),
        (("government", "gouvernement"), "Governo Mundial"),
        (("revolution", "revolucion"), "Exército Revolucionário"),
        (("chapeau de paille", "straw hat"), "Piratas do Chapéu de Palha"),
        (("clown",), "Piratas do Buggy"),
        (("blackbeard", "barbe noire"), "Piratas do Barba Negra"),
        (("whitebeard", "barbe blanche"), "Piratas do Barba Branca"),
        (("big mom",), "Piratas da Big Mom"),
        (("hundred beasts", "beasts"), "Piratas das Feras"),
        (("kid",), "Piratas do Kid"),
        (("heart", "coeur"), "Piratas do Coração"),
        (("roger",), "Piratas do Roger"),
        (("roux", "red hair"), "Piratas do Ruivo"),
        (("kuja",), "Piratas Kuja"),
        (("don quixote", "donquixote"), "Piratas Donquixote"),
        (("sun", "soleil"), "Piratas do Sol"),
    ]
    for chaves, rotulo in mapa:
        if any(c in n for c in chaves):
            return rotulo
    limpo = re.sub(r"^(the|le|la|les|os|as)\s+", "", n)
    limpo = re.sub(r"\b(crew|equipage|pirates?|pirate|fleet|armada)\b", "", limpo).strip()
    limpo = " ".join(p.capitalize() for p in limpo.split())
    if any(x in n for x in ("crew", "pirate", "equipage", "fleet", "armada")):
        return f"Piratas {limpo}".strip() if limpo else "Piratas"
    return limpo or "Desconhecida"


# --- Download das APIs ---
def _get_json(url, dados=None, tries=3):
    for t in range(tries):
        try:
            if dados is None:
                req = urllib.request.Request(url, headers={"User-Agent": "QuePedaco/2.0"})
            else:
                req = urllib.request.Request(url, data=json.dumps(dados).encode(),
                                             headers={"Content-Type": "application/json",
                                                      "User-Agent": "QuePedaco/2.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if t == tries - 1:
                raise
            print(f"  ... falhou ({e}), tentando de novo", flush=True)
            time.sleep(2)


def _salvar(caminho, obj):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def _carregar_cache(nome):
    with open(os.path.join(CACHE, nome), encoding="utf-8") as f:
        return json.load(f)


def baixar():
    os.makedirs(CACHE, exist_ok=True)
    print("Baixando personagens da API...", flush=True)
    _salvar(os.path.join(CACHE, "api_characters.json"), _get_json(f"{API}/characters/en"))
    print("Baixando frutas da API...", flush=True)
    _salvar(os.path.join(CACHE, "api_fruits.json"), _get_json(f"{API}/fruits/en"))
    print("Baixando tripulações da API...", flush=True)
    _salvar(os.path.join(CACHE, "api_crews.json"), _get_json(f"{API}/crews/en"))

    print("Baixando enriquecimento (OnePieceQL)...", flush=True)
    ql = {}
    consulta = ("{ characters(page:%d){ info{pages} results{ id englishName origin "
                "affiliations debut avatarSrc devilFruitName age bounty } } }")
    for p in range(1, QL_PAGINAS + 1):
        d = _get_json(QL, {"query": consulta % p})
        if d and d.get("data"):
            for c in d["data"]["characters"]["results"]:
                ql[str(c["id"])] = c
        if p % 5 == 0:
            print(f"  OnePieceQL página {p}/{QL_PAGINAS} ({len(ql)} registros)", flush=True)
    _salvar(os.path.join(CACHE, "onepieceql.json"), ql)
    print(f"Pronto: {len(ql)} personagens enriquecidos.", flush=True)


# --- Montagem da base ---
def _ficha(nome):
    return {
        "nome": nome, "genero": "Desconhecido", "raca": "Desconhecido",
        "afiliacao": "Desconhecida", "status": "Desconhecido",
        "fruta": "Nenhuma", "fruta_tipo": "Nenhuma", "haki": "Nenhum",
        "recompensa": 0, "altura": 0.0, "idade": 0, "origem": "Desconhecida",
        "arco": "", "episodio": 0, "risada": "", "foto": None,
        "id_api": None, "fonte": [],
    }


def _indexar(registros, campo, alias_local=False):
    idx = {}
    for r in registros:
        for k in _chaves(r.get(campo), alias_local):
            idx.setdefault(k, r)
    return idx


def _buscar(idx, nome, alias_local=False):
    for k in _chaves(nome, alias_local):
        if k in idx:
            return idx[k]
    return None


def _aplicar(destino, origem, campos):
    for c in campos:
        if origem.get(c) not in (None, "", 0, 0.0):
            destino[c] = origem[c]


def montar():
    from dados import (PERSONAGENS as LOCAIS, FRUTAS as FRUTAS_LOCAIS,
                       GRUPOS as GRUPOS_LOCAIS, JOLLY_ROGERS, FRASES)

    api = _carregar_cache("api_characters.json")
    ql = list(_carregar_cache("onepieceql.json").values())

    loc_idx = _indexar(LOCAIS, "nome", alias_local=True)
    api_idx = _indexar(api, "name")
    ql_idx = _indexar(ql, "englishName")

    traducao_por_fruta = {_norm(n): tr for n, _t, _u, tr in FRUTAS_LOCAIS}

    fichas = []
    usados_api = set()
    usados_ql = set()

    # 1) personagens da API (enriquecidos com local + OnePieceQL)
    for c in api:
        nome = (c.get("name") or "").split(" / ")[0].strip()
        local = _buscar(loc_idx, nome, alias_local=True)
        q = _buscar(ql_idx, nome) or (local and _buscar(ql_idx, local["nome"], alias_local=True))
        f = _ficha(local["nome"] if local else nome)
        f["id_api"] = c.get("id")
        f["fonte"] = ["api"]

        if c.get("crew"):
            f["afiliacao"] = _afiliacao(c["crew"])
        if c.get("status"):
            f["status"] = _status(c["status"])
        if c.get("fruit"):
            f["fruta"] = c["fruit"].get("roman_name") or c["fruit"].get("name") or "Nenhuma"
            f["fruta_tipo"] = _tipo_fruta(c["fruit"].get("type"))
        f["recompensa"] = _parse_recompensa(c.get("bounty"))
        alt = _parse_altura(c.get("size"))
        if alt:
            f["altura"] = alt
        idade = _parse_idade(c.get("age"))
        if idade:
            f["idade"] = idade

        if q:
            org = (q.get("origin") or "").strip()
            if org and org.upper() != "N/A":
                f["origem"] = org
            ep = _parse_episodio(q.get("debut"))
            if ep:
                f["episodio"] = ep
            f["fonte"].append("onepieceql")
            usados_ql.add(id(q))
        if local:
            _aplicar(f, local, ("genero", "raca", "afiliacao", "status", "fruta",
                                "fruta_tipo", "haki", "recompensa", "altura",
                                "idade", "origem", "arco", "episodio", "risada", "foto"))
            f["fonte"].append("local")
        if not f["fruta"]:
            f["fruta"] = "Nenhuma"
        fichas.append(f)
        usados_api.add(id(c))

    # 2) personagens do dicionário que a API não tem
    for p in LOCAIS:
        if _buscar(api_idx, p["nome"]) is not None:
            continue
        q = _buscar(ql_idx, p["nome"], alias_local=True)
        f = _ficha(p["nome"])
        _aplicar(f, p, ("genero", "raca", "afiliacao", "status", "fruta",
                        "fruta_tipo", "haki", "recompensa", "altura", "idade",
                        "origem", "arco", "episodio", "risada", "foto"))
        f["fonte"] = ["local"]
        if q:
            org = (q.get("origin") or "").strip()
            if org and org.upper() != "N/A" and f["origem"] == "Desconhecida":
                f["origem"] = org
            ep = _parse_episodio(q.get("debut"))
            if ep and not f["episodio"]:
                f["episodio"] = ep
            f["fonte"].append("onepieceql")
        fichas.append(f)

    # 3) tira duplicatas e fotos que não existem
    vistos, personagens = set(), []
    img_dir = os.path.join(BASE, "static", "img")
    for f in fichas:
        k = _norm(f["nome"])
        if k in vistos:
            continue
        vistos.add(k)
        if f["foto"] and not os.path.exists(os.path.join(img_dir, f["foto"])):
            f["foto"] = None
        personagens.append(f)
    personagens.sort(key=lambda p: p["nome"].lower())

    # 4) frutas
    frutas, vistos_fruta = [], set()
    for p in personagens:
        if not p["fruta"] or p["fruta"] == "Nenhuma":
            continue
        chave = _norm(p["fruta"])
        if chave in vistos_fruta:
            continue
        vistos_fruta.add(chave)
        frutas.append((p["fruta"], p["fruta_tipo"], p["nome"],
                       traducao_por_fruta.get(chave, "")))
    for nome, tipo, usuario, traducao in FRUTAS_LOCAIS:
        if _norm(nome) not in vistos_fruta:
            vistos_fruta.add(_norm(nome))
            frutas.append((nome, tipo, usuario, traducao))

    # 5) grupos e frases com nomes canônicos
    nome_por_chave = {}
    for p in personagens:
        for k in _chaves(p["nome"]):
            nome_por_chave.setdefault(k, p["nome"])

    def _canonico(nome):
        for k in _chaves(nome):
            if k in nome_por_chave:
                return nome_por_chave[k]
        return nome

    grupos = {}
    for grupo, membros in GRUPOS_LOCAIS.items():
        limpos = []
        for m in membros:
            c = _canonico(m)
            if c not in limpos:
                limpos.append(c)
        if len(limpos) >= 4:
            grupos[grupo] = limpos

    frases = [(fr, _canonico(p)) for fr, p in FRASES]

    return {
        "personagens": personagens,
        "frutas": frutas,
        "grupos": grupos,
        "jolly_rogers": JOLLY_ROGERS,
        "frases": frases,
        "meta": {
            "total_personagens": len(personagens),
            "api": len(api),
            "onepieceql": len(ql),
            "gerado_em": time.strftime("%Y-%m-%d %H:%M"),
        },
    }


def construir():
    if not os.path.exists(os.path.join(CACHE, "api_characters.json")):
        baixar()
    dados = montar()
    _salvar(ARQ_FINAL, dados)
    print("Base gravada em", ARQ_FINAL)
    print("Personagens:", dados["meta"]["total_personagens"],
          "| frutas:", len(dados["frutas"]),
          "| grupos:", len(dados["grupos"]))
    return dados


def carregar():
    if not os.path.exists(ARQ_FINAL):
        return construir()
    with open(ARQ_FINAL, encoding="utf-8") as f:
        return json.load(f)


# --- API do módulo ---
try:
    _DADOS = carregar()
    PERSONAGENS = _DADOS["personagens"]
    FRUTAS = [tuple(f) for f in _DADOS["frutas"]]
    GRUPOS = _DADOS["grupos"]
    JOLLY_ROGERS = _DADOS["jolly_rogers"]
    FRASES = [tuple(f) for f in _DADOS["frases"]]
    META = _DADOS.get("meta", {})
    ORIGEM_DADOS = "api"
except Exception as _erro:
    print("Aviso: não deu pra usar a API (%s). Usando o dicionário local." % _erro,
          file=sys.stderr)
    from dados import (PERSONAGENS, FRUTAS, GRUPOS, JOLLY_ROGERS, FRASES)  # noqa
    META = {"total_personagens": len(PERSONAGENS)}
    ORIGEM_DADOS = "local"


COMPLETOS = [p for p in PERSONAGENS if p["genero"] != "Desconhecido"]
COM_RECOMPENSA = [p for p in PERSONAGENS if p["recompensa"] > 0]
COM_RISADA = [p for p in PERSONAGENS if p["risada"]]
COM_EPISODIO = [p for p in PERSONAGENS if p["episodio"] > 0]


if __name__ == "__main__":
    if "--atualizar" in sys.argv:
        baixar()
    construir()
