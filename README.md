# ENEM_APP

Sistema de estudo pro ENEM orientado a dado: decide o que estudar agora
a partir de recorrência histórica de incidência × taxa de erro pessoal,
não por cronograma genérico. App mobile/web (React Native + Expo) sobre
uma API REST própria (Python + FastAPI + SQLite), alimentada por um
pipeline próprio de extração de questões a partir de PDFs oficiais do
INEP e de uma API pública externa.

## Problema

Decidir o que estudar pra um exame de larga escala (ENEM) é, na prática,
um problema de dado: qual assunto tem mais incidência histórica, em qual
matéria a taxa de erro pessoal é mais alta, e onde o tempo de estudo
rende mais pontos por hora investida. A maioria das ferramentas de
estudo trata isso como cronograma fixo, sem cruzar dado real de
desempenho com dado real de incidência da prova.

## Solução

Um pipeline de dados que transforma PDF oficial (e uma API pública
externa) em banco relacional, uma camada de regra de negócio que
calcula prioridade de estudo e repetição espaçada em cima desse banco, e
um app (mobile + web, mesmo código) que consome tudo isso via API REST
própria. A migração de um protótipo em CSV único, depois um monolito
Streamlit, até a arquitetura atual (API + app nativo) está documentada
decisão por decisão em `adr/` — cada trade-off tem o motivo e a
alternativa descartada registrados, não só o resultado final.

## Tecnologias

- **Dados / backend:** Python, SQLite, SQL puro (sem ORM), FastAPI,
  Pydantic
- **Pipeline de dados:** PyMuPDF (parsing de PDF), pandas, requests
  (consumo de API externa)
- **Mobile/Web:** React Native, Expo (Expo Router), TypeScript,
  `react-native-web` (mesmo código gera app nativo e site)
- **Testes:** unittest (`fastapi.testclient.TestClient` pro backend),
  Jest (mobile)
- **Documentação de decisão técnica:** Architecture Decision Records
  (`adr/`)
- **Ferramenta pessoal legada (ainda em uso, sem mais investimento
  visual):** Streamlit

## Arquitetura

```
usuário (app Expo — mobile ou web)
   → mobile/src/app/*.tsx
   → mobile/src/lib/api.ts (HTTP)
   → core/api.py (FastAPI)
   → core/db.py (regra de negócio: Leitner, prioridade, trilha)
   → core/enem.db (SQLite)
```

Toda a lógica de negócio vive em `core/db.py`, um módulo "folha": zero
dependência de UI, zero dependência externa além da stdlib. `core/api.py`
é uma camada fina — só traduz HTTP em chamada de função, sem duplicar
regra nenhuma. Essa separação foi o que permitiu migrar de um monolito
Streamlit para API + app mobile sem reescrever Leitner, priorização ou
taxonomia (ver [`adr/0007`](adr/0007-api-rest-mais-cliente-expo.md)).

O algoritmo de priorização de estudo (`prioridade_de_estudo()`) cruza
recorrência histórica por matéria com a taxa de erro pessoal numa fórmula
determinística e explicável (cada recomendação vem com sua própria conta
em aberto) — decisão documentada de usar heurística em vez de ML, dado o
volume de dado de um único usuário (ver
[`adr/0003`](adr/0003-heuristica-em-vez-de-ml.md)).

A API tem uma trava simples por chave compartilhada (`API_AUTH_TOKEN`,
opcional), não autenticação de usuário de verdade — não existe tabela de
usuário no schema hoje (ver [`adr/0009`](adr/0009-trava-simples-antes-de-autenticacao-real.md)
e "Limitações conhecidas" abaixo).

## Pipeline de dados

Duas fases, sempre separadas — gabarito primeiro, enunciado depois, nunca
misturadas:

```
PDF oficial do INEP / API pública enem.dev
   ↓  extração  (extrair_gabarito_pdf.py, PyMuPDF + pdftotext)
CSV de gabarito versionado (core/gabaritos_reais/*.csv, 17 arquivos)
   ↓  carga idempotente  (reconstruir_base.py)
core/enem.db (SQLite, 9 tabelas relacionais)
   ↓  enriquecimento  (extrair_enunciados_pdf.py / extrair_figuras_pdf.py / importar_enem_dev.py)
enunciado, imagem, validação cruzada de gabarito
   ↓
indicadores derivados ao vivo (prioridade de estudo, recorrência,
taxa de acerto, evolução semanal — nunca pré-calculado/cacheado)
```

