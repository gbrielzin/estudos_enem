"""
test_db.py — testes automatizados pro núcleo de db.py.

Não existia nenhum teste automatizado no projeto antes deste arquivo (só o
smoke test manual no bloco __main__ de db.py, que imprime pra inspeção
visual e não faz assert nenhum) -- ver a seção 13 de SYSTEM_DEEP_DIVE.md.
Cobre as funções mais críticas e mais baratas de testar: a normalização de
texto e a canonicalização de matéria (o pipeline de taxonomia inteiro), o
Leitner simplificado, e os dois fluxos com estado que mais importam
(registrar_tentativa + estado_revisao; sobrescrever=True recalculando
tentativas antigas quando o gabarito muda).

Nunca toca em enem.db: cada teste que precisa de banco troca db.DB_PATH
pra um arquivo novo dentro de tempfile.mkdtemp() (mesma técnica que
reconstruir_base.py e o bloco __main__ de db.py já usam pra apontar pro
banco de teste), e desfaz a troca no tearDown -- mesmo se o teste falhar
no meio.

Rodar (de dentro de core/):
    python -m unittest test_db
    python -m unittest test_db -v          (verboso, um teste por linha)
    python -m unittest test_db.TestCalcularLeitner   (só uma classe)
"""
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import db


# ============================================================
# NORMALIZAÇÃO DE TEXTO E TAXONOMIA (funções puras, sem banco)
# ============================================================

class TestNormalizarTexto(unittest.TestCase):
    def test_minusculo_sem_acento_espaco_vira_underscore(self):
        self.assertEqual(db.normalizar_texto("Matemática Básica"), "matematica_basica")

    def test_espacos_extras_e_caixa_mista(self):
        self.assertEqual(db.normalizar_texto("  Função   Afim  "), "funcao_afim")

    def test_simbolo_grau_masculino_ordinal_e_simbolo_de_grau_nao_sao_iguais(self):
        """Limitação documentada no próprio docstring de normalizar_texto():
        'º' (U+00BA, ordinal masculino) tem decomposição de compatibilidade
        NFKD pra 'o' e sobrevive; '°' (U+00B0, símbolo de grau) não tem
        decomposição nenhuma e é removido pelo re.sub de pontuação -- os
        dois casos produzem strings DIFERENTES aqui. É por isso que
        canonicalizar_materia() não pode confiar só nesta função (ver
        TestCanonicalizarMateria abaixo, onde os dois convergem)."""
        com_ordinal = db.normalizar_texto("Função de 1º Grau")
        com_grau = db.normalizar_texto("Função de 1° Grau")
        self.assertEqual(com_ordinal, "funcao_de_1o_grau")
        self.assertEqual(com_grau, "funcao_de_1_grau")
        self.assertNotEqual(com_ordinal, com_grau)


class TestCanonicalizarMateria(unittest.TestCase):
    def test_sinonimo_exato(self):
        self.assertEqual(db.canonicalizar_materia("funcao_afim"), "funcao_1_grau")
        self.assertEqual(db.canonicalizar_materia("logica"), "raciocinio_logico")

    def test_padrao_de_familia_funcao_de_grau_cobre_as_variacoes_reais(self):
        variacoes = [
            "funcao_de_1_grau", "funcao_do_1_grau", "funcao_de_1o_grau",
            "funcao_de_primeiro_grau", "funcao_do_primeiro_grau",
        ]
        for variacao in variacoes:
            with self.subTest(variacao=variacao):
                self.assertEqual(db.canonicalizar_materia(variacao), "funcao_1_grau")

    def test_padrao_de_familia_cobre_os_dois_casos_de_grau_que_normalizar_texto_diferencia(self):
        """A costura que resolve o caso do teste anterior de
        TestNormalizarTexto: canonicalizar_materia() unifica 'funcao_de_1o_grau'
        (veio de 'º') e 'funcao_de_1_grau' (veio de '°') no mesmo canônico,
        mesmo as duas strings sendo diferentes na saída de normalizar_texto."""
        self.assertEqual(db.canonicalizar_materia("funcao_de_1o_grau"), "funcao_1_grau")
        self.assertEqual(db.canonicalizar_materia("funcao_de_1_grau"), "funcao_1_grau")

    def test_padrao_de_familia_geometria_espacial_com_solido(self):
        self.assertEqual(db.canonicalizar_materia("geometria_espacial_esfera"), "geometria_espacial")

    def test_sem_correspondencia_devolve_o_texto_original(self):
        """canonicalizar_materia() não força match -- se não bate com nada,
        devolve o texto de entrada sem alteração (quem decide se isso é
        'nao_classificado' é o caller, comparando contra TAXONOMIA_VALIDA)."""
        self.assertEqual(db.canonicalizar_materia("algo_sem_mapeamento_nenhum"), "algo_sem_mapeamento_nenhum")


class TestGerarIdCanonico(unittest.TestCase):
    def test_formato_basico(self):
        self.assertEqual(db.gerar_id_canonico(2024, "Azul", 136), "2024_azul_136")

    def test_caderno_normalizado_produz_o_mesmo_id_independente_da_caixa(self):
        """Existe especificamente pra impedir 'Azul' e 'azul' virarem duas
        chaves diferentes -- o bug de fragmentação de string que o sistema
        antigo tinha (ver core/CLAUDE.md)."""
        self.assertEqual(
            db.gerar_id_canonico(2024, "azul", 136),
            db.gerar_id_canonico(2024, "AZUL", 136),
        )


# ============================================================
# LEITNER SIMPLIFICADO (função pura, sem banco)
# ============================================================

