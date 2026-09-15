# -*- coding: utf-8 -*-
"""Script de uma vez só (one-off): carrega no banco de prática
(origem='banco_pratica') as questões de Óptica/Ondulatória e Ecologia
que o usuário construiu manualmente numa sessão longa com outra IA de
chat, questão por questão, com gabarito confirmado por rodadas de
"engenharia reversa".

Fonte: transcrição colada pelo usuário na conversa com o Claude Code em
2026-09-15. Cada bloco abaixo é texto EXTRAÍDO VERBATIM dessa
transcrição -- nenhum enunciado ou alternativa foi inventado.

Escopo (deliberadamente menor que o "total" que a outra IA alegou ter
alcançado -- ver nota abaixo):

- Óptica e Ondulatória: 40 questões confirmadas (25 da faixa 36-60 do
  banco original + 10 do "Lote de Revisão Geral" + 5 do "Lote de
  Transição Nível Médio"). As questões 1-35 do banco original de
  Óptica NUNCA tiveram o texto completo colado na transcrição -- só
  apareceram resumidas em recapitulações de "engenharia reversa" (ex:
  "a questão do avião" sem o enunciado nem as 5 alternativas). Não dá
  para reconstruir isso sem inventar texto, então ficaram de fora.

- Ecologia: 110 questões confirmadas, NÃO as 120 que a outra IA alegou
  ter fechado. Dois blocos de 5 questões (os que a própria transcrição
  rotulava como "56 a 60" e "86 a 90") foram apresentados mas NUNCA
  tiveram resposta do usuário nem correção explícita da IA -- a
  conversa mudou de assunto antes de qualquer um dos dois ser
  respondido, e a contagem "cumulativa" que a IA foi anunciando
  (60, 70, 80... 120 questões) não refletia isso; ela incrementava o
  contador mesmo sem gabarito confirmado. Sem uma frase explícita tipo
  "o gabarito é X" pareada com uma resposta do usuário, não há como
  confirmar a resposta certa -- por isso esses dois blocos de 5 ficaram
  de fora (110 = 120 - 10).

- Questão 51 de Ecologia (pirâmide de números do fitoplâncton/
  zooplâncton) tinha uma contradição na própria transcrição: uma
  passagem de correção diz que o gabarito é B, outra (no mesmo texto)
  trata a resposta A do usuário como certa. Resolvido usando a MESMA
  regra física repetida em todas as outras questões de pirâmide de
  números do lote (ex: Q52, Q56 revisado, Q97, Q107): "barra da base
  menor que a barra de cima = inversão na base de produtores" -- e Q51
  descreve exatamente esse cenário (1 milhão de fitoplâncton
  sustentando 10 milhões de zooplâncton, base menor que o meio), então
  o gabarito usado aqui é a letra B ("uma inversão em sua base de
  produtores").

Rodar (a partir de core/): `python popular_banco_pratica_natureza.py`
"""

import db

FONTE = "chatgpt"

# ============================================================
# OPTICA E ONDULATORIA -- 40 questoes confirmadas, na ordem:
# Lote 8 (36-40), Lote 9 (41-45), Lote 10 (46-50), Lote 11 (51-55),
# Lote 12 (56-60), Revisao Geral (10), Transicao Nivel Medio (5)
# ============================================================

