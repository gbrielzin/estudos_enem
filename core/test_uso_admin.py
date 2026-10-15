"""
test_uso_admin.py — testes do resumo de uso do painel de admin (uso_admin.py).

Só banco sintético: cada teste cria bancos pequenos numa pasta temporária,
com a tabela tentativas_usuario mínima (as colunas que o painel lê) e
datas escolhidas a dedo. Nunca toca em enem.db nem em banco de ninguém.

Rodar (de dentro de core/):
    python -m unittest test_uso_admin -v
"""
import hashlib
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date
from pathlib import Path

import uso_admin

HOJE = date(2026, 10, 20)


class TestResumoUso(unittest.TestCase):
    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp(prefix="enem_teste_uso_"))

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def _banco(self, nome, tentativas):
        """tentativas: lista de (data_tentativa, id_questao, resultado)."""
        with closing(sqlite3.connect(self.pasta / f"{nome}.db")) as conn:
            conn.execute(
                "CREATE TABLE tentativas_usuario (id_tentativa INTEGER PRIMARY KEY, id_questao TEXT, data_tentativa TEXT, resultado TEXT)"
            )
            conn.executemany(
                "INSERT INTO tentativas_usuario (data_tentativa, id_questao, resultado) VALUES (?, ?, ?)", tentativas
            )
            conn.commit()

    def _eventos(self, nome, eventos):
        """eventos: lista de (criado_em, tipo, aparelho). Cria a tabela no banco já existente."""
        with closing(sqlite3.connect(self.pasta / f"{nome}.db")) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS eventos (id_evento INTEGER PRIMARY KEY, tipo TEXT, tela TEXT, aparelho TEXT, criado_em TEXT)"
            )
            conn.executemany("INSERT INTO eventos (criado_em, tipo, aparelho) VALUES (?, ?, ?)", eventos)
            conn.commit()

    def _por_usuario(self, hoje=HOJE):
        return {r["usuario"]: r for r in uso_admin.resumo_uso(self.pasta, hoje=hoje)}

    def test_contagens_e_acerto(self):
        self._banco("ana", [
            ("2026-10-01 10:00:00", "q1", "acertou"),
            ("2026-10-01 10:05:00", "q2", "errou"),
            ("2026-10-03 21:00:00", "q1", "acertou"),
            ("2026-10-03 21:02:00", "q3", "acertou"),
        ])
        ana = self._por_usuario()["ana"]
        self.assertEqual(ana["primeira_atividade"], "2026-10-01 10:00:00")
        self.assertEqual(ana["ultima_atividade"], "2026-10-03 21:02:00")
        self.assertEqual(ana["tentativas"], 4)
        self.assertEqual(ana["questoes"], 3)  # q1 respondida duas vezes conta uma
        self.assertEqual(ana["taxa_acerto"], 0.75)

    def test_voltou_no_dia_seguinte(self):
        self._banco("ana", [("2026-10-01 23:50:00", "q1", "acertou"), ("2026-10-02 00:10:00", "q2", "errou")])
        ana = self._por_usuario()["ana"]
        self.assertTrue(ana["voltou_d1"])
        self.assertTrue(ana["voltou_d7"])

    def test_voltou_so_no_meio_da_semana(self):
        self._banco("bia", [("2026-10-01 10:00:00", "q1", "acertou"), ("2026-10-05 10:00:00", "q2", "acertou")])
        bia = self._por_usuario()["bia"]
        self.assertFalse(bia["voltou_d1"])
        self.assertTrue(bia["voltou_d7"])

    def test_voltar_depois_da_semana_nao_conta_como_d7(self):
        self._banco("caio", [("2026-10-01 10:00:00", "q1", "acertou"), ("2026-10-09 10:00:00", "q2", "acertou")])
        caio = self._por_usuario()["caio"]
        self.assertFalse(caio["voltou_d1"])
        self.assertFalse(caio["voltou_d7"])

    def test_quem_comecou_agora_ainda_nao_tem_resposta(self):
        # Começou ontem e não voltou hoje: D1 e D7 ainda podem acontecer.
        self._banco("duda", [("2026-10-19 10:00:00", "q1", "acertou")])
        duda = self._por_usuario()["duda"]
        self.assertIsNone(duda["voltou_d1"])
        self.assertIsNone(duda["voltou_d7"])
        # Dois dias depois, D1 já fechou; D7 ainda não.
        duda = self._por_usuario(hoje=date(2026, 10, 21))["duda"]
        self.assertFalse(duda["voltou_d1"])
        self.assertIsNone(duda["voltou_d7"])

    def test_banco_sem_tentativa_aparece_zerado_no_fim(self):
        self._banco("nova", [])
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        resumos = uso_admin.resumo_uso(self.pasta, hoje=HOJE)
        self.assertEqual([r["usuario"] for r in resumos], ["ana", "nova"])
        nova = resumos[1]
        self.assertEqual((nova["tentativas"], nova["questoes"]), (0, 0))
        self.assertIsNone(nova["taxa_acerto"])
        self.assertIsNone(nova["primeira_atividade"])
        self.assertIsNone(nova["voltou_d1"])

    def test_ordem_por_ultima_atividade(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        self._banco("bia", [("2026-10-10 10:00:00", "q1", "acertou")])
        self.assertEqual([r["usuario"] for r in uso_admin.resumo_uso(self.pasta, hoje=HOJE)], ["bia", "ana"])

    def test_nao_altera_o_banco(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        caminho = self.pasta / "ana.db"
        antes = hashlib.sha256(caminho.read_bytes()).hexdigest()
        uso_admin.resumo_uso(self.pasta, hoje=HOJE)
        self.assertEqual(hashlib.sha256(caminho.read_bytes()).hexdigest(), antes)
        self.assertEqual(sorted(p.name for p in self.pasta.iterdir()), ["ana.db"])  # nem -journal, nem -wal

    def test_arquivo_que_nao_e_banco_do_app_nao_derruba_os_outros(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        with closing(sqlite3.connect(self.pasta / "outro.db")) as conn:
            conn.execute("CREATE TABLE qualquer (x)")
        resumos = self._por_usuario()
        self.assertEqual(resumos["ana"]["tentativas"], 1)
        self.assertIn("erro", resumos["outro"])

    def test_com_nomes_so_entram_as_pessoas_configuradas(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        self._banco("ana_backup", [("2026-10-01 10:00:00", "q1", "acertou")])
        resumos = {r["usuario"]: r for r in uso_admin.resumo_uso(self.pasta, ["ana", "bia"], hoje=HOJE)}
        self.assertEqual(set(resumos), {"ana", "bia"})  # o backup fica de fora
        self.assertIn("erro", resumos["bia"])  # configurada, mas o banco ainda não existe
        self.assertEqual(sorted(p.name for p in self.pasta.iterdir()), ["ana.db", "ana_backup.db"])  # não criou bia.db

    def test_data_fora_do_formato_nao_derruba_o_painel(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        self._banco("bia", [("01/10/2026", "q1", "acertou")])
        resumos = self._por_usuario()
        self.assertEqual(resumos["ana"]["tentativas"], 1)
        self.assertIn("erro", resumos["bia"])

    def test_abriu_e_nao_respondeu(self):
        self._banco("irma", [])
        self._eventos("irma", [("2026-10-15 19:00:00", "app_aberto", "Android · Chrome"), ("2026-10-15 19:01:00", "erro", "Android · Chrome")])
        irma = self._por_usuario()["irma"]
        self.assertTrue(irma["abriu_sem_responder"])
        self.assertEqual((irma["aberturas"], irma["erros"], irma["tentativas"]), (1, 1, 0))
        self.assertEqual(irma["aparelho"], "Android · Chrome")
        self.assertEqual(irma["primeira_atividade"], "2026-10-15 19:00:00")
        self.assertIsNone(irma["taxa_acerto"])

    def test_abrir_o_app_conta_como_voltar(self):
        # Respondeu no dia 1 e só abriu o app no dia 2: voltou em D1.
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        self._eventos("ana", [("2026-10-02 08:00:00", "app_aberto", "iPhone · Safari")])
        ana = self._por_usuario()["ana"]
        self.assertTrue(ana["voltou_d1"])
        self.assertFalse(ana["abriu_sem_responder"])
        self.assertEqual(ana["ultima_atividade"], "2026-10-02 08:00:00")

    def test_erro_conta_mas_nao_vira_atividade(self):
        # Erro no dia 2 é o app falhando sozinho, não a pessoa voltando.
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])
        self._eventos("ana", [("2026-10-02 08:00:00", "erro", "Android · Chrome")])
        ana = self._por_usuario()["ana"]
        self.assertEqual(ana["erros"], 1)
        self.assertFalse(ana["voltou_d1"])
        self.assertEqual(ana["ultima_atividade"], "2026-10-01 10:00:00")

    def test_aparelho_e_o_mais_recente(self):
        self._banco("ana", [])
        self._eventos("ana", [("2026-10-01 10:00:00", "app_aberto", "Windows · Chrome"), ("2026-10-03 10:00:00", "app_aberto", "Android · Chrome")])
        self.assertEqual(self._por_usuario()["ana"]["aparelho"], "Android · Chrome")

    def test_banco_antigo_sem_tabela_eventos(self):
        self._banco("ana", [("2026-10-01 10:00:00", "q1", "acertou")])  # sem eventos: banco de antes deste PR
        ana = self._por_usuario()["ana"]
        self.assertEqual((ana["tentativas"], ana["aberturas"], ana["aparelho"]), (1, 0, None))
        self.assertNotIn("erro", ana)

    def test_pasta_que_nao_existe(self):
        self.assertEqual(uso_admin.resumo_uso(self.pasta / "nao_existe", hoje=HOJE), [])


if __name__ == "__main__":
    unittest.main()
