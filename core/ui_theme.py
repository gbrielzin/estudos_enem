"""
ui_theme.py — CSS complementar ao tema em .streamlit/config.toml.

O config.toml cobre cor/fonte/raio via API oficial do Streamlit (robusto
entre versões). O que ele não alcança — esconder o rodapé "Made with
Streamlit", dar cara de cartão pras métricas, estilizar as bolhas de
resposta A-E, desenhar o mascote "Pipoco" — fica aqui, isolado, pra não
espalhar <style> solto pelas telas.

Chamar injetar_tema() uma vez, no topo do entrypoint (__main__ de
cartao_resposta.py). Streamlit reprocessa o script inteiro a cada
interação, então isso roda de novo a cada rerun — é barato (só injeta
uma tag <style>), não precisa de cache.
"""
import html

import streamlit as st

import enem_theme

_CSS = """
<style>
/* Design tokens -- vêm de docs/design_handoff_enem_gamificado/README.md
   (handoff formal, 2026-09), a fonte da verdade agora pra nome e valor
   de token (antes vinha só de um mockup solto). MESMOS valores do app
   mobile (mobile/src/constants/brand.ts) -- mantenha os dois em
   sincronia se um mudar. Três cores de função, não uma: lima = ação,
   violeta = progresso/marca, âmbar = recompensa, coral = alerta/vidas/
   ofensivo. Fundo escuro por padrão (config.toml base="dark"). */
:root {
    /* Ver o mesmo comentário em theme.css -- protege TODA página (não só
       Banco de Questões) do "Auto Dark Mode" do Chromium re-processar um
       tema que já é escuro de propósito, escurecendo/dessaturando lima e
       âmbar por cima. */
    color-scheme: dark;
    --tema-bg: #0A0C10;
    --tema-surface: #171B24;
    --tema-surface-2: #1F2531;
    --tema-surface-3: #232936;
    --tema-border: #232733;
    --tema-border-2: #262C39;
    --tema-ink: #F2F4F7;
    --tema-ink-2: #8B93A7;
    --tema-ink-3: #5B6472;
    --tema-lime: #6EE12B;
    --tema-lime-shadow: #3F8F14;
    --tema-on-lime: #0D2705;
    --tema-violet: #7C5CFF;
    --tema-violet-shadow: #4E33C4;
    --tema-on-violet: #F1EEFF;
    --tema-amber: #FFC42E;
    --tema-amber-shadow: #C08A00;
    --tema-amber-bg: #2A2210;
    --tema-amber-border: #4A3B10;
    --tema-coral: #FF6B4A;
    --tema-coral-shadow: #C33F22;
}

/* Remove marca d'água padrão do Streamlit (rodapé "Made with
   Streamlit" e o botão "Deploy") -- é o maior "carimbo de template"
   visual que o framework deixa por padrão.

   IMPORTANTE: esconder [data-testid="stToolbar"] inteiro (como esta
   regra fazia antes) também esconde stExpandSidebarButton -- ele mora
   DENTRO do toolbar, não ao lado. Em tela larga isso passava
   despercebido porque a sidebar já abre expandida por padrão; no
   celular ela abre FECHADA, e esse botão escondido era a única forma
   de abrir o menu -- ficava só o cartão-resposta, sem acesso a
   nenhuma outra página. Por isso a regra abaixo mira só
   stToolbarActions (Deploy + menu hambúrguer), nunca o stToolbar
   inteiro. Descoberto porque o usuário reportou o menu sumido no
   celular depois do deploy -- não foi achado testando local. */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbarActions"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Menu próprio (hamburguer + gaveta), substitui st.sidebar. Toggle é
   CSS PURO via checkbox+label (:checked ~), de propósito -- SEM
   JavaScript nenhum envolvido. Duas abordagens com JS já foram
   tentadas e falharam por motivos que não davam pra prever de antemão:
   (1) onclick como atributo HTML -- st.markdown(unsafe_allow_html=True)
   SANITIZA atributos on*, o atributo simplesmente não existe no DOM
   renderizado; (2) onclick ligado via um <script> dentro de
   components.html (iframe srcdoc, caminho que o Streamlit não
   sanitiza) -- funcionou nos meus próprios testes (window.parent.
   document alcançava os elementos, confirmado via DOM), mas falhou pro
   usuário de verdade em todo contexto testado (celular, PC, nuvem,
   local) sem erro nenhum aparecendo -- o suspeito mais provável é
   acesso cross-frame bloqueado silenciosamente em algum navegador/
   contexto que eu não consigo reproduzir aqui. CSS puro com
   checkbox+label não depende de NENHUMA dessas coisas: é
   comportamento nativo do HTML (clicar num <label for="id"> alterna o
   checkbox associado), suportado por qualquer navegador com CSS
   habilitado, sem sanitização possível e sem cross-frame envolvido --
   a categoria inteira de bug das duas tentativas anteriores deixa de
   poder acontecer. Estrutura obrigatória: checkbox + as duas labels +
   a nav, todos irmãos diretos dentro do MESMO elemento pai (o
   <div class="nav-root"> em navegacao_lateral()), senão o seletor de
   irmão geral (~) não bate -- ver o comentário lá sobre o parser de
   markdown do Streamlit fragmentar isso em <p> se não for tudo
   embrulhado num único bloco.

   Antes do redesign, esta gaveta era a ÚNICA parte do app propositalmente
   escura (chrome de navegação, ver histórico), com cores hardcoded
   separadas do resto porque o conteúdo era claro. Com o app inteiro
   escuro agora, essa separação não faz mais sentido -- a gaveta consome
   as MESMAS variáveis --tema-* do resto do app, uma fonte de cor só. */
.nav-toggle-checkbox {
    position: absolute;
    opacity: 0;
    width: 2.5rem;
    height: 2.5rem;
    margin: 0;
    top: 0.7rem;
    left: 0.7rem;
    z-index: 1000002;
    cursor: pointer;
}
/* z-index alto de propósito: [data-testid="stHeader"]/stToolbar (a
   barra do Streamlit que sobra no topo, área do Deploy que já
   escondemos) usa z-index: 999990 -- descoberto inspecionando
   elementFromPoint() no botão hambúrguer, que visualmente aparecia por
   cima mas não recebia o clique (o header, mesmo transparente, ainda
   captura o evento por estar num contexto de empilhamento mais alto).
   999999+ garante que hambúrguer/gaveta/overlay ficam acima dessa
   barra em qualquer estado. */
.nav-hamburger {
    position: fixed;
    top: 0.7rem;
    left: 0.7rem;
    z-index: 1000001;
    background: var(--tema-surface);
    border: 1px solid var(--tema-border-2);
    border-radius: 0.7rem;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    line-height: 1;
    color: var(--tema-ink);
    cursor: pointer;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5);
    user-select: none;
}

.nav-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(5, 8, 5, 0.6);
    z-index: 999999;
    cursor: pointer;
}
#nav-toggle:checked ~ .nav-overlay { display: block !important; }

.nav-drawer {
    position: fixed;
    top: 0;
    left: -300px;
    width: 280px;
    max-width: 80vw;
    height: 100vh;
    background: #12151C;
    border-right: 1px solid var(--tema-border);
    z-index: 1000000;
    /* Sem transition de propósito: com "transition: left" o toggle
       ficava impossível de verificar nesta ferramenta de teste --
       getComputedStyle().left continuava preso no valor antigo
       indefinidamente após o toggle (mesmo com a classe .aberto
       correta e a regra !important correta, confirmado via
       document.styleSheets), mesmo em elemento isolado de teste sem
       nenhuma ligação com o Streamlit -- reproduzido mesmo esperando
       vários segundos reais entre checagens. Tudo indica que é a aba
       automatizada não rodando frames de composição de verdade (sem
       foco visual), não um bug de CSS -- mas como não dá pra confirmar
       isso com certeza aqui, abrir/fechar direto (sem slide) troca um
       polimento visual por um comportamento 100% verificável. */
    display: flex;
    flex-direction: column;
    padding: 4.5rem 0 1.5rem;
    overflow-y: auto;
    box-shadow: 4px 0 24px rgba(0,0,0,0.4);
}
#nav-toggle:checked ~ .nav-drawer { left: 0 !important; }

.nav-drawer .nav-title {
    font-family: 'Baloo 2', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--tema-ink);
    padding: 0 1.3rem 1rem;
    letter-spacing: 0.02em;
}

/* Pills de raio 14 (handoff, seção Desktop) em vez do sublinhado à
   esquerda da 1a rodada -- item ativo vira uma pill lima com sombra
   sólida, igual ao item ativo da sidebar de 268px do mockup. */
.nav-drawer {
    padding-left: 1rem;
    padding-right: 1rem;
    gap: 3px;
}
.nav-drawer a.nav-item {
    display: flex;
    align-items: center;
    padding: 11px 12px;
    border-radius: 14px;
    color: var(--tema-ink-2);
    text-decoration: none;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 14px;
    transition: background 0.15s ease, color 0.15s ease;
}
.nav-drawer a.nav-item:hover {
    background: rgba(110, 225, 43, 0.08);
}
.nav-drawer a.nav-item.ativo {
    color: var(--tema-on-lime);
    background: var(--tema-lime);
    box-shadow: 0 4px 0 var(--tema-lime-shadow);
    font-weight: 800;
}

/* Botão de trocar modo escuro/claro (ver navegacao_lateral) -- mesma
   pill de .nav-item, com um espaço/linha separando dos itens de
   navegação de verdade (ele troca ?tema=, não ?pagina=). */
.nav-drawer a.nav-toggle-tema {
    gap: 10px;
    margin-top: 8px;
    padding-top: 15px;
    border-top: 1px solid var(--tema-border);
}

/* Card "N dias até o ENEM" fixado no rodapé da gaveta (margin-top:auto
   dentro do .nav-drawer flex-column) -- ver navegacao_lateral(). */
.nav-drawer .nav-footer {
    margin: auto 4px 0;
    background: var(--tema-surface);
    border: 1px solid var(--tema-border);
    border-radius: 18px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.nav-drawer .nav-footer-label { font-weight: 700; font-size: 13px; color: var(--tema-ink-2); }
.nav-drawer .nav-footer-track { height: 9px; border-radius: 999px; background: var(--tema-surface-3); overflow: hidden; }
.nav-drawer .nav-footer-fill { height: 100%; background: var(--tema-amber); }

/* >= 1100px (mesmo corte de docs/design_handoff_enem_gamificado/README.md,
   seção "Interactions & Behavior", e do app mobile --
   mobile/src/components/app-tabs.web.tsx usa o mesmo número pro
   mesmo motivo): a gaveta vira sidebar FIXA sempre aberta, como no
   mockup original e no app mobile -- pedido explícito do usuário
   depois de ver a versão mobile (que já tinha ganho essa sidebar)
   funcionando. navegacao_lateral() descrevia isso como deixado de
   fora "por ora" por ser mais arriscado que o pedido original de
   "mesma cara" pedia -- isto é exatamente esse "depois".

   Zero HTML novo, zero JS, zero estado novo: o checkbox/hambúrguer/
   overlay continuam existindo no DOM (abaixo de 1100px o
   comportamento de toggle não muda em nada), só ficam escondidos
   aqui, e a MESMA regra `left: 0` que `#nav-toggle:checked ~
   .nav-drawer` já aplicava passa a valer sempre, sem depender do
   checkbox. Isso transforma a gaveta de overlay modal (por cima do
   conteúdo, com escurecedor) em parte fixa do layout -- por isso o
   conteúdo principal (`[data-testid="stMain"]`, o wrapper real do
   Streamlit 1.61 confirmado no bundle, não um nome adivinhado) ganha
   `padding-left` igual à largura da gaveta, senão o texto entraria
   por baixo dela. */
@media (min-width: 1100px) {
    .nav-hamburger, .nav-overlay { display: none !important; }
    .nav-drawer { left: 0 !important; box-shadow: none; }
    [data-testid="stMain"] {
        padding-left: 280px;
        /* `stMain` reserva um padding-top próprio por padrão (pensado
           pra sobrar espaço pro hambúrguer flutuante, top:0.7rem, que
           essa mesma media query já escondeu duas regras acima) --
           acima de 1100px ele não existe mais, então esse espaço fica
           sobrando por cima do padding-top de verdade que já é
           controlado (.block-container, 28px, ver theme.css) -- daí o
           "Óptica" (enem_theme.header(), primeira coisa da página)
           ficar longe do topo. Zerado só aqui (>=1100px): abaixo desse
           corte o hambúrguer volta a existir e precisa da folga. */
        padding-top: 0 !important;
    }
}

/* "Cena da mesa" (Provas ENEM, topo da página) -- panorâmica de
   verdade, encostando nas duas bordas do espaço disponível (depois da
   gaveta fixa), não uma caixa flutuando dentro do padding padrão do
   Streamlit. .block-container nesta versão instalada (1.61.1) usa
   80px de padding lateral em qualquer viewport >=1100px (confirmado
   ao vivo via getComputedStyle em 1150px e 1800px, mesmo valor nos
   dois -- estável nessa faixa, não chutado), por isso a margem
   negativa é fixa aqui, só dentro da MESMA media query que já trava a
   gaveta lateral fixa (breakpoint compartilhado de propósito, mesmo
   corte de ui_theme já usa acima). Abaixo de 1100px (celular/gaveta em
   overlay) cai pro padding normal do Streamlit -- sem margem negativa
   lá, zero risco de estourar a viewport numa tela estreita que esta
   sessão não consegue testar de verdade. */
.cena-mesa-full-bleed { width: 100%; }
@media (min-width: 1100px) {
    .cena-mesa-full-bleed {
        width: calc(100% + 160px);
        margin-left: -80px;
        margin-right: -80px;
    }
}

/* Barra de navegação de ícones (App ENEM.dc.html, Turno 4, 4a) --
   SUBSTITUI a gaveta de texto (.nav-drawer/.nav-hamburger/.nav-overlay
   acima, mantidas no arquivo só pra não perder o código, mas não são
   mais chamadas por __main__) -- pedido explícito do usuário,
   2026-09-11: "substitua cartão resposta, prova enem e tudo aquele
   menu por aqueles ícones". Uma tentativa anterior deste MESMO visual
   escopada só dentro de Provas ENEM (classes .entrada-bleed/.barra-
   icones-entrada) saiu "bugada" segundo o usuário e foi revertida --
   esta versão é a navegação real do app inteiro, sempre fixa, sempre
   visível (ver barra_navegacao_icones() em ui_theme.py).

   Fixa a esquerda em QUALQUER largura de tela, sem hambúrguer/gaveta
   nenhum -- 82px é estreito o bastante pra nunca precisar de um modo
   "recolhido": a mesma lição de "não dá pra testar comportamento
   responsivo de verdade nesta sessão" que motivou trocar a sidebar
   nativa por esta gaveta CSS (ver navegacao_lateral()) se aplica aqui
   só que ao extremo -- eliminando o breakpoint por completo eliminou
   também a classe inteira de bug ("hambúrguer inacessível no celular")
   que motivou toda a reescrita anterior. */
.barra-nav-icones {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 82px;
    background: #0F1218;
    border-right: 1px solid #1D222B;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
    gap: 8px;
    z-index: 999999;
    overflow-y: auto;
}
/* border:2px solid transparent na base (não "sem borda") -- crucial:
   o estado ativo (inline, ver barra_navegacao_icones()) só troca
   border-color/background, nunca adiciona a borda -- se a base não
   reservasse os mesmos 2px, o ícone puxaria 4px de largura extra ao
   ativar e todo o resto da coluna se deslocaria (layout shift). Cor
   de "ativo" vem de _COR_ATIVA_NAV (a cor do PRÓPRIO ícone, mesma
   lógica de mobile/tab-bar.tsx -- COR_ATIVA/isFocused), não mais um
   anel branco genérico (1a versão: "provas_enem"/"guia" tinham cor de
   repouso fixa que colidia visualmente com um destaque lima de
   "ativo" -- resolvido junto com a troca pra cor-própria-do-ícone,
   que não tem mais cor de repouso nenhuma, só ativo/inativo). */
.barra-nav-icones a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 15px;
    border: 2px solid transparent;
    flex: 0 0 auto;
    text-decoration: none;
}
[data-testid="stMain"] {
    padding-left: 82px !important;
    padding-top: 0 !important;
}
@media (max-width: 480px) {
    /* Tela realmente minúscula: encolhe a barra em vez de escondê-la
       (nunca some -- ver comentário grande acima). */
    .barra-nav-icones { width: 60px; padding: 12px 0; gap: 6px; }
    .barra-nav-icones a { width: 40px; height: 40px; border-radius: 12px; }
    [data-testid="stMain"] { padding-left: 60px !important; }
}

/* Título principal com uma régua lima embaixo. */
.app-hero {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.25rem;
    margin-top: 2.5rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--tema-lime);
}
.app-hero h1 {
    margin: 0;
}
.app-hero span.tagline {
    color: var(--tema-lime);
    font-size: 0.95rem;
    opacity: 0.85;
}

/* Cabeçalho com badge de ícone (ver hero(icone=...)) -- mesma
   linguagem visual do badge violeta de enem_theme.header() na Home
   (ícone 46x46 com sombra sólida + título Baloo 2), pra toda página
   fora do redesign trilha/home também ganhar identidade própria em vez
   do hero genérico só-texto (era "📝 Cartão-resposta digital" fixo em
   TODA página que não é a Home -- resquício de antes da 3a rodada do
   handoff mover a trilha pra cá; corrigido junto com isto). */
.app-hero-badged {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 1.75rem;
    margin-bottom: 1.1rem;
}
.app-hero-badge {
    width: 46px;
    height: 46px;
    border-radius: 16px;
    background: var(--tema-violet);
    box-shadow: 0 5px 0 var(--tema-violet-shadow);
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
}
.app-hero-badged h1 {
    font-family: 'Baloo 2', sans-serif;
    font-weight: 800;
    font-size: 1.55rem;
    margin: 0;
    color: var(--tema-ink);
}
.app-hero-badged .tagline {
    display: block;
    color: var(--tema-ink-2);
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.15rem;
}

/* Cards de métrica (Rank / XP / Ofensiva) com borda e leve textura lima,
   em vez do bloco chapado padrão do st.metric. Fundo escuro secundário
   (--tema-surface) + glow sutil, igual à linguagem de card do
   mobile (ver mobile/src/components/status-header.tsx). */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(110,225,43,0.08), var(--tema-surface) 60%);
    border: 1px solid var(--tema-border);
    border-radius: 0.9rem;
    padding: 1rem 1.1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}
div[data-testid="stMetricLabel"] {
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    opacity: 0.75;
}

/* Botões primários com glow lima no hover -- feedback tátil. Cor do
   texto forçada pra ESCURA: o design pede texto escuro sobre botão lima
   (mesmo padrão do mobile, ver Brand.bg usado como cor de texto nos
   botões) -- alto contraste com o lima claro, diferente do branco que o
   Streamlit usaria por padrão num tema escuro. */
button[kind="primary"], button[kind="primaryFormSubmit"] {
    font-weight: 700;
    color: #0D2705 !important;
    transition: box-shadow 0.15s ease, transform 0.05s ease;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    box-shadow: 0 0 18px rgba(110, 225, 43, 0.45);
}
button[kind="primary"]:active, button[kind="primaryFormSubmit"]:active {
    transform: scale(0.98);
}

/* Formulários (o cartão-resposta inteiro é um st.form) com cara de
   cartão -- sem isso, a grade de questões fica "boiando" no fundo.
   Raio 22px = token "card" do handoff (docs/design_handoff_enem_gamificado/
   README.md, seção Raio de canto). */
div[data-testid="stForm"] {
    border: 1px solid var(--tema-border);
    border-radius: 22px;
    padding: 1.25rem 1.25rem 0.5rem;
    background: var(--tema-surface);
}

/* Grade de resposta (A-B-C-D-E por questão): opções horizontais viram
   "bolhas" -- visual de cartão-resposta de verdade em vez de radio
   button cru. :has() é suportado no Chrome/Edge/Firefox atuais; onde
   não for, cai de volta pro radio padrão (degradação segura). */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0.3rem;
}
div[data-testid="stRadio"] label {
    border: 1px solid var(--tema-border-2);
    border-radius: 999px;
    padding: 0.15rem 0.6rem;
    margin: 0 !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}
div[data-testid="stRadio"] label:has(input:checked) {
    border-color: var(--tema-lime);
    background: rgba(110, 225, 43, 0.12);
}

/* Grade de blocos do cartão-resposta (Turno 2 do handoff, App ENEM.dc.
   html seção 2a) -- reestiliza SÓ os st.radio(horizontal=True) da
   grade de 3 colunas em _renderizar_grade_questoes() (estilo_exame=
   False), via o marcador ".grade-blocos" que aquela função renderiza
   como irmão anterior de cada linha de colunas (mesmo truque de
   seletor-irmão geral ~ que .ex-desktop-cols usa, ver theme.css) --
   não toca no radio vertical do modo "estilo_exame" (enunciado inteiro
   + alternativa por extenso) nem em nenhum outro st.radio do app, que
   ficam com o visual de pílula genérico acima. Cores batem exatamente
   com a função cell() do data-dc-script do handoff (marcado = lima
   cheio + sombra sólida; não marcado = surface-2 + borda). Opção "—"
   é sempre o 1o filho (["—","A",...]), estilizada menor/apagada de
   propósito pra não competir visualmente com as 5 letras de verdade.

   NENHUMA destas regras batia de verdade até 2026-09-11 (achado ao
   vivo no Chrome comparando getComputedStyle contra o que o CSS
   deveria produzir): o "truque de irmão-geral" pressupunha que o
   `<div class="grade-blocos">` fosse irmão DIRETO do
   `[data-testid="stHorizontalBlock"]` seguinte, mas o Streamlit 1.61
   embrulha CADA um em containers próprios -- o marcador fica 4 níveis
   dentro de um `[data-testid="stElementContainer"]` (stMarkdownContainer
   > div > stMarkdown > stElementContainer), e o `st.columns()` seguinte
   vem dentro de um `[data-testid="stLayoutWrapper"]` -- então
   `.grade-blocos ~ [data-testid="stHorizontalBlock"]` nunca eram irmãos
   de verdade, e todo st.radio caía no visual de pílula fina genérica
   acima. Corrigido ancorando o `~` no `stElementContainer` que CONTÉM
   o marcador (via :has(), suportado em todo browser moderno) e
   atravessando o `stLayoutWrapper` extra do lado do alvo. */
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] {
    gap: 5px !important;
}
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] > label {
    width: 26px;
    height: 26px;
    padding: 0 !important;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: var(--tema-surface-2);
    border: 1px solid #2C3342;
    color: var(--tema-ink-3);
    font-weight: 800;
    font-size: 12px;
}
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: var(--tema-lime);
    border-color: var(--tema-lime-shadow);
    box-shadow: 0 2px 0 var(--tema-lime-shadow);
    color: var(--tema-on-lime);
}
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] > label:first-child {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    font-size: 10px;
    opacity: .6;
    align-self: center;
}
/* Mesmo bug do .ano-pills (ver comentário grande logo abaixo): a
   bolinha nativa do radio ficava por cima do texto/número aqui
   também, só que nunca aparecia de verdade porque a regra INTEIRA
   acima nunca batia -- corrigido junto. */
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] > label > div > div {
    justify-content: center !important;
}
div[data-testid="stElementContainer"]:has(div.grade-blocos)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stRadio"] [role="radiogroup"] > label > div > div > div:first-child {
    display: none !important;
}

/* Pills grandes do wizard "Montar prova" (App ENEM.dc.html, Turno 3,
   seções 3a/3b -- ver _renderizar_montar_prova em cartao_resposta.py):
   "Qual ano" e "Como responder" usam isto (marcador ".ano-pills" antes
   de cada um, mesmo truque de irmão-geral que .grade-blocos já usa) --
   pill grande arredondada com sombra sólida e número/texto em Baloo 2,
   BEM diferente do pill fino genérico (div[data-testid="stRadio"]
   label, acima) que o resto do app usa -- pedido explícito do usuário
   pra bater de verdade com o visual do mockup, não só reaproveitar o
   estilo padrão de radio.

   Mesmo bug de nesting do .grade-blocos acima (achado ao vivo
   2026-09-11 investigando por que "os botões de ano ainda não tá como
   no design" mesmo com esta regra já escrita): `.ano-pills` fica
   fundo demais dentro do seu próprio stElementContainer pro `~` puro
   alcançar o `[data-testid="stRadio"]` seguinte (que também tem SEU
   PRÓPRIO stElementContainer) -- ancorado com :has() dos dois lados
   agora, confirmado via `label.matches(seletor)` no DOM real antes de
   fechar o fix, não só por inspeção visual. */
div[data-testid="stElementContainer"]:has(div.ano-pills)
  ~ div[data-testid="stElementContainer"] div[data-testid="stRadio"] [role="radiogroup"] {
    gap: 9px !important;
}
div[data-testid="stElementContainer"]:has(div.ano-pills)
  ~ div[data-testid="stElementContainer"] div[data-testid="stRadio"] [role="radiogroup"] > label {
    background: var(--tema-surface) !important;
    border: 1.5px solid var(--tema-border-2) !important;
    box-shadow: 0 4px 0 #14181F !important;
    border-radius: 16px !important;
    padding: 11px 17px !important;
    font-family: 'Baloo 2', sans-serif !important;
    font-weight: 800 !important;
    font-size: 19px !important;
    color: var(--tema-ink-2) !important;
    transition: none !important;
}
/* A bolinha nativa do radio (anel + miolo, mesma estrutura já mapeada
   ao vivo no DOM pra corrigir o contraste do modo claro em stRadio)
   continuava renderizada DENTRO da pill, ao lado do número -- o
   mockup não tem bolinha nenhuma, só o número centralizado, cor/fundo
   da própria pill é o que marca "selecionado". `label > div > div` é
   o container flex que hoje tem 2 filhos (a bolinha e o texto);
   escondendo o primeiro e centralizando o que sobra reproduz isso sem
   tocar no radio em si (continua funcionando, só não aparece mais). */
div[data-testid="stElementContainer"]:has(div.ano-pills)
  ~ div[data-testid="stElementContainer"] div[data-testid="stRadio"] [role="radiogroup"] > label > div > div {
    justify-content: center !important;
}
div[data-testid="stElementContainer"]:has(div.ano-pills)
  ~ div[data-testid="stElementContainer"] div[data-testid="stRadio"] [role="radiogroup"] > label > div > div > div:first-child {
    display: none !important;
}
div[data-testid="stElementContainer"]:has(div.ano-pills)
  ~ div[data-testid="stElementContainer"] div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: var(--tema-lime) !important;
    border-color: var(--tema-lime-shadow) !important;
    box-shadow: 0 5px 0 var(--tema-lime-shadow) !important;
    color: var(--tema-on-lime) !important;
}

/* Cartões "Qual área" do mesmo wizard -- são st.button de verdade
   (não st.radio, ver _renderizar_montar_prova), então usam type=
   "primary"/"secondary" nativos do Streamlit pra marcar qual está
   selecionado em vez de CSS -- aqui só engorda a altura/raio pra
   parecer cartão, não botão de ação comum. Marcador ".area-cards"
   ANTES do st.columns() que contém os botões (mesmo truque de
   irmão-geral) -- sem isso a regra pegaria QUALQUER st.button dentro
   de QUALQUER st.columns do app inteiro (Corrigir/Continuar/etc),
   que é exatamente o tipo de vazamento que esse truque existe pra
   evitar.

   Mesmo bug de nesting do .grade-blocos/.ano-pills (2026-09-11):
   ancorado com :has() no stElementContainer do marcador, e
   atravessando o stLayoutWrapper que embrulha todo st.columns() --
   confirmado via button.matches(seletor) no DOM real antes de fechar. */
div[data-testid="stElementContainer"]:has(div.area-cards)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stButton"] button {
    border-radius: 20px;
    padding-top: 16px;
    padding-bottom: 16px;
    font-family: 'Baloo 2', sans-serif;
    font-weight: 800;
    font-size: 15px;
}

/* Botões "Qual ano" (mesmo wizard) -- também virou st.button (era
   st.radio, ver comentário grande em _renderizar_montar_prova sobre
   por que precisou trocar: a referência visual do usuário mostra o
   número GRANDE dentro do quadrado e uma bolinha de status PEQUENA
   por fora, embaixo -- st.radio só aceita uma linha de texto simples
   por opção, sem dar pra ter dois tamanhos de fonte). Marcador
   ".ano-cards", mesmo truque/fix de :has()+stLayoutWrapper que
   .area-cards usa logo acima. Quadrado bem maior que o botão de área
   (a referência mostra 7 deles lado a lado, mais altos que largos) e
   sombra sólida tipo "botão físico" (0 4px 0 cor-mais-escura) igual
   ao resto do wizard -- cor da sombra muda com type= primary/
   secondary porque button[kind=] já é o atributo real que o Streamlit
   usa pra essa distinção (confirmado: já usado em outra regra global
   deste mesmo arquivo). */
div[data-testid="stElementContainer"]:has(div.ano-cards)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stButton"] button {
    border-radius: 18px;
    padding-top: 20px;
    padding-bottom: 20px;
    font-family: 'Baloo 2', sans-serif;
    font-weight: 800;
    font-size: 22px;
    box-shadow: 0 4px 0 #14181F;
}
div[data-testid="stElementContainer"]:has(div.ano-cards)
  ~ div[data-testid="stLayoutWrapper"] div[data-testid="stHorizontalBlock"]
  div[data-testid="stButton"] button[kind="primary"] {
    box-shadow: 0 4px 0 var(--tema-lime-shadow);
}

/* Separadores e expanders com a mesma linguagem de borda, pra tudo
   parecer parte do mesmo sistema visual. */
div[data-testid="stExpander"] {
    border: 1px solid var(--tema-border);
    border-radius: 0.9rem;
}

/* Rail "Por matéria" ao lado da grade de Provas ENEM (ver
   _renderizar_rail_por_materia em cartao_resposta.py) -- card + barra
   de progresso fina, mesma linguagem visual do .ex-card/.ex-track de
   enem_theme.py/theme.css, só que com nome e tokens próprios porque
   esta página NÃO carrega theme.css (o cap de largura 720px dele
   espremeria a grade de 3 colunas da prova real -- ver comentário
   grande em cartao_resposta.py sobre isso). */
.materia-rail-card {
    background: var(--tema-surface);
    border: 1px solid var(--tema-border);
    border-radius: 1.1rem;
    padding: 18px;
}
.materia-rail-track {
    height: 8px;
    border-radius: 999px;
    background: var(--tema-surface-3);
    overflow: hidden;
}
.materia-rail-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--tema-lime);
}

/* CTA do wizard "Montar prova" (ver _renderizar_montar_prova em
   cartao_resposta.py) quando a casca sorteada é "bilhete" -- o botão
   de confirmar vira âmbar em vez do lima padrão de type="primary",
   pra bater com a cor do bilhete no mockup (App ENEM.dc.html, Turno 3,
   seção 3b). Mesmo truque de marcador-irmão de sempre
   (.grade-blocos/.ex-desktop-cols): só afeta o PRÓXIMO botão renderizado,
   não qualquer st.button("...", type="primary") do resto do app. */
div.montar-prova-cta-bilhete ~ div[data-testid="stButton"] button {
    background: var(--tema-amber) !important;
    border-color: var(--tema-amber-shadow) !important;
    color: #3D2C00 !important;
    box-shadow: 0 5px 0 var(--tema-amber-shadow) !important;
}

/* Tabela própria (ver tabela_html() abaixo) -- substitui st.dataframe()
   nos 5 lugares que só mostram dado (nunca ordenam/selecionam célula)
   porque st.dataframe é desenhado em <canvas> (glide-data-grid, desde
   Streamlit ~1.19) com as cores vindas de .streamlit/config.toml
   assadas nos pixels do canvas -- confirmado checando a assinatura de
   st.dataframe() (sem parâmetro "theme" nenhum nesta versão) e o fato
   de já não existir NENHUMA regra de CSS pra ele em nenhum dos dois
   arquivos de tema deste projeto até agora. Isso significa que
   NENHUMA quantidade de CSS consegue fazer st.dataframe() acompanhar
   o toggle claro/escuro -- ele ficaria travado nas cores do config.
   toml (escuro) pra sempre, mesmo com o resto da página clara. <table>
   normal (HTML de verdade) não tem esse problema. */
.tabela-tema {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    margin-bottom: 0.5rem;
}
.tabela-tema th {
    text-align: left;
    font-weight: 800;
    font-size: 11.5px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--tema-ink-3);
    border-bottom: 1px solid var(--tema-border-2);
    padding: 8px 10px;
}
.tabela-tema td {
    padding: 8px 10px;
    border-bottom: 1px solid var(--tema-border);
    color: var(--tema-ink);
}
.tabela-tema tr:last-child td { border-bottom: none; }

/* Calendário de ofensiva: quadradinhos desenhados via CSS (não emoji)
   pra cor bater exatamente com o tema, em vez de depender de como o
   emoji 🟩/⬜ é renderizado pela fonte do sistema. */
/* !important porque o markdown do Streamlit encaixa isso dentro de um
   wrapper com regra própria de display mais específica que uma classe
   solta -- sem isso, os quadrados colapsam pra altura zero. */
div.app-streak-calendar {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    margin: 0.4rem 0 0.2rem !important;
}
.app-streak-calendar span {
    width: 18px !important;
    height: 18px !important;
    border-radius: 6px !important;
    display: inline-block !important;
}
.app-streak-calendar .dia-inativo {
    background: var(--tema-surface) !important;
    border: 1px solid var(--tema-border) !important;
}
.app-streak-calendar .dia-ativo {
    background: var(--tema-lime) !important;
    border: 1px solid var(--tema-lime-shadow) !important;
}

/* Blocos que o Streamlit monta com st.container(border=True) (ex: a
   folha do enunciado na página "Prova com enunciado (beta)") --
   mesmo card escuro secundário dos formulários, pra tudo (form,
   container, expander) parecer a mesma família de "cartão". Raio 22px
   = token "card" do handoff. */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--tema-surface);
    border: 1px solid var(--tema-border);
    border-radius: 22px;
}

/* Barra de progresso NATIVA do Streamlit (st.progress), retemada pros
   tokens do handoff -- trilho em --tema-surface-3, preenchimento lima
   por padrão. Usar dentro de um st.container com a classe utilitária
   .progresso-violeta quando o handoff pede preenchimento violeta (ex:
   a missão "Foco em matéria" -- ver README, seção Home) em vez de
   inventar uma barra de progresso em HTML puro. */
div[data-testid="stProgress"] > div > div {
    background: var(--tema-surface-3) !important;
    border-radius: 999px !important;
    height: 10px !important;
}
div[data-testid="stProgress"] > div > div > div {
    background: var(--tema-lime) !important;
    border-radius: 999px !important;
}
.progresso-violeta div[data-testid="stProgress"] > div > div > div {
    background: var(--tema-violet) !important;
}
.progresso-coral div[data-testid="stProgress"] > div > div > div {
    background: var(--tema-coral) !important;
}

/* Pill de status (streak, rank, XP, kicker de matéria) -- pedaço
   ATÔMICO de HTML (só o selo, nunca a tela inteira), estilizado por
   classe em vez de estilo inline repetido em cada call site. Ver
   pilula_html() abaixo. */
.pilula {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 9px 15px;
    border-radius: 999px;
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    font-size: 14px;
    border: 1px solid transparent;
}
.pilula-neutra { background: var(--tema-surface); border-color: var(--tema-border-2); color: var(--tema-ink-3); }
.pilula-lima { background: var(--tema-lime); color: var(--tema-on-lime); }
.pilula-ambar { background: var(--tema-amber-bg); border-color: var(--tema-amber-border); color: var(--tema-amber); }
.pilula-coral { background: #3A1F14; border-color: var(--tema-coral-shadow); color: var(--tema-coral); }
.pilula-violeta { background: var(--tema-violet); color: var(--tema-on-violet); }

/* Badge de ícone quadrado (seletor, card de missão) -- mesmo raciocínio
   da pílula: componente atômico reutilizável, não tela inteira em HTML.
   Ver emblema_html() abaixo. */
.emblema {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    font-size: 15px;
}

/* Mascote "Pipoco" (ver mascote_html() abaixo) -- gatinho, MESMA
   implementação conceitual do componente mobile (ver
   mobile/src/components/mascote.tsx): corpo com sombra sólida 3D via
   boxShadow offset sem blur (CSS de verdade tem isso nativo, não
   precisa de duas camadas empilhadas como o RN antigo precisava), e
   as orelhas/nariz via border-trick (par de bordas transparentes +
   uma colorida = triângulo, mesmo truque, funciona em qualquer motor
   CSS). Substituiu o desenho anterior (um passarinho verde, "bico" e
   "tufo" de pena) -- a nomenclatura das classes ficou por conveniência
   (evita renomear todo o arquivo por causa de uma troca visual), mas
   NENHUMA delas desenha mais bico/pena. */
.pipo-root { position: relative; flex: 0 0 auto; }
.pipo-orelha { position: absolute; top: 0; width: 33px; height: 35px; }
.pipo-orelha-fora { width: 0; height: 0; border-left: 16.5px solid transparent; border-right: 16.5px solid transparent; border-bottom: 35px solid; }
.pipo-orelha-dentro { position: absolute; left: 9.5px; top: 13px; opacity: .8; width: 0; height: 0; border-left: 7px solid transparent; border-right: 7px solid transparent; border-bottom: 18px solid; }
.pipo-corpo-sombra, .pipo-corpo { position: absolute; left: 8px; top: 14px; width: 88px; height: 84px; border-radius: 50% 50% 44% 44% / 56% 56% 44% 44%; }
.pipo-corpo { overflow: hidden; }
.pipo-olho { position: absolute; width: 27px; height: 27px; border-radius: 50%; background: #F4F7FA; display: flex; align-items: center; justify-content: center; overflow: hidden; top: 34px; }
.pipo-pupila { width: 9.5px; height: 18px; border-radius: 4.75px; background: #141821; }
.pipo-palpebra { position: absolute; left: 0; top: 0; width: 27px; border-bottom: 2.5px solid; }
.pipo-nariz { position: absolute; left: 50%; top: 63px; margin-left: -7.5px; width: 0; height: 0; border-left: 7.5px solid transparent; border-right: 7.5px solid transparent; border-top: 11px solid; }
.pipo-bochecha { position: absolute; top: 70px; width: 15px; height: 9px; border-radius: 7.5px; background: rgba(255,143,163,.5); }
.pipo-bigode { position: absolute; width: 28px; height: 2.5px; border-radius: 999px; }
.pipo-boca-fechada { position: absolute; left: 50%; top: 74px; margin-left: -9.5px; width: 19px; height: 9px; border-radius: 0 0 999px 999px; border: 2.5px solid; border-top: 0; background: transparent; }
.pipo-boca-aberta { position: absolute; left: 50%; top: 75px; margin-left: -10.5px; width: 21px; height: 15px; border-radius: 0 0 999px 999px; background: #8C3448; }
.pipo-coleira { position: absolute; left: 22px; top: 60px; width: 60px; height: 11px; border-radius: 6px; z-index: 2; }
.pipo-coleira-fivela { position: absolute; left: 50%; top: 1.5px; margin-left: -4px; width: 8px; height: 8px; border-radius: 4px; background: rgba(255,255,255,.85); }
</style>
"""


