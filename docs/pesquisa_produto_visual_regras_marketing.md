# Pesquisa de produto: visual, regra de negócio e marketing (2026-09-25)

Pedido do Gabriel no almoço de 25/09: analisar impacto visual, regra de
negócio e já pensar em marketing. **Nada aqui está decidido.** É entrada pra
sessão de projeto, junto com [ideias_melhorias.md](ideias_melhorias.md) e
[metodo_e_aprendizados.md](metodo_e_aprendizados.md).

Limite honesto: a evidência "de dentro" é **1 aluno em 4 dias** de sessão
guiada. A evidência "de fora" é pesquisa publicada sobre aprendizagem e
notícia de mercado. Onde as duas batem, a recomendação é mais forte.

---

## 0. Resumo em 5 linhas

1. **Posicionamento:** não é "Duolingo do ENEM" (o MEC já faz isso de graça, com 1 mi+ de usuários). É **"o app que descobre o *seu* erro e te faz repetir até sair sozinho"**.
2. **Visual:** manter a identidade (paleta, trilha, mascote) e trocar **o que a tela celebra**: sair sozinho, armadilha evitada, branco que virou acerto. Sem vidas.
3. **Regra central:** errou → kit → molde sozinho → original volta espaçada. Resolveu com ajuda = não conta como acerto.
4. **Marketing:** custo zero, orgânico, **o próprio Gabriel como caso** (build in public + "de 560 pra 700 em Natureza"), TikTok/Reels com "a armadilha da semana".
5. **Antes de divulgar:** autenticação real na API e LGPD (público tem menor de idade).

---

## 1. Mercado e concorrência

| Dado | Valor | Fonte |
|---|---|---|
| Inscritos confirmados ENEM 2026 | 5 055 818 (+5% vs 2025) | MEC, via Jornal de Brasília |
| Provas 2026 | 8 e 15 de novembro | idem |
| App MEC Enem | 1 mi+ usuários; trilhas por complexidade, simulado com questão real, IA que monta cronograma e corrige redação em ~60 s; grátis, login gov.br | Bizu/TechTudo |
| Descomplica (pago) | ~R$ 40-55/mês (6 a 18 meses); Matemática ou Redação isolada a partir de 18x R$ 29,90 | Descomplica |

**Leitura:**
- Trilha + gamificação + simulado + IA de redação **já é commodity grátis**. Competir nisso é perder.
- Os cursinhos vendem **aula** (conteúdo). Ninguém, pelo que as descrições mostram, vende **diagnóstico do erro + repetição parametrizada**.
- Brecha real: o aluno que **já viu o conteúdo** (aula, TikTok, cursinho) e mesmo assim erra na prova. É o caso do Gabriel na Matemática: a base existe, derrubam 3 desvios repetidos.

---

## 2. Impacto visual

### 2.1 O que a pesquisa diz sobre gamificação
- Gamificação em educação tem efeito positivo médio em aprendizagem, motivação e comportamento (meta-análise Sailer & Homner, 2020), mas o efeito depende **de qual elemento** e **de como** é usado.
- **Streak** é a mecânica de retenção mais forte do Duolingo (relatos de retenção D1 de 12% → 55%), e funciona por **aversão à perda**. Classificada como técnica "black hat": prende, mas com ansiedade.
- **Vidas/corações** interrompem a prática justamente depois do erro, que no nosso método é o diagnóstico. Decisão do Gabriel (25/09): **sem vidas**.

### 2.2 Recomendações visuais (em ordem de impacto)

| # | Mudança | Por quê |
|---|---|---|
| 1 | **Card de kit** antes do exercício (fórmula + "quando usar" + apelido) | Worked examples em Matemática: g ≈ 0,48 (meta-análise 2023). O kit é a versão curta disso. Apelido é diferencial visível. |
| 2 | **Feedback da armadilha** no erro ("você caiu no *passo pela metade*") com botão "tentar outra variação sozinho" | Feedback elaborado > certo/errado (Wisniewski et al., 2020). Distrator de ENEM é montado sobre erro comum, então dá pra nomear o erro. `moldes.py` já tem isso; a tela de moldes já mostra. |
| 3 | **Passo a passo que some aos poucos** (faded example): 1ª variação com todos os passos, 2ª com o último em branco, 3ª sem nenhum | Pesquisa de faded worked examples: adapta o apoio ao ganho do aluno. É exatamente o que o tutor fez à mão (escala: 5/6 passos sozinho). |
| 4 | **Celebrações novas:** "saiu sozinho", "branco virou acerto", "armadilha evitada", "original confirmada após N dias" | Muda o que o visual premia sem mudar a identidade. |
| 5 | **Tela de questão pra enunciado longo:** rolagem, imagem ampliável, alternativas fixas embaixo | ENEM real tem texto longo, tabela e gráfico. |
| 6 | **Cronômetro discreto por questão** + referência de 3 min | Pedido do Gabriel. `registrar_tentativa` já aceita `duracao_segundos`. |
| 7 | **"Seus 3 desvios"** no perfil (contagem por tipo de armadilha) | O que mais ajudou hoje foi nomear o padrão (conferir alternativas, ler decimal, área x volume). |

