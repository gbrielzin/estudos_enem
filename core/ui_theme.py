"""
ui_theme.py — CSS complementar ao tema em .streamlit/config.toml.

O config.toml cobre cor/fonte/raio via API oficial do Streamlit (robusto
entre versões). O que ele não alcança — esconder o rodapé "Made with
Streamlit", dar cara de cartão pras métricas, estilizar as bolhas de
resposta A-E — fica aqui, isolado, pra não espalhar <style> solto pelas
telas.

Chamar injetar_tema() uma vez, no topo do entrypoint (__main__ de
cartao_resposta.py). Streamlit reprocessa o script inteiro a cada
interação, então isso roda de novo a cada rerun — é barato (só injeta
uma tag <style>), não precisa de cache.
"""
import streamlit as st

_CSS = """
<style>
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
   embrulhado num único bloco. */
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
    background: #131C13;
    border: 1px solid #245C2E;
    border-radius: 0.5rem;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    line-height: 1;
    color: #E7FFEA;
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
    background: #0A0F0A;
    border-right: 1px solid #245C2E;
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
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: #E7FFEA;
    padding: 0 1.3rem 1rem;
    letter-spacing: 0.02em;
}

.nav-drawer a.nav-item {
    display: block;
    padding: 0.75rem 1.3rem;
    color: #C9E8CE;
    text-decoration: none;
    font-size: 0.96rem;
    border-left: 3px solid transparent;
    transition: background 0.15s ease, border-color 0.15s ease;
}
.nav-drawer a.nav-item:hover {
    background: rgba(57, 255, 20, 0.08);
}
.nav-drawer a.nav-item.ativo {
    color: #39FF14;
    border-left-color: #39FF14;
    background: rgba(57, 255, 20, 0.1);
    font-weight: 600;
}

/* Título principal com leve brilho neon -- só aqui, não em todo H1,
   pra não cansar a vista em telas com várias seções. */
.app-hero {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.25rem;
    margin-top: 2.5rem;
}
.app-hero h1 {
    margin: 0;
    text-shadow: 0 0 18px rgba(57, 255, 20, 0.45);
}
.app-hero span.tagline {
    color: #8FE39A;
    font-size: 0.95rem;
    opacity: 0.85;
}

/* Cards de métrica (Rank / XP / Ofensiva) com borda e brilho sutil,
   em vez do bloco chapado padrão do st.metric. */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(57,255,20,0.07), rgba(57,255,20,0.02));
    border: 1px solid #245C2E;
    border-radius: 0.75rem;
    padding: 1rem 1.1rem;
    box-shadow: 0 0 24px rgba(57, 255, 20, 0.06);
}
div[data-testid="stMetricLabel"] {
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    opacity: 0.75;
}

/* Botões primários com glow no hover -- feedback tátil que reforça o
   tema "terminal/neon" em vez do botão liso padrão. */
button[kind="primary"], button[kind="primaryFormSubmit"] {
    font-weight: 600;
    transition: box-shadow 0.15s ease, transform 0.05s ease;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.55);
}
button[kind="primary"]:active, button[kind="primaryFormSubmit"]:active {
    transform: scale(0.98);
}

/* Formulários (o cartão-resposta inteiro é um st.form) com cara de
   cartão -- sem isso, a grade de questões fica "boiando" no fundo. */
div[data-testid="stForm"] {
    border: 1px solid #245C2E;
    border-radius: 0.9rem;
    padding: 1.25rem 1.25rem 0.5rem;
    background: rgba(19, 28, 19, 0.4);
}

/* Grade de resposta (A-B-C-D-E por questão): opções horizontais viram
   "bolhas" -- visual de cartão-resposta de verdade em vez de radio
   button cru. :has() é suportado no Chrome/Edge/Firefox atuais; onde
   não for, cai de volta pro radio padrão (degradação segura). */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0.3rem;
}
div[data-testid="stRadio"] label {
    border: 1px solid #245C2E;
    border-radius: 999px;
    padding: 0.15rem 0.6rem;
    margin: 0 !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}
div[data-testid="stRadio"] label:has(input:checked) {
    border-color: #39FF14;
    background: rgba(57, 255, 20, 0.12);
}

/* Separadores e expanders com a mesma linguagem de borda verde-escura,
   pra tudo parecer parte do mesmo sistema visual. */
div[data-testid="stExpander"] {
    border: 1px solid #245C2E;
    border-radius: 0.75rem;
}

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
    border-radius: 4px !important;
    display: inline-block !important;
}
.app-streak-calendar .dia-inativo {
    background: rgba(231, 255, 234, 0.06) !important;
    border: 1px solid #245C2E !important;
}
.app-streak-calendar .dia-ativo {
    background: #39FF14 !important;
    box-shadow: 0 0 8px rgba(57, 255, 20, 0.8) !important;
}
</style>
"""

