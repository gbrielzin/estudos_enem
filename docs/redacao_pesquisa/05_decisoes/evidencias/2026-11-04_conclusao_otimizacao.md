# Conclusão fixa: como aumentar a cobertura sem aumentar demais o custo de decorar (04/11)

**Aviso: todo veredito SERVE / FORÇA / QUEBRA e toda classificação das redações abaixo é avaliação minha (Claude), feita à mão, não do INEP, e não mede nota. Contagem de amostra, não estatística. Nada aqui foi corrigido por banca.**

## Contagens no topo

**37 temas, só a conclusão (SERVE / FORÇA / QUEBRA)**

| Combinação | Regulares/digital (18) | PPL/3ª/Pará (19) | Total (37) |
|---|---|---|---|
| K0 duas formas de hoje (incluir / ampliar + "verba e contratação") | 11 / 7 / 0 | 7 / 6 / 6 | **18 / 13 / 6** |
| K1 H1: três verbos (incluir / ampliar / criar) | 11 / 7 / 0 | 9 / 4 / 6 | 20 / 11 / 6 |
| K2 H2: verbo único "garantir a oferta de" na Forma 2 | 11 / 7 / 0 | 9 / 4 / 6 | 20 / 11 / 6 |
| K3 H3: meio único "investimento federal, capacitação e campanhas educativas" | 11 / 7 / 0 | 8 / 5 / 6 | 19 / 12 / 6 |
| K4 H2 + meio da Forma 2 trocado por "verba federal e parceria com estados e municípios" | 12 / 6 / 0 | 10 / 3 / 6 | **22 / 9 / 6** |
| K5 H4 + H6: escolher Forma 3 (conscientização) pelo TIPO DO TEMA | 13 / 5 / 0 | 8 / 5 / 6 | 21 / 10 / 6 |
| K6 K4 + Medida 2 fixa para todo tema (mídia faz campanha, H4 + H5) | 15 / 3 / 0 | 12 / 1 / 6 | **27 / 4 / 6** |
| K7 K6 + plano B para tema sem grupo (H7) | 16 / 2 / 0 | 13 / 5 / 1 | **29 / 7 / 1** |
| Referência: A só escola (rodada anterior) | | | 12 / 15 / 10 |
| Referência: B três linhas, verbo livre (rodada anterior) | | | 24 / 7 / 6 |

**Redações nota 1000 (amostra nova de validação, 79 válidas; 6 tiradas)**

| Tipo da ação principal | Quantas de 79 | % |
|---|---|---|
| ENSINO (escola, aula, palestra na escola, currículo) | 24 | 30% |
| FALTA (criar/ampliar serviço, verba, profissionais, fiscalizar) | 34 | 43% |
| CONSCIENTIZAÇÃO fora da escola (mídia, redes, ONG, igreja, palestra solta) | 14 | 18% |
| LEI NOVA (emenda, reformular lei, regulamentar) | 4 | 5% |
| OUTRO (empresa como agente, ação solta) | 3 | 4% |

| Cobertura nas nota 1000 | Regra larga | Regra estrita |
|---|---|---|
| Só ENSINO + FALTA (K0 a K4) | 58 de 79 = **73%** | 46 de 79 = **58%** |
| ENSINO + FALTA + CONSCIENTIZAÇÃO (K5 a K7) | 72 de 79 = **91%** | 60 de 79 = **76%** |

Regra larga = qualquer ação de serviço, verba, subsídio, sanção ou fiscalização conta como FALTA (a mesma da rodada anterior). Regra estrita = só conta FALTA o que a Forma 2 de fato escreve (criar/ampliar serviço, verba, profissionais, fiscalização); ficam de fora 12 casos de "vale-cultura", incentivo fiscal, redução de imposto, regulação de mercado, sanção a empresa, salário mínimo, subsídio a empresa. Dos 79, cerca de 24 (30%) têm campanha de conscientização como ação principal OU como segunda ação.

## Como medi e o que NÃO consigo afirmar

