# Workflow de design com IA: o que copiar da live do PC (2026-10-13)

Fonte: live "Criando produto e ouvindo funk sujo" do PC (Acelera Dev),
~3 h, transcrição lida inteira em 13/10. Ele constrói o **Money Flow**
(controle de gastos por áudio no Telegram) e passa a live fazendo a
landing page e o redesign do dashboard com Claude. No fim, react de
vídeos do Marc Lou.

Nomes de ferramenta como ele fala na live; **não conferi cada uma**.
Antes de instalar qualquer coisa, abrir o site e ver preço e se roda no
nosso setup.

---

## 1. Ferramentas que ele usa

| Ferramenta | Pra quê | Equivalente que já temos |
|---|---|---|
| **Paper** (paper.design) + MCP do Claude | Canvas de design: o Claude cria telas, variações e imagens. Ele usa no lugar do Figma | Claude Design (já usamos: `design_handoff_enem_gamificado/`) |
| **Orca** | Orquestra vários chats/agentes em paralelo, cada um numa worktree/branch | Claude Code com subagentes e worktree |
| **Fluid Voice** | Ditado: aperta uma tecla, fala, o prompt sai escrito. Fez a live quase sem mouse | ditado do sistema (Win+H no Windows) |
| **Vercel Agent Browser** | O agente abre o front no navegador e confere com o design gastando pouco token | Playwright (já instalado no ambiente de nuvem) |

## 2. O processo dele, em ordem

1. **Briefing + 2 referências + "lê meu código e entende o produto"** antes de desenhar.
2. **Hero primeiro.** A primeira dobra define tipografia, estilo e componentes; as outras seções herdam. (Aprendizado que ele trouxe do Samuel Rison.)
3. **Variações em lote:** "3 variações trocando só o amarelo". Escolhe, descarta, pede de novo.
4. **Design aprovado vira issue** ("cria uma issue pra essa mudança") e **outro chat executa**.
5. **Verificação visual:** o agente sobe o front, abre no navegador e **compara com o frame do design**.
6. **Agente pra coisa que não é código**, em paralelo. Prompt do agente de copy: *"você é copywriter sênior… **antes de escrever, leia o código**"*. A copy só promete o que existe.
7. **Protótipo antes do código:** a landing nasceu como um HTML de ~1.700 linhas num Artifact do Claude e só depois foi pro repositório.
8. **Pesquisa com o público na hora:** "você pagaria?", "o que te faria não confiar?", "Telegram ou WhatsApp?".

## 3. O que adotar no ENEM GI

Status: 💡 a fazer · 🟡 em andamento · ✅ feito

| # | Mudança | Por quê | Status |
|---|---|---|---|
| W1 | **Hero primeiro** na landing de captação (diagnóstico grátis → cadastro) | define o estilo de tudo; é o que a pessoa vê vindo do TikTok | 💡 |
| W2 | **Toda mudança visual vira issue antes do PR** (print do design anexado na issue) | já é quase o nosso fluxo; falta o print do design como critério de pronto | 💡 |
| W3 | **Verificação visual com Playwright** antes do PR de tela: subir `npm run web`, tirar print, comparar com o design | hoje o PR de tela é testado por tsc + jest, que não veem layout | 💡 |
| W4 | **Agente de copy que lê o código** pra textos da landing e roteiros | evita prometer recurso que não existe (ver regra em `marketing/README.md`) | 💡 |
| W5 | **Ditado por voz** pra prompts longos | o Gabriel já pensa falando (áudios longos nas sessões) | 💡 |
| W6 | **Variações em lote** ao pedir design (sempre 3) | escolher entre 3 é mais rápido que corrigir 1 | 💡 |
| W7 | **Animações do placar e da tela de resultado** (seção 4) | é o "número de cassino" da live | 🟡 (A1 feito) |

**Não copiar agora:** plano Max (ele estourou o Pro em 3 h rodando
vários agentes de imagem ao mesmo tempo e assinou ao vivo por ~€106/mês;
pra nós, 1 agente por vez basta) e animação pela animação (ele mesmo
achou o cadeado 3D "esquisito"; o que vende é a frase do hero).

## 4. Animações: o que ele fez e o que serve pro app

O app já tem gramática de animação (design TURNO 6): botão afunda,
barra enche, acerto estufa, erro treme, XP sobe, lição destrava. A live
acrescenta:

| # | Animação da live | No ENEM GI | Status |
|---|---|---|---|
| A1 | Saldo "rolando igual número de cassino" | **Placar do simulado** (acertos e nota TRI) contando de 0 até o valor (`components/numero-sobe.tsx`) | ✅ 13/10 (falta ver rodando no celular) |
| A2 | Gráfico crescendo devagar no scroll | Barras por matéria no resultado do simulado enchendo uma depois da outra (reusar `BarraProgresso` com atraso escalonado) | 💡 |
| A3 | Cards entrando conforme o scroll | Cards "O que você errou" entrando em cascata (60 ms entre um e outro) | 💡 |
| A4 | Loading suave no dashboard | Skeleton no lugar do `ActivityIndicator` enquanto a API responde | 💡 |
| A5 | Celular 3D cortado pela metade pra induzir scroll | Só na **landing** (não no app): print do app num celular inclinado aparecendo pela metade | 💡 |
| A6 | Fundo topográfico / textura | Landing: fundo discreto; no app, não | 💡 |

Regra pra todas: respeitar "reduzir movimento" do aparelho
(`AccessibilityInfo.isReduceMotionEnabled`) e nunca atrasar o aluno:
animação acaba em menos de 1 s e não bloqueia toque.

