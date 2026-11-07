# Aprendizados — Lote 2 e erratas

1. **Experiência tem custo medido em caixa, não só em tempo.** O ano nos EUA (SIM_012) leva o personagem a −R$ 64 mil; o mestrado fora (SIM_013), a −R$ 17 mil e 6 anos de renda baixa.
2. **Sócio operador e salário reduzem o risco de uma empresa em paralelo.** SIM_014 e SIM_011 mantêm renda e experiência com patrimônio ajustado de R$ 4,3 a 4,6 mi.
3. **O resultado do TOP 3 é robusto ao peso da experiência.** Dobrar o peso não muda os 3 primeiros.
4. **Foco total vence em patrimônio de papel; híbrido vence em patrimônio realizável por ano.** Depende de como o usuário valoriza liquidez.
5. **Conflito societário é o principal risco novo (SIM_014).** Governança desde o início é decisão de custo baixo.

## Errata técnica (2026-11-07)
- O motor v1 atribuía 100% dos dividendos ao fundador mesmo com sócios. Foi criada a opção `div_share`, ligada nas simulações do Lote 2 e desligada nas do Lote 1 para preservar a reprodutibilidade. Verifiquei os casos com sócios do Lote 1 (SIM_010): não houve dividendos no período, então os resultados v1 não mudam.
- O critério 16 não existia no Lote 1; as notas foram atribuídas a posteriori e ficam em `06_RANKINGS/notas_criterio16_lote1.md`.
