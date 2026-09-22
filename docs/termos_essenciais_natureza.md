# Termos essenciais — Ciências da Natureza (frequência no corpus)

Gerado em 2026-09-22 a partir de `core/corpus_analise.db` (2865 questões 2009-2025, filtro `disciplina='ciencias-natureza'` = 706 questões). Script: contagem de documento (questão) por palavra, considerando contexto + enunciado + alternativas, com lista de palavras-função removida (artigos, preposições, conectivos e boilerplate de prova como "disponível em", "acesso em", "assinale").

**PPL não está incluído.** Os PDFs de PPL 2015-2020+ estão em `core/inep_ppl/` mas ainda não foram extraídos pra texto/banco (ver `docs/plano_ampliar_banco_provas_antigas_e_ppl.md`) — é trabalho de pipeline separado, não entra nesta contagem.

## O que a hipótese de "90% das questões" não confirma

Nenhuma palavra de conteúdo chega perto de 90%. Ciências da Natureza mistura física, química e biologia, então o vocabulário se espalha — não existe uma palavra "universal" da prova. O topo real:

| Termo | Questões | % do total |
|---|---|---|
| água | 153 | 21,7% |
| energia | 93 | 13,2% |
| meio | 91 | 12,9% |
| química | 87 | 12,3% |
| massa | 72 | 10,2% |
| ambiente | 71 | 10,1% |
| ocorre | 65 | 9,2% |
| produção | 64 | 9,1% |
| reação | 64 | 9,1% |
| temperatura | 60 | 8,5% |
| velocidade | 59 | 8,4% |
| células | 48 | 6,8% |
| calor | 48 | 6,8% |
| substâncias | 48 | 6,8% |
| plantas | 46 | 6,5% |
| elétrica | 45 | 6,4% |
| espécies | 44 | 6,2% |
| ácido | 43 | 6,1% |
| oxigênio | 42 | 5,9% |
| carbono | 39 | 5,5% |
| moléculas | 38 | 5,4% |
| concentração | 37 | 5,2% |
| organismo | 35 | 5,0% |
| corrente | 35 | 5,0% |
| solo | 34 | 4,8% |

## Leitura

- **água, energia, massa, temperatura, reação, velocidade** são o núcleo transversal (física + química) — aparecem em ~1 a cada 8-12 questões de Natureza, independente da matéria específica que você está estudando no dia.
- **células, substâncias, ácido, oxigênio, carbono, moléculas, organismo** puxam mais pro lado biologia/química — são vocabulário que vale a pena ter automático, porque reaparece em contextos variados (igual você observou na sessão de hoje: "enzima" não é o assunto, é o vocabulário de fundo que trava a leitura).
- Nenhum termo isolado é "obrigatório" sozinho — o ganho está em ter um punhado deles automáticos (não precisa parar pra pensar o que significa), porque eles se acumulam: uma questão de eletroquímica cruza "reação", "concentração", "elétrica", "oxigênio" ao mesmo tempo.

## Limites

- Contagem por presença (0/1) na questão, não por repetição dentro do texto.
- Sem normalização de singular/plural nem sinônimo (ex.: "célula" e "células" contam separado — o valor real de "célula\*" junto é maior que os 6,8% mostrados).
- PPL fora (só provas regulares 2009-2025, `enem.dev` + `enem.db_local`).
- Corte em 4+ letras; siglas curtas (pH, DNA, ATP) não entram nessa lista mas são candidatas a checar à parte.