OPTICA_TEXTO = r"""
Janelas de aviões comerciais de última geração não possuem mais aquela cortininha plástica manual. Em vez disso, o passageiro aperta um botão e o vidro escurece gradativamente. O sistema funciona aplicando uma pequena tensão elétrica que alinha partículas microscópicas alongadas em uma película interna. Quando desalinhadas, essas partículas barram as ondas de luz que vibram na horizontal e na vertical de forma cruzada, impedindo a entrada de claridade sem que o vidro precise ser pintado ou focado.
O fenômeno físico manipulado eletronicamente para escurecer a janela do avião é a:
A) difração.
B) refração.
C) reflexão.
D) polarização.
E) interferência.
GABARITO: D
---
Em cirurgias oftalmológicas a laser para correção de miopia, os médicos utilizam o laser de femtossegundo para fazer um corte ultrafino e preciso na córnea do paciente. O feixe de laser viaja pelo ar, penetra no tecido ocular transparente e sofre uma alteração imediata em sua velocidade de propagação e no seu comprimento de onda, desviando sua trajetória original para focar exatamente no ponto da córnea que precisa ser esculpido, enquanto a frequência do aparelho se mantém constante.
O fenômeno ondulatório sofrido pelo laser ao entrar no tecido ocular do paciente é a:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) polarização.
GABARITO: B
---
Alguns relógios de luxo utilizam mostradores feitos com madrepérola, uma substância rica em calcário produzida no interior de certas conchas de moluscos. A madrepérola possui uma estrutura interna formada por finas lâminas sobrepostas. Quando a luz ambiente atinge o relógio, ela reflete tanto na camada mais externa quanto nas camadas microscópicas inferiores dessas lâminas. Ao retornarem juntas para o olho do observador, essas ondas sofrem uma superposição que intensifica cores brilhantes e mutáveis (iridescência) de acordo com o ângulo de visão.
A formação do brilho colorido e mutável no mostrador de madrepérola ocorre devido ao fenômeno da:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: E
---
Copos térmicos de inox escovado possuem superfícies externas com microrrugosidades metálicas propositais. Quando a luz do Sol ou das lâmpadas atinge o copo, os raios luminosos batem e retornam para o ambiente ricocheteando em infinitas direções aleatórias. Esse mecanismo impede que o usuário veja seu próprio reflexo nítido no copo (como veria em um espelho), mas faz com que o objeto exiba um brilho suave e uniforme por toda a sua extensão.
O fenômeno óptico que faz a luz rebater na superfície do copo de inox e se espalhar de forma desordenada é a:
A) difração.
B) refração.
C) reflexão difusa.
D) polarização.
E) absorção.
GABARITO: C
---
Equipamentos de endoscopia utilizam um feixe de fibras ópticas flexíveis inserido no tubo flexível para iluminar o estômago do paciente durante o exame. A luz gerada por uma lâmpada externa forte entra na ponta do cabo de vidro e viaja por metros fazendo curvas acentuadas, batendo sucessivamente nas paredes internas do filamento sem conseguir escapar para o corpo do paciente, iluminando perfeitamente os órgãos internos.
O fenômeno que garante o aprisionamento e a condução da luz sem perdas por dentro das curvas do cabo de fibra óptica é a:
A) difração.
B) refração total.
C) reflexão interna total.
D) dispersão cromática.
E) interferência construtiva.
GABARITO: C
---
Sensores infravermelhos instalados em torneiras automáticas de shoppings funcionam emitindo um feixe de luz invisível continuamente. Quando uma pessoa aproxima as mãos da torneira, as ondas de luz colidem com a pele e retornam diretamente para um fotodetector embutido no metal. O circuito integrado processa o sinal recebido de volta e abre a válvula de água instantaneamente, fechando-a assim que as mãos são retiradas.
O funcionamento da torneira automática baseia-se diretamente no fenômeno da:
A) refração.
B) difração.
C) reflexão.
D) dispersão.
E) polarização.
GABARITO: C
---
Equipamentos de sonar utilizados por navios de pesquisa oceanográfica emitem pulsos de som direcionados para o leito do oceano. Essas ondas acústicas se propagam pela água salgada e, ao atingirem a fronteira com o solo marinho (passando da água para a camada de lama densa ou rocha), sofrem uma mudança drástica em sua velocidade de propagação e no seu comprimento de onda, continuando a se mover verticalmente para o interior da crosta terrestre, enquanto a frequência do pulso original não sofre alteração.
O fenômeno ondulatório sofrido pelo som do sonar ao penetrar no solo marinho é a:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) polarização.
GABARITO: B
---
Vidros texturizados do tipo "canelado" ou "antílope", muito utilizados em portas de banheiros e divisórias de escritórios, permitem que a claridade do dia entre no ambiente, mas impedem que se enxergue nitidamente através deles. Isso ocorre porque a superfície irregular e cheia de ondulações do vidro faz com que os raios de luz sofram rebatimentos e espalhamentos em infinitas direções desordenadas ao atingirem o material, quebrando a formação de imagens nítidas.
O fenômeno óptico responsável pelo espalhamento desordenado da luz na superfície do vidro texturizado é a:
A) difração.
B) refração.
C) reflexão difusa.
D) polarização.
E) absorção.
GABARITO: C
---
Telas de projeção de cinemas convencionais são feitas de um tecido branco fosco e rugoso em nível microscópico. Quando o projetor joga o feixe de luz focado na tela para exibir o filme, essa textura microscópica faz com que os raios de luz retornem ricocheteando em todas as direções possíveis pelo recinto. Esse design é essencial para garantir que um espectador sentado na fileira lateral enxergue a mesma imagem e com o mesmo brilho que alguém sentado exatamente no centro da sala.
O fenômeno óptico que os engenheiros utilizam na tela do cinema para espalhar a imagem por toda a sala é a:
A) difração.
B) refração.
C) reflexão difusa.
D) polarização.
E) absorção.
GABARITO: C
---
Óculos de sol de alto desempenho utilizados por pescadores esportivos trazem filtros moleculares especiais em suas lentes. Quando a luz solar atinge a superfície plana da água do rio, ela sofre uma alteração e passa a vibrar quase inteiramente em um plano horizontal, criando um brilho intenso que cega o pescador. Ao passar pelas lentes desses óculos, essa vibração horizontal é bloqueada, permitindo que apenas a luz vertical chegue aos olhos do usuário, revelando os peixes abaixo da superfície.
A tecnologia desses óculos de pesca consegue eliminar o brilho da água utilizando o fenômeno da:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: D
---
Sensores de segurança instalados em portas de elevadores modernos utilizam uma cortina invisível de feixes de LED infravermelho alinhados verticalmente. Quando uma pessoa ou objeto intercepta essa linha invisível, a luz deixa de atingir o receptor do lado oposto. O microcontrolador do elevador detecta imediatamente a ausência do sinal de luz e reverte o fechamento das portas, evitando acidentes.
O princípio de funcionamento dessa barreira de segurança baseia-se na interrupção direta da propagação da luz, que deixa de sofrer o fenômeno da:
A) difração.
B) refração.
C) transmissão.
D) polarização.
E) interferência.
GABARITO: C
---
Em geofísica, para mapear lençóis freáticos e falhas geológicas profundas sem precisar escavar, os cientistas utilizam o GPR (Radar de Penetração no Solo). O aparelho emite ondas eletromagnéticas de rádio em direção ao chão. Quando essa onda passa da camada de areia seca para uma camada de argila úmida, a velocidade da onda cai significativamente e seu comprimento de onda encurta, enquanto a frequência do sinal emitido pelo satélite de controle permanece idêntica.
O fenômeno sofrido pela onda do radar ao passar de uma camada de solo para a outra com umidade diferente é a:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) polarização.
GABARITO: B
---
Janelas de estufas agrícolas de alta tecnologia são feitas com vidros que possuem ranhuras microscópicas paralelas em sua superfície. O objetivo desse design é fazer com que a luz solar direta, ao passar pelas fendas milimétricas do vidro, se espalhe e mude de direção ao contornar as bordas das ranhuras. Esse processo faz com que a luz atinja as folhas das plantas de maneira uniforme por todos os ângulos, evitando sombras excessivas e otimizando a fotossíntese.
O fenômeno ondulatório que ocorre quando a luz contorna as bordas das fendas microscópicas do vidro da estufa é a:
A) difração.
B) refração.
C) reflexão.
D) dispersão.
E) polarização.
GABARITO: A
---
Copos de vidro comuns, quando cheios de água cristalina, funcionam como lentes convergentes improvisadas se colocados à frente de um texto impresso. Se uma pessoa olhar para as letras de um livro através do copo cheio d'água a uma distância curta, verá as letras aparecerem significativamente ampliadas e distorcidas. Isso ocorre porque os raios de luz refletidos pelo papel sofrem desvios sucessivos nas superfícies curvas ao passarem do ar para o vidro, do vidro para a água, e depois de volta para o ar até atingirem os olhos.
O fenômeno óptico responsável pela ampliação e distorção das letras através do copo com água é a:
A) difração.
B) refração.
C) reflexão especular.
D) polarização.
E) absorção.
GABARITO: B
---
Telas de smartphones com tecnologia AMOLED possuem películas antirreflexo de polarização circular acopladas ao vidro externo. A luz do Sol, ao atingir a tela, vibra em todas as direções, mas essa película força a luz a vibrar em apenas um plano helicoidal. Quando o reflexo tenta voltar do interior do display para os olhos do usuário, a película bloqueia essa trajetória de retorno, garantindo que a tela permaneça perfeitamente legível mesmo sob a luz direta do meio-dia.
A tecnologia da tela AMOLED elimina o reflexo solar incômodo manipulando diretamente o fenômeno da:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: D
---
Sensores de oximetria de pulso, muito utilizados em hospitais para medir a oxigenação do sangue de pacientes, funcionam emitindo dois feixes de luz através da pele do dedo: um feixe de luz vermelha e outro de infravermelho. Do outro lado do dedo, um fotodetector mede a quantidade de luz que conseguiu atravessar o tecido sem ser retida. Como a hemoglobina carregada de oxigênio retém mais luz infravermelha e deixa passar a vermelha, o aparelho calcula a saturação com base na energia que foi aprisionada pelo sangue.
O princípio utilizado pelo oxímetro para medir a oxigenação baseia-se na quantidade de luz que sofreu o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) polarização.
E) absorção.
GABARITO: E
---
Em engenharia de tráfego, para evitar acidentes em cruzamentos perigosos com pouca visibilidade, instalam-se grandes espelhos convexos nos postes. Esses espelhos possuem superfícies perfeitamente polidas e curvadas para fora. Quando os raios de luz dos carros atingem o espelho, eles batem e retornam para os olhos dos motoristas em ângulos abertos, permitindo enxergar uma área muito maior da rua transversal (amaciando o campo de visão), embora as imagens pareçam menores e mais distantes.
O fenômeno óptico responsável pela formação das imagens amplas nos espelhos convexos dos cruzamentos é a:
A) difração.
B) refração.
C) reflexão especular.
D) reflexão difusa.
E) polarização.
GABARITO: C
---
Equipamentos de transmissão de TV via satélite operam com antenas parabólicas feitas de telas metálicas vazadas. Os engenheiros projetam os furos dessa tela de modo que sejam significativamente menores que o comprimento de onda do sinal eletromagnético recebido do espaço. Dessa forma, as ondas não conseguem passar direto pelos furos; em vez disso, elas rebatem na malha metálica e convergem perfeitamente para o receptor central (LNB), garantindo a qualidade da imagem na televisão.
O sinal de TV rebate na parabólica e converge para o receptor porque a malha metálica atua gerando o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) polarização.
E) interferência.
GABARITO: C
---
Filtros de luz utilizados em telescópios amadores para observação do planeta Júpiter são feitos de lâminas de vidro coloridas artificialmente. Ao apontar o telescópio, a luz branca refletida pelo planeta atinge o filtro. O vidro colorido deixa passar apenas a faixa de luz azul e retém todas as outras cores do espectro luminoso. Isso aumenta o contraste das faixas de tempestades gasosas do planeta, permitindo que o astrônomo enxergue detalhes atmosféricos que seriam invisíveis a olho nu.
A separação da cor azul pelo filtro do telescópio ocorre porque as outras cores sofreram o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) absorção.
E) polarização.
GABARITO: D
---
Em sistemas de som automotivo de alta fidelidade, os alto-falantes do tipo tweeter (responsáveis pelos sons agudos, como pratos de bateria e vocais finos) são projetados com domos muito pequenos, medindo poucos centímetros. Os engenheiros escolhem esse tamanho reduzido porque as ondas sonoras agudas possuem comprimentos de onda milimétricos. Assim, ao saírem do falante, as ondas conseguem contornar as bordas do próprio aparelho e se espalhar por todo o interior do veículo, evitando que o som agudo fique focado em uma única direção reta.
O projeto dos tweeters busca otimizar o espalhamento dos sons agudos no carro utilizando o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) interferência.
GABARITO: A
---
Sensores de fotometria instalados em relógios inteligentes (smartwatches) monitoram o estresse do usuário medindo a variação do diâmetro dos vasos sanguíneos periféricos na pele do pulso. O sensor dispara um feixe de LED verde. Parte dessa energia penetra no tecido e fica totalmente retida e aprisionada pelas moléculas de hemoglobina, enquanto a fração de luz restante bate nas camadas mais profundas e retorna para o fotodetector do relógio.
O monitoramento do relógio inteligente baseia-se diretamente na quantidade de luz verde que sofreu o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) polarização.
E) absorção.
GABARITO: E
---
Em óticas e laboratórios de lentes, os técnicos utilizam aparelhos chamados lensômetros para medir o grau de óculos. O equipamento projeta um feixe de laser verde perfeitamente retilíneo. Quando esse laser atravessa a lente de vidro curvada dos óculos do paciente, o raio sofre uma mudança imediata em sua velocidade de propagação e desvia de sua trajetória original, convergindo para um ponto exato do sensor que calcula a curvatura da lente.
O desvio sofrido pelo laser ao atravessar a lente de vidro dos óculos do paciente é um exemplo clássico de:
A) difração.
B) refração.
C) reflexão especular.
D) reflexão difusa.
E) polarização.
GABARITO: B
---
Faróis de milha de carros de rali utilizam refletores parabólicos internos fabricados com alumínio perfeitamente polido e espelhado. O objetivo desse componente é coletar a luz emitida pela lâmpada central e, ao fazê-la rebater na parede de alumínio, direcionar todos os raios na mesma direção exata, criando um feixe retilíneo, focado e concentrado capaz de iluminar a estrada a centenas de metros de distância.
O fenômeno óptico que ocorre quando a luz da lâmpada rebate nas paredes polidas do refletor parabólico e retorna direcionada é a:
A) difração.
B) refração.
C) reflexão especular.
D) reflexão difusa.
E) polarização.
GABARITO: C
---
Filtros de luz infravermelha instalados em câmeras de segurança noturnas são feitos de lâminas de policarbonato dopadas quimicamente. Durante o dia, a luz solar branca atinge a lente da câmera. Esse filtro especial permite que apenas a radiação infravermelha invisível atravesse em direção ao sensor eletrônico, enquanto impede a passagem e retém todas as frequências da luz visível colorida, evitando que a imagem diurna fique saturada ou distorcida.
O filtro da câmera noturna elimina a luz visível colorida porque essas ondas sofreram o fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) absorção.
E) polarização.
GABARITO: D
---
Em telecomunicações, as antenas parabólicas residenciais utilizam um receptor central (LNB) sustentado por uma haste exatamente à frente do prato metálico. Quando as micro-ondas enviadas pelo satélite no espaço atingem a superfície curvada e lisa do prato, elas sofrem um rebatimento ordenado e mudam de direção conjuntamente, indo se encontrar exatamente na ponta do receptor, o que garante a recepção limpa do sinal de TV.
O fenômeno ondulatório que ocorre quando as micro-ondas batem na superfície lisa do prato da antena e mudam de direção ordenadamente em direção ao receptor é a:
A) difração.
B) refração.
C) reflexão especular.
D) ressonância.
E) polarização.
GABARITO: C
---
Um engenheiro biomédico projetou um sensor de monitoramento cardíaco colado à pele do pulso do paciente. O dispositivo dispara continuamente um feixe de laser infravermelho invisível que atravessa a epiderme e, ao atingir a fronteira com os vasos sanguíneos em movimento, sofre uma alteração sutil na sua frequência e no seu comprimento de onda ao retornar para o receptor. O computador do aparelho usa essa variação de frequência para calcular a velocidade do fluxo de sangue e os batimentos por minuto.
O funcionamento do sensor cardíaco baseia-se diretamente no mecanismo do(a):
A) efeito Doppler.
B) difração de ondas.
C) polarização da luz.
D) ressonância acústica.
E) interferência destrutiva.
GABARITO: A
---
Em grandes centros de triagem de correspondências, os leitores ópticos de código de barras utilizam um feixe de laser vermelho que varre rapidamente a superfície das embalagens. Quando o laser atinge as barras pretas, a energia luminosa é totalmente retida pelo pigmento escuro. Já quando atinge as barras brancas, a luz bate e retorna inteiramente para um sensor eletrônico. O computador converte essa diferença entre luz retida e luz retornada em números para identificar o destino da encomenda.
O fenômeno que ocorre quando o laser atinge as barras pretas da etiqueta e tem sua energia retida pelo pigmento é a:
A) difração.
B) refração.
C) reflexão.
D) polarização.
E) absorção.
GABARITO: E
---
Janelas de salas de reuniões de tribunais utilizam vidros laminados duplos com uma película interna especial de cristais líquidos. Ao acionar um interruptor de parede, o sistema aplica uma corrente elétrica que orienta as moléculas dessa película em uma única direção fixa. Esse alinhamento impede a passagem das ondas de luz que vibram em planos perpendiculares ao eixo molecular, reduzindo drasticamente a luminosidade da sala e impedindo que pessoas do lado de fora vejam os documentos sobre a mesa.
O fenômeno óptico manipulado eletronicamente para controlar a privacidade da sala de reuniões é a:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: D
---
Técnicos de manutenção de redes de internet utilizam um aparelho chamado OTDR para testar a integridade de cabos subterrâneos. O equipamento injeta um pulso de laser em uma das pontas do filamento de vidro transparente. Devido à diferença geométrica e de densidade entre o núcleo e a casca do cabo, a luz sofre desvios sucessivos de 100% nas paredes internas, viajando quilômetros presa no interior do vidro sem conseguir vazar pelas laterais, mesmo quando o cabo faz curvas acentuadas sob as ruas.
O aprisionamento e a condução do laser por dentro das curvas do filamento de vidro ocorrem devido à:
A) difração das ondas.
B) refração total do meio.
C) reflexão interna total.
D) dispersão cromática da luz.
E) interferência construtiva contínua.
GABARITO: C
---
Ao projetar o revestimento interno de salas de cinema de alta fidelidade, arquitetos instalam painéis de madeira perfurada preenchidos com mantas de fibra de vidro espessa nas paredes laterais. O objetivo desse arranjo é fazer com que as ondas sonoras emitidas pelas caixas de som de alta potência batam nessas superfícies e percam sua energia mecânica, que se dissipa na forma de calor no interior das fibras do material, evitando que o som retorne para a plateia e crie ecos borrados.
O princípio físico utilizado pelos painéis das paredes para eliminar o eco na sala de cinema é a:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) absorção.
GABARITO: E
---
Durante uma inspeção de trânsito à noite, um policial aponta sua lanterna tática para a placa de um veículo. A placa possui uma pintura retroreflexiva composta por milhões de microesferas de vidro texturizadas. Quando a luz da lanterna atinge essas esferas, os raios luminosos batem e retornam desordenadamente em múltiplos ângulos na direção geral do policial, fazendo com que os números da placa pareçam brilhar intensamente no escuro, permitindo a leitura clara da identificação.
O fenômeno óptico responsável pelo retorno desordenado e espalhado da luz nas microesferas da placa é a:
A) difração.
B) refração.
C) reflexão especular.
D) reflexão difusa.
E) polarização.
GABARITO: D
---
Em exames de ecocardiograma, o transdutor do aparelho encostado no peito do paciente emite ondas de ultrassom que penetram no corpo humano. Ao passar do tecido muscular do coração para o sangue contido no interior das cavidades cardíacas, a onda acústica sofre uma alteração drástica em sua velocidade de propagação e no seu comprimento de onda devido à diferença de densidade dos meios, enquanto a frequência do aparelho permanece rigorosamente constante.
O fenômeno ondulatório sofrido pelo ultrassom ao passar do músculo cardíaco para o sangue é a:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) polarização.
GABARITO: B
---
Laboratórios de criminalística utilizam espectrofotômetros para identificar substâncias proibidas em amostras apreendidas. O equipamento faz um feixe de luz branca atravessar um prisma de vidro de alta precisão. Ao passar pelo material, a luz branca se decompõe perfeitamente nas sete cores do arco-íris, porque cada cor viaja com uma velocidade ligeiramente diferente dentro do vidro, sofrendo desvios separados que são detectados pelo computador.
A decomposição da luz branca em suas cores constituintes ao atravessar o prisma de vidro do aparelho é a:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: C
---
Moradores de uma casa localizada em um vale profundo atrás de uma grande colina rochosa conseguem sintonizar canais de televisão aberta usando uma antena de alumínio comum instalada no telhado. Os engenheiros de telecomunicações explicam que isso é possível porque as ondas eletromagnéticas de alta frequência emitidas pela torre da cidade, ao atingirem o topo e as quinas da colina, conseguem contornar o obstáculo de pedra e se propagar em direção às casas localizadas abaixo.
O fenômeno que permite às ondas de televisão contornarem a quina da colina e chegarem até a antena é a:
A) difração.
B) refração.
C) reflexão.
D) dispersão.
E) polarização.
GABARITO: A
---
Ao observar uma película fina de óleo diesel flutuando sobre uma poça de água em um posto de combustíveis em um dia ensolarado, um motorista nota que a superfície exibe faixas de cores brilhantes e mutáveis. Esse efeito visual ocorre porque a luz do Sol reflete tanto na face superior da camada de óleo quanto na face inferior (onde o óleo toca a água). Ao retornarem juntas para o olho do motorista, essas ondas se cruzam no ar, somando a intensidade de algumas cores e cancelando outras.
A formação das cores brilhantes na fina película de óleo sobre a água deve-se ao fenômeno da:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: E
---
Um engenheiro acústico foi contratado para reduzir o barulho ensurdecedor que vinha da sala de máquinas de uma fábrica de tecidos e que atrapalhava os escritórios vizinhos. Em vez de erguer paredes grossas de concreto, ele cobriu a sala com painéis estruturais cheios de microperfurações acoplados a mantas de lã de vidro. Essa intervenção reduziu o barulho porque a energia mecânica das ondas sonoras colide com o material e deixa de ser transmitida para o ambiente externo.
A propriedade física do material utilizado pelo engenheiro para solucionar o problema do barulho na fábrica baseia-se na ocorrência do fenômeno da:
A) difração.
B) refração.
C) reflexão.
D) ressonância.
E) absorção.
GABARITO: E
---
Ao comprar óculos para a prática de pesca esportiva em rios e lagoas, um esportista escolheu lentes equipadas com uma tecnologia que bloqueia o brilho intenso da luz solar que reflete horizontalmente na superfície plana da água. Ao utilizar os óculos sob o sol do meio-dia, o pescador consegue enxergar com clareza os peixes nadando abaixo da linha d'água, eliminando completamente a cegueira temporária causada pelo reflexo da luz na lagoa.
A tecnologia aplicada nas lentes desses óculos de pesca elimina o incômodo do reflexo solar manipulando diretamente o fenômeno da:
A) difração.
B) refração.
C) dispersão.
D) polarização.
E) interferência.
GABARITO: D
---
Em sistemas de segurança residencial, os sensores de presença instalados acima das portas de garagens funcionam emitindo um feixe invisível de laser infravermelho em direção a um pequeno receptor fixado no muro oposto. Sempre que um carro ou um pedestre atravessa o portão, a linha invisível de luz é interrompida, impedindo que o sinal luminoso complete sua trajetória retilínea no espaço até o detector, o que aciona o alarme imediatamente.
O funcionamento desse dispositivo de segurança perimetral baseia-se na interrupção direta da:
A) difração do feixe.
B) refração do meio.
C) transmissão da luz.
D) polarização da onda.
E) interferência do sinal.
GABARITO: C
---
Um motorista trafegando por uma rodovia asfaltada em um dia extremamente quente e ensolarado avista, a algumas centenas de metros à sua frente, uma miragem que faz o chão parecer completamente molhado, espelhando o céu azul no horizonte. O efeito ocorre porque o calor intenso do asfalto aquece a camada de ar logo acima dele, alterando sua densidade em relação às camadas superiores e forçando os raios de luz solar a sofrerem desvios contínuos em sua trajetória antes de tocarem a pista.
O fenômeno óptico atmosférico responsável por desviar a trajetória dos raios de luz e gerar o efeito visual da miragem na rodovia é a:
A) difração.
B) refração.
C) reflexão especular.
D) polarização.
E) interferência.
GABARITO: B
---
Uma empresa de engenharia civil instalou grandes espelhos esféricos convexos nos postes localizados nos cantos de um estacionamento subterrâneo de um shopping. A instalação desse modelo de espelho polido foi estratégica para os motoristas, pois a geometria de sua superfície permite captar os raios de luz vindos de corredores transversais ocultos e devolvê-los de forma organizada para os condutores, ampliando significativamente a área visível do cruzamento.
A ampliação do campo de visão dos motoristas nas curvas do estacionamento ocorre devido à ocorrência do fenômeno da:
A) difração das ondas.
B) refração do vidro.
C) reflexão especular.
D) reflexão difusa.
E) polarização linear.
GABARITO: C
""".strip()

