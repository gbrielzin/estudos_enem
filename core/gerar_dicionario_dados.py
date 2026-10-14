"""gerar_dicionario_dados.py — gera o dicionário/catálogo de dados do banco
(docs/dicionario_dados.md) direto do schema real, não à mão.

A estrutura (colunas, tipos, chaves, domínios dos CHECK) sai de um banco novo
criado por db.inicializar_banco() — o mesmo caminho que a API e os testes
usam, então inclui as colunas que só existem por migração (tipo_erro,
duracao_segundos...). O texto de negócio de cada tabela/coluna fica em
DESCRICOES, aqui embaixo; test_dicionario_dados.py falha se uma coluna nova
entrar no schema sem descrição, então o catálogo não fica desatualizado em
silêncio.

Com --perfil, junta volumetria e qualidade (linhas, % de nulos, valores
distintos) lidas do enem.db local. Só números agregados — nenhum valor de
linha vai pro documento.

Uso (de dentro de core/):
    python gerar_dicionario_dados.py             # só estrutura
    python gerar_dicionario_dados.py --perfil    # estrutura + perfil do enem.db
"""
import argparse
import re
import sqlite3
import tempfile
from contextlib import closing
from datetime import date
from pathlib import Path

import db
from criar_banco_usuario import CONFIGURACOES_PESSOAIS, TABELAS_PESSOAIS

SAIDA = Path(__file__).parent.parent / "docs" / "dicionario_dados.md"

# Abaixo disso, % de nulos não diz nada (1 redação sem texto não é padrão).
MIN_LINHAS_ALERTA = 20

