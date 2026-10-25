# Ideias de melhoria (backlog acumulativo)

Lugar único pra juntar ideias de produto/UI que surgem nas sessões de estudo,
pra não se perderem no chat. **Nada aqui está decidido nem priorizado:** é
entrada pra sessão de projeto. Cada ideia leva data, origem e, quando tem,
a evidência. Ideia nova entra no fim da seção certa; ideia implementada é
marcada com ✅ e o commit/PR, não apagada.

Relacionados: [metodo_e_aprendizados.md](metodo_e_aprendizados.md) (o que as
sessões ensinaram), [filosofia.md](filosofia.md) (trilha ROI, em aberto),
[questoes_sinteticas_repeticao.md](questoes_sinteticas_repeticao.md).

---

## 1. Avaliação da UI — 2026-09-24

Baseada nas telas do handoff (`design_handoff_enem_gamificado/screens`) e nos
tokens do app mobile, não no app rodando.

| Critério | Nota | Resumo |
|---|---|---|
| Acabamento visual | 8/10 | Paleta coerente (grafite, lima, violeta, âmbar), botões com degrau 3D, boa tipografia e contraste |
| Apelo ao público jovem | 7/10 | Trilha, XP, streak, liga e mascote (Pipoco) são linguagem reconhecida na hora |
| Diferenciação | 4/10 | Visualmente é "Duolingo do ENEM"; o app oficial MEC Enem já tem trilhas + gamificação + assistente de IA, de graça |
| Encaixe com o ENEM real | 5/10 | Tela de questão pensada pra enunciado curto; ENEM real tem texto longo, gráfico e tabela. Corações punem o erro, que no método é diagnóstico |
| **Geral** | **~6/10** | Execução boa, proposta visual genérica |

Detalhes vistos nos prints: nome interno vazando ("geometria_espacial"),
"questão(ões)", "S-Rank · 4564 XP" ao lado de streak 0.

**Conclusão:** o diferencial não é o visual, é o método (diagnóstico → kit →
molde → original espaçada), e a UI ainda não mostra nada dele. Manter o
visual e mudar **o que ele celebra**.

---

## 2. Ideias

### 2.1 Mostrar o método na tela

- **Card de kit antes do molde** (2026-09-24): fórmula + gatilho por
  unidade + apelido ("Você Ri", "Que macete"). Nenhum concorrente usa
  apelido. Origem: sessões de 23 e 24/09.
- **Feedback da armadilha** (2026-09-24): `moldes.py` já guarda o motivo de
  cada alternativa errada (`distratores`). Mostrar "você caiu no *passo pela
  metade*" em vez de só "errou". Evidência: feedback elaborado (explica o
  erro e como evitar) supera feedback de certo/errado, meta-análise d ≈ 0,48
  pra feedback em geral (Wisniewski, Zierer & Hattie, 2020). Também reduz o
  risco de o aluno memorizar a alternativa errada, que existe em múltipla
  escolha sem feedback.
- **"A original voltou"** (2026-09-24): quando uma questão que ficou em
  branco volta na revisão espaçada, sinalizar ("ontem em branco, hoje
  sozinho?"). Foi a sensação de competência relatada em 24/09 (3 de 4
  originais saíram sozinhas).
- **Molde conceitual** (2026-09-24): pra biologia/ecologia, o molde troca
  as pistas e o contexto, não os números (bioma com outras pistas, pares
  vizinhos, mesmo mecanismo por outro ângulo). Ver metodo_e_aprendizados.md
  seção 7.

### 2.2 Gamificação que não pune o erro

- **Trocar corações por outra coisa** (2026-09-24): corações interrompem a
  prática depois de errar, e no método o erro é o diagnóstico. A crítica
  pública ao sistema do Duolingo é justamente ansiedade e "aprendizado
  truncado"; o argumento a favor é que dá peso ao erro e evita chute. Ideia
  intermediária: sem bloqueio, mas o erro abre o kit/degrau obrigatório
  antes de seguir (dá peso sem travar).
- **Celebrar outras coisas além de XP por acerto** (2026-09-24):
  "armadilha evitada", "saiu sozinho", "branco virou acerto", "original
  confirmada depois de N dias".

### 2.3 Encaixe com o ENEM real

- **Tela de questão pra enunciado longo** (2026-09-24): rolagem confortável,
  imagem/tabela ampliável, alternativas fixas embaixo. Hoje o design assume
  3 linhas de enunciado.
- **Glossário na própria questão** (2026-09-24): em 23 e 24/09 a trava
  principal foi vocabulário (fóton, efluente, peptídeo sinal, gema apical,
  tricoma). Tocar na palavra mostra o significado sem entregar a resposta.
  Cuidado: só o significado da palavra, nunca a função que resolve a questão
  (erro cometido à mão em 24/09, questão 2012_azul_57).
  - 2026-09-28: a ideia vale também para Linguagens/Humanas (oligarquia,
    drenagem, monopólio, taramelar, fastidioso). Gabriel pediu glossário
    pensando em outros usuários do app, não só nele.
- **Revisão de hoje de volta na UI** (2026-09-28): a barra de modos saiu
  em 11/09 e o `estado_revisao` acumulou 660 questões atrasadas (quase todas
  dos simulados de agosto). Precisa de porta de entrada e de algum teto/filtro
  (ex.: priorizar prática guiada), senão a fila assusta.

### 2.4 Revisão

- **Revisão intercalada** (2026-09-24): misturar matérias/fórmulas na
  revisão, como a "mistura" de 23/09 (escolher a fórmula certa entre 4).
  Evidência: prática espaçada em matemática g ≈ 0,28 (Murray et al., 2025);
  intercalar prática de recuperação ajudou aprendizado de ciências (Sana &
  Yan, 2022). O efeito de testagem isolado em matemática foi fraco nessa
  mesma meta-análise, então o ganho parece vir mais de espaçar e misturar
  do que de só "fazer mais questão".
