# D-004: calibrar a correção do Claude contra o INEP

- **Data:** 03/11/2026
- **Problema:** as notas que eu dava a texto dele não tinham referência. Ele precisava saber quanto confiar.
- **Alternativas:** confiar na nota · corrigir às cegas redações que já têm nota INEP e medir a diferença.
- **Decisão:** corrigir às cegas 30 redações com nota INEP e usar o resultado para saber como ler as minhas notas.
- **Por quê:** sem calibração, nota minha parece mais exata do que é.
- **Número:** minha régua rigorosa ficou de 40 a 80 pontos abaixo do INEP em redações nota 1000, nunca dá 200 em C3, correlação 0,28 com a nota INEP (n = 30).
- **Resultado:** regra de uso: minhas notas servem para comparar versões e achar o que está abaixo de 160, não para prever a nota final nem chegar a 200 em C3.
- **Limites:** amostra de 30; correlação baixa; régua dura por construção.
- **Evidência:** seção de calibração em `../04_treinos/2026-11-03_teste_frio_d1_d2.md`.
