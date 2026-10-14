"""test_dicionario_dados.py — garante que o catálogo de dados acompanha o schema.

Se uma coluna ou tabela nova entrar no banco (schema.sql ou migração em
db.inicializar_banco) sem descrição em gerar_dicionario_dados.DESCRICOES,
o teste quebra no CI em vez de o dicionário ficar desatualizado em silêncio.
Não toca no enem.db: a estrutura vem de um banco temporário e o perfil é
testado contra um banco sintético.

Rodar (de dentro de core/):
    python -m unittest test_dicionario_dados
"""
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import gerar_dicionario_dados as gd

# Um banco temporário com schema + migrações, montado uma vez para o arquivo todo.
ESTRUTURA = gd.estrutura_do_schema()


class TestCatalogoCobreSchema(unittest.TestCase):
    estrutura = ESTRUTURA

    def test_toda_tabela_tem_descricao_e_camada(self):
        for tabela in self.estrutura:
            with self.subTest(tabela=tabela):
                self.assertIn(tabela, gd.DESCRICOES, "tabela nova sem entrada em DESCRICOES")
                self.assertTrue(gd.DESCRICOES[tabela].get("_tabela"))
                self.assertTrue(gd.DESCRICOES[tabela].get("_camada"))

    def test_toda_coluna_tem_descricao(self):
        for tabela, info in self.estrutura.items():
            for col in info["colunas"]:
                with self.subTest(coluna=f"{tabela}.{col['nome']}"):
                    self.assertTrue(gd.DESCRICOES.get(tabela, {}).get(col["nome"]),
                                    "coluna nova sem descrição em DESCRICOES")

    def test_nao_sobra_descricao_de_coluna_que_nao_existe(self):
        for tabela, descricoes in gd.DESCRICOES.items():
            self.assertIn(tabela, self.estrutura, f"DESCRICOES cita tabela inexistente: {tabela}")
            existentes = {c["nome"] for c in self.estrutura[tabela]["colunas"]}
            for coluna in descricoes:
                if not coluna.startswith("_"):
                    with self.subTest(coluna=f"{tabela}.{coluna}"):
                        self.assertIn(coluna, existentes)

    def test_colunas_de_migracao_aparecem(self):
        colunas = {c["nome"] for c in self.estrutura["tentativas_usuario"]["colunas"]}
        self.assertTrue({"tipo_erro", "duracao_segundos"} <= colunas)

    def test_le_chave_estrangeira_e_dominio_do_check(self):
        cols = {c["nome"]: c for c in self.estrutura["tentativas_usuario"]["colunas"]}
        self.assertEqual(cols["id_questao"]["fk"], "questoes.id_questao")
        self.assertEqual(cols["resultado"]["dominio"], ["acertou", "errou"])
        self.assertTrue(cols["id_tentativa"]["pk"])
        self.assertEqual(cols["resposta_escolhida"]["dominio"], ["A", "B", "C", "D", "E", "NULL"])

    def test_pk_de_texto_nao_conta_como_obrigatoria(self):
        """No SQLite só INTEGER PRIMARY KEY impede NULL; TEXT PRIMARY KEY aceita."""
        questoes = {c["nome"]: c for c in self.estrutura["questoes"]["colunas"]}
        self.assertFalse(questoes["id_questao"]["obrigatoria"])
        self.assertTrue(questoes["ano"]["obrigatoria"])
        tentativas = {c["nome"]: c for c in self.estrutura["tentativas_usuario"]["colunas"]}
        self.assertTrue(tentativas["id_tentativa"]["obrigatoria"])

    def test_doc_commitado_cobre_todas_as_colunas(self):
        """Pega quem mudou o schema e DESCRICOES mas esqueceu de rodar o script."""
        md = gd.SAIDA.read_text(encoding="utf-8")
        for tabela, info in self.estrutura.items():
            self.assertIn(f"### `{tabela}`", md)
            for col in info["colunas"]:
                with self.subTest(coluna=f"{tabela}.{col['nome']}"):
                    self.assertIn(f"| `{col['nome']}` |", md.split(f"### `{tabela}`")[1].split("### ")[0])


class TestPerfilEMarkdown(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.estrutura = {"t": {"colunas": [
            {"nome": "a", "tipo": "INTEGER", "obrigatoria": True, "pk": True, "fk": None, "dominio": None},
            {"nome": "b", "tipo": "TEXT", "obrigatoria": False, "pk": False, "fk": None, "dominio": None},
            {"nome": "c", "tipo": "TEXT", "obrigatoria": False, "pk": False, "fk": None, "dominio": None},
        ]}}
        self.caminho = Path(self.pasta) / "sintetico.db"
        with closing(sqlite3.connect(self.caminho)) as conn:
            conn.execute("CREATE TABLE t (a INTEGER PRIMARY KEY, b TEXT, c TEXT)")
            # 20 linhas (= MIN_LINHAS_ALERTA): b metade nula, c toda nula.
            conn.executemany("INSERT INTO t VALUES (?, ?, NULL)",
                             [(i, "x" if i % 2 else None) for i in range(1, 21)])
            conn.commit()

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_perfil_conta_nulos_e_distintos(self):
        p = gd.perfil_do_banco(self.caminho, self.estrutura)["t"]
        self.assertEqual(p["linhas"], 20)
        self.assertEqual(p["colunas"]["b"], {"nulos": 10, "pct_nulos": 50.0, "distintos": 1})
        self.assertEqual(p["colunas"]["c"]["nulos"], 20)

    def test_alerta_coluna_vazia_e_quase_vazia(self):
        alertas = gd.alertas_de_qualidade(gd.perfil_do_banco(self.caminho, self.estrutura))
        self.assertTrue(any("`t.c`" in a and "100%" in a for a in alertas))
        self.assertTrue(any("`t.b`" in a and "50%" in a for a in alertas))
        self.assertFalse(any("`t.a`" in a for a in alertas))

    def test_tabela_pequena_nao_gera_alerta(self):
        with closing(sqlite3.connect(self.caminho)) as conn:
            conn.execute("DELETE FROM t WHERE a > 5")
            conn.commit()
        self.assertEqual(gd.alertas_de_qualidade(gd.perfil_do_banco(self.caminho, self.estrutura)), [])

    def test_banco_nao_migrado_nao_quebra_o_perfil(self):
        estrutura = {"t": {"colunas": self.estrutura["t"]["colunas"] + [
            {"nome": "nova", "tipo": "TEXT", "obrigatoria": False, "pk": False, "fk": None, "dominio": None}]}}
        perfil = gd.perfil_do_banco(self.caminho, estrutura)
        self.assertNotIn("nova", perfil["t"]["colunas"])
        md = gd.gerar_markdown(estrutura, perfil)
        self.assertIn("| `nova` |", md)

    def test_barra_vertical_na_descricao_nao_quebra_a_tabela(self):
        self.assertEqual(gd._cel("a | b\nc"), "a \\| b c")

    def test_markdown_tem_todas_as_tabelas_e_o_diagrama(self):
        md = gd.gerar_markdown(ESTRUTURA)
        self.assertIn("```mermaid", md)
        for tabela in ESTRUTURA:
            self.assertIn(f"### `{tabela}`", md)


if __name__ == "__main__":
    unittest.main()