## 5. Do react do Marc Lou (fim da live)

- **Ship or die:** "você está a duas semanas de lançar há 4 meses. Polir em privado não é progresso."
- **Taxa de acerto de 5-10%:** 90% do que ele lança não pega. Desistir rápido do que não pega compra tempo pra mais apostas.
- **Surfar tendência:** ver alguém reclamando de um problema e construir a solução no mesmo dia.
- **Fosso contra a IA:** o que a IA não copia é confiança (marketplace, comunidade). Pra nós: a história do Gabriel e os usuários reais.

## 6. Outras coisas da live

- **"Mentor prompt"** (repo público do PC): prompt que nunca dá a resposta pronta e desafia cada decisão. Mesma linha do método das sessões de estudo; vale ler pra comparar com a skill `/estudo`.
- **Validação antes de lançar:** ele perguntou à audiência se pagaria e o que faria desconfiar. Fazer o mesmo com os usuários do beta.

---

## 7. Segundo vídeo (13/10): app animado "estilo Finch" com Claude

Fonte: "Watch Me Vibe Code an Animated App…" (24 min, transcrição lida inteira). O criador recria o Finch (app de autocuidado com um bichinho que reage) com um jacaré chamado Chewy: React Native + Expo, imagens e vídeos curtos gerados por IA via conector no Claude. Ele diz que o Finch fatura US$ 1 mi/mês; é alegação dele, não conferi.

### Processo dele

1. **Contexto antes do prompt:** imagem do personagem + **gravação de tela do app de referência** numa pasta, e o link da loja pra ler descrição e avaliações (avaliação mostra o recurso que o povo pede).
2. **Primeiro prompt é de plano**, não de construção: "quebra as funcionalidades e as telas, quero planejar antes de construir".
3. **Níveis:** (1) telas principais, (2) onboarding completo com paywall, (3) animar tudo. Depois, como ligar no celular.
4. **Prompt falado** (ditado), não digitado.
5. **Protótipo no navegador dentro de moldura de celular** antes do app de verdade.
6. **Correção por print** ("tira o contorno", "imagem quebrada aqui") e, pra muita coisa, **vídeo gravado com voz e mouse** comentando tela por tela, que ele diz ser mais rápido que anotar print.
7. **Enquanto a IA gera as animações, o agente (parado) monta o back end.** Tempo de espera não fica ocioso.
8. **Animação pronta (Lottie):** baixa de um site de animações gratuitas, troca a cor pra combinar com o tema e pede "aparece no centro quando completar a meta".
9. **Preview no celular de verdade** (EAS Build, exige conta de desenvolvedor Apple, ~US$ 99/ano) em vez do Expo Go, que não aceita banco de dados nem login do Google.

### O que o app dele mostra que vale pro ENEM GI

- **Personagem que reage é o que prende.** O Finch é um app de tarefa pequena (saúde mental) que virou jogo por causa do bichinho. Mesma lógica do Pipo.
- **Onboarding de 17-18 telas antes do paywall** faz a pessoa "comprar a ideia". Pro ENEM GI a versão certa é o **diagnóstico grátis como onboarding** (perguntas que mostram o erro do aluno), sem paywall agora. Atenção: o público tem menor de idade, então qualquer cobrança precisa passar pelo responsável.
- **Confete só no momento de concluir** (tarefa marcada), não solto.
- Ele alerta pra **não copiar o app de referência telas por tela**. O ENEM GI tem identidade própria (Pipo, trilha, diagnóstico); a referência serve pra aprender o que funciona.

### O que NÃO se aplica (e por quê)

| Ideia dele | Por que não pro ENEM GI |
|---|---|
| Personagem animado com **vídeo gerado por IA** (loops em vídeo) | O Pipo já é **desenhado em código** (`components/mascote.tsx`) e já "respira" em loop. Vídeo pesa no app, e o próprio criador viu defeitos: personagem mudando de tamanho no loop, nuvem que não fecha o ciclo. Vetor em código não tem isso e funciona com `reduzir movimento`. |
| Pagar plataforma de geração de imagem/vídeo | Gasto novo sem necessidade agora. Fica pra material da landing (imagem, não vídeo). |
| EAS Build / conta Apple de US$ 99 | O app roda como web e Expo; publicar em loja é decisão futura, depois de autenticação e LGPD. |
| Vídeo de tela como entrada | Aqui eu leio imagem e texto; **não assisto vídeo**. Funciona com sequência de prints ou transcrição. |

### O que adotar (entra no backlog de animação, seção 4)

| # | Ideia | Como | Status |
|---|---|---|---|
| A7 | **Pipo reage ao resultado do simulado** (comemora/consola conforme a nota) | o `Mascote` já tem `mood` (`happy`, `cheer`, `sad`, `sleep`); falta ligar ao placar na tela de resultado | 💡 |
| A8 | **Pipo pisca e olha pro lado de vez em quando** (idle mais vivo) | extensão do "respirando", em código, sem vídeo | 💡 |
| A9 | **Confete em Lottie na conclusão** | `lottie-react-native` ainda não está no `package.json`. Antes: conferir se o Expo 57 suporta, e **ler a licença de cada animação** baixada | 💡 |
| A10 | **Protótipo em moldura de celular no navegador antes de codar** tela nova | já é o fluxo do Claude Design; manter | ✅ |
| W8 | **Plano antes de construir** como primeiro prompt de feature grande | combina com o fluxo de issue antes de PR | 💡 |
| W9 | **Agente trabalha em outra parte enquanto algo demora** (geração, teste longo) | usar subagente em paralelo quando houver tarefa independente | 💡 |
