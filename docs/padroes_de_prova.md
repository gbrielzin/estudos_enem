# Padrões de prova: onde estudar pra ganhar mais pontos

Complementa `docs/pesquisa_estrategia_de_prova.md` (o que a ciência diz sobre estudar) e a função `recorrencia_por_materia` de `core/db.py` (que só mede "em quantas provas a matéria apareceu", por matéria e contando caderno). Aqui o nível é **tópico e termo**, contando por **ano**, com o nome da questão como evidência. Todo número abaixo saiu de consultas rodadas em `core/enem.db` (somente leitura); nada foi estimado de cabeça.

## 0. Base usada e limitações (leia antes dos números)

**Base:** `origem = 'enem_oficial'`, uma prova por ano, sem contar a mesma questão duas vezes: 2019 azul, 2020 azul, 2021 azul, 2022 azul, 2023 cinza (a azul de 2023 tem só 44 questões e é o mesmo conteúdo em outra ordem), 2024 amarelo (a azul de 2024 tem 89 questões sem texto e foi ignorada), 2025 azul. Total: **621 questões** (310 de matemática, 311 de ciências da natureza), 87 a 90 por ano. Como recorrência é por ano, o máximo possível de qualquer termo é 7.

| Ano | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Questões na base | 90 | 88 | 89 | 89 | 89 | 89 | 87 |
| Com texto utilizável | 90 | 88 | 84 | 89 | 89 | 89 | 87 |

Limitações que afetam a leitura:

1. **Só matemática e ciências da natureza.** Não há Linguagens, Ciências Humanas nem Redação no banco. Nada aqui diz nada sobre metade da prova (e sobre a redação, que pesa muito na nota).
2. **Amostra de 7 provas.** Números são indícios, não taxas oficiais. Um tema que apareceu em 5 de 7 anos pode simplesmente ter tido azar de sorteio.
3. **Sem provas de reaplicação (PPL)** nem dos anos anteriores a 2019. Não dá pra saber se um tema "some" ou só não caiu nesses 7 anos.
4. **5 questões de 2021 sem texto** (`2021_azul_100`, `_106`, `_120`, `_140`, `_149`; 3 de ciências e 2 de matemática) ficam fora das análises de texto (seções 3 e 4), mas contam na seção 1.
5. **Enunciado ≠ questão inteira.** Em 159 questões (de ambas as áreas; mais em 2020, 2023, 2024 e 2025) o próprio banco avisa que figura/gráfico/tabela não foi capturado (o ENEM desenha isso como vetor). Análise por palavra-chave subconta conceitos que só aparecem na figura. Exemplo concreto: trigonometria tem 9 questões pela matéria (seção 1), mas só 2 enunciados citam "seno/cosseno/tangente".
6. **Classificação de matéria desigual entre anos** (isso distorce a seção 1):
   - 2019: 43 das 45 questões de ciências usam rótulo genérico (`quimica` 16, `biologia` 14, `fisica` 13; as outras 2 são `optica`) em vez de tópico específico, e 16 de matemática caem em `matematica_basica`.
   - 2022: 13 questões de matemática em `matematica_basica` (balde genérico).
   - 2025: **todas as 43 questões de ciências estão como `sem_video_pendente`** (ou seja, não classificadas por matéria), além de 2 de matemática (e mais 3 de matemática em 2019 e 2022).
   - Consequência: pra ciências, "em quantos anos a matéria apareceu" só é comparável entre 2020 e 2024 (5 anos). Os números de "7 anos" abaixo pra ciências vêm das palavras-chave (seções 2 e 3), não do campo `materia`.
7. **Só 34 das 621 questões têm `topico` preenchido** (ecologia 11, cinemática 7, óptica 6, fisiologia humana 5, separação de misturas 4, sistema nervoso 1). Existe `docs/proposta_topicos_biologia.md` com proposta de tópicos pra biologia/citologia; ela **não está confirmada** e é citada aqui só como proposta.

## 1. Recorrência por matéria (por ano, 7 anos)

"Média/ano" = total de questões ÷ 7. Colunas por ano na ordem 2019, 2020, 2021, 2022, 2023, 2024, 2025.

### 1.1 Matemática

