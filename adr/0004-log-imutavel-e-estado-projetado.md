# ADR-0004: Log imutável (`tentativas_usuario`) + estado projetado (`estado_revisao`)

Status: aceito
Data: 2026-09-12 (retroativo)

## Contexto

O sistema precisa saber duas coisas diferentes sobre uma questão: o que
aconteceu (toda tentativa, na ordem real) e o que fazer agora (quando
revisar de novo). O sistema legado misturava as duas num `.update()` só,
o que confundia histórico com estado atual.

## Decisão

Duas tabelas: `tentativas_usuario` (append-only, nunca editada in-loco em
uso normal) e `estado_revisao` (1 linha por questão já tentada, sempre
recalculável do zero a partir do log via `_recomputar_estado_revisao()`).

## Alternativas consideradas

- **1 tabela só, atualizada in-place** (o que o sistema legado fazia) —
  editar/apagar uma tentativa no meio do histórico não tem como "consertar"
  o valor atual sem replay completo, porque streak/intervalo são
  cumulativos; uma tabela só faria exatamente o bug que o legado tinha.

## Consequências

Ganha: `estado_revisao` nunca "deriva" de um estado corrompido — é sempre
100% reconstruível a partir de `tentativas_usuario` (mesmo princípio de
event sourcing em sistemas maiores, implementado à mão aqui). Editar uma
tentativa no meio do histórico dispara um replay completo dali pra frente,
nunca um ajuste pontual. Custa: toda escrita em `tentativas_usuario` que
afeta o streak precisa lembrar de também acionar
`_recomputar_estado_revisao()` — por isso `registrar_tentativa()` é a ÚNICA
função com permissão de escrever nas duas tabelas juntas, de propósito.

## Quando revisitar

Não há sinal concreto pra revisitar isso — é uma decisão de modelagem que
continua correta em qualquer escala (o padrão log-imutável+projeção só fica
mais valioso com mais volume, não menos).
