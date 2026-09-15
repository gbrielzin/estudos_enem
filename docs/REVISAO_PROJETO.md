# Revisão geral do projeto — ENEM GI

> ⚠️ **Documento histórico, desatualizado na arquitetura.** Retrato de
> **2026-09-02** — descreve o sistema como um monólito Streamlit sem API
> nem HTTP. Isso mudou: hoje existe uma API REST própria (`core/api.py`,
> FastAPI) e um app Expo/React Native como produto principal (ver
> `adr/0007`). `enem.db` também não é mais versionado no Git (ver
> `.gitignore` e `adr/0009`) — este documento ainda descreve a versão
> antiga desse ponto. **Para o estado atual, ver `README.md` (raiz) e
> `adr/`.** Mantido aqui só como registro histórico de raciocínio válido
> à época.

Retrato de **2026-09-02**. Como o próprio `core/manual_prioridade_de_estudo.md`
já avisa sobre os números que cita: isto é uma fotografia do estado do código
e do banco *agora* — contagens de linhas/questões vão mudar. O raciocínio
arquitetural (por que as coisas são como são) é a parte que dura.

Responde, nesta ordem, as perguntas que motivaram este documento: arquitetura,
onde estão os dados, estrutura do banco, como o sistema é alimentado, como o
Streamlit fala com o "backend", onde entra ML, se já existe ML, se dá pra
colocar uma IA (tipo Llama) agora, o que falta, e qual a próxima
funcionalidade realmente importante.

---

## 1. Qual é a arquitetura?

Não é client-server. É **um processo Python só**: `streamlit run
cartao_resposta.py` sobe um único processo que é front-end e "back-end" ao
mesmo tempo. Não existe API REST, não existe outro serviço rodando, não
existe fila/worker separado.

```
core/cartao_resposta.py   ← entrypoint único (1548 linhas)
        │  import direto (chamada de função Python, não HTTP)
        ▼
core/db.py                ← toda a lógica de dados/negócio (2122 linhas)
        │  sqlite3 (stdlib, sem ORM)
        ▼
core/enem.db               ← um arquivo SQLite
```

Módulos irmãos de `db.py`, todos consumidos por `cartao_resposta.py` e cada
um também importando de `db.py`:

| Módulo | Linhas | Papel |
|---|---|---|
| `db.py` | 2122 | schema, taxonomia, CRUD, Leitner, prioridade, redações — o "backend" de verdade |
| `cartao_resposta.py` | 1548 | única entrypoint Streamlit; 12 páginas por função (`render_*`), navegação por `?pagina=` |
| `coletar_videos.py` | 500 | liga vídeo/texto de resolução a questões, grava direto no banco |
| `ui_theme.py` | 381 | CSS complementar ao `.streamlit/config.toml` |
| `reconstruir_base.py` | 250 | carrega/atualiza `enem.db` a partir dos CSVs de gabarito |
| `triagem.py` | 101 | classificação manual de questões `nao_classificado` |
| `backup_db.py` | 63 | snapshot timestampado de `enem.db` |

**Regra de camadas (explícita no topo de `db.py` e em `core/CLAUDE.md`):**
`db.py` não importa nada de módulo de UI e não tem nenhuma dependência fora
da stdlib — é uma **folha**. Todo o resto importa *dele*, nunca o contrário.
É a única coisa que faz o papel de "contrato de API" num projeto que não tem
API de verdade: qualquer lógica nova de UI que precise virar dado
compartilhado tem que subir pra `db.py`, nunca o caminho inverso.

