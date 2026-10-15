"""
uso_admin.py — resumo de uso por pessoa, para o painel de admin (/admin/uso).

Responde "a pessoa do beta abriu o app? respondeu? voltou? que recurso
usou?" lendo o que cada banco já tem (ver adr/0010): `tentativas_usuario`,
`eventos` (abriu o app, viu tela, deu erro, abriu explicação, respondeu
molde, com aparelho resumido; sem IP) e `respostas_pesquisa` (NPS), e
calculando na hora.

Abre cada banco em modo somente leitura (`?mode=ro`): o painel nunca
escreve no banco de ninguém, nem migração. Por isso não reaproveita as
funções de db.py (resumo_geral_desempenho etc.): elas usam o banco da
requisição e a conexão de escrita de lá. Só biblioteca padrão. Banco
antigo, sem `eventos` ou `respostas_pesquisa`, continua funcionando.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

# Mais de 30 minutos parado = sessão nova (mesmo corte padrão do Google Analytics).
INTERVALO_SESSAO = timedelta(minutes=30)
# Eventos que contam como a pessoa usando o app. `erro` fica de fora: é o
# app que manda sozinho, não a pessoa escolhendo voltar.
TIPOS_ATIVIDADE = ("app_aberto", "tela_vista", "explicacao_aberta", "molde_respondido")


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


def _hora(texto: str | None) -> datetime | None:
    # 'AAAA-MM-DD HH:MM:SS' (datetime('now','localtime')); fora do formato = ignorada.
    try:
        return datetime.fromisoformat(texto) if texto else None
    except ValueError:
        return None


def _sessoes(horas: list[datetime]) -> list[timedelta]:
    """Duração de cada sessão: atividades com menos de 30 min entre si."""
    duracoes: list[timedelta] = []
    inicio = anterior = None
    for hora in sorted(horas):
        if anterior is None or hora - anterior > INTERVALO_SESSAO:
            if inicio is not None:
                duracoes.append(anterior - inicio)
            inicio = hora
        anterior = hora
    if inicio is not None:
        duracoes.append(anterior - inicio)
    return duracoes


def _minutos(delta: timedelta) -> float:
    return round(delta.total_seconds() / 60, 1)


def _tem_tabela(conn: sqlite3.Connection, nome: str) -> bool:
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (nome,)).fetchone() is not None


def resumo_banco(caminho: Path, hoje: date) -> dict:
    """Resumo de uso de um banco. Erro de leitura (arquivo que falta, que
    não é banco do app, data fora do formato) vira o campo "erro", sem
    derrubar o painel inteiro."""
    resumo = {
        "usuario": caminho.stem,
        "primeira_atividade": None,
        "ultima_atividade": None,
        "aberturas": 0,
        "sessoes": 0,
        "minutos_por_sessao": None,
        "minutos_ate_1a_questao": None,
        "origem": None,
        "tentativas": 0,
        "questoes": 0,
        "taxa_acerto": None,
        "explicacoes_abertas": 0,
        "moldes_respondidos": 0,
        "erros": 0,
        "aparelho": None,
        "nota_pesquisa": None,
        "comentario_pesquisa": None,
        "respostas_pesquisa": 0,
        "abriu_sem_responder": False,
        "voltou_d1": None,
        "voltou_d7": None,
    }
    try:
        uri = f"{caminho.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as conn:
            total, questoes, acertos = conn.execute(
                """
                SELECT COUNT(*), COUNT(DISTINCT id_questao),
                       SUM(CASE WHEN resultado = 'acertou' THEN 1 ELSE 0 END)
                FROM tentativas_usuario
                """
            ).fetchone()
            horas_tentativas = [t for (t,) in conn.execute("SELECT data_tentativa FROM tentativas_usuario")]
            eventos = []
            if _tem_tabela(conn, "eventos"):
                # `eventos` da 1ª versão (antes da migração do startup) não tem `detalhe`.
                colunas = {r[1] for r in conn.execute("PRAGMA table_info(eventos)")}
                detalhe = "detalhe" if "detalhe" in colunas else "NULL"
                eventos = conn.execute(
                    f"SELECT criado_em, tipo, {detalhe}, aparelho FROM eventos ORDER BY criado_em, id_evento"
                ).fetchall()
            pesquisa = []
            if _tem_tabela(conn, "respostas_pesquisa"):
                pesquisa = conn.execute(
                    "SELECT nota, comentario FROM respostas_pesquisa ORDER BY criado_em, id_resposta"
                ).fetchall()
    except sqlite3.Error as erro:
        return {**resumo, "erro": str(erro)}

    contagem = {tipo: 0 for tipo in ("app_aberto", "erro", "explicacao_aberta", "molde_respondido")}
    for _, tipo, _, _ in eventos:
        if tipo in contagem:
            contagem[tipo] += 1
    aberturas = [_hora(h) for h, tipo, _, _ in eventos if tipo == "app_aberto"]
    origens = [detalhe for _, tipo, detalhe, _ in eventos if tipo == "app_aberto" and detalhe]
    aparelhos = [aparelho for _, _, _, aparelho in eventos if aparelho]
    resumo.update(
        aberturas=contagem["app_aberto"],
        erros=contagem["erro"],
        explicacoes_abertas=contagem["explicacao_aberta"],
        moldes_respondidos=contagem["molde_respondido"],
        origem=origens[0] if origens else None,  # o 1º link que a pessoa usou
        aparelho=aparelhos[-1] if aparelhos else None,  # o mais recente
        tentativas=total,
        questoes=questoes,
        respostas_pesquisa=len(pesquisa),
    )
    if total:
        resumo["taxa_acerto"] = round((acertos or 0) / total, 3)
    if pesquisa:
        resumo["nota_pesquisa"], resumo["comentario_pesquisa"] = pesquisa[-1]

    # Atividade = responder questão OU evento da pessoa usando o app.
    textos = horas_tentativas + [h for h, tipo, _, _ in eventos if tipo in TIPOS_ATIVIDADE]
    horas = [(hora, texto) for texto in textos if (hora := _hora(texto))]
    # O caso que o painel mais precisa mostrar: abriu o app e travou antes da 1ª questão.
    resumo["abriu_sem_responder"] = bool(textos) and not total
    if not textos:
        return resumo
    if not horas:
        return {**resumo, "erro": "data fora do formato AAAA-MM-DD HH:MM:SS"}

    primeira, ultima = min(horas), max(horas)
    duracoes = _sessoes([h for h, _ in horas])
    resumo.update(
        primeira_atividade=primeira[1],
        ultima_atividade=ultima[1],
        sessoes=len(duracoes),
        minutos_por_sessao=_minutos(sum(duracoes, timedelta()) / len(duracoes)),
    )
    # Ativação: da 1ª abertura até a 1ª resposta (só se abriu antes de responder).
    hora_tentativas = [h for t in horas_tentativas if (h := _hora(t))]
    hora_aberturas = [h for h in aberturas if h]
    if hora_tentativas and hora_aberturas and min(hora_aberturas) <= min(hora_tentativas):
        resumo["minutos_ate_1a_questao"] = _minutos(min(hora_tentativas) - min(hora_aberturas))

    dias = {h.date() for h, _ in horas}
    primeiro_dia = primeira[0].date()
    # D1: voltou no dia seguinte ao primeiro. D7: voltou em algum dia da
    # semana seguinte (do 1º ao 7º dia depois do primeiro).
    resumo["voltou_d1"] = _voltou(dias, primeiro_dia, 1, 1, hoje)
    resumo["voltou_d7"] = _voltou(dias, primeiro_dia, 1, 7, hoje)
    return resumo


def resumo_uso(pasta: Path, nomes: list[str] | None = None, hoje: date | None = None) -> list[dict]:
    """Um resumo por pessoa, quem usou por último primeiro e quem nunca
    usou nada no fim.

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