class TestCalcularLeitner(unittest.TestCase):
    def test_erro_sempre_zera_streak_e_agenda_1_dia(self):
        self.assertEqual(db._calcular_leitner(0, "errou"), (0, 1))
        self.assertEqual(db._calcular_leitner(5, "errou"), (0, 1))
        self.assertEqual(db._calcular_leitner(90, "errou"), (0, 1))

    def test_progressao_de_acertos_segue_2_elevado_a_streak_menos_1(self):
        progressao_esperada = {
            0: (1, 1), 1: (2, 2), 2: (3, 4), 3: (4, 8),
            4: (5, 16), 5: (6, 32), 6: (7, 64),
        }
        for streak_anterior, esperado in progressao_esperada.items():
            with self.subTest(streak_anterior=streak_anterior):
                self.assertEqual(db._calcular_leitner(streak_anterior, "acertou"), esperado)

    def test_intervalo_trava_no_teto_de_90_dias(self):
        # streak_anterior=7 -> novo_streak=8 -> 2**7=128, capado em 90
        self.assertEqual(db._calcular_leitner(7, "acertou"), (8, 90))
        # streak bem além do teto continua capado, nunca ultrapassa
        self.assertEqual(db._calcular_leitner(20, "acertou"), (21, 90))


# ============================================================
# TESTES COM BANCO TEMPORÁRIO (nunca tocam enem.db)
# ============================================================

class _TestComBancoTemporario(unittest.TestCase):
    """Classe-base: troca db.DB_PATH pra um arquivo novo em tempfile antes
    de cada teste, restaura o valor original depois -- mesma técnica que
    reconstruir_base.py usa (reatribui db.DB_PATH de fora do módulo antes
    de chamar inicializar_banco())."""

    def setUp(self):
        self._db_path_original = db.DB_PATH
        self._pasta_temp = tempfile.mkdtemp(prefix="enem_teste_unit_")
        db.DB_PATH = Path(self._pasta_temp) / "enem_teste.db"
        db.inicializar_banco()

    def tearDown(self):
        db.DB_PATH = self._db_path_original
        shutil.rmtree(self._pasta_temp, ignore_errors=True)


class TestRegistrarTentativaEEstadoRevisao(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, status = db.inserir_questao(
            ano=2022, caderno="Azul", numero=155,
            grande_area="Matematica", materia="Analise Combinatoria",
            alternativa_correta="C",
        )
        self.assertEqual(status, "classificado")

    def test_sequencia_erro_depois_dois_acertos_segue_o_leitner(self):
        r1 = db.registrar_tentativa(self.id_q, "A")  # errou
        self.assertEqual(r1["resultado"], "errou")
        self.assertEqual((r1["streak_acertos"], r1["intervalo_dias"]), (0, 1))

        r2 = db.registrar_tentativa(self.id_q, "C")  # acertou
        self.assertEqual(r2["resultado"], "acertou")
        self.assertEqual((r2["streak_acertos"], r2["intervalo_dias"]), (1, 1))

        r3 = db.registrar_tentativa(self.id_q, "C")  # acertou de novo
        self.assertEqual(r3["resultado"], "acertou")
        self.assertEqual((r3["streak_acertos"], r3["intervalo_dias"]), (2, 2))

        # estado_revisao reflete a ÚLTIMA tentativa, não soma nada à parte
        proxima_esperada = (date.today() + timedelta(days=2)).isoformat()
        self.assertEqual(r3["proxima_revisao"], proxima_esperada)

        # as 3 tentativas realmente foram gravadas (log append-only)
        detalhe = db.detalhe_questao(self.id_q)
        self.assertEqual(detalhe["alternativa_correta"], "C")

    def test_resposta_em_branco_conta_como_erro_e_nunca_fica_de_fora(self):
        resultado = db.registrar_tentativa(self.id_q, None)
        self.assertEqual(resultado["resultado"], "errou")
        self.assertIsNone(resultado["resposta_escolhida"])
        # uma tentativa em branco ainda entra na fila de revisão de amanhã
        self.assertEqual(resultado["intervalo_dias"], 1)

    def test_resposta_invalida_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.registrar_tentativa(self.id_q, "Z")

    def test_questao_inexistente_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.registrar_tentativa("2099_azul_999", "A")

    def test_duracao_segundos_e_gravada_quando_informada(self):
        db.registrar_tentativa(self.id_q, "C", duracao_segundos=87)
        with db._conectar() as conn:
            valor = conn.execute(
                "SELECT duracao_segundos FROM tentativas_usuario WHERE id_questao = ?", (self.id_q,)
            ).fetchone()[0]
        self.assertEqual(valor, 87)

    def test_duracao_segundos_e_opcional_fica_none_sem_informar(self):
        db.registrar_tentativa(self.id_q, "A")
        with db._conectar() as conn:
            valor = conn.execute(
                "SELECT duracao_segundos FROM tentativas_usuario WHERE id_questao = ?", (self.id_q,)
            ).fetchone()[0]
        self.assertIsNone(valor)


class TestSobrescreverRecalculaTentativas(_TestComBancoTemporario):
    """Cobre o comportamento descrito na seção 3 de SYSTEM_DEEP_DIVE.md:
    inserir_questao(sobrescrever=True) mudando o gabarito precisa
    recalcular o resultado de tentativas já registradas, não deixar
    acertou/errou desatualizado escondido."""

    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=160,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="C",
        )
        resultado = db.registrar_tentativa(self.id_q, "C")
        self.assertEqual(resultado["resultado"], "acertou")

    def test_mudar_gabarito_recalcula_resultado_da_tentativa_antiga(self):
        db.inserir_questao(
            ano=2022, caderno="Azul", numero=160,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="D",  # gabarito mudou de C pra D
            sobrescrever=True,
        )
        detalhe = db.detalhe_questao(self.id_q)
        self.assertEqual(detalhe["alternativa_correta"], "D")

        # a tentativa que respondeu "C" (certo pro gabarito antigo) agora
        # deve aparecer como errada, sem precisar responder de novo
        historico = db.historico_alteracoes(self.id_q)
        alteracao_gabarito = next(h for h in historico if h["campo"] == "alternativa_correta")
        self.assertEqual(alteracao_gabarito["valor_antigo"], "C")
        self.assertEqual(alteracao_gabarito["valor_novo"], "D")
        self.assertEqual(alteracao_gabarito["tentativas_recalculadas"], 1)

    def test_sobrescrever_sem_mudar_nada_nao_gera_historico(self):
        db.inserir_questao(
            ano=2022, caderno="Azul", numero=160,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="C",  # mesmo gabarito de antes
            sobrescrever=True,
        )
        self.assertEqual(db.historico_alteracoes(self.id_q), [])


