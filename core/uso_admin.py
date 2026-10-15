"""
uso_admin.py — resumo de uso por pessoa, para o painel de admin (/admin/uso).

Responde "a pessoa do beta usou o app? voltou?" sem guardar dado novo:
lê só o que cada banco já tem (`tentativas_usuario`, ver adr/0010) e
calcula na hora. Nada de IP, aparelho ou registro de acesso.

Abre cada banco em modo somente leitura (`?mode=ro`): o painel nunca
escreve no banco de ninguém, nem migração. Só biblioteca padrão, mesmo
espírito de db.py (não importa db.py porque não usa o banco da
requisição: percorre todos os bancos da pasta).
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path


def _dia(texto: str) -> date:
    # data_tentativa vem como 'AAAA-MM-DD HH:MM:SS' (datetime('now','localtime')).
    return datetime.fromisoformat(texto).date()


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
    """Resumo de uso de um banco. Erro de leitura (arquivo que não é
    banco do app) vira o campo "erro", sem derrubar o painel inteiro."""
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
            dias = {_dia(d) for (d,) in conn.execute("SELECT DISTINCT data_tentativa FROM tentativas_usuario")}
    except sqlite3.Error as erro:
        return {**resumo, "erro": str(erro)}

    if not total:
        return resumo
    primeiro_dia = _dia(primeira)
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


def resumo_uso(pasta: Path, hoje: date | None = None) -> list[dict]:
    """Um resumo por banco `<nome>.db` da pasta, quem usou por último
    primeiro e quem nunca respondeu nada no fim. Pasta que não existe
    devolve lista vazia (modo de uma pessoa só, sem bancos por pessoa)."""
    hoje = hoje or date.today()
    if not pasta.is_dir():
        return []
    resumos = [resumo_banco(caminho, hoje) for caminho in sorted(pasta.glob("*.db"))]
    return sorted(resumos, key=lambda r: r["ultima_atividade"] or "", reverse=True)
