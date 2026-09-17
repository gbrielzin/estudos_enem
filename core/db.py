"""
db.py — camada de core do sistema de estudo ENEM.

Responsabilidade única: schema, inserção de dados canônicos, registro
de tentativas e cálculo de revisão espaçada (Leitner simplificado).

Não importa nada de main.py ou app.py — é uma folha na árvore de
dependências. main.py/app.py (interface/coleta) e o futuro módulo de
quiz importam DESTE módulo, nunca o contrário. Isso é o que evita
import circular: se algum dia este arquivo precisar de algo que hoje
mora em main.py (ex: extrair_numero_questao), essa função deve ser
promovida pra cá ou pra um terceiro módulo de utilitários — nunca
importada de volta de main.py.

Não usa nenhuma dependência fora da standard library.
"""

from __future__ import annotations

import csv
import io
import re
import sqlite3
import unicodedata
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "enem.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# ============================================================
# TAXONOMIA FECHADA
# ============================================================
# Formato: (grande_area, materia). "materia" já normalizada (ver
# normalizar_texto): minúsculo, sem acento, sem espaço.
#
# Ciências da Natureza atualizada em 2026-08 pra granularidade fina
# (mesmo nível de Matemática) -- a versão anterior só tinha
# biologia/quimica/fisica como um todo, o que jogava praticamente
# 100% do gabarito real de Ciências em triagem, porque nenhum CSV usa
# rótulo tão genérico. Lista construída a partir dos tópicos que mais
# aparecem no ENEM historicamente; espera-se editar conforme os
# cadernos reais forem classificados e novos rótulos aparecerem.
TAXONOMIA_VALIDA: set[tuple[str, str]] = {
    ("matematica", "estatistica"),
    ("matematica", "geometria_plana"),
    ("matematica", "geometria_analitica"),
    ("matematica", "geometria_espacial"),
    ("matematica", "razao_e_proporcao"),
    ("matematica", "porcentagem"),
    ("matematica", "probabilidade"),
    ("matematica", "analise_combinatoria"),
    ("matematica", "funcao_1_grau"),
    ("matematica", "funcao_2_grau"),
    ("matematica", "funcao_exponencial"),
    ("matematica", "logaritmo"),
    ("matematica", "trigonometria"),
    ("matematica", "progressao_aritmetica"),
    ("matematica", "progressao_geometrica"),
    ("matematica", "sistema_de_equacoes"),
    ("matematica", "matematica_financeira"),
    ("matematica", "raciocinio_logico"),
    ("matematica", "interpretacao_de_grafico"),
    ("matematica", "escala"),
    ("matematica", "unidade_de_medida"),
    ("matematica", "regra_de_tres"),
    ("matematica", "aritmetica"),
    ("matematica", "matematica_basica"),
    ("matematica", "geometria"),
    ("matematica", "inequacao_e_modulo"),
    ("matematica", "conjuntos"),
    ("matematica", "funcoes"),
    ("matematica", "projecao_ortogonal"),

    # --- Biologia ---
    ("ciencias_natureza", "ecologia"),
    ("ciencias_natureza", "genetica"),
    ("ciencias_natureza", "evolucao"),
    ("ciencias_natureza", "citologia"),
    ("ciencias_natureza", "fisiologia_humana"),
    ("ciencias_natureza", "sistema_nervoso"),
    ("ciencias_natureza", "sistema_imunologico"),
    ("ciencias_natureza", "sistema_circulatorio"),
    ("ciencias_natureza", "sistema_respiratorio"),
    ("ciencias_natureza", "sistema_digestorio"),
    ("ciencias_natureza", "sistema_endocrino"),
    ("ciencias_natureza", "reproducao_humana"),
    ("ciencias_natureza", "embriologia"),
    ("ciencias_natureza", "botanica"),
    ("ciencias_natureza", "zoologia"),
    ("ciencias_natureza", "microbiologia"),
    ("ciencias_natureza", "virus_e_bacterias"),
    ("ciencias_natureza", "fungos"),
    ("ciencias_natureza", "biotecnologia"),
    ("ciencias_natureza", "meio_ambiente"),
    ("ciencias_natureza", "saude_publica"),
    ("ciencias_natureza", "biologia"),  # fallback genérico, só se não der pra afinar

    # --- Química ---
    ("ciencias_natureza", "quimica_organica"),
    ("ciencias_natureza", "quimica_inorganica"),
    ("ciencias_natureza", "funcoes_organicas"),
    ("ciencias_natureza", "estequiometria"),
    ("ciencias_natureza", "termoquimica"),
    ("ciencias_natureza", "eletroquimica"),
    ("ciencias_natureza", "cinetica_quimica"),
    ("ciencias_natureza", "equilibrio_quimico"),
    ("ciencias_natureza", "solucoes"),
    ("ciencias_natureza", "ligacoes_quimicas"),
    ("ciencias_natureza", "tabela_periodica"),
    ("ciencias_natureza", "radioatividade"),
    ("ciencias_natureza", "polimeros"),
    ("ciencias_natureza", "ph_e_poh"),
    ("ciencias_natureza", "gases"),
    ("ciencias_natureza", "reacoes_quimicas"),
    ("ciencias_natureza", "densidade"),
    ("ciencias_natureza", "quimica"), 
    ("ciencias_natureza", "eletrostatica"),
    ("ciencias_natureza", "ciclos_biogeoquimicos"),
    ("ciencias_natureza", "separacao_de_misturas"),
    ("ciencias_natureza", "quimica_verde"), # fallback genérico, só se não der pra afinar

    # --- Física ---
    ("ciencias_natureza", "cinematica"),
    ("ciencias_natureza", "dinamica"),
    ("ciencias_natureza", "estatica"),
    ("ciencias_natureza", "termologia"),
    ("ciencias_natureza", "calorimetria"),
    ("ciencias_natureza", "ondas"),
    ("ciencias_natureza", "acustica"),
    ("ciencias_natureza", "optica"),
    ("ciencias_natureza", "eletricidade"),
    ("ciencias_natureza", "eletrodinamica"),
    ("ciencias_natureza", "eletromagnetismo"),
    ("ciencias_natureza", "energia_e_trabalho"),
    ("ciencias_natureza", "hidrostatica"),
    ("ciencias_natureza", "gravitacao"),
    ("ciencias_natureza", "fisica_moderna"),
    ("ciencias_natureza", "fisica"),  # fallback genérico, só se não der pra afinar
}

NIVEL_VALIDO = {"facil", "medio", "dificil"}
MIN_AMOSTRA_CONFIAVEL = 3  # abaixo disso, taxa de acerto entra como pista, não veredito

# Sinônimos: nomes diferentes pro mesmo conteúdo, ou variações de
# singular/plural/parêntese que a normalização de texto sozinha não
# resolve (normalizar_texto tira acento e caixa, não decide que
# "Função Afim" e "Função de 1º Grau" são a mesma coisa).
# Descoberto rodando o gabarito real 2019-2025: 11 de 38 questões
# caíram em 'nao_classificado' na primeira tentativa, e quase todas
# eram sinônimo, não lixo de verdade (tipo 'Marketing digital').
# Mapeia pro nome canônico ANTES de checar contra TAXONOMIA_VALIDA.
SINONIMOS_MATERIA: dict[str, str] = {
    "funcao_afim": "funcao_1_grau",
    "funcao_quadratica": "funcao_2_grau",
    "estatistica_media": "estatistica",
    "estatistica_mediana": "estatistica",
    "unidades_de_medida": "unidade_de_medida",
    "escala_numerica": "escala",
    "logaritmos": "logaritmo",
    "logica": "raciocinio_logico",
    "media_ponderada": "estatistica",
    "interpretacao_de_graficos": "interpretacao_de_grafico",
    "mediana": "estatistica",
    "media": "estatistica",
    "proporcao": "razao_e_proporcao",
    "projecao": "projecao_ortogonal",
    "fator_de_reducao": "escala",
    "grafico": "interpretacao_de_grafico",
    "graficos": "interpretacao_de_grafico",
    "volume_da_esfera_e_do_cilindro": "geometria_espacial",

    # --- Biologia ---
    "genetica_mendeliana": "genetica",
    "leis_de_mendel": "genetica",
    "hereditariedade": "genetica",
    "dna_e_rna": "genetica",
    "ecologia_ambiental": "ecologia",
    "ecologia_populacional": "ecologia",
    "cadeia_alimentar": "ecologia",
    "teia_alimentar": "ecologia",
    "meio_ambiente_e_ecologia": "meio_ambiente",
    "sustentabilidade": "meio_ambiente",
    "sistema_nervoso_central": "sistema_nervoso",
    "sistema_imune": "sistema_imunologico",
    "imunologia": "sistema_imunologico",
    "vacinas": "sistema_imunologico",
    "aparelho_circulatorio": "sistema_circulatorio",
    "aparelho_respiratorio": "sistema_respiratorio",
    "aparelho_digestorio": "sistema_digestorio",
    "aparelho_digestivo": "sistema_digestorio",
    "sistema_digestivo": "sistema_digestorio",
    "hormonios": "sistema_endocrino",
    "reproducao": "reproducao_humana",
    "celula": "citologia",
    "biologia_celular": "citologia",
    "evolucao_das_especies": "evolucao",
    "selecao_natural": "evolucao",
    "darwinismo": "evolucao",
    "plantas": "botanica",
    "animais": "zoologia",
    "bacterias": "virus_e_bacterias",
    "virus": "virus_e_bacterias",
    "epidemiologia": "saude_publica",
    "doencas": "saude_publica",

    # --- Química ---
    "organica": "quimica_organica",
    "inorganica": "quimica_inorganica",
    "funcao_organica": "funcoes_organicas",
    "hidrocarbonetos": "funcoes_organicas",
    "calculo_estequiometrico": "estequiometria",
    "estequiometria_e_calculos": "estequiometria",
    "termoquimica_entalpia": "termoquimica",
    "entalpia": "termoquimica",
    "pilhas_e_baterias": "eletroquimica",
    "pilhas": "eletroquimica",
    "eletrolise": "eletroquimica",
    "velocidade_das_reacoes": "cinetica_quimica",
    "ph": "ph_e_poh",
    "poh": "ph_e_poh",
    "acidos_e_bases": "ph_e_poh",
    "ligacao_ionica": "ligacoes_quimicas",
    "ligacao_covalente": "ligacoes_quimicas",
    "tabela_periodica_propriedades": "tabela_periodica",
    "radioatividade_nuclear": "radioatividade",
    "quimica_nuclear": "radioatividade",
    "plasticos": "polimeros",
    "solucoes_quimicas": "solucoes",
    "concentracao": "solucoes",
    "eletrizacao": "eletrostatica",
    "carga_eletrica": "eletrostatica",
    "ciclo_do_carbono": "ciclos_biogeoquimicos",
    "ciclo_do_nitrogenio": "ciclos_biogeoquimicos",
    "ciclo_da_agua": "ciclos_biogeoquimicos",
    "destilacao": "separacao_de_misturas",
    "extracao": "separacao_de_misturas",
    "polaridade": "separacao_de_misturas",
    
    # --- Física ---
    "movimento_uniforme": "cinematica",
    "movimento_uniformemente_variado": "cinematica",
    "mu": "cinematica",
    "muv": "cinematica",
    "leis_de_newton": "dinamica",
    "forcas": "dinamica",
    "trabalho_e_energia": "energia_e_trabalho",
    "energia_mecanica": "energia_e_trabalho",
    "conservacao_de_energia": "energia_e_trabalho",
    "calor_e_temperatura": "termologia",
    "temperatura": "termologia",
    "dilatacao_termica": "termologia",
    "ondas_sonoras": "acustica",
    "som": "acustica",
    "ondas_eletromagneticas": "ondas",
    "optica_geometrica": "optica",
    "lentes_e_espelhos": "optica",
    "eletricidade_basica": "eletricidade",
    "circuitos_eletricos": "eletrodinamica",
    "corrente_eletrica": "eletrodinamica",
    "campo_magnetico": "eletromagnetismo",
    "empuxo": "hidrostatica",
    "pressao": "hidrostatica",
    "gravitacao_universal": "gravitacao",
    "leis_de_kepler": "gravitacao",
}

_SOLIDO = r"(esfera|cilindro|cone|cubo|piramide|prisma)"

# Padrões que cobrem famílias inteiras de variação (preposição "de"/"do",
# número por extenso/numeral/ordinal, singular/plural) em vez de listar
# cada combinação à mão -- descoberto que ficar adicionando variante por
# variante não escala (função de/do 1º/1/primeiro grau já tinha 6+
# combinações reais nos dados do usuário).
_PADROES_MATERIA: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^funcao_d[eo]_(1|1o|primeiro)_grau$"), "funcao_1_grau"),
    (re.compile(r"^funcao_d[eo]_(2|2o|segundo)_grau$"), "funcao_2_grau"),
    (re.compile(r"^sistemas?_de_(equacao|equacoes)$"), "sistema_de_equacoes"),
    (re.compile(r"^progressao_aritmetica(_pa)?$"), "progressao_aritmetica"),
    (re.compile(r"^progressao_geometrica(_pg)?$"), "progressao_geometrica"),
    (re.compile(rf"^volume_d(?:e|o|a)s?_{_SOLIDO}(_e_d(?:e|o|a)s?_{_SOLIDO})*$"), "geometria_espacial"),
    (re.compile(rf"^geometria_espacial(_{_SOLIDO})+$"), "geometria_espacial"),
]


def canonicalizar_materia(materia_norm: str) -> str:
    """Aplica primeiro o dicionário de sinônimos exatos, depois os
    padrões de família (função de grau, sistema de equações etc).
    Retorna o texto original se nada bater -- não força match."""
    if materia_norm in SINONIMOS_MATERIA:
        return SINONIMOS_MATERIA[materia_norm]
    for padrao, canonico in _PADROES_MATERIA:
        if padrao.match(materia_norm):
            return canonico
    return materia_norm


# ============================================================
# NORMALIZAÇÃO DE TEXTO
# ============================================================

def normalizar_texto(bruto: str) -> str:
    """Minúsculo, sem acento, espaço vira underscore.

    Resolve o caso 'Matemática Básica' vs 'matemática básica' vs
    'Matematica Basica'. NÃO resolve por si só o caso 'º' (U+00BA)
    vs '°' (U+00B0) que achamos em 'Função de 1º/1° Grau' — os dois
    símbolos não são unicode-equivalentes, então sobrevivem à
    normalização NFKD. Por isso a validação abaixo compara contra
    TAXONOMIA_VALIDA em vez de confiar em normalização sozinha: texto
    fora da lista fechada vira 'nao_classificado', não uma chave nova.
    """
    texto = unicodedata.normalize("NFKD", bruto.strip().lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", "_", texto.strip())
    return texto


MAPA_NIVEL = {
    "facil": "facil",
    "media": "medio",
    "medio": "medio",
    "dificil": "dificil",
}


def normalizar_nivel(bruto: str) -> str | None:
    """Mapeia qualquer variação textual pro enum fechado
    {'facil', 'medio', 'dificil'}. Retorna None se não reconhecer —
    o chamador decide se rejeita ou marca para triagem.

    Nota: no desenho atual, dificuldade não é mais um atributo salvo
    da questão — ela é derivada do desempenho do usuário (ver
    taxa_acerto() mais abaixo). Esta função existe pra migração de
    dado antigo e pra qualquer conteúdo externo que ainda venha
    rotulado (ex: um vídeo de resolução que cita nível na descrição).
    """
    return MAPA_NIVEL.get(normalizar_texto(bruto))


# ============================================================
# CONEXÃO
# ============================================================

@contextmanager
def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_banco() -> None:
    """Cria as tabelas (idempotente — CREATE TABLE IF NOT EXISTS) e
    popula topicos_validos a partir de TAXONOMIA_VALIDA. Também aplica
    migrações leves em bancos já existentes (coluna nova em tabela
    antiga), sem apagar nenhum dado."""
    with _conectar() as conn:
        # Migra coluna nova em `questoes` ANTES de rodar schema.sql:
        # schema.sql cria índice sobre `origem` (idx_questoes_origem),
        # e CREATE INDEX falha se a coluna ainda não existe numa
        # tabela já antiga que o CREATE TABLE IF NOT EXISTS do script
        # não vai alterar -- então a migração de coluna precisa
        # acontecer antes do script rodar, não depois.
        tabelas = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "questoes" in tabelas:
            colunas_questoes = {r[1] for r in conn.execute("PRAGMA table_info(questoes)").fetchall()}
            if "origem" not in colunas_questoes:
                conn.execute(
                    "ALTER TABLE questoes ADD COLUMN origem TEXT NOT NULL DEFAULT 'enem_oficial' "
                    "CHECK(origem IN ('enem_oficial','banco_pratica'))"
                )
            if "fonte" not in colunas_questoes:
                conn.execute("ALTER TABLE questoes ADD COLUMN fonte TEXT")

        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany(
            "INSERT OR IGNORE INTO topicos_validos (grande_area, materia) VALUES (?, ?)",
            list(TAXONOMIA_VALIDA),
        )
        colunas = {r[1] for r in conn.execute("PRAGMA table_info(tentativas_usuario)").fetchall()}
        if "tipo_erro" not in colunas:
            conn.execute("ALTER TABLE tentativas_usuario ADD COLUMN tipo_erro TEXT")

        # SQLite não tem ALTER TABLE pra mudar CHECK constraint -- só dá
        # pra recriar a tabela. Só roda se a tabela já existir com a
        # constraint ANTIGA (resposta_escolhida NOT NULL, sem a opção
        # IS NULL); depois de rodar uma vez, o texto novo não bate mais
        # com essa checagem e vira no-op pra sempre. Preserva todo dado
        # -- é um INSERT INTO ... SELECT * da tabela antiga pra nova,
        # nunca um DELETE.
        sql_tabela_atual = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='tentativas_usuario'"
        ).fetchone()[0]
        if "resposta_escolhida IN ('A','B','C','D','E'))" in sql_tabela_atual:
            conn.executescript(
                """
                ALTER TABLE tentativas_usuario RENAME TO tentativas_usuario_migracao_old;
                CREATE TABLE tentativas_usuario (
                    id_tentativa        INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_questao          TEXT NOT NULL REFERENCES questoes(id_questao) ON DELETE CASCADE,
                    data_tentativa       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                    resposta_escolhida  TEXT CHECK(resposta_escolhida IN ('A','B','C','D','E') OR resposta_escolhida IS NULL),
                    resultado           TEXT NOT NULL CHECK(resultado IN ('acertou','errou')),
                    intervalo_dias      INTEGER NOT NULL,
                    streak_acertos      INTEGER NOT NULL,
                    proxima_revisao     TEXT NOT NULL,
                    tipo_erro           TEXT
                );
                INSERT INTO tentativas_usuario
                    (id_tentativa, id_questao, data_tentativa, resposta_escolhida, resultado,
                     intervalo_dias, streak_acertos, proxima_revisao, tipo_erro)
                SELECT id_tentativa, id_questao, data_tentativa, resposta_escolhida, resultado,
                       intervalo_dias, streak_acertos, proxima_revisao, tipo_erro
                FROM tentativas_usuario_migracao_old;
                DROP TABLE tentativas_usuario_migracao_old;
                CREATE INDEX IF NOT EXISTS idx_tentativas_questao ON tentativas_usuario(id_questao);
                CREATE INDEX IF NOT EXISTS idx_tentativas_data ON tentativas_usuario(data_tentativa);
                """
            )

        # Migração separada: DEFAULT de data_tentativa mudou de UTC
        # (datetime('now')) pra hora LOCAL (datetime('now','localtime')).
        # Bug real, não cosmético -- achado rodando os testes à noite:
        # SQLite datetime('now') é sempre UTC, mas todo o Python do
        # projeto usa date.today()/datetime.now() (hora local). Num
        # usuário em UTC-3, das ~21h às 23h59 locais o UTC já é o dia
        # seguinte -- uma tentativa registrada nesse intervalo gravava
        # com data_tentativa de AMANHÃ, fazendo "hoje" (meta diária,
        # missão do dia, streak) nunca bater com o que acabou de ser
        # respondido. SQLite não tem ALTER TABLE pra mudar um DEFAULT --
        # mesmo padrão de rebuild da migração acima, só que trocando o
        # DEFAULT, não o CHECK. Dado já gravado (datas antigas em UTC)
        # não é reescrito -- só INSERTs novos, a partir de agora, usam a
        # hora certa; script bem antigo com poucas tentativas do fim do
        # dia UTC-3 pode ter uma data ligeiramente adiantada no passado,
        # não vale a pena tentar adivinhar/corrigir retroativamente.
        sql_tabela_atual = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='tentativas_usuario'"
        ).fetchone()[0]
        if "datetime('now'))" in sql_tabela_atual:
            conn.executescript(
                """
                ALTER TABLE tentativas_usuario RENAME TO tentativas_usuario_migracao_old;
                CREATE TABLE tentativas_usuario (
                    id_tentativa        INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_questao          TEXT NOT NULL REFERENCES questoes(id_questao) ON DELETE CASCADE,
                    data_tentativa       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                    resposta_escolhida  TEXT CHECK(resposta_escolhida IN ('A','B','C','D','E') OR resposta_escolhida IS NULL),
                    resultado           TEXT NOT NULL CHECK(resultado IN ('acertou','errou')),
                    intervalo_dias      INTEGER NOT NULL,
                    streak_acertos      INTEGER NOT NULL,
                    proxima_revisao     TEXT NOT NULL,
                    tipo_erro           TEXT
                );
                INSERT INTO tentativas_usuario
                    (id_tentativa, id_questao, data_tentativa, resposta_escolhida, resultado,
                     intervalo_dias, streak_acertos, proxima_revisao, tipo_erro)
                SELECT id_tentativa, id_questao, data_tentativa, resposta_escolhida, resultado,
                       intervalo_dias, streak_acertos, proxima_revisao, tipo_erro
                FROM tentativas_usuario_migracao_old;
                DROP TABLE tentativas_usuario_migracao_old;
                CREATE INDEX IF NOT EXISTS idx_tentativas_questao ON tentativas_usuario(id_questao);
                CREATE INDEX IF NOT EXISTS idx_tentativas_data ON tentativas_usuario(data_tentativa);
                """
            )

        # Migração de duracao_segundos: checada de novo aqui (não junto
        # com tipo_erro acima) DE PROPÓSITO -- os dois rebuilds de
        # tentativas_usuario acima (CHECK antigo / DEFAULT antigo) têm
        # CREATE TABLE com lista de coluna hardcoded que não inclui
        # duracao_segundos; se essa migração rodasse ANTES deles, a
        # coluna seria adicionada e depois APAGADA pelo rebuild (o
        # INSERT INTO...SELECT do rebuild só copia as colunas que ele
        # lista). Rodando por último, com PRAGMA table_info() lido de
        # novo (não reaproveitando `colunas` de cima, que pode estar
        # desatualizado se um rebuild rodou), fica correto nos dois
        # casos: banco que nunca teve rebuild, e banco que acabou de
        # passar por um agora mesmo.
        colunas_tentativas_final = {r[1] for r in conn.execute("PRAGMA table_info(tentativas_usuario)").fetchall()}
        if "duracao_segundos" not in colunas_tentativas_final:
            conn.execute("ALTER TABLE tentativas_usuario ADD COLUMN duracao_segundos INTEGER")


