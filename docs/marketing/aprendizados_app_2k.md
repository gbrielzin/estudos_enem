# Aprendizados: "How I built an app that makes $2,000 in one month" (13/10/2026)

Fonte: vídeo de ~64 min do Arthur (20 anos, 4º ano de ciência da computação). Ele constrói e lança um app iOS de frases motivacionais ("Glow", vela mascote) com Expo, em 57 dias, e acompanha o funil dia a dia. **Os números são ele falando de si** (US$ 2,8 mil de receita em 28 dias, lucro acima de US$ 2 mil, ajudado por cerca de US$ 360 de crédito grátis de anúncio); não conferi. Ele também vende comunidade/curso (Discord), então há interesse em mostrar o caminho como fácil.

Ligado a: [aprendizados_funil.md](aprendizados_funil.md), [reta_final.md](reta_final.md), [../workflow_ia_design.md](../workflow_ia_design.md).

## O que o app dele tem de útil pro ENEM GI (e o que mostra do funil)

### 1. Quase todo o dinheiro está no onboarding
Ele diz que mais de 80% das conversões acontecem ali e que gastou ~90% do tempo nele. O que mexeu no número:

| Mudança | Efeito que ele mediu |
|---|---|
| Barra de progresso no topo | conclusão do onboarding de 74% para 83% (com outras mudanças junto) |
| Tirar 1 tela específica (teste A/B) | foi a melhor variante |
| Tirar 3 perguntas pessoais | **derrubou a conversão**. Pergunta pessoal ajudava |
| Tela de "compromisso" (segurar o dedo) antes do preço | ajuda, segundo artigo que ele seguiu |
| Mostrar **uma informação por tela** no paywall | o usuário não lê bloco grande |
| Período de carência da cobrança ligado (3 dias) | ~10% da receita dele |

Lição geral: **mudança pequena muda muito, então mede antes de decidir.** Tirar tela "porque parece demais" pode piorar.

### 2. A métrica que manda é retenção
Dia 2: só 15% voltaram. Ele passou a codar só duas coisas: pedido de usuário e as métricas (retenção, conversão, perfil dos usuários). Retenção primeiro, porque quem volta todo dia converte sem esforço.

### 3. Audiência certa para o produto certo
Dois shorts no canal de programação: 20 mil visualizações, ~300 cliques, **10 downloads**. O público dele era de desenvolvedores, que não procuram app de afirmações. O canal de Reddit com oferta honesta ("tá grátis por enquanto, quer testar?") trouxe mais.

Para o Gabriel isso pesa direto no mapa Núcleo e Galhos: **conteúdo de "dev de 18 anos construindo" (galho 3) não traz aluno de ENEM.** Aluno vem de conteúdo de estudo (galho 1). O galho 3 serve pra estágio e rede, não pra usuário.

### 4. Orgânico é loteria, então teste gancho
15 vídeos no TikTok, 2 passaram de 2 mil visualizações, 2 testes iniciados e os dois cancelaram. A regra dele: mudar **só o começo** do vídeo e ver qual segura mais; fazer 10 a 20 peças e postar 2-3 por dia pra ver o que pega. Três formatos que ele usa:
1. **POV** ("POV: você finalmente achou…"): fácil e funciona quando você conhece a dor do público.
2. **Demo**: o app em uso.
3. **Resultado/transformação**: "usei 3 semanas, olha o que mudou".

### 5. Anúncio pago só depois de o funil funcionar
Primeiros dias de anúncio: ~100 downloads por dia, 10 testes iniciados, ninguém pagou, perdeu quase tudo que gastou. Só depois de refazer o onboarding o mesmo anúncio deu lucro. Pro ENEM GI isso reforça: sem anúncio (menor de idade) e sem pressa de tráfego antes de o funil existir.

### 6. Privacidade: a Apple rejeitou o app por um checkbox
Ele marcou "usa dados pra rastreamento" em tudo, sem ler, e a política dizia o contrário. Rejeição de 5 dias. **Política de privacidade e termos são obrigatórios.** Ele gerou com ChatGPT e diz que contrataria advogado se crescer. Pro ENEM GI, com menor de idade e LGPD, isso não pode ser improvisado.

### 7. Outros detalhes
- Guardar tudo **no aparelho, sem login** deixou o app mais simples e funcionando offline. O ENEM GI hoje tem API própria, então a decisão é outra; vale lembrar que menos dado coletado = menos obrigação.
- O recurso mais pedido foi **modo escuro** (20+ mensagens). Pedido repetido de usuário é backlog confiável.
- **Responder avaliação ruim** com educação: quem lê é o próximo usuário, não o autor.
- Avaliação de 1 estrela por "não consegui comprar premium" porque o app estava grátis: expectativa mal explicada vira nota baixa.
- Dar **acesso grátis vitalício** gerou 600 resgates, mas número inflado não é conversão.
- Uma matéria sobre o app no **blog do Expo** veio de um post no subreddit deles: comunidade da tecnologia que você usa pode divulgar. (Serve pro galho 3, estágio e rede.)
- Ele montou um painel com Claude Code pra ver receita por instalação e **em que tela cada usuário sai** do onboarding.

## O que adotar

| # | Ação | Esforço | Quando | Status |
|---|---|---|---|---|
| F1 | Escrever o onboarding do ENEM GI como o diagnóstico de 5-8 perguntas, com **barra de progresso** e uma ideia por tela | médio | antes de abrir cadastro | 💡 |
| F2 | Medir **tela a tela** onde o usuário sai do diagnóstico (evento mínimo, sem dado pessoal) | médio | com F1 | 💡 |
| F3 | Medir **retenção no dia 2 e no dia 7** quando houver usuário real (hoje: amigo do beta) | pequeno | agora, na mão | 💡 |
| F4 | Vídeos: **testar 2-3 ganchos do mesmo vídeo** em vez de refazer o vídeo | pequeno | já nos V0/E1/E5 | 💡 |
| F5 | Usar os 3 formatos: POV (dor), demo (simulado corrigindo), resultado (progresso do Gabriel) | pequeno | calendário da reta final | 💡 |
| F6 | Política de privacidade e termos revisados (menor de idade, LGPD) antes de abrir cadastro | grande | antes de divulgar link | 💡 |
| F7 | Backlog por pedido de usuário: perguntar a cada tester e anotar o que se repete | pequeno | contínuo | 💡 |
| A11 | Tocar no Pipo faz ele reagir (pula, põe óculos) | pequeno | junto com A7/A8 | 💡 |

## O que não adotar

| Ideia dele | Por quê |
|---|---|
| Anúncio pago no TikTok | público menor de idade e funil ainda não existe |
| Assinatura mensal/anual com teste grátis de 3 dias | cobrança de menor precisa de responsável; produto ainda sem modelo de preço decidido |
| Notificação como recurso central e tela pedindo permissão | o ENEM GI não depende disso agora |
| Widgets em Swift, EAS Build, conta Apple | publicação em loja é decisão futura |
| Ferramentas citadas (RevenueCat, PostHog, Supabase, ferramentas de palavra-chave de loja, Jitter, Linktree) | nenhuma está no projeto e nenhuma é necessária agora. PostHog (análise de uso e teste A/B) é a única que pode virar candidata **depois da LGPD**, porque coleta dado de comportamento |
| Pagar criador por vídeo (US$ 20) | sem orçamento e sem funil pra receber |
| Escrever a política de privacidade só com ChatGPT | produto com menor de idade pede revisão de quem entende |
