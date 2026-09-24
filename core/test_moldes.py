"""
test_moldes.py — testes do gerador de variações (moldes.py).

Garante as duas promessas do módulo: a resposta certa está SEMPRE entre as
alternativas (o erro que aconteceu à mão na sessão de 2026-09-23), e cada
molde, com os números da questão âncora, reproduz o gabarito oficial.

Não toca em banco nenhum (moldes.py é puro).

Rodar (de dentro de core/):
    python -m unittest test_moldes
"""
import unittest

import moldes

SEEDS = range(300)


def _valor(texto: str) -> float:
    return float(texto.replace(",", "."))


class TestReproduzQuestaoOficial(unittest.TestCase):
    """Com os parâmetros originais, o molde chega na mesma resposta do
    gabarito do INEP. É o que dá confiança de que a fórmula do molde é a
    da questão e não uma aproximação."""

    def test_resposta_original_bate_com_o_gabarito(self):
        for id_molde, molde in moldes.MOLDES.items():
            with self.subTest(id_molde=id_molde):
                variacao = moldes.gerar_variacao(id_molde, original=True)
                marcada = _valor(variacao["alternativas"][variacao["correta"]])
                self.assertAlmostEqual(marcada, molde["resposta_original"], places=2)


class TestAlternativas(unittest.TestCase):

    def test_sempre_cinco_alternativas_distintas_com_a_correta(self):
        for id_molde in moldes.MOLDES:
            for seed in SEEDS:
                with self.subTest(id_molde=id_molde, seed=seed):
                    v = moldes.gerar_variacao(id_molde, seed=seed)
                    self.assertEqual(list(v["alternativas"]), list("ABCDE"))
                    self.assertEqual(len(set(v["alternativas"].values())), 5)
                    self.assertIn(v["correta"], v["alternativas"])

    def test_alternativas_em_ordem_crescente_e_sem_zero(self):
        for id_molde in moldes.MOLDES:
            for seed in SEEDS:
                with self.subTest(id_molde=id_molde, seed=seed):
                    valores = [_valor(t) for t in moldes.gerar_variacao(id_molde, seed=seed)["alternativas"].values()]
                    self.assertEqual(valores, sorted(valores))
                    self.assertGreater(min(valores), 0)

    def test_toda_alternativa_errada_tem_motivo(self):
        for id_molde in moldes.MOLDES:
            v = moldes.gerar_variacao(id_molde, seed=1)
            erradas = set(v["alternativas"]) - {v["correta"]}
            self.assertEqual(set(v["distratores"]), erradas)


class TestSeed(unittest.TestCase):

    def test_mesma_seed_gera_a_mesma_questao(self):
        for id_molde in moldes.MOLDES:
            self.assertEqual(moldes.gerar_variacao(id_molde, seed=42), moldes.gerar_variacao(id_molde, seed=42))

    def test_seeds_diferentes_variam_os_numeros(self):
        for id_molde in moldes.MOLDES:
            parametros = {str(moldes.gerar_variacao(id_molde, seed=s)["parametros"]) for s in range(30)}
            self.assertGreater(len(parametros), 5)


class TestCatalogo(unittest.TestCase):

    def test_molde_inexistente_levanta_value_error(self):
        with self.assertRaises(ValueError):
            moldes.gerar_variacao("nao_existe")

    def test_listar_traz_ancora_e_kit(self):
        for item in moldes.listar_moldes():
            self.assertRegex(item["id_questao_ancora"], r"^\d{4}_\w+_\d+$")
            self.assertTrue(item["kit"])


if __name__ == "__main__":
    unittest.main()
