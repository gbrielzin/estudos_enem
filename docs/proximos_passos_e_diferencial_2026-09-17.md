# Próximos passos e diferencial do ENEM_APP — síntese de 2026-09-17

Documento de planejamento, não de arquitetura nem de pesquisa — junta o que saiu
de `docs/pesquisa_estrategia_de_prova.md` (13 seções), de
`docs/questoes/moldes_novos_padroes_2026-09-17.md` e do trabalho de código do
dia (relatos, subfases, classificação de questão oficial) numa pergunta só:
**o que fazer a seguir, o que já pode jogar fora, e por que isso é diferente
de qualquer cursinho/app de estudo por aí**.

---

## 1. O que já dá pra "tirar" (crença que os dados de hoje derrubaram)

Nenhuma dessas coisas é erro de código — é crença/hipótese que a gente tratava
como verdade e hoje tem dado real contra ela.

1. **"Poluição Atmosférica é a prioridade máxima de Ecologia (28%)."** Zero
   ocorrência nas 11 questões oficiais já classificadas; Relações Ecológicas
   empatou como o padrão mais recorrente. O número de 28% em
   `docs/filosofia.md` nunca teve fonte citada (pendência já registrada antes
   de hoje) — depois de hoje, ele é oficialmente candidato a estar errado, não
   só "sem fonte".
2. **"Um resumo por matéria/fase é suficiente."** Falhou 2x no mesmo dia —
   Óptica (137 questões, 3 fenômenos bem diferentes) e Ecologia fase 2 (14
   padrões). A regra prática que sobrou: **se uma fase tem mais de ~5-6
   `topico` distintos, ela provavelmente precisa de sub-fase, não de resumo
   maior**. Vale auditar as fases 3/5/6 de Ecologia com essa régua antes de
   escrever resumo novo pra elas.
3. **"Repetir bastante o mesmo padrão é sempre bom."** Tinha dois lados que a
   gente só separou hoje: repetir ajuda a PEGAR O HÁBITO no início, mas
   continuar do mesmo jeito depois que o aluno já decorou o "tell" (palavra-
   chave no comando) é desperdício — e pior, ensina o aluno errado sobre como
   a prova real cobra. Ver achado da seção 2.5 do doc de pesquisa (illusion of
   fluency) + o relato do próprio Gabriel sobre inquilinismo repetindo tarde
   demais.
4. **"Confiar no que a IA gera sem desconfiar."** A seção 11 do doc de
   pesquisa achou o oposto do que se esperava: alunos que praticaram COM
   ajuda de IA foram PIORES na prova real depois, mesmo acertando mais durante
   a prática (estudo pré-registrado, PNAS). Isso não invalida gerar questão
   com IA (a seção 12 mostra que funciona bem com revisão humana) — invalida
   é usar IA como MULETA durante a prática de resolver (ex: um aluno real
   abrindo a explicação ANTES de tentar responder). O app já protege disso por
   acidente (a explicação só aparece DEPOIS de confirmar a resposta) — vale
   proteger de propósito, não por acaso, se a feature crescer.
5. **Amostra pequena tratada como veredito.** 11-17 questões oficiais por
   matéria é sinal, não prova. Toda vez que uma decisão de peso/ordem for
   tomada só com isso, tratar como "melhor palpite disponível hoje", não como
   fato — e revisar quando a amostra crescer.

---

## 2. O que falta com urgência real (não é "seria legal", é lacuna que já
   dói)

Ordenado por quanto está travando decisão HOJE, não por quanto dá trabalho:

1. **Nenhuma tela pra revisar os relatos.** 18 relatos, 3 resolvidos, 15
   abertos — hoje a única forma de ver isso é eu rodar uma query Python.
   Sem isso, o botão de reportar vira um funil sem saída conforme o volume
   cresce. É a peça que mais rápido vira gargalo se a validação continuar no
   ritmo de hoje.
2. **Classificação de `topico` real cobre só 5 das ~50 matérias carregadas**
   (Ecologia, Óptica, Acústica, Fisiologia Humana, Cinemática, Separação de
   Misturas — e olhe que Acústica ficou sem nenhuma questão oficial). Sem
   isso pras outras matérias (Química, Física, Biologia genérica —
   Eletrodinâmica já tem 13 questões oficiais e ZERO questão de prática),
   nenhuma decisão de "o que cai mais" fora desses 5 nós tem base nenhuma.
