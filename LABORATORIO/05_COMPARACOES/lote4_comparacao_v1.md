# Comparação — Lote 4 (startups em nichos diferentes, apostas em estágios)

Fonte: `SIM_021..029/v1.md`, `06_RANKINGS/ranking_v4_29_simulacoes.md`, `04_RESULTADOS_FINANCEIROS/consolidado_lote4.md`. Todas usam a regra corrigida de valor patrimonial (valor da empresa − dívida líquida) e dividendos proporcionais à participação.

## Premissa nova do personagem
Personagem racional: testa 3 apostas baratas, define o critério de abandono antes, mantém o emprego até a empresa se sustentar e só então reduz a dedicação ao salário. Os Lotes 1 a 3 exploraram também caminhos mais arriscados (por exemplo SIM_004, tudo em uma aposta com capital de terceiros e aval pessoal) e continuam válidos como contraste.

## Resultados por nicho (cenário base, R$ mil)

| ID | Nicho | Patrimônio ajustado (pess./base/otim.) | Pessoal líquido A10 | Menor patrimônio pessoal no caminho | Renda mensal A10 | Prob. subjetiva |
|---|---|---|---|---|---|---|
| SIM_021 | LegalTech: contratos e compliance para escritórios pequenos | 1.924 / 5.923 / 12.649 | 317 | 3 | 26.8 | 30% |
| SIM_022 | HRTech: onboarding e benefícios para PMEs | 937 / 3.392 / 7.545 | 197 | -1 | 11.9 | 25% |
| SIM_023 | Construtech: orçamento e gestão de obras para construtoras pequenas | 1.283 / 4.307 / 9.470 | 179 | 3 | 11.9 | 25% |
| SIM_024 | FoodTech abandonada no portão (perda limitada) | 44 / 183 / 338 | 183 | 3 | 12.5 | 45% |
| SIM_025 | CyberTech: segurança e adequação à LGPD para PMEs | 1.028 / 3.654 / 8.127 | 179 | 3 | 11.9 | 25% |
| SIM_026 | CleanTech: software para instaladoras de energia solar | 1.051 / 3.629 / 8.087 | 187 | 3 | 11.9 | 20% |
| SIM_027 | InsurTech: CRM e cotação para corretores de seguros | 2.063 / 6.379 / 13.635 | 331 | 3 | 23.5 | 25% |
| SIM_028 | Hospitality: gestão de receita para pousadas | 707 / 2.718 / 6.140 | 135 | 3 | 11.0 | 30% |
| SIM_029 | FinTech B2B para PMEs, refeita com portões de decisão | 2.305 / 6.007 / 12.360 | 289 | 3 | 21.3 | 20% |

O pior ano de patrimônio pessoal nas nove simulações fica entre −R$ 1 mil (SIM_022) e R$ 3 mil, contra −R$ 75 mil na SIM_004 (falência e aval) e −R$ 64 mil na SIM_012 (ano nos EUA). Esse é o efeito de manter o salário e limitar o custo de cada aposta.

## Valor esperado ilustrativo: em estágios × tudo em uma aposta

Mesma probabilidade de sucesso `p` (estimativa subjetiva do laboratório) para os dois estilos. Desfecho de fracasso do estilo em estágios: SIM_024 (parou no portão), patrimônio ajustado R$ 183 mil. Desfecho de fracasso de tudo em uma aposta: SIM_004, R$ 72 mil. A coluna 'em estágios, p reduzida' assume que parar cedo reduz em 20% a chance relativa de chegar ao sucesso (pessimista para o estilo em estágios).

| ID | p | Sucesso (base) | VE em estágios | VE em estágios, p×0,8 | VE tudo em uma aposta |
|---|---|---|---|---|---|
| SIM_021 | 30% | 5.923 | 1.905 | 1.561 | 1.827 |
| SIM_022 | 25% | 3.392 | 985 | 825 | 902 |
| SIM_023 | 25% | 4.307 | 1.214 | 1.008 | 1.131 |
| SIM_025 | 25% | 3.654 | 1.051 | 877 | 967 |
| SIM_026 | 20% | 3.629 | 872 | 735 | 783 |
| SIM_027 | 25% | 6.379 | 1.732 | 1.422 | 1.649 |
| SIM_028 | 30% | 2.718 | 943 | 791 | 866 |
| SIM_029 | 20% | 6.007 | 1.348 | 1.115 | 1.259 |

Leitura: com as mesmas chances, o ganho do estilo em estágios é pequeno em valor esperado (diferença de fracasso: R$ 111 mil por tentativa) e o estilo continua melhor mesmo com p reduzida. A diferença grande está no risco: o pior caso cai de uma dívida pessoal e anos de recuperação para uma perda de cerca de R$ 25 mil. Isso é um modelo com probabilidades subjetivas; não é estatística.

## Mesma ambição, decisões diferentes (SIM_004 × SIM_029 × SIM_024)

- **SIM_004:** B2C, capital de risco cedo, aval pessoal, escala antes da retenção. Resultado: falência e dívida.
- **SIM_029:** mesma área (fintech). Mata a ideia B2C pelo critério (LTV/CAC 0,9), escolhe B2B, capta só com tração e sem aval. Resultado: patrimônio ajustado base R$ 6,0 mi e mínimo pessoal de R$ 3 mil.
- **SIM_024:** nicho concorrido (restaurantes); o critério de abandono encerra a aposta no ano 5 com perda de ~R$ 25 mil.

## Padrões
- **Melhores no equilíbrio:** SIM_021 (LegalTech, 6,06), SIM_027 (InsurTech, 5,81), SIM_024 e SIM_028 (5,50). Nenhum supera as híbridas anteriores com experiência alta (SIM_012, 014, 006).
- **Nichos com ticket e recorrência melhores:** jurídico, seguros, construção e segurança entregam LTV/CAC entre 4,8 e 6,1 com canais baratos (indicação, associações, contadores). HR e food têm ticket baixo e churn alto.
- **Canal importa mais que produto:** contabilidade (HR, LGPD), associações (seguros), advogados (LegalTech) e engenheiros (obra) dão CAC menor que venda direta.
- **Salário até a tração:** em todas, o personagem sai do emprego só no ano 8 ou 9, com receita recorrente e reserva. Isso custa velocidade (a empresa cresce com poucas horas) e economiza risco.
- **Limite do modelo:** todos os parâmetros de receita e margem de cada nicho são premissas minhas e não vêm de dados setoriais.
