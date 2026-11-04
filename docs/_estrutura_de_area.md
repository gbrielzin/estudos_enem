# Estrutura padrão de uma área do projeto

Cada área (redação, matemática, natureza, linguagens, app, carreira...) é como um time separado, com o mesmo molde. Começou pela redação em 04/11/2026 (`redacao_pesquisa/`); as outras seguem depois do ENEM.

```
docs/<area>/
  README.md        índice: onde está o quê, estado atual, regras da área
  01_regras/       a ÚNICA fonte da verdade (um arquivo mestre + peças de apoio)
  02_fontes/       material de terceiros e opinião de canais (com status de confiança)
  03_dados/        bancos, planilhas, estatísticas
  04_treinos/      histórico diário + metricas.csv (números comparáveis)
  05_decisoes/     uma ficha por decisão + evidencias/
  06_ferramentas/  scripts da área
  arquivo/         versões superadas (guardar, não apagar)
docs/_geral/       regras que valem para todas as áreas (canais confiáveis, como o Claude trabalha)
```

## Regras do molde
- Um arquivo mestre de regras por área. O resto aponta para ele.
- Nada é apagado sem teste: só o que um script recria idêntico (conferir por hash). O resto vai para `arquivo/`.
- Mover arquivo = atualizar `.gitignore`, scripts e referências no mesmo passo.
- Número sempre com **antes → depois**, amostra e limite. Se não foi medido, escrever "sem número".

## Ficha de decisão (padrão para entrevista)
Copiar `05_decisoes/_modelo_ficha.md`. Campos: Data · Problema · Alternativas · Decisão · Por quê · **Número (antes → depois)** · Resultado · Limites · Evidência.