TOPICOS_OPTICA = [
    # Lote 8 (36-40)
    "polarizacao", "refracao", "interferencia", "reflexao_difusa", "reflexao_interna_total",
    # Lote 9 (41-45)
    "reflexao", "refracao", "reflexao_difusa", "reflexao_difusa", "polarizacao",
    # Lote 10 (46-50)
    "transmissao", "refracao", "difracao", "refracao", "polarizacao",
    # Lote 11 (51-55)
    "absorcao", "reflexao_especular", "reflexao", "absorcao", "difracao",
    # Lote 12 (56-60)
    "absorcao", "refracao", "reflexao_especular", "absorcao", "reflexao_especular",
    # Revisao Geral (10)
    "efeito_doppler", "absorcao", "polarizacao", "reflexao_interna_total", "absorcao",
    "reflexao_difusa", "refracao", "dispersao", "difracao", "interferencia",
    # Transicao Nivel Medio (5)
    "absorcao", "polarizacao", "transmissao", "refracao", "reflexao_especular",
]

assert OPTICA_TEXTO.count("GABARITO:") == 40 == len(TOPICOS_OPTICA), (
    OPTICA_TEXTO.count("GABARITO:"), len(TOPICOS_OPTICA)
)

# ============================================================
# ECOLOGIA -- 110 questoes confirmadas (ver docstring: faltam os dois
# blocos de 5 que a transcricao apresentou mas nunca teve resposta
# graduada -- "56 a 60" e "86 a 90" da contagem da outra IA).
# ============================================================