**Sistema legado, na raiz do repo (`main.py`, `app.py`):** um protótipo
anterior a `core/`, guardava tudo num CSV único (`questoes_enem_classificadas.csv`)
e tinha bugs de verdade (dois scripts gravando esquemas diferentes no mesmo
arquivo, taxonomia fragmentada por string). `core/` é uma reescrita do zero
projetada especificamente pra tornar essa classe de bug impossível por
construção (banco relacional com schema/tipo centralizado). `core/` **não**
importa da raiz, com uma única exceção sancionada: `coletar_videos.py` importa
de `main.py` só a autenticação OAuth/busca do YouTube já testada, pra não
duplicar código que já funciona. `app.py` (raiz) continua vivo só porque tem
um modo de busca automática por palavra-chave que ainda não foi portado —
não é "o produto", é `core/cartao_resposta.py`.

---

## 2. Onde estão os dados?

Tudo dentro de `core/`, nenhum banco externo, nenhuma nuvem própria (a não
ser o deploy do app em si — ver `DEPLOY.md`):

| Local | O quê | Tamanho hoje |
|---|---|---|
| `core/enem.db` | banco SQLite principal — questões, tentativas, resoluções, config | 811 KB, 754 questões |
| `core/enunciados/*.png` | recortes de figura/gráfico/tabela extraídos dos PDFs ou baixados da API | 202 arquivos, ~12 MB |
| `core/gabaritos_reais/*.csv` | gabarito oficial por ano/caderno/área — fonte da verdade que alimenta `enem.db` | 17 CSVs |
| `core/backups/*.db` | snapshots timestampados de `enem.db`, gerados antes de cada `reconstruir_base.py` | 8 arquivos (gitignored — só nesta máquina) |
| `core/vision_board/` | fotos do quadro de objetivos (página "Objetivos") | gitignored, vazio hoje |
| `.env` (raiz) | `YOUTUBE_API_KEY` | gitignored |

Tudo isso (menos o que está listado em `.gitignore`) vai **junto no git**,
inclusive `enem.db` — é assim que o banco chega no Streamlit Community Cloud
no deploy (ver `DEPLOY.md`), e é por isso que o repositório precisa
continuar **privado**.

---

## 3. Como o banco está estruturado?

`core/schema.sql`, SQLite, `PRAGMA foreign_keys = ON`. Estado atual (linhas
por tabela):

| Tabela | Linhas | Papel |
|---|---|---|
| `questoes` | 754 | 1 linha por questão real. PK = `id_questao` canônico (`"{ano}_{caderno}_{numero}"`, ex. `2024_azul_136`) |
| `tentativas_usuario` | 587 | log **append-only** de toda resposta dada, nunca editado in-loco |
| `estado_revisao` | 468 | ponteiro **mutável** de repetição espaçada (1 linha por questão já tentada) |
| `resolucoes` | 536 | N resoluções (vídeo e/ou texto) por questão |
| `historico_alteracoes` | 499 | auditoria: toda correção de gabarito/matéria feita depois que já havia tentativa |
| `topicos_validos` | 89 | espelho, no banco, da taxonomia fechada que vive em `TAXONOMIA_VALIDA` (`db.py`) |
| `configuracoes` | 3 | chave-valor (data da prova, meta diária, metas de nota) |
| `redacoes` | 1 | tema/texto/nota/observações de redações escritas |
| `nomes_tentativas` | 0 | rótulo opcional por rodada de simulado |

Decisões de design que valem a pena entender (não são óbvias olhando só a
tabela):

- **Sem `FOREIGN KEY` de `questoes` pra `topicos_validos`, de propósito.**
  Uma questão com matéria fora da taxonomia fechada ainda precisa ser
  *gravada* (com `status_classificacao='nao_classificado'`), não rejeitada —
  é o que alimenta a fila de triagem (`triagem.py`).
- **`tentativas_usuario` (imutável) vs. `estado_revisao` (mutável) são
  tabelas separadas de propósito** — histórico de verdade não pode ser a
  mesma coisa que "o que revisar hoje", ou vira a mesma ambiguidade que o
  `.update()` do sistema legado tinha.
