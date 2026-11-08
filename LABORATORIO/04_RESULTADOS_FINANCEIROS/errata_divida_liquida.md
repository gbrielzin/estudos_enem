# Errata — participação societária sem desconto de dívida (2026-11-08)

**Problema:** nos Lotes 1 e 2, a participação societária foi calculada como `% × valor da empresa` (múltiplo de faturamento), sem subtrair dívida nem somar caixa. Isso superestima empresas alavancadas e subestima as com caixa.

**Correção:** a partir do Lote 3, o motor usa `valor patrimonial = valor da empresa − dívida + caixa` (opção `ev_net_debt`). Os arquivos v1 dos Lotes 1 e 2 **não foram alterados** (versões preservadas); a tabela abaixo mostra o patrimônio ajustado corrigido, cenário base.

| ID | Trajetória | Ajustado v1 | Ajustado corrigido | Variação | Pessimista corrigido | Otimista corrigido |
|---|---|---|---|---|---|---|
| SIM_002 | Do flip de iPhone à marca de eletrônicos reformados | 1.596 | 1.105 | -31% | 252 | 4.192 |
| SIM_003 | Agência de automação com IA que vira SaaS vertical | 5.804 | 6.138 | +6% | 1.712 | 13.289 |
| SIM_005 | Carreira + poupança e aquisição de empresa de TI | 1.034 | 720 | -30% | 60 | 2.311 |
| SIM_007 | EdTech do ENEM: do app B2C ao contrato com escolas | 7.383 | 7.909 | +7% | 2.581 | 16.661 |
| SIM_008 | Consultoria de dados que vira holding com imóveis | 3.264 | 3.395 | +4% | 994 | 7.180 |
| SIM_009 | Portfólio de micro-projetos sem foco | 844 | 840 | -1% | 475 | 1.475 |
| SIM_010 | AgTech para cooperativas de café no Espírito Santo | 4.186 | 4.132 | -1% | 1.602 | 8.528 |
| SIM_011 | Carreira primeiro, empresa-satélite depois | 4.335 | 4.469 | +3% | 1.386 | 9.629 |
| SIM_012 | Ano nos EUA, contratos em dólar e produto próprio | 3.723 | 3.808 | +2% | 1.691 | 7.300 |
| SIM_013 | Mestrado no exterior e spin-off de IA aplicada | 3.453 | 3.554 | +3% | 1.306 | 7.371 |
| SIM_014 | Sócio operador e carreira em paralelo | 4.619 | 4.871 | +5% | 1.885 | 9.799 |
| SIM_015 | Atlética como mercado: plataforma de eventos e pagamentos | 3.917 | 4.108 | +5% | 1.364 | 8.676 |
| SIM_016 | Carreira com franquia gerida por gerente | 581 | 366 | -37% | -53 | 1.269 |

Efeito nos rankings: o TOP 3 equilibrado (SIM_012, SIM_014, SIM_006) e o TOP 3 por patrimônio ajustado (SIM_007, SIM_003, SIM_014) não mudam. As maiores quedas são SIM_002, SIM_005 e SIM_016, todas alavancadas, que já estavam nas posições inferiores.
