"""copiar_enunciado_entre_cadernos.py — preenche o enunciado de um caderno
(ex: 2024 azul, que ficou sem texto) copiando do MESMO item em outro caderno
do mesmo ano que já tem texto (ex: 2024 amarelo).

Cadernos de cor diferente são a mesma prova com as questões em ordem
embaralhada — a ordem das alternativas não muda. Qual posição de um caderno
corresponde a qual do outro vem do ITENS_PROVA oficial do INEP
(core/inep_itens/): o mesmo CO_ITEM aparece em cada CO_PROVA, cada um na sua
CO_POSICAO. Nada de casar por texto ou por palpite.

Checagens antes de gravar (aborta sem gravar nada se falharem):
  - escolhe, entre os vários CO_PROVA de cada cor (aplicação regular,
    reaplicação...), o que bate 100% com o gabarito já carregado no enem.db;
  - os dois CO_PROVA escolhidos têm exatamente o mesmo conjunto de itens;
  - para cada par mapeado, o gabarito do destino é igual ao da origem.

Só escreve enunciado_texto/enunciado_imagem_path via db.atualizar_enunciado()
(mesma função dos outros scripts de extração) — nunca cria questão nem mexe
em matéria/gabarito/tópico. Sem --sobrescrever, só preenche questão que está
sem texto.

Uso (de dentro de core/):
    python copiar_enunciado_entre_cadernos.py 2024 amarelo azul            # só leitura
    python copiar_enunciado_entre_cadernos.py 2024 amarelo azul --aplicar  # backup + grava
"""
import csv
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import backup_db
import db

AQUI = Path(__file__).parent
COR_INEP = {"azul": "AZUL", "amarelo": "AMARELA", "cinza": "CINZA", "rosa": "ROSA", "verde": "VERDE"}
AREA_INEP = {"ciencias_natureza": "CN", "matematica": "MT"}


def _itens_por_prova(ano: int, sigla_area: str) -> dict[tuple[str, str], dict[int, dict]]:
    caminho = AQUI / "inep_itens" / f"{ano}_ITENS_PROVA_{ano}.csv"
    por_prova: dict[tuple[str, str], dict[int, dict]] = defaultdict(dict)
    with open(caminho, encoding="latin-1") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["SG_AREA"] == sigla_area:
                por_prova[(r["TX_COR"], r["CO_PROVA"])][int(r["CO_POSICAO"])] = r
    return por_prova


def _gabarito_banco(conn, ano: int, caderno: str, area: str) -> dict[int, str]:
    return dict(conn.execute(
        "SELECT numero_questao, alternativa_correta FROM questoes "
        "WHERE ano = ? AND caderno = ? AND grande_area = ?",
        (ano, caderno, area),
    ))


def _escolher_prova(por_prova, cor_inep: str, gabarito: dict[int, str]) -> tuple[str, dict[int, dict]]:
    """CO_PROVA da cor cujo gabarito bate 100% com o do banco."""
    for (cor, co_prova), itens in por_prova.items():
        if cor != cor_inep:
            continue
        if gabarito and all(n in itens and itens[n]["TX_GABARITO"] == g for n, g in gabarito.items()):
            return co_prova, itens
    raise SystemExit(f"Nenhum CO_PROVA {cor_inep} bate 100% com o gabarito do banco -- abortando.")


def montar_pares(ano: int, origem: str, destino: str, area: str = "ciencias_natureza"):
    por_prova = _itens_por_prova(ano, AREA_INEP[area])
    with sqlite3.connect(db.DB_PATH) as conn:
        gab_origem = _gabarito_banco(conn, ano, origem, area)
        gab_destino = _gabarito_banco(conn, ano, destino, area)
    prova_o, itens_o = _escolher_prova(por_prova, COR_INEP[origem], gab_origem)
    prova_d, itens_d = _escolher_prova(por_prova, COR_INEP[destino], gab_destino)
    print(f"CO_PROVA origem {origem}={prova_o}, destino {destino}={prova_d}")

    posicao_origem = {r["CO_ITEM"]: pos for pos, r in itens_o.items()}
    if set(posicao_origem) != {r["CO_ITEM"] for r in itens_d.values()}:
        raise SystemExit("Os dois cadernos não têm o mesmo conjunto de itens -- abortando.")

    pares = []
    for n_destino in sorted(gab_destino):
        n_origem = posicao_origem[itens_d[n_destino]["CO_ITEM"]]
        if gab_origem.get(n_origem) != gab_destino[n_destino]:
            raise SystemExit(f"Gabarito diverge: {destino} {n_destino} x {origem} {n_origem} -- abortando.")
        pares.append((f"{ano}_{origem}_{n_origem}", f"{ano}_{destino}_{n_destino}"))
    return pares


def main(argv: list[str]) -> None:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 3:
        raise SystemExit(__doc__)
    ano, origem, destino = int(args[0]), args[1], args[2]
    aplicar, sobrescrever = "--aplicar" in argv, "--sobrescrever" in argv

    pares = montar_pares(ano, origem, destino)
    with sqlite3.connect(db.DB_PATH) as conn:
        linha = lambda i: conn.execute(
            "SELECT enunciado_texto, enunciado_imagem_path FROM questoes WHERE id_questao = ?", (i,)
        ).fetchone()
        a_gravar = []
        for id_o, id_d in pares:
            texto_o, img_o = linha(id_o)
            texto_d, _ = linha(id_d)
            if texto_o is None or (texto_d is not None and not sobrescrever):
                continue
            a_gravar.append((id_o, id_d, texto_o, img_o))

    print(f"{len(pares)} pares mapeados, {len(a_gravar)} a preencher em {destino}.")
    for id_o, id_d, *_ in a_gravar[:5]:
        print(f"  {id_d} <- {id_o}")
    if not aplicar:
        print("Só leitura. Rode de novo com --aplicar para gravar (faz backup antes).")
        return
    print(f"Backup: {backup_db.fazer_backup()}")
    for _, id_d, texto, img in a_gravar:
        db.atualizar_enunciado(id_d, texto=texto, imagem_path=img)
    print(f"Gravado: {len(a_gravar)} enunciados.")


if __name__ == "__main__":
    main(sys.argv[1:])
