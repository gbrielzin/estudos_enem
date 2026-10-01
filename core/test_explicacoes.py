"""test_explicacoes.py — explicacoes.ler/sincronizar com arquivo sintético.
Nunca toca em enem.db (banco temporário de test_db)."""
import json
import unittest
from pathlib import Path

import db
import explicacoes
from test_db import _TestComBancoTemporario


class TestSincronizarExplicacoes(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=91, grande_area="ciencias_natureza",
            materia="Optica", alternativa_correta="A",
        )
        self.arquivo = Path(self._pasta_temp) / "explicacoes.jsonl"

    def _escrever(self, *registros):
        self.arquivo.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in registros) + "\n", encoding="utf-8")

    def _textos(self):
        return [(r["conteudo"], r["canal"]) for r in db.resolucoes_da_questao(self.id_q)]

    def test_grava_e_e_idempotente(self):
        self._escrever({"id_questao": self.id_q, "texto": "A, porque reflete."})
        self.assertEqual(explicacoes.sincronizar(self.arquivo), (1, 0))
        self.assertEqual(explicacoes.sincronizar(self.arquivo), (0, 0))
        self.assertEqual(self._textos(), [("A, porque reflete.", explicacoes.CANAL)])

    def test_correcao_substitui_e_nao_toca_resolucao_manual(self):
        db.inserir_resolucao(self.id_q, "texto", "anotação minha", canal=None)
        self._escrever({"id_questao": self.id_q, "texto": "versão 1"})
        explicacoes.sincronizar(self.arquivo)
        self._escrever({"id_questao": self.id_q, "texto": "versão 2 corrigida"})
        explicacoes.sincronizar(self.arquivo)
        self.assertCountEqual(self._textos(), [("anotação minha", None), ("versão 2 corrigida", explicacoes.CANAL)])

    def test_questao_que_nao_existe_e_pulada(self):
        self._escrever({"id_questao": "2099_azul_1", "texto": "x"})
        self.assertEqual(explicacoes.sincronizar(self.arquivo), (0, 1))

    def test_linha_sem_texto_e_erro(self):
        self._escrever({"id_questao": self.id_q, "texto": "  "})
        with self.assertRaises(ValueError):
            explicacoes.ler(self.arquivo)

    def test_arquivo_do_repositorio_e_valido(self):
        # o jsonl versionado tem que sempre carregar (é lido em todo deploy)
        explicacoes.ler()


if __name__ == "__main__":
    unittest.main()
