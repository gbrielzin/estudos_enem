# Eletrodinâmica - Fase 2 [Lâmpadas em Série/Paralelo — "o que continua aceso"]

Lote de validação (15 questões) — padrão nº2 confirmado na análise real
(6 ocorrências em 12 provas: 2019 Q126, 2023 Q128, PPL 2020 Q95 "cordão
de Natal", PPL 2022 Q118, PPL 2024 Q132). É o padrão puramente
interpretativo que o usuário descreveu: reconhecer se os componentes
estão em série ou paralelo e "seguir o caminho" pra saber o que
continua recebendo corrente — sem precisar calcular valor numérico na
maioria dos casos.

Quatro templates de raciocínio se repetem nesse padrão real, então
variei o contexto mas mantive a lógica:

- **Série pura**: um caminho só. Se um componente queima (abre o
  circuito), TUDO apaga — não tem caminho alternativo.
- **Paralelo puro, fonte ideal**: cada ramo é independente. Se um
  componente queima, os outros continuam exatamente com o mesmo
  brilho (a tensão da fonte não muda).
- **Paralelo, fonte real (com resistência interna)**: se um componente
  sai do circuito, a corrente TOTAL cai, a queda de tensão na
  resistência interna diminui, e sobra mais tensão pros componentes
  restantes — eles ficam ligeiramente MAIS brilhantes.
- **Grupos em série de sub-blocos paralelos** (o "cordão de Natal"):
  o circuito inteiro é dividido em grupos; dentro de cada grupo os
  componentes estão em paralelo, mas os grupos entre si estão em
  série. Tirar um componente de um grupo apaga o GRUPO INTEIRO (não o
  cordão todo, e não só aquele componente).

Não importar ainda — mesma lógica do lote anterior: validar primeiro.

---

Questão 1 (Contexto: Guirlanda Decorativa Simples)

Uma guirlanda de Natal tem 8 lâmpadas idênticas ligadas todas em série a uma única fonte de energia, formando um único caminho fechado. Se uma dessas 8 lâmpadas queimar, o que acontece com as demais 7 lâmpadas da guirlanda?A) Continuam acesas com o mesmo brilho.B) Continuam acesas, porém mais fracas.C) Continuam acesas, porém mais fortes.D) Todas se apagam.E) Apenas as duas lâmpadas vizinhas à que queimou se apagam.

Gabarito: D

Justificativa: Em uma associação em série, existe um único caminho para a corrente. Se qualquer lâmpada queima (circuito aberto naquele ponto), a corrente deixa de circular em todo o percurso, apagando todas as lâmpadas.

---

Questão 2 (Contexto: Iluminação de Vitrine de Loja)

Uma vitrine de loja utiliza 6 lâmpadas de LED idênticas, todas ligadas em paralelo diretamente aos terminais de uma fonte de tensão considerada ideal (tensão constante, independente da carga). Se uma dessas lâmpadas queimar, o que ocorre com o brilho das 5 lâmpadas restantes?A) Permanece exatamente o mesmo.B) Diminui, pois a corrente total se redistribui.C) Aumenta bastante, podendo queimar as demais.D) Todas se apagam junto com a que queimou.E) Piscam de forma intermitente.

Gabarito: A

Justificativa: Em uma associação em paralelo, cada lâmpada está diretamente sujeita à mesma tensão da fonte. Como a fonte é ideal (tensão constante), a tensão sobre as lâmpadas restantes não muda quando uma delas sai do circuito — o brilho permanece o mesmo.

---

Questão 3 (Contexto: Pilha Real com Resistência Interna)

Um conjunto de 4 lâmpadas idênticas está ligado em paralelo aos terminais de uma pilha real, que possui uma resistência interna não desprezível. Ao remover uma das lâmpadas do circuito (deixando apenas 3 ligadas), o que acontece com o brilho das lâmpadas restantes?A) Diminui, pois a corrente total aumenta.B) Aumenta ligeiramente, pois a corrente total diminui e a queda de tensão na resistência interna também diminui.C) Permanece exatamente o mesmo, como em qualquer associação em paralelo.D) As lâmpadas se apagam completamente.E) Aumenta de forma descontrolada até queimar.

Gabarito: B

Justificativa: Com uma lâmpada a menos, a corrente total fornecida pela pilha diminui. Como há resistência interna, uma corrente menor gera uma queda de tensão menor sobre essa resistência, sobrando mais tensão para os terminais externos — por isso as lâmpadas restantes ficam ligeiramente mais brilhantes.