ECOLOGIA_TEXTO = r"""
O uso indiscriminado do inseticida DDT em lavouras nas décadas passadas provocou a contaminação de ecossistemas aquáticos vizinhos através do escoamento da água da chuva. Cientistas monitoraram a concentração desse composto químico nos tecidos dos seres vivos locais e constataram que, embora a água apresentasse níveis quase indetectáveis do poluente, os organismos apresentavam contaminação severa, sendo os maiores índices encontrados nos gaviões-pescadores, que se alimentavam exclusivamente de peixes carnívoros.
O acúmulo progressivo desse poluente ao longo da estrutura trófica ocorre porque o composto é lipossolúvel e:
A) diminui sua concentração devido à perda de energia em cada nível trófico.
B) é excretado rapidamente pelos produtores antes de atingir os consumidores.
C) acumula-se em maior quantidade nos organismos do topo da cadeia alimentar.
D) sofre degradação bacteriana acelerada nos tecidos dos consumidores primários.
E) estimula a eficiência ecológica dos herbívoros ao longo do fluxo unidirecional.
GABARITO: C
---
O descarte inadequado de esgoto doméstico rico em matéria orgânica nas águas de uma lagoa urbana provocou uma alteração drástica no ecossistema local. Em poucos dias, a superfície da lagoa foi totalmente coberta por uma camada densa de algas verdes (florações), bloqueando a entrada de luz solar. Esse bloqueio desencadeou a morte da vegetação submersa, seguida pela proliferação de bactérias aeróbicas decompositoras, culminando na mortandade em massa dos peixes por asfixia.
A morte dos peixes nessa lagoa ocorre como consequência direta da:
A) redução drástica dos níveis de oxigênio dissolvido na água devido à decomposição.
B) liberação excessiva de gás carbônico pelas algas fotossintetizantes da superfície.
C) contaminação dos tecidos dos consumidores secundários por metais pesados do esgoto.
D) falta de nutrientes minerais para a sobrevivência dos microrganismos aeróbicos.
E) competição intraespecífica por espaço entre as populações de peixes da lagoa.
GABARITO: A
---
O mexilhão-zebra (Dreissena polymorpha), um pequeno molusco originário do Mar Cáspio, foi introduzido acidentalmente nos Grandes Lagos da América do Norte através da água de lastro de navios cargueiros. Por não encontrar predadores ou parasitas naturais nesse novo ambiente, a espécie proliferou descontroladamente, cobrindo substratos rochosos e tubulações industriais, alterando a transparência da água e reduzindo drasticamente as populações de bivalves nativos que dependiam dos mesmos micro-habitats.
A redução das populações de moluscos nativos nos Grandes Lagos é explicada pelo fato de a espécie exótica:
A) estabelecer uma relação parasitária direta com os bivalves locais.
B) competir por espaço e recursos alimentares com as espécies nativas.
C) sofrer mutações genéticas causadas pela poluição industrial da água.
D) atuar como produtora primária, saturando a base da pirâmide de energia.
E) apresentar uma taxa de reprodução limitada pela capacidade de suporte local.
GABARITO: B
---
Em uma floresta tropical equilibrada, analistas mapearam o fluxo de energia entre os componentes bióticos do ecossistema. Eles registraram a quantidade de energia fixada pelas plantas produtoras através da fotossíntese e acompanharam sua transferência para os herbívoros e, sequencialmente, para os carnívoros. Os dados comprovaram que a quantidade de energia disponível para o metabolismo dos seres vivos diminui drasticamente a cada passo da transferência.
A redução da energia disponível nos níveis tróficos superiores deve-se ao fato de que a energia:
A) acumula-se nos tecidos biológicos na forma de poluentes não biodegradáveis.
B) é dissipada na forma de calor e processos metabólicos em cada nível trófico.
C) aumenta sua concentração à medida que caminha no fluxo cíclico do ecossistema.
D) é reaproveitada integralmente pelos decompositores na base da cadeia alimentar.
E) fica retida exclusivamente nos consumidores do topo da pirâmide de números.
GABARITO: B
---
A construção de uma rodovia cortando uma área de preservação ambiental dividiu uma população de pequenos roedores em dois grupos isolados geograficamente. Além de impedir o fluxo gênico entre as populações, a fragmentação do habitat reduziu drasticamente a área de vida disponível para os animais, alterando a oferta de abrigos e alimentos, o que tornou ambas as populações muito mais vulneráveis a gargalos populacionais e extinções locais.
O impacto imediato da fragmentação desse habitat sobre a sobrevivência dos roedores deve-se à:
A) introdução de espécies exóticas competidoras na região central da rodovia.
B) ocorrência de bioacumulação de poluentes pesados nos tecidos dos roedores.
C) redução dos recursos disponíveis e isolamento das populações nativas.
D) aceleração da taxa de mutações genéticas benéficas nos grupos isolados.
E) estabilização da capacidade de suporte devido ao aumento do espaço físico.
GABARITO: C
---
Pesquisadores coletaram amostras de água e de tecidos de diversos seres vivos ao longo do leito de um rio que corta uma região de garimpo ilegal de ouro na Amazônia. As análises laboratoriais indicaram que a concentração de metilmercúrio, um metal pesado altamente tóxico, nos tecidos dos botos-cor-de-rosa (grandes predadores que ocupam o topo da cadeia alimentar) era cerca de dez mil vezes maior do que a concentração encontrada na água do próprio rio.
O fenômeno biológico responsável por essa disparidade na concentração do poluente tóxico entre a água e o topo da cadeia alimentar é a:
A) eutrofização do ecossistema aquático.
B) magnificação trófica do metal pesado.
C) eficiência ecológica dos produtores primários.
D) dissipação térmica ao longo do fluxo de matéria.
E) competição interespecífica entre os consumidores.
GABARITO: B
---
O uso excessivo de adubos químicos e fertilizantes agrícolas à base de nitratos e fosfatos em plantações de cana-de-açúcar resultou no escoamento desses nutrientes para um rio próximo após uma forte tempestade. Dias depois, os moradores locais notaram que a água do rio ficou completamente verde e opaca, com um cheiro forte. Logo em seguida, ocorreu uma mortandade generalizada de peixes, que boiavam na superfície sem apresentar sinais de ferimentos ou infecções.
A morte dos peixes nesse cenário agrícola é explicada pelo(a):
A) acúmulo de toxinas bioacumulativas nos tecidos dos produtores.
B) aumento do oxigênio dissolvido causado pela fotossíntese das plantas.
C) esgotamento do oxigênio na água devido à proliferação de bactérias decompositoras.
D) introdução acidental de uma espécie exótica herbívora na bacia hidrográfica.
E) redução da taxa de mutações genéticas nas populações de peixes nativos.
GABARITO: C
---
O javali-europeu (Sus scrofa), animal de grande porte trazido originalmente para o Brasil para a criação em cativeiro, escapou e espalhou-se por diversas regiões do país. Sem predadores naturais eficientes no território nacional, a espécie multiplicou-se rapidamente. Os javalis escavam o solo em busca de raízes, destroem nascentes de rios e devoram plantações e ovos de aves nativas que nidificam no chão, reduzindo drasticamente os recursos disponíveis para os porcos-do-mato locais.
O impacto negativo causado pela introdução do javali no ecossistema brasileiro ocorre porque esse animal:
A) atua como parasita exclusivo dos mamíferos nativos da floresta.
B) estabelece uma cooperação mútua com a flora original da região.
C) compete por espaço e recursos alimentares com as espécies nativas.
D) converte a energia solar na base da pirâmide ecológica do ambiente.
E) sofre um controle populacional rigoroso pela capacidade de suporte do solo.
GABARITO: C
---
Ao analisar a quantidade de biomassa e energia contida em uma plantação de milho, um agrônomo calculou que apenas uma fração muito pequena da energia solar captada pelas folhas do milharal é repassada para as lagartas que se alimentam das espigas. Ele explicou que a maior parte da energia química produzida pela planta é gasta no seu próprio crescimento, respiração celular e transpiração, deixando de ficar disponível para o próximo nível da cadeia.
A redução drástica da energia disponível para as lagartas deve-se ao fato de que a energia no ecossistema:
A) acumula-se de forma cíclica entre os consumidores e produtores.
B) é dissipada na forma de calor e processos metabólicos da própria planta.
C) aumenta sua concentração à medida que caminha em direção aos decompositores.
D) fica retida de forma permanente nos tecidos dos consumidores primários.
E) é reciclada integralmente pelas bactérias do solo após a queda das folhas.
GABARITO: B
---
A expansão de áreas de pastagem para a pecuária bovina provocou o isolamento de pequenos fragmentos de Mata Atlântica, cercados por pastos abertos. Biólogos constataram que os pequenos primatas que viviam no interior da floresta não conseguiam cruzar as áreas abertas de pasto por medo de predadores, ficando confinados em pequenos grupos. Esse isolamento diminuiu a quantidade de parceiros disponíveis para reprodução e reduziu o acesso a árvores frutíferas na época de seca.
O impacto imediato desse isolamento provocado pela pecuária sobre a sobrevivência dos primatas deve-se à:
A) introdução de espécies exóticas de árvores frutíferas no interior da floresta.
B) ocorrência de bioacumulação de inseticidas nos tecidos musculares dos primatas.
C) fragmentação do habitat, que isola as populações e reduz os recursos.
D) aceleração da taxa de reprodução provocada pelo estresse ambiental.
E) eliminação dos decompositores, que satura a matéria orgânica no solo.
GABARITO: C
---
Um incêndio florestal de grandes proporções destruiu completamente uma área de cerrado, deixando o solo coberto de cinzas e sem nenhuma vegetação viva. Após alguns meses, pequenas gramíneas e plantas rasteiras começaram a brotar na terra queimada. Anos depois, arbustos começaram a surgir e, décadas mais tarde, a floresta de cerrado original restabeleceu-se por completo, atingindo novamente o equilíbrio ecológico estável.
O processo de recuperação gradual da biodiversidade e da estrutura da comunidade vegetal após a destruição pelo fogo é denominado:
A) sucessão primária.
B) sucessão secundária.
C) magnificação trófica.
D) equilíbrio intraespecífico.
E) competição interespecífica.
GABARITO: B
---
Plantas da família das leguminosas (como o feijão e a soja) possuem pequenos nódulos em suas raízes que abrigam colônias de bactérias do gênero Rhizobium. Essas bactérias são capazes de captar o nitrogênio gasoso da atmosfera e transformá-lo em amônia, que a planta utiliza para produzir suas proteínas. Em troca, a planta fornece às bactérias os açúcares que produz na fotossíntese. Essa associação é tão íntima que nenhuma das duas espécies consegue sobreviver isoladamente no ambiente.
A relação ecológica estabelecida entre as plantas leguminosas e as bactérias fixadoras de nitrogênio é um caso de:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) parasitismo clássico.
GABARITO: A
---
Em florestas temperadas, algumas espécies de aves de pequeno porte constroem seus ninhos no interior de buracos localizados nos troncos de árvores centenárias. As aves encontram nesses buracos proteção contra a chuva e contra predadores terrestres, além de um local seguro para chocar seus ovos. Para a árvore, a presença dos ninhos nos buracos do tronco não gera nenhum tipo de benefício, mas também não causa nenhum dano ou prejuízo ao seu desenvolvimento.
A relação ecológica em que as aves utilizam o corpo da árvore como abrigo, sem causar prejuízos ou benefícios ao hospedeiro, é chamada de:
A) mutualismo.
B) amensalismo.
C) parasitismo.
D) inquilinismo.
E) competição.
GABARITO: D
---
Biólogos introduziram uma população de peixes carnívoros exóticos em um lago artificial que continha uma comunidade equilibrada de pequenos peixes herbívoros nativos. Inicialmente, a população de peixes exóticos cresceu exponencialmente devido à abundância de alimento. No entanto, após alguns meses, a população de peixes herbívoros locais reduziu-se drasticamente, o que fez os recursos escassearem e provocou, consequentemente, uma queda acentuada no número de peixes carnívoros exóticos.
A oscilação e o controle mútuo no tamanho das populações de peixes exóticos e nativos no lago ocorrem devido à relação de:
A) canibalismo.
B) amensalismo.
C) comensalismo.
D) predação.
E) mutualismo.
GABARITO: D
---
Agricultores que cultivam laranjiras em grande escala sofrem com o ataque de pulgões, pequenos insetos que sugam a seiva das folhas, enfraquecendo as árvores e estragando os frutos. Para combater a praga sem o uso de agrotóxicos químicos, os produtores decidiram liberar milhares de joaninhas na plantação. As joaninhas alimentam-se ativamente dos pulgões, controlando a população da praga de forma natural e devolvendo a produtividade ao laranjal.
A estratégia utilizada pelos agricultores para salvar o laranjal baseia-se no controle biológico por meio da relação de:
A) parasitismo.
B) amensalismo.
C) mutualismo.
D) predação.
E) competição.
GABARITO: D
---
Uma erupção vulcânica em uma ilha isolada cobriu grande parte do território com uma espessa camada de lava ardente. Após o resfriamento, a rocha magmática nua ficou completamente exposta, sem qualquer vestígio de solo ou matéria orgânica. Décadas depois, os primeiros líquens começaram a colonizar a rocha nua. Com o tempo, a ação desses organismos começou a esmiuçar a rocha, permitindo o acúmulo de poeira e a formação do primeiro solo, onde gramíneas puderam crescer.
O processo de colonização biológica que se inicia do zero absoluto sobre a rocha vulcânica nua é classificado como:
A) sucessão primária.
B) sucessão secundária.
C) magnificação trófica.
D) equilíbrio trófico cíclico.
E) competição intraespecífica.
GABARITO: A
---
Pássaros conhecidos como "pássaros-palito" entram voluntariamente na boca aberta de crocodilos africanos para se alimentarem de restos de carne e parasitas presos entre os dentes dos répteis. Para o pássaro, a relação garante alimento fácil; para o crocodilo, funciona como uma higiene bucal que evita infecções. Embora a troca de favores seja benéfica para ambos, os pássaros conseguem sobreviver perfeitamente na natureza comendo outros insetos, e os crocodilos não morrem se os pássaros não aparecerem.
A relação ecológica harmônica e opcional estabelecida entre o pássaro-palito e o crocodilo é chamada de:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) parasitismo.
GABARITO: D
---
Orquídeas silvestres crescem fixadas nos galhos mais altos de grandes árvores no interior da Mata Atlântica. Ao se posicionarem no topo do dossel florestal, as orquídeas conseguem captar uma quantidade muito maior de luz solar para realizar sua fotossíntese. Suas raízes apenas abraçam a casca do tronco para sustentação, sem retirar nenhuma gota de seiva ou nutriente da árvore hospedeira, que permanece indiferente à presença da planta.
A associação vegetal em que a orquídea utiliza o tronco da árvore apenas como suporte para alcançar a luz, sem causar danos ou benefícios ao hospedeiro, é um caso de:
A) mutualismo.
B) epifitismo.
C) amensalismo.
D) parasitismo.
E) competição.
GABARITO: B
---
Larvas de vespas da espécie Cotesia congregata eclodem de ovos depositados por uma fêmea adulta diretamente sob a pele de lagartas-do-tomateiro. À medida que se desenvolvem, as micro-larvas alimentam-se dos tecidos internos e dos fluidos corporais da lagarta, mantendo-a viva o maior tempo possível. Próximo à metamorfose, as larvas perfuram a pele da presa para tecer seus casulos externos, o que culmina inevitavelmente na morte da lagarta enfraquecida.
A interação biológica descrita entre as larvas da vespa e a lagarta-do-tomateiro caracteriza a relação de:
A) predação.
B) mutualismo.
C) parasitismo.
D) comensalismo.
E) amensalismo.
GABARITO: C
---
Tubarões-brancos costumam ser acompanhados de perto por peixes pilotos conhecidos como rêmoras. Esses pequenos peixes possuem uma ventosa no topo da cabeça que lhes permite fixarem-se temporariamente na pele do predador. À medida que o tubarão ataca suas presas, as rêmoras se soltam para abocanhar os pedaços menores de carne que flutuam na água e que seriam ignorados pelo tubarão. O tubarão não sofre nenhum prejuízo e não recebe nenhum benefício com o banquete dos pequenos peixes.
A relação ecológica em que as rêmoras aproveitam os restos alimentares deixados pelo tubarão, sem prejudicá-lo ou ajudá-lo, é denominada:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) amensalismo.
E) parasitismo.
GABARITO: C
---
Em savanas africanas, bandos de babuínos e antílopes costumam pastar juntos na mesma região. Os babuínos possuem uma visão excelente do alto das árvores, enquanto os antílopes têm um olfato e audição apuradíssimos no solo. Quando um babuíno avista um leopardo, emite um grito de alerta que avisa os antílopes. Da mesma forma, se o antílope sente o cheiro do predador, corre e alerta os babuínos. Ambos se beneficiam imensamente da proteção mútua, embora consigam sobreviver isolados em outras áreas da reserva.
A associação harmônica e facultativa estabelecida entre as populações de babuínos e antílopes é classificada como:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) amensalismo.
GABARITO: D
---
Plantas conhecidas como bromélias crescem fixadas sobre os galhos de grandes árvores na floresta tropical. Elas utilizam o topo das árvores estritamente como uma plataforma física para receber luz solar e realizar fotossíntese. Suas raízes são adaptadas apenas para prender a planta na casca protetora do galho, sem sugar fluidos ou causar qualquer tipo de enfraquecimento ou benefício à árvore hospedeira, que permanece inalterada.
A relação ecológica observada entre as bromélias e as árvores hospedeiras na floresta é um caso de:
A) mutualismo.
B) epifitismo.
C) amensalismo.
D) parasitismo.
E) predação.
GABARITO: B
---
Fungos do gênero Penicillium produzem e secretam naturalmente uma substância química chamada penicilina no solo ao seu redor. Essa substância inibe fortemente o crescimento e provoca a destruição das paredes celulares de colônias de bactérias vizinhas. Para o fungo, a eliminação das bactérias ocorre de forma acidental através do seu metabolismo, sem que ele retire delas nenhum tipo de nutriente ou benefício direto para a sua sobrevivência.
A interação biológica em que o fungo prejudica e impede o desenvolvimento das bactérias sem obter vantagens diretas é denominada:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) competição.
GABARITO: B
---
Uma área de pastagem abandonada por agricultores começou a ser colonizada gradualmente pela vegetação nativa da região. No primeiro ano, o solo foi tomado por ervas rasteiras de crescimento rápido. No quinto ano, pequenos arbustos começaram a sombrear o capim antigo. Após trinta anos, uma floresta secundária jovem restabeleceu-se no local, apresentando uma comunidade clímax estável e em perfeito equilíbrio dinâmico com o clima local.
O processo ordenado de modificação da comunidade biológica ao longo do tempo na área de pastagem antiga exemplifica uma:
A) sucessão primária.
B) sucessão secundária.
C) magnificação trófica.
D) competição interespecífica.
E) interferência ecológica destrutiva.
GABARITO: B
---
Lobos-cinzentos reintroduzidos em um parque nacional caçam ativamente grandes alces para garantir a alimentação da alcateia. Os biólogos do parque notaram que a atividade de caça dos lobos mantém a população de alces controlada, impedindo que esses herbívoros destruam toda a vegetação de brotos de árvores nas margens dos rios, o que estabiliza o tamanho de ambas as populações ao longo das estações do ano.
A relação ecológica responsável pelo controle populacional dos alces pelos lobos no parque nacional é a:
A) predação.
B) mutualismo.
C) amensalismo.
D) comensalismo.
E) parasitismo.
GABARITO: A
---
Em florestas tropicais de grande altitude, certas espécies de árvores da família das mirtáceas liberam pelas suas raízes e folhas caídas compostos químicos voláteis conhecidos como terpenos. Essas substâncias penetram no solo ao redor e inibem drasticamente a germinação de sementes e o crescimento de raízes de qualquer outra planta herbácea rasteira vizinha. Para a árvore arbórea, a secreção dessas substâncias ocorre como um subproduto natural de seu metabolismo de defesa contra insetos, sem que ela retire nenhum nutriente ou benefício das plantas herbáceas que foram eliminadas.
A interação ecológica estabelecida entre a árvore que secreta os terpenos e as plantas herbáceas vizinhas é um caso de:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) competição.
GABARITO: B
---
Pássaros conhecidos como "anu-preto" são frequentemente avistados pousados sobre o lombo de bois e cavalos em pastagens brasileiras. Os pássaros alimentam-se ativamente de carrapatos e moscas que infestam a pele do gado, obtendo uma fonte abundante de proteínas de forma fácil. Para os grandes mamíferos, a presença das aves é extremamente vantajosa, pois reduz o desconforto e o risco de infecções causadas pelos parasitas. No entanto, o gado sobrevive sem os pássaros, e os anus-pretos também se alimentam de insetos no capim se o gado não estiver por perto.
A relação ecológica harmônica, benéfica para ambos os lados, mas que não é obrigatória para a sobrevivência de nenhuma das espécies, caracteriza a:
A) protocooperação.
B) inquilinismo.
C) comensalismo.
D) ressonância.
E) mutualismo.
GABARITO: A
---
O rompimento de uma barragem de rejeitos de mineração cobriu uma vasta área de vegetação nativa com uma camada espessa de lama tóxica e estéril, dizimando toda a fauna e flora locais. Após alguns anos de chuvas intensas que lavaram parte dos contaminantes na superfície, o solo argiloso antigo que permaneceu por baixo começou a ser colonizado por briófitas e gramíneas pioneiras de crescimento rápido, iniciando uma lenta reconstrução da comunidade biológica.
O processo de restauração ecológica da comunidade vegetal que ocorre sobre o solo remanescente após o desastre da lama de rejeitos é classificado como uma:
A) sucessão primária.
B) sucessão secundária.
C) magnificação trófica.
D) competição interespecífica.
E) interferência intraespecífica.
GABARITO: B
---
O fenômeno conhecido como "Maré Vermelha" ocorre em regiões costeiras devido à proliferação excessiva e descontrolada de certas microalgas dinoflageladas marinhas, estimulada pelo excesso de nutrientes na água. Essas algas produzem e liberam na água do mar toxinas potentes que bloqueiam o sistema nervoso de peixes, moluscos e mamíferos marinhos, causando mortandade generalizada da fauna local. Para as microalgas, a morte dos peixes ocorre de forma acidental e não gera nenhuma vantagem nutricional ou metabólica direta.
A interação biológica descrita entre as microalgas que liberam toxinas e a fauna marinha afetada configura a relação de:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) predação.
GABARITO: B
---
Em savanas tropicais, grandes bandos de avestruzes e zebras costumam compartilhar as mesmas áreas de pastagem para se protegerem de grandes felinos. O avestruz possui uma visão panorâmica fantástica devido à sua altura, mas tem um olfato ruim. A zebra tem uma audição e olfato aguçadíssimos, mas não enxerga bem de longe. Quando um dos dois percebe a aproximação de um leão e foge, o outro bando reage imediatamente e escapa do ataque. Ambas as populações aumentam suas chances de sobrevivência com essa vigilância mútua, embora consigam viver sozinhas em outras regiões.
A associação ecológica harmônica e facultativa observada entre as avestruzes e as zebras na savana é chamada de:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) amensalismo.
GABARITO: D
---
Cupins são insetos conhecidos por digerirem a celulose da madeira de troncos e móveis antigos. No entanto, os cupins não possuem os genes necessários para produzir a enzima celulase. A digestão só ocorre porque o intestino desses insetos é habitado por protozoários flagelados do gênero Trichonympha, que produzem a enzima e digerem a madeira, liberando os nutrientes para o cupim. Em troca, o cupim fornece abrigo e alimento constante aos protozoários. Se forem separados artificialmente em laboratório, tanto os cupins quanto os protozoários morrem em poucos dias.
A associação íntima e vital estabelecida entre os cupins e os protozoários que habitam seu trato digestório é classificada como:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) parasitismo.
GABARITO: A
---
Peixes conhecidos como agulhões (Carapus) utilizam o corpo de pepinos-do-mar (animais invertebrados de corpo mole que vivem no fundo do oceano) como esconderijo contra predadores. Quando o perigo se aproxima, o agulhão entra nadando de ré pelo ânus do pepino-do-mar, ficando protegido em sua cavidade digestiva interna. Para o pepino-do-mar, a entrada e saída do peixe em seu corpo não gera nenhum tipo de benefício, mas também não causa nenhuma lesão, dor ou prejuízo ao seu metabolismo.
A relação ecológica em que o agulhão utiliza o corpo do pepino-do-mar estritamente como abrigo seguro, sem ajudá-lo ou prejudicá-lo, configura o:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) parasitismo.
GABARITO: D
---
Uma ilha vulcânica recém-formada no Oceano Pacífico, composta inteiramente por rochas magmáticas nuas e estéreis, começou a receber suas primeiras formas de vida. Esporos de líquens e briófitas trazidos pelo vento fixaram-se na superfície áspera da rocha vulcânica. Ao longo de décadas, o metabolismo desses organismos pioneiros liberou ácidos orgânicos que iniciaram a degradação física da rocha, misturando fragmentos minerais à matéria orgânica morta e criando a primeira fina camada de solo da ilha.
O processo de colonização ecológica que se inicia do marco zero sobre a rocha vulcânica nua, sem solo pré-existente, é denominado:
A) sucessão primária.
B) sucessão secundária.
C) magnificação trófica.
D) competição interespecífica.
E) interferência intraespecífica.
GABARITO: A
---
Hienas e urubus-de-cabeça-preta são frequentemente observados ao redor das carcaças de grandes mamíferos (como zebras e gnus) que foram caçados e parcialmente devorados por leões nas savanas. Assim que os leões se fartam e abandonam a presa, esses animais necrófagos aproximam-se para rasgar os tecidos restantes e comer os pedaços de carne e ossos deixados para trás, limpando o ambiente. Os leões permanecem completamente indiferentes ao banquete das hienas e urubus com os restos.
A interação em que os animais necrófagos alimentam-se estritamente dos restos orgânicos deixados pelo predador, sem prejudicar ou beneficiar o caçador original, é um caso de:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) amensalismo.
E) predação.
GABARITO: C
---
Uma espécie de planta trepadeira exótica foi introduzida em uma reserva florestal urbana. Por não possuir insetos herbívoros ou fungos parasitas que atacassem suas folhas nesse novo ecossistema, a trepadeira cresceu descontroladamente, subindo pelos troncos das árvores nativas e cobrindo completamente suas copas. Esse tapete de folhas exóticas bloqueou a entrada de luz solar, impedindo as árvores nativas de realizarem fotossíntese, o que causou o enfraquecimento e a morte de dezenas de espécimes locais que disputavam a luminosidade da floresta.
O impacto severo causado pela trepadeira exótica sobre as árvores nativas na disputa pela luz solar é explicado pela relação de:
A) predação.
B) mutualismo.
C) amensalismo.
D) comensalismo.
E) competição.
GABARITO: E
---
Durante o verão, praias do litoral catarinense registraram manchas escuras na água provocadas pelo crescimento explosivo de microalgas dinoflageladas. Os biólogos notaram que essas algas, ao realizarem seu metabolismo normal, liberam substâncias químicas altamente tóxicas na água que paralisam os músculos respiratórios de peixes e crustáceos nativos, gerando uma grande mortandade. Para as microalgas, a eliminação dos peixes ocorre de forma totalmente involuntária, não trazendo nenhuma vantagem de espaço ou nutriente.
A relação estabelecida entre as microalgas dinoflageladas e a fauna marinha afetada pelas toxinas é um caso de:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) competição.
GABARITO: B
---
Em plantações de eucalipto voltadas para a produção de celulose, as árvores são plantadas muito próximas umas das outras. À medida que crescem, suas raízes profundas absorvem rapidamente quase toda a água e os nutrientes minerais disponíveis nas camadas superficiais do solo. Devido a esse consumo agressivo, pequenas samambaias e arbustos nativos que tentam crescer embaixo dos eucaliptos acabam morrendo secos pela escassez crônica desses recursos hídricos e minerais.
O desaparecimento dos arbustos e samambaias sob a floresta de eucaliptos é explicado pela relação de:
A) predação.
B) mutualismo.
C) amensalismo.
D) comensalismo.
E) competição.
GABARITO: E
---
Raízes de plantas orquídeas e bromélias servem de abrigo para pequenas formigas em florestas tropicais. As formigas constroem seus ninhos nesses emaranhados vegetais, encontrando proteção contra predadores e estabilidade contra ventos fortes. Para as plantas, a presença física dos formigueiros nas suas raízes externas não provoca nenhum tipo de perfuração, perda de seiva, infecção ou benefício, mantendo o vegetal completamente indiferente à presença dos insetos.
A associação harmônica em que as formigas utilizam a estrutura das plantas estritamente como abrigo, sem beneficiá-las ou prejudicá-las, configura o:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) parasitismo.
GABARITO: D
---
Certas espécies de fungos do solo produzem e excretam de forma contínua compostos orgânicos complexos chamados ácidos liguínicos. Essas substâncias químicas se espalham pela terra ao redor e destroem a membrana celular de várias espécies de bactérias fixadoras de nutrientes que vivem próximas, matando-as. Os biólogos confirmaram que o fungo faz isso como um subproduto natural de sua digestão celular, sem absorver nenhum fragmento ou nutriente dessas bactérias mortas.
A interação descrita entre os fungos que liberam os ácidos orgânicos e as bactérias vizinhas eliminadas caracteriza o:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) inquilinismo.
E) competição.
GABARITO: B
---
Em recifes de coral no Nordeste brasileiro, duas espécies diferentes de pequenos peixes herbívoros disputam ativamente as mesmas fendas e buracos nas rochas para depositarem seus ovos e se protegerem de predadores durante a noite. Como o número de fendas seguras no recife é muito menor do que a população de peixes, as duas espécies travam batalhas por território, o que limita o crescimento populacional de ambos os grupos devido à falta de locais de abrigo.
A limitação no crescimento das populações desses peixes herbívoros provocada pela disputa por abrigos nas rochas deve-se à:
A) predação.
B) mutualismo.
C) amensalismo.
D) comensalismo.
E) competição.
GABARITO: E
---
Agricultores utilizam a técnica da "rotação de culturas", alternando o plantio de milho com o de soja ou feijão na mesma área a cada safra. Eles sabem que as leguminosas possuem bactérias em suas raízes que enriquecem o solo com compostos nitrogenados essenciais para o crescimento do milho na safra seguinte, reduzindo drasticamente a necessidade de comprar fertilizantes químicos industriais caros.
No ciclo do nitrogênio, a etapa executada por essas bactérias associadas às raízes das leguminosas, que capta o gás nitrogênio da atmosfera e o transforma em amônia, é denominada:
A) nitrificação.
B) desnitrificação.
C) amonificação.
D) fixação biológica.
E) assimilação vegetal.
GABARITO: D
---
O aumento acelerado da queima de combustíveis fósseis (como carvão, óleo diesel e gasolina) por indústrias e veículos automotores desde a Revolução Industrial tem provocado uma alteração severa na dinâmica atmosférica global. Esse processo libera bilhões de toneladas de dióxido de carbono (CO2) anualmente, superando a capacidade de absorção dos oceanos e das florestas tropicais, o que retém mais calor na Terra.
A interferência humana descrita atua diretamente no ciclo do carbono, intensificando o fenômeno do(a):
A) inversão térmica.
B) efeito estufa natural.
C) aquecimento global por retenção térmica.
D) destruição da camada de ozônio por gases.
E) eutrofização de corpos d'água superficiais.
GABARITO: C
---
Ao desenhar a estrutura trófica de um ecossistema de floresta temperada, biólogos registraram que uma única árvore de grande porte (como um carvalho centenário) serve de alimento e habitat para mais de dez mil pequenas lagartas herbívoras. Por sua vez, essas milhares de lagartas servem de alimento para poucas dezenas de pássaros insetívoros de pequeno porte que habitam a região.
Ao representar graficamente a quantidade de indivíduos em cada nível trófico desse ecossistema, a pirâmide de números apresentará um formato:
A) perfeitamente reto e simétrico.
B) invertido em sua base de produtores.
C) idêntico ao formato da pirâmide de energia.
D) plano e horizontal em todos os níveis tróficos.
E) triangular regular com o topo sendo o mais largo.
GABARITO: B
---
Projetos de reflorestamento em larga escala são apontados por cientistas como uma das estratégias biológicas mais eficientes para mitigar os impactos das mudanças climáticas globais. À medida que as árvores plantadas crescem e aumentam sua biomassa, elas incorporam o carbono gasoso da atmosfera em suas estruturas moleculares de celulose e tecidos vegetais estáveis, funcionando como verdadeiros "sumidouros" de poluição.
O processo metabólico celular realizado pelas plantas que permite a retirada direta do dióxido de carbono (CO2) da atmosfera para incorporá-lo na biomassa vegetal é a:
A) respiração celular.
B) transpiração cuticular.
C) fermentação lática.
D) fotossíntese.
E) quimiossíntese do solo.
GABARITO: D
---
Ao construir um gráfico para representar o fluxo energético de uma cadeia alimentar composta por capim, gafanhotos, sapos e cobras, um estudante de biologia tentou desenhar uma pirâmide invertida, colocando o capim no topo com uma barra menor e as cobras na base com uma barra gigante, argumentando que as cobras acumulam mais energia por serem maiores e estarem no topo da cadeia.
O professor corrigiu o estudante, explicando que o desenho violava uma lei física absoluta dos ecossistemas, pois a pirâmide de energia:
A) deve ser sempre invertida devido ao fluxo cíclico da matéria orgânica.
B) apresenta formato retangular estável determinado pelos decompositores.
C) é sempre direta, pois a energia diminui a cada nível devido à dissipação.
D) inverte-se apenas quando os consumidores primários são microscopicamente pequenos.
E) possui barras de tamanhos idênticos determinada pela eficiência dos produtores.
GABARITO: C
---
Em solos empobrecidos de biomas como o Cerrado, certas espécies de bactérias de vida livre do gênero Azotobacter desempenham um papel ecológico vital. Elas absorvem o nitrogênio molecular gasoso (N2) diretamente das fendas de ar do solo e o convertem em íons amônio (NH4+), disponibilizando o elemento para a comunidade vegetal sem a necessidade de fertilizantes artificiais.
A conversão do nitrogênio molecular gasoso diretamente em compostos de amônio por essas bactérias do solo é chamada de:
A) nitrificação.
B) desnitrificação.
C) amonificação.
D) fixação biológica.
E) assimilação vegetal.
GABARITO: D
---
Relatórios climáticos internacionais apontam que o desmatamento massivo e as queimadas florestais na Amazônia reduzem drasticamente o número de árvores adultas em atividade metabólica. Esse processo, além de eliminar os ecossistemas, joga fumaça na atmosfera e interrompe o recolhimento de carbono gasoso do ar, fazendo com que o planeta acumule mais calor e sofra alterações drásticas nos regimes de chuvas.
O desmatamento contribui diretamente para as mudanças climáticas porque interrompe o processo do ciclo do carbono que atua como sumidouro de gases, intensificando o(a):
A) inversão térmica industrial.
B) aquecimento global por retenção de calor.
C) destruição da camada de ozônio por cinzas.
D) chuva ácida por óxidos de carbono.
E) eutrofização atmosférica regional.
GABARITO: B
---
Um estudante de ecologia marinha tentou desenhar a pirâmide de energia de um ecossistema marinho onde o fitoplâncton (produtores microscópicos) possui uma biomassa muito pequena em um determinado instante, mas se reproduz tão rápido que consegue sustentar uma biomassa gigante de zooplâncton e peixes. O estudante desenhou a pirâmide de energia com a base bem fininha e o topo largo, justificando a reprodução rápida das algas.
O professor invalidou o desenho do estudante, explicando que, independente do tamanho ou da velocidade de reprodução dos organismos, a pirâmide de energia:
A) deve ser representada de forma retangular devido aos decompositores.
B) inverte-se apenas em ecossistemas aquáticos devido à densidade da água.
C) é sempre direta, pois a energia diminui a cada nível devido à dissipação.
D) apresenta formato circular simétrico determinado pelos consumidores.
E) inverte-se quando os produtores possuem ciclo de vida microscopicamente curto.
GABARITO: C
---
Em uma plantação de eucaliptos para reflorestamento comercial, biólogos monitoraram o fluxo trófico e registraram que um único eucalipto de grande porte serve de alimento para mais de cinco mil pulgões parasitas. Por sua vez, esses milhares de pulgões servem de alimento para algumas dezenas de joaninhas predadoras que controlam a população da praga na árvore.
Ao representar graficamente esse ecossistema focado na quantidade de indivíduos em cada nível, a pirâmide de números apresentará:
A) um formato triangular perfeito e regular.
B) uma inversão em sua base de produtores.
C) um desenho idêntico ao da pirâmide de energia.
D) barras horizontais de tamanhos estritamente iguais.
E) o topo como a barra mais larga do gráfico.
GABARITO: B
---
No ciclo do carbono, os seres vivos realizam processos metabólicos contínuos que fazem a matéria orgânica transitar entre o meio abiótico e os tecidos biológicos. Enquanto alguns processos devolvem o carbono para a atmosfera na forma de gás carbônico (CO2), existe um mecanismo biológico principal que faz o caminho inverso, retirando o gás do ar para transformá-lo em cadeias de açúcares estáveis.
O processo biológico responsável pela retirada do gás carbônico da atmosfera para incorporá-lo na matéria orgânica dos seres vivos é a:
A) respiração celular.
B) fermentação alcoólica.
C) transpiração estomática.
D) fotossíntese.
E) digestão enzimática.
GABARITO: D
---
Um oceanógrafo desenhou um gráfico para representar a contagem física de indivíduos em uma cadeia alimentar marinha de mar aberto. Os dados coletados mostraram que, em um determinado dia de verão, um milhão de indivíduos microscópicos do fitoplâncton sustentavam dez milhões de pequenos microcrustáceos do zooplâncton, que por sua vez alimentavam algumas centenas de peixes. Ao tentar desenhar o gráfico, o estudante percebeu que a barra da base (fitoplâncton) ficou menor do que a barra do meio (zooplâncton).
Ao representar graficamente a quantidade de indivíduos em cada nível desse ecossistema marinho específico, a pirâmide de números apresentará:
A) um formato perfeitamente reto e simétrico.
B) uma inversão em sua base de produtores.
C) um desenho idêntico ao da pirâmide de energia.
D) barras horizontais de tamanhos estritamente iguais.
E) o topo como a barra mais larga do gráfico.
GABARITO: B
---
Em plantações de reflorestamento de pinus, biólogos mapearam a estrutura biológica local e constataram que uma única árvore de pinus de grande porte serve de alimento e hospedeira para cerca de oito mil pulgões parasitas. Esses milhares de pulgões, por sua vez, servem de base alimentar para trezentas joaninhas predadoras que habitam as folhas da árvore.
Se representarmos graficamente a contagem de indivíduos para cada nível trófico dessa cadeia alimentar, a pirâmide de números resultante será caracterizada por:
A) apresentar todas as barras com o mesmo comprimento horizontal.
B) ter o topo (joaninhas) como a barra mais larga de todo o gráfico.
C) possuir uma base estreita (um pinus) sustentando uma barra do meio larga (pulgões).
D) ser perfeitamente direta e triangular, idêntica à pirâmide de energia.
E) ter uma base larga que vai se estreitando simetricamente até o topo.
GABARITO: C
---
Engenheiros ambientais monitoram o ciclo do carbono em uma área de floresta nativa para calcular o balanço de gases estufa. Eles medem continuamente a troca de gases entre as árvores e a atmosfera. O relatório técnico indicou que, durante a noite, na ausência de luz solar, as plantas realizam um processo metabólico vital que consome oxigênio e devolve dióxido de carbono (CO2) para a atmosfera, atuando temporariamente como fontes do gás, ao contrário do que fazem durante o dia.
O processo celular realizado pelas plantas durante a noite que devolve o dióxido de carbono (CO2) para a atmosfera é a:
A) fotossíntese.
B) respiração celular.
C) transpiração cuticular.
D) fermentação alcoólica.
E) fixação biológica.
GABARITO: B
---
No ciclo do nitrogênio, após as bactérias fixadoras prenderem o elemento no solo na forma de amônia, entra em ação um segundo grupo de bactérias quimiossintetizantes do solo (como as dos gêneros Nitrosomonas e Nitrobacter). Essas bactérias oxidam a amônia, transformando-a primeiramente em nitrito e, sequencialmente, em nitrato. O nitrato é a forma química mais estável e solúvel, sendo a única que as raízes das plantas conseguem absorver em larga escala para produzir suas proteínas e DNA.
A etapa do ciclo do nitrogênio em que a amônia é convertida em nitrito e nitrato pelas bactérias quimiossintetizantes é denominada:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: B
---
Em solos encharcados e pobres em oxigênio, como em regiões de pântanos ou plantações alagadas de arroz, certas bactérias anaeróbicas (como as do gênero Pseudomonas) utilizam os nitratos do solo em seu metabolismo respiratório. Ao quebrarem essas moléculas, essas bactérias liberam o nitrogênio na forma de gás molecular (N2), fazendo o elemento retornar diretamente para a atmosfera e fechando o ciclo biogeoquímico.
A etapa do ciclo do nitrogênio realizada por essas bactérias anaeróbicas, que transforma o nitrato do solo de volta em gás nitrogênio (N2) atmosférico, é a:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: C
---
Indústrias metalúrgicas localizadas em um polo industrial termelétrico queimam toneladas de carvão mineral rico em impurezas. Moradores de cidades vizinhas começaram a notar que a água das precipitações estava corroendo as estruturas metálicas de pontes, estátuas de mármore e alterando o pH de solos agrícolas, matando plantações sensíveis. Análises químicas indicaram a presença de altos teores de ácido sulfúrico e ácido nítrico na água.
Os danos ambientais causados nas cidades vizinhas ao polo industrial são uma consequência direta do fenômeno da:
A) inversão térmica sazonal.
B) destruição da camada de ozônio.
C) magnificação trófica do carbono.
D) ocorrência de chuva ácida.
E) intensificação do efeito estufa.
GABARITO: D
---
Durante os meses de inverno em grandes metrópoles poluídas, como São Paulo, é comum a ocorrência de dias com o céu cinzento e uma névoa densa de poluentes estagnada logo acima dos prédios. Esse fenômeno ocorre porque o solo resfria rapidamente à noite, criando uma camada de ar frio e denso colada ao chão, sobreposta por uma camada de ar quente. Isso impede a subida dos gases dos escapamentos e chaminés, que ficam retidos na altura em que a população respira.
O fenômeno atmosférico que impede a dispersão dos poluentes urbanos durante o inverno é denominado:
A) chuva ácida.
B) inversão térmica.
C) efeito estufa global.
D) destruição do ozônio.
E) ilha de calor urbana.
GABARITO: B
---
Relatórios de saúde pública indicaram um aumento estatístico nos casos de melanoma (câncer de pele) e catarata ocular em populações que vivem em regiões de alta latitude no hemisfério sul. Cientistas associam esse fenômeno ao uso histórico de gases refrigerantes do tipo clorofluorcarbono (CFC) em geladeiras e aerossóis, que reagiram quimicamente com os gases da estratosfera, abrindo falhas na barreira de proteção gasosa do planeta.
O aumento da incidência de raios ultravioleta prejudiciais à saúde humana na superfície da Terra deve-se ao impacto do CFC na(o):
A) intensificação do efeito estufa.
B) formação de chuvas ácidas regionais.
C) destruição da camada de ozônio.
D) surgimento de ilhas de calor severas.
E) processo de inversão térmica urbana.
GABARITO: C
---
Ao queimar óleo diesel e gasolina, os motores dos carros liberam compostos gasosos na atmosfera. No entanto, o senso comum confunde os impactos ambientais desses gases. Enquanto o dióxido de carbono (CO2) atua retendo o calor na Terra e gerando o aquecimento global, os gases à base de enxofre lançados pelas chaminés industriais reagem com as nuvens, gerando um impacto químico completamente diferente que queima as folhas das árvores de florestas distantes.
O impacto químico nas florestas gerado pelos gases à base de enxofre misturados às nuvens difere do aquecimento global por se caracterizar como:
A) inversão térmica.
B) chuva ácida.
C) destruição do ozônio.
D) eutrofização do ar.
E) magnificação trófica.
GABARITO: B
---
Em uma aula de ecologia urbana, o professor explicou que a inversão térmica, apesar de causar graves crises de asma e bronquite na população devido ao acúmulo de fumaça perto do chão, não é provocada pela poluição humana em si. Trata-se de um fenômeno climático natural que ocorre principalmente em madrugadas frias, cuja gravidade é ampliada pela presença das indústrias.
A inversão térmica é classificada como um fenômeno natural porque baseia-se estritamente na(o):
A) reação química entre gases industriais e o vapor de água.
B) bloqueio dos raios ultravioleta por nuvens de poluição densas.
C) comportamento físico de massas de ar com densidades e temperaturas diferentes.
D) liberação de compostos de CFC pelas indústrias durante a noite.
E) acúmulo de matéria orgânica que consome o oxigênio atmosférico.
GABARITO: C
---
Uma estação de tratamento de água (ETA) municipal capta água turva e barrenta de um rio local. No início do processo, os técnicos adicionam cal e sulfato de alumínio à água. Essas substâncias químicas alteram as cargas elétricas das partículas de argila em suspensão, fazendo com que elas colidam e se unam, formando agregados gelatinosos e pesados que começam a se depositar no fundo do tanque por ação da gravidade.
A etapa inicial descrita do tratamento de água, em que as partículas de sujeira se unem formando agregados pesados que afundam, engloba sequencialmente os processos de:
A) filtração e cloração.
B) decantação e fluoretação.
C) coagulação (floculação) e decantação.
D) aeração biológica e peneiramento.
E) osmose reversa e absorção química.
GABARITO: C
---
Engenheiros sanitários projetaram uma nova Estação de Tratamento de Esgoto (ETE) para uma cidade industrial. Na fase secundária do tratamento, o esgoto líquido é bombeado para grandes tanques abertos onde motores agitam a água constantemente para injetar oxigênio. Essa injeção forçada estimula a proliferação massiva de colônias de bactérias e protozoários que consomem e decompõem rapidamente a matéria orgânica dissolvida, limpando a água antes de sua devolução ao rio.
O processo realizado na fase secundária da ETE, que utiliza microrganismos e oxigênio para reduzir a carga orgânica do esgoto, baseia-se na:
A) decantação primária física.
B) cloração química dos resíduos.
C) digestão anaeróbica em biodigestores.
D) decomposição aeróbica por aeração.
E) filtração em carvão ativado.
GABARITO: D
---
Municípios modernos estão substituindo os antigos lixões a céu aberto por aterros sanitários controlados. Durante a construção do aterro, os engenheiros cobrem todo o fundo do terreno com mantas de polietileno de alta densidade (plástico grosso) e camadas de argila compactada. O objetivo dessa engenharia é reter o líquido escuro, viscoso e altamente poluente gerado pela decomposição dos resíduos orgânicos, impedindo que ele penetre na terra e atinja as reservas de água subterrâneas.
A impermeabilização do fundo do aterro sanitário com mantas plásticas e argila visa proteger o meio ambiente contra a contaminação do lençol freático pelo(a):
A) gás metano liquefeito.
B) liberação de chorume.
C) formação de lixo eletrônico.
D) inversão térmica do solo.
E) escoamento de chuva ácida.
GABARITO: B
---
Em uma estação de tratamento de água (ETA), após a remoção da maior parte da lama e das partículas sólidas por decantação, a água ainda contém microrganismos patogênicos (como bactérias e vírus) invisíveis a olho nu e partículas microscópicas flutuantes. Para finalizar o processo antes da distribuição para as casas, a água passa por tanques compostos por camadas sucessivas de areia, cascalho e carvão ativado, recebendo em seguida a adição de compostos de cloro.
Os dois processos finais citados, responsáveis por reter as impurezas microscópicas restantes e eliminar os agentes causadores de doenças na água, são, respectivamente:
A) floculação e decantação.
B) decantação e aeração.
C) filtração e cloração.
D) coagulação e fluoretação.
E) peneiramento e sedimentação.
GABARITO: C
---
A decomposição da matéria orgânica no interior de aterros sanitários ocorre em condições de ausência de oxigênio nas camadas profundas. Esse processo anaeróbico gera grandes volumes de um gás combustível que, se acumulado, pode causar explosões. Para mitigar o problema e reduzir os impactos nas mudanças climáticas, os aterros modernos instalam tubulações verticais para queimar esse gás ou direcioná-lo para geradores, transformando o resíduo gasoso em energia elétrica.
O gás combustível gerado em abundância pela decomposição anaeróbica no aterro sanitário, que é captado pelas tubulações para geração de energia, é o:
A) dióxido de carbono.
B) gás metano.
C) óxido de enxofre.
D) cloro gasoso.
E) vapor de água.
GABARITO: B
---
Sensores térmicos instalados em satélites meteorológicos registraram que os bairros centrais de uma grande metrópole apresentavam temperaturas médias até 6 °C superiores às áreas de florestas e fazendas localizadas na periferia. Os cientistas explicaram que a pavimentação asfáltica maciça e a grande quantidade de edifícios de concreto retêm a radiação solar durante o dia, enquanto a escassez de áreas verdes impede o resfriamento natural que ocorreria pela liberação de vapor de água pelas folhas.
O fenômeno climático urbano caracterizado pelo aumento artificial da temperatura nas regiões centrais e impermeabilizadas da cidade é denominado:
A) inversão térmica.
B) ilha de calor.
C) efeito estufa global.
D) destruição do ozônio.
E) chuva ácida regional.
GABARITO: B
---
Em tardes quentes e abafadas de verão em regiões tropicais, é muito comum a ocorrência de temporais rápidos, localizados e intensos por volta das 17h. O processo se inicia com o forte aquecimento do solo pelo Sol ao longo do dia, fazendo com que o ar quente e úmido colado ao chão suba rapidamente por ser menos denso. Ao atingir as camadas elevadas e frias da atmosfera, o vapor se condensa abruptamente, formando nuvens densas de tempestade que desabam com ventos e raios.
A dinâmica descrita, que envolve a subida rápida do ar aquecido pelo solo seguida de condensação e tempestades rápidas de final de tarde, caracteriza a:
A) chuva frontal.
B) chuva ácida.
C) chuva de convecção.
D) chuva orográfica.
E) inversão térmica.
GABARITO: C
---
Grandes empresas de tecnologia e logística estão adotando relatórios anuais para mensurar a "Pegada de Carbono" de suas operações de entrega. O cálculo avalia desde os quilômetros rodados pelos caminhões movidos a óleo diesel até a energia gasta nos centros de distribuição. O objetivo é criar planos de compensação ambiental, como o plantio de árvores nativas, para neutralizar a massa de poluentes gasosos que suas atividades jogam na atmosfera, retendo calor e piorando as mudanças climáticas globais.
A mensuração da "Pegada de Carbono" dessas indústrias quantifica diretamente o impacto ambiental associado à emissão de gases responsáveis pelo(a):
A) destruição da camada de ozônio.
B) formação de chuvas ácidas nas cidades.
C) intensificação do efeito estufa.
D) surgimento de ilhas de calor no centro.
E) processo de inversão térmica no inverno.
GABARITO: C
---
Urbanistas que buscam mitigar o problema das ilhas de calor em metrópoles estão propondo leis para a instalação obrigatória de "telhados verdes" (cobertura vegetal sobre as lajes dos prédios) e a arborização maciça de calçadas. Além de embelezar a cidade, a vegetação atua retirando calor do ambiente por meio de um processo biológico em que as plantas absorvem água pelas raízes e a liberam na forma de vapor através de microfuros nas folhas, diminuindo a temperatura do ar ao redor.
O processo fisiológico vegetal realizado pelas folhas que libera vapor de água na atmosfera e ajuda a resfriar o microclima urbano contra as ilhas de calor é a:
A) fotossíntese.
B) respiração celular.
C) evapotranspiração.
D) digestão enzimática.
E) fixação de carbono.
GABARITO: C
---
Em dias de calor intenso nas grandes cidades, a combinação do asfalto quente com a fumaça de poluentes gerada pelos escapamentos dos veículos piora drasticamente o desconforto térmico da população. Os termômetros de rua mostram que a temperatura cai de forma perceptível à medida que o pedestre se afasta do centro e entra em parques urbanos arborizados. Isso ocorre porque o asfalto seco possui uma baixíssima capacidade de refletir a luz solar, absorvendo quase toda a energia do Sol na forma de calor, ao contrário das folhas das árvores.
A alta absorção de calor pelo asfalto e concreto nos centros urbanos, que impulsiona a formação das ilhas de calor, deve-se ao fato de esses materiais apresentarem:
A) uma alta taxa de bioacumulação de energia.
B) um baixo índice de reflexão da radiação solar (albedo).
C) um processo contínuo de inversão térmica molecular.
D) uma eficiência ecológica superior à da vegetação.
E) uma liberação massiva de gases clorofluorcarbonos.
GABARITO: B
---
Em uma região montanhosa que abriga um grande complexo de indústrias petroquímicas, biólogos começaram a registrar a morte de anfíbios e a descamação de árvores em uma reserva florestal localizada a 50 quilômetros de distância, na direção dos ventos predominantes. Exames na água das nascentes da reserva apontaram um pH extremamente baixo, causado pela reação do vapor de água das nuvens com os gases dióxido de enxofre (SO2) e dióxido de nitrogênio (NO2) lançados pelas chaminés das fábricas.
O impacto ambiental destrutivo que atingiu a reserva florestal distante, caracterizado pela alteração química do pH da água da chuva, é a:
A) inversão térmica.
B) chuva ácida.
C) destruição da camada de ozônio.
D) magnificação trófica.
E) intensificação do efeito estufa.
GABARITO: B
---
Durante o planejamento de uma Estação de Tratamento de Água (ETA) para uma nova região metropolitana, os engenheiros detalharam a etapa em que a água, após passar pelos tanques de decantação onde a lama mais pesada afundou, precisa atravessar grandes filtros compostos por camadas de cascalho, areia fina e carvão ativado. Esse procedimento é crucial para reter as impurezas microscópicas que ainda permanecem flutuando na água.
A etapa do tratamento de água descrita, responsável por fazer o líquido atravessar barreiras físicas porosas para reter impurezas microscópicas, é a:
A) floculação.
B) decantação.
C) filtração.
D) cloração.
E) fluoretação.
GABARITO: C
---
Campanhas globais de conscientização ecológica alertam que o descarte de aparelhos de ar-condicionado e sistemas de refrigeração industrial muito antigos em lixões comuns pode liberar na atmosfera resíduos de gases clorofluorcarbonos (CFC). Esses gases sobem até a estratosfera e quebram as moléculas de ozônio (O3), gerando uma falha que permite a passagem direta de altos índices de radiação ultravioleta para a superfície do planeta.
A liberação dos gases CFC descrita no texto gera um impacto ambiental que atua diretamente na:
A) intensificação do efeito estufa.
B) formação de chuvas ácidas nas cidades.
C) destruição da camada de ozônio.
D) ocorrência de inversão térmica no solo.
E) criação de ilhas de calor urbanas.
GABARITO: C
---
O gerenciamento de resíduos orgânicos em um aterro sanitário moderno envolve a captação e o tratamento do chorume, o líquido escuro e poluente que escorre da massa de lixo. No entanto, as camadas profundas do aterro, por estarem compactadas e sem contato com o ar, realizam uma decomposição anaeróbica que produz grandes volumes de um gás combustível que, se acumulado, pode causar explosões. Para mitigar o problema e reduzir os impactos nas mudanças climáticas, os aterros modernos instalam tubulações verticais para queimar esse gás ou direcioná-lo para geradores, transformando o resíduo gasoso em energia elétrica.
O subproduto gasoso gerado em abundância pela decomposição biológica na ausência de oxigênio no interior do aterro sanitário é o:
A) dióxido de carbono.
B) gás metano.
C) óxido de enxofre.
D) cloro gasoso.
E) vapor de água.
GABARITO: B
---
Em grandes centros urbanos cercados por montanhas, como a cidade do México ou Santiago, os meses mais frios do ano são marcados por alertas de qualidade do ar. Durante a madrugada, o solo perde calor muito rápido, resfriando o ar próximo ao chão. Esse ar frio e pesado fica estagnado embaixo de uma camada de ar mais quente, funcionando como uma tampa que impede a subida da fumaça dos carros e das indústrias, deixando a poluição concentrada na altura da respiração das pessoas.
O fenômeno meteorológico natural que impede a subida e a dispersão dos poluentes atmosféricos durante os dias frios é a:
A) chuva ácida.
B) inversão térmica.
C) ilha de calor urbana.
D) destruição do ozônio.
E) evapotranspiração regional.
GABARITO: B
---
Moradores de uma região litorânea próxima a um complexo portuário de carvão começaram a notar que as folhas das árvores frutíferas em seus quintais apresentavam queimaduras químicas e caíam precocemente. Análises laboratoriais revelaram que a queima do combustível nos navios e usinas liberava grandes quantidades de óxidos de enxofre que, ao reagirem com a umidade do ar, precipitavam alterando o pH da água e do solo.
O fenômeno responsável pela queima das folhas e acidificação do solo ao redor do complexo portuário é a:
A) inversão térmica.
B) chuva ácida.
C) destruição da camada de ozônio.
D) magnificação trófica.
E) intensificação do efeito estufa.
GABARITO: B
---
No projeto de engenharia de uma grande Estação de Tratamento de Água (ETA), os técnicos detalharam o funcionamento dos tanques de sedimentação. Após a adição de agentes coagulantes que fizeram as micropartículas de sujeira se aglomerarem em flocos densos, a água permanece em repouso absoluto por algumas horas. Esse período é essencial para que a força da gravidade puxe os flocos pesados de sujeira para o fundo do tanque, permitindo que a água limpa seja coletada pela superfície.
A etapa do tratamento de água descrita, em que a água fica em repouso para que os flocos de impurezas afundem por gravidade, é a:
A) floculação.
B) decantação.
C) filtração.
D) cloração.
E) fluoretação.
GABARITO: B
---
Emissões industriais antigas de gases compostos por cloro, flúor e carbono na alta atmosfera provocaram um impacto ambiental severo que ainda é monitorado por agências espaciais. Esses gases quebram as moléculas que filtram as radiações solares mais energéticas, resultando em um aumento da incidência de raios UV na superfície terrestre, o que eleva os índices de mutações genéticas em plantas e animais.
O impacto de longo prazo descrito no texto, gerado pela liberação desses gases na alta atmosfera, refere-se à:
A) intensificação do efeito estufa.
B) formação de chuvas ácidas regionais.
C) destruição da camada de ozônio.
D) ocorrência de inversão térmica urbana.
E) criação de ilhas de calor no centro.
GABARITO: C
---
Urbanistas mediram que, durante o verão, a temperatura no centro financeiro de uma cidade era até 5 °C maior do que nos bairros residenciais arborizados da mesma cidade. Eles apontaram que a substituição da cobertura vegetal por extensas superfícies de asfalto escuro e concreto armado faz com que o ambiente urbano absorva quase toda a energia do Sol na forma de calor, em vez de refleti-la de volta para o espaço.
A propriedade física do asfalto e do concreto de refletir pouca luz solar e absorver muito calor, impulsionando o aquecimento do centro da cidade, está associada a um:
A) alto índice de bioacumulação.
B) baixo índice de albedo.
C) processo de inversão térmica molecular.
D) alto fluxo unidirecional de energia.
E) escoamento massivo de chorume.
GABARITO: B
---
Em uma Estação de Tratamento de Esgoto (ETE), a fase biológica envolve o bombeamento do efluente líquido para tanques de aeração mecânica. Motores potentes agitam o esgoto continuamente para garantir um fornecimento constante de oxigênio gasoso na água. Esse ambiente hiperoxigenado é fundamental para acelerar o metabolismo de micro-organismos que quebram a matéria orgânica dissolvida de forma rápida e eficiente.
Os motores que injetam oxigênio nos tanques da ETE buscam otimizar o processo biológico de:
A) decantação física primária.
B) cloração química dos resíduos.
C) digestão anaeróbica em biodigestores.
D) decomposição aeróbica por aeração.
E) filtração em carvão ativado.
GABARITO: D
---
O setor de transporte de cargas de uma região agrícola utiliza frotas pesadas de caminhões movidos a óleo diesel. Durante a queima desse combustível nos motores, além dos gases estufa, são liberados na atmosfera compostos gasosos derivados do enxofre. À medida que esses gases sobem e entram em contato com as gotículas de água que formam as nuvens, eles sofrem reações químicas e geram uma precipitação que altera o equilíbrio químico de rios e lagos localizados em florestas distantes, afetando a reprodução dos peixes nativos.
O impacto ecológico gerado nas florestas distantes pelo escoamento dessa precipitação específica é a:
A) inversão térmica na bacia.
B) ocorrência de chuva ácida.
C) destruição do ozônio das águas.
D) magnificação trófica do diesel.
E) intensificação do efeito estufa local.
GABARITO: B
---
Moradores de vales cercados por serras em regiões industriais sofrem constantemente com crises alérgicas intensas nas primeiras horas da manhã durante o inverno. O problema se agrava porque, com o forte resfriamento do solo na madrugada, uma massa de ar frio e denso se fixa próxima às ruas, sendo sobreposta por uma massa de ar mais quente. Essa configuração física impede o fluxo vertical dos ventos, fazendo com que a fumaça preta lançada pelas chaminés das fábricas passe horas trancada na altura em que a população caminha.
O fenômeno climático natural cuja gravidade é ampliada pela poluição industrial nas manhãs de inverno é denominado:
A) chuva ácida regional.
B) inversão térmica.
C) ilha de calor urbana.
D) destruição da camada de ozônio.
E) evapotranspiração do vale.
GABARITO: B
---
Relatórios emitidos por órgãos de proteção ambiental indicaram que o descarte incorreto de fluidos térmicos de refrigeradores industriais abandonados em galpões antigos resultou no vazamento de gases da família dos clorofluorcarbonos. Esses compostos migraram para as camadas mais altas da atmosfera terrestre e aceleraram a degradação das moléculas responsáveis por filtrar a radiação solar de alta energia. Como consequência, houve um registro de elevação nos índices de mutações celulares na pele de animais silvestres da região.
A elevação nos índices de radiação solar nociva que atinge a fauna da região decorre do impacto dos gases vazados diretamente na(o):
A) intensificação do efeito estufa global.
B) formação de chuvas ácidas severas.
C) destruição da camada de ozônio.
D) surgimento de ilhas de calor severas.
E) processo de inversão térmica do solo.
GABARITO: C
---
Uma usina termelétrica a carvão mineral foi instalada perto de uma área de preservação. A queima do carvão lança na atmosfera gases à base de nitrogênio e enxofre que alteram quimicamente as nuvens ao redor. O relatório de monitoramento indicou que, semanas após o início das operações da usina, as estátuas e monumentos de pedra calcária do parque ecológico começaram a apresentar um processo acelerado de corrosão e desgaste em suas superfícies após os dias chuvosos.
A degradação física sofrida pelos monumentos de pedra calcária do parque ecológico é explicada pela ocorrência de:
A) inversão térmica severa.
B) chuva ácida na região.
C) destruição do ozônio local.
D) magnificação trófica molecular.
E) efeito estufa concentrado.
GABARITO: B
---
Uma grande indústria siderúrgica e de refino de petróleo ampliou suas chaminés de exaustão de gases. O senso comum dos moradores locais teme que as emissões de dióxido de carbono (CO2) dessas chaminés causem falhas na atmosfera que facilitem a entrada de raios solares ultravioleta causadores de queimaduras na pele. O engenheiro químico da fábrica acalmou a comunidade explicando que o CO2 atua aprisionando a energia térmica na Terra, e que o impacto ambiental que facilita a entrada de raios UV na verdade depende de gases industriais totalmente diferentes.
O impacto ambiental que o engenheiro químico citou como o verdadeiro responsável por facilitar a entrada dos raios ultravioleta nocivos na Terra é a:
A) inversão térmica de inverno.
B) formação de chuva ácida.
C) destruição da camada de ozônio.
D) eutrofização da atmosfera.
E) ilha de calor industrial.
GABARITO: C
---
Em plantações comerciais de tomate, uma espécie de mosca-branca ataca as folhas sugando os fluidos vitais do vegetal, o que reduz drasticamente a produtividade do tomateiro. Para resolver o problema sem defensivos químicos, um agrônomo liberou na lavoura ácaros predadores da espécie Phytoseiulus persimilis. Esses ácaros caçam e devoram ativamente as moscas-brancas, controlando a população da praga em poucas semanas e devolvendo o equilíbrio à plantação.
A estratégia de manejo biológico adotada pelo agrônomo para salvar o tomateiro baseia-se na dinâmica da relação ecológica de:
A) mutualismo.
B) amensalismo.
C) comensalismo.
D) predação.
E) parasitismo.
GABARITO: D
---
Uma grande indústria de papel e celulose instalou uma floresta artificial de eucaliptos em uma área que antes era coberta por pasto degradado. Ecólogos monitoraram a fauna local após dez anos e constataram que um único eucalipto centenário de grande porte servia de morada e base alimentar para mais de sete mil pulgões parasitas que atacavam suas folhas. Por sua vez, esses milhares de pulgões sustentavam uma população de duzentas joaninhas caçadoras.
Ao construir um gráfico para representar fisicamente a contagem de indivíduos pertencentes a cada degrau dessa cadeia alimentar, a pirâmide de números resultante apresentará:
A) um formato perfeitamente triangular e simétrico.
B) uma inversão em sua base de produtores.
C) um desenho idêntico ao da pirâmide de energia.
D) todas as barras horizontais com o mesmo comprimento.
E) o topo (joaninhas) como a maior e mais larga barra do gráfico.
GABARITO: B
---
Em solos tropicais arenosos, altamente lavados pelas chuvas e pobres em nutrientes, a sobrevivência de grandes árvores da floresta depende de fungos microscópicos que abraçam suas raízes, formando estruturas conhecidas como micorrizas. Esses fungos absorvem água e minerais do solo profundo com extrema eficiência e os entregam para as raízes da árvore. Em contrapartida, os fungos recebem os açúcares produzidos pela árvore na fotossíntese. Estudos de laboratório comprovam que, se essa associação for desfeita, os fungos secam e as árvores morrem desnutridas em poucos meses.
A interação anatômica e fisiológica estabelecida entre os fungos das micorrizas e as raízes das árvores é classificada como:
A) mutualismo.
B) inquilinismo.
C) comensalismo.
D) protocooperação.
E) parasitismo.
GABARITO: A
---
Agricultores que cultivam milho em solos compactados sofrem com a perda de produtividade devido à falta de compostos nitrogenados na terra. Para reverter o quadro de forma sustentável, engenheiros agrônomos recomendaram o uso de bactérias quimiossintetizantes de solo dos gêneros Nitrosomonas e Nitrobacter. Essas bactérias atuam em sequência na terra, pegando os compostos de amônia decorrentes da decomposição e os transformando em nitritos e, posteriormente, em nitratos, que são facilmente absorvidos pelas raízes do milharal.
A ação biológica dessas bactérias quimiossintetizantes enriquece o solo para o milho por meio da execução direta da etapa de:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: B
---
Em extensos pomares de macieiras, biólogos detectaram a presença de uma espécie de vespa exótica que se espalhou rapidamente pela região por não encontrar pássaros caçadores ou doenças nativas que controlassem sua população. Essas vespas começaram a construir seus ninhos nas mesmas cavidades de troncos de árvores e a colher os mesmos frutos silvestres que serviam de base alimentar exclusiva para uma espécie de ave nativa regional, resultando no declínio severo da população da ave local por falta de recursos disponíveis no ecossistema.
A redução drástica na população da ave nativa regional provocada pela introdução da vespa exótica é explicada pela ocorrência de:
A) predação direta.
B) mutualismo obrigatório.
C) amensalismo químico.
D) comensalismo trófico.
E) competição interespecífica.
GABARITO: E
---
Fazendeiros que criam gado de corte em pastagens extensivas monitoram constantemente a saúde do rebanho devido ao ataque de carrapatos (Rhipicephalus microplus). Esses pequenos artrópodes fixam-se na pele dos bois, perfuram os vasos sanguíneos e passam dias sugando o sangue dos animais. Embora essa atividade enfraqueça o gado, cause anemia e transmita doenças, o objetivo biológico do artrópode não é matar o hospedeiro imediatamente, mas sim garantir nutrientes para sua própria reprodução.
A interação biológica prejudicial estabelecida entre os carrapatos e o gado bovino caracteriza a relação de:
A) predação.
B) mutualismo.
C) comensalismo.
D) amensalismo.
E) parasitismo.
GABARITO: E
---
Em um experimento de laboratório, biólogos colocaram uma população de roedores em um grande biotério com oferta constante de água e ração. Eles registraram que a população cresceu de forma acelerada no início. No entanto, após alguns meses, o gráfico de crescimento parou de subir e estabilizou-se em uma linha horizontal constante. Os cientistas explicaram que, embora houvesse comida, o espaço físico limitado e o acúmulo de resíduos impediram que a população continuasse aumentando.
No gráfico de crescimento populacional, a linha horizontal onde a população se estabiliza devido às limitações do ambiente representa o(a):
A) potencial biótico teórico da espécie.
B) capacidade de suporte (carga biótica máxima).
C) taxa de mutação genética induzida.
D) fluxo unidirecional de energia térmica.
E) processo de sucessão ecológica primária.
GABARITO: B
---
Ecólogos colocaram duas espécies diferentes de protozoários ciliados (Paramecium caudatum e Paramecium aurelia) para crescerem isoladas em tubos de ensaio separados com a mesma quantidade de nutrientes. Ambas as espécies cresceram bem e estabilizaram suas populações. Em seguida, os cientistas colocaram as duas espécies juntas no mesmo tubo de ensaio. Após alguns dias, a população de P. aurelia continuou crescendo, enquanto a população de P. caudatum declinou severamente até desaparecer por completo do tubo.
O resultado do crescimento conjunto das duas espécies de protozoários no mesmo tubo de ensaio exemplifica o princípio da:
A) exclusão competitiva por competição interespecífica.
B) cooperação mútua por mutualismo obrigatório.
C) liberação de toxinas por amensalismo químico.
D) partilha de recursos por inquilinismo espacial.
E) simbiose obrigatória por dissipação térmica.
GABARITO: A
---
Durante o período de reprodução de uma espécie de aranha conhecida como viúva-negra (Latrodectus mactans), biólogos registraram um comportamento intrigante em cativeiro. Logo após a cópula, a fêmea, que é significativamente maior e mais forte, ataca o macho e o devora por completo. Esse ato garante à fêmea um aporte imediato de proteínas e energia essencial para o desenvolvimento saudável dos ovos que serão depositados em seguida.
A interação biológica desarmônica descrita, em que a fêmea se alimenta de um indivíduo da mesma espécie, é classificada como:
A) predação interespecífica.
B) parasitismo clássico.
C) canibalismo.
D) amensalismo.
E) competição.
GABARITO: C
---
Ao analisar o gráfico de crescimento de uma população de insetos praga em uma lavoura de algodão, um estudante notou que a curva real de crescimento ficava sempre abaixo de uma linha curva teórica que subia infinitamente de forma vertical (gráfico em forma de J). O professor explicou que a linha teórica representa como a população cresceria se não houvesse falta de comida, predadores ou doenças, o que nunca acontece na natureza.
A linha curva teórica que representa o crescimento máximo e infinito de uma população na ausência total de fatores limitantes expressa o(a):
A) resistência do meio ambiente.
B) capacidade de suporte do habitat.
C) potencial biótico da espécie.
D) taxa de desnitrificação do solo.
E) nível de magnificação trófica.
GABARITO: C
---
Em pântanos e áreas alagadas para a cultura de arroz, o solo permanece constantemente submerso, criando um ambiente sem oxigênio gasoso. Nessas condições, colônias de bactérias anaeróbicas quebram as moléculas de nitrato presentes na lama para realizar seu metabolismo. Esse processo quebra a estrutura química do nutriente e faz com que o elemento seja liberado diretamente para a atmosfera na forma de gás molecular (N2).
A etapa do ciclo do nitrogênio executada por essas bactérias anaeróbicas nos arrozais alagados é a:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: C
---
Um estudante monitorou uma cadeia alimentar em um bosque e registrou que uma única jaqueira centenária de grande porte (1 produtor) serve de morada e fornece alimento para cerca de dez mil pequenas lagartas herbívoras. Por sua vez, essas milhares de lagartas servem de alimento para cinquenta pássaros predadores de pequeno porte.
Ao transpor esses dados brutos para um gráfico que representa a quantidade física de indivíduos em cada nível trófico, a pirâmide de números exibirá:
A) uma base perfeitamente larga que afunila regularmente até o topo.
B) uma inversão em sua base de produtores.
C) um formato idêntico ao desenho da pirâmide de energia.
D) todas as barras com o mesmo comprimento horizontal.
E) o topo (pássaros) como a maior e mais larga barra do gráfico.
GABARITO: B
---
Horticultores utilizam a técnica de adubação verde, plantando alfafa e ervilhaca entre as fileiras de suas culturas principais. Eles sabem que essas plantas possuem associações biológicas em suas raízes capazes de captar o nitrogênio gasoso (N2) que circula livremente no ar e transformá-lo em amônia no solo, enriquecendo a terra de forma natural e barata.
No ciclo do nitrogênio, o processo realizado pelas bactérias associadas às raízes dessas plantas, que converte o nitrogênio molecular do ar em amônia, é a:
A) fixação biológica.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação vegetal.
GABARITO: A
---
Ecólogos marinhos mapearam o fluxo energético de uma cadeia alimentar em uma região de recifes de coral composta por algas, microcrustáceos, pequenos peixes e tubarões. O estudante do grupo tentou desenhar o gráfico com a base de algas bem estreita e o topo de tubarões muito largo, argumentando que os grandes predadores acumulam mais energia por estarem no topo da cadeia.
O pesquisador chefe corrigiu o desenho, relembrando que, devido à perda contínua de energia na forma de calor pelo metabolismo ao longo da cadeia, a pirâmide de energia:
A) deve ser sempre invertida devido ao fluxo cíclico de matéria orgânica.
B) inverte-se apenas quando os consumidores primários são microscópicos.
C) apresenta formato retangular determinado pela ação dos decompositores.
D) é sempre direta, pois a energia diminui a cada nível devido à dissipação.
E) possui barras horizontais de comprimentos estritamente idênticos.
GABARITO: D
---
Em solos agrícolas bem arados e oxigenados, bactérias quimiossintetizantes realizam uma função química vital para a lavoura de milho. Elas coletam a amônia decorrente da decomposição da matéria orgânica e a oxidam, transformando-a em nitrito e, logo em seguida, em nitrato. O nitrato é a única forma estável que as raízes do milharal conseguem absorver em grande escala para construir suas proteínas e crescer.
A etapa do ciclo do nitrogênio em que a amônia é convertida em nitrato pelas bactérias quimiossintetizantes do solo é a:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: B
---
Um oceanógrafo mediu a concentração de microplásticos nos tecidos de seres vivos em uma cadeia alimentar isolada no Oceano Atlântico. Os dados laboratoriais mostraram que, embora a água do mar apresentasse partículas quase indetectáveis, os tecidos das orcas (grandes baleias predadoras que ocupam o topo da cadeia) acumulavam uma quantidade massiva do poluente sintético, sofrendo danos severos em seus órgãos internos.
O acúmulo progressivo desse poluente sintético ao longo dos níveis da cadeia ocorre porque o microplástico não é biodegradável e sofre o fenômeno da:
A) eutrofização do ecossistema marinho.
B) magnificação trófica do poluente.
C) eficiência ecológica dos produtores.
D) dissipação térmica ao longo do fluxo.
E) competição interespecífica dos predadores.
GABARITO: B
---
Moradores de uma pequena vila de pescadores localizada próxima a uma grande usina termoelétrica a carvão notaram que, após os dias de chuva, as folhas das árvores de seus pomares apareciam com manchas pretas de queimaduras e caíam antes do tempo. Análises laboratoriais da água da chuva indicaram que a queima do carvão liberava óxidos de enxofre (SOx) na atmosfera, reduzindo drasticamente o pH da precipitação.
O fenômeno responsável pelos danos químicos nas folhas das árvores do pomar é a:
A) inversão térmica local.
B) chuva ácida regional.
C) destruição da camada de ozônio.
D) magnificação trófica do carvão.
E) intensificação do efeito estufa.
GABARITO: B
---
No projeto estrutural de uma grande Estação de Tratamento de Esgoto (ETE), os engenheiros sanitários planejaram a etapa de aeração mecânica secundária. O processo consiste em injetar continuamente grandes jatos de ar comprimido em tanques contendo o efluente líquido para ativar o metabolismo de bactérias que necessitam de oxigênio gasoso. Essas bactérias proliferam-se rapidamente e digerem a matéria orgânica dissolvida na água antes de sua devolução ao rio.
O processo de injeção de oxigênio nos tanques da ETE busca otimizar a atividade biológica de:
A) decantação física primária.
B) cloração química dos resíduos.
C) digestão anaeróbica em biodigestores.
D) decomposição aeróbica por aeração.
E) filtração em carvão ativado.
GABARITO: D
---
Meteorologistas monitorando o clima em grandes desertos arenosos e em áreas cobertas por calotas polares registraram que as superfícies de neve e gelo puro conseguem rebater cerca de 80% de toda a radiação solar recebida de volta para o espaço. Já as áreas de areia escura ou asfalto urbano retêm quase toda essa energia na forma de calor.
A propriedade física que descreve a capacidade de uma superfície de refletir a luz solar, sendo alta na neve e baixíssima no asfalto, é o(a):
A) índice de bioacumulação.
B) taxa de albedo.
C) processo de inversão térmica.
D) fluxo unidirecional de energia.
E) escoamento de chorume orgânico.
GABARITO: B
---
Ao calcular a produtividade de uma pastagem de capim-brachiaria, um agrônomo observou que apenas uma fração muito pequena da energia fixada pelo capim através da fotossíntese é convertida em carne nos bois que se alimentam na área. Ele relembrou aos fazendeiros que o capim consome a maior parte da energia produzida em sua própria respiração celular e crescimento, e que os bois perdem energia nas fezes e na manutenção de sua temperatura corporal.
A redução drástica da energia disponível à medida que se avança na cadeia alimentar deve-se ao fato de que a energia no ecossistema:
A) acumula-se de forma cíclica entre os consumidores.
B) é dissipada na forma de calor e processos metabólicos.
C) aumenta sua concentração em direção ao topo da cadeia.
D) é reciclada integralmente pelos decompositores do solo.
E) fica retida de forma permanente nos tecidos dos herbívoros.
GABARITO: B
---
Em solos tropicais de cerrado, um grupo de bactérias de vida livre realiza uma etapa fundamental para a reciclagem da matéria. Elas absorvem o nitrogênio em forma de gás (N2) contido nas fendas de ar do solo e o convertem em amônia, incorporando o elemento no meio biótico sem a necessidade de fertilizantes industriais.
A conversão do nitrogênio molecular gasoso diretamente em compostos de amônia por essas bactérias é denominada:
A) nitrificação.
B) desnitrificação.
C) amonificação.
D) fixação biológica.
E) assimilação vegetal.
GABARITO: D
---
Em uma Estação de Tratamento de Água (ETA), após o líquido passar pelos tanques onde as impurezas pesadas afundaram por gravidade, a água ainda contém pequenas partículas flutuantes em suspensão. Para retê-las, os engenheiros direcionam o fluxo de água para tanques verticais compostos por camadas sucessivas de cascalho grosso, areia fina e carvão ativado poroso.
A etapa descrita do tratamento de água, que força o líquido a passar por barreiras porosas para reter impurezas microscópicas, é a:
A) floculação.
B) decantação.
C) filtração.
D) cloração.
E) fluoretação.
GABARITO: C
---
Cientistas atmosféricos registraram que o uso de compostos gasosos industriais que contêm átomos de cloro e bromo provocou a abertura de uma falha em uma barreira gasosa localizada na alta atmosfera (estratosfera). Essa falha permitiu um aumento severo na incidência de raios solares ultravioleta (UV) na superfície da Terra, elevando o risco de câncer de pele na população humana.
A falha provocada pela liberação desses compostos gasosos industriais atua diretamente na:
A) intensificação do efeito estufa global.
B) formação de chuvas ácidas regionais.
C) destruição da camada de ozônio.
D) ocorrência de inversão térmica urbana.
E) criação de ilhas de calor no centro.
GABARITO: C
---
Urbanistas mediram que os bairros centrais de uma metrópole exibiam temperaturas médias até 5 °C superiores às áreas de fazendas e matas localizadas na periferia rústica da cidade. Eles apontaram que a falta de árvores impede a evapotranspiração natural que resfriaria o ar, enquanto a pavimentação asfáltica maciça atua absorvendo e estocando calor ao longo do dia.
O fenômeno climático urbano caracterizado pelo superaquecimento artificial das regiões centrais impermeabilizadas da cidade é a:
A) inversão térmica.
B) ilha de calor.
C) chuva ácida.
D) destruição do ozônio.
E) eutrofização regional.
GABARITO: B
---
Em solos de pântanos e áreas agrícolas inundadas para o plantio, a falta de oxigênio gasoso induz um grupo específico de bactérias anaeróbicas a utilizarem os nitratos do solo em seu metabolismo respiratório. Esse processo destrói a molécula de nitrato e faz com que o elemento nitrogênio retorne diretamente para a atmosfera na forma de gás molecular (N2).
A etapa do ciclo do nitrogênio em que o nitrato é convertido de volta em gás nitrogênio (N2) pelas bactérias anaeróbicas é a:
A) fixação.
B) nitrificação.
C) desnitrificação.
D) amonificação.
E) assimilação.
GABARITO: C
""".strip()

