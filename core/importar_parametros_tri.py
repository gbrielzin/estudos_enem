"""importar_parametros_tri.py — grava em cada questão oficial os
parâmetros TRI (tri_a, tri_b, tri_c) e a habilidade (H1-H30) do item
correspondente no ITENS_PROVA oficial do INEP (core/inep_itens/).

tri_b é a dificuldade oficial do item: é o que permite separar questão
fácil/média/difícil sem palpite (ver db.nivel_tri()).

Ligação questão -> item: para cada (ano, caderno, área) do banco, escolhe
o CO_PROVA da mesma cor cujo gabarito por CO_POSICAO mais bate com o do
banco (mesma ideia de copiar_enunciado_entre_cadernos.py). Exige >= 90%
de concordância (o resto costuma ser item anulado, gabarito "X"); abaixo
disso o caderno é pulado e listado. Questão cujo gabarito diverge do item
nunca é gravada.

Só escreve tri_a/tri_b/tri_c/habilidade via db.atualizar_parametros_tri()
— nunca cria questão nem mexe em matéria/gabarito/tópico. Idempotente:
rodar de novo regrava os mesmos valores (rode depois de reconstruir_base.py
ou de importar prova nova).

Uso (de dentro de core/):
    python importar_parametros_tri.py            # só leitura: cobertura por caderno
    python importar_parametros_tri.py --aplicar  # backup + grava
"""
import csv
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import backup_db
import db

PASTA_ITENS = Path(__file__).parent / "inep_itens"
COR_INEP = {"azul": "AZUL", "amarelo": "AMARELA", "cinza": "CINZA", "rosa": "ROSA", "verde": "VERDE", "branco": "BRANCA"}
AREA_INEP = {"ciencias_natureza": "CN", "matematica": "MT"}
CONCORDANCIA_MINIMA = 0.9


def _num(valor: str) -> float | None:
    valor = (valor or "").strip().replace(",", ".")
    return float(valor) if valor else None


def _itens_por_prova(ano: int, sigla_area: str, pasta: Path = PASTA_ITENS) -> dict[tuple[str, str], dict[int, dict]]:
    caminho = pasta / f"{ano}_ITENS_PROVA_{ano}.csv"
    por_prova: dict[tuple[str, str], dict[int, dict]] = defaultdict(dict)
    if not caminho.exists():
        return por_prova
    with open(caminho, encoding="latin-1") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["SG_AREA"] == sigla_area:
                por_prova[(r["TX_COR"].upper(), r["CO_PROVA"])][int(r["CO_POSICAO"])] = r
    return por_prova


def ligar_caderno(gabarito: dict[int, str], por_prova, cor_inep: str) -> tuple[str | None, float, dict[int, dict]]:
    """Melhor CO_PROVA da cor para esse gabarito: (co_prova, concordância,
    itens indexados pelo numero_questao do banco).

    Em alguns anos o INEP numera a área diferente do caderno impresso
    (2016: CN em 91-135 no ITENS_PROVA, 46-90 no banco; 2017: 1-45 x
    91-135), então além da posição exata testa o deslocamento que alinha
    as primeiras posições. A concordância do gabarito decide qual vale.
    """
    melhor = (None, 0.0, {})
    if not gabarito:
        return melhor
    for (cor, co_prova), itens in por_prova.items():
        if cor != cor_inep or not itens:
            continue
        for desloc in {0, min(itens) - min(gabarito)}:
            alinhados = {n: itens[n + desloc] for n in gabarito if n + desloc in itens}
            iguais = sum(1 for n, g in gabarito.items() if n in alinhados and alinhados[n]["TX_GABARITO"] == g)
            taxa = iguais / len(gabarito)
            if taxa > melhor[1]:
                melhor = (co_prova, taxa, alinhados)
    return melhor


def montar_parametros(pasta: Path = PASTA_ITENS) -> tuple[list[tuple], list[str]]:
    """Lista de (id_questao, a, b, c, habilidade) a gravar + relatório por caderno."""
    with sqlite3.connect(db.DB_PATH) as conn:
        linhas = conn.execute(
            "SELECT ano, caderno, grande_area, numero_questao, alternativa_correta, id_questao "
            "FROM questoes WHERE origem = 'enem_oficial'"
        ).fetchall()
    cadernos: dict[tuple, dict[int, tuple[str, str]]] = defaultdict(dict)
    for ano, caderno, area, numero, correta, id_questao in linhas:
        if area in AREA_INEP:
            cadernos[(ano, caderno, area)][numero] = (correta, id_questao)

    a_gravar, relatorio = [], []
    for (ano, caderno, area), questoes in sorted(cadernos.items()):
        rotulo = f"{ano} {caderno} {AREA_INEP[area]}"
        cor = COR_INEP.get(caderno)
        if cor is None:
            relatorio.append(f"{rotulo}: cor de caderno desconhecida, pulado")
            continue
        gabarito = {n: g for n, (g, _) in questoes.items()}
        co_prova, taxa, itens = ligar_caderno(gabarito, _itens_por_prova(ano, AREA_INEP[area], pasta), cor)
        if taxa < CONCORDANCIA_MINIMA:
            relatorio.append(f"{rotulo}: melhor CO_PROVA {co_prova} bate {taxa:.0%}, pulado")
            continue
        gravadas = 0
        for numero, (correta, id_questao) in questoes.items():
            item = itens.get(numero)
            if item is None or item["TX_GABARITO"] != correta or _num(item["NU_PARAM_B"]) is None:
                continue
            habilidade = _num(item.get("CO_HABILIDADE", ""))
            a_gravar.append((
                id_questao, _num(item["NU_PARAM_A"]), _num(item["NU_PARAM_B"]), _num(item["NU_PARAM_C"]),
                int(habilidade) if habilidade is not None else None,
            ))
            gravadas += 1
        relatorio.append(f"{rotulo}: CO_PROVA {co_prova} bate {taxa:.0%}, {gravadas}/{len(questoes)} com TRI")
    return a_gravar, relatorio


def main(argv: list[str]) -> None:
    a_gravar, relatorio = montar_parametros()
    print("\n".join(relatorio))
    print(f"\nTotal: {len(a_gravar)} questões com parâmetros TRI.")
    if "--aplicar" not in argv:
        print("Só leitura. Rode de novo com --aplicar para gravar (faz backup antes).")
        return
    db.inicializar_banco()
    print(f"Backup: {backup_db.fazer_backup()}")
    for id_questao, a, b, c, habilidade in a_gravar:
        db.atualizar_parametros_tri(id_questao, a, b, c, habilidade)
    print(f"Gravado: {len(a_gravar)} questões.")


if __name__ == "__main__":
    main(sys.argv[1:])
