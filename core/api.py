"""
api.py — API HTTP pro app de celular (Expo/React Native), envolvendo db.py.

Camada fina de propósito: não duplica NENHUMA regra de negócio (Leitner,
prioridade, trilha etc.) -- tudo isso já mora em db.py, testado em
test_db.py. Este módulo só traduz chamada HTTP em chamada de função Python
e devolve o resultado como JSON. Mesma regra de camadas do resto de core/:
importa de db.py, nunca o contrário (ver CLAUDE.md).

Cresce endpoint por endpoint junto com cada fase do app de celular (ver
plano em C:\\Users\\WIN\\.claude\\plans\\validated-leaping-umbrella.md) --
não expõe todo o db.py de uma vez, só o que a fase atual do app usa.

Rodar (de dentro de core/, ou da raiz do projeto -- ver o --app-dir abaixo):
    uvicorn api:app --reload --host 0.0.0.0 --port 8000

--host 0.0.0.0 é o que permite o celular na mesma wifi alcançar (não só
localhost). Depois de rodar, o terminal mostra o IP da máquina, ou descubra
com `ipconfig` (Windows) -- é esse IP que o app no celular usa, não
"localhost" (que no celular apontaria pra ele mesmo).
"""
from __future__ import annotations

import hmac
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

import db
import moldes

# Carrega o .env da raiz do projeto pra dentro de os.environ -- é assim
# que API_AUTH_TOKEN (ver _verificar_autenticacao abaixo) chega até
# aqui sem precisar exportar a variável manualmente no shell toda vez.
# Não sobrescreve uma variável já setada de outra forma (comportamento
# padrão do load_dotenv).
load_dotenv()


PASTA_BANCOS_PADRAO = Path(__file__).parent / "bancos"
_NOME_USUARIO = re.compile(r"[a-z0-9_]{1,40}")


def usuarios_configurados() -> dict[str, str]:
    """{codigo: nome} a partir de `API_USUARIOS` ("nome:codigo,nome2:codigo2").

    Cada nome tem o próprio banco em `API_PASTA_BANCOS/<nome>.db` (criado
    com criar_banco_usuario.py). Sem a variável, a API continua no modo de
    uma pessoa só (API_AUTH_TOKEN + enem.db), como antes (ver adr/0010).
    Lido a cada chamada, mesmo motivo do API_AUTH_TOKEN: dá pra testar com
    patch.dict(os.environ) sem recarregar o módulo."""
    usuarios = {}
    for par in os.environ.get("API_USUARIOS", "").split(","):
        if not par.strip():
            continue
        nome, _, codigo = par.strip().partition(":")
        if not _NOME_USUARIO.fullmatch(nome) or len(codigo) < 16:
            raise RuntimeError(
                f"API_USUARIOS mal formado em '{nome}': nome só com a-z, 0-9 e _, código com 16+ caracteres."
            )
        usuarios[codigo] = nome
    return usuarios


def caminho_banco_usuario(nome: str) -> Path:
    return Path(os.environ.get("API_PASTA_BANCOS", PASTA_BANCOS_PADRAO)) / f"{nome}.db"


async def _verificar_autenticacao(authorization: str | None = Header(default=None)) -> None:
    """Trava por chave (Bearer token). Dois modos:

    - **Várias pessoas** (`API_USUARIOS` configurado, ver adr/0010): o
      código de acesso diz QUEM é, e a requisição inteira passa a usar o
      banco daquela pessoa (db.usar_banco). Não é login de verdade: o
      código é a credencial, como um link secreto.
    - **Uma pessoa** (sem `API_USUARIOS`): a trava de chave compartilhada
      do adr/0009, sem mudança — fechada por padrão (503 sem
      `API_AUTH_TOKEN`), aberta só com `API_PERMITIR_SEM_TOKEN=1`.

    É `async` de propósito: dependency síncrona roda numa thread com uma
    CÓPIA do contexto, então o banco escolhido aqui não chegaria até o
    endpoint. Async roda no contexto da própria requisição, que o
    endpoint herda. A comparação usa `hmac.compare_digest`."""
    recebido = (authorization or "").encode("utf-8")
    usuarios = usuarios_configurados()
    if usuarios:
        for codigo, nome in usuarios.items():
            if hmac.compare_digest(recebido, f"Bearer {codigo}".encode("utf-8")):
                caminho = caminho_banco_usuario(nome)
                if not caminho.exists():
                    raise HTTPException(status_code=503, detail=f"Banco de '{nome}' ainda não foi criado.")
                db._BANCO_DA_REQUISICAO.set(caminho)
                return
        raise HTTPException(status_code=401, detail="Código de acesso ausente ou inválido.")

    token_esperado = os.environ.get("API_AUTH_TOKEN")
    if not token_esperado:
        if os.environ.get("API_PERMITIR_SEM_TOKEN") == "1":
            return
        raise HTTPException(
            status_code=503,
            detail="API sem API_AUTH_TOKEN configurado. Configure no .env "
            "(ou API_PERMITIR_SEM_TOKEN=1 só pra desenvolvimento local).",
        )
    if not hmac.compare_digest(recebido, f"Bearer {token_esperado}".encode("utf-8")):
        raise HTTPException(status_code=401, detail="Token de autenticação ausente ou inválido.")


