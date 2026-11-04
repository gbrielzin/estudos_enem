# Redação: índice da área

Área separada do resto do projeto (como um time dentro de uma empresa): tem as suas **regras**, as suas **fontes**, os seus **dados**, o seu **histórico de treinos**, as suas **decisões** e as suas **ferramentas**. A estrutura é a mesma para qualquer área (ver `../_estrutura_de_area.md`).

Prazo: ENEM em 15/11/2026. Meta da redação: 900+ pensando o mínimo possível.

## Onde está o quê

| Pasta | O que tem | Abra quando... |
|---|---|---|
| `01_regras/` | **`REGRAS_REDACAO.md` = a única fonte da verdade** (modelo, D1, D2, conclusão, regras de trabalho). Peças de apoio: `modelo_caderno.md`, `d1_padrao_crase.md`, `pecas_*`, `mapa_eixos.md`, `roteiro_aluno.md`, `rubrica_bloco.md` | for treinar, copiar para o caderno ou corrigir um texto |
| `02_fontes/` | Cartilhas do INEP, análise de canais e dicas, `pesquisa_inicial.md`, `metodo_960.md`. Transcrições dos vídeos ficam em `06_ferramentas/transcritor/saida/` | for conferir uma opinião antes de mudar uma regra |
| `03_dados/` | `banco_1000/` (redações nota 1000, fora do git), `banco_temas/` (109 temas inventados), `padroes_1000.md` | for medir uma ideia contra as redações reais |
| `04_treinos/` | Um arquivo por dia: o que foi treinado, o placar a frio, os erros, os textos corrigidos. `metricas.csv` guarda os números comparáveis | for ver a evolução ou registrar um treino |
| `05_decisoes/` | **Uma ficha por decisão** (problema, alternativas, decisão, número antes/depois, limite). `evidencias/` guarda os testes completos | for lembrar por que uma regra é como é, ou contar numa entrevista |
| `06_ferramentas/` | `transcritor/` (baixa transcrições de vídeos) | for baixar mais fontes |
| `arquivo/` | Versões superadas (guardadas, não apagadas) | quase nunca |

## Regras desta área
1. **Só `01_regras/REGRAS_REDACAO.md` manda.** Se um arquivo antigo contradiz, vale ele (os conflitos abertos estão na seção 8 dele).
2. Mudou uma regra? Atualiza o `REGRAS_REDACAO.md` e abre uma ficha em `05_decisoes/` com o número.
3. Todo treino ou teste vira arquivo em `04_treinos/` + linha em `metricas.csv` (e em `../registro_estudo.csv` quando houver minutos).
4. Veredito de nota meu (do Claude) é **avaliação minha, não do INEP**; vale a comparação, não o número absoluto.
5. Opinião de canal: os canais confiáveis valem na letra; o resto passa pelo filtro (banco + cartilha). Lista em `../_geral/` quando existir (hoje em `02_fontes/dicas_canais.md`).

## Estado em 04/11/2026
- Conclusão K4 decidida (ver `05_decisoes/D-001`).
- Cena do D2 em 1 de 6 limpa a frio: é o gargalo até a prova.
- 9 conflitos de regra esperando decisão dele: `01_regras/REGRAS_REDACAO.md` seção 8.
- Redação completa "do zero" (ENEM 2024) ainda por fazer.

## Histórico da reorganização
04/11/2026: 23 itens soltos na raiz viraram as 6 pastas acima. Apagados só dois arquivos gerados (`temas.json`, `redacoes_montadas.md`): os scripts `gerar.py` e `montar.py` os recriam idênticos (conferido por hash). O resto foi movido, não apagado.