Validações no meio do caminho: `importar_enem_dev.py` só aceita dado da
API externa se ≥90% das respostas baterem com o gabarito oficial já
carregado, abortando em vez de gravar sob identificador errado.
Classificação de matéria passa por um pipeline de normalização
(remove acento, casa contra taxonomia fechada de 89 matérias) antes de
entrar no banco — questão fora da taxonomia é marcada `nao_classificado`
em vez de rejeitada, alimentando uma fila de triagem manual.

## Principais resultados

- **1504 questões** no banco (1157 de provas oficiais 2010-2025 + 347 de
  banco de prática próprio)
- **800 tentativas** de usuário processadas pelo sistema
- **18 endpoints REST** (`core/api.py`)
- **9 tabelas** relacionais (SQLite)
- **123 testes automatizados** — 80 na regra de negócio + 28 na camada
  HTTP + 8 no gerador de moldes (`core/test_db.py`/`test_api.py`/
  `test_moldes.py`) + 7 no app mobile (Jest), rodando
  em CI (GitHub Actions, `.github/workflows/testes.yml`) junto com lint
  (`ruff`) e checagem de tipo (`tsc`) a cada push/PR
- **9 ADRs** documentando as principais decisões de arquitetura (`adr/`)

## Como executar

Backend:
```
cd core
pip install -r ../requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

App mobile/web:
```
cd mobile
npm install
npx expo start --web   # ou --android / --ios
```

Rodar os testes automatizados (backend):
```
cd core
python -m unittest discover -p "test_*.py"
```

Rodar os testes automatizados (mobile):
```
cd mobile
npm test
```

Ferramenta pessoal (Streamlit, legado — ver [`core/CLAUDE.md`](core/CLAUDE.md)):
```
cd core
streamlit run cartao_resposta.py
```

**Banco de dados:** `core/enem.db` não é versionado no repositório
(dado pessoal de uso real). Pra recriar do zero, a partir dos gabaritos
oficiais já versionados em `core/gabaritos_reais/`:
```
cd core
python reconstruir_base.py
```
Nenhuma variável de ambiente é obrigatória — `API_AUTH_TOKEN` (ver
`.env.example`) é opcional, liga a trava simples da API.

**Rodar de qualquer lugar (celular, sem notebook ligado):** ver
[`docs/DEPLOY.md`](docs/DEPLOY.md).

## Limitações conhecidas

Este é um projeto pessoal migrando pra multiusuário, não um serviço em
produção ainda — e isso molda decisões deliberadas, não descuidos:

- A trava da API (`API_AUTH_TOKEN`) não é autenticação de usuário de
  verdade — não há como diferenciar quem está chamando, só se tem ou
  não tem o segredo (ver `adr/0009`).
- CORS continua aberto (`allow_origins=["*"]`) — adequado hoje porque o
  único cliente é o próprio celular do usuário, na mesma wifi doméstica.
- O banco (SQLite) suporta um único escritor por vez — adequado para 1
  usuário, sem escrita concorrente real.

Cada decisão técnica relevante — e por que a alternativa foi descartada —
está documentada em [`adr/README.md`](adr/README.md): SQLite em vez de
Postgres, heurística em vez de ML, log imutável de tentativas separado
de estado mutável de revisão, IA hospedada em vez de modelo local, e a
migração de monolito Streamlit para API + app mobile.

## Próximos passos

- Trilha de estudo entrelaçada entre matérias, ponderada por incidência
  histórica (`docs/filosofia.md` — hoje a priorização já existe
  [`prioridade_de_estudo()`], mas a trilha por fase ainda cobre 1 matéria
  por vez); bloqueada por conteúdo, não por algoritmo — precisa de mais
  questões de banco de prática além de Ecologia/Óptica
- Correção de redação por IA hospedada (`adr/0006`)
- Modelo de usuário de verdade (tabela + login/sessão), pré-requisito
  pra multiusuário real e pra login/sessão substituir a trava simples
  atual
- Ampliar cobertura de teste no app mobile (hoje só `lib/` tem teste —
  componentes e telas ainda não)