# Tokens do modo claro (--tema-bg/--tema-ink/--tema-lime...) --
# MESMOS valores e MESMO raciocínio de contraste WCAG da versão gêmea
# em enem_theme.py (_CSS_CLARO lá) -- os dois arquivos não podem
# compartilhar um único bloco de texto porque usam sufixo diferente pro
# token de sombra (--tema-lime-shadow aqui vs --lime-sh lá), mas os
# VALORES em si (calculados uma vez, ver comentário lá) são idênticos;
# mantenha os dois em sincronia se um mudar. Só o nome do token muda,
# nunca o valor.
_CSS_CLARO = """
<style>
:root {
    color-scheme: light;
    --tema-bg: #FAFAFB;
    --tema-surface: #FFFFFF;
    --tema-surface-2: #F1F2F5;
    --tema-surface-3: #E6E8EE;
    --tema-border: #E3E5EB;
    --tema-border-2: #D3D6DF;
    --tema-ink: #171B24;
    --tema-ink-2: #565E70;
    --tema-ink-3: #7E8697;
    --tema-lime: #4FAE12;
    --tema-lime-shadow: #2F7D0E;
    --tema-coral: #C5401F;
}
/* `--tema-bg` acima nunca tocava a tela de verdade: o fundo real da
   página vem de `config.toml`'s `backgroundColor` (#0A0C10), lido UMA
   vez na subida do servidor e travado (não dá pra mudar em runtime,
   ver core/CLAUDE.md) -- sem esta regra, o toggle "Modo claro" deixava
   a gaveta de navegação clara mas o CONTEÚDO principal continuava
   preto atrás dela, um "meio-claro" quebrado (confirmado ao vivo no
   Chrome: sidebar branca, `[data-testid="stMain"]` ainda `#0A0C10`).
   `stAppViewContainer` é o pai que realmente pinta o fundo por trás de
   tudo no Streamlit 1.61 (confirmado no bundle, mesmo raciocínio já
   usado pro `stMain` acima); `stMain` também recebe a cor por
   segurança, caso alguma versão pinte ali em vez do pai. */
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--tema-bg) !important;
}
/* Gaveta de navegação: era hardcoded #12151C (deliberadamente escura
   mesmo antes do redesign, ver comentário grande em _CSS acima) --
   no modo claro ela também vira clara, senão fica uma faixa escura
   destoando de uma página clara ao lado (pior que só manter escura
   sempre, que ao menos seria uma escolha consistente -- mas já que o
   pedido é "alternar de verdade", a gaveta acompanha). */
.nav-drawer { background: var(--tema-surface) !important; }
.nav-drawer a.nav-item:hover { background: var(--tema-surface-2); }
</style>
"""


