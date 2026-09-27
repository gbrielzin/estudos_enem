"""Banco de redações nota alta (1000/980/960) pra análise de padrão.

Pipeline reprodutível: fontes locais (PDFs já baixados) -> texto -> redações
-> SQLite -> duplicatas marcadas -> estatísticas. Nasceu de uma coleta
exploratória em loop (2026-09-26); aqui ela vira código pra rodar de novo
com um comando quando sair edição nova (ex.: notas 1000 de cada janeiro).

Os TEXTOS são de terceiros (alunos, INEP, cartilha Redação a Mil): ficam só
na pasta do banco, que está no .gitignore, e servem pra análise local. O que
vai pro git é este código e `docs/redacao_pesquisa/fontes.md` (de onde vem
cada coisa e o que pode ou não ser guardado).

Módulo independente: não importa db.py nem nada de UI. `pymupdf` só é
importado na hora de converter PDF em texto.

Uso (da pasta core/):
    python coleta_redacoes.py ../docs/redacao_pesquisa/banco_1000
"""
from __future__ import annotations

import csv
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Cartilha do INEP (ano da cartilha) -> (edição do ENEM, tema). A de 2023
# (redações do ENEM 2022) fica de fora: o PDF tem fonte embaralhada.
CARTILHAS_INEP = {
    2019: (2018, "Manipulação do comportamento do usuário pelo controle de dados na internet"),
    2022: (2021, "Invisibilidade e registro civil: garantia de acesso à cidadania no Brasil"),
    2024: (2023, "Desafios para o enfrentamento da invisibilidade do trabalho de cuidado realizado pela mulher no Brasil"),
    2025: (2024, "Desafios para a valorização da herança africana no Brasil"),
}
TEMA_2019 = "Democratização do acesso ao cinema no Brasil"
TEMA_2018 = "Manipulação do comportamento do usuário pelo controle de dados na internet"
URL_CARTILHA_2020 = ("https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/"
                     "a_redacao_do_enem_2020_-_cartilha_do_participante.pdf")
URL_REDAMIL = "https://www.lucasfelpi.com.br/redamil"
# Redação a Mil: edição -> ENEM. A 1.0 e a 2.0 têm layout próprio.
EDICOES_REDAMIL = {1: 2018, 2: 2019, 3: 2020, 4: 2021, 5: 2022, 6: 2023, 7: 2024}

SCHEMA = """
CREATE TABLE IF NOT EXISTS redacoes (
    id INTEGER PRIMARY KEY, fonte TEXT, nivel_fonte TEXT, cartilha INTEGER, enem INTEGER, tema TEXT,
    autor TEXT, nota INTEGER, introducao TEXT, n_paragrafos INTEGER, legibilidade REAL, texto TEXT,
    comentario_inep TEXT, url TEXT, abertura_tipo TEXT, abertura_repertorio TEXT, causa_1 TEXT, causa_2 TEXT,
    rep_d1 TEXT, rep_d2 TEXT, proposta TEXT, c1 INTEGER, c2 INTEGER, c3 INTEGER, c4 INTEGER, c5 INTEGER,
    duplicada_de INTEGER
);
CREATE TABLE IF NOT EXISTS relatos (
    id INTEGER PRIMARY KEY, nome TEXT, nota_redacao INTEGER, ano_enem INTEGER, origem TEXT,
    o_que_fez TEXT, url TEXT, nivel_fonte TEXT
);
"""
COLUNAS = ["fonte", "nivel_fonte", "cartilha", "enem", "tema", "autor", "nota", "introducao", "n_paragrafos",
           "legibilidade", "texto", "comentario_inep", "url", "abertura_tipo", "abertura_repertorio", "causa_1",
           "causa_2", "rep_d1", "rep_d2", "proposta", "c1", "c2", "c3", "c4", "c5"]


# ------------------------------------------------------------
# Utilidades de texto
# ------------------------------------------------------------

