# Pesquisa: redação do ENEM (correção, notas altas, modelo pronto)

Começada em 2026-09-25. Objetivo: entender como a redação é corrigida de verdade, o que as redações nota 1000 têm em comum e onde o "modelo coringa" ajuda ou atrapalha — base pra treinar e, no futuro, pra uma correção por IA que imite o corretor humano.

## Material coletado

`cartilhas/` (fora do git, só consulta local): Cartilha do Participante do INEP de **2019, 2022, 2023, 2024, 2025 e 2026** em PDF e em texto extraído (`.txt`). Cada uma traz a matriz de referência, as 5 competências e **redações nota 1000 comentadas pelo INEP** (blocos "COMENTÁRIO"). A de 2026 baixada é a versão para participantes surdos (`cartilha_enem_2026_da.pdf`); falta a versão geral de 2026. Faltam 2020 e 2021 (links antigos deram 404).

## Como a correção funciona

- Cada redação é corrigida por **dois corretores independentes**. Cada um dá de 0 a 200 em cada uma das **5 competências** (em degraus de 40), somando até 1000. A nota final é a **média** dos dois.
- **Discrepância**: diferença maior que **100 pontos no total** ou maior que **80 pontos em qualquer competência** → vai pra um **terceiro corretor**. Se ainda assim não resolver, uma **banca** (supervisor + 2) dá a nota final.
- **Ritmo**: um corretor corrige de **50 a 100 redações por dia** (até 150), durante uns dois meses. Na prática são poucos minutos por texto — o corretor reconhece rápido estrutura, tese e proposta; o que não está claro na leitura rápida tende a não pontuar.

## Tendência recente: a correção ficou mais dura no repertório

| Edição | Redações nota 1000 |
|---|---|
| 2023 | 60 |
| 2024 | 12 |
| 2025 | **10** (menor da série histórica) |

- Em 2025 a média nacional da redação caiu ~6%, e a **Competência 2** (tema, repertório sociocultural, tipo textual) foi a que mais caiu: **−11,1%** em relação a 2024.
- A **cartilha de 2025** usa como exemplo negativo o conceito de "instituições zumbis", do Bauman, aplicado sem explicação — chama isso de enfeite teórico e de **"repertório de bolso"**. Orientação: explicar o conteúdo citado e articular com a tese.
- A **cartilha de 2026** dá nome oficial: **"repertório memorizado"**. Memorizar **não é problema em si**; o problema é inserir a referência decorada em qualquer tema, sem ligação com a tese e sem explicar — aí ela parece artificial e não faz o texto progredir.

## O que isso quer dizer pro "modelo coringa"

| Parte do modelo | Risco | O que fazer |
|---|---|---|
| Estrutura fixa (intro → D1 → D2 → conclusão) | **Baixo.** A cartilha não pune estrutura previsível | Manter |
| Repertório fixo (ex.: Constituição, Bauman) usado em todo tema | **Alto em C2/C3** desde 2025 | Ter um **banco de repertórios por eixo temático** e, em cada um, uma frase que **explica** a referência e a **liga ao recorte** do tema |
| Tese genérica ("é preciso refletir...") | Alto em C2/C3 | Tese com o **recorte exato** da proposta + os 2 motivos que vão virar D1 e D2 |
| Proposta de intervenção genérica | Médio em C5 | 5 elementos (agente, ação, meio, finalidade, detalhamento) **ligados aos problemas dos D1 e D2** |

**Calibragem da nota:** correção de plataforma/professor pode ser mais generosa que a do INEP, principalmente em C2 (é comum a nota oficial vir bem abaixo da nota dos treinos). Antes de contar com a nota dos treinos no planejamento, vale corrigir redações novas **contra os comentários das cartilhas** (o padrão do INEP), competência por competência.

## Ideia: correção por IA que imita o corretor humano

1. **Dois "corretores" independentes** (duas chamadas separadas, sem ver a nota do outro), cada um dando 0-200 por competência em degraus de 40 e justificando com a grade da cartilha.
2. **Regra de discrepância do INEP**: se diferirem >100 no total ou >80 numa competência, chamar um terceiro.
3. **Calibrar com as redações nota 1000 das cartilhas** (devem dar 1000) e com redações de nota conhecida, pra medir se a IA está generosa ou rigorosa.
4. Leitura "rápida" como o corretor: primeiro julgar pelo que salta aos olhos (tese, tópicos frasais, repertório explicado, proposta completa), depois o detalhe.

## Pendências

- Relatos de quem tirou 900+ com modelo (Reddit/YouTube): a busca não trouxe fonte confiável; tentar busca direta em fóruns e canais de professores.
- Extrair cada redação nota 1000 das cartilhas pra um arquivo próprio (tema, ano, parágrafos, repertórios usados) e mapear padrões: tipo de repertório, como a tese é escrita, tamanho, conectivos.
- Baixar a versão geral da cartilha 2026.

## Fontes

- Cartilha 2025 (INEP): https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_no_enem_2025_cartilha_do_participante.pdf
- Cartilha 2026, página do INEP: https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/a-redacao-do-enem-2026-cartilha-do-a-participante
- Processo de correção (INEP): https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/conheca-o-processo-de-correcao-das-redacoes
- Discrepância e ritmo dos corretores: https://www.otempo.com.br/enem/2025/2025/11/14/quem-corrige-a-redacao-do-enem-saiba-criterios · https://www.cnnbrasil.com.br/educacao/redacao-do-enem-perguntas-e-respostas-sobre-a-correcao/
- Nota 1000 por ano e queda da C2: https://www.otempo.com.br/educacao/2026/6/23/enem-2025-redacoes-nota-1-000-despencam-e-atingem-menor-marca-da-serie-historica-veja-os-numeros · https://projetomedicina.com.br/noticias/enem-2025-10-notas-mil-redacao-microdados-inep/ · https://www.cnnbrasil.com.br/educacao/levantamento-indica-queda-de-6-nas-notas-de-redacao-do-enem-em-2025/