| Matéria (campo `materia`) | Anos com a matéria | Total | Média/ano | Por ano |
|---|---|---|---|---|
| geometria_espacial | 7 | 36 | 5,1 | 4, 8, 6, 6, 3, 4, 5 |
| geometria_plana | 7 | 23 | 3,3 | 3, 5, 2, 1, 5, 6, 1 |
| estatistica | 7 | 22 | 3,1 | 4, 2, 6, 4, 2, 2, 2 |
| probabilidade | 7 | 15 | 2,1 | 2, 2, 1, 1, 3, 3, 3 |
| sistema_de_equacoes | 7 | 13 | 1,9 | 3, 1, 4, 1, 1, 1, 2 |
| razao_e_proporcao | 6 | 32 | 4,6 | 0, 9, 5, 5, 5, 4, 4 |
| porcentagem | 6 | 14 | 2,0 | 0, 3, 4, 1, 3, 2, 1 |
| analise_combinatoria | 6 | 12 | 1,7 | 2, 2, 1, 3, 0, 2, 2 |
| trigonometria | 6 | 9 | 1,3 | 2, 1, 2, 0, 2, 1, 1 |
| escala | 6 | 8 | 1,1 | 0, 1, 1, 2, 1, 1, 2 |
| interpretacao_de_grafico | 5 | 19 | 2,7 | 0, 3, 4, 0, 3, 4, 5 |
| raciocinio_logico | 5 | 18 | 2,6 | 0, 2, 5, 1, 7, 0, 3 |
| logaritmo | 5 | 6 | 0,9 | 2, 1, 0, 0, 1, 1, 1 |
| unidade_de_medida | 4 | 4 | 0,6 | 0, 1, 1, 0, 0, 1, 1 |
| funcao_1_grau | 3 | 7 | 1,0 | 2, 0, 0, 0, 3, 2, 0 |
| funcao_2_grau | 3 | 6 | 0,9 | 0, 0, 2, 2, 2, 0, 0 |
| progressao_aritmetica | 3 | 4 | 0,6 | 2, 1, 0, 0, 1, 0, 0 |
| funcao_exponencial | 3 | 3 | 0,4 | 0, 1, 0, 0, 1, 1, 0 |
| aritmetica | 2 | 6 | 0,9 | 0, 0, 0, 0, 0, 3, 3 |
| progressao_geometrica | 2 | 2 | 0,3 | 0, 0, 0, 0, 1, 1, 0 |
| matematica_basica (**balde genérico**) | 3 | 30 | 4,3 | 16, 0, 0, 13, 0, 1, 0 |
| sem_video_pendente / sem_classificar / marketing_digital | (não classificadas) | 7 | - | - |

Leitura: **geometria espacial, geometria plana, estatística, probabilidade e sistema de equações apareceram nos 7 anos.** Razão e proporção tem o segundo maior volume (32) e só falhou em 2019, justamente o ano em que 16 questões estão no balde `matematica_basica`; então esse "0" provavelmente é rótulo, não ausência. Os 30 de `matematica_basica` (2019 e 2022) são questões de contexto (juros, medidas, média, etc.) que não foram distribuídas; a recorrência de porcentagem, razão e estatística está **subcontada** nesses dois anos.

### 1.2 Ciências da natureza (só 2020 a 2024 são comparáveis pelo campo `materia`)

| Matéria | Anos (de 5 comparáveis) | Total | Por ano (2019 a 2025) |
|---|---|---|---|
| eletrodinamica | 5 | 13 | 0, 2, 4, 4, 1, 2, 0 |
| ecologia | 5 | 11 | 0, 3, 2, 2, 2, 2, 0 |
| biotecnologia | 5 | 8 | 0, 2, 2, 2, 1, 1, 0 |
| genetica | 5 | 8 | 0, 1, 4, 1, 1, 1, 0 |
| cinematica | 5 | 7 | 0, 2, 1, 1, 2, 1, 0 |
| estequiometria | 5 | 7 | 0, 1, 1, 1, 2, 2, 0 |
| optica | 5 (inclui 2019) | 6 | 2, 1, 0, 1, 1, 1, 0 |
| acustica | 5 | 6 | 0, 2, 1, 1, 1, 1, 0 |
| ciclos_biogeoquimicos | 5 | 5 | 0, 1, 1, 1, 1, 1, 0 |
| meio_ambiente | 4 | 8 | 0, 3, 2, 0, 2, 1, 0 |
| quimica_organica | 4 | 7 | 0, 0, 1, 1, 4, 1, 0 |
| reacoes_quimicas | 4 | 6 | 0, 1, 1, 3, 0, 1, 0 |
| dinamica | 4 | 6 | 0, 0, 1, 2, 1, 2, 0 |
| termologia | 3 | 9 | 0, 3, 3, 0, 0, 3, 0 |
| funcoes_organicas | 3 | 7 | 0, 1, 4, 0, 0, 2, 0 |
| botanica | 3 | 7 | 0, 1, 3, 0, 3, 0, 0 |
| citologia | 3 | 7 | 0, 0, 0, 3, 3, 1, 0 |
| eletroquimica | 3 | 6 | 0, 0, 3, 1, 0, 2, 0 |
| rótulo genérico (`fisica` 14, `quimica` 16, `biologia` 14) | só 2019 (+1 `fisica` em 2022) | 44 | 43 em 2019, 1 em 2022 |
| sem_video_pendente | só 2025 | 43 | 2025: 43 |

