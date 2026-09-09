# Handoff: Redesign visual do app ENEM (gamificado)

## Prompt para colar no Claude Code (projeto Streamlit)

> Copie `design_handoff_enem_gamificado/streamlit/theme.css` e `enem_theme.py` para a raiz do app.
> Em cada página, chame `enem_theme.inject()` como primeira instrução depois do `st.set_page_config`, e remova todo CSS de tema que já exista espalhado no projeto — o tema tem que vir de um lugar só.
> Substitua os blocos que são **só exibição** (pills de streak/XP, card de missões, trilha de nós, tela de resultado) pelos helpers de `enem_theme.py`. Widget nativo do Streamlit fica apenas onde há entrada real: `st.selectbox`, `st.radio(horizontal=True)`, `st.button`. Nada de `st.progress` — use a barra dos helpers.
> Não mude a lógica de navegação, de trilha, de XP nem de missões. Comece por uma página só (Banco de Questões) e me mostre o diff antes de aplicar.
> Leia o restante deste README para os valores exatos das telas que os helpers ainda não cobrem.

## Por que a primeira tentativa não mudou nada

Estilizar os widgets nativos do Streamlit por cima não produz este design. Três coisas travam:

1. `.block-container` abre em ~1700px — o layout é de coluna única de 720px. Sem capar a largura, tudo estica e nada parece um app.
2. `st.progress`, `st.radio` e `st.metric` trazem DOM próprio que não aceita a sombra sólida nem o raio grande. Onde o elemento é só exibição, ele tem que ser HTML próprio.
3. `st.markdown` sem `unsafe_allow_html=True` imprime as tags como texto. Os helpers já passam a flag.

Os arquivos em `streamlit/` resolvem os três: `theme.css` capa a largura e reestiliza o que sobra de nativo; `enem_theme.py` entrega os blocos de exibição prontos.

---

## Overview

Redesign apenas da **camada visual** de um app de estudo para o ENEM. A estrutura de tela existente é mantida integralmente: streak, rank/XP, missões do dia, trilha com nós bloqueados e abas inferiores. Nada de navegação ou de regra de gamificação muda.

A direção é de app de aprendizado gamificado: cores vivas, formas arredondadas e "gordinhas", profundidade tátil nos botões (sombra sólida deslocada no eixo Y, sem blur), ícones grandes e amigáveis. O mascote é original — nenhum personagem ou marca de app existente é reproduzido.

## About the Design Files

Os arquivos em `reference/` são **referências de design feitas em HTML** — protótipos que mostram aparência e comportamento pretendidos, não código de produção para colar.

A tarefa é **recriar esses designs no ambiente que o codebase já usa** (React, Vue, Streamlit, etc.), com os padrões e bibliotecas já estabelecidos ali. Se não houver ambiente definido, escolha o mais adequado e implemente lá.

`App ENEM.dc.html` e `Mascote.dc.html` usam um runtime de streaming (`support.js`) que não faz parte da entrega — leia-os como fonte de valores (hex, px, pesos de fonte, estrutura), não como app rodável.

**Nota específica de Streamlit** (o print do estado atual mostra `localhost:8502` com sidebar de menu): o app estava renderizando as tags HTML como texto literal. Isso é `st.markdown(...)` sem `unsafe_allow_html=True`. Prefira injetar **um** bloco de CSS por página e usar containers do Streamlit, em vez de montar telas inteiras como string de HTML.

## Fidelity

**Alta fidelidade.** Cores, tipografia, raios, sombras e espaçamentos são finais. Recrie fielmente usando os componentes do codebase.

## Design Tokens

### Paleta — tema escuro (padrão)

| Token | Hex | Uso |
| --- | --- | --- |
| `bg` | `#0A0C10` | fundo da tela |
| `surface` | `#171B24` | cards, pills, tab bar |
| `surface-2` | `#1F2531` | nós bloqueados, linhas de liga |
| `surface-3` | `#232936` | trilhos de barra de progresso |
| `border` | `#232733` | borda de card |
| `border-2` | `#262C39` | borda de controle |
| `ink` | `#F2F4F7` | texto primário |
| `ink-2` | `#8B93A7` | texto secundário |
| `ink-3` | `#5B6472` | texto terciário / desabilitado |
| `lime` | `#6EE12B` | ação primária, nó atual, progresso |
| `lime-shadow` | `#3F8F14` | sombra sólida da ação primária |
| `on-lime` | `#0D2705` | texto sobre lima |
| `violet` | `#7C5CFF` | aba ativa, marca, seleção |
| `violet-shadow` | `#4E33C4` | sombra sólida do violeta |
| `on-violet` | `#F1EEFF` | texto sobre violeta |
| `amber` | `#FFC42E` | XP, recompensa, baú |
| `amber-shadow` | `#C08A00` | sombra sólida do âmbar |
| `amber-bg` / `amber-border` | `#2A2210` / `#4A3B10` | pill de XP |
| `coral` | `#FF6B4A` | vidas, ofensivo, alerta |
| `coral-shadow` | `#C33F22` | sombra sólida do coral |

### Paleta — tema claro

| Token | Hex |
| --- | --- |
| `bg` | `#F4F6F8` |
| `surface` | `#FFFFFF` |
| `border` | `#E2E7ED` |
| `ink` | `#131722` |
| `ink-2` | `#5D6675` |
| `ink-3` | `#7A8494` |
| `lime` / `lime-shadow` | `#57C114` / `#35800A` (texto sobre lima: `#FFFFFF`) |
| `track` | `#EAEEF3` |
| `locked` / `locked-shadow` | `#E8EDF3` / `#D3DAE2` |

Violeta, âmbar e coral são os mesmos nos dois temas.

### Tipografia

- **Baloo 2** (600/700/800) — títulos, números grandes, rótulos de botão. Google Fonts.
- **Nunito** (400/600/700/800/900) — corpo, rótulos, listas. Google Fonts.

Escala em uso:

| Papel | Fonte / peso / tamanho |
| --- | --- |
| Título de tela | Baloo 2 800 · 22px |
| Título de unidade (banner) | Baloo 2 800 · 24px |
| Título de card | Baloo 2 700 · 16.5px |
| Número de destaque | Baloo 2 800 · 21–30px |
| Rótulo de botão | Baloo 2 800 · 17–18px |
| Enunciado de questão | Nunito 700 · 20px / line-height 1.42 |
| Item de lista | Nunito 700 · 14.5–16px |
| Texto de apoio | Nunito 600 · 12.5–13px |
| Kicker / all-caps | Nunito 800 · 11.5–12px · letter-spacing .10–.14em |
| Barra de status | Nunito 800 · 14px |

### Raio de canto

`8px` checkbox · `10–11px` badge de ícone pequeno · `14px` botão de ícone · `18px` seletor / alternativa · `20px` botão primário e card de missão · `22px` card · `48px` moldura do telefone · `999px` pill, tab bar, barra de progresso · `50%` nó da trilha e olhos do mascote.

### Profundidade (a regra mais importante)

Nada usa sombra difusa dentro da UI. Profundidade é **sombra sólida deslocada em Y, sem blur**, na cor escura do próprio elemento:

- botão primário: `box-shadow: 0 6px 0 <shadow>`
- nó atual da trilha: `0 8px 0 <shadow>`
- nó bloqueado: `0 7px 0 #14181F`
- badge de ícone / chip: `0 3px 0` ou `0 4px 0 <shadow>`
- estado pressionado: `transform: translateY(4px)` + sombra reduzida para `0 2px 0` (mesma distância total, o botão "afunda")

Sombra difusa só existe fora da UI, para separar as molduras do fundo do documento (`0 30px 70px rgba(0,0,0,.6)`).

### Espaçamento

Escala de 4: `4 · 6 · 8 · 10 · 12 · 14 · 16 · 18 · 20 · 22 · 26`. Padding lateral de tela: `20px`. Gap entre cards: `12–16px`. Padding interno de card: `16–18px`.

