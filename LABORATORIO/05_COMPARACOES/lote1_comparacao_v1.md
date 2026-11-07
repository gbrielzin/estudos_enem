# Comparação — Lote 1 (10 simulações)

Fonte: `04_RESULTADOS_FINANCEIROS/consolidado_lote1.md` e cada `SIM_NNN/v1.md`. Não há outras simulações armazenadas.

## Patrimônio pessoal líquido ao longo do tempo (cenário base, R$ mil)

| ID | Ano 3 (22 anos) | Ano 5 (24) | Ano 8 (27) | Ano 10 (29) | Valor da participação A10 (ilíquido) |
|---|---|---|---|---|---|
| SIM_001 | 23 | 54 | 250 | 550 | 0 |
| SIM_002 | 4 | 21 | 137 | 252 | 1.920 |
| SIM_003 | 6 | 34 | 109 | 659 | 7.350 |
| SIM_004 | 2 | 57 | -48 | 72 | 0 |
| SIM_005 | 39 | 92 | 109 | 142 | 1.275 |
| SIM_006 | 60 | 220 | 737 | 1.309 | 0 |
| SIM_007 | 20 | 84 | 173 | 915 | 9.240 |
| SIM_008 | 67 | 157 | 414 | 796 | 3.525 |
| SIM_009 | 55 | 164 | 396 | 624 | 315 |
| SIM_010 | 28 | 67 | 149 | 329 | 5.510 |

Resposta direta: aos 29 anos, **SIM_006** tem o maior patrimônio pessoal líquido e mais líquido (R$ 1,31 milhão); **SIM_007** tem o maior patrimônio ajustado (R$ 7,38 milhões), mas R$ 9,2 milhões do valor da empresa são ilíquidos. Aos 24 anos (ano 5), SIM_006 também lidera em patrimônio pessoal.

## Capital externo e ativo vendável

| ID | Capital externo/dívida relevante | Ativo vendável ao fim |
|---|---|---|
| SIM_001 | nenhum | não |
| SIM_002 | capital de giro por dívida (~R$ 0,7 mi) | sim, múltiplo baixo |
| SIM_003 | nenhum (dívida operacional pequena e quitada) | sim, SaaS |
| SIM_004 | R$ 4,3 mi de investidores + R$ 0,5 mi de dívida + aval pessoal | não (empresa encerrada) |
| SIM_005 | R$ 580 mil de financiamento do vendedor | sim, empresa de TI |
| SIM_006 | nenhum | participações minoritárias ilíquidas |
| SIM_007 | pequena dívida operacional nos anos 3-6 | sim, SaaS B2B |
| SIM_008 | financiamento imobiliário | empresa + imóveis |
| SIM_009 | nenhum | pequeno (dois produtos) |
| SIM_010 | subvenção R$ 400 mil + anjo R$ 800 mil (12%) + BNDES R$ 400 mil | sim, SaaS agrícola |

## O que uma trajetória fez que outra não fez

- **SIM_007 × SIM_004 (ambas com produto B2C):** SIM_007 percebeu LTV/CAC de ~1,9 e trocou de modelo (B2B) sem escalar gasto; SIM_004 escalou com LTV/CAC de ~0,85 usando R$ 4,3 mi de investidores. Mesmo risco de produto, decisões opostas.
- **SIM_003 × SIM_007 (ambas SaaS):** SIM_003 financiou o produto com serviços (nenhum capital externo); SIM_007 financiou com renda de emprego parcial e prejuízo operacional pequeno. SIM_003 foi mais lenta no caixa dos anos 3-8, SIM_007 teve mais recorrência.
- **SIM_001 × SIM_006 (ambas assalariadas):** SIM_006 ganhou em moeda forte e investiu em ativos de risco; SIM_001 ficou em contrato local. Diferença no ano 10: R$ 1,31 mi contra R$ 0,55 mi de patrimônio pessoal.
- **SIM_005 × SIM_002:** ambas compraram/giraram negócios existentes; SIM_005 comprou com poupança e dívida do vendedor, SIM_002 construiu pelo giro de estoque. SIM_005 tem menor risco operacional no início e menor renda disponível por anos.

## Padrões (somente nestas 10 simulações)

- **Habilidades que geraram mais renda acumulada:** inglês + programação em contrato internacional (SIM_006, R$ 1,71 mi), produto de software de nicho (SIM_007, R$ 1,64 mi), automação/IA e dados (SIM_003 e SIM_008).
- **Menos capital:** SIM_001, 003, 006, 007 e 009 não exigiram capital externo. SIM_004 exigiu o maior (R$ 4,3 mi) e foi a única a falir.
- **Melhor margem bruta:** SIM_007 (~80%), SIM_003 (~72%), SIM_010 (~62%), SIM_008 (~55%); SIM_002 (~23%) é a pior entre as empresas.
- **Mais liberdade:** SIM_006, depois SIM_007 e SIM_003 após o pivô/terceirização. Comércio (SIM_002) e consultoria (SIM_008) mantêm o fundador no centro.
- **Decisões que aumentaram o risco:** escalar sem retenção (004), capital de giro por dívida (002), dívida do vendedor (005), hardware e safra (010).
- **Combinações de maior crescimento:** serviços financiando produto (003) e produto B2C validando antes de pivotar para B2B (007).
- **Caveat:** a escala das notas e as probabilidades são julgamentos do laboratório; os números vêm de premissas explícitas, não de dados reais.
