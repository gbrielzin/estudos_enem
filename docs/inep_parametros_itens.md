# Parâmetros TRI dos itens do ENEM (Microdados INEP)

Tudo abaixo foi verificado nos arquivos baixados em `core/inep_itens/`.

## Fontes
- Portal: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
- Zips (um por ano, 2009-2025, todos existem): `https://download.inep.gov.br/microdados/microdados_enem_<ANO>.zip`
  (ex.: .../microdados_enem_2024.zip, 526 MB; 2022: 621 MB; 2014: 1,05 GB).
- Dentro de cada zip: `DADOS/ITENS_PROVA_<ano>.csv` (2023-2025 com prefixo `microdados_enem_<ano>/`) e
  `DICIONÁRIO/Dicionário_Microdados_Enem_<ano>.xlsx` (mais .ods e inputs R/SAS/SPSS).
- O servidor aceita Range (HTTP 206 / `Accept-Ranges: bytes`). O arquivo de itens tem 50-330 KB descompactado.

## O que foi baixado
Só o CSV de itens e o dicionário .xlsx de cada ano (17 anos), lidos via range requests no diretório central do zip
(~1-2 MB de tráfego por ano, ~3,6 MB de dados no total; pasta `core/inep_itens/` = 11 MB).
Nenhum zip inteiro foi baixado. Nota técnica: o Python/requests falhou na verificação TLS do host `download.inep.gov.br`
(cadeia de certificados incompleta no servidor); o `curl` do Windows funcionou, então a leitura foi feita com `curl -r`
(`rz.py`). Verificação de certificado NÃO foi desativada.

Arquivos: `<ano>_ITENS_PROVA_<ano>.csv`, `<ano>_Dicionario_*.xlsx`, `all.pkl` (união), `itens_ligados_ao_corpus.csv`
(itens já ligados ao corpus), scripts `rz.py`, `get.py`, `list.py`.

## Colunas (dicionário oficial, aba ITENS_PROVA_2024)
CO_POSICAO (posição do item na prova), SG_AREA (CH/CN/LC/MT), CO_ITEM, TX_GABARITO ("X" = item anulado),
CO_HABILIDADE, IN_ITEM_ABAN, TX_MOTIVO_ABAN, **NU_PARAM_A** (discriminação), **NU_PARAM_B** (dificuldade),
**NU_PARAM_C** (acerto ao acaso), TX_COR, CO_PROVA, e conforme o ano TP_LINGUA, IN_ITEM_ADAPTADO, TP_VERSAO_DIGITAL (2020).
Todos os 17 anos (2009-2025) têm as colunas A/B/C. CO_POSICAO vai de 1 a 180 e o bloco de cada área muda por ano: 2009 CN 1-45, CH 46-90, LC 91-135, MT 136-180;
2015 CH 1-45, CN 46-90, LC 91-135, MT 136-180; 2022-2025 LC 1-45 (inclui idioma), CH 46-90, CN 91-135, MT 136-180.
Não há coluna com a matéria/tópico do item, só CO_HABILIDADE (H1..H30 da matriz).

## Cobertura por ano (linhas = item x prova/caderno; A/B/C preenchidos)
| Ano | linhas | itens únicos | provas (CO_PROVA) | com B | abandonados |
|---|---|---|---|---|---|
| 2009 | 1440 | 359 | 32 | 1412 | 28 |
| 2010 | 1480 | 370 | 32 | 1388 | 92 |
| 2011 | 925 | 370 | 20 | 906 | 19 |
| 2012 | 1015 | 460 | 22 | 1015 | 0 |
| 2013 | 1295 | 393 | 24 | 1293 | 2 |
| 2014 | 1665 | 566 | 36 | 1645 | 20 |
| 2015 | 2775 | 392 | 60 | 2775 | 0 |
| 2016 | 2590 | 393 | 56 | 2566 | 24 |
| 2017 | 1850 | 553 | 40 | 1850 | 0 |
| 2018 | 1850 | 383 | 40 | 1836 | 14 |
| 2019 | 1945 | 373 | 42 | 1907 | 38 |
| 2020 | 4415 | 582 | 92 | 4373 | 42 |
| 2021 | 5365 | 400 | 116 | 5299 | 66 |
| 2022 | 5365 | 381 | 116 | 5273 | 92 |
| 2023 | 5550 | 381 | 120 | 5526 | 24 |
| 2024 | 5550 | 381 | 120 | 5520 | 30 |
| 2025 | 6105 | 565 | 132 | 6030 | 75 |

Itens únicos por área e ano: ~90-150 (CH/CN), ~90-153 (LC, inclui inglês/espanhol), ~90-147 (MT); os anos com 2 aplicações
(2012, 2014, 2017, 2020, 2025) têm mais itens únicos. A/B/C ausentes: 96 itens únicos (abandonados/anulados, ~1,3%).
Itens anulados (TX_GABARITO = X): 15 itens únicos.

