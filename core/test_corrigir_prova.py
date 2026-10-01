"""test_corrigir_prova.py — db.corrigir_prova/provas_para_corrigir e as
rotas /provas e /provas/corrigir. Banco temporário, nunca o enem.db."""
import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("API_PERMITIR_SEM_TOKEN", "1")

import api  # noqa: E402
import db  # noqa: E402
from test_db import _TestComBancoTemporario  # noqa: E402

os.environ.pop("API_AUTH_TOKEN", None)
os.environ.pop("API_USUARIOS", None)


class TestCorrigirProva(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.ids = []
        for i in range(40):
            id_q, _ = db.inserir_questao(
                ano=2023, caderno="Azul", numero=91 + i, grande_area="ciencias_natureza",
                materia="Optica", alternativa_correta="A",
            )
            db.atualizar_parametros_tri(id_q, 2.0, -1.0 + 4.0 * i / 40, 0.2, 1)
            self.ids.append(id_q)
        db.inserir_resolucao(self.ids[39], "texto", "porque a A", canal="explicacao_ia")

    def test_corrige_conta_branco_e_traz_explicacao(self):
        respostas = {91 + i: "A" for i in range(30)}  # 30 certas
        respostas[91 + 39] = "B"                      # 1 errada (tem explicação); 9 ficam em branco
        r = db.corrigir_prova(2023, "azul", "ciencias_natureza", respostas)
        self.assertEqual((r["total"], r["acertos"], r["em_branco"]), (40, 30, 9))
        self.assertIsNotNone(r["nota_tri"])
        errada = next(e for e in r["erradas"] if e["numero_questao"] == 130)
        self.assertEqual((errada["marcada"], errada["correta"], errada["explicacao"]), ("B", "A", "porque a A"))
        # cada questão ganhou uma tentativa (entra na revisão espaçada)
        self.assertEqual(db.resumo_por_tentativa(2023, "azul", "ciencias_natureza")[0]["total"], 40)

    def test_letra_invalida_nao_grava_nada(self):
        with self.assertRaises(ValueError):
            db.corrigir_prova(2023, "azul", "ciencias_natureza", {91: "A", 92: "Z"})
        self.assertEqual(db.resumo_por_tentativa(2023, "azul", "ciencias_natureza"), [])

    def test_questao_de_outra_prova_e_recusada(self):
        with self.assertRaises(ValueError):
            db.corrigir_prova(2023, "azul", "ciencias_natureza", {5: "A"})

    def test_rotas(self):
        cliente = TestClient(api.app)
        provas = cliente.get("/provas").json()
        self.assertEqual(provas, [{"ano": 2023, "caderno": "azul", "grande_area": "ciencias_natureza",
                                   "total_questoes": 40, "com_tri": 40,
                                   "numeros": list(range(91, 131))}])
        r = cliente.post("/provas/corrigir", json={"ano": 2023, "caderno": "azul",
                                                   "grande_area": "ciencias_natureza", "respostas": {"91": "A"}})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["acertos"], 1)
        r = cliente.post("/provas/corrigir", json={"ano": 1999, "caderno": "azul",
                                                   "grande_area": "ciencias_natureza", "respostas": {}})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
