# Padrões de prova com o corpus de 2009 a 2025

Estende `docs/padroes_de_prova.md` (7 provas de Matemática e Ciências da Natureza, 2019 a 2025, salvas em `core/enem.db`) usando `core/corpus_analise.db` (tabela `questoes_corpus`: 2.865 questões, 2009 a 2025). Complementa `docs/pesquisa_estrategia_de_prova.md` (o que a ciência diz sobre estudar) e não repete o que aquele documento já diz. Toda contagem abaixo saiu de consultas rodadas nesta análise (somente leitura, sem alterar nenhum banco); nada foi estimado de cabeça. O que é indício fica marcado como indício.

**Leia primeiro:** os números de Natureza e Matemática dependem de um dicionário de palavras-chave que eu escrevi (seção 2.1). Ele concorda com os rótulos do `enem.db` em ~56% (tema exato, Natureza), ~82% (só a disciplina Física/Química/Biologia) e ~46% (tema exato, Matemática). Trate as tabelas como mapa grosso, não como classificação oficial.

## 0. Base, verificações e ressalvas de método

### 0.1 Como a "área" foi definida (e uma correção à premissa)

A área vem do `indice`, não da coluna `disciplina`. Conferi contra a `disciplina` majoritária em cada bloco de 45 índices, por ano, e o layout **não é o mesmo em todos os anos**:

| Anos | 1-45 | 46-90 | 91-135 | 136-180 | Como verifiquei |
|---|---|---|---|---|---|
| 2009 | Natureza | Humanas | Linguagens | Matemática | `disciplina` majoritária por bloco + leitura de 2009 nº 1, 10, 46, 60, 91, 140 |
| 2010 a 2016 | Humanas | Natureza | Linguagens | Matemática | idem (ex.: 2012 nº 50 é o carrinho de brinquedo, Natureza; 2012 nº 100 é interpretação de texto, Linguagens) |
| 2017 a 2023 | Linguagens | Humanas | Natureza | Matemática | idem (igual à premissa do pedido) |
| 2024 e 2025 | (ausente) | (ausente) | Natureza | Matemática | só há índices 91 a 180 |

Ou seja: usar "1-45 = Linguagens" para 2009 a 2016 misturaria Humanas (ou, em 2009, Natureza) com Linguagens. A `disciplina` também erra em algumas linhas (ex.: 2012 nº 140 vem como `ciencias-humanas` mas é Matemática; em 2010 boa parte do bloco 91-135 está como `ciencias-humanas` mas é Linguagens). Por isso a `disciplina` não foi usada em nenhuma análise. Com o mapeamento por ano acima: Linguagens 673, Humanas 674, Natureza 759, Matemática 759 (total 2.865, batendo com a tabela).

### 0.2 Outras verificações que mudaram o método

1. **Marca d'água e alternativas em 2024 e 2025.** Nesses dois anos (fonte `enem.db_local`) o texto vem com lixo de PDF (`ENEM2024ENEM2024...`, rodapé "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS • 2º DIA • CADERNO ...", caracteres de controle) e as **alternativas estão dentro do `enunciado`** (`a<tab>...b<tab>...`), com `alternativas_json` vazio em 15 questões de 2024 e 32 de 2025. Removi a marca d'água antes de qualquer contagem de termos. Nesses anos o `tem_imagem` é sempre 0, então **não há sinal de imagem** (tratei como "n/d" e usei, como substituto, "o texto cita figura/gráfico/tabela").
2. **2023 no corpus não é a mesma ordem do `enem.db`.** O `enem.db` usa o caderno cinza de 2023; o corpus (enem.dev) tem outra ordem. Casei as questões por sobreposição de vocabulário (≥ 60%): das 619 questões de Natureza e Matemática de 2019 a 2025 no corpus, **609 casaram** com uma questão do `enem.db` (uma-para-uma, sem duplicata); as 10 que não casaram são de 2020, 2021, 2022 e 2023 (quase todas sem texto por causa de imagem). Todos os `(ano, índice)` citados neste documento são **do corpus**; para 2023 eles não coincidem com os ids `2023_cinza_N` do documento anterior.
3. **Itens ausentes do corpus (15):** 2009 nº 101; 2015 nº 145; 2018 nº 62; 2019 nº 98, 100, 128; 2020 nº 144, 168, 179; 2023 nº 34, 174; 2024 nº 102; 2025 nº 123, 132, 174. (Esperado: 2.880 = 15 × 180 + 2 × 90.)
4. **Uma prova por ano, sem PPL, sem 2008 ou antes.** 61 questões de língua estrangeira existem, só em versão espanhol (2010 e 2012 a 2023; 2009 e 2011 não têm). Como em 2009 o exame mudou de matriz (registrado em `pesquisa_estrategia_de_prova.md`), a comparabilidade com 2010 em diante já é uma ressalva.

## 1. Cobertura, texto utilizável e dependência de imagem

### 1.1 Questões por área e ano

| Ano | Linguagens | Humanas | Natureza | Matemática | Total | Língua estrangeira (idioma preenchido) |
|---|---|---|---|---|---|---|
| 2009 | 44 | 45 | 45 | 45 | 179 | 0 |
| 2010 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2011 | 45 | 45 | 45 | 45 | 180 | 0 |
| 2012 | 45 | 45 | 45 | 45 | 180 | 4 |
| 2013 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2014 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2015 | 45 | 45 | 45 | 44 | 179 | 4 |
| 2016 | 45 | 45 | 45 | 45 | 180 | 4 |
| 2017 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2018 | 45 | 44 | 45 | 45 | 179 | 5 |
| 2019 | 45 | 45 | 42 | 45 | 177 | 5 |
| 2020 | 45 | 45 | 45 | 42 | 177 | 4 |
| 2021 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2022 | 45 | 45 | 45 | 45 | 180 | 5 |
| 2023 | 44 | 45 | 45 | 44 | 178 | 5 |
| 2024 | - | - | 44 | 45 | 89 | 0 |
| 2025 | - | - | 43 | 44 | 87 | 0 |
| **Total** | 673 | 674 | 759 | 759 | 2865 | 61 |

### 1.2 Fração afetada por imagem ou por texto curto (Natureza e Matemática)

Colunas: **n** = questões no corpus; **img** = % com `tem_imagem = 1` ou com imagem em alguma alternativa (só 2009 a 2023); **<120c** = % com menos de 120 caracteres de texto útil (contexto + enunciado, sem URL e sem marcação de imagem), ou seja, o essencial provavelmente está na figura; **cita fig** = % cujo texto menciona figura, gráfico, tabela, quadro, esquema, imagem, mapa, charge etc. (única medida disponível nos 4 anos sem flag, mas subconta figura sem menção).

| Ano | nat: n | img | <120c | cita fig | mat: n | img | <120c | cita fig |
|---|---|---|---|---|---|---|---|---|
| 2009 | 45 | 49% | 4% | 22% | 45 | 53% | 0% | 49% |
| 2010 | 45 | 36% | 4% | 18% | 45 | 76% | 11% | 33% |
| 2011 | 45 | 47% | 16% | 16% | 45 | 60% | 20% | 16% |
| 2012 | 45 | 38% | 13% | 20% | 45 | 62% | 27% | 29% |
| 2013 | 45 | 44% | 22% | 18% | 45 | 71% | 38% | 13% |
| 2014 | 45 | 49% | 27% | 22% | 45 | 62% | 49% | 18% |
| 2015 | 45 | 40% | 27% | 7% | 44 | 59% | 41% | 9% |
| 2016 | 45 | 49% | 40% | 22% | 45 | 69% | 36% | 9% |
| 2017 | 45 | 51% | 0% | 33% | 45 | 76% | 18% | 42% |
| 2018 | 45 | 56% | 0% | 31% | 45 | 67% | 0% | 47% |
| 2019 | 42 | 48% | 0% | 38% | 45 | 56% | 0% | 47% |
| 2020 | 45 | 44% | 2% | 29% | 42 | 81% | 0% | 64% |
| 2021 | 45 | 58% | 0% | 42% | 45 | 71% | 0% | 51% |
| 2022 | 45 | 56% | 0% | 33% | 45 | 62% | 0% | 42% |
| 2023 | 45 | 40% | 0% | 27% | 44 | 68% | 2% | 48% |
| 2024 | 44 | n/d | 0% | 45% | 45 | n/d | 0% | 53% |
| 2025 | 43 | n/d | 0% | 42% | 44 | n/d | 0% | 45% |

Leitura:

- **2009 a 2016 têm muito mais questão "cega"**: em 2014, 49% das questões de Matemática e 27% das de Natureza têm menos de 120 caracteres; em 2016, 36% e 40%. De 2017 em diante isso cai para 0 a 3% (só 2017 fica em 18% em Matemática). Média do período: Natureza 19% (2009-2016) contra 0% (2017-2023); Matemática 28% contra 3%. **Isso reduz o poder de qualquer análise de texto em 2013 a 2016** e é a razão dos números "indefinido" da seção 2.
- **Dependência de imagem é alta o tempo todo**: 44% a 50% das questões de Natureza e 64% a 68% das de Matemática têm imagem (flag). Não dá para separar imagem essencial de imagem decorativa; em 58 questões de Natureza e 73 de Matemática (2009 a 2023) há imagem **e** texto curto, o caso mais provável de "essencial na figura".
- **O texto passa a citar figura/gráfico/tabela cada vez mais**: 18% (2009-2016) → 33% (2017-2023) → 44% (2024-2025) em Natureza; 22% → 49% → 49% em Matemática. Parte disso é que 2009-2016 tem menos texto capturado, então a comparação é otimista para a tendência; mas o nível de 2017 em diante (42% a 64% em Matemática) é medido em anos com texto completo.

### 1.3 Linguagens e Humanas (2009 a 2023, sem 2024-2025)

| Ano | lin: n | img | <120c | cita fig | hum: n | img | <120c | cita fig |
|---|---|---|---|---|---|---|---|---|
| 2009 | 44 | 30% | 14% | 20% | 45 | 18% | 2% | 13% |
| 2010 | 45 | 27% | 0% | 7% | 45 | 11% | 0% | 9% |
| 2011 | 45 | 33% | 0% | 16% | 45 | 20% | 0% | 13% |
| 2012 | 45 | 31% | 0% | 16% | 45 | 20% | 4% | 16% |
| 2013 | 45 | 31% | 7% | 20% | 45 | 22% | 9% | 24% |
| 2014 | 45 | 20% | 0% | 9% | 45 | 27% | 11% | 16% |
| 2015 | 45 | 18% | 0% | 7% | 45 | 16% | 7% | 18% |
| 2016 | 45 | 16% | 0% | 11% | 45 | 27% | 9% | 11% |
| 2017 | 45 | 22% | 2% | 18% | 45 | 16% | 9% | 16% |
| 2018 | 45 | 29% | 0% | 22% | 44 | 18% | 7% | 9% |
| 2019 | 45 | 20% | 4% | 13% | 45 | 11% | 0% | 9% |
| 2020 | 45 | 22% | 2% | 13% | 45 | 9% | 0% | 9% |
| 2021 | 45 | 24% | 2% | 13% | 45 | 4% | 2% | 9% |
| 2022 | 45 | 22% | 4% | 11% | 45 | 18% | 2% | 16% |
| 2023 | 44 | 5% | 5% | 5% | 45 | 9% | 2% | 11% |
| 2024 | - | - | - | - | - | - | - | - |
| 2025 | - | - | - | - | - | - | - | - |

Linguagens: 26% das questões têm imagem em 2009-2016 e 21% em 2017-2023; Humanas: 20% e 12%. Texto curto é raro (3% a 5%). Ou seja, **Linguagens e Humanas são quase totalmente analisáveis por texto** (o que falta é a imagem das charges, mapas e quadros, que não consigo ler).

## 2. Ciências da Natureza e Matemática, 2009 a 2025

### 2.1 Método do agrupamento por tema

- **Texto usado:** contexto + enunciado + alternativas (em 2024 e 2025 as alternativas já estão no enunciado), minúsculas e sem acento.
- **Dicionário próprio, documentado abaixo:** cada tema tem listas de expressões regulares com pesos (2,5 a 4 para o termo característico; 0,6 a 1,5 para palavras de contexto). A pontuação do tema é a soma de peso × ocorrências (limitado a 3 por expressão); vence o tema de maior pontuação (empate: ordem de declaração); pontuação 0 = "indefinido". **Cada questão entra em um único tema**, então nunca conta duas vezes.
- **Natureza (19 temas, agrupados em Física / Química / Biologia):** F eletricidade e magnetismo (corrente, resistor, tensão, circuito, campo magnético, indução, carga, kWh, lâmpada, chuveiro); F óptica (lente, espelho, refração, reflexão, luz, prisma); F ondas e acústica (onda, frequência, som, ressonância, Doppler, interferência); F termologia (calor, temperatura, calor específico, dilatação, condução); F mecânica (velocidade, aceleração, força, atrito, energia cinética/potencial, trabalho, empuxo, pressão, gravidade, órbita, densidade); F radiação e física moderna (radioativo, meia-vida, isótopo, nuclear, raio X, fóton); Q soluções e concentração (concentração, soluto, diluição, mol/L, ppm, solubilidade); Q estequiometria e química geral (massa molar, mol, rendimento, equação química); Q equilíbrio, ácido-base e cinética (equilíbrio químico, pH, ácido, base, neutralização, catalisador, energia de ativação); Q eletroquímica (pilha, eletrólise, eletrodo, ânodo, cátodo, oxidação, redução, corrosão); Q orgânica e polímeros (hidrocarboneto, álcool, éster, polímero, plástico, petróleo, biodiesel, tensoativo); Q ligações, materiais e separação (ligação iônica/covalente, polaridade, ponto de ebulição, metal, íon, destilação, filtração, decantação); Q termoquímica (entalpia, exotérmica, poder calorífico); B ecologia e meio ambiente (ecossistema, cadeia alimentar, poluente, efeito estufa, bioacumulação, eutrofização, agrotóxico, esgoto, desmatamento, bioma); B genética e biotecnologia (gene, DNA, alelo, cromossomo, mutação, transgênico, PCR, cruzamento, proteína); B citologia e metabolismo celular (célula, membrana, mitocôndria, ATP, respiração celular, fotossíntese, enzima, osmose, mitose); B saúde, doenças e microrganismos (vírus, bactéria, vacina, parasita, dengue, antibiótico, epidemia, saneamento); B fisiologia humana e animal (sangue, hormônio, coração, neurônio, músculo, insulina, digestão, gestação, visão); B evolução, botânica e zoologia (evolução, seleção natural, fóssil, planta, semente, raiz, inseto, vertebrado).
- **Matemática (13 temas):** geometria plana (triângulo, círculo, ângulo, perímetro, área, Pitágoras); geometria espacial (volume, cilindro, cone, esfera, prisma, pirâmide, cubo, paralelepípedo; capacidade/litros com peso baixo); estatística (média, mediana, moda, desvio padrão, amostra; tabela/gráfico com peso baixo); probabilidade (probabilidade, chance, sorteio, aleatório, espaço amostral); funções (função, f(x), parábola, exponencial, logaritmo, coeficiente angular, valor máximo/mínimo); razão, proporção e escala (proporcional, razão, regra de três, escala, velocidade média, mapa, fração); porcentagem e matemática financeira (%, juros, desconto, lucro, parcela, montante; preço/custo/reais com peso baixo); análise combinatória (de quantas maneiras, anagrama, permutação, arranjo, fatorial); sequências e progressões (PA, PG, termo geral); trigonometria (seno, cosseno, tangente, radianos); geometria analítica (plano cartesiano, coordenadas, equação da reta); sistemas, equações e álgebra (sistema linear, equação, matriz, determinante, MDC/MMC, raiz quadrada); raciocínio lógico e contagem simples (lógica, calendário, relógio, tabuleiro, baralho).
- **Limitação estrutural:** o dicionário só enxerga o que está escrito. Trigonometria, por exemplo, aparece por palavra-chave em só 4 dos 17 anos, enquanto o `enem.db` rotula 9 questões de trigonometria só em 2019-2025 (quase nenhum enunciado cita "seno/cosseno"). Onde o conceito só aparece na figura, o dicionário subconta.

### 2.2 Concordância do agrupamento com os rótulos do `enem.db` (2019 a 2025)

Universo comparável: as 609 questões casadas (seção 0.2). Para comparar **tema**, usei só as 470 que têm um rótulo `materia` específico e mapeável (221 de Natureza e 249 de Matemática); rótulos genéricos (`quimica`, `fisica`, `biologia` = 41 questões classificadas, `sem_video_pendente`, `matematica_basica` = 30, `interpretacao_de_grafico` = 18, `sem_classificar`) ficaram fora da comparação por tema. Os rótulos do `enem.db` **não são verdade absoluta** (às vezes marcam a habilidade principal e o dicionário marca o contexto; ex.: uma questão de volume que usa proporção).