- **Amostras separadas.** Banco `banco_1000/redacoes_1000.db`, tabela `redacoes`, nota 1000 com texto (296). Amostra de **projeto** = 45 (`random.seed(11)`) + 30 do resto (`random.seed(5)`), a tentativa de reproduzir as amostras das rodadas anteriores; usei só para calibrar quanto de campanha existe. Amostra de **validação** = 85 sorteadas (`random.seed(2026)`) do que sobrou, sem nenhuma das 75 acima (sobreposição checada por código: 0). Tirei 6 (3 sem ação visível no trecho, 2 cortadas, 1 repetida com outra grafia de "fi"), ficaram 79.
- **Não consigo confirmar que as 75 de projeto são as mesmas das rodadas de hoje cedo** (a ordem do banco pode ter mudado). Se não forem, a validação pode ter alguma redação já lida antes. Não dá para saber o tamanho disso.
- **As categorias foram definidas antes de ler a validação** e não foram mexidas depois. A regra larga/estrita foi criada depois de ler (para não vender 91% sem aviso); as duas aparecem.
- **O que a cobertura mede:** o TIPO da ação do último parágrafo (escola, serviço, campanha). Não mede o agente (Governo Federal), nem o verbo exato, nem a nota. Por isso K0, K1, K2, K3 e K4 dão a mesma cobertura nas nota 1000: a diferença entre eles é de verbo e de meio, que só sei julgar nos 37 temas (por leitura minha).
- **Reclassifiquei a amostra de projeto só em parte** (li os 25 trechos que não tinham palavra de escola/serviço). Nela, campanha como ação principal parece ser coisa de 3 a 5 em 68 (cerca de 4% a 7%), bem abaixo dos 18% da validação. Estimo que K5 a K7 cubram entre 83% e 86% na amostra de projeto (largo) contra 91% na validação. Estimativa grosseira, não contagem completa.
- **A base tem poucos temas.** Na validação li uns 14 de cinema e uns 17 de trabalho de cuidado (contagem à mão, aproximada). Se o tema do dia for outro, a proporção pode mudar.
- **Contagem automática de palavras nos últimos 600 caracteres (grosseira, só para o meio):** verba/investimento/subsídio em 25 de 79 (32%); profissionais/capacitação/contratação em 14 (18%); parceria/município/estado em 14 (18%); palestra/oficina/debate em 19 (24%); campanha/conscientização/divulgação em 27 (34%); mídia/meios de comunicação/redes em 18 (23%). Leitura: "verba" aparece quase o dobro de "contratação de profissionais". É o único apoio que tenho nos textos para trocar o meio fixo.
- **Risco de ajuste fino:** as hipóteses nasceram depois de eu ver os 37 temas. Os números dos 37 temas de K4 a K7 brilham em parte porque foram desenhados olhando para os casos que falhavam (cinema, renda, lazer, estigma). A validação nas nota 1000 só testa se os TIPOS de ação existem (existem: campanha 18% principal e 30% em qualquer posição), não se a frase fixa funciona em cada tema. **K4 a K7 não têm teste independente da frase em si.**
- **O que não dá para medir:** se a banca aceita uma Medida 2 igual para todo tema (pode virar "coringa", risco já anotado nas pesquisas anteriores), quanto tempo a frase extra consome na prova, e a nota.

## Custo de aprendizagem (em itens)

Contagem: cada verbo, cada meio, cada exceção e cada frase-modelo extra conta 1. "Decisões" = escolhas que ele faz na hora da prova, fora o preenchimento dos colchetes. A frase fixa de abertura/fecho é igual em todos e não entra.