# ============================================================
# ID CANÔNICO
# ============================================================

def gerar_id_canonico(ano: int, caderno: str, numero: int) -> str:
    """Gera 'ano_caderno_numero', ex: '2024_azul_136'.

    Normaliza o caderno pra não criar '2024_azul_136' e
    '2024_Azul_136' como IDs diferentes — o mesmo tipo de bug de
    string que fragmentou a tabela de probabilidade antiga."""
    caderno_norm = normalizar_texto(caderno)
    return f"{ano}_{caderno_norm}_{numero}"


# ============================================================
# INSERÇÃO DE QUESTÕES E RESOLUÇÕES
# ============================================================

def inserir_questao(
    ano: int,
    caderno: str,
    numero: int,
    grande_area: str,
    materia: str,
    alternativa_correta: str,
    topico: str | None = None,
    enunciado_texto: str | None = None,
    enunciado_imagem_path: str | None = None,
    sobrescrever: bool = False,
) -> tuple[str, str]:
    """Insere uma questão pelo ID canônico. Se já existir e
    sobrescrever=False (padrão), não altera nada — idempotente.

    Se sobrescrever=True, faz UPDATE nos campos de conteúdo (matéria,
    gabarito, etc) mantendo o MESMO id_questao — usar quando uma fonte
    mais confiável (ex: gabarito oficial em PDF) precisa corrigir um
    dado de origem duvidosa que já estava na base. Como o id_questao
    não muda, resolucoes e tentativas_usuario já ligadas a essa
    questão continuam intactas (FOREIGN KEY não quebra).

    Valida (grande_area, materia) contra TAXONOMIA_VALIDA. Se não
    bater, a questão AINDA é gravada — mas com
    status_classificacao='nao_classificado', para triagem humana
    depois, em vez de perder o registro ou inventar uma categoria
    nova.

    Retorna (id_questao, status_classificacao).
    """
    if alternativa_correta.strip().upper() not in {"A", "B", "C", "D", "E"}:
        raise ValueError(f"alternativa_correta inválida: '{alternativa_correta}'")

    id_questao = gerar_id_canonico(ano, caderno, numero)
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    materia_norm = normalizar_texto(materia)
    materia_norm = canonicalizar_materia(materia_norm)

    status = (
        "classificado"
        if (grande_area_norm, materia_norm) in TAXONOMIA_VALIDA
        else "nao_classificado"
    )

    clausula_conflito = (
        """
        ON CONFLICT(id_questao) DO UPDATE SET
            grande_area = excluded.grande_area,
            materia = excluded.materia,
            topico = excluded.topico,
            enunciado_texto = COALESCE(excluded.enunciado_texto, questoes.enunciado_texto),
            enunciado_imagem_path = COALESCE(excluded.enunciado_imagem_path, questoes.enunciado_imagem_path),
            alternativa_correta = excluded.alternativa_correta,
            status_classificacao = excluded.status_classificacao
        """
        if sobrescrever
        else "ON CONFLICT(id_questao) DO NOTHING"
    )

    with _conectar() as conn:
        antes = conn.execute(
            "SELECT materia, alternativa_correta FROM questoes WHERE id_questao = ?", (id_questao,)
        ).fetchone() if sobrescrever else None

        conn.execute(
            f"""
            INSERT INTO questoes (
                id_questao, ano, caderno, numero_questao, grande_area, materia,
                topico, enunciado_texto, enunciado_imagem_path,
                alternativa_correta, status_classificacao
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            {clausula_conflito}
            """,
            (
                id_questao, ano, caderno_norm, numero,
                grande_area_norm,
                materia_norm,
                topico, enunciado_texto, enunciado_imagem_path,
                alternativa_correta.strip().upper(), status,
            ),
        )

        if antes is not None:
            materia_antiga, gabarito_antigo = antes
            gabarito_novo = alternativa_correta.strip().upper()

            if gabarito_antigo != gabarito_novo:
                # O gabarito mudou de verdade -- toda tentativa já registrada
                # pra essa questão foi avaliada contra o gabarito ERRADO.
                # Recalcula o resultado de cada uma contra o gabarito novo,
                # em vez de deixar acerto/erro desatualizado escondido.
                afetadas = conn.execute(
                    "SELECT id_tentativa, resposta_escolhida, resultado FROM tentativas_usuario WHERE id_questao = ?",
                    (id_questao,),
                ).fetchall()
                corrigidas = 0
                for id_tentativa, resposta, resultado_antigo in afetadas:
                    resultado_novo = "acertou" if resposta == gabarito_novo else "errou"
                    if resultado_novo != resultado_antigo:
                        conn.execute(
                            "UPDATE tentativas_usuario SET resultado = ? WHERE id_tentativa = ?",
                            (resultado_novo, id_tentativa),
                        )
                        corrigidas += 1
                conn.execute(
                    "INSERT INTO historico_alteracoes (id_questao, campo, valor_antigo, valor_novo, tentativas_recalculadas) "
                    "VALUES (?,?,?,?,?)",
                    (id_questao, "alternativa_correta", gabarito_antigo, gabarito_novo, corrigidas),
                )

            if materia_antiga != materia_norm:
                conn.execute(
                    "INSERT INTO historico_alteracoes (id_questao, campo, valor_antigo, valor_novo) VALUES (?,?,?,?)",
                    (id_questao, "materia", materia_antiga, materia_norm),
                )

    return id_questao, status


# ============================================================
# BANCO DE PRÁTICA (questões fora do ENEM oficial -- ex: trazidas de
# uma sessão de estudo com IA sobre um assunto específico)
# ============================================================

ANO_BANCO_PRATICA = 0
CADERNO_BANCO_PRATICA = "banco_pratica"

# Mapeamento topico -> fase, só pra ecologia por enquanto. Conteúdo
# AUTORAL (mesma categoria de RESUMOS_TRILHA em
# mobile/src/constants/resumos-trilha.ts e de manual_prioridade_de_estudo.md):
# espelha as 6 fases e pesos de incidência definidos em
# docs/filosofia.md, não é taxonomia derivada do TAXONOMIA_VALIDA
# acima (que só sabe "materia", nunca "fase dentro da materia"). Uma
# matéria sem entrada aqui (ex: 'optica', que ainda é uma trilha única
# sem fase) simplesmente não tem fase -- fase_de_topico() devolve None
# e trilha_banco_pratica(fase=...) não filtra nada pra ela.
FASES_ECOLOGIA: dict[int, set[str]] = {
    1: {"magnificacao_trofica", "dissipacao_termica", "fragmentacao_de_habitat", "eutrofizacao"},
    # A antiga fase 2 ("Relações Ecológicas", 14 padrões diferentes numa
    # tela só) foi dividida em 3 em 2026-09-17 -- achado ao vivo do
    # usuário validando a trilha: resumo "muito coisa" numa tela só, e
    # um padrão de população (capacidade_de_suporte) aparecendo "do
    # nada" no meio de padrões de relação ENTRE espécies diferentes
    # (são coisas conceitualmente distintas, mereciam fases separadas).
    # Números 7/8 usados pras duas fases novas (em vez de renumerar
    # 3-6 que já existiam) -- ver NOMES_FASES_ECOLOGIA abaixo.
    2: {"mutualismo", "protocooperacao", "comensalismo", "inquilinismo", "epifitismo"},  # Harmônicas
    3: {
        "fixacao_biologica", "nitrificacao", "desnitrificacao",
        "piramide_numeros_invertida", "piramide_energia_direta",
        "respiracao_celular", "fotossintese",
    },
    4: {"chuva_acida", "destruicao_camada_ozonio", "inversao_termica", "aquecimento_global"},
    5: {"filtracao_e_cloracao", "coagulacao_decantacao", "decomposicao_aerobica", "chorume", "gas_metano"},
    6: {"ilha_de_calor", "chuva_de_conveccao", "evapotranspiracao", "albedo", "pegada_de_carbono"},
    7: {"competicao_interespecifica", "predacao", "parasitismo", "amensalismo"},  # Desarmônicas
    8: {"sucessao_primaria", "sucessao_secundaria", "capacidade_de_suporte", "potencial_biotico", "canibalismo"},  # População/Sucessão
}

NOMES_FASES_ECOLOGIA: dict[int, str] = {
    1: "Cadeias Alimentares e Fluxo de Energia",
    2: "Relações Ecológicas Harmônicas",
    3: "Ciclos Biogeoquímicos e Pirâmides",
    4: "Poluição Atmosférica",
    5: "Saneamento Básico, Lixo e Resíduos",
    6: "Impactos Urbanos",
    7: "Relações Ecológicas Desarmônicas",
    8: "População e Sucessão Ecológica",
}

# Óptica/Ondulatória -- 2ª matéria a ganhar fase (2026-09), a partir de
# 'docs/questoes/Óptica - Fase 1 (PARTE 2).docx' (fonte autoral do
# usuário): a Fase 1 desse documento já vem dividida em 3 subfases
# (1.1 Polarização x Difração, 1.2 Refração/Dispersão/Absorção/
# Reflexão, 1.3 Eco/Reverberação/Doppler/Interferência), cada uma
# testando um "pool" fixo de fenômenos parecidos com contexto variado
# -- achado ao vivo confirmando a suspeita do usuário de que "a banca
# repete o mesmo conjunto de alternativas, só troca o cenário" (ver
# docs/pesquisa_estrategia_de_prova.md, seção sobre Automatic Item
# Generation). Diferente de Ecologia, essa trilha combina DUAS
# matérias (óptica + acústica, mesmo nó de TRILHA_FIXA_NOS) -- por
# isso duas tabelas de fase (uma por matéria), não uma. Fenômeno sem
# entrada em nenhuma das duas (ex: 'transmissao', 'ressonancia',
# 'reflexao' genérico) foi encaixado na subfase mais próxima
# tematicamente (reflexão/refração → subfase 2; ressonância, por
# depender de frequência igual a Doppler/interferência → subfase 3) em
# vez de criar uma 4ª fase para meia dúzia de questão -- reavaliar se
# uma 2ª parte do documento (Fase 2 de Óptica, ainda não escrita)
# trouxer volume suficiente pra justificar separar de verdade.
FASES_OPTICA: dict[int, set[str]] = {
    1: {"polarizacao", "difracao"},
    2: {
        "refracao", "dispersao", "absorcao", "reflexao_especular", "reflexao_difusa",
        "reflexao_interna_total", "reflexao", "transmissao",
    },
    3: {"interferencia", "ressonancia", "efeito_doppler"},
}

FASES_ACUSTICA: dict[int, set[str]] = {
    1: set(),
    2: {"frequencia_constante_na_refracao"},
    3: {"eco", "reverberacao", "efeito_doppler"},
}

NOMES_FASES_OPTICA: dict[int, str] = {
    1: "Polarização e Difração",
    2: "Refração, Dispersão, Absorção e Reflexão",
    3: "Interferência e Ressonância",
}

NOMES_FASES_ACUSTICA: dict[int, str] = {
    1: "Fundamentos (ainda sem questão nesta subfase)",
    2: "Refração do Som",
    3: "Eco, Reverberação e Efeito Doppler",
}

_FASES_POR_MATERIA: dict[str, dict[int, set[str]]] = {
    "ecologia": FASES_ECOLOGIA,
    "optica": FASES_OPTICA,
    "acustica": FASES_ACUSTICA,
}

# Espelhada em _FASES_POR_MATERIA acima -- fases_disponiveis() usava
# NOMES_FASES_ECOLOGIA direto, hardcoded, o que daria nome ERRADO
# (nomes de fase de Ecologia) pra qualquer matéria nova com fase
# própria. Generalizado junto com a adição de Óptica/Acústica.
_NOMES_FASES_POR_MATERIA: dict[str, dict[int, str]] = {
    "ecologia": NOMES_FASES_ECOLOGIA,
    "optica": NOMES_FASES_OPTICA,
    "acustica": NOMES_FASES_ACUSTICA,
}


def fase_de_topico(materia: str, topico: str | None) -> int | None:
    """Devolve o número da fase (1-6) que um `topico` pertence, pra
    quem chamou uma matéria com fases definidas (hoje só 'ecologia').
    Devolve None pra matéria sem fases mapeadas, ou pra questão sem
    `topico` preenchido, ou cujo `topico` não bate com nenhuma fase
    conhecida (ex: questão antiga inserida antes deste mapeamento
    existir) -- nesses casos ela fica de fora de qualquer fase
    específica em vez de quebrar a consulta."""
    mapa = _FASES_POR_MATERIA.get(materia)
    if not mapa or not topico:
        return None
    for fase, topicos in mapa.items():
        if topico in topicos:
            return fase
    return None


def fases_disponiveis(grande_area: str, materia: str, fonte: str | None = None) -> list[dict]:
    """Lista as fases de uma matéria com fase mapeada ('ecologia',
    'optica', 'acustica'), cada uma com quantas questões tem e quantas
    dessas já foram respondidas ao menos uma vez -- alimenta uma
    futura tela de 'escolher a fase' no app mobile. Matéria sem fase
    mapeada devolve lista vazia -- comportamento explícito, não erro,
    pra UI decidir mostrar ou não esse seletor.

    Cada entrada: {'fase', 'nome', 'total', 'respondidas', 'concluida'}."""
    materia_norm = canonicalizar_materia(normalizar_texto(materia))
    mapa = _FASES_POR_MATERIA.get(materia_norm)
    if not mapa:
        return []

    questoes = questoes_por_materia(grande_area, materia_norm, origem="banco_pratica")
    if fonte:
        questoes = [q for q in questoes if q.get("fonte") == fonte]

    ids_por_fase: dict[int, list[str]] = {fase: [] for fase in mapa}
    for q in questoes:
        fase = fase_de_topico(materia_norm, q.get("topico"))
        if fase is not None:
            ids_por_fase[fase].append(q["id_questao"])

    todos_ids = [id_q for ids in ids_por_fase.values() for id_q in ids]
    respondidas_geral: set[str] = set()
    if todos_ids:
        with _conectar() as conn:
            marcadores = ",".join("?" * len(todos_ids))
            linhas = conn.execute(
                f"SELECT DISTINCT id_questao FROM tentativas_usuario WHERE id_questao IN ({marcadores})",
                todos_ids,
            ).fetchall()
        respondidas_geral = {r[0] for r in linhas}

    resultado = []
    for fase in sorted(mapa):
        ids = ids_por_fase[fase]
        respondidas = sum(1 for id_q in ids if id_q in respondidas_geral)
        nomes_materia = _NOMES_FASES_POR_MATERIA.get(materia_norm, {})
        resultado.append({
            "fase": fase,
            "nome": nomes_materia.get(fase, f"Fase {fase}"),
            "total": len(ids),
            "respondidas": respondidas,
            "concluida": len(ids) > 0 and respondidas == len(ids),
        })
    return resultado


def gerar_id_pratica(numero: int) -> str:
    """Gera o id_questao de uma questão do banco de prática, ex:
    'pratica_00001'. Separado de gerar_id_canonico() de propósito --
    banco de prática não tem ano/caderno/numero de prova real por
    trás, só um contador sequencial próprio (ver numero_questao em
    inserir_questao_pratica)."""
    return f"pratica_{numero:05d}"


