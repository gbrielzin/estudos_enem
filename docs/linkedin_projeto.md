# ENEM GI — material pra seção de Projetos do LinkedIn

Rascunho pronto pra copiar/colar e ajustar. Separado em blocos porque o
campo "Descrição" de projeto do LinkedIn tem limite de caracteres — use o
resumo curto lá, e o resto (stack, decisões, roadmap) fica de referência
pra você adaptar em entrevista ou num link externo (ex: um README do
repo, se ele virar público, ou um post separado).

Tudo aqui reflete o estado real do código nesta data (2026-09-15) — não
infla nada que ainda não existe. A seção "Roadmap" é honesta sobre o que
é plano, não implementação.

---

## 1. Resumo curto (campo "Descrição" do LinkedIn, ~2-3 linhas)

> Sistema pessoal de estudo pro ENEM: app mobile/web (React Native + Expo)
> com backend próprio em Python (FastAPI + SQLite), repetição espaçada
> (Leitner), pipeline de extração de dados de PDFs oficiais do INEP, e um
> algoritmo de priorização de estudo por ROI (incidência histórica ×
> taxa de erro). Arquitetura documentada via ADRs, com decisões técnicas
> justificadas por trade-off real, não por padrão de mercado.

Versão ainda mais curta (se o campo cortar):

> App de estudo (React Native/Expo + FastAPI + SQLite) com repetição
> espaçada, extração automática de questões de PDFs oficiais e um
> algoritmo próprio de priorização de conteúdo por ROI.

---

## 2. Descrição completa (pra entrevista ou README)

Ferramenta que comecei pra resolver um problema meu — estudar pro ENEM de
forma orientada a dado, não a "sensação" de progresso — e que virou um
projeto de engenharia de verdade: reescrevi a versão original (protótipo
em CSV único, com bugs reais de schema e taxonomia) do zero em cima de um
banco relacional, depois migrei a camada de apresentação de um app
Streamlit single-process pra uma arquitetura cliente-servidor de verdade
(API REST + app React Native), sem nunca precisar reescrever a lógica de
negócio do meio (repetição espaçada, priorização, taxonomia) — prova de
que a separação em camadas desde o início compensou.

Pontos que mostram profundidade técnica, não só "usei tal framework":

- **Pipeline de dados real**: extrai gabarito e enunciado de PDFs oficiais
  do INEP (`pymupdf`, detecção de figura vetorial vs. imagem embutida,
  parsing de layout em 2 colunas), cruza com uma API pública externa
  (enem.dev) pra cobrir o que o PDF não consegue por construção, e
  reconcilia os dois sem duplicar ou perder classificação manual feita
  antes.
- **Modelagem de dado com intenção**: log de tentativas **imutável**
  (append-only) separado do estado mutável de revisão — a mesma lógica
  por trás de sistema de auditoria/contábil (nunca sobrescreve histórico,
  sempre recalcula estado a partir da fonte da verdade).
- **Algoritmo de priorização explicável**: cada recomendação de estudo
  vem com a conta em aberto (peso × recorrência, contribuição de cada
  termo) — decisão consciente de não usar ML numa base pequena demais pra
  justificar (documentado em ADR: heurística determinística > modelo
  black-box prematuro).
- **Decisões arquiteturais documentadas via ADR** (Architecture Decision
  Records) — cada escolha técnica relevante (SQLite em vez de Postgres,
  monólito em vez de microsserviço, heurística em vez de ML, IA hospedada
  em vez de modelo local) tem um documento curto justificando o trade-off
  e quando revisitar a decisão. Não é só "código que funciona", é
  raciocínio de engenharia registrado.

---

## 3. Stack tecnológica atual

**Mobile / Frontend** (mesmo código roda em iOS, Android e Web):
`React Native`, `Expo` (Expo Router, file-based routing), `TypeScript`,
`React Native Reanimated` (animações), `React Native SVG`, `react-native-web`
(web a partir do mesmo código nativo, zero reescrita)

**Backend / API:**
`Python`, `FastAPI`, `Uvicorn`, `Pydantic` (validação de request/response)

**Dados:**
`SQLite` (schema relacional com `PRAGMA foreign_keys`), SQL puro (sem ORM,
decisão deliberada pro tamanho do projeto)

**Pipeline de extração de dados:**
`PyMuPDF` (parsing de PDF, geometria de página, recorte de figura
vetorial), `pandas`, `requests` (consumo de API externa), `Pillow`

**Ferramenta legada (ainda em uso pessoal, sem mais investimento visual):**
`Streamlit`

**Prática de engenharia:**
Architecture Decision Records (ADRs), separação em camadas (`db.py` como
leaf module — zero dependência de UI), controle de versão Git com
disciplina de commit por decisão

---

## 4. Roadmap (o que vem depois — mostra visão de produto e maturidade técnica)

Itens já decididos/planejados no projeto, ainda não implementados:

- **Integração com IA hospedada** (API da Anthropic/Claude) pra correção
  automática de redação contra a rubrica pública do ENEM (5 competências)
  — decisão já tomada via ADR de usar API hospedada em vez de modelo
  local (Llama/Ollama), justamente pra funcionar igual local ou em
  produção na nuvem.
- **Testes automatizados** na camada de regra de negócio (`db.py` já é
  isolado o suficiente pra isso ser barato — zero dependência externa).
- **CI** rodando os testes a cada push.
- **Deploy em nuvem própria do backend FastAPI** (hoje só roda local/wifi
  doméstica) — candidatos naturais: Render/Railway/Fly.io ou um free tier
  de AWS/GCP, com o SQLite trocado por Postgres se o projeto crescer pra
  multiusuário de verdade (decisão de manter SQLite hoje já está
  documentada como reversível, não permanente).
- **Autenticação multiusuário** — pré-requisito pra "Liga"/ranking (hoje
  decorativo, single-user) virar social de verdade.

---

## 5. Bullet points prontos (formato "verbo de ação" pra colar direto)

- Arquitetei e implementei um app mobile/web multiplataforma (React
  Native + Expo) consumindo uma API REST própria (Python/FastAPI)
  desenhada e versionada do zero.
- Construí um pipeline de extração automática de dados a partir de PDFs
  oficiais (parsing de geometria de página, detecção de figura vetorial)
  cruzado com API pública externa, com validação cruzada contra gabarito
  oficial pra garantir integridade do dado.
- Desenhei um modelo de dados relacional (SQLite) com log de eventos
  imutável e estado derivado recalculável, evitando divergência entre
  histórico e estado atual.
- Implementei um algoritmo de repetição espaçada (Leitner) e um sistema
  de priorização de estudo explicável, com decisões de design registradas
  formalmente via Architecture Decision Records.
- Migrei a camada de apresentação de um monólito Streamlit pra uma
  arquitetura cliente-servidor (API + app nativo) preservando 100% da
  lógica de negócio já validada, sem reescrever regra nenhuma.

---

## 6. Palavras-chave pra busca/ATS (tags soltas)

Python · FastAPI · REST API · SQLite · SQL · React Native · Expo ·
TypeScript · React · Pydantic · PyMuPDF · Data Pipeline · ETL ·
Arquitetura de Software · Architecture Decision Records (ADR) ·
Modelagem de Dados · Algoritmos · Spaced Repetition · Streamlit ·
Git · Engenharia de Software · Mobile Development · Cross-platform
