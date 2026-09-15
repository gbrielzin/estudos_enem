# ENEM GI

Sistema pessoal de estudo pro ENEM (Matemática e Ciências da Natureza),
com foco em decisão orientada a dado: o que estudar agora, calculado a
partir de recorrência histórica e da própria taxa de erro — não um
cronograma genérico. Prova em 08/11/2026.

App mobile/web (React Native + Expo) consumindo uma API REST própria
(Python + FastAPI + SQLite), com repetição espaçada (Leitner), correção
automática e um pipeline próprio de extração de questões a partir de PDFs
oficiais do INEP.

## Estado atual (verificado em 2026-09-15 — ver auditoria completa)

- **946 questões** no banco (754 de provas oficiais 2019-2025 + 192 de
  banco de prática próprio)
- **658 tentativas** de usuário registradas
- **13 endpoints REST** (`core/api.py`)
- **9 tabelas** relacionais (SQLite)
- **72 testes automatizados**, cobrindo a camada de regra de negócio
  (`core/test_db.py`)
- **8 ADRs** documentando as principais decisões de arquitetura (`adr/`)

## Stack

- **Mobile/Web:** React Native, Expo (Expo Router), TypeScript,
  React Native Reanimated, `react-native-web` (mesmo código gera app nativo
  e site)
- **Backend:** Python, FastAPI, Pydantic
- **Banco:** SQLite (SQL puro, sem ORM — decisão documentada em
  [`adr/0002`](adr/0002-sqlite-em-vez-de-postgres.md))
- **Pipeline de dados:** PyMuPDF (extração de PDF), pandas, requests
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

## Dados

`core/enem.db` **não é versionado no repositório** (dado pessoal de uso
real — tentativas, streak, configuração). Pra rodar o projeto do zero:

```
cd core
python reconstruir_base.py
```

**Faça um backup primeiro se já tiver um `enem.db` local** (o script já
faz isso sozinho, mas uma cópia extra não faz mal): botão "📦 Fazer
backup agora" na tela Admin do cartão-resposta, ou `python backup_db.py`
de dentro de `core/`. `reconstruir_base.py` não apaga o banco — atualiza
em cima do que já existe, sem perder tentativa registrada nem correção
manual de triagem (idempotente, seguro rodar de novo).

Isso carrega o banco a partir dos gabaritos oficiais já versionados em
`core/gabaritos_reais/*.csv` (17 arquivos, cobrindo 2019-2025) — o mesmo
pipeline usado pra manter o banco real atualizado, não uma cópia
simplificada. O resultado tem o gabarito completo; enunciado/imagem de
questão (que dependem de PDF baixado à parte, não incluso aqui) podem ser
preenchidos depois com `extrair_enunciados_pdf.py`/`importar_enem_dev.py`
(ver `core/CLAUDE.md`).

Não é preciso nenhuma variável de ambiente pra rodar o projeto hoje.

## Rodar o app

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

Rodar os testes automatizados:
```
cd core
python -m unittest test_db
```

Ferramenta pessoal (Streamlit, legado — ver [`core/CLAUDE.md`](core/CLAUDE.md)):
```
cd core
streamlit run cartao_resposta.py
```

## Rodar de qualquer lugar (celular, sem notebook ligado)

Ver [`docs/DEPLOY.md`](docs/DEPLOY.md) — tem uma opção que já funciona
agora (mesma wifi, zero configuração) e uma de deploy de verdade, de
graça (Streamlit Community Cloud), com os passos que só você pode fazer
(login em conta) separados do que já está pronto no código.

## Decisões de arquitetura

Cada decisão técnica relevante — e por que a alternativa foi descartada —
está documentada em `adr/`: SQLite em vez de Postgres, heurística em vez
de ML, log imutável de tentativas separado de estado mutável de revisão,
IA hospedada em vez de modelo local para a próxima integração planejada,
e a migração de monolito Streamlit para API + app mobile. Ver
[`adr/README.md`](adr/README.md) para o índice completo.

## Limitações conhecidas

Este é um projeto pessoal para um único usuário, não um serviço em
produção multiusuário — e isso molda decisões deliberadas, não descuidos:

- A API não tem autenticação nem controle de acesso, e roda com CORS
  aberto (`allow_origins=["*"]`) — adequado hoje porque o único cliente é
  o próprio celular do usuário, na mesma wifi doméstica.
- O banco (SQLite) suporta um único escritor por vez — adequado para 1
  usuário, sem escrita concorrente real.
- Autenticação, controle de acesso e configuração restritiva de CORS
  fazem parte da evolução natural para um cenário multiusuário, ainda não
  implementada.

## Roadmap

- Trilha de estudo entrelaçada entre matérias, ponderada por incidência
  histórica (`docs/filosofia.md` — hoje a priorização já existe
  [`prioridade_de_estudo()`], mas a trilha por fase ainda cobre 1 matéria
  por vez)
- Correção de redação por IA hospedada (`adr/0006`)
- Testes automatizados no app mobile e na API