| Combinação | Peças a decorar | Decisões na prova | Custo (qualitativo) |
|---|---|---|---|
| K0 | 5 (2 verbos, 2 meios, 1 exceção de fiscalização) | 2 (escola ou falta? é fiscalização?) | médio-baixo |
| K1 | 6 (3 verbos, 2 meios, 1 exceção) | 3 (+ existe ou não existe?) | médio |
| K2 | 4 (2 verbos, 2 meios) | 1 (escola ou falta?) | baixo |
| K3 | 4 (2 verbos, 1 meio, 1 exceção) | 2 | baixo |
| K4 | 4 (2 verbos, 2 meios) | 1 | baixo |
| K5 | 7 (K4 + Forma 3 com ação e meio + lista de palavras de título) | 3 (título de atitude? escola ou falta? ...) | médio-alto |
| K6 | 6 (K4 + Medida 2 em 2 pedaços: quem/o quê e meio/finalidade) | 1 (a Medida 2 não pede decisão) | baixo-médio, mas escreve uma frase a mais na prova |
| K7 | 7 (K6 + 1 exceção para tema sem grupo) | 2 (escola ou falta? achei grupo?) | médio |

## Veredito por hipótese (avaliação minha)

- **H1 (criar):** sobe 2 temas (lazer de rolezinhos 2014, espaço cultural 2024), não resolve cinema nem renda porque o MEIO "contratação de profissionais" continua errado. Custa 1 verbo e 1 decisão a mais. Dominada por K2.
- **H2 (verbo universal):** "garantir a oferta de [o que falta]" e "garantir a fiscalização de [o que a lei garante]" dão o mesmo ganho de H1 (+2) com um verbo só e sem a exceção da fiscalização: menos peças que K0 e mais temas. Vale mais que dois verbos. "Fortalecer" não ajuda: continua estranho para coisa que não existe (cinema, lazer). "Implementar" serve quase igual a "garantir a oferta", mas fica pesado com "psicólogos nos postos". O custo é um verbo mais genérico, que soa menos concreto (juízo meu).
- **H3 (meio único "investimento federal, capacitação e campanhas educativas"):** resolve o meio que não cabe só em renda (+1) e corta uma peça, mas deixa os dois pedaços genéricos ("capacitação", "campanhas") sem sentido em construção e em transferência de renda, e não conserta o verbo. Perde para meios separados com o meio da Forma 2 trocado (K4: +4 temas, mesma contagem de peças). Meio único economiza 1 peça e entrega 3 temas a menos que K4.
- **H4 (Forma 3 conscientização) por tipo de tema (com H6):** piora. Ganha estigma (2020) e padrões de beleza (2017 PPL), perde valorizar o professor, racismo e arte de periferia, que eram SERVE pela fiscalização ou pelo espaço. Saldo −1 em relação a K4 e custo de decisão maior. **Escolher a forma pelo tipo do tema perde para escolher pelo buraco do D1.** Isso vale nos 37; na validação não tenho como testar a escolha, só que campanha existe.
- **H4 + H5 como Medida 2 fixa (mídia faz campanha sobre [TEMA]):** é o que mais sobe: +5 temas (imigração, estigma, povos tradicionais, trabalhadores rurais, padrões de beleza), porque a primeira medida resolve o buraco do D1 e a segunda toca o centro do tema (atitude), que era a maior causa de FORÇA. Nas nota 1000, o agente mídia/meios de comunicação aparece em cerca de 23% dos textos (palavra-chave) e campanha em 30% (qualquer posição). Fica fora de um agente só, mas o "Governo Federal" continua sendo o agente da Medida 1.
- **H5 (Ministério da Educação como segundo agente):** não testei como alternativa. Para a Medida 2 ele repete a escola da Forma 1; a mídia complementa melhor. É uma lacuna do teste.
- **H6:** pior que o buraco do D1, ver acima.
- **H7 (plano B):** a melhor opção que achei é apagar a oração do grupo e escrever só uma medida de campanha (ver texto copy-pronto). Em 37 temas: ética nacional e desperdício de alimentos passam a SERVIR; família, ajuda humanitária, cultura e mudança social e "o grupo fortalece o indivíduo?" saem de QUEBRA para FORÇA; problemas econômicos continua QUEBRA. Alternativa testada: apagar a oração do grupo e manter Forma 1 ("incluir [TEMA] nas escolas"): fica pior (ética SERVE; os outros ficam FORÇA ou QUEBRA, QUEBRA em 2).

## Pareto (custo de peças x temas que SERVEM)

