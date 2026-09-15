# ADR-0006: IA hospedada (API), não modelo local, para a próxima integração

Status: proposto — ainda não implementado
Data: 2026-09-12 (retroativo — raciocínio já existia em `REVISAO_PROJETO.md`)

## Contexto

A primeira integração de IA planejada é correção de redação (tabela
`redacoes` e `fonte_correcao` já têm o `CHECK` pronto pra aceitar `'ia'`). O
deploy já escolhido (`DEPLOY.md`) é Streamlit Community Cloud — sem GPU, sem
processo de fundo próprio, free tier com recurso limitado.

## Decisão

Quando essa integração for implementada, usar uma API hospedada (ex: Claude)
via `ANTHROPIC_API_KEY` em `.env`/Secrets — mesmo padrão já usado pra
`YOUTUBE_API_KEY` — em vez de um modelo local via Ollama/Llama.

## Alternativas consideradas

- **Llama local via Ollama** — rodaria de graça por chamada, mas exige um
  processo à parte com RAM/GPU suficiente na MESMA máquina que serve o
  Streamlit. Isso só funciona enquanto o app roda na própria máquina do
  Gabriel (mesma wifi) — contradiz o objetivo de acesso remoto (do celular,
  sem notebook ligado) que o projeto já persegue.

## Consequências

Ganha: funciona idêntico local ou no Streamlit Cloud (quem faz o trabalho
pesado é o servidor da Anthropic). Custa: por chamada, ao contrário de local
que é "grátis" depois do hardware — mas o volume (1 usuário, redações
esporádicas) torna esse custo irrelevante na prática.

## Quando revisitar

Se o objetivo de "rodar de qualquer lugar, sem notebook ligado" mudar (por
exemplo, se o projeto virar uso 100% em uma única máquina fixa) — nesse
cenário, Llama local via Ollama volta a ser uma opção válida como "modo
offline".
