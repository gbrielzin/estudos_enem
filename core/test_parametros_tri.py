"""
test_parametros_tri.py — testes de db.atualizar_parametros_tri(),
db.nivel_tri() e da ligação questão -> item INEP de
importar_parametros_tri.py.

O ITENS_PROVA de verdade (core/inep_itens/) é gitignored, então os testes
escrevem um CSV sintético no mesmo formato numa pasta temporária. Nunca
toca em enem.db (usa a mesma classe-base de banco temporário de test_db).

Rodar (de dentro de core/):
    python -m unittest test_parametros_tri -v
"""
import sqlite3
import unittest
from pathlib import Path

import db
import importar_parametros_tri as tri
from test_db import _TestComBancoTemporario

CABECALHO = "CO_POSICAO;SG_AREA;CO_ITEM;TX_GABARITO;CO_HABILIDADE;IN_ITEM_ABAN;TX_MOTIVO_ABAN;NU_PARAM_A;NU_PARAM_B;NU_PARAM_C;TX_COR;CO_PROVA;TP_LINGUA;IN_ITEM_ADAPTADO"


def _linha(posicao, gabarito, b, cor="AZUL", prova="500", item=None, habilidade="17"):
    item = item or 1000 + posicao
    return f"{posicao};CN;{item};{gabarito};{habilidade};0;;2.0;{b};0.2;{cor};{prova};;0"


class TestNivelTri(unittest.TestCase):
    def test_cortes(self):
        self.assertEqual(db.nivel_tri(0.4), "facil")
        self.assertEqual(db.nivel_tri(db.CORTE_TRI_FACIL), "medio")
        self.assertEqual(db.nivel_tri(db.CORTE_TRI_DIFICIL), "medio")
        self.assertEqual(db.nivel_tri(2.5), "dificil")

    def test_sem_parametro_devolve_none(self):
        self.assertIsNone(db.nivel_tri(None))


class TestAtualizarParametrosTri(_TestComBancoTemporario):
    def test_grava_e_le_de_volta(self):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=93, grande_area="ciencias_natureza",
            materia="Optica", alternativa_correta="A",
        )
        db.atualizar_parametros_tri(id_q, 2.1, 1.7, 0.18, 21)
        with sqlite3.connect(db.DB_PATH) as conn:
            linha = conn.execute(
                "SELECT tri_a, tri_b, tri_c, habilidade, materia FROM questoes WHERE id_questao = ?", (id_q,)
            ).fetchone()
        self.assertEqual(linha, (2.1, 1.7, 0.18, 21, "optica"))

    def test_questao_inexistente_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            db.atualizar_parametros_tri("2099_azul_999", 1.0, 1.0, 0.2, 1)

    def test_migracao_adiciona_colunas_em_banco_antigo(self):
        with sqlite3.connect(db.DB_PATH) as conn:
            for coluna in ("tri_a", "tri_b", "tri_c", "habilidade"):
                conn.execute(f"ALTER TABLE questoes DROP COLUMN {coluna}")
        db.inicializar_banco()
        with sqlite3.connect(db.DB_PATH) as conn:
            colunas = {r[1] for r in conn.execute("PRAGMA table_info(questoes)")}
        self.assertTrue({"tri_a", "tri_b", "tri_c", "habilidade"} <= colunas)


class TestMontarParametros(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.pasta = Path(self._pasta_temp)

    def _questao(self, ano, numero, correta):
        id_q, _ = db.inserir_questao(
            ano=ano, caderno="Azul", numero=numero, grande_area="ciencias_natureza",
            materia="Optica", alternativa_correta=correta,
        )
        return id_q

    def _csv(self, ano, linhas):
        (self.pasta / f"{ano}_ITENS_PROVA_{ano}.csv").write_text(
            "\n".join([CABECALHO, *linhas]), encoding="latin-1"
        )

    def test_liga_pela_posicao_e_escolhe_a_prova_que_bate(self):
        ids = [self._questao(2020, 91 + i, g) for i, g in enumerate("ABCDE")]
        self._csv(2020, [
            # outra prova azul (reaplicação) com gabarito diferente: não pode ganhar
            *[_linha(91 + i, g, 9.9, prova="600") for i, g in enumerate("EEEEE")],
            *[_linha(91 + i, g, 0.5 + i, prova="500") for i, g in enumerate("ABCDE")],
        ])
        a_gravar, relatorio = tri.montar_parametros(self.pasta)
        self.assertEqual({x[0]: x[2] for x in a_gravar}, {ids[i]: 0.5 + i for i in range(5)})
        self.assertIn("CO_PROVA 500 bate 100%", relatorio[0])

    def test_numeracao_deslocada_alinha_pelo_gabarito(self):
        # caso real de 2017: INEP numera CN 1-45, o caderno impresso 91-135
        ids = [self._questao(2017, 91 + i, g) for i, g in enumerate("ABCDE")]
        self._csv(2017, [_linha(1 + i, g, 1.5) for i, g in enumerate("ABCDE")])
        a_gravar, _ = tri.montar_parametros(self.pasta)
        self.assertEqual(sorted(x[0] for x in a_gravar), sorted(ids))

    def test_nao_grava_item_anulado_nem_gabarito_divergente(self):
        ids = [self._questao(2021, 91 + i, g) for i, g in enumerate("ABCDEABCDE")]
        linhas = [_linha(91 + i, g, 1.0) for i, g in enumerate("ABCDEABCDE")]
        linhas[3] = _linha(94, "X", "")  # anulado: sem parâmetro
        self._csv(2021, linhas)
        a_gravar, _ = tri.montar_parametros(self.pasta)
        self.assertEqual(len(a_gravar), 9)
        self.assertNotIn(ids[3], {x[0] for x in a_gravar})

    def test_concordancia_baixa_pula_o_caderno(self):
        for i, g in enumerate("ABCDE"):
            self._questao(2022, 91 + i, g)
        self._csv(2022, [_linha(91 + i, g, 1.0) for i, g in enumerate("EDCBA")])
        a_gravar, relatorio = tri.montar_parametros(self.pasta)
        self.assertEqual(a_gravar, [])
        self.assertIn("pulado", relatorio[0])

    def test_ano_sem_arquivo_inep_nao_quebra(self):
        self._questao(2009, 91, "A")
        a_gravar, relatorio = tri.montar_parametros(self.pasta)
        self.assertEqual(a_gravar, [])
        self.assertIn("pulado", relatorio[0])


if __name__ == "__main__":
    unittest.main()