| Medida | Resultado |
|---|---|
| Natureza, tema exato (19 temas; 18 têm rótulo comparável) | 123 de 221 = **56%** |
| Natureza, só a disciplina (Física / Química / Biologia) | 181 de 221 = **82%** |
| Natureza, disciplina nos rótulos genéricos (2019) | 33 de 41 = 80% |
| Matemática, tema exato (13 temas) | 114 de 249 = **46%** (versão inicial do dicionário, antes de ajustar pesos: 99 de 249 = 40%) |
| Matemática, 4 grupos grossos (geometria; dados e contagem; funções e sequências; proporcionalidade e aritmética) | 161 de 249 = **65%** |
| 2019-2022 versus 2023-2025 (Natureza, tema exato) | 57% (75/132) versus 54% (48/89) |
| 2019-2022 versus 2023-2025 (Matemática, tema exato) | 53% (70/132) versus 38% (44/117) |

**Honestidade sobre a incerteza:**

- Ajustei os pesos de Matemática depois de ver a matriz de confusão **agregada** de 2019-2025 (reduzi o peso de palavras de contexto como preço, custo, litros, km); portanto 46% é otimista, e a queda para 38% em 2023-2025 (as 77 questões de 2024 e 2025 sozinhas também dão 38%) é sinal de sobreajuste. Natureza não foi ajustada depois da primeira versão.
- **Por tema (precisão = quando o dicionário diz "X", quantas vezes o rótulo também diz "X"):**

| Tema (rótulos do enem.db agrupados) | Rotulados | Acertos do dicionário (recall) | Atribuídos pelo dicionário | Precisão |
|---|---|---|---|---|
| citologia e metabolismo celular | 7 | 5 (71%) | 11 | 45% |
| ecologia e meio ambiente | 24 | 10 (42%) | 14 | 71% |
| evolucao, botanica e zoologia | 16 | 6 (38%) | 12 | 50% |
| fisiologia humana e animal | 12 | 6 (50%) | 15 | 40% |
| genetica e biotecnologia | 16 | 11 (69%) | 15 | 73% |
| saude, doencas e microrganismos | 11 | 5 (45%) | 10 | 50% |
| eletricidade e magnetismo | 20 | 16 (80%) | 20 | 80% |
| mecanica | 25 | 18 (72%) | 21 | 86% |
| ondas e acustica | 10 | 8 (80%) | 11 | 73% |
| optica | 6 | 3 (50%) | 5 | 60% |
| radiacao e fisica moderna | 6 | 5 (83%) | 6 | 83% |
| termologia | 11 | 8 (73%) | 10 | 80% |
| eletroquimica | 6 | 2 (33%) | 5 | 40% |
| equilibrio, acido-base e cinetica | 9 | 3 (33%) | 13 | 23% |
| estequiometria e quimica geral | 15 | 2 (13%) | 6 | 33% |
| ligacoes, materiais e separacao | 7 | 4 (57%) | 16 | 25% |
| quimica organica e polimeros | 17 | 11 (65%) | 23 | 48% |
| solucoes e concentracao | 3 | 0 (0%) | 8 | 0% |
| analise combinatoria | 12 | 7 (58%) | 14 | 50% |
| estatistica | 21 | 16 (76%) | 31 | 52% |
| funcoes | 25 | 7 (28%) | 13 | 54% |
| geometria analitica | 1 | 0 (0%) | 0 | 0% |
| geometria espacial | 39 | 25 (64%) | 41 | 61% |
| geometria plana | 25 | 17 (68%) | 37 | 46% |
| porcentagem e matematica financeira | 16 | 12 (75%) | 43 | 28% |
| probabilidade | 15 | 9 (60%) | 13 | 69% |
| raciocinio logico e contagem simples | 17 | 0 (0%) | 5 | 0% |
| razao, proporcao e escala | 44 | 18 (41%) | 27 | 67% |
| sequencias e progressoes | 6 | 1 (17%) | 2 | 50% |
| sistemas, equacoes e algebra | 19 | 1 (5%) | 5 | 20% |
| trigonometria | 9 | 1 (11%) | 4 | 25% |

- **Confiáveis (precisão ≥ 70% e recall ≥ 60%):** eletricidade/magnetismo, mecânica, ondas/acústica, termologia, radiação, genética/biotecnologia. **Razoáveis (entre 50% e 76% nas duas medidas):** estatística, geometria espacial, geometria plana, probabilidade. **Frágeis (precisão < 50% ou recall < 35%):** soluções, estequiometria, equilíbrio/ácido-base, ligações/separação, eletroquímica, funções, sistemas/álgebra, trigonometria, raciocínio lógico, sequências, fisiologia, citologia. **Porcentagem/financeira é superatribuída** (43 atribuições para 16 rótulos, precisão 28%) porque palavras como preço e reais aparecem em muita questão que o rótulo trata como razão, funções ou estatística.
- Mesmo com as ressalvas, o que se pode afirmar com segurança é o nível de disciplina (Natureza) e de grupo grosso (Matemática); as tabelas por tema abaixo mostram os temas fracos com a nota "frágil" na leitura.

### 2.3 Ciências da Natureza (759 questões; 11 "indefinido")

**Recorrência por tema** (Anos = em quantos dos 17 anos o tema aparece pelo menos uma vez; 09-14 / 15-19 / 20-25 = média de questões por ano em cada período; `%` = fatia entre as questões classificadas do período; `z` = diferença de proporção de 2020-2025 contra 2009-2019, apenas como sinal de tendência, sem correção para múltiplas comparações; com ~19 temas, 1 ou 2 valores com |z| > 2 saem por acaso).

| Tema | Anos (de 17) | Total | Média/ano | 09-14 | 15-19 | 20-25 | % dos classif. 09-14 / 15-19 / 20-25 | z(20-25 vs 09-19) |
|---|---|---|---|---|---|---|---|---|
| quimica organica e polimeros | 17 | 82 | 4.8 | 5.0 | 5.0 | 4.5 | 11% / 11% / 10% | -0.6 |
| mecanica | 17 | 80 | 4.7 | 5.0 | 5.0 | 4.2 | 11% / 11% / 9% | -0.9 |
| eletricidade e magnetismo | 17 | 70 | 4.1 | 3.8 | 3.8 | 4.7 | 9% / 9% / 10% | +0.8 |
| ligacoes, materiais e separacao | 17 | 59 | 3.5 | 3.3 | 4.0 | 3.2 | 8% / 9% / 7% | -0.6 |
| genetica e biotecnologia | 17 | 57 | 3.4 | 3.2 | 3.8 | 3.2 | 7% / 9% / 7% | -0.4 |
| saude, doencas e microrganismos | 17 | 50 | 2.9 | 4.5 | 2.0 | 2.2 | 10% / 5% / 5% | -1.5 |
| ecologia e meio ambiente | 17 | 49 | 2.9 | 4.0 | 1.6 | 2.8 | 9% / 4% / 6% | -0.2 |
| evolucao, botanica e zoologia | 14 | 39 | 2.3 | 1.5 | 2.8 | 2.7 | 3% / 6% / 6% | +0.7 |
| estequiometria e quimica geral | 16 | 38 | 2.2 | 3.2 | 2.2 | 1.3 | 7% / 5% / 3% | -1.9 |
| ondas e acustica | 16 | 37 | 2.2 | 2.0 | 2.4 | 2.2 | 5% / 6% / 5% | -0.1 |
| fisiologia humana e animal | 16 | 34 | 2.0 | 1.7 | 1.6 | 2.7 | 4% / 4% / 6% | +1.4 |
| equilibrio, acido-base e cinetica | 15 | 33 | 1.9 | 1.3 | 2.0 | 2.5 | 3% / 5% / 6% | +1.2 |
| citologia e metabolismo celular | 15 | 31 | 1.8 | 1.3 | 2.0 | 2.2 | 3% / 5% / 5% | +0.7 |
| termologia | 14 | 27 | 1.6 | 1.2 | 1.6 | 2.0 | 3% / 4% / 4% | +1.0 |
| solucoes e concentracao | 12 | 19 | 1.1 | 0.8 | 1.2 | 1.3 | 2% / 3% / 3% | +0.6 |
| radiacao e fisica moderna | 11 | 14 | 0.8 | 0.5 | 0.6 | 1.3 | 1% / 1% / 3% | +1.7 |
| optica | 9 | 13 | 0.8 | 0.8 | 0.6 | 0.8 | 2% / 1% / 2% | +0.2 |
| eletroquimica | 8 | 13 | 0.8 | 0.7 | 0.8 | 0.8 | 2% / 2% / 2% | +0.2 |
| termoquimica | 3 | 3 | 0.2 | 0.0 | 0.6 | 0.0 | 0% / 1% / 0% | -1.3 |
| indefinido | - | 11 | 0.6 | | | | | |

