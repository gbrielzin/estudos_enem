"""Tema ENEM gamificado — helpers de UI para Streamlit.

Uso:

    import enem_theme as t

    t.inject()                       # uma vez, no topo de cada página
    t.header("Banco de Questoes", streak=1, rank="S-Rank", xp=4674)
    t.missions_card([
        t.Mission("Complete sua meta diaria", "9/5 questao(oes) hoje", 1.0, "lime", done=True),
        t.Mission("Foco em geometria_espacial",
                  "Pratique geometria_espacial hoje - e sua maior prioridade agora",
                  0.02, "violet"),
    ])
    t.trilha("Optica", "Ciencias da Natureza", nodes=9, done=2, current=3)

Regra geral: widget nativo do Streamlit so onde precisa de INPUT
(selectbox, radio, button). Todo o resto - pills, cards de missao,
trilha, resultado - e HTML proprio com as classes de theme.css.
"""

import math
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).with_name("theme.css")

TONES = {
    "lime": "#6EE12B",
    "violet": "#7C5CFF",
    "amber": "#FFC42E",
    "coral": "#FF6B4A",
    "neutral": "#8B93A7",
}

# Ícones inline SVG, traço estilo Lucide (README: "nunca emoji") -- só
# os que este arquivo usa de verdade. play/lock/flame/star/sparkle/bolt
# são os MESMOS <path> do mockup aprovado (reference/App ENEM.dc.html,
# copiados literalmente, não redesenhados) pra não arriscar um ícone
# "no estilo" mas visualmente diferente do handoff; check é o único
# desenhado aqui (não aparece em nenhum estado do mockup de referência,
# que só mostra nós concluído=0), um simples check de 2 segmentos.
_ICONS = {
    "play": ('<path d="M8 5v14l11-7z"/>', "fill"),
    "check": ('<path d="M5 13l4 4L19 7"/>', "stroke"),
    "lock": ('<rect x="5" y="11" width="14" height="9" rx="3"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>', "stroke"),
    "flame": ('<path d="M12 2c1 4-3 5-3 9a3 3 0 0 0 6 0c0-1-.5-2-1-2.5 2 1 3 3 3 5.5a5 5 0 0 1-10 0c0-5 3-6 5-12z"/>', "stroke"),
    "star": ('<path d="M12 2l2.9 6.3 6.9.6-5.2 4.6 1.6 6.8L12 16.9 5.8 20.3l1.6-6.8L2.2 8.9l6.9-.6z"/>', "fill"),
    "sparkle": ('<path d="M12 2l1.9 6.3L20 10l-6.1 1.7L12 18l-1.9-6.3L4 10l6.1-1.7z"/>', "fill"),
    "bolt": ('<path d="M11 2L4 14h6l-1 8 8-12h-6z"/>', "fill"),
    # Ícones adicionados pra dar cabeçalho próprio (badge + título) às
    # páginas fora do redesign trilha/home (Provas ENEM, Prova com
    # enunciado, Calendário, Objetivos e demais) -- mesmo estilo Lucide/
    # traço 2.2px dos ícones acima, um por página em vez de reusar
    # "sparkle" em tudo. Ver ui_theme.hero(icone=...).
    "file-text": ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
                  '<path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>', "stroke"),
    "flask": ('<path d="M10 2v6.5a2 2 0 0 1-.5 1.3L4 17a2 2 0 0 0 1.6 3.3h12.8A2 2 0 0 0 20 17l-5.5-7.2a2 2 0 0 1-.5-1.3V2"/>'
              '<path d="M8.5 2h7"/><path d="M7 16h10"/>', "stroke"),
    "calendar": ('<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/>'
                 '<path d="M8 2v4"/><path d="M3 10h18"/>', "stroke"),
    "target": ('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>', "stroke"),
    "bar-chart": ('<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>', "stroke"),
    "archive": ('<rect x="2" y="4" width="20" height="5" rx="1"/>'
                '<path d="M4 9v9a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9"/><path d="M10 13h4"/>', "stroke"),
    "pen": ('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>', "stroke"),
    "link": ('<path d="M9 17H7a5 5 0 0 1 0-10h2"/><path d="M15 7h2a5 5 0 0 1 0 10h-2"/><path d="M8 12h8"/>', "stroke"),
    "tag": ('<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/>'
            '<circle cx="7.5" cy="7.5" r="1.5"/>', "stroke"),
    "shield": ('<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 '
               '6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>', "stroke"),
    "book": ('<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>', "stroke"),
    # Toggle de modo escuro/claro (ver ui_theme.navegacao_lateral).
    "sun": ('<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/>'
            '<path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
            '<path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/>'
            '<path d="m19.07 4.93-1.41 1.41"/>', "stroke"),
    "moon": ('<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>', "stroke"),
}