K4 (4 peças, 22 SERVE) domina K0, K1, K2 e K3. K6 (6 peças, 27 SERVE, 91%/76% nas nota 1000) é o salto grande. K7 (7 peças, 29 SERVE, 1 QUEBRA) ainda sobe, mas quase todo o ganho está nas provas PPL: nos regulares ele só acrescenta ética nacional (+1). K5 é dominada. A fronteira é **K4 → K6 → K7**.

Recomendação: **K6, com a exceção do plano B anexada só se sobrar tempo (vira K7).** Motivo: K6 tem custo baixo de decisão (uma pergunta), tem o maior ganho por peça (+5 SERVE por +2 peças), e a prova de 15/11 é a regular, onde K6 deixa 0 QUEBRA e só 3 FORÇA nos 18 temas.

## RECOMENDADA, copy-pronta para o caderno (K6, com o plano B de K7 no fim)

**Frase fixa (igual em todos os temas; só mudam os colchetes):**

> Portanto, medidas urgentes são necessárias para mitigar esse impasse. Para tanto, cabe ao Governo Federal — órgão responsável pela gestão das políticas públicas nacionais — [AÇÃO], [MEIO], para que [GRUPO] tenha acesso efetivo [à/ao] [DIREITO DO D1] e, consequentemente, o corpo social supere a indiferença. Ademais, cabe aos meios de comunicação — principais formadores de opinião da sociedade — promover campanhas de conscientização sobre [TEMA], por meio de programas e anúncios, a fim de que a população respeite [GRUPO]. Com essas ações, o Brasil poderá, finalmente, afastar-se do cenário de "cidadão de papel" e consolidar a dignidade garantida pela Constituição Federal de 1988.

([TEMA] = o núcleo da introdução. [GRUPO] e [DIREITO] vêm do D1. "[GRUPO]" já traz o artigo: "o imigrante", "a mulher".)

**Forma 1, ENSINO** (D1: a escola não ensina):
- [AÇÃO] = "incluir [TEMA] nas escolas"
- [MEIO] = "por meio de palestras, oficinas e material didático"

**Forma 2, FALTA** (D1: não existe X, fila, falta profissional, ou lei sem fiscalização):
- [AÇÃO] = "garantir a oferta de [o que falta no D1]" ou, se o D1 for lei sem fiscalização, "garantir a fiscalização de [o que a lei garante]"
- [MEIO] = "por meio de verba federal e parceria com estados e municípios"

**A pergunta de decisão (uma só):** "No meu D1, o problema é a escola que não ensina o assunto?" Sim: Forma 1. Não: Forma 2. A Medida 2 (mídia) entra sempre, sem pensar.

**Plano B (acrescenta 1 exceção, só quando o D1 não achou grupo humano):** apague "para que [GRUPO] tenha acesso efetivo ... e, consequentemente," e apague o "Ademais, ... a fim de que a população respeite [GRUPO]". Fica:

> Portanto, medidas urgentes são necessárias para mitigar esse impasse. Para tanto, cabe ao Governo Federal — órgão responsável pela gestão das políticas públicas nacionais — promover campanhas de conscientização sobre [TEMA], nas escolas e nos meios de comunicação, para que o corpo social supere a indiferença. Com essas ações, o Brasil poderá, finalmente, afastar-se do cenário de "cidadão de papel" e consolidar a dignidade garantida pela Constituição Federal de 1988.

## Tabela dos 37 temas (veredito em cada combinação)

S = SERVE, F = FORÇA, Q = QUEBRA. Coluna K0 repete a rodada anterior. Dica de leitura: onde K4 ou K6 muda, o motivo está na coluna do fim.

