# Ferramentas pouco conhecidas que resolvem problema de dado

Lista montada em 2026-09-27, a partir do que foi usado de verdade no projeto (✅) e do que vale conhecer pra estágio de dados. Critério: coisa que a maioria dos estudantes não conhece e que muda o que dá pra fazer. Para cada uma: o que é, quando usar, custo.

## 1. Onde achar dado (o que já existe pronto)

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Microdados do INEP** | Resultado individual (anonimizado) de todos os participantes do ENEM, Censo Escolar, SISU | Qualquer pergunta "quantas pessoas...", "em que competência..." | Grátis | ✅ nota de redação por competência de 3,46 mi pessoas (2025) |
| **Hugging Face Datasets** | Biblioteca pública de datasets pra IA (texto, imagem, áudio) | Antes de coletar do zero: alguém pode já ter montado | Grátis (alguns pedem login/aceite) | ✅ 63 notas 1000 do g1/O Globo com nota por competência |
| **Base dos Dados** (basedosdados.org) | Dados públicos brasileiros limpos e ligados entre si, consultáveis em SQL (BigQuery) | Cruzar ENEM com IBGE, renda, escola, município | Grátis até uma cota | — |
| **dados.gov.br** | Catálogo oficial de dados abertos do governo federal | Qualquer dado de órgão federal | Grátis | — |
| **Kaggle** | Datasets + notebooks de outras pessoas | Ver como alguém já analisou um dado parecido | Grátis | — |
| **Google Dataset Search** | Buscador só de datasets | "Existe dataset de X?" | Grátis | — |
| **OpenAlex** | Catálogo aberto de ~250 milhões de artigos científicos | Achar pesquisa com dado sobre um tema (ex.: método de estudo) | Grátis, com API | — |
| **GDELT** | Notícias do mundo inteiro catalogadas desde 2015, com tema e tom | Tendência de assunto (ex.: temas que viram redação) | Grátis | — |

## 2. Como coletar sem visitar site por site

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Common Crawl** | Cópia mensal de bilhões de páginas da web, com índice de URLs aberto | Achar páginas de um assunto sem crawler próprio | Grátis | ✅ 197 páginas de redação em 28 sites |
| **Wayback Machine** (web.archive.org) | Arquivo histórico da web desde os anos 90, com API (CDX) | Recuperar página que saiu do ar; ver como um site era numa data | Grátis | — |
| **Range request (HTTP)** | Baixar só um pedaço de um arquivo remoto | Ler o índice de um ZIP gigante sem baixar tudo | Grátis | ✅ `rz.py`: ler 2 GB do INEP em fluxo |
| **pymupdf** | Extrair texto/imagem de PDF em Python | Qualquer PDF oficial (provas, cartilhas) | Grátis | ✅ cartilhas e provas do INEP |
| **Tesseract (OCR)** | Ler texto de imagem | Foto de redação, espelho, documento escaneado | Grátis | — |

Regra que acompanha todas: só página pública, respeitar bloqueio e termo de uso, não usar conta de terceiros. Coleta que contorna bloqueio é o que derruba a credibilidade de um projeto de dados.

## 3. Como processar dado grande num PC comum

| Ferramenta | O que é | Quando usar | Custo |
|---|---|---|---|
| **DuckDB** | Banco analítico que roda SQL direto em CSV/Parquet, inclusive remoto | Arquivo grande demais pro Excel/pandas; consultar Parquet na internet sem baixar | Grátis |
| **Parquet** | Formato de tabela comprimido e colunar | Guardar dataset grande (10x menor que CSV e muito mais rápido) | Grátis |
| **Polars** | Alternativa ao pandas, muito mais rápida | Tabela com milhões de linhas | Grátis |
| **SQLite + FTS5** | Busca de texto completo dentro do SQLite | "Achar todas as redações que citam Bauman" em milissegundos | Grátis |

## 4. IA aplicada a dado

| Ferramenta | O que é | Quando usar |
|---|---|---|
| **Extração estruturada com LLM** | Pedir pra IA transformar texto livre em campos (ex.: dica, competência, fonte) | Texto que regra de código não resolve (o banco de dicas) |
| **Embeddings + busca semântica** | Representar texto como vetor pra achar "parecidos" mesmo com palavras diferentes | Agrupar dicas iguais escritas de jeitos diferentes; achar redação parecida com a sua |
| **Agentes em loop / rotinas agendadas** | IA repetindo uma tarefa em intervalo ou na nuvem | Fase de descoberta de fontes (o loop de hoje); coleta mensal |

## 5. Engenharia (o que separa script de projeto)

| Ferramenta | O que é | No projeto |
|---|---|---|
| **Pipeline reprodutível** | Script que refaz o dado do zero com um comando | ✅ `coleta_redacoes.py` |
| **Teste com dado sintético** | Testar o extrator sem pôr dado de terceiro no repo | ✅ `test_coleta_redacoes.py` |
| **Cartão de dados (data card)** | Documento de fontes, licença e limites | ✅ `docs/redacao_pesquisa/fontes.md` |
| **GitHub Actions** | Rodar teste e coleta automática na nuvem | ✅ CI do projeto |
| **ADR** | Registro de decisão de arquitetura | ✅ `adr/` |

## Como usar isso numa entrevista de estágio

Não é listar ferramenta; é contar o problema e por que a ferramenta resolveu. Exemplo pronto: *"Queria saber em que competência quem tira 900+ perde ponto. Os microdados do INEP têm 2 GB por ano; em vez de baixar, li o ZIP em fluxo com range request e guardei só um resumo de 3 KB. Resultado: 96% de quem tira 960-980 não faz 200 em gramática."*