A tabela é um recorte: omite as matérias menores (por exemplo `fisiologia_humana` 5 questões em 2 anos, `zoologia`, `evolucao`, `saude_publica`, `ph_e_poh`, `radioatividade`, `sistema_endocrino`), todas com no máximo 4 anos. Quase nenhum rótulo específico de ciências aparece em 2019 (só `optica`) nem em 2025 porque esses anos estão sem classificação fina (limitação 6). Por isso a seção 2 recorre a palavras-chave.

## 2. Recorrência por tópico

### 2.1 Onde `topico` existe (34 questões, 2019 a 2024)

| Matéria / tópico | Questões (ano) | Anos distintos |
|---|---|---|
| ecologia / sucessao_secundaria | 2020_azul_127, 2024_amarelo_131 | 2 |
| ecologia / magnificacao_trofica | 2021_azul_104, 2023_cinza_114 | 2 |
| ecologia / competicao_interespecifica | 2022_azul_99, 2022_azul_132 | 1 (2 questões) |
| cinematica / mruv | 2020_azul_99, 2023_cinza_122 | 2 |
| cinematica / lancamento_horizontal | 2020_azul_113, 2022_azul_100 | 2 |
| optica / difracao | 2019_azul_132, 2023_cinza_124 | 2 |
| separacao_de_misturas / metodos_separacao_misturas | 2020_azul_123, 2022_azul_97, 2022_azul_126, 2024_amarelo_92 | 3 |
| demais (uma questão cada) | ecologia: fragmentacao_de_habitat, eutrofizacao, dispersao_de_sementes, capacidade_de_suporte, mimetismo; cinematica: lancamento_obliquo, velocidade_media_mru, composicao_de_velocidades; optica: natureza_da_luz, dispersao, espelhos_esfericos, refracao; fisiologia_humana: desnaturacao_enzimatica, bioacumulacao_tecido_adiposo, formacao_nitrosaminas, fibras_musculares, eritropoiese; sistema_nervoso: fotorrecepcao | 1 |

Com 34 questões e 7 anos, **nenhum tópico se repete em mais de 3 anos**; a base de tópicos é fina demais pra falar em "tópico que sempre cai". O que se vê é a *matéria* ecologia (11 questões em 5 anos) repetindo com tópicos diferentes cada vez, o que combina com o registro em `pesquisa_estrategia_de_prova.md` sobre padrão repetido em ecologia.

**Proposta (não confirmada)** de `docs/proposta_topicos_biologia.md`, só como pista: respiracao_celular (2019_azul_127, 2022_azul_127, 2023_cinza_108), membrana_transporte (2019_azul_130, 2022_azul_114), controle/ecologia diversos em 2019. Confiança "alta" segundo o próprio documento em parte dessas linhas; tratar como hipótese até o usuário confirmar.

### 2.2 Onde `topico` é NULL: agrupamento aproximado por palavra-chave

**Isto é aproximação.** Cada questão de ciências com texto (308) foi colocada no *primeiro* grupo cuja lista de palavras aparece no enunciado (ordem de prioridade fixa). Teste de sanidade: nas 233 questões que já têm uma `materia` específica de biologia/química/física, a área (bio/quí/fís) do agrupamento coincidiu com a do rótulo em **164 (70%)**. Os 30% de discordância podem ser erro do agrupamento ou do rótulo; por isso use o resultado como mapa grosso, não como classificação.

| Grupo (aproximado) | Total | Anos com o grupo | Por ano (2019 a 2025) |
|---|---|---|---|
| bio: fisiologia / saúde humana (vacina, hormônio, sangue, doença, parasita) | 49 | 7 | 8, 3, 6, 10, 7, 8, 7 |
| bio: ecologia / meio ambiente (espécie, poluição, cadeia, bioacumulação) | 40 | 7 | 6, 8, 6, 4, 5, 6, 5 |
| bio: citologia / metabolismo celular (célula, membrana, ATP, enzima) | 35 | 7 | 4, 8, 3, 6, 7, 5, 2 |
| qui: orgânica / polímeros | 24 | 7 | 3, 2, 5, 4, 3, 3, 4 |
| fís: ondas / óptica / acústica | 22 | 7 | 3, 5, 3, 2, 5, 2, 2 |
| qui: ligações / propriedades / separação de misturas | 22 | 7 | 3, 5, 3, 4, 1, 3, 3 |
| fís: mecânica (cinemática, dinâmica, energia) | 20 | 7 | 4, 2, 1, 3, 4, 4, 2 |
| fís: eletricidade / magnetismo | 19 | 7 | 4, 3, 2, 4, 1, 2, 3 |
| qui: estequiometria / soluções / gases | 19 | 7 | 1, 1, 2, 2, 7, 2, 4 |
| qui: eletroquímica / oxirredução | 15 | 5 | 0, 2, 4, 4, 0, 1, 4 |
| bio: genética / biotecnologia | 12 | 7 | 1, 1, 2, 1, 2, 2, 3 |
| bio: evolução / botânica / zoologia | 11 | 6 | 3, 0, 3, 1, 1, 2, 1 |
| qui: ácido-base / equilíbrio / cinética | 9 | 5 | 2, 2, 0, 0, 1, 2, 2 |
| não classificado (nenhuma palavra bateu) | 8 | 6 | 1, 1, 2, 0, 1, 2, 1 |
| fís: termologia | 2 | 1 | 2, 0, 0, 0, 0, 0, 0 |