def _origens_cors() -> list[str]:
    """Origens liberadas pro navegador (só afeta o app rodando na web;
    o app nativo não passa por CORS). Vem de `API_CORS_ORIGENS`,
    separadas por vírgula; sem a variável, só o Expo web local."""
    valor = os.environ.get("API_CORS_ORIGENS", "")
    origens = [o.strip() for o in valor.split(",") if o.strip()]
    return origens or ["http://localhost:8081", "http://127.0.0.1:8081"]


app = FastAPI(title="ENEM GI API", dependencies=[Depends(_verificar_autenticacao)])

# CORS restrito às origens de _origens_cors() (antes era "*"; ver a
# atualização de 2026-09-26 no adr/0009).
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens_cors(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _inicializar() -> None:
    usuarios = usuarios_configurados()
    if not usuarios:
        db.inicializar_banco()
        return
    # Aplica as migrações em cada banco que já existe. Banco que falta
    # NÃO é criado aqui (sairia vazio, sem questão): quem cria é
    # criar_banco_usuario.py, e até lá aquela pessoa recebe 503.
    for nome in usuarios.values():
        caminho = caminho_banco_usuario(nome)
        if caminho.exists():
            with db.usar_banco(caminho):
                db.inicializar_banco()


@app.get("/health")
def health() -> dict:
    """Endpoint de teste da Fase 0 -- só confirma que o celular conseguiu
    alcançar o backend pela rede, antes de existir qualquer tela de
    verdade no app. Não faz nada com o banco."""
    return {"status": "ok"}


# ============================================================
# FASE 1 — Banco de Questões / trilha (ver render_banco_pratica em
# core/cartao_resposta.py, a versão Streamlit já validada desta mesma
# tela -- estes endpoints só expõem as MESMAS funções de db.py que
# aquela tela já usa, nenhuma regra nova).
# ============================================================

@app.get("/materias")
def materias(grande_area: str) -> list[str]:
    return db.materias_validas(grande_area)


@app.get("/fontes-banco-pratica")
def fontes_banco_pratica() -> list[str]:
    return db.fontes_banco_pratica()


@app.get("/materias-com-banco-pratica")
def materias_com_banco_pratica(grande_area: str) -> list[str]:
    """Matérias da área ordenadas da com MAIS questão de banco de
    prática pra com menos -- mesma função que a versão Streamlit usa
    pra escolher um padrão sensato (`_padrao_materia_banco_pratica` em
    cartao_resposta.py) em vez de cair na 1a matéria em ordem
    alfabética da taxonomia inteira (a maioria sem nenhuma questão
    ainda). O app mobile usa isto pra entrar direto na trilha (pedido
    explícito do usuário, mesma mudança que a versão Streamlit já
    tinha: a "Home"/seletores deixa de ser a tela inicial de fato)."""
    return db.materias_com_banco_pratica(grande_area)


@app.get("/trilha")
def trilha(grande_area: str, materia: str, fonte: str | None = None, fase: int | None = None) -> list[dict]:
    return db.trilha_banco_pratica(grande_area, materia, fonte=fonte, fase=fase)


@app.get("/trilha-fixa")
def trilha_fixa() -> list[dict]:
    """Trilha fixa entrelaçada entre matérias de Ciências da Natureza,
    na ordem de ROI definida em
    docs/arquitetura_questoes/arquitetura-trilha.docx (ver
    db.TRILHA_FIXA_NOS) -- diferente de /trilha, que só monta a
    sequência de UMA matéria por vez. Nos bancos com a configuração
    'trilha_ativa' = 'semana' (os dos amigos), devolve a trilha da semana
    no mesmo formato (ver db.TRILHA_SEMANA_NOS)."""
    return db.trilha_ativa()


@app.get("/fases")
def fases(grande_area: str, materia: str, fonte: str | None = None) -> list[dict]:
    """Fases de uma matéria (hoje só ecologia tem) -- lista vazia pra
    matéria sem fase mapeada, ver db.fases_disponiveis()."""
    return db.fases_disponiveis(grande_area, materia, fonte=fonte)


class TentativaRequest(BaseModel):
    id_questao: str
    resposta_escolhida: str | None = None
    # Opcional, de propósito: quem chama sem medir tempo (scripts,
    # clientes antigos) não manda nada, e db.registrar_tentativa()
    # trata None como "não sei", não como 0s.
    duracao_segundos: int | None = None


@app.post("/tentativas")
def registrar_tentativa(corpo: TentativaRequest) -> dict:
    try:
        return db.registrar_tentativa(corpo.id_questao, corpo.resposta_escolhida, corpo.duracao_segundos)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


# ============================================================
# Cartão-resposta de prova inteira (aba Simulado do celular): a pessoa
# faz a prova no papel ou na tela e marca as letras; a correção, a nota
# TRI e as explicações vêm de db.corrigir_prova().
# ============================================================

@app.get("/provas")
def provas() -> list[dict]:
    return db.provas_para_corrigir()


class CorrecaoRequest(BaseModel):
    ano: int
    caderno: str
    grande_area: str
    # {numero_questao: "A".."E" ou null}. Questão que não vier conta como em branco.
    respostas: dict[int, str | None]


@app.post("/provas/corrigir")
def corrigir(corpo: CorrecaoRequest) -> dict:
    try:
        return db.corrigir_prova(corpo.ano, corpo.caderno, corpo.grande_area, corpo.respostas)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


# ============================================================
# FASE 1.5 — Header de status (streak, XP/rank, missões do dia).
# Expõe sistemas que JÁ EXISTIAM em db.py (calcular_ofensiva,
# calcular_nivel_jogador -- já usados na versão Streamlit, "Minha
# análise") + missoes_do_dia (novo, mas também derivado ao vivo, sem
# tabela nova). Nenhum dos três bloqueia o usuário -- decisão
# deliberada, ver docstring de missoes_do_dia em db.py: um sistema
# tipo "vidas" que trava o progresso ao errar trabalha contra o
# objetivo de fixar conteúdo antes da prova.
# ============================================================

@app.get("/streak")
def streak() -> dict:
    return db.calcular_ofensiva()


@app.get("/nivel")
def nivel() -> dict:
    return db.calcular_nivel_jogador()


@app.get("/missoes-do-dia")
def missoes_do_dia() -> list[dict]:
    return db.missoes_do_dia()


# ============================================================
# FASE 2 — Explore e Perfil (ver plano de implementação das 8 telas do
# design_handoff em C:\Users\WIN\.claude\plans\validated-leaping-umbrella.md).
# Mesma regra das fases anteriores: só expõe função que já existe em
# db.py, exceto explorar_materias (nova, mas pura leitura agregada,
# sem regra de negócio nova).
# ============================================================

@app.get("/dias-ate-prova")
def dias_ate_prova() -> dict:
    return db.dias_ate_prova()


@app.get("/resumo-geral")
def resumo_geral() -> dict:
    return db.resumo_geral_desempenho()


@app.get("/explorar")
def explorar(grande_area: str) -> list[dict]:
    return db.explorar_materias(grande_area)


# ============================================================
# FASE 3 — Reportar questão + resolução/explicação por questão.
# Pedido explícito do usuário: enquanto ele valida o banco de
# questões pergunta por pergunta, precisa de um jeito de sinalizar
# "acho que isto está errado" sem sair do fluxo de resolver, e de
# ver a explicação/resolução já cadastrada de uma questão (mesma
# db.resolucoes_da_questao() que o Cartão-resposta já usa) quando
# existir uma.
# ============================================================

class RelatoRequest(BaseModel):
    id_questao: str
    comentario: str


@app.post("/relatos")
def relatos(corpo: RelatoRequest) -> dict:
    try:
        id_relato = db.reportar_questao(corpo.id_questao, corpo.comentario)
        return {"id_relato": id_relato}
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@app.get("/resolucoes")
def resolucoes(id_questao: str) -> list[dict]:
    return db.resolucoes_da_questao(id_questao)


# ============================================================
# Moldes — variações de questão oficial com números trocados (ver
# moldes.py). Módulo puro, não toca no banco: estes endpoints só geram
# a variação; registrar a tentativa continua sendo de /tentativas.
# ============================================================

@app.get("/moldes")
def listar_moldes() -> list[dict]:
    return moldes.listar_moldes()


@app.get("/moldes/{id_molde}/variacao")
def variacao_molde(id_molde: str, seed: int | None = None, original: bool = False) -> dict:
    try:
        return moldes.gerar_variacao(id_molde, seed=seed, original=original)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))