def icon(name: str, size: int = 16, color: str = "currentColor", stroke_width: float = 2.2) -> str:
    inner, kind = _ICONS[name]
    if kind == "fill":
        return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}">{inner}</svg>'
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )


def _css_widgets_nativos_claro(prefixo: str) -> str:
    """CSS de cobertura pra widgets nativos do Streamlit que NENHUM dos
    dois arquivos de tema (ui_theme.py, theme.css) estilizava até agora
    -- checkbox, text_input, text_area, number_input, date_input,
    file_uploader, tabs, popover, select + seu popover de opções,
    alertas. Confirmado que cada data-testid abaixo existe de verdade
    no bundle do Streamlit 1.61 instalado (grep no JS estático, não
    chutado) antes de escrever isto.

    Por que só entra no modo CLARO (nunca no escuro): esses widgets
    hoje já saem com cara "certa" no modo escuro por COINCIDÊNCIA --
    eles herdam as cores nativas do Streamlit vindas de .streamlit/
    config.toml (base="dark", que não muda em tempo de execução,
    Streamlit só lê isso uma vez ao subir o servidor), e essas cores já
    foram escolhidas pra bater com os tokens --tema-*/-- daqui. No modo
    claro esse acaso desaparece: os widgets ficariam presos nas cores
    ESCURAS do config.toml enquanto o resto da página vira clara --
    daí esta cobertura só existir aqui. Aplicar isto também no escuro
    arriscaria regredir um visual já aceito sem trazer benefício
    nenhum (as cores já baterim por coincidência), risco sem ganho.

    `prefixo`: "tema-" pra ui_theme.py (--tema-bg, --tema-ink...) ou
    "" pra theme.css/enem_theme.py (--bg, --ink...) -- os dois arquivos
    usam --lime-sh/--tema-lime-shadow com sufixo DIFERENTE (não só
    prefixo diferente), então essa função nunca referencia esses
    tokens de sombra -- só bg/surface/surface-2/surface-3/border/
    border-2/ink/ink-2/ink-3/lime, que têm o mesmo sufixo nos dois
    arquivos."""
    p = prefixo
    return f"""
[data-testid="stAlertContainer"] {{
    background: var(--{p}surface) !important;
    border: 1px solid var(--{p}border) !important;
    color: var(--{p}ink) !important;
}}
[data-testid="stCheckbox"] label span:last-child {{ color: var(--{p}ink); }}
[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"] {{
    background: var(--{p}surface) !important;
    border-color: var(--{p}border-2) !important;
}}
[data-testid="stTextInputRootElement"] input,
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stNumberInputField"],
[data-testid="stDateInputField"] input {{
    background: var(--{p}surface) !important;
    color: var(--{p}ink) !important;
}}
[data-baseweb="select"] > div {{
    background: var(--{p}surface) !important;
    border-color: var(--{p}border-2) !important;
    color: var(--{p}ink) !important;
}}
[data-baseweb="select"] svg {{ color: var(--{p}ink-3) !important; }}
[data-baseweb="popover"] [role="listbox"] {{
    background: var(--{p}surface) !important;
    border: 1px solid var(--{p}border-2) !important;
}}
[data-baseweb="popover"] li {{ color: var(--{p}ink) !important; }}
[data-baseweb="popover"] li:hover {{ background: var(--{p}surface-2) !important; }}
[data-testid="stPopoverBody"] {{
    background: var(--{p}surface) !important;
    border: 1px solid var(--{p}border) !important;
    color: var(--{p}ink) !important;
}}
[data-testid="stTabs"] button[role="tab"] {{ color: var(--{p}ink-3) !important; }}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: var(--{p}ink) !important;
    border-bottom-color: var(--{p}lime) !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: var(--{p}surface) !important;
    border: 1px dashed var(--{p}border-2) !important;
    color: var(--{p}ink-2) !important;
}}
"""