## Screens / Views

Todas as telas mobile são 390×812 (área útil), com barra de status de 46px no topo e tab bar flutuante fixa embaixo (padding `10px 20px 22px`).

### 1. Home

Ponto de entrada. Escolha de área/matéria/fonte e início de sessão.

- **Header**: ícone do app 46×46 (violeta, raio 16, sombra `0 5px 0`) + título "Banco de Questões" (Baloo 2 800 21px) + botão de engrenagem 40×40 (surface, raio 14).
- **Pills de status**, gap 10: streak (surface, borda, `ink-3`, ícone de chama, valor `0`) e rank (`amber-bg` + `amber-border`, texto âmbar, "S-Rank · 4564 XP").
- **Card "Missões de hoje"**: badge de alvo laranja 30×30, título, link "VER TODAS" em lima. Duas missões, cada uma com checkbox 22×22 (raio 8, borda 2px `#3A4152`), título, subtítulo e barra de progresso de 10px. Barra 1 lima, barra 2 violeta. Copy exata:
  - "Complete sua meta diária" / "0/20 questão(ões) hoje"
  - "Foco em geometria_espacial" / "Pratique geometria_espacial hoje — é sua maior prioridade agora"
- **Três seletores** empilhados (gap 10), cada um: badge de ícone 32×32 tintado + rótulo (Nunito 700 11.5px `#6B7385`) + valor (Nunito 700 14.5px) + chevron. Valores: Área/"Ciências da Natureza", Matéria/"Escolha uma matéria" (estado vazio em `ink-2`), Fonte/"Todas".
- **CTA** "COMEÇAR SESSÃO": lima, raio 20, padding 17, Baloo 2 800 17px, sombra `0 6px 0`.
- **Tab bar**: três abas (Home / Explore / Perfil) numa pill de surface; a ativa é uma pill violeta com ícone + rótulo em coluna.

### 2. Trilha

Percurso de nós de uma matéria.

- **Banner da unidade**: bloco lima raio 22, kicker "CIÊNCIAS DA NATUREZA" + título "Óptica" (Baloo 2 800 24px, `on-lime`), e à direita um botão circular violeta 48×48 com engrenagem.
- **Linha de progresso**: barra de 10px + "0 de 9 nó(s)".
- **Trilha**: área de 350×560 com um `path` SVG em `#232936`, `stroke-width: 12`, `stroke-linecap: round`, `stroke-dasharray: 1 26` (pontilhado redondo). Path usado:
  `M175 56 C 175 116, 258 126, 258 176 C 258 236, 175 246, 175 296 C 175 346, 95 356, 95 406 C 95 456, 150 466, 150 516`
  Nós posicionados absolutamente nas âncoras (175,56) (258,176) (175,296) (95,406) (150,516), cada um com `transform: translate(-50%,-50%)`.
  - **Nó atual**: 78×78, lima, sombra `0 8px 0`, ícone play preenchido 32px; acima dele um flag branco "COMEÇAR" (Baloo 2 800 13px, sombra `0 3px 0 #A6AEBD`); abaixo o rótulo "Nó 1 · 5q".
  - **Nó bloqueado**: 70×70, `surface-2`, borda `#2C3342`, sombra `0 7px 0 #14181F`, cadeado 22px em `ink-3`.
- **Mascote** ancorado à direita, na altura do segundo/terceiro nó, com uma pill de nome ("Pipo") abaixo.

### 3. Missões do dia

- Header com botão voltar + título "Missões do dia" + pill âmbar "18h restantes".
- **Card de ofensivo**: sete quadrados (aspect-ratio 1, raio 12) em linha, um por dia; o de hoje é lima com sombra `0 3px 0` e rótulo "HOJE" em lima; o de amanhã tem borda tracejada.
- **Quatro cards de missão**, cada um: badge quadrado 44×44 com sombra sólida na cor do tema da missão, título + valor de XP em âmbar à direita, subtítulo, barra de 10px. Temas: lima (meta diária, +30 XP), violeta (foco, +40 XP), coral (ofensivo, +15 XP), neutro (revisão espaçada, +20 XP).