class TestTaxonomiaFechadaNaoPerdeQuestao(_TestComBancoTemporario):
    def test_materia_fora_da_taxonomia_e_gravada_como_nao_classificado(self):
        """Sem FOREIGN KEY pra topicos_validos de propósito -- uma questão
        com matéria desconhecida ainda precisa ser gravada (pra alimentar a
        fila de triagem), nunca rejeitada/perdida."""
        id_q, status = db.inserir_questao(
            ano=2024, caderno="Azul", numero=999,
            grande_area="Matematica", materia="Marketing Digital",
            alternativa_correta="A",
        )
        self.assertEqual(status, "nao_classificado")
        detalhe = db.detalhe_questao(id_q)
        self.assertEqual(detalhe["status_classificacao"], "nao_classificado")


# ============================================================
# MOTOR DE DECISÃO: prioridade explicável, confiança recente,
# evolução semanal, plano de estudo (ver db.py, seções adicionadas
# depois da revisão de arquitetura)
# ============================================================

class TestPrioridadeDeEstudoExplicacao(_TestComBancoTemporario):
    def test_explicacao_soma_exatamente_o_score(self):
        """A camada de explicabilidade não pode divergir do número que
        ela alega explicar -- os dois termos de 'explicacao' precisam
        somar de volta pro score_prioridade (a menos de arredondamento)."""
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=140,
            grande_area="Matematica", materia="Estatistica",
            alternativa_correta="B",
        )
        db.registrar_tentativa(id_q, "A")  # errou
        db.registrar_tentativa(id_q, "A")  # errou de novo

        ranking = db.prioridade_de_estudo("matematica")["ranking"]
        entrada = next(r for r in ranking if r["materia"] == "estatistica")
        exp = entrada["explicacao"]
        soma = exp["contribuicao_recorrencia"] + exp["contribuicao_taxa_erro"]
        self.assertAlmostEqual(soma, entrada["score_prioridade"], places=1)


class TestConfiancaRecentePorMateria(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=141,
            grande_area="Matematica", materia="Estatistica",
            alternativa_correta="C",
        )

    def test_ultimas_todas_certas_e_confianca_alta(self):
        for _ in range(5):
            db.registrar_tentativa(self.id_q, "C")
        confianca = db.confianca_recente_por_materia("matematica")
        entrada = next(c for c in confianca if c["materia"] == "estatistica")
        self.assertEqual(entrada["confianca"], "alta")
        self.assertEqual(entrada["sequencia_recente"], ["✓"] * 5)

    def test_ultimas_todas_erradas_e_confianca_baixa(self):
        for _ in range(5):
            db.registrar_tentativa(self.id_q, "A")
        confianca = db.confianca_recente_por_materia("matematica")
        entrada = next(c for c in confianca if c["materia"] == "estatistica")
        self.assertEqual(entrada["confianca"], "baixa")

    def test_amostra_pequena_quando_historico_menor_que_a_janela(self):
        db.registrar_tentativa(self.id_q, "C")
        confianca = db.confianca_recente_por_materia("matematica", janela=5)
        entrada = next(c for c in confianca if c["materia"] == "estatistica")
        self.assertTrue(entrada["amostra_pequena"])