# Tokens do modo claro (--bg/--ink/--lime... de theme.css). Valores
# verificados por contraste WCAG (fórmula de luminância relativa
# calculada à mão, ver conversa 2026-09 -- não há como abrir um
# navegador de verdade nesta sessão pra conferir visualmente, mas dá
# pra confirmar matematicamente que o texto vai ser legível):
#   ink (#171B24) sobre bg: 16.5:1 · ink-2 (#565E70): 6.2:1 ·
#   ink-3 (#7E8697): 3.5:1 (mesmo patamar que o ink-3 ESCURO já usa
#   contra seu próprio fundo, ~3.3:1 -- não é um padrão novo, é
#   igualar o que o modo escuro já considera aceitável pra texto
#   terciário) · lime (#4FAE12) escurecido de #6EE12B porque o
#   original dá só 1.6:1 de contraste como texto/borda sobre fundo
#   branco (marca d'água ilegível) -- mesma lição do tema
#   "fluorescente" anterior ao redesign atual, que precisou escurecer
#   pro mesmo motivo (ver core/CLAUDE.md, "#15803D... já que neon-on-
#   white falha contraste WCAG de texto") · coral (#C5401F) pela mesma
#   razão (original dava 2.7:1). Violeta e âmbar ficam com o MESMO
#   valor do escuro de propósito: violeta só aparece como FUNDO de
#   badge (nunca como texto direto no fundo da página, cru já dá 4.2:1
#   de contraste de borda ali) e âmbar só aparece como texto DENTRO de
#   um chip com fundo escuro próprio (--amber-bg), que não muda com o
#   tema da página -- nenhum dos dois precisa de variante clara.
_CSS_CLARO = """
:root {
    color-scheme: light;
    --bg: #FAFAFB;
    --surface: #FFFFFF;
    --surface-2: #F1F2F5;
    --surface-3: #E6E8EE;
    --border: #E3E5EB;
    --border-2: #D3D6DF;
    --ink: #171B24;
    --ink-2: #565E70;
    --ink-3: #7E8697;
    --lime: #4FAE12;
    --lime-sh: #2F7D0E;
    --coral: #C5401F;
}
"""


def inject(tema: str = "escuro") -> None:
    """Injeta o tema. Chame uma unica vez por pagina, antes de tudo.
    `tema`: "escuro" (padrão, tokens originais do theme.css) ou "claro"
    -- nesse caso, acrescenta por cima um bloco redefinindo os MESMOS
    nomes de variável (--bg, --ink, --lime...) pros valores claros, sem
    tocar no arquivo theme.css em si (mesmo raciocínio de ui_theme.
    injetar_tema: o bloco escuro nunca muda, o claro é só um adendo).
    Ver `_CSS_CLARO` pra explicação de cada valor escolhido."""
    css = CSS_PATH.read_text(encoding="utf-8")
    if tema == "claro":
        css += _CSS_CLARO + _css_widgets_nativos_claro("")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------- header

def header(title: str, streak: int = 0, rank: str = "S-Rank", xp: int = 0) -> None:
    streak_on = " on" if streak > 0 else ""
    _html(
        f'<div class="ex-row" style="margin-bottom:14px">'
        f'  <div style="width:46px;height:46px;border-radius:16px;background:var(--violet);'
        f'box-shadow:0 5px 0 var(--violet-sh);display:flex;align-items:center;justify-content:center;'
        f'flex:0 0 auto">{icon("sparkle", 22, "var(--on-violet)")}</div>'
        f'  <div style="flex:1;font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:21px;'
        f'color:var(--ink)">{title}</div>'
        f'</div>'
        f'<div class="ex-pills">'
        f'  <div class="ex-pill{streak_on}">{icon("flame", 15)}{streak}</div>'
        f'  <div class="ex-pill on">{icon("star", 14)}{rank} - {xp} XP</div>'
        f'</div>'
    )


def banner_continuar(kicker: str, titulo: str, cta: str = "COMEÇAR") -> None:
    """Banner lima "continue de onde parou" (README, seção Desktop) --
    decorativo/informativo, mostra onde o aluno parou. A ação de
    verdade continua sendo o botão Começar/Continuar de cada nó na
    lista abaixo da trilha (_renderizar_mapa_trilha em
    cartao_resposta.py) -- não duplica lógica de abrir nó aqui, só
    apresentação (bug #6 do relatório de design)."""
    _html(
        f'<div class="ex-row" style="justify-content:space-between;background:var(--lime);'
        f'box-shadow:0 6px 0 var(--lime-sh);border-radius:22px;padding:20px 24px;margin-bottom:18px">'
        f'  <div style="flex:1;min-width:0">'
        f'    <div style="font-weight:800;font-size:12px;letter-spacing:.12em;color:#2A5A10">{kicker}</div>'
        f'    <div style="font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:26px;'
        f'color:var(--on-lime)">{titulo}</div>'
        f'  </div>'
        f'  <div style="background:var(--on-lime);border-radius:16px;padding:14px 26px;'
        f'font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:16px;color:#B9F58C;'
        f'flex:0 0 auto;white-space:nowrap">{cta}</div>'
        f'</div>'
    )


