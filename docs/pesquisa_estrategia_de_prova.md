# Pesquisa: o que a ciência (e quem já passou) diz sobre estudar pouco e bem

Documento de pesquisa, não de arquitetura — feito pra decidir o que vale a
pena tentar copiar pro ENEM_APP, não pra descrever código nenhum. Motivação:
Gabriel já teve a experiência de estudar 10h/dia sem reter quase nada; a
aposta agora é o oposto — pouco tempo, muito foco, engenharia reversa
agressiva do que a prova realmente cobra, e repetição pesada em cima só
disso. Este documento tenta separar o que tem evidência real por trás dessa
aposta do que é só intuição popular.

Regra seguida na pesquisa: nenhum número foi inventado. Onde a busca trouxe
um estudo controlado de verdade, cito autor/ano e o que ele mediu. Onde só
achei relato/blog/anedota (comum na parte "gente que foi bem estudando
pouco"), digo isso explicitamente — relato não é evidência controlada, mas
ainda é sinal, principalmente quando vários relatos convergem pro mesmo
padrão.

---

## 0. Roteiro da pesquisa (o que já foi coberto, o que falta)

Documento cresce em rodadas — cada `##` abaixo foi uma rodada separada,
pedida em momentos diferentes da conversa. Mantendo isto no topo pra não
repetir tema nem perder o fio entre sessões.

**Coberto até agora:**
- §1-2 — técnicas com evidência (retrieval practice, spacing, interleaving,
  TRI, testwiseness, o que NÃO funciona apesar de popular)
- §3 — relatos de quem foi bem estudando pouco tempo (ENEM/vestibular),
  com ressalva de que é sinal, não prova
- §4 — sistemas parecidos já validados em produção (Anki, Duolingo, Khan
  Academy) e o que dá pra copiar de arquitetura
- §5 — conexão dos achados com o ENEM_APP (trilha fixa, Leitner,
  prioridade_de_estudo, `topico`)
- §6 — fora do Brasil (gaokao, SAT, Oxbridge, PISA/OCDE, suneung coreano)
- §7 — desperdício de tempo e ROI por técnica (troca de tarefa,
  implementation intentions, sono, reestudar o que já sabe)
- §8 — achado ao vivo: relato real do Gabriel (repetição de padrão em
  Ecologia + "rever conteúdo" invisível lá) batendo com §2.3
- §9 — espaçamento de longo prazo (teto de 90 dias do Leitner vs. Cepeda
  et al., SM-2/FSRS vs Leitner, permastore de Bahrick) e worked
  examples/chunking (Sweller, expertise reversal, productive failure de
  Kapur) pra matéria processual (matemática) vs. conceitual (ecologia)
- §10 — redação sob prazo (escrita cronometrada, rubrica, repertório
  sociocultural) e ansiedade de prova/autoeficácia (Zeidner, expressive
  writing de Ramirez & Beilock, stress inoculation, Bandura, crítica à
  gamificação)
- §11 — estudar com apoio de IA (relatos, RCTs de tutor de IA, geração de
  questão/flashcard por IA, interleaving turbinado por tecnologia, IA como
  "banca simulada") — inclui um ALERTA real (PNAS/Turquia): acesso a IA
  em prática melhorou resolução de exercício mas PIOROU nota em prova
  real sem a IA, mesmo mecanismo de ilusão de fluência da §2.5
- §12 — geração de questão por padrão (a ideia do Gabriel de "trocar o
  padrão pro aluno pegar"): nome do campo é Automatic Item Generation
  (Gierl), distinção radical/incidental como o cuidado técnico real,
  validação de que GPT-4o gera item com dificuldade/discriminação
  equivalente a humano MAS só em fluxo com revisão humana (exatamente o
  processo atual do Gabriel), exemplos reais de mineração de padrão em
  prova (CBSE, 1.955 provas) e pipeline gera-e-valida em produção
  (Duolingo), e conexão direta com `questoes.topico`/ADR 0005 já
  existente — APROFUNDADO em §12.6-12.12 (pedido "aprofunde então"):
  processo formal de 3 estágios pra achar radical/incidental (~3h+2h por
  especialista), distractor generation baseado em erro real (60 estudos),
  overlearning ratio como equivalente formal ao "40-60 questões" (sem
  confirmar o número exato), previsão de dificuldade sem dado real
  (77% da variância explicada num caso real), dois projetos open source
  (Book-RAG, ExamRAG) fazendo o mesmo fluxo, confirmação formal na
  literatura de que a confusão ozônio×efeito-estufa×chuva-ácida É o erro
  mais documentado do mundo nesse tópico, e desenho de pipeline concreto
  em cima do que o app já tem

- §13 — até que ano vale carregar prova antiga pra análise de padrão: 2009
  é a virada real (TRI + matriz atual), não achei confirmação de corte em
  2015-2017 (a mudança de 2017 foi só logística, matriz continua a mesma
  desde 2009), TRI é comparável entre anos por design (equalização), e
  análises comerciais sérias usam a série INTEIRA 2009-2025 sem excluir
  os anos mais antigos

**Pendente / candidato pra próximas rodadas:** nenhum tema pendente
registrado no momento. Próxima rodada depende de novo pedido do Gabriel.

---

## 1. Resumo executivo — as técnicas com mais evidência, ranqueadas

1. **Retrieval practice / testing effect** — responder questão (não reler)
   é a técnica isolada com maior evidência experimental replicada pra
   retenção de longo prazo. Efeito médio-grande (g ≈ 0,50–0,61 em
   meta-análise), crescendo quanto mais tempo passa até a prova de verdade.
2. **Espaçamento (spacing effect)** — distribuir a prática no tempo em vez
   de concentrar (massed practice) supera reler/reestudar em bloco único,
   com meta-análise de 317 experimentos confirmando o efeito e mostrando
   que o intervalo ideal cresce junto com o tempo até a prova real.
3. **Interleaving (entrelaçar assunto/tipo de problema)** — misturar tipos
   de questão em vez de praticar um assunto isolado até dominar (blocked
   practice) melhora desempenho em teste posterior, principalmente em
   matemática — mesmo quando os alunos SENTEM que aprenderam menos (é uma
   "desirable difficulty": mais difícil na hora, melhor depois).
4. **Prática com feedback imediato e focada no erro** (deliberate practice
   aplicada, não a definição forte/contestada de Ericsson) — o valor não é
   "praticar muito", é fechar o loop erro → por que errei → pratica de novo
   o que errou, rápido.
5. **Análise de provas anteriores (past-paper practice)** — usar provas
   passadas pra treinar sob condição real E pra mapear o que se repete é
   uma das estratégias com mais consenso na literatura de preparação pra
   exame, mas só funciona DEPOIS de uma base mínima de conteúdo — não
   substitui aprender, substitui reler.
6. **Sono logo depois de estudar** — não é lenda: existe uma base real de
   neurociência mostrando que o sono consolida memória declarativa
   recém-formada; virar a noite estudando ou estudar até a exaustão sem
   dormir tende a jogar fora parte do que foi aprendido no dia.
7. **Autoavaliação de confiança calibrada** — parte do motivo de "estudar
   muito e não reter" é ilusão de fluência: reler/grifar cria familiaridade
   que o cérebro confunde com domínio. Testar-se (e registrar acerto/erro
   de verdade) corrige essa ilusão; só reler NUNCA corrige.
8. **Priorizar por dificuldade+frequência, não só por "matéria que gosto
   menos"** — no contexto específico do ENEM, a nota não é soma simples de
   acertos (ver TRI, seção 5) — isso muda o que "estudar bem" significa
   literalmente dentro da prova, não só na preparação.

Os itens 1–4 têm o suporte experimental mais forte e mais replicado da
psicologia cognitiva. Os itens 5–8 são mais aplicados/específicos de
contexto de prova, com evidência real mas mais heterogênea.

---

## 2. Por tema

### 2.1 Retrieval practice / testing effect

O achado central (Roediger & Karpicke, 2006, *Psychological Science*):
alunos que praticaram recuperação ativa de um texto retiveram ~61% dele
depois de uma semana, contra ~40% de quem só reestudou o mesmo texto
repetidamente pelo mesmo tempo total. Num experimento seguinte com pares
de palavras Swahili-inglês (Karpicke & Roediger, 2008, *Science*), quem
continuava SE TESTANDO nos pares já acertados lembrava ~80% deles uma
semana depois; quem só continuava reestudando os pares já acertados
(sem se testar de novo) lembrava só ~1/3 — reestudar o que você já acerta
adiciona quase nada, testar sim.

Meta-análises situam o efeito em torno de g ≈ 0,50–0,61 (efeito
médio-grande), e ele CRESCE quanto maior o intervalo de retenção — ou
seja, quanto mais longe a prova de verdade está, maior a vantagem de
testar-se em vez de reler.

Mecanismo proposto: o ato de recuperar reconstrói a memória, fortalece o
traço de armazenamento e cria rotas de recuperação adicionais — reler só
reconhece o que já está na página, não treina o "puxar de dentro" que a
prova exige.

Fontes: [The Power of Testing Memory (Roediger & Karpicke)](http://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PPS.pdf), [Repeated retrieval during learning (Karpicke & Roediger, JML)](https://learninglab.psych.purdue.edu/downloads/2007/2007_Karpicke_Roediger_JML.pdf), [Test-Enhanced Learning in the Classroom (Roediger, Agarwal et al. 2011)](https://pdf.retrievalpractice.org/guide/Roediger_Agarwal_etal_2011_JEPA.pdf).

### 2.2 Espaçamento (spacing effect) e a curva de Ebbinghaus

Cepeda, Pashler, Vul, Wixted & Rohrer (2006, *Psychological Bulletin*)
revisaram 839 comparações em 317 experimentos e confirmaram: prática
distribuída no tempo bate prática maciça (tudo de uma vez). O achado mais
importante pra decisão prática — não é "espaçar mais é sempre melhor": o
intervalo entre estudo (ISI) que maximiza retenção CRESCE junto com o
tempo até o teste final. Ou seja, o espaçamento ideal pra uma prova daqui
a 1 semana é diferente do ideal pra uma prova daqui a 6 meses — um sistema
de repetição espaçada de intervalo fixo é uma aproximação grosseira disso,
não a otimização real. Intervalos "expandindo" (crescentes) bateram
intervalos uniformes na própria meta-análise dos autores.

A curva de esquecimento de Ebbinghaus (1885) é a origem histórica da
ideia — memória decai rápido logo após aprender e depois desacelera — mas
o dado moderno (Cepeda et al.) é o que dá o número prático: o espaçamento
importa mais quanto mais longe está a prova real.

Fontes: [Cepeda et al. 2006 — página do autor](https://www.yorku.ca/ncepeda/publications/CPVWR2006.html), [Distributed Practice in Verbal Recall Tasks (ResearchGate)](https://www.researchgate.net/publication/7062225_Distributed_Practice_in_Verbal_Recall_Tasks_A_Review_and_Quantitative_Synthesis).

### 2.3 Interleaving (misturar, não bloquear)

Rohrer & Taylor (e sucessores) mostraram repetidamente, em matemática, que
misturar tipos de problema (em vez de fazer 20 questões seguidas do MESMO
tipo, que deixa óbvio qual fórmula usar antes mesmo de ler o enunciado)
melhora desempenho em teste posterior — inclusive num experimento em sala
de aula real com alunos de 7º ano (n=140) ao longo de 9 semanas, com teste
não-anunciado 2 semanas depois: quem praticou entrelaçado teve nota média
maior que quem praticou em bloco.

O motivo é o mesmo de "desirable difficulty": prática entrelaçada é mais
difícil NA HORA (você precisa decidir qual estratégia usar, não só
executá-la) — só que é exatamente essa decisão que a prova de verdade vai
cobrar, e prática em bloco nunca treina ela. A literatura tem resultados
mistos fora de matemática (alguns estudos não acharam efeito, ou
encontraram efeito negativo em domínios diferentes) — o efeito é mais
sólido especificamente pra matemática/problemas com múltiplas estratégias
possíveis, que é justamente o formato ENEM.

Fontes: [A Randomized Controlled Trial of Interleaved Mathematics Practice (Rohrer et al.)](https://gwern.net/doc/psychology/spaced-repetition/2019-rohrer.pdf), [The benefit of interleaved mathematics practice is not limited... (PubMed)](https://pubmed.ncbi.nlm.nih.gov/24578089/).

### 2.4 "Desirable difficulties" (Bjork) — o fio condutor de tudo acima

Robert Bjork (1994, formalizado depois com Elizabeth Bjork) descreve uma
categoria de manipulações que tornam a prática mais lenta e mais sujeita a
erro NA HORA, mas melhoram retenção e transferência de longo prazo:
espaçar, entrelaçar, testar-se em vez de reler, variar o contexto. A
distinção central dele é entre "performance" (ir bem AGORA, ex: decorar
pra uma prova amanhã) e "aprendizagem" (lembrar e conseguir usar depois,
em contexto diferente) — as duas parecem a mesma coisa durante o estudo,
mas geram resultados opostos. Ressalva do próprio Bjork: nem toda
dificuldade é desejável — o aluno precisa ter uma base mínima de
conhecimento pra a dificuldade ajudar em vez de só confundir (relevante
pra decidir quando entrelaçar questão difícil: só depois de alguma base,
não desde o dia 1 de uma matéria nova).

Fontes: [Desirable difficulty — Wikipedia](https://en.wikipedia.org/wiki/Desirable_difficulty), [Desirable difficulties in theory and practice (Bjork & Bjork 2020, PDF)](https://www.waddesdonschool.com/wp-content/uploads/2021/02/Desriable-Difficulties-in-theory-and-practice-Bjork-Bjork-2020.pdf).

### 2.5 Por que estudar muitas horas sem método não reteve nada (o caso pessoal do Gabriel, com respaldo)

Duas coisas na literatura explicam bem essa experiência:

- **Ilusão de fluência/competência**: reler e grifar são, de longe, os
  métodos de estudo mais populares do mundo — e estão entre os menos
  eficazes. O motivo é que reler treina RECONHECIMENTO ("essa frase é
  familiar"), enquanto a prova cobra PRODUÇÃO ("lembra o conteúdo do
  zero"). Cada releitura aumenta a familiaridade, e o cérebro interpreta
  familiaridade crescente como domínio crescente — uma ilusão que só
  piora com mais horas de releitura, não melhora.
- **Metacognição mal calibrada**: pesquisa mostra que, mesmo quando os
  próprios alunos sentem na pele o benefício de se testar (desempenho
  melhor), muitos continuam ACHANDO que reestudar é igual ou melhor que se
  testar — é um erro sistemático de julgamento sobre o próprio
  aprendizado, não falta de esforço. Intervenção que ajuda: treino
  explícito de calibração (comparar julgamento prévio com desempenho real
  repetidamente) melhora a precisão do que a pessoa acha que sabe.

Dunlosky, Rawson, Marsh, Nathan & Willingham (2013, *Psychological Science
in the Public Interest*) — o levantamento mais citado nessa área —
avaliaram 10 técnicas de estudo por utilidade com base em evidência.
Prática de recuperação e prática distribuída (itens 2.1/2.2 acima) ficaram
classificadas como ALTA utilidade; releitura, grifar/destacar e resumir
ficaram como BAIXA a moderada utilidade — não porque "não fazem nada", mas
porque o ganho por hora investida é muito menor que o das duas primeiras,
e o efeito de releitura/grifar é pouco consistente entre tipo de aluno e
tipo de material.

Fontes: [Dunlosky et al. 2013 — Psychological Science in the Public Interest](https://journals.sagepub.com/doi/abs/10.1177/1529100612453266), [PDF completo](https://gwern.net/doc/psychology/spaced-repetition/2013-dunlosky.pdf), [Illusion of competence — resumo aplicado](https://www.structural-learning.com/post/fluency-illusions-students-think-they-know).

### 2.6 Deliberate practice — o que aproveitar (e o que não)

A teoria forte de Ericsson ("expertise é quase inteiramente explicada por
prática deliberada acumulada") tem crítica séria e replicação fraca — em
domínios como xadrez e música, prática deliberada NÃO explica sozinha a
diferença entre especialistas, e uma réplica direta encontrou efeito bem
menor que o estudo original. Ou seja: não dá pra vender "só treine questão
o suficiente que qualquer um vira nota 900" como fato estabelecido — a
literatura contesta isso.

O que sobrevive da ideia, mesmo com a crítica, e É bem suportado por outra
linha de evidência (a de retrieval practice/feedback): prática só funciona
bem quando tem (a) objetivo específico do que melhorar, (b) feedback
imediato certo/errado, e (c) repetição focada especificamente no que
falhou — não "fazer mais questão genérica". Isso é o núcleo prático útil,
separado da alegação forte e contestada sobre "10 mil horas = expert".

Fontes: [Is the Deliberate Practice View Defensible? (revisão crítica, PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7461852/), [Macnamara et al. 2016 — réplica com efeito menor](https://hhs.purdue.edu/skill-learning-and-performance-lab/wp-content/uploads/sites/43/2024/08/macnamara-et-al-2016-how-important-is-deliberate-practice-reply-to-ericsson-2016.pdf).

### 2.7 Estratégia específica de prova de múltipla escolha

- **Trocar de resposta funciona, ao contrário do senso comum**: uma
  revisão de 33 estudos ao longo de 70 anos encontrou que, em média,
  quem troca de resposta melhora a nota — e em NENHUM desses 33 estudos
  trocar piorou a média. Isso contraria a crença popular (75% dos alunos e
  55% dos professores acreditam no contrário) — é um viés de memória
  chamado "first instinct fallacy": lembramos muito mais forte das vezes
  em que trocamos de certo pra errado (dói mais) do que das vezes,
  estatisticamente mais comuns, em que trocamos de errado pra certo.
  Recomendação prática da própria pesquisa: a régua não é "nunca troque",
  é acompanhar o nível de confiança na hora — trocar quando genuinamente
  reconsidera com um motivo novo, não só por ansiedade.
- **Ordem de resolução / pular questão difícil**: fontes de orientação de
  prova (não meta-análise formal, mas consistentes entre si) recomendam
  varredura inicial rápida, resolver fácil/médio primeiro, marcar e voltar
  no difícil depois — o argumento é reduzir ansiedade E garantir que
  nenhum ponto fácil seja perdido por falta de tempo no fim. Isso conecta
  direto com TRI (seção 2.8): no ENEM, errar fácil pesa proporcionalmente
  mais que errar difícil, então esse hábito não é só "conforto psicológico",
  tem lastro estatístico real na forma como a nota é calculada.
- **Reconhecimento de "pegadinha"/distrator típico de banca**: não achei
  meta-análise formal específica pra "como reconhecer pegadinha do ENEM"
  (é um tópico de exam-prep aplicado, não de laboratório) — mas a técnica
  em si (catalogar TIPOS de distrator recorrentes de uma banca específica,
  não só o conteúdo) é uma aplicação direta de "análise de padrão" (seção
  2.9) — na prática, é a mesma lógica de interleaving: reconhecer o
  PADRÃO da armadilha importa mais do que decorar a resposta de uma
  questão específica.

Fontes: [Myth: better to stick with first impulse (Association for Psychological Science)](https://www.psychologicalscience.org/uncategorized/myth-its-better-to-stick-to-your-first-impulse-than-go-back-and-change-multiple-choice-test-answers.html), [Counterfactual Thinking and the First Instinct Fallacy (Kruger et al.)](https://people.wku.edu/steven.wininger/Kruger%20First%20Instinct%20Myth.pdf).

### 2.8 TRI (Teoria de Resposta ao Item) — específico do ENEM, e isso muda a estratégia

Isto é o achado mais acionável e ESPECÍFICO do ENEM de toda a pesquisa, e
vale destacar bem: **o ENEM não soma acertos.** Cada item já foi testado
antes (pré-teste com milhares de candidatos), e o INEP conhece de cada um:
dificuldade e discriminação (capacidade do item de separar quem domina o
assunto de quem não domina). A nota final é a habilidade que melhor
EXPLICA o padrão inteiro de respostas, não a contagem de acertos.

Duas implicações práticas diretas:

1. **Errar fácil pesa mais que acertar difícil.** Um candidato que acerta
   várias questões difíceis do mesmo tópico mas erra as fáceis do MESMO
   tópico gera um padrão incoerente — o sistema reduz a confiança nesses
   acertos difíceis (trata como possível chute). Já quem acerta
   consistentemente fácil/médio de um tópico, mesmo errando parte do
   difícil, mantém proficiência alta ali — coerência importa mais que
   picos isolados de acerto.
2. **Chutar aleatoriamente em muitas questões é penalizado pela própria
   matemática do modelo**, não só pela chance de acerto de 20% — um
   padrão de acerto aleatório sem coerência por assunto reduz a
   proficiência estimada mesmo quando por acaso acerta algumas.

Isso sugere uma coisa concreta pro app: dominar SÓLIDO o básico de uma
matéria (sem furo nas fáceis) vale mais nota do que resolver questão
difícil de tópico que você não tem base nenhuma — o oposto do instinto de
"pular direto pro difícil pra impressionar".

Fontes: [Guia completo: como funciona a TRI do Enem (Exame)](https://exame.com/carreira/guia-completo-como-funciona-a-teoria-de-resposta-ao-item-tri-do-enem/), [Teoria de Resposta ao Item — Unyleya](https://blog.unyleya.edu.br/inicie-sua-carreira/teoria-de-resposta-ao-item/).

### 2.9 Análise de provas anteriores (past-paper practice)

A literatura de preparação pra exame (menos "laboratório de psicologia
cognitiva", mais "o que funciona pra alunos de verdade em provas reais")
converge em: usar provas anteriores é uma das técnicas de MAIOR consenso —
tanto pelo efeito de retrieval practice (é, literalmente, praticar
recuperação em condição real) quanto por permitir mapear o que se repete
(recorrência de tema, tipo de pegadinha, formato de enunciado). Um estudo
publicado em *Physical Review Physics Education Research* mediu impacto
de provas de prática mais realistas e mais cedo no semestre sobre
metacognição e comportamento de estudo dos alunos — achado consistente
com a ideia de que treinar sob formato real corrige calibração, não só
"decora questão".

Ressalva importante e repetida nas fontes: provas anteriores funcionam
MELHOR depois de já ter uma base mínima de conteúdo — usadas cedo demais
(sem nenhuma base), viram simulado de adivinhação, não de retrieval de
verdade. Isso valida diretamente a arquitetura que o ENEM_APP já tem
(TelaApresentacao antes do Nó 1, ver seção 3) — não é enfeite, é a ordem
certa segundo essa literatura.

Fontes: [Impact of more realistic and earlier practice exams (Phys. Rev. Phys. Educ. Res.)](https://link.aps.org/doi/10.1103/PhysRevPhysEducRes.19.010130), [Testing pays off twice (Springer, Metacognition and Learning)](https://link.springer.com/article/10.1007/s11409-022-09295-x).

### 2.10 Carga cognitiva (cognitive load theory)

Sweller (1988) e sucessores: memória de trabalho é pequena e limitada;
carga cognitiva tem 3 componentes — intrínseca (complexidade real do
conteúdo), extrínseca (como o material é apresentado — pode ser reduzida
com melhor design) e "germane" (esforço dedicado a construir schema de
verdade). Sobrecarregar memória de trabalho (informação demais de uma vez,
enunciado poluído, distração de interface) reduz aprendizagem mesmo que o
conteúdo em si esteja correto — não é sobre "o aluno não se esforçou o
suficiente", é sobre a apresentação competir por um recurso mental
limitado. Isso é argumento direto a favor de: enunciado limpo, uma questão
por vez, feedback imediato mas sem enfeite visual que disputa atenção com
o conteúdo.

Fonte: [Cognitive Load Theory — visão geral aplicada (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12246501/).

### 2.11 Sono e consolidação de memória

Não é lenda popular — há base real: sono após aprender é consistentemente
associado a melhor consolidação de memória declarativa (fatos, conceitos —
exatamente o tipo que ENEM cobra) em vários estudos controlados. Privação
de sono antes OU depois de estudar prejudica retenção em meta-análises.
Timing importa: treino à tarde mostrou retenção mais alta que treino à
noite em pelo menos um estudo controlado, mas o efeito de timing do dia
varia por tipo de memória — o achado mais robusto e consistente entre
fontes é simplesmente "não cortar sono pra estudar mais horas às vésperas
da prova" — o corte tende a devolver menos do que rende.

Fontes: [Sleep after learning aids consolidation of factual knowledge (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7953205/), [Does overnight memory consolidation support next-day learning? (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12332499/).

### 2.12 Gestão de tempo no dia da prova

Fontes de orientação prática (não meta-análise formal — mas convergentes
entre si) recomendam: 2 a 4 minutos de varredura inicial da prova inteira,
resolver fácil/médio primeiro, marcar e pular o que trava (regra comum:
se não resolveu em ~90 segundos a 3 minutos, marca e segue), voltar no
fim pro que ficou pra trás. Isso é coerente com TRI (seção 2.8): garantir
as fáceis primeiro protege a parte da nota que mais pesa antes de arriscar
tempo no que rende proporcionalmente menos.

### 2.13 O que NÃO funciona, apesar de popular

- **Reler o material** — cria familiaridade, não retenção; ver seção 2.5.
- **Grifar/destacar passivamente** — mesma raiz de problema: reconhecimento
  ilusório, sem produção ativa.
- **Resumir sem seletividade** (reescrever tudo com outras palavras, sem
  focar no que erra) — melhor que reler, mas abaixo de retrieval practice
  na classificação de Dunlosky et al.; um "resumo seletivo" (só do que
  você erra/esquece, prática já citada por fontes de preparação pro ENEM)
  é uma versão mais alinhada com retrieval practice do que resumo
  genérico de tudo.
- **Maratona sem sono / cramming intenso na véspera** — rende pior que o
  intuitivo, por dois motivos que se somam: prática massed (sem
  espaçamento) e corte de sono que prejudica consolidação do que acabou
  de ser estudado.
- **"10 mil horas garantem expertise"** — a versão forte dessa ideia
  (Ericsson) tem crítica séria e réplica fraca; não é mentira que prática
  importa, é que a quantidade bruta sozinha não é o fator decisivo — o
  tipo de prática (com feedback, focada no erro) é.

---

## 3. Relatos (não é estudo controlado — é sinal, com essa ressalva clara)

Busquei especificamente relatos de aprovados no ENEM/vestibular que
estudaram pouco tempo e foram bem, focando no que mais cai. O material
encontrado é majoritariamente de blogs de cursinho (não é fonte
independente — tem interesse comercial em vender curso), então trato
como pista de padrão recorrente, não como prova:

- Convergência entre várias fontes distintas de orientação pra ENEM:
  priorizar Matemática e Redação (maior peso/impacto relativo na nota
  final combinada), estudar por META DE TÓPICO concluído, não por HORA
  cumprida, blocos curtos (relatado como ~50 min de foco + intervalo) em
  vez de sessão longa contínua, e revisão em camadas com intervalos
  crescentes (citado como 24h / 7 dias / 30 dias — um padrão de
  espaçamento expandido, coerente com o achado real de Cepeda et al. na
  seção 2.2, mesmo vindo de fonte não-acadêmica).
- O padrão qualitativo comum entre essas fontes ("qualidade e constância
  batem maratona exaustiva", "resolva exercício, não releia") é
  literalmente o mesmo argumento da seção 2.5 (Dunlosky et al.) — só que
  chegando lá por experiência relatada, não por experimento controlado.
  A convergência entre uma literatura acadêmica séria e relato de quem
  passou é o dado mais forte deste documento pra validar a aposta do
  Gabriel: os dois caminhos, independentes, apontam pro mesmo lugar.
- Não encontrei um relato individual isolado, verificável e detalhado
  (tipo "fulano estudou X meses, Y horas/semana, fez Z e tirou nota W")
  robusto o bastante pra citar como caso — o que existe é conteúdo
  agregado de cursinho descrevendo o "método dos aprovados" de forma
  genérica. Vale registrar essa limitação em vez de forçar uma fonte
  fraca como se fosse forte.

Fontes (tratadas como relato, não pesquisa): [Bernoulli — Técnicas de estudo para o Enem](https://www.bernoulli.com.br/quem-somos/acontece-no-bernoulli/tecnicas-de-estudo-para-o-enem-estrategias-para-notas-altas/), [Aprova Total — Como estudar com pouco tempo](https://unifaveni.com.br/como-estudar-para-o-enem-com-pouco-tempo-disponivel-por-dia/).

---

## 4. Sistemas parecidos — o que já foi validado em produção

- **Anki / algoritmo SM-2 e descendentes**: repetição espaçada com
  intervalo crescente por item, ajustado por acerto/erro — a mesma ideia
  central do Leitner simplificado que o ENEM_APP já usa
  (`db._calcular_leitner()`), só que Anki calibra o multiplicador por
  "facilidade" individual do card em vez de só streak. Não achei
  meta-análise formal específica de Anki (é ferramenta, não teoria), mas
  ele implementa diretamente o spacing effect (seção 2.2) validado em
  laboratório.
- **Duolingo — Half-Life Regression (Settles & Meeder, 2016, ACL)**:
  publicado com 13 milhões de "traços" de aprendizagem reais de usuários,
  o modelo estima o "meio-tempo" de memória de cada item por usuário
  (em vez de um intervalo fixo por streak) e reduziu erro de previsão de
  recall em ~16% relativo ao SM-2 clássico. É a versão "aprende com dado
  real do próprio usuário" do mesmo princípio de espaçamento — mostra que
  dá pra ir além de um Leitner de intervalo fixo usando o histórico real
  de acerto/erro por questão/tópico que o ENEM_APP já registra em
  `tentativas_usuario`.
- **Khan Academy / mastery learning / "Bloom's 2 Sigma Problem"**: Bloom
  (1984) mostrou que tutoria individual (1 aluno : 1 tutor, com domínio
  exigido antes de avançar) produzia desempenho ~2 desvios-padrão acima de
  aula tradicional em grupo — o "problema" é que tutoria individual não
  escala. Khan Academy é a tentativa mais conhecida de aproximar isso via
  software (avançar só após domínio, dado real de erro decidindo o que
  reforçar). Uma revisão de sistemas de aprendizagem adaptativa encontrou
  efeito médio de ~0,70 desvio-padrão sobre controle não-adaptativo — forte,
  mas ainda abaixo do 2-sigma de tutoria humana individual. Ponto relevante
  pro ENEM_APP: a arquitetura de "priorizar o que você mais erra E o que
  mais cai" (`prioridade_de_estudo()`) é literalmente a mesma ideia central
  por trás desses sistemas — o que falta pra chegar mais perto do efeito
  observado neles é a MESMA coisa que os fez funcionar: não deixar o aluno
  avançar sem sinal real de domínio, e ajustar o próximo conteúdo pelo
  padrão de erro individual, não por um cronograma fixo.

Fontes: [A Trainable Spaced Repetition Model for Language Learning (Duolingo)](https://research.duolingo.com/papers/settles.acl16.pdf), [Bloom's 2 Sigma Problem — Wikipedia](https://en.wikipedia.org/wiki/Bloom's_2_sigma_problem), [Nintil — revisão sistemática de mastery learning e tutoria](https://nintil.com/bloom-sigma/).

---

## 5. O que isso sugere pro ENEM_APP (direção, não prescrição)

Conectando cada achado de maior evidência a algo que já existe ou poderia
existir — sem prescrever implementação, só apontando pra onde a evidência
empurra:

- **Retrieval practice (2.1) já é o núcleo do app** (responder questão >
  reler) — o ganho marginal maior aqui não é "adicionar retrieval", é
  proteger esse núcleo de virar releitura disfarçada (ex: um "ver
  explicação" fácil demais de abrir ANTES de tentar responde,
  em vez de depois — o botão de explicação que acabei de implementar
  correndo aparece só DEPOIS de responder, de propósito, alinhado com
  isso).
- **Espaçamento (2.2) já existe via Leitner simplificado** — a direção que
  a evidência aponta (Cepeda et al.: intervalo ideal cresce com a distância
  até a prova real) sugere que um intervalo fixo por streak é uma
  aproximação; o histórico real em `tentativas_usuario` (que já é
  gravado) teoricamente permite algo mais parecido com Half-Life
  Regression do Duolingo no futuro, se algum dia valer o esforço de
  mexer nisso — não é urgente, o Leitner atual já captura o princípio
  central.
- **Interleaving (2.3)**: a trilha fixa entrelaçada entre matérias de
  Ciências da Natureza (já existe, ver `TRILHA_FIXA_NOS`/`arquitetura-trilha.docx`)
  é literalmente esse princípio aplicado — a pesquisa dá respaldo
  concreto pra essa escolha de arquitetura já feita, não é só intuição.
- **TRI (2.8) é o achado mais específico e mais alinhado com o objetivo
  do Gabriel** ("engenharia reversa da prova"): a implicação prática —
  dominar sólido o fácil/médio de um tópico vale mais que acertar difícil
  isolado do mesmo tópico — sugere que `prioridade_de_estudo()` e a
  hipótese de "padrão de cobrança" (`topico`, ver ADR 0005) já estão na
  direção certa, e que uma futura métrica de "coerência por tópico" (acerta
  fácil e médio antes de avançar pro difícil do mesmo assunto) teria
  respaldo teórico real, não seria só gamificação.
- **Past-paper practice (2.9) valida a ordem já escolhida no app**:
  TelaApresentacao (conteúdo base) ANTES do Nó 1, prática de questão
  DEPOIS — a literatura confirma que provas/questões de prática rendem
  mais quando já existe uma base mínima, não early demais. O botão novo
  de "rever conteúdo base" no meio de uma questão também é coerente com
  isso — deixa reforçar a base sem quebrar o fluxo de retrieval.
- **Metacognição/calibração (2.5)**: o sistema de streak + acerto real
  gravado já corrige, estruturalmente, a ilusão de fluência (não tem como
  "achar que sabe" sem confrontar um resultado real). Um ganho possível
  seria pedir, ANTES de confirmar a resposta, um nível de confiança
  (ex: "tenho certeza" / "cutucando") — é exatamente a manipulação que a
  pesquisa de calibração (seção 2.5) usa pra treinar julgamento de
  aprendizagem mais preciso; fica registrado aqui como ideia com respaldo,
  não como próximo passo decidido.
- **Sono (2.11) e gestão de tempo no dia da prova (2.12)** são as duas
  áreas onde a evidência é real mas está fora do escopo de "app de banco
  de questões" — mais relevante pro planejamento pessoal do Gabriel
  (não virar a noite estudando véspera de simulado grande) do que pra
  uma feature de software.
- **O que a pesquisa NÃO sustenta**: qualquer promessa de atalho
  "estudo pouco e garanto nota alta" sem o par retrieval+espaçamento
  fazendo o trabalho de verdade — a aposta do Gabriel (pouco tempo, muito
  foco, repetição pesada em cima do que mais cai) é exatamente o que a
  literatura sustenta, DESDE que "foco" signifique praticar recuperação
  ativa espaçada no que a prova realmente cobra — não signifique estudar
  pouco tempo mas do jeito errado (reler resumo bonito por 40 minutos é
  "pouco tempo" e ainda assim ineficaz, pelos mesmos motivos da seção 2.5).

---

## 6. Fora do Brasil — outros vestibulares de alta pressão, e onde "estudar mais esperto" realmente aparece

Pedido explícito do Gabriel: olhar pra fora, especificamente atrás de gente/
sistema mais ESTRATÉGICO, não só "mais estudado". A resposta honesta é mista
— tem um achado forte e direto a favor da tese dele (seção 6.1), tem uma
técnica que aparece repetida de forma quase idêntica em TODO sistema de
admissão seletiva do mundo (seção 6.2), e tem um contraste que precisa ser
dito sem filtro: os sistemas asiáticos de alta pressão mais citados como
"exemplo" são, na verdade, o OPOSTO de "pouco tempo" (seção 6.4) — a
inteligência ali não está em estudar menos, está na estrutura da prática
dentro de muitas horas.

### 6.1 OCDE/PISA: mais horas de estudo NÃO correlaciona com melhor nota — o achado mais forte desta rodada

Este é provavelmente o dado mais direto de todo o documento a favor da
aposta do Gabriel, e vem de fora do Brasil, comparando dezenas de países:
na PISA 2022, sistemas educacionais com alunos estudando entre 24 e 27
horas semanais de aula regular tendem a pontuar MELHOR em matemática que
sistemas com menos de 20h OU mais de 39h semanais — ou seja, existe um
ponto de excesso a partir do qual mais hora deixa de ajudar e passa a
associar com nota pior. O mesmo padrão aparece em lição de casa: sistemas
onde mais alunos fazem até 2h/dia de dever pontuam melhor, em média, do
que sistemas onde 3h+ é comum.

O exemplo mais citado pra ilustrar isso: a Finlândia (~14h de aula/semana)
supera a Coreia do Sul (~3h a mais por semana em sala) em matemática e
ciência — mais tempo em sala não é o fator decisivo, qualidade da prática
é. A própria OCDE resume: tempo de aula regular tem correlação positiva
mas FRACA com desempenho do país, e tempo de estudo individual/fora da
escola tem correlação NEGATIVA — sinal de que estudo extra mal orientado
(cramming, aula particular sem foco) pode ativamente atrapalhar, não só
"não ajudar".

Fontes: [Learning time and disciplinary climate (OECD)](https://www.oecd.org/en/topics/sub-issues/learning-time-and-disciplinary-climate.html), [Study Time and Scholarly Achievement in PISA (paper)](https://economicsofeducation.com/wp-content/uploads/2020/02/053.pdf).

### 6.2 Past-paper practice — a técnica que se repete, quase idêntica, em todo sistema seletivo do mundo

Analisar e resolver provas ANTERIORES de verdade (não questão genérica de
banco de terceiros) aparece como técnica central e documentada em
praticamente todo sistema de admissão competitiva que existe, com o mesmo
racional em todos: você treina formato real + recuperação ativa + mapeia
padrão de cobrança da banca, tudo ao mesmo tempo. Alguns exemplos
concretos, fora do Brasil:

- **Gaokao (China)** — provas anteriores, chamadas de *zhenti/zhenkaoti*
  (真题/真考题), são descritas por fontes de preparação como "o padrão
  ouro" da preparação de matemática pro gaokao, justamente porque o
  formato da prova se repete de forma consistente ano a ano e as provas
  reais de décadas anteriores são públicas — é praticamente o mesmo
  princípio do banco de questões reais que o ENEM_APP já usa como matéria
  prima (`questoes` com `origem='enem_oficial'`), só que a cultura de
  estudo lá nomeia e centraliza isso como técnica própria.
- **Oxbridge (Oxford/Cambridge, testes de admissão)** — orientação oficial
  de preparação recomenda: fazer a primeira prova antiga cedo, completa e
  cronometrada, como DIAGNÓSTICO (não como treino ainda), depois ESPAÇAR
  as provas seguintes ao longo das semanas até o teste real pra conseguir
  medir evolução — é literalmente o spacing effect (seção 2.2) aplicado
  na prática de admissão mais seletiva do Reino Unido, description
  quase didática do próprio princípio.
- **SAT/ACT (EUA)** — não é só orientação informal: existe DADO REAL em
  larga escala. A parceria Khan Academy + College Board publicou que 20h
  de prática oficial personalizada (adaptativa — ajusta o que praticar
  pelo erro de cada aluno) correlacionam com ganho médio de 115 pontos na
  prova redesenhada, quase o dobro do ganho de quem não usa a plataforma;
  mesmo só 6h de prática com pelo menos uma "boa prática" já correlaciona
  com ~40 pontos a mais, num estudo com ~250 mil alunos reais. É a mesma
  arquitetura central que `prioridade_de_estudo()`/Leitner do ENEM_APP já
  implementam — prática adaptada ao erro individual, não bloco genérico —
  só que aqui com número real de impacto em prova de admissão de verdade.

Ressalva igual à da seção 2.9: past-paper practice funciona melhor DEPOIS
de uma base mínima — nenhuma das fontes acima recomenda começar por prova
antiga sem nenhum conteúdo de base.

Fontes: [Preparation for the Gaokao — GK.NET](https://www.gk.net/gaokao/en/004-preparation-for-the-gaokao-strategies-and-tips-for.html), [Cracking the Code: Gaokao tips (Acquire Education)](https://www.acquireeducation.com/cracking-the-code-tips-and-tricks-for-gaokao-entrance-exam/), [Mock Admissions Tests — Oxbridge Applications](https://oxbridgeapplications.com/mock-admissions-tests/), [New Data Links 20 Hours of Official SAT Practice to 115-Point Gains (College Board Newsroom)](https://newsroom.collegeboard.org/new-data-links-20-hours-personalized-official-sat-practice-khan-academy-115-point-average-score), [OSP Technical Report (College Board Research, PDF)](https://research.collegeboard.org/media/pdf/osp-technical-report.pdf).

### 6.3 Testwiseness — uma linha de pesquisa própria sobre estratégia DE PROVA (não de conteúdo)

Existe uma linha de pesquisa específica, separada de "quanto/como estudar
conteúdo", chamada *testwiseness* — a capacidade de usar as
características do FORMATO da prova (não o domínio da matéria) pra
pontuar mais. A referência fundadora é Millman, Bishop & Ebel (1965, *An
Analysis of Test-Wiseness*, *Educational and Psychological Measurement*),
que definiram o conceito como logicamente independente do conhecimento de
conteúdo — é uma habilidade treinável à parte. Um achado relevante de
replicações posteriores: pra usar test-wiseness de verdade (eliminar
alternativa por pista estrutural do enunciado, por exemplo), o aluno
ainda precisa de conhecimento mínimo do conteúdo do enunciado/opções —
não é um atalho que substitui saber a matéria, é um multiplicador em cima
de uma base que já existe. Isso é exatamente a mesma lógica de "pegadinha
de banca" já discutida na seção 2.7 — só que aqui com nome próprio e
tradição de pesquisa de 60 anos, incluindo instrumentos formais (o
teste de 14 itens de Millman/Bishop/Ebel) pra medir o quanto um aluno já
domina isso separado do conteúdo.

Fontes: [An Analysis of Test-Wiseness — Millman, Bishop & Ebel 1965 (Sage)](https://journals.sagepub.com/doi/abs/10.1177/001316446502500304), [Using Test-Taking Strategies to Maximize Multiple-Choice Test Scores (Dolly & Williams 1986)](https://doi.org/10.1177/0013164486463014), [The Relative Difficulty of Selected Test-Wiseness Skills (Morse 1998)](https://doi.org/10.1177/0013164498058003003).

### 6.4 Onde a tese "menos horas, mais esperto" NÃO se sustenta lá fora — dito sem filtro

Os sistemas de admissão mais competitivos e mais citados como referência
mundial de "prova difícil" — gaokao chinês e *suneung*/CSAT sul-coreano —
são, na prática, o exato OPOSTO de "poucas horas": relatos e reportagens
consistentes (não um único caso isolado) descrevem alunos do ensino médio
chinês estudando 12h+/dia em rotina comum, com escolas-fábrica como
Maotanchang (~10 mil alunos, rotina de 6h10 às 22h50, dois intervalos de
30min pra refeição) virando símbolo nacional do modelo; na Coreia, quem
se prepara pro *suneung* comumente frequenta *hagwon* (cursinho privado)
desde os 4-5 anos de idade, com estudantes do ensino médio dormindo em
média ~5h30 por noite nos meses antes da prova e menos de 1h/dia de lazer
— aos pontos de o próprio governo coreano classificar publicamente os
hagwons como "cartel da educação privada" e tentar (sem sucesso total)
limitar o horário de funcionamento deles, e de reportagens ligarem essa
cultura de pressão a problemas sérios de saúde mental adolescente.

Isso não invalida o que já foi levantado nas seções anteriores — dentro
dessas MUITAS horas, a prática ainda é estruturada (provas cronometradas
repetidas, foco em past-paper, feedback constante de professor/tutor), o
que é coerente com "prática deliberada com feedback" (seção 2.6). Mas a
honestidade aqui importa: não existe um sistema de admissão de elite
mundial conhecido por "poucas horas E nota alta" ao mesmo tempo — o que
existe, e é o que sustenta de verdade a aposta do Gabriel, é a evidência
CONTROLADA (retrieval practice, espaçamento, interleaving, PISA/OCDE
seção 6.1, SAT/Khan Academy seção 6.2) de que, PRA UM INDIVÍDUO com tempo
real limitado (não decidindo currículo de um país), técnica estruturada
rende mais por hora investida do que volume bruto sem método — é uma
afirmação sobre EFICIÊNCIA MARGINAL por hora, não sobre "gente inteligente
lá fora estuda pouco e vai bem", que os dados de gaokao/suneung
contradizem diretamente se lida ao pé da letra.

Fontes: [China's Cram School from Hell (Foreign Policy)](https://foreignpolicy.com/2013/10/11/chinas-cram-school-from-hell/), [What China's most famous "gaokao factory" reveals (AsiaNews Network)](https://asianews.network/what-chinas-most-famous-gaokao-factory-reveals-about-the-limits-of-its-exam-driven-education-model/), [The Price of Perfection: Korea's Cram School Culture](https://thesciencesurvey.com/editorial/2026/07/25/the-price-of-perfection-pressure-inside-koreas-cram-school-culture/), [South Korea's Hagwon Culture: A Failure of Education? (Vanguard Think Tank)](https://vanguardthinktank.org/south-koreas-hagwon-culture-a-failure-of-education), [South Korea is cutting "killer questions"... (CNN)](https://www.cnn.com/2023/07/01/asia/south-korea-college-exam-fertility-pressure-intl-hnk-dst).

### 6.5 O que a seção 6 acrescenta pro ENEM_APP (direção, não prescrição)

Os dois achados mais fortes desta rodada — **6.1 (PISA/OCDE: mais hora
não é mais nota, qualidade da prática domina)** e **6.2 (past-paper
practice como técnica quase universal em sistema seletivo, com dado real
de escala no caso SAT/Khan Academy: prática adaptativa ao erro
individual rendendo ganho mensurável)** — reforçam, com evidência de
fora do Brasil e em outra escala (país inteiro, meio milhão de alunos),
exatamente os mesmos dois pilares já identificados na seção 5 a partir da
literatura de psicologia cognitiva: (a) o app já usa questão REAL de
prova como matéria-prima, o que a seção 6.2 mostra ser a prática mais
replicada mundialmente em admissão seletiva, não uma escolha só
brasileira; (b) o modelo de "praticar o que você mais erra, adaptado por
indivíduo" (`prioridade_de_estudo()`, Leitner) é a mesma arquitetura que
o caso SAT/Khan Academy mediu render ganho real em escala — o número
concreto (115 pontos/20h) é uma referência externa de que esse tipo de
sistema, quando bem calibrado, tem efeito mensurável de verdade, não só
plausibilidade teórica. A seção 6.3 (testwiseness) sugere que "catalogar
padrão de pegadinha de banca" (já cogitado na seção 2.7) tem uma
tradição de pesquisa própria com 60 anos, o que dá mais peso pra tratar
isso como categoria própria de estudo (separada de "dominar conteúdo"),
não só um efeito colateral de fazer muita questão. E a seção 6.4 é o
freio necessário: nenhum desses achados autoriza interpretar "estudar
pouco tempo" como sinônimo de "sistema de admissão de elite mundial" —
a honestidade que sustenta a aposta do Gabriel é mais estreita e mais
específica do que isso (eficiência por hora individual, não um atalho
validado por outros países).
---

## 7. Desperdício de tempo e ROI por técnica

Pedido explícito do Gabriel, reformulado depois de uma rodada anterior que
saiu do foco: ele não está atrás de "lá fora estudam pouco" — está atrás de
**onde o tempo investido se perde** (pra cortar isso) e **o que rende mais
POR HORA investida**, com relato/documentário além do estudo controlado.
As seções anteriores já cobriram o maior vilão isolado (reler/grifar, seção
2.5) — esta seção vai atrás do que ainda não foi coberto: escolha errada do
QUE estudar, interrupção, sono como corte de ROI e não só "regra de boa
conduta", e o que existe (pouco, mas existe) de tentativa de comparar
retorno por hora entre técnicas.

### 7.1 Reestudar o que você já sabe — o desperdício mais escondido de todos

Existe uma diferença entre "reler o texto errado" (seção 2.5) e um problema
mais sutil: mesmo quando o aluno pratica retrieval de verdade, ele tende a
ESCOLHER revisar de novo o que já domina, porque acertar de novo dá uma
sensação imediata de competência — e essa escolha rouba tempo do que
realmente precisa de mais prática. A pesquisa mostra dois ângulos
complementares:

- Fazer um julgamento explícito de "aprendi isso?" (judgment of learning)
  logo depois de estudar aumenta a chance de o aluno escolher reestudar
  justamente os itens que ele JÁ ACERTOU — um viés de reforçar conforto, não
  cobrir lacuna.
- Comparando dois tipos de julgamento, quem faz um julgamento de CONFIANÇA
  retrospectivo (não só "aprendi ou não", mas "quão confiante estou") fica
  bem melhor em decidir o que NÃO precisa mais de revisão — ou seja, o
  problema não é falta de metacognição nenhuma, é o TIPO de pergunta que o
  aluno faz a si mesmo antes de decidir o que revisar de novo.

Aplicação direta: perguntar "confio nisso ou só reconheço?" antes de decidir
revisar de novo um tópico já é mais eficaz do que só perguntar "eu sei
isso?" — a segunda pergunta tende a resposta "sim" cedo demais.

Fontes: [Making Judgments of Learning Increases Restudy Choices (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13413214/), [Making Retrospective Confidence Judgments Improves Learners' Ability to Decide What Not to Study (Robey, Dougherty & Buttaccio 2017)](https://doi.org/10.1177/0956797617718800), [How to Learn What Not to Study (Association for Psychological Science)](https://www.psychologicalscience.org/publications/observer/obsonline/how-to-learn-what-not-to-study.html).

### 7.2 Interrupção e troca de tarefa — o custo é maior do que parece na hora

Duas linhas de pesquisa, uma mais de laboratório e uma mais de campo, apontam
pro mesmo problema por ângulos diferentes:

- **Rubinstein, Meyer & Evans (2001, *Journal of Experimental Psychology:
  Human Perception and Performance*)** — em 4 experimentos controlados,
  alternar rapidamente entre tarefas (mesmo tarefas simples e familiares)
  aumenta tempo de reação e taxa de erro; o custo de troca cresce com a
  complexidade da regra e diminui quando existe um sinal claro de qual
  tarefa vem a seguir. É a base experimental de que "multitasking" durante
  estudo tem custo real, mensurável, não é só sensação.
- **Gloria Mark (UC Irvine, observação de campo em ambiente de trabalho
  real, citada de forma consistente desde 2008 em replicações e reportagens
  subsequentes)** — depois de uma interrupção que exige pensar de novo
  (não uma interrupção trivial), leva em média ~23 minutos pra voltar ao
  nível de foco anterior. Separadamente, o tempo médio numa mesma tela/
  atividade antes de trocar caiu de ~2,5 minutos (2004) pra ~47 segundos
  em medições mais recentes — o ambiente de hoje (notificação de celular)
  interrompe numa frequência incompatível com esse tempo de recuperação.
- Mesmo uma notificação que a pessoa NÃO responde já reduz desempenho em
  tarefa que exige atenção — o simples aviso já puxa atenção ou dispara
  monitoramento mental de "será que preciso olhar", mesmo sem checar o
  celular.

Aplicação direta pro Gabriel: uma sessão de 50 minutos com o celular no
modo avião (ou fora da sala) rende mais que 90 minutos com notificação
ligada — não é força de vontade, é custo cognitivo mensurável de trocar de
contexto, que o cérebro paga de novo a cada interrupção, mesmo pequena.

Fontes: [Executive Control of Cognitive Processes in Task Switching (Rubinstein, Meyer & Evans 2001, PDF via APA)](https://www.apa.org/pubs/journals/releases/xhp274763.pdf), [The Attentional Cost of Receiving a Cell Phone Notification](https://www.researchgate.net/publication/279457726_The_Attentional_Cost_of_Receiving_a_Cell_Phone_Notification), [It takes 23 mins to recover after an interruption (resumo da pesquisa de Gloria Mark)](https://addyo.substack.com/p/it-takes-23-mins-to-recover-after).

### 7.3 Sono não é "regra de boa conduta" — é corte direto de ROI

A seção 2.11 já cobriu que sono consolida memória declarativa. O ponto que
falta aqui, específico de ROI: cortar sono pra "ganhar" mais hora de estudo
na prática DEVOLVE MENOS do que rende, porque a mesma hora de estudo cansado
produz menos retenção por hora do que uma hora de estudo descansado — ou
seja, sacrificar sono pra estudar mais não é neutro, é trocar hora "cara"
(baixo retorno, estudando exausto) por hora que já foi investida durante o
dia com retorno melhor. Não é sobre "durma bem porque é saudável", é sobre
o cálculo de retorno por hora não fechar a conta de quem faz essa troca.

(Ver fontes já citadas na seção 2.11 — não repetidas aqui de propósito.)

### 7.4 ROI por técnica — o que existe formalmente, e o que é relato sério de praticante

Comparação FORMAL de "retorno por hora" entre técnicas de estudo é rara na
literatura acadêmica — os estudos controlados (seções 2.1-2.4) comparam
RETENÇÃO entre técnicas, quase nunca tempo investido em cada uma de forma
equalizada o bastante pra virar um número de "ROI por hora" direto. Onde
existe uma tentativa mais próxima disso:

- **Dunlosky et al. 2013** (já citado na seção 2.5) é o mais próximo de uma
  comparação formal: ao classificar 10 técnicas por UTILIDADE (não só por
  eficácia absoluta), o critério explícito dos autores inclui o quão bem a
  técnica se generaliza pra diferentes idades/matérias/formatos de prova
  COM POUCO TREINO PRÉVIO do próprio aluno na técnica — ou seja, já é uma
  espécie de "custo de adoção" embutido no ranking, mesmo sem ser chamado
  de ROI.
- **Fora da academia, com peso de evidência menor mas relevante**: Barbara
  Oakley ("A Mind for Numbers"/curso "Learning How to Learn", uma das
  formações online mais assistidas do mundo em técnicas de estudo,
  professora de engenharia, não só divulgadora) defende explicitamente
  blocos curtos de foco (Pomodoro, ~25 min foco + pausa) alternados com
  "modo difuso" (mente solta, sem foco direto no problema) como forma de
  aproveitar consolidação que acontece FORA da hora sentado estudando — a
  alegação central dela é que empurrar sessão de estudo pra além do ponto
  de fadiga tem retorno marginal decrescente rápido, mesmo sem citar um
  número de ROI formal.
- **Scott Young ("Ultralearning", MIT Challenge — aprendeu o currículo de
  4 anos de Ciência da Computação do MIT sozinho, batendo nos exames finais
  reais, em 12 meses)**: é RELATO DE PRATICANTE, não estudo controlado —
  tratado aqui com a mesma ressalva da seção 3. O método dele é
  essencialmente uma aplicação agressiva do que já está nas seções
  2.1-2.4 (retrieval/prática ativa, não passividade) com um passo extra
  que a literatura acadêmica citada não cobre tão explicitamente:
  **metalearning** — antes de estudar o conteúdo, gastar um tempo pequeno
  mapeando COMO aquele assunto costuma ser cobrado/estruturado (o
  equivalente, em espírito, ao "padrão de cobrança"/`topico` que o
  ENEM_APP já testa como hipótese) — e overlearning direcionado só no que
  é mais cobrado, não uniforme.

Honestidade necessária: não existe hoje uma tabela confiável de "técnica X
rende Y% de retenção por hora investida" comparando retrieval practice vs
spacing vs interleaving de forma equalizada por tempo — o que existe é
convergência entre a classificação por UTILIDADE de Dunlosky et al. (mais
acadêmica) e o relato de praticantes de alta performance (Oakley, Young)
apontando pro MESMO conjunto pequeno de técnicas (retrieval, blocos curtos
com pausa, foco no que falta, mapear o formato da cobrança antes de
mergulhar no conteúdo).

Fontes: [Ultralearning Manifesto/Principles (Scott Young)](https://www.scribd.com/document/926326347/Kupdf-net-Ultralearning-Manifesto-Scott-Youngpdf-en-Es), [Learning How to Learn — resumo de conceitos (Erudia)](https://erudia.io/courses/barbara-oakley-learning-how-to-learn), [Barbara Oakley — dicas contra procrastinação e Pomodoro (Mentalzon)](https://mentalzon.com/en/post/4985/barbara-oakleys-essential-tips-for-beating-procrastination-and-boosting-memory).

### 7.5 Falta de plano específico é, ela mesma, uma fonte de desperdício (implementation intentions)

Gollwitzer (linha de pesquisa consolidada desde os anos 1990, com
meta-análise de Gollwitzer & Sheeran 2006 somando 94 estudos independentes
e >8.000 participantes, efeito médio d ≈ 0,65 — médio-grande, e não
encolhe com amostra maior, sinal de que não é artefato de viés de
publicação) mostra que transformar uma meta vaga ("vou estudar mais") num
plano do tipo SE-ENTÃO ("SE for 19h, ENTÃO abro o app e faço o bloco de
Ecologia") aumenta muito a chance de execução real. Uma meta-análise mais
recente (642 testes independentes) refina isso: o efeito é maior
especificamente quando o plano tem formato condicional explícito
(se-então, não só "vou fazer X"), a pessoa já está motivada pela meta em
si (o plano não cria motivação do zero, só destrava execução de uma
motivação que já existe), e o plano é repetido/ensaiado pelo menos uma vez
antes.

Isso é relevante pro desperdício de tempo especificamente porque muito do
que PARECE falta de disciplina é, na verdade, falta de gatilho específico:
"vou estudar hoje" sem hora/lugar/ação definidos deixa a decisão de
QUANDO começar pra um momento de baixa energia (final do dia, cansado),
que é justamente quando mais se perde tempo decidindo em vez de fazendo.

Fontes: [Implementation Intentions and Goal Achievement: A Meta-Analysis of Effects and Processes (Gollwitzer & Sheeran 2006)](https://www.researchgate.net/publication/37367696_Implementation_Intentions_and_Goal_Achievement_A_Meta-Analysis_of_Effects_and_Processes), [The When and How of Planning: Meta-Analysis of 642 Tests (2024)](https://www.tandfonline.com/doi/abs/10.1080/10463283.2024.2334563).

### 7.6 Relatos brasileiros — cultura de "aprovado em concurso em poucos meses"

O Brasil tem uma cultura MUITO documentada disso, mas fora do ENEM: o
universo de concursos públicos de alta concorrência (Receita Federal, TRT,
INSS, carreiras policiais). Busquei especificamente relato/conteúdo dessa
cena, com a mesma ressalva da seção 3 — a maior parte é conteúdo de
cursinho/blog com interesse comercial, então trato como sinal de padrão
convergente, não como prova:

- Convergência entre várias fontes distintas: "constância vence
  intensidade" (2h/dia por 2 anos relatado como batendo 8h/dia por 6 meses
  interrompidos), Pomodoro modificado (50min foco + 10min pausa, 4 ciclos
  + pausa maior de 30min) citado especificamente por aprovados em carreiras
  federais de alta dificuldade, e o mesmo mantra despejado em praticamente
  toda fonte: "quem estuda 4h com foco aprende mais que quem estuda 10h
  distraído" — literalmente o mesmo argumento da seção 2.5, chegando lá por
  relato de concurseiro, não por Dunlosky et al.
- O padrão QUALITATIVO (constância > intensidade, bloco curto com pausa,
  foco > hora bruta) converge tanto com a literatura acadêmica (seções
  2.1-2.5) quanto com os relatos de ENEM já levantados na seção 3 — três
  fontes independentes (psicologia cognitiva, relato de vestibulando,
  relato de concurseiro) apontando pro mesmo padrão é o tipo de
  convergência que vale mais que qualquer uma delas sozinha.
- Mesma limitação da seção 3: não achei um caso individual isolado,
  detalhado e verificável ("fulano estudou X meses, Y horas, método Z,
  nota W") robusto o bastante pra citar como estudo de caso — o que existe
  é conteúdo agregado e genérico de cursinho.

Fontes (tratadas como relato, não pesquisa): [Como Passar em Concurso em 6 Meses (Painel do Concurseiro)](https://paineldoconcurseiro.com/como-passar-em-concurso-em-6-meses/), [Quantas horas estudar para concurso público — guia com faixas reais (Passa no Concurso)](https://passanoconcurso.com.br/quantas-horas-estudar-concurso-publico), [Os meus segredos para ter sucesso em concursos públicos (relato pessoal, Substack)](https://yohannbtc.substack.com/p/os-meus-segredos-para-ter-sucesso).

### 7.7 Recomendações diretas pro método do Gabriel (não é sobre o app)

Objetivas, sem enrolação, ranqueadas pelo peso de evidência por trás:

1. **Celular fora da sala (não só silencioso) durante todo bloco de
   estudo.** Uma notificação não respondida já custa atenção; o custo de
   religar foco depois de uma interrupção real é ~23 minutos — maior que
   o próprio bloco de Pomodoro. (Evidência: 7.2, forte — controlada + campo.)
2. **Antes de decidir revisar um tópico de novo, perguntar "confio nisso
   ou só reconheço?"** — não "eu sei isso?". A segunda pergunta engana
   fácil; a primeira não. (Evidência: 7.1, controlada.)
3. **Blocos de ~50 minutos de foco, pausa de verdade entre eles** (não
   "pausa" que é só trocar de tela) — convergência entre Oakley (Pomodoro/
   modo difuso) e o relato de concurseiro brasileiro de alta dificuldade
   (7.4, 7.6 — praticante + relato, não estudo controlado, mas
   convergente).
4. **Plano SE-ENTÃO específico por sessão, escrito, não "vou estudar
   hoje".** Ex: "SE terminar o jantar, ENTÃO abro o ENEM_APP e faço 1 nó
   de Ecologia antes de qualquer outra coisa no celular." Efeito médio
   d≈0,65 em 94 estudos — uma das maiores evidências isoladas de toda
   esta seção pra uma mudança que custa zero tempo de implementar.
   (Evidência: 7.5, forte.)
5. **Nunca cortar sono pra ganhar hora de estudo.** A hora "ganha" rende
   menos por estar cansado do que a hora que já foi investida durante o
   dia — na prática, é hora perdida, não hora extra. (Evidência: 2.11 +
   7.3, forte.)
6. **Gastar um tempo pequeno, ANTES de mergulhar no conteúdo de um
   assunto novo, mapeando como ele costuma ser cobrado** (metalearning de
   Young, mesma lógica de "padrão de cobrança"/`topico` que o ENEM_APP já
   testa) — evita estudar profundidade que a prova não cobra desse jeito.
   (Evidência: relato de praticante, mais fraca isoladamente, mas
   convergente com TRI/seção 2.8 e past-paper practice/seção 2.9, que são
   fortes.)

---

## 8. Achado ao vivo: um relato real do Gabriel bate direto com §2

Em 2026-09-17, validando o banco de Ecologia no celular, o Gabriel reportou
(via botão "Reportar" do app, tabela `relatos_questao`, id_relato 1):

> "Muito repetitivo, apareceu umas 7 seguidas de destruição da camada de
> ozônio, e não consigo voltar o conteúdo pra fazer retrieval recall, tipo
> se eu tivesse com dúvida agora e precisasse voltar no conteúdo pra
> relembrar, fazer essa força."

Duas coisas reais aqui, confirmadas no banco (`core/db.py`,
`questoes.topico`), não só percepção:

1. **A ordem de fato agrupa por padrão.** Consultando
   `questoes WHERE materia='ecologia' AND origem='banco_pratica'` por
   `numero_questao`, o trecho por volta da 210 tem
   `chuva_acida, chuva_acida, chuva_acida, destruicao_camada_ozonio,
   destruicao_camada_ozonio, chuva_acida, chuva_acida, inversao_termica,
   inversao_termica, inversao_termica, chuva_acida,
   destruicao_camada_ozonio, destruicao_camada_ozonio,
   destruicao_camada_ozonio, chuva_acida, aquecimento_global,
   aquecimento_global, inversao_termica` — blocos de 2-3 do MESMO tópico
   seguidos, repetidas vezes ao longo da sequência (não é um caso
   isolado). Isso é **massed/blocked practice**, o padrão que §2.3
   (interleaving, Rohrer & Taylor) mostra perder pra prática misturada
   especificamente em matemática/ciências. A hipótese registrada em
   `docs/filosofia.md` ("repetição de padrão, 40-60 questões pra fixar")
   não é incompatível com interleaving em si — mas a FORMA como está
   ordenado hoje (várias seguidas do mesmo tópico, sem misturar) é
   literalmente o oposto do que §2.3 recomenda. Repetir um padrão 40-60
   vezes ao longo de uma trilha inteira ≠ repetir 3-7 vezes SEGUIDAS sem
   nada no meio. **Tensão real, não resolvida** — fica registrada aqui, a
   decisão de reordenar (ou não) é do Gabriel, não foi mexida.
2. **"Rever conteúdo base" (recém-implementado) é invisível pra Ecologia.**
   O botão só aparece quando existe um resumo curado em
   `mobile/src/constants/resumos-trilha.ts` (`RESUMOS_TRILHA`) — hoje SÓ
   `optica` tem um escrito. Ecologia (a matéria que o Gabriel está
   validando agora, a primeira/maior da trilha fixa) não tem nenhum, então
   o link nunca aparece nela — exatamente o caso que ele descreveu
   ("não consigo voltar o conteúdo"). Não é bug de código, é conteúdo
   faltando: alguém (o Gabriel, é conteúdo autoral, ver comentário do
   próprio arquivo) precisa escrever um resumo de Ecologia no mesmo
   formato do de Óptica pra a feature aparecer lá.

---

## 9. Espaçamento de longo prazo e worked examples/chunking

### 9.1 O Leitner do app (teto de 90 dias) contra o que a literatura diz sobre intervalo ótimo e retenção de meses

O ENEM_APP usa Leitner simplificado (`core/db.py`, `_calcular_leitner()`):
errou → revisa em 1 dia, streak zera; acertou → intervalo dobra
(2^(streak-1) dias), com teto fixo de 90 dias. Três achados relevantes pra
avaliar esse desenho:

1. **O intervalo ótimo é uma FRAÇÃO do tempo até a prova, não um número
   fixo.** Cepeda, Vul, Rohrer, Wixted & Pashler (2008, *Psychological
   Science*, >1.350 participantes, testados até 1 ano depois) encontraram
   que o gap ideal entre estudo e revisão fica em torno de **10-20% do
   tempo até o teste final** pra atrasos de semanas, caindo pra **5-10%**
   quando o atraso é de 1 ano. Aplicando isso ao Gabriel: se a prova é
   daqui a, digamos, 4 meses (~120 dias), o gap ótimo pra revisão está
   bem mais perto de **6-24 dias** do que de 90 — o teto atual do app não
   está "errado" (o próprio achado diz que o gap ótimo CRESCE com a
   distância até a prova, então limitar em 90 dias é razoável como TETO
   superior), mas ele é um número fixo, e o ideal segundo Cepeda et al.
   seria recalcular esse teto conforme os dias até a prova encolhem — bem
   perto da prova (últimas semanas), o teto de 90 dias vira quase inútil
   na prática (nenhum item vai chegar perto disso), mas MESES antes,
   pode estar deixando o intervalo crescer mais devagar do que o ótimo
   sugerido pela pesquisa.
2. **Expanding interval (o que o Leitner do app faz, dobrando a cada
   streak) não é estritamente superior a intervalo fixo/igual pra retenção
   de LONGO prazo** — achado mais nuançado do que o senso comum sugere.
   Logan & Balota (2008) e Kang, Lindsey, Mozer & Pashler (2014) encontram
   que expanding-interval produz melhor desempenho DURANTE o período de
   treino (mantém a taxa de acerto alta ao longo do caminho), mas em teste
   final de retenção adiada, intervalo IGUAL/equal-interval às vezes supera
   expanding — a diferença entre os dois esquemas é menor do que a
   diferença entre "ter algum espaçamento" e "não ter nenhum" (o mesmo
   padrão já visto na comparação SM-2 vs Leitner abaixo). Não é motivo pra
   trocar o algoritmo, é motivo pra não superestimar o ganho de ajustar
   os multiplicadores do Leitner atual — o retorno marginal disso é menor
   do que parece.
3. **Retenção de meses/anos é real quando passou por espaçamento antes —
   "permastore" (Bahrick).** Harry Bahrick (décadas de estudos, incluindo
   vocabulário de espanhol e reconhecimento de colegas de escola)
   descobriu que memória que passa por exposição espaçada real tende a
   platô-ar numa fase estável ("permastore") depois dos primeiros anos —
   mas o achado central relevante aqui é que ISSO SÓ ACONTECE quando o
   material foi revisado de forma distribuída antes, não com uma única
   exposição. Não é evidência direta sobre o horizonte de meses do ENEM (a
   pesquisa de Bahrick mede anos/décadas), mas reforça o princípio: o
   Leitner do app, mesmo simplificado, está no caminho certo em
   PRINCÍPIO — o ajuste fino que valeria a pena não é trocar de algoritmo,
   é fazer o teto/multiplicador reagir à distância real até a prova.
4. **SM-2/Anki bate Leitner simples pra banco grande e itens de
   dificuldade heterogênea** (mesmo argumento already covered em §4, mas
   com a nuance a mais aqui): a vantagem do SM-2 sobre Leitner cresce
   especificamente quando o banco passa de ~200 itens e a dificuldade
   varia muito entre eles — exatamente o caso do ENEM_APP (140+ questões só
   de Ecologia, dificuldade heterogênea por tópico). FSRS (o sucessor
   mais moderno do SM-2, usado hoje pelo Anki) consegue 20-30% MENOS
   revisões pra atingir a mesma retenção-alvo, ajustando intervalo por
   "facilidade" individual do item em vez de só por streak. **Mas** a
   mesma fonte que documenta isso também deixa claro: a diferença entre
   usar QUALQUER sistema de espaçamento (mesmo o Leitner simples) e não
   usar nenhum é maior que a diferença entre Leitner e SM-2/FSRS — ou
   seja, o ganho de trocar de algoritmo é real mas secundário comparado ao
   ganho de já ter espaçamento nenhum pra ter algum, que o app já tem.

**Força de evidência**: (1) e (3) são estudos controlados fortes e bem
replicados; (2) é achado controlado mas mais nuançado/misto entre fontes;
(4) é consenso de fontes técnicas (não meta-análise formal comparando os
dois algoritmos ponta a ponta), tratado com peso um degrau abaixo.

Fontes: [A Temporal Ridgeline of Optimal Retention (Cepeda et al. 2008)](https://laplab.ucsd.edu/articles/Cepeda%20et%20al%202008_psychsci.pdf), [Expanded vs. Equal Interval Spaced Retrieval Practice (Logan & Balota 2008)](http://psychnet.wustl.edu/coglab/publications/Logan%20&%20Balota,%202008.pdf), [Retrieval practice over the long term: expanding or equal-interval? (Kang et al. 2014)](https://link.springer.com/article/10.3758/s13423-014-0636-z), [Harry Bahrick — permastore (supermemo.guru)](https://supermemo.guru/wiki/Harry_Bahrick), [Very Long Term Retention of Knowledge (Bahrick, ResearchGate)](https://www.researchgate.net/publication/2650892_Very_Long_Term_Retention_Of_Knowledge), [Spaced Repetition From The Ground Up — SM-2 vs Leitner](https://controlaltbackspace.org/spacing-algorithm/), [The optimal retention — FSRS wiki](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention/4d7def68b93f99cc2a8674c0b0fbce83afd315eb).

### 9.2 Worked examples/chunking — matemática (processual) provavelmente precisa de tratamento diferente de ecologia (conceitual)

1. **Worked examples ajudam iniciante, atrapalham quem já tem base — expertise
   reversal effect.** Sweller & Cooper (1985) e a linha de pesquisa
   seguinte: pra quem ainda não tem schema formado, ver o passo a passo
   resolvido ANTES de tentar sozinho reduz carga cognitiva extrínseca e
   libera atenção pra entender o princípio, não só executar. Mas o
   "expertise reversal effect" (Kalyuga e outros) mostra o oposto pra quem
   já tem alguma base: nesse ponto, resolver sozinho (mesmo travando) rende
   mais que ver exemplo pronto — o exemplo vira redundante e até atrapalha.
   **Implicação prática**: não existe um único formato certo pra
   "conteúdo antes do Nó 1" — depende de quão nova a matéria é pro aluno.
   Matemática onde o Gabriel já tem alguma base prévia (ex: função do 1º
   grau) pode já estar no território de "melhor resolver direto", enquanto
   um tópico genuinamente novo se beneficia de ver um exemplo resolvido
   primeiro.
2. **CLT sugere ORDEM DIFERENTE pra conteúdo processual vs conceitual, não
   só formato diferente.** Pra conhecimento PROCEDURAL (matemática: "qual
   fórmula, em qual ordem, pra este tipo de problema"), instrução ANTES de
   tentar resolver reduz exploração desnecessária e carga cognitiva durante
   a prática — o formato clássico de worked example é bem alinhado aqui.
   Pra conhecimento CONCEITUAL (ecologia: relação causa-efeito entre
   conceitos, tipo "por que CFC destrói camada de ozônio especificamente,
   não chuva ácida"), a pesquisa de **productive failure** (Kapur — d entre
   0,6 e 2,3 em vários estudos, efeito médio-grande a grande, consistente)
   mostra o OPOSTO: deixar o aluno tentar resolver/explicar PRIMEIRO, expor
   a lacuna conceitual, e só DEPOIS dar a instrução formal, produz
   compreensão conceitual e transferência maiores do que instrução seguida
   de prática — sem prejudicar fluência procedural.
3. **Isso sugere que o formato de "Apresentação" hoje (resumo de conceitos
   ANTES do Nó 1, igual pra qualquer matéria) pode estar otimizado pra
   matemática e subotimizado pra ecologia.** Não é prescrição de
   implementação (o pedido explícito é só direção), mas o padrão que a
   pesquisa sugere: matérias processuais (matemática) se beneficiam de
   resumo/exemplo resolvido ANTES de praticar; matérias conceituais
   (ecologia, e provavelmente boa parte de ciências humanas) podem se
   beneficiar mais de começar direto pela questão (mesmo errando) e só
   trazer o resumo conceitual DEPOIS — o que é literalmente o formato
   inverso do que o app faz hoje pra qualquer matéria. Vale notar que isso
   não conflita com "rever conteúdo base" (recém-implementado, §8) — esse
   já é sob demanda, no meio da questão, quando o aluno sente falta; o que
   muda aqui é só a ordem da PRIMEIRA exposição ao tópico, antes do Nó 1.

**Força de evidência**: (1) e (2) procedural são clássicos bem replicados
da cognitive load theory; productive failure (2, conceitual) tem efeito
grande e replicado em múltiplos estudos de Kapur e outros, mas é uma linha
de pesquisa mais recente e mais restrita a domínios específicos (matemática
conceitual, ciências) do que CLT clássica — tratado como forte mas não tão
consolidado quanto retrieval practice/spacing (§2.1-2.2).

Fontes: [The Expertise Reversal Effect (ResearchGate)](https://www.researchgate.net/publication/48829036_The_Expertise_Reversal_Effect), [Expertise reversal effect — Wikipedia](https://en.wikipedia.org/wiki/Expertise_reversal_effect), [Knowledge elaboration: A cognitive load perspective (Kalyuga)](https://www.psychology.mcmaster.ca/bennett/psy720/readings/m1/m1r5.pdf), [When Problem Solving Followed by Instruction Works: Evidence for Productive Failure (Sinha & Kapur 2021)](https://journals.sagepub.com/doi/10.3102/00346543211019105), [Productive Failure in Learning Math (Kapur 2014, Cognitive Science)](https://onlinelibrary.wiley.com/doi/10.1111/cogs.12107), [Productive Failure: How to Use Struggle Before Teaching (resumo aplicado)](https://www.structural-learning.com/post/productive-failure-education-teachers-need).

### 9.3 O que isso sugere pro ENEM_APP (direção, não prescrição)

- O teto de 90 dias do Leitner (`core/db.py`) não está errado em
  princípio, mas um teto que reage à distância real até a prova (dado que
  o app já tem — `dias_ate_prova()` já existe) chegaria mais perto do
  ótimo de Cepeda et al. (10-20% do tempo restante) do que um número fixo.
  Isso é um ajuste pequeno em cima de infraestrutura que já existe, não
  uma reescrita do Leitner.
- Trocar Leitner simples por algo tipo SM-2/FSRS é um ganho real mas
  secundário — vale mais a pena só depois de o banco crescer bem além dos
  ~200 itens por matéria (Ecologia já passou disso: 140+), não é urgente.
- A diferença mais acionável de toda esta seção: **o formato de
  "Apresentação" antes do primeiro Nó talvez devesse variar por tipo de
  matéria** — resumo/exemplo resolvido antes pra matemática (processual),
  jogar o aluno na questão primeiro e trazer o conceito depois pra
  ecologia/matérias conceituais (productive failure). Isso é uma decisão
  de arquitetura de conteúdo, não algo pra implementar sem o Gabriel
  decidir primeiro — fica registrado aqui como direção com respaldo.

---

## 10. Redação sob prazo e ansiedade de prova

### 10.1 Redação: prática cronometrada, rubrica e repertório sociocultural

O ENEM_APP já registra tentativas de redação (`core/db.py`, tabela
`redacoes` — tema, data, texto/foto, nota preenchida depois por correção
externa). Três achados relevantes:

1. **Escrever sob prazo real é uma habilidade treinável separada de saber
   escrever bem.** As fontes de orientação de escrita cronometrada
   (universidades, coaching de prova) convergem no mesmo argumento presente
   em §2.1/2.9 deste documento: praticar sob a condição real (tempo
   fechado, sem parar pra revisar infinitamente) treina planejamento rápido
   de argumento, não só "escrever bonito" — é a mesma lógica de retrieval
   practice/past-paper practice aplicada à escrita, não uma técnica nova.
   Não achei meta-análise formal isolando só "escrita cronometrada" (é
   pouco estudada como variável isolada), mas o mecanismo proposto é
   coerente com o resto do documento, não é afirmação solta.
2. **Rubrica explícita + autoavaliação acelera a melhora, mas só combinada
   com feedback externo real.** A linha de pesquisa de Heidi Andrade sobre
   "rubric-referenced self-assessment" (estudos com alunos do ensino
   fundamental/médio) mostra relação entre autoavaliar o próprio texto
   contra os critérios da rubrica ANTES de entregar e nota mais alta depois
   — mas a mesma literatura é clara numa ressalva: só dar a rubrica pro
   aluno, sem ALGUÉM (professor, corretor) dar feedback real sobre a
   autoavaliação dele, não basta sozinho pra melhorar. Isso é direto pro
   ENEM: a rubrica das 5 competências (0-200 cada) já é pública e
   conhecida — o ganho de usá-la pra autoavaliação antes de mandar corrigir
   é real, mas não substitui a correção externa que o app já modela via
   `fonte_correcao` (`propria`/`externa`/`oficial`).
3. **Repertório sociocultural: validação parcial, não causal.** Existe pelo
   menos um estudo acadêmico de verdade (não blog de cursinho) analisando
   44 redações nota 1000 do ENEM de 2019 e catalogando que tipo de
   repertório (filosofia/sociologia, dados, literatura) aparece mais e em
   qual parágrafo — mas é um estudo DESCRITIVO/correlacional (o que
   redações boas TÊM), não um experimento controlado provando que treinar
   repertório CAUSA nota mais alta. É evidência mais fraca que retrieval
   practice, mas ainda é sinal real: alinhado com a técnica de
   metalearning/"mapear como o assunto é cobrado antes de mergulhar"
   (§7.4) e com testwiseness (§6.3) — reconhecer o PADRÃO de argumentação
   que pontua bem, não só decorar dado solto.

Fontes: [How Timed Writing Practice Can Help You Write Better Essays and Ace Your Exams](https://northaveeducation.com/blog/how-timed-writing-practice-can-help-you-write-better-essays-and-ace-your-exams), [Rubric-Referenced Self-Assessment and Self-Efficacy for Writing (Andrade)](https://scholarsarchive.library.albany.edu/cgi/viewcontent.cgi?article=1012&context=etap_fac_scholar), [Putting Rubrics to the Test (Andrade et al.)](https://www.researchgate.net/publication/229518031_Putting_Rubrics_to_the_Test_The_Effect_of_a_Model_Criteria_Generation_and_Rubric-Referenced_Self-Assessment_on_Elementary_School_Students%27_Writing), [Repertório sociocultural em redações nota 1000 do ENEM (UNIR, periódico acadêmico)](https://periodicos.unir.br/index.php/RE-UNIR/article/download/5793/4071).

### 10.2 Ansiedade de prova, autoeficácia e o que a gamificação do app realmente faz (e não faz)

1. **Ansiedade de prova reduz nota de verdade, mas o tamanho do efeito
   depende da dificuldade da questão — achado bem específico pro ENEM.**
   Zeidner (1998) e a literatura seguinte situam a correlação geral entre
   ansiedade e desempenho em torno de r ≈ -0,2 a -0,3, mas o efeito é bem
   mais forte (r ≈ -0,45) em questões de dificuldade média/alta do que em
   questões fáceis (r ≈ -0,07). Isso conecta direto com TRI (§2.8): as
   questões que mais pesam na nota (onde errar fácil é mais grave) não são
   necessariamente as mais afetadas por ansiedade — são as médias/difíceis
   que mais sofrem, o que reforça a importância de chegar a ELAS com
   domínio sólido, não só "tentar ficar calmo" de forma genérica.
2. **Um único experimento real, publicado na revista *Science*, mostrou
   redução de ansiedade virando nota melhor — não é intuição.** Ramirez &
   Beilock (2011): escrever livremente por 10 minutos sobre os próprios
   medos/sentimentos em relação à prova, IMEDIATAMENTE antes dela, melhorou
   o desempenho de estudantes cronicamente ansiosos em provas de verdade
   (2 experimentos de laboratório + 2 de campo em sala de aula real). O
   mecanismo proposto: a preocupação consome memória de trabalho enquanto
   a pessoa tenta suprimi-la; escrever sobre ela libera esse recurso em vez
   de gastá-lo segurando a ansiedade. É uma intervenção de CUSTO ZERO (10
   minutos, sem app nenhum) com evidência experimental forte.
3. **Prática sob condição simulada de prova é o mecanismo central do
   stress inoculation training (Meichenbaum), mas ele é mais amplo que só
   "treinar cronometrado".** O protocolo formal tem 3 fases (educação sobre
   a ansiedade, aprender técnica de enfrentamento tipo relaxamento, e só
   DEPOIS expor a situações progressivamente mais parecidas com a real) —
   simular a prova cronometrada sem passar pelas duas primeiras fases é só
   um pedaço do protocolo original, não o pacote inteiro. Ainda assim, é
   coerente com o que já está em §2.9/§2.12 deste documento: quanto mais a
   prática se parecer com a condição real (tempo, formato, sem consulta),
   menos a prova em si é uma situação nova pro sistema nervoso reagir.
4. **Autoeficácia prediz nota — mas precisa ser calibrada por sucesso REAL,
   não por sensação de progresso.** A meta-análise clássica de Multon,
   Brown & Lent (1991), confirmada por sínteses mais recentes, encontra
   autoeficácia explicando ~14% da variância em desempenho acadêmico — uma
   fração grande pra uma única variável psicológica. O mecanismo de Bandura
   é recíproco: sucesso real gera mais autoeficácia, que gera mais esforço/
   persistência, que gera mais sucesso real — um ciclo que só começa a
   girar em cima de mastery experiences GENUÍNAS (acertar de verdade, não
   ganhar pontos por participar).
5. **Aqui entra uma ressalva crítica que o Gabriel pediu explicitamente
   ("seja crítico, não só favorável") sobre o próprio sistema de
   streak/XP/missões do app**: a pesquisa sobre gamificação é mista, não
   uniformemente favorável. Uma meta-análise recente encontra que
   gamificação aumenta motivação intrínseca e sensação de autonomia, mas
   tem impacto MÍNIMO sobre competência de verdade — e existe um risco
   descrito na literatura como "gamificação rasa" (só pontos/streak/
   leaderboard colados em cima de uma atividade, sem mudar a atividade em
   si): pode gerar uma sensação de progresso desconectada de aprendizado
   real, e o "efeito de supersedimentação" (overjustification) pode até
   corroer motivação intrínseca que já existia. A diferença que decide se
   o streak do ENEM_APP cai nesse risco ou não: ele está OBRIGATORIAMENTE
   amarrado a `registrar_tentativa()` de verdade (acerto/erro real gravado
   em `tentativas_usuario`), não é um contador que sobe por só abrir o
   app ou "participar" — isso é exatamente a diferença entre autoeficácia
   calibrada por mastery real (o que a pesquisa de Bandura valida) e
   gamificação rasa (o que a pesquisa de gamificação critica). O risco real
   a vigiar não é o streak em si, é se algum ponto futuro do app passar a
   dar XP/progresso por AÇÃO (abrir o app, ver um vídeo) em vez de
   RESULTADO (responder certo) — aí sim viraria o tipo de gamificação que
   a literatura mostra não ajudar competência de verdade.

Fontes: [Test Anxiety — an overview (ScienceDirect)](https://www.sciencedirect.com/topics/neuroscience/test-anxiety), [Further evidence for the deficit account of the test anxiety–test performance relationship (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0160289615001075), [Writing About Testing Worries Boosts Exam Performance in the Classroom (Ramirez & Beilock 2011, Science — via PubMed)](https://pubmed.ncbi.nlm.nih.gov/21233387/), [Stress Inoculation Training (Meichenbaum & Deffenbacher 1988)](https://journals.sagepub.com/doi/10.1177/0011000088161005), [I believe, therefore I achieve (and vice versa): meta-analytic cross-lagged panel analysis of self-efficacy and academic performance](https://www.sciencedirect.com/science/article/abs/pii/S104160801730211X), [Gamification enhances student intrinsic motivation... but minimal impact on competency: a meta-analysis (Springer)](https://link.springer.com/article/10.1007/s11423-023-10337-7), [The Dark Side of Gamification (Growth Engineering)](https://www.growthengineering.co.uk/dark-side-of-gamification/).

### 10.3 O que isso sugere pro ENEM_APP (direção, não prescrição)

- **Achado de menor custo/maior retorno desta seção**: um campo opcional de
  "escreva 5-10 min sobre o que te preocupa nessa prova/redação" antes de
  um simulado cronometrado teria respaldo experimental direto (Ramirez &
  Beilock) — custa uma tela, não uma feature complexa.
- A rubrica de 5 competências já é pública; se algum dia o app ganhar
  autoavaliação de redação, a literatura de Andrade sugere que ela só
  funciona bem acoplada a alguém revisando a autoavaliação depois — não
  como substituto de `fonte_correcao='externa'`/`'oficial'`.
- O achado de Zeidner (ansiedade pesa mais em questão média/difícil, quase
  nada em questão fácil) é outro reforço, de ângulo diferente, pro mesmo
  argumento de TRI já registrado em §2.8/§5: dominar sólido o fácil não é
  só sobre nota, é também a parte da prova menos vulnerável a travar de
  ansiedade — dá pra "garantir" um chão antes de chegar no que mais
  desestabiliza.
- Sobre o streak/XP/missões: a pesquisa não pede pra tirar — pede pra
  manter a regra que já existe (XP só sobe com tentativa real registrada)
  como linha vermelha, não decoração que pode ser relaxada depois por
  conveniência de engajamento.

---

## 11. Estudar com apoio de IA

Pedido explícito do Gabriel, com orçamento apertado de propósito (máximo
11 buscas — respeitado à risca, uma por pergunta). Resultado honesto:
a evidência aqui é mais recente, mais mista, e tem pelo menos um achado
que vale como ALERTA direto pra aposta dele, não só reforço.

### 11.1 Relatos de gente estudando com IA pra prova concorrida

Não achei relato individual detalhado e verificável no formato que o
Gabriel descreveu (algo como "cunhar 12 pensões ao mesmo tempo" com
método explicado passo a passo) — o que existe é: (a) pesquisa acadêmica
com estudantes de medicina/saúde usando ChatGPT durante a prep pra prova
de licenciamento (formato survey/pré-pós, não "um caso"), e (b) conteúdo
de blog de cursinho de concurso público brasileiro, mesmo padrão de fonte
fraca já registrado na §3.

O caso mais concreto encontrado: um concurseiro brasileiro aprovado em
cinco concursos de tabelião relata ter alimentado o ChatGPT com os
PRÓPRIOS resumos e pedido pra ele atuar como examinador, gerando questões
em cima só daquele material — é literalmente "IA como banca simulada"
(pergunta 10 abaixo), mas é um relato único, sem verificação externa.

Um estudo controlado real e nomeado, porém: 29 alunos de terapia
ocupacional usando um bot baseado em ChatGPT pra gerar questões de
múltipla escolha (anatomia/cinesiologia/fisiologia) por 1 mês — achado
principal foi que TEMPO TOTAL investido correlacionou mais com ganho de
desempenho do que QUANTIDADE de questão gerada — mesmo padrão de "volume
sozinho não é o fator", já visto em outras seções deste documento (§2.6).

Fontes: [Exploratory Evaluation of Learning Behaviors Using a ChatGPT-Based Question-Generating Bot (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12606513/), [IA para concurso público — Ceisc](https://ceisc.com.br/blog/post/uso-de-inteligencia-artificial-nos-estudos-para-concursos), [Concurseiro Inteligente](https://www.iaparaconcursopublico.com.br/).

### 11.2 O achado que funciona como ALERTA, não só reforço

Este é o resultado mais importante da rodada, e vai na direção OPOSTA do
que seria confortável ouvir: um estudo pré-registrado (PNAS, alta escala,
ensino médio na Turquia) deu acesso a GPT-4 pra alunos resolvendo questão
de matemática em prática. Resultado: os alunos com acesso à IA resolveram
**48% a mais** de questões de prática corretamente — E foram **PIORES**
na prova de verdade depois, sem o acesso à IA, comparado a quem praticou
sem IA nenhuma. É o mesmo mecanismo da ilusão de fluência já documentado
na §2.5 (reler cria familiaridade, não retenção) — só que turbinado: a IA
resolve/explica rápido demais, o aluno confunde "consegui acompanhar a
explicação" com "eu sei fazer isso sozinho", e só descobre que não sabia
na hora que mais custa (a prova real, sem ajuda).

Achado complementar, mais geral (não específico de estudo, mas do mesmo
mecanismo): pesquisa de UX/decisão mostra que explicações de IA nem
sempre reduzem dependência excessiva — em alguns casos AUMENTAM, porque
uma explicação bem escrita parece mais autoritativa, não porque o usuário
de fato verificou o raciocínio. Isso é uma extensão direta da "illusory
explanatory depth" (as pessoas superestimam o quanto entendem um
mecanismo até serem obrigadas a explicá-lo do zero) aplicada a explicação
GERADA por IA, especificamente.

**Implicação prática, direta pro método do Gabriel**: usar IA pra GERAR
questão/explicação é diferente de usar IA como SUBSTITUTO de responder
sozinho e depois conferir — a primeira forma tem risco documentado real
de inflar confiança sem inflar competência; a segunda (que é como o
ENEM_APP já funciona: responde, DEPOIS vê explicação) está alinhada com o
lado certo desse achado.

Fontes: [Generative AI without guardrails can harm learning: Evidence from high school mathematics (PNAS)](https://www.pnas.org/doi/10.1073/pnas.2422633122), [versão PMC completa](https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/), [Explanations Can Reduce Overreliance on AI Systems During Decision-Making (arXiv)](https://arxiv.org/pdf/2212.06823), [Don't Be Fooled: The Misinformation Effect of Explanations in Human–AI Collaboration](https://www.tandfonline.com/doi/full/10.1080/10447318.2025.2574511).

### 11.3 IA como tutor — RCTs recentes, e por que são mais fortes do que pareciam

Ao contrário da maior parte deste documento, aqui existe evidência
EXPERIMENTAL de verdade, recente (2025-2026), não só relato:

- **Kestin et al. 2025 (Harvard, *Scientific Reports*, RCT em sala de aula
  real)**: alunos aprenderam significativamente mais, em MENOS tempo, com
  tutoria de IA bem desenhada comparado a aula ativa presencial — e
  relataram mais engajamento/motivação. É citado como "mais que o dobro"
  de ganho de aprendizagem em algumas coberturas da imprensa
  especializada — vale ler a ressalva: o desenho do prompt/tutor importa
  tanto quanto a ferramenta em si (mesmo recado da §11.2).
- **Meta-análise de 34 estudos experimentais**: efeito positivo
  estatisticamente significativo de IA generativa em aprendizagem,
  g ≈ 0,795 (dimensão cognitiva) e 0,711 (competência) — tamanho de
  efeito GRANDE pelos padrões usuais da área. Uma revisão sistemática
  separada, com 68 estudos e 337 tamanhos de efeito, achou um resultado
  mais conservador (SMD ≈ 0,45, efeito moderado) — a diferença entre os
  dois números é o tipo de coisa que costuma acontecer quando o critério
  de inclusão de estudo varia; tratar 0,45-0,80 como a faixa real, não um
  número único.
- **Khanmigo (Khan Academy)**: piloto de 1 ano com 2 milhões de alunos
  reportou 32% de aumento na velocidade de domínio de conceito, 24% de
  redução de tempo gasto em conceito já dominado, 45% de melhora em
  métrica de desempenho de longo prazo — mas um estudo acadêmico
  independente sobre o mesmo produto achou GANHO SIGNIFICATIVO em todas
  as condições testadas, PORÉM SEM diferença estatística ENTRE grupos
  (ou seja: melhorou, mas não ficou claro que foi o Khanmigo
  especificamente causando a diferença) — mesmo padrão de "dado de
  empresa é mais otimista que estudo independente" que já apareceu antes
  neste documento (comparar com a ressalva sobre gamificação na §10.2).

Fontes: [AI tutoring outperforms in-class active learning (Nature Scientific Reports)](https://www.nature.com/articles/s41598-025-97652-6), [A Harvard RCT Found AI Tutors Produced More Than Double the Learning Gains — o que o estudo realmente mostra](https://impactaieducation.substack.com/p/a-harvard-randomized-controlled-trial), [What the research shows about generative AI in tutoring (Brookings)](https://www.brookings.edu/articles/what-the-research-shows-about-generative-ai-in-tutoring/), [Estudia Khanmigo — piloto com foco em equidade (Digital Promise/PDF)](https://digitalpromise.org/wp-content/uploads/2024/09/SRM-Gates-Khanmigo-Report-Final.pdf), [Leveraging "Khanmigo" — estudo acadêmico independente](https://jtl.uwindsor.ca/index.php/jtl/article/view/10052).

### 11.4 Geração de questão/flashcard por IA — qualidade é o ponto fraco real

- **Questão de múltipla escolha gerada por IA vs. humano** (educação
  médica, vários estudos): sem diferença significativa no "efeito de
  pré-questionamento" em pelo menos um estudo — mas revisão de
  especialista encontrou MAIS erro factual (6% vs 4%), MAIS
  irrelevância (6% vs 0%) e MAIS dificuldade mal calibrada (14% vs 1%) em
  questões geradas por IA; além disso, questão de IA tende a testar
  habilidade cognitiva de ordem MAIS BAIXA (lembrar/reconhecer) que
  questão feita por humano especialista (aplicar/analisar). O ganho real
  e mensurado é em EFICIÊNCIA de produção (24,5 contra 96 pessoas-hora
  pra montar um banco), não em qualidade pedagógica superior.
- **Flashcard gerado por IA (Anki-style)**: evidência ainda incompleta —
  keyword mnemônico gerado por IA melhorou retenção de vocabulário em
  pelo menos um estudo, mas comparação sistemática de GPT-4 vs GPT-3.5 vs
  LLM local pra gerar flashcard achou muito cartão irrelevante/ambíguo
  sem edição humana depois. Não existe ainda comparação de longo prazo
  entre cartão feito à mão e cartão gerado por IA e editado por humano.

Isso reforça, com dado específico de IA generativa, o mesmo ponto que a
§4 já tinha feito sobre o banco de questões do próprio ENEM_APP: gerar
com IA e VALIDAR manualmente antes de entrar na trilha (exatamente o que
o Gabriel está fazendo agora, questão por questão, com o botão de
reportar) é a combinação que a literatura sustenta — gerar e confiar sem
revisão humana é onde a qualidade cai.

Fontes: [Quality assurance and validity of AI-generated single best answer questions (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11854382/), [AI versus human-generated multiple-choice questions for medical education (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11806894/), [When AI Asks the Questions, Human Beings Can Benefit (Psychology Today)](https://www.psychologytoday.com/us/blog/the-future-of-learning/202511/when-ai-asks-the-questions-human-beings-can-benefit), [Comparing GPT-4, 3.5 and local LLMs at generating Anki flashcards (R-bloggers)](https://www.r-bloggers.com/2024/01/comparing-gpt-4-3-5-and-some-offline-local-llms-at-the-task-of-generating-flashcards-for-spaced-repetition-e-g-anki/).

### 11.5 Interleaving turbinado por tecnologia, e IA como "banca simulada"

- **Sequenciamento adaptativo de interleaving NÃO bateu interleaving
  aleatório simples**, num estudo controlado específico sobre isso — a
  tecnologia ajuda a ENTREGAR entrelaçamento (misturar tópico
  automaticamente), mas ajustar a ordem "de forma inteligente" por
  padrão de confusão do aluno não mostrou ganho extra sobre só misturar
  aleatoriamente. Achado direto pro ENEM_APP: a trilha fixa entrelaçada
  já existente (§2.3/§5) não precisa de um algoritmo sofisticado de
  ordenação pra capturar o efeito — misturar já basta, o ganho marginal
  de "misturar de forma mais esperta" parece pequeno.
- **IA como "banca simulada"** (gerar questão no estilo/dificuldade de
  uma prova específica): existe em produção pra prova médica padronizada
  (USMLE-style, QUEST-AI: gera, verifica com outro modelo, refina) e pra
  bancos alinhados a blueprint de prova — mas a validação encontrada é de
  QUALIDADE da questão gerada (por especialista humano revisando), não de
  GANHO DE NOTA de quem estudou com essas questões geradas — ou seja,
  "IA consegue imitar o estilo de uma banca" tem alguma validação;
  "estudar com questão de IA no estilo de uma banca melhora nota tanto
  quanto estudar com questão REAL da banca" não achei nenhum estudo
  medindo isso diretamente. É diferença relevante pro ENEM_APP, que hoje
  usa só questão REAL de prova (`origem='enem_oficial'`) como base — a
  pesquisa não dá motivo pra trocar isso por questão gerada.
- Aprender "em paralelo" várias matérias com apoio de IA gerando prática
  sob demanda: não achei estudo controlado testando isso como bloco único
  — o que existe é (a) a literatura de interleaving já citada (§2.3),
  que dá suporte a ALTERNAR rápido entre matérias, e (b) uma reflexão de
  praticante (Scott Young, não peer-reviewed) argumentando que aprender
  múltiplas coisas ao mesmo tempo tende a funcionar melhor quando você já
  tem alguma base em pelo menos uma delas — mesma ressalva de Bjork sobre
  "desirable difficulty" precisar de base mínima (§2.4). Tratar como
  extrapolação lógica em cima de evidência real de tema adjacente, não
  como achado direto.

Fontes: [Tailoring interleaved practice: Does adaptive sequencing boost the interleaving effect? (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S1041608025001803), [QUEST-AI: Question Generation for USMLE-Style Exams (medRxiv)](https://www.medrxiv.org/content/10.1101/2023.04.25.23288588.full.pdf), [Should You Try Learning More Than One Thing at a Time? (Scott Young)](https://www.scotthyoung.com/blog/2016/10/14/focus-or-parallel/).

### 11.6 O que isso sugere pro ENEM_APP (direção, não prescrição)

O ENEM_APP já usa IA/scripts em pontos específicos (extração automática
de questão de PDF em `core/extrair_enunciados_pdf.py`/`importar_enem_dev.py`,
e o próprio Gabriel usando IA — inclusive esta conversa — pra gerar
conteúdo de banco de prática que depois valida um por um). A seção 11
inteira sustenta a forma como isso já é feito, mais do que sugere algo
novo:

- **O alerta da §11.2 (PNAS) é o achado que mais importa desta rodada**:
  o risco real de estudar com IA não é "IA erra o conteúdo" — é confiar
  na velocidade de acompanhar uma explicação como se fosse a mesma coisa
  que saber resolver sozinho. O ENEM_APP já estrutura isso do jeito
  certo por acidente de arquitetura, não por design deliberado contra
  esse risco específico: responde PRIMEIRO, sem ajuda, só DEPOIS vê
  explicação (quando existe) — o próprio botão implementado nesta
  conversa. Vale manter essa ordem como regra dura, não flexibilizar
  "pra ajudar" no futuro.
- **§11.4 valida o fluxo atual de criação de conteúdo**: gerar questão
  com IA e validar manualmente uma por uma (o que o Gabriel está fazendo
  agora, com o botão de reportar) é exatamente a combinação que a
  literatura sustenta — a IA sozinha, sem revisão humana, tem taxa de
  erro/dificuldade mal calibrada real e mensurada.
- **§11.5 sugere que a trilha fixa entrelaçada não precisa ficar mais
  sofisticada** — o ganho de misturar matéria já está capturado por
  misturar simples, sequenciamento "inteligente" adicional não mostrou
  ganho extra no único estudo controlado que testou isso.
- **O que a pesquisa NÃO sustenta**: usar IA pra gerar questão no estilo
  de uma banca como substituto de questão real da banca — não há dado de
  que isso funcione tão bem quanto questão de prova real pra ganho de
  nota, só validação de qualidade da questão em si. Reforça manter
  `origem='enem_oficial'` como base principal, banco de prática
  (`banco_pratica`) como complemento, não substituto.

---

## 12. Geração de questão por padrão (a ideia do Gabriel) — o que a pesquisa diz

A ideia do Gabriel, nas palavras dele: pegar as provas que o banco já tem,
identificar o padrão que mais se repete (ex: "4 teorias que caem de novo em
questão parecida, X vezes em todas as provas que a gente tem") e treinar o
aluno especificamente nesse padrão, trocando o "enfeite" da questão (contexto,
números, redação) mas mantendo o que realmente é cobrado. E perguntou se
existe "um sistema por trás disso" — alguém que já faz isso de forma
estruturada, pegando várias provas de anos anteriores pra achar padrão.

**Resposta direta: sim, existe um campo de pesquisa inteiro pra exatamente
isso, com décadas de trabalho por trás — não é uma ideia improvisada, é uma
técnica com nome, teoria e validação.**

### 12.1 O nome do campo: Automatic Item Generation (AIG)

Chama-se *Automatic Item Generation* (Gierl & Haladyna, com Mark Gierl na
University of Alberta como um dos nomes centrais do campo há mais de 20
anos, usado em exames de larga escala incluindo certificação médica). O
processo formal tem dois passos, e bate quase palavra por palavra com o que
o Gabriel descreveu:

1. Um especialista extrai um **"item model"** (modelo/template) de itens já
   existentes — as características estruturais que TÊM que ser mantidas pra
   a questão continuar cobrando a mesma coisa.
2. Um algoritmo manipula os elementos variáveis desse modelo pra gerar
   dezenas/centenas de itens novos — mesma lógica cobrada, contexto/números/
   redação diferentes.

Isso é literalmente "trocar o padrão pro aluno pegar", só que com nome
técnico (item model) e uma tradição de pesquisa validando quando funciona e
quando não funciona.

Fontes: [Automatic item generation — Wikipedia](https://en.wikipedia.org/wiki/Automatic_Item_Generation), [The Role of Item Models in Automatic Item Generation (Gierl, International Journal of Testing, 2012)](https://www.researchgate.net/publication/239794821_The_Role_of_Item_Models_in_Automatic_Item_Generation), [Instructional Topics Module: Using Automated Processes to Generate Test Items (Gierl & Lai, NCME)](https://ncme.org/wp-content/uploads/2025/10/Module-34-Automated-Item-Generation-Gierl-Lai.pdf).

### 12.2 O cuidado real pra fazer isso funcionar: "radical" vs "incidental"

Aqui está o ponto técnico mais importante pra ideia do Gabriel dar certo de
verdade, não só na intenção: a literatura (terminologia de Irvine, usada por
Gierl) separa dois tipos de elemento dentro de um item:

- **Radicais (radicals)**: os elementos ESTRUTURAIS — a lógica/conceito que
  o item testa. Mexer neles muda a dificuldade e o que está sendo cobrado de
  verdade.
- **Incidentais (incidentals)**: os elementos de SUPERFÍCIE — contexto,
  números, nomes, redação. Mexer neles NÃO deveria mudar a dificuldade, se
  os radicais ficaram intactos.

Ou seja: "trocar o padrão" só funciona se quem monta a questão nova souber
identificar CORRETAMENTE o que é radical (não pode mudar) e o que é
incidental (pode variar à vontade). Trocar só o número sem entender qual
parte é a estrutura lógica de fato (ex: no exemplo de Ecologia que o Gabriel
reportou — chuva ácida × destruição da camada de ozônio × efeito estufa —
o radical é "qual poluente causa qual mecanismo", não o cenário da fábrica
específica da questão) é o jeito de fazer isso ERRADO. Pesquisa recente
confirma que itens isomórficos bem construídos (radical mantido, incidental
variado) preservam dificuldade comparável entre si — mas a MESMA fonte
alerta que isomorfismo estrutural sozinho não garante que o processo
COGNITIVO do aluno pra resolver seja de fato equivalente; ainda depende de
validação.

Fontes: [Computational Blueprints: Generating Isomorphic Mathematics Problems with LLMs](https://arxiv.org/html/2511.07932v1), [Scalable Generation and Validation of Isomorphic Physics Problems with GenAI](https://arxiv.org/pdf/2602.05114), [Introducing a Computerized Figural Memory Test Based on AIG (radicals/incidentals, Rasch model)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7298330/).

### 12.3 Validação real de que IA consegue gerar item com qualidade psicométrica equivalente — MAS só com revisão humana no meio

Este é o achado mais forte e mais diretamente aplicável desta rodada: um
estudo pré-registrado, cego, comparando 24 questões geradas por GPT-4o
contra 24 questões feitas por humano (mesmo tópico), aplicado a 82
estudantes de medicina + 46 médicos, achou que **dificuldade** (humano:
0,65 vs IA: 0,67) e **discriminação** (0,27 vs 0,29) — os dois parâmetros
centrais de TRI — **não tiveram diferença estatisticamente significativa**.
Os alunos também não conseguiram identificar de forma confiável qual
questão era gerada por IA.

O detalhe que mais importa pro Gabriel: esse resultado bom só apareceu num
fluxo **"expert-reviewed, human-in-the-loop"** — ou seja, IA gera, humano
com conhecimento de conteúdo revisa e ajusta ANTES de usar. É exatamente o
processo que ele já está seguindo agora (gerar com IA, validar uma por uma
com o botão de reportar) — a pesquisa valida especificamente esse fluxo, não
"IA gera e usa direto".

Uma ressalva séria na mesma linha de pesquisa: distratores (alternativas
erradas) gerados por IA tendem a ser matematicamente/logicamente válidos,
mas **não necessariamente capturam os erros/concepções erradas que alunos
de verdade cometem** — ou seja, a "pegadinha" pode não ser a pegadinha real
que a banca usa, mesmo parecendo plausível. Isso é outro motivo concreto
pra revisão humana continuar sendo necessária, não só formalidade.

Fontes: [Psychometric properties and detectability of GPT-4o–generated MCQs (npj Digital Medicine)](https://www.nature.com/articles/s41746-025-02313-7), [Generating Plausible Distractors for MCQs via Student Choice Prediction (ACL 2025)](https://aclanthology.org/2025.acl-long.1154/), [Exploring Automated Distractor Generation for Math MCQs via LLMs](https://arxiv.org/html/2404.02124v1).

### 12.4 "Existe um sistema por trás disso" — sim, e tem gente fazendo em escala

Respondendo direto à pergunta do Gabriel: sim, existem sistemas reais que
pegam várias provas de anos anteriores e minam padrão de forma sistemática,
não manual:

- **Projeto público de mineração de padrão em prova real**: um repositório
  analisou estruturalmente **1.955 provas do CBSE (equivalente indiano ao
  ensino médio)** ao longo de 2022-2026, minerando tópicos recorrentes como
  n-gramas de 2-4 palavras que se repetem em 3+ anos — exatamente a pergunta
  "o que se repete, de forma automática, não por lista feita à mão" que o
  Gabriel fez.
- **Duolingo já roda esse pipeline em produção, em escala, HOJE**: eles
  definem um "prompt template" por tipo de exercício (30+ templates), o LLM
  gera várias opções a partir do template, e um "Learning Designer" humano
  ESCOLHE e edita antes de publicar — mesmo fluxo gera-e-valida do Gabriel,
  só que rodando pra 40+ cursos e mais de 50 milhões de usuários. Resultado
  reportado: produção de conteúdo 40% mais rápida.
- **Caso específico do ENEM, academicamente**: existem estudos brasileiros
  publicados (não TCC informal, peer-review de verdade) cruzando a matriz de
  referência oficial do ENEM com os itens reais aplicados — um no SciELO
  sobre Química (2009-2013), outro sobre Ciências da Natureza (2009-2020) —
  mostrando que esse tipo de análise sistemática de recorrência já é uma
  linha de pesquisa ativa especificamente pro ENEM, não só uma intuição do
  Gabriel.

Fontes: [CBSE_paper_patterns — análise estrutural de 1.955 provas (GitHub)](https://github.com/herrrickshaw/CBSE_paper_patterns), [Case Study: How Duolingo Scaled Content 10x Using LLMs](https://architecturallyspeaking.substack.com/p/case-study-how-duolingo-scaled-content), [Correlação entre a matriz de referência e os itens de Química no ENEM 2009-2013 (SciELO)](https://www.scielo.br/j/ciedu/a/CVC5n3z8gMxBTZ9GjcRSh5F/), [Explorando a Matriz de Referência do ENEM em Ciências da Natureza 2009-2020](https://revistarede.ifce.edu.br/ojs/index.php/rede/article/view/111).

### 12.5 Conexão com o que o ENEM_APP já tem — a ideia já tem embrião no código

O mais direto de tudo: o Gabriel já construiu, sem saber o nome acadêmico, a
peça de dado que esse campo de pesquisa chama de base pra um "item model":
`questoes.topico` (ver ADR 0005, `core/db.py`). Hoje `topico` já registra o
"padrão de cobrança" de cada questão (ex: `destruicao_camada_ozonio`,
`chuva_acida`) e já alimenta `fase_de_topico()`/`desempenho_por_topico()` —
ou seja, contar QUANTAS VEZES um padrão se repete ao longo dos anos/provas
já carregadas no banco é uma consulta possível HOJE com o dado que já
existe (`SELECT topico, COUNT(*) FROM questoes WHERE origem='enem_oficial'
GROUP BY topico ORDER BY COUNT(*) DESC`), sem precisar de nenhuma feature
nova — só ninguém rodou essa pergunta ainda.

Isso é literalmente o primeiro passo de um pipeline AIG: identificar quais
`topico` são mais recorrentes nas provas REAIS (`origem='enem_oficial'`) —
aí sim, gerar questão nova de banco_pratica NAQUELE `topico` específico
(trocando o incidental, mantendo o radical) deixa de ser "gerar questão
genérica de Ecologia" e vira "gerar mais questão especificamente do padrão
que mais cai", com prioridade guiada por dado real, não por achismo de qual
tópico "parece" importante. A seção 12.3 é o que diz COMO fazer essa geração
com qualidade (radical certo + revisão humana, que já é o processo atual) e
a seção 12.2 é o alerta técnico de que confundir radical com incidental é o
jeito de fazer isso errado. Não é prescrição de implementação — é confirmar
que a ideia do Gabriel tem, ao mesmo tempo, respaldo acadêmico sério E um
caminho técnico concreto usando dado que o app já grava.

---

### Aprofundamento (pedido explícito do Gabriel: "aprofunde então")

Esta parte usou 8 buscas adicionais focadas nos pontos que a §12 original
deixou resumidos demais pra virar decisão de verdade: como identificar
radical/incidental NA PRÁTICA (não só na teoria), como gerar distrator
bom, se existe número de saturação de repetição, como calibrar dificuldade
sem esperar dado real de aluno, se existe pipeline de ponta a ponta já
documentado, e — bônus que valeu a busca — se a literatura já documenta
exatamente a confusão ozônio×efeito-estufa×chuva-ácida que o próprio banco
de Ecologia usa como distrator.

### 12.6 Radical vs. incidental NA PRÁTICA: existe método formal, não é só "olho clínico"

A pergunta era: um especialista decide o que é radical/incidental por
julgamento (subjetivo, sem método) ou existe processo formal? Resposta:
existe processo formal, com estágios definidos e tempo médio conhecido —
não é uma arte solta.

O processo tem **3 estágios sequenciais**:

1. **Desenvolver o "cognitive model"** — um especialista de conteúdo parte
   de um item real (o "parent item") e explicita, passo a passo, o
   raciocínio COMPLETO que alguém precisa seguir pra resolvê-lo: que
   informação é usada, em que ordem, que decisão cada etapa exige. É
   nesse mapeamento que fica claro o que É a lógica (radical) e o que é
   só pano de fundo (incidental) — não é intuição, é o produto de
   escrever o raciocínio inteiro no papel.
2. **Desenvolver o "item model" (template)** — a partir do cognitive
   model, definir explicitamente QUAIS elementos do item podem variar
   (os incidentais) e quais ficam fixos (os radicais).
3. **Geração em software** — um algoritmo (ou, hoje, um LLM guiado pelo
   item model) produz dezenas/centenas de itens variando só os
   incidentais.

Um método híbrido mais recente (IA + template) formaliza isso em **7
passos**, os 5 primeiros feitos por um especialista: (1) fornecer o item
"pai", (2) identificar os elementos manipuláveis, (3) escolher as opções
possíveis pra cada elemento, (4) atribuir valores, (5) gerar o cognitive
model — com revisão final de especialista antes da geração em massa.
Custo medido: **~3 horas por cognitive model + ~2 horas por item model**,
pra um especialista já experiente no método — depois disso, a geração em
si é rápida/barata.

Aplicado ao exemplo de Ecologia que o Gabriel reportou: o cognitive model
de uma questão de "poluição atmosférica" seria algo como "identificar o
poluente citado → associar ao mecanismo correto (SOx/NOx→chuva ácida;
CFC→ozônio; CO2/CH4→efeito estufa; inversão térmica→fenômeno físico sem
poluente novo) → eliminar os outros três mecanismos como distrator". O
RADICAL é essa cadeia de associação poluente→mecanismo; o INCIDENTAL é o
cenário (fábrica, cidade, ano, redação da alternativa).

Fontes: [Establishing Cognitive Item Models for Fair and Theory-Grounded AIG (Taylor & Francis, 2025)](https://doi.org/10.1080/08957347.2025.2563889), [Using a hybrid of AI and template-based method in AIG for medical MCQs (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11990652/), [The Role of Item Models in Automatic Item Generation (Gierl, ResearchGate)](https://www.researchgate.net/publication/239794821_The_Role_of_Item_Models_in_Automatic_Item_Generation).

### 12.7 Geração de distrator: confirmação de que "baseado em erro comum" é o método certo, não um atalho

A pesquisa confirma diretamente a intuição do Gabriel: distratores de
qualidade são formulados pra bater com o erro/concepção errada que o
aluno TERIA — não são opções aleatoriamente erradas. Uma revisão
sistemática recente catalogou **60 estudos (2009–2024)** especificamente
sobre geração automática de distrator, migrando de métodos simples
(busca/recuperação de termo parecido) pra redes neurais e LLM, todos
com o mesmo objetivo: prever qual erro específico um aluno real cometeria
e transformar ISSO na alternativa errada — exatamente o padrão que já
está na fase 4 de Ecologia (cada distrator é literalmente "o mecanismo
de um OUTRO fenômeno real", não um erro aleatório).

Fontes: [Distractor Generation in Multiple-Choice Tasks: A Survey of Methods, Datasets, and Evaluation (arXiv)](https://arxiv.org/abs/2402.01512), [Automatic distractor generation in MCQs: a systematic literature review (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11623049/).

### 12.8 Quantos itens do mesmo padrão antes de virar redundante — não achei "40-60", mas achei o conceito formal equivalente

Não existe pesquisa medindo especificamente "quantas questões do mesmo
`topico`" (não é assim que a literatura de AIG fatia o problema) — mas
existe o conceito formal adjacente, **overlearning ratio**: se levou N
repetições pra atingir domínio de um item/padrão, a pesquisa aponta
**50% de repetição extra (1,5×N) como o mínimo que ainda rende algum
ganho**, e **100% extra (2×N) rende mais que 150-200% extra** — ou seja,
depois de dobrar a prática em cima do que já foi dominado, o ganho
marginal cai forte. Cada repetição a mais no MESMO padrão, além desse
ponto, é tempo tirado de um padrão diferente que ainda precisa de
prática — o mesmo argumento de ROI já registrado na §7.

Isso não confirma nem derruba o número "40-60" que está em
`docs/filosofia.md`/memória do projeto — não achei fonte que valide esse
número específico. O que dá pra dizer com alguma base: se 40-60 é o
total até "fixar" o padrão pela primeira vez, bloco adicional de prática
no MESMO padrão depois disso deveria ser bem menor (na faixa de 50-100%
daquilo, não outro bloco do mesmo tamanho) — e o tempo economizado vai
melhor pra outro `topico` ainda fraco, não pra mais repetição do que já
está sólido.

Fontes: [Adequate Learning vs. Overlearning: How Many Repetitions Is Enough? (Bulletproof Musician)](https://bulletproofmusician.com/adequate-learning-vs-overlearning-how-many-repetitions-is-enough/), [How Overlearning Works](https://edukatesg.com/2026/09/11/how-overlearning-works-when-more-practice-after-mastery-helps-and-when-spacing-beats-it/).

### 12.9 Calibrar dificuldade de item novo SEM esperar dado real de aluno — existe, e tem número

Sim, existe um caminho formal: prever os parâmetros de TRI (dificuldade/
discriminação) diretamente das CARACTERÍSTICAS do item — vocabulário,
sintaxe, complexidade conceitual, comprimento — via regressão, sem
precisar aplicar a questão pra uma turma inteira primeiro
("field testing"). A tradição remonta ao **Linear Logistic Test Model**
(LLTM), de décadas atrás; a versão moderna troca a codificação manual de
características por embeddings de texto. Um resultado concreto, em item
de raciocínio numérico gerado automaticamente: as características do
próprio item explicaram **77% da variância na dificuldade real
observada** — ou seja, dá pra prever com bastante precisão se um item
gerado vai sair fácil/médio/difícil ANTES de qualquer aluno responder,
desde que o gerador (humano ou IA) já saiba quais características do
item pesam em qual direção.

Isso é relevante pro ENEM_APP num ponto concreto: um item novo de
banco_pratica, gerado seguindo o item model de um padrão recorrente,
pode nascer com uma dificuldade ESTIMADA (fácil/médio/difícil) antes de
qualquer `tentativas_usuario` real acumular — útil especificamente pra
alimentar a lógica de TRI/coerência já discutida na §2.8/§5, sem precisar
esperar dado.

Fontes: [Automated Item Difficulty Prediction (EmergentMind)](https://www.emergentmind.com/topics/automated-item-difficulty-prediction), [Evaluating an Automated Number Series Item Generator Using Linear Logistic Test Models (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6480725/), [From Text to Parameters: Predicting Item Parameters from Embedding Regularization (arXiv)](https://arxiv.org/html/2607.07141).

### 12.10 Pipeline de ponta a ponta — existe, e tem projeto open source fazendo quase literalmente o que o Gabriel descreveu

Achei dois projetos abertos que fazem o fluxo completo "prova antiga →
padrão → questão nova no mesmo padrão":

- **Book-RAG**: aprende com provas de anos anteriores pra extrair a
  estrutura do examinador (layout de seção, distribuição de peso,
  padrão de linguagem, tópicos recorrentes) e ESCREVE questões novas
  nesse mesmo padrão — roda localmente, sem mandar dado pra fora.
- **ExamRAG**: ingere provas antigas + material de conteúdo, monta uma
  base pesquisável, e oferece previsão de questão/geração de simulado
  guiada por padrão detectado nas provas.

Nenhum dos dois é polido o suficiente pra "copiar e rodar" sem trabalho
(são projetos pequenos/recentes, não produto maduro), mas confirmam que
o desenho de pipeline que o Gabriel imaginou já foi construído por
outras pessoas, de forma similar, e serve de mapa das etapas que um
pipeline de verdade precisa ter: extrair estrutura → identificar
recorrência → gerar no padrão → (falta nos dois: validação humana
formal antes de publicar, que é exatamente o passo que o ENEM_APP já
tem via botão de reportar).

Bônus fora do escopo direto mas relevante por ser especificamente
brasileiro: existe **BLUEX**, um benchmark acadêmico público (arXiv)
com mais de 1.000 questões de vestibular de USP/Unicamp anotadas por
área/habilidade cognitiva, usado pra medir o quanto LLMs acertam questão
de vestibular real — não é ferramenta de geração, mas mostra que
"estruturar prova de vestibular brasileira como dataset anotado" (o que
`questoes`+`topico` já faz, em miniatura) é uma prática acadêmica
reconhecida, não um formato inventado pro ENEM_APP.

Fontes: [Book-RAG (GitHub)](https://github.com/darklegend91/book-rag), [ExamRAG (GitHub)](https://github.com/Ayushhgit/ExamRAG), [BLUEX: A benchmark based on Brazilian Leading Universities Entrance eXams (arXiv)](https://arxiv.org/pdf/2307.05410), [BLUEX v2 (arXiv)](https://arxiv.org/abs/2606.22723).

### 12.11 Bônus direto: a literatura JÁ documenta a confusão exata que a fase 4 de Ecologia usa como distrator

Achado que vale destacar sozinho: existe uma linha de pesquisa em
educação ambiental, com múltiplos estudos (incluindo um **teste
diagnóstico de três níveis**, instrumento formal, validado, pra medir
exatamente isso) mostrando que a confusão entre **efeito estufa ×
destruição da camada de ozônio × chuva ácida** é uma das concepções
erradas MAIS documentadas do mundo em ciências ambientais — presente
igual em aluno de ensino médio E universitário, e mesmo entre
professores em formação. Os padrões de erro documentados incluem
literalmente: achar que o efeito estufa É CAUSADO pela destruição da
camada de ozônio, achar que a camada de ozônio protege contra chuva
ácida, e tratar os três fenômenos como "a mesma coisa: poluição
esquenta o planeta".

Isso confirma, com literatura pedagógica formal (não só a intuição de
quem escreveu a questão), que o padrão de distrator já usado na fase 4
do banco (misturar exatamente esses três mecanismos) está em cima do
erro REAL mais comum do mundo nesse tópico — não é um distrator
arbitrário, é o distrator com mais respaldo possível.

Fontes: [A Three-Tier Diagnostic Test to Assess Misconceptions about Global Warming, Greenhouse Effect, Ozone Layer Depletion, and Acid Rain (Taylor & Francis)](https://www.tandfonline.com/doi/full/10.1080/09500693.2012.680618), [Students' Misconceptions about the Ozone Layer (ERIC)](https://files.eric.ed.gov/fulltext/EJ1130607.pdf), [Prospective Primary Teachers' Understanding of Climate Change, Greenhouse Effect, and Ozone Layer Depletion (Springer)](https://link.springer.com/article/10.1023/B:JOST.0000031268.72848.6d).

### 12.12 Desenho concreto do pipeline em cima do que o ENEM_APP JÁ TEM (direção, não prescrição de código)

Juntando §12.6-12.11 com o que já existe hoje no repositório:

1. **Extrair padrão recorrente** — `SELECT topico, COUNT(*) FROM questoes
   WHERE origem='enem_oficial' GROUP BY topico ORDER BY COUNT(*) DESC`
   (já rodável hoje, dado já existe, ver §12.5).
2. **Cognitive model do padrão** — pra cada `topico` de alta recorrência,
   Gabriel (especialista de conteúdo, papel que a literatura exige um
   humano preencher, §12.6) escreve o raciocínio completo de resolução —
   é basicamente o que ele já fez ao me colar o resumo da fase 4 nesta
   conversa, só formalizado como "isso é radical, isso é incidental".
3. **Item model / geração** — IA gera N variações trocando só o
   incidental (cenário/números/redação), mantendo o radical — mesmo
   processo de geração que já está em uso pro banco_pratica hoje.
4. **Estimativa de dificuldade sem esperar dado real** — opcionalmente,
   pedir à própria IA geradora uma dificuldade-alvo declarada
   (fácil/médio/difícil) no momento da geração, seguindo o princípio da
   §12.9 (é uma extensão do processo atual, não uma feature nova de
   infraestrutura).
5. **Validação humana** — Gabriel responde/revisa um por um, usando o
   MESMO botão de reportar que já existe (`relatos_questao`) pra marcar
   o que saiu errado — este passo já está pronto e em uso, é o único elo
   da cadeia que a pesquisa inteira (§11.4, §12.3) confirma ser
   indispensável e que nenhum projeto open source achado (§12.10) tem de
   forma madura.
6. **Controle de saturação** — evitar gerar mais de ~1,5-2× a quantidade
   que levou pra "fixar" o padrão a primeira vez (§12.8) antes de voltar
   a atenção pra outro `topico` ainda fraco.

Peças que JÁ EXISTEM: `questoes.topico`, `fase_de_topico()`,
`desempenho_por_topico()`, tabela `relatos_questao`, o próprio fluxo
manual de gerar-com-IA-e-validar que o Gabriel já roda. Peças que
FALTARIAM pra automatizar de verdade: nenhuma tabela nova é
estritamente necessária — o que falta é só rodar a consulta de
recorrência do passo 1 e decidir, com esse número em mãos, onde apontar
o próximo lote de geração — ou seja, a lacuna real é de PROCESSO
(decidir prioridade com dado), não de arquitetura de banco.

---

## 13. Até que ano vale carregar prova antiga pra análise de padrão

Pergunta direta do Gabriel: ele lembrava, sem certeza, que "2017 pra cima
é mais representativo" do ENEM atual, e queria saber até onde vale a pena
carregar prova antiga pro banco antes de confiar em qualquer contagem de
recorrência de `topico`. Resposta direta: **não achei confirmação de um
corte em 2015-2017 — a virada real é 2009, e nada de estrutural muda
depois disso até hoje.**

### 13.1 O que muda de fato em 2009 (a virada real)

2009 é quando o ENEM deixou de ser só uma autoavaliação e virou porta de
entrada pra faculdade: a prova foi reformulada, expandida pra 180 questões
objetivas cobrindo as 4 áreas do PCN (Linguagens, Humanas, Natureza,
Matemática), e passou a usar uma **Matriz de Referência** nova, com as
competências/habilidades que ainda hoje estruturam a prova. A **TRI**
(Teoria de Resposta ao Item) foi adotada junto — a primeira aplicação
corrigida por TRI foi a prova de 2009 (nota divulgada em 2010). Antes de
2009, o ENEM era outra coisa (uma única redação, sem TRI, não usado pra
ingresso direto na maioria das faculdades) — comparar conteúdo de antes de
2009 com hoje não faria sentido nem estrutural nem estatisticamente.

**A Matriz de Referência usada hoje é a MESMA de 2009** — nenhuma fonte
encontrada aponta uma matriz nova ou revisão de competências entre 2009 e
hoje. Ou seja: tecnicamente, toda prova de 2009 em diante testa a MESMA
estrutura de competências que a prova de 2025 testa.

### 13.2 O que (não) mudou em 2017

A mudança de 2017 foi **só logística**: a prova passou a ser aplicada em
dois domingos seguidos, em vez de sábado+domingo (mudança de calendário,
não de conteúdo). Não achei nenhuma fonte que documente uma revisão da
Matriz de Referência, mudança na proporção de itens por competência, ou
qualquer alteração de CONTEÚDO nesse período — a intuição do Gabriel de
"2017 é mais representativo" não tem uma origem estrutural clara que a
pesquisa confirme. É possível que a memória dele venha de outra fonte
(algum cursinho específico que usa esse corte por outro motivo, ou uma
confusão com a mudança de calendário), mas não é uma virada documentada
de matriz/conteúdo.

### 13.3 TRI torna dificuldade comparável entre anos, por design

Ponto técnico a favor de carregar mais anos: a TRI do ENEM existe
justamente pra tornar a nota comparável entre edições diferentes — "uma
nota de 700 em 2024 equivale ao mesmo nível de 700 em 2025", via
equalização contra um banco de itens comum. Isso significa que a
DIFICULDADE de um item de 2010 é, por construção do próprio modelo,
comparável à de um item de 2024 — não é um instrumento novo e desconectado
a cada ano. Isso reforça que não há razão TÉCNICA pra descartar anos mais
antigos por "não serem comparáveis" — a comparabilidade é o motivo pelo
qual a TRI existe.

### 13.4 O que análises reais (fora do meio acadêmico) já fazem

Não achei literatura formal declarando um tamanho mínimo de amostra
específico pra "quantos ANOS de prova analisar antes de confiar num
padrão de recorrência de tema" (é um recorte muito específico — a
literatura de sample size que existe é sobre número de EXAMINANDOS pra
calibrar um item via TRI, ~27-61 no mínimo segundo uma referência, não
sobre número de EDIÇÕES da prova pra contar recorrência de tema, que é
uma pergunta diferente). Na ausência de um número formal, o que existe é
precedente real: sites de preparação pro ENEM que fazem exatamente esse
tipo de levantamento usam janelas BEM diferentes entre si — um usa
2015-2024, outro conta desde 2016, e pelo menos um (alvoenem.com, 6.840
questões catalogadas) usa a série **inteira desde 2009**, sem excluir os
anos mais antigos. Não existe consenso de mercado em cortar em 2017 —
pelo contrário, quem tem MAIS dado (alvoenem) usa a janela MAIOR.

### 13.5 Recomendação prática pro ENEM_APP

Sem corte formal claro e com o argumento técnico (13.3) e o precedente de
mercado (13.4) apontando pro mesmo lado: **carregar a partir de 2009 faz
mais sentido do que restringir a 2017+.** Quanto mais prova real carregada,
menor o problema já visto na prática (seção 8, e a própria classificação
de hoje): com só 8 provas (2019-2025), nenhum `topico` de Ecologia/Óptica
teve mais que 2 ocorrências — amostra pequena demais pra qualquer
afirmação forte de "isso é o que mais cai". `importar_enem_dev.py` já
cobre 2009-2023 via API pública (`https://api.enem.dev`) sem precisar de
PDF local pra puxar enunciado/imagem — mas ele só PREENCHE questão que já
existe no banco (ver docstring do script); pra ANOS NOVOS (ainda não
carregados), falta primeiro o gabarito oficial (`gabarito_<ano>_<caderno>_OFICIAL.csv`),
que hoje só existe pra 2019 em diante em `gabaritos_reais/` — carregar
2009-2018 de verdade depende de conseguir o gabarito oficial desses anos
(PDF do INEP ou outra fonte), não só da API de enunciado.

Fontes: [História do ENEM: TRI e Sistema de Correção (SimpleTeacher)](https://www.simpleteacher.com.br/blog/historia-enem-tri-corrrecao-2009-2012), [Andifes — Saiba tudo sobre o Enem 2009](https://www.andifes.org.br/2009/05/15/saiba-tudo-sobre-o-enem-2009/), [ENEM 2017: confira as principais mudanças para este ano (AppProva)](https://appprova.com.br/enem-2017-confira-as-principais-mudancas-para-este-ano/), [Nota do Enem: como funciona a TRI (QueroBolsa)](https://querobolsa.com.br/revista/nota-do-enem-como-funciona-a-tri), [O que mais cai no Enem: análise 2015-2024 (Evolucional)](https://blog.evolucional.com.br/o-que-mais-cai-no-enem/), [O que mais cai no ENEM em cada matéria — 6.840 questões (AlvoEnem)](https://alvoenem.com/materiais/guia/assuntos-que-mais-caem-no-enem), [Sample Size and Item Calibration or Person Measure Stability (Rasch.org)](https://www.rasch.org/rmt/rmt74m.htm).