| Tema | K0 | K1 | K2 | K3 | K4 | K5 | K6 | K7 | Por que muda |
|---|---|---|---|---|---|---|---|---|---|
| 2009 ética nacional | F | F | F | F | F | F | F | S | direito "educação" circular; plano B tira o direito |
| 2010 trabalho e dignidade | S | S | S | S | S | S | S | S | |
| 2011 viver em rede | F | F | F | F | F | F | F | F | direito "informação" não casa com privacidade |
| 2012 imigração | F | F | F | F | F | F | S | S | Medida 2 toca a xenofobia |
| 2013 Lei Seca | S | S | S | S | S | S | S | S | |
| 2014 publicidade infantil | S | S | S | S | S | S | S | S | |
| 2015 violência contra a mulher | S | S | S | S | S | S | S | S | |
| 2016 intolerância religiosa | S | S | S | S | S | S | S | S | |
| 2017 surdos | S | S | S | S | S | S | S | S | |
| 2018 dados | F | F | F | F | F | F | F | F | mesmo problema de 2011 |
| 2019 cinema | F | F | F | F | S | S | S | S | meio "verba e parceria" cabe em construir sala |
| 2020 doenças mentais | F | F | F | F | F | S | S | S | centro é estigma; campanha toca |
| 2020 digital desigualdades | S | S | S | S | S | S | S | S | |
| 2021 registro civil | S | S | S | S | S | S | S | S | |
| 2022 povos tradicionais | F | F | F | F | F | F | S | S | valorização vem na Medida 2 |
| 2023 trabalho de cuidado | S | S | S | S | S | S | S | S | |
| 2024 herança africana | S | S | S | S | S | S | S | S | |
| 2025 envelhecimento | S | S | S | S | S | S | S | S | |
| 2009 PPL família | Q | Q | Q | Q | Q | Q | Q | F | sem grupo; só campanha genérica |
| 2010 PPL ajuda humanitária | Q | Q | Q | Q | Q | Q | Q | F | idem |
| 2011 PPL cultura e mudança social | Q | Q | Q | Q | Q | Q | Q | F | idem |
| 2012 PPL o grupo fortalece o indivíduo? | Q | Q | Q | Q | Q | Q | Q | F | idem, pergunta filosófica |
| 2013 PPL cooperativismo | S | S | S | S | S | S | S | S | |
| 2014 PPL rolezinhos | F | S | S | F | S | S | S | S | "garantir a oferta" cobre espaço que não existe |
| 2015 PPL valorizar o professor | S | S | S | S | S | F | S | S | K5 troca a fiscalização do piso por campanha e perde |
| 2016 PPL racismo | S | S | S | S | S | F | S | S | idem |
| 2016 3ª desperdício de alimentos | Q | Q | Q | Q | Q | Q | Q | S | sem grupo; campanha é a solução natural |
| 2017 PPL padrões de beleza | F | F | F | F | F | S | S | S | o causador é a mídia; Medida 2 acerta |
| 2018 PPL problemas econômicos | Q | Q | Q | Q | Q | Q | Q | Q | nem campanha faz sentido |
| 2019 PPL tecnologia e criança | S | S | S | S | S | S | S | S | |
| 2020 PPL falta de empatia | F | F | F | F | F | F | F | F | "supere a indiferença" quase repete o tema |
| 2021 PPL mulheres na ciência | S | S | S | S | S | S | S | S | |
| 2022 PPL insegurança alimentar | F | F | F | S | S | S | S | S | meio sem "contratação" |
| 2023 PPL situação de rua | S | S | S | S | S | S | S | S | |
| 2024 PPL arte de periferia | F | S | S | F | S | F | S | S | "garantir a oferta" cobre espaço novo |
| 2025 PPL idade mínima | S | S | S | S | S | S | S | S | |
| 2025 Pará trabalhadores rurais | F | F | F | F | F | F | S | S | valorização vem na Medida 2 |

## Frase preenchida de cada tema na versão recomendada (K6; plano B nos sem grupo)

Mostro só o miolo: [AÇÃO], [MEIO] / grupo / direito / e a Medida 2. Forma 1 tem meio "palestras, oficinas e material didático"; Forma 2 tem meio "verba federal e parceria com estados e municípios".