def inserir_questao_pratica(
    grande_area: str,
    materia: str,
    alternativa_correta: str,
    enunciado_texto: str,
    fonte: str | None = None,
    topico: str | None = None,
) -> tuple[str, str]:
    """Insere UMA questão no banco de prática (origem='banco_pratica')
    -- não é uma questão de prova real do ENEM, então não tem
    ano/caderno/numero de verdade por trás. Usa ANO_BANCO_PRATICA/
    CADERNO_BANCO_PRATICA como sentinela só pra satisfazer as colunas
    NOT NULL de `questoes`; numero_questao aqui é um contador GLOBAL
    do banco de prática inteiro (não por matéria), derivado do maior
    já usado -- suficiente pra id único, sem precisar de outra tabela
    só pra isso.

    Passa pela MESMA validação de taxonomia que inserir_questao() (se
    a matéria não bater com TAXONOMIA_VALIDA, ainda grava, mas com
    status_classificacao='nao_classificado' pra triagem) -- de
    propósito, pra não perder registro nem inventar categoria nova.

    `fonte` é texto livre (ex: 'gemini', 'chatgpt', 'autoral') --
    filtro auxiliar dentro do banco de prática, não afeta a
    identidade da questão nem a validação.

    Retorna (id_questao, status_classificacao), igual inserir_questao().
    """
    if alternativa_correta.strip().upper() not in {"A", "B", "C", "D", "E"}:
        raise ValueError(f"alternativa_correta inválida: '{alternativa_correta}'")
    if not enunciado_texto or not enunciado_texto.strip():
        raise ValueError("enunciado_texto não pode ser vazio numa questão do banco de prática.")

    grande_area_norm = normalizar_texto(grande_area)
    materia_norm = canonicalizar_materia(normalizar_texto(materia))
    status = (
        "classificado"
        if (grande_area_norm, materia_norm) in TAXONOMIA_VALIDA
        else "nao_classificado"
    )

    with _conectar() as conn:
        numero = conn.execute(
            "SELECT COALESCE(MAX(numero_questao), 0) + 1 FROM questoes WHERE origem = 'banco_pratica'"
        ).fetchone()[0]
        id_questao = gerar_id_pratica(numero)
        conn.execute(
            """
            INSERT INTO questoes (
                id_questao, ano, caderno, numero_questao, grande_area, materia,
                topico, enunciado_texto, alternativa_correta, status_classificacao,
                origem, fonte
            ) VALUES (?,?,?,?,?,?,?,?,?,?,'banco_pratica',?)
            """,
            (
                id_questao, ANO_BANCO_PRATICA, CADERNO_BANCO_PRATICA, numero,
                grande_area_norm, materia_norm, topico, enunciado_texto.strip(),
                alternativa_correta.strip().upper(), status, fonte.strip() if fonte else None,
            ),
        )
    return id_questao, status


_PADRAO_ALTERNATIVA_IMPORT = re.compile(r"^\s*([A-Ea-e])\s*[\)\.\:\-]\s+(.+)$")
_PADRAO_GABARITO_IMPORT = re.compile(r"^\s*gabarito\s*[:\-]?\s*([A-Ea-e])\s*$", re.IGNORECASE)


def importar_questoes_praticas_texto(
    texto: str, grande_area: str, materia: str, fonte: str | None = None,
) -> dict:
    """Importa VÁRIAS questões do banco de prática de um texto colado
    de uma vez (ex: uma sessão inteira de prática de Óptica com uma
    IA) -- alternativa ao formulário questão-por-questão, que não
    escala pra "faça 40 questões pra fixar".

    Formato esperado, um bloco por questão, blocos separados por uma
    linha só com '---':

        <enunciado, uma ou mais linhas>
        A) <alternativa A>
        B) <alternativa B>
        C) <alternativa C>
        D) <alternativa D>
        E) <alternativa E>
        GABARITO: <letra>

    A letra de cada alternativa aceita ')', '.', ':' ou '-' depois
    (A), A., A:, A-) e é case-insensitive -- cópia de resposta de IA
    varia o formato o tempo todo, não vale a pena travar num único
    separador. Cada bloco malformado (faltando alguma alternativa ou
    o gabarito) é reportado em 'erros' com um trecho do bloco, mas NÃO
    aborta a importação inteira -- os blocos válidos do mesmo texto
    colado ainda são gravados, prática real de como isso vai ser usado
    (colar uma sessão inteira, corrigir só o que deu problema depois).

    O enunciado_texto gravado reconstrói as 5 alternativas em ordem
    A-E (mesmo que coladas fora de ordem), então a leitura na prática
    por matéria sempre mostra as opções na ordem certa.

    Retorna {'inseridas': [id_questao, ...], 'erros': [str, ...]}."""
    blocos = re.split(r"(?m)^\s*-{3,}\s*$", texto)
    inseridas: list[str] = []
    erros: list[str] = []

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue

        linhas = bloco.split("\n")
        gabarito_letra = None
        linhas_restantes = []
        for linha in linhas:
            m_gab = _PADRAO_GABARITO_IMPORT.match(linha)
            if m_gab:
                gabarito_letra = m_gab.group(1).upper()
            else:
                linhas_restantes.append(linha)

        alternativas: dict[str, str] = {}
        linhas_enunciado = []
        for linha in linhas_restantes:
            m_alt = _PADRAO_ALTERNATIVA_IMPORT.match(linha)
            if m_alt:
                letra = m_alt.group(1).upper()
                alternativas[letra] = m_alt.group(2).strip()
            elif not alternativas:
                # só conta como enunciado o que vem ANTES da primeira
                # alternativa -- qualquer linha solta depois (ex: uma
                # observação da IA no final) não vira enunciado.
                linhas_enunciado.append(linha)

        trecho = bloco[:80].replace("\n", " ") + ("..." if len(bloco) > 80 else "")

        if gabarito_letra is None:
            erros.append(f"Sem 'GABARITO: <letra>' encontrado no bloco: \"{trecho}\"")
            continue
        faltando = [l for l in "ABCDE" if l not in alternativas]
        if faltando:
            erros.append(f"Faltando alternativa(s) {', '.join(faltando)} no bloco: \"{trecho}\"")
            continue
        enunciado = "\n".join(linhas_enunciado).strip()
        if not enunciado:
            erros.append(f"Sem enunciado (texto antes das alternativas) no bloco: \"{trecho}\"")
            continue

        enunciado_completo = enunciado + "\n\n" + "\n".join(f"{l}) {alternativas[l]}" for l in "ABCDE")
        id_questao, _ = inserir_questao_pratica(
            grande_area=grande_area, materia=materia,
            alternativa_correta=gabarito_letra, enunciado_texto=enunciado_completo,
            fonte=fonte,
        )
        inseridas.append(id_questao)

    return {"inseridas": inseridas, "erros": erros}


def fontes_banco_pratica() -> list[str]:
    """Valores distintos de 'fonte' já usados no banco de prática --
    alimenta o filtro/seletor da tela de prática por matéria."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT DISTINCT fonte FROM questoes WHERE origem = 'banco_pratica' AND fonte IS NOT NULL ORDER BY fonte"
        ).fetchall()
    return [r[0] for r in linhas]


def trilha_banco_pratica(
    grande_area: str, materia: str, tamanho_no: int = 5, fonte: str | None = None,
    fase: int | None = None,
) -> list[dict]:
    """Divide as questões do banco de prática de uma matéria em 'nós'
    sequenciais de tamanho_no questões — a trilha estilo Duolingo
    (pedido explícito do usuário: "em cada ponto que separa se tem
    que fazer 5 exercícios, aí depois vai pros próximos 5").

    `fase`, quando passado, restringe a trilha às questões daquela
    fase (ver FASES_ECOLOGIA/fase_de_topico) antes de dividir em nós
    -- pra matéria sem fase mapeada (ex: 'optica'), passar fase=None
    (padrão) preserva o comportamento antigo de trilha única; passar
    um fase para essa matéria devolveria lista vazia (nenhuma questão
    tem fase_de_topico() != None), então a UI só deve oferecer o
    seletor de fase pra matéria que fases_disponiveis() não devolve
    vazio.

    Cada nó vem com:
      - 'indice': posição do nó na trilha (0, 1, 2...)
      - 'questoes': as questões do nó, cada uma com 'ja_respondida'
        (bool) somada aos campos normais de _linha_para_questao_grade
      - 'concluido': True se TODAS as questões do nó já têm pelo menos
        uma tentativa registrada
      - 'desbloqueado': True se este nó pode ser jogado agora -- o
        primeiro nó sempre está desbloqueado; os seguintes só
        desbloqueiam quando TODOS os nós anteriores estão concluídos
        (progressão sequencial, igual ao Duolingo)

    Nada disso é armazenado à parte -- 'concluido'/'ja_respondida' são
    derivados ao vivo de tentativas_usuario, mesmo princípio de toda
    outra função analítica deste módulo (prioridade_de_estudo,
    confianca_recente_por_materia etc.): sem tabela nova, sem estado
    que possa divergir do histórico real.

    questoes_por_materia() já ordena por numero_questao ASC dentro de
    banco_pratica (todo mundo tem ano=0, então o ORDER BY ano DESC não
    discrimina) -- que é exatamente a ordem de inserção/criação, a
    ordem certa pra uma trilha sequencial."""
    materia_norm = canonicalizar_materia(normalizar_texto(materia))
    questoes = questoes_por_materia(grande_area, materia_norm, origem="banco_pratica")
    if fonte:
        questoes = [q for q in questoes if q.get("fonte") == fonte]
    if fase is not None:
        questoes = [q for q in questoes if fase_de_topico(materia_norm, q.get("topico")) == fase]
    if not questoes:
        return []

    ids = [q["id_questao"] for q in questoes]
    with _conectar() as conn:
        marcadores = ",".join("?" * len(ids))
        linhas = conn.execute(
            f"SELECT DISTINCT id_questao FROM tentativas_usuario WHERE id_questao IN ({marcadores})",
            ids,
        ).fetchall()
    respondidas = {r[0] for r in linhas}

    nos = []
    desbloqueado = True
    for i in range(0, len(questoes), tamanho_no):
        bloco = [dict(q, ja_respondida=q["id_questao"] in respondidas) for q in questoes[i:i + tamanho_no]]
        concluido = all(q["ja_respondida"] for q in bloco)
        nos.append({
            "indice": i // tamanho_no, "questoes": bloco,
            "concluido": concluido, "desbloqueado": desbloqueado,
        })
        desbloqueado = desbloqueado and concluido
    return nos


# Trilha fixa entrelaçada, especificada em
# docs/arquitetura_questoes/arquitetura-trilha.docx: ordem de matérias
# escolhida por ROI (assunto de maior incidência/menor esforço de
# aprendizado primeiro), não pela ordem alfabética/curricular. Cada
# item é (materia, fase) -- fase=None pega o banco inteiro da matéria
# (hoje só ecologia tem fase mapeada, ver FASES_ECOLOGIA); um nó pode
# juntar mais de uma matéria (ex: Óptica + Acústica, ambas fazem parte
# do mesmo "Nó 2: Óptica/Ondulatória" do documento).
#
# Eletrodinâmica (Nó 6 do documento) fica de fora por enquanto -- ainda
# não tem nenhuma questão no banco (precisa dos SVGs de circuito
# primeiro). Adicionar aqui assim que a primeira leva de questões
# entrar; não criar o nó vazio antes disso (ver decisão do usuário
# 2026-09-16: só entra na trilha fixa quando tiver conteúdo de verdade).
TRILHA_FIXA_NOS: list[dict] = [
    {
        "chave": "ecologia_poluicao_atmosferica",
        "nome": "Ecologia — Poluição Atmosférica",
        "materias": [("ecologia", 4)],
    },
    # Relações Ecológicas adicionada em 2026-09-17 logo depois da
    # Poluição Atmosférica, não antes dela -- achado ao vivo
    # (classificando as questões oficiais já carregadas, ver
    # docs/pesquisa_estrategia_de_prova.md): na amostra real (11
    # questões), Poluição Atmosférica teve ZERO ocorrência e Relações
    # Ecológicas empatou como o padrão mais recorrente, além de ser
    # mais fácil de fixar (tabela de sinais +/-/0 vs. 4 mecanismos
    # causais distintos da fase 4). Não foi colocada ANTES da fase 4
    # de propósito: o usuário já tinha tentativas registradas em
    # blocos da fase 4 no momento desta mudança, e trilha_fixa()
    # destrava nó por ORDEM da lista -- inserir antes teria travado de
    # volta um nó que ele já tinha começado a concluir.
    #
    # Dividida em 3 sub-nós no mesmo dia, ainda validando -- "Relações
    # Ecológicas" virou um resumo com 14 padrões diferentes numa tela
    # só ("muito coisa", achado ao vivo), e um padrão de DINÂMICA
    # POPULACIONAL (capacidade_de_suporte) aparecia misturado com
    # padrões de relação ENTRE espécies diferentes -- coisas
    # conceitualmente distintas (ver FASES_ECOLOGIA fases 2/7/8).
    {
        "chave": "ecologia_relacoes_harmonicas",
        "nome": "Ecologia — Relações Ecológicas Harmônicas",
        "materias": [("ecologia", 2)],
    },
    {
        "chave": "ecologia_relacoes_desarmonicas",
        "nome": "Ecologia — Relações Ecológicas Desarmônicas",
        "materias": [("ecologia", 7)],
    },
    {
        "chave": "ecologia_populacao_sucessao",
        "nome": "Ecologia — População e Sucessão Ecológica",
        "materias": [("ecologia", 8)],
    },
    # Óptica/Ondulatória dividida em 3 subfases (2026-09), espelhando
    # a estrutura real de 'docs/questoes/Óptica - Fase 1 (PARTE 2).docx'
    # (ver FASES_OPTICA/FASES_ACUSTICA acima) -- cada subfase testa um
    # conjunto fixo de fenômenos parecidos, progressão sequencial igual
    # às outras matérias (só desbloqueia a próxima ao concluir a
    # anterior). Antes disso, 'optica_ondulatoria' era um nó só com
    # fase=None (as 137 questões de óptica+acústica misturadas sem
    # nenhuma ordem pedagógica) -- ver docs/pesquisa_estrategia_de_prova.md
    # §8/§12 pro raciocínio (Automatic Item Generation, pool fixo de
    # alternativas por subfase).
    {
        "chave": "optica_ondulatoria_1",
        "nome": "Óptica/Ondulatória — Polarização e Difração",
        "materias": [("optica", 1), ("acustica", 1)],
    },
    {
        "chave": "optica_ondulatoria_2",
        "nome": "Óptica/Ondulatória — Refração, Dispersão, Absorção e Reflexão",
        "materias": [("optica", 2), ("acustica", 2)],
    },
    {
        "chave": "optica_ondulatoria_3",
        "nome": "Óptica/Ondulatória — Eco, Reverberação, Doppler e Interferência",
        "materias": [("optica", 3), ("acustica", 3)],
    },
    {
        "chave": "fisiologia_vacina_soro",
        "nome": "Fisiologia Humana — Vacina vs. Soro",
        "materias": [("fisiologia_humana", None)],
    },
    {
        "chave": "cinematica_mru",
        "nome": "Cinemática — Velocidade Média e MRU",
        "materias": [("cinematica", None)],
    },
    {
        "chave": "separacao_de_misturas",
        "nome": "Química Geral — Separação de Misturas",
        "materias": [("separacao_de_misturas", None)],
    },
]


def trilha_fixa(tamanho_no: int = 5) -> list[dict]:
    """Monta a trilha fixa entrelaçada entre matérias (TRILHA_FIXA_NOS),
    com progressão sequencial em DOIS níveis:

      1. dentro de cada nó, os mini-blocos de `tamanho_no` questões
         desbloqueiam em sequência (mesma regra de trilha_banco_pratica);
      2. entre nós, um nó só desbloqueia quando TODOS os blocos do nó
         ANTERIOR estiverem concluídos -- é isso que faz a trilha
         "entrelaçada" (Ecologia -> Óptica -> Fisiologia -> ...) em vez
         de várias trilhas soltas por matéria.

    Cada entrada do retorno: {'chave', 'nome', 'concluido', 'desbloqueado',
    'blocos': [...]}, onde cada bloco tem o mesmo formato de
    trilha_banco_pratica ('indice', 'questoes', 'concluido', 'desbloqueado'
    -- aqui 'desbloqueado' do bloco já leva em conta se o NÓ INTEIRO está
    desbloqueado, não só a posição do bloco dentro dele).

    grande_area é sempre 'ciencias_natureza' -- todas as matérias de
    TRILHA_FIXA_NOS são de Ciências da Natureza; não parametrizado de
    propósito, pra não sugerir que isso já suporta Matemática (não
    suporta -- nenhuma matéria de matemática está mapeada aqui ainda)."""
    grande_area = "ciencias_natureza"
    resultado = []
    no_anterior_concluido = True

    for config in TRILHA_FIXA_NOS:
        questoes: list[dict] = []
        for materia, fase in config["materias"]:
            materia_norm = canonicalizar_materia(normalizar_texto(materia))
            qs = questoes_por_materia(grande_area, materia_norm, origem="banco_pratica")
            if fase is not None:
                qs = [q for q in qs if fase_de_topico(materia_norm, q.get("topico")) == fase]
            questoes.extend(qs)

        ids = [q["id_questao"] for q in questoes]
        respondidas: set[str] = set()
        if ids:
            with _conectar() as conn:
                marcadores = ",".join("?" * len(ids))
                linhas = conn.execute(
                    f"SELECT DISTINCT id_questao FROM tentativas_usuario WHERE id_questao IN ({marcadores})",
                    ids,
                ).fetchall()
            respondidas = {r[0] for r in linhas}

        no_desbloqueado = no_anterior_concluido
        blocos = []
        bloco_anterior_concluido = True
        for i in range(0, len(questoes), tamanho_no):
            bloco_questoes = [
                dict(q, ja_respondida=q["id_questao"] in respondidas)
                for q in questoes[i:i + tamanho_no]
            ]
            bloco_concluido = all(q["ja_respondida"] for q in bloco_questoes)
            blocos.append({
                "indice": i // tamanho_no,
                "questoes": bloco_questoes,
                "concluido": bloco_concluido,
                "desbloqueado": no_desbloqueado and bloco_anterior_concluido,
            })
            bloco_anterior_concluido = bloco_anterior_concluido and bloco_concluido

        no_concluido = len(questoes) > 0 and all(b["concluido"] for b in blocos)
        resultado.append({
            "chave": config["chave"],
            "nome": config["nome"],
            "concluido": no_concluido,
            "desbloqueado": no_desbloqueado,
            "blocos": blocos,
        })
        no_anterior_concluido = no_anterior_concluido and no_concluido

    return resultado


def listar_banco_pratica() -> list[dict]:
    """Toda questão do banco de prática, mais recente primeiro --
    alimenta a listagem/gerenciamento no Admin (apagar uma questão
    ruim usa apagar_questao(id_questao), que já é genérico o
    suficiente pra funcionar aqui sem mudança nenhuma).

    Ordena por numero_questao DESC (não só criado_em) porque
    criado_em só tem resolução de segundo -- duas inserções no mesmo
    segundo (ex: importar_questoes_praticas_texto inserindo vários
    blocos de uma vez) empatariam nele; numero_questao é sequencial
    por inserção, então desempata na ordem certa sempre."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT id_questao, grande_area, materia, status_classificacao, "
            "alternativa_correta, fonte, enunciado_texto, criado_em "
            "FROM questoes WHERE origem = 'banco_pratica' ORDER BY numero_questao DESC"
        ).fetchall()
    return [
        {
            "id_questao": r[0], "grande_area": r[1], "materia": r[2],
            "status_classificacao": r[3], "alternativa_correta": r[4],
            "fonte": r[5], "enunciado_texto": r[6], "criado_em": r[7],
        }
        for r in linhas
    ]


