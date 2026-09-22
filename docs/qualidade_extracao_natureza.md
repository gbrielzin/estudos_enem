# Inventário de qualidade de extração — Ciências da Natureza (`enem.db`)

Gerado em 2026-09-22, a pedido do Gabriel (revisão do sistema no meio de uma sessão de estudo). Só levanta dado, não conserta nada ainda — decisão de prioridade e arquitetura fica com ele.

Total de questões oficiais em `ciencias_natureza` (fora banco de prática, que são as 347 de `ano=0`/`caderno='banco_pratica'`, óptica/ecologia): **1105** (2010-2025, cadernos duplicados por cor — mesma prova, ordem embaralhada).

## 1. Caderno inteiro sem texto: 2024 azul

**44 de 44 questões do 2024_azul estão com `enunciado_texto = NULL`.** O 2024_amarelo (mesma prova, ordem diferente) está completo. É por isso que toda busca de hoje só achou `2024_amarelo_*` e nunca `2024_azul_*` — não é falta de conteúdo, é falha de extração/importação desse caderno específico. Também há 3 questões do 2021_azul sem texto (pontual, não o caderno inteiro).

**Impacto prático:** qualquer questão de 2024 só é "achável" pelo amarelo. Se o amarelo também tiver problema pontual numa questão específica, aquele item de 2024 fica invisível pra busca por palavra-chave.

## 2. Questões que dependem de figura não capturada

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