# Tema claro só pra página "Prova com enunciado (beta)" -- pedido
# explícito do usuário pra parecer com o PDF do ENEM (folha branca,
# texto escuro) em vez do tema escuro verde do resto do app, enquanto
# ele lê e responde. Mira só [data-testid="stMain"] (a área de
# conteúdo principal) e o que tem DENTRO dela via herança de `color`
# (que se propaga pra filho sem cor própria, mas nunca vence uma regra
# mais específica -- ex: os links do menu (.nav-drawer a.nav-item) têm
# cor própria declarada, então não mudam) -- a gaveta/hambúrguer de
# navegação, com z-index acima de tudo e cor própria em cada regra,
# fica com o visual de sempre de propósito, é navegação, não é "a
# folha de prova". Não troca o tema inteiro do Streamlit (teria que
# mudar .streamlit/config.toml, que vale pro app inteiro, não só uma
# página) -- por isso st.success/st.warning depois de corrigir ainda
# usam o estilo pensado pro tema escuro; only a parte de LER a questão
# (o que importava pro pedido) foi ajustada.
_CSS_TEMA_CLARO_EXAME = """
<style>
[data-testid="stMain"] {
    background: #FFFFFF !important;
    color: #1A1A1A !important;
}
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] h4, [data-testid="stMain"] h5, [data-testid="stMain"] p,
[data-testid="stMain"] li, [data-testid="stMain"] span, [data-testid="stMain"] label {
    color: #1A1A1A !important;
}
[data-testid="stMain"] [data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #CCCCCC !important;
}
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: #FAFAFA !important;
    border: 1px solid #DDDDDD !important;
}
[data-testid="stMain"] div[data-testid="stRadio"] label {
    border: 1px solid #999999 !important;
    background: #FFFFFF !important;
}
[data-testid="stMain"] div[data-testid="stRadio"] label:has(input:checked) {
    border-color: #1A1A1A !important;
    background: #EAEAEA !important;
}
[data-testid="stMain"] .app-hero span.tagline {
    color: #555555 !important;
}
</style>
"""


def injetar_tema() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def injetar_tema_exame_claro() -> None:
    """Chamar SÓ na página beta de prova com enunciado, depois de
    injetar_tema() -- ver comentário de _CSS_TEMA_CLARO_EXAME."""
    st.markdown(_CSS_TEMA_CLARO_EXAME, unsafe_allow_html=True)


def navegacao_lateral(paginas: list[tuple[str, str, str]], pagina_atual: str) -> None:
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

    `paginas`: lista de (chave, emoji, rótulo). `pagina_atual`: chave
    da página selecionada agora, só pra destacar no menu."""
    itens_html = "".join(
        f'<a href="?pagina={chave}" target="_self" '
        f'class="nav-item{" ativo" if chave == pagina_atual else ""}">{emoji} {rotulo}</a>'
        for chave, emoji, rotulo in paginas
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
        '<div class="nav-title">📝 Menu</div>'
        f"{itens_html}"
        "</nav>"
        "</div>",
        unsafe_allow_html=True,
    )


def hero(titulo: str, tagline: str = "") -> None:
    """Título de página com o leve brilho neon do tema, opcionalmente
    com uma legenda ao lado (ex: contagem regressiva pro ENEM)."""
    st.markdown(
        f'<div class="app-hero"><h1>{titulo}</h1>'
        + (f'<span class="tagline">{tagline}</span>' if tagline else "")
        + "</div>",
        unsafe_allow_html=True,
    )
