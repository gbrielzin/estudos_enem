# Inventário de qualidade de extração — Ciências da Natureza (`enem.db`)

Gerado em 2026-09-22, a pedido do Gabriel (revisão do sistema no meio de uma sessão de estudo). Só levanta dado, não conserta nada ainda — decisão de prioridade e arquitetura fica com ele.

Total de questões oficiais em `ciencias_natureza` (fora banco de prática, que são as 347 de `ano=0`/`caderno='banco_pratica'`, óptica/ecologia): **1105** (2010-2025, cadernos duplicados por cor — mesma prova, ordem embaralhada).

## 1. Caderno inteiro sem texto: 2024 azul — ✅ resolvido em 2026-09-23

**Resolução:** `core/copiar_enunciado_entre_cadernos.py 2024 amarelo azul --aplicar` copiou o texto das 44 questões do amarelo para o azul. O casamento de posições não é por texto: vem do `ITENS_PROVA_2024.csv` oficial do INEP (mesmo `CO_ITEM` em `CO_PROVA` 1419 azul e 1420 amarelo, escolhidos por baterem 100% com o gabarito já carregado). Checado antes de gravar: mesmo conjunto de 45 itens nos dois cadernos e gabarito igual nos 44 pares (a 45ª, azul 129 = amarelo 102, é o item anulado que nenhum dos dois tem no banco). Backup automático em `core/backups/enem_20260923_114958.db`. Resultado: 0 de 44 sem texto no 2024 azul.

**Continua aberto:** as 3 do 2021 azul (`2021_azul_100`, `2021_azul_106`, `2021_azul_120`). Não estão na API enem.dev (ela devolve 84 das 90 de Natureza+Matemática de 2021), o banco não tem outro caderno de 2021 para copiar e em `core/inep_ppl/` só há os PDFs da reaplicação/PPL, não os da prova regular. Para resolver, é preciso baixar o PDF da prova regular 2021 (dia 2, azul) do INEP e rodar `extrair_enunciados_pdf.py 2021 azul`.

Texto original do inventário (22/09), mantido como registro:


**44 de 44 questões do 2024_azul estão com `enunciado_texto = NULL`.** O 2024_amarelo (mesma prova, ordem diferente) está completo. É por isso que toda busca de hoje só achou `2024_amarelo_*` e nunca `2024_azul_*` — não é falta de conteúdo, é falha de extração/importação desse caderno específico. Também há 3 questões do 2021_azul sem texto (pontual, não o caderno inteiro).

**Impacto prático:** qualquer questão de 2024 só é "achável" pelo amarelo. Se o amarelo também tiver problema pontual numa questão específica, aquele item de 2024 fica invisível pra busca por palavra-chave.

## 2. Questões que dependem de figura não capturada — reduzido de 259 para 94 em 2026-09-23

**Atualização 2026-09-23:** `importar_enem_dev.py <ano> --aplicar` rodado para 2010-2020, 2022 e 2023. Nas questões que já tinham texto e não tinham imagem, ele baixa a figura da API enem.dev e tira o aviso ⚠️. Antes de gravar, confere a numeração contra o gabarito oficial: deu 98-100% em todos os anos. Foram 195 figuras novas em `core/enunciados/` (171 em 2010-2018, 24 em 2022), conferidas por amostragem (ex.: `2016_azul_48`, figuras 1 e 2 do biodigestor, corretas). Backup antes: `core/backups/enem_20260923_115147.db`.

| Ano | Com aviso (22/09) | Com aviso (23/09) |
|---|---|---|
| 2010-2013 | 74 | 0 |
| 2014-2018 | 110 | 13 |
| 2019-2021 | 13 | 13 |
| 2022 | 13 | 0 |
| 2023 | 11 | 11 |
| 2024 | 19* | 38 |
| 2025 | 19 | 19 |
| **Total** | **259** | **94** |

\* Em 22/09, as 44 do 2024 azul estavam sem texto nenhum, então não entravam na contagem. Com o texto copiado do amarelo, o aviso delas também foi copiado (19 → 38).