| Tema | Forma | Ação (K6) | Grupo / direito | Medida 2: campanha sobre | Veredito K6 |
|---|---|---|---|---|---|
| 2009 ética | 1 | incluir a ética nacional nas escolas | o cidadão / à educação | a ética nacional | F (plano B vira S) |
| 2010 trabalho | 2 | garantir a fiscalização das condições de trabalho | o trabalhador informal / ao trabalho | o trabalho na construção da dignidade humana | S |
| 2011 rede | 2 | garantir a fiscalização da privacidade de dados e imagens | o usuário / à informação | viver em rede e os limites entre o público e o privado | F |
| 2012 imigração | 2 | garantir a oferta de intérpretes nos postos de saúde | o imigrante / à saúde | o movimento imigratório para o Brasil | S |
| 2013 Lei Seca | 2 | garantir a fiscalização noturna da Lei Seca | o pedestre / à segurança | os efeitos da Lei Seca | S |
| 2014 publicidade | 2 | garantir a fiscalização dos anúncios de doces | a criança / à saúde | a publicidade infantil | S |
| 2015 mulher | 2 | garantir a oferta de delegacias com atendimento especializado | a mulher / à segurança | a violência contra a mulher | S |
| 2016 intolerância | 1 | incluir a intolerância religiosa nas escolas | o adepto de religião de matriz africana / à educação | a intolerância religiosa | S |
| 2017 surdos | 2 | garantir a oferta de intérpretes de Libras nas escolas | o aluno surdo / à educação | a formação educacional de surdos | S |
| 2018 dados | 2 | garantir a fiscalização do uso de dados | o usuário / à informação | a manipulação do comportamento pelo controle de dados | F |
| 2019 cinema | 2 | garantir a oferta de salas de cinema nos bairros | o morador da periferia / à cultura | a democratização do acesso ao cinema | S |
| 2020 mental | 2 | garantir a oferta de psicólogos nos postos | o paciente / à saúde | o estigma associado às doenças mentais | S |
| 2020 digital | 2 | garantir a oferta de especialistas nos hospitais das regiões pobres | o morador de região pobre / à saúde | as desigualdades entre as regiões | S |
| 2021 registro | 2 | garantir a oferta de cartórios de registro civil | o cidadão sem certidão / à saúde | a invisibilidade e o registro civil | S |
| 2022 povos | 2 | garantir a oferta de equipes de saúde nas aldeias | o povo indígena / à saúde | a valorização dos povos tradicionais | S |
| 2023 cuidado | 2 | garantir a oferta de creches públicas | a mulher / ao trabalho | a invisibilidade do trabalho de cuidado | S |
| 2024 herança | 1 | incluir a herança africana nas escolas | a população negra / à educação | a valorização da herança africana | S |
| 2025 envelhecimento | 2 | garantir a oferta de consultas e geriatras na rede pública | o idoso / à saúde | o envelhecimento | S |
| 2009 PPL família | plano B | campanha sobre a família contemporânea (sem grupo) | sem grupo | a família | Q (K6) / F (K7) |
| 2010 PPL ajuda | plano B | campanha sobre a ajuda humanitária | sem grupo | a ajuda humanitária | Q / F |
| 2011 PPL cultura | plano B | campanha sobre cultura e mudança social | sem grupo | cultura e mudança social | Q / F |
| 2012 PPL grupo | plano B | campanha sobre a importância do grupo para o indivíduo | sem grupo | o grupo e o indivíduo | Q / F |
| 2013 PPL cooperativismo | 2 | garantir a oferta de apoio técnico ao cooperativismo | o pequeno produtor / ao trabalho | o cooperativismo | S |
| 2014 PPL rolezinhos | 2 | garantir a oferta de espaços de lazer nas periferias | o jovem da periferia / ao lazer | os rolezinhos | S |
| 2015 PPL professor | 2 | garantir a fiscalização do pagamento do piso | o professor / ao trabalho | a valorização do professor | S |
| 2016 PPL racismo | 2 | garantir a fiscalização da lei contra discriminação nas seleções | a população negra / ao trabalho | o racismo | S |
| 2016 3ª desperdício | plano B | campanha sobre a diminuição do desperdício de alimentos nas escolas e na mídia | sem grupo | o desperdício de alimentos | Q / S |
| 2017 PPL beleza | 2 | garantir a oferta de psicólogos nos postos | a jovem / à saúde | os padrões de beleza idealizados | S |
| 2018 PPL econômicos | plano B | não preenche | sem grupo | sem núcleo claro | Q |
| 2019 PPL tecnologia | 1 | incluir o uso saudável das tecnologias nas escolas | a criança / à saúde | o uso das tecnologias por crianças | S |
| 2020 PPL empatia | 1 | incluir a empatia nas escolas | o cidadão / à educação | a falta de empatia | F |
| 2021 PPL mulheres | 2 | garantir a fiscalização da igualdade salarial | a cientista / ao trabalho | a contribuição das mulheres na ciência | S |
| 2022 PPL alimentar | 2 | garantir a oferta de programas de renda e alimentação | a família de baixa renda / à alimentação | a insegurança alimentar | S |
| 2023 PPL rua | 2 | garantir a oferta de centros de acolhida e de atendimento sem exigir endereço | a pessoa em situação de rua / à saúde | a inserção da população em situação de rua | S |
| 2024 PPL arte | 2 | garantir a oferta de espaços culturais nos bairros periféricos | o artista da periferia / à cultura | a arte de periferia | S |
| 2025 PPL idade mínima | 2 | garantir a fiscalização do trabalho infantil | a criança / à educação | a idade mínima para o trabalho | S |
| 2025 Pará rurais | 2 | garantir a oferta de médicos nos postos dos povoados | o trabalhador rural / à saúde | a valorização dos trabalhadores rurais | S |