# ============================================================
# Arquivos sem trava (adr/0010): figuras das questões e o app web.
# São `mount`, não rota, então a trava de _verificar_autenticacao (que
# vale para as rotas da API) não se aplica -- de propósito: <img> e a
# página inicial não conseguem mandar o header Authorization. Nada aqui
# é dado pessoal: figuras de prova pública do INEP e o JS do app.
# Montados por ÚLTIMO, para nenhuma rota da API ficar escondida pelo "/".
# ============================================================

PASTA_ENUNCIADOS = Path(__file__).parent / "enunciados"
app.mount("/enunciados", StaticFiles(directory=PASTA_ENUNCIADOS, check_dir=False), name="enunciados")


class _AppWeb(StaticFiles):
    """Export do Expo (web.output "static"): cada tela vira <rota>.html.
    Abrir /simulado direto (atualizar a página, atalho na tela inicial)
    procura simulado.html; o que não existir cai no index.html."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as erro:
            if erro.status_code != 404:
                raise
        try:
            return await super().get_response(f"{path}.html", scope)
        except StarletteHTTPException:
            return await super().get_response("index.html", scope)


PASTA_WEB = Path(os.environ.get("API_PASTA_WEB", Path(__file__).parent.parent / "mobile" / "dist"))
if PASTA_WEB.is_dir():
    app.mount("/", _AppWeb(directory=PASTA_WEB, html=True), name="web")
