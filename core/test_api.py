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
import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

# A trava da API é fechada por padrão (ver api._verificar_autenticacao);
# o resto da suíte testa rota e validação, não a trava, então roda no
# modo de desenvolvimento. TestAutenticacao controla as variáveis na mão.
os.environ.setdefault("API_PERMITIR_SEM_TOKEN", "1")

import api  # noqa: E402
import db  # noqa: E402

# `import api` roda load_dotenv(): se o .env de verdade tiver
# API_AUTH_TOKEN, ele vence a flag de dev e toda rota daria 401 aqui.
# O token real não pertence à suíte; TestAutenticacao seta o dela.
os.environ.pop("API_AUTH_TOKEN", None)


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
    """A trava (ver adr/0009): fechada por padrão, aberta só com a flag
    de desenvolvimento, e com token configurado exige o header certo."""

    def test_sem_token_e_sem_flag_de_dev_recusa(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("API_AUTH_TOKEN", None)
            os.environ.pop("API_PERMITIR_SEM_TOKEN", None)
            resposta = self.client.get("/health")
        self.assertEqual(resposta.status_code, 503)

    def test_sem_token_com_flag_de_dev_fica_aberta(self):
        with patch.dict(os.environ, {"API_PERMITIR_SEM_TOKEN": "1"}, clear=False):
            os.environ.pop("API_AUTH_TOKEN", None)
            resposta = self.client.get("/health")
        self.assertEqual(resposta.status_code, 200)

    def test_flag_de_dev_nao_abre_quando_ha_token(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste", "API_PERMITIR_SEM_TOKEN": "1"}):
            resposta = self.client.get("/health")
        self.assertEqual(resposta.status_code, 401)

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




class _TestComDuasPessoas(_TestComBancoTemporario):
    """Bancos de "ana" e "bia" criados por criar_banco_usuario.py, base de
    TestVariasPessoas e TestPainelAdmin."""

    CODIGO_ANA = "codigo-da-ana-123456"
    CODIGO_BIA = "codigo-da-bia-654321"

    def setUp(self):
        super().setUp()
        import criar_banco_usuario
        self.id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=93, grande_area="ciencias_natureza",
            materia="Optica", alternativa_correta="A",
        )
        db.registrar_tentativa(self.id_q, "B")  # dado pessoal do dono do banco de origem
        self.pasta = Path(self._pasta_temp) / "bancos"
        for nome in ("ana", "bia"):
            criar_banco_usuario.criar_banco(nome, self.pasta, origem=db.DB_PATH)
        self.env = {
            "API_USUARIOS": f"ana:{self.CODIGO_ANA},bia:{self.CODIGO_BIA}",
            "API_PASTA_BANCOS": str(self.pasta),
        }

    def _tentativas(self, nome):
        with closing(sqlite3.connect(self.pasta / f"{nome}.db")) as conn:
            return conn.execute("SELECT resposta_escolhida FROM tentativas_usuario").fetchall()

    def _responder(self, codigo, letra):
        return self.client.post(
            "/tentativas", json={"id_questao": self.id_q, "resposta_escolhida": letra},
            headers={"Authorization": f"Bearer {codigo}"},
        )


class TestVariasPessoas(_TestComDuasPessoas):
    """API com API_USUARIOS (ver adr/0010): cada código de acesso usa o
    próprio banco, criado por criar_banco_usuario.py sem dado pessoal."""

    def test_banco_novo_nao_leva_dado_pessoal(self):
        self.assertEqual(self._tentativas("ana"), [])
        with closing(sqlite3.connect(self.pasta / "ana.db")) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM questoes").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name = 'tentativas_usuario'").fetchone()[0], 0)

    def test_cada_codigo_grava_no_proprio_banco(self):
        with patch.dict(os.environ, self.env):
            self.assertEqual(self._responder(self.CODIGO_ANA, "A").status_code, 200)
            self.assertEqual(self._responder(self.CODIGO_BIA, "C").status_code, 200)
            self.assertEqual(self._responder(self.CODIGO_BIA, "D").status_code, 200)
        self.assertEqual(self._tentativas("ana"), [("A",)])
        self.assertEqual(self._tentativas("bia"), [("C",), ("D",)])
        with closing(sqlite3.connect(db.DB_PATH)) as conn:  # o banco de origem não foi tocado
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM tentativas_usuario").fetchone()[0], 1)

    def test_codigo_errado_ou_token_antigo_recusa(self):
        with patch.dict(os.environ, {**self.env, "API_AUTH_TOKEN": "token-antigo"}):
            self.assertEqual(self._responder("codigo-inventado-000000", "A").status_code, 401)
            self.assertEqual(self._responder("token-antigo", "A").status_code, 401)
            self.assertEqual(self.client.get("/health").status_code, 401)

    def test_banco_que_falta_responde_503(self):
        (self.pasta / "bia.db").unlink()
        with patch.dict(os.environ, self.env):
            self.assertEqual(self._responder(self.CODIGO_BIA, "A").status_code, 503)

    def test_codigo_curto_demais_e_recusado_na_configuracao(self):
        with patch.dict(os.environ, {"API_USUARIOS": "ana:curto"}):
            with self.assertRaises(RuntimeError):
                api.usuarios_configurados()

    def test_nao_sobrescreve_banco_existente(self):
        import criar_banco_usuario
        with self.assertRaises(SystemExit):
            criar_banco_usuario.criar_banco("ana", self.pasta, origem=db.DB_PATH)