## Casos que seguem quebrando e o que fazer (sem inventar)

Na versão recomendada (K7), nos 37 temas: **7 FORÇA e 1 QUEBRA**.

1. **Dados e privacidade (2011, 2018): FORÇA.** O direito "informação" não casa com privacidade. Sugestão, não testada na tabela: usar "segurança" (já é um dos quatro direitos da ordem do caderno) em vez de "informação". Se o aluno topar, são +2 SERVE; não contei.
2. **Ética nacional (2009): FORÇA com o grupo "o cidadão"; SERVE com o plano B.** Use o plano B.
3. **Empatia (2020 PPL): FORÇA.** O "supere a indiferença" do fecho quase repete o tema. Seguir com a frase, aceitando o risco.
4. **Temas abstratos sem grupo (família, ajuda humanitária, cultura e mudança, "o grupo fortalece o indivíduo?"): FORÇA com o plano B.** A frase fica genérica e a conclusão não amarra com um D1 que nem existiu. Não dá para transformar em SERVE com essa frase. Para esses, o que sobra é escrever conclusão livre com um agente, uma ação e um meio concretos.
5. **Problemas econômicos (2018 PPL): QUEBRA.** Nem a campanha tem sentido. Conclusão livre.
6. **Ações que o molde não escreve (nas nota 1000, 4 de 79 são "lei nova" e 3 de 79 são empresa ou ação solta; na regra estrita, mais 12 são incentivo fiscal, subsídio, vale, regulação de mercado, sanção a empresa ou salário mínimo):** a frase fixa não cobre. Não tentei encaixar. Se o D1 pedir isso, o que dá para fazer é aceitar que a Forma 2 vai dizer "verba federal" e seguir.
7. **Medida 2 fixa pode virar "coringa":** como é igual em todo tema, só o [TEMA] a distingue. Não sei medir se isso pesa na correção. Se ele preferir menos risco e menos escrita, a opção de baixo custo é **K4** (22 SERVE nos 37, 73%/58% nas nota 1000, 4 peças, 1 decisão).

## Resumo em uma linha por hipótese

H1 sobe 2, mas é pior que H2. H2 (garantir a oferta) sobe 2 e corta peças. H3 meio único sobe 1 e perde para trocar o meio da Forma 2 (+4 com H2). H4 por tipo de tema piora (−1). H4 como Medida 2 fixa com a mídia como segundo agente (H5) é o maior ganho (+5 temas, 91% largo / 76% estrito nas nota 1000). H6 pior que o buraco do D1. H7 apagar a oração do grupo e usar só campanha reduz QUEBRA de 6 para 1.