def normalizar(texto: str | None) -> str:
    """Minúsculo, sem acento, sem ligaduras de PDF (ﬁ, ﬂ), sem caractere invisível."""
    t = (texto or "").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("​", "").replace("\xa0", " ")
    return "".join(c for c in unicodedata.normalize("NFKD", t.lower()) if not unicodedata.combining(c))


def chave_duplicata(enem: int, autor: str | None) -> tuple[int, str]:
    """Mesma redação em fontes diferentes: mesma edição + os 2 primeiros nomes."""
    return enem, " ".join(normalizar(autor).split()[:2])


def legibilidade(linha: str) -> float:
    """Fração de caracteres "normais"; PDF com fonte embaralhada dá valor baixo."""
    if not linha.strip():
        return 1.0
    boas = sum(ch.isalpha() and ord(ch) < 0x250 or ch in " ,.;:!?-–—()“”\"'0123456789" for ch in linha)
    return boas / len(linha)


def dividir_paragrafos(linhas: list[str]) -> list[str]:
    """Junta linhas de PDF em parágrafos: o parágrafo acaba numa linha que
    termina em ponto, é bem mais curta que a linha típica e é seguida de
    maiúscula (a última linha de um parágrafo justificado não chega na margem)."""
    linhas = [" ".join(l.split()) for l in linhas if l.strip()]
    tamanhos = sorted(len(x) for x in linhas if len(x) > 20)
    mediana = tamanhos[len(tamanhos) // 2] if tamanhos else 60
    pars, atual = [], []
    for i, t in enumerate(linhas):
        atual.append(t)
        prox = linhas[i + 1] if i + 1 < len(linhas) else ""
        if t.rstrip('"”').endswith((".", "!", "?")) and len(t) < 0.8 * mediana and prox[:1].isupper():
            pars.append(" ".join(atual))
            atual = []
    if atual:
        pars.append(" ".join(atual))
    return [p.strip('"“” ') for p in pars]


def pdf_para_texto(pdf: Path) -> Path:
    """Converte um PDF em .txt ao lado dele (só se o .txt ainda não existir)."""
    destino = pdf.with_suffix(".txt")
    if not destino.exists():
        import pymupdf  # só quando precisa
        doc = pymupdf.open(pdf)
        destino.write_text("\n".join(p.get_text() for p in doc), encoding="utf-8")
    return destino


# ------------------------------------------------------------
# Extratores, um por formato de fonte
# ------------------------------------------------------------

_NOME = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõçü]+"
_RE_NUMERADO = re.compile(rf"^\s*\d+\.\s+({_NOME}(?:\s+(?:d[aeo]s?|e|{_NOME}))+)\s*$")
_RE_REDACAO_DE = re.compile(r"^Redação de (.+?)\s*$")
_RE_CAIXA_ALTA = re.compile(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}(?:\s+(?:D[AEO]S?|E|[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,})){1,6})\s*$")
_NAO_E_NOME = {"CARTILHA DO PARTICIPANTE", "VOLTAR PARA", "CARTILHA ENEM", "O SUMÁRIO", "COMENTÁRIO"}
_RE_CABECALHO_PAGINA = re.compile(r"^\s*(\d+|VOLTAR PARA|O SUMÁRIO|CARTILHA.*|T9.*)\s*$")