def injetar_tema(tema: str = "escuro") -> None:
    """`tema`: "escuro" (padrão, _CSS original, nunca muda) ou "claro"
    -- acrescenta por cima o bloco `_CSS_CLARO`, que redefine os MESMOS
    nomes --tema-* pros valores claros mais a cobertura de widgets
    nativos (enem_theme._css_widgets_nativos_claro) que só faz sentido
    nesse modo (ver docstring dessa função pro motivo). O bloco escuro
    em si nunca é reescrito -- zero risco de regressão no modo já
    testado, o claro é 100% aditivo."""
    css = _CSS
    if tema == "claro":
        css += _CSS_CLARO + f"<style>{enem_theme._css_widgets_nativos_claro('tema-')}</style>"
    st.markdown(css, unsafe_allow_html=True)


def navegacao_lateral(
    paginas: list[tuple[str, str, str]],
    pagina_atual: str,
    dias_restantes: int | None = None,
    pct_decorrido: float | None = None,
    tema_atual: str = "escuro",
) -> None:
    """Menu próprio (hamburguer + gaveta deslizante), substitui
    st.sidebar.radio(). A sidebar nativa do Streamlit abre FECHADA por
    padrão em tela estreita, e o botão pra reabrir ficou inacessível
    no celular do usuário mesmo depois de eu corrigir o CSS que
    escondia ele por engano -- reportado em produção múltiplas vezes,
    inclusive depois de duas reescritas com JavaScript que funcionavam
    nos meus próprios testes (ver comentário no bloco de CSS pro
    porquê da versão atual não usar JS nenhum). Em vez de continuar
    caçando comportamento responsivo interno do Streamlit
    que eu não consigo testar de verdade nesta sessão (sem jeito de
    simular celular aqui), a navegação virou links puros
    (?pagina=chave, lidos via st.query_params em cartao_resposta.py) +
    gaveta CSS -- funciona igual em qualquer largura de tela, e dá pra
    verificar via DOM sem precisar de viewport estreito de verdade.

    `paginas`: lista de (chave, emoji, rótulo) -- o emoji é ignorado de
    propósito (2a rodada do handoff, bug #3: "nunca emoji", e o mockup
    de sidebar do handoff -- README, seção Desktop -- não usa ícone
    nenhum por item, só o texto e a pill lima no item ativo). Mantido
    na assinatura de _PAGINAS só pra não quebrar quem ainda lê aquela
    tupla em outro lugar. `pagina_atual`: chave da página selecionada
    agora, só pra destacar no menu. `dias_restantes`/`pct_decorrido`
    alimentam o card de rodapé (real, vem de db.plano_periodizacao() no
    caller) -- opcionais pra não quebrar quem já chamava sem eles.

    `tema_atual`: "escuro" ou "claro" -- precisa entrar em TODO link
    daqui (inclusive os de navegação normal, não só o botão de trocar
    tema), senão clicar em qualquer item do menu voltaria pro escuro
    (o padrão de `st.query_params.get`) mesmo com o claro ativado --
    a escolha de tema não vive em session_state, vive na própria URL
    (?tema=claro), mesmo raciocínio zero-JS de `?pagina=` -- então cada
    link precisa carregar os DOIS parâmetros adiante."""
    itens_html = "".join(
        f'<a href="?pagina={chave}&tema={tema_atual}" target="_self" '
        f'class="nav-item{" ativo" if chave == pagina_atual else ""}">{rotulo}</a>'
        for chave, _emoji, rotulo in paginas
    )
    outro_tema = "claro" if tema_atual == "escuro" else "escuro"
    # Ícone bate com o DESTINO (o que o clique faz), não o estado atual
    # -- "sol" ao lado do texto "Modo claro" (não "lua"), senão ícone e
    # rótulo pareceriam contradizer um ao outro.
    icone_tema = enem_theme.icon("sun" if outro_tema == "claro" else "moon", 15)
    rotulo_tema = "Modo claro" if tema_atual == "escuro" else "Modo escuro"
    toggle_tema_html = (
        f'<a href="?pagina={pagina_atual}&tema={outro_tema}" target="_self" class="nav-item nav-toggle-tema">'
        f'{icone_tema}<span>{rotulo_tema}</span></a>'
    )
    rodape_html = ""
    if dias_restantes is not None:
        pct = max(0.0, min(1.0, pct_decorrido or 0.0)) * 100
        rodape_html = (
            '<div class="nav-footer">'
            f'  <div class="nav-footer-label">{dias_restantes} dias até o ENEM</div>'
            f'  <div class="nav-footer-track"><div class="nav-footer-fill" style="width:{pct:.0f}%"></div></div>'
            '</div>'
        )
    # Tudo dentro de UM <div class="nav-root">: o parser de markdown do
    # Streamlit trata <input>/<label> soltos como conteúdo inline e os
    # embrulha num <p> automático, mas <nav> (bloco) escapa desse <p> --
    # quebra a relação de irmão que o seletor CSS ~ depende. Um <div>
    # envolvendo tudo é claramente bloco, então o parser passa o
    # conteúdo interno direto, sem fragmentar (confirmado via DOM antes
    # de existir esse <div>: checkbox e nav-drawer não eram irmãos).
    st.markdown(
        '<div class="nav-root">'
        '<input type="checkbox" id="nav-toggle" class="nav-toggle-checkbox" aria-label="Abrir menu">'
        '<label for="nav-toggle" class="nav-hamburger">☰</label>'
        '<label for="nav-toggle" class="nav-overlay"></label>'
        '<nav class="nav-drawer">'
        # "Enem" em vez do genérico "Menu" -- pedido explícito do
        # usuário, marcado como provisório por ele mesmo ("por
        # enquanto"): a gaveta agora é uma sidebar fixa sempre visível
        # em telas largas (ver bloco @media acima), então o topo dela
        # passou a fazer o papel de "marca" do app, não só de rótulo de
        # seção -- um nome de verdade ainda não foi decidido.
        '<div class="nav-title">Enem</div>'
        f"{itens_html}"
        f"{toggle_tema_html}"
        f"{rodape_html}"
        "</nav>"
        "</div>",
        unsafe_allow_html=True,
    )


# Ícones copiados byte-a-byte de mobile/src/components/tab-bar.tsx
# (ITENS_NAV/ICONES/COR_ATIVA de lá) -- fonte de verdade, não o mockup
# solto: o usuário pediu explicitamente, 2026-09-11, pra bater com a
# barra de baixo do app mobile de verdade, não com um mapeamento
# inventado por tema (a 1a tentativa, comentário antigo removido daqui,
# errou nisso -- ex: bandeira virou "Provas ENEM" quando no mobile ela
# é "Trilha"). Nome interno de cada item aqui é o MESMO `nome` de
# ITENS_NAV (trilha/explorar/simulado/missoes/liga/perfil), não a chave
# de _PAGINAS -- o mapeamento pra página real do site (que o mobile não
# tem 1-pra-1, ver _PAGINA_POR_ICONE_NAV) é uma camada SEPARADA.
_ICONE_NAV: dict[str, str] = {
    "trilha": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><rect x="5.4" y="3" width="2.6" height="18.4" rx="1.2" fill="#8B93A7"/>'
        '<path d="M8.6 4h10.6l-2.7 3.7 2.7 3.7H8.6z" fill="#6EE12B"/></svg>'
    ),
    "explorar": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.6" fill="#7C5CFF"/>'
        '<path d="M16.4 7.6l-2.3 6.5-6.5 2.3 2.3-6.5z" fill="#FFFFFF"/></svg>'
    ),
    "simulado": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><rect x="3.6" y="3.4" width="16.8" height="18" rx="2.4" fill="#FFC42E"/>'
        '<rect x="8.4" y="1.5" width="7.2" height="3.6" rx="1.4" fill="#D99A16"/><rect x="6.6" y="8.6" width="10.8" height="2.2" rx="1.1" fill="#FFFFFF"/>'
        '<rect x="6.6" y="13" width="7" height="2.2" rx="1.1" fill="#FFFFFF"/></svg>'
    ),
    "missoes": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.6" fill="#FF5A45"/>'
        '<circle cx="12" cy="12" r="6" fill="#FFF1EE"/><circle cx="12" cy="12" r="2.7" fill="#FF5A45"/></svg>'
    ),
    "liga": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M6.4 3.6h11.2v4.2a5.6 5.6 0 0 1-11.2 0z" fill="#FFC42E"/>'
        '<path d="M6.4 5.2H4v1.9a3.4 3.4 0 0 0 2.4 3.2zM17.6 5.2H20v1.9a3.4 3.4 0 0 1-2.4 3.2z" fill="#D99A16"/>'
        '<rect x="10.8" y="12.6" width="2.4" height="3.9" fill="#D99A16"/><rect x="7.4" y="16.4" width="9.2" height="2.8" rx="1" fill="#FFC42E"/></svg>'
    ),
    "perfil": (
        '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M5.6 8.4L4.4 3.2l4.8 2.6zM18.4 8.4l1.2-5.2-4.8 2.6z" fill="#FDFEFF"/>'
        '<ellipse cx="12" cy="13.4" rx="8" ry="7.2" fill="#FDFEFF"/><ellipse cx="9.2" cy="12.4" rx="1.25" ry="1.6" fill="#2A3140"/>'
        '<ellipse cx="14.8" cy="12.4" rx="1.25" ry="1.6" fill="#2A3140"/><path d="M12 15.4l-1.5-1.3h3z" fill="#FF8FA3"/></svg>'
    ),
}
# Mesmas cores de mobile/tab-bar.tsx (COR_ATIVA) -- acende a borda do
# PRÓPRIO ícone quando a página está ativa (não um anel branco genérico
# como a 1a tentativa fazia) -- mesma linguagem visual dos dois apps.
_COR_ATIVA_NAV: dict[str, str] = {
    "trilha": "#6EE12B", "explorar": "#7C5CFF", "simulado": "#FFC42E",
    "missoes": "#FF5A45", "liga": "#FFC42E", "perfil": "#FDFEFF",
}
# O mobile tem 6 abas (trilha/explorar/simulado/missões/liga/perfil)
# pra 6 telas que só existem lá. O site tem 7 páginas, 3 delas sem
# equivalente nenhum no app (Admin, Guia do Estudante, Coletar vídeos)
# e 2 conceitos do mobile sem página própria aqui (Missões e Liga --
# "ilustrativo por enquanto" mesmo no mobile, ver liga.tsx). Mapeamento
# escolhido pra cobrir as 7 páginas sem repetir nenhuma, mas ENTRE OS
# QUE NÃO TÊM PÁGINA IGUAL é só o melhor encaixe possível, avise se
# quiser outra combinação:
#   trilha->cartao (mesma tela: home/trilha) -- 1-pra-1 real
#   simulado->provas_enem (mesma tela: fazer prova de verdade) -- 1-pra-1 real
#   explorar->guia (mobile explora MATÉRIAS pra estudar, mais perto do
#     Guia do Estudante do que de qualquer outra página existente)
#   perfil->analise ("Minha análise" já mostra rank/XP/streak, o mais
#     parecido com uma tela de perfil que o site tem)
#   liga->simulados (troféu/conquista -> registro de simulados feitos)
#   missoes->coletar (o encaixe mais fraco de todos -- sobrou ele,
#     Missões não tem nada parecido no site hoje)
#   admin fica de fora deste dict de propósito: não existe no mobile,
#   ganha o próprio ícone (engrenagem) fixado embaixo, ver a função.
_PAGINA_POR_ICONE_NAV: dict[str, str] = {
    "trilha": "cartao", "explorar": "guia", "simulado": "provas_enem",
    "missoes": "coletar", "liga": "simulados", "perfil": "analise",
}
_ICONE_ADMIN = (
    '<svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="#5B6472" stroke-width="2.2" stroke-linecap="round">'
    '<circle cx="12" cy="12" r="3.2"/><path d="M19.4 15a1.6 1.6 0 0 0 .32 1.77l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.6 1.6 0 0 0 15 19.4a1.6 1.6 0 0 0-1 1.47V21a2 2 0 1 1-4 0v-.09A1.6 1.6 0 0 0 9 19.4a1.6 1.6 0 0 0-1.77.32l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.6 1.6 0 0 0 4.6 15a1.6 1.6 0 0 0-1.47-1H3a2 2 0 1 1 0-4h.09A1.6 1.6 0 0 0 4.6 9a1.6 1.6 0 0 0-.32-1.77l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.6 1.6 0 0 0 9 4.6h.09A1.6 1.6 0 0 0 10 3.13V3a2 2 0 1 1 4 0v.09A1.6 1.6 0 0 0 15 4.6a1.6 1.6 0 0 0 1.77-.32l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.6 1.6 0 0 0 19.4 9v.09A1.6 1.6 0 0 0 20.87 10H21a2 2 0 1 1 0 4h-.09a1.6 1.6 0 0 0-1.47 1z"/></svg>'
)