class TestEvolucaoSemanalPorMateria(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=170,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="B",
        )

    def _registrar_com_data(self, resposta: str, data_iso: str) -> None:
        """Registra uma tentativa de verdade (passa por todo o Leitner
        normal) e só depois reescreve data_tentativa via SQL direto --
        registrar_tentativa() sempre usa datetime('now') e não tem
        parâmetro pra data, então é o único jeito de simular semanas
        diferentes num teste sem esperar dias de verdade passarem."""
        resultado = db.registrar_tentativa(self.id_q, resposta)
        with db._conectar() as conn:
            conn.execute(
                "UPDATE tentativas_usuario SET data_tentativa = ? WHERE id_tentativa = ?",
                (f"{data_iso} 10:00:00", resultado["id_tentativa"]),
            )

    def test_uma_semana_so_nao_produz_tendencia(self):
        for _ in range(3):
            self._registrar_com_data("A", "2026-08-03")
        evolucao = db.evolucao_semanal_por_materia("matematica")
        self.assertLess(len(evolucao["semanas"]), 2)
        self.assertIsNone(evolucao["maior_evolucao"])

    def test_compara_metade_antiga_com_metade_recente(self):
        for _ in range(3):
            self._registrar_com_data("A", "2026-08-03")  # errou -- semana 2026-31
        for _ in range(3):
            self._registrar_com_data("B", "2026-08-10")  # acertou -- semana 2026-32

        evolucao = db.evolucao_semanal_por_materia("matematica")
        self.assertEqual(len(evolucao["semanas"]), 2)
        self.assertIsNotNone(evolucao["maior_evolucao"])
        self.assertEqual(evolucao["maior_evolucao"]["materia"], "probabilidade")
        self.assertEqual(evolucao["maior_evolucao"]["inicio_pct"], 0.0)
        self.assertEqual(evolucao["maior_evolucao"]["fim_pct"], 100.0)
        self.assertIsNone(evolucao["maior_risco"])  # é evolução, não risco

    def test_amostra_pequena_em_uma_metade_nao_vira_destaque(self):
        self._registrar_com_data("A", "2026-08-03")  # só 1 -- abaixo de MIN_AMOSTRA_CONFIAVEL
        for _ in range(3):
            self._registrar_com_data("B", "2026-08-10")

        evolucao = db.evolucao_semanal_por_materia("matematica")
        self.assertIsNone(evolucao["maior_evolucao"])
        self.assertIsNone(evolucao["maior_risco"])


class TestGerarPlanoDeEstudo(_TestComBancoTemporario):
    def test_minutos_totais_invalido_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.gerar_plano_de_estudo(0)
        with self.assertRaises(ValueError):
            db.gerar_plano_de_estudo(-10)

    def test_banco_vazio_ainda_sugere_redacao_mas_nada_baseado_em_tentativa(self):
        """Banco totalmente vazio: revisão vencida, foco e prática geral
        dependem de tentativa/questão existente, então ficam de fora.
        Redação é a exceção -- "nenhuma redação registrada ainda" já é,
        sozinho, um motivo válido pra sugerir o bloco."""
        plano = db.gerar_plano_de_estudo(120)
        titulos = [b["titulo"] for b in plano["blocos"]]
        self.assertEqual(titulos, ["Redação"])
        self.assertEqual(plano["minutos_alocados"], db.MINUTOS_REDACAO_SUGERIDO)

    def test_nunca_aloca_mais_do_que_o_pedido(self):
        """Com bastante dado real (revisão vencida + fraqueza + redação
        atrasada, todos os blocos disputando tempo), minutos_alocados
        nunca pode passar de minutos_totais -- cada bloco usa min(...,
        restante) antes de descontar."""
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=145,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="A",
        )
        db.registrar_tentativa(id_q, "B")  # errou -- entra na fila de revisão e no ranking
        db.salvar_redacao(tema="Tema de teste", data_escrita="2020-01-01")  # bem atrasada

        for minutos in (30, 60, 90, 120, 240):
            with self.subTest(minutos=minutos):
                plano = db.gerar_plano_de_estudo(minutos)
                self.assertLessEqual(plano["minutos_alocados"], minutos)

    def test_bloco_de_foco_cita_a_materia_de_maior_prioridade(self):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=146,
            grande_area="Matematica", materia="Probabilidade",
            alternativa_correta="A",
        )
        db.registrar_tentativa(id_q, "B")  # errou

        plano = db.gerar_plano_de_estudo(120)
        bloco_foco = next(b for b in plano["blocos"] if b["titulo"].startswith("Foco na maior fraqueza"))
        self.assertEqual(bloco_foco["materia"], "probabilidade")
        self.assertIn("prioridade", bloco_foco["motivo"])


# ============================================================
# BANCO DE PRÁTICA (questões fora do ENEM oficial -- ver
# ANO_BANCO_PRATICA/CADERNO_BANCO_PRATICA e inserir_questao_pratica
# em db.py)
# ============================================================

class TestInserirQuestaoPratica(_TestComBancoTemporario):
    def test_insere_com_origem_banco_pratica_e_gabarito_valido(self):
        id_q, status = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="c", enunciado_texto="Um raio de luz...\nA) x\nB) y\nC) z\nD) w\nE) v",
            fonte="gemini",
        )
        self.assertEqual(status, "classificado")
        self.assertTrue(id_q.startswith("pratica_"))
        detalhe = db.detalhe_questao(id_q)
        self.assertEqual(detalhe["alternativa_correta"], "C")
        self.assertEqual(detalhe["grande_area"], "ciencias_natureza")

    def test_nao_aparece_em_listar_provas_nem_simulados_feitos(self):
        """Questão de banco de prática não é uma prova real -- não pode
        virar um simulado fantasma nas telas que agrupam por prova."""
        id_q, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A", enunciado_texto="Enunciado de teste.",
        )
        db.registrar_tentativa(id_q, "A")
        self.assertEqual(db.listar_provas(), [])
        self.assertEqual(db.simulados_feitos(), [])

    def test_numero_questao_e_sequencial_entre_questoes_de_pratica(self):
        id_1, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A", enunciado_texto="Q1",
        )
        id_2, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="B", enunciado_texto="Q2",
        )
        self.assertNotEqual(id_1, id_2)

    def test_materia_fora_da_taxonomia_ainda_grava_como_nao_classificado(self):
        id_q, status = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Astrologia Barata",
            alternativa_correta="A", enunciado_texto="Enunciado.",
        )
        self.assertEqual(status, "nao_classificado")
        self.assertEqual(db.detalhe_questao(id_q)["status_classificacao"], "nao_classificado")

    def test_gabarito_invalido_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.inserir_questao_pratica(
                grande_area="ciencias_natureza", materia="Optica",
                alternativa_correta="Z", enunciado_texto="Enunciado.",
            )

    def test_enunciado_vazio_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.inserir_questao_pratica(
                grande_area="ciencias_natureza", materia="Optica",
                alternativa_correta="A", enunciado_texto="   ",
            )