- **Leitner simplificado** (`_calcular_leitner()` em `db.py:595`): errou →
  streak zera, revisão em 1 dia. Acertou → streak+1, intervalo =
  `2^(streak-1)` dias, teto de 90. Recalculado do zero a cada mudança
  (nunca ajustado incrementalmente), então nunca "deriva" de um estado
  corrompido — é 100% reconstruível a partir de `tentativas_usuario`.
- **`resposta_escolhida` aceita `NULL`** — questão em branco é uma tentativa
  real (sempre `resultado='errou'`), não a ausência de uma. Isso importa pro
  cálculo de taxa de acerto e pro Leitner não subestimarem erro.
- **`redacoes` é uma tabela isolada**, sem `FOREIGN KEY` pra nada — guarda,
  não corrige (nota e erro ortográfico vêm de correção externa, digitados
  à mão). É a única tabela sem menção nenhuma em `core/CLAUDE.md` hoje (ver
  seção 8).

---

## 4. Como o sistema é alimentado com PDFs, questões e provas?

Pipeline em **duas fases bem separadas**, nunca misturadas: primeiro o
gabarito (o que garante que a questão existe e tem resposta certa), depois
— só depois, em cima de linhas que já existem — o enunciado/imagem.

**Fase 1 — gabarito (cria a linha em `questoes`):**

| Script | Entrada | Saída |
|---|---|---|
| `extrair_gabarito_pdf.py` | PDF oficial do INEP (GB) + `pdftotext` | `gabaritos_reais/gabarito_<ano>_<caderno>[_CIENCIAS]_OFICIAL.csv` |
| `reconstruir_base.py` | todos os CSVs em `gabaritos_reais/` + `correcoes_manuais.csv` (triagem persistida) | `enem.db` atualizado **in-place**, idempotente (faz backup antes, nunca apaga o banco) |

**Fase 2 — enunciado/imagem (só faz `UPDATE`, nunca `INSERT`):**

| Script | Fonte | Cobre o quê |
|---|---|---|
| `extrair_enunciados_pdf.py` | mesmo PDF, via `pymupdf` | texto da questão + alternativas; marca ⚠️ quando detecta menção a figura/gráfico que o PDF desenha como vetor (não recupera sozinho) |
| `extrair_figuras_pdf.py` | mesmo PDF | recorta a figura vetorial em PNG, associa à "Questão N" mais próxima na ordem de leitura em 2 colunas |
| `importar_enem_dev.py` | API pública `enem.dev` (só 2009–2023) | cobre o que os dois scripts de PDF **não conseguem por construção**: foto embutida de verdade (tirinha) ou imagem já separada por alternativa |

Caminhos manuais complementares: colar CSV de gabarito e editar questão
individual em **Admin**; upload avulso de imagem de enunciado dentro do
próprio Cartão-resposta; classificação manual de matéria em **Triagem**
(persistida em `gabaritos_reais/correcoes_manuais.csv` pra sobreviver a um
`reconstruir_base.py` — ver seção 8, esse arquivo ainda não existe).

Nenhum desses scripts é automático/agendado — todos são rodados a mão,
um `ano`/`caderno` por vez, e o próprio `core/CLAUDE.md` recomenda
conferência humana pontual (especialmente nas questões marcadas ⚠️).

---

## 5. Como o Streamlit conversa com o "backend"?

Não conversa por rede — **não existe HTTP entre eles**. `cartao_resposta.py`
faz `import db` e chama função Python diretamente
(`db.registrar_tentativa(...)`, `db.prioridade_de_estudo(...)`), no mesmo
processo, síncrono, sem serialização.

Pontos que decorrem disso e valem entender:

- **Sem pool de conexão.** `db._conectar()` (linha 348) abre uma conexão
  sqlite3 nova a cada chamada de função e fecha no fim dela — não há
  conexão persistente nem ORM (SQL puro, stdlib).
- **Sem sessão/cache própria.** Streamlit reprocessa o script inteiro a
  cada interação do usuário (rerun model). O que precisa sobreviver a um
  rerun vive em `st.session_state` (chaves de widget, contadores de upload)
  ou é gravado direto no SQLite — não há camada intermediária de cache.