Matriz por ano (contagens; colunas = anos 2009 a 2025, 2 dígitos):

| Tema | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| quimica organica e polimeros | 7 | 1 | 7 | 5 | 6 | 4 | 3 | 7 | 4 | 6 | 5 | 6 | 7 | 2 | 3 | 6 | 3 |
| mecanica | 3 | 4 | 5 | 7 | 6 | 5 | 7 | 2 | 4 | 6 | 6 | 6 | 3 | 5 | 4 | 3 | 4 |
| eletricidade e magnetismo | 7 | 4 | 2 | 3 | 5 | 2 | 1 | 4 | 5 | 6 | 3 | 4 | 4 | 5 | 3 | 5 | 7 |
| ligacoes, materiais e separacao | 3 | 7 | 3 | 2 | 2 | 3 | 2 | 3 | 5 | 4 | 6 | 4 | 2 | 2 | 4 | 4 | 3 |
| genetica e biotecnologia | 5 | 1 | 3 | 4 | 3 | 3 | 5 | 3 | 4 | 4 | 3 | 2 | 3 | 5 | 3 | 3 | 3 |
| saude, doencas e microrganismos | 4 | 4 | 7 | 5 | 3 | 4 | 4 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 3 |
| ecologia e meio ambiente | 5 | 5 | 5 | 4 | 4 | 1 | 1 | 1 | 4 | 1 | 1 | 4 | 3 | 2 | 1 | 4 | 3 |
| evolucao, botanica e zoologia | 0 | 2 | 2 | 2 | 0 | 3 | 1 | 4 | 2 | 4 | 3 | 1 | 6 | 1 | 4 | 0 | 4 |
| estequiometria e quimica geral | 2 | 6 | 3 | 4 | 2 | 2 | 2 | 3 | 2 | 1 | 3 | 2 | 0 | 1 | 2 | 1 | 2 |
| ondas e acustica | 1 | 1 | 2 | 2 | 3 | 3 | 2 | 5 | 2 | 3 | 0 | 2 | 1 | 1 | 4 | 3 | 2 |
| fisiologia humana e animal | 1 | 1 | 2 | 2 | 3 | 1 | 4 | 1 | 0 | 2 | 1 | 1 | 3 | 3 | 5 | 2 | 2 |
| equilibrio, acido-base e cinetica | 1 | 1 | 1 | 0 | 0 | 5 | 4 | 1 | 1 | 2 | 2 | 2 | 3 | 4 | 2 | 2 | 2 |
| citologia e metabolismo celular | 0 | 4 | 0 | 1 | 1 | 2 | 1 | 1 | 3 | 3 | 2 | 1 | 2 | 3 | 3 | 3 | 1 |
| termologia | 2 | 2 | 0 | 1 | 2 | 0 | 3 | 1 | 1 | 0 | 3 | 2 | 3 | 1 | 1 | 3 | 2 |
| solucoes e concentracao | 1 | 0 | 1 | 0 | 2 | 1 | 2 | 2 | 1 | 0 | 1 | 3 | 2 | 1 | 2 | 0 | 0 |
| radiacao e fisica moderna | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 2 | 2 | 1 | 2 |
| optica | 0 | 2 | 1 | 0 | 0 | 2 | 1 | 0 | 1 | 1 | 0 | 2 | 0 | 1 | 0 | 2 | 0 |
| eletroquimica | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 1 | 4 | 0 | 0 | 0 |
| termoquimica | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| indefinido | 0 | 0 | 1 | 1 | 2 | 3 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**O que os números dizem (com incerteza):**

- **12 dos 19 temas aparecem em 15 ou mais dos 17 anos, e 7 deles em todos**: química orgânica/polímeros (4,8/ano), mecânica (4,7), eletricidade/magnetismo (4,1), ligações/materiais/separação (3,5), genética/biotecnologia (3,4), saúde/doenças (2,9), ecologia/meio ambiente (2,9). Tem variação grande ano a ano (mecânica vai de 2 a 7; orgânica de 1 a 7), então "média/ano" é uma expectativa, não uma cota.
- **Física, Química e Biologia dividem a prova quase em três partes iguais**: na primeira análise (2019-2025, primeira-palavra-vence) Biologia saiu com 48% (147/308), Física 20% e Química 29%. Com o dicionário por pontuação, 2019-2025 dá Biologia 105, Física 104, Química 100 de 309 (34% / 34% / 32%); nos 221 rotulados do `enem.db`, o rótulo diz Biologia 39%, Física 35%, Química 26%. Ou seja, o "Biologia é quase metade" do documento anterior **não se sustenta** (era em parte efeito da ordem de prioridade do método antigo). Por período (fatia das classificadas): Biologia 37% / 32% / 35%, Física 30% / 32% / 34%, Química 33% / 36% / 31% (09-14 / 15-19 / 20-25), sem tendência clara. O número de questões por disciplina por ano:

| Ano | Física | Química | Biologia |
|---|---|---|---|
| 2009 | 14 | 16 | 15 |
| 2010 | 13 | 15 | 17 |
| 2011 | 10 | 15 | 19 |
| 2012 | 14 | 12 | 18 |
| 2013 | 16 | 13 | 14 |
| 2014 | 13 | 15 | 14 |
| 2015 | 15 | 14 | 16 |
| 2016 | 12 | 17 | 12 |
| 2017 | 14 | 16 | 15 |
| 2018 | 16 | 14 | 15 |
| 2019 | 13 | 18 | 11 |
| 2020 | 17 | 17 | 11 |
| 2021 | 11 | 15 | 19 |
| 2022 | 15 | 14 | 16 |
| 2023 | 14 | 13 | 18 |
| 2024 | 17 | 13 | 14 |
| 2025 | 17 | 10 | 16 |

- **Sinais de tendência 2020-2025 versus 2009-2019 são fracos**: nenhum tema passa de |z| = 1,9 (o maior positivo é radiação/física moderna, +1,7, de 1% para 3% das questões). Saúde/doenças parece cair (10% → 5% → 5%, z = −1,5) e estequiometria também (7% → 5% → 3%, z = −1,9), mas com esta base isso pode ser ruído.
- **Temas de baixa frequência não "somem"**: eletroquímica aparece em 8 dos 17 anos (13 questões), óptica em 9 (13), radiação em 11 (14), termoquímica em 3 (3). São ~0,8/ano ou menos; "não cair num ano" é comum para eles.
- **Termologia** não é rara como o documento anterior sugeriu (2 questões): aqui são 27 questões em 14 dos 17 anos. Aquela contagem era artefato de prioridade do método antigo.

### 2.4 Matemática (759 questões; 100 "indefinido", 13%)

`indefinido` concentra-se em 2013 a 2016 (10, 12, 13, 13 por ano, imagem sem texto; seção 1.2) e cai para 1 a 4 por ano depois de 2019; portanto, contagens absolutas de 2011 a 2016 estão **subestimadas**. Por isso a tabela traz também a fatia entre as classificadas.