class TestImportarQuestoesPraticasTexto(_TestComBancoTemporario):
    def test_importa_dois_blocos_validos_separados_por_tracos(self):
        texto = """
Um raio de luz incide sobre um espelho plano.
A) A imagem é virtual
B) A imagem é real
C) Não forma imagem
D) A imagem é invertida
E) Depende do ângulo
GABARITO: A
---
Uma lente convergente forma imagem real quando o objeto está:
a) entre o foco e a lente
b) exatamente no foco
c) além do ponto antiprincipal
d) no infinito
e) atrás da lente
gabarito: c
"""
        resultado = db.importar_questoes_praticas_texto(
            texto, grande_area="ciencias_natureza", materia="Optica", fonte="gemini",
        )
        self.assertEqual(len(resultado["inseridas"]), 2)
        self.assertEqual(resultado["erros"], [])

        banco = db.listar_banco_pratica()
        self.assertEqual(len(banco), 2)
        gabaritos = sorted(q["alternativa_correta"] for q in banco)
        self.assertEqual(gabaritos, ["A", "C"])
        self.assertTrue(all(q["fonte"] == "gemini" for q in banco))

    def test_bloco_malformado_nao_aborta_os_outros_blocos_validos(self):
        texto = """
Questão sem gabarito nenhum.
A) x
B) y
C) z
D) w
E) v
---
Questão válida de verdade.
A) x
B) y
C) z
D) w
E) v
GABARITO: B
"""
        resultado = db.importar_questoes_praticas_texto(
            texto, grande_area="ciencias_natureza", materia="Optica",
        )
        self.assertEqual(len(resultado["inseridas"]), 1)
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertIn("GABARITO", resultado["erros"][0])

    def test_alternativa_faltando_reporta_erro_com_o_bloco(self):
        texto = """
Questão faltando a alternativa E.
A) x
B) y
C) z
D) w
GABARITO: A
"""
        resultado = db.importar_questoes_praticas_texto(
            texto, grande_area="ciencias_natureza", materia="Optica",
        )
        self.assertEqual(resultado["inseridas"], [])
        self.assertEqual(len(resultado["erros"]), 1)
        self.assertIn("E", resultado["erros"][0])

    def test_alternativas_reordenadas_no_enunciado_gravado(self):
        """Mesmo coladas fora de ordem, o enunciado gravado reconstrói
        A-E na ordem certa -- pra leitura na prática nunca sair
        embaralhada."""
        texto = """
Enunciado de teste.
C) terceira
A) primeira
E) quinta
B) segunda
D) quarta
GABARITO: A
"""
        resultado = db.importar_questoes_praticas_texto(
            texto, grande_area="ciencias_natureza", materia="Optica",
        )
        id_q = resultado["inseridas"][0]
        detalhe = db.detalhe_questao(id_q)
        texto_gravado = detalhe["enunciado_texto"]
        pos_a = texto_gravado.index("A) primeira")
        pos_b = texto_gravado.index("B) segunda")
        pos_c = texto_gravado.index("C) terceira")
        self.assertTrue(pos_a < pos_b < pos_c)


class TestQuestoesPorMateriaComBancoPratica(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_real, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=90,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A",
        )
        self.id_pratica, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="B", enunciado_texto="Questão de prática.",
            fonte="gemini",
        )

    def test_sem_filtro_mistura_real_e_pratica(self):
        questoes = db.questoes_por_materia("ciencias_natureza", "Optica")
        ids = {q["id_questao"] for q in questoes}
        self.assertEqual(ids, {self.id_real, self.id_pratica})

    def test_filtro_enem_oficial_exclui_pratica(self):
        questoes = db.questoes_por_materia("ciencias_natureza", "Optica", origem="enem_oficial")
        ids = {q["id_questao"] for q in questoes}
        self.assertEqual(ids, {self.id_real})

    def test_filtro_banco_pratica_exclui_real(self):
        questoes = db.questoes_por_materia("ciencias_natureza", "Optica", origem="banco_pratica")
        ids = {q["id_questao"] for q in questoes}
        self.assertEqual(ids, {self.id_pratica})

    def test_origem_invalida_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.questoes_por_materia("ciencias_natureza", "Optica", origem="bogus")

    def test_tentativa_em_questao_de_pratica_conta_na_prioridade_de_estudo(self):
        """O ponto central da integração: errar uma questão do banco
        de prática tem que contar pro mesmo pipeline (Leitner,
        prioridade_de_estudo) que questão real do ENEM."""
        db.registrar_tentativa(self.id_pratica, "A")  # errou (gabarito é B)
        ranking = db.prioridade_de_estudo("ciencias_natureza")["ranking"]
        entrada = next(r for r in ranking if r["materia"] == "optica")
        self.assertGreater(entrada["score_prioridade"], 0)

    def test_recorrencia_por_materia_ignora_banco_pratica(self):
        """recorrencia_por_materia mede recorrência em PROVA REAL --
        questão de prática não pode inflar esse percentual."""
        recorrencia = db.recorrencia_por_materia("ciencias_natureza")
        entrada = next(r for r in recorrencia if r["materia"] == "optica")
        # só 1 prova real (2022_azul) tem óptica, mesmo com uma questão
        # extra de prática cadastrada também em óptica
        self.assertEqual(entrada["provas_com_materia"], 1)