def extrair_cartilha_inep(texto: str, ano_cartilha: int) -> list[dict]:
    """Cartilhas de 2019, 2022, 2024 e 2025: nome do aluno (numerado, "Redação
    de NOME" ou em caixa alta), texto, e um bloco COMENTÁRIO do INEP depois."""
    enem, tema = CARTILHAS_INEP[ano_cartilha]
    L = texto.splitlines()
    candidatos = []
    for i, linha in enumerate(L):
        m = _RE_NUMERADO.match(linha) or _RE_REDACAO_DE.match(linha)
        if not m:
            m2 = _RE_CAIXA_ALTA.match(linha)
            if m2 and m2.group(1) not in _NAO_E_NOME and len(m2.group(1).split()) >= 2:
                m = m2
        if not m:
            continue
        fim = next((j for j in range(i + 1, min(i + 140, len(L))) if "COMENTÁRIO" in L[j]), None)
        if fim and fim - i > 12:
            candidatos.append((i, m.group(1).strip(), fim))
    # vence o cabeçalho mais perto do COMENTÁRIO ("Textos motivadores" não rouba a redação)
    por_fim = {fim: (i, nome, fim) for i, nome, fim in candidatos}
    saida = []
    for i, nome, fim in por_fim.values():
        corpo = [l for l in L[i + 1:fim] if not _RE_CABECALHO_PAGINA.match(l)]
        ls = [l for l in corpo if l.strip()]
        leg = sum(legibilidade(l) for l in ls) / max(len(ls), 1)
        if leg < 0.8:
            continue
        pars = dividir_paragrafos(corpo)
        comentario = []
        for l in L[fim + 1:fim + 40]:
            if _RE_NUMERADO.match(l) or _RE_REDACAO_DE.match(l) or "VOLTAR PARA" in l:
                break
            comentario.append(l.strip())
        saida.append(dict(
            fonte="cartilha INEP", nivel_fonte="oficial (INEP)", cartilha=ano_cartilha, enem=enem, tema=tema,
            autor=nome.title() if nome.isupper() else nome, nota=1000,
            introducao=pars[0] if pars else None, n_paragrafos=len(pars), legibilidade=round(leg, 2),
            texto="\n\n".join(pars), comentario_inep=" ".join(comentario)))
    return saida


def extrair_cartilha_2020(texto: str) -> list[dict]:
    """Cartilha de 2020 (redações do ENEM 2019): nome em caixa alta colado no
    começo do texto e um "Comentário:" depois de cada redação."""
    L = texto.splitlines()
    comentarios = [i for i, l in enumerate(L) if l.startswith("Comentário")]
    cabecalhos = [i for i, l in enumerate(L) if l.strip() == "CARTILHA DO PARTICIPANTE"]
    inicio_amostra = next((i for i, l in enumerate(L) if "AMOSTRA DE REDAÇÕES NOTA 1.000" in l and i > 100), 0)
    saida, anterior = [], inicio_amostra
    for c in comentarios:
        hs = [h for h in cabecalhos if anterior < h < c]
        comeco = hs[0] + 1 if hs else anterior + 1
        corpo = [l for l in L[comeco:c] if l.strip() and not _RE_CABECALHO_PAGINA.match(l)]
        corrido = re.sub(r"^REDAÇÃO DO ENEM 2020\s+", "", " ".join(x.strip() for x in corpo))
        m = re.match(r"^((?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}\s+){1,6})", corrido)
        nome = m.group(1).strip().title().replace(" De ", " de ") if m else None
        corrido = corrido[m.end():] if m else corrido
        fim_com = next((j for j in range(c + 1, min(c + 40, len(L))) if L[j].strip() == "CARTILHA DO PARTICIPANTE"), c + 20)
        saida.append(dict(
            fonte="cartilha INEP", nivel_fonte="oficial (INEP)", cartilha=2020, enem=2019, tema=TEMA_2019,
            autor=nome, nota=1000, texto=corrido, url=URL_CARTILHA_2020,
            comentario_inep=" ".join(x.strip() for x in L[c + 1:fim_com])))
        anterior = c
    return saida


def _registro_redamil(enem: int, tema: str | None, autor: str | None, info: str | None, pars: list[str]) -> dict:
    autor = re.sub(r"\s*\((?:ela|ele|elu)[^)]*\)", "", autor or "").strip()
    return dict(fonte="Redação a Mil", nivel_fonte="compilação com espelho oficial", enem=enem, tema=tema,
                autor=autor, nota=1000, introducao=pars[0] if len(pars) >= 3 else None, n_paragrafos=len(pars),
                texto="\n\n".join(pars), url=URL_REDAMIL, comentario_inep=info)