def inserir_resolucao(id_questao: str, tipo: str, conteudo: str, canal: str | None = None) -> bool:
    """Adiciona uma resolução (vídeo ou texto) a uma questão que já
    existe. Uma questão pode ter N resoluções DIFERENTES — não há
    chave única entre questão e tipo aqui de propósito, é o ponto
    principal que o modelo antigo (1 linha CSV = 1 vídeo = 1 questão)
    não permitia.

    O que não pode duplicar é o MESMO conteúdo (link/texto) repetido
    pra mesma questão — sem checar isso, recarregar a mesma playlist
    duas vezes (ou rodar reconstruir_base.py de novo) empilha o vídeo
    idêntico de novo a cada execução. Retorna False (no-op) se esse
    exato (id_questao, tipo, conteudo) já existia; True se inseriu."""
    if tipo not in ("video", "texto"):
        raise ValueError(f"tipo deve ser 'video' ou 'texto', recebi '{tipo}'")

    with _conectar() as conn:
        existe = conn.execute(
            "SELECT 1 FROM questoes WHERE id_questao = ?", (id_questao,)
        ).fetchone()
        if not existe:
            raise ValueError(f"Questão '{id_questao}' não existe — insira a questão antes da resolução.")

        ja_existe = conn.execute(
            "SELECT 1 FROM resolucoes WHERE id_questao = ? AND tipo = ? AND conteudo = ?",
            (id_questao, tipo, conteudo),
        ).fetchone()
        if ja_existe:
            return False

        conn.execute(
            "INSERT INTO resolucoes (id_questao, tipo, conteudo, canal) VALUES (?,?,?,?)",
            (id_questao, tipo, conteudo, canal),
        )
        return True


# ============================================================
# REVISÃO ESPAÇADA (LEITNER SIMPLIFICADO)
# ============================================================

TETO_INTERVALO_DIAS = 90  # trava o intervalo pra questão não sumir da rotação de vez


def _calcular_leitner(streak_anterior: int, resultado: str) -> tuple[int, int]:
    """Regra: errou -> volta em 1 dia, streak zera.
    Acertou -> streak sobe 1, intervalo = 2^(streak-1) dias, com teto.
    (1º acerto: 1 dia. 2º acerto seguido: 2 dias. 3º: 4. 4º: 8...)

    Calculado a partir do streak, não do intervalo anterior guardado
    — assim o número nunca "deriva" por acúmulo de arredondamento ou
    por um bug de estado corrompido; sempre dá pra recalcular do zero
    a partir do histórico em tentativas_usuario.
    """
    if resultado == "errou":
        return 0, 1
    novo_streak = streak_anterior + 1
    novo_intervalo = min(2 ** (novo_streak - 1), TETO_INTERVALO_DIAS)
    return novo_streak, novo_intervalo


def calcular_proxima_revisao(id_questao: str, resultado: str, conn: sqlite3.Connection) -> tuple[date, int, int]:
    """Lê o streak atual de estado_revisao (0 se a questão nunca foi
    tentada) e devolve (data_proxima_revisao, intervalo_dias, streak).
    Não grava nada — só calcula. Quem grava é registrar_tentativa()."""
    linha = conn.execute(
        "SELECT streak_acertos FROM estado_revisao WHERE id_questao = ?", (id_questao,)
    ).fetchone()
    streak_anterior = linha[0] if linha else 0

    novo_streak, novo_intervalo = _calcular_leitner(streak_anterior, resultado)
    proxima = date.today() + timedelta(days=novo_intervalo)
    return proxima, novo_intervalo, novo_streak


def _recomputar_estado_revisao(id_questao: str, conn: sqlite3.Connection) -> None:
    """Reconstrói estado_revisao de UMA questão do zero, reproduzindo
    TODO o histórico restante em tentativas_usuario (ordem cronológica)
    pelo Leitner -- streak/intervalo são cumulativos, então editar ou
    apagar uma tentativa no meio da história pode mudar o que toda
    tentativa seguinte teria calculado; só um replay completo garante
    o streak final certo. Sem nenhuma tentativa restando, apaga
    estado_revisao (questão volta a 'nunca tentada'). Assume que quem
    chama já fez a mutação em tentativas_usuario antes (INSERT/UPDATE/
    DELETE) dentro da MESMA conexão/transação."""
    restantes = conn.execute(
        "SELECT data_tentativa, resultado FROM tentativas_usuario "
        "WHERE id_questao = ? ORDER BY data_tentativa",
        (id_questao,),
    ).fetchall()
    if not restantes:
        conn.execute("DELETE FROM estado_revisao WHERE id_questao = ?", (id_questao,))
        return
    streak, intervalo = 0, 1
    for _, resultado in restantes:
        streak, intervalo = _calcular_leitner(streak, resultado)
    ultima_data = restantes[-1][0]
    proxima = (date.fromisoformat(ultima_data[:10]) + timedelta(days=intervalo)).isoformat()
    conn.execute(
        """
        INSERT INTO estado_revisao (id_questao, intervalo_dias, streak_acertos, proxima_revisao, ultima_tentativa)
        VALUES (?,?,?,?,?)
        ON CONFLICT(id_questao) DO UPDATE SET
            intervalo_dias = excluded.intervalo_dias,
            streak_acertos = excluded.streak_acertos,
            proxima_revisao = excluded.proxima_revisao,
            ultima_tentativa = excluded.ultima_tentativa
        """,
        (id_questao, intervalo, streak, proxima, ultima_data[:10]),
    )


# ============================================================
# REGISTRO DE TENTATIVA
# ============================================================

def registrar_tentativa(id_questao: str, resposta_escolhida: str | None, duracao_segundos: int | None = None) -> dict:
    """Única função que deve gravar em tentativas_usuario e
    estado_revisao — evita os dois divergirem por escritas separadas.

    Compara a resposta contra o gabarito guardado em questoes (o
    próprio sistema decide acerto/erro; não depende de nenhum rótulo
    externo, o que elimina o problema antigo de 'fonte_nivel' que
    cravava 'confirmado_transcricao_ia' mesmo quando não era verdade).

    resposta_escolhida=None registra questão deixada em branco --
    SEMPRE 'errou' (não tem letra pra comparar, e não responder nunca
    pode contar como acerto). É uma tentativa de verdade, não um
    "pular": entra no Leitner (agenda revisão, e cedo -- streak zera
    igual erro comum) e em toda estatística baseada em
    tentativas_usuario, em vez de desaparecer da conta como se a
    questão não existisse na prova.

    duracao_segundos é OPCIONAL e só de registro (pedido explícito do
    usuário: "saber quanto tempo gasto numa questão", guardado pra
    métrica futura -- hoje nenhuma função deste módulo lê essa coluna
    de volta). None quando quem chamou não mediu tempo nenhum (scripts
    de carga em lote como reconstruir_base.py, chamadas antigas do
    Streamlit antes desta coluna existir) -- não é 0s, é "não sei"."""
    if resposta_escolhida is not None:
        resposta_escolhida = resposta_escolhida.strip().upper()
        if resposta_escolhida not in {"A", "B", "C", "D", "E"}:
            raise ValueError(f"resposta_escolhida inválida: '{resposta_escolhida}'")
    resposta = resposta_escolhida

    with _conectar() as conn:
        linha = conn.execute(
            "SELECT alternativa_correta FROM questoes WHERE id_questao = ?", (id_questao,)
        ).fetchone()
        if linha is None:
            raise ValueError(f"Questão '{id_questao}' não existe na base.")

        resultado = "acertou" if (resposta is not None and resposta == linha[0]) else "errou"
        proxima_revisao, intervalo_dias, streak = calcular_proxima_revisao(id_questao, resultado, conn)

        conn.execute(
            """
            INSERT INTO tentativas_usuario
                (id_questao, resposta_escolhida, resultado, intervalo_dias, streak_acertos, proxima_revisao, duracao_segundos)
            VALUES (?,?,?,?,?,?,?)
            """,
            (id_questao, resposta, resultado, intervalo_dias, streak, proxima_revisao.isoformat(), duracao_segundos),
        )
        id_tentativa = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """
            INSERT INTO estado_revisao (id_questao, intervalo_dias, streak_acertos, proxima_revisao, ultima_tentativa)
            VALUES (?,?,?,?, date('now','localtime'))
            ON CONFLICT(id_questao) DO UPDATE SET
                intervalo_dias = excluded.intervalo_dias,
                streak_acertos = excluded.streak_acertos,
                proxima_revisao = excluded.proxima_revisao,
                ultima_tentativa = excluded.ultima_tentativa
            """,
            (id_questao, intervalo_dias, streak, proxima_revisao.isoformat()),
        )

    return {
        "id_tentativa": id_tentativa,
        "id_questao": id_questao,
        "resultado": resultado,
        "resposta_escolhida": resposta,
        "alternativa_correta": linha[0],
        "intervalo_dias": intervalo_dias,
        "streak_acertos": streak,
        "proxima_revisao": proxima_revisao.isoformat(),
    }


def desfazer_tentativas(ids_tentativa: list[int]) -> dict:
    """Desfaz um lote de tentativas recém-registradas -- pensado pra
    corrigir um erro de transcrição percebido na hora logo após clicar
    'Corrigir' ('marquei a letra errada por engano'), não pra reescrever
    desempenho de dias/semanas atrás (tentativas_usuario continua
    append-only pra qualquer outro caso -- ver CLAUDE.md).

    Só desfaz questão que NÃO tinha NENHUMA tentativa anterior a essa
    (ou seja, essa era a primeira/única) -- pra qualquer questão com
    histórico anterior, desfazer exigiria recalcular streak/intervalo
    do Leitner reproduzindo o que sobra, o que esta função
    deliberadamente não tenta fazer ainda (sem caso de uso real pra
    justificar esse risco agora). Questões puladas aparecem em
    'puladas_com_historico' pra a UI avisar em vez de fingir que
    desfez."""
    if not ids_tentativa:
        return {"desfeitas": [], "puladas_com_historico": []}
    with _conectar() as conn:
        placeholders = ",".join("?" * len(ids_tentativa))
        linhas = conn.execute(
            f"SELECT id_tentativa, id_questao FROM tentativas_usuario WHERE id_tentativa IN ({placeholders})",
            ids_tentativa,
        ).fetchall()
        desfeitas, puladas = [], []
        for id_t, id_q in linhas:
            total = conn.execute(
                "SELECT COUNT(*) FROM tentativas_usuario WHERE id_questao = ?", (id_q,)
            ).fetchone()[0]
            if total > 1:
                puladas.append(id_q)
                continue
            conn.execute("DELETE FROM tentativas_usuario WHERE id_tentativa = ?", (id_t,))
            _recomputar_estado_revisao(id_q, conn)
            desfeitas.append(id_t)
    return {"desfeitas": desfeitas, "puladas_com_historico": puladas}


def apagar_rodada_tentativa(ano: int, caderno: str, grande_area: str, numero_tentativa: int) -> dict:
    """Apaga uma rodada INTEIRA (a tentativa de número numero_tentativa
    de cada questão dessa prova que chegou a essa rodada -- mesma
    numeração que resumo_por_tentativa()/simulados_feitos() já
    mostram) e recalcula estado_revisao de cada questão afetada
    reproduzindo o que sobra (ver _recomputar_estado_revisao).

    Diferente de desfazer_tentativas() (só desfaz a ÚLTIMA rodada de
    uma questão sem histórico nenhum antes, pensada pra corrigir um
    misclique agora mesmo): esta função apaga de propósito mesmo
    havendo histórico -- pra quando uma rodada inteira foi reenviada
    sem querer (ex: duplicada) e precisa sumir, uso deliberado da aba
    'Simulados já feitos', não uma correção instantânea."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT id_tentativa, id_questao FROM (
                SELECT t.id_tentativa, t.id_questao,
                       ROW_NUMBER() OVER (PARTITION BY t.id_questao ORDER BY t.data_tentativa) AS numero_tentativa
                FROM tentativas_usuario t JOIN questoes q ON q.id_questao = t.id_questao
                WHERE q.ano = ? AND q.caderno = ? AND q.grande_area = ?
            )
            WHERE numero_tentativa = ?
            """,
            (ano, caderno_norm, grande_area_norm, numero_tentativa),
        ).fetchall()
        ids_tentativa = [r[0] for r in linhas]
        ids_questao = [r[1] for r in linhas]
        if ids_tentativa:
            placeholders = ",".join("?" * len(ids_tentativa))
            conn.execute(f"DELETE FROM tentativas_usuario WHERE id_tentativa IN ({placeholders})", ids_tentativa)
        for id_q in ids_questao:
            _recomputar_estado_revisao(id_q, conn)
        conn.execute(
            "DELETE FROM nomes_tentativas WHERE ano=? AND caderno=? AND grande_area=? AND numero_tentativa=?",
            (ano, caderno_norm, grande_area_norm, numero_tentativa),
        )
    return {"tentativas_apagadas": len(ids_tentativa), "questoes_recalculadas": len(set(ids_questao))}


def editar_resposta_tentativa(id_tentativa: int, nova_resposta: str | None) -> dict:
    """Corrige a letra marcada numa tentativa JÁ REGISTRADA, de
    qualquer rodada (não precisa ser a mais recente) -- recalcula
    resultado contra o gabarito atual e reconstrói estado_revisao da
    questão inteira via replay (ver _recomputar_estado_revisao), já
    que mudar uma tentativa no meio do histórico pode mudar o streak
    que toda tentativa seguinte teria calculado na hora. Zera
    tipo_erro dessa tentativa -- uma classificação de erro presa a uma
    letra que não é mais a registrada não faz sentido manter.

    nova_resposta=None marca a tentativa como deixada em branco
    (sempre 'errou') -- simétrico ao que registrar_tentativa() já
    aceita na hora de responder."""
    if nova_resposta is not None:
        nova_resposta = nova_resposta.strip().upper()
        if nova_resposta not in {"A", "B", "C", "D", "E"}:
            raise ValueError(f"resposta_escolhida inválida: '{nova_resposta}'")
    with _conectar() as conn:
        linha = conn.execute(
            "SELECT t.id_questao, q.alternativa_correta FROM tentativas_usuario t "
            "JOIN questoes q ON q.id_questao = t.id_questao WHERE t.id_tentativa = ?",
            (id_tentativa,),
        ).fetchone()
        if linha is None:
            raise ValueError(f"Tentativa '{id_tentativa}' não existe.")
        id_questao, gabarito = linha
        resultado = "acertou" if (nova_resposta is not None and nova_resposta == gabarito) else "errou"
        conn.execute(
            "UPDATE tentativas_usuario SET resposta_escolhida=?, resultado=?, tipo_erro=NULL WHERE id_tentativa=?",
            (nova_resposta, resultado, id_tentativa),
        )
        _recomputar_estado_revisao(id_questao, conn)
    return {"id_tentativa": id_tentativa, "id_questao": id_questao, "resposta_escolhida": nova_resposta, "resultado": resultado}


TIPOS_ERRO = {
    "erro_de_conta": "Erro de conta (contas certas na cabeça, errou na execução)",
    "erro_de_pegadinha": "Erro de pegadinha (leu rápido, confundiu o que foi pedido)",
    "erro_de_conteudo": "Erro de conteúdo (não sabia a fórmula/conceito)",
}


def atualizar_tipo_erro(id_tentativa: int, tipo_erro: str) -> None:
    """Classifica POR QUE uma tentativa errada errou -- inspirado no
    guia de classificação de erro do Xequemat. Só faz sentido pra
    tentativa com resultado='errou'; não valida isso aqui de propósito
    (quem decide o que é 'erro' é sempre resultado, calculado contra
    o gabarito -- essa classificação é só um rótulo complementar)."""
    if tipo_erro not in TIPOS_ERRO:
        raise ValueError(f"tipo_erro inválido: '{tipo_erro}'. Use um de {list(TIPOS_ERRO)}")
    with _conectar() as conn:
        conn.execute(
            "UPDATE tentativas_usuario SET tipo_erro = ? WHERE id_tentativa = ?",
            (tipo_erro, id_tentativa),
        )


def analise_por_tipo_erro(grande_area: str) -> list[dict]:
    """Cruza matéria x tipo de erro -- 'você erra Geometria, mas é erro
    de conta, não de conteúdo' é exatamente o tipo de insight que isso
    devolve. Filtra por grande_area e só considera questão
    classificada, mesma regra de sempre."""
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT q.materia, t.tipo_erro, COUNT(*)
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE t.resultado = 'errou' AND t.tipo_erro IS NOT NULL
              AND q.status_classificacao = 'classificado' AND q.grande_area = ?
            GROUP BY q.materia, t.tipo_erro
            ORDER BY q.materia
            """,
            (grande_area_norm,),
        ).fetchall()
    return [{"materia": m, "tipo_erro": t, "quantidade": q} for m, t, q in linhas]


# ============================================================
# CONSULTAS DE APOIO (base pras métricas que você pediu depois)
# ============================================================

def _carregar_gabarito_de_texto(
    texto_csv: str, ano: int, caderno: str, grande_area_padrao: str, sobrescrever: bool,
    preservar_materia_classificada: bool = False,
) -> dict:
    """Núcleo compartilhado: recebe o CONTEÚDO do CSV já como string
    (não um caminho de arquivo) e faz a carga. carregar_gabarito_csv()
    e carregar_gabarito_texto() só diferem em como conseguem esse
    texto -- ler de arquivo ou receber já colado.

    preservar_materia_classificada=True muda o que "sobrescrever" quer
    dizer pra matéria especificamente: se a questão já existe e já
    está status_classificacao='classificado', a matéria do CSV é
    ignorada e a matéria JÁ GRAVADA é reenviada no lugar (só o
    gabarito/demais campos do CSV realmente sobrescrevem). Existe pra
    reconstruir_base.py: os CSVs de gabarito oficial servem de fonte
    pra RESPOSTA, mas a matéria neles é só um valor inicial/placeholder
    (ex: 'sem_video_pendente') -- sem isso, recarregar o gabarito
    oficial derruba classificação melhor já conseguida depois via
    título de vídeo ou triagem manual. Callers de UI (Admin, Triagem)
    não usam isso -- lá sobrescrever=True É pra vencer o que já existe,
    porque é correção humana deliberada."""
    resumo = {"classificadas": 0, "nao_classificadas": [], "erros": []}

    leitor = csv.DictReader(io.StringIO(texto_csv))
    obrigatorias = {"numero", "materia", "gabarito"}
    faltando = obrigatorias - set(leitor.fieldnames or [])
    if faltando:
        raise ValueError(f"CSV sem as colunas obrigatórias: {sorted(faltando)}")

    for i, linha in enumerate(leitor, start=2):  # start=2: linha 1 é o header
        try:
            numero = int(linha["numero"])
            materia = (linha["materia"] or "").strip()
            gabarito = (linha["gabarito"] or "").strip()
            grande_area = (linha.get("grande_area") or grande_area_padrao).strip()

            if not materia or not gabarito:
                resumo["erros"].append(f"linha {i}: materia ou gabarito vazio")
                continue

            if preservar_materia_classificada and sobrescrever:
                id_provisorio = gerar_id_canonico(ano, caderno, numero)
                with _conectar() as conn:
                    atual = conn.execute(
                        "SELECT materia FROM questoes WHERE id_questao = ? AND status_classificacao = 'classificado'",
                        (id_provisorio,),
                    ).fetchone()
                if atual is not None:
                    materia = atual[0]

            id_q, status = inserir_questao(
                ano=ano, caderno=caderno, numero=numero,
                grande_area=grande_area, materia=materia,
                alternativa_correta=gabarito,
                sobrescrever=sobrescrever,
            )
            if status == "classificado":
                resumo["classificadas"] += 1
            else:
                resumo["nao_classificadas"].append(id_q)
        except (ValueError, KeyError) as e:
            resumo["erros"].append(f"linha {i}: {e}")

    return resumo


def carregar_gabarito_csv(
    caminho: str | Path, ano: int, caderno: str,
    grande_area_padrao: str = "matematica", sobrescrever: bool = False,
    preservar_materia_classificada: bool = False,
) -> dict:
    """Carrega o gabarito de uma prova inteira a partir de um arquivo
    CSV com colunas obrigatórias: numero, materia, gabarito (e uma
    coluna opcional grande_area, útil quando a prova mistura
    matemática e ciências da natureza).

    Retorna um resumo (classificadas, nao_classificadas, erros) pra
    você ver de cara, sem abrir o banco, se algo no CSV precisa de
    revisão antes de liberar a prova pro cartão-resposta.

    Ver _carregar_gabarito_de_texto() pro que preservar_materia_classificada faz.
    """
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        texto_csv = f.read()
    return _carregar_gabarito_de_texto(
        texto_csv, ano, caderno, grande_area_padrao, sobrescrever, preservar_materia_classificada
    )


def carregar_gabarito_texto(
    texto_csv: str, ano: int, caderno: str,
    grande_area_padrao: str = "matematica", sobrescrever: bool = False,
) -> dict:
    """Mesma coisa que carregar_gabarito_csv(), mas recebe o CSV como
    texto colado direto (ex: de uma caixa de texto na tela), em vez de
    caminho de arquivo -- pra carregar gabarito sem precisar salvar
    arquivo em pasta nenhuma antes."""
    return _carregar_gabarito_de_texto(texto_csv, ano, caderno, grande_area_padrao, sobrescrever)


def listar_provas() -> list[tuple[int, str, str]]:
    """Provas distintas (ano, caderno, grande_area) já cadastradas —
    alimenta o seletor de prova do cartão-resposta digital. Matemática
    e Ciências da Natureza do mesmo ano/caderno aparecem como opções
    SEPARADAS, mesmo sendo o mesmo dia de prova de verdade — pra não
    misturar 45+44 questões de áreas diferentes na mesma grade.

    Filtra origem='enem_oficial' -- questão do banco de prática não é
    uma prova de verdade (ver ANO_BANCO_PRATICA/CADERNO_BANCO_PRATICA),
    não deve aparecer aqui nem em nada que dependa disto (simulado
    completo, simulados já feitos, apagar prova)."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT DISTINCT ano, caderno, grande_area FROM questoes "
            "WHERE origem = 'enem_oficial' ORDER BY ano DESC, caderno, grande_area"
        ).fetchall()
    return linhas