| Tema | Anos (de 17) | Total | Média/ano | 09-14 | 15-19 | 20-25 | % dos classif. 09-14 / 15-19 / 20-25 | z(20-25 vs 09-19) |
|---|---|---|---|---|---|---|---|---|
| porcentagem e matematica financeira | 17 | 135 | 7.9 | 7.5 | 8.6 | 7.8 | 20% / 23% / 19% | -0.9 |
| geometria espacial | 17 | 112 | 6.6 | 7.5 | 5.6 | 6.5 | 20% / 15% / 16% | -0.8 |
| geometria plana | 17 | 102 | 6.0 | 5.0 | 7.0 | 6.2 | 13% / 19% / 15% | -0.4 |
| estatistica | 17 | 69 | 4.1 | 3.7 | 3.2 | 5.2 | 10% / 9% / 12% | +1.2 |
| razao, proporcao e escala | 17 | 63 | 3.7 | 4.0 | 2.6 | 4.3 | 11% / 7% / 10% | +0.5 |
| funcoes | 17 | 54 | 3.2 | 3.0 | 3.4 | 3.2 | 8% / 9% / 8% | -0.5 |
| probabilidade | 17 | 45 | 2.6 | 2.7 | 2.4 | 2.8 | 7% / 6% / 7% | -0.0 |
| analise combinatoria | 12 | 29 | 1.7 | 0.5 | 2.2 | 2.5 | 1% / 6% / 6% | +1.5 |
| raciocinio logico e contagem simples | 9 | 16 | 0.9 | 1.2 | 0.6 | 1.0 | 3% / 2% / 2% | -0.0 |
| sistemas, equacoes e algebra | 10 | 16 | 0.9 | 1.0 | 0.6 | 1.2 | 3% / 2% / 3% | +0.5 |
| sequencias e progressoes | 8 | 9 | 0.5 | 0.8 | 0.4 | 0.3 | 2% / 1% / 1% | -1.0 |
| geometria analitica | 5 | 5 | 0.3 | 0.3 | 0.4 | 0.2 | 1% / 1% / 0% | -0.8 |
| trigonometria | 4 | 4 | 0.2 | 0.0 | 0.0 | 0.7 | 0% / 0% / 2% | +2.6 |
| indefinido | - | 100 | 5.9 | | | | | |

Matriz por ano:

| Tema | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| porcentagem e matematica financeira | 8 | 7 | 8 | 5 | 6 | 11 | 6 | 9 | 6 | 11 | 11 | 7 | 11 | 8 | 6 | 9 | 6 |
| geometria espacial | 8 | 12 | 3 | 9 | 7 | 6 | 5 | 6 | 7 | 2 | 8 | 4 | 6 | 9 | 5 | 5 | 10 |
| geometria plana | 6 | 6 | 5 | 5 | 6 | 2 | 5 | 6 | 9 | 10 | 5 | 7 | 6 | 6 | 8 | 7 | 3 |
| estatistica | 5 | 3 | 2 | 3 | 4 | 5 | 3 | 3 | 3 | 3 | 4 | 5 | 6 | 5 | 6 | 4 | 5 |
| razao, proporcao e escala | 6 | 3 | 6 | 3 | 4 | 2 | 1 | 2 | 2 | 4 | 4 | 7 | 5 | 2 | 3 | 4 | 5 |
| funcoes | 1 | 5 | 4 | 3 | 2 | 3 | 4 | 2 | 5 | 2 | 4 | 4 | 1 | 2 | 4 | 5 | 3 |
| probabilidade | 3 | 2 | 4 | 3 | 3 | 1 | 2 | 2 | 2 | 5 | 1 | 2 | 1 | 2 | 5 | 3 | 4 |
| analise combinatoria | 2 | 0 | 0 | 0 | 0 | 1 | 2 | 2 | 4 | 0 | 3 | 2 | 4 | 2 | 2 | 3 | 2 |
| raciocinio logico e contagem simples | 1 | 0 | 1 | 4 | 0 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 1 | 2 | 0 |
| sistemas, equacoes e algebra | 0 | 0 | 3 | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 3 | 3 | 0 | 0 | 0 |
| sequencias e progressoes | 1 | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 0 |
| geometria analitica | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| trigonometria | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 |
| indefinido | 3 | 5 | 8 | 9 | 10 | 12 | 13 | 13 | 6 | 4 | 3 | 3 | 1 | 2 | 2 | 2 | 4 |

**Leitura por grupo grosso** (os grupos mais confiáveis: concordância de 65% com os rótulos). Coluna = média de questões/ano (fatia das classificadas) em 09-14 / 15-19 / 20-25:

| Grupo | Anos (de 17) | 09-14 | 15-19 | 20-25 | Recall / precisão vs. rótulos |
|---|---|---|---|---|---|
| Geometria (plana, espacial, analítica, trigonometria) | 17 | 12,8 (35%) | 13,0 (35%) | 13,5 (32%) | 80% / 72% |
| Proporcionalidade e aritmética (razão, %, finanças, sistemas, lógica) | 17 | 13,7 (37%) | 12,4 (34%) | 14,3 (34%) | 61% / 74% |
| Dados e contagem (estatística, probabilidade, combinatória) | 17 | 6,8 (18%) | 7,8 (21%) | 10,5 (25%) | 73% / 60% |
| Funções e sequências | 17 | 3,8 (10%) | 3,8 (10%) | 3,5 (8%) | 26% / 53% |

- **Geometria e proporcionalidade/aritmética contextual somam ~25 a 28 questões por ano (66% a 72% das classificadas) nos 17 anos**, sem tendência.
- **Dados e contagem é o único grupo que sobe** (de 18% para 25% das classificadas; +1,0 e depois +2,7 questões/ano entre períodos). Como a fatia é entre classificadas, a queda do `indefinido` não explica sozinha o aumento, mas 2009-2016 tem menos texto: é um sinal de **evidência média**, com o mesmo rumo que o aumento de "gráfico/tabela" no texto (seção 3.4).
- **Funções e sequências** têm concordância baixa com os rótulos (recall 26%): parte das questões de função aparece como razão/financeira no dicionário. Não use 3,5/ano como valor firme; pode ser o dobro.
- **Por tema** (dicionário mais fino, com as ressalvas de 2.2): geometria espacial (6,6/ano, 17 anos), geometria plana (6,0), estatística (4,1), razão/proporção/escala (3,7), funções (3,2), probabilidade (2,6) e porcentagem/financeira (7,9, superatribuída) aparecem nos 17 anos. Análise combinatória aparece em 12 dos 17 (zero de 2010 a 2013 nas contagens, mas esses anos têm 5 a 10 questões indefinidas), com 0,5 questão/ano em 09-14 e 2,2 a 2,5 depois (z = +1,5): sinal fraco de crescimento. Trigonometria, progressões, geometria analítica e raciocínio lógico têm 0,2 a 0,9/ano no dicionário, valor provavelmente subcontado.

### 2.5 Comparação com `docs/padroes_de_prova.md` (7 anos)

| Item do documento anterior | Com 17 anos |
|---|---|
| Geometria espacial, plana, estatística e probabilidade "nos 7 anos" | **Confirmado nos 17 anos** (mesmas quatro, mais razão/proporção, funções e porcentagem). |
| Sistemas de equações "nos 7 anos" | **Não confirmável**: o dicionário só acerta 1 de 19 rótulos de "sistemas/equações/álgebra" (recall 5%); tema aparece em só 10 dos 17 anos por palavra-chave. Provavelmente é problema de vocabulário, não de ausência. |
| Razão/proporção sem contar 2019 por causa do balde `matematica_basica` | Sem esse problema aqui; presente nos 17 anos. |
| Biologia como bloco de 48% de Natureza | **Revisto para ~35%**; Física e Química ficaram perto de 1/3 cada (ver 2.3). |
| Termologia quase inexistente | **Artefato**: 27 questões em 14 anos. |
| Equilíbrio químico "quatro anos seguidos de 2022 a 2025, antes disso sem o nome no texto" | **Não é novidade**: aparece em 2009, 2011, 2014, 2015, 2018 e depois 2022 a 2025 (seção 4, cadeia 4). |
| Tópicos de 1 a 2 anos (fotossíntese, osmose, ATP) podem só ter caído menos | Compatível: osmose aparece em 4 dos 17 anos, mas 2012, 2017, 2019 e 2022 são espaçados. |
| Cadeia respiratória em 2019, 2022 e 2023 | **Continua só nesses 3 anos** em 17 (não há antecedente antes de 2019 nas palavras "desacoplador", "ATP sintase", "gradiente de prótons"). Fica mais fraco como "padrão histórico". |
| Indução eletromagnética em 2019, 2020, 2023, 2025 | **Ganhou um antecedente**: 2011 nº 56 (captador de guitarra elétrica). |
| Ecologia/meio ambiente estável | 09-14: 4,0/ano; 15-19: 1,6; 20-25: 2,8. **Instável** (não é uma constante). |

## 3. Termos e bigramas mais frequentes por área

Método: tokens de 4 ou mais letras, sem acento, sem stopwords do português (lista própria com artigos, preposições, conjunções, verbos auxiliares e palavras de rotina de prova como "texto", "adaptado", "figura", "acesso", "considere"), com singular/plural aproximado (remoção de "s"; por isso aparecem formas como "massa molare" e "portugue"). Contagem por **questão distinta** (uma questão conta uma vez por termo), texto = contexto + enunciado. "Bigrama" = duas palavras vizinhas depois de remover stopwords (então "comprimento de onda" vira "comprimento onda"). Aparecem só termos com pelo menos 12 questões (unigramas) ou 5 (bigramas). "Técnico" = o termo é mais frequente na área que nas outras (razão ≥ 2,5 em unigramas, ≥ 2 em bigramas) e aparece em pelo menos 70% dos anos (unigramas) ou em ≥ 5 anos (bigramas). Nomes de fonte bibliográfica (Porto Alegre, Petrópolis Vozes, Companhia das Letras, etc.) foram tirados dos bigramas.