class TestEventos(_TestComDuasPessoas):
    """POST /eventos: grava no banco de quem mandou, com o aparelho resumido
    pelo servidor (o User-Agent completo nunca chega ao banco)."""

    UA_ANDROID = "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"

    def _evento(self, codigo, corpo, ua=UA_ANDROID):
        with patch.dict(os.environ, self.env):
            return self.client.post("/eventos", json=corpo, headers={"Authorization": f"Bearer {codigo}", "User-Agent": ua})

    def _gravados(self, nome):
        with closing(sqlite3.connect(self.pasta / f"{nome}.db")) as conn:
            return conn.execute("SELECT tipo, tela, aparelho FROM eventos").fetchall()

    def test_grava_no_banco_de_quem_mandou_com_aparelho_resumido(self):
        self.assertEqual(self._evento(self.CODIGO_ANA, {"tipo": "app_aberto", "tela": "/"}).status_code, 200)
        self.assertEqual(self._gravados("ana"), [("app_aberto", "/", "Android · Chrome")])
        self.assertEqual(self._gravados("bia"), [])

    def test_tipo_invalido_400_e_sem_codigo_401(self):
        self.assertEqual(self._evento(self.CODIGO_ANA, {"tipo": "qualquer"}).status_code, 400)
        self.assertEqual(self._evento("codigo-inventado-000000", {"tipo": "app_aberto"}).status_code, 401)
        self.assertEqual(self._gravados("ana"), [])

    def test_detalhe_e_pesquisa_no_banco_de_quem_mandou(self):
        self.assertEqual(self._evento(self.CODIGO_ANA, {"tipo": "app_aberto", "tela": "/", "detalhe": "whatsapp"}).status_code, 200)
        with closing(sqlite3.connect(self.pasta / "ana.db")) as conn:
            self.assertEqual(conn.execute("SELECT detalhe FROM eventos").fetchone()[0], "whatsapp")
        cabecalho = {"Authorization": f"Bearer {self.CODIGO_BIA}"}
        with patch.dict(os.environ, self.env):
            self.assertIsNone(self.client.get("/pesquisa/ultima", headers=cabecalho).json()["criado_em"])
            self.assertEqual(self.client.post("/pesquisa", json={"nota": 11}, headers=cabecalho).status_code, 400)
            self.assertEqual(self.client.post("/pesquisa", json={"nota": 9, "comentario": "a explicação"}, headers=cabecalho).status_code, 200)
            self.assertIsNotNone(self.client.get("/pesquisa/ultima", headers=cabecalho).json()["criado_em"])
            self.assertIsNone(self.client.get("/pesquisa/ultima", headers={"Authorization": f"Bearer {self.CODIGO_ANA}"}).json()["criado_em"])

    def test_resumir_aparelho(self):
        casos = {
            self.UA_ANDROID: "Android · Chrome",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1": "iPhone · Safari",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36 Edg/129.0": "Windows · Edge",
            "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-A135M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0 Mobile Safari/537.36": "Android · Samsung",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/129.0 Mobile/15E148 Safari/604.1": "iPhone · Chrome",
            "okhttp/4.12.0": "Android · app",
            "curl/8.4.0": "outro · outro",
        }
        for ua, esperado in casos.items():
            self.assertEqual(api.resumir_aparelho(ua), esperado)
        self.assertIsNone(api.resumir_aparelho(None))

    def test_banco_novo_nao_leva_eventos_do_dono(self):
        import criar_banco_usuario
        db.registrar_evento("app_aberto", "/", "Windows · Chrome")  # no banco de origem
        destino = criar_banco_usuario.criar_banco("caio", self.pasta, origem=db.DB_PATH)
        with closing(sqlite3.connect(destino)) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM eventos").fetchone()[0], 0)


