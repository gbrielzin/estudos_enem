"""importar_corpus_antigo.py — traz Ciências da Natureza de provas regulares antigas
(caderno AZUL) do corpus (core/corpus_analise.db) para o enem.db.

Fonte de cada campo:
  - gabarito: ITENS_PROVA oficial do INEP (core/inep_itens/), NUNCA o do corpus.
    O corpus só serve pra achar qual prova/posição do INEP corresponde (casamento
    do gabarito, exigindo >= 40 de 45 iguais). Divergência corpus x INEP é
    reportada; item anulado (gabarito "X") é PULADO, não importado.
  - enunciado/alternativas: corpus (enem.dev). Links de imagem markdown são
    removidos e a questão recebe o mesmo aviso ⚠️ de "pode faltar figura" que
    extrair_enunciados_pdf.py usa.
  - matéria: 'sem_video_pendente' (nao_classificado, fica na Triagem; classificação
    automática por palavra-chave concordou só ~56% com os rótulos, então não uso).
  - `fonte` = 'corpus_enem_dev+gabarito_inep' marca o bloco (a coluna `origem`
    só aceita enem_oficial/banco_pratica).

Numeração: usa o índice do corpus (2010-2016: 46-90; 2017+: 91-135), que é a
numeração do caderno azul. 2009 fica de fora (matriz diferente).

Uso (de dentro de core/):
    python importar_corpus_antigo.py                 # só leitura, 2010-2018
    python importar_corpus_antigo.py --aplicar       # backup + grava
    python importar_corpus_antigo.py 2015 2016       # intervalo de anos
Idempotente: questão que já existe não é alterada.
"""
import csv
import json
import re
import sqlite3
import sys
from collections import defaultdict

import backup_db
import db

AVISO_FIGURA = (
    "⚠️ Esta questão pode depender de figura/gráfico/tabela que a extração de texto "
    "não capturou (o ENEM desenha isso como vetor, não como imagem separada) -- "
    "confere contra o PDF original antes de confiar só neste texto."
)
FONTE = "corpus_enem_dev+gabarito_inep"
MATERIA_PLACEHOLDER = "sem_video_pendente"
IMG_MD = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def bloco(ano):
    return (46, 90) if ano <= 2016 else (91, 135)


def gabarito_inep(ano, corp):
    """Acha (prova, deslocamento) do caderno azul que casa com o corpus e devolve
    ({indice_corpus: letra oficial}, prova, acertos, n)."""
    rows = csv.DictReader(
        open(f"inep_itens/{ano}_ITENS_PROVA_{ano}.csv", encoding="latin-1"), delimiter=";"
    )
    provas = defaultdict(dict)
    for r in rows:
        if r["SG_AREA"] == "CN" and r["TX_COR"].strip().upper().startswith("AZUL"):
            provas[r["CO_PROVA"]][int(r["CO_POSICAO"])] = r["TX_GABARITO"].strip().upper()
    melhor = None
    for cp, g in provas.items():
        for off in range(-100, 101):
            comuns = [i for i in corp if (i + off) in g and corp[i] in "ABCDE" and corp[i]]
            if len(comuns) < 40:
                continue
            ok = sum(corp[i] == g[i + off] for i in comuns)
            if not melhor or ok > melhor[2]:
                melhor = (cp, off, ok, len(comuns), g)
    if not melhor or melhor[2] < 40:
        raise SystemExit(f"{ano}: sem casamento confiável com o gabarito do INEP ({melhor and melhor[:4]})")
    cp, off, ok, n, g = melhor
    return {i: g[i + off] for i in corp if (i + off) in g}, cp, ok, n


def montar_texto(contexto, enunciado, alternativas, tem_imagem):
    tinha_img = bool(IMG_MD.search(contexto or "") or IMG_MD.search(enunciado or ""))
    partes = []
    for p in (contexto, enunciado):
        p = IMG_MD.sub("", p or "").strip()
        if p:
            partes.append(p)
    linhas = []
    for a in alternativas:
        txt = IMG_MD.sub("", a.get("text") or "").strip()
        if not txt:
            txt = "(alternativa em imagem)"
            tinha_img = True
        linhas.append(f"{a['letter']}\t{txt}")
    corpo = re.sub(r"\n{3,}", "\n\n", "\n\n".join(partes)) + "\n" + "\n".join(linhas)
    if tem_imagem or tinha_img:
        corpo = AVISO_FIGURA + "\n\n" + corpo
    return corpo, bool(tem_imagem or tinha_img)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    aplicar = "--aplicar" in sys.argv
    ini, fim = (int(args[0]), int(args[1])) if len(args) >= 2 else (2010, 2018)
    corpus = sqlite3.connect("corpus_analise.db")
    plano, resumo = [], []
    for ano in range(ini, fim + 1):
        lo, hi = bloco(ano)
        linhas = corpus.execute(
            "SELECT indice, contexto, enunciado, alternativas_json, gabarito, tem_imagem "
            "FROM questoes_corpus WHERE ano=? AND indice BETWEEN ? AND ? ORDER BY indice",
            (ano, lo, hi),
        ).fetchall()
        corp = {r[0]: (r[4] or "").strip().upper() for r in linhas}
        oficial, cp, ok, n = gabarito_inep(ano, corp)
        div, anuladas, sem_alt, com_aviso = [], [], [], 0
        for indice, contexto, enunc, alts_json, _gab_corpus, tem_img in linhas:
            letra = oficial.get(indice, "")
            if letra not in list("ABCDE"):
                anuladas.append((indice, letra))
                continue
            if corp[indice] != letra:
                div.append((indice, corp[indice], letra))
            alts = json.loads(alts_json or "[]")
            if len(alts) != 5:
                sem_alt.append(indice)
                continue
            texto, aviso = montar_texto(contexto, enunc, alts, tem_img)
            com_aviso += aviso
            plano.append((ano, indice, letra, texto))
        resumo.append((ano, cp, ok, n, len(linhas), div, anuladas, sem_alt, com_aviso))

    print("ano | prova INEP | casamento | itens | divergências (índice, corpus, INEP) | anuladas | sem 5 alternativas | com ⚠️")
    for ano, cp, ok, n, tot, div, anu, sem, av in resumo:
        print(f"{ano} | {cp} | {ok}/{n} | {tot} | {div} | {anu} | {sem} | {av}")
    print(f"\nTotal a importar: {len(plano)} questões")

    if not aplicar:
        print("\n(modo leitura: nada foi gravado; use --aplicar)")
        return
    db.inicializar_banco()
    print("backup:", backup_db.fazer_backup())
    novas = puladas = 0
    for ano, indice, letra, texto in plano:
        id_q = db.gerar_id_canonico(ano, "azul", indice)
        with db._conectar() as conn:
            if conn.execute("SELECT 1 FROM questoes WHERE id_questao=?", (id_q,)).fetchone():
                puladas += 1
                continue
        db.inserir_questao(ano, "azul", indice, "ciencias_natureza", MATERIA_PLACEHOLDER, letra,
                           enunciado_texto=texto)
        with db._conectar() as conn:
            conn.execute("UPDATE questoes SET fonte=? WHERE id_questao=?", (FONTE, id_q))
        novas += 1
    print(f"gravadas: {novas}; já existiam (não alteradas): {puladas}")


if __name__ == "__main__":
    main()