def barra_navegacao_icones(
    paginas: list[tuple[str, str, str]],
    pagina_atual: str,
    tema_atual: str = "escuro",
) -> None:
    """Navegação real do app inteiro (App ENEM.dc.html, Turno 4, 4a) --
    SUBSTITUI navegacao_lateral() por pedido explícito do usuário,
    2026-09-11: "substitua cartão resposta, prova enem e tudo aquele
    menu por aqueles ícones", depois ajustado no mesmo dia pra bater
    com a ORDEM e o SIGNIFICADO reais da barra de baixo do app mobile
    (mobile/src/components/tab-bar.tsx) em vez de um mapeamento por
    tema inventado -- ver _ICONE_NAV/_COR_ATIVA_NAV/_PAGINA_POR_ICONE_
    NAV logo acima pro porquê de cada association. Fixa à esquerda,
    SEMPRE visível (CSS em ui_theme.py, .barra-nav-icones) -- 82px é
    estreito o bastante pra não precisar de hambúrguer/gaveta em tela
    nenhuma, eliminando de vez a classe de bug ("hambúrguer inacessível
    no celular real") que motivou toda a reescrita anterior de
    navegacao_lateral().

    Ordem: trilha, explorar, simulado, missões, liga, perfil (idêntica
    à ITENS_NAV do mobile -- perfil/mascote por ÚLTIMO, não primeiro,
    pedido explícito do usuário: "o gatinho ele tá no final"), com
    admin (engrenagem, sem equivalente no mobile) fixado embaixo de
    tudo via margin-top:auto -- mesmo papel que já tinha antes.

    Zero texto, zero emoji (mesma regra "nunca emoji" de sempre) --
    `title=` HTML nativo em cada link dá um tooltip no hover, única
    pista textual, sem virar rótulo permanente na tela."""
    def _link(nome_icone: str, pagina: str, rotulo: str) -> str:
        ativo = pagina == pagina_atual
        cor = _COR_ATIVA_NAV[nome_icone]
        estilo_ativo = f'border-color:{cor};background:#141821' if ativo else ""
        return (
            f'<a href="?pagina={pagina}&tema={tema_atual}" target="_self" title="{rotulo}" '
            f'style="{estilo_ativo}">{_ICONE_NAV[nome_icone]}</a>'
        )

    rotulo_por_pagina = {chave: rotulo for chave, _emoji, rotulo in paginas}
    ordem_icones = ["trilha", "explorar", "simulado", "missoes", "liga", "perfil"]
    itens_html = "".join(
        _link(nome, _PAGINA_POR_ICONE_NAV[nome], rotulo_por_pagina.get(_PAGINA_POR_ICONE_NAV[nome], nome))
        for nome in ordem_icones
    )
    admin_ativo = pagina_atual == "admin"
    estilo_admin = "border-color:#5B6472;background:#141821" if admin_ativo else ""
    admin_html = (
        f'<a href="?pagina=admin&tema={tema_atual}" target="_self" title="Admin" '
        f'style="margin-top:auto;{estilo_admin}">{_ICONE_ADMIN}</a>'
    )
    st.markdown(
        f'<div class="barra-nav-icones">{itens_html}{admin_html}</div>',
        unsafe_allow_html=True,
    )


