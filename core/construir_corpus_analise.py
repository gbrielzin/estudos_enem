"""
construir_corpus_analise.py -- constroi/atualiza core/corpus_analise.db, um
corpus SEPARADO (nao toca enem.db, exceto leitura) com provas ENEM 2009-2023
da API publica enem.dev (todas as 4 areas, idiomas como linhas distintas) mais
2024/2025 (so matematica e ciencias-natureza) lidos de enem.db em modo somente
leitura. Idempotente (INSERT OR REPLACE). Nao baixa imagens, guarda so URLs.

Uso: python construir_corpus_analise.py [--sem-api] [--sem-local]
"""
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://api.enem.dev/v1/exams"
LIMITE = 50
PAUSA_S = 0.3
AQUI = Path(__file__).parent
DB_CORPUS = AQUI / "corpus_analise.db"
DB_ENEM = AQUI / "enem.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS questoes_corpus (
    ano INTEGER NOT NULL,
    indice INTEGER NOT NULL,
    disciplina TEXT,
    idioma TEXT NOT NULL DEFAULT '',
    contexto TEXT,
    enunciado TEXT,
    alternativas_json TEXT,
    gabarito TEXT,
    tem_imagem INTEGER NOT NULL DEFAULT 0,
    fonte TEXT NOT NULL,
    PRIMARY KEY (ano, indice, idioma)
)
"""
# Obs: idioma NULL vira '' (PRIMARY KEY com NULL nao deduplica no SQLite).


def get_json(url, params=None, tentativas=5):
    espera = 2
    for i in range(tentativas):
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {r.status_code}")
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if i == tentativas - 1:
                raise
            time.sleep(espera)
            espera *= 2


def buscar_ano(ano):
    por_chave = {}
    offset = 0
    while True:
        corpo = get_json(f"{BASE_URL}/{ano}/questions", {"limit": LIMITE, "offset": offset})
        for q in corpo["questions"]:
            por_chave[(q["index"], q.get("language") or "")] = q
        if not corpo["metadata"]["hasMore"]:
            break
        offset += LIMITE
        time.sleep(PAUSA_S)
    return list(por_chave.values())


def linha_api(ano, q):
    alts = [{"letter": a["letter"], "text": a.get("text"), "file": a.get("file"), "isCorrect": a.get("isCorrect")}
            for a in q.get("alternatives") or []]
    tem_img = int(bool(q.get("files")) or any(a["file"] for a in alts))
    return (ano, q["index"], q.get("discipline"), q.get("language") or "", q.get("context"),
            q.get("alternativesIntroduction"), json.dumps(alts, ensure_ascii=False),
            q.get("correctAlternative"), tem_img, "enem.dev")


_ALT = re.compile(r"^([A-E])\s+(.*)$")
_AVISO = re.compile(r"^⚠️[^\n]*\n\n")


def separar_local(texto):
    """Texto local = contexto+enunciado+5 linhas 'A\ttexto'. Devolve (corpo, alternativas)."""
    texto = _AVISO.sub("", texto or "")
    linhas = texto.split("\n")
    ult = [l for l in linhas if l.strip()]
    alts = []
    if len(ult) >= 5:
        cand = [_ALT.match(l.strip()) for l in ult[-5:]]
        if all(cand) and [m.group(1) for m in cand] == list("ABCDE"):
            alts = [{"letter": m.group(1), "text": m.group(2).strip(), "file": None, "isCorrect": None} for m in cand]
            # remove as 5 ultimas linhas nao vazias
            n = 0
            while n < 5:
                if linhas.pop().strip():
                    n += 1
    return "\n".join(linhas).strip(), alts


def linhas_locais():
    con = sqlite3.connect(f"file:{DB_ENEM.as_posix()}?mode=ro", uri=True)
    out = []
    for ano, cad in ((2024, "amarelo"), (2025, "azul")):
        for numero, area, texto, img, gab in con.execute(
            "SELECT numero_questao, grande_area, enunciado_texto, enunciado_imagem_path, alternativa_correta "
            "FROM questoes WHERE ano=? AND caderno=? AND grande_area IN ('matematica','ciencias_natureza')", (ano, cad)):
            corpo, alts = separar_local(texto)
            for a in alts:
                a["isCorrect"] = a["letter"] == gab
            out.append((ano, numero, area.replace("_", "-"), "", None, corpo,
                        json.dumps(alts, ensure_ascii=False), gab, int(bool(img)), "enem.db_local"))
    con.close()
    return out


def main():
    con = sqlite3.connect(DB_CORPUS)
    con.execute(SCHEMA)
    ins = "INSERT OR REPLACE INTO questoes_corpus VALUES (?,?,?,?,?,?,?,?,?,?)"
    if "--sem-api" not in sys.argv:
        anos = sorted(e["year"] for e in get_json(BASE_URL) if 2009 <= e["year"] <= 2023)
        for ano in anos:
            qs = buscar_ano(ano)
            con.executemany(ins, [linha_api(ano, q) for q in qs])
            con.commit()
            print(f"{ano}: {len(qs)} questoes", flush=True)
            time.sleep(PAUSA_S)
    if "--sem-local" not in sys.argv:
        ls = linhas_locais()
        con.executemany(ins, ls)
        con.commit()
        print(f"local 2024/2025: {len(ls)} questoes")
    con.close()


if __name__ == "__main__":
    main()