Resumo por grande área (mesmo método, mesmas ressalvas; 1 questão ficou em "energia geral"): biologia 147, química 89, física 63 de 308. Por ano, biologia fica entre 18 e 23 questões (de 2019 a 2025: 22, 20, 20, 22, 22, 23, 18); química vai de 9 (2019) a 17 (2025); física de 6 (2021) a 13 (2019). A "termologia" quase não aparece como grupo porque calor/temperatura foram absorvidos por grupos anteriores na ordem de prioridade (um artefato do método, não ausência do tema; a seção 3 mostra calor/temperatura em 45 questões).

### 2.3 Matemática por tópico

Vale a tabela da seção 1.1 (a `materia` de matemática já funciona como tópico). O único problema é o balde `matematica_basica` (30 questões em 2019 e 2022, mais 7 outras sem classificação): tentei redistribuí-lo por palavras-chave e o resultado ficou ruidoso demais pra publicar, então **não há redistribuição**; tratar razão, porcentagem e estatística de 2019 e 2022 como subcontadas.

## 3. Termos e conceitos frequentes nos enunciados

Método: lista curada de termos técnicos (partindo de unigramas e bigramas frequentes sem stopwords do português, depois filtrando palavras genéricas como "quantidade", "processo", "adaptado") contados por **questão distinta** e por ano. Uma questão conta uma vez por termo, mesmo que o termo apareça vários trechos. Marcas d'água do PDF, URLs e o aviso de figura ausente foram removidos antes de contar. Regexes cobrem variações (por exemplo "célula/células"), mas termos só presentes na figura não são vistos (limitação 5).

### 3.1 Ciências da natureza (308 questões com texto)

| Termo / conceito | Questões distintas | Anos | Por ano (2019 a 2025) |
|---|---|---|---|
| água (H2O) | 76 | 7 | 10, 17, 7, 11, 8, 10, 13 |
| calor / temperatura | 45 | 7 | 7, 9, 5, 6, 7, 4, 7 |
| agrotóxico / poluente / resíduo / esgoto | 43 | 7 | 5, 10, 6, 4, 6, 8, 4 |
| velocidade / aceleração | 41 | 7 | 7, 6, 4, 5, 9, 5, 5 |
| corrente elétrica / resistência / tensão / circuito | 37 | 7 | 5, 3, 6, 8, 3, 6, 6 |
| concentração / solução / soluto | 37 | 7 | 3, 7, 4, 9, 8, 3, 3 |
| ácido / base / neutralização | 36 | 7 | 8, 2, 5, 8, 3, 5, 5 |
| oxidação / redução (redox) | 33 | 7 | 5, 3, 5, 6, 5, 4, 5 |
| gás / pressão | 33 | 7 | 2, 10, 2, 3, 7, 4, 5 |
| célula(s) | 31 | 7 | 5, 4, 2, 7, 6, 6, 1 |
| espécie(s) | 27 | 7 | 4, 2, 3, 2, 6, 5, 5 |
| oxigênio (O2) | 27 | 7 | 5, 4, 2, 5, 4, 3, 4 |
| ecossistema / meio ambiente | 25 | 7 | 3, 9, 3, 2, 4, 1, 3 |
| vírus / bactéria / microrganismo / patógeno | 23 | 7 | 1, 3, 1, 7, 3, 6, 2 |
| combustível fóssil / petróleo | 22 | 7 | 3, 4, 5, 1, 3, 4, 2 |
| ligação (iônica/covalente/H) / polaridade | 20 | 6 | 4, 3, 0, 2, 5, 1, 5 |
| enzima / catalisador | 20 | 6 | 3, 3, 0, 4, 4, 4, 2 |
| radiação / radioatividade / meia-vida | 19 | 7 | 2, 2, 3, 3, 2, 1, 6 |
| hidrocarboneto / carbono / cadeia carbônica | 19 | 6 | 4, 5, 2, 1, 4, 3, 0 |
| sangue / hemoglobina | 17 | 7 | 3, 1, 1, 3, 4, 3, 2 |
| onda / frequência / comprimento de onda | 17 | 6 | 0, 4, 1, 4, 5, 1, 2 |
| genes / cromossomos / mutação / alelo | 17 | 7 | 1, 1, 3, 3, 4, 4, 1 |
| equação / reação química | 17 | 7 | 2, 3, 2, 2, 2, 2, 4 |
| densidade | 17 | 7 | 2, 5, 4, 2, 1, 1, 2 |
| mol / massa molar | 14 | 6 | 2, 2, 0, 2, 3, 2, 3 |
| gravidade / órbita / satélite | 14 | 7 | 5, 1, 1, 4, 1, 1, 1 |
| CO2 (gás carbônico) | 14 | 7 | 1, 3, 1, 1, 3, 3, 2 |
| luz / refração / reflexão / lente / difração | 13 | 7 | 1, 3, 1, 1, 2, 3, 2 |
| eletrólise / pilha / eletrodo / bateria | 13 | 6 | 1, 2, 4, 2, 0, 3, 1 |
| álcool / etanol / biocombustível | 13 | 6 | 2, 1, 4, 2, 0, 3, 1 |
| proteína | 12 | 6 | 3, 0, 1, 3, 2, 2, 1 |
| membrana | 12 | 7 | 3, 1, 1, 2, 2, 2, 1 |
| força / atrito / torque / empuxo | 12 | 6 | 3, 0, 1, 4, 2, 1, 1 |
| polímero / plástico | 11 | 7 | 1, 3, 2, 1, 1, 2, 1 |
| som / acústica / decibel | 10 | 6 | 0, 1, 1, 1, 2, 3, 2 |
| potência / energia elétrica (kWh) | 10 | 7 | 2, 2, 1, 1, 1, 1, 2 |
| pH | 10 | 6 | 1, 2, 2, 3, 0, 1, 1 |
| evolução / seleção natural | 9 | 6 | 1, 0, 3, 1, 1, 2, 1 |
| DNA / RNA | 9 | 5 | 1, 0, 2, 3, 2, 1, 0 |
| campo magnético / indução | 7 | 6 | 2, 1, 1, 1, 1, 0, 1 |
| mitocôndria | 6 | 5 | 1, 0, 0, 1, 1, 2, 1 |
| fotossíntese / cloroplasto | 6 | 3 | 0, 3, 1, 0, 2, 0, 0 |
| calor específico / calorimetria | 5 | 3 | 2, 1, 0, 2, 0, 0, 0 |
| equilíbrio químico | 4 | 4 | 0, 0, 0, 1, 1, 1, 1 |
| ATP | 4 | 3 | 2, 0, 0, 1, 1, 0, 0 |
| efeito estufa / camada de ozônio / chuva ácida (nome explícito) | 4 | 3 | 0, 0, 0, 1, 1, 0, 2 |

