# Padrões das redações nota 1000

## O que o banco diz pro modelo do Gabriel (245 redações únicas, ENEM 2013-2025, fechado em 2026-09-26)

> Atualização 2026-09-27: com o dataset aberto da USP (Hugging Face) o banco passou pra **342 redações únicas (ENEM 2012-2025)**, 63 delas notas 1000 publicadas pelo g1/O Globo. Repertórios mais citados agora: Constituição 73, Dimenstein 19, Simone de Beauvoir 17, Bauman 15, Kant 13, Milton Santos 12. As conclusões abaixo se mantêm.

1. **A estrutura dele é padrão de nota 1000**: há notas 1000 que abrem com a CF/88 quase palavra por palavra como ele (Evely Lima 2021, Nicole C. Almeida 2022, Lucas Malta 2023, Laryssa Melo 2025).
2. **Abrir com a Constituição funciona, mas é minoria**: 19 de 207 aberturas; livro (49), filme (24), pensador (24) e fato/contexto histórico (40) são mais comuns.
3. **A Constituição é o repertório mais citado no texto** (56 redações); depois Dimenstein (17), Simone de Beauvoir (13), Milton Santos (12), Kant (11), Bauman (10).
4. **Causa do Estado genérica é aceita**: 65 de 207 introduções têm causa estatal; 138 têm causa social/cultural; 38 têm as duas (o par dele). Manter "omissão do Poder Público".
5. **A causa social precisa ter a cara do tema** (etarismo, patriarcalismo, epistemicídio, estigma), não "inércia do corpo social".
6. **Mbembe e Chomsky são moda de 2025** (Mbembe em 4 redações, todas de 2025; Chomsky em 1): funcionam, mas o corretor vai ver muito — o fato concreto do tema logo depois é o que diferencia.
7. **Do 960/980 pro 1000 costuma ser a C1**: as duas 980 do IFMG tiraram 180 só em gramática; o aluno 880→1000 de 2025 também subiu atacando a C1.
8. **Proposta com 2 agentes/2 ações** (uma por causa) é o padrão das notas 1000 com esqueleto mapeado.

Números por heurística automática (tipo de abertura e causas por palavra-chave, 207 de 245 com introdução ou esqueleto): servem pra tendência, não são exatos.

---

## Atualização (2026-09-26, noite): banco com 220 redações únicas

Loop de coleta: iteração 1 +28 do ENEM 2018 (Redação a Mil 1.0 reconstruída); iteração 2 +9 do ENEM 2025 (coRedação e Quero Bolsa, só esqueleto; ATENÇÃO: o INEP informou 10 notas mil em 2025 e os portais somam 15 nomes, então parte pode não ser 1000); iteração 3: +3 do e-book do IFMG (duas 980 e uma 1000, só metadado e nota por competência) e +5 relatos de 980. Achado: **as duas 980 do IFMG perderam os 20 pontos só na C1 (gramática)** e fizeram 200 nas outras — o mesmo padrão do aluno 880→1000 de 2025. Iteração 4: +11 esqueletos do Imaginie (243 únicas). Iteração 5: Estratégia (19 exemplos) quase tudo repetido: +2 novas (245 únicas; "Clara de Oliveira" 2024 provavelmente é a Clara da Barra de Oliveira já no banco) e o esqueleto (causas, repertórios, proposta) preenchido em 7 redações que só tinham texto, abrindo 2013-2017 (Lei Seca, publicidade infantil, violência contra a mulher, intolerância religiosa, surdos). Por ano (únicas): 2018: 35 · 2019: 37 · 2020: 23 · 2021: 22 · 2022: 26 · 2023: 52 · 2024: 19 · 2025: 6.

Fontes agora: cartilhas do INEP (41, oficial, com comentário), **Cartilha Redação a Mil** (Lucas Felpi/Poliedro, 161, cada uma com o **espelho oficial** da nota, ENEM 2019-2024) e portais (16, só esqueleto). 26 repetidas entre fontes foram marcadas (`duplicada_de`). Por ano (únicas): 2018: 7 · 2019: 37 · 2020: 23 · 2021: 22 · 2022: 26 · 2023: 52 · 2024: 19 · 2025: 6. Faltam: Redação a Mil 1.0 (ENEM 2018, 31 redações; o PDF tem texto quebrado) e 8.0 (ENEM 2025, link não encontrado).

Números em 183 redações com texto completo (158 com a introdução isolada automaticamente — heurística de fim de parágrafo, pode errar):