# Camada de cada tabela, no vocabulário de modelagem: referência (lista
# fechada), dimensão/fato (conteúdo e eventos), estado (ponteiro mutável
# derivado do fato), auditoria e configuração.
DESCRICOES: dict[str, dict[str, str]] = {
    "topicos_validos": {
        "_camada": "referência",
        "_tabela": "Taxonomia fechada de matérias aceitas. Espelha TAXONOMIA_VALIDA de db.py; existe para impedir a mesma matéria escrita de dois jeitos.",
        "grande_area": "Área do ENEM da matéria.",
        "materia": "Matéria normalizada (minúsculo, sem acento, com _).",
    },
    "questoes": {
        "_camada": "dimensão",
        "_tabela": "Uma linha por questão: real de prova ENEM ou do banco de prática. Centro do modelo.",
        "id_questao": "Chave canônica 'ano_caderno_numero' (ex.: 2024_azul_136), gerada por gerar_id_canonico().",
        "ano": "Ano da prova. 0 = sentinela de questão do banco de prática.",
        "caderno": "Cor do caderno (azul, amarelo...) ou 'banco_pratica'.",
        "numero_questao": "Número da questão no caderno.",
        "grande_area": "Área do ENEM.",
        "materia": "Matéria da taxonomia (sem FK de propósito: fora da lista grava como nao_classificado).",
        "topico": "Subtópico livre, mais fino que a matéria.",
        "enunciado_texto": "Texto do enunciado e alternativas (PDF do INEP ou API enem.dev).",
        "enunciado_imagem_path": "Caminho da figura recortada do PDF/API, quando a questão tem imagem.",
        "alternativa_correta": "Gabarito oficial.",
        "status_classificacao": "Se a matéria passou na taxonomia ou espera triagem manual.",
        "origem": "Questão real de prova ou do banco de prática.",
        "fonte": "De onde veio a questão de prática (gemini, chatgpt, autoral...). Só faz sentido com origem='banco_pratica'.",
        "tri_a": "Parâmetro TRI de discriminação (INEP, ITENS_PROVA).",
        "tri_b": "Parâmetro TRI de dificuldade (INEP). Base de nivel_tri(): fácil/médio/difícil.",
        "tri_c": "Parâmetro TRI de acerto ao acaso (INEP).",
        "habilidade": "Habilidade H1–H30 da Matriz de Referência (INEP).",
        "criado_em": "Quando a linha entrou no banco (hora local).",
    },
    "resolucoes": {
        "_camada": "dimensão",
        "_tabela": "Resoluções de uma questão (1 questão → N). Hoje guarda texto escrito à mão e as explicações de IA versionadas em explicacoes.jsonl.",
        "id_resolucao": "Chave substituta.",
        "id_questao": "Questão resolvida.",
        "tipo": "Vídeo ou texto.",
        "conteudo": "URL do vídeo ou o texto da resolução.",
        "canal": "Origem da resolução (ex.: 'explicacao_ia').",
        "criado_em": "Quando foi gravada.",
    },
    "relatos_questao": {
        "_camada": "fato",
        "_tabela": "Botão 'reportar' do app: sinal de que algo na questão pode estar errado (gabarito, enunciado cortado), para revisar em lote.",
        "id_relato": "Chave substituta.",
        "id_questao": "Questão reportada.",
        "comentario": "O que a pessoa achou de errado.",
        "resolvido": "0 = pendente, 1 = já revisado (o relato não é apagado).",
        "criado_em": "Quando foi reportado.",
    },
    "tentativas_usuario": {
        "_camada": "fato",
        "_tabela": "Log de cada resposta dada. Append-only: é o histórico de verdade; só muda por correção de gabarito ou edição explícita, sempre recalculando estado_revisao.",
        "id_tentativa": "Chave substituta.",
        "id_questao": "Questão respondida.",
        "data_tentativa": "Data/hora local da resposta (local, não UTC — ver comentário no schema).",
        "resposta_escolhida": "Letra marcada. NULL = deixou em branco (conta como erro).",
        "resultado": "Calculado contra o gabarito, nunca digitado.",
        "intervalo_dias": "Intervalo Leitner calculado nesta tentativa.",
        "streak_acertos": "Acertos seguidos até esta tentativa.",
        "proxima_revisao": "Data em que a questão volta para revisão.",
        "tipo_erro": "Por que errou: erro_de_conta, erro_de_pegadinha ou erro_de_conteudo (TIPOS_ERRO). Opcional.",
        "duracao_segundos": "Tempo gasto na questão, quando cronometrado.",
    },
    "estado_revisao": {
        "_camada": "estado",
        "_tabela": "Uma linha por questão já tentada: o ponteiro mutável 'o que revisar hoje', derivado de tentativas_usuario.",
        "id_questao": "Questão.",
        "intervalo_dias": "Intervalo Leitner atual.",
        "streak_acertos": "Acertos seguidos atuais.",
        "proxima_revisao": "Próxima data de revisão.",
        "ultima_tentativa": "Data da última resposta.",
    },
    "historico_alteracoes": {
        "_camada": "auditoria",
        "_tabela": "Trilha de auditoria: toda correção de matéria/gabarito (ou questão apagada) depois que a questão já existia.",
        "id": "Chave substituta.",
        "id_questao": "Questão alterada (sem FK: precisa sobreviver à questão apagada).",
        "campo": "Campo alterado (materia, alternativa_correta, questao_apagada).",
        "valor_antigo": "Valor antes da correção.",
        "valor_novo": "Valor depois da correção.",
        "data_alteracao": "Quando foi corrigido.",
        "tentativas_recalculadas": "Quantas tentativas tiveram o resultado recalculado por causa da correção.",
    },
    "configuracoes": {
        "_camada": "configuração",
        "_tabela": "Chave-valor de preferências da pessoa (data da prova, início do plano, motivo pessoal).",
        "chave": "Nome da configuração.",
        "valor": "Valor em texto.",
    },
    "redacoes": {
        "_camada": "fato",
        "_tabela": "Registro de redações. Guarda, não corrige: a nota vem de quem corrigiu.",
        "id": "Chave substituta.",
        "tema": "Tema da redação.",
        "data_escrita": "Dia em que foi escrita.",
        "texto": "Texto digitado, se houver.",
        "arquivo_path": "Foto/PDF da redação manuscrita, se houver.",
        "nota": "Nota de 0 a 1000. NULL = ainda não corrigida.",
        "erros_ortograficos": "Contagem de erros apontada na correção.",
        "fonte_correcao": "Quem corrigiu: a própria pessoa, externa ou oficial.",
        "observacoes": "Comentários da correção.",
        "criado_em": "Quando foi registrada.",
    },
    "nomes_tentativas": {
        "_camada": "configuração",
        "_tabela": "Rótulo opcional para uma rodada de simulado (ex.: 'fiz cansado'). Não cria a numeração, só nomeia.",
        "ano": "Ano da prova.",
        "caderno": "Caderno.",
        "grande_area": "Área.",
        "numero_tentativa": "Nº da rodada, o mesmo que resumo_por_tentativa() deriva com ROW_NUMBER.",
        "nome": "Rótulo livre.",
    },
}


def estrutura_do_schema() -> dict[str, dict]:
    """Cria um banco novo num diretório temporário e lê a estrutura dele."""
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "estrutura.db"
        with db.usar_banco(caminho):
            db.inicializar_banco()
        with closing(sqlite3.connect(caminho)) as conn:
            return _ler_estrutura(conn)


