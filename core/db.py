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
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany(
            "INSERT OR IGNORE INTO topicos_validos (grande_area, materia) VALUES (?, ?)",
            list(TAXONOMIA_VALIDA),
        )
        colunas = {r[1] for r in conn.execute("PRAGMA table_info(tentativas_usuario)").fetchall()}
        if "tipo_erro" not in colunas:
            conn.execute("ALTER TABLE tentativas_usuario ADD COLUMN tipo_erro TEXT")


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


# ============================================================
# REGISTRO DE TENTATIVA
# ============================================================

def registrar_tentativa(id_questao: str, resposta_escolhida: str) -> dict:
    """Única função que deve gravar em tentativas_usuario e
    estado_revisao — evita os dois divergirem por escritas separadas.

    Compara a resposta contra o gabarito guardado em questoes (o
    próprio sistema decide acerto/erro; não depende de nenhum rótulo
    externo, o que elimina o problema antigo de 'fonte_nivel' que
    cravava 'confirmado_transcricao_ia' mesmo quando não era verdade).
    """
    resposta = resposta_escolhida.strip().upper()
    if resposta not in {"A", "B", "C", "D", "E"}:
        raise ValueError(f"resposta_escolhida inválida: '{resposta_escolhida}'")

    with _conectar() as conn:
        linha = conn.execute(
            "SELECT alternativa_correta FROM questoes WHERE id_questao = ?", (id_questao,)
        ).fetchone()
        if linha is None:
            raise ValueError(f"Questão '{id_questao}' não existe na base.")

        resultado = "acertou" if resposta == linha[0] else "errou"
        proxima_revisao, intervalo_dias, streak = calcular_proxima_revisao(id_questao, resultado, conn)

        conn.execute(
            """
            INSERT INTO tentativas_usuario
                (id_questao, resposta_escolhida, resultado, intervalo_dias, streak_acertos, proxima_revisao)
            VALUES (?,?,?,?,?,?)
            """,
            (id_questao, resposta, resultado, intervalo_dias, streak, proxima_revisao.isoformat()),
        )
        id_tentativa = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """
            INSERT INTO estado_revisao (id_questao, intervalo_dias, streak_acertos, proxima_revisao, ultima_tentativa)
            VALUES (?,?,?,?, date('now'))
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
        "intervalo_dias": intervalo_dias,
        "streak_acertos": streak,
        "proxima_revisao": proxima_revisao.isoformat(),
    }


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
    misturar 45+44 questões de áreas diferentes na mesma grade."""
    with _conectar() as conn:
        linhas = conn.execute(
            "SELECT DISTINCT ano, caderno, grande_area FROM questoes ORDER BY ano DESC, caderno, grande_area"
        ).fetchall()
    return linhas


def listar_questoes_da_prova(ano: int, caderno: str, grande_area: str) -> list[dict]:
    """Questões de uma prova específica (ano+caderno+área), ordenadas
    por número — monta a grade do cartão-resposta. 'caderno' é
    normalizado aqui pra aceitar 'Azul' ou 'azul' indiferentemente."""
    caderno_norm = normalizar_texto(caderno)
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        linhas = conn.execute(
            """
            SELECT id_questao, numero_questao, materia, status_classificacao
            FROM questoes
            WHERE ano = ? AND caderno = ? AND grande_area = ?
            ORDER BY numero_questao
            """,
            (ano, caderno_norm, grande_area_norm),
        ).fetchall()
    return [
        {"id_questao": r[0], "numero_questao": r[1], "materia": r[2], "status_classificacao": r[3]}
        for r in linhas
    ]


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
        })

    ranking.sort(key=lambda x: x["score_prioridade"], reverse=True)
    sem_dados.sort(key=lambda x: x["percentual_recorrencia"], reverse=True)
    return {"ranking": ranking, "sem_dados": sem_dados}


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
            "SELECT tipo, conteudo, canal FROM resolucoes WHERE id_questao = ? ORDER BY criado_em",
            (id_questao,),
        ).fetchall()
    return [{"tipo": r[0], "conteudo": r[1], "canal": r[2]} for r in linhas]


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


def materias_validas(grande_area: str = "matematica") -> list[str]:
    """Lista ordenada de matérias válidas pra uma grande área — alimenta
    o seletor da tela de triagem manual."""
    return sorted(materia for area, materia in TAXONOMIA_VALIDA if area == grande_area)


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
    que só têm ciências carregada, e vice-versa)."""
    grande_area_norm = normalizar_texto(grande_area)
    with _conectar() as conn:
        total_provas = conn.execute(
            "SELECT COUNT(DISTINCT ano || '_' || caderno) FROM questoes WHERE grande_area = ?",
            (grande_area_norm,),
        ).fetchone()[0]
        linhas = conn.execute(
            """
            SELECT materia, COUNT(DISTINCT ano || '_' || caderno) AS provas_com_materia
            FROM questoes
            WHERE status_classificacao = 'classificado' AND grande_area = ?
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

    inserir_resolucao(id_q, "video", "https://www.youtube.com/watch?v=exemplo", canal="Xequemat ENEM")
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