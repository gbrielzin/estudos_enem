# Bug report + próxima rodada — tela principal única

Print de referência: `localhost:8503`, página Cartão-resposta, tema já aplicado parcialmente.
O tema carregou (as sombras sólidas e o lima aparecem), mas 10 coisas estão erradas. Corrija na ordem — as 4 primeiras são as que fazem a tela parecer "sem vida".

---

## P0 — bugs que quebram a tela

### 1. A página inteira está renderizando escurecida

Todo texto e todo card aparecem com contraste muito abaixo do especificado — os títulos de missão, o texto da Liga Diamante e o card "Marco especial" estão praticamente ilegíveis. O verde do banner "Óptica" saiu oliva escuro em vez de `#6EE12B`, e os nós concluídos saíram marrons em vez de âmbar `#FFC42E`.

Causa provável, em ordem: um `opacity` menor que 1 em algum wrapper que envolve o conteúdo; ou um `filter: brightness()`; ou as cores estão sendo emitidas via `color-mix()`/`rgba()` com alpha em vez do hex cheio.

Como verificar: no DOM renderizado, pegue o `computed style` de um `.ex-mission-title` e de um `.ex-banner`. Se `opacity` não for exatamente `1` nos dois e em todos os ancestrais, é isso. Me diga qual elemento carrega o valor.

Regra: **nenhum texto de UI usa alpha.** Ink é `#F2F4F7` cheio, ink-2 é `#8B93A7` cheio. Alpha só existe dentro do desenho do mascote.

### 2. HTML cru sendo impresso como texto

No rodapé, o card do mascote mostra literalmente:

```
<div style="font-weight:600;font-size:14px;color:var(--ink-2);line-height:1.5">
  "Cinco questões e o Nó 4 abre. Vamos?" — <span ...>Pipo</span></div>
```

Esse `st.markdown` está sem `unsafe_allow_html=True`. Procure **todas** as chamadas de `st.markdown` / `st.write` que passam HTML e garanta a flag — ou melhor, faça toda saída de HTML passar por um único helper `_html()`, como em `enem_theme.py`, e proíba HTML fora dele.

### 3. Emoji no lugar de ícones

A sidebar usa 📄🍏📊🟨✏️📅🎯✍️🎥🔧🔒📚, e os cards usam 🏆🎁. O spec pede **inline SVG de traço 2–2.4px, `stroke-linecap: round`, estilo Lucide**, nunca emoji. Emoji quebra o tom e não aceita cor do tema.

Troque por SVG. Se o projeto não tem biblioteca de ícones, adicione `streamlit-lucide` ou embuta os paths direto no helper.

### 4. A coluna da trilha está estrangulada

A trilha ocupa ~260px de largura no print, com uns 540px de margem vazia à esquerda e à direita. Os nós ficaram empilhados quase na vertical e os rótulos colidem entre si.

O percurso precisa de **350px de largura útil, no mínimo**. E o `.block-container` capado em 720px está brigando com `st.columns` — se a página é o layout de 3 colunas do desktop, ela precisa de `layout="wide"` e do cap removido nessa página específica.

Alvo no desktop (≥1100px): sidebar 268px · centro flexível com mínimo de 700px · rail direito 340px. Abaixo de 1100px, esconda o rail e mantenha sidebar + centro. Abaixo de 760px, coluna única de 390px.

---

## P1 — o que falta pra tela ter vida

### 5. Não existe header

Falta a faixa de identidade no topo do centro: ícone do app 46×46 violeta com sombra `0 5px 0`, título em Baloo 2 800 21px, e a linha de pills logo abaixo — streak (chama) e rank ("S-Rank · 4674 XP" em âmbar sobre `#2A2210`). É a primeira coisa que o olho pega e hoje ela não está lá. Use `enem_theme.header()`.

### 6. O CTA principal desapareceu

O print não tem nenhum botão grande. A tela precisa do banner de continuação em lima cheia, largura total do centro, raio 24, sombra `0 6px 0 #3F8F14`, com o kicker "CIÊNCIAS DA NATUREZA · 2 DE 9 NÓ(S) CONCLUÍDO(S)", o título "Continue de onde parou — Nó 3" em Baloo 2 800 26px, e um botão escuro "COMEÇAR" à direita. Hoje o "COMEÇAR" é uma etiqueta cinza de 60px perdida no meio do percurso.

### 7. A flag "COMEÇAR" está no nó errado e colidindo

Ela aparece entre o nó 2 e o nó 3, encavalada no rótulo "Nó 2 · 5q". Ela pertence **só ao nó atual**, ancorada acima dele com 8px de gap, e o rótulo do nó de cima precisa de espaço reservado. Aumente o espaçamento vertical entre âncoras para 120px.

### 8. Os nós estão pequenos e sem hierarquia

No atual: 78×78, lima, sombra `0 8px 0`, ícone play de 32px. Concluído: 70×70, âmbar `#FFC42E`, sombra `0 7px 0 #C08A00`, check em `#3A2A00`. Bloqueado: 70×70, `#1F2531`, borda `#2C3342`, sombra `0 7px 0 #14181F`, cadeado 22px em `#5B6472`. Rótulo sempre Nunito 700 12.5px `#8B93A7`.

O pontilhado do percurso precisa ser visível: `stroke: #232936`, `stroke-width: 12`, `stroke-linecap: round`, `stroke-dasharray: 1 26`.

### 9. O mascote está no rodapé, fora de vista

Ele tem que ficar **ao lado da trilha**, na altura do nó atual, dentro de um card de surface raio 22, com a fala à direita. É o elemento que dá personalidade — no rodapé, abaixo da dobra, ele não existe.

O mascote é o **Pipoco**, um gato branco. Corpo `#FDFEFF`, sombra `#C4CFDB`, orelhas triangulares com interior rosa `#FF8FA3`, nariz triangular rosa, três bigodes de cada lado, cauda em pill. Quatro estados: `happy`, `cheer` (nó concluído), `sad` (ofensivo perdido), `sleep` (dia sem estudo). Referência: `reference/Mascote.dc.html`.

Troque **todas** as ocorrências de "Pipo" por "Pipoco" no código e nos textos.

**Variantes destraváveis.** A silhueta nunca muda — só o desenho. Props: `pattern` (`none` | `patches` | `tabby` | `tuxedo`), `patch` (cor da mancha), `collar` (cor da coleira, vazio = sem coleira), `color` (cor do corpo). Modele como catálogo de skins com regra de desbloqueio (ex.: 7 dias de ofensivo destrava `tabby`; primeira prova completa destrava a coleira lima). O estado atual do aluno guarda só o id da skin equipada.

### 10. Sidebar ainda é Streamlit puro

Itens precisam ser pills de raio 14, Nunito 700 14px `#8B93A7`, e o ativo é uma pill lima com sombra `0 4px 0` e texto `#0D2705`. Fundo `#12151C`, borda direita `#232733`. No rodapé da sidebar, o card "N dias até o ENEM" com barra âmbar.

---

## Mudança estrutural: uma página principal só

Hoje "Cartão-resposta" e "Banco de Questões" são páginas separadas e é preciso navegar entre elas. Junte: **Cartão-resposta passa a ser a home e contém a trilha**.

Estrutura da home, de cima para baixo no centro:

1. Header (ícone + título + pills de streak/XP)
2. Banner de continuação em lima com o CTA "COMEÇAR"
3. Painel da trilha (`#0F1218`, borda `#1D222B`, raio 24) com o percurso e o card do mascote ao lado
4. Seletores de área/matéria/fonte — **colapsados atrás de um botão "Trocar matéria"**, não expandidos por padrão

No rail direito: missões de hoje, Liga Diamante (top 3 + a linha do usuário em faixa lima), card âmbar do próximo marco.

"Banco de Questões" deixa de ser item de menu de primeiro nível. A entrada no conteúdo passa a ser o nó da trilha. Mantenha a rota antiga funcionando com redirect para a home, para não quebrar link salvo.

**Não mude a lógica de trilha, de XP, de missões nem de sessão de questão.** Isso é reorganização de camada de apresentação.

---

## Remover: a lista de nós abaixo da trilha

Abaixo do percurso existe uma lista de cartões repetindo "Nó 1 — 5 questão(ões) · concluído / Nó 2 — ... / Nó 3 — disponível / Nó 4 — bloqueado ...", cada um com botão Repetir ou Começar. **Apague inteira.**

Ela duplica exatamente a informação que a trilha já dá — estado, contagem de questões e ação — e é o que faz a página ter 2000px de rolagem morta. A trilha é a única representação dos nós.

O que fazer com as ações que estavam ali:
- **Começar** já é o nó atual, clicável na trilha.
- **Repetir** vira um clique no nó concluído (âmbar), que abre um popover pequeno com "Repetir · 5q" e o resultado anterior.
- O texto "Conclua o(s) nó(s) anterior(es) pra destravar este" vira tooltip no nó bloqueado, não linha permanente.

## Liga Diamante: top 3 + a linha do aluno

No card de liga do perfil, mostre só os três primeiros e a faixa do aluno — cinco linhas não cabem na moldura e a informação útil é a posição relativa, não a tabela inteira. "Ver liga completa" abre a lista cheia.

## Como validar

AppTest não vê aparência. Um teste que confirma "tokens em uso" e "sem `<svg>`" passa com a tela idêntica ao print de cima.

Antes de dizer que terminou:

1. `streamlit run` e **screenshot** da home.
2. Compare com `reference/App ENEM.dc.html` (a seção "DESKTOP · 1440").
3. Confirme item por item: contraste cheio, zero HTML impresso como texto, zero emoji, trilha com 350px, header presente, banner de CTA presente, mascote ao lado da trilha.
4. Só então me mostre o diff.


---

# Cartão-resposta: nova interface

Referência visual: `reference/App ENEM.dc.html`, seções **2a** (modo cartão) e **2b** (modo foco).

## O problema do cartão atual

O print de `localhost:8502` mostra 43 questões como 43 linhas idênticas de 6 controles cada — 258 elementos de mesmo peso visual. Consequências:

- Não se vê o que já foi respondido sem ler linha por linha. Não existe contagem, barra de progresso nem cronômetro.
- Cada questão gasta uma linha inteira de ~1750px de largura para 6 controles pequenos, com 3 colunas mal aproveitadas.
- O sexto controle de cada linha (a pill verde "—", de "sem resposta") é redundante: em branco já é o estado inicial. São 43 controles a menos.
- Os três acordeões de configuração ("Carregar gabarito", "Adicionar enunciado", "Preenchimento rápido") ocupam três faixas de largura total antes de qualquer conteúdo.
- O aviso "43 questões cadastradas. 43 com matéria não classificada (⚠)" repete um ⚠ em cada uma das 43 questões. Um aviso agregado basta.
- Nada indica que responder a prova rende XP — o cartão está desligado da camada de gamificação.

## Modo cartão (2a) — padrão

**Barra fixa no topo**, sempre visível ao rolar:
identidade da prova ("CIÊNCIAS DA NATUREZA · CADERNO AZUL" / "ENEM 2025") · contagem "18 de 43 respondidas" com barra de 12px · "25 em branco" · cronômetro em pill · botão **CORRIGIR** em lima com sombra `0 5px 0`.

**Toolbar de uma linha** substituindo os três acordeões: três botões secundários (Gabarito CSV · Enunciados com badge de contagem · Colar sequência) e, à direita, um segmented de dois estados **Cartão / Foco**.

**Grade de blocos** — o núcleo da mudança. Cada questão é um bloco compacto, não uma linha:

- container: `#171B24`, borda `#232733`, raio 16, padding `10px 12px`, `display:flex` gap 6
- número: 36px de largura, Nunito 800 13px. `#F2F4F7` se respondida, `#5B6472` se em branco
- cinco quadrados de 30×30, raio 9: em branco é `#1F2531` + borda `#2C3342` + letra `#5B6472`; selecionado é `#6EE12B` + sombra `0 3px 0 #3F8F14` + letra `#0D2705`
- marcada para revisão: fundo `#2A2210`, borda `#4A3B10`, ponto âmbar de 10px no canto superior direito
- grade de 4 colunas em ≥1280px, 3 em ≥1024px, 2 em ≥760px, 1 no mobile
- **sem** o controle de "sem resposta": clicar na letra já selecionada limpa

Acima da grade, um cabeçalho de faixa ("QUESTÕES 91–120") e uma legenda de três estados. É o que permite bater o olho e saber onde parou.

**Rodapé fixo**: card do Pipoco com a dica de teclado e o teclado A–E visível.

**Rail direito 312px**: progresso por matéria (Física / Química / Biologia com barra própria) · card âmbar "+120 XP na correção" ligando o cartão à gamificação · chips das questões marcadas para revisão · botão "SALVAR E SAIR".

## Modo foco (2b)

Mesma sessão, mesmo estado — só o enquadramento muda. Uma questão por vez, enunciado em Nunito 700 20px, cinco alternativas no estilo da tela de lição, e um mini-mapa de 5 colunas à direita para saltar (respondida = lima, atual = violeta, em branco = neutro). Rodapé com ANTERIOR / PRÓXIMA e a linha de atalhos.

É o modo certo quando há enunciado cadastrado. O modo cartão é para quem já fez a prova no papel e só está transcrevendo.

## Teclado

Fundamental para transcrever 43 respostas: **A–E** responde e pula para a próxima · **← →** navega · **Espaço** marca para revisão · **Backspace** limpa. Mostre a linha de atalhos no rodapé dos dois modos.

## Onde isso vive na navegação

O cartão-resposta deixa de ser página separada e passa a ser **um destino dentro da home**: o bloco "Provas" na home lista as provas disponíveis (ano · caderno · área · progresso), e abrir uma prova entra no cartão. Voltar retorna à home com a trilha.

Simulado completo, revisão de hoje e praticar por matéria são **modos da mesma tela**, não páginas — hoje eles são um radio de 4 opções no topo do cartão, e podem continuar sendo, só reestilizado como chips.