- **Fila de revisão antiga** (2026-09-24): ~630 revisões vencidas de
  agosto/começo de setembro (blocos inteiros de 2019-2024 e `pratica_*`)
  que não vieram das sessões guiadas. Decidir: entram na fila, zeram, ou
  viram fila separada de "simulado".

### 2.5 Correções pequenas de UI

- Nome interno vazando na missão ("geometria_espacial" → "Geometria espacial").
- "questão(ões)" → plural resolvido pelo número.
- Rank/XP alto ao lado de streak 0 soa incoerente; revisar o que o header destaca.

---

## 3. Concorrência (anotado em 2026-09-24)

- **MEC Enem (oficial, grátis):** trilhas por complexidade e área,
  simulados com questões reais, gamificação, assistente de IA. É o
  concorrente direto do formato "trilha gamificada".
- **Apps privados** ("Questões ENEM Simulado Gamificado", "Prepara",
  "Enem Questões e Simulados"): banco de questões + ranking/desafios +
  simulado por área/tema.
- **enemwiki.com.br:** TRI/Raio-X gratuito (ver memória de referência).

Nenhum dos listados, pelo que as descrições mostram, faz molde com números
trocados, feedback por armadilha ou kit com apelido. Não verificado dentro
dos apps, só pelas descrições das lojas/notícias.

---

## Fontes

- Murray et al. (2025), *A Meta-analytic Review of the Effectiveness of Spacing and Retrieval Practice for Mathematics Learning*, Educational Psychology Review — https://link.springer.com/article/10.1007/s10648-025-10035-1
- Sana & Yan (2022), *Interleaving Retrieval Practice Promotes Science Learning* — https://pdf.retrievalpractice.org/spacing/InterleavedRetrievalPracticePromotesScienceLearning_SanaYan_2022.pdf
- Wisniewski, Zierer & Hattie (2020), *The Power of Feedback Revisited* — https://pmc.ncbi.nlm.nih.gov/articles/PMC6987456/
- *Elaborated feedback and learning* (Computers & Education) — https://www.sciencedirect.com/science/article/abs/pii/S036013151930082X
- *When Gamification Spoils Your Learning* (estudo qualitativo, Duolingo) — https://arxiv.org/pdf/2203.16175
- Análise do sistema de corações/energia do Duolingo — https://trophy.so/blog/why-duolingos-energy-system-works-and-when-to-copy-it
- INEP, aplicativo MEC Enem — https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/aplicativo-mec-enem-apresenta-questoes-e-simulados-do-exame
- TechTudo, apps grátis pro Enem 2026 — https://www.techtudo.com.br/listas/2026/09/enem-2026-8-aplicativos-gratis-para-estudar-para-a-prova-edapps.ghtml

---

## 4. Ideias de 2026-09-25 (sessão de faculdade e estágio)

- **Simulador "onde eu entro"** (2026-09-25): o aluno digita as 5 notas (ou o app estima a partir dos acertos, via tabela TRI) e vê cursos com nota ponderada pelos pesos de cada curso vs corte da cota dele. Protótipo já existe como página (ranking de 24 cursos de tecnologia, cortes SISU 2025 + Enem-USP 2026). Cuidados aprendidos: pesos têm decimal (UFABC 1,5), confiar só em PDF oficial, corte varia 10-30 pontos por ano.
- **"Quanto vale cada acerto pro meu curso"** (2026-09-25): usar os pesos do curso-alvo pra priorizar matéria (ex.: em SI USP, +1 acerto em Matemática ≈ +2,4 na nota final vs ≈ +0,7 em Humanas). Liga com `prioridade_de_estudo()`.
- **Estimativa de nota por área a partir dos acertos do app** (2026-09-25): já foi feita à mão nesta sessão (Natureza ~560, Matemática ~695 pelas provas inteiras); virar função/tela, com aviso de que TRI pesa coerência.

---

## 5. Projeto 3 (separado do ENEM): "Radar de Estágios" — plano de fases (2026-09-25)

**Status:** ideia aprovada pra backlog; **não começar antes do ENEM (08 e 15/11/2026)**, no máximo a Fase 0-1 se sobrar tempo.

**O que é:** sistema que coleta vagas de estágio de TI todo dia, usa IA pra extrair o que cada vaga pede e mostra num painel quais habilidades/cidades/áreas estão em alta e como mudam no tempo.

**Por que este projeto:** cobre os 3 diferenciais que faltam no currículo, vistos nas vagas "elite" de 25/09 (Salesforce AI Builder Intern, BCG X AI Engineering Intern, AWS, Artefact Engenharia de Dados, 99 AI Transformation): **pipeline de dados automatizado**, **IA via API** (não só chat) e **cloud**. Tem uso real (achar a própria vaga).

**Ponto de partida:** a coleta manual de 25/09 — script e amostra salvos fora do repo em `Desktop/Projetos/radar_estagios_rascunho/` (`coleta_gupy.py`, `amostra_2026-09-25.json`, 104 estágios de TI).

**Regra de fonte:** só fontes abertas (busca pública da Gupy e similares). **Nada de raspagem do LinkedIn** num projeto público (termos de uso proíbem); LinkedIn só como conferência manual.

| Fase | Entrega | Habilidade que prova | Tamanho |
|---|---|---|---|
| **0. Esqueleto** | repo novo, README com o problema, `coleta_gupy.py` limpo, testes do filtro (título de TI x "Programa de Estágio", "Desenvolvimento Humano") | Python, Git, testes | 1 sessão |
| **1. Banco + histórico** | coleta grava em SQLite/DuckDB com data; roda de novo sem duplicar vaga | SQL, modelagem, idempotência | 1-2 sessões |
| **2. Agendamento** | GitHub Actions roda a coleta todo dia e salva o resultado | automação, CI/CD | 1 sessão |
| **3. IA estruturada** | LLM via API lê a descrição e devolve JSON (habilidades, área, suporte x dev x dados x IA, remoto, nível); comparar com o filtro por regex e medir a diferença | IA aplicada, saída estruturada, avaliação | 2 sessões |
| **4. Painel** | habilidades mais pedidas, vagas por cidade e área, evolução semanal (Streamlit ou Power BI) | visualização, BI | 1-2 sessões |
| **5. Cloud** | banco e painel hospedados (ex.: um serviço gratuito/barato de nuvem) com link público | cloud, deploy | 1-2 sessões |
| **6. Uso pessoal** | alerta de vaga nova que combina com o perfil dele; "o que me falta pra essa vaga" | produto | depois |