def _ler_estrutura(conn: sqlite3.Connection) -> dict[str, dict]:
    estrutura = {}
    tabelas = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
    ).fetchall()
    for nome, sql in tabelas:
        # fk[4] (coluna do pai) vem None quando o REFERENCES não nomeia coluna.
        fks = {fk[3]: f"{fk[2]}.{fk[4]}" if fk[4] else fk[2]
               for fk in conn.execute(f'PRAGMA foreign_key_list("{nome}")')}
        info = conn.execute(f'PRAGMA table_info("{nome}")').fetchall()
        n_pk = sum(1 for c in info if c[5])
        colunas = []
        for _, coluna, tipo, notnull, _default, pk in info:
            # No SQLite, PRIMARY KEY sozinha NÃO impede NULL -- só INTEGER
            # PRIMARY KEY (apelido do rowid) ou NOT NULL declarado.
            rowid = bool(pk) and n_pk == 1 and tipo.upper() == "INTEGER"
            colunas.append({
                "nome": coluna,
                "tipo": tipo,
                "obrigatoria": bool(notnull) or rowid,
                "pk": bool(pk),
                "fk": fks.get(coluna),
                "dominio": _dominio_check(sql, coluna),
            })
        estrutura[nome] = {"colunas": colunas}
    return estrutura


def _dominio_check(sql: str, coluna: str) -> list[str] | None:
    """Valores permitidos por um CHECK(coluna IN (...)) na definição da tabela,
    com NULL no fim quando o CHECK tem 'OR coluna IS NULL'. Cobre a forma que
    schema.sql usa; um CHECK escrito de outro jeito fica sem domínio."""
    col = rf'"?{re.escape(coluna)}"?'
    m = re.search(rf"CHECK\s*\(\s*{col}\s+IN\s*\(([^)]*)\)(\s*OR\s+{col}\s+IS\s+NULL)?", sql, re.I)
    if not m:
        return None
    valores = re.findall(r"'((?:[^']|'')*)'", m.group(1))
    return valores + (["NULL"] if m.group(2) else [])


def perfil_do_banco(caminho: Path, estrutura: dict) -> dict[str, dict]:
    """Linhas por tabela e, por coluna, nulos, % de nulos e nº de valores
    distintos. Tabela/coluna que ainda não existe no banco lido (banco não
    migrado) fica de fora do perfil em vez de quebrar."""
    perfil = {}
    with closing(sqlite3.connect(caminho)) as conn:
        existentes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for tabela, info in estrutura.items():
            if tabela not in existentes:
                continue
            no_banco = {r[1] for r in conn.execute(f'PRAGMA table_info("{tabela}")')}
            linhas = conn.execute(f'SELECT COUNT(*) FROM "{tabela}"').fetchone()[0]
            colunas = {}
            for col in info["colunas"]:
                if col["nome"] not in no_banco:
                    continue
                nulos, distintos = conn.execute(
                    f'SELECT SUM("{col["nome"]}" IS NULL), COUNT(DISTINCT "{col["nome"]}") FROM "{tabela}"'
                ).fetchone()
                nulos = nulos or 0
                pct = 100 * nulos / linhas if linhas else None
                colunas[col["nome"]] = {"nulos": nulos, "pct_nulos": pct, "distintos": distintos}
            perfil[tabela] = {"linhas": linhas, "colunas": colunas}
    return perfil


def alertas_de_qualidade(perfil: dict) -> list[str]:
    """Colunas vazias ou quase vazias em tabelas com volume suficiente."""
    alertas = []
    for tabela, p in perfil.items():
        if p["linhas"] < MIN_LINHAS_ALERTA:
            continue
        for coluna, c in p["colunas"].items():
            pct = c["pct_nulos"]
            if pct == 100:
                alertas.append(f"`{tabela}.{coluna}` está 100% nula em {_milhar(p['linhas'])} linhas: campo existe, mas ninguém preenche.")
            elif pct >= 50:
                alertas.append(f"`{tabela}.{coluna}` tem {pct:.0f}% de nulos.")
    return alertas


def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _classificacao(tabela: str) -> str:
    if tabela in TABELAS_PESSOAIS:
        return "pessoal"
    if tabela == "configuracoes":
        return f"misto ({', '.join(CONFIGURACOES_PESSOAIS)} são pessoais)"
    return "compartilhado"


def _cel(texto) -> str:
    """Texto seguro dentro de uma célula de tabela Markdown."""
    return str(texto).replace("|", "\\|").replace("\n", " ")