---

Questão 4 (Contexto: Cordão de Luzes de Natal — 200 Lâmpadas)

Um cordão de luzes de Natal possui 200 pequenas lâmpadas idênticas. O fabricante organiza essas lâmpadas em 20 grupos de 10 lâmpadas cada: dentro de cada grupo, as 10 lâmpadas estão ligadas em paralelo entre si, e os 20 grupos, por sua vez, estão ligados em série ao longo do cordão. Ao retirar uma única lâmpada de um dos grupos, quantas lâmpadas do cordão inteiro se apagam?A) Apenas 1 (só a lâmpada retirada).B) 9 (as demais lâmpadas do mesmo grupo).C) 10 (todas as lâmpadas do grupo ao qual pertencia a lâmpada retirada).D) 19 (uma lâmpada de cada um dos outros grupos).E) 200 (o cordão inteiro se apaga).

Gabarito: A

Justificativa: Dentro de cada grupo, as lâmpadas estão em PARALELO — retirar uma não interrompe o caminho das outras 9 do mesmo grupo (permanecem acesas). Como os grupos estão em série entre si, o grupo em questão continua fechado (as outras 9 lâmpadas dele mantêm o caminho), então só a lâmpada retirada deixa de acender; as demais 199 continuam normalmente.

---

Questão 5 (Contexto: Cordão de Luzes — Variação com Grupo em Série)

Um cordão de luzes decorativas tem 90 lâmpadas idênticas organizadas em 9 grupos de 10. Dentro de cada grupo, as 10 lâmpadas estão ligadas em SÉRIE entre si, e os 9 grupos estão ligados em PARALELO uns com os outros no cordão. Se uma lâmpada de um dos grupos queimar (abrindo o circuito naquele ponto), quantas lâmpadas do cordão se apagam?A) Apenas 1.B) 9 (as outras lâmpadas do mesmo grupo).C) 10 (todas as lâmpadas do grupo, incluindo a que queimou).D) 81 (todas menos as do grupo afetado).E) 90 (o cordão inteiro).

Gabarito: C

Justificativa: Dentro do grupo afetado, as lâmpadas estão em SÉRIE — uma queimando interrompe o único caminho daquele grupo, apagando as 10 lâmpadas dele (a que queimou e as outras 9). Como os grupos estão em paralelo entre si, os outros 8 grupos (80 lâmpadas) continuam funcionando normalmente.

---

Questão 6 (Contexto: Painel de Aviso com LEDs — Fonte Ideal)

Um painel luminoso de aviso rodoviário usa 12 LEDs idênticos ligados em paralelo a uma fonte regulada, que mantém a tensão de saída constante independentemente da carga (comportamento de fonte ideal). Dois desses LEDs queimam simultaneamente. O que acontece com o brilho dos 10 LEDs restantes?A) Diminui proporcionalmente.B) Permanece o mesmo.C) Aumenta o suficiente para compensar a perda de luminosidade total.D) Todos se apagam, pois o circuito abre.E) Piscam até se estabilizar num novo valor menor.

Gabarito: B

Justificativa: Assim como no caso de uma única lâmpada, numa fonte ideal em paralelo a tensão sobre os LEDs restantes não muda mesmo com a saída de mais de um componente — o brilho de cada LED que continua no circuito permanece o mesmo.

---

Questão 7 (Contexto: Luminárias de Estufa Agrícola em Série)

Uma estufa agrícola utiliza 15 lâmpadas de crescimento idênticas, todas ligadas em série ao longo de um único circuito, para simular luz solar durante a noite. Durante uma manutenção, o agricultor percebe que todas as 15 lâmpadas apagaram ao mesmo tempo. Qual é a explicação mais provável para essa falha, considerando a associação em série?A) Uma lâmpada queimou, interrompendo o único caminho da corrente.B) A tensão da fonte aumentou repentinamente.C) Apenas as lâmpadas das extremidades pararam de funcionar.D) A resistência total do circuito diminuiu.E) As lâmpadas centrais continuam acesas normalmente.

Gabarito: A

Justificativa: Numa associação em série, existe um único caminho para a corrente elétrica. A queima de qualquer lâmpada interrompe esse caminho e apaga todas as demais — é a explicação mais coerente para todas apagarem simultaneamente.

---