**Lições da coleta manual (não repetir):** "Programa de Estágio" casava com "programação"; "Desenvolvimento Humano/de Fornecedores" casava com desenvolvimento; regex escrito via heredoc virou caractere de backspace (usar arquivo .py, não heredoc); a busca deslogada do LinkedIn devolve no máximo ~60 por consulta e mistura júnior/aprendiz (não serve pra volume).

**Acréscimo (2026-10-03) — empresa-alvo como bússola:** filtrar o radar pelas empresas que ele quer (Itaú, Nubank, Mercado Livre...) e usar a contagem de habilidades pra escolher o próximo projeto de portfólio. Pitch de entrevista: "analisei X vagas de vocês e montei o portfólio em cima disso". Não chutar o que a empresa cobra; tirar das vagas reais.

- **Moldes das famílias de 26/09 + oferecer o molde logo após o erro** (2026-09-26, pedido do usuário: "armazenar essas questões caso alguém erre, pra fixação"). Famílias que apareceram com erro e saíram sozinhas na variação: (1) proporção por partes (contrapiso 2013_159; pergunta pede outro ingrediente), (2) aumento percentual → consumo total, não o pedaço (café 2011_145), (3) escala com dois limites (navio 2018_169; testar um número de dentro de cada alternativa), (4) densidade superficial com vírgula decimal (papel 2020_azul_179). Evidência: 4 originais com ajuda → 3 de 4 variações certas sozinho no mesmo bloco. Regra de produto: questão oficial errada ou com ajuda → abre o kit → oferece o molde da família antes de seguir.
- **Banco de redações nota 1000 pra análise de padrão** (2026-09-26, ideia do usuário): extrair das cartilhas do INEP já baixadas (2019, 2022-2026, `docs/redacao_pesquisa/cartilhas/*.txt`) cada redação nota 1000 pra uma tabela (tema, ano, abertura/repertório da intro, as 2 causas, repertório de D1/D2, proposta: agente/ação/meio/finalidade/detalhamento, comentário do INEP). Uso: comparar padrões (quantas abrem com CF/88, tipo de causa material x imaterial) e, depois, calibrar o corretor por IA. Bom material de vídeo ("analisei todas as nota 1000").
- **Mais textos de redação 900+ (2026-09-26, pra depois)**: (1) experimento com o **Common Crawl** (índice de URLs de bilhões de páginas, aberto) procurando páginas de redação 900+ e puxando o HTML arquivado, sem acessar os sites; (2) **Wayback Machine** pra recuperar redações que saíram do ar; (3) **coleta com consentimento no app** ("mande sua redação + foto do espelho" em troca de uma análise contra o banco de notas 1000) — o único caminho pra milhares de textos 900+ legítimos; OCR da foto do espelho. Contexto: notas 1000 de 2018-2025 são só 272 e o banco já tem ~85%; o gargalo das 900+ é que quase ninguém publica o texto (privacidade), não a busca.
- **Painel de visualização do banco de redações e dos microdados** (2026-09-27, ideia do usuário na revisão do PR #23: "tem muita informação útil, seria interessante visualizar"): aberturas mais usadas, repertórios por ano (ex.: Mbembe surgindo em 2025), distribuição das notas e média por competência por faixa (microdados 2025), consenso das dicas (top 25 + contradições). PR separado do #23.

- **Treino de redação por chunking (27/09, ideia dele):** treinar uma parte da redação por vez (introdução → D1 → D2 → conclusão) com repetição curta em vários temas, como treino de inglês por blocos, até a parte ficar automática. No app: exercício "só a introdução" com tema sorteado, cronômetro curto e checklist da parte (recorte exato, causa do Estado, causa social do tema, repertório ligado à tese).
- **Ler as alternativas antes (27/09, padrão dele):** quando 3+ alternativas têm os mesmos algarismos e só muda a quantidade de zeros/expoente, o distrator é de unidade/conversão -> a decisão é contar zeros. Dica contextual no app pra questões de escala/unidade.
- **Corretor de redação por LLM "justo" (27/09, reforço dele):** a correção tem que imitar o corretor humano, não um revisor letra por letra. Nota 1000 tem erros que o humano não pega/não desconta, então um LLM que caça todo desvio fica mais duro que o INEP. Calibrar pelo banco de notas 1000 + comentários das cartilhas (o que é aceitável no conjunto), com 2 corretores e a regra de discrepância do INEP. Página de treino por partes já existe: https://claude.ai/artifact/P6B6NzZFQGVRuXwUufnM4F (introduções salvas no db do artifact).

---

## 6. Ideias de 2026-09-25 (diagnóstico de Matemática)

- **Sem vidas/corações, confirmado pelo usuário** (2026-09-25): o Duolingo inspira só a trilha. Reforça a 2.2: o erro abre o kit, não bloqueia.
- **Tempo por questão** (2026-09-25): pedido do usuário. `registrar_tentativa` já aceita `duracao_segundos`; falta a tela medir (início ao abrir, fim ao confirmar) e mostrar contra a referência de ~3 min/questão do ENEM. Evidência: no mesmo bloco, uma questão levou ~10 min (densidade) e uma variação 2 min.
- **"Não bateu? Relê as 5"** (2026-09-25): quando a resposta marcada é um distrator do tipo "ordem de grandeza" (×10, ÷10), o feedback manda reler as alternativas e refazer a conta, nunca ajustar o resultado. Evidência: 2 vezes em 2 dias o aluno chegou no número certo (93; 0,09) e mudou pra alternativa ×10 porque não viu a certa.
- **Molde de fator de escala: linha × área × volume** (2026-09-25): família que derrubou 3 questões reais (caixa-d'água/escala, docinhos esféricos, e as mesmas em agosto). Molde com números trocados (fator 2, 3, 10; esfera, cubo, maquete) e o desenho azulejo (×4) x dado (×8) como kit. Saiu sozinho em 2 min na 2ª variação.
- **Diagnóstico por padrão de desvio, não por matéria** (2026-09-25): em Matemática a base existia; o que derrubou foram 3 desvios repetidos (conferir alternativas, ler decimal, área x volume). O painel poderia mostrar "seus 3 desvios" com contagem, alimentado pelos `distratores` que o aluno escolhe.
- **Macetes de cálculo e de estudo no app** (2026-09-25, pedido do usuário): cards curtos de "conta de cabeça" e hábitos de prova, mostrados no ponto em que ajudam (no kit, ou no feedback quando o erro foi de conta). Já testados na sessão: n² de 11-19 = (n + unidade)·10 + unidade²; terminado em 5 = dezena·(dezena+1) e cola 25; ÷250 = ÷1000 ×4; multiplicar o "pequeno" e colar os zeros no fim (4,65×20 000); potência separando 400³ = 4³·100³; conferir letra × texto antes de marcar; resultado fora das alternativas = reler as 5 e refazer. Liga com "seus 3 desvios": o macete aparece quando o desvio correspondente aparece.

## 7. Ideias de 2026-10-03

- **Prova com variações:** o aluno refaz uma prova inteira (ex.: ENEM 2024) com cada questão + 3 variações (45 × 4 = 180 itens, ou 45 × 3 = 135 se trocar a original). Cuidados: parâmetros TRI só valem pra questão original (variação treina, não mede nota); variação gerada por IA precisa de revisão de gabarito. Começo pequeno: variações só das questões que o aluno errou.
- **"Pergunte ao canal" (RAG em transcrições):** a partir da coleta do YouTube-Commons (PR #26), busca semântica nas transcrições que devolve o trecho + link no minuto exato. No app: "vídeo que explica essa questão". Só vídeos com licença aberta ou com autorização do canal (baixar canal dos outros esbarra nos termos do YouTube).

**Correção (2026-10-03) — fonte do Radar:** os termos de uso da Gupy (gupy.io/termos-de-uso-recrutamento-e-selecao-candidatos) proíbem "agregar, copiar ou duplicar partes do Gupy Recrutamento e Seleção, incluindo oportunidades de trabalho expiradas". A "regra de fonte" acima (Gupy como fonte aberta) **não vale** pra um projeto público que acumula vagas. Antes da Fase 0: ler os termos de cada fonte candidata; opções a avaliar — boards com API pública feita pra isso (ex.: Greenhouse/Lever, conferir quais empresas-alvo usam), pedir autorização, ou coleta manual pequena só pra análise pessoal sem republicar. Pesquisa de concorrência em `Desktop/ideias/pesquisa_concorrencia_radar.md`.

## 8. Ideias de 2026-10-05

- **Cadernos visuais por conteúdo:** as páginas que nascem nas sessões de estudo (ex.: `docs/materiais/caderno_organica.html`, química orgânica do zero com moléculas em zigue-zague desenhadas por código, etapas progressivas e exercícios) ficam guardadas em `docs/materiais/` pra servir a outros alunos. Depois: linkar no app pelo tópico da questão errada ("não sabe a base? abre o caderno"). Cuidado: revisar o conteúdo antes de publicar pra outros (feito durante a aula, pode ter atalho didático).

## 9. Ideias de 2026-10-06

- **Questão real dentro do caderno, e cadernos interativos:** a questão real do bloco entra no próprio caderno (imagem + enunciado + alternativas), em vez de só no chat. O aluno não precisa trocar de tela. Pros conteúdos que pedem movimento, o caderno vira interativo. Exemplo: em eletrodinâmica, um circuito em que se liga e desliga chave ou se troca resistor e a corrente muda na hora (série × paralelo). Mesma lógica pra gráfico (arrastar um ponto e ver a inclinação mudar) e vetores.
- **Treinos em formato de game (sinal de produto, 06/10):** o treino de nomes do caderno de orgânica (níveis pares → todas → digitar, errou volta em 2-3 rodadas, feedback na hora) levou o Gabriel de 6/10 a 19/20 digitando no mesmo dia. Ele disse que "tem futuro", e o amigo do beta deu feedback muito positivo. Candidato a recurso do app: um "game" por conteúdo (nomes, fórmulas, unidades), com o histórico salvo no banco em vez de no navegador. Caderno de combinatória (montar duplas clicando + tabela que pinta) é o 2º exemplo.
- **Macetes de conta por matéria + caderno de contas básicas (06/10):** cada caderno ganha um card "atalho de conta" do conteúdo (combinatória: cortar antes de multiplicar, ×11, ×9). E um caderno/game à parte pra treinar soma, subtração, multiplicação e macetes gerais (ex.: multiplicar de 11 a 19), com o mesmo formato de repetição com feedback na hora. Ele observou: tem matéria que pede visual/dinâmica, e tem matéria em que basta passar a fórmula e fazer repetir, sem poluir de informação.
- **Prioridade de produto (06/10, revista no mesmo dia):** com a entrada do amigo do beta como usuário, simplificar o app e priorizar qualidade na reta final. A trilha ainda não está madura pra usuários e fica de fora por enquanto. Perguntar a cada usuário o que quer e personalizar.

## Referência: MaTRIx / Chapéu do Mago (análise 09/10/2026)
O que eles têm e dá pra fazer no ENEM GI com os **parâmetros TRI oficiais do INEP que já estão no banco** (`tri_a`, `tri_b`, `tri_c`):
- **Mapa térmico dos erros:** grade dificuldade (fácil/média/difícil/desafiadora, por `tri_b`) × discriminação (fraco/moderado/forte, por `tri_a`), com perfis nomeados (“Obrigatória”, “Alavancagem”, “Filtro competitivo”…) e ganho médio de pontos por célula. Pago no site deles.
- **“Quanto cada erro custou”:** simulação TRI de +X pontos se tivesse acertado aquela questão. Pago lá.
- **“O que revisar agora”:** top 5 temas por prioridade a partir dos erros. Pago lá.
- **Tela da questão:** cronômetro de tempo gasto (pausa com aba em segundo plano), “marcar como dúvida” (amarelo no mapa), mapa das 90 com 4 estados, grifo em 5 cores + caneta + borracha, eliminar alternativa (✕), reportar erro (7 tipos), salvamento offline.
- **Por questão:** % de alunos em cada alternativa, inclusive entre os de alto desempenho.
- **Ao concluir:** aviso de quantas estão em branco (“em branco conta como erro”).
Diferencial possível: entregar de graça o que eles cobram (mapa térmico + custo do erro), já que o dado é público.
Preço (09/10/2026): MaTRIx+ só vem no pacote “Revisão Enem CdM”, R$ 147 à vista ou 12x R$ 14,70, acesso até 30/11/2026, garantia de 7 dias. Âncora de “R$ 991” sem venda avulsa visível. Diferenciais anunciados: TRI “calculada, não estimada” com parâmetros do INEP, % de marcação por alternativa (microdados), TRI Lab (chance de acerto por faixa de nota), matriz de 9 perfis, link com SISU (simulador “em breve”).

## Referência: Medly AI (análise 10/10/2026)

App britânico de revisão pra GCSE/A-Level/IB com tutor de IA. Mesma proposta do ENEM GI (questão no formato da prova + correção na hora + tutor), outro mercado. Lançou em fev/2025, diz ter 400 mil usuários no Reino Unido com ~1h/dia de uso; seed de US$ 8 mi em ago/2026 (Felix Capital), indo pros EUA com SAT. Plano pago citado de £24,99/mês com versão grátis (preço visto em uma fonte só).

O que eles têm e serve de ideia pra cá:
- **Correção com IA de resposta escrita, com comentário no texto** → equivalente aqui é a redação corrigida por competência (C1-C5).
- **Simulado nacional grátis com nota de corte** ("Medly Mocks") → simulado ENEM GI aberto em data marcada, com nota TRI estimada; serve de porta de entrada e gera dado.
- **Questão organizada pelo conteúdo oficial da prova** → já temos (matriz/habilidade do INEP).
- **Teste com grupo de controle** (efeito 0,33, maior em Biologia) → pro beta: medir quem usou x quem não usou antes de dizer "melhora a nota".
- Ponto fraco apontado: sem vídeo, só texto/diálogo.

O que nós temos e eles não: dado oficial do INEP (TRI, parâmetros dos itens, microdados de redação), foco no ENEM e preço pra quem tem pouco dinheiro.

Fontes: [tech.eu](https://tech.eu/2026/08/19/medly-ai-raises-8m-to-bring-ai-powered-tutoring-to-more-students/), [The Next Web](https://thenextweb.com/news/medly-ai-8m-seed-felix-capital-gcse-tutoring), [EdTech Innovation Hub (teste)](https://www.edtechinnovationhub.com/news/medly-ai-trial-finds-significant-gcse-science-gains-across-all-three-subject), [Cognito (comparação)](https://cognito.org/blog/medly-ai-vs-save-my-exams), [App Store](https://apps.apple.com/gb/app/medly-ace-your-exams/id6670685314).

**Atualização 10/10/2026: o Medly já chegou ao Brasil com ENEM** (https://www.medlyai.com/pt-br/exams). Concorrente direto agora:
- Cobre as 4 áreas do ENEM + vestibulares + trilha universitária (sobe aula/slides e vira exercício e cartão de revisão).
- **Simulados Medly ENEM '26 grátis**, com correção e colocação nacional (inscrição desde 23/09).
- Tutor socrático (pergunta em vez de entregar; botões dica / conceito / passo a passo), plano de estudo em blocos de 15/30/60 min com data da prova.
- **Preço: R$ 124,90/mês ou R$ 74,90/mês no anual (R$ 898,80).** Grátis pra começar.
- **Não corrige redação**; avisa que não tem parceria com INEP/MEC; não mostra gamificação na página.
- Onde o ENEM GI ainda se diferencia: preço pra quem tem pouco dinheiro, dado oficial do INEP (TRI dos itens, microdados de redação), questões reais com resolução própria + cadernos visuais/interativos, redação por competência, mascote/gamificação (Pipoco).

## Referência: Kuadro (análise 10/10/2026)

https://kuadro.com.br/ — cursinho online ENEM + vestibulares (Medicina, ITA/IME, Fuvest), desde 2015, de Bruno Werneck e Lucimara Anacleto (começou como canal no YouTube em 2011). Site feito em Lovable.
- **Preço:** Extensivo 2027, 15-16 meses, 12x R$ 119 ("de R$ 1.848", "menos de R$ 3 por dia"); 22% off no anúncio.
- **Planejador de Estudos** é a vitrine: a pessoa informa dias/horas, quanto domina cada matéria e o vestibular → tarefas do dia; matéria fraca e de peso alto vai pra frente; redação semanal reservada; simulado completo a cada 6 semanas; vira revisão com provas antigas na reta final; "ajuste automático" depois de simulado ("mandou bem em Química, +1h de Física").
- Diagnóstico de fraquezas, correção de redação ilimitada (em até 48h), simulados com **nota TRI**, tira-dúvidas todo dia, mentoria em grupo a cada 15 dias, "método de estudo ativo baseado em resolução de questões".
- Marketing: garantia "seguiu o plano e não passou, devolvemos 100%" (com regulamento), "+5,5k aprovados" (número deles), mural de aprovados com história de cada um, "clube das notas 900+" em redação.

O que serve de ideia pro ENEM GI:
- O **planejador do dia** é o que o app já tem em `gerar_plano_de_estudo()` (Streamlit) — falta levar pro mobile com a mesma cara: "hoje é terça, 2h30 livres, faltam 2 tarefas".
- **Ajuste automático explicado em uma frase** depois de cada simulado (o motivo de cada bloco já existe no plano).
- **Mural de resultados com história** → no beta, registrar a evolução de quem usa (com permissão) desde o 1º dia.
- O método deles ("resolução de questões") é o mesmo do projeto; a diferença a mostrar é o **dado do INEP** e o preço.

## Referência: PraticAI do Bernoulli (análise 10/10/2026)

https://www.bernoulli.com.br/info/praticai/ — correção de redação com IA dentro da "Central Enem" do Bernoulli (o Kuadro cita experiência no Grupo Bernoulli).
- Escreve na plataforma ou sobe arquivo; tema estilo ENEM ou livre; volta em **menos de 2 min** com nota por competência (C1-C5), marcações no texto, feedback, sugestões e plano de treino.
- **Grátis com créditos mensais** (1 crédito por redação); planos pagos não aparecem na página. Avisa que a nota oficial é humana e que é ferramenta de treino.
- Chegou por **anúncio no Instagram/Facebook**; os parâmetros do link mostram teste A/B ("CORRIJA-SUA-REDAÇÃO-COM-IA-EM-MINUTOS"), público 18-24 com interesse em ENEM, objetivo de captar contato (lead). Ou seja: redação corrigida grátis é **isca** pra vender o resto.

Lição pro ENEM GI: corrigir redação com IA virou item básico (Bernoulli grátis, Kuadro ilimitada, Medly não faz). Não é diferencial sozinho. O que ainda pode ser: correção ligada ao **dado real** (o que os 900+ fazem por competência, dos microdados e das cartilhas do INEP em docs/redacao_pesquisa) e mostrar o padrão de erro da pessoa ao longo das redações, não só a nota de uma.

## Referência: UniBF "materiais ENEM grátis" (10/10/2026)

https://inscricao.unibf.com.br/enem — faculdade EaD (diz 100 mil formados, 1.200 cursos, foco em pós acelerada). Anúncio pago no Instagram → cadastro com nome, e-mail e **WhatsApp** → 9 materiais (dicas, revisão, simulado) liberados um por semana até a prova (08/11). Não fala de bolsa, nota ou ingresso: é captação de contato pra vender curso depois.
Padrão que se repete (Bernoulli, Kuadro, UniBF): **material grátis de ENEM como isca + liberação semanal até o dia da prova**. Ideia pro ENEM Pipoco/beta: "1 caderno visual por semana até o ENEM" como série, com contagem regressiva — sem pedir WhatsApp.

## Referência: Reta Final ProEnem (10/10/2026)

https://retafinal.proenem.com.br/ — lives grátis de 26/10 a 15/11 (+30 h): temas que mais caem por matéria resolvidos ao vivo, revisão na véspera de cada dia de prova e gabarito extraoficial comentado no dia. Pede inscrição ("vagas limitadas"). Também anúncio pago no Instagram. Mesmo padrão de isca com data marcada; aqui o formato é **evento ao vivo** em vez de material semanal.

## Referência: "Manual Anti-Atraso Enem 2026" (10/10/2026)

https://manual-anti-atraso.vercel.app/ — infoproduto anônimo (só e-mail de suporte de outro domínio, site em subdomínio grátis da Vercel), anúncio pago no Facebook. **R$ 37** (Pix ou 3x): 400+ resumos de 5 min, mapas mentais, guia de fórmulas, "Rota dos 2 Domingos" (2 blocos por dia, redação no sábado, prova antiga cronometrada no domingo), bônus "Redação +900 com modelos" e "simulados com todas as provas oficiais" (que o INEP dá de graça). Sem nenhuma prova social; contagem regressiva, ancoragem "cursinho custa R$ 500", apelo à ansiedade; garantia de 7 dias. Datas contraditórias na própria página.
Lição: na reta final o que vende é **alívio de ansiedade + roteiro do dia**, não conteúdo. Ponto de preço baixo (R$ 37) funciona com isca de contagem regressiva. O ENEM GI pode oferecer o roteiro diário de graça e com dado real.

## Referência: enemgabarito.online/diagnostico (10/10/2026) — o mais parecido com o ENEM GI até agora

Site não oficial, anônimo (sem CNPJ/responsável), anúncio pago no Instagram. **Diagnóstico grátis, sem cadastro: 25 questões reais em ~25 min** → nota estimada por área (exemplo: geral 612; LC 640, CH 590, CN 610, MT 560), **"faltam 85 pontos pra Enfermagem"** e quais áreas mais derrubam. Depois: plano grátis com **"vidas"** (limite estilo Duolingo) e áreas Plano, Simulado, SiSU, Redação, Desempenho. Preço não aparece.
- Ponto fraco técnico: 25 questões nas 4 áreas dá ~6 por área. Estimar nota TRI com 6 itens tem erro enorme; o número parece preciso, mas não é.
- Ideias pro ENEM GI: (1) **diagnóstico de entrada curto como porta de entrada** (onboarding) — o app já tem os parâmetros TRI oficiais dos itens (`tri_a/b/c`), então dá pra fazer a estimativa direito e **mostrar a margem de erro** ("entre 560 e 640"), o que vira diferencial honesto; (2) **"quanto falta pro seu curso"** usando as notas de corte do SiSU (pesquisa já feita em 21/09 pro objetivo dele); (3) o gancho é a **distância até o curso**, não a nota em si.

## Referência: simulador-enem.lovable.app (10/10/2026)

Simulado ENEM pago, anônimo, feito no **Lovable** (gerador de site por IA, subdomínio grátis), anúncio em **Reels** com campanhas "— Cópia — Cópia" (duplicando anúncio que funcionou). Fluxo: paga → acesso → questão → correção → explicação → resultado. Dois planos ("Simulador" e "Continue treinando"), preço só depois do clique. Prova social = prints de WhatsApp ("20 acertos em 48", "32 acertos e 417 pontos").
Lição: o produto é **o mesmo fluxo que o ENEM GI já tem de graça**, e é vendido. Barreira de entrada pra fazer site virou zero (Lovable/Vercel); o que diferencia é dado (TRI oficial, banco real), método e confiança (quem está por trás, número honesto).

## Ideia: motor que escolhe o formato da explicação (11/10/2026)

Pedido do Gabriel durante o estudo (Q107 nitrosos: o desenho do caminho da comida destravou o que o fato solto não destravou). Hoje quem decide se a explicação vira desenho, roteiro de conta, tabela de eliminação ou glossário sou eu, na hora. A ideia é o app decidir isso sozinho:
- **Filtro de perguntas por questão** (triagem): é processo com ordem/lugar (→ desenho do caminho)? é conta (→ roteiro com passos e dica de conta)? as alternativas se eliminam por função (→ tabela A–E)? o enunciado usa termo que o aluno não conhece (→ glossário antes)?
- **Vizinhos mais próximos (embeddings + busca vetorial, k-NN):** transformar cada questão em vetor e achar as já explicadas mais parecidas; reaproveitar o formato que funcionou nelas (o "parâmetro mais próximo" que ele lembrou).
- **RAG:** na hora de gerar a explicação, buscar no banco os trechos/explicações aprovadas das questões vizinhas e passar pro modelo como contexto, em vez de gerar do zero.
- Sinal de "funcionou": acerto sozinho na variação depois da explicação (já registrado em `tentativas_usuario`). Base inicial: `docs/materiais/` (lote1_desenhado, q101_acustica, q107_nitrosos, cadernos) e `docs/materiais/explicacoes_por_erro.md`.
- Liga com a ideia de "vídeo que explica essa questão" (RAG em transcrições, acima). Fazer **depois do ENEM**; antes, só anotar quais formatos funcionaram em cada questão.
- Teste 11/10 na Q102: 5 ângulos em paralelo + juiz. O crítico ("o que as explicações comuns esquecem") achou a lacuna principal; o juiz pegou erro de analogia (tesoura × juntar). Custo ~125k tokens Sonnet, ~10 s cada. Vale pra montar explicação-modelo de questão difícil, não pra toda questão.

## Ideia: "onde eu perco mais ponto" — erros × dificuldade TRI × matéria (11/10/2026)
Pedido do Gabriel: pegar **todas** as questões que ele já errou (não só o Marco 1), cruzar o `tri_b` dos microdados (quanto menor, mais gente acertou → errar custa mais ponto e quebra a coerência TRI) com matéria/tópico e com a incidência no corpus, e ranquear o que aprofundar. Score sugerido por tópico: Σ(erros com b baixo) × incidência/ano × (1 se falta base / 0,5 se foi descuido). Coluna extra "pré-requisito" (ex.: Q94 travou por falta de ácido-base). Já foi feito à mão pro reestudo 2024 (lotes por b); generalizar pra todas as tentativas. Bom candidato a painel Tableau (rotina Python+Tableau) e a tela "o que estudar" no app.

## Ideia: prova em ordem de dificuldade + lista por conteúdo (13/10/2026)
Pedido do Gabriel em duas partes:
1. **Ordenar as questões de uma prova pelo `tri_b`, da mais fácil pra mais difícil.** Serve pra treinar juntando acerto rápido, pra corrigir a prova começando pelas fáceis erradas e pra mostrar no app "esta foi a 17ª mais difícil de 45". Os dados já existem (`questoes.tri_b`).
2. **Errou por falta de conteúdo → lista personalizada daquele conteúdo**, com questões REAIS inéditas do assunto em ordem de `tri_b`, depois do kit e das variações inventadas. Exemplo de logaritmo (13/10): 2019_154, 2019_137, 2020_149, 2023_152. A origem é uma dica de vídeo do TikTok (o vídeo era recente demais e não tinha transcrição).
Hoje eu faço isso à mão no chat. No app, viraria um botão "treinar este conteúdo" na tela de correção.

### Extensão (15/10/2026): desenho `Desktop/Lista_Exercicio_App.excalidraw`
Ele desenhou o fluxo completo da ideia acima, e hoje foi o fluxo que deu certo no estudo (log 5/6, escala, parcelas):
- **Banco novo = ranking por assunto:** todas as questões de um assunto, da mais fácil pra mais difícil (`tri_b`), além da ordem por prova.
- **Errou a mais fácil → gera variações daquele tipo** pra repetir (é o `core/moldes.py`, que hoje tem só 4 moldes: carro elétrico, aquário, frenagem, pedágio).
- **Cada questão real ganha as suas variações**, então a lista fica muito maior que o banco.
- **Mira no erro recorrente** ("faz a questão que te faz errar um padrão"): dá pra usar `tentativas_usuario.tipo_erro` + tópico.
- **Lacunas pra virar feature:** (1) `topico` é NULL nas 177 de MT 2019-2022, então o ranking por assunto precisa classificar essas antes; (2) variação gerada precisa da resposta CALCULADA por código (molde), nunca só por LLM; (3) as páginas HTML que eu faço no chat (q170_logaritmo, treino_escala_area_volume) são o protótipo da tela.
- Quando: depois de 15/11. Até lá eu monto as listas à mão (docs/materiais/listas_focadas.md).

### Fonte visível em toda questão (15/10/2026)
Em lista misturada (por assunto, revisão, variações), **toda questão mostra de onde vem**: "ENEM 2018 · 2º dia · azul · Q153" e, se for variação, "variação da ENEM 2018 Q153". Motivo (relato dele): no ProEnem, mesmo filtrando por ENEM, as questões não mostravam ano/prova e ele não sabia se treinava com prova real, o que fazia o estudo parecer ineficaz. É dado que o banco já tem (`ano`, `caderno`, `numero_questao`, `origem`, `fonte`); conferir se todas as telas mostram.

### Diagnóstico mais fundo do erro (15/10/2026)
Pedido dele: rastrear se o erro é falta de conteúdo ou outra coisa. Hoje o app tem 3 tipos (`TIPOS_ERRO`: conta, pegadinha, conteúdo). Proposta, testada primeiro no `registro_questoes.csv`: (1) **confiança na hora de marcar** (1 chute, 2 dúvida, 3 certeza), porque certeza + erro = conceito errado fixado e acerto com confiança 1 = chute que não pode contar como sabido; (2) mais 3 tipos: **vocabulário** (não entendeu palavra do enunciado, comum em bio), **método** (sabia o conteúdo, não soube montar: ex. 2018_153) e **tempo/chute**; (3) pergunta-sonda nos erros de conteúdo ("já viu X?"), separando "nunca viu" de "viu e não lembrou". Painel depois: tipo de erro × tema × b.

### Usuário beta nº 3 (15/10/2026), do grupo de programação
Objetivo: **ProUni** em Engenharia de Software na Cruzeiro do Sul (plano B: pagar a FIAP). Pendente perguntar: matéria que mais erra, celular ou PC, se já fez simulado. Implicação pro app: nota ProUni = média simples das 5 áreas (redação pesa 1/5), então o perfil dele pede redação + base ampla, diferente do perfil "MT peso 4" do Gabriel. Prometido a ele: correção de redação "por lá" (conferir o que o app entrega hoje antes de liberar).

### Recrutar usuários beta na reta final (15/10/2026)
Insight dele: a reta final é o melhor momento pra achar usuário (todo mundo estudando agora). Canais: grupos (programação, ENEM), TikTok com vídeos normais do próprio estudo, e DM pra quem interagir ("quer me ajudar a testar?"). Vira história (build in public). Cuidados combinados: teto de usuários que dá pra atender (cada um exige código + suporte); prometer só o que o app entrega (beta, grátis, sem garantia de nota); coletar o mínimo de dado pessoal; tempo de projeto fora do bloco de estudo (hora das ideias). Medir: usuários, quem voltou no dia seguinte e na semana, questões respondidas por usuário.

### Painel de admin de uso (15/10/2026) — próximo PR pequeno
Ele mandou o link pro beta 3 e perguntou "como sei que ele acessou?". Hoje o app guarda por usuário só o que ele faz (tentativas com data/hora/duração, revisão, relatos), num banco próprio em /data/bancos/<nome>.db; não há registro de acesso nem tela pra ver. Proposta: endpoint protegido por token de admin (`/admin/uso`) que lê os bancos e devolve por usuário: 1ª e última atividade, nº de questões, % de acerto, voltou no dia seguinte (D1) e na semana (D7); + tela simples. Sem guardar dado novo (nada de IP/aparelho). Junto: 1 linha no app dizendo o que é guardado (LGPD/confiança).


## Ideias de 20/10/2026 (vídeos de Instagram sobre IA, produto e marketing)

Origem: 9 vídeos que o Gabriel mandou (transcrição colada), guardados com tags em `Desktop/ideias/inbox_videos/`. Os números
e nomes de ferramenta vêm dos autores dos vídeos, sem prova no post. Prioridade combinada: ENEM (15/11) primeiro, poucos PRs,
sem ferramenta nova paga.

**Já feito em 20/10:**
- Política de privacidade e termos de uso em `core/legal/` (servidos em `/legal/privacidade.html` e `/legal/termos.html`,
  sem token, como os enunciados), link no rodapé do Perfil e teste em `test_api.py`. Contato LGPD preenchido com o e-mail dele
  (PR #59, 25/10).
- `docs/estilo.md`: regras de cor, contraste medido, tipografia, espaçamento, animação em ms e o que evitar, tiradas do
  `brand.ts`. Achado: `textoApagado` (3,3:1) e `textoMuted` (2,5:1) reprovam AA para texto; o aviso de privacidade do Perfil foi
  movido para `textoSuave` (5,2:1). Falta revisar onde mais esses dois tokens são usados para texto.

**Fazer depois do ENEM, nesta ordem:**
1. **Exclusão de dados (LGPD):** rota/botão "Excluir meus dados" que apaga tentativas, eventos, relatos e pesquisa do banco da
   pessoa. Hoje a política manda pedir por contato. Destrutivo: precisa confirmação dupla.
2. **Idade/menor de idade:** muitos usuários têm 16 a 17 anos. Decidir se pede ano de nascimento ou só mantém o aviso.
3. **Funil e retenção com os eventos que já existem** (vídeos Duolingo e SaaS): visita → primeira questão → volta no dia 3 e no
   dia 7; coortes por dia de primeira visita. Serve de exercício de SQL/Tableau para o portfólio. Sem rastrear localização nem Wi-Fi.
4. **Acessibilidade:** `accessibilityLabel` nos ícones, texto alternativo nas figuras das questões, teste só com teclado.
5. **Banner de cookies:** só se entrar analytics com cookie. Hoje o app usa só o código no armazenamento local.
6. **Teste ponta a ponta no navegador (Playwright)** nas telas principais, quando o app estiver estável.
7. **Pontos de contato:** mensagem de boas-vindas e canal claro de feedback (o NPS já existe).

**Só observar / não fazer agora:** rastrear rede ou localização (LGPD, menores), OpenSpec, painel de agentes, instalar skills de
terceiros sem ler o conteúdo inteiro, entrar em lista de espera de efeitos de vídeo.

**Conteúdo do canal (não é do app):** técnica "hook repetido 3 vezes + revelação do produto no fim", série "dia N" com meta
pública, efeitos Phone Mockup / Chart Grow / Pull Back Reveal, desafio de ganhar dinheiro depois do ENEM (orçamento e prazo
fixos, números reais). Detalhe em `Desktop/ideias/inbox_videos/`.

- **Gerador de escada de memorização (23/10/2026):** o aluno monta o próprio modelo de redação (introdução, D1, D2, conclusão) e o app gera o jogo de escrever do zero em fases (palavra-chave → frase → frases juntas), com cola que não conta acerto e registro de tentativas/erros/tempo. Protótipo do D1: https://claude.ai/artifact/4HErs8yvAhY72ZyJ1qGoEw. Ideia do Gabriel; fazer depois de 15/11.