## Parâmetro B por área (itens únicos por ano+CO_ITEM, 2009-2025)
| Área | n | mín | mediana | máx |
|---|---|---|---|---|
| CH | 1698 | -2,11 | 0,98 | 11,14 |
| CN | 1792 | -1,80 | 1,30 | 61,05 |
| LC | 1930 | -2,60 | 0,68 | 8,28 |
| MT | 1787 | -1,26 | 1,85 | 17,62 |

Mediana de A ~2,0-2,2 e de C ~0,16-0,18 em todas as áreas. Medianas de B por ano/área variam pouco (CN 1,1-1,6; MT 1,5-2,2).
Escala do B: a escala TRI do ENEM (média 500, dp 100 na população de referência), então B está em unidades de desvio padrão;
MT é a área mais difícil em mediana, LC a mais fácil. Máximos absurdos (CN 61,05; MT 17,6) são itens mal calibrados ou
outliers, tratar com winsorização/mediana, não média.

## Ligação ao corpus (`core/corpus_analise.db`, tabela `questoes_corpus`)
Achado principal: **`indice` do corpus = `CO_POSICAO` do caderno AZUL** (1-180), e o gabarito bate. Método: para cada
ano/área, comparei o gabarito do corpus (idioma='') com TX_GABARITO por CO_POSICAO em cada CO_PROVA e escolhi a melhor;
só liguei itens em que o gabarito da questão concorda individualmente e o ano/área tem >=90% de concordância.

- Resultado: **2476 questões ligadas** a (ano, indice) com CO_ITEM e A/B/C (2437 com B; 39 sem B/abandonadas), em
  `core/inep_itens/itens_ligados_ao_corpus.csv` (colunas ano, indice, area, co_item, co_prova, cor, gabarito, co_habilidade, a, b, c, aban).
- Cobertura ~99-100% das questões do corpus em 2009-2015, 2018-2025 (2021: 95%). 2024 e 2025 só têm CN e MT no corpus
  (~88 questões, cadernos amarela/azul) e foram ligadas 100%.
- **Não ligadas com confiança**: 2016 CN/CH/LC (concordância 24-33%) e 2017 inteiro (~30%): o corpus (enem.dev) usa numeração
  de outro caderno que não o azul do INEP (em 2016 e 2017 as cores/numeração diferem); MT 2016 ligou 45/45. Seria preciso testar
  outros CO_PROVA/cadernos (o melhor caderno ficou com ~30%, que é chance) ou ligar por texto/conteúdo, que não foi feito.
- Ressalvas: (a) 2021 e 2022 têm 4 provas AZUL por área (aplicações regular/reaplicação) com posições e gabarito iguais;
  a ligação ficou empatada e escolhi a primeira, os CO_ITEM/parâmetros podem diferir entre aplicações (não verifiquei);
  (b) gabarito coincidir em 1 letra tem 20% de chance, então pequenas divergências (1-4 por área, ex.: LC 2010 39/40, MT 2021 41/45)
  sugerem anulação/troca de gabarito ou diferença de fonte, não erro de posição; as poucas divergentes foram excluídas
  do CSV ligado; (c) a linha do LC tem itens de inglês/espanhol; o corpus só tem idioma='' (inglês?) e 61 linhas 'espanhol',
  não liguei o espanhol; (d) o banco do app (`enem.db`, ids `ano_caderno_numero`) tem outros cadernos: a numeração de cores
  diferentes exige buscar o CO_PROVA da cor correspondente (TX_COR está no arquivo, ligar por CO_ITEM entre cores é possível
  porque o mesmo CO_ITEM aparece em várias CO_PROVA com posições diferentes).

## Limitações
- Não há coluna de matéria/assunto; só CO_HABILIDADE. Tópico continua vindo da classificação do projeto.
- B contém outliers extremos; alguns itens sem A/B/C (abandonados).
- Parâmetros vêm da calibração oficial do INEP por prova/ano; comparar B entre anos é aproximado (mesma escala, mas calibrações separadas).
- Ligação de 2016/2017 pendente; 2021/2022 ambíguo entre aplicações; 2024/2025 só CN+MT no corpus.
- Não usei os Microdados de participantes (respostas), portanto não há taxa de acerto empírica por item, só os parâmetros.

## Próximos passos sugeridos
1. Usar `itens_ligados_ao_corpus.csv` (join por ano+indice) para calcular dificuldade média por tópico do corpus.
2. Ligar 2016/2017 testando outros cadernos ou por conteúdo; resolver empates 2021/2022.
3. Se quiser nota real do ENEM por acerto por item, os microdados de participantes teriam que ser lidos (arquivos grandes, GB).