Questão 8 (Contexto: Semáforo com Lâmpadas Redundantes em Paralelo)

Um semáforo experimental usa 3 lâmpadas de LED idênticas ligadas em paralelo para compor o sinal vermelho, como medida de segurança redundante — a intenção é que o sinal continue visível mesmo que uma lâmpada falhe. Supondo uma fonte ideal, se uma das 3 lâmpadas queimar, o sinal vermelho:A) Se apaga completamente, comprometendo a segurança.B) Continua aceso, com as 2 lâmpadas restantes no mesmo brilho de antes.C) Continua aceso, mas com metade do brilho de antes.D) Continua aceso, mas pisca de forma irregular.E) Fica mais brilhante que antes.

Gabarito: B

Justificativa: A escolha de ligar as lâmpadas em paralelo (e não em série) é exatamente o que garante a redundância: cada lâmpada opera de forma independente sob a mesma tensão da fonte, então a queima de uma não afeta o funcionamento nem o brilho das demais.

---

Questão 9 (Contexto: Toca-Discos Vintage com Lâmpada Indicadora em Série com o Motor)

Um aparelho antigo tem uma lâmpada indicadora de funcionamento ligada em série com o motor principal, de modo que ambos compartilham o mesmo único caminho de corrente. Certo dia, o motor para de funcionar e a lâmpada indicadora também se apaga ao mesmo tempo. Considerando a associação em série entre os dois componentes, a explicação mais coerente é que:A) O motor e a lâmpada falharam por coincidência, sem relação entre si.B) A interrupção em qualquer um dos dois componentes (motor ou lâmpada) interrompe o único caminho da corrente, desligando o outro também.C) A lâmpada sempre apaga primeiro, independentemente do estado do motor.D) Estando em série, os dois componentes são eletricamente independentes.E) O motor recebe tensão mesmo com o circuito aberto.

Gabarito: B

Justificativa: Como a lâmpada e o motor compartilham o mesmo caminho (série), uma falha em qualquer um dos dois interrompe a corrente para ambos — por isso os dois pararam de funcionar juntos.

---

Questão 10 (Contexto: Sistema de Iluminação com Dois Grupos Independentes)

Uma sala tem duas fileiras de lâmpadas: a fileira A, com 5 lâmpadas em série entre si, e a fileira B, com 5 lâmpadas em paralelo entre si — as duas fileiras são circuitos completamente independentes, cada uma ligada à sua própria tomada. Uma lâmpada da fileira A queima ao mesmo tempo que uma lâmpada da fileira B. O que se observa em cada fileira?A) As duas fileiras apagam completamente.B) A fileira A apaga completamente; a fileira B mantém as 4 lâmpadas restantes acesas.C) A fileira B apaga completamente; a fileira A mantém as 4 lâmpadas restantes acesas.D) As duas fileiras mantêm as lâmpadas restantes acesas normalmente.E) Não é possível prever o comportamento sem saber a potência das lâmpadas.

Gabarito: B

Justificativa: A fileira A está em série — a queima de uma lâmpada interrompe o único caminho e apaga toda a fileira. A fileira B está em paralelo — a queima de uma lâmpada não afeta o caminho das outras 4, que continuam acesas.

---

Questão 11 (Contexto: Régua de Tomadas com Lâmpadas de Teste em Paralelo, Fonte Real)

Uma régua de tomadas alimenta 8 lâmpadas de teste idênticas, ligadas em paralelo, a partir de uma fonte que possui resistência interna considerável (não pode ser tratada como ideal). Um técnico retira 3 dessas 8 lâmpadas do circuito. O que se espera do brilho das 5 lâmpadas restantes, em comparação com a situação anterior?A) Diminui, pois a corrente total aumentou.B) Fica ligeiramente maior, pois a corrente total drenada da fonte diminuiu, reduzindo a queda de tensão na resistência interna.C) Permanece idêntico, pois lâmpadas em paralelo nunca são afetadas por mudanças no circuito.D) As lâmpadas se apagam, pois o circuito ficou incompleto.E) Não é possível determinar sem saber a potência de cada lâmpada retirada.

Gabarito: B

Justificativa: Com menos lâmpadas em paralelo, a corrente total fornecida pela fonte diminui. Como a fonte tem resistência interna, essa corrente menor causa uma queda de tensão menor internamente, sobrando mais tensão para as lâmpadas restantes — que ficam ligeiramente mais brilhantes.