def provas_com_enunciado() -> list[tuple[int, str, str, int, int]]:
    """Provas (ano, caderno, grande_area) que têm AO MENOS UMA questão
    com enunciado_texto preenchido, com a cobertura (quantas de quantas)
    -- alimenta a página beta de fazer a prova inteira lendo o
    enunciado no site, que só faz sentido oferecer pra prova que já
    passou por extrair_enunciados_pdf.py (ou pelo editor manual).

    Filtra origem='enem_oficial' pelo mesmo motivo de listar_provas()."""
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT ano, caderno, grande_area,
                   SUM(CASE WHEN enunciado_texto IS NOT NULL THEN 1 ELSE 0 END),
                   COUNT(*)
            FROM questoes
            WHERE origem = 'enem_oficial'
            GROUP BY ano, caderno, grande_area
            HAVING SUM(CASE WHEN enunciado_texto IS NOT NULL THEN 1 ELSE 0 END) > 0
            ORDER BY ano DESC, caderno, grande_area
            """
        ).fetchall()
    return linhas


def simulados_completos_disponiveis() -> list[dict]:
    """Combinações (ano, caderno) com AS DUAS grandes áreas carregadas
    -- o que 'Simulado completo' precisa pra existir. Um mesmo ano pode
    ter MAIS DE UM caderno completo (ex: 2024 tem azul completo E
    amarelo completo) -- cada um vira sua PRÓPRIA opção, nunca só uma
    por ano (uma versão anterior desta função guardava só um caderno
    por (ano, área) e um sobrescrevia o outro em silêncio assim que um
    segundo caderno apareceu pra mesma área/ano).

    Quando um ano não tem NENHUM caderno com as duas áreas ao mesmo
    tempo, mas cada área tem exatamente UM caderno carregado (podem ser
    cores diferentes -- 2023 é matemática/Azul + ciências/Cinza, um
    padrão real do INEP naquele ano), cai num modo de reserva que cruza
    os dois mesmo assim. Quando as duas áreas têm MAIS de um caderno
    cada e nenhum coincide, não há como adivinhar qual par faz sentido
    -- esse ano fica de fora do simulado completo (mas continua
    disponível em 'Uma prova por vez')."""
    por_ano: dict[int, dict[str, set[str]]] = {}
    for ano, caderno, area in listar_provas():
        por_ano.setdefault(ano, {}).setdefault(area, set()).add(caderno)

    combos = []
    for ano, areas in sorted(por_ano.items(), reverse=True):
        cadernos_mat = areas.get("matematica", set())
        cadernos_cie = areas.get("ciencias_natureza", set())
        if not cadernos_mat or not cadernos_cie:
            continue
        comuns = cadernos_mat & cadernos_cie
        if comuns:
            for caderno in sorted(comuns):
                combos.append({"ano": ano, "caderno_matematica": caderno, "caderno_ciencias": caderno})
        elif len(cadernos_mat) == 1 and len(cadernos_cie) == 1:
            combos.append({
                "ano": ano,
                "caderno_matematica": next(iter(cadernos_mat)),
                "caderno_ciencias": next(iter(cadernos_cie)),
            })
    return combos


def progresso_simulados() -> list[dict]:
    """Pra cada ano com simulado completo disponível: quanto já foi
    respondido (cobertura) e quanto das erradas já tem tipo_erro
    classificado -- a 'correção' de verdade, refletir sobre o motivo,
    não só bater contra o gabarito. Base pro checklist do Calendário."""
    resultado = []
    for combo in simulados_completos_disponiveis():
        ano = combo["ano"]
        with _conectar() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM questoes WHERE ano = ? AND "
                "((grande_area='matematica' AND caderno=?) OR (grande_area='ciencias_natureza' AND caderno=?))",
                (ano, combo["caderno_matematica"], combo["caderno_ciencias"]),
            ).fetchone()[0]
            respondidas = conn.execute(
                "SELECT COUNT(DISTINCT t.id_questao) FROM tentativas_usuario t "
                "JOIN questoes q ON q.id_questao = t.id_questao "
                "WHERE q.ano = ? AND "
                "((q.grande_area='matematica' AND q.caderno=?) OR (q.grande_area='ciencias_natureza' AND q.caderno=?))",
                (ano, combo["caderno_matematica"], combo["caderno_ciencias"]),
            ).fetchone()[0]
            erradas = conn.execute(
                "SELECT COUNT(*), SUM(CASE WHEN t.tipo_erro IS NOT NULL THEN 1 ELSE 0 END) "
                "FROM tentativas_usuario t JOIN questoes q ON q.id_questao = t.id_questao "
                "WHERE t.resultado='errou' AND q.ano = ? AND "
                "((q.grande_area='matematica' AND q.caderno=?) OR (q.grande_area='ciencias_natureza' AND q.caderno=?))",
                (ano, combo["caderno_matematica"], combo["caderno_ciencias"]),
            ).fetchone()
        total_erradas, erradas_com_motivo = erradas[0] or 0, erradas[1] or 0
        resultado.append({
            "ano": ano,
            "caderno_matematica": combo["caderno_matematica"],
            "caderno_ciencias": combo["caderno_ciencias"],
            "total_questoes": total,
            "respondidas": respondidas,
            "cobertura_pct": round(respondidas / total * 100, 1) if total else 0.0,
            "feito": respondidas >= total * 0.8 if total else False,
            "erradas_total": total_erradas,
            "erradas_corrigidas": erradas_com_motivo,
            "correcao_completa": (erradas_com_motivo >= total_erradas) if total_erradas else True,
        })
    return resultado


_COLUNAS_QUESTAO_GRADE = (
    "id_questao, numero_questao, materia, status_classificacao, "
    "ano, caderno, grande_area, enunciado_texto, enunciado_imagem_path, origem, fonte, topico"
)


def _linha_para_questao_grade(r: tuple) -> dict:
    """Mapeia uma linha de _COLUNAS_QUESTAO_GRADE pro dict que a grade
    do cartão-resposta (e o enunciado inline) esperam -- um lugar só
    pra esse formato, usado por toda consulta que alimenta a grade
    (prova inteira, revisão do dia, prática por matéria).

    'topico' foi adicionado (2026-09) só pra alimentar
    fase_de_topico()/fases_disponiveis() -- nenhum caller existente
    quebra por causa disso, todos acessam por chave de dict."""
    return {
        "id_questao": r[0], "numero_questao": r[1], "materia": r[2],
        "status_classificacao": r[3], "ano": r[4], "caderno": r[5],
        "grande_area": r[6], "enunciado_texto": r[7], "enunciado_imagem_path": r[8],
        "origem": r[9], "fonte": r[10], "topico": r[11],
    }


def listar_questoes_da_prova(ano: int, caderno: str, grande_area: str) -> list[dict]:
    """Questões de uma prova específica (ano+caderno+área), ordenadas
    por número — monta a grade do cartão-resposta. 'caderno' é
    normalizado aqui pra aceitar 'Azul' ou 'azul' indiferentemente."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            f"""
            SELECT {_COLUNAS_QUESTAO_GRADE}
            FROM questoes
            WHERE ano = ? AND caderno = ? AND grande_area = ?
            ORDER BY numero_questao
            """,
            (ano, caderno_norm, grande_area_norm),
        ).fetchall()
    return [_linha_para_questao_grade(r) for r in linhas]


def questoes_por_ids(ids: list[str]) -> list[dict]:
    """Busca questões por id_questao, na ordem em que os ids foram
    passados — usado pela Revisão do Dia, cuja ordem (mais atrasada
    primeiro) já vem de questoes_para_revisar() e não deve ser
    reordenada por ano/número."""
    if not ids:
        return []
    marcadores = ",".join("?" * len(ids))
    with _conectar() as conn:
        linhas = conn.execute(
            f"SELECT {_COLUNAS_QUESTAO_GRADE} FROM questoes WHERE id_questao IN ({marcadores})",
            ids,
        ).fetchall()
    por_id = {r[0]: _linha_para_questao_grade(r) for r in linhas}
    return [por_id[id_q] for id_q in ids if id_q in por_id]


def questoes_por_materia(grande_area: str, materia: str, origem: str | None = None) -> list[dict]:
    """Todas as questões JÁ CLASSIFICADAS de uma matéria, de qualquer
    ano/caderno -- alimenta o modo 'Praticar por matéria', que mistura
    anos de propósito (o oposto do cartão-resposta de prova única, que
    nunca mistura). Só questão 'classificado' entra, mesma regra do
    resto do sistema: matéria de questão pendente é só um placeholder,
    não um assunto de verdade pra praticar.

    Mistura questão real do ENEM ('enem_oficial') com questão do banco
    de prática ('banco_pratica') por padrão (origem=None) -- de
    propósito: as duas alimentam o MESMO pipeline de estudo (Leitner,
    prioridade), então a mesma tela que já mistura ano deve misturar
    origem também. Passe origem='enem_oficial' ou 'banco_pratica' pra
    restringir a um dos dois quando o usuário quiser praticar só um."""
    if origem is not None and origem not in ("enem_oficial", "banco_pratica"):
        raise ValueError(f"origem inválida: '{origem}'")
    grande_area_norm = normalizar_texto(grande_area)
    materia_norm = normalizar_texto(materia)
    clausula_origem = "AND origem = ?" if origem else ""
    parametros = (grande_area_norm, materia_norm) + ((origem,) if origem else ())
    with _conectar() as conn:
        linhas = conn.execute(
            f"""
            SELECT {_COLUNAS_QUESTAO_GRADE}
            FROM questoes
            WHERE grande_area = ? AND materia = ? AND status_classificacao = 'classificado' {clausula_origem}
            ORDER BY ano DESC, numero_questao
            """,
            parametros,
        ).fetchall()
    return [_linha_para_questao_grade(r) for r in linhas]


def atualizar_enunciado(id_questao: str, texto: str | None = None, imagem_path: str | None = None) -> None:
    """Atualiza só o enunciado (texto e/ou imagem) de uma questão que
    já existe -- não mexe em matéria, gabarito nem status, então não
    passa por inserir_questao()/historico_alteracoes (não é uma
    correção de conteúdo classificatório, é só anexar o enunciado que
    faltava). Passar None num campo mantém o valor atual (COALESCE)."""
    with _conectar() as conn:
        existe = conn.execute("SELECT 1 FROM questoes WHERE id_questao = ?", (id_questao,)).fetchone()
        if not existe:
            raise ValueError(f"Questão '{id_questao}' não existe.")
        conn.execute(
            """
            UPDATE questoes SET
                enunciado_texto = COALESCE(?, enunciado_texto),
                enunciado_imagem_path = COALESCE(?, enunciado_imagem_path)
            WHERE id_questao = ?
            """,
            (texto, imagem_path, id_questao),
        )


def atualizar_topico(id_questao: str, topico: str | None) -> None:
    """Marca (ou limpa, com topico=None) o padrão de cobrança de uma
    questão que já existe, sem mexer em matéria/gabarito/status -- por
    isso não passa por inserir_questao()/historico_alteracoes, mesma
    lógica de atualizar_enunciado() acima.

    topico é texto livre, não uma taxonomia fechada como materia: é o
    campo mínimo pra testar a hipótese (ainda não validada) de que
    repetição concentrada num padrão específico de cobrança da banca
    -- não só na matéria inteira -- é o que ensina o aluno a reconhecer
    o distrator típico daquele padrão. Ver desempenho_por_topico()."""
    with _conectar() as conn:
        existe = conn.execute("SELECT 1 FROM questoes WHERE id_questao = ?", (id_questao,)).fetchone()
        if not existe:
            raise ValueError(f"Questão '{id_questao}' não existe.")
        conn.execute(
            "UPDATE questoes SET topico = ? WHERE id_questao = ?",
            (topico.strip() if topico else None, id_questao),
        )


def prioridade_de_estudo(grande_area: str, peso_recorrencia: float = 0.5) -> dict:
    """Cruza recorrência (recorrencia_por_materia) com desempenho
    (taxa_acerto_por_materia) num ranking único de prioridade de
    estudo: score = peso_recorrencia * %recorrência + (1 - peso) * %erro.
    Quanto mais a matéria cai E mais você erra nela, maior o score.

    Matéria recorrente que você nunca tentou responder vai pra
    'sem_dados', separada do ranking numérico — calcular um score de
    desempenho sem nenhuma tentativa seria inventar confiança que não
    existe, o mesmo erro que já corrigimos na tabela de probabilidade
    do sistema antigo. Aparece como aviso, não como número no ranking.
    """
    recorrencia = {r["materia"]: r for r in recorrencia_por_materia(grande_area)}
    desempenho = {d["materia"]: d for d in taxa_acerto_por_materia(grande_area)}

    ranking, sem_dados = [], []

    for materia, r in recorrencia.items():
        d = desempenho.get(materia)
        if d is None:
            sem_dados.append({"materia": materia, "percentual_recorrencia": r["percentual"]})
            continue

        taxa_erro_pct = 100 - d["taxa_acerto"] * 100
        score = peso_recorrencia * r["percentual"] + (1 - peso_recorrencia) * taxa_erro_pct

        ranking.append({
            "materia": materia,
            "percentual_recorrencia": r["percentual"],
            "taxa_acerto_pct": round(d["taxa_acerto"] * 100, 1),
            "total_tentativas": d["total_tentativas"],
            "amostra_pequena": d["total_tentativas"] < MIN_AMOSTRA_CONFIAVEL,
            "score_prioridade": round(score, 1),
            # Camada de explicabilidade: os dois termos que somam pro score
            # acima, já calculados -- pra UI poder responder "por que essa
            # prioridade" mostrando a conta em vez de só o número final.
            # Chave nova, não quebra nenhum caller que só lia as chaves de
            # cima (reconstruir_base.py incluso).
            "explicacao": {
                "peso_recorrencia": peso_recorrencia,
                "contribuicao_recorrencia": round(peso_recorrencia * r["percentual"], 1),
                "contribuicao_taxa_erro": round((1 - peso_recorrencia) * taxa_erro_pct, 1),
            },
        })

    ranking.sort(key=lambda x: x["score_prioridade"], reverse=True)
    sem_dados.sort(key=lambda x: x["percentual_recorrencia"], reverse=True)
    return {"ranking": ranking, "sem_dados": sem_dados}


# ============================================================
# CONFIANÇA RECENTE (recência, separado de taxa de acerto acumulada)
# ============================================================

LIMIAR_CONFIANCA_ALTA = 0.8   # >= 80% das últimas tentativas certas
LIMIAR_CONFIANCA_BAIXA = 0.2  # <= 20% das últimas tentativas certas -- entre os dois, "media"


def confianca_recente_por_materia(grande_area: str, janela: int = 5) -> list[dict]:
    """Complementa taxa_acerto_por_materia() (média histórica, desde
    sempre) com um sinal de RECÊNCIA: como foram as últimas `janela`
    tentativas de cada matéria, não a média acumulada inteira. Existe pra
    separar dois perfis que uma taxa de acerto sozinha não distingue --
    50% de acerto esconde tanto "sempre errei, últimas 5 eu acertei 4"
    quanto "sempre acertei, últimas 5 eu errei 4"; olhar só a média
    histórica trata os dois como o mesmo caso, quando o segundo é
    claramente mais urgente.

    Mesma regra de sempre: só questão 'classificado' entra. `janela` é o
    tamanho da amostra recente considerada (padrão 5, sem justificativa
    estatística formal por trás do número — é "o suficiente pra ver um
    padrão sem exigir tanto dado que a matéria nunca acumule confiança
    nenhuma", mesmo espírito de MIN_AMOSTRA_CONFIAVEL).
    """
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT q.materia, t.resultado
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.status_classificacao = 'classificado' AND q.grande_area = ?
            ORDER BY q.materia, t.data_tentativa
            """,
            (grande_area_norm,),
        ).fetchall()

    por_materia: dict[str, list[str]] = {}
    for materia, resultado in linhas:
        por_materia.setdefault(materia, []).append(resultado)

    ordem_confianca = {"baixa": 0, "media": 1, "alta": 2}
    resultado_final = []
    for materia, historico in por_materia.items():
        recentes = historico[-janela:]
        acertos_recentes = recentes.count("acertou")
        fracao = acertos_recentes / len(recentes)
        if fracao >= LIMIAR_CONFIANCA_ALTA:
            confianca = "alta"
        elif fracao <= LIMIAR_CONFIANCA_BAIXA:
            confianca = "baixa"
        else:
            confianca = "media"
        resultado_final.append({
            "materia": materia,
            "sequencia_recente": ["✓" if r == "acertou" else "✗" for r in recentes],
            "acertos_recentes": acertos_recentes,
            "tentativas_consideradas": len(recentes),
            "confianca": confianca,
            "amostra_pequena": len(historico) < janela,
        })

    resultado_final.sort(key=lambda r: (ordem_confianca[r["confianca"]], r["materia"]))
    return resultado_final


# ============================================================
# EVOLUÇÃO SEMANAL (tendência, não só o placar de hoje)
# ============================================================

LIMIAR_ESTAGNACAO_PCT = 60.0  # abaixo disso E parado, vale sinalizar; parado em 95% não é problema


