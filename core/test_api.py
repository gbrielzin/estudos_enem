"""
test_api.py — testes automatizados pra camada HTTP de api.py.

api.py é uma camada fina de propósito (ver seu próprio docstring): não
duplica regra de negócio nenhuma, só traduz chamada HTTP em chamada de
função de db.py (já coberto a fundo em test_db.py). Este arquivo não
re-testa Leitner/prioridade/trilha -- testa só o que é responsabilidade
DESTA camada e nada mais: rota certa, parâmetro repassado certo, corpo
de request validado (Pydantic), status HTTP certo (200/400/404/422), e
erro de negócio (ValueError em db.py) virando HTTPException(400) em vez
de vazar como 500.

Nunca toca em enem.db: mesma técnica de test_db.py -- cada teste troca
db.DB_PATH pra um arquivo novo em tempfile.mkdtemp() antes, restaura
depois. api.py importa o MESMO módulo db (import db, não from db import
x), então reatribuir db.DB_PATH de fora afeta as chamadas que a API faz
por baixo também, sem precisar de nenhum mock.

Rodar (de dentro de core/):
    python -m unittest test_api
    python -m unittest test_api -v
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
import db


class _TestComBancoTemporario(unittest.TestCase):
    """Mesma técnica de test_db.py -- ver docstring lá. Duplicado aqui
    (em vez de importado de test_db) de propósito: os dois arquivos de
    teste devem poder rodar isolados um do outro, sem depender da
    ordem/existência um do outro."""

    def setUp(self):
        self._db_path_original = db.DB_PATH
        self._pasta_temp = tempfile.mkdtemp(prefix="enem_teste_api_")
        db.DB_PATH = Path(self._pasta_temp) / "enem_teste.db"
        db.inicializar_banco()
        self.client = TestClient(api.app)

    def tearDown(self):
        db.DB_PATH = self._db_path_original
        shutil.rmtree(self._pasta_temp, ignore_errors=True)


class TestHealth(unittest.TestCase):
    def test_health_nao_toca_no_banco(self):
        # De propósito SEM _TestComBancoTemporario: /health não deve
        # depender de banco nenhum existir (ver docstring do endpoint).
        resposta = TestClient(api.app).get("/health")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"status": "ok"})


class TestMaterias(_TestComBancoTemporario):
    def test_lista_materias_da_area_pedida(self):
        resposta = self.client.get("/materias", params={"grande_area": "matematica"})
        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertIsInstance(corpo, list)
        self.assertIn("analise_combinatoria", corpo)

    def test_falta_grande_area_da_422(self):
        # grande_area é obrigatório (sem default) -- FastAPI/Pydantic
        # devolve 422 sozinho, sem passar por nenhuma linha nossa.
        resposta = self.client.get("/materias")
        self.assertEqual(resposta.status_code, 422)


class TestBancoPratica(_TestComBancoTemporario):
    def test_sem_questao_nenhuma_listas_vem_vazias(self):
        self.assertEqual(self.client.get("/fontes-banco-pratica").json(), [])
        resposta = self.client.get(
            "/materias-com-banco-pratica", params={"grande_area": "ciencias_natureza"}
        )
        self.assertEqual(resposta.json(), [])

    def test_materia_com_questao_pratica_aparece_na_lista(self):
        db.inserir_questao_pratica(
            grande_area="ciencias_natureza", materia="ecologia",
            alternativa_correta="A", enunciado_texto="Enunciado de teste\n\nA) x\nB) y",
            fonte="teste",
        )
        resposta = self.client.get(
            "/materias-com-banco-pratica", params={"grande_area": "ciencias_natureza"}
        )
        self.assertEqual(resposta.json(), ["ecologia"])
        self.assertEqual(self.client.get("/fontes-banco-pratica").json(), ["teste"])


class TestTrilhaEFases(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        for _ in range(7):
            db.inserir_questao_pratica(
                grande_area="ciencias_natureza", materia="ecologia",
                alternativa_correta="A", enunciado_texto="Enunciado\n\nA) x\nB) y",
                fonte="teste",
            )

    def test_trilha_divide_em_nos_e_repassa_parametros(self):
        resposta = self.client.get(
            "/trilha",
            params={"grande_area": "ciencias_natureza", "materia": "ecologia", "fonte": "teste"},
        )
        self.assertEqual(resposta.status_code, 200)
        nos = resposta.json()
        # tamanho_no padrão em db.trilha_banco_pratica() é 5 -- 7 questões
        # devem virar 2 nós (5 + 2), primeiro desbloqueado, segundo não.
        self.assertEqual(len(nos), 2)
        self.assertTrue(nos[0]["desbloqueado"])
        self.assertFalse(nos[1]["desbloqueado"])

    def test_materia_sem_fase_mapeada_devolve_lista_vazia(self):
        # separacao_de_misturas nao tem fase mapeada (ver
        # db._FASES_POR_MATERIA) -- ver db.fases_disponiveis.
        resposta = self.client.get(
            "/fases", params={"grande_area": "ciencias_natureza", "materia": "separacao_de_misturas"}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [])

    def test_trilha_fixa_devolve_um_no_por_entrada_de_db_trilha_fixa_nos(self):
        # as 7 questoes do setUp sao 'ecologia' sem topico -- nao caem na
        # fase 4 (ver FASES_ECOLOGIA), entao o 1o no fica vazio mesmo
        # assim; o endpoint so precisa repassar db.trilha_fixa() como esta.
        resposta = self.client.get("/trilha-fixa")
        self.assertEqual(resposta.status_code, 200)
        nos = resposta.json()
        self.assertEqual([n["chave"] for n in nos], [c["chave"] for c in db.TRILHA_FIXA_NOS])
        self.assertTrue(nos[0]["desbloqueado"])


class TestTentativas(_TestComBancoTemporario):
    def setUp(self):
        super().setUp()
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=155,
            grande_area="Matematica", materia="Analise Combinatoria",
            alternativa_correta="C",
        )

    def test_registra_acerto(self):
        resposta = self.client.post(
            "/tentativas", json={"id_questao": self.id_q, "resposta_escolhida": "C"}
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resultado"], "acertou")

    def test_questao_inexistente_vira_400_nao_500(self):
        # db.registrar_tentativa levanta ValueError -- api.py precisa
        # traduzir isso pra HTTPException(400), nunca deixar vazar como
        # 500 (erro interno genérico não diz nada útil pro app mobile).
        resposta = self.client.post(
            "/tentativas", json={"id_questao": "id_que_nao_existe", "resposta_escolhida": "A"}
        )
        self.assertEqual(resposta.status_code, 400)

    def test_corpo_sem_id_questao_da_422(self):
        resposta = self.client.post("/tentativas", json={"resposta_escolhida": "A"})
        self.assertEqual(resposta.status_code, 422)

    def test_duracao_segundos_repassada_e_gravada(self):
        resposta = self.client.post(
            "/tentativas",
            json={"id_questao": self.id_q, "resposta_escolhida": "C", "duracao_segundos": 42},
        )
        self.assertEqual(resposta.status_code, 200)
        with db._conectar() as conn:
            valor = conn.execute(
                "SELECT duracao_segundos FROM tentativas_usuario WHERE id_questao = ?", (self.id_q,)
            ).fetchone()[0]
        self.assertEqual(valor, 42)

    def test_sem_duracao_segundos_continua_funcionando(self):
        # clientes antigos (ou scripts) que nunca mandaram esse campo
        # não podem quebrar -- tem que continuar opcional pra sempre.
        resposta = self.client.post(
            "/tentativas", json={"id_questao": self.id_q, "resposta_escolhida": "C"}
        )
        self.assertEqual(resposta.status_code, 200)


class TestHeaderDeStatus(_TestComBancoTemporario):
    """streak/nivel/missoes-do-dia -- nenhum bloqueia o usuário (ver
    docstring de missoes_do_dia em db.py), então banco vazio precisa
    devolver 200 com valores zerados, nunca erro."""

    def test_streak_banco_vazio(self):
        resposta = self.client.get("/streak")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["atual"], 0)

    def test_nivel_banco_vazio(self):
        resposta = self.client.get("/nivel")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["total_tentativas"], 0)

    def test_missoes_do_dia_devolve_lista(self):
        resposta = self.client.get("/missoes-do-dia")
        self.assertEqual(resposta.status_code, 200)
        self.assertIsInstance(resposta.json(), list)


class TestPerfilEExplorar(_TestComBancoTemporario):
    def test_dias_ate_prova(self):
        resposta = self.client.get("/dias-ate-prova")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("dias_restantes", resposta.json())

    def test_resumo_geral_banco_vazio(self):
        resposta = self.client.get("/resumo-geral")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"total_tentativas": 0, "acertos": 0, "taxa_acerto": None})

    def test_explorar_lista_todas_as_materias_da_taxonomia(self):
        # explorar_materias precisa listar TODA matéria da taxonomia,
        # com ou sem questão -- é o ponto central da função (ver
        # docstring dela em db.py e o plano que a motivou).
        resposta = self.client.get("/explorar", params={"grande_area": "matematica"})
        self.assertEqual(resposta.status_code, 200)
        corpo = resposta.json()
        self.assertGreater(len(corpo), 0)
        self.assertIn("total_questoes", corpo[0])


class TestAutenticacao(_TestComBancoTemporario):
    """A trava (ver adr/0009) só entra em vigor quando API_AUTH_TOKEN
    está configurado -- todo o resto desta suíte roda sem a variável
    setada de propósito, provando que o comportamento de hoje (API
    aberta) continua intacto quando ninguém configurou nada."""

    def test_sem_variavel_configurada_continua_aberta(self):
        # Garante que a env de teste não vaza um token de outra parte.
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("API_AUTH_TOKEN", None)
            resposta = self.client.get("/health")
        self.assertEqual(resposta.status_code, 200)

    def test_com_variavel_configurada_barra_sem_header(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            resposta = self.client.get("/health")
        self.assertEqual(resposta.status_code, 401)

    def test_com_variavel_configurada_barra_token_errado(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            resposta = self.client.get("/health", headers={"Authorization": "Bearer errado"})
        self.assertEqual(resposta.status_code, 401)

    def test_com_variavel_configurada_libera_token_certo(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            resposta = self.client.get(
                "/health", headers={"Authorization": "Bearer segredo-de-teste"}
            )
        self.assertEqual(resposta.status_code, 200)

    def test_trava_vale_pra_qualquer_endpoint_nao_so_health(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            resposta = self.client.get("/materias", params={"grande_area": "matematica"})
        self.assertEqual(resposta.status_code, 401)




class TestMoldes(_TestComBancoTemporario):
    """Só a camada HTTP: rota, parâmetros e 404. A lógica do gerador é
    testada em test_moldes.py."""

    def test_listar_moldes(self):
        resposta = self.client.get("/moldes")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("frenagem", {m["id_molde"] for m in resposta.json()})

    def test_variacao_com_seed_e_deterministica(self):
        r1 = self.client.get("/moldes/aquario/variacao", params={"seed": 5}).json()
        r2 = self.client.get("/moldes/aquario/variacao", params={"seed": 5}).json()
        self.assertEqual(r1, r2)

    def test_variacao_original_repassa_o_parametro(self):
        corpo = self.client.get("/moldes/carro_eletrico/variacao", params={"original": True}).json()
        self.assertEqual(corpo["parametros"]["distancia_km"], 110)

    def test_molde_inexistente_da_404(self):
        self.assertEqual(self.client.get("/moldes/nao_existe/variacao").status_code, 404)


if __name__ == "__main__":
    unittest.main()