| Padrão | Quantas |
|---|---|
| Cita a Constituição em algum ponto do texto | **61 de 202** (≈30%) |
| **Abre** com a Constituição | 14 de 158 intros |
| Cita Dimenstein | 16 (10 com "O Cidadão de Papel") |
| Cita Bauman | 8 |
| Outros repertórios frequentes | Milton Santos 13, Hannah Arendt 8, Kant 8, Durkheim 7, Djamila Ribeiro 7, Paulo Freire 6, Aristóteles 6, Sérgio Buarque 6 |
| Fim da intro com causa **social/cultural** | 112 de 158 |
| Fim da intro com causa **do Estado** | 44 de 158 (30 têm as duas) |

**Aberturas quase idênticas à dele** (CF/88 + "norma de maior hierarquia" ou art. 1º/dignidade): Evely Lima (2021), Nicole Carvalho Almeida (2022), Lucas Malta de Carvalho (2023), Helena Moreira Alves (2023), Alice Souza Moreira (2021), Francisco Roney (2023), Maria Eduarda Graciano (2022), Ana Carolina Riechel Famoso (2023).

Nota de método: Mbembe e Chomsky não aparecem nos textos completos (2019-2024); só nas notas 1000 de 2025 vistas pelo portal. Parece repertório "da moda" recente.

---

## Primeira análise (50 redações)

Banco local (fora do git, texto de terceiros): `docs/redacao_pesquisa/banco_1000/redacoes_1000.db`, tabela `redacoes`.
- **34 redações das cartilhas do INEP** (texto completo + comentário oficial): ENEM 2018 (7), 2021 (7), 2023 (10), 2024 (10). A cartilha com as de 2022 (povos tradicionais) tem a fonte do PDF embaralhada e ficou de fora.
- **16 redações de portal** (só o esqueleto: abertura, 2 causas, repertórios de D1/D2, proposta, com link): ENEM 2023 (10) e 2025 (6), resumidas do Estratégia Vestibulares.

Aqui só os padrões; os textos ficam no banco local.

## 1. Como abrem (50 redações)

| Tipo de abertura | Quantas |
|---|---|
| Livro | 12 |
| Filósofo / pensador | 7 |
| Contextualização histórica | 7 |
| **Constituição / lei** | **6** |
| Música | 4 |
| Filme | 4 |
| Fato histórico | 4 |
| Série | 2 |
| Poema, dado, conceito do tema, arte | 1 cada |

**Leitura:** abrir com a Constituição funciona (6 notas 1000: Alice 2021; Lucas Malta, Helena, Francisco, Indira 2023; Laryssa 2025), mas é minoria. Cultura (livro, música, filme, série, arte, poema) soma **24 de 50**.

## 2. As 2 causas (16 redações de portal com as causas mapeadas)

- **12 de 16 têm uma causa do Estado**, quase sempre com nome genérico: "negligência estatal" (5), "negligência/omissão governamental" (4), "escassez de fiscalização estatal", "inobservância governamental", "falta de apoio governamental", "legislação inadequada".
- A outra causa é **social/cultural e do tema**: patriarcalismo, convenções de gênero, preconceito/etarismo, desvalorização da figura feminina, mídia estereotipando a velhice, omissão midiática, ausência de valorização social.
- Exemplo muito próximo do molde do Gabriel: **Letícia Fernandes (2023)**: "omissão governamental" + "ausência de valorização social".

**Correção do que eu tinha dito antes:** a causa do Estado com nome genérico ("omissão do Poder Público") **não é o problema** — aparece em 12 de 16 notas 1000. O que precisa ter cara do tema é a **causa social** e, principalmente, **o conteúdo do desenvolvimento** (o fato concreto: CREAS/UBS, falta de geriatras, Lei Orçamentária, Lei dos Sexagenários).

## 3. Os repertórios dele aparecem em nota 1000

| Repertório | Onde apareceu com nota 1000 |
|---|---|
| Constituição Federal de 1988 | 6 aberturas (acima) + D2 de Rafaela Muller (art. 3º) e Francisco (art. 23) |
| Dimenstein, "O Cidadão de Papel" | D2 de Francisco Roney Sousa Suriano (2023); "letargia institucional" em Millena Bacelar (2023) |
| Mbembe, Necropolítica | D1 de Lucas Rodrigues e de Carlos Eduardo Gomes dos Santos (2025) |
| Chomsky, "A fabricação do consentimento" | D2 de Carlos Eduardo Gomes dos Santos (2025) |
| Bauman, "instituição zumbi" | D2 de Arthur Sanches Sales (2023) — mas é o mesmo conceito que a cartilha 2025 critica como "repertório de bolso" em outra redação: o que separa uma da outra é a explicação e a ligação com o tema |