**Streak: manter, mas com freio.** Proposta: streak conta **dia com pelo menos 1 "saiu sozinho"** (não só abrir o app), e tem "congelar" grátis pra 1 dia. Aproveita a retenção sem premiar o clique vazio.

---

## 3. Regras de negócio

### 3.1 Regras já validadas nas sessões (candidatas a regra do produto)

| Regra | Evidência interna | Evidência externa |
|---|---|---|
| **Resolveu com ajuda = erro** no Leitner | Regra do próprio aluno; "entendeu na explicação" ≠ fixou | Efeito de testagem exige recuperação sem apoio |
| **Errou → kit → molde sozinho → original volta espaçada** | 3 de 4 originais saíram sozinhas no dia seguinte (24/09); velas em 2 min após o kit (25/09) | Worked examples g ≈ 0,48; espaçamento em Matemática g ≈ 0,28 (Murray et al., 2025) |
| **Vertical no dia do conteúdo novo, misturado na revisão** | Escolha de fórmula 1/4 → 6/6 com mistura (23-24/09) | Interleaving ajuda a *reconhecer* qual método usar |
| **8-12 questões por tema por dia**, não o pool inteiro | Pool de razão e proporção tem ~37 questões com texto; gastar tudo mata a revisão inédita | — (decisão de produto) |
| **Resultado fora das alternativas → reler as 5 e refazer**, nunca ajustar | 2 vezes em 2 dias (93 → 930; 0,09 → 0,9) | Distrator ×10 é erro comum desenhado de propósito |
| **Diagnóstico antes do conteúdo**, "não sei" é resposta válida | Achou lacunas que o dado agregado não mostrava (1 dm³ = 1000 cm³) | — |

### 3.2 Decisões em aberto (só o Gabriel decide)

1. **O que substitui as vidas?** Proposta: errou → abre o kit → variação obrigatória antes de seguir (dá peso ao erro sem travar).
2. **~630 revisões antigas de agosto:** entram na fila, zeram, ou viram fila separada "simulado".
3. **Trilha ROI** (`filosofia.md`): ordem por peso do curso-alvo?
4. **Modelo de receita** (ver 4.4).

### 3.3 Riscos de regra
- **Molde mal calibrado ensina errado.** Toda variação precisa de teste automático (o `/code-review` rodou 20 000 sorteios por molde; manter isso como padrão).
- **Enunciado do banco com erro** (ex.: 2021_azul_165 diz "10 km" e o gabarito só fecha com 20 km). Botão "reportar" já existe; precisa de fila de revisão.
- **Uso de 2024/2025 azul** reservado pra simulado; o app deveria respeitar essa reserva por configuração.

---

## 4. Marketing

### 4.1 Posicionamento (uma frase)
> **"Você já viu a matéria. O app descobre onde você erra e te faz repetir até sair sozinho."**

Contra quem: contra a sensação de "estudei e errei igual". Não contra o MEC (grátis, trilha) nem contra cursinho (aula).

### 4.2 Público inicial
- Quem vai **refazer** o ENEM ou está no 3º ano, já viu conteúdo, mira curso com peso alto em Matemática.
- Canal de chegada: TikTok/Reels (2/3 dos 100 mi+ usuários brasileiros do TikTok têm 18-34 anos; studytok é gênero consolidado no ENEM).

### 4.3 Estratégia de conteúdo (custo zero)

| Formato | Exemplo concreto (já temos o material) | Canal |
|---|---|---|
| **"A armadilha da semana"** (30-45 s) | "Dobrou o diâmetro, quantas vezes mais massa? 90% responde 4. É 8." (docinhos 2022_azul_178) | TikTok, Reels, Shorts |
| **Apelido que gruda** | "Que macete" (Q = mcΔT), "Você Ri", "É Pt", "caixa de leite" (1 L = 1000 cm³) | TikTok, carrossel |
| **Build in public** | "Tô estudando pro ENEM e construindo o app que uso. Dia 12: descobri que meu erro não era conta" | LinkedIn (carreira) + TikTok (alunos) |
| **Caso real com número** | "Natureza: estimativa ~560 → meta 700 em 50 dias", atualizado a cada simulado | LinkedIn, TikTok |
| **Antes/depois do molde** | Tela: questão original em branco → 3 variações → original certa sozinho | Reels |