def evolucao_semanal_por_materia(grande_area: str, n_semanas: int = 4) -> dict:
    """Compara a metade mais ANTIGA contra a metade mais RECENTE das
    últimas `n_semanas` com atividade real na área (não semana de
    calendário vazia -- se você não estudou numa semana, ela simplesmente
    não conta como uma das N). Metade a metade em vez de só o primeiro e o
    último ponto isolados, porque uma única semana com pouquíssima
    tentativa sozinha seria ruído demais pra virar "tendência".

    Só entra na comparação de uma matéria quem tem tentativa nas DUAS
    metades -- sem isso, "caiu de 100% pra 0%" às vezes seria só ausência
    de dado numa metade, não piora de verdade.

    Devolve as 3 leituras que a UI mostra prontas: maior_evolucao (maior
    ganho positivo), maior_risco (maior queda), estagnado (menor variação
    entre quem ainda está abaixo de LIMIAR_ESTAGNACAO_PCT — parado longe
    do topo é o caso que precisa de atenção; parado já dominando não).
    Qualquer um dos três pode vir None se não houver candidato real.
    """
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT strftime('%Y-%W', t.data_tentativa) AS semana, q.materia, t.resultado
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.status_classificacao = 'classificado' AND q.grande_area = ?
            ORDER BY t.data_tentativa
            """,
            (grande_area_norm,),
        ).fetchall()

    vazio = {"semanas": [], "por_materia": {}, "maior_evolucao": None, "maior_risco": None, "estagnado": None}
    if not linhas:
        return vazio

    semanas_ordenadas = sorted({semana for semana, _, _ in linhas})
    janela = semanas_ordenadas[-n_semanas:]
    if len(janela) < 2:
        # não dá pra comparar "antes x depois" com só 1 semana de atividade
        return {**vazio, "semanas": janela}

    corte = len(janela) // 2
    metade_1 = set(janela[:corte])
    metade_2 = set(janela[corte:])

    stats: dict[str, dict[str, list[int]]] = {}
    for semana, materia, resultado in linhas:
        if semana not in janela:
            continue
        chave_metade = "m1" if semana in metade_1 else "m2"
        registro = stats.setdefault(materia, {"m1": [0, 0], "m2": [0, 0]})
        registro[chave_metade][0] += 1
        if resultado == "acertou":
            registro[chave_metade][1] += 1

    por_materia = {}
    candidatos_delta = []
    for materia, r in stats.items():
        total_1, acertos_1 = r["m1"]
        total_2, acertos_2 = r["m2"]
        entrada = {
            "inicio_pct": round(acertos_1 / total_1 * 100, 1) if total_1 else None,
            "fim_pct": round(acertos_2 / total_2 * 100, 1) if total_2 else None,
            "total_inicio": total_1,
            "total_fim": total_2,
        }
        por_materia[materia] = entrada
        if total_1 and total_2:
            delta = entrada["fim_pct"] - entrada["inicio_pct"]
            candidatos_delta.append((materia, delta, entrada))

    # As 3 chamadas de destaque só saem de candidato com amostra confiável
    # NAS DUAS metades (mesmo MIN_AMOSTRA_CONFIAVEL usado em todo o resto
    # do arquivo) -- sem esse filtro, um 1-vs-1 (1 tentativa errada numa
    # semana, 1 certa na outra) sempre "vence" como maior evolução/risco,
    # porque delta de amostra minúscula é sempre o mais extremo possível
    # (0% ou 100%). `por_materia` continua com TODO mundo, filtrado ou não
    # -- é só o destaque que precisa de confiança, a tabela completa não.
    candidatos_confiaveis = [
        c for c in candidatos_delta
        if c[2]["total_inicio"] >= MIN_AMOSTRA_CONFIAVEL and c[2]["total_fim"] >= MIN_AMOSTRA_CONFIAVEL
    ]

    maior_evolucao = maior_risco = estagnado = None
    if candidatos_confiaveis:
        materia_evo, delta_evo, entrada_evo = max(candidatos_confiaveis, key=lambda c: c[1])
        if delta_evo > 0:
            maior_evolucao = {"materia": materia_evo, "delta_pct": round(delta_evo, 1), **entrada_evo}

        materia_risco, delta_risco, entrada_risco = min(candidatos_confiaveis, key=lambda c: c[1])
        if delta_risco < 0:
            maior_risco = {"materia": materia_risco, "delta_pct": round(delta_risco, 1), **entrada_risco}

        estagnados = [c for c in candidatos_confiaveis if c[2]["fim_pct"] < LIMIAR_ESTAGNACAO_PCT]
        if estagnados:
            materia_estag, delta_estag, entrada_estag = min(estagnados, key=lambda c: abs(c[1]))
            estagnado = {"materia": materia_estag, "delta_pct": round(delta_estag, 1), **entrada_estag}

    return {
        "semanas": janela, "por_materia": por_materia,
        "maior_evolucao": maior_evolucao, "maior_risco": maior_risco, "estagnado": estagnado,
    }


# ============================================================
# PLANO DE ESTUDO (motor de decisão: transforma prioridade em tempo)
# ============================================================

MINUTOS_TOTAIS_PADRAO = 120
MINUTOS_POR_QUESTAO_REVISAO = 2   # revisão Leitner é reconhecimento rápido, não resolução do zero
MINUTOS_POR_QUESTAO_PRATICA = 3   # prática nova/prioritária demora mais que revisão
FRACAO_REVISAO_VENCIDA = 0.25     # teto do tempo total reservado pra fila atrasada
FRACAO_FOCO_FRAQUEZA = 0.20       # teto do tempo total reservado pro bloco de foco isolado
MINUTOS_REDACAO_SUGERIDO = 20
DIAS_SEM_REDACAO_PARA_SUGERIR = 7


def _dias_desde_ultima_redacao() -> int | None:
    """None se nenhuma redação foi registrada ainda -- usado só por
    gerar_plano_de_estudo() pra decidir se sugere um bloco de redação."""
    redacoes = listar_redacoes()
    if not redacoes:
        return None
    ultima = date.fromisoformat(redacoes[0]["data_escrita"])
    return (date.today() - ultima).days


def _tipo_erro_predominante(grande_area: str, materia: str) -> str | None:
    """O tipo_erro mais frequente pra uma matéria específica, via
    analise_por_tipo_erro() -- usado só pra explicar o bloco de foco do
    plano de estudo (dá pra dizer POR QUE focar, não só QUANTO tempo).
    None sem dado suficiente, pra não inventar um motivo que não existe."""
    por_erro = [r for r in analise_por_tipo_erro(grande_area) if r["materia"] == materia]
    if not por_erro:
        return None
    return max(por_erro, key=lambda r: r["quantidade"])["tipo_erro"]


def gerar_plano_de_estudo(minutos_totais: int = MINUTOS_TOTAIS_PADRAO) -> dict:
    """Divide minutos_totais em blocos de estudo, nesta ordem: revisões
    vencidas (Leitner, sensível a tempo -- quanto mais atrasa, mais a
    memória decai) -> prática geral por área (mais tempo pra área onde
    você mais erra) -> foco isolado na matéria de maior prioridade de
    qualquer área -> redação, se estiver atrasada.

    Todo bloco carrega um "motivo" em texto -- é a camada de
    explicabilidade do plano: nenhum bloco aparece só dizendo QUANTO
    tempo, sempre também POR QUE esse tempo foi pra ali. O bloco de foco
    ainda cita o tipo de erro predominante quando existe dado (ver
    _tipo_erro_predominante()) -- "maioria erro de conteúdo" pede Modo
    Aula Base antes de mais questão; "maioria erro de conta/pegadinha"
    pede só mais prática cronometrada, é uma orientação bem diferente pro
    mesmo score de prioridade, e o campo `tipo_erro` já existia no banco
    sem nenhuma função de planejamento usar ele até agora.

    Não persiste nada -- recalculado do zero a cada chamada, igual toda
    outra função analítica de db.py, então reflete a tentativa mais
    recente sem precisar de um botão de "recalcular". `minutos_alocados`
    no retorno pode ser menor que `minutos_totais` quando não há dado
    suficiente pra preencher tudo (ex: banco vazio) -- reportado explícito
    em vez de forçar um bloco a esticar pra fechar a conta.
    """
    if minutos_totais <= 0:
        raise ValueError("minutos_totais precisa ser positivo.")

    blocos_iniciais = []
    blocos_area = []
    bloco_foco = None
    bloco_redacao = None
    restante = minutos_totais

    # 1. Revisões vencidas
    fila_revisao = questoes_para_revisar()
    if fila_revisao and restante > 0:
        minutos_necessarios = len(fila_revisao) * MINUTOS_POR_QUESTAO_REVISAO
        minutos_bloco = min(minutos_necessarios, round(minutos_totais * FRACAO_REVISAO_VENCIDA), restante)
        if minutos_bloco > 0:
            blocos_iniciais.append({
                "titulo": "Revisões vencidas",
                "minutos": minutos_bloco,
                "questoes_sugeridas": max(1, minutos_bloco // MINUTOS_POR_QUESTAO_REVISAO),
                "motivo": (
                    f"{len(fila_revisao)} questão(ões) já passaram da data de revisão (Leitner) -- "
                    "quanto mais atrasa, mais a memória decai."
                ),
            })
            restante -= minutos_bloco

    # 2. Foco isolado na maior fraqueza (uma matéria só, de qualquer área)
    candidatos_foco = []
    for area in ("matematica", "ciencias_natureza"):
        ranking = prioridade_de_estudo(area)["ranking"]
        if ranking:
            candidatos_foco.append((area, ranking[0]))
    if candidatos_foco and restante > 0:
        area_foco, materia_foco = max(candidatos_foco, key=lambda par: par[1]["score_prioridade"])
        minutos_bloco = min(round(minutos_totais * FRACAO_FOCO_FRAQUEZA), restante)
        if minutos_bloco > 0:
            motivo = (
                f"prioridade {materia_foco['score_prioridade']}/100 "
                f"({materia_foco['percentual_recorrencia']}% de recorrência x "
                f"{materia_foco['taxa_acerto_pct']}% de acerto)."
            )
            tipo_erro_top = _tipo_erro_predominante(area_foco, materia_foco["materia"])
            if tipo_erro_top:
                motivo += f" Maioria dos erros classificados aqui: {TIPOS_ERRO[tipo_erro_top].lower()}."
                if tipo_erro_top == "erro_de_conteudo":
                    motivo += " Sinal de lacuna de base -- Modo Aula Base antes de mais questão."
            bloco_foco = {
                "titulo": f"Foco na maior fraqueza — {materia_foco['materia']}",
                "area": area_foco,
                "materia": materia_foco["materia"],
                "minutos": minutos_bloco,
                "motivo": motivo,
            }
            restante -= minutos_bloco

    # 3. Redação, se atrasada (ou nunca escrita)
    dias_redacao = _dias_desde_ultima_redacao()
    redacao_devida = dias_redacao is None or dias_redacao >= DIAS_SEM_REDACAO_PARA_SUGERIR
    if redacao_devida and restante > 0:
        minutos_bloco = min(MINUTOS_REDACAO_SUGERIDO, restante)
        if minutos_bloco > 0:
            motivo = (
                "nenhuma redação registrada ainda." if dias_redacao is None
                else f"{dias_redacao} dias desde a última redação registrada."
            )
            bloco_redacao = {"titulo": "Redação", "minutos": minutos_bloco, "motivo": motivo}
            restante -= minutos_bloco

    # 4. O que sobrar: prática geral, dividida entre as áreas proporcional
    # a qual delas você mais erra (mais erro = mais tempo) -- só entre
    # área que já tem tentativa suficiente pra medir isso.
    if restante > 0:
        pesos_erro = {}
        for area in ("matematica", "ciencias_natureza"):
            desempenho = taxa_acerto_por_materia(area)
            total = sum(d["total_tentativas"] for d in desempenho)
            acertos = sum(d["acertos"] for d in desempenho)
            if total > 0:
                pesos_erro[area] = 100 - (acertos / total * 100)
        soma_pesos = sum(pesos_erro.values())
        for area, peso in pesos_erro.items():
            fracao = (peso / soma_pesos) if soma_pesos else (1 / len(pesos_erro))
            minutos_bloco = round(restante * fracao)
            if minutos_bloco <= 0:
                continue
            materias_sugeridas = [r["materia"] for r in prioridade_de_estudo(area)["ranking"][:2]]
            blocos_area.append({
                "titulo": "Prática geral",
                "area": area,
                "minutos": minutos_bloco,
                "questoes_sugeridas": max(1, minutos_bloco // MINUTOS_POR_QUESTAO_PRATICA),
                "materias_sugeridas": materias_sugeridas,
                "motivo": (
                    f"{round(peso)}% de taxa de erro geral na área -- prioridades do momento: "
                    + (", ".join(materias_sugeridas) or "sem dado suficiente ainda") + "."
                ),
            })

    blocos = blocos_iniciais + blocos_area
    if bloco_foco:
        blocos.append(bloco_foco)
    if bloco_redacao:
        blocos.append(bloco_redacao)

    return {
        "minutos_totais": minutos_totais,
        "minutos_alocados": sum(b["minutos"] for b in blocos),
        "blocos": blocos,
    }


def questoes_para_revisar(hoje: date | None = None) -> list[str]:
    """IDs de questão cuja proxima_revisao já chegou — a fila do dia,
    estilo Anki. Só cobre questões já tentadas ao menos uma vez."""
    hoje = hoje or date.today()
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT id_questao FROM estado_revisao WHERE proxima_revisao <= ? ORDER BY proxima_revisao",
            (hoje.isoformat(),),
        ).fetchall()
    return [linha[0] for linha in linhas]


def taxa_acerto_por_materia(grande_area: str) -> list[dict]:
    """Base direta pro insight 'você erra fácil de matéria X': taxa
    de acerto agregada por matéria, usando só tentativas reais
    (tabela append-only), não opinião de vídeo nenhuma.

    Filtra por grande_area de propósito -- misturar 'geometria_plana'
    (matemática) com 'fisica' (ciências) no mesmo ranking não ajuda
    ninguém a decidir o que estudar.

    Só considera questões com status_classificacao='classificado' —
    misturar tentativas de questões 'nao_classificado' (materia é só
    um placeholder tipo 'sem_video_pendente') faria elas aparecerem
    como se fosse uma matéria de verdade, escondendo exatamente o
    dado que mais precisa de atenção. Use
    tentativas_pendentes_classificacao() pra ver o que fica de fora."""
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT q.materia,
                   COUNT(*) AS total_tentativas,
                   SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END) AS acertos
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.status_classificacao = 'classificado' AND q.grande_area = ?
            GROUP BY q.materia
            ORDER BY (CAST(acertos AS REAL) / total_tentativas) ASC
            """,
            (grande_area_norm,),
        ).fetchall()
    return [
        {
            "materia": materia,
            "total_tentativas": total,
            "acertos": acertos,
            "taxa_acerto": round(acertos / total, 3) if total else None,
        }
        for materia, total, acertos in linhas
    ]


def desempenho_por_topico(grande_area: str, materia: str) -> dict:
    """Um nível abaixo de taxa_acerto_por_materia(): taxa de acerto
    agrupada por questoes.topico DENTRO de uma matéria já escolhida --
    o experimento mínimo pra testar a hipótese (ainda não validada, ver
    Central ENEM GI, seção 'Hipótese central de produto') de que
    repetição concentrada num padrão específico de cobrança da banca
    ensina mais do que praticar a matéria inteira sem foco.

    topico é texto livre (marcado à mão via atualizar_topico(), ou na
    hora de inserir a questão) -- não é uma taxonomia fechada como
    materia, então não passa por canonicalizar_materia() nem por
    TAXONOMIA_VALIDA. Duas grafias diferentes do "mesmo" padrão
    aparecem como duas entradas distintas; isso é uma limitação
    conhecida, não um bug -- normalizar automaticamente inventaria uma
    correspondência que ninguém validou.

    Questão sem topico marcado entra em 'sem_topico', fora do ranking
    -- mesmo princípio do sem_dados em prioridade_de_estudo(): não
    inventa um padrão que ninguém etiquetou ainda."""
    grande_area_norm = normalizar_texto(grande_area)
    materia_norm = canonicalizar_materia(normalizar_texto(materia))
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT q.topico,
                   COUNT(*) AS total_tentativas,
                   SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END) AS acertos
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.grande_area = ? AND q.materia = ?
            GROUP BY q.topico
            """,
            (grande_area_norm, materia_norm),
        ).fetchall()

    ranking, sem_topico = [], None
    for topico, total, acertos in linhas:
        entrada = {
            "topico": topico,
            "total_tentativas": total,
            "acertos": acertos,
            "taxa_acerto": round(acertos / total, 3) if total else None,
            "amostra_pequena": total < MIN_AMOSTRA_CONFIAVEL,
        }
        if topico is None:
            sem_topico = entrada
        else:
            ranking.append(entrada)

    ranking.sort(key=lambda r: r["taxa_acerto"])
    return {"materia": materia_norm, "ranking": ranking, "sem_topico": sem_topico}


def explorar_materias(grande_area: str) -> list[dict]:
    """Lista TODAS as matérias válidas da área (não só as que já têm
    tentativa, diferente de taxa_acerto_por_materia) com contagem de
    questões disponíveis (ENEM oficial + banco de prática somados) e
    taxa de acerto -- base da tela "Explore" do app, que precisa
    mostrar toda matéria da taxonomia, inclusive a que ainda não foi
    praticada nenhuma vez (taxa_acerto None, total_questoes podendo
    ser 0 -- é esse total_questoes==0 que a tela usa pra marcar a
    matéria como bloqueada, não uma condição de progresso)."""
    grande_area_norm = normalizar_texto(grande_area)
    materias = materias_validas(grande_area_norm)
    with _conectar() as conn:
        contagens = dict(conn.execute(
            "SELECT materia, COUNT(*) FROM questoes WHERE grande_area = ? GROUP BY materia",
            (grande_area_norm,),
        ).fetchall())
        taxas = {
            materia: (total, acertos)
            for materia, total, acertos in conn.execute(
                """
                SELECT q.materia, COUNT(*), SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END)
                FROM tentativas_usuario t
                JOIN questoes q ON q.id_questao = t.id_questao
                WHERE q.grande_area = ?
                GROUP BY q.materia
                """,
                (grande_area_norm,),
            ).fetchall()
        }
    return [
        {
            "materia": materia,
            "total_questoes": contagens.get(materia, 0),
            "total_tentativas": taxas.get(materia, (0, 0))[0],
            "taxa_acerto": round(taxas[materia][1] / taxas[materia][0], 3) if taxas.get(materia, (0,))[0] else None,
        }
        for materia in materias
    ]


def resumo_geral_desempenho() -> dict:
    """Taxa de acerto geral, agregando TODAS as tentativas — inclusive
    as de questão ainda não classificada por matéria. Não depende de
    taxonomia nenhuma, então funciona mesmo quando 100% das questões
    tentadas ainda estão pendentes de classificação (ex: uma prova
    inteira sem fonte de matéria disponível, como 2019 hoje)."""
    with _conectar() as conn:
        linha = conn.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN resultado='acertou' THEN 1 ELSE 0 END)
            FROM tentativas_usuario
            """
        ).fetchone()
    total, acertos = linha[0], linha[1] or 0
    return {
        "total_tentativas": total,
        "acertos": acertos,
        "taxa_acerto": round(acertos / total, 3) if total else None,
    }


def tentativas_pendentes_classificacao() -> dict:
    """Quantas tentativas reais existem em questões ainda
    'nao_classificado' — o que taxa_acerto_por_materia() está
    deixando de fora do ranking por matéria, pra não ficar escondido
    silenciosamente."""
    with _conectar() as conn:
        linha = conn.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN t.resultado='acertou' THEN 1 ELSE 0 END)
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.status_classificacao = 'nao_classificado'
            """
        ).fetchone()
    total, acertos = linha[0] or 0, linha[1] or 0
    return {"total_tentativas": total, "acertos": acertos}


def resolucoes_da_questao(id_questao: str) -> list[dict]:
    """Resoluções (vídeo e/ou texto) ligadas a uma questão — usado pra
    mostrar o vídeo de explicação assim que o usuário erra no
    cartão-resposta, sem precisar procurar em outro lugar."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT id_resolucao, tipo, conteudo, canal FROM resolucoes WHERE id_questao = ? ORDER BY criado_em",
            (id_questao,),
        ).fetchall()
    return [{"id_resolucao": r[0], "tipo": r[1], "conteudo": r[2], "canal": r[3]} for r in linhas]