### 4. Questão

- **Topo**: X de fechar, barra de progresso de 14px (com `inset 0 3px 0 rgba(255,255,255,.35)` no preenchimento para dar volume) e contador de vidas em coral com coração preenchido.
- **Kicker** violeta: "ÓPTICA · NÓ 1 · QUESTÃO 2 DE 5".
- **Enunciado**: Nunito 700 20px, line-height 1.42, `text-wrap: pretty`.
- **Cinco alternativas** (gap 11): linha de surface, borda `border-2`, sombra `0 4px 0 #14181F`, raio 18, com um quadrado de letra 32×32 (raio 10) à esquerda. **Selecionada**: fundo `#241A3A`, borda 2px violeta, sombra `0 4px 0 <violet-shadow>`, quadrado da letra violeta preenchido.
- **Rodapé**: "Dica custa 10 XP" centralizado em `ink-3`, e o botão "CONFIRMAR" lima.

### 5. Resultado

- Mascote em estado `cheer` a 1.5× no topo.
- Título "Nó 1 concluído!" (Baloo 2 800 30px, lima) + subtítulo.
- **Três tiles** de estatística lado a lado: 4/5 ACERTOS (surface), +25 XP (fundo âmbar), 3:12 TEMPO (surface).
- Card de ofensivo com uma linha de reforço do mascote.
- Dois botões: "CONTINUAR" (lima) e "REVER OS ERROS" (surface, borda, sombra `0 4px 0`).

### 6. Explore

- Título, campo de busca (surface, raio 18) e quatro chips de área — o ativo é lima com sombra `0 3px 0`.
- **Lista de matérias**: linhas de card com badge 46×46 colorido (lima / violeta / âmbar / coral), nome, metadados e barra de progresso de 8px na cor do badge. A última é um estado bloqueado: badge neutro com cadeado, texto em `ink-2`, sem barra, copy "Destrava com 3 nós concluídos".

### 7. Perfil e ligas

- Avatar 64×64 (violeta, raio 22, inicial em Baloo 2 26px), nome, rank em âmbar, botão de ajuste.
- **Três tiles**: 61 DIAS P/ ENEM, 1240 QUESTÕES, 78% ACERTO (o último em lima).
- **Card de liga**: escudo azul, "Liga Diamante", subtítulo "Top 5 sobem · faltam 3 dias" e cinco linhas de ranking. A linha do usuário é uma faixa lima com sombra `0 4px 0` e texto `on-lime`.
- Card do mascote no estado `sleep` com a mensagem de retorno.

### 8. Desktop (1440×900)

Três colunas:

- **Sidebar 268px** (`#12151C`, borda direita): marca + itens de navegação em pills de raio 14. O item ativo é uma pill lima com sombra `0 4px 0`. Itens: Cartão-resposta, Banco de Questões, Minha análise, Simulados já feitos, Prova com enunciado (tag BETA), Calendário, Objetivos, Redação, Guia do Estudante. No rodapé, o card "61 dias até o ENEM" com barra âmbar.
- **Centro**: header com título da matéria + pills de streak/XP + avatar; banner lima de continuação com botão escuro "COMEÇAR"; painel da trilha (`#0F1218`, borda `#1D222B`, raio 24) com o percurso na horizontal e o card do mascote com fala.
- **Rail direito 340px**: card de missões, card de liga (top 3) e card âmbar de baú.

## Mascote — "Pipo"

Personagem original, construído só com formas geométricas (sem SVG ilustrado). Referência completa em `reference/Mascote.dc.html`.

Caixa base 104×104, `transform-origin: bottom center`, escalável por `scale()`.

