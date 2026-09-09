"""
ui_theme.py — CSS complementar ao tema em .streamlit/config.toml.

O config.toml cobre cor/fonte/raio via API oficial do Streamlit (robusto
entre versões). O que ele não alcança — esconder o rodapé "Made with
Streamlit", dar cara de cartão pras métricas, estilizar as bolhas de
resposta A-E, desenhar o mascote "Pipo" — fica aqui, isolado, pra não
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
/* Design tokens -- vêm de design_handoff_enem_gamificado/README.md
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
   Raio 22px = token "card" do handoff (design_handoff_enem_gamificado/
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
   propósito pra não competir visualmente com as 5 letras de verdade. */
div.grade-blocos ~ div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] [role="radiogroup"] {
    gap: 5px !important;
}
div.grade-blocos ~ div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] [role="radiogroup"] > label {
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
div.grade-blocos ~ div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: var(--tema-lime);
    border-color: var(--tema-lime-shadow);
    box-shadow: 0 2px 0 var(--tema-lime-shadow);
    color: var(--tema-on-lime);
}
div.grade-blocos ~ div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] [role="radiogroup"] > label:first-child {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    font-size: 10px;
    opacity: .6;
    align-self: center;
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

/* Mascote "Pipo" (ver mascote_html() abaixo) -- corpo arredondado com
   sombra sólida 3D via duas camadas empilhadas (mesma técnica do
   mobile, ver mobile/src/components/mascote.tsx e trilha-path.tsx),
   já que CSS puro não tem um jeito nativo de "box-shadow offset sólido
   sem blur" que funcione igual em toda situação de fundo. */
.pipo-root { position: relative; flex: 0 0 auto; }
.pipo-tufo { position: absolute; width: 26px; height: 26px; }
.pipo-corpo-sombra, .pipo-corpo { position: absolute; left: 8px; width: 88px; height: 84px; border-radius: 40px; }
.pipo-corpo { overflow: hidden; }
.pipo-olho { position: absolute; width: 27px; height: 27px; border-radius: 50%; background: #FDFEFF; display: flex; align-items: center; justify-content: center; overflow: hidden; top: 33px; }
.pipo-pupila { width: 13px; height: 13px; border-radius: 50%; background: #141821; }
.pipo-palpebra { position: absolute; left: 0; top: 0; width: 27px; }
.pipo-bico { position: absolute; left: 50%; top: 63px; border-radius: 3px; transform: rotate(45deg); }
.pipo-bochecha { position: absolute; top: 68px; width: 14px; height: 9px; border-radius: 50%; background: rgba(255,120,110,.42); }
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
        '<div class="nav-title">Menu</div>'
        f"{itens_html}"
        f"{toggle_tema_html}"
        f"{rodape_html}"
        "</nav>"
        "</div>",
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
    "happy": {"tilt": 0, "pupil_y": 0, "beak": 17, "fechado": False},
    "cheer": {"tilt": -7, "pupil_y": -2, "beak": 22, "fechado": False},
    "sad": {"tilt": 5, "pupil_y": 4, "beak": 13, "fechado": True},
    "sleep": {"tilt": 0, "pupil_y": 0, "beak": 17, "fechado": True},
}


def mascote_html(
    mood: str = "happy",
    color: str = "#6EE12B",
    shadow: str = "#3F8F14",
    beak: str = "#FFC42E",
    size: float = 1.0,
) -> str:
    """"Pipo", o mascote -- porta direta de Mascote.dc.html (projeto de
    design do usuário no Claude Design, importado via DesignSync), MESMA
    implementação conceitual do componente React Native (ver
    mobile/src/components/mascote.tsx) -- aqui como uma string de HTML
    puro (divs com estilo inline + classes do bloco .pipo-* em _CSS),
    pra injetar via st.markdown(mascote_html(...), unsafe_allow_html=True).

    Não retorna um componente Streamlit de verdade (é só HTML), então
    quem chama precisa envolver com st.markdown(..., unsafe_allow_html=True)
    -- deliberado, mantém esta função pura/testável sem depender de
    st.* internamente."""
    humor = _HUMORES_PIPO.get(mood, _HUMORES_PIPO["happy"])
    fechado = humor["fechado"]
    altura_palpebra = 16 if mood == "sleep" else 14
    palpebra_html = (
        f'<div class="pipo-palpebra" style="height:{altura_palpebra}px;background:{color};'
        f'border-bottom:2px solid {shadow}"></div>'
        if fechado else ""
    )
    sparkle_html = (
        f'<div style="position:absolute;right:-8px;top:-10px;width:15px;height:15px;'
        f'transform:rotate(45deg);border-radius:4px;background:{beak}"></div>'
        if mood == "cheer" else ""
    )
    return f"""
<div class="pipo-root" style="width:104px;height:104px;transform:scale({size}) rotate({humor['tilt']}deg)">
  <div class="pipo-tufo" style="left:6px;top:2px;transform:rotate(-18deg);background:{shadow};
       border-radius:50% 50% 40% 60%"></div>
  <div class="pipo-tufo" style="right:6px;top:2px;transform:rotate(18deg);background:{shadow};
       border-radius:50% 50% 60% 40%"></div>
  <div class="pipo-corpo-sombra" style="top:22px;background:{shadow}"></div>
  <div class="pipo-corpo" style="top:14px;background:{color}">
    <div style="position:absolute;left:8px;top:20px;width:56px;height:44px;border-radius:24px;
         background:rgba(255,255,255,.26)"></div>
    <div style="position:absolute;left:2px;top:-8px;width:30px;height:22px;border-radius:15px;
         background:rgba(255,255,255,.22)"></div>
  </div>
  <div class="pipo-olho" style="left:17px">
    <div class="pipo-pupila" style="transform:translateY({humor['pupil_y']}px)"></div>
    {palpebra_html}
  </div>
  <div class="pipo-olho" style="right:17px">
    <div class="pipo-pupila" style="transform:translateY({humor['pupil_y']}px)"></div>
    {palpebra_html}
  </div>
  <div class="pipo-bochecha" style="left:11px"></div>
  <div class="pipo-bochecha" style="right:11px"></div>
  <div class="pipo-bico" style="width:{humor['beak']}px;height:{humor['beak']}px;
       margin-left:-{humor['beak'] / 2}px;background:{beak}"></div>
  {sparkle_html}
</div>
"""
