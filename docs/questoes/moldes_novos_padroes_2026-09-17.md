# Moldes de padrão novo — pra revisar antes de gerar questão de verdade

Gerado a partir da classificação de questões oficiais reais + trade-off
frequência x dificuldade (ver `docs/pesquisa_estrategia_de_prova.md`, seções
12/13 e a conversa que motivou este arquivo). Mesmo formato dos seus próprios
documentos em `docs/questoes/*.docx` (radical = o que NÃO pode mudar entre as
questões; incidental = o que pode variar à vontade) — a ideia é você aprovar
o molde primeiro, só depois vira lote de questão de verdade.

Nenhuma questão aqui foi inserida no banco. É conteúdo pra revisão.

---

## 1. Cinemática — MRUV (Movimento Retilíneo Uniformemente Variado)

**Por que este e não outro**: 2 das 7 questões oficiais da amostra (maior
frequência do grupo), e ainda é a mesma família de fórmula do MRU que já
existe no banco — só estende `v = v₀ + at` e `Δs = v₀t + at²/2`, sem
precisar de vetor 2D nem trigonometria.

**CONCEITO INICIAL PARA O ALUNO**

> MRUV: a velocidade MUDA a uma taxa constante (aceleração). Duas fórmulas
> cobrem quase tudo: `v = v₀ + a·t` (velocidade em função do tempo) e
> `v² = v₀² + 2·a·Δs` (velocidade em função do espaço, sem precisar do
> tempo). Sinal de `a` positivo = acelerando; negativo = freando. No ponto
> mais alto de um lançamento vertical pra cima, `v = 0` mas `a` continua
> sendo a gravidade (nunca zero) — é a pegadinha mais comum.

**Radical (não muda)**: um objeto parte com velocidade inicial conhecida
(ou do repouso), sofre aceleração constante, e a questão pede pra achar
velocidade final, distância percorrida, ou tempo — usando uma das duas
fórmulas acima.

**Incidental (varia à vontade)**: carro freando/acelerando, trem, foguete,
elevador, queda vertical (a = g), objeto lançado pra cima (a = -g), qualquer
cenário com "aceleração constante" nomeada ou implícita.

**Distrator plausível**: confundir MRUV com MRU (usar `v = d/t` quando a
velocidade não é constante), ou errar o sinal de `a` no lançamento vertical.

---

## 2. Cinemática — Lançamento Horizontal

**Por que este e não outro**: também 2/7 na amostra, mas dificuldade maior
que MRUV (decompõe em 2 eixos independentes) — prioridade 2, não 1.

**CONCEITO INICIAL PARA O ALUNO**

> Lançamento horizontal = dois movimentos ACONTECENDO AO MESMO TEMPO, mas
> INDEPENDENTES um do outro: no eixo horizontal (x) é MRU puro (velocidade
> constante, a mesma que o objeto tinha ao sair); no eixo vertical (y) é
> queda livre (MRUV com a = g, começando do repouso NESSE eixo). O tempo de
> queda depende só da altura (eixo y) — a velocidade horizontal não muda
> quanto tempo o objeto leva pra cair.

**Radical (não muda)**: um objeto sai de uma altura com velocidade
horizontal constante, e a questão pede alcance horizontal, tempo de queda,
ou altura — sempre separando os dois eixos.

**Incidental (varia)**: bolinha saindo de mesa, mangueira de água, avião
soltando carga, projétil de brinquedo, qualquer "sai correndo e cai".

**Distrator plausível**: aplicar a fórmula de queda livre no eixo
horizontal (ou vice-versa), ou achar que a velocidade horizontal afeta o
tempo de queda.

---

## 3. Fisiologia Humana — Bioacumulação em Tecido Adiposo

**Por que este e não outro**: prioridade 1 do grupo — reaproveita a MESMA
regra que Ecologia já ensina (magnificação trófica/bioacumulação), só que
aplicada dentro do corpo humano em vez de cadeia alimentar. Sinergia real:
quem já fixou o conceito em Ecologia aprende este quase de graça.

**CONCEITO INICIAL PARA O ALUNO**

> Substâncias LIPOSSOLÚVEIS (se dissolvem em gordura, não em água) não são
> eliminadas facilmente pela urina — o corpo as guarda no tecido ADIPOSO
> (gordura). Com exposição repetida, a concentração no tecido adiposo sobe
> ao longo do tempo (bioacumulação). Isso vale pra poluente ambiental
> (agrotóxico organoclorado, microplástico com aditivo lipofílico) e
> também explica por que substância lipossolúvel demora mais pra "sair do
> corpo" que uma hidrossolúvel.

**Radical (não muda)**: uma substância lipossolúvel entra em contato com o
organismo repetidamente, e a questão pede em qual tecido/órgão ela se
concentra mais.

**Incidental (varia)**: agrotóxico em alimento, microplástico, medicamento
lipossolúvel, poluente industrial — sempre reforçando "não solúvel em
água" como a pista central.

**Distrator plausível**: tecido sanguíneo (só transporta, não acumula),
tecido ósseo (acumula outro tipo de substância, ex: metal pesado tipo
chumbo — cuidado pra não confundir os dois padrões numa prova futura).

---

## 4. Fisiologia Humana — Fibras Musculares (rápidas x lentas)

**Por que este e não outro**: prioridade 2 — distinção binária limpa,
mesmo estilo "diferencie A de B" que já funcionou bem em Óptica.

**CONCEITO INICIAL PARA O ALUNO**

> Fibra lenta (vermelha): muita mitocôndria, muito vaso sanguíneo,
> metabolismo AERÓBICO, resistente à fadiga, mas não é explosiva — favorece
> esporte de LONGA duração (maratona, ciclismo de estrada, triatlo).
> Fibra rápida (branca): pouca mitocôndria, pouco suprimento sanguíneo,
> metabolismo ANAERÓBICO, contrai forte e rápido mas cansa logo — favorece
> esporte de EXPLOSÃO curta (salto, arremesso, sprint, levantamento de
> peso).

**Radical (não muda)**: descreve a proporção de fibra de um atleta (mais
branca ou mais vermelha) e pede em qual modalidade ele teria vantagem — ou
o inverso (dada a modalidade, qual tipo de fibra predomina).

**Incidental (varia)**: qualquer par de esportes contrastando
resistência/longa duração vs. explosão/curta duração.

**Distrator plausível**: trocar aeróbico por anaeróbico, ou associar fibra
branca (explosão) a prova de resistência por engano.

---

## Como usar isto

Cada bloco acima é o mesmo formato que você já usa nos seus `.docx` — dá pra
colar direto num prompt de geração pra IA produzir as ~6-10 questões
regulares + reserva técnica, do mesmo jeito que já foi feito pra Óptica. Eu
não gerei as questões em si porque isso é decisão de conteúdo sua — mas se
quiser, posso gerar um lote de rascunho pra cada um destes 4 pra você só
revisar/aprovar (mesmo fluxo que já validamos: IA gera, você valida via
relato, e a pesquisa de hoje mostrou que isso mantém a qualidade
psicométrica equivalente a questão feita por humano).