| Parte | Geometria |
| --- | --- |
| Topetes | dois círculos 26×26 no topo, cor = cor de sombra do corpo, rotacionados ∓18° |
| Corpo | 88×84 em `border-radius: 52% 52% 46% 46% / 58% 58% 42% 42%`, cor base, `box-shadow: 0 8px 0 <shadow>, inset 0 -7px 0 rgba(0,0,0,.09)` |
| Barriga | elipse 56×44 em `rgba(255,255,255,.26)` |
| Brilho | elipse 30×22 em `rgba(255,255,255,.22)` no alto à esquerda |
| Olhos | dois círculos 27×27 em `#FDFEFF`, pupilas de 13px em `#141821` |
| Bico | quadrado de 17px rotacionado 45°, raio 3, cor âmbar |
| Bochechas | elipses 14×9 em `rgba(255,120,110,.42)` |

Estados (prop `mood`), acionados pelo progresso do usuário:

| Estado | Quando | Diferenças |
| --- | --- | --- |
| `happy` | padrão | como acima |
| `cheer` | nó concluído / missão completa | rotação −7°, pupilas 2px acima, bico 22px, losango de faísca no canto superior direito |
| `sad` | ofensivo perdido | rotação +5°, pupilas 4px abaixo, bico 13px, pálpebras cobrindo 14px do olho |
| `sleep` | dia sem estudo | pálpebras cobrindo 16px do olho |

Props: `color`, `shadow`, `beak`, `mood`, `size`. Nos mocks: `color: #6EE12B`, `shadow: #3F8F14`, `beak: #FFC42E` (tema claro usa `#57C114` / `#35800A`).

O rascunho geométrico é substituível: onde o mascote aparece, deixe um slot que aceite uma imagem quadrada (512×512, PNG transparente) no lugar do desenho.

## Interactions & Behavior

- **Pressionar botão / nó**: `transform: translateY(4px)` e a sombra sólida cai de `0 6px 0` para `0 2px 0` (nó: de `0 8px 0` para `0 3px 0`). Sem transição de cor. Duração 80ms, `ease-out`.
- **Nó bloqueado**: não responde a toque; um toque pode disparar um shake curto (±3px, 200ms).
- **Selecionar alternativa**: troca para o estilo violeta; só uma por vez; "CONFIRMAR" fica inativo (opacidade 45%) até haver seleção.
- **Barra de progresso**: anima a largura em 400ms `ease-out` quando o valor muda.
- **Mascote**: troca de estado com um pop rápido (`scale(1)→1.06→1`, 240ms). No `cheer`, a faísca aparece com 120ms de atraso.
- **Responsivo**: mobile é coluna única com padding lateral 20px; a partir de ~1100px entra o layout de três colunas do desktop; entre os dois, esconda o rail direito e mantenha sidebar + centro.

## State Management

Nenhum estado novo. O redesign consome o que a lógica de gamificação já produz:

- streak (dias), XP total e rank
- lista de missões do dia (título, subtítulo, progresso atual/meta, XP de recompensa, tema)
- trilha ativa (matéria, total de nós, nós concluídos, índice do nó atual, estado por nó)
- sessão de questão (índice atual, total, vidas restantes, alternativa selecionada)
- resultado do nó (acertos, XP ganho, tempo)
- liga (posição, lista de participantes com XP)

O estado do mascote é **derivado**, não armazenado: `cheer` logo após concluir nó ou missão; `sad` se o streak zerou hoje; `sleep` se não houve atividade hoje; `happy` no resto.

## Assets

Nenhuma imagem. Ícones são inline SVG de traço 2–2.4px, `stroke-linecap: round`, no estilo Lucide — troque pela biblioteca de ícones que o projeto já usa. Fontes vêm do Google Fonts (Baloo 2, Nunito).

## Files

- `streamlit/theme.css` — tema completo, injetado uma vez por página.
- `streamlit/enem_theme.py` — helpers: `inject()`, `header()`, `Mission` + `missions_card()`, `trilha()`, `resultado()`.
- `reference/App ENEM.dc.html` — as sete telas mobile (escuro), duas em tema claro e a tela desktop.
- `reference/Mascote.dc.html` — o mascote e seus quatro estados.