def hero(titulo: str, tagline: str = "", icone: str | None = None) -> None:
    """Título de página. Sem `icone`: título + régua lima embaixo,
    opcionalmente com uma legenda ao lado (comportamento original,
    ainda usado por quem não passa ícone). Com `icone` (nome de
    enem_theme._ICONS, ex: "calendar", "target", "file-text"): badge
    quadrado violeta + título Baloo 2 + legenda embaixo -- mesma
    linguagem do cabeçalho da Home (enem_theme.header()), aplicada às
    páginas fora do redesign trilha/home (Provas ENEM, Prova com
    enunciado, Calendário, Objetivos, etc)."""
    if icone:
        st.markdown(
            f'<div class="app-hero-badged">'
            f'  <div class="app-hero-badge">{enem_theme.icon(icone, 22, "#F1EEFF")}</div>'
            f'  <div><h1>{titulo}</h1>'
            + (f'<span class="tagline">{tagline}</span>' if tagline else "")
            + "</div></div>",
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        f'<div class="app-hero"><h1>{titulo}</h1>'
        + (f'<span class="tagline">{tagline}</span>' if tagline else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def tabela_html(linhas: list[dict]) -> None:
    """Tabela só-leitura própria (classe .tabela-tema), no lugar de
    st.dataframe() -- ver o comentário grande em _CSS sobre por que
    st.dataframe() nunca consegue acompanhar o toggle claro/escuro
    (desenhado em canvas com cor vinda do config.toml, travado). Só
    faz sentido pra tabela que já era puramente exibição (nenhuma das
    5 chamadas trocadas por isto usava ordenação/seleção de célula).
    `linhas`: lista de dict com as MESMAS chaves em todo item (usa as
    chaves do primeiro item como cabeçalho, na ordem que vierem)."""
    if not linhas:
        return
    colunas = list(linhas[0].keys())
    cabecalho = "".join(f"<th>{html.escape(str(c))}</th>" for c in colunas)
    corpo = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(linha.get(c, '')))}</td>" for c in colunas) + "</tr>"
        for linha in linhas
    )
    st.markdown(
        f'<table class="tabela-tema"><thead><tr>{cabecalho}</tr></thead>'
        f'<tbody>{corpo}</tbody></table>',
        unsafe_allow_html=True,
    )


