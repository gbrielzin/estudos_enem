"""Testes do coleta_redacoes.py com textos sintéticos (nenhum texto de
terceiros entra no repositório). Cada teste imita o layout de uma fonte."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import coleta_redacoes as cr

PARAGRAFO = ("Esta é uma linha comprida de texto sintético que ocupa a largura normal da página toda\n"
             "e continua aqui com mais palavras para parecer justificada no documento original\n")


def redacao_sintetica(marca: str) -> str:
    """Quatro parágrafos; cada um termina numa linha curta com ponto."""
    return "".join(f"{PARAGRAFO}{marca} parágrafo {i} termina aqui.\n" for i in range(1, 5))


class TestUtilidades(unittest.TestCase):
    def test_normalizar_tira_acento_ligadura_e_invisivel(self):
        self.assertEqual(cr.normalizar("Delﬁno​ ÁREA"), "delfino area")

    def test_chave_duplicata_usa_ano_e_dois_primeiros_nomes(self):
        self.assertEqual(cr.chave_duplicata(2023, "Lucas Malta de Carvalho"),
                         cr.chave_duplicata(2023, "LUCAS MALTA"))
        self.assertNotEqual(cr.chave_duplicata(2023, "Lucas Malta"), cr.chave_duplicata(2024, "Lucas Malta"))

    def test_dividir_paragrafos_quebra_em_linha_curta_com_ponto(self):
        pars = cr.dividir_paragrafos(redacao_sintetica("X").splitlines())
        self.assertEqual(len(pars), 4)
        self.assertTrue(pars[0].endswith("parágrafo 1 termina aqui."))

    def test_legibilidade_baixa_em_texto_embaralhado(self):
        self.assertGreater(cr.legibilidade("Texto normal, com acentuação."), 0.9)
        self.assertLess(cr.legibilidade("ҁ҂ҏҎĤĉ޲ҁ҂ҏҎĤĉ"), 0.5)


class TestExtratores(unittest.TestCase):
    def test_cartilha_inep_pega_nome_numerado_e_comentario(self):
        texto = ("1. Ana Teste Silva\n" + redacao_sintetica("A") + "\n" * 4 +
                 "COMENTÁRIO\nA participante demonstra excelente domínio.\n")
        r = cr.extrair_cartilha_inep(texto, 2024)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["autor"], "Ana Teste Silva")
        self.assertEqual(r[0]["enem"], 2023)
        self.assertEqual(r[0]["n_paragrafos"], 4)
        self.assertIn("excelente domínio", r[0]["comentario_inep"])

    def test_cartilha_inep_prefere_o_cabecalho_mais_perto_do_comentario(self):
        texto = ("TEXTOS MOTIVADORES\n" + "linha qualquer\n" * 3 + "Redação de MARIA TESTE\n" +
                 redacao_sintetica("M") + "\n" * 4 + "COMENTÁRIO\nok\n")
        r = cr.extrair_cartilha_inep(texto, 2019)
        self.assertEqual([x["autor"] for x in r], ["Maria Teste"])

    def test_cartilha_inep_descarta_texto_embaralhado(self):
        lixo = "ҁ҂ҏҎĤĉ޲ҁ҂ҏҎĤĉ ҁ҂ҏҎĤĉ޲ҁ҂ҏҎĤĉ ҁ҂ҏҎĤĉ\n" * 20
        texto = "1. Ana Teste Silva\n" + lixo + "COMENTÁRIO\nx\n"
        self.assertEqual(cr.extrair_cartilha_inep(texto, 2024), [])

    def test_redamil_ignora_transcricao_do_sumario(self):
        texto = ("Transcrição\n51\n"  # sumário
                 "Tema:\n\"Tema sintético\"\nEnem Aplicação Regular\n"
                 "João Teste (ele/dele)\n20 anos | Cidade - UF | @joao\nEspelho\n\nTranscrição\n"
                 "\"" + redacao_sintetica("J").rstrip("\n") + "\"\n")
        r = cr.extrair_redamil(texto, 5)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["autor"], "João Teste")  # pronome removido
        self.assertEqual(r[0]["tema"], "Tema sintético")
        self.assertEqual(r[0]["enem"], 2022)
        self.assertIsNotNone(r[0]["introducao"])

    def test_redamil_v1_reconstroi_texto_palavra_por_palavra(self):
        palavras = ("Segundo um pensador fictício a tecnologia muda tudo. " * 12).split()
        palavras += "Primeiramente é preciso notar que isso afeta a sociedade inteira de forma ampla.".split() * 3
        texto = "Pedro Teste\n18 anos\nCidade - UF\n\"\n" + "\n12\n".join(palavras) + "\n\"\n"
        r = cr.extrair_redamil_v1(texto)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["autor"], "Pedro Teste")
        self.assertNotIn(" 12 ", r[0]["texto"])  # número de página removido
        self.assertTrue(r[0]["introducao"].startswith("Segundo um pensador"))
        self.assertNotIn("Primeiramente", r[0]["introducao"])


class TestBanco(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.con = sqlite3.connect(self.dir / "t.db")
        self.con.executescript(cr.SCHEMA)

    def tearDown(self):
        self.con.close()

    def test_duplicada_fica_com_a_fonte_mais_confiavel(self):
        cr.gravar(self.con, [
            dict(fonte="portal", enem=2023, autor="Lucas Malta"),
            dict(fonte="cartilha INEP", enem=2023, autor="Lucas Malta de Carvalho"),
            dict(fonte="Redação a Mil", enem=2023, autor="Outra Pessoa"),
        ])
        self.assertEqual(cr.marcar_duplicadas(self.con), 1)
        dup = dict(self.con.execute("SELECT fonte, duplicada_de FROM redacoes").fetchall())
        self.assertIsNone(dup["cartilha INEP"])
        self.assertIsNotNone(dup["portal"])

    def test_estatisticas_conta_repertorio_e_causas_so_nas_unicas(self):
        cr.gravar(self.con, [
            dict(fonte="cartilha INEP", enem=2023, autor="A Um", texto="Segundo a Constituição e Bauman...",
                 causa_1="negligência estatal", causa_2="preconceito social"),
            dict(fonte="portal", enem=2023, autor="A Um", texto="Constituição repetida"),
        ])
        cr.marcar_duplicadas(self.con)
        self.con.commit()
        est = cr.estatisticas(self.dir / "t.db")
        self.assertEqual(est["unicas"], 1)
        self.assertEqual(dict(est["repertorios"])["Constituição"], 1)
        self.assertEqual(est["causas"]["ambas"], 1)


if __name__ == "__main__":
    unittest.main()


class TestCommonCrawl(unittest.TestCase):
    def test_normalizar_url_tira_query_e_barra_e_forca_https(self):
        import commoncrawl_redacoes as cc
        self.assertEqual(cc.normalizar_url("http://site.com/redacao-nota-1000/?utm=x#topo"),
                         "https://site.com/redacao-nota-1000")


class TestMesmaRedacao(unittest.TestCase):
    def test_reconhece_mesma_redacao_com_pequena_diferenca_de_extracao(self):
        a = "A Constituição Federal de 1988 garante direitos a todos os cidadãos brasileiros, mas a realidade mostra outra coisa."
        b = "A Constituicao Federal de 1988 garante direitos a todos os cidadaos brasileiros mas a realidade mostra outra coisa"
        c = "O filme retrata uma família do sertão que enfrenta a seca e a fome sem nenhum apoio do poder público local."
        self.assertTrue(cr.mesma_redacao(cr.trechos(a), cr.trechos(b)))
        self.assertFalse(cr.mesma_redacao(cr.trechos(a), cr.trechos(c)))