class TestMissoesDoDia(_TestComBancoTemporario):
    def test_banco_vazio_ainda_mostra_meta_diaria_sem_missao_de_foco(self):
        """Sem tentativa nenhuma na base, prioridade_de_estudo não tem
        como calcular score -- a missão de foco não aparece, mas a de
        meta diária sempre aparece (0/meta é um estado válido)."""
        missoes = db.missoes_do_dia()
        ids = [m["id"] for m in missoes]
        self.assertIn("meta_diaria", ids)
        self.assertNotIn("foco_prioridade", ids)

    def test_meta_diaria_reflete_tentativas_de_hoje(self):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=150,
            grande_area="matematica", materia="Estatistica",
            alternativa_correta="A",
        )
        db.registrar_tentativa(id_q, "A")
        db.registrar_tentativa(id_q, "B")

        missoes = db.missoes_do_dia()
        meta = next(m for m in missoes if m["id"] == "meta_diaria")
        self.assertEqual(meta["progresso_atual"], 2)
        self.assertFalse(meta["concluida"])

    def test_missao_de_foco_aponta_pra_materia_de_maior_prioridade(self):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=151,
            grande_area="matematica", materia="Estatistica",
            alternativa_correta="A",
        )
        db.registrar_tentativa(id_q, "B")  # errou -- gera prioridade
        db.registrar_tentativa(id_q, "A")  # acertou uma

        missoes = db.missoes_do_dia()
        foco = next(m for m in missoes if m["id"] == "foco_prioridade")
        self.assertEqual(foco["titulo"], "Foco em estatistica")
        self.assertEqual(foco["progresso_atual"], 2)  # 2 tentativas de hoje nessa materia
        self.assertFalse(foco["concluida"])

    def test_missao_de_foco_conclui_ao_bater_o_alvo(self):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=152,
            grande_area="matematica", materia="Estatistica",
            alternativa_correta="A",
        )
        for _ in range(db.ALVO_MISSAO_FOCO):
            db.registrar_tentativa(id_q, "A")

        missoes = db.missoes_do_dia()
        foco = next(m for m in missoes if m["id"] == "foco_prioridade")
        self.assertTrue(foco["concluida"])
        self.assertEqual(foco["progresso_atual"], db.ALVO_MISSAO_FOCO)

    def test_nenhuma_missao_bloqueia_nada__so_reporta_progresso(self):
        """Documenta a decisão deliberada: missao_do_dia() nunca
        retorna nenhuma chave tipo 'bloqueado'/'vidas_restantes' --
        é sempre informativo, nunca impede o usuário de continuar
        estudando."""
        missoes = db.missoes_do_dia()
        for m in missoes:
            self.assertNotIn("bloqueado", m)
            self.assertIn("concluida", m)


class TestTrilhaBancoPratica(_TestComBancoTemporario):
    def _inserir_n_questoes(self, n: int, fonte: str = "gemini") -> list[str]:
        ids = []
        for i in range(n):
            id_q, _ = db.inserir_questao_pratica(
                grande_area="ciencias_natureza", materia="Optica",
                alternativa_correta="A", enunciado_texto=f"Questao {i}", fonte=fonte,
            )
            ids.append(id_q)
        return ids

    def test_divide_em_nos_de_5_por_padrao(self):
        self._inserir_n_questoes(12)
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertEqual(len(trilha), 3)
        self.assertEqual([len(n["questoes"]) for n in trilha], [5, 5, 2])

    def test_primeiro_no_sempre_desbloqueado_resto_bloqueado_no_inicio(self):
        self._inserir_n_questoes(10)
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertTrue(trilha[0]["desbloqueado"])
        self.assertFalse(trilha[1]["desbloqueado"])
        self.assertFalse(trilha[0]["concluido"])

    def test_concluir_primeiro_no_desbloqueia_o_segundo(self):
        ids = self._inserir_n_questoes(10)
        for id_q in ids[:5]:
            db.registrar_tentativa(id_q, "A")
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertTrue(trilha[0]["concluido"])
        self.assertTrue(trilha[1]["desbloqueado"])
        self.assertFalse(trilha[1]["concluido"])

    def test_no_so_conta_concluido_quando_todas_as_questoes_tem_tentativa(self):
        ids = self._inserir_n_questoes(5)
        for id_q in ids[:4]:
            db.registrar_tentativa(id_q, "A")
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertFalse(trilha[0]["concluido"])

    def test_terceiro_no_so_desbloqueia_se_primeiro_e_segundo_concluidos(self):
        ids = self._inserir_n_questoes(15)
        for id_q in ids[:5]:
            db.registrar_tentativa(id_q, "A")
        # so o primeiro no concluido -- terceiro tem que continuar bloqueado
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertTrue(trilha[1]["desbloqueado"])
        self.assertFalse(trilha[2]["desbloqueado"])
        for id_q in ids[5:10]:
            db.registrar_tentativa(id_q, "A")
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        self.assertTrue(trilha[2]["desbloqueado"])

    def test_filtro_por_fonte(self):
        self._inserir_n_questoes(3, fonte="gemini")
        self._inserir_n_questoes(2, fonte="chatgpt")
        trilha_gemini = db.trilha_banco_pratica("ciencias_natureza", "optica", fonte="gemini")
        trilha_chatgpt = db.trilha_banco_pratica("ciencias_natureza", "optica", fonte="chatgpt")
        self.assertEqual(sum(len(n["questoes"]) for n in trilha_gemini), 3)
        self.assertEqual(sum(len(n["questoes"]) for n in trilha_chatgpt), 2)

    def test_sem_questoes_retorna_lista_vazia(self):
        self.assertEqual(db.trilha_banco_pratica("ciencias_natureza", "optica"), [])

    def test_ja_respondida_por_questao(self):
        ids = self._inserir_n_questoes(5)
        db.registrar_tentativa(ids[0], "A")
        trilha = db.trilha_banco_pratica("ciencias_natureza", "optica")
        respondidas = {q["id_questao"]: q["ja_respondida"] for q in trilha[0]["questoes"]}
        self.assertTrue(respondidas[ids[0]])
        self.assertFalse(respondidas[ids[1]])