### 3.1 Natureza (17 anos)

| Tipo | Termos (questões / anos em que aparece) |
|---|---|
| Unigramas técnicos em 15+ dos 17 anos | água 135/17; energia 83/17; substância 71/17; massa 68/17; reação 65/17; espécie 62/17; composto 59/17; temperatura 53/16; elétrica 52/17; planta 50/17; organismo 50/17; célula 49/17; velocidade 42/15; ácido 39/17; concentração 36/15; molécula 35/17; doença 35/16; solução 33/16; corrente 33/15; ambiente 69/17 |
| Bigramas químicos | equação química 18/11; massa molar 14/9; reação química 10/8; solução aquosa 9/8; composto orgânico 7/6; cloreto de sódio 7/6; matéria orgânica 9/9 |
| Bigramas de física | energia elétrica 16/11; corrente elétrica 14/11; comprimento de onda 14/9; aceleração da gravidade 11/9; resistência elétrica 10/8; campo magnético 8/7; calor específico 7/5; diferença de potencial 7/6; circuito elétrico 5/5; energia térmica 7/6 |
| Bigramas de biologia/ambiente | seres vivos 14/11; combustíveis fósseis 7/6; energia solar 7/7; cadeia alimentar 7/7; dióxido de carbono 6/6; efeito estufa 5/5; ciclo do nitrogênio 5/5; *Aedes aegypti* 5/5 |

O vocabulário técnico que atravessa quase todos os anos é o mesmo da primeira análise (reação/equação, mol/massa molar, corrente/resistência/potencial, onda/comprimento de onda, célula, poluente, combustível). O que os 17 anos acrescentam é que **"seres vivos", "cadeia alimentar", "energia solar", "combustíveis fósseis" e "dióxido de carbono"** também são vocabulário de longa data, não novidade recente.

### 3.2 Matemática (17 anos)

| Tipo | Termos (questões / anos) |
|---|---|
| Unigramas | número 138/17; quantidade 126/17; valor 108/17; medida 85/17; empresa 62/17; área 62/17; altura 59/17; dados 53/17; média 52/17; volume 48/15; probabilidade 45/17; distância 42/17; preço 35/14; litro 32/14; máximo 32/14; mínimo 26/13; percentual 26/13 |
| Bigramas | quantidade mínima 13/9; metro quadrado 12/10; "utilize aproximação" 12/9 (instrução de arredondar π ou raiz); unidade de medida 10/8; projeção ortogonal 10/9; metro cúbico 9/6; segmento de reta 9/7; circular reto 9/7 (cilindro/cone); expressão algébrica 8/7; plano cartesiano 8/6; cilindro circular 8/6; vazão constante 7/6; diretamente proporcional 6/5; paralelepípedo reto 6/6 |

Leitura: o vocabulário que se repete em Matemática é **de cenário** (quantidade, valor, empresa, preço, medida, litro, metro quadrado) e de geometria de sólidos (cilindro, paralelepípedo, projeção ortogonal), mais do que de conceito puro (função, sequência aparecem pouco no ranking).

### 3.3 Linguagens e Humanas (15 anos, exploratório)

| Área | Unigramas técnicos (questões / anos) | Bigramas (questões / anos) |
|---|---|---|
| Linguagens | língua 88/15; palavra 86/15; linguagem 65/15; poema 53/14; gênero 49/15; leitor 39/14; poesia 35/13; canção 32/12; internet 32/13; estratégia 32/14; comunicação 54/15 | língua portuguesa 34/13; letra de canção 16/9; tecnologia da informação 14/10; redes sociais 13/9; função social 11/8; estratégia argumentativa 10/6; função da linguagem 10/10; literatura brasileira 10/7; gênero textual 8/6; norma padrão 7/7; Machado de Assis 7/5; campanha publicitária 5/5 |
| Humanas | Brasil 155/15; século 103/15; política 91/15; Estado 86/15; sociedade 83/15; cidade 82/14; terra 80/15; guerra 37/15; filosofia 29/13; democracia 28/13; regime 28/14 | Estados Unidos 17/11; século XVIII 11/8; Idade Média 10/8; movimentos sociais 9/6; América Latina 7/7; regime político 7/7; política pública 7/7; centro urbano 6/5; reforma agrária 5/5; Brasil colonial 5/5; fluxo migratório 5/5 |

### 3.4 Termos recentes (2020 a 2025 contra 2009 a 2019)

Duas abordagens, ambas com cautela: os textos de 2020 em diante são mais longos (mediana da razão de frequência de termos comuns: 1,45 em Natureza e 1,71 em Matemática), então qualquer termo "cresce" só por isso; usei razão normalizada por essa mediana na primeira, e uma lista curada de conceitos na segunda (proporção de questões que citam o conceito). Vale para Natureza e Matemática (2020-2025, 267 e 265 questões, contra 492 e 494 antes).

**(a) Conceitos curados** (n = questões que citam; % = fatia; z aproximado; "anos" = em quantos dos 6 anos recentes aparece):

| Área | Conceito | 2009-2019 | 2020-2025 | z | Anos recentes |
|---|---|---|---|---|---|
| Natureza | poluente / resíduo | 15 (3%) | 22 (8%) | +3,2 | 6/6 |
| Natureza | enzima | 4 (1%) | 9 (3%) | +2,6 | 5/6 |
| Natureza | densidade | 8 (2%) | 10 (4%) | +1,8 | 5/6 |
| Natureza | bateria / pilha | 10 (2%) | 11 (4%) | +1,7 | 5/6 |
| Natureza | pH / ácido | 25 (5%) | 22 (8%) | +1,7 | 6/6 |
| Natureza | efeito estufa / aquecimento global | 8 (2%) | 1 (0%) | −1,5 | 1/6 |
| Natureza | célula, energia, genes, vírus/vacina, radiação | estáveis (|z| < 1,1) | | | |
| Matemática | aplicativo / internet / celular | 5 (1%) | 15 (6%) | +3,8 | 6/6 |
| Matemática | preço / compra / desconto | 43 (9%) | 40 (15%) | +2,7 | 6/6 |
| Matemática | cilindro / cone / esfera / prisma / pirâmide | 17 (3%) | 21 (8%) | +2,7 | 6/6 |
| Matemática | gráfico / tabela | 59 (12%) | 49 (18%) | +2,5 | 6/6 |
| Matemática | velocidade / km/h | 10 (2%) | 13 (5%) | +2,2 | 6/6 |
| Matemática | volume / capacidade / litros | 53 (11%) | 42 (16%) | +2,0 | 6/6 |
| Matemática | probabilidade, função, área | estáveis (|z| < 0,8) | | | |

(Foram testados 22 conceitos em Natureza e 13 em Matemática; com esse número de testes, 1 a 2 resultados com |z| > 2 por acaso são esperados. Os mais consistentes por estarem em 6 de 6 anos recentes são poluente/resíduo, aplicativo/internet/celular, preço/compra, gráfico/tabela e cilindro/sólidos.)

**(b) Termos genéricos que "crescem"** (razão ≥ 2 após normalização, presentes em ≥ 3 dos anos recentes). Natureza: contendo (15 questões contra 7), representada (15 contra 7), ilustra (13 contra 5), resíduo (13 contra 7), aula (8 contra 1), enzima (9 contra 3), poluente (9 contra 5), carga (9 contra 4). Matemática: apresenta (37 contra 14), pretende (29 contra 15), preço (25 contra 10), reto (18 contra 5), compra (15 contra 7), estudante (12 contra 4). Em Matemática também ficam "quantidade mínima" (9 contra 4), "circular reto" (7 contra 2), "paralelepípedo reto" (5 contra 1) e "triângulo equilátero" (5 contra 0). Em Linguagens (2020-2023, 179 questões) e Humanas (180), praticamente nada passa dos filtros; os poucos itens são de 3 ou 4 anos e 5 a 21 questões (Machado de Assis 5 contra 2, canção 7 contra 9): ruído.

