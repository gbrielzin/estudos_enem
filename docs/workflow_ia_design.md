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