def _coletar_ate_fecha_aspas(L: list[str], inicio: int) -> list[str]:
    linhas, k = [], inicio
    while k < len(L):
        t = " ".join(L[k].split())
        if t:
            linhas.append(t)
            if t.endswith(('"', "”")) and len(" ".join(linhas)) > 600:
                break
        k += 1
    return linhas


def extrair_redamil(texto: str, edicao: int) -> list[dict]:
    """Redação a Mil 3.0 a 7.0: "Nome", "idade | cidade | @", "Espelho",
    "Transcrição" e o texto entre aspas. O tema vem do bloco "Tema:"."""
    enem = EDICOES_REDAMIL[edicao]
    L = texto.splitlines()
    tema = None
    saida = []
    for i, linha in enumerate(L):
        s = linha.strip()
        if s == "Tema:" and i + 1 < len(L):
            tema = L[i + 1].strip().strip('"“”')
        if s != "Transcrição":
            continue
        j = i + 1
        while j < len(L) and not L[j].strip():
            j += 1
        if j >= len(L) or not L[j].strip().startswith(('"', "“")):
            continue  # "Transcrição" do sumário
        info_idx = next((k for k in range(i - 1, max(i - 12, 0), -1) if "|" in L[k]), None)
        autor = L[info_idx - 1].strip() if info_idx else None
        info = L[info_idx].strip() if info_idx else None
        saida.append(_registro_redamil(enem, tema, autor, info, dividir_paragrafos(_coletar_ate_fecha_aspas(L, j))))
    return saida


def extrair_redamil_v2(texto: str) -> list[dict]:
    """Redação a Mil 2.0 (ENEM 2019): sem "Transcrição"; a âncora é a linha
    "NN anos | cidade | @perfil", com o nome na linha anterior."""
    L = [l for l in (" ".join(x.split()) for x in texto.splitlines()) if l]
    saida = []
    for i, linha in enumerate(L):
        if not (re.search(r"\d+ anos \|", linha) and "@" in linha):
            continue
        j = next((k for k in range(i + 1, min(i + 8, len(L))) if L[k].startswith(('"', "“"))), None)
        if j is None:
            continue
        saida.append(_registro_redamil(2019, TEMA_2019, L[i - 1], linha, dividir_paragrafos(_coletar_ate_fecha_aspas(L, j))))
    return saida


_INICIO_D1 = re.compile(r"\b(Em primeiro lugar|Em primeira análise|Primeiramente|Inicialmente|De início|A princípio|"
                        r"Diante desse cenário|Sob essa ótica|Em primeiro plano|Nesse sentido, é)")


def extrair_redamil_v1(texto: str) -> list[dict]:
    """Redação a Mil 1.0 (ENEM 2018): texto quebrado, uma palavra por linha,
    com números de página no meio. Âncora: "NN anos" com o nome antes; o
    texto vai da aspa de abertura até uma linha só com a aspa de fechamento.
    Parágrafos não dá pra recuperar; a introdução vai até o primeiro conector
    típico de desenvolvimento."""
    t = texto.replace("​", "").replace("\xa0", " ")
    L = [l for l in (" ".join(x.split()) for x in t.splitlines()) if l]
    saida = []
    for k, linha in enumerate(L):
        if not re.fullmatch(r"\d{2} anos( \|.*)?", linha):
            continue
        s = next((j for j in range(k + 1, min(k + 6, len(L))) if L[j].startswith(('"', "“"))), None)
        if s is None:
            continue
        palavras, j = [], s + 1
        while j < len(L) and L[j] not in ('"', "”"):
            if not re.fullmatch(r"\d{1,3}", L[j]):
                palavras.append(L[j])
            j += 1
        corrido = " ".join(palavras)
        if len(corrido) <= 800:
            continue
        m = _INICIO_D1.search(corrido[150:])
        registro = _registro_redamil(2018, TEMA_2018, L[k - 1], linha, [corrido])
        registro.update(introducao=corrido[:150 + m.start()].strip() if m else None, n_paragrafos=None)
        saida.append(registro)
    return saida


