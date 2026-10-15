"""
uso_admin.py — resumo de uso por pessoa, para o painel de admin (/admin/uso).

Responde "a pessoa do beta usou o app? voltou?" sem guardar dado novo:
lê só o que cada banco já tem (`tentativas_usuario`, ver adr/0010) e
calcula na hora. Nada de IP, aparelho ou registro de acesso.

Abre cada banco em modo somente leitura (`?mode=ro`): o painel nunca
escreve no banco de ninguém, nem migração. Por isso não reaproveita as
funções de db.py (resumo_geral_desempenho etc.): elas usam o banco da
requisição e a conexão de escrita de lá. Só biblioteca padrão.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path


def _voltou(dias: set[date], primeiro: date, de: int, ate: int, hoje: date) -> bool | None:
    """Teve atividade em algum dia entre primeiro+de e primeiro+ate?

    None = ainda não dá pra saber: a janela não terminou e ele ainda não
    voltou. Sem isso, quem começou ontem apareceria como "não voltou"."""
    janela = {primeiro + timedelta(days=n) for n in range(de, ate + 1)}
    if dias & janela:
        return True
    if hoje <= primeiro + timedelta(days=ate):
        return None
    return False


def resumo_banco(caminho: Path, hoje: date) -> dict:
    """Resumo de uso de um banco. Erro de leitura (arquivo que falta, que
    não é banco do app, data fora do formato) vira o campo "erro", sem
    derrubar o painel inteiro."""
    resumo = {
        "usuario": caminho.stem,
        "primeira_atividade": None,
        "ultima_atividade": None,
        "tentativas": 0,
        "questoes": 0,
        "taxa_acerto": None,
        "voltou_d1": None,
        "voltou_d7": None,
    }
    try:
        uri = f"{caminho.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as conn:
            primeira, ultima, total, questoes, acertos = conn.execute(
                """
                SELECT MIN(data_tentativa), MAX(data_tentativa), COUNT(*),
                       COUNT(DISTINCT id_questao),
                       SUM(CASE WHEN resultado = 'acertou' THEN 1 ELSE 0 END)
                FROM tentativas_usuario
                """
            ).fetchone()
            # Um dia por linha (mesmo padrão de db.calcular_ofensiva); data
            # fora do formato vira NULL no date() do SQLite e fica de fora.
            dias = {
                date.fromisoformat(d)
                for (d,) in conn.execute(
                    "SELECT DISTINCT date(data_tentativa) FROM tentativas_usuario WHERE date(data_tentativa) IS NOT NULL"
                )
            }
    except (sqlite3.Error, ValueError) as erro:
        return {**resumo, "erro": str(erro)}

    if not total:
        return resumo
    if not dias:
        return {**resumo, "tentativas": total, "erro": "data_tentativa fora do formato AAAA-MM-DD"}
    primeiro_dia = min(dias)
    return {
        **resumo,
        "primeira_atividade": primeira,
        "ultima_atividade": ultima,
        "tentativas": total,
        "questoes": questoes,
        "taxa_acerto": round((acertos or 0) / total, 3),
        # D1: voltou no dia seguinte ao primeiro. D7: voltou em algum dia da
        # semana seguinte (do 1º ao 7º dia depois do primeiro).
        "voltou_d1": _voltou(dias, primeiro_dia, 1, 1, hoje),
        "voltou_d7": _voltou(dias, primeiro_dia, 1, 7, hoje),
    }


def resumo_uso(pasta: Path, nomes: list[str] | None = None, hoje: date | None = None) -> list[dict]:
    """Um resumo por pessoa, quem usou por último primeiro e quem nunca
    respondeu nada no fim.

    `nomes` = as pessoas de API_USUARIOS: só elas entram, então banco de
    quem saiu do beta ou cópia de backup na pasta não vira "pessoa" nem
    infla o D1/D7. Sem `nomes` (modo de uma pessoa só), lista todo `*.db`
    da pasta; pasta que não existe devolve lista vazia."""
    hoje = hoje or date.today()
    if nomes is not None:
        caminhos = [pasta / f"{nome}.db" for nome in nomes]
    elif pasta.is_dir():
        caminhos = sorted(pasta.glob("*.db"))
    else:
        return []
    resumos = [resumo_banco(caminho, hoje) for caminho in caminhos]
    return sorted(resumos, key=lambda r: r["ultima_atividade"] or "", reverse=True)