- **"API" = a assinatura das funções de `db.py`.** A regra de camadas da
  seção 1 é o que faz esse contrato não virar espaguete: qualquer página
  Streamlit pode chamar qualquer função pública de `db.py`, mas `db.py`
  nunca sabe que Streamlit existe.
- Isso é adequado pro tamanho do projeto (1 usuário, uso pessoal) — o custo
  apareceria só se o projeto precisasse de multi-usuário concorrente ou de
  rodar fora de um processo Streamlit (ex. um app mobile nativo
  consumindo os mesmos dados exigiria extrair `db.py` atrás de uma API de
  verdade).

---

## 6. Onde entra o ML? O sistema já tem machine learning?

**Não. Hoje não existe nenhum modelo treinado em lugar nenhum do projeto** —
nem em `core/`, nem no legado da raiz. Busquei por `sklearn`, `tensorflow`,
`torch`, `xgboost`, embeddings, classificador etc. no `requirements.txt` e em
todo o código: zero ocorrências.

O que existe e **parece** ML de longe, mas é heurística determinística:

| O que parece ML | O que é de verdade | Onde |
|---|---|---|
| Repetição espaçada (Leitner) | fórmula fixa (streak/intervalo), sem parâmetro aprendido | `db._calcular_leitner()` |
| "Prioridade de estudo" | média ponderada de recorrência × taxa de erro, pesos fixos (`peso_recorrencia`) calculados ao vivo via SQL | `db.prioridade_de_estudo()` (linha 1211) |
| Classificação de matéria | dicionário de sinônimos + regex (`canonicalizar_materia`, `_PADROES_MATERIA`) | `db.py` |