**Leitura:** o "novo" de 2020 em diante é mais **estilo** (enunciado mais longo, contexto de aplicativo, aula, compra) do que **conteúdo** (poluente/resíduo, enzima e sólidos geométricos crescem um pouco). Não há indício de tema científico totalmente novo.

## 4. Cadeias de conceito que voltam com o mesmo mecanismo

Critério: para cada mecanismo, busquei o termo-chave em Natureza (ou Matemática) nos 17 anos e li o trecho do enunciado ou do contexto (cerca de 200 a 300 caracteres em torno do termo, não a questão inteira) para conferir se o mecanismo é o mesmo. Ids são `(ano, índice)` do corpus. "Anos" = quantos anos distintos.

| # | Mecanismo / cadeia | Questões `(ano, índice)` lidas | Anos | Observação |
|---|---|---|---|---|
| 1 | **Cadeia respiratória, gradiente de prótons, ATP sintase, desacoplador ou inibidor** (falta de ATP ou calor como consequência) | (2019, 127) DNP como desacoplador; (2022, 127) termogenina impede prótons de chegarem à ATP sintetase, gerando calor; (2023, 127) cianeto e gradiente de prótons | 3 | Só a partir de 2019; antes há mitocôndria só como organela (2014, 73; 2024, 132 fibras musculares). |
| 2 | **Indução eletromagnética: fluxo magnético variável gera corrente**, com efeito Joule | (2011, 56) captador de guitarra; (2019, 92) linha de alta tensão e cerca; (2020, 98) gerador de usina; (2023, 108) fogão por indução; (2025, 122) fogão por indução | 5 | O cenário "fogão por indução" repete em 2023 e 2025. |
| 3 | **Poluente persistente/apolar acumula em organismo ou tecido e sobe na cadeia** | (2009, 23) metais pesados bioacumulativos; (2019, 123) estrôncio-90 acumula em cadeias; (2023, 129) aldrin de baixa polaridade, em qual fluido se concentra; (2023, 115) metais tóxicos captados pelo vegetal; (2024, 128) microplástico com poluentes orgânicos apolares lipossolúveis; (2025, 134) descarte inadequado de hormônios contamina solo, plantas e recursos hídricos | 5 | Química (polaridade, solubilidade) + ecologia; o enunciado muda o "contaminante", o mecanismo se mantém. |
| 4 | **Equilíbrio químico: deslocamento e constante** | (2009, 12) sabão e hidrólise; (2011, 75) desmineralização dental por OH⁻ deslocando o equilíbrio; (2014, 71) CO₂ no mar, equilíbrio e corais; (2015, 71) constantes de equilíbrio; (2018, 102) cloreto e pigmento; (2022, 107) papel do H⁺ e equilíbrio; (2023, 104) dissolução por deslocamento; (2024, 94) equilíbrio de desmineralização do esmalte; (2025, 117) favorecer TiCl₄ | 9 | **(2011, 75) e (2024, 94) são o mesmo cenário** (esmalte dentário) com 13 anos de distância. |
| 5 | **Meia-vida / decaimento exponencial** (datação, pesticida, radioisótopo) | (2013, 49) carbono-11 (medicina); (2016, 70) datação por carbono-14 de DNA de mamute; (2017, 104) datação de fóssil por emissões beta; (2020, 150) carbono-14 (Matemática); (2021, 95) meia-vida de pesticida no solo; (2022, 109) iodo-131; (2025, 110) cobalto-60 | 7 | Aparece em Química, Física e Matemática. |
| 6 | **Osmose e pressão osmótica** | (2012, 86) célula em solução de NaCl; (2017, 120) osmose reversa (dessalinização); (2019, 130) sal em batata; (2022, 114) epiderme em meio hipotônico | 4 | Pouco frequente (4 de 17 anos), mas repetitivo. |
| 7 | **Eutrofização, oxigênio dissolvido e DBO** | (2010, 57) esgoto e eutrofização; (2010, 72) DBO; (2014, 63) fertilizante e algas; (2015, 47) escurecimento da água; (2020, 119) OD e DBO; (2024, 127) urbanização e eutrofização; (2025, 111) descarte (eutrofização como alternativa) | 6 | 2010, 72 e 2020, 119 são sobre DBO/OD. |
| 8 | **Tensoativo, micela, sabão e detergente** (polar/apolar) | (2012, 70) tensoativo sintético; (2012, 89) anfifílica; (2014, 58) sabão forma micelas; (2018, 126) tensoativos anfifílicos; (2019, 122) "sabonete" como tensoativo; (2020, 104) aves lavadas com detergente após vazamento; (2023, 133) detergente e espuma no esgoto | 6 | Mecanismo estável; mudou o cenário. |
| 9 | **Pilha e eletrólise** (reações nos eletrodos, ânodo/cátodo, força eletromotriz) | (2009, 15) eletrorrefino do cobre; (2010, 74) eletrólise do cobre; (2013, 74) pilha de Daniell; (2017, 95) eletrólise de salmoura; (2018, 93) pilha de Bagdá; (2019, 118) bateria zinco-ar; (2021, 133) pilhas de lítio; (2022, 119) três pilhas em série (Física) | 8 | Eletroquímica (Química) e circuito de pilhas (Física). |
| 10 | **Separação de misturas e tratamento de água** (destilação, decantação, filtração, extração) | (2009, 44) destilação do etanol; (2011, 52) tratamento de água de rio; (2014, 51) remover clorofórmio; (2016, 72) aromatização em sauna; (2020, 123) mistura de água e acetato de etila; (2022, 126) estação de tratamento; (2025, 91) filtração em carvão | 7 | Já usada como rótulo `metodos_separacao_misturas` no `enem.db` em algumas. |
| 11 | **CO₂ e ambiente** (efeito estufa, absorção pelo mar, fixação por plantas) | (2009, 1) alternativa viável para combater o efeito estufa; (2011, 80) metano em hidrelétricas; (2014, 71) CO₂ no mar; (2016, 69) CO₂ elevado e trigo; (2020, 103) gás carbônico e ciclo do carbono; (2025, 104) aumento de 50% de CO₂ | 6 | Contexto amplo; foco varia (às vezes é só cenário). |
| 12 | **Matemática: escolher a opção mais barata / quantidade mínima** (custo, compra, frete, consumo) | (2009, 178) empréstimo com juros; (2010, 173) custo de deslocamento entre cidades; (2013, 147) quantidade mínima de rolos; (2017, 163) custo de passagem; (2020, 159) preço de cimento e frete; (2024, 166) valor por loja; (2025, 136) consumo de GNV | 7 | 23 questões em 12 anos citam "quantidade mínima", "menor custo" ou similar; li o trecho de 7. |
| 13 | **Matemática: projeção ortogonal sobre um plano** | (2013, 180) gangorra; (2014, 160) caminho sobre o piso; (2016, 178) caminho em globo; (2024, 162) pontos em planos paralelos | 4 | 14 questões em 11 anos citam o termo; li 4. |

Mecanismos 1 a 11 estão em Natureza. Os ids de 2023 que o documento anterior chama de `2023_cinza_N` correspondem aqui a outros índices (seção 0.2).

## 5. Linguagens e Humanas, 2009 a 2023 (exploratório)

**Aviso:** analiso só o que o corpus permite: texto de contexto e enunciado (2024 e 2025 não têm Linguagens nem Humanas). **Os temas são multirrótulo** (uma questão pode entrar em mais de um tema; 211 questões de Linguagens e 184 de Humanas casam com 2 ou mais temas) e **154 questões de Linguagens e 193 de Humanas não casam com nenhum**; por isso os totais não somam. As palavras-chave são amplas e não são gênero textual oficial. Não há como ler imagem (charge, mapa, quadro). Não usar para priorizar tema fino.

### 5.1 Linguagens (673 questões)

| Tema por palavra-chave | Questões com o termo | Anos (de 15) | Média/ano | % das questões 2009-2016 | % 2017-2023 |
|---|---|---|---|---|---|
| Tecnologia / internet / redes sociais / mídia | 115 | 15 | 7,7 | 17% | 17% |
| Crônica / conto / romance / literatura | 109 | 15 | 7,3 | 16% | 17% |
| Poesia / poema / verso | 101 | 15 | 6,7 | 16% | 14% |
| Teatro / dança / cinema / prática corporal / esporte | 85 | 15 | 5,7 | 10% | 16% |
| Canção / música | 66 | 15 | 4,4 | 9% | 10% |
| Notícia / reportagem / jornal / opinião | 66 | 15 | 4,4 | 10% | 10% |
| Publicidade / propaganda / campanha | 56 | 15 | 3,7 | 9% | 8% |
| Gramática / coesão / função da linguagem | 50 | 15 | 3,3 | 9% | 5% |
| Artes visuais (pintura, escultura, fotografia) | 45 | 15 | 3,0 | 5% | 9% |
| Literatura por escola (romantismo, modernismo, autores) | 44 | 14 | 2,9 | 8% | 5% |
| Variação linguística / oralidade / norma | 41 | 13 | 2,7 | 6% | 6% |
| Charge / cartum / tirinha / humor | 28 | 11 | 1,9 | 5% | 3% |