Bigramas técnicos que se repetem (questões / anos): "equação química" 10/6, "massa molar" 8/6, "corrente elétrica" 8/5, "seres vivos" 8/6, "campo magnético" 7/6, "energia elétrica" 6/5, "reação química" 5/5, "energia térmica" 5/4, "ácido base" 4/4, "solução aquosa" 4/4, "combustíveis fósseis" 4/4, "equilíbrio químico" 4/4, "vasos sanguíneos" 4/4, "calor específico" 4/3.

**Vocabulário-base provável** (aparece nos 7 anos e é técnico, não só palavra comum): **pH e ácido/base, redox (oxidação/redução, pilha), concentração e mol, polaridade e ligações, catalisador/enzima, radiação e meia-vida, corrente/resistência/potência, onda/frequência, densidade, célula e membrana, genes/mutação, microrganismos, poluentes e bioacumulação, combustíveis e biocombustíveis, calor e temperatura**. Sobre siglas: ATP (4 questões, 3 anos), DNA/RNA (9, 5 anos) e pH (10, 6 anos) aparecem, mas em pouca quantidade absoluta; a sigla sozinha não garante que o assunto é o mais importante, só que o vocabulário pode aparecer.

### 3.2 Matemática (308 questões com texto)

| Termo / conceito | Questões distintas | Anos | Por ano (2019 a 2025) |
|---|---|---|---|
| gráfico / tabela / quadro | 86 | 7 | 14, 14, 14, 10, 12, 12, 10 |
| mínimo / máximo / menor custo/preço (otimização) | 61 | 7 | 12, 6, 9, 9, 6, 9, 10 |
| triângulo / círculo / retângulo / quadrado | 60 | 7 | 5, 12, 8, 7, 7, 14, 7 |
| porcentagem / percentual / % | 54 | 7 | 10, 9, 8, 7, 7, 9, 4 |
| escala / unidade de medida (cm, km, m²) | 50 | 7 | 7, 10, 6, 3, 6, 10, 8 |
| volume / capacidade / litros | 48 | 7 | 7, 7, 7, 6, 7, 6, 8 |
| velocidade / distância / tempo | 46 | 7 | 3, 8, 3, 7, 9, 5, 11 |
| juros / desconto / preço / custo / lucro | 42 | 7 | 6, 4, 11, 4, 5, 8, 4 |
| cilindro / cone / esfera / prisma / pirâmide | 36 | 7 | 2, 7, 3, 7, 4, 5, 8 |
| média / mediana / moda / desvio padrão | 32 | 7 | 3, 5, 7, 5, 5, 2, 5 |
| área | 29 | 7 | 3, 4, 2, 4, 5, 8, 3 |
| razão / proporção / regra de três | 26 | 7 | 6, 3, 3, 3, 4, 4, 3 |
| função (1º/2º grau, exponencial, log) | 20 | 7 | 4, 2, 2, 3, 5, 3, 1 |
| probabilidade / chance | 18 | 7 | 2, 2, 1, 3, 4, 3, 3 |
| combinatória (anagrama, combinação, "de quantas maneiras") | 9 | 6 | 2, 1, 1, 2, 0, 2, 1 |