class TestPainelAdmin(_TestComDuasPessoas):
    """/admin/uso (ver api._verificar_admin): chave própria do admin,
    separada dos códigos das pessoas. O cálculo em si é coberto em
    test_uso_admin.py; aqui só a trava e a ligação com a pasta de bancos."""

    CHAVE_ADMIN = "chave-do-admin-0123456789"

    def _uso(self, chave, env_extra=None):
        env = {**self.env, "API_ADMIN_TOKEN": self.CHAVE_ADMIN, **(env_extra or {})}
        with patch.dict(os.environ, env):
            return self.client.get("/admin/uso", headers={"Authorization": f"Bearer {chave}"})

    def test_chave_certa_ve_uso_de_cada_pessoa(self):
        with patch.dict(os.environ, self.env):
            self._responder(self.CODIGO_ANA, "A")  # acertou
            self._responder(self.CODIGO_ANA, "B")  # errou, mesma questão
        resposta = self._uso(self.CHAVE_ADMIN)
        self.assertEqual(resposta.status_code, 200)
        por_pessoa = {p["usuario"]: p for p in resposta.json()}
        self.assertEqual(set(por_pessoa), {"ana", "bia"})
        self.assertEqual((por_pessoa["ana"]["tentativas"], por_pessoa["ana"]["questoes"]), (2, 1))
        self.assertEqual(por_pessoa["ana"]["taxa_acerto"], 0.5)
        self.assertEqual(por_pessoa["bia"]["tentativas"], 0)

    def test_quem_abriu_e_nao_respondeu_aparece_marcado(self):
        with patch.dict(os.environ, self.env):
            self.client.post("/eventos", json={"tipo": "app_aberto", "tela": "/"}, headers={"Authorization": f"Bearer {self.CODIGO_BIA}"})
        bia = {p["usuario"]: p for p in self._uso(self.CHAVE_ADMIN).json()}["bia"]
        self.assertEqual((bia["aberturas"], bia["tentativas"]), (1, 0))
        self.assertTrue(bia["abriu_sem_responder"])
        self.assertIsNotNone(bia["primeira_atividade"])

    def test_chave_errada_ou_codigo_de_pessoa_recusa(self):
        self.assertEqual(self._uso("chave-inventada-0000000000").status_code, 401)
        self.assertEqual(self._uso(self.CODIGO_ANA).status_code, 401)
        self.assertEqual(self._uso("").status_code, 401)

    def test_sem_chave_configurada_fica_desligado(self):
        with patch.dict(os.environ, self.env):
            os.environ.pop("API_ADMIN_TOKEN", None)
            resposta = self.client.get("/admin/uso", headers={"Authorization": f"Bearer {self.CHAVE_ADMIN}"})
        self.assertEqual(resposta.status_code, 503)

    def test_chave_curta_ou_igual_a_codigo_de_pessoa_e_recusada(self):
        self.assertEqual(self._uso("curta", {"API_ADMIN_TOKEN": "curta"}).status_code, 503)
        self.assertEqual(self._uso(self.CODIGO_ANA, {"API_ADMIN_TOKEN": self.CODIGO_ANA}).status_code, 503)

    def test_quem_nao_tem_a_chave_nao_descobre_erro_de_configuracao(self):
        # Chave configurada curta demais: sem a chave, a resposta é só 401.
        self.assertEqual(self._uso("chute-qualquer-000000", {"API_ADMIN_TOKEN": "curta"}).status_code, 401)

    def test_so_aparecem_as_pessoas_de_api_usuarios(self):
        shutil.copy(self.pasta / "ana.db", self.pasta / "ana_backup.db")
        nomes = {p["usuario"] for p in self._uso(self.CHAVE_ADMIN).json()}
        self.assertEqual(nomes, {"ana", "bia"})

    def test_chave_do_admin_nao_abre_banco_de_ninguem(self):
        with patch.dict(os.environ, {**self.env, "API_ADMIN_TOKEN": self.CHAVE_ADMIN}):
            self.assertEqual(self._responder(self.CHAVE_ADMIN, "A").status_code, 401)
            self.assertEqual(self.client.get("/health", headers={"Authorization": f"Bearer {self.CHAVE_ADMIN}"}).status_code, 401)

    def test_painel_nao_grava_nada(self):
        antes = {p.name: p.read_bytes() for p in self.pasta.iterdir()}
        self.assertEqual(self._uso(self.CHAVE_ADMIN).status_code, 200)
        self.assertEqual({p.name: p.read_bytes() for p in self.pasta.iterdir()}, antes)

    def test_pagina_abre_sem_chave_e_sem_dado(self):
        with patch.dict(os.environ, {**self.env, "API_ADMIN_TOKEN": self.CHAVE_ADMIN}):
            pagina = self.client.get("/admin/")
            sem_barra = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(pagina.status_code, 200)
        self.assertIn("Painel de uso", pagina.text)
        self.assertEqual(sem_barra.status_code, 307)
        self.assertEqual(sem_barra.headers["location"], "/admin/")