**O que falta, e por quê:**
- **2024 e 2025 (57):** a API ainda não cobre esses anos. Precisa do PDF da prova regular e rodar `extrair_figuras_pdf.py`. Em `core/inep_ppl/` só há PPL.
- **2023 (11):** a Natureza 2023 do banco está no caderno **cinza**, e a API numera pelo azul. Dá para resolver com o mesmo mapeamento `ITENS_PROVA` de `copiar_enunciado_entre_cadernos.py` (azul da API → cinza do banco), mas isso ainda não foi implementado.
- **2014-2021 (26):** a API não tem imagem para essas questões, ou o aviso é falso positivo (texto cita "figura" mas a questão não depende dela). Precisa olhar uma a uma.

Texto original do inventário (22/09), mantido como registro:


**259 de 1105 (23%)** carregam o aviso "pode depender de figura/gráfico/tabela que a extração não capturou". Distribuição por ano:

| Ano | Com aviso | Total | % |
|---|---|---|---|
| 2010 | 16 | 45 | 36% |
| 2011 | 21 | 45 | 47% |
| 2012 | 17 | 45 | 38% |
| 2013 | 20 | 44 | 45% |
| 2014 | 22 | 45 | 49% |
| 2015 | 18 | 45 | 40% |
| 2016 | 22 | 44 | 50% |
| 2017 | 23 | 45 | 51% |
| 2018 | 25 | 45 | 56% |
| 2019 | 2 | 45 | 4% |
| 2020 | 11 | 44 | 25% |
| 2021 | — | 45 | — |
| 2022 | 13 | 45 | 29% |
| 2023 | 11 | 45 | 24% |
| 2024 | 19 | 88 | 22% |
| 2025 | 19 | 43 | 44% |

**Padrão claro: 2010-2018 tem taxa muito mais alta (36-56%) que 2019-2025 (4-29%, com exceção de 2025).** Faz sentido — 2010-2018 é o corpus recém-importado (commit de hoje mesmo, "importa Natureza 2010-2018"), ainda não passou pelo mesmo processo de revisão/uso que 2019-2025 (que já foram resolvidas em prática e erros de extração provavelmente já apareceram e foram corrigidos ao longo do uso).

**Risco concreto:** ao escolher questão de 2010-2018 pra diagnóstico, quase metade das vezes vai ter uma figura essencial faltando — hoje mesmo descartei várias por isso (`2013_azul_73`, `2022_azul_128`, `2022_azul_125`, etc.).

## 3. O que este documento NÃO decide

- Não prioriza se vale mais a pena reprocessar 2010-2018, reimportar o 2024_azul, ou seguir sem mexer (o corpus já tem cobertura via outros cadernos/anos pra muita coisa).
- Não propõe pipeline de correção — isso depende de como o 2024_azul e o 2010-2018 foram originalmente extraídos (`core/construir_corpus_analise.py` e o importador do `enem.db`, que não li a fundo aqui).

## PPL — teste rápido de viabilidade (resultado: viável)

Testei extração de texto com `pymupdf` (já disponível no ambiente Python, não precisa instalar nada) em `2019_PV_reaplicacao_PPL_D2_CD5.pdf` (dia 2 = Ciências da Natureza + Matemática). Resultado: **texto limpo, estruturado, com contexto + enunciado + alternativas completos**, mesmo padrão de qualidade do que já está em `enem.db` pra 2019-2025 (inclusive as mesmas falhas de encoding de acento que o resto do banco já tem e que os scripts existentes já sabem tratar).

**Conclusão prática:** o "2/10" de PPL não é dificuldade técnica — a ferramenta que já existe no projeto dá conta. É trabalho de pipeline não começado (extrair todos os PDFs de `core/inep_ppl/`, separar questão por questão, mapear gabarito oficial do INEP, importar pro `enem.db` no mesmo formato de `id_questao`). Isso é decisão de arquitetura/prioridade dele, não vou começar a implementar sem ele decidir (seguindo o padrão já estabelecido: gargalo é dado, e ele quer organizar isso antes de eu mexer).

Nota: o PDF de dia 1 (`2015_PV_reaplicacao_PPL_D1_CD9.pdf`) testado primeiro era de Ciências Humanas, não Natureza — confirma que os PDFs de PPL seguem a mesma separação dia 1 (Linguagens+Humanas) / dia 2 (Natureza+Matemática) da prova regular. Pra Natureza, usar sempre os arquivos `_D2_`.