---

Questão 12 (Contexto: Pisca-Pisca com Três Segmentos em Série, Lâmpadas em Paralelo Dentro de Cada Segmento)

Um pisca-pisca de vitrine tem 3 segmentos ligados em série entre si; dentro de cada segmento existem 6 lâmpadas idênticas ligadas em paralelo. Uma lâmpada do segundo segmento queima. O que acontece com o restante do pisca-pisca?A) O pisca-pisca inteiro se apaga.B) Apenas o segundo segmento se apaga por completo; os outros dois continuam piscando normalmente.C) Apenas a lâmpada queimada fica apagada; as outras 5 do segundo segmento e os demais segmentos continuam normais.D) O primeiro e o terceiro segmentos apagam; o segundo continua aceso.E) Todas as lâmpadas ficam mais fracas, mas nenhuma apaga.

Gabarito: C

Justificativa: Dentro do segundo segmento, as lâmpadas estão em paralelo — a queima de uma não interrompe o caminho das outras 5 do mesmo segmento. Como o segmento continua fechado (as 5 lâmpadas restantes mantêm a corrente circulando), a ligação em série entre os segmentos não é afetada, e os outros dois segmentos seguem piscando normalmente.

---

Questão 13 (Contexto: Comparação Conceitual — Escolha de Projeto)

Um engenheiro precisa decidir como ligar as 10 lâmpadas de emergência de um corredor de hospital: em série ou em paralelo. O requisito de segurança exige que a falha de uma única lâmpada NUNCA apague as demais. Qual associação atende a esse requisito, e por quê?A) Série, porque garante um único caminho estável para a corrente.B) Série, porque a resistência total diminui com mais lâmpadas.C) Paralelo, porque cada lâmpada opera em um caminho independente, sujeito à mesma tensão da fonte.D) Paralelo, porque a corrente total é sempre menor que em série.E) Qualquer uma das duas associações atende ao requisito igualmente.

Gabarito: C

Justificativa: Só a associação em paralelo garante que a falha de um componente não interrompa o caminho dos demais, já que cada um tem seu próprio ramo independente ligado diretamente aos terminais da fonte.

---

Questão 14 (Contexto: Diagnóstico de Defeito em Guirlanda Antiga)

Uma guirlanda antiga de 50 lâmpadas em série parou de funcionar por completo. Um morador suspeita que apenas uma lâmpada queimou, mas não sabe qual. Do ponto de vista da associação em série, por que a falha de apenas 1 lâmpada em 50 é suficiente para apagar todas as outras 49?A) Porque, em série, todas as lâmpadas compartilham o mesmo e único caminho de corrente, e a interrupção em qualquer ponto interrompe o circuito inteiro.B) Porque lâmpadas em série sempre queimam em sequência, uma após a outra.C) Porque a tensão da fonte cai a zero quando qualquer lâmpada é retirada.D) Porque, em série, cada lâmpada tem seu próprio caminho independente.E) Porque a resistência total da guirlanda se torna infinita apenas nas lâmpadas vizinhas.

Gabarito: A

Justificativa: A característica definidora da associação em série é o caminho único — não há rota alternativa para a corrente contornar o ponto interrompido, por isso a falha de uma única lâmpada compromete as 49 restantes.

---

Questão 15 (Contexto: Loja com Vitrine em Paralelo — Fonte Ideal, Substituição Parcial)

Uma vitrine tem 10 lâmpadas de LED em paralelo, alimentadas por uma fonte considerada ideal. O lojista substitui 4 dessas 10 lâmpadas por modelos de LED mais modernos, porém de mesma tensão nominal e mesmo brilho que as originais. As 6 lâmpadas antigas que permaneceram no circuito terão seu brilho:A) Reduzido, pois agora há lâmpadas diferentes compartilhando o mesmo circuito.B) Aumentado, pois lâmpadas novas drenam menos corrente.C) Inalterado, pois a tensão da fonte ideal continua a mesma sobre cada ramo em paralelo.D) Instável, alternando entre mais forte e mais fraco.E) Impossível de prever sem saber a potência exata dos novos LEDs.

Gabarito: C

Justificativa: Em uma associação em paralelo com fonte ideal, cada ramo está sujeito à mesma tensão constante, independentemente do que acontece nos outros ramos — trocar algumas lâmpadas por outras de mesma tensão nominal não altera o brilho das que permanecem no circuito.
