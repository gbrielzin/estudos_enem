"""test_trilha_semana.py — db.trilha_semana/trilha_ativa e a configuração
'trilha_ativa' gravada por preparar_servidor. Banco temporário."""
import unittest

import db
from test_db import _TestComBancoTemporario

TEXTO = "Enunciado longo o bastante para entrar na trilha da semana.\nA\t um\nB\t dois\nC\t três\nD\t quatro\nE\t cinco"


class TestTrilhaSemana(_TestComBancoTemporario):
    def _questao(self, numero, b, materia="ecologia", area="ciencias_natureza", texto=TEXTO):
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=numero, grande_area=area,
            materia=materia, alternativa_correta="A",
        )
        db.atualizar_parametros_tri(id_q, 2.0, b, 0.2, 1)
        if texto:
            db.atualizar_enunciado(id_q, texto=texto)
        return id_q

    def _no(self, chave):
        return next(n for n in db.trilha_semana() if n["chave"] == chave)

    def test_so_oficial_facil_ou_media_com_texto_da_mais_facil(self):
        dificil = self._questao(91, 2.5)
        media = self._questao(92, 1.5)
        facil = self._questao(93, 0.3)
        sem_texto = self._questao(94, 0.1, texto=None)
        ids = [q["id_questao"] for b in self._no("semana_ecologia")["blocos"] for q in b["questoes"]]
        self.assertEqual(ids, [facil, media])
        self.assertNotIn(dificil, ids)
        self.assertNotIn(sem_texto, ids)

    def test_questao_com_alternativa_em_desenho_fica_de_fora(self):
        com_texto = self._questao(91, 0.2)
        desenho = self._questao(92, 0.1, texto="Qual figura representa a planta do telhado? A D B E C")
        ver_imagem = self._questao(93, 0.15, texto="A sombra projetada é\n" + "\n".join(f"{l} (ver imagem)" for l in "ABCDE"))
        ids = [q["id_questao"] for b in self._no("semana_ecologia")["blocos"] for q in b["questoes"]]
        self.assertEqual(ids, [com_texto])
        self.assertNotIn(desenho, ids)
        self.assertNotIn(ver_imagem, ids)

    def test_nos_abertos_e_blocos_em_sequencia(self):
        for i in range(7):
            self._questao(91 + i, 0.1 * i)
        no = self._no("semana_ecologia")
        self.assertTrue(all(n["desbloqueado"] for n in db.trilha_semana()))
        self.assertEqual([b["desbloqueado"] for b in no["blocos"]], [True, False])
        for q in no["blocos"][0]["questoes"]:
            db.registrar_tentativa(q["id_questao"], "B")
        self.assertEqual([b["desbloqueado"] for b in self._no("semana_ecologia")["blocos"]], [True, True])

    def test_junta_materias_do_mesmo_no(self):
        a = self._questao(136, 0.5, materia="razao_e_proporcao", area="matematica")
        b = self._questao(137, 0.6, materia="porcentagem", area="matematica")
        ids = [q["id_questao"] for bl in self._no("semana_proporcao")["blocos"] for q in bl["questoes"]]
        self.assertEqual(ids, [a, b])

    def test_trilha_ativa_segue_a_configuracao(self):
        self.assertEqual(db.trilha_ativa(), db.trilha_fixa())
        db.definir_configuracao("trilha_ativa", "semana")
        self.assertEqual([n["chave"] for n in db.trilha_ativa()], [n["chave"] for n in db.TRILHA_SEMANA_NOS])


if __name__ == "__main__":
    unittest.main()
