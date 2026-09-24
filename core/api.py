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

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import moldes

# Carrega o .env da raiz do projeto pra dentro de os.environ -- é assim
# que API_AUTH_TOKEN (ver _verificar_autenticacao abaixo) chega até
# aqui sem precisar exportar a variável manualmente no shell toda vez.
# Não sobrescreve uma variável já setada de outra forma (comportamento
# padrão do load_dotenv).
load_dotenv()


def _verificar_autenticacao(authorization: str | None = Header(default=None)) -> None:
    """Trava simples por chave compartilhada (Bearer token) -- NÃO é
    autenticação de usuário de verdade, só barra quem não tem o
    segredo (ver adr/0009 pro raciocínio completo e por que um sistema
    de conta/login de verdade ainda não tem onde pendurar dado: não
    existe tabela de usuário nenhuma hoje).

    Lê `API_AUTH_TOKEN` do ambiente a CADA chamada (não cacheia em
    import) -- de propósito, pra dar pra testar com
    `unittest.mock.patch.dict(os.environ, ...)` sem precisar recarregar
    o módulo, mesmo espírito de `db.DB_PATH` ser reatribuível de fora
    pros testes de banco.

    Sem a variável configurada, a API roda ABERTA -- mesmo
    comportamento de hoje (uso pessoal, wifi doméstica). Configurar a
    variável é o que liga a trava; não quebra ninguém que ainda não
    setou nada."""
    token_esperado = os.environ.get("API_AUTH_TOKEN")
    if not token_esperado:
        return
    if authorization != f"Bearer {token_esperado}":
        raise HTTPException(status_code=401, detail="Token de autenticação ausente ou inválido.")


app = FastAPI(title="ENEM GI API", dependencies=[Depends(_verificar_autenticacao)])

# CORS liberado geral: uso pessoal/local (mesma wifi de casa), sem usuário
# de terceiros nem dado sensível exposto pra internet -- não é uma API
# pública. Reavaliar se algum dia isso for hospedado fora da rede local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _inicializar() -> None:
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
    sequência de UMA matéria por vez."""
    return db.trilha_fixa()


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