TOPICOS_ECOLOGIA = [
    # Lote 1 (1-5)
    "magnificacao_trofica", "eutrofizacao", "competicao_interespecifica", "dissipacao_termica", "fragmentacao_de_habitat",
    # Lote 2 (6-10)
    "magnificacao_trofica", "eutrofizacao", "competicao_interespecifica", "dissipacao_termica", "fragmentacao_de_habitat",
    # Lote 3 (11-15)
    "sucessao_secundaria", "mutualismo", "inquilinismo", "predacao", "predacao",
    # Lote 4 (16-20)
    "sucessao_primaria", "protocooperacao", "epifitismo", "parasitismo", "comensalismo",
    # Lote 5 (21-25)
    "protocooperacao", "epifitismo", "amensalismo", "sucessao_secundaria", "predacao",
    # Lote 6 (26-30)
    "amensalismo", "protocooperacao", "sucessao_secundaria", "amensalismo", "protocooperacao",
    # Lote 7 (31-35)
    "mutualismo", "inquilinismo", "sucessao_primaria", "comensalismo", "competicao_interespecifica",
    # Lote 8 (36-40)
    "amensalismo", "competicao_interespecifica", "inquilinismo", "amensalismo", "competicao_interespecifica",
    # Lote 9 (41-45)
    "fixacao_biologica", "aquecimento_global", "piramide_numeros_invertida", "fotossintese", "piramide_energia_direta",
    # Lote 10 (46-50)
    "fixacao_biologica", "aquecimento_global", "piramide_energia_direta", "piramide_numeros_invertida", "fotossintese",
    # Lote 11 (51-55)
    "piramide_numeros_invertida", "piramide_numeros_invertida", "respiracao_celular", "nitrificacao", "desnitrificacao",
    # Lote 13 (61-65)
    "chuva_acida", "inversao_termica", "destruicao_camada_ozonio", "chuva_acida", "inversao_termica",
    # Lote 14 (66-70)
    "coagulacao_decantacao", "decomposicao_aerobica", "chorume", "filtracao_e_cloracao", "gas_metano",
    # Lote 15 final (71-75)
    "ilha_de_calor", "chuva_de_conveccao", "pegada_de_carbono", "evapotranspiracao", "albedo",
    # Lote 16 (76-80)
    "chuva_acida", "filtracao_e_cloracao", "destruicao_camada_ozonio", "gas_metano", "inversao_termica",
    # Lote 17 (81-85)
    "chuva_acida", "coagulacao_decantacao", "destruicao_camada_ozonio", "albedo", "decomposicao_aerobica",
    # Lote 19 (91-95)
    "chuva_acida", "inversao_termica", "destruicao_camada_ozonio", "chuva_acida", "destruicao_camada_ozonio",
    # Lote 20 (96-100)
    "predacao", "piramide_numeros_invertida", "mutualismo", "nitrificacao", "competicao_interespecifica",
    # Lote 21 (101-105)
    "parasitismo", "capacidade_de_suporte", "competicao_interespecifica", "canibalismo", "potencial_biotico",
    # Lote 22 (106-110)
    "desnitrificacao", "piramide_numeros_invertida", "fixacao_biologica", "piramide_energia_direta", "nitrificacao",
    # Bloco final (111-120)
    "magnificacao_trofica", "chuva_acida", "decomposicao_aerobica", "albedo", "dissipacao_termica",
    "fixacao_biologica", "filtracao_e_cloracao", "destruicao_camada_ozonio", "ilha_de_calor", "desnitrificacao",
]