class TestArquivosSemTrava(_TestComBancoTemporario):
    """Figuras e app web (adr/0010) são `mount`: abertos mesmo com a trava
    ligada, porque <img> e a página inicial não mandam Authorization."""

    def test_figura_abre_sem_token_mas_api_continua_travada(self):
        figura = next(api.PASTA_ENUNCIADOS.glob("*.png"))
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            self.assertEqual(self.client.get(f"/enunciados/{figura.name}").status_code, 200)
            self.assertEqual(self.client.get("/health").status_code, 401)

    def test_privacidade_e_termos_abrem_sem_token(self):
        with patch.dict(os.environ, {"API_AUTH_TOKEN": "segredo-de-teste"}):
            privacidade = self.client.get("/legal/privacidade.html")
            termos = self.client.get("/legal/termos.html")
            self.assertEqual(self.client.get("/health").status_code, 401)
        self.assertEqual(privacidade.status_code, 200)
        self.assertIn("Política de privacidade", privacidade.text)
        self.assertEqual(termos.status_code, 200)
        self.assertIn("Termos de uso", termos.text)

    def test_app_web_serve_tela_e_cai_no_index(self):
        from fastapi import FastAPI
        pasta = Path(self._pasta_temp) / "dist"
        pasta.mkdir()
        (pasta / "index.html").write_text("inicio", encoding="utf-8")
        (pasta / "simulado.html").write_text("tela simulado", encoding="utf-8")
        app_web = FastAPI()
        app_web.mount("/", api._AppWeb(directory=pasta, html=True))
        cliente = TestClient(app_web)
        self.assertEqual(cliente.get("/").text, "inicio")
        self.assertEqual(cliente.get("/simulado").text, "tela simulado")
        self.assertEqual(cliente.get("/rota/que/nao/existe").text, "inicio")


class TestPrepararServidor(_TestComBancoTemporario):
    def test_cria_so_o_banco_que_falta(self):
        import preparar_servidor
        import criar_banco_usuario
        id_q, _ = db.inserir_questao(
            ano=2022, caderno="Azul", numero=91, grande_area="ciencias_natureza",
            materia="Optica", alternativa_correta="A",
        )
        pasta = Path(self._pasta_temp) / "bancos"
        criar_banco_usuario.criar_banco("ana", pasta, origem=db.DB_PATH)
        with db.usar_banco(pasta / "ana.db"):
            db.registrar_tentativa(id_q, "B")  # histórico da ana, que não pode sumir
        arquivo = Path(self._pasta_temp) / "explicacoes.jsonl"
        arquivo.write_text(json.dumps({"id_questao": id_q, "texto": "porque sim"}) + "\n", encoding="utf-8")
        env = {"API_USUARIOS": "ana:codigo-da-ana-123456,bia:codigo-da-bia-654321", "API_PASTA_BANCOS": str(pasta)}
        with patch.dict(os.environ, env), patch.object(preparar_servidor, "SEMENTE", db.DB_PATH), patch.object(preparar_servidor.explicacoes, "ARQUIVO", arquivo):
            self.assertEqual(preparar_servidor.preparar(), ["bia"])
        for nome in ("ana", "bia"):  # explicação chega em banco novo E em banco antigo
            with db.usar_banco(pasta / f"{nome}.db"):
                self.assertEqual([r["conteudo"] for r in db.resolucoes_da_questao(id_q)], ["porque sim"])
                self.assertEqual(db.obter_configuracao("trilha_ativa"), "semana")
        with closing(sqlite3.connect(pasta / "ana.db")) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM tentativas_usuario").fetchone()[0], 1)


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
