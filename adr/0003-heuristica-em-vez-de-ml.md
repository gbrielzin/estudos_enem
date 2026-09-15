# ADR-0003: Heurística determinística (Leitner + score ponderado) em vez de ML

Status: aceito
Data: 2026-09-12 (retroativo)

## Contexto

O sistema precisa decidir (a) quando reapresentar uma questão já respondida
(repetição espaçada) e (b) qual matéria merece mais atenção agora (prioridade
de estudo). O banco tem hoje 657 tentativas, geradas por 1 pessoa só.

## Decisão

Duas fórmulas fixas, sem parâmetro aprendido de dado: `_calcular_leitner()`
(erro zera streak/revisa em 1 dia; acerto dobra intervalo até teto de 90
dias) e `prioridade_de_estudo()` (`score = peso_recorrencia × %recorrência +
(1-peso_recorrencia) × %erro`, pesos fixos passados como argumento).

## Alternativas consideradas

- **Modelo de ML treinado** (ex: classificador de próxima questão a
  recomendar) — 657 tentativas de 1 usuário é pouco dado pra qualquer modelo
  estatístico não-trivial generalizar melhor que a heurística; e um modelo
  treinado não seria auditável numa frase, o que importa numa ferramenta
  onde o próprio usuário precisa confiar no ranking pra agir sobre ele.

## Consequências

Ganha: fórmula 100% auditável (`db.py`'s `explicacao` decompõe o score de
volta nos dois termos que o formam), reprodutível a partir do histórico bruto
(`tentativas_usuario`), sem risco de overfitting em N pequeno. Custa: não
captura padrão nenhum que a fórmula não preveja explicitamente — ex.: não
existe hoje nenhuma noção de "que TIPO de erro" além do score agregado por
matéria (ver `analise_por_tipo_erro`, que é um recorte separado, não fundido
no score).

## Quando revisitar

Quando o volume de tentativas crescer por pelo menos uma ordem de grandeza
(milhares, não centenas) E existir uma pergunta que a fórmula atual
comprovadamente responde mal — não por "parecer mais profissional" ter ML.
