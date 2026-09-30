"""Procura vídeos sobre redação/ENEM no YouTube-Commons (PleIAs, Hugging Face).

YouTube-Commons é um dataset aberto (CC-BY 4.0) com transcrições de vídeos do
YouTube cujos autores os liberaram com licença livre. São 439 arquivos
Parquet, ~163 GB no total. Com DuckDB lemos só as colunas pequenas (título,
canal, idioma) direto da internet, sem baixar os arquivos; a transcrição
(`text`) só é lida para os vídeos que passam no filtro.

Achado da primeira coleta (30/09/2026, arquivos 0-133 de 439): o dataset
guarda uma linha por TRADUÇÃO automática da transcrição. O filtro antigo
aceitava o vídeo quando o idioma ORIGINAL era português e salvou 471 linhas
que eram só 76 vídeos, cada um em 7 traduções (de, ru, it, fr, en, es, nl) e
nenhuma em português. Por isso o filtro agora exige a transcrição em si em
português; se o dataset não tiver o original, o resultado vem vazio, e isso
é informação: o YouTube-Commons não serve de fonte de texto de redação em PT.

Uso (da pasta core/):
    python youtube_commons_redacao.py ../docs/redacao_pesquisa/banco_1000/youtube_commons.csv
"""
from __future__ import annotations

import csv
import hashlib
import os
import sys

BASE = "https://huggingface.co/datasets/PleIAs/YouTube-Commons/resolve/main/cctube_{n}.parquet"
N_ARQUIVOS = 439
# "enem" como palavra inteira: com ILIKE '%enem%' entravam títulos como
# "Invading the Enemy Field" (airsoft).
FILTRO_TITULO = r"regexp_matches(title, '(?i)(\benem\b|reda[cç][aã]o|nota (mil|1000)|dissertativ)')"
# Só a transcrição conta: original_language 'pt' com transcrição 'de' é
# tradução automática (ver o achado no topo).
FILTRO_IDIOMA = "transcription_language ILIKE 'pt%'"


def consulta(fonte: str) -> str:
    """SELECT dos vídeos em português com título de redação/ENEM. `fonte` é
    o que vai no FROM (read_parquet(url) na coleta, uma tabela nos testes)."""
    return (f"SELECT video_id, video_link, title, channel, transcription_language, word_count, license, text "
            f"FROM {fonte} WHERE ({FILTRO_IDIOMA}) AND ({FILTRO_TITULO})")


def assinatura_filtro() -> str:
    """Muda sempre que o filtro muda: o progresso de uma coleta feita com
    outro filtro não pode ser reaproveitado."""
    return hashlib.sha1(consulta("x").encode("utf-8")).hexdigest()[:12]


def ler_progresso(prog: str) -> set[int]:
    """Arquivos já lidos. Primeira linha = `filtro:<assinatura>`. Se o
    progresso é de outro filtro (ou do formato antigo, sem assinatura), para
    em vez de pular esses arquivos: o CSV ao lado tem linhas do filtro velho."""
    if not os.path.exists(prog):
        return set()
    with open(prog, encoding="utf-8") as f:
        linhas = f.read().split()
    if not linhas or linhas[0] != f"filtro:{assinatura_filtro()}":
        raise SystemExit(f"{prog} é de uma coleta com outro filtro. Use outro arquivo de saída "
                         f"(ou apague o CSV e o .progresso) pra recomeçar.")
    return {int(x) for x in linhas[1:]}


def chaves_salvas(saida: str) -> set[tuple[str, str]]:
    """(video_id, idioma) já no CSV. Se o processo cair entre gravar as linhas
    e anotar o progresso, o arquivo é relido; isto evita gravar de novo."""
    if not os.path.exists(saida):
        return set()
    csv.field_size_limit(2**31 - 1)
    with open(saida, encoding="utf-8", newline="") as f:
        return {(r["video_id"], r["language"]) for r in csv.DictReader(f)}


def main(saida: str) -> None:
    """Salva o progresso a cada arquivo (em <saida>.progresso) e retoma de
    onde parou: se o processo cair no meio, nada do que já foi lido se perde."""
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET memory_limit='1GB'")
    prog = saida + ".progresso"
    feitos = ler_progresso(prog)
    salvas = chaves_salvas(saida)
    novo_csv = not os.path.exists(saida)
    novo_prog = not os.path.exists(prog)
    with open(saida, "a", encoding="utf-8", newline="") as f_out, open(prog, "a", encoding="utf-8") as f_prog:
        w = csv.writer(f_out)
        if novo_csv:
            w.writerow(["video_id", "video_link", "title", "channel", "language", "word_count", "license", "text"])
        if novo_prog:
            f_prog.write(f"filtro:{assinatura_filtro()}\n")
        for n in range(N_ARQUIVOS):
            if n in feitos:
                continue
            url = BASE.format(n=n)
            try:
                linhas = con.execute(consulta(f"read_parquet('{url}')")).fetchall()
            except Exception as e:  # arquivo fora do ar ou rede instável: tenta na próxima execução
                print(f"cctube_{n}: {str(e)[:80]}", file=sys.stderr)
                continue
            novas = [r for r in linhas if (r[0], r[4]) not in salvas]
            w.writerows(novas)
            salvas.update((r[0], r[4]) for r in novas)
            f_out.flush()
            f_prog.write(f"{n}\n")
            f_prog.flush()
            if n % 20 == 0:
                print(f"{n}/{N_ARQUIVOS} arquivos", file=sys.stderr)
    # vazio é um resultado possível (ver o achado no topo): diz em vez de
    # deixar só o cabeçalho no CSV sem explicação
    print(f"fim -> {saida}: {len(salvas)} transcrições em português no total", file=sys.stderr)
    if not salvas:
        print("nenhuma: o YouTube-Commons não tem transcrição PT desses vídeos", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