# ------------------------------------------------------------
# Banco
# ------------------------------------------------------------

def gravar(con: sqlite3.Connection, registros: list[dict]) -> None:
    con.executemany(
        f"INSERT INTO redacoes ({', '.join(COLUNAS)}) VALUES ({', '.join('?' * len(COLUNAS))})",
        [tuple(r.get(c) for c in COLUNAS) for r in registros])


def carregar_csv_manual(con: sqlite3.Connection, pasta_manual: Path) -> None:
    """Dados feitos à mão durante a coleta (esqueletos de portal, metadados do
    IFMG, relatos e a classificação das aberturas das cartilhas)."""
    esq = pasta_manual / "esqueletos.csv"
    if esq.exists():
        with esq.open(encoding="utf-8") as f:
            gravar(con, [{k: (v or None) for k, v in linha.items()} for linha in csv.DictReader(f)])
    rel = pasta_manual / "relatos.csv"
    if rel.exists():
        with rel.open(encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
        con.executemany("INSERT INTO relatos (nome, nota_redacao, ano_enem, origem, o_que_fez, url, nivel_fonte) "
                        "VALUES (:nome, :nota_redacao, :ano_enem, :origem, :o_que_fez, :url, :nivel_fonte)", linhas)
    ab = pasta_manual / "aberturas_cartilhas.csv"
    if ab.exists():
        with ab.open(encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                con.execute("UPDATE redacoes SET abertura_tipo = ?, abertura_repertorio = ? "
                            "WHERE fonte = 'cartilha INEP' AND enem = ? AND autor = ?",
                            (linha["abertura_tipo"], linha["abertura_repertorio"], linha["enem"], linha["autor"]))


_PRIORIDADE = {"cartilha INEP": 0, "IFMG": 1, "Redação a Mil": 2, "portal": 3}


def marcar_duplicadas(con: sqlite3.Connection) -> int:
    """A mesma redação pode vir de várias fontes: fica a mais confiável
    (INEP > IFMG > Redação a Mil > portal); as outras apontam pra ela."""
    linhas = con.execute("SELECT id, fonte, enem, autor FROM redacoes").fetchall()
    linhas.sort(key=lambda r: (_PRIORIDADE.get(r[1], 9), r[0]))
    vistos: dict[tuple[int, str], int] = {}
    dup = 0
    for id_, _, enem, autor in linhas:
        chave = chave_duplicata(enem, autor)
        original = vistos.get(chave)
        con.execute("UPDATE redacoes SET duplicada_de = ? WHERE id = ?", (original, id_))
        if original is None:
            vistos[chave] = id_
        else:
            dup += 1
    return dup


def construir_banco(pasta: Path, destino: Path | None = None) -> dict:
    """Reconstrói o banco do zero a partir das fontes na pasta (idempotente)."""
    destino = destino or pasta / "redacoes_1000.db"
    if destino.exists():
        destino.unlink()
    con = sqlite3.connect(destino)
    con.executescript(SCHEMA)
    cartilhas = pasta.parent / "cartilhas"
    for ano in CARTILHAS_INEP:
        txt = cartilhas / f"cartilha_{ano}.txt"
        if txt.exists():
            gravar(con, extrair_cartilha_inep(txt.read_text(encoding="utf-8", errors="replace"), ano))
    pdf_2020 = cartilhas / "cartilha_2020.pdf"
    if pdf_2020.exists():
        gravar(con, extrair_cartilha_2020(pdf_para_texto(pdf_2020).read_text(encoding="utf-8")))
    redamil = pasta / "redamil"
    for edicao in EDICOES_REDAMIL:
        pdf = redamil / f"redamil_v{edicao}.pdf"
        if not pdf.exists():
            continue
        texto = pdf_para_texto(pdf).read_text(encoding="utf-8")
        extrator = {1: extrair_redamil_v1, 2: extrair_redamil_v2}.get(edicao)
        gravar(con, extrator(texto) if extrator else extrair_redamil(texto, edicao))
    carregar_csv_manual(con, pasta / "manual")
    dup = marcar_duplicadas(con)
    con.commit()
    resumo = {
        "total": con.execute("SELECT COUNT(*) FROM redacoes").fetchone()[0],
        "duplicadas": dup,
        "por_enem": dict(con.execute("SELECT enem, COUNT(*) FROM redacoes WHERE duplicada_de IS NULL "
                                     "GROUP BY enem ORDER BY enem").fetchall()),
        "relatos": con.execute("SELECT COUNT(*) FROM relatos").fetchone()[0],
    }
    resumo["unicas"] = sum(resumo["por_enem"].values())
    con.close()
    return resumo


# ------------------------------------------------------------
# Estatísticas (alimentam docs/redacao_pesquisa/padroes_1000.md)
# ------------------------------------------------------------

REPERTORIOS = {
    "Constituição": r"constituic", "Dimenstein": r"dimenstein", "Simone de Beauvoir": r"beauvoir",
    "Milton Santos": r"milton santos", "Kant": r"\bkant", "Bauman": r"bauman", "Hannah Arendt": r"arendt",
    "Durkheim": r"durkheim", "Carolina Maria de Jesus": r"carolina maria de jesus|quarto de despejo",
    "Djamila Ribeiro": r"djamila", "Paulo Freire": r"paulo freire", "Aristóteles": r"aristoteles",
    "Sérgio Buarque": r"buarque|homem cordial", "Boaventura": r"boaventura", "Ailton Krenak": r"krenak",
    "Mbembe": r"mbembe|necropolit", "Foucault": r"foucault", "Chomsky": r"chomsky",
}
_ESTADO = r"estat|governament|poder public|\bestado\b|governo|legisla|politic"
_SOCIAL = r"social|sociedade|populac|cultur|preconceit|midi|coletiv|familia|machis|patriarc|etaris|estigm|racis|mentalidade|senso comum"


def estatisticas(db_path: Path) -> dict:
    """Contagens sobre as redações únicas. Heurística por palavra-chave:
    boa pra tendência, não exata."""
    con = sqlite3.connect(db_path)
    linhas = con.execute("SELECT introducao, texto, abertura_tipo, causa_1, causa_2, rep_d1, rep_d2, "
                         "abertura_repertorio FROM redacoes WHERE duplicada_de IS NULL").fetchall()
    con.close()
    reps: Counter = Counter()
    causas = Counter()
    for intro, texto, _, c1, c2, d1, d2, ab in linhas:
        tudo = normalizar(" ".join(x or "" for x in (texto, d1, d2, ab)))
        for nome, padrao in REPERTORIOS.items():
            if re.search(padrao, tudo):
                reps[nome] += 1
        base = normalizar(f"{c1 or ''} {c2 or ''}") if c1 else (normalizar(intro)[-350:] if intro else "")
        if base:
            causas["analisadas"] += 1
            e, s = bool(re.search(_ESTADO, base)), bool(re.search(_SOCIAL, base))
            causas["estado"] += e
            causas["social"] += s
            causas["ambas"] += e and s
    return {"unicas": len(linhas), "repertorios": reps.most_common(), "causas": dict(causas)}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    pasta_banco = Path(sys.argv[1]).resolve()
    resumo = construir_banco(pasta_banco)
    print(f"{resumo['unicas']} redações únicas ({resumo['duplicadas']} repetidas entre fontes), "
          f"{resumo['relatos']} relatos")
    print("por ENEM:", resumo["por_enem"])
    est = estatisticas(pasta_banco / "redacoes_1000.db")
    print("causas:", est["causas"])
    print("repertórios:", est["repertorios"][:12])