### 5.2 Humanas (674 questões)

| Tema por palavra-chave | Questões com o termo | Anos (de 15) | Média/ano | % 2009-2016 | % 2017-2023 |
|---|---|---|---|---|---|
| Geografia: urbanização / população / migração | 134 | 15 | 8,9 | 20% | 19% |
| Geografia econômica / campo / indústria / energia | 109 | 15 | 7,3 | 16% | 16% |
| Cidadania / direitos / movimentos sociais / política | 94 | 15 | 6,3 | 15% | 12% |
| Geografia física / meio ambiente (clima, relevo, bioma) | 89 | 15 | 5,9 | 14% | 12% |
| Brasil Colônia / Império / escravidão | 86 | 15 | 5,7 | 13% | 12% |
| Filosofia (autores, ética) | 75 | 15 | 5,0 | 11% | 12% |
| História geral antiga / medieval / moderna | 45 | 15 | 3,0 | 7% | 7% |
| Brasil República / Vargas / ditadura | 37 | 12 | 2,5 | 8% | 3% |
| História contemporânea (guerras, nazismo, Guerra Fria) | 33 | 13 | 2,2 | 6% | 4% |
| Sociologia (autores e conceitos) | 26 | 13 | 1,7 | 4% | 4% |

**Achados possíveis, todos fracos:** (i) todos os 12 temas de Linguagens e 10 de Humanas aparecem em quase todos os anos, ou seja, a prova **não concentra em poucos temas que caem sempre**; (ii) as mudanças 2009-2016 contra 2017-2023 são pequenas (maiores: "teatro/dança/cinema/prática corporal" de 10% para 16% e "Brasil República/Vargas/ditadura" de 8% para 3%), sem teste de significância e com palavras-chave amplas; (iii) a dependência de imagem em Linguagens (26% e 21%) e Humanas (20% e 12%) está em 1.3. Para Linguagens e Humanas, o mais que este corpus autoriza é dizer "o vocabulário é variado e estável"; não há base para ordem de prioridade por tema. Redação não está no corpus.

## 6. Hipóteses de priorização

**São indícios, não taxas oficiais de incidência.** Com 15 a 17 provas regulares e sem PPL, o intervalo de incerteza de uma média por ano de 3 a 5 questões é largo (um tema que "vem 4 vezes por ano" pode ter vindo 2 ou 7 em um ano específico: veja as matrizes). Evidência **forte** = padrão constante nos 17 anos e o dicionário concorda bem com os rótulos; **média** = padrão constante mas com o dicionário só parcialmente confiável, ou tendência com |z| ≈ 2; **fraca** = baseada em poucos anos, poucas questões ou classificação frágil.

| # | Hipótese | Evidência | O que ainda falta para confirmar |
|---|---|---|---|
| 1 | Em Matemática, **geometria (plana e espacial)** é o maior bloco estável: ~13 questões por ano (32% a 35% das classificadas) nos 17 anos, sem tendência; geometria espacial (6,6/ano) e plana (6,0/ano) aparecem em todos os anos | **Forte** | Ler uma amostra de 30 a 40 questões de geometria para ver quantas dependem de figura (o corpus tem 64% a 68% de Matemática com imagem em 2017-2023); dividir "sólidos com volume" de "geometria plana pura". |
| 2 | Em Matemática, **proporcionalidade e aritmética de contexto** (razão, escala, porcentagem, preço/compra, sistemas simples) soma ~13 a 14 questões por ano (34% a 37%), 17/17 anos | **Média** | O dicionário só acerta 61% dos rótulos do grupo e superatribui porcentagem; medir com rótulo manual de uma amostra. |
| 3 | **Dados e contagem (estatística, probabilidade, análise combinatória)** cresce: 6,8 → 7,8 → 10,5 questões/ano (18% → 21% → 25% das classificadas), e "gráfico/tabela" nos enunciados sobe de 12% para 18% | **Média** | 2009-2016 tem muitas questões sem texto (o crescimento pode ser efeito); precisa ler as figuras (OCR ou revisão manual). |
| 4 | **Funções, trigonometria, progressões, geometria analítica e lógica** têm baixa frequência no dicionário (0,2 a 3,5/ano por tema), então valem menos horas **se** o tempo for curto | **Fraca** | Concordância baixa com os rótulos (recall 26% em funções, 5% a 17% nos demais); pode estar subcontado. Verificar com rótulo manual. |
| 5 | Em Natureza, **Física, Química e Biologia pesam cerca de um terço cada** (2019-2025, Física / Química / Biologia: 34% / 32% / 34% pelo dicionário; 35% / 26% / 39% nos rótulos), e a fatia é estável entre 2009 e 2025; não há "bloco dominante" | **Média** | O documento anterior (Biologia 48%) discorda; a diferença de método pode ser resolvida rotulando uma amostra à mão. |
| 6 | **Mecânica e eletricidade/magnetismo** (≈ 4,7 e 4,1 questões/ano, 17/17 anos, precisão 80% a 86%) formam o bloco mais confiável de Física; **ondas/acústica** (2,2/ano, 16/17 anos) e **termologia** (1,6/ano, 14/17) vêm depois | **Forte** (mecânica, eletricidade); **média** (ondas, termologia) | Confirmar que "eletricidade" no dicionário é circuito/potência e não só contexto (chuveiro, lâmpada). |
| 7 | **Química orgânica/polímeros** (4,8/ano) e **ligações/polaridade/separação de misturas** (3,5/ano) aparecem nos 17 anos e se ligam a várias cadeias (tensoativo, bioacumulação, tratamento de água) | **Média** | Precisão baixa (48% orgânica, 25% ligações/separação): parte da contagem é contexto. |
| 8 | **Mecanismos repetidos em cenários novos**: equilíbrio químico (9 anos), meia-vida (7), pilha/eletrólise (8), tensoativo (6), eutrofização (6), indução (5), poluente que acumula (5). Vale estudar o mecanismo e treinar com cenários diferentes, não decorar o exemplo | **Média** | Li só trechos de 200 a 300 caracteres; conferir as questões inteiras e contar quantas cobram exatamente o mesmo raciocínio. |
| 9 | Eletroquímica (8 dos 17 anos), óptica (9), radiação (11) e termoquímica (3) são **temas de baixa frequência** (≤ 0,8/ano), não "temas que nunca caem"; eles caem em cerca de metade dos anos | **Fraca** | Muitos aparecem também dentro de outros temas (pilha em Física, radiação em Ecologia); o dicionário divide esses casos de forma instável. |
| 10 | **Saber ler figura, gráfico e tabela** e **contexto de consumo/tecnologia** pesa cada vez mais: o texto cita figura/gráfico/tabela em 18% (2009-2016) → 33% (2017-2023) → 44% (2024-2025) em Natureza, e 22% → 49% → 49% em Matemática; termos como "aplicativo/internet/celular" (1% → 6%) e "preço/compra/desconto" (9% → 15%) crescem em Matemática | **Média** | 2009-2016 tem muito texto perdido (subestima o passado); 2024-2025 não tem sinal de imagem (o `tem_imagem` é 0); precisa contar imagens de verdade nas provas originais. |

**Limitações que continuam abertas:** (1) Linguagens e Humanas só de 2009 a 2023, exploratório e sem imagem; (2) nada de reaplicação (PPL) nem de provas anteriores a 2009 (o formato mudou em 2009, então uma ponte para trás é discutível); (3) 15 questões ausentes; 10 dos 609 casamentos com o `enem.db` falharam; (4) o dicionário é meu, sem validação externa além dos rótulos do `enem.db`, que também não são verdade absoluta; (5) 2013 a 2016 têm muitas questões com o essencial em imagem; (6) qualquer tendência entre períodos de 5 a 6 anos é pouco poderosa estatisticamente; (7) as cadeias da seção 4 foram conferidas por trechos e não por leitura integral.