def _mermaid(estrutura: dict) -> str:
    linhas = ["```mermaid", "erDiagram"]
    for tabela, info in estrutura.items():
        for col in info["colunas"]:
            if col["fk"]:
                pai = col["fk"].split(".")[0]
                linhas.append(f'    {pai} ||--o{{ {tabela} : "{col["nome"]}"')
    linhas.append("```")
    return "\n".join(linhas)


def gerar_markdown(estrutura: dict, perfil: dict | None = None) -> str:
    out = [
        "# Dicionário de dados — ENEM GI",
        "",
        "> Gerado por `core/gerar_dicionario_dados.py` a partir do schema real. Não edite à mão:",
        "> mude `DESCRICOES` no script e rode de novo. O teste `test_dicionario_dados.py` quebra",
        "> se uma coluna nova entrar no banco sem descrição.",
        "",
        f"Atualizado em {date.today():%d/%m/%Y}." + (" Perfil lido do `enem.db` local." if perfil else ""),
        "",
        "**Classificação:** *pessoal* = dado de uso de uma pessoa, apagado ao criar o banco de um",
        "usuário novo (`criar_banco_usuario.py`); *compartilhado* = conteúdo igual para todos.",
        "",
        "## Visão geral",
        "",
        "| Tabela | Camada | Classificação | Colunas | " + ("Linhas | " if perfil else "") + "Para que serve |",
        "|---|---|---|---|" + ("---|" if perfil else "") + "---|",
    ]
    for tabela, info in estrutura.items():
        d = DESCRICOES.get(tabela, {})
        classe = _classificacao(tabela)
        linhas = f" {_milhar(perfil[tabela]['linhas'])} |" if perfil and tabela in perfil else (" — |" if perfil else "")
        out.append(f"| `{tabela}` | {d.get('_camada', '—')} | {classe} | {len(info['colunas'])} |{linhas} {_cel(d.get('_tabela', ''))} |")

    out += ["", "## Relacionamentos", "", _mermaid(estrutura), ""]

    if perfil:
        alertas = alertas_de_qualidade(perfil)
        out += ["## Alertas de qualidade", "",
                f"Colunas com 50% ou mais de nulos, em tabelas com {MIN_LINHAS_ALERTA}+ linhas. Nem todo nulo é",
                "defeito (ex.: `topico` é opcional de propósito); o alerta é o que vale investigar.", ""]
        out += [f"- {a}" for a in alertas] or ["- Nenhuma coluna com 50% ou mais de nulos."]
        out.append("")

    out += ["## Tabelas", ""]
    for tabela, info in estrutura.items():
        d = DESCRICOES.get(tabela, {})
        out += [f"### `{tabela}`", "", d.get("_tabela", ""), ""]
        cab = "| Coluna | Tipo | Obrigatória | Chave | Valores permitidos | Descrição |"
        sep = "|---|---|---|---|---|---|"
        if perfil and tabela in perfil:
            cab += " % nulos | Distintos |"
            sep += "---|---|"
        out += [cab, sep]
        for col in info["colunas"]:
            chave = "PK" if col["pk"] else (f"FK → `{col['fk']}`" if col["fk"] else "")
            dominio = ", ".join(f"`{_cel(v)}`" for v in col["dominio"]) if col["dominio"] else ""
            linha = (f"| `{col['nome']}` | {col['tipo']} | {'sim' if col['obrigatoria'] else 'não'} | {chave} "
                     f"| {dominio} | {_cel(d.get(col['nome'], ''))} |")
            if perfil and tabela in perfil:
                c = perfil[tabela]["colunas"].get(col["nome"])
                if c is None:
                    linha += " — | — |"
                else:
                    pct = f"{c['pct_nulos']:.0f}%" if c["pct_nulos"] is not None else "—"
                    linha += f" {pct} | {c['distintos']} |"
            out.append(linha)
        out.append("")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--perfil", action="store_true", help="junta volumetria e %% de nulos do enem.db local")
    parser.add_argument("--saida", type=Path, default=SAIDA)
    args = parser.parse_args()

    estrutura = estrutura_do_schema()
    perfil = None
    if args.perfil:
        if not db.DB_PATH.exists():
            raise SystemExit(f"{db.DB_PATH} não existe -- rode sem --perfil.")
        perfil = perfil_do_banco(db.DB_PATH, estrutura)
    args.saida.write_text(gerar_markdown(estrutura, perfil), encoding="utf-8")
    print(f"Escrito {args.saida}")


if __name__ == "__main__":
    main()