3. **Auditoria de distrator-óbvio ainda não rodou de verdade.** A gente
   discutiu fazer isso (checar se a resposta "vaza" no comando) mas nunca
   chegou a rodar contra o banco inteiro — só reagiu aos casos que o Gabriel
   achou na mão. Um script simples (checar sobreposição de palavra-chave
   entre comando e alternativa correta) cobriria isso sistematicamente em vez
   de depender só do relato manual.
4. **Redação não tem NENHUM trabalho de pesquisa ou padrão ainda**, apesar de
   valer 20% da nota do ENEM (200 de 1000 pontos) e já ter tabela própria
   (`redacoes`) no banco. Ficou de fora de todas as rodadas de hoje.
5. **Eletrodinâmica tem dado real (13 questões oficiais) parado sem uso** —
   não está na trilha fixa (por falta de questão de prática, decisão de
   2026-09-16), mas ninguém classificou essas 13 pra pelo menos SABER o
   padrão antes de decidir gerar conteúdo pra ela.

---

## 3. Como a implementação de questão deve seguir a partir daqui

O ciclo que a gente validou hoje, na prática, com Óptica e Ecologia:

```
prova oficial carregada
        ↓
classificar `topico` (radical -- o que NÃO muda)
        ↓
achar o pool de alternativas que se repete (ex: difração/refração/
dispersão/polarização/absorção) -- isso é o "item model" de verdade
        ↓
escrever o molde (CONCEITO INICIAL + radical + incidental + distrator
plausível baseado em erro real, não em opção aleatória)
        ↓
gerar lote com IA a partir do molde
        ↓
Gabriel valida (responde, reporta o que está errado -- já é rotina)
        ↓
entra no banco de prática com `topico` correto desde o nascimento
```

O gargalo real não é gerar questão (a seção 12 do doc de pesquisa validou que
IA + revisão humana produz item psicometricamente equivalente a item
humano) — é a ETAPA 1 (classificar `topico` de questão oficial), porque
ainda é 100% manual e cobre 5 de ~50 matérias. Se alguma coisa merece virar
ferramenta (um script que ajuda a sugerir `topico` a partir do texto,
mesmo que precise de confirmação humana depois), é essa etapa.

---

## 4. Onde este app é diferente de qualquer cursinho/Anki/Duolingo genérico

Isso é a pergunta mais importante do pedido, então merece ser dita direto,
sem meio-termo:

**A maioria dos concorrentes otimiza por VOLUME de questão ou por HORAS de
estudo. Este app está montando algo que nenhum deles faz de verdade:
recorrência REAL medida, item por item, contra a prova que o aluno vai
fazer, com o próprio aluno validando a qualidade do conteúdo gerado antes
dele virar prática.**

Detalhando os 4 pontos que sustentam essa frase:

1. **Recorrência medida, não assumida.** Cursinho grande vende "o que mais
   cai" com base em intuição de professor experiente (que é real, mas não é
   auditável). Este app tem uma tabela (`topico` + `fase_de_topico` +
   provas oficiais carregadas) que permite CONTAR, questão por questão, e
   MUDAR de ideia quando o dado discorda da intuição inicial (foi
   literalmente o que aconteceu hoje com Poluição Atmosférica). Nenhum
   cursinho vai reclassificar o material dele publicamente quando confrontado
   com o próprio histórico de provas.
2. **O ciclo de geração de questão é auditado por quem vai USAR.** A
   pesquisa (seção 12) mostra que IA gerando item com revisão humana funciona
   — mas a maioria das ferramentas que geram questão com IA (incluindo
   produtos comerciais) não têm um Gabriel resolvendo cada questão e
   reportando o que está errado ANTES do conteúdo virar "oficial" no banco.
   O relato de hoje pegou coisa que nenhuma revisão só de leitura pegaria
   (ex: "só dá pra matar lendo o comando" -- isso só aparece resolvendo de
   verdade sob pressão de tempo, não relendo com calma).