Bigramas de matemática (questões / anos): "nessas condições" 15/6, "quantidade mínima" 10/6, "circular reto" 8/5 (cilindro), "metro quadrado" 7/5, "diretamente proporcional" 6/5, "paralelepípedo reto" 6/5, "cilindro circular" 6/4, "projeção ortogonal" 5/4, "triângulo equilátero" 5/4, "inversamente proporcional" 4/4.

Leitura: em matemática o que se repete é menos "fórmula" e mais **cenário**: compra, preço, custo mínimo, consumo, medidas de recipientes, leitura de gráfico/tabela. Isso sugere que interpretação de texto + unidades pesa tanto quanto o conteúdo. Os termos de regex de "mínimo/máximo" e "gráfico/tabela" são amplos (podem pegar a palavra em contexto não matemático); considerar como indício de estilo, não de tema.

## 4. Cadeias de conceito repetidas em anos diferentes

Critério: mesmo mecanismo em questões de anos diferentes, verificado lendo o trecho do enunciado (não só a palavra-chave). "Anos" = anos distintos. Nomes de questão seguem `ano_caderno_número`.

| # | Mecanismo / cadeia | Questões (evidência) | Anos | Observação |
|---|---|---|---|---|
| 1 | **Cadeia respiratória, gradiente de prótons, ATP sintase, desacoplador/inibidor** (calor ou falta de ATP como consequência) | 2019_azul_127 (desacoplador DNP na mitocôndria), 2022_azul_127 (termogenina impede prótons de chegar à ATP sintetase, gera calor), 2023_cinza_108 (cianeto inibe a cadeia, gradiente de prótons) | 2019, 2022, 2023 | Mesmo mecanismo, três cenários (emagrecedor, urso, veneno). Confirmado o caso já observado pelo usuário. |
| 2 | **Indução eletromagnética: campo magnético variável gera corrente**, depois efeito Joule | 2019_azul_92 (linhas de alta tensão induzem corrente em cerca), 2020_azul_98 (gerador, fluxo magnético variável), 2023_cinza_93 (fogão por indução, corrente induzida na panela, calor por efeito Joule), 2025_azul_122 (fogão por indução, campo magnético variável, aquece por efeito Joule) | 2019, 2020, 2023, 2025 | 2023 e 2025 são o **mesmo cenário** (fogão por indução). |
| 3 | **Potência elétrica / efeito Joule / energia dissipada em resistência** | 2021_azul_128 (carregador: tensão, corrente, kWh), 2022_azul_116 (chuveiro: potência dissipada aquece a água, calor específico, disjuntor), 2023_cinza_93, 2025_azul_122 | 2021, 2022, 2023, 2025 | Ligada à cadeia 2 e à calorimetria (calor específico da água aparece em 2022_azul_116 e 2020_azul_128). |
| 4 | **Poluente apolar/lipossolúvel: acumula em gordura ou tecido e sobe a cadeia** (polaridade explica o destino) | 2019_azul_123 (estrôncio-90 acumula em cadeias), 2023_cinza_96 (contaminante acumulado nos tecidos do vegetal), 2023_cinza_114 (aldrin, baixa polaridade, magnificação), 2024_amarelo_128 (poluentes apolares se acumulam em tecido adiposo), 2025_azul_134 (baixa polaridade, pouca solubilidade em água) | 2019, 2023, 2024, 2025 | Junta química (polaridade/solubilidade) com ecologia (magnificação). 2021_azul_104 também tem tópico `magnificacao_trofica`. |
| 5 | **Petróleo/óleo derramado sobre aves: penas encharcadas, perda de flutuação** | 2020_azul_104 (aves lavadas com detergente, precisam recuperar flutuação), 2025_azul_93 (aves com dificuldade de flutuação por encharcamento das penas) | 2020, 2025 | Cenário praticamente repetido; ligado a polaridade/detergente (também 2019_azul_122, "sabonete" como tensoativo). |
| 6 | **Equilíbrio químico: deslocamento/constante** | 2022_azul_107 (função do H+, deslocar equilíbrio, constante), 2023_cinza_134 (dissolução por deslocamento do equilíbrio), 2024_amarelo_94 (equilíbrio e desmineralização do esmalte), 2025_azul_117 (favorecer formação de TiCl4 por pressão, equilíbrio químico) | 2022, 2023, 2024, 2025 | Quatro anos seguidos; antes de 2022 não apareceu com o nome no texto. |
| 7 | **Meia-vida / decaimento exponencial** | 2020_azul_150 (carbono 14, matemática), 2021_azul_95 (meia-vida de pesticida no solo), 2022_azul_109 (decaimento do iodo-131), 2025_azul_110 (radioisótopo, meia-vida 5,3 anos), 2019_azul_123 (radionuclídeos) | 2019, 2020, 2021, 2022, 2025 | Aparece em química, física e matemática (função exponencial). |
| 8 | **Bateria/pilha: reação nos eletrodos, força eletromotriz** | 2019_azul_118 (bateria zinco-ar, espécie formada no ânodo), 2021_azul_102 (montagem que alimenta cronômetro), 2021_azul_133 (pilhas de lítio-iodo em série, potencial padrão), 2022_azul_119 (pilhas em série com resistência interna, física) | 2019, 2021, 2022 | Eletroquímica e eletrodinâmica se tocam nesse ponto. |
| 9 | **Fenômeno ondulatório a identificar: difração/interferência/ressonância** | 2019_azul_132 (difração na pupila), 2020_azul_111 (interferência em fone com cancelamento), 2022_azul_135 (luz engarrafada, difração), 2023_cinza_124 (espalhamento por difração), 2025_azul_114 (reflexão/ressonância/timbre) | 2019, 2020, 2022, 2023, 2025 | Pergunta do tipo "qual fenômeno explica" repete. |
| 10 | **Acústica: frequência, ressonância, velocidade do som** | 2020_azul_114, 2021_azul_92, 2022_azul_134, 2023_cinza_112, 2023_cinza_123, 2024_amarelo_117 (Doppler), 2025_azul_114 | 2020 a 2025 (6 anos) | Matéria `acustica` tem 6 questões em 5 anos; aqui somam-se ondas, radar e acústica. |
| 11 | **Separação de misturas** (destilação, decantação, filtração, extração) | 2019_azul_112 (destilação fracionada do petróleo), 2020_azul_123, 2022_azul_97, 2022_azul_126 (etapas de tratamento de água), 2024_amarelo_92 | 2019, 2020, 2022, 2024 | Já tem tópico `metodos_separacao_misturas` em 4 dessas. |
| 12 | **Catalisador/energia de ativação/velocidade da reação** | 2020_azul_110, 2022_azul_107, 2022_azul_120 (enzima catalase e temperatura), 2024_amarelo_101 | 2020, 2022, 2024 | Enzima é o caso biológico do mesmo conceito. |
| 13 | **Osmose / meio hipotônico** | 2019_azul_130 (sal em batata, osmose), 2022_azul_114 (epiderme em meio hipotônico) | 2019, 2022 | Só 2 anos; fraco. |
| 14 | **Eutrofização / oxigênio dissolvido / poluição da água** | 2020_azul_119 (OD e DBO), 2024_amarelo_127 (urbanização causa eutrofização), 2025_azul_111 (eutrofização como alternativa em questão sobre descarte) | 2020, 2024, 2025 | Também aparece como alternativa errada, junto de chuva ácida e camada de ozônio. |
| 15 | **Chuva ácida e óxidos de nitrogênio/enxofre** | 2020_azul_132, 2022_azul_129 (chuva ácida interfere no ciclo do nitrogênio), 2023_cinza_102 (alternativa "produção de chuva ácida"), 2024_amarelo_123 (óxidos de nitrogênio, fumaça fotoquímica), 2025_azul_111 | 2020, 2022, 2023, 2024, 2025 | Costuma entrar como distrator ou contexto, nem sempre é o foco. |
| 16 | **Biotecnologia/vírus: vacina, RNA, PCR, transgênico** | verificar caso a caso; agrupamento por palavra-chave deu 9 questões em 6 anos (transgênico/PCR/clonagem) e 12 em 7 anos (vírus/vacina/anticorpo) | 6 e 7 | **Não verificado questão a questão** neste documento; tratar como pista. |