**Caso-chave: Carlos Eduardo Gomes dos Santos (ENEM 2025, envelhecimento)** usou praticamente o **Modelo Crítico** do Gabriel: causas "negligência estatal em saúde" + "omissão midiática"; D1 = Necropolítica + dado concreto do tema (falta de atividades em CREAS, campanhas em UBS); D2 = Chomsky; proposta com 2 agentes (Ministério da Saúde e mídia). O molde chega em 1000 quando **cada repertório vem com o fato concreto do tema** e a proposta tem **uma ação por causa**.

## 4. Proposta

A maioria das 16 tem **2 agentes ou 2 ações** (ex.: "Ministério da Saúde + mídia", "Governo + escolas", "emissoras + famílias"), uma por causa.

## 5. O que muda no treino dele

1. **Manter** a introdução fixa com a CF/88 e a causa do Estado ("omissão do Poder Público" pode ficar).
2. **Trocar "inércia do corpo social"** pela causa social **do tema** (preconceito/estereótipo/desvalorização/omissão midiática sobre o grupo).
3. **No D1 e no D2, o fato concreto do tema** logo depois do repertório (é o que as notas 1000 com Mbembe e Chomsky têm e a redação 2 dele não tinha).
4. **Proposta com 2 ações**, uma por causa.

## Fontes

- Cartilhas do INEP 2019, 2022, 2024, 2025 (arquivos locais em `cartilhas/`).
- Estratégia Vestibulares, notas 1000 ENEM 2025: https://vestibulares.estrategia.com/portal/noticias/redacao-nota-1000-leia-redacoes-do-enem-2025/
- Estratégia Vestibulares, notas 1000 ENEM 2023: https://vestibulares.estrategia.com/portal/materias/redacao/redacao-nota-1000-leia-10-redacoes-do-enem-2023/

---

## Microdados do ENEM 2025: nota de redação por competência de TODOS os participantes

Fonte: `RESULTADOS_2025.csv` dos microdados do INEP, lido em fluxo do ZIP oficial por `core/inep_itens/redacao_microdados.py` (nada do arquivo fica no disco; só o resumo `core/inep_itens/redacao_2025.json`). 4.810.772 linhas; 3.457.555 com nota de redação.

| Nota | Quantas pessoas | Percentual (de quem tem nota) |
|---|---|---|
| 1000 | 10 | 0,0003% |
| ≥ 980 | 850 | 0,02% |
| ≥ 960 | 16.226 | 0,47% |
| ≥ 940 | 55.047 | 1,6% |
| ≥ 920 | 115.085 | 3,3% |
| ≥ 900 | 173.543 | 5,0% |
| ≥ 880 | 250.370 | 7,2% |
| exatamente 880 | 76.827 | a nota mais frequente da faixa alta |

**Média de cada competência e % que NÃO tirou 200, por faixa de nota:**

| Faixa | n | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|
| 860-880 | 137.887 | 157 (100% sem 200) | 181 (69%) | 163 (98%) | 182 (70%) | 189 (41%) |
| 900-940 | 157.317 | 161 (100%) | 192 (35%) | 176 (86%) | 193 (31%) | 195 (20%) |
| 960-980 | 16.216 | 167 (96%) | 199 (5%) | 196 (18%) | 199 (3%) | 199 (3%) |
| 1000 | 10 | 200 | 200 | 200 | 200 | 200 |

**O que isso diz:**
1. **Em 2025, a C1 (gramática/norma culta) foi o gargalo de todo mundo da faixa alta**: praticamente ninguém de 860 a 940 tirou 200 em C1, e 96% dos 960-980 também não. É o que separa 980 de 1000 — confirma, com 16 mil redações, o que as duas 980 do IFMG e o aluno 880→1000 mostravam.
2. **De 880 pra 900-940, o ganho vem de C3 e C2** (projeto de texto/argumentação e repertório): C3 sobe de 163 pra 176 e C2 de 181 pra 192. **De 940 pra 960+, C3 quase fecha** (196).
3. **880 é a nota mais comum da faixa alta** (76.827 pessoas). Sair dela exige mexer em C3/C2 primeiro e C1 por último.

---

## Redações 900-980 (loop de coleta)

- Iteração 1: +21 (Cartilha do 900+ da Profª Luma — 17 do ENEM 2021, 900-980, só nome e nota; 4 alunos 980 do ENEM 2024 por secretarias e imprensa).
- Iteração 2: +2 do ENEM 2015 (980 e 960, Colégio Bandeirantes; texto publicado no Blog do Enem, não extraído) e +4 relatos. Total 900-980 no banco: 25, quase todos sem texto — as fontes de 900+ publicam a notícia, raramente a redação.
- Common Crawl (2026-09-27): 197 URLs candidatas em 28 domínios; +6 notas 1000 de 2014-2016 (coRedação). Banco: **274 redações únicas** (inclui as 25 de 900-980).