3. **Pedagogia que muda por TIPO de conteúdo, não uma fórmula pra tudo.** A
   seção 9 do doc de pesquisa (productive failure pra conceitual, worked
   example pra procedural) ainda não está implementada, mas já está
   documentada como direção -- e é uma diferenciação real: Duolingo/Anki
   tratam todo conteúdo com o mesmo algoritmo de repetição, sem diferenciar
   "decorar uma tabela de sinais" (Ecologia) de "aplicar uma fórmula em
   sequência" (Cinemática).
4. **TRI-aware, não "quanto mais acerto melhor".** A seção 2.8 (TRI) e o
   trade-off frequência x dificuldade que gerou a reordenação de hoje são a
   mesma lógica: dominar o fácil/médio de verdade protege mais a nota do que
   arriscar difícil sem base -- isso é contra-intuitivo pra quem vem de
   sistema de nota tipo prova de escola (soma pontos), e é exatamente onde um
   sistema comum de "banco de questão" não ajuda, porque trata toda questão
   como valendo o mesmo.

**Onde isso ainda é promessa, não produto**: hoje só Ecologia e Óptica
passaram pelo ciclo completo (classificar → validar → reordenar). O
diferencial só vira real pro aluno quando isso escalar pras outras ~45
matérias com dado carregado — e é exatamente o item #2 da seção 2 acima.

---

## 5. O que ainda não está claro / falta pesquisa

Sendo honesto sobre os buracos, não só sobre o que já foi validado:

1. **N=1.** Toda validação de hoje veio de UM aluno (o próprio Gabriel)
   fazendo UMA trilha. É sinal forte pra decisão de conteúdo, mas zero
   evidência de que o SISTEMA (gamificação, streak, XP) funciona pra outro
   perfil de aluno -- não tem como saber isso sem mais gente usando.
2. **O número "40-60 questões pra fixar um padrão"** (hipótese registrada
   antes de hoje em `docs/filosofia.md`) nunca foi confirmado por pesquisa
   -- o mais perto que a seção 9 chegou foi "overlearning ratio de 1,5-2x a
   repetição inicial", que é um número DIFERENTE e não bate exatamente. Vale
   marcar esse "40-60" como não-verificado até achar a fonte original ou
   descartar.
3. **A mecânica de dificuldade escalando por exposição** (achado do relato de
   hoje sobre inquilinismo repetir "fácil demais" depois de já aprendido) não
   tem NENHUMA pesquisa por trás ainda -- é uma boa intuição pedagógica, mas
   precisa da mesma checagem que o resto do documento de pesquisa já fez pro
   resto (existe estudo sobre isso? qual nome tem esse conceito na
   literatura -- possivelmente "adaptive difficulty"/"desirable difficulty
   progression"?).
4. **Redação inteira sem pesquisa** (item 4 da seção 2).
5. **Retenção de longo prazo (meses) deste sistema específico** não tem como
   ser medida ainda -- é cedo demais (todas as mudanças de hoje têm horas de
   idade). Vale marcar uma data futura (ex: daqui a 60-90 dias) pra revisitar
   e ver se o que pareceu bom hoje realmente segurou.

---

## Resumo de uma linha por seção

- **Tirar**: peso de 28% sem fonte, resumo único pra fase grande, repetição
  sem variar dificuldade, confiar em IA sem desconfiômetro, tratar amostra de
  11 questões como veredito.
- **Urgente**: tela de relatos, classificar as outras ~45 matérias, auditoria
  automática de distrator óbvio, começar a pesquisar redação, usar as 13
  questões de Eletrodinâmica já carregadas.
- **Como a implementação segue**: o ciclo classificar → molde → gerar →
  validar já está provado (Óptica/Ecologia) -- o gargalo é escalar a
  classificação, não a geração.
- **Diferencial**: recorrência medida (não assumida) + geração de IA
  auditada por quem usa + pedagogia por tipo de conteúdo + prioridade
  TRI-aware -- isso ainda só cobre 2 de ~50 matérias, o resto é promessa até
  escalar.
- **Não está claro**: tudo isso é validado com 1 aluno só; "40-60 questões"
  não tem fonte confirmada; dificuldade escalando por exposição é ideia nova
  sem pesquisa; redação é zero; retenção de longo prazo só se mede daqui a
  meses.
