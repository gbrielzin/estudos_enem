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

/* Título principal com leve brilho neon -- só aqui, não em todo H1,
   pra não cansar a vista em telas com várias seções. */
.app-hero {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.25rem;
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


def injetar_tema() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(titulo: str, tagline: str = "") -> None:
    """Título de página com o leve brilho neon do tema, opcionalmente
    com uma legenda ao lado (ex: contagem regressiva pro ENEM)."""
    st.markdown(
        f'<div class="app-hero"><h1>{titulo}</h1>'
        + (f'<span class="tagline">{tagline}</span>' if tagline else "")
        + "</div>",
        unsafe_allow_html=True,
    )