def apagar_resolucao(id_resolucao: int) -> None:
    """Remove UMA resolução (vídeo ou texto) -- pra tirar um link
    errado/quebrado ligado à questão errada, sem precisar apagar a
    questão inteira."""
    with _conectar() as conn:
        conn.execute("DELETE FROM resolucoes WHERE id_resolucao = ?", (id_resolucao,))


def editar_resolucao(id_resolucao: int, conteudo: str, canal: str | None = None) -> None:
    """Corrige o link/texto (e opcionalmente o canal) de uma resolução
    já ligada, mantendo o mesmo id_resolucao -- pra quando o link
    certo aparece depois ou foi digitado errado, sem apagar e
    recriar."""
    conteudo = conteudo.strip()
    if not conteudo:
        raise ValueError("conteudo não pode ser vazio.")
    with _conectar() as conn:
        existe = conn.execute(
            "SELECT 1 FROM resolucoes WHERE id_resolucao = ?", (id_resolucao,)
        ).fetchone()
        if not existe:
            raise ValueError(f"Resolução '{id_resolucao}' não existe.")
        conn.execute(
            "UPDATE resolucoes SET conteudo=?, canal=? WHERE id_resolucao=?",
            (conteudo, canal or None, id_resolucao),
        )


def reportar_questao(id_questao: str, comentario: str) -> int:
    """Registra um relato ('acho que o gabarito está errado', 'falta
    a figura', 'alternativa ambígua' etc.) pra uma questão -- botão de
    reportar do app mobile, pensado pra Gabriel acumular sinal
    enquanto valida o banco pergunta por pergunta, sem precisar parar
    o fluxo de resolver questão pra corrigir na hora. Retorna
    id_relato pra quem chamar poder confirmar que gravou."""
    comentario = comentario.strip()
    if not comentario:
        raise ValueError("comentario não pode ser vazio.")
    with _conectar() as conn:
        existe = conn.execute("SELECT 1 FROM questoes WHERE id_questao = ?", (id_questao,)).fetchone()
        if not existe:
            raise ValueError(f"Questão '{id_questao}' não existe.")
        cursor = conn.execute(
            "INSERT INTO relatos_questao (id_questao, comentario) VALUES (?, ?)",
            (id_questao, comentario),
        )
        return cursor.lastrowid


def listar_relatos_questao(resolvido: bool | None = None) -> list[dict]:
    """Relatos mais recentes primeiro -- alimenta uma futura tela de
    revisão em lote no Admin. `resolvido=None` traz tudo; True/False
    filtra só um dos dois estados."""
    query = (
        "SELECT r.id_relato, r.id_questao, r.comentario, r.resolvido, r.criado_em, "
        "q.enunciado_texto, q.materia "
        "FROM relatos_questao r JOIN questoes q ON q.id_questao = r.id_questao"
    )
    parametros: tuple = ()
    if resolvido is not None:
        query += " WHERE r.resolvido = ?"
        parametros = (1 if resolvido else 0,)
    query += " ORDER BY r.criado_em DESC"
    with _conectar() as conn:
        linhas = conn.execute(query, parametros).fetchall()
    return [
        {
            "id_relato": r[0], "id_questao": r[1], "comentario": r[2],
            "resolvido": bool(r[3]), "criado_em": r[4],
            "enunciado_texto": r[5], "materia": r[6],
        }
        for r in linhas
    ]


def marcar_relato_resolvido(id_relato: int, resolvido: bool = True) -> None:
    """Marca (ou desmarca) um relato como já revisado, sem apagar o
    histórico -- pra Gabriel riscar da lista de pendências depois de
    corrigir a questão."""
    with _conectar() as conn:
        conn.execute(
            "UPDATE relatos_questao SET resolvido = ? WHERE id_relato = ?",
            (1 if resolvido else 0, id_relato),
        )


def reclassificar_pendentes() -> dict:
    """Reaplica SINONIMOS_MATERIA + TAXONOMIA_VALIDA em cima das
    questões já gravadas como 'nao_classificado' -- sem tocar em vídeo
    nenhum. Necessário porque adicionar um sinônimo novo no código não
    reclassifica sozinho o que já está no banco; essa função é o
    'reprocessa com a régua atual' pra rodar depois de qualquer
    atualização de taxonomia."""
    pendentes = questoes_pendentes_classificacao()
    reclassificadas, continuam = 0, 0

    for q in pendentes:
        materia_norm = canonicalizar_materia(q["materia_bruta"])
        if (q["grande_area"], materia_norm) in TAXONOMIA_VALIDA:
            with _conectar() as conn:
                conn.execute(
                    "UPDATE questoes SET materia = ?, status_classificacao = 'classificado' "
                    "WHERE id_questao = ?",
                    (materia_norm, q["id_questao"]),
                )
            reclassificadas += 1
        else:
            continuam += 1

    return {"reclassificadas": reclassificadas, "continuam_pendentes": continuam}


def historico_alteracoes(id_questao: str | None = None) -> list[dict]:
    """Log de auditoria: toda vez que gabarito ou matéria de uma
    questão foi corrigido depois de já existir, fica aqui -- incluindo
    quantas tentativas tiveram o resultado recalculado por causa
    disso. Sem filtro, devolve tudo; com id_questao, só daquela."""
    with _conectar() as conn:
        if id_questao:
            linhas = conn.execute(
                "SELECT id_questao, campo, valor_antigo, valor_novo, data_alteracao, tentativas_recalculadas "
                "FROM historico_alteracoes WHERE id_questao = ? ORDER BY data_alteracao DESC",
                (id_questao,),
            ).fetchall()
        else:
            linhas = conn.execute(
                "SELECT id_questao, campo, valor_antigo, valor_novo, data_alteracao, tentativas_recalculadas "
                "FROM historico_alteracoes ORDER BY data_alteracao DESC"
            ).fetchall()
    return [
        {
            "id_questao": r[0], "campo": r[1], "valor_antigo": r[2], "valor_novo": r[3],
            "data_alteracao": r[4], "tentativas_recalculadas": r[5],
        }
        for r in linhas
    ]


def apagar_prova(ano: int, caderno: str, grande_area: str) -> dict:
    """Remove uma prova inteira (todas as questões de um ano+caderno+
    grande_area) e tudo que depende dela: tentativas_usuario,
    estado_revisao, resolucoes. Não usa FOREIGN KEY CASCADE de
    propósito -- apaga explicitamente em cada tabela, pra funcionar
    mesmo se o schema não tiver cascade configurado. Usado pra
    limpar carga acidental (ex: CSV colado no ano/caderno errado).

    Loga cada questão apagada em historico_alteracoes (campo
    'questao_apagada') antes de remover, pra manter rastro do que
    existia -- irreversível depois disso, então o chamador deve
    confirmar antes."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)

    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT id_questao, materia, alternativa_correta FROM questoes "
            "WHERE ano = ? AND caderno = ? AND grande_area = ?",
            (ano, caderno_norm, grande_area_norm),
        ).fetchall()

        if not linhas:
            return {"apagadas": 0, "tentativas_perdidas": 0, "resolucoes_perdidas": 0}

        ids = [linha[0] for linha in linhas]
        marcadores = ",".join("?" * len(ids))

        for id_questao, materia, gabarito in linhas:
            conn.execute(
                "INSERT INTO historico_alteracoes (id_questao, campo, valor_antigo, valor_novo) "
                "VALUES (?,?,?,?)",
                (id_questao, "questao_apagada", f"{materia}/{gabarito}", "DELETADO"),
            )

        n_tentativas = conn.execute(
            f"DELETE FROM tentativas_usuario WHERE id_questao IN ({marcadores})", ids
        ).rowcount
        conn.execute(f"DELETE FROM estado_revisao WHERE id_questao IN ({marcadores})", ids)
        n_resolucoes = conn.execute(
            f"DELETE FROM resolucoes WHERE id_questao IN ({marcadores})", ids
        ).rowcount
        conn.execute(f"DELETE FROM questoes WHERE id_questao IN ({marcadores})", ids)

    return {
        "apagadas": len(ids),
        "tentativas_perdidas": n_tentativas,
        "resolucoes_perdidas": n_resolucoes,
    }


def detalhe_questao(id_questao: str) -> dict | None:
    """Ficha completa de UMA questão (ano, caderno, número, área,
    matéria, gabarito, status, enunciado) -- base pra editar/apagar uma
    questão específica no Admin, fora do fluxo de Triagem (que só cobre
    questão ainda nao_classificado), e pra scripts de extração de
    enunciado saberem se já existe algo gravado antes de sobrescrever."""
    with _conectar() as conn:
        linha = conn.execute(
            "SELECT ano, caderno, numero_questao, grande_area, materia, "
            "alternativa_correta, status_classificacao, enunciado_texto, "
            "enunciado_imagem_path, topico FROM questoes WHERE id_questao = ?",
            (id_questao,),
        ).fetchone()
    if linha is None:
        return None
    return {
        "id_questao": id_questao, "ano": linha[0], "caderno": linha[1],
        "numero_questao": linha[2], "grande_area": linha[3], "materia": linha[4],
        "alternativa_correta": linha[5], "status_classificacao": linha[6],
        "enunciado_texto": linha[7], "enunciado_imagem_path": linha[8],
        "topico": linha[9],
    }


def apagar_questao(id_questao: str) -> dict:
    """Remove UMA questão só (não a prova inteira) e tudo que depende
    dela -- mesma lógica de apagar_prova(), só que filtrando por um
    único id_questao. Pensada pra corrigir um CSV colado com uma linha
    extra/errada (numero digitado errado, por exemplo) sem precisar
    apagar as outras 44 questões certas da mesma prova junto."""
    with _conectar() as conn:
        linha = conn.execute(
            "SELECT materia, alternativa_correta FROM questoes WHERE id_questao = ?", (id_questao,)
        ).fetchone()
        if linha is None:
            return {"apagada": False, "tentativas_perdidas": 0, "resolucoes_perdidas": 0}

        materia, gabarito = linha
        conn.execute(
            "INSERT INTO historico_alteracoes (id_questao, campo, valor_antigo, valor_novo) VALUES (?,?,?,?)",
            (id_questao, "questao_apagada", f"{materia}/{gabarito}", "DELETADO"),
        )
        n_tentativas = conn.execute(
            "DELETE FROM tentativas_usuario WHERE id_questao = ?", (id_questao,)
        ).rowcount
        conn.execute("DELETE FROM estado_revisao WHERE id_questao = ?", (id_questao,))
        n_resolucoes = conn.execute(
            "DELETE FROM resolucoes WHERE id_questao = ?", (id_questao,)
        ).rowcount
        conn.execute("DELETE FROM questoes WHERE id_questao = ?", (id_questao,))

    return {"apagada": True, "tentativas_perdidas": n_tentativas, "resolucoes_perdidas": n_resolucoes}


def resumo_por_tentativa(ano: int, caderno: str, grande_area: str) -> list[dict]:
    """Separa as tentativas de uma prova (ano+caderno+área) em '1ª
    vez', '2ª vez' etc, por questão -- sem precisar de tabela de
    sessão nem de rotular nada na mão. Se você responder a prova
    inteira de novo depois de já ter respondido antes, cada questão
    vira automaticamente uma 'tentativa 2' distinta da primeira, na
    ordem em que realmente aconteceu (data_tentativa)."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT numero_tentativa, COUNT(*) AS total,
                   SUM(CASE WHEN resultado='acertou' THEN 1 ELSE 0 END) AS acertos,
                   MIN(data_tentativa) AS inicio, MAX(data_tentativa) AS fim
            FROM (
                SELECT t.resultado, t.data_tentativa,
                       ROW_NUMBER() OVER (PARTITION BY t.id_questao ORDER BY t.data_tentativa) AS numero_tentativa
                FROM tentativas_usuario t
                JOIN questoes q ON q.id_questao = t.id_questao
                WHERE q.ano = ? AND q.caderno = ? AND q.grande_area = ?
            )
            GROUP BY numero_tentativa
            ORDER BY numero_tentativa
            """,
            (ano, caderno_norm, grande_area_norm),
        ).fetchall()
    return [
        {
            "tentativa": r[0], "total": r[1], "acertos": r[2],
            "taxa_acerto": round(r[2] / r[1], 3) if r[1] else None,
            "inicio": r[3], "fim": r[4],
        }
        for r in linhas
    ]


def nomear_tentativa(ano: int, caderno: str, grande_area: str, numero_tentativa: int, nome: str) -> None:
    """Dá um rótulo livre pra uma tentativa (numero_tentativa é o mesmo
    número derivado por resumo_por_tentativa() -- essa função só
    anota um nome pra ele, nunca cria/renumera tentativa nenhuma)."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        conn.execute(
            """
            INSERT INTO nomes_tentativas (ano, caderno, grande_area, numero_tentativa, nome)
            VALUES (?,?,?,?,?)
            ON CONFLICT(ano, caderno, grande_area, numero_tentativa) DO UPDATE SET nome=excluded.nome
            """,
            (ano, caderno_norm, grande_area_norm, numero_tentativa, nome.strip()),
        )


def nomes_tentativas(ano: int, caderno: str, grande_area: str) -> dict[int, str]:
    """{numero_tentativa: nome} pra uma prova -- só as que já foram
    nomeadas; tentativa sem nome simplesmente não aparece aqui."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT numero_tentativa, nome FROM nomes_tentativas WHERE ano=? AND caderno=? AND grande_area=?",
            (ano, caderno_norm, grande_area_norm),
        ).fetchall()
    return dict(linhas)


def detalhe_rodada(ano: int, caderno: str, grande_area: str, numero_tentativa: int) -> list[dict]:
    """Uma linha por questão respondida numa rodada específica --
    id_tentativa, número, o que foi marcado e o gabarito. Base pra
    editar respostas de uma rodada já registrada (a UI mostra isso
    numa grade editável e chama editar_resposta_tentativa por
    questão alterada)."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT id_tentativa, numero_questao, resposta_escolhida, resultado, alternativa_correta
            FROM (
                SELECT t.id_tentativa, q.numero_questao, t.resposta_escolhida, t.resultado,
                       q.alternativa_correta,
                       ROW_NUMBER() OVER (PARTITION BY t.id_questao ORDER BY t.data_tentativa) AS numero_tentativa
                FROM tentativas_usuario t JOIN questoes q ON q.id_questao = t.id_questao
                WHERE q.ano = ? AND q.caderno = ? AND q.grande_area = ?
            )
            WHERE numero_tentativa = ?
            ORDER BY numero_questao
            """,
            (ano, caderno_norm, grande_area_norm, numero_tentativa),
        ).fetchall()
    return [
        {
            "id_tentativa": r[0], "numero_questao": r[1], "resposta_escolhida": r[2],
            "resultado": r[3], "alternativa_correta": r[4],
        }
        for r in linhas
    ]


def simulados_feitos() -> list[dict]:
    """Toda prova (ano, caderno, grande_area) com AO MENOS uma
    tentativa registrada -- alimenta a aba 'Simulados já feitos'.
    Cada rodada de resumo_por_tentativa() já conta como uma tentativa
    distinta (responder a prova de novo depois de já ter respondido
    vira 'tentativa 2' automaticamente, sem precisar de tabela de
    sessão) -- aqui só agrupamos isso por prova e aplicamos o nome
    customizado quando existe.

    Filtra origem='enem_oficial' pelo mesmo motivo de listar_provas()
    -- tentativa em questão do banco de prática não deve virar uma
    "prova fantasma" aqui."""
    with _conectar() as conn:
        provas = conn.execute(
            "SELECT DISTINCT q.ano, q.caderno, q.grande_area "
            "FROM questoes q JOIN tentativas_usuario t ON t.id_questao = q.id_questao "
            "WHERE q.origem = 'enem_oficial' "
            "ORDER BY q.ano DESC, q.caderno, q.grande_area"
        ).fetchall()

    resultado = []
    for ano, caderno, area in provas:
        rodadas = resumo_por_tentativa(ano, caderno, area)
        nomes = nomes_tentativas(ano, caderno, area)
        for r in rodadas:
            r["nome"] = nomes.get(r["tentativa"], "")
        resultado.append({
            "ano": ano, "caderno": caderno, "grande_area": area,
            "total_questoes": questoes_totais_da_prova(ano, caderno, area),
            "rodadas": rodadas,
            "primeira_tentativa": rodadas[0]["inicio"] if rodadas else None,
            "ultima_tentativa": rodadas[-1]["fim"] if rodadas else None,
        })
    return resultado


def questoes_totais_da_prova(ano: int, caderno: str, grande_area: str) -> int:
    """Tamanho real da prova (todas as questões cadastradas, respondidas
    ou não) -- usado por simulados_feitos() pra mostrar cobertura
    (ex: '43/44 respondidas') sem depender de nenhuma resposta já ter
    sido dada."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM questoes WHERE ano=? AND caderno=? AND grande_area=?",
            (ano, caderno_norm, grande_area_norm),
        ).fetchone()[0]