# --------------------------------------------------------------- missoes

@dataclass
class Mission:
    title: str
    subtitle: str
    progress: float           # 0.0 - 1.0
    tone: str = "lime"        # lime | violet | amber | coral | neutral
    done: bool = False
    xp: int | None = None


def missions_card(missions: list[Mission], title: str = "Missoes de hoje",
                  link: str = "VER TODAS") -> None:
    rows = []
    for m in missions:
        color = TONES.get(m.tone, TONES["lime"])
        pct = max(0.0, min(1.0, m.progress)) * 100
        xp = (f'<span style="font-weight:800;font-size:12px;color:var(--amber)">+{m.xp} XP</span>'
              if m.xp else "")
        rows.append(
            f'<div class="ex-mission">'
            f'  <div class="ex-check{" done" if m.done else ""}"></div>'
            f'  <div class="ex-mission-body">'
            f'    <div style="display:flex;justify-content:space-between;align-items:baseline;gap:10px">'
            f'      <div class="ex-mission-title">{m.title}</div>{xp}</div>'
            f'    <div class="ex-mission-sub">{m.subtitle}</div>'
            f'    <div class="ex-track"><div class="ex-fill" style="width:{pct:.0f}%;'
            f'background:{color}"></div></div>'
            f'  </div>'
            f'</div>'
        )
    _html(
        f'<div class="ex-card">'
        f'  <div class="ex-card-head">'
        f'    <div class="ex-badge" style="background:#3A1F14"></div>'
        f'    <div class="ex-card-title">{title}</div>'
        f'    <div class="ex-link">{link}</div>'
        f'  </div>'
        f'  {"".join(rows)}'
        f'</div>'
    )


# --------------------------------------------------------------- trilha

# O mockup original tem 5 ancoras fixas (path SVG desenhado a mao). Uma
# materia real do banco de pratica pode ter mais de 5 nos (25+ questoes),
# entao as ancoras sao geradas por formula (mesmo ziguezague, generaliza
# pra qualquer `nodes`) em vez de uma lista fixa.
_CENTRO_X, _AMPLITUDE_X, _ESPACAMENTO_Y, _TOPO_Y = 175, 83, 120, 56


def _ancoras(nodes: int) -> list[tuple[float, float]]:
    return [
        (_CENTRO_X + _AMPLITUDE_X * math.sin(i * math.pi / 2.5), _TOPO_Y + i * _ESPACAMENTO_Y)
        for i in range(nodes)
    ]


