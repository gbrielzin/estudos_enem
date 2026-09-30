"""Testes do filtro do youtube_commons_redacao.py com títulos sintéticos,
rodando a consulta num DuckDB em memória (sem internet)."""
import os
import shutil
import tempfile
import unittest

import youtube_commons_redacao as yc

try:
    import duckdb
except ImportError:  # duckdb só é preciso pra coleta; sem ele, pula
    duckdb = None


@unittest.skipIf(duckdb is None, "duckdb não instalado")
class TestFiltro(unittest.TestCase):
    def titulos_aceitos(self, linhas):
        con = duckdb.connect()
        con.execute("CREATE TABLE v (video_id TEXT, video_link TEXT, title TEXT, channel TEXT, "
                    "transcription_language TEXT, original_language TEXT, source_language TEXT, "
                    "word_count INT, license TEXT, text TEXT)")
        for i, (titulo, idioma) in enumerate(linhas):
            con.execute("INSERT INTO v VALUES (?, '', ?, '', ?, 'pt', 'pt', 0, '', '')", [str(i), titulo, idioma])
        return {r[2] for r in con.execute(yc.consulta("v")).fetchall()}

    def test_aceita_titulos_de_redacao_e_enem(self):
        titulos = ["REDAÇÃO NOTA 1000: como fazer", "Revisão ENEM Biologia", "Texto dissertativo-argumentativo",
                   "redacao sem acento", "Nota mil no Enem 2024"]
        self.assertEqual(self.titulos_aceitos([(t, "pt") for t in titulos]), set(titulos))

    def test_enem_so_como_palavra_inteira(self):
        aceitos = self.titulos_aceitos([("Invading the Enemy Field", "pt"), ("Enemies of the state", "pt")])
        self.assertEqual(aceitos, set())

    def test_descarta_traducao_de_video_em_portugues(self):
        # vídeo original em PT (original/source_language = 'pt'), transcrição
        # traduzida pra alemão: era o que a primeira coleta salvava
        self.assertEqual(self.titulos_aceitos([("Redação ENEM", "de")]), set())


class TestRetomada(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.prog = os.path.join(self.pasta, "saida.csv.progresso")

    def tearDown(self):
        shutil.rmtree(self.pasta)

    def escrever(self, caminho, texto):
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            f.write(texto)

    def test_progresso_do_mesmo_filtro_retoma(self):
        self.escrever(self.prog, f"filtro:{yc.assinatura_filtro()}\n0\n1\n")
        self.assertEqual(yc.ler_progresso(self.prog), {0, 1})

    def test_progresso_de_outro_filtro_para(self):
        self.escrever(self.prog, "filtro:outro\n0\n")
        with self.assertRaises(SystemExit):
            yc.ler_progresso(self.prog)

    def test_progresso_antigo_sem_assinatura_para(self):
        self.escrever(self.prog, "0\n1\n")
        with self.assertRaises(SystemExit):
            yc.ler_progresso(self.prog)

    def test_chaves_salvas_le_video_e_idioma_do_csv(self):
        saida = os.path.join(self.pasta, "saida.csv")
        self.escrever(saida, "video_id,video_link,title,channel,language,word_count,license,text\n"
                             "abc,,t,c,pt,1,cc,\"texto, com vírgula\"\n")
        self.assertEqual(yc.chaves_salvas(saida), {("abc", "pt")})
        self.assertEqual(yc.chaves_salvas(os.path.join(self.pasta, "nao_existe.csv")), set())


if __name__ == "__main__":
    unittest.main()