def calcular_ofensiva() -> dict:
    """Ofensiva (streak) estilo Duolingo: dias seguidos com pelo menos
    uma tentativa registrada. 'Seguido' conta a partir de hoje ou
    ontem (se ainda não respondeu nada hoje, a ofensiva de ontem
    continua valendo até o fim do dia). Também devolve os últimos 30
    dias pra desenhar um calendário simples."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT DISTINCT date(data_tentativa) FROM tentativas_usuario ORDER BY date(data_tentativa) DESC"
        ).fetchall()
    dias_com_atividade = {r[0] for r in linhas}

    hoje = date.today()
    if not dias_com_atividade:
        atual = 0
    else:
        cursor = hoje if hoje.isoformat() in dias_com_atividade else hoje - timedelta(days=1)
        atual = 0
        while cursor.isoformat() in dias_com_atividade:
            atual += 1
            cursor -= timedelta(days=1)

    melhor = 0
    if dias_com_atividade:
        ordenados = sorted(dias_com_atividade)
        sequencia = 1
        melhor = 1
        for i in range(1, len(ordenados)):
            anterior = date.fromisoformat(ordenados[i - 1])
            atual_data = date.fromisoformat(ordenados[i])
            if (atual_data - anterior).days == 1:
                sequencia += 1
                melhor = max(melhor, sequencia)
            else:
                sequencia = 1

    calendario_30_dias = [
        {"data": (hoje - timedelta(days=i)).isoformat(), "ativo": (hoje - timedelta(days=i)).isoformat() in dias_com_atividade}
        for i in range(29, -1, -1)
    ]

    return {"atual": atual, "melhor": melhor, "calendario_30_dias": calendario_30_dias}


def obter_configuracao(chave: str, padrao: str | None = None) -> str | None:
    with _conectar() as conn:
        linha = conn.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,)).fetchone()
    return linha[0] if linha else padrao


def definir_configuracao(chave: str, valor: str) -> None:
    with _conectar() as conn:
        conn.execute(
            "INSERT INTO configuracoes (chave, valor) VALUES (?, ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
            (chave, valor),
        )


META_DIARIA_PADRAO = 5


def progresso_meta_diaria() -> dict:
    """Quantas tentativas de hoje contra a meta diária configurada
    (padrão 5, editável na tela Admin). Baixo de propósito -- mesmo
    princípio do Duolingo mostrar 'ganhe 10 XP' em vez de 500: a meta
    diária só cria hábito se for batível em poucos minutos; uma meta
    alta demais vira fricção em vez de gatilho de hábito (era 20 antes,
    baixado a pedido do usuário). Conta TENTATIVA, não questão
    distinta -- responder a mesma questão de novo ainda é prática,
    mesma lógica de calcular_ofensiva() pra 'teve atividade hoje'."""
    meta = int(obter_configuracao("meta_diaria", str(META_DIARIA_PADRAO)))
    hoje = date.today().isoformat()
    with _conectar() as conn:
        feitas_hoje = conn.execute(
            "SELECT COUNT(*) FROM tentativas_usuario WHERE date(data_tentativa) = ?", (hoje,)
        ).fetchone()[0]
    return {
        "meta": meta,
        "feitas_hoje": feitas_hoje,
        "restantes": max(0, meta - feitas_hoje),
        "atingida": feitas_hoje >= meta,
    }


DATA_PROVA_PADRAO = "2026-11-08"


def dias_ate_prova() -> dict:
    """Contagem regressiva. data_prova vem de configuracoes (editável
    na tela Admin) -- não hardcoded direto no código, porque a data
    muda a cada edição/ano e não é algo pra depender de deploy pra
    corrigir."""
    data_prova = date.fromisoformat(obter_configuracao("data_prova", DATA_PROVA_PADRAO))
    hoje = date.today()
    dias = (data_prova - hoje).days
    return {"data_prova": data_prova.isoformat(), "dias_restantes": dias, "ja_passou": dias < 0}


_FASES_PLANO = {
    "fase1_fundacao": "Fase 1 — Fundação em Natureza + manutenção",
    "fase2_consolidacao": "Fase 2 — Consolidação, todas as áreas em rotação plena",
    "fase3_blindagem": "Fase 3 — Blindagem, sem conteúdo novo pesado",
    "prova": "Dia da prova",
    "pos_prova": "Prova já passou",
}

# Datas de corte das fases 1 e 2 -- vêm do cronograma de 74 dias que o
# próprio Gabriel escreveu (documento colado em 2026-08-26), não de uma
# fórmula proporcional. A fase 3 sempre termina na data da prova. Ambas
# editáveis em configuracoes pra não exigir mexer em código se o plano
# mudar de novo.
FASE1_FIM_PADRAO = "2026-09-16"
FASE2_FIM_PADRAO = "2026-10-11"


def plano_periodizacao() -> dict:
    """3 fases com datas de corte FIXAS (do plano do usuário, não
    proporcionais a 'dias restantes') -- fase 1 até FASE1_FIM_PADRAO,
    fase 2 até FASE2_FIM_PADRAO, fase 3 até a prova. Se as datas de
    corte forem editadas depois (configuracoes), a duração de cada
    fase muda de verdade, é intencional -- diferente da versão anterior
    (proporcional), esta reflete um cronograma escrito à mão."""
    prova = dias_ate_prova()
    data_prova = date.fromisoformat(prova["data_prova"])
    hoje = date.today()
    dias_restantes = prova["dias_restantes"]

    data_inicio_str = obter_configuracao("data_inicio_plano")
    if data_inicio_str is None:
        data_inicio_str = hoje.isoformat()
        definir_configuracao("data_inicio_plano", data_inicio_str)
    data_inicio = date.fromisoformat(data_inicio_str)

    fase1_fim = date.fromisoformat(obter_configuracao("fase1_fim", FASE1_FIM_PADRAO))
    fase2_fim = date.fromisoformat(obter_configuracao("fase2_fim", FASE2_FIM_PADRAO))

    if dias_restantes < 0:
        fase = "pos_prova"
    elif dias_restantes == 0:
        fase = "prova"
    elif hoje <= fase1_fim:
        fase = "fase1_fundacao"
    elif hoje <= fase2_fim:
        fase = "fase2_consolidacao"
    else:
        fase = "fase3_blindagem"

    return {
        "fase": fase,
        "fase_label": _FASES_PLANO[fase],
        "dias_decorridos": max((hoje - data_inicio).days, 0),
        "dias_restantes": dias_restantes,
        "data_prova": prova["data_prova"],
        "fase1_fim": fase1_fim.isoformat(),
        "fase2_fim": fase2_fim.isoformat(),
    }


def historico_diario_por_area(grande_area: str, minimo_questoes: int = 15) -> list[dict]:
    """Dias com pelo menos `minimo_questoes` tentativas numa área -- a
    aproximação de 'isso foi um simulado' sem precisar de uma tabela de
    sessão dedicada. Base pra média móvel: o próprio plano do usuário
    diz pra ler por TENDÊNCIA dos últimos simulados, não pelo resultado
    isolado de um dia (nota varia por cansaço, tema sorteado etc)."""
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT date(t.data_tentativa) AS dia, COUNT(*) AS total,
                   SUM(CASE WHEN t.resultado='acertou' THEN 1 ELSE 0 END) AS acertos
            FROM tentativas_usuario t
            JOIN questoes q ON q.id_questao = t.id_questao
            WHERE q.grande_area = ?
            GROUP BY dia
            HAVING total >= ?
            ORDER BY dia
            """,
            (grande_area_norm, minimo_questoes),
        ).fetchall()
    return [
        {"dia": d, "total": t, "acertos": a, "taxa_acerto_pct": round(a / t * 100, 1)}
        for d, t, a in linhas
    ]


def media_movel_simulados(grande_area: str, n: int = 3) -> dict:
    """Média dos últimos N dias com simulado (ver historico_diario_por_
    area) -- a métrica que o plano do usuário trata como a que importa
    de verdade, em vez do resultado de um dia isolado."""
    historico = historico_diario_por_area(grande_area)
    ultimos = historico[-n:]
    if not ultimos:
        return {"tem_dado": False, "n_simulados": 0}
    media = sum(h["taxa_acerto_pct"] for h in ultimos) / len(ultimos)
    return {
        "tem_dado": True,
        "n_simulados": len(ultimos),
        "media_pct": round(media, 1),
        "detalhe": ultimos,
    }


_RANKS = [
    (0, "E-Rank"), (100, "D-Rank"), (300, "C-Rank"),
    (600, "B-Rank"), (1000, "A-Rank"), (1500, "S-Rank"),
]


def calcular_nivel_jogador() -> dict:
    """Sistema de nível derivado 100% de tentativas reais -- XP = 10
    por acerto + 2 por tentativa (errar também vale alguma coisa,
    porque tentar é a parte que importa pra aprender). Ranks E a S
    (mesma nomenclatura de Solo Leveling). Puramente cosmético: não
    influencia gabarito, Leitner nem nenhuma métrica de estudo real."""
    geral = resumo_geral_desempenho()
    total = geral["total_tentativas"] or 0
    acertos = geral["acertos"] or 0
    xp = acertos * 10 + total * 2

    rank_atual = _RANKS[0][1]
    proximo_rank, xp_para_proximo = None, None
    for i, (limite, nome) in enumerate(_RANKS):
        if xp >= limite:
            rank_atual = nome
        else:
            proximo_rank, xp_para_proximo = nome, limite - xp
            break

    return {
        "xp": xp, "rank": rank_atual,
        "proximo_rank": proximo_rank, "xp_para_proximo": xp_para_proximo,
        "total_tentativas": total, "acertos": acertos,
    }


ALVO_MISSAO_FOCO = 10


def missoes_do_dia() -> list[dict]:
    """Missões do dia estilo Duolingo, mas SEM tabela nova e SEM
    bloquear nada -- reforço positivo puro (mesmo princípio de
    calcular_ofensiva/calcular_nivel_jogador: derivado ao vivo de
    tentativas_usuario, nunca persistido, então não tem "reset diário"
    pra implementar -- o dia troca sozinho porque date.today() troca
    sozinho). Decisão deliberada de NÃO ter uma missão que trava o
    progresso (tipo 'vidas' do Duolingo) -- bloquear prática logo
    quando o usuário mais precisa repetir uma questão errada trabalha
    contra o objetivo real (fixar conteúdo antes da prova).

    Duas missões:
    1) Meta diária -- reaproveita progresso_meta_diaria() como está,
       sem duplicar a lógica de contagem.
    2) Foco na matéria de maior prioridade do momento (o topo do
       ranking de prioridade_de_estudo(), cruzando as duas áreas) --
       quantas tentativas de HOJE já foram nessa matéria específica.
       Sem tentativa nenhuma na base ainda, essa missão não aparece
       (não tem prioridade calculável sem dado)."""
    missoes = []

    meta = progresso_meta_diaria()
    missoes.append({
        "id": "meta_diaria",
        "titulo": "Complete sua meta diária",
        "descricao": f"{meta['feitas_hoje']}/{meta['meta']} questão(ões) hoje",
        "progresso_atual": meta["feitas_hoje"],
        "progresso_meta": meta["meta"],
        "concluida": meta["atingida"],
    })

    candidatos = []
    for area in ("matematica", "ciencias_natureza"):
        ranking = prioridade_de_estudo(area)["ranking"]
        if ranking:
            topo = ranking[0]
            candidatos.append((topo["score_prioridade"], area, topo["materia"]))
    if candidatos:
        candidatos.sort(key=lambda c: c[0], reverse=True)
        _, area_foco, materia_foco = candidatos[0]
        hoje = date.today().isoformat()
        with _conectar() as conn:
            feitas_hoje_materia = conn.execute(
                """
                SELECT COUNT(*) FROM tentativas_usuario t
                JOIN questoes q ON q.id_questao = t.id_questao
                WHERE date(t.data_tentativa) = ? AND q.grande_area = ? AND q.materia = ?
                """,
                (hoje, area_foco, materia_foco),
            ).fetchone()[0]
        missoes.append({
            "id": "foco_prioridade",
            "titulo": f"Foco em {materia_foco}",
            "descricao": f"Pratique {materia_foco} hoje — é sua maior prioridade agora",
            "progresso_atual": min(feitas_hoje_materia, ALVO_MISSAO_FOCO),
            "progresso_meta": ALVO_MISSAO_FOCO,
            "concluida": feitas_hoje_materia >= ALVO_MISSAO_FOCO,
        })

    return missoes


def materias_validas(grande_area: str = "matematica") -> list[str]:
    """Lista ordenada de matérias válidas pra uma grande área — alimenta
    o seletor da tela de triagem manual."""
    return sorted(materia for area, materia in TAXONOMIA_VALIDA if area == grande_area)


def materias_com_banco_pratica(grande_area: str) -> list[str]:
    """Matérias da área que já têm ao menos uma questão de banco de
    prática (origem='banco_pratica'), ordenadas da com MAIS questões pra
    com menos. Existe pra dar um padrão sensato ao seletor de matéria da
    Home (`_renderizar_home_banco_pratica`) -- antes ele caía sempre na
    1a matéria em ordem alfabética de `materias_validas()` (a lista
    completa da taxonomia fechada, a maioria sem NENHUMA questão de
    prática ainda), o que é essencialmente aleatório e frequentemente
    mostra "nenhuma questão ainda" na primeira renderização."""
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT materia, COUNT(*) as n FROM questoes
            WHERE origem = 'banco_pratica' AND grande_area = ?
            GROUP BY materia ORDER BY n DESC, materia
            """,
            (grande_area,),
        ).fetchall()
    return [r[0] for r in linhas]


def questoes_pendentes_classificacao() -> list[dict]:
    """Lista de questões 'nao_classificado', com o que já se sabe delas
    (gabarito, grande_area) pra alimentar a tela de triagem manual sem
    precisar de consulta extra."""
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT id_questao, ano, caderno, numero_questao, materia, grande_area, alternativa_correta
            FROM questoes WHERE status_classificacao = 'nao_classificado'
            ORDER BY ano, numero_questao
            """
        ).fetchall()
    return [
        {
            "id_questao": r[0], "ano": r[1], "caderno": r[2], "numero_questao": r[3],
            "materia_bruta": r[4], "grande_area": r[5], "alternativa_correta": r[6],
        }
        for r in linhas
    ]


def recorrencia_por_materia(grande_area: str) -> list[dict]:
    """Base pro insight 'matéria X apareceu em N% das provas'. Só
    conta questões classificadas — 'sem_video_pendente' e afins não
    são um tópico de verdade, então não entram no ranking.

    Filtra por grande_area, e o denominador (total_provas_na_base)
    também é filtrado -- é quantas provas TÊM matemática (ou
    ciências) carregada, não o total de provas da base toda (senão
    o percentual de matemática ficaria artificialmente baixo em anos
    que só têm ciências carregada, e vice-versa).

    Filtra também origem='enem_oficial' -- isto mede recorrência em
    PROVA REAL do ENEM; sem esse filtro, praticar 40 questões de um
    assunto no banco de prática inflaria artificialmente a recorrência
    dele (pareceria "cair sempre" quando na verdade é só muito
    praticado), corrompendo exatamente o insight que TRI coherence /
    manual_prioridade_de_estudo.md usa pra priorizar tema recorrente."""
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        total_provas = conn.execute(
            "SELECT COUNT(DISTINCT ano || '_' || caderno) FROM questoes WHERE grande_area = ? AND origem = 'enem_oficial'",
            (grande_area_norm,),
        ).fetchone()[0]
        linhas = conn.execute(
            """
            SELECT materia, COUNT(DISTINCT ano || '_' || caderno) AS provas_com_materia
            FROM questoes
            WHERE status_classificacao = 'classificado' AND grande_area = ? AND origem = 'enem_oficial'
            GROUP BY materia
            ORDER BY provas_com_materia DESC
            """,
            (grande_area_norm,),
        ).fetchall()
    return [
        {
            "materia": materia,
            "provas_com_materia": provas,
            "percentual": round(provas / total_provas * 100, 1) if total_provas else None,
            "total_provas_na_base": total_provas,
        }
        for materia, provas in linhas
    ]


def salvar_redacao(
    tema: str, data_escrita: str | None = None, texto: str | None = None,
    arquivo_path: str | None = None, nota: int | None = None,
    erros_ortograficos: int | None = None, fonte_correcao: str | None = None,
    observacoes: str | None = None,
) -> int:
    """Só guarda -- não corrige. nota/erros_ortograficos vêm de quem
    corrigiu (própria, externa ou oficial), o sistema não avalia
    redação. Retorna o id da linha criada."""
    tema = tema.strip()
    if not tema:
        raise ValueError("Tema não pode ser vazio.")
    if fonte_correcao not in (None, "propria", "externa", "oficial"):
        raise ValueError(f"fonte_correcao inválida: '{fonte_correcao}'")

    with _conectar() as conn:
        cursor = conn.execute(
            """
            INSERT INTO redacoes
                (tema, data_escrita, texto, arquivo_path, nota, erros_ortograficos, fonte_correcao, observacoes)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                tema, data_escrita or date.today().isoformat(), texto or None, arquivo_path,
                nota, erros_ortograficos, fonte_correcao, observacoes or None,
            ),
        )
        return cursor.lastrowid


def listar_redacoes() -> list[dict]:
    """Mais recente primeiro."""
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT id, tema, data_escrita, texto, arquivo_path, nota,
                   erros_ortograficos, fonte_correcao, observacoes
            FROM redacoes ORDER BY data_escrita DESC, id DESC
            """
        ).fetchall()
    return [
        {
            "id": r[0], "tema": r[1], "data_escrita": r[2], "texto": r[3],
            "arquivo_path": r[4], "nota": r[5], "erros_ortograficos": r[6],
            "fonte_correcao": r[7], "observacoes": r[8],
        }
        for r in linhas
    ]


def temas_redacoes_usados() -> list[str]:
    with _conectar() as conn:
        linhas = conn.execute("SELECT DISTINCT tema FROM redacoes ORDER BY tema").fetchall()
    return [r[0] for r in linhas]


def apagar_redacao(id_redacao: int) -> None:
    with _conectar() as conn:
        conn.execute("DELETE FROM redacoes WHERE id = ?", (id_redacao,))


def atualizar_redacao(
    id_redacao: int, tema: str, data_escrita: str, texto: str | None,
    nota: int | None, erros_ortograficos: int | None,
    fonte_correcao: str | None, observacoes: str | None,
) -> None:
    """Corrige uma redação já salva -- pensada pro fluxo real (salva
    sem nota assim que escreve, corrige quando o resultado sai dias
    depois). UPDATE completo, não COALESCE parcial como
    atualizar_enunciado(): a UI já manda o valor atual de cada campo
    (editado ou não), então não tem ambiguidade de 'None significa o
    quê' -- inclusive permite limpar nota/observações de propósito.
    Não mexe em arquivo_path nem criado_em."""
    tema = tema.strip()
    if not tema:
        raise ValueError("Tema não pode ser vazio.")
    if fonte_correcao not in (None, "propria", "externa", "oficial"):
        raise ValueError(f"fonte_correcao inválida: '{fonte_correcao}'")
    with _conectar() as conn:
        existe = conn.execute("SELECT 1 FROM redacoes WHERE id = ?", (id_redacao,)).fetchone()
        if not existe:
            raise ValueError(f"Redação '{id_redacao}' não existe.")
        conn.execute(
            """
            UPDATE redacoes SET tema=?, data_escrita=?, texto=?, nota=?,
                erros_ortograficos=?, fonte_correcao=?, observacoes=?
            WHERE id=?
            """,
            (tema, data_escrita, texto or None, nota, erros_ortograficos,
             fonte_correcao, observacoes or None, id_redacao),
        )


if __name__ == "__main__":
    # Smoke test roda contra um banco SEPARADO, nunca contra o
    # enem.db de produção. Escrever dado de demonstração ('Marketing
    # digital', questões 2022_azul_155 etc) direto no banco real é
    # exatamente o tipo de dado sintético misturado com dado real que
    # a auditoria original apontou como problema crítico no sistema
    # antigo (enem_2019_2025_preenchido.csv). Não repete o erro aqui.
    DB_PATH = Path(__file__).parent / "enem_teste.db"
    if DB_PATH.exists():
        DB_PATH.unlink()

    inicializar_banco()

    id_q, status = inserir_questao(
        ano=2022, caderno="Azul", numero=155,
        grande_area="Matemática", materia="Análise Combinatória",
        alternativa_correta="C",
    )
    print(f"Questão inserida: {id_q} (status={status})")

    inserir_resolucao(id_q, "video", "https://www.youtube.com/watch?v=exemplo", canal="Canal de exemplo")
    inserir_resolucao(id_q, "texto", "Resolução escrita: usar combinação simples C(n,k)...")

    # tentativa errada, depois duas certas seguidas
    print(registrar_tentativa(id_q, "A"))   # errou -> streak 0, 1 dia
    print(registrar_tentativa(id_q, "C"))   # acertou -> streak 1, 1 dia
    print(registrar_tentativa(id_q, "C"))   # acertou -> streak 2, 2 dias

    # questão com matéria fora da taxonomia -> vai pra triagem, não é perdida
    id_lixo, status_lixo = inserir_questao(
        ano=2024, caderno="Azul", numero=999,
        grande_area="Matemática", materia="Marketing digital",
        alternativa_correta="A",
    )
    print(f"Questão fora da taxonomia: {id_lixo} (status={status_lixo})")

    # mais duas questões na mesma prova de 2022, pra testar a listagem
    # que o cartão-resposta vai usar (caderno em caixa diferente de
    # propósito, pra provar que a normalização funciona na consulta)
    inserir_questao(ano=2022, caderno="azul", numero=136, grande_area="Matemática",
                     materia="Geometria Plana", alternativa_correta="D")
    inserir_questao(ano=2022, caderno="AZUL", numero=176, grande_area="Matemática",
                     materia="Geometria Plana", alternativa_correta="A")

    print("Provas cadastradas:", listar_provas())
    print("Questões da prova 2022/Azul:", listar_questoes_da_prova(2022, "Azul"))

    print("Fila de revisão hoje:", questoes_para_revisar())
    print("Taxa de acerto por matéria:", taxa_acerto_por_materia("matematica"))
    print("Recorrência por matéria:", recorrencia_por_materia("matematica"))