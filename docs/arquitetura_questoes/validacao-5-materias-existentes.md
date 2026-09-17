# Validação das 5 matérias já escritas contra dado real do ENEM

Mesmo método usado em Eletrodinâmica (`eletrodinamica-analise-7anos.md`),
aplicado agora às 5 matérias que já têm banco de prática escrito:
Ecologia, Óptica/Acústica, Fisiologia Humana, Cinemática e Separação de
Misturas. Fonte: questões reais já classificadas no `enem.db`
(2019-2025, aplicação regular) + busca por palavra-chave nos 6 arquivos
de PPL já extraídos (2019-2024).

Nível de rigor mais leve que o de Eletrodinâmica (não foi feita
contagem questão-a-questão de todo padrão possível) — o objetivo aqui
foi responder uma pergunta prática: **o que já está escrito no banco
de prática bate com o que o ENEM cobra de verdade, e falta alguma
coisa óbvia?**

## Ecologia — bem alinhado, com uma lacuna pequena

O banco atual (140 questões, 6 fases: cadeias/relações/ciclos/poluição
atmosférica/saneamento/impactos urbanos) cobre bem o que aparece nos
dados reais: fragmentação de hábitat e corredores ecológicos (2020
Q95, PPL 2022 Q109, PPL 2023 Q120/Q121), ciclos biogeoquímicos (PPL
2023 Q96), poluição atmosférica clássica — CFC/ozônio, efeito estufa,
chuva ácida (PPL 2020 Q107/Q135, PPL 2024 Q144), relações ecológicas
como parasitoidismo (PPL 2023 Q134).

**Lacuna pequena**: "espécie exótica invasora" aparece como tema
próprio em mais de uma prova real (2022 Q99 — jaqueira; PPL 2022 Q91 —
inseticida e abelhas) e não tem um `topico` dedicado no
`FASES_ECOLOGIA` atual — hoje ficaria classificado de forma genérica.
Não é urgente, mas vale considerar um `topico` novo se for escrever
mais questões de ecologia.

## Óptica/Acústica — bem alinhado

Confirma os `topico` já usados: refração/índice de refração (2022 PPL
Q107, 2019 azul Q132), polarização (óculos 3D, PPL 2020 Q117), lentes
fotocrômicas e concentração de luz por lente (PPL 2023 Q106, PPL 2019
Q100), espectro eletromagnético além do visível — infravermelho/UV/
raios X (PPL 2023 Q112), reflexão em satélites (PPL 2023 Q124). Em
acústica, efeito Doppler e ressonância seguem aparecendo (2020 azul
Q114, 2021 azul Q92). Sem gap relevante encontrado.

## Separação de Misturas — bem alinhado

Confirma fortemente o padrão único já coberto pelo banco (`topico`
`metodos_separacao_misturas`): destilação (2020 Q123, PPL 2019 Q109 —
dessalinização), decantação (2022 Q126 — ETA, PPL 2019 Q96 —
petróleo), filtração (2024 Q92), catação (PPL 2022 Q124). O banco
atual está bem direcionado — não achei padrão forte fora desse recorte.

## Cinemática — GAP real: falta MRUV e lançamento de projéteis

O banco atual tem só 1 `topico` (`velocidade_media_mru`, 15 questões).
Os dados reais confirmam que velocidade média/MRU é comum (2023 Q118,
PPL 2020 Q170, PPL 2021 Q138, PPL 2022 Q148) — o padrão já coberto
está certo. **Mas apareceram dois padrões recorrentes que o banco
atual não cobre nenhum pouco:**

- **MRUV (aceleração constante)**: 2020 Q99 — carro parte do repouso
  com aceleração de 1 m/s² até atingir velocidade de cruzeiro, tem que
  sincronizar semáforos.
- **Lançamento de projéteis / queda livre**: 2022 Q100 — jato de água
  horizontal caindo (alcance vertical), 2021 Q94 — jogo de canhões com
  ângulo de disparo, 2020 Q113 — trajetória de queda de uma bolinha
  lançada horizontalmente sobre uma mesa.

Isso é um padrão de conteúdo, não só de questão isolada — MRUV e
lançamento horizontal/oblíquo são a continuação natural de MRU dentro
de Cinemática, e a matéria toda está sendo representada só pelo caso
mais simples.

## Fisiologia Humana — GAP grande: banco muito estreito

O banco atual tem só 1 `topico` (`vacina_vs_soro`, 15 questões) — mas
os dados reais mostram que Fisiologia Humana no ENEM é muito mais
diversa do que esse recorte sozinho. Nas provas reais analisadas
apareceram, cada uma como tema isolado e sem repetição entre si:

- Doping sanguíneo / eritropoietina (sistema circulatório) — 2022 Q104
- Tipos de fibra muscular e desempenho esportivo (sistema muscular) —
  2024 Q132
- Sífilis congênita (sistema imunológico / DSTs) — PPL 2023 Q114
- Anfetaminas e hormônios (sistema endócrino) — PPL 2023 Q119
- Vacina e sorotipos da dengue (sistema imunológico) — PPL 2023 Q128
- Vacina que falha por variação viral (sistema imunológico) — PPL 2024
  Q91
- Audiograma / capacidade auditiva (sistema nervoso/sensorial) — PPL
  2022 Q128

Isso é o achado mais importante da validação: **`vacina_vs_soro` é só
uma fatia pequena de um universo bem maior de Fisiologia Humana** —
sistema circulatório, muscular, endócrino e sensorial aparecem tanto
ou mais que vacina/soro nos dados reais. Escrever mais questões só
nesse tópico teria retorno decrescente; o próximo lote de Fisiologia
Humana deveria abrir pelo menos 2-3 tópicos novos.

## Recomendação de prioridade pros próximos lotes (fora de Eletrodinâmica)

1. **Fisiologia Humana** — maior lacuna relativa (banco muito estreito
   vs. diversidade real). Sugestão de próximos tópicos: sistema
   imunológico geral (além de vacina/soro), sistema circulatório
   (doping, transporte de O₂), sistema muscular (fibras
   lentas/rápidas).
2. **Cinemática** — segunda maior lacuna. Sugestão: MRUV (aceleração
   constante) e lançamento de projéteis (queda livre, lançamento
   horizontal) como dois tópicos novos.
3. Ecologia, Óptica/Acústica e Separação de Misturas — sem urgência,
   o que já está escrito bate com o padrão real.