O que unifica as cadeias 4, 5, 14 e 15: **poluição/ambiente vira pergunta de química** (polaridade, solubilidade, acidez), e a resposta depende de saber o mecanismo, não só o nome do problema.

## 5. Distribuição de gabaritos (curiosidade estatística)

Contagem sobre as 621 questões da base (uma prova por ano). **Isto não é um método pra chutar**: cada prova é montada de forma independente, e com 621 questões a distribuição observada é compatível com uniforme. O teste de qui-quadrado deu 6,4 com 4 graus de liberdade (o valor crítico convencional a 5% é 9,49), então não há evidência de letra favorecida.

| Ano | A | B | C | D | E | Total |
|---|---|---|---|---|---|---|
| 2019 | 17 | 17 | 19 | 19 | 18 | 90 |
| 2020 | 14 | 15 | 26 | 21 | 12 | 88 |
| 2021 | 12 | 21 | 21 | 19 | 16 | 89 |
| 2022 | 17 | 18 | 20 | 17 | 17 | 89 |
| 2023 | 17 | 18 | 19 | 19 | 16 | 89 |
| 2024 | 17 | 18 | 20 | 18 | 16 | 89 |
| 2025 | 15 | 18 | 18 | 19 | 17 | 87 |
| **Total** | **109** | **125** | **143** | **132** | **112** | **621** |

