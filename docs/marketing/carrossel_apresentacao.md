# Carrossel de apresentação (1º post no LinkedIn)

Decisões dele (2026-09-27): carrossel **sem rosto**, apresentando o **produto** (visual, ideia, um pouco do que já foi feito); **sem citar IA** — o post é sobre o app e as ideias, não sobre a ferramenta usada pra construir. Slides montados no Claude Design com a identidade visual que ele já tem. Compromisso público: 1 post por semana.

## Antes dos prints

PR curto de UI com o que aparece nas telas (da avaliação em [../ideias_melhorias.md](../ideias_melhorias.md) seção 2.5):
1. Nome interno vazando ("geometria_espacial" → "Geometria espacial").
2. "questão(ões)" → plural resolvido pelo número.
3. Rank/XP alto ao lado de streak 0.

Prints (sessão com Playwright): tela principal/trilha, tela de moldes (kit + variação + motivo do erro), revisão do dia.

## Slides

| # | Texto | Visual |
|---|---|---|
| 1 | "Construí o app que eu uso pra estudar pro ENEM." | Print da tela principal |
| 2 | "Eu estudava muito e não sabia **onde** errava." | Fundo liso, frase grande |
| 3 | "Errou? O app mostra o kit — fórmula, quando usar e um apelido — e gera a **mesma questão com números novos** até você acertar sozinho." | Print da tela de moldes |
| 3b | **Os números de quem usa de verdade (eu):** 1.157 questões oficiais do ENEM (2010-2025) no banco · 867 tentativas registradas · **363 erros** — cada um virou revisão agendada · 31 h de estudo registradas · 342 redações nota 1000 analisadas | Painel de números grandes (tipo "stat tile") |
| 4 | "A questão que você errou volta amanhã. A que acertou volta em 2, 4, 8 dias." | Esquema da revisão espaçada |
| 5 | "Por dentro: o app conversa com uma API em Python, que guarda cada tentativa num banco e agenda a revisão." | Diagrama com setinhas (feito por ele) |
| 6 | "Analisei as notas de redação de 3,46 milhões de participantes do ENEM 2025: 96% de quem tirou 960-980 perdeu ponto na mesma competência — gramática." | Gráfico de barras simples |
| 7 | "O que vem: painel de redação, banco de redações nota 1000, mais questões com números trocados." | Lista curta |
| 8 | "Vou mostrar a construção toda semana. Me segue pra acompanhar." | Logo / mascote |

## Números (conferidos no banco em 2026-09-27, 01:55)

| Número | Valor | De onde |
|---|---|---|
| Questões oficiais do ENEM no banco | 1.157 (Natureza e Matemática, 2010-2025) | `questoes` (1.509 menos 352 de prática) |
| Questões de prática | 352 | `origem='banco_pratica'` |
| Tentativas registradas | 867 (504 acertos, **363 erros**) | `tentativas_usuario`, 26/08 a 26/09/2026 |
| Questões diferentes já feitas | 666, todas na revisão espaçada | `estado_revisao` |
| Horas de estudo registradas | 31 h | `docs/registro_estudo.csv` |
| Redações nota 1000 analisadas | 342 (ENEM 2012-2025) | banco de redações |
| Notas de redação analisadas | 3,46 milhões (ENEM 2025) | microdados do INEP |
| Testes automatizados | 131 | suíte do core |

Mostrar erro é o gancho honesto: "363 erros" diz que o app é usado de verdade. Atualizar os números no dia de postar.

## Texto do post (acompanha o carrossel)

Primeira linha = gancho (a mesma do slide 1). Depois 2-3 linhas: por que construiu, o que o app faz de diferente (descobrir onde erra + repetir com números novos), convite pra acompanhar. Sem hashtag em excesso (no máximo 3).

## Checklist

Sem token, `.env`, senha, e-mail, nota pessoal que ele não queira mostrar, nome de aluno de terceiros, texto de redação de terceiros. Prints só do que está no master.