def trilha(materia: str, area: str, nodes: int, done: int, current: int,
           questions_per_node: int = 5, mascote_bloco: str = "") -> None:
    """Banner da unidade + percurso de nos.

    done    = quantos nos ja concluidos
    current = indice (1-based) do no liberado agora (nodes+1 se todos concluidos)
    mascote_bloco = HTML pronto (ex: um .ex-card com mascote_html() +
        fala) pra renderizar ao LADO do percurso, alinhado verticalmente
        na altura do no atual -- bug #9 do relatorio de design ("o
        mascote tem que ficar ao lado da trilha, na altura do no
        atual"). Vazio (padrao) = comportamento antigo, so o percurso.
        Quem monta o HTML da fala continua sendo o caller (cartao_
        resposta.py) -- esta funcao so cuida do LAYOUT lado a lado.

    O path entre os nos e desenhado com <div> rotacionado via CSS puro,
    nao <svg><path> como no mockup original -- Streamlit nao renderiza
    <svg> de forma confiavel dentro de st.markdown(unsafe_allow_html=True)
    (confirmado em bug real desta mesma trilha antes deste arquivo
    existir: a tag aparecia como texto cru em vez de desenhar).
    """
    pct = (done / nodes * 100) if nodes else 0
    _html(
        f'<div class="ex-banner">'
        f'  <div style="flex:1">'
        f'    <div class="ex-banner-kicker">{area.upper()}</div>'
        f'    <div class="ex-banner-title">{materia}</div>'
        f'  </div>'
        f'  <div style="width:48px;height:48px;border-radius:50%;background:var(--violet);'
        f'box-shadow:0 4px 0 var(--violet-sh);flex:0 0 auto"></div>'
        f'</div>'
        f'<div class="ex-row" style="margin-bottom:16px">'
        f'  <div class="ex-track" style="flex:1"><div class="ex-fill" style="width:{pct:.0f}%;'
        f'background:var(--lime)"></div></div>'
        f'  <div style="font-weight:700;font-size:12.5px;color:var(--ink-2)">'
        f'{done} de {nodes} no(s)</div>'
        f'</div>'
    )

    if nodes == 0:
        return

    ancoras = _ancoras(nodes)
    altura = _TOPO_Y * 2 + max(0, nodes - 1) * _ESPACAMENTO_Y

    segmentos = []
    for (x0, y0), (x1, y1) in zip(ancoras, ancoras[1:]):
        dx, dy = x1 - x0, y1 - y0
        comprimento = math.hypot(dx, dy)
        angulo = math.degrees(math.atan2(dy, dx))
        meio_x, meio_y = (x0 + x1) / 2, (y0 + y1) / 2
        segmentos.append(
            f'<div style="position:absolute;left:{meio_x - comprimento / 2:.0f}px;'
            f'top:{meio_y - 6:.0f}px;width:{comprimento:.0f}px;height:12px;'
            f'transform:rotate({angulo:.1f}deg);'
            f'background:repeating-linear-gradient(to right,var(--surface-3) 0 12px,transparent 12px 38px);'
            f'border-radius:6px"></div>'
        )

    cols = []
    for i, (x, y) in enumerate(ancoras, start=1):
        if i < current:
            cls, glyph, flag = "ex-node done", icon("check", 26, "#3A2A00", 3), ""
        elif i == current:
            cls, glyph = "ex-node current", icon("play", 32, "var(--on-lime)")
            flag = '<div class="ex-flag">COMEÇAR</div>'
        else:
            cls, glyph, flag = "ex-node", icon("lock", 22, "var(--ink-3)", 2.4), ""
        cols.append(
            f'<div class="ex-node-col" style="left:{x:.0f}px;top:{y:.0f}px">'
            f'  {flag}<div class="{cls}">{glyph}</div>'
            f'  <div class="ex-node-label">Nó {i} &middot; {questions_per_node}q</div>'
            f'</div>'
        )

    path_html = (
        f'<div class="ex-path" style="height:{altura:.0f}px">'
        f'  {"".join(segmentos)}'
        f'  {"".join(cols)}'
        f'</div>'
    )

    if mascote_bloco:
        indice_atual = min(max(current, 1), nodes)
        y_atual = ancoras[indice_atual - 1][1]
        # alinha o TOPO do bloco do mascote perto do centro do no atual
        # (metade da largura media de um card de mascote, ~70px, pra
        # nao empurrar ele pra baixo do no de verdade).
        _html(
            f'<div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap">'
            f'  <div style="flex:0 0 auto">{path_html}</div>'
            f'  <div style="flex:1 1 240px;min-width:240px;margin-top:{max(y_atual - 70, 0):.0f}px">'
            f'{mascote_bloco}</div>'
            f'</div>'
        )
    else:
        _html(path_html)


# -------------------------------------------------------------- resultado

def resultado(titulo: str, subtitulo: str, acertos: str, xp: int, tempo: str) -> None:
    tiles = [
        ("var(--surface)", "var(--border)", "var(--ink)", acertos, "ACERTOS"),
        ("var(--amber-bg)", "var(--amber-bd)", "var(--amber)", f"+{xp}", "XP"),
        ("var(--surface)", "var(--border)", "var(--ink)", tempo, "TEMPO"),
    ]
    cells = "".join(
        f'<div style="flex:1;background:{bg};border:1px solid {bd};border-radius:20px;'
        f'padding:16px 12px;display:flex;flex-direction:column;align-items:center;gap:6px">'
        f'  <div style="font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:24px;'
        f'color:{fg}">{val}</div>'
        f'  <div style="font-weight:700;font-size:11.5px;letter-spacing:.05em;'
        f'color:var(--ink-3)">{lbl}</div>'
        f'</div>'
        for bg, bd, fg, val, lbl in tiles
    )
    _html(
        f'<div style="text-align:center;margin:8px 0 18px">'
        f'  <div style="font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:30px;'
        f'color:var(--lime)">{titulo}</div>'
        f'  <div style="font-weight:600;font-size:15px;color:var(--ink-2)">{subtitulo}</div>'
        f'</div>'
        f'<div style="display:flex;gap:10px">{cells}</div>'
    )