**Por que build in public funciona aqui:** o Gabriel é, ao mesmo tempo, o usuário, o desenvolvedor e a prova de conceito. Isso também serve à busca de estágio (vaga de dados): o LinkedIn mostra produto, dado e decisão (ADRs).

### 4.4 Receita (quando fizer sentido; não agora)
- **Fase 1 (até o ENEM 2026):** grátis, 20-50 alunos beta, só pra validar se o ciclo kit → molde funciona em mais de 1 pessoa. Métrica: % de "original que saiu sozinha na revisão".
- **Fase 2:** freemium. Grátis: questões e revisão. Pago: moldes ilimitados + diagnóstico de desvios. Âncora de preço: bem abaixo do Descomplica (R$ 40-55/mês); algo como R$ 9,90-14,90/mês.
- **Alternativa B2B:** licença pra cursinho popular ou escola pública (professor vê os desvios da turma).

### 4.5 Métricas que importam (não vaidade)
1. **Taxa de "saiu sozinho"** na 2ª variação do molde.
2. **Original confirmada** na revisão espaçada (D+1, D+3, D+7).
3. **Retenção D7** dos beta.
4. **Nota de simulado** antes/depois (Marco 1 ~05/10), com o aviso de que é n pequeno.

---

## 5. Pré-requisitos antes de divulgar (bloqueantes)

1. **Autenticação real na API.** Hoje, sem `API_AUTH_TOKEN`, a API aceita chamada sem senha (verificado no /run de 25/09); CORS `*`; Admin do Streamlit sem senha.
2. **LGPD:** aluno de ENEM pode ser menor de 18. Dado de desempenho é dado pessoal. Precisa de política de privacidade, consentimento e mínimo de dado coletado.
3. **Direitos das questões:** as questões e imagens do INEP são públicas, mas vale citar a fonte na tela.
4. **Hospedagem fora da rede de casa** (hoje o celular só alcança a API na mesma wifi).

---

## 6. Próximos passos sugeridos (ordem)

1. Sessão de projeto: decidir 3.2 (vidas, fila antiga, trilha ROI).
2. Implementar o **molde de fator de escala** (linha × área × volume), que derrubou 3 questões reais.
3. Cronômetro por questão na tela.
4. Card de kit + feedback da armadilha nas questões oficiais (hoje só nos moldes).
5. Segurança (seção 5), **antes** de qualquer divulgação.
6. Primeiro vídeo "armadilha da semana" com o docinho: testar formato sem ainda divulgar o app.

---

## Fontes

- MEC/INEP: Enem 2026, 5 055 818 inscritos confirmados — https://jornaldebrasilia.com.br/noticias/concursos-e-carreiras/enem-2026-tem-mais-de-5-milhoes-de-inscritos-confirmados/
- App MEC Enem (1 mi+ usuários, IA de redação) — https://blog.bizu.com.br/estudantes-do-enem-ganham-app-do-mec-com-simulados-e-correcao-de-redacao-por-ia-em-ate-60-segundos/ e https://www.techtudo.com.br/guia/2026/09/mec-enem-veja-como-funciona-o-app-seus-simulados-e-redacoes-para-a-prova-edapps.ghtml
- Descomplica, planos Enem 2026 — https://descomplica.com.br/vestibulares/enem/
- Meta-análise worked examples em Matemática (g ≈ 0,48) — https://link.springer.com/article/10.1007/s10648-023-09745-1
- Faded worked examples em jogo de Matemática — https://www.sciencedirect.com/science/article/abs/pii/S0959475216302316
- Sailer & Homner (2020), meta-análise de gamificação em aprendizagem — https://link.springer.com/article/10.1007/s10648-019-09498-w
- Streak do Duolingo e aversão à perda — https://yukaichou.com/gamification-study/master-the-art-of-streak-design-for-short-term-engagement-and-long-term-success/ e https://www.strivecloud.io/blog/gamification-examples-boost-user-retention-duolingo
- Distratores ligados a erro comum — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.00825/full
- Studytok e ENEM — https://blog.bizu.com.br/dicas-de-tiktok-ajudam-no-enem-conheca-5-studytoks-que-realmente-fazem-diferenca/
- Perfil do TikTok no Brasil — https://www.shopify.com/br/blog/tiktok-brasil
- Build in public com Gen Z — https://thedigitalnative.substack.com/p/2-building-in-public-and-tiktok-for
- Murray et al. (2025), espaçamento em Matemática, e Wisniewski et al. (2020), feedback: ver Fontes de [ideias_melhorias.md](ideias_melhorias.md)