def pilula_html(texto: str, variante: str = "neutra", icone: str = "") -> str:
    """Selo/badge pequeno (streak, rank, kicker de matéria) -- pedaço
    ATÔMICO de HTML, nunca uma tela inteira (ver design_handoff_enem_
    gamificado/README.md: "prefira injetar um bloco de CSS e usar
    containers do Streamlit, em vez de montar telas inteiras como
    string de HTML" -- isto aqui é o tipo de HTML pequeno e pontual que
    ainda faz sentido, porque Streamlit não tem um componente nativo de
    "pill"). `variante` é uma das classes .pilula-* já definidas em
    _CSS (neutra/lima/ambar/coral/violeta)."""
    return f'<span class="pilula pilula-{variante}">{icone + " " if icone else ""}{texto}</span>'


def emblema_html(icone: str, bg: str, cor: str, tamanho: int = 32, raio: int = 11) -> str:
    """Badge de ícone quadrado colorido (usado nos seletores da Home e
    nos cards de missão) -- mesmo raciocínio de pilula_html(): elemento
    atômico, não tela inteira."""
    return (
        f'<span class="emblema" style="width:{tamanho}px;height:{tamanho}px;'
        f'border-radius:{raio}px;background:{bg};color:{cor}">{icone}</span>'
    )


