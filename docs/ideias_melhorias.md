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

**Ponto de partida:** a coleta manual de 25/09 — script e amostra salvos fora do repo em `Desktop/radar_estagios_rascunho/` (`coleta_gupy.py`, `amostra_2026-09-25.json`, 104 estágios de TI).

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