Por área: matemática 54, 63, 77, 60, 56 (A a E; total 310); ciências 55, 62, 66, 72, 56 (total 311). A maior sequência de gabarito igual em questões consecutivas dentro da mesma área e ano foi 3 (4 em 2022). O único ano com distribuição bem irregular é 2020 (26 letras C contra 12 letras E), o que é típico de variação aleatória em 88 questões, sem valor preditivo.

## 6. Hipóteses de priorização

Sete provas é amostra pequena: tudo abaixo é **indício**, não taxa oficial de incidência. Nível de evidência = quão consistente é o padrão nos dados, não certeza de que cairá em 2026.

| # | Hipótese | Evidência | Motivo |
|---|---|---|---|
| 1 | Matemática: estudar geometria espacial, geometria plana, estatística, probabilidade e sistemas de equações primeiro; e razão/proporção/porcentagem junto | **Forte** | Os 5 primeiros apareceram nos 7 anos (seção 1.1); razão/proporção (32 questões) e porcentagem (14) só "faltam" onde existe o balde genérico de 2019. Geometria espacial é a maior: 36 em 7 anos, entre 3 e 8 por ano. |
| 2 | Treinar leitura de gráfico/tabela e problemas de contexto de compra, custo, consumo e medidas (interpretação + unidades) | **Média** | Termos de "gráfico/tabela" em 86 e de preço/custo/juros em 42 enunciados, todos os anos; mas a regex é ampla e parte do contexto vem de figura não capturada. |
| 3 | Ciências: biologia é o bloco mais estável por ano (18 a 23 questões estimadas de 45), e dentro dela **ecologia/meio ambiente, fisiologia/saúde e celular/metabolismo** aparecem nos 7 anos | **Média** | Números vêm de agrupamento por palavra-chave, com 70% de concordância com o rótulo existente (seção 2.2). Forte na constância, fraca na precisão do agrupamento. |
| 4 | Vocabulário-base químico: pH/ácido-base, redox/pilha, mol e concentração, polaridade/solubilidade, catalisador, meia-vida | **Média** | Cada termo aparece nos 6 ou 7 anos (seção 3.1) e várias cadeias verificadas a olho (4, 6, 7, 8, 12) confirmam que é mecanismo, não só palavra. Equilíbrio químico é 4 anos seguidos (2022 a 2025) mas com só 4 questões. |
| 5 | Física: eletricidade/magnetismo (indução, efeito Joule, potência), ondas/acústica e cinemática | **Média** | Indução e Joule em 6 e 8 questões (seção 4, cadeias 2 e 3), acústica em 6 dos 7 anos; a física é o bloco menor (63 de 308 estimadas). |
| 6 | Estudar mecanismo completo, não só definição: cadeia respiratória (2019, 2022, 2023), indução (2019, 2020, 2023, 2025), poluente apolar que acumula em gordura (2019, 2023, 2024, 2025) | **Média** | Cadeias verificadas leitura a leitura com 3 a 4 anos; a repetição é do mecanismo em cenário novo, então decorar exemplos não basta (o que combina com a nota de padrão repetido em `pesquisa_estrategia_de_prova.md`). |
| 7 | Poluição/ambiente como ponte química-biologia (chuva ácida, eutrofização, agrotóxico, petróleo) merece bloco próprio | **Fraca** | Termos de poluente/resíduo em 43 questões nos 7 anos, mas muitas vezes como distrator (2025_azul_111) ou contexto; o foco cobrado varia. |
| 8 | Não priorizar tema por ter "sumido": tópicos com 1 a 2 anos (fotossíntese, osmose, ATP) podem só ter caído menos nesta amostra | **Fraca** | Com 7 provas e classificação fina incompleta (só 34 tópicos, 2019 e 2025 sem matéria específica em ciências), "não caiu" é ausência de dado tanto quanto ausência de tema; **falta dado de Linguagens, Humanas e Redação, PPL e anos anteriores a 2019**. |

Próximos passos que aumentariam a confiança (nenhum feito aqui): classificar as 43 questões de 2025 e as 44 de 2019 por matéria, redistribuir `matematica_basica`, confirmar `proposta_topicos_biologia.md` e carregar provas de 2009 a 2018 e reaplicações (a pesquisa já registra 2009 como virada de matriz).