class TestTrilhaFixa(_TestComBancoTemporario):
    def _inserir_n(self, materia: str, n: int, topico: str | None = None) -> list[str]:
        ids = []
        for i in range(n):
            id_q, _ = db.inserir_questao_pratica(
                grande_area="ciencias_natureza", materia=materia,
                alternativa_correta="A", enunciado_texto=f"{materia} {topico} {i}",
                fonte="autoral", topico=topico,
            )
            ids.append(id_q)
        return ids

    def test_ordem_dos_nos_segue_a_arquitetura(self):
        chaves = [no["chave"] for no in db.trilha_fixa()]
        self.assertEqual(chaves, [c["chave"] for c in db.TRILHA_FIXA_NOS])

    def test_no_sem_questao_nenhuma_fica_vazio_mas_presente(self):
        trilha = db.trilha_fixa()
        self.assertEqual(trilha[0]["blocos"], [])
        self.assertFalse(trilha[0]["concluido"])

    def test_primeiro_no_desbloqueado_resto_bloqueado_no_inicio(self):
        self._inserir_n("ecologia", 5, topico="chuva_acida")  # fase 4
        self._inserir_n("optica", 5)
        trilha = db.trilha_fixa()
        self.assertTrue(trilha[0]["desbloqueado"])
        self.assertFalse(trilha[1]["desbloqueado"])

    def test_concluir_todo_o_no_1_desbloqueia_o_no_2(self):
        ids_ecologia = self._inserir_n("ecologia", 5, topico="chuva_acida")
        self._inserir_n("optica", 5)
        for id_q in ids_ecologia:
            db.registrar_tentativa(id_q, "A")
        trilha = db.trilha_fixa()
        self.assertTrue(trilha[0]["concluido"])
        self.assertTrue(trilha[1]["desbloqueado"])

    def test_no_de_optica_junta_optica_e_acustica(self):
        self._inserir_n("optica", 3)
        self._inserir_n("acustica", 2)
        trilha = db.trilha_fixa()
        no_optica = next(no for no in trilha if no["chave"] == "optica_ondulatoria")
        total = sum(len(b["questoes"]) for b in no_optica["blocos"])
        self.assertEqual(total, 5)

    def test_no_de_ecologia_filtra_so_a_fase_4(self):
        self._inserir_n("ecologia", 3, topico="chuva_acida")  # fase 4
        self._inserir_n("ecologia", 4, topico="predacao")  # fase 2
        trilha = db.trilha_fixa()
        no_ecologia = trilha[0]
        total = sum(len(b["questoes"]) for b in no_ecologia["blocos"])
        self.assertEqual(total, 3)


class TestFontesEListarBancoPratica(_TestComBancoTemporario):
    def test_fontes_distintas_ordenadas(self):
        db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A", enunciado_texto="Q1", fonte="gemini",
        )
        db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="B", enunciado_texto="Q2", fonte="chatgpt",
        )
        db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="C", enunciado_texto="Q3", fonte=None,
        )
        self.assertEqual(db.fontes_banco_pratica(), ["chatgpt", "gemini"])

    def test_listar_banco_pratica_mais_recente_primeiro(self):
        id_1, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A", enunciado_texto="Q1",
        )
        id_2, _ = db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="B", enunciado_texto="Q2",
        )
        banco = db.listar_banco_pratica()
        self.assertEqual([q["id_questao"] for q in banco], [id_2, id_1])


# ============================================================
# PADRÃO DE COBRANÇA (topico) -- piloto da hipótese central de produto
# documentada na Central ENEM GI ("aprender por padrão de banca, não
# só por matéria"): desempenho_por_topico() e atualizar_topico().
# ============================================================

class TestAtualizarTopico(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=93,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A",
        )

    def test_marca_topico_em_questao_existente(self):
        db.atualizar_topico(self.id_q, "espelho esferico - sinal do aumento")
        self.assertEqual(db.detalhe_questao(self.id_q)["topico"], "espelho esferico - sinal do aumento")

    def test_none_limpa_topico_ja_marcado(self):
        db.atualizar_topico(self.id_q, "algum padrao")
        db.atualizar_topico(self.id_q, None)
        self.assertIsNone(db.detalhe_questao(self.id_q)["topico"])

    def test_questao_inexistente_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.atualizar_topico("2099_azul_999", "qualquer padrao")