_HUMORES_PIPO = {
    "happy": {"tilt": 0, "pupil_y": 0, "pupil_w": 9.5, "ear_tilt": 7, "fechado": False, "tail_top": 62, "tail_rot": -16},
    "cheer": {"tilt": -7, "pupil_y": -2, "pupil_w": 12, "ear_tilt": -4, "fechado": False, "tail_top": 40, "tail_rot": -54},
    "sad": {"tilt": 5, "pupil_y": 4, "pupil_w": 9.5, "ear_tilt": 32, "fechado": True, "tail_top": 62, "tail_rot": -16},
    "sleep": {"tilt": 0, "pupil_y": 0, "pupil_w": 9.5, "ear_tilt": 7, "fechado": True, "tail_top": 62, "tail_rot": -16},
}


def mascote_html(
    mood: str = "happy",
    color: str = "#FDFEFF",
    shadow: str = "#C4CFDB",
    beak: str = "#FF8FA3",
    size: float = 1.0,
    pattern: str = "solido",
    patch: str | None = None,
    collar: str | None = None,
) -> str:
    """"Pipoco", o mascote (gatinho branco) -- porta direta da versão
    ATUAL de Mascote.dc.html (projeto de design do usuário no Claude
    Design, importado via DesignSync), MESMA implementação conceitual
    do componente React Native (ver mobile/src/components/mascote.tsx,
    fonte de verdade -- qualquer mudança de anatomia/humor deveria ser
    feita lá primeiro e replicada aqui) -- aqui como uma string de HTML
    puro (divs com estilo inline + classes do bloco .pipo-* em _CSS),
    pra injetar via st.markdown(mascote_html(...), unsafe_allow_html=True).
    Substitui o desenho anterior (um passarinho verde -- `color`/
    `shadow`/`beak` tinham default lima/verde-escuro/âmbar, os tokens de
    MARCA do app, não do bichinho; os novos defaults são os do gato
    branco, mesmos valores de mobile/src/constants/brand.ts).

    `beak` (nome mantido por compatibilidade, ver mesma nota em
    mascote.tsx) tinge o nariz e a parte interna da orelha, não desenha
    mais bico. `pattern`/`patch`/`collar`: mesmas variações de pelagem
    do componente mobile (ver docstring de lá pro porquê) -- só
    'tuxedo' e 'patches' têm desenho aqui, qualquer outro valor cai no
    'solido' (cor única, comportamento de sempre).

    Não retorna um componente Streamlit de verdade (é só HTML), então
    quem chama precisa envolver com st.markdown(..., unsafe_allow_html=True)
    -- deliberado, mantém esta função pura/testável sem depender de
    st.* internamente."""
    humor = _HUMORES_PIPO.get(mood, _HUMORES_PIPO["happy"])
    fechado = humor["fechado"]
    altura_palpebra = 16 if mood == "sleep" else 14
    cor_orelha = patch if (pattern == "tuxedo" and patch) else color

    palpebra_html = (
        f'<div class="pipo-palpebra" style="height:{altura_palpebra}px;background:{color};border-bottom-color:{shadow}"></div>'
        if fechado else ""
    )
    sparkle_html = (
        '<div style="position:absolute;right:-10px;top:-6px;width:15px;height:15px;'
        'transform:rotate(45deg);border-radius:4px;background:#FFC42E"></div>'
        if mood == "cheer" else ""
    )
    boca_html = (
        '<div class="pipo-boca-aberta"></div>' if mood == "cheer"
        else f'<div class="pipo-boca-fechada" style="border-color:{shadow}"></div>'
    )
    manchas_html = ""
    if pattern == "tuxedo" and patch:
        # "Capuz": só o terço de cima do corpo, mesmo raio do corpo em
        # cima -- lê como pelagem escura na cabeça/costas sobre um corpo
        # claro. Mesma abordagem de mobile/src/components/mascote.tsx.
        manchas_html = f'<div style="position:absolute;left:0;top:0;right:0;height:32px;background:{patch};border-radius:44px 44px 0 0"></div>'
    elif pattern == "patches" and patch:
        manchas_html = (
            f'<div style="position:absolute;left:-6px;top:-4px;width:34px;height:30px;border-radius:16px;'
            f'background:{patch};transform:rotate(-12deg)"></div>'
            f'<div style="position:absolute;right:-8px;bottom:-6px;width:30px;height:26px;border-radius:14px;'
            f'background:{patch};transform:rotate(10deg)"></div>'
        )
    coleira_html = (
        f'<div class="pipo-coleira" style="background:{collar}"><div class="pipo-coleira-fivela"></div></div>'
        if collar else ""
    )
    bigodes_html = "".join(
        f'<div class="pipo-bigode" style="{lado}:-8px;top:{63 + i * 8}px;background:{shadow};'
        f'transform:rotate({(1 if lado == "left" else -1) * angulo}deg)"></div>'
        for lado in ("left", "right")
        for i, angulo in enumerate((13, 0, -13))
    )

    # Div de fora com o tamanho VISUAL de verdade ({size}x104px), .pipo-root
    # por dentro continua no tamanho nativo 104x104 (todo o resto deste
    # desenho usa offsets em px pensados pra essa referência) só encolhido
    # por transform:scale -- que NUNCA muda o espaço reservado em layout,
    # só o que é pintado na tela. Sem este wrapper, um mascote com
    # size<1 dentro de uma linha flex (mascote + texto ao lado, como no
    # cartão "Seu bilhete") reservava 104px de largura mesmo aparentando
    # ser bem menor -- sobrava pouco espaço de verdade pro texto vizinho,
    # que quebrava letra por letra (bug real, achado ao vivo no Chrome).
    # transform-origin:top left (em vez do padrão "center") é o que faz
    # o conteúdo encolhido bater exatamente com o canto (0,0) do
    # wrapper, em vez de encolher pro centro e sobrar espaço torto.
    html = f"""
<div style="width:{104 * size:.2f}px;height:{104 * size:.2f}px;flex:0 0 auto">
<div class="pipo-root" style="width:104px;height:104px;transform:scale({size}) rotate({humor['tilt']}deg);transform-origin:top left">
  <div style="position:absolute;right:-18px;top:{humor['tail_top']}px;width:46px;height:13px;border-radius:999px;
       background:{color};box-shadow:0 3px 0 {shadow};transform:rotate({humor['tail_rot']}deg);transform-origin:left center"></div>

  <div class="pipo-orelha" style="left:8px;transform:rotate(-{humor['ear_tilt']}deg);transform-origin:center bottom">
    <div class="pipo-orelha-fora" style="border-bottom-color:{cor_orelha}"></div>
    <div class="pipo-orelha-dentro" style="border-bottom-color:{beak}"></div>
  </div>
  <div class="pipo-orelha" style="right:8px;transform:rotate({humor['ear_tilt']}deg);transform-origin:center bottom">
    <div class="pipo-orelha-fora" style="border-bottom-color:{cor_orelha}"></div>
    <div class="pipo-orelha-dentro" style="border-bottom-color:{beak}"></div>
  </div>

  <div class="pipo-corpo-sombra" style="background:{shadow}"></div>
  <div class="pipo-corpo" style="background:{color}">
    {manchas_html}
    <div style="position:absolute;left:18px;top:26px;width:52px;height:38px;border-radius:26px;
         background:rgba(255,255,255,.5)"></div>
  </div>
  {coleira_html}

  <div class="pipo-olho" style="left:17px">
    <div class="pipo-pupila" style="width:{humor['pupil_w']}px;border-radius:{humor['pupil_w'] / 2}px;transform:translateY({humor['pupil_y']}px)"></div>
    {palpebra_html}
  </div>
  <div class="pipo-olho" style="right:17px">
    <div class="pipo-pupila" style="width:{humor['pupil_w']}px;border-radius:{humor['pupil_w'] / 2}px;transform:translateY({humor['pupil_y']}px)"></div>
    {palpebra_html}
  </div>

  {bigodes_html}
  <div class="pipo-nariz" style="border-top-color:{beak}"></div>
  {boca_html}
  <div class="pipo-bochecha" style="left:11px"></div>
  <div class="pipo-bochecha" style="right:11px"></div>
  {sparkle_html}
</div>
</div>
"""
    # Achatado pra uma linha só (sem quebra/indentação) antes de devolver:
    # este HTML quase sempre é interpolado DENTRO de outro st.markdown(...,
    # unsafe_allow_html=True) maior (cena da mesa, bilhete, cards de área).
    # Uma linha em branco no meio encerra o "HTML block" do CommonMark mais
    # cedo -- o resto do markdown pai volta a ser parseado como texto comum,
    # onde qualquer linha com 4+ espaços de indentação (comum em f-string
    # Python) vira bloco de código literal em vez de HTML de verdade. Já
    # aconteceu de verdade: o cartão "SEU BILHETE" e o "mesa"/"área" ao
    # lado mostravam pedaços de `<div ...>` crus com botão "Copy to
    # clipboard" bem depois de qualquer chamada a mascote_html(). Uma só
    # linha nunca aciona nem a regra de linha-em-branco nem a de
    # indentação, então é imune ao mesmo bug em qualquer contexto onde for
    # colada.
    return " ".join(linha.strip() for linha in html.splitlines() if linha.strip())