Nenhuma dessas três "aprende" com o tempo no sentido de ML — são regras e
agregações estatísticas simples sobre os dados ao vivo, reavaliadas do zero
a cada consulta. E isso é uma escolha razoável no estágio atual: com 587
tentativas registradas (e uma pessoa só gerando os dados), não há volume
suficiente pra treinar um modelo que supere essas heurísticas — o próprio
`manual_prioridade_de_estudo.md` reconhece isso na seção 6 ("o banco hoje só
tem 6 provas... não invalida [o ranking], mas é por isso que ele empata").

A única coisa "IA" que já existe no projeto hoje é **manual e externa ao
app**: três prompts prontos pra colar num chat separado (ChatGPT/Gemini/
Claude) —

- `core/guia_estudante.md` — Tutor Socrático de Ciências da Natureza +
  Síntese Semanal
- `core/prompt_extracao_gabarito.md` — extração de gabarito de PDF

Zero chamada de API de LLM a partir do código. É prompt engineering como
documentação estática, não integração.

---

## 7. Dá pra colocar uma IA (Llama ou algo do tipo) agora?

Tecnicamente sim, e é mais simples do que parece dado como o projeto já é
estruturado — mas **Llama local não é a escolha certa aqui**, e vale
explicar por quê antes de recomendar a alternativa.

**Opção A — modelo local (Llama via Ollama, por exemplo).** Roda de graça
por chamada, mas exige um processo à parte (Ollama) rodando na mesma
máquina que serve o Streamlit, com RAM/CPU (idealmente GPU) suficiente pro
modelo. O **Streamlit Community Cloud** — que é o deploy que `DEPLOY.md` já
preparou, justamente pra "rodar de qualquer lugar, do celular, sem notebook
ligado" — não tem GPU, não roda processo de fundo próprio, e é free tier com
recurso limitado. Ou seja: Llama local só funciona enquanto o app roda na
sua própria máquina (opção 1 do `DEPLOY.md`, mesma wifi) — o que contradiz
o objetivo de acesso remoto que o projeto já persegue.

**Opção B — modelo hospedado via API (Claude, por exemplo).** Uma chamada
HTTP simples, paga por uso (centavos por chamada num modelo pequeno),
funciona **idêntico** rodando local ou no Streamlit Cloud — porque quem faz
o trabalho pesado é o servidor da Anthropic, não a máquina que roda o app.
O padrão de integração já existe no projeto: `YOUTUBE_API_KEY` já é lido do
`.env` local e cai pros **Secrets** do Streamlit Cloud quando `.env` não
existe (mesmo código, os dois lugares — `main.py`). Repetir esse padrão com
uma `ANTHROPIC_API_KEY` é a mesma receita: um módulo novo (`core/ia.py`,
seguindo a mesma regra de camada que os outros módulos seguem hoje) e uma
linha nova em `requirements.txt`.

**Minha recomendação:** opção B. Dado que você já escolheu o objetivo de
"rodar de qualquer lugar" (`DEPLOY.md` já existe pra isso), um modelo local
resolveria um problema que você não tem (custo) criando um que você não
quer (só funciona com o notebook ligado). Guardo Llama/Ollama como "modo
offline" possível *depois*, se um dia esse objetivo mudar — não como
ponto de partida.

Dois pontos de entrada concretos pra essa integração, ambos já meio
desenhados pelo próprio projeto (ver seção 9 pra qual eu recomendo
primeiro):

1. **Correção de redação** — `redacoes` (tabela + `render_redacao()`) hoje
   só guarda nota/observações digitadas à mão; `fonte_correcao` já tem um
   `CHECK(... IN ('propria','externa','oficial') OR NULL)` em `schema.sql`
   que bastaria estender com `'ia'`.
2. **Tutor Socrático embutido no app** — `core/guia_estudante.md` já
   termina com uma seção "O que fica pra depois do ENEM" citando uma
   tabela `analise_ia` ligada a `resolucoes` pra isso exatamente. Ou seja:
   você já esboçou essa ideia sozinho antes deste documento existir.

---

## 8. O que ainda está faltando?

Verificado direto no banco/repo hoje, não é achismo:

- **Cobertura de enunciado/imagem incompleta.** Só **337/754 (44,7%)**
  questões têm `enunciado_texto`, e só **202/754 (26,8%)** têm imagem — é
  por isso que "Prova com enunciado (beta)" cobre só uma fração das provas
  carregadas. Os últimos 4 commits do repo são exatamente esse trabalho em
  andamento (`importar_enem_dev.py` pra 2019/2021/2022/2023 azul); como a
  API cobre só até 2023, **2024 e 2025 dependem inteiramente do pipeline de
  PDF** (mais manual, com o próprio `core/CLAUDE.md` pedindo conferência
  humana nas questões ⚠️).
- **96 questões (12,7%) ainda `nao_classificado`**, esperando triagem
  manual — e `gabaritos_reais/correcoes_manuais.csv` (onde a triagem
  deveria ficar persistida pra sobreviver a um `reconstruir_base.py`,
  conforme `core/CLAUDE.md`) **ainda não existe**: a fila existe, mas
  nenhuma classificação manual foi salva por ali ainda.
- **`core/CLAUDE.md` está incompleto num ponto concreto:** a tabela
  `redacoes` (em `schema.sql`) e a página inteira "Redação"
  (`render_redacao()`, ~144 linhas em `cartao_resposta.py`) não aparecem
  **nenhuma vez** no arquivo de arquitetura do projeto — toda outra
  feature do mesmo tamanho tem uma seção dedicada, essa não tem nenhuma.
- **O "Retrato de hoje" do próprio `manual_prioridade_de_estudo.md`
  (datado 28/08/2026) já ficou desatualizado**: ele cita "faltam 2022 e
  2025 inteiras [de Ciências]" como motivo de eletrodinâmica empatar no
  ranking — mas essas duas provas já foram carregadas (2022: 45 questões,
  2025: 43 questões, confirmado no banco). O arquivo já se declara
  descartável nesse sentido, mas vale atualizar a data pra não confundir
  uma leitura futura.
- **Nenhum teste automatizado, lint ou CI** — declarado abertamente em
  `core/CLAUDE.md`. Razoável pro tamanho atual, mas `db.py` (2122 linhas,
  zero dependência externa, fácil de testar em isolamento) é exatamente o
  tipo de módulo onde um punhado de testes de regressão no Leitner, na
  canonicalização de matéria e na prioridade de estudo sairia barato e
  protegeria a parte do sistema da qual o método de estudo real depende.
- **IA/ML integrados: zero**, como respondido nas seções 6 e 7 — o gap
  mais estrutural, mas opcional, não um bug.

---

## 9. Qual é a próxima funcionalidade realmente importante?

São duas trilhas, e elas **não competem** — uma é manutenção contínua, a
outra é capacidade nova:

- **Trilha de manutenção (continuar o que já está em andamento):** fechar
  a cobertura de enunciado/imagem e a fila de triagem (seção 8). É
  trabalho mecânico, de baixo risco, e os últimos commits já mostram que
  está sendo feito — vale continuar, mas não é "a próxima funcionalidade",
  é terminar a atual.

- **Capacidade nova, e minha recomendação de foco:** **correção de redação
  por IA**, via API hospedada (seção 7, opção B), como primeira integração
  de verdade. Motivos concretos, não genéricos:
  1. É a única área do sistema com **zero** automação hoje — nota e erro
     ortográfico são 100% digitados à mão, contra uma rubrica pública e
     bem definida (as 5 competências do ENEM), exatamente o tipo de tarefa
     onde um LLM tem baixa ambiguidade pra errar.
  2. A infraestrutura já existe e não precisa de nada novo estrutural:
     tabela `redacoes`, página `render_redacao()`, e um `CHECK` de schema
     que já antecipa mais uma `fonte_correcao` (bastaria adicionar `'ia'`).
  3. É um escopo pequeno e contido pra validar o padrão de integração
     (chave em `.env`/Secrets, módulo novo tipo `core/ia.py`) antes de
     expandir pro Tutor Socrático embutido — que é maior (envolve a UI de
     revisão de erro já existente no Cartão-resposta) mas seria o passo
     natural seguinte, e o próprio projeto já esboçou essa direção em
     `guia_estudante.md`.

Nessa ordem — redação primeiro, tutor embutido depois — dá pra provar a
integração no ponto de menor risco (uma tela isolada, sem tocar no fluxo de
correção/Leitner que todo o resto do app depende) antes de levar IA pro
coração do app.

---

## Resumo

| Pergunta | Resposta curta |
|---|---|
| Arquitetura | Um processo Streamlit só; `db.py` é o "backend" (leaf module), sem API/HTTP interno |
| Onde estão os dados | `core/enem.db` (SQLite) + `core/enunciados/*.png` + `core/gabaritos_reais/*.csv`, tudo versionado no git (repo privado) |
| Estrutura do banco | 9 tabelas relacionais, `id_questao` canônico como PK, histórico imutável separado de estado mutável |
| Alimentação de PDFs/questões | Pipeline em 2 fases: gabarito (PDF→CSV→banco) depois enunciado/imagem (PDF vetorial + API enem.dev), tudo manual/script por script |
| Streamlit ↔ backend | Chamada de função Python direta, mesmo processo, sem rede, sem pool de conexão |
| ML hoje | Não existe — o que parece ML é heurística/estatística determinística (Leitner, prioridade, regex de taxonomia) |
| IA (Llama) agora | Sim, mas hospedada (tipo Claude), não local — Llama local contradiz o objetivo de deploy já escolhido |
| Falta | Cobertura de enunciado/imagem (44,7%/26,8%), triagem (96 pendentes), `CLAUDE.md` sem documentar Redação, zero teste automatizado |
| Próxima funcionalidade | Correção de redação por IA via API hospedada — menor risco, zero automação hoje, infraestrutura já pronta |