assert ECOLOGIA_TEXTO.count("GABARITO:") == 110 == len(TOPICOS_ECOLOGIA), (
    ECOLOGIA_TEXTO.count("GABARITO:"), len(TOPICOS_ECOLOGIA)
)


def main() -> None:
    resultado_optica = db.importar_questoes_praticas_texto(
        OPTICA_TEXTO, grande_area="ciencias_natureza", materia="optica", fonte=FONTE,
    )
    for id_questao, topico in zip(resultado_optica["inseridas"], TOPICOS_OPTICA):
        db.atualizar_topico(id_questao, topico)

    resultado_ecologia = db.importar_questoes_praticas_texto(
        ECOLOGIA_TEXTO, grande_area="ciencias_natureza", materia="ecologia", fonte=FONTE,
    )
    for id_questao, topico in zip(resultado_ecologia["inseridas"], TOPICOS_ECOLOGIA):
        db.atualizar_topico(id_questao, topico)

    print(f"Óptica:   {len(resultado_optica['inseridas'])} inseridas, {len(resultado_optica['erros'])} erros")
    for erro in resultado_optica["erros"]:
        print("  ERRO:", erro)
    print(f"Ecologia: {len(resultado_ecologia['inseridas'])} inseridas, {len(resultado_ecologia['erros'])} erros")
    for erro in resultado_ecologia["erros"]:
        print("  ERRO:", erro)


if __name__ == "__main__":
    main()

