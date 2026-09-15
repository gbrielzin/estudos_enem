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


def inject() -> None:
    """Injeta o tema. Chame uma unica vez por pagina, antes de tudo."""
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------- header

def header(title: str, streak: int = 0, rank: str = "S-Rank", xp: int = 0) -> None:
    streak_on = " on" if streak > 0 else ""
    _html(
        f'<div class="ex-row" style="margin-bottom:14px">'
        f'  <div style="width:46px;height:46px;border-radius:16px;background:var(--violet);'
        f'box-shadow:0 5px 0 var(--violet-sh);display:flex;align-items:center;justify-content:center;'
        f'font-size:22px;flex:0 0 auto">*</div>'
        f'  <div style="flex:1;font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:21px;'
        f'color:var(--ink)">{title}</div>'
        f'</div>'
        f'<div class="ex-pills">'
        f'  <div class="ex-pill{streak_on}">{streak}</div>'
        f'  <div class="ex-pill on">{rank} - {xp} XP</div>'
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

# Ancoras do percurso, na ordem. Coordenadas dentro de um box de 350 x altura.
_ANCHORS = [(175, 56), (258, 176), (175, 296), (95, 406), (150, 516)]
_PATH = ("M175 56 C 175 116, 258 126, 258 176 C 258 236, 175 246, 175 296 "
         "C 175 346, 95 356, 95 406 C 95 456, 150 466, 150 516")


def trilha(materia: str, area: str, nodes: int, done: int, current: int,
           questions_per_node: int = 5) -> None:
    """Banner da unidade + percurso de nos.

    done    = quantos nos ja concluidos
    current = indice (1-based) do no liberado agora
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

    cols = []
    for i, (x, y) in enumerate(_ANCHORS[:nodes], start=1):
        if i < current:
            cls, glyph, flag = "ex-node done", "&#10003;", ""
        elif i == current:
            cls, glyph = "ex-node current", "&#9654;"
            flag = '<div class="ex-flag">COMECAR</div>'
        else:
            cls, glyph, flag = "ex-node", "&#128274;", ""
        cols.append(
            f'<div class="ex-node-col" style="left:{x}px;top:{y}px">'
            f'  {flag}<div class="{cls}">{glyph}</div>'
            f'  <div class="ex-node-label">No {i} &middot; {questions_per_node}q</div>'
            f'</div>'
        )

    _html(
        f'<div class="ex-path" style="height:580px">'
        f'  <svg width="350" height="580" viewBox="0 0 350 580" fill="none" '
        f'style="position:absolute;left:0;top:0">'
        f'    <path d="{_PATH}" stroke="#232936" stroke-width="12" stroke-linecap="round" '
        f'stroke-dasharray="1 26"/>'
        f'  </svg>'
        f'  {"".join(cols)}'
        f'</div>'
    )


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