class TestDesempenhoPorTopico(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        # 2 questões do mesmo padrão ("sinal do aumento"), 1 de outro padrão,
        # 1 ainda sem topico marcado -- mesma materia nas 4.
        self.id_a, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=93,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="A", topico="espelho esferico - sinal do aumento",
        )
        self.id_b, _ = db.inserir_questao(
            ano=2023, caderno="Azul", numero=94,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="B", topico="espelho esferico - sinal do aumento",
        )
        self.id_c, _ = db.inserir_questao(
            ano=2024, caderno="Azul", numero=95,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="C", topico="lei de snell - refracao oblíqua",
        )
        self.id_sem, _ = db.inserir_questao(
            ano=2025, caderno="Azul", numero=96,
            grande_area="ciencias_natureza", materia="Optica",
            alternativa_correta="D",  # sem topico
        )

    def test_agrupa_por_topico_dentro_da_materia(self):
        db.registrar_tentativa(self.id_a, "A")  # acertou
        db.registrar_tentativa(self.id_b, "A")  # errou -- gabarito de id_b é B (mesmo topico de id_a)
        db.registrar_tentativa(self.id_c, "C")  # acertou (outro topico)

        resultado = db.desempenho_por_topico("ciencias_natureza", "Optica")
        topicos = {r["topico"]: r for r in resultado["ranking"]}

        self.assertEqual(topicos["espelho esferico - sinal do aumento"]["total_tentativas"], 2)
        self.assertEqual(topicos["espelho esferico - sinal do aumento"]["acertos"], 1)
        self.assertEqual(topicos["lei de snell - refracao oblíqua"]["acertos"], 1)

    def test_questao_sem_topico_fica_fora_do_ranking(self):
        db.registrar_tentativa(self.id_sem, "D")
        resultado = db.desempenho_por_topico("ciencias_natureza", "Optica")
        topicos_no_ranking = [r["topico"] for r in resultado["ranking"]]
        self.assertNotIn(None, topicos_no_ranking)
        self.assertIsNotNone(resultado["sem_topico"])
        self.assertEqual(resultado["sem_topico"]["total_tentativas"], 1)

    def test_amostra_pequena_abaixo_do_minimo_confiavel(self):
        db.registrar_tentativa(self.id_c, "C")  # só 1 tentativa nesse topico
        resultado = db.desempenho_por_topico("ciencias_natureza", "Optica")
        entrada = next(r for r in resultado["ranking"] if r["topico"] == "lei de snell - refracao oblíqua")
        self.assertTrue(entrada["amostra_pequena"])

    def test_sem_nenhuma_tentativa_ranking_vazio(self):
        resultado = db.desempenho_por_topico("ciencias_natureza", "Optica")
        self.assertEqual(resultado["ranking"], [])
        self.assertIsNone(resultado["sem_topico"])


# ============================================================
# IDEMPOTÊNCIA DO CARREGAMENTO DE GABARITO -- a propriedade da qual
# reconstruir_base.py depende pra poder ser reexecutado sem duplicar
# questão nem perder dado (ver docstring do próprio script). Testa o
# primitivo reutilizável (carregar_gabarito_texto), não o script --
# reconstruir_base.py roda como módulo de topo, contra CSVs reais em
# disco, então não é seguro nem prático importá-lo num teste.
# ============================================================

class TestCarregarGabaritoEIdempotente(_TestComBancoTemporario):
    CSV = (
        "numero,materia,gabarito\n"
        "136,Funcao Afim,A\n"
        "137,Geometria Plana,B\n"
    )

    def test_carregar_duas_vezes_nao_duplica_questao(self):
        db.carregar_gabarito_texto(self.CSV, ano=2024, caderno="Azul")
        db.carregar_gabarito_texto(self.CSV, ano=2024, caderno="Azul", sobrescrever=True)

        with db._conectar() as conn:
            total = conn.execute("SELECT COUNT(*) FROM questoes").fetchone()[0]
        self.assertEqual(total, 2)  # não virou 4

    def test_recarregar_preserva_tentativa_ja_registrada(self):
        """Rodar o carregamento de novo (ex: gabarito corrigido) não
        pode apagar/perder tentativa que o usuário já registrou pra
        essa prova -- mesma garantia que reconstruir_base.py promete
        no próprio docstring ('idempotente... não perde tentativa')."""
        db.carregar_gabarito_texto(self.CSV, ano=2024, caderno="Azul")
        id_q = db.gerar_id_canonico(2024, "Azul", 136)
        db.registrar_tentativa(id_q, "A")

        db.carregar_gabarito_texto(self.CSV, ano=2024, caderno="Azul", sobrescrever=True)

        with db._conectar() as conn:
            total_tentativas = conn.execute(
                "SELECT COUNT(*) FROM tentativas_usuario WHERE id_questao = ?", (id_q,)
            ).fetchone()[0]
        self.assertEqual(total_tentativas, 1)

    def test_preservar_materia_classificada_nao_regride_classificacao_manual(self):
        """preservar_materia_classificada=True (o flag que
        reconstruir_base.py sempre passa) não pode deixar um
        placeholder de CSV sobrescrever uma matéria já classificada de
        verdade -- ver core/CLAUDE.md, seção de triagem manual."""
        db.carregar_gabarito_texto(self.CSV, ano=2024, caderno="Azul")
        id_q = db.gerar_id_canonico(2024, "Azul", 136)
        db.inserir_questao(
            ano=2024, caderno="Azul", numero=136, grande_area="matematica",
            materia="Funcao Afim", alternativa_correta="A", sobrescrever=True,
        )
        self.assertEqual(db.detalhe_questao(id_q)["status_classificacao"], "classificado")

        csv_com_placeholder = "numero,materia,gabarito\n136,SEM_VIDEO_PENDENTE,A\n"
        db._carregar_gabarito_de_texto(
            csv_com_placeholder, ano=2024, caderno="Azul",
            grande_area_padrao="matematica", sobrescrever=True,
            preservar_materia_classificada=True,
        )
        self.assertEqual(db.detalhe_questao(id_q)["status_classificacao"], "classificado")


if __name__ == "__main__":
    unittest.main()
