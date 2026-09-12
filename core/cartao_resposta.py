"""
cartao_resposta.py — MVP do cartão-resposta digital.

Fluxo: escolhe uma prova já cadastrada -> marca A/B/C/D/E por questão
-> corrige contra o gabarito em questoes -> grava em
tentativas_usuario e agenda a próxima revisão (Leitner), tudo via
registrar_tentativa() do db.py. Não duplica nenhuma lógica de correção
aqui — a tela só coleta e mostra.

Pré-requisito: a prova (ano+caderno) já precisa ter as questões
inseridas via inserir_questao() (com gabarito), senão não aparece
no seletor. Este arquivo não cadastra questão nenhuma.

Rodar isolado:  streamlit run cartao_resposta.py
Ou copiar o conteúdo da função render_cartao_resposta() como uma
nova aba dentro do app.py existente, junto das outras abas.
"""

import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path

import streamlit as st

import db
import coletar_videos
import triagem
import backup_db
import ui_theme
import enem_theme


def render_carregar_gabarito() -> None:
    with st.expander("➕ Carregar gabarito de uma prova nova (CSV)"):
        st.caption("Colunas obrigatórias: numero, materia, gabarito. Opcional: grande_area.")
        col1, col2, col3 = st.columns(3)
        with col1:
            ano = st.number_input("Ano da prova", min_value=2009, max_value=2100, value=2024, step=1)
        with col2:
            caderno = st.text_input("Caderno", value="Azul")
        with col3:
            grande_area = st.selectbox("Grande área padrão", ["matematica", "ciencias_natureza"])
        arquivo = st.file_uploader("Arquivo CSV", type="csv")
        if arquivo is not None and st.button("Carregar"):
            with tempfile.TemporaryDirectory() as pasta_temp:
                caminho_temp = os.path.join(pasta_temp, arquivo.name)
                with open(caminho_temp, "wb") as f:
                    f.write(arquivo.getbuffer())
                try:
                    resumo = db.carregar_gabarito_csv(caminho_temp, ano=int(ano), caderno=caderno, grande_area_padrao=grande_area)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.success(f"{resumo['classificadas']} questão(ões) classificada(s).")
                    if resumo["nao_classificadas"]:
                        st.warning(
                            f"{len(resumo['nao_classificadas'])} foram pra triagem (matéria fora da taxonomia): "
                            + ", ".join(resumo["nao_classificadas"])
                        )
                    if resumo["erros"]:
                        st.error("Linhas com erro: " + "; ".join(resumo["erros"]))
                    st.rerun()


RÓTULO_AREA = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}

# Limiar de taxa de acerto médio pra decidir se o Pipoco fica feliz ou
# cabisbaixo numa área, no wizard "Montar prova" (ver _humor_por_area).
# 1a versão -- valor solto, não tem análise nenhuma por trás além de
# "50% pra cima é indo bem", ajustar conforme o uso real mostrar que
# está feliz/triste demais.
_LIMIAR_HUMOR_AREA = 0.5


def _status_provas_por_ano(provas: list[tuple[int, str, str]]) -> dict[int, str]:
    """"feito" / "parcial" / "nunca" por ano, pro passo "Qual ano" do
    wizard Montar Prova (App ENEM.dc.html, Turno 3, seções 3a/3b) --
    não existe função pronta pra isso em db.py, calculado aqui
    comparando db.simulados_feitos() (o que já foi tentado, com
    quantas questões respondidas na última rodada) contra
    "total_questoes" que a própria db.simulados_feitos() já devolve
    (tamanho real da prova).

    Simplificação deliberada (ver plano): o dot é por ANO, não por
    caderno -- usa só o caderno "azul" quando existe pra aquele ano
    (senão o primeiro em ordem alfabética), e combina o status das
    áreas disponíveis nesse caderno (feito > parcial > nunca). Uma
    prova real tem várias cores de caderno com o MESMO conteúdo em
    ordem diferente (ver core/CLAUDE.md, "Múltiplos cadernos") -- pra
    um indicador rápido de "já treinei esse ano" isso é suficiente,
    sem precisar mostrar 4+ dots por ano."""
    feitos = {(f["ano"], f["caderno"], f["grande_area"]): f for f in db.simulados_feitos()}
    anos = sorted({ano for ano, _, _ in provas})
    status: dict[int, str] = {}
    for ano in anos:
        cadernos_do_ano = sorted({c for a, c, _ in provas if a == ano})
        caderno_repr = "azul" if "azul" in cadernos_do_ano else cadernos_do_ano[0]
        areas_do_ano = {area for a, c, area in provas if a == ano and c == caderno_repr}
        melhor = "nunca"
        for area in areas_do_ano:
            f = feitos.get((ano, caderno_repr, area))
            if f is None:
                continue
            total = f["total_questoes"]
            feito_total = f["rodadas"][-1]["total"] if f["rodadas"] else 0
            atual = "feito" if total and feito_total >= total else "parcial"
            if atual == "feito":
                melhor = "feito"
                break
            if melhor == "nunca":
                melhor = atual
        status[ano] = melhor
    return status


def _humor_por_area(area: str) -> str:
    """"happy"/"sad" pro Pipoco do wizard Montar Prova, conforme o
    desempenho médio na área inteira -- não existe agregação pronta
    nesse nível (taxa_acerto_por_materia() é por matéria, não por
    grande_área), então pondera aqui por total_tentativas. Sem
    tentativa nenhuma ainda = "happy" (neutro/otimista de propósito --
    não faz sentido o mascote já começar desanimado sem histórico
    nenhum pra basear isso)."""
    linhas = db.taxa_acerto_por_materia(area)
    total_tentativas = sum(r["total_tentativas"] for r in linhas)
    if total_tentativas == 0:
        return "happy"
    acertos = sum(r["acertos"] for r in linhas)
    return "happy" if (acertos / total_tentativas) >= _LIMIAR_HUMOR_AREA else "sad"


def _caderno_padrao(provas: list[tuple[int, str, str]], ano: int, area: str) -> str | None:
    """Caderno "azul" se existir pra esse (ano, área), senão o primeiro
    disponível em ordem alfabética -- o wizard escolhe ano+área, não
    caderno (o mockup também não expõe essa escolha), mas
    _renderizar_bloco_prova/_renderizar_prova_no_a_no precisam de um
    caderno de verdade pra buscar as questões."""
    cadernos = sorted({c for a, c, ar in provas if a == ano and ar == area})
    if not cadernos:
        return None
    return "azul" if "azul" in cadernos else cadernos[0]


def _taxa_media_area(area: str) -> float | None:
    """Taxa de acerto média ponderada por total_tentativas, pra
    comparar Natureza x Matemática e achar a área mais fraca de
    verdade (dado real, não hardcoded como o mockup faz) -- None
    quando não há tentativa nenhuma ainda naquela área."""
    linhas = db.taxa_acerto_por_materia(area)
    total = sum(r["total_tentativas"] for r in linhas)
    if total == 0:
        return None
    return sum(r["acertos"] for r in linhas) / total


def _formatar_tempo_estimado(minutos: int) -> str:
    """"1h30"/"3h" (sem "min", sem zero-padding quando exato) -- mesmo
    formato do bilhete no mockup."""
    horas, resto = divmod(minutos, 60)
    return f"{horas}h{resto:02d}" if resto else f"{horas}h"


def _renderizar_cena_mesa(provas: list[tuple[int, str, str]]) -> None:
    """Cena decorativa panorâmica (App ENEM.dc.html, Turno 4, 4a) --
    mesa + relógio + cadernos + Pipoco. Virou o TOPO DE VERDADE da
    página inteira "Provas ENEM" (pedido do usuário, 2026-09-11): antes
    disso, o hero genérico (ui_theme.hero() -- título "Provas ENEM" +
    tagline) e o loader de CSV/seletor de "Modo" ficavam ACIMA dela,
    duplicando a mesma informação que a própria cena já mostra
    (título, dias até o ENEM) e "poluindo" o que devia abrir como um
    cenário panorâmico só, igual à referência de design. `__main__`
    agora PULA a chamada de ui_theme.hero() especificamente pra
    "provas_enem" (única página que faz isso), e esta função é
    chamada incondicionalmente, ANTES do loader de CSV e do radio de
    "Modo" -- funciona como cabeçalho fixo da página inteira, não só
    do wizard "Uma prova por vez" (antes só aparecia dentro dele).

    Full-bleed de verdade (classe .cena-mesa-full-bleed, CSS central em
    ui_theme.py): cancela o padding lateral do .block-container pra
    encostar nas duas bordas do espaço disponível, como o frame do
    mockup. (2026-09-11: uma versão com barra de ícones própria +
    st.columns()+".entrada-bleed" foi tentada e depois revertida a
    pedido do usuário -- a barra de ícones virou navegação real do app
    inteiro, ver ui_theme.barra_navegacao_icones(), não mais algo
    específico desta página.)

    Continua reagindo aos MESMOS 3 campos que o wizard abaixo escolhe
    -- relógio acende com "Com cronômetro", ícone/legenda da área
    mudam com a matéria -- lendo session_state ANTES dos widgets
    correspondentes serem criados mais abaixo no código (Streamlit já
    preenche session_state antes do script rodar, mesmo padrão de
    sempre). Sem valor ainda (primeiro load) cai nos defaults reais.
    Legendas sob o relógio/ícone usam o MODO/ÁREA já escolhidos (texto,
    não um tempo estimado) em vez do "1h30 NO RELÓGIO" fixo do mockup
    -- aquele número no mockup é só decorativo pra UM exemplo fixo;
    aqui ano/área ainda não estão escolhidos neste ponto da página
    (só o wizard abaixo tem essa info), então uma legenda de tempo
    seria inventada -- a legenda real (modo/área) já é 100% honesta com
    o que se sabe até aqui."""
    dias = db.dias_ate_prova()
    total_questoes_banco = sum(db.questoes_totais_da_prova(a, c, ar) for a, c, ar in provas)
    anos = sorted({ano for ano, _, _ in provas})
    if not anos:
        return

    modo_previa = st.session_state.get("montar_prova_modo", "cronometro")
    area_previa = st.session_state.get("montar_prova_area_valor")
    _ICONE_AREA_MESA = {
        "matematica": ('#8B93A7', 'MATEMÁTICA', '<path d="M5 7h6M8 4v6"/><path d="M13.5 6.5h5.5"/>'
                        '<path d="M13.5 15h5.5M13.5 18.5h5.5"/><path d="M5.5 15.5l4.5 4.5M10 15.5l-4.5 4.5"/>'),
        "ciencias_natureza": ('#6EE12B', 'NATUREZA', '<path d="M12 3v4"/><path d="M9 7h6l2.5 10a5.5 5.5 0 0 1-11 0z"/><path d="M7.6 14h8.8"/>'),
        "ambas": ('#A594FF', 'AS DUAS', '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>'),
    }
    cor_area_mesa, rotulo_area_mesa, path_area_mesa = _ICONE_AREA_MESA.get(
        area_previa, ('#5B6472', 'PROVA', '<path d="M8 4h8l4 4v12H8z"/><path d="M16 4v4h4"/>')
    )
    rotulo_modo_mesa = {
        "cronometro": "CRONÔMETRO", "sem_pressa": "SEM PRESSA",
        "corrige_cada": "CORRIGE JÁ", "so_errei_antes": "SÓ ERROS",
    }.get(modo_previa, "CRONÔMETRO")
    cor_relogio = "#FFC42E" if modo_previa == "cronometro" else "#5B6472"
    bg_relogio = "#2A2210" if modo_previa == "cronometro" else "#171B24"
    borda_relogio = "#4A3A12" if modo_previa == "cronometro" else "#262C39"
    st.markdown(
        f'''<div class="cena-mesa-full-bleed" style="position:relative;height:196px;background:#12161E;border-radius:16px;
             overflow:hidden;margin-bottom:22px">
          <div style="position:absolute;left:0;right:0;top:0;height:130px;background:#171C26"></div>
          <div style="position:absolute;left:0;right:0;top:130px;height:8px;background:#6B4A2F"></div>
          <div style="position:absolute;left:0;right:0;top:138px;bottom:0;background:#0E1117"></div>
          <div style="position:absolute;left:calc(50% - 78px);bottom:6px;width:9px;height:40px;border-radius:2px;background:#57391F"></div>
          <div style="position:absolute;right:calc(50% - 78px);bottom:6px;width:9px;height:40px;border-radius:2px;background:#57391F"></div>
          <div style="position:absolute;left:44px;top:16px;display:flex;flex-direction:column;gap:4px;z-index:2">
            <div style="font:800 10px 'Nunito';letter-spacing:.16em;color:#5B6472">MONTAR PROVA</div>
            <div style="font:800 22px 'Baloo 2';color:#F2F4F7;line-height:1.1">Senta que a prova é sua</div>
          </div>
          <div style="position:absolute;right:44px;top:16px;display:flex;flex-direction:column;align-items:flex-end;gap:5px;z-index:2">
            <div style="font:800 11px 'Nunito';color:#FFC42E;background:#2A2210;border:1px solid #4A3A12;
                 border-radius:999px;padding:5px 12px">{dias["dias_restantes"]} dias até o ENEM</div>
            <div style="font:700 11px 'Nunito';color:#6B7385">{total_questoes_banco} questões · {min(anos)} a {max(anos)}</div>
          </div>
          <div style="position:absolute;left:0;right:0;top:56px;display:flex;align-items:flex-end;justify-content:center;gap:46px;transform:translateX(78px)">
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:0 0 auto">
              <div style="width:44px;height:44px;border-radius:999px;background:{bg_relogio};border:2px solid {borda_relogio};
                   display:flex;align-items:center;justify-content:center;flex:0 0 auto">
                <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="{cor_relogio}" stroke-width="2.3" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
              </div>
              <div style="font:800 9px 'Nunito';letter-spacing:.06em;color:{cor_relogio};white-space:nowrap">{rotulo_modo_mesa}</div>
            </div>
            <div style="display:flex;align-items:flex-end;gap:2px;flex:0 0 auto">
              <div style="width:40px;height:52px;border-radius:4px;background:#E8EDF3;box-shadow:0 4px 0 rgba(0,0,0,.35);transform:rotate(-6deg)"></div>
              <div style="width:46px;height:60px;border-radius:4px;background:#FFFFFF;box-shadow:0 5px 0 rgba(0,0,0,.32);
                   display:flex;flex-direction:column;gap:4px;padding:8px 7px;position:relative;z-index:1">
                <div style="height:3px;border-radius:2px;background:#C8CEDA"></div>
                <div style="height:3px;border-radius:2px;background:#C8CEDA"></div>
                <div style="height:3px;width:60%;border-radius:2px;background:#C8CEDA"></div>
                <div style="margin-top:auto;height:7px;border-radius:3px;background:{cor_area_mesa}"></div>
              </div>
              <div style="width:40px;height:52px;border-radius:4px;background:#E8EDF3;box-shadow:0 4px 0 rgba(0,0,0,.35);transform:rotate(5deg)"></div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:0 0 auto">
              <div style="width:44px;height:44px;border-radius:14px;background:#141821;border:2px solid {cor_area_mesa};
                   display:flex;align-items:center;justify-content:center;flex:0 0 auto">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{cor_area_mesa}" stroke-width="2.1" stroke-linecap="round">{path_area_mesa}</svg>
              </div>
              <div style="font:800 9px 'Nunito';letter-spacing:.06em;color:{cor_area_mesa};white-space:nowrap">{rotulo_area_mesa}</div>
            </div>
          </div>
          <div style="position:absolute;left:50%;top:20px;transform:translateX(calc(-50% - 148px));z-index:3">
            {ui_theme.mascote_html("happy", size=0.92, pattern="tuxedo", patch="#3A4152", collar="#6EE12B")}
          </div>
        </div>''',
        unsafe_allow_html=True,
    )


def _renderizar_montar_prova(provas: list[tuple[int, str, str]]) -> tuple[int, str, str, str] | None:
    """Wizard "Montar prova" -- 3 passos à esquerda + o "bilhete"
    (ficha-resumo que se preenche ao vivo) à direita, terminando no
    botão "Sentar e começar". A cena decorativa (mesa/relógio/
    cadernos/Pipoco) que costumava abrir esta função foi PROMOVIDA a
    cabeçalho fixo da página inteira -- ver _renderizar_cena_mesa(),
    chamada uma vez só em render_cartao_resposta(), antes de tudo.

    Devolve (ano, caderno, area, modo_resposta) só quando "Sentar e
    começar" é clicado -- `caderno` vem None quando area == "ambas"
    (quem chama escolhe um caderno por área via _caderno_padrao).
    Devolve None enquanto o usuário ainda está escolhendo.

    Tudo dentro de UM st.container(border=True) de propósito: os
    marcadores-irmão (.ano-pills/.area-cards, mesmo truque do
    .grade-blocos) usam seletor de irmão GERAL "~", que não para de
    procurar -- sem um limite, vazariam pra tela de responder a prova
    (_renderizar_bloco_prova/_renderizar_prova_no_a_no, cheia de
    st.radio/st.button dela mesma), renderizada logo depois na MESMA
    página assim que o botão é clicado."""
    with st.container(border=True):
        total_questoes_banco = sum(db.questoes_totais_da_prova(a, c, ar) for a, c, ar in provas)
        anos = sorted({ano for ano, _, _ in provas})

        col_passos, col_bilhete = st.columns([2, 1], gap="large")

        with col_passos:
            status_por_ano = _status_provas_por_ano(provas)
            ponto_status = {"feito": "🟢", "parcial": "🟡", "nunca": "⚪"}
            # Legenda por EXTENSO só quando o ano é o selecionado (pedido
            # do usuário, 2026-09-11, seguindo à risca a referência
            # visual: 2025 selecionado mostra "nunca feita" por baixo do
            # número, os outros só mostram a bolinha colorida) -- os
            # outros dois nomes seguem a MESMA palavra da legenda acima
            # ("já fez" -> "já feita", "parou no meio" fica igual).
            texto_status = {"feito": "já feita", "parcial": "parou no meio", "nunca": "nunca feita"}

            st.markdown(
                '<div class="ano-cards"></div>'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
                '<div style="width:22px;height:22px;border-radius:8px;background:#6EE12B;display:flex;'
                'align-items:center;justify-content:center;font:800 12px \'Nunito\';color:#0D2705;flex:0 0 auto">1</div>'
                '<div style="font:800 12px \'Nunito\';letter-spacing:.14em;color:var(--tema-ink-3)">QUAL ANO</div>'
                '<div style="flex:1;height:1px;background:var(--tema-border)"></div>'
                f'<div style="font:700 11px \'Nunito\';color:var(--tema-ink-3)">{ponto_status["feito"]} já fez &nbsp; '
                f'{ponto_status["parcial"]} parou no meio &nbsp; {ponto_status["nunca"]} não abriu</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            # Virou grade de st.button (era st.radio) -- MESMO padrão de
            # "Qual área" logo abaixo (chave própria em session_state,
            # botão primary/secondary marca a seleção). Pedido do
            # usuário, 2026-09-11: a referência visual mostra o número
            # GRANDE dentro do botão e uma bolinha de status PEQUENA
            # POR FORA, embaixo -- st.radio só aceita texto simples numa
            # linha só (sem HTML, sem dois tamanhos de fonte diferentes
            # na mesma label), então não dava pra chegar nesse resultado
            # só com CSS em cima do radio nativo, por mais que se
            # corrigisse o seletor -- precisa de HTML de verdade fora do
            # botão, que só st.markdown ao lado de um st.button permite.
            chave_ano_valor = "montar_prova_ano_valor"
            if st.session_state.get(chave_ano_valor) not in anos:
                st.session_state[chave_ano_valor] = anos[0]
            cols_ano = st.columns(len(anos))
            for col, ano in zip(cols_ano, anos):
                with col:
                    selecionado = st.session_state[chave_ano_valor] == ano
                    if st.button(
                        str(ano), key=f"montar_prova_ano_btn_{ano}",
                        type="primary" if selecionado else "secondary", use_container_width=True,
                    ):
                        st.session_state[chave_ano_valor] = ano
                        st.rerun()
                    status = status_por_ano.get(ano, "nunca")
                    legenda_status = texto_status[status] if selecionado else ponto_status[status]
                    cor_legenda = "var(--tema-on-lime)" if selecionado else "var(--tema-ink-3)"
                    st.markdown(
                        f'<div style="text-align:center;margin-top:4px;font:800 10px \'Nunito\';'
                        f'color:{cor_legenda}">{legenda_status}</div>',
                        unsafe_allow_html=True,
                    )
            ano_sel = st.session_state[chave_ano_valor]

            areas_do_ano = sorted({area for a, c, area in provas if a == ano_sel})
            if not areas_do_ano:
                st.info("Nenhuma prova cadastrada pra esse ano ainda.")
                return None

            opcoes_area = list(areas_do_ano) + (["ambas"] if len(areas_do_ano) > 1 else [])
            rotulo_area = {**RÓTULO_AREA, "ambas": "As duas"}

            # Área mais fraca de verdade (dado real, ver _taxa_media_area)
            # -- só marca "seu ponto fraco" em quem tem MENOS acerto das
            # duas, nunca hardcoded pra uma área específica como o mockup.
            taxas = {a: _taxa_media_area(a) for a in areas_do_ano if a != "ambas"}
            conhecidas = {a: t for a, t in taxas.items() if t is not None}
            area_mais_fraca = min(conhecidas, key=conhecidas.get) if len(conhecidas) > 1 else None

            st.markdown(
                '<div class="area-cards"></div>'
                '<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px">'
                '<div style="width:22px;height:22px;border-radius:8px;background:#6EE12B;display:flex;'
                'align-items:center;justify-content:center;font:800 12px \'Nunito\';color:#0D2705;flex:0 0 auto">2</div>'
                '<div style="font:800 12px \'Nunito\';letter-spacing:.14em;color:var(--tema-ink-3)">QUAL ÁREA</div>'
                '<div style="flex:1;height:1px;background:var(--tema-border)"></div></div>',
                unsafe_allow_html=True,
            )
            chave_area_valor = "montar_prova_area_valor"
            if st.session_state.get(chave_area_valor) not in opcoes_area:
                st.session_state[chave_area_valor] = opcoes_area[0]
            cols_area = st.columns(len(opcoes_area))
            for col, opcao in zip(cols_area, opcoes_area):
                with col:
                    selecionada = st.session_state[chave_area_valor] == opcao
                    if opcao == "ambas":
                        legenda = f"{total_questoes_banco and '90 questões · 3h' or ''}"
                    else:
                        n_questoes = db.questoes_totais_da_prova(ano_sel, _caderno_padrao(provas, ano_sel, opcao) or "azul", opcao)
                        legenda = f"{n_questoes}q · {_formatar_tempo_estimado(n_questoes * 2)}"
                        if opcao == area_mais_fraca:
                            legenda += " · seu ponto fraco"
                    humor = _humor_por_area(opcao) if opcao != "ambas" else None
                    icone_html = ui_theme.mascote_html("cheer" if humor == "happy" else humor, size=0.36) if humor else ""
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">{icone_html}'
                        f'<div style="font:700 11.5px \'Nunito\';color:var(--tema-ink-3)">{legenda}</div></div>',
                        unsafe_allow_html=True,
                    )
                    rotulo_card = ("✓ " if selecionada else "") + rotulo_area.get(opcao, opcao)
                    if st.button(
                        rotulo_card, key=f"montar_prova_area_btn_{opcao}",
                        type="primary" if selecionada else "secondary", use_container_width=True,
                    ):
                        st.session_state[chave_area_valor] = opcao
                        st.rerun()
            area_sel = st.session_state[chave_area_valor]

            st.markdown(
                '<div class="ano-pills"></div>'
                '<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px">'
                '<div style="width:22px;height:22px;border-radius:8px;background:#39435A;display:flex;'
                'align-items:center;justify-content:center;font:800 12px \'Nunito\';color:#C8CEDA;flex:0 0 auto">3</div>'
                '<div style="font:800 12px \'Nunito\';letter-spacing:.14em;color:var(--tema-ink-3)">COMO RESPONDER</div>'
                '<div style="flex:1;height:1px;background:var(--tema-border)"></div></div>',
                unsafe_allow_html=True,
            )
            modo_resposta = st.radio(
                "Como responder", ["cronometro", "sem_pressa", "corrige_cada", "so_errei_antes"],
                format_func=lambda m: {
                    "cronometro": "Com cronômetro", "sem_pressa": "Sem pressa",
                    "corrige_cada": "Corrige a cada questão", "so_errei_antes": "Só as que errei antes",
                }[m],
                horizontal=True, key="montar_prova_modo", label_visibility="collapsed",
            )
            if modo_resposta == "cronometro":
                st.caption("⏱️ O cronômetro em si ainda não existe de verdade — por enquanto se comporta igual \"Sem pressa\".")
            if modo_resposta == "so_errei_antes":
                st.caption("🚧 Filtro ainda não implementado — por enquanto mostra a prova inteira, igual \"Sem pressa\".")

        with col_bilhete:
            caderno_bilhete = _caderno_padrao(provas, ano_sel, area_sel) if area_sel != "ambas" else None
            if area_sel == "ambas":
                n_questoes_bilhete = sum(
                    db.questoes_totais_da_prova(ano_sel, _caderno_padrao(provas, ano_sel, a) or "azul", a)
                    for a in areas_do_ano
                )
                nome_materia = "Matemática + Ciências"
            else:
                n_questoes_bilhete = db.questoes_totais_da_prova(ano_sel, caderno_bilhete or "azul", area_sel)
                nome_materia = RÓTULO_AREA.get(area_sel, area_sel)
            tempo_bilhete = _formatar_tempo_estimado(n_questoes_bilhete * 2)
            rotulo_modo = {
                "cronometro": "Com cronômetro", "sem_pressa": "Sem pressa",
                "corrige_cada": "Corrige a cada questão", "so_errei_antes": "Só as que errei antes",
            }[modo_resposta]
            barras_codigo = "".join(
                f'<div style="width:{w}px;height:34px;background:#131722"></div>'
                for w in [3, 2, 5, 2, 3, 6, 2, 4, 2, 5]
            )
            st.markdown(
                f'''<div style="display:flex;flex-direction:column;gap:16px">
                  <div style="display:flex;align-items:center;gap:12px">
                    <div style="font:800 12px 'Nunito';letter-spacing:.14em;color:var(--tema-ink-3);flex:1">SEU BILHETE</div>
                    <div style="font:800 11px 'Nunito';color:#3D2C00;background:#FFC42E;border-radius:7px;padding:4px 9px">Nº {(db.resumo_geral_desempenho()["total_tentativas"] % 900) + 100:04d}</div>
                  </div>
                  <div style="background:#F2F4F7;border-radius:20px;overflow:hidden">
                    <div style="background:#7C5CFF;padding:16px 20px;display:flex;align-items:center;gap:12px">
                      {ui_theme.mascote_html("cheer", size=0.42)}
                      <div style="flex:1;min-width:0">
                        <div style="font:800 11px 'Nunito';letter-spacing:.14em;color:#D7CEFF">ENEM · CADERNO {(caderno_bilhete or "azul").upper()}</div>
                        <div style="font:800 20px 'Baloo 2';color:#FFFFFF">{nome_materia}</div>
                      </div>
                    </div>
                    <div style="padding:18px 20px;display:flex;flex-direction:column;gap:14px">
                      <div style="display:flex;gap:18px">
                        <div style="flex:1"><div style="font:800 10.5px 'Nunito';letter-spacing:.12em;color:#7A8494">ANO</div>
                          <div style="font:800 30px 'Baloo 2';color:#131722;line-height:1.1">{ano_sel}</div></div>
                        <div style="flex:1"><div style="font:800 10.5px 'Nunito';letter-spacing:.12em;color:#7A8494">QUESTÕES</div>
                          <div style="font:800 30px 'Baloo 2';color:#131722;line-height:1.1">{n_questoes_bilhete}</div></div>
                        <div style="flex:1"><div style="font:800 10.5px 'Nunito';letter-spacing:.12em;color:#7A8494">TEMPO</div>
                          <div style="font:800 30px 'Baloo 2';color:#131722;line-height:1.1">{tempo_bilhete}</div></div>
                      </div>
                      <div style="height:2px;background:repeating-linear-gradient(90deg,#C8CEDA 0 7px,transparent 7px 14px)"></div>
                      <div style="display:flex;align-items:flex-end;gap:12px">
                        <div style="flex:1"><div style="font:800 10.5px 'Nunito';letter-spacing:.12em;color:#7A8494">MODO</div>
                          <div style="font:800 14px 'Baloo 2';color:#131722">{rotulo_modo}</div></div>
                        <div style="display:flex;gap:2.5px;align-items:flex-end;height:34px;flex:0 0 auto">{barras_codigo}</div>
                      </div>
                    </div>
                  </div>
                  <div style="font:600 13px 'Nunito';color:var(--tema-ink-3);line-height:1.55">Ele se preenche à medida
                    que você escolhe ao lado. Terminada a prova, volta carimbado com nota, acertos e tempo.</div>
                </div>''',
                unsafe_allow_html=True,
            )
            st.markdown('<div style="margin-top:14px"></div>', unsafe_allow_html=True)
            if st.button("Sentar e começar", type="primary", key="montar_prova_confirmar", use_container_width=True):
                if area_sel == "ambas":
                    return (ano_sel, None, "ambas", modo_resposta)
                caderno_sel = _caderno_padrao(provas, ano_sel, area_sel)
                return (ano_sel, caderno_sel, area_sel, modo_resposta)
        return None


def render_cartao_resposta() -> None:
    db.inicializar_banco()

    # O loader de CSV (render_carregar_gabarito) SAIU desta página
    # (pedido do usuário, 2026-09-11: "isso é uma opção de
    # administração... pra não embaralhar aí no próprio ENEM" -- Admin
    # já tem o próprio jeito de carregar gabarito, "Colar gabarito
    # direto"). A função continua existindo, só não é mais chamada
    # daqui -- mesmo padrão reversível já usado noutras remoções desta
    # rodada de simplificação.
    provas = db.listar_provas()
    if not provas:
        st.info("Nenhuma prova cadastrada ainda — carregue um gabarito na aba Admin antes de responder.")
        return

    # A barra de ícones que ficava aqui (App ENEM.dc.html, 4a) virou a
    # navegação de VERDADE do app inteiro (pedido do usuário,
    # 2026-09-11: "substitua... e tudo aquele menu por aqueles ícones")
    # -- ver ui_theme.barra_navegacao_icones(), chamada uma vez em
    # __main__, não mais duplicada aqui dentro de Provas ENEM. Essa
    # tentativa anterior (st.columns([rail, conteúdo]) + marcador
    # ".entrada-bleed") saiu "bugada" segundo o usuário e foi revertida
    # -- a cena volta a ser a única coisa full-bleed nesta página.
    _renderizar_cena_mesa(provas)

    # A barra "Modo" (Simulado completo/Revisão de hoje/Praticar por
    # matéria/Prova com enunciado) foi tirada da página inteira por
    # enquanto (pedido do usuário, 2026-09-11: só visual por ora, a
    # funcionalidade de acessar esses 4 modos de novo fica pra uma
    # rodada futura, decidida com calma -- não é pra inventar uma
    # solução funcional agora). `_render_simulado_completo`,
    # `render_revisao_hoje`, `render_praticar_por_materia` e
    # `render_prova_beta` continuam existindo, só não são chamadas por
    # nenhum caminho desta página neste momento.
    selecao = _renderizar_montar_prova(provas)
    if selecao is None:
        return
    ano_sel, caderno_sel, area_sel, modo_resposta = selecao

    if area_sel == "ambas":
        areas_ambas = sorted({area for a, c, area in provas if a == ano_sel})
        abas = st.tabs([RÓTULO_AREA.get(a, a) for a in areas_ambas])
        for aba, area_aba in zip(abas, areas_ambas):
            with aba:
                caderno_aba = _caderno_padrao(provas, ano_sel, area_aba)
                if modo_resposta == "corrige_cada":
                    _renderizar_prova_no_a_no(ano_sel, caderno_aba, area_aba)
                else:
                    _renderizar_bloco_prova(ano_sel, caderno_aba, area_aba)
        return

    if modo_resposta == "corrige_cada":
        _renderizar_prova_no_a_no(ano_sel, caderno_sel, area_sel)
    else:
        _renderizar_bloco_prova(ano_sel, caderno_sel, area_sel)


def _render_simulado_completo() -> None:
    """Faz Matemática e Ciências da Natureza do mesmo ano em sequência,
    cada uma na sua aba. Corrige, guarda e mostra o resultado de cada
    área separadamente — nunca mistura as duas na mesma grade nem no
    mesmo cálculo, mesma regra do resto do sistema. Um ano pode ter
    mais de um caderno completo (ex: 2024 azul E amarelo) -- cada
    combinação vira sua própria opção no seletor, rotulada por cor pra
    não colidir (ver db.simulados_completos_disponiveis)."""
    combinacoes = db.simulados_completos_disponiveis()
    if not combinacoes:
        st.info(
            "Nenhum ano tem as duas áreas cadastradas ainda — "
            "o simulado completo só aparece quando Matemática e Ciências "
            "da mesma prova já foram carregadas."
        )
        return

    def _rotulo(c: dict) -> str:
        if c["caderno_matematica"] == c["caderno_ciencias"]:
            return f"{c['ano']} — {c['caderno_matematica']}"
        return f"{c['ano']} — Mat. {c['caderno_matematica']} / Ciê. {c['caderno_ciencias']}"

    opcoes = {_rotulo(c): c for c in combinacoes}
    escolha = st.selectbox("Simulado", list(opcoes.keys()))
    combo = opcoes[escolha]

    aba_mat, aba_ciencias = st.tabs(["📐 Matemática", "🔬 Ciências da Natureza"])
    with aba_mat:
        _renderizar_bloco_prova(combo["ano"], combo["caderno_matematica"], "matematica")
    with aba_ciencias:
        _renderizar_bloco_prova(combo["ano"], combo["caderno_ciencias"], "ciencias_natureza")


def _renderizar_bloco_prova(ano_sel: int, caderno_sel: str, area_sel: str) -> None:
    """Corpo real da tela de responder + corrigir UMA PROVA INTEIRA.
    Recebe a área como parâmetro (em vez de pegar de um seletor
    global) pra poder ser chamada duas vezes na mesma página, uma por
    aba, no modo simulado completo — por isso toda chave de widget/
    session_state aqui dentro é sufixada com ano+caderno+área, senão
    colidiria."""
    sufixo = f"{ano_sel}_{caderno_sel}_{area_sel}"

    questoes = db.listar_questoes_da_prova(ano_sel, caderno_sel, area_sel)
    if not questoes:
        st.info("Essa prova não tem questões cadastradas.")
        return

    n_triagem = sum(1 for q in questoes if q["status_classificacao"] == "nao_classificado")
    st.caption(
        f"{len(questoes)} questões cadastradas."
        + (f" {n_triagem} com matéria não classificada (⚠️)." if n_triagem else "")
    )

    historico = db.resumo_por_tentativa(ano_sel, caderno_sel, area_sel)
    if historico:
        nomes = db.nomes_tentativas(ano_sel, caderno_sel, area_sel)
        with st.expander(f"📈 Histórico de tentativas dessa prova ({len(historico)})", expanded=True):
            for h in historico:
                pct = f"{h['taxa_acerto']*100:.0f}%" if h["taxa_acerto"] is not None else "—"
                nome_atual = nomes.get(h["tentativa"], "")
                rotulo = f"Tentativa {h['tentativa']}" + (f" — {nome_atual}" if nome_atual else "")
                col_txt, col_nome = st.columns([3, 2])
                with col_txt:
                    st.write(f"**{rotulo}**: {h['acertos']}/{h['total']} ({pct}) — {h['inicio'][:10]}")
                with col_nome:
                    novo_nome = st.text_input(
                        "Nome", value=nome_atual, placeholder="ex: fiz cansado à noite",
                        key=f"nome_tentativa_{sufixo}_{h['tentativa']}", label_visibility="collapsed",
                    )
                    if novo_nome != nome_atual and novo_nome.strip():
                        db.nomear_tentativa(ano_sel, caderno_sel, area_sel, h["tentativa"], novo_nome)
                        st.rerun()

    _renderizar_grade_questoes(
        questoes, sufixo,
        titulo_bloco=f"ENEM {ano_sel}",
        kicker_bloco=f"{RÓTULO_AREA.get(area_sel, area_sel).upper()} · CADERNO {caderno_sel.upper()}",
    )


def render_revisao_hoje() -> None:
    """Fila do dia estilo Anki: só questões cuja proxima_revisao (do
    Leitner simplificado) já chegou. Mistura anos/áreas de propósito
    -- o ponto é revisar o que está atrasado, não fingir que é uma
    prova única."""
    ids = db.questoes_para_revisar()
    if not ids:
        st.success("Nada atrasado pra revisão hoje. 🎉")
        st.caption("Isso só cobre questão já respondida ao menos uma vez — a fila enche conforme você usa o cartão-resposta.")
        return

    st.caption(f"{len(ids)} questão(ões) atrasada(s), das mais atrasadas pras mais recentes.")
    questoes = db.questoes_por_ids(ids)
    _renderizar_grade_questoes(questoes, sufixo="revisao_hoje")


def render_praticar_por_materia() -> None:
    """Pega a matéria mais fraca do painel 'Minha análise' e transforma
    em prática de verdade, misturando questões de qualquer ano/prova
    -- sem isso, 'Prioridade de estudo' é só diagnóstico que não dá pra
    agir em cima na hora.

    Só ENEM oficial (origem='enem_oficial') de propósito -- questão do
    banco de prática tem sua própria página separada (ver
    render_banco_pratica), pra não misturar 'fiz uma prova de verdade'
    com 'treinei questão de IA' no mesmo lugar (pedido explícito do
    usuário)."""
    area_sel = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True, key="praticar_materia_area",
    )
    materias = db.materias_validas(area_sel)
    if not materias:
        st.info("Nenhuma matéria válida cadastrada pra essa área.")
        return

    materia_sel = st.selectbox("Matéria", materias, key="praticar_materia_sel")

    questoes = db.questoes_por_materia(area_sel, materia_sel, origem="enem_oficial")
    if not questoes:
        st.info(f"Nenhuma questão classificada como '{materia_sel}' ainda.")
        return

    anos = sorted({q["ano"] for q in questoes}, reverse=True)
    st.caption(f"{len(questoes)} questão(ões) de {materia_sel}, de {len(anos)} prova(s) ({', '.join(str(a) for a in anos)}).")
    _renderizar_grade_questoes(questoes, sufixo=f"materia_{area_sel}_{materia_sel}")


def render_banco_pratica() -> None:
    """Página própria pro banco de prática (origem='banco_pratica') --
    questão fora do ENEM oficial, trazida de sessão de estudo com IA
    sobre um assunto específico (ex: Óptica com o Gemini). Separado de
    'Praticar por matéria' de propósito: o usuário não quer misturar
    'fiz uma prova de verdade' com 'treinei questão de IA' no mesmo
    fluxo.

    Trilha estilo Duolingo (pedido explícito do usuário): as questões
    da matéria são divididas em 'nós' de 5 (db.trilha_banco_pratica),
    destravados em sequência -- só dá pra abrir o nó N+1 depois de
    concluir o nó N. Dentro de um nó, uma questão de cada vez com
    feedback imediato (_renderizar_no_trilha_ativo), diferente do
    resto do sistema (que corrige em lote via
    _renderizar_grade_questoes) -- fluxo de exercício, não de prova.

    Reimplementado seguindo design_handoff_enem_gamificado/README.md
    (handoff formal, 2026-09) -- router entre duas telas com estado
    próprio em session_state, igual o handoff descreve Home e Trilha
    como telas SEPARADAS (a matéria só vira "conteúdo de primeira
    classe" -- pedido anterior do usuário -- na tela de Trilha; a Home
    é onde a escolha em si mora, com espaço de verdade, não escondida
    num popover pequeno como numa tentativa anterior).

    Segunda rodada do handoff (mesmo mês): tema passou a vir de
    enem_theme.py + theme.css (pacote pronto do usuário) em vez do
    ui_theme.py tokens/pilula_html/emblema_html usados na primeira
    rodada -- só nesta página por enquanto (ui_theme.injetar_tema()
    continua rodando pra toda página, porque a gaveta de navegação e o
    mascote ainda dependem das variáveis --tema-* dela; enem_theme.css
    é injetado por cima e vence nos seletores que ele também estiliza,
    já que entra depois no DOM). O hero genérico ("📝 Cartão-resposta
    digital") também é pulado só nesta página -- ver o `if pagina_atual
    != "cartao"` no bloco __main__ ("banco_pratica" é resolvido pro
    alias "cartao" antes desse if, ver o mesmo bloco).

    Terceira rodada do handoff: virou a HOME do app (fundiu com o que
    era a página "Cartão-resposta" separada -- ver _PAGINAS e o bloco
    __main__ pra onde o cartão-resposta de prova real foi realocado).
    Também é onde o `.block-container` de 720px (pensado pro layout
    mobile de coluna única do resto do handoff) é alargado pra esta
    página -- ela usa o layout desktop de 3 colunas (ver
    _renderizar_mapa_trilha), que fica sufocado nos 720px padrão (bug
    #4 do relatório de design)."""
    tema_atual = st.query_params.get("tema", "escuro")
    if tema_atual not in ("escuro", "claro"):
        tema_atual = "escuro"
    enem_theme.inject(tema_atual)
    st.markdown("<style>.block-container{max-width:1200px !important}</style>", unsafe_allow_html=True)
    tela = st.session_state.get("banco_pratica_tela", "trilha")
    if tela == "trilha":
        _renderizar_tela_trilha()
    else:
        _renderizar_home_banco_pratica()


_TOM_MISSAO = {"meta_diaria": "lime", "foco_prioridade": "violet"}


def _padrao_materia_banco_pratica(area: str, materias_da_area: list[str]) -> str:
    """Prefere uma matéria que JÁ tem questão de banco de prática (a
    com mais questões primeiro) em vez de simplesmente a 1a em ordem
    alfabética de materias_validas() -- essa lista é a taxonomia
    fechada inteira, a maioria sem nenhuma questão de prática ainda,
    então o padrão antigo caía quase sempre em "nenhuma questão ainda"
    na primeira renderização (ex: "acustica" antes de "optica", que tem
    prática cadastrada). Usada tanto pela Home (valor inicial do
    seletor) quanto pela Trilha (pra pular a Home de vez numa sessão
    nova, ver _renderizar_tela_trilha)."""
    com_pratica = db.materias_com_banco_pratica(area)
    if com_pratica:
        return com_pratica[0]
    return materias_da_area[0] if materias_da_area else ""


def _renderizar_home_banco_pratica() -> None:
    """Tela "Home" do handoff (README.md, seção 1): escolha de área/
    matéria/fonte + prévia das missões do dia + CTA "Começar sessão".
    Componentes nativos do Streamlit só onde há entrada real
    (radio/selectbox/button) -- streak/rank e o card de missões usam
    os helpers prontos de enem_theme.py (header/missions_card), sem
    st.progress (o handoff pede a barra própria dos helpers, que aceita
    a sombra sólida e o raio grande que o widget nativo não aceita)."""
    streak = db.calcular_ofensiva()
    nivel = db.calcular_nivel_jogador()
    enem_theme.header("Banco de Questões", streak=streak["atual"], rank=nivel["rank"], xp=nivel["xp"])

    st.caption(
        "Questões fora do ENEM oficial — trazidas de sessões de estudo com IA sobre um assunto "
        "específico (ex: Óptica). Pra adicionar questões novas: Admin → 🧠 Banco de prática."
    )

    missoes = db.missoes_do_dia()
    if missoes:
        enem_theme.missions_card([
            enem_theme.Mission(
                m["titulo"], m["descricao"],
                m["progresso_atual"] / m["progresso_meta"] if m["progresso_meta"] else 0,
                tone=_TOM_MISSAO.get(m["id"], "neutral"), done=m["concluida"],
            )
            for m in missoes
        ])

    area_atual = st.session_state.get("banco_pratica_area_atual", "ciencias_natureza")
    materias_area_atual = db.materias_validas(area_atual)
    if not materias_area_atual:
        st.info("Nenhuma matéria válida cadastrada pra essa área.")
        return

    materia_atual = st.session_state.get("banco_pratica_materia_atual")
    if materia_atual not in materias_area_atual:
        materia_atual = _padrao_materia_banco_pratica(area_atual, materias_area_atual)
    fonte_atual = st.session_state.get("banco_pratica_fonte_atual")

    area_sel = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True,
        index=["matematica", "ciencias_natureza"].index(area_atual), key="banco_pratica_area_input",
    )
    materias_area_sel = db.materias_validas(area_sel)
    if area_sel != area_atual and materia_atual not in materias_area_sel:
        materia_atual = _padrao_materia_banco_pratica(area_sel, materias_area_sel)
    indice_materia = materias_area_sel.index(materia_atual) if materia_atual in materias_area_sel else 0
    materia_sel = st.selectbox("Matéria", materias_area_sel, index=indice_materia, key="banco_pratica_materia_input")

    fontes = db.fontes_banco_pratica()
    fonte_sel = None
    if fontes:
        opcoes_fonte = ["Todas"] + fontes
        indice_fonte = opcoes_fonte.index(fonte_atual) if fonte_atual in opcoes_fonte else 0
        escolha_fonte = st.selectbox("Fonte", opcoes_fonte, index=indice_fonte, key="banco_pratica_fonte_input")
        fonte_sel = None if escolha_fonte == "Todas" else escolha_fonte

    trilha_previa = db.trilha_banco_pratica(area_sel, materia_sel, fonte=fonte_sel)
    if not trilha_previa:
        st.info(
            f"Nenhuma questão do banco de prática ainda em '{materia_sel}'"
            + (f" da fonte '{fonte_sel}'" if fonte_sel else "")
            + ". Adicione em Admin → 🧠 Banco de prática."
        )
        return

    if st.button(f"COMEÇAR SESSÃO — {len(trilha_previa)} nó(s)", type="primary", use_container_width=True):
        st.session_state["banco_pratica_area_atual"] = area_sel
        st.session_state["banco_pratica_materia_atual"] = materia_sel
        st.session_state["banco_pratica_fonte_atual"] = fonte_sel
        st.session_state["banco_pratica_tela"] = "trilha"
        st.rerun()


def _renderizar_tela_trilha() -> None:
    """Tela "Trilha" do handoff (README.md, seção 2): banner da unidade
    (matéria como conteúdo de primeira classe -- pedido explícito
    anterior do usuário) + percurso de nós + mascote + coluna de
    gamificação. Lê a seleção feita na Home (session_state) -- nenhuma
    lógica de trilha/XP/missão muda, só a apresentação.

    Numa sessão nova (1a visita, F5) sem matéria escolhida ainda, entra
    DIRETO na trilha usando o padrão esperto (_padrao_materia_banco_
    pratica) em vez de voltar pra Home e obrigar um clique manual em
    "COMEÇAR SESSÃO" -- pedido explícito do usuário: a Home deixa de
    ser a tela inicial de fato, só continua existindo pra quem quer
    trocar de matéria (botão "⬅️ Trocar matéria" em
    _renderizar_mapa_trilha)."""
    area_sel = st.session_state.get("banco_pratica_area_atual", "ciencias_natureza")
    materia_sel = st.session_state.get("banco_pratica_materia_atual")
    fonte_sel = st.session_state.get("banco_pratica_fonte_atual")
    materias_area = db.materias_validas(area_sel)
    if not materia_sel or materia_sel not in materias_area:
        materia_sel = _padrao_materia_banco_pratica(area_sel, materias_area) if materias_area else ""
        if not materia_sel:
            # Nem a taxonomia tem matéria válida pra essa área -- não
            # tem trilha nenhuma possível de montar, Home é quem sabe
            # mostrar esse vazio (st.info "Nenhuma matéria válida...").
            st.session_state["banco_pratica_tela"] = "home"
            st.rerun()
            return
        st.session_state["banco_pratica_area_atual"] = area_sel
        st.session_state["banco_pratica_materia_atual"] = materia_sel
        st.session_state["banco_pratica_fonte_atual"] = None
        fonte_sel = None

    trilha = db.trilha_banco_pratica(area_sel, materia_sel, fonte=fonte_sel)
    if not trilha:
        st.info(f"Nenhuma questão do banco de prática ainda em '{materia_sel}'.")
        if st.button("⬅️ Voltar"):
            st.session_state["banco_pratica_tela"] = "home"
            st.rerun()
        return

    chave_base = f"{area_sel}_{materia_sel}_{fonte_sel or 'todas'}"
    chave_no_ativo = f"trilha_no_ativo_{chave_base}"

    # Clique direto na bolinha da trilha -- pedido explícito do usuário:
    # mesma interação do app mobile, tocar no nó abre ele, não um botão
    # separado embaixo. enem_theme.trilha() embrulha cada nó
    # desbloqueado num <a href="?...&no=N">, o MESMO truque zero-JS que
    # navegacao_lateral() já usa pra página/tema (não é a tentativa com
    # JavaScript que já falhou antes -- ver docstring da gaveta em
    # ui_theme.py -- é link puro, sempre funciona em qualquer
    # navegador). Lido e IMEDIATAMENTE removido da URL: senão um F5 na
    # tela do nó reabriria ele de novo pra sempre, e voltar pra trilha
    # por outro caminho deixaria o parâmetro preso na barra de
    # endereço, incoerente com session_state (a fonte de verdade de
    # "qual nó está ativo" continua sendo session_state, igual antes --
    # a URL só entrega o clique inicial).
    no_da_url = st.query_params.pop("no", None)
    if no_da_url is not None:
        try:
            indice_clicado = int(no_da_url)
        except ValueError:
            indice_clicado = -1
        if 0 <= indice_clicado < len(trilha) and trilha[indice_clicado]["desbloqueado"]:
            st.session_state[chave_no_ativo] = indice_clicado
            pos_inicial = next(
                (i for i, q in enumerate(trilha[indice_clicado]["questoes"]) if not q["ja_respondida"]), 0,
            )
            st.session_state[f"trilha_pos_{chave_base}_{indice_clicado}"] = pos_inicial

    no_ativo_idx = st.session_state.get(chave_no_ativo)

    if no_ativo_idx is not None and no_ativo_idx < len(trilha):
        _renderizar_no_trilha_ativo(trilha[no_ativo_idx], chave_base, no_ativo_idx, len(trilha))
    else:
        if no_ativo_idx is not None:
            # a trilha mudou de tamanho (ex: questão nova cadastrada
            # no meio da sessão) e o nó ativo não existe mais -- volta
            # pro mapa em vez de quebrar tentando renderizar um índice
            # inválido.
            del st.session_state[chave_no_ativo]
        _renderizar_mapa_trilha(trilha, materia_sel, area_sel)


def _renderizar_mapa_trilha(trilha: list[dict], materia_sel: str, area_sel: str) -> None:
    """Cabeçalho + banner "continue de onde parou" + trilha visual +
    Pipo + coluna lateral (missões, liga, baú) -- tela "Trilha" do
    handoff, agora usando o helper enem_theme.trilha() em vez de HTML
    próprio (segunda rodada do handoff, ver docstring de
    render_banco_pratica). Duas adaptações deliberadas em relação ao
    mockup:

    1. Menu lateral fixo de 268px do mockup: implementado via CSS puro
       em cima da MESMA gaveta hamburguer/checkbox de sempre (ver
       ui_theme._CSS, bloco "@media (min-width: 1100px)") -- acima
       desse corte ela fica sempre aberta e o hambúrguer some; abaixo
       continua exatamente como era (nenhum bug de responsividade
       reaberto). Pedido explícito do usuário depois de ver a mesma
       sidebar já funcionando no app mobile (mobile/src/components/
       app-tabs.web.tsx) -- antes disto ficava de fora por ser mudança
       de infraestrutura mais arriscada do que o pedido original de
       "mesma cara" pedia.
    2. enem_theme.trilha() gera as âncoras por fórmula (não a lista
       fixa de 5 do mockup) porque uma matéria real pode ter mais de
       5 nós -- ver comentário em enem_theme.py.

    "Liga Diamante" e "Baú de XP" são decorativos por pedido explícito
    do usuário (aprovado cientes de que são fictícios/sem sistema de
    moeda por trás) -- ver conversa. A linha "Você" na liga usa XP
    real; as outras posições são fixas/fictícias."""
    concluidos = sum(1 for n in trilha if n["concluido"])
    no_atual = next((n for n in trilha if n["desbloqueado"] and not n["concluido"]), None)
    nivel = db.calcular_nivel_jogador()
    streak = db.calcular_ofensiva()
    missoes = db.missoes_do_dia()

    # Marcador vazio + .ex-desktop-cols: fica irmão direto do
    # stHorizontalBlock do st.columns logo abaixo, o que dá um gancho
    # CSS (ver theme.css, seção 8) pra esconder só a coluna lateral em
    # telas estreitas sem afetar st.columns(...) de outras páginas.
    st.markdown('<div class="ex-desktop-cols"></div>', unsafe_allow_html=True)
    col_principal, col_lateral = st.columns([2, 1], gap="large")

    with col_principal:
        enem_theme.header(materia_sel.capitalize(), streak=streak["atual"], rank=nivel["rank"], xp=nivel["xp"])

        if st.button("⬅️ Trocar matéria", key="trilha_voltar_home", type="secondary"):
            st.session_state["banco_pratica_tela"] = "home"
            st.rerun()

        current_1based = (no_atual["indice"] + 1) if no_atual else len(trilha) + 1
        area_label = RÓTULO_AREA.get(area_sel, area_sel)
        if no_atual:
            kicker = f"{area_label.upper()} · {concluidos} DE {len(trilha)} NÓ(S) CONCLUÍDO(S)"
            titulo = f"Continue de onde parou — Nó {current_1based}"
        else:
            kicker = f"{area_label.upper()} · {materia_sel.upper()}"
            titulo = "Trilha concluída!"
        enem_theme.banner_continuar(kicker, titulo)

        # Pipoco "areia" com manchas nesta tela especificamente -- mesma
        # variação da tela "Trilha" do projeto de design (dc-import
        # scene="fogueira" pattern="patches"), espelhando o que já foi
        # feito no app mobile (ver trilha-path.tsx) em vez do gatinho
        # branco liso genérico de ui_theme.mascote_html().
        _MASCOTE_TRILHA = dict(color="#F5C98A", shadow="#C99A5B", pattern="patches", patch="#E0A05C")
        if no_atual:
            frase = f"Cinco questões e o Nó {no_atual['indice'] + 2} abre. Vamos?" if no_atual["indice"] + 1 < len(trilha) else "Última leva! Bora fechar com chave de ouro."
            mascote_bloco = (
                '<div class="ex-card" style="display:flex;align-items:center;gap:16px;padding:14px 20px 14px 14px">'
                f'{ui_theme.mascote_html("happy", size=0.7, **_MASCOTE_TRILHA)}'
                '<div style="font-weight:600;font-size:14px;color:var(--ink-2);line-height:1.5">'
                f'"{frase}" — <span style="color:var(--lime);font-weight:800">Pipoco</span></div>'
                '</div>'
            )
        else:
            mascote_bloco = (
                '<div class="ex-card" style="display:flex;align-items:center;gap:16px;padding:14px 20px 14px 14px">'
                f'{ui_theme.mascote_html("cheer", size=0.7, **_MASCOTE_TRILHA)}'
                '<div style="font-weight:600;font-size:14px;color:var(--ink-2);line-height:1.5">'
                '"Você zerou essa trilha!" — <span style="color:var(--lime);font-weight:800">Pipoco</span></div>'
                '</div>'
            )
        # As bolinhas da trilha SÃO o botão agora -- pedido explícito do
        # usuário: tocar no nó abre ele, igual no app mobile, sem lista
        # de botão separada embaixo repetindo "Nó N" (isso já foi tirado
        # daqui uma vez). no_href_base vira, dentro de enem_theme.trilha(),
        # um <a href="...&no=I"> de verdade em cada nó desbloqueado --
        # zero JS, mesmo truque que a navegação lateral já usa (ver
        # docstring de trilha() e o tratamento de ?no= no topo desta
        # função). tema preservado no link pra não voltar pro escuro ao
        # clicar num nó com o claro ativado.
        tema_atual = st.query_params.get("tema", "escuro")
        enem_theme.trilha(
            materia_sel.capitalize(), area_label,
            nodes=len(trilha), done=concluidos, current=current_1based,
            mascote_bloco=mascote_bloco,
            no_href_base=f"?pagina=cartao&tema={tema_atual}",
        )

    with col_lateral:
        _renderizar_sidebar_gamificacao(missoes, nivel, concluidos)


def _renderizar_sidebar_gamificacao(missoes: list[dict], nivel: dict, nos_concluidos: int) -> None:
    """Coluna lateral direita do layout "Desktop" do design: missões
    reais via enem_theme.missions_card() (mesmo helper da Home) + Liga
    Diamante (fictícia, decorativa) + Baú (decorativo, marco a cada 3
    nós concluídos) -- ver docstring de _renderizar_mapa_trilha pra por
    que Liga/Baú são fictícios. Liga/Baú não têm helper pronto em
    enem_theme.py, então usam as classes .ex-card/.ex-pill dele
    diretamente -- mesma folha de estilo, sem inventar um terceiro
    vocabulário de CSS."""
    if missoes:
        enem_theme.missions_card([
            enem_theme.Mission(
                m["titulo"], m["descricao"],
                m["progresso_atual"] / m["progresso_meta"] if m["progresso_meta"] else 0,
                tone=_TOM_MISSAO.get(m["id"], "neutral"), done=m["concluida"],
            )
            for m in missoes
        ])
    else:
        with st.container(border=True):
            st.caption("Nenhuma tentativa hoje ainda.")

    st.markdown(
        '<div class="ex-card">'
        '  <div class="ex-card-head"><div class="ex-card-title">Liga Diamante</div></div>'
        '  <div class="ex-pill" style="width:100%;justify-content:space-between;margin-bottom:8px">'
        '    <span>1 · Marina S.</span><span>6120</span></div>'
        '  <div class="ex-pill" style="width:100%;justify-content:space-between;margin-bottom:8px">'
        '    <span>2 · Caio R.</span><span>5480</span></div>'
        f'  <div class="ex-pill on" style="width:100%;justify-content:space-between">'
        f'    <span>3 · Você</span><span>{nivel["xp"]}</span></div>'
        '  <div style="font-size:11px;color:var(--ink-3);margin-top:10px">'
        'Ilustrativo por enquanto — vira liga de verdade quando houver mais alunos.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    proximo_marco = ((nos_concluidos // 3) + 1) * 3
    faltam = proximo_marco - nos_concluidos
    st.markdown(
        '<div class="ex-card" style="background:var(--amber-bg);border-color:var(--amber-bd);'
        'display:flex;align-items:center;gap:14px">'
        '  <div style="width:44px;height:44px;border-radius:15px;background:var(--amber);'
        f'box-shadow:0 4px 0 var(--amber-sh);display:flex;align-items:center;justify-content:center;'
        f'flex:0 0 auto">{enem_theme.icon("bolt", 22, "#3A2A00")}</div>'
        f'  <div style="font-weight:700;font-size:13.5px;color:#FFD98A;line-height:1.45">'
        f'Marco especial em {faltam} nó(s) — sem recompensa de verdade ainda, só um lembrete visual '
        'de progresso.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _renderizar_no_trilha_ativo(no: dict, chave_base: str, no_indice: int, total_nos: int) -> None:
    """Uma questão de cada vez, com feedback imediato antes de avançar
    -- a dinâmica de exercício do Duolingo que o usuário pediu, em vez
    da grade em lote (responde tudo, corrige tudo no final) que o
    resto do app usa. Cada resposta já grava via
    db.registrar_tentativa() na hora (mesmo Leitner/histórico de
    qualquer outra tentativa), não espera o nó terminar pra gravar."""
    questoes = no["questoes"]
    chave_pos = f"trilha_pos_{chave_base}_{no_indice}"
    chave_no_ativo = f"trilha_no_ativo_{chave_base}"
    pos = st.session_state.get(chave_pos, 0)

    if st.button("⬅️ Voltar pra trilha", key=f"trilha_sair_{chave_base}_{no_indice}"):
        del st.session_state[chave_no_ativo]
        st.rerun()

    if pos >= len(questoes):
        st.success(f"✅ Nó {no_indice + 1} concluído! {len(questoes)} questão(ões) respondida(s) nesta rodada.")
        if no_indice + 1 < total_nos:
            if st.button("Próximo nó ➜", type="primary", key=f"trilha_prox_{chave_base}_{no_indice}"):
                del st.session_state[chave_no_ativo]
                st.rerun()
        else:
            st.caption("Essa era a última leva desta matéria no banco de prática. 🎉")
        return

    q = questoes[pos]
    st.progress(pos / len(questoes), text=f"Questão {pos + 1} de {len(questoes)}")

    texto = q.get("enunciado_texto") or ""
    corpo, alternativas = _separar_alternativas_banco_pratica(texto)

    with st.container(border=True):
        if q.get("fonte"):
            st.caption(f"🧠 Banco de prática · fonte: {q['fonte']}")
        st.write(corpo or texto)
        if q.get("enunciado_imagem_path") and Path(q["enunciado_imagem_path"]).exists():
            st.image(q["enunciado_imagem_path"])

    chave_resultado = f"trilha_resultado_{chave_base}_{no_indice}_{pos}"
    resultado = st.session_state.get(chave_resultado)

    if resultado is None:
        chave_radio = f"trilha_radio_{chave_base}_{no_indice}_{pos}"
        if alternativas:
            escolha = st.radio(
                "Resposta", ["—", "A", "B", "C", "D", "E"],
                format_func=lambda letra, alt=alternativas: f"{letra}) {alt[letra]}" if letra in alt else "Selecione uma alternativa",
                key=chave_radio,
            )
        else:
            escolha = st.radio("Resposta", ["—", "A", "B", "C", "D", "E"], horizontal=True, key=chave_radio)

        if st.button("Confirmar", type="primary", disabled=(escolha == "—"), key=f"trilha_confirmar_{chave_base}_{no_indice}_{pos}"):
            resultado_novo = db.registrar_tentativa(q["id_questao"], escolha)
            st.session_state[chave_resultado] = resultado_novo
            st.rerun()
    else:
        if resultado["resultado"] == "acertou":
            st.success(f"✅ Certo! A resposta era {resultado['alternativa_correta']}.")
        else:
            marcou = resultado["resposta_escolhida"] or "— (em branco)"
            st.error(f"❌ Você marcou {marcou}. A resposta certa era {resultado['alternativa_correta']}.")
        if st.button("Continuar ➜", type="primary", key=f"trilha_continuar_{chave_base}_{no_indice}_{pos}"):
            st.session_state[chave_pos] = pos + 1
            st.rerun()


def _renderizar_prova_no_a_no(ano: int, caderno: str, area: str) -> None:
    """"Corrige a cada questão" do wizard Montar Prova -- mesma
    dinâmica de feedback imediato que _renderizar_no_trilha_ativo já
    usa pro banco de prática, só que pra uma prova REAL (ENEM oficial):
    cada resposta é gravada e corrigida NA HORA via
    db.registrar_tentativa(), avançando uma questão de cada vez, em vez
    do lote (responde tudo, corrige no fim) que
    _renderizar_grade_questoes usa pros outros dois "como responder"
    (Com cronômetro / Sem pressa). Usa _mostrar_enunciado_exame() --
    mesma função que "Prova com enunciado" já usa -- pra mostrar
    enunciado+imagem com segurança (texto de PDF pode ter '<'/'>' de
    verdade, por isso não é markdown com HTML)."""
    sufixo = f"noano_{ano}_{caderno}_{area}"
    questoes = db.listar_questoes_da_prova(ano, caderno, area)
    if not questoes:
        st.info("Essa prova não tem questões cadastradas.")
        return

    chave_pos = f"prova_no_a_no_pos_{sufixo}"
    pos = st.session_state.get(chave_pos, 0)

    if st.button("⬅️ Trocar prova", key=f"prova_no_a_no_sair_{sufixo}"):
        st.session_state[chave_pos] = 0
        for chave in ("montar_prova_ano", "montar_prova_area", "montar_prova_modo"):
            st.session_state.pop(chave, None)
        st.rerun()

    if pos >= len(questoes):
        acertos = sum(
            1 for q in questoes
            if st.session_state.get(f"prova_no_a_no_resultado_{sufixo}_{q['id_questao']}", {}).get("resultado") == "acertou"
        )
        st.success(f"✅ Prova concluída! {acertos}/{len(questoes)} acertos.")
        return

    q = questoes[pos]
    st.progress(pos / len(questoes), text=f"Questão {q['numero_questao']} · {pos + 1} de {len(questoes)}")

    alternativas = _mostrar_enunciado_exame(q)

    chave_resultado = f"prova_no_a_no_resultado_{sufixo}_{q['id_questao']}"
    resultado = st.session_state.get(chave_resultado)

    if resultado is None:
        chave_radio = f"prova_no_a_no_radio_{sufixo}_{q['id_questao']}"
        if alternativas:
            escolha = st.radio(
                "Resposta", ["—", "A", "B", "C", "D", "E"],
                format_func=lambda letra, alt=alternativas: f"{letra}) {alt[letra]}" if letra in alt else "Selecione uma alternativa",
                key=chave_radio,
            )
        else:
            escolha = st.radio("Resposta", ["—", "A", "B", "C", "D", "E"], horizontal=True, key=chave_radio)

        if st.button("Confirmar", type="primary", disabled=(escolha == "—"), key=f"prova_no_a_no_confirmar_{sufixo}_{q['id_questao']}"):
            resultado_novo = db.registrar_tentativa(q["id_questao"], escolha)
            st.session_state[chave_resultado] = resultado_novo
            st.rerun()
    else:
        if resultado["resultado"] == "acertou":
            st.success(f"✅ Certo! A resposta era {resultado['alternativa_correta']}.")
        else:
            marcou = resultado["resposta_escolhida"] or "— (em branco)"
            st.error(f"❌ Você marcou {marcou}. A resposta certa era {resultado['alternativa_correta']}.")
        if st.button("Continuar ➜", type="primary", key=f"prova_no_a_no_continuar_{sufixo}_{q['id_questao']}"):
            st.session_state[chave_pos] = pos + 1
            st.rerun()


def render_prova_beta() -> None:
    """Faz a prova inteira lendo o enunciado direto no site, sem
    precisar do PDF aberto do lado. Até a 10a rodada (2026-09) era uma
    página própria no menu ("separado de propósito", pedido antigo do
    usuário) -- juntada como mais um "Modo" dentro de "Provas ENEM"
    (render_cartao_resposta) a pedido explícito dele, mesma aba do
    carregador de gabarito CSV. Continua restrita a provas com
    enunciado_texto carregado (extração por PDF ainda é nova e ~40%
    das questões citam figura/gráfico/tabela que a extração de texto
    não captura -- ver extrair_enunciados_pdf.py -- marcadas com ⚠️ no
    início do texto). Mesmo mecanismo de correção/tracking de 'Uma
    prova por vez' por baixo (_renderizar_grade_questoes) -- só a
    origem das questões (só prova com enunciado carregado) e o aviso
    são diferentes."""
    st.warning(
        "🧪 **Beta** -- lê o enunciado extraído automaticamente do PDF oficial. "
        "~40% das questões citam figura/gráfico/tabela que a extração de texto sozinha não "
        "captura (aparecem com ⚠️ no início) -- confere contra o PDF nessas. O resto "
        "funciona igual ao Cartão-resposta normal (mesma correção, mesmo histórico)."
    )

    provas = db.provas_com_enunciado()
    if not provas:
        st.info("Nenhuma prova com enunciado carregado ainda -- rode extrair_enunciados_pdf.py primeiro.")
        return

    opcoes = {
        f"{ano} — {caderno} — {RÓTULO_AREA.get(area, area)} ({com_enunciado}/{total} com enunciado)": (ano, caderno, area)
        for ano, caderno, area, com_enunciado, total in provas
    }
    escolha = st.selectbox("Prova", list(opcoes.keys()), key="beta_prova_sel")
    ano_sel, caderno_sel, area_sel = opcoes[escolha]

    questoes = db.listar_questoes_da_prova(ano_sel, caderno_sel, area_sel)
    _renderizar_grade_questoes(questoes, sufixo=f"beta_{ano_sel}_{caderno_sel}_{area_sel}", estilo_exame=True)


def render_simulados_feitos() -> None:
    """Lista toda prova com ao menos uma tentativa registrada -- pra
    responder 'quais provas eu já fiz' sem precisar abrir cada uma
    em 'Uma prova por vez' e olhar o expander de histórico ali dentro.
    Cada rodada é a mesma numeração que resumo_por_tentativa() já
    deriva (não inventa sessão nova) -- só reúne isso por prova e
    permite nomear/rever mais fácil, num lugar só."""
    simulados = db.simulados_feitos()
    if not simulados:
        st.info("Nenhum simulado respondido ainda -- assim que você corrigir a primeira prova, ela aparece aqui.")
        return

    st.caption(f"{len(simulados)} prova(s) com pelo menos uma tentativa registrada.")

    for s in simulados:
        ultima = s["rodadas"][-1]
        cobertura = f"{ultima['total']}/{s['total_questoes']}"
        titulo = f"{s['ano']} — {s['caderno']} — {RÓTULO_AREA.get(s['grande_area'], s['grande_area'])}"
        pct_ultima = f"{ultima['taxa_acerto']*100:.0f}%" if ultima["taxa_acerto"] is not None else "—"

        with st.expander(f"{titulo} — última tentativa: {ultima['acertos']}/{ultima['total']} ({pct_ultima}) — cobertura {cobertura}"):
            for r in s["rodadas"]:
                pct = f"{r['taxa_acerto']*100:.0f}%" if r["taxa_acerto"] is not None else "—"
                rotulo = f"Tentativa {r['tentativa']}" + (f" — {r['nome']}" if r["nome"] else "")
                sufixo_rodada = f"{s['ano']}_{s['caderno']}_{s['grande_area']}_{r['tentativa']}"

                col_txt, col_nome = st.columns([3, 2])
                with col_txt:
                    st.write(f"**{rotulo}**: {r['acertos']}/{r['total']} ({pct}) — {r['inicio'][:10]}")
                with col_nome:
                    novo_nome = st.text_input(
                        "Nome", value=r["nome"], placeholder="ex: fiz cansado à noite",
                        key=f"nome_simulados_feitos_{sufixo_rodada}", label_visibility="collapsed",
                    )
                    if novo_nome != r["nome"] and novo_nome.strip():
                        db.nomear_tentativa(s["ano"], s["caderno"], s["grande_area"], r["tentativa"], novo_nome)
                        st.rerun()

                with st.expander("📋 Ver detalhes (pra colar na IA)"):
                    detalhe_texto = db.detalhe_rodada(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                    linhas_texto = [f"{titulo} — {rotulo}", f"{r['acertos']}/{r['total']} acertos", ""]
                    for item in detalhe_texto:
                        if item["resposta_escolhida"] is None:
                            linhas_texto.append(f"Q{item['numero_questao']}: NÃO RESPONDI — gabarito {item['alternativa_correta']}")
                        elif item["resultado"] == "acertou":
                            linhas_texto.append(f"Q{item['numero_questao']}: acertei (marquei {item['resposta_escolhida']})")
                        else:
                            linhas_texto.append(f"Q{item['numero_questao']}: ERREI — marquei {item['resposta_escolhida']}, gabarito {item['alternativa_correta']}")
                    st.code("\n".join(linhas_texto), language=None)

                col_editar, col_excluir = st.columns(2)
                with col_editar:
                    with st.popover("✏️ Editar respostas", key=f"popover_editar_{sufixo_rodada}"):
                        detalhe = db.detalhe_rodada(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                        opcoes_letra = ["— (não respondida)", "A", "B", "C", "D", "E"]
                        alteracoes = {}
                        for item in detalhe:
                            valor_atual = item["resposta_escolhida"] or "— (não respondida)"
                            nova = st.selectbox(
                                f"Q{item['numero_questao']} (gabarito {item['alternativa_correta']})",
                                opcoes_letra,
                                index=opcoes_letra.index(valor_atual),
                                key=f"editar_{sufixo_rodada}_{item['id_tentativa']}",
                            )
                            if nova != valor_atual:
                                alteracoes[item["id_tentativa"]] = None if nova == "— (não respondida)" else nova
                        if st.button(
                            f"Salvar {len(alteracoes)} alteração(ões)" if alteracoes else "Nenhuma alteração",
                            disabled=not alteracoes, key=f"salvar_editar_{sufixo_rodada}",
                        ):
                            for id_tentativa, nova_resposta in alteracoes.items():
                                db.editar_resposta_tentativa(id_tentativa, nova_resposta)
                            st.rerun()
                with col_excluir:
                    with st.popover("🗑️ Excluir esta rodada", key=f"popover_excluir_{sufixo_rodada}"):
                        st.caption(
                            "Apaga essa rodada inteira (todas as respostas dela) e recalcula a revisão "
                            "espaçada de cada questão como se essa rodada nunca tivesse acontecido. "
                            "Não desfaz -- pra reenvio duplicado ou rodada errada, não pra 'não gostei do resultado'."
                        )
                        confirmar = st.checkbox(
                            f"Confirmo apagar a Tentativa {r['tentativa']} de {titulo}",
                            key=f"confirmar_excluir_{sufixo_rodada}",
                        )
                        if st.button("Apagar rodada", type="primary", disabled=not confirmar, key=f"excluir_{sufixo_rodada}"):
                            db.apagar_rodada_tentativa(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                            st.rerun()
                st.divider()
            if ultima["total"] < s["total_questoes"]:
                st.caption(f"{s['total_questoes'] - ultima['total']} questão(ões) dessa prova ainda sem tentativa nenhuma.")


def _renderizar_grade_questoes(
    questoes: list[dict], sufixo: str, estilo_exame: bool = False,
    titulo_bloco: str = "", kicker_bloco: str = "",
) -> None:
    """Núcleo compartilhado por prova única, simulado, revisão do dia,
    prática por matéria e a prova beta com enunciado: grade de
    resposta A-E, correção contra o gabarito via registrar_tentativa(),
    classificação de erro e vídeo de resolução. Todo mundo que monta
    uma lista de questões (não importa a origem) cai aqui — não
    duplica essa lógica em cada modo.

    `titulo_bloco`/`kicker_bloco` (opcionais): cabeçalho "CADERNO ·
    ÁREA" + "ENEM 2025" só faz sentido quando as questões vêm de UMA
    prova específica (só _renderizar_bloco_prova passa isso) -- Revisão
    de hoje e Praticar por matéria misturam ano/prova de propósito,
    então ficam sem esse cabeçalho (string vazia = não renderiza).

    estilo_exame=True troca só a PARTE DE ENTRADA (como a questão é
    exibida antes de responder) pro layout "uma embaixo da outra, com
    o enunciado inteiro visível antes da resposta", pedido explícito
    do usuário pra prova beta parecer com o PDF do ENEM em vez do
    cartão-resposta compacto. Tudo depois de responder (corrigir,
    desfazer, ver o que marcou, erros) continua idêntico nos dois
    estilos -- inclusive o "⚡ Preenchimento rápido" (colar sequência),
    que ANTES só aparecia fora de estilo_exame (raciocínio: "não faz
    sentido colar sequência numa prova que você está lendo pela
    primeira vez") -- pedido explícito do usuário pra reverter isso:
    o simulado completo serve tanto pra quem lê a questão no app e
    responde na hora quanto pra quem resolve no papel/PDF impresso e só
    quer digitar o gabarito depois, sem rolar a tela toda pra achar
    cada rádio -- caso em que colar sequência é exatamente a ferramenta
    certa, mesmo no estilo "uma questão por vez com enunciado".

    Modo Cartão/Foco (design_handoff_enem_gamificado/App ENEM.dc.html,
    Turno 2 -- ver DesignSync 2026-09-09): só aparece quando
    estilo_exame=False (a prova beta já mostra a questão inteira, uma
    de cada vez, não precisa de um segundo "modo foco" por cima). Os
    dois modos leem/escrevem as MESMAS chaves resp_{id_questao} do
    session_state, então trocar de modo no meio da sessão não perde
    nada respondido -- só o Cartão fica dentro do st.form (resposta em
    lote, sem rerun por clique, testado em prova real de até ~180
    questões); o Foco fica FORA do form de propósito (precisa de rerun
    a cada Anterior/Próxima/salto, senão a barra de progresso e o
    grid de saltos nunca atualizariam).

    Modo Cartão reformatado (2026-09, 9a rodada): número + A-E numa
    ÚNICA linha por questão (`st.columns([1, 5], gap="small")` aninhada
    dentro de cada uma das 3 colunas externas) em vez do rótulo nativo
    do st.radio (que o Streamlit sempre desenha numa linha ACIMA do
    grupo de opções, nunca ao lado) -- era essa pilha vertical,
    comparada ao "número e letras na mesma linha" do mockup (App
    ENEM.dc.html, Turno 2, seção 2a), que o usuário reportou como "não
    formatado direito". Colunas aninhadas em vez de um truque de CSS
    por seletor-irmão porque o resultado não depende de nenhum detalhe
    de versão do DOM interno do Streamlit pra funcionar -- mesmo
    raciocínio de ".ex-desktop-cols"/"grade-blocos" (preferir o
    primitivo nativo quando ele resolve), só que aqui o primitivo
    nativo (colunas) já basta, não precisa de CSS adicional nenhum.
    Contagem de respondida/em branco e o resumo por matéria no rail
    lateral refletem o estado como da ÚLTIMA vez que o form rodou
    (session_state de widget DENTRO de um st.form só atualiza no
    submit) -- mesma limitação, documentada, do contador ao vivo que a
    8a rodada já tinha descartado por ser arquiteturalmente impossível
    sem abrir mão do envio em lote; não é um live counter, é um
    retrato "desde a última correção/aplicação de sequência"."""
    _renderizar_editor_enunciado(questoes, sufixo)

    with st.expander("⚡ Preenchimento rápido (cola a sequência de letras)"):
        st.caption(
            "Cola as letras na ordem das questões, sem espaço nem pontuação (ex: ABCDEBAACD...). "
            "Use * ou deixa em branco pra pular uma questão que você não respondeu."
        )
        sequencia = st.text_input("Sequência de respostas", key=f"sequencia_rapida_{sufixo}")
        if st.button("Aplicar sequência", key=f"aplicar_seq_{sufixo}"):
            aplicadas = 0
            for i, q in enumerate(questoes):
                letra = sequencia[i].upper() if i < len(sequencia) else "*"
                chave_resp = f"resp_{q['id_questao']}"
                if letra in "ABCDE":
                    st.session_state[chave_resp] = letra
                    aplicadas += 1
                else:
                    # * (ou string mais curta que a prova) LIMPA a
                    # resposta de propósito -- sem isso, colar uma
                    # sequência corrigida com * numa posição que já
                    # tinha letra de uma aplicação anterior deixava a
                    # letra velha lá (só escrevia em cima de A-E, nunca
                    # apagava), então "pular" não pulava de verdade se
                    # já tinha algo marcado ali antes.
                    st.session_state[chave_resp] = "—"
            st.success(f"{aplicadas} resposta(s) aplicada(s) — confere a grade abaixo antes de corrigir.")

    # Ano de questão do banco de prática é um sentinela (ANO_BANCO_PRATICA
    # = 0, ver db.py), não um ano de prova real -- fica fora da conta de
    # "mostrar ano", senão questão real + questão de prática misturadas
    # (ex: Praticar por matéria) fariam mostrar_ano=True e a questão de
    # prática rotularia "· 0" no lugar do ano.
    mostrar_ano = len({q["ano"] for q in questoes if q.get("origem") != "banco_pratica"}) > 1

    if titulo_bloco:
        st.markdown(
            f'<div style="margin-bottom:6px">'
            f'<div style="font-weight:800;font-size:12px;letter-spacing:.1em;'
            f'color:var(--tema-ink-3);text-transform:uppercase">{kicker_bloco}</div>'
            f'<div style="font-family:\'Baloo 2\',sans-serif;font-weight:800;font-size:22px;'
            f'color:var(--tema-ink)">{titulo_bloco}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    modo_foco = False
    if not estilo_exame:
        modo_foco = st.radio(
            "Modo de resposta", ["Cartão", "Foco"], horizontal=True,
            key=f"modo_resposta_{sufixo}", label_visibility="collapsed",
        ) == "Foco"

    if modo_foco:
        enviado = _renderizar_modo_foco(questoes, sufixo, mostrar_ano)
        _processar_correcao_e_resultados(questoes, sufixo, enviado)
        return

    # Rail lateral existe sempre que não é estilo_exame agora -- antes
    # só aparecia com mais de 1 matéria (só o card "Por matéria" morava
    # lá); o card novo "Marcadas p/ revisão" (App ENEM.dc.html, Turno 2,
    # seção 2a) é útil em QUALQUER grade, inclusive "Praticar por
    # matéria" (1 matéria só). _renderizar_rail_por_materia() continua
    # só sendo chamada quando há mais de 1 matéria de verdade -- ver
    # dentro de col_rail abaixo.
    materias_da_grade = sorted({q["materia"] for q in questoes if q.get("materia")})
    usar_rail = not estilo_exame
    if usar_rail:
        col_grade, col_rail = st.columns([3, 1])
    else:
        col_grade, col_rail = st.container(), None

    with col_grade:
        with st.form(f"cartao_resposta_form_{sufixo}"):
            enviado_topo = False
            if estilo_exame:
                # Uma questão por "linha", enunciado inteiro visível ANTES
                # da resposta -- igual abrir o caderno de prova de verdade:
                # lê a questão, só depois marca a letra. O grid compacto
                # (radio primeiro, enunciado escondido num expander depois)
                # faz sentido pra revisão rápida, não pra ler uma prova
                # pela primeira vez.
                for q in questoes:
                    rotulo = f"Questão {q['numero_questao']}" + (f" · {q['ano']}" if mostrar_ano else "")
                    if q["status_classificacao"] == "nao_classificado":
                        rotulo += " ⚠️"
                    st.markdown(f"##### {rotulo}")
                    alternativas = _mostrar_enunciado_exame(q)
                    if alternativas:
                        # Vertical (sem horizontal=True) de propósito: com
                        # o texto da alternativa embutido no rótulo, 5
                        # opções de frase inteira lado a lado ficariam
                        # espremidas -- só faz sentido horizontal quando a
                        # opção é uma letra sozinha.
                        #
                        # alt=alternativas (default arg, não closure sobre
                        # a variável do loop): sem isso, as ~90 lambdas
                        # deste for compartilham a MESMA célula de
                        # `alternativas`, que o Python só resolve no
                        # MOMENTO em que a lambda é chamada -- dentro do
                        # st.radio() da própria iteração isso nunca dá
                        # errado (é chamado na hora, com o valor certo),
                        # mas qualquer código que guarde essa função pra
                        # invocar depois (AppTest faz isso, pra computar o
                        # índice selecionado) pega o `alternativas` da
                        # ÚLTIMA questão do loop, não da questão dona do
                        # radio -- descoberto tentando testar isso via
                        # AppTest, não em uso real, mas era uma fragilidade
                        # de verdade independente do teste.
                        st.radio(
                            "Resposta", ["—", "A", "B", "C", "D", "E"],
                            format_func=lambda letra, alt=alternativas: f"{letra}) {alt[letra]}" if letra in alt else "Não respondida",
                            key=f"resp_{q['id_questao']}", label_visibility="collapsed",
                        )
                    else:
                        st.radio(
                            "Resposta", ["—", "A", "B", "C", "D", "E"],
                            horizontal=True, key=f"resp_{q['id_questao']}", label_visibility="collapsed",
                        )
                    st.divider()
            else:
                # Resumo respondida/em branco + botão Corrigir NO TOPO,
                # em vez de só no rodapé -- pedido explícito do usuário
                # (mockup App ENEM.dc.html, Turno 2, seção 2a: barra de
                # progresso + CORRIGIR acima da grade, não escondido
                # depois de rolar). Reflete session_state como ficou
                # depois da ÚLTIMA vez que o form rodou (submit ou
                # "Aplicar sequência"), não ao vivo -- ver docstring da
                # função sobre por que isso não dá pra ser diferente
                # dentro de um st.form.
                respondidas = sum(
                    1 for q in questoes if st.session_state.get(f"resp_{q['id_questao']}", "—") != "—"
                )
                em_branco = len(questoes) - respondidas
                pct_respondido = (respondidas / len(questoes) * 100) if questoes else 0
                st.markdown(
                    '<div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px">'
                    '  <div style="display:flex;align-items:baseline;justify-content:space-between;'
                    'flex-wrap:wrap;gap:10px">'
                    f'    <span style="font-weight:800;font-size:15px;color:var(--tema-ink)">'
                    f'{respondidas} de {len(questoes)} respondidas</span>'
                    f'    <span style="font-weight:700;font-size:13px;color:var(--tema-ink-3)">'
                    f'{em_branco} em branco</span>'
                    '  </div>'
                    '  <div style="height:12px;border-radius:999px;background:var(--tema-surface-3);'
                    'overflow:hidden;box-shadow:inset 0 2px 0 rgba(0,0,0,.3)">'
                    f'    <div style="width:{pct_respondido:.0f}%;height:100%;border-radius:999px;'
                    'background:var(--tema-lime);box-shadow:inset 0 3px 0 rgba(255,255,255,.32)"></div>'
                    '  </div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                enviado_topo = st.form_submit_button(
                    "Corrigir", type="primary", key=f"corrigir_topo_{sufixo}",
                )

                # Legenda + marcador ".grade-blocos": o marcador fica irmão
                # direto de cada stHorizontalBlock do st.columns(3) logo
                # abaixo (mesmo truque de seletor-irmão já usado em
                # .ex-desktop-cols, ver theme.css) -- dá um gancho CSS (ver
                # ui_theme.py) pra estilizar só ESTA grade como blocos
                # compactos (Turno 2 do handoff, App ENEM.dc.html, seção
                # 2a), sem afetar o radio vertical do estilo_exame acima
                # nem nenhum outro st.radio do resto do app.
                st.markdown(
                    '<div class="grade-blocos"></div>'
                    '<div style="display:flex;gap:14px;font-size:11.5px;font-weight:700;'
                    'color:var(--tema-ink-3);margin-bottom:10px">'
                    '<span><span style="display:inline-block;width:10px;height:10px;border-radius:3px;'
                    'background:var(--tema-lime);margin-right:5px"></span>respondida</span>'
                    '<span><span style="display:inline-block;width:10px;height:10px;border-radius:3px;'
                    'background:var(--tema-surface-2);border:1px solid #2C3342;margin-right:5px"></span>em branco</span>'
                    '<span><span style="display:inline-block;width:10px;height:10px;border-radius:3px;'
                    'background:var(--tema-amber-bg);border:1px solid var(--tema-amber-border);margin-right:5px">'
                    '</span>marcada p/ revisão</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                # Uma st.columns(3) NOVA por linha de 3, em vez de uma só pra
                # grade inteira -- com uma única chamada, cols[i % 3] distribui
                # "por coluna" (Q1,Q4,Q7... na coluna 0, Q2,Q5,Q8... na coluna
                # 1...), e no celular, onde o Streamlit empilha as colunas na
                # vertical, cada coluna renderiza seu bloco inteiro antes da
                # próxima -- a leitura vira 1,4,7,10...,2,5,8,11...,3,6,9,12...,
                # parecendo que questão foi pulada. Uma st.columns(3) por linha
                # preserva a ordem sequencial mesmo empilhada.
                for inicio in range(0, len(questoes), 3):
                    cols = st.columns(3)
                    for col, q in zip(cols, questoes[inicio:inicio + 3]):
                        with col:
                            # Número + A-E na MESMA linha via colunas
                            # aninhadas (1 pro número, 5 pro grupo de
                            # opções) -- o rótulo nativo do st.radio
                            # (agora escondido, label_visibility=
                            # "collapsed") sempre desenha numa linha
                            # ACIMA do grupo, nunca ao lado; era essa
                            # pilha vertical que ficava "não formatada"
                            # comparada ao mockup (número e letras juntos
                            # na mesma linha).
                            col_num, col_resp = st.columns([1, 5], gap="small")
                            with col_num:
                                if q.get("origem") == "banco_pratica":
                                    numero_texto = f'Pr{q["numero_questao"]}'
                                elif mostrar_ano:
                                    numero_texto = f'{q["numero_questao"]}·{q["ano"]}'
                                else:
                                    numero_texto = str(q["numero_questao"])
                                aviso_html = (
                                    ' <span title="matéria não classificada" '
                                    'style="color:var(--tema-coral);font-weight:800">!</span>'
                                    if q["status_classificacao"] == "nao_classificado" else ""
                                )
                                # Lida ANTES de desenhar o checkbox de propósito
                                # -- mesma limitação/convenção de frescor do
                                # resto do form (reflete a última vez que ele
                                # rodou, não ao vivo -- ver docstring da
                                # função). Cor do número muda pra âmbar só
                                # como reforço visual extra; a bandeirinha em
                                # si é a fonte de verdade (session_state).
                                marcada_antes = st.session_state.get(f"marcada_revisao_{q['id_questao']}", False)
                                cor_numero = "var(--tema-amber)" if marcada_antes else "var(--tema-ink-2)"
                                st.markdown(
                                    f'<div style="font-weight:800;font-size:13px;'
                                    f'color:{cor_numero};padding-top:9px;'
                                    f'white-space:nowrap">{numero_texto}{aviso_html}</div>',
                                    unsafe_allow_html=True,
                                )
                                st.checkbox(
                                    "Marcar p/ revisão", key=f"marcada_revisao_{q['id_questao']}",
                                    label_visibility="collapsed",
                                )
                            with col_resp:
                                st.radio(
                                    f"Questão {q['numero_questao']}",
                                    ["—", "A", "B", "C", "D", "E"],
                                    horizontal=True, label_visibility="collapsed",
                                    key=f"resp_{q['id_questao']}",
                                )
                            _mostrar_enunciado_leitura(q)
            enviado_rodape = st.form_submit_button(
                "Corrigir", type="primary", key=f"corrigir_rodape_{sufixo}",
            )
        enviado = enviado_topo or enviado_rodape

    if col_rail is not None:
        with col_rail:
            if len(materias_da_grade) > 1:
                _renderizar_rail_por_materia(questoes, materias_da_grade)
            _renderizar_rail_marcadas_revisao(questoes)

    _processar_correcao_e_resultados(questoes, sufixo, enviado)


def _renderizar_rail_por_materia(questoes: list[dict], materias: list[str]) -> None:
    """Card lateral "Por matéria" (App ENEM.dc.html, Turno 2, seção 2a)
    -- quantas de cada matéria já foram respondidas nesta prova, pra dar
    uma visão rápida de onde falta responder sem precisar rolar a grade
    inteira contando. Só é chamado quando há mais de 1 matéria na lista
    (ver `usar_rail` em _renderizar_grade_questoes) -- "Praticar por
    matéria" é sempre uma matéria só, não teria o que quebrar aqui.
    Mesma limitação de frescor dos números do resumo do topo: reflete
    o session_state como ficou desde a última vez que o form rodou."""
    linhas = []
    for materia in materias:
        qs_materia = [q for q in questoes if q.get("materia") == materia]
        if not qs_materia:
            continue
        resp_materia = sum(
            1 for q in qs_materia if st.session_state.get(f"resp_{q['id_questao']}", "—") != "—"
        )
        pct = resp_materia / len(qs_materia) * 100
        linhas.append(
            f'<div style="margin-bottom:14px">'
            f'  <div style="display:flex;justify-content:space-between;font-weight:700;'
            f'font-size:13px;color:var(--tema-ink);margin-bottom:5px">'
            f'    <span>{materia}</span>'
            f'    <span style="color:var(--tema-ink-3)">{resp_materia}/{len(qs_materia)}</span>'
            f'  </div>'
            f'  <div class="materia-rail-track"><div class="materia-rail-fill" '
            f'style="width:{pct:.0f}%"></div></div>'
            f'</div>'
        )
    st.markdown(
        '<div class="materia-rail-card">'
        '<div style="font-family:\'Baloo 2\',sans-serif;font-weight:700;font-size:15px;'
        'color:var(--tema-ink);margin-bottom:14px">Por matéria</div>'
        f'{"".join(linhas)}'
        '</div>',
        unsafe_allow_html=True,
    )


def _renderizar_rail_marcadas_revisao(questoes: list[dict]) -> None:
    """Card lateral "Marcadas p/ revisão" (App ENEM.dc.html, Turno 2,
    seção 2a) -- lista as questões que o aluno marcou com a bandeirinha
    🚩 (checkbox `marcada_revisao_{id_questao}`, ao lado do número, ver
    _renderizar_grade_questoes). Puramente de sessão: não grava nada no
    banco, é só um lembrete visual de "quero olhar de novo antes de
    corrigir" -- desaparece ao fechar a aba, igual o resto do estado do
    form (mesma limitação de frescor: reflete a última vez que o form
    rodou). Chamado pra QUALQUER grade (Modo Cartão), mesmo com 1 matéria
    só -- diferente de _renderizar_rail_por_materia."""
    marcadas = [
        q for q in questoes if st.session_state.get(f"marcada_revisao_{q['id_questao']}", False)
    ]
    if not marcadas:
        return
    chips = "".join(
        f'<span style="padding:6px 11px;border-radius:999px;background:var(--tema-amber-bg);'
        f'border:1px solid var(--tema-amber-border);font-weight:800;font-size:12px;'
        f'color:var(--tema-amber)">Q{q["numero_questao"]}</span>'
        for q in marcadas
    )
    st.markdown(
        '<div class="materia-rail-card" style="margin-top:14px">'
        '<div style="font-family:\'Baloo 2\',sans-serif;font-weight:700;font-size:15px;'
        'color:var(--tema-ink);margin-bottom:12px">Marcadas p/ revisão</div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap">{chips}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _processar_correcao_e_resultados(questoes: list[dict], sufixo: str, enviado: bool) -> None:
    """Grava as tentativas e mostra nota/desfazer/revisão de erros --
    extraído de _renderizar_grade_questoes() (que ainda é quem chama
    isto pro Modo Cartão, dentro do form) pra também ser chamado por
    _renderizar_modo_foco() (fora do form -- Foco não usa
    st.form_submit_button, usa um st.button comum que fornece o mesmo
    `enviado`). Lógica de correção em si é idêntica à de antes desta
    extração, não mudou nada aqui."""
    chave_resultado = f"resultados_{sufixo}"

    if enviado:
        respostas = {
            q["id_questao"]: st.session_state.get(f"resp_{q['id_questao']}", "—")
            for q in questoes
        }
        if not any(resp != "—" for resp in respostas.values()):
            st.warning("Marque pelo menos uma resposta antes de corrigir.")
            return
        # Questão em branco ("—") registra como None, não fica de fora
        # -- é uma tentativa de verdade (sempre errou, ver
        # registrar_tentativa), não um "pular" que sumia de toda
        # estatística baseada em tentativas_usuario.
        st.session_state[chave_resultado] = [
            db.registrar_tentativa(id_q, None if resp == "—" else resp)
            for id_q, resp in respostas.items()
        ]

    resultados = st.session_state.get(chave_resultado)
    if not resultados:
        return

    # total é o tamanho da prova INTEIRA -- agora toda questão (branca
    # ou não) vira uma tentativa, então len(resultados) já é
    # len(questoes) sempre, mas manter a variável explícita deixa a
    # intenção clara caso os dois algum dia divirjam de novo.
    acertos = sum(1 for r in resultados if r["resultado"] == "acertou")
    total = len(questoes)

    st.success(f"{acertos}/{total} acertos ({acertos / total * 100:.0f}%)")

    with st.popover("↩️ Desfazer essa correção"):
        st.caption(
            "Pra quando você marcou errado por engano agora e quer corrigir de novo -- "
            "só desfaz questão que ainda não tinha nenhuma tentativa antes desta."
        )
        if st.button("Confirmar desfazer", key=f"desfazer_confirmar_{sufixo}"):
            resultado_desfazer = db.desfazer_tentativas([r["id_tentativa"] for r in resultados])
            del st.session_state[chave_resultado]
            n_ok = len(resultado_desfazer["desfeitas"])
            n_puladas = len(resultado_desfazer["puladas_com_historico"])
            if n_puladas:
                st.session_state[f"desfazer_aviso_{sufixo}"] = (
                    f"{n_ok} tentativa(s) desfeita(s). {n_puladas} não foram desfeitas "
                    "porque já tinham tentativa anterior a esta (desfazer exigiria mexer "
                    "no histórico de revisão dela, não fiz isso automaticamente)."
                )
            st.rerun()

    aviso_desfazer = st.session_state.pop(f"desfazer_aviso_{sufixo}", None)
    if aviso_desfazer:
        st.warning(aviso_desfazer)

    numero_por_id = {q["id_questao"]: q["numero_questao"] for q in questoes}
    resultado_por_id = {r["id_questao"]: r for r in resultados}

    with st.expander(f"📋 Ver o que você marcou (prova inteira, {total} questões)"):
        for q in questoes:
            numero = q["numero_questao"]
            r = resultado_por_id[q["id_questao"]]
            if r["resposta_escolhida"] is None:
                st.write(f"⬜ **Q{numero}** — não respondida (conta como erro), gabarito é **{r['alternativa_correta']}**")
                continue
            marca = "✅" if r["resultado"] == "acertou" else "❌"
            st.write(
                f"{marca} **Q{numero}** — você marcou **{r['resposta_escolhida']}**, "
                f"gabarito é **{r['alternativa_correta']}**"
            )

    erros = [r for r in resultados if r["resultado"] == "errou"]
    if erros:
        with st.expander(f"⚠️ {len(erros)} questão(ões) errada(s) — já agendadas pra revisão", expanded=True):
            for r in erros:
                numero = numero_por_id.get(r["id_questao"], r["id_questao"])
                marcou = f"você marcou **{r['resposta_escolhida']}**" if r["resposta_escolhida"] is not None else "**não respondida**"
                st.write(
                    f"**Q{numero}** — {marcou}, "
                    f"gabarito é **{r['alternativa_correta']}** — próxima revisão: {r['proxima_revisao']}"
                )

                opcoes_erro = ["—"] + list(db.TIPOS_ERRO.values())
                escolha_erro = st.selectbox(
                    "Por que errou? (opcional)", opcoes_erro,
                    key=f"tipo_erro_{r['id_tentativa']}", label_visibility="collapsed",
                )
                if escolha_erro != "—":
                    chave_tipo = next(k for k, v in db.TIPOS_ERRO.items() if v == escolha_erro)
                    db.atualizar_tipo_erro(r["id_tentativa"], chave_tipo)

                resolucoes = db.resolucoes_da_questao(r["id_questao"])
                if not resolucoes:
                    st.caption("Sem vídeo de resolução ligado a essa questão ainda.")
                for res in resolucoes:
                    col_res, col_del = st.columns([5, 1])
                    with col_res:
                        if res["tipo"] == "video":
                            st.video(res["conteudo"])
                        else:
                            st.caption(f"Resolução em texto ({res['canal'] or 'sem canal'}): {res['conteudo']}")
                    with col_del:
                        if st.button("🗑️", key=f"apagar_res_{res['id_resolucao']}", help="Remover essa resolução (link errado/quebrado)"):
                            db.apagar_resolucao(res["id_resolucao"])
                            st.rerun()

    n_brancas = sum(1 for r in resultados if r["resposta_escolhida"] is None)
    if n_brancas:
        st.caption(
            f"{n_brancas} questão(ões) deixada(s) em branco -- contam como erro no total acima "
            "e já entraram na fila de revisão, igual questão errada com letra marcada."
        )


def _renderizar_modo_foco(questoes: list[dict], sufixo: str, mostrar_ano: bool) -> bool:
    """Uma questão de cada vez, fora do st.form (precisa de rerun a cada
    Anterior/Próxima/salto -- st.form nunca daria isso). Escreve nas
    MESMAS chaves resp_{id_questao} que o Modo Cartão usa, então trocar
    de modo no meio da sessão não perde nada respondido. Baseado no
    Turno 2 do handoff (App ENEM.dc.html, seção 2b "Modo foco", lido
    via DesignSync 2026-09-09), com 3 recortes deliberados em relação
    ao mockup:

    1. SEM cronômetro -- decorativo no mockup ("1:42:08"), esta app não
       mede tempo de prova nenhuma; inventar esse mecanismo não foi
       pedido em lugar nenhum do resto do sistema.
    2. SEM atalho de teclado (A-E responde, setas navegam, espaço
       marca p/ revisão) -- captura de tecla precisa de JS de verdade,
       e este mesmo projeto já documentou (ver comentário de
       ui_theme.navegacao_lateral()) que uma tentativa real de JS
       funcionou nos testes do desenvolvedor mas falhou pro usuário de
       verdade sem erro nenhum aparecendo. Anterior/Próxima são botões
       clicáveis -- mesmo padrão já comprovado em
       _renderizar_no_trilha_ativo (banco de prática).
    3. O grid "SALTAR PARA" é só visual (pontinhos coloridos, sem
       clique) -- 90 botões individuais alinhados certinho sem
       conseguir ver o resultado renderizado (sem acesso a navegador
       nesta sessão) é arriscado demais pra acertar de primeira. A
       navegação de verdade é o selectbox "Ir para a questão" logo
       abaixo, que não depende de nenhuma posição de pixel.

    Retorna True no rerun em que "Corrigir" foi clicado -- mesmo
    contrato de st.form_submit_button, pra _processar_correcao_e_
    resultados() não precisar saber qual dos dois modos chamou."""
    chave_pos = f"foco_pos_{sufixo}"
    total = len(questoes)
    pos = max(0, min(st.session_state.get(chave_pos, 0), total - 1))
    q = questoes[pos]

    def respondida(qq: dict) -> bool:
        return st.session_state.get(f"resp_{qq['id_questao']}", "—") != "—"

    respondidas = sum(1 for qq in questoes if respondida(qq))

    rotulo_atual = f"{q['ano']} · Q{q['numero_questao']}" if mostrar_ano else f"Questão {q['numero_questao']}"
    col_kicker, col_barra, col_flag = st.columns([2, 5, 1])
    with col_kicker:
        st.caption(f"{rotulo_atual} · {pos + 1}/{total}")
    with col_barra:
        st.progress(respondidas / total if total else 0)
    with col_flag:
        chave_flag = f"revisao_{sufixo}_{q['id_questao']}"
        marcada = st.session_state.get(chave_flag, False)
        if st.button("Marcada p/ revisão" if marcada else "Marcar p/ revisão", key=f"btn_revisar_{sufixo}_{pos}", type="secondary" if not marcada else "primary"):
            st.session_state[chave_flag] = not marcada
            st.rerun()

    alternativas = _mostrar_enunciado_exame(q)
    if alternativas:
        # alt=alternativas (default arg, não closure) -- mesmo motivo
        # documentado no radio equivalente do Modo Cartão acima.
        st.radio(
            "Resposta", ["—", "A", "B", "C", "D", "E"],
            format_func=lambda letra, alt=alternativas: f"{letra}) {alt[letra]}" if letra in alt else "Não respondida",
            key=f"resp_{q['id_questao']}", label_visibility="collapsed",
        )
    else:
        st.radio(
            "Resposta", ["—", "A", "B", "C", "D", "E"],
            horizontal=True, key=f"resp_{q['id_questao']}", label_visibility="collapsed",
        )

    # Grid de saltos só-visual (ver recorte 3 na docstring) -- lima =
    # respondida, violeta = questão aberta agora, cinza = em branco.
    # Mesma paleta do bloco 2b do handoff.
    pontos = "".join(
        f'<div style="width:14px;height:14px;border-radius:5px;flex:0 0 auto;'
        f'background:{"#7C5CFF" if i == pos else ("#6EE12B" if respondida(qq) else "#1F2531")}'
        + ("" if i == pos or respondida(qq) else ";border:1px solid #2C3342")
        + '"></div>'
        for i, qq in enumerate(questoes)
    )
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:5px;margin:10px 0">{pontos}</div>', unsafe_allow_html=True)

    opcoes_ir = [
        f"{i + 1}. Q{qq['numero_questao']}" + (" ✓" if respondida(qq) else "")
        for i, qq in enumerate(questoes)
    ]
    escolha_ir = st.selectbox("Ir para a questão", opcoes_ir, index=pos, key=f"foco_ir_para_{sufixo}")
    indice_escolhido = opcoes_ir.index(escolha_ir)
    if indice_escolhido != pos:
        st.session_state[chave_pos] = indice_escolhido
        st.rerun()

    col_ant, col_meio, col_prox = st.columns([1, 2, 1])
    with col_ant:
        if st.button("⬅️ Anterior", disabled=pos == 0, key=f"foco_anterior_{sufixo}", width="stretch"):
            st.session_state[chave_pos] = pos - 1
            st.rerun()
    with col_meio:
        enviado = st.button("Corrigir", type="primary", key=f"foco_corrigir_{sufixo}", width="stretch")
    with col_prox:
        if st.button("Próxima ➡️", disabled=pos == total - 1, key=f"foco_proxima_{sufixo}", width="stretch"):
            st.session_state[chave_pos] = pos + 1
            st.rerun()

    return enviado


PASTA_ENUNCIADOS = Path(__file__).parent / "enunciados"


def _mostrar_enunciado_leitura(q: dict) -> None:
    """Exibição só-leitura dentro da grade (dentro do st.form — por
    isso não tem botão nenhum aqui, só texto/imagem)."""
    if q.get("origem") == "banco_pratica" and q.get("fonte"):
        st.caption(f"🧠 Banco de prática · fonte: {q['fonte']}")
    texto = q.get("enunciado_texto")
    imagem = q.get("enunciado_imagem_path")
    if not texto and not imagem:
        return
    with st.expander("📄 Enunciado"):
        if texto:
            st.write(texto)
        if imagem and Path(imagem).exists():
            st.image(imagem)


_PADRAO_ALTERNATIVA_LINHA = re.compile(r"^([A-E])\s+(.+)$")


def _separar_alternativas(texto: str) -> tuple[str, dict[str, str]]:
    """Tenta separar as 5 alternativas do resto do enunciado, pra
    poder mostrar o texto de cada uma junto da letra no radio (em vez
    de só 'A B C D E' soltos, obrigando a rolar pra cima e contar qual
    letra é qual). Só confia que as ÚLTIMAS 5 linhas não-vazias são as
    alternativas, e só se vierem na ordem estrita A,B,C,D,E -- um
    regex solto por linha (ex: r'^[A-E]\\s') pegaria falso positivo
    toda vez que uma frase do ENUNCIADO começa com o artigo 'A' (comum
    em português: "A enorme quantidade de resíduos...") ou queimaria
    uma questão cujas alternativas são diagrama, não texto, onde a
    extração já sai fora de ordem (ver extrair_figuras_pdf.py, questão
    93 do 2020 azul: "A ... D ... B ... E ... C ..." embaralhado). Se
    as 5 últimas linhas não baterem exatamente com A-B-C-D-E nessa
    ordem, devolve o texto inteiro sem separar nada -- degrada pro
    radio de letra pura em vez de arriscar cortar o texto errado."""
    linhas = [l for l in texto.split("\n") if l.strip()]
    if len(linhas) < 5:
        return texto, {}
    alternativas = {}
    for letra_esperada, linha in zip("ABCDE", linhas[-5:]):
        m = _PADRAO_ALTERNATIVA_LINHA.match(linha.strip())
        if not m or m.group(1) != letra_esperada:
            return texto, {}
        alternativas[letra_esperada] = m.group(2).strip()
    corpo = "\n".join(linhas[:-5]).strip()
    return corpo, alternativas


_PADRAO_ALTERNATIVA_PRATICA = re.compile(r"^([A-E])\)\s*(.+)$")


def _separar_alternativas_banco_pratica(texto: str) -> tuple[str, dict[str, str]]:
    """Mesma ideia de _separar_alternativas(), mas pro formato "A) texto"
    que importar_questoes_praticas_texto() (db.py) SEMPRE usa ao gravar
    uma questão do banco de prática -- diferente do texto extraído de
    PDF (origem incerta, por isso aquela função precisa da heurística
    de ordem estrita como única defesa), aqui o formato é gerado por
    este mesmo sistema, então um parse direto do padrão "A)" é
    suficiente e não se confunde com uma frase começando com o artigo
    "A" (que nunca vem seguida de ")"). Mantém a mesma checagem de
    ordem estrita A-E nas últimas 5 linhas como rede de segurança
    barata, caso alguém edite o enunciado na mão fora do formato."""
    linhas = [l for l in texto.split("\n") if l.strip()]
    if len(linhas) < 5:
        return texto, {}
    alternativas = {}
    for letra_esperada, linha in zip("ABCDE", linhas[-5:]):
        m = _PADRAO_ALTERNATIVA_PRATICA.match(linha.strip())
        if not m or m.group(1) != letra_esperada:
            return texto, {}
        alternativas[letra_esperada] = m.group(2).strip()
    corpo = "\n".join(linhas[:-5]).strip()
    return corpo, alternativas


def _mostrar_enunciado_exame(q: dict) -> dict[str, str]:
    """Enunciado SEMPRE visível (nunca escondido num expander) --
    versão pra estilo_exame=True, onde o objetivo é ler a questão
    igual um caderno de prova de verdade, não esconder o texto atrás
    de um clique. st.container(border=True) + st.write() em vez de
    markdown com HTML de propósito -- o texto vem de extração de PDF e
    questão de matemática frequentemente tem '<'/'>' de verdade
    (ex: "x < 5"), que markdown com unsafe_allow_html interpretaria
    como tag HTML e quebraria a exibição.

    Devolve {letra: texto_alternativa} (vazio se não deu pra separar
    com segurança, ver _separar_alternativas) pro chamador montar o
    radio com o texto de cada opção, em vez de só a letra."""
    texto = q.get("enunciado_texto")
    imagem = q.get("enunciado_imagem_path")
    if not texto and not imagem:
        st.caption("Sem enunciado carregado pra essa questão ainda.")
        return {}
    corpo, alternativas = _separar_alternativas(texto) if texto else ("", {})
    with st.container(border=True):
        if corpo:
            st.write(corpo)
        if imagem and Path(imagem).exists():
            st.image(imagem)
    return alternativas


def _renderizar_editor_enunciado(questoes: list[dict], sufixo: str) -> None:
    """Adicionar enunciado (texto e/ou imagem) fica FORA do st.form da
    grade de propósito -- st.form só permite um botão de envio (o
    'Corrigir'), então salvar enunciado por questão precisa do próprio
    botão, independente. Só aparece a questão de cada vez, escolhida
    num seletor, pra não virar 44 uploaders na tela ao mesmo tempo."""
    sem_enunciado = [q for q in questoes if not q.get("enunciado_texto") and not q.get("enunciado_imagem_path")]
    if not sem_enunciado:
        return

    with st.expander(f"📄 Adicionar enunciado ({len(sem_enunciado)} questão(ões) ainda sem)"):
        opcoes = {f"Q{q['numero_questao']} — {q['id_questao']}": q["id_questao"] for q in sem_enunciado}
        escolha = st.selectbox("Questão", list(opcoes.keys()), key=f"enun_sel_{sufixo}")
        id_q = opcoes[escolha]

        texto = st.text_area(
            "Texto do enunciado (pode deixar em branco se for só imagem)",
            key=f"enun_texto_{sufixo}_{id_q}", height=120,
        )
        imagem = st.file_uploader(
            "Imagem do enunciado (opcional)", type=["png", "jpg", "jpeg"],
            key=f"enun_imagem_{sufixo}_{id_q}",
        )

        if st.button("Salvar enunciado", key=f"enun_salvar_{sufixo}_{id_q}"):
            caminho_imagem = None
            if imagem is not None:
                PASTA_ENUNCIADOS.mkdir(exist_ok=True)
                extensao = Path(imagem.name).suffix or ".png"
                caminho_imagem = str(PASTA_ENUNCIADOS / f"{id_q}{extensao}")
                with open(caminho_imagem, "wb") as f:
                    f.write(imagem.getbuffer())

            if not texto.strip() and not caminho_imagem:
                st.warning("Cole um texto ou uma imagem antes de salvar.")
            else:
                db.atualizar_enunciado(id_q, texto=texto.strip() or None, imagem_path=caminho_imagem)
                st.success(f"Enunciado salvo pra {id_q}.")
                st.rerun()


def render_analise() -> None:
    nivel = db.calcular_nivel_jogador()
    ofensiva = db.calcular_ofensiva()

    col1, col2, col3 = st.columns(3)
    col1.metric("Rank", nivel["rank"], f"{nivel['xp']} XP")
    col2.metric("🔥 Ofensiva atual", f"{ofensiva['atual']} dia(s)")
    col3.metric("Melhor ofensiva", f"{ofensiva['melhor']} dia(s)")

    if nivel["proximo_rank"]:
        st.caption(f"Faltam {nivel['xp_para_proximo']} XP pro {nivel['proximo_rank']}.")

    meta = db.progresso_meta_diaria()
    fracao = min(1.0, meta["feitas_hoje"] / meta["meta"]) if meta["meta"] else 0.0
    st.progress(fracao)
    if meta["atingida"]:
        st.caption(f"✅ Meta de hoje batida: {meta['feitas_hoje']}/{meta['meta']} questões.")
    else:
        st.caption(f"Meta de hoje: {meta['feitas_hoje']}/{meta['meta']} questões — faltam {meta['restantes']}.")

    st.caption("Últimos 30 dias:")
    dias = ofensiva["calendario_30_dias"]
    quadrados = "".join(
        f'<span class="dia-ativo" title="{d["data"]}"></span>' if d["ativo"]
        else f'<span class="dia-inativo" title="{d["data"]}"></span>'
        for d in dias
    )
    st.markdown(f'<div class="app-streak-calendar">{quadrados}</div>', unsafe_allow_html=True)

    st.divider()

    area_analise = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True, key="area_analise",
    )

    st.subheader("Prioridade de estudo")
    prioridade = db.prioridade_de_estudo(area_analise)
    confianca_por_materia = {c["materia"]: c for c in db.confianca_recente_por_materia(area_analise)}
    _RÓTULO_CONFIANCA = {"alta": "🟢 alta", "media": "🟡 média", "baixa": "🔴 baixa"}

    if not prioridade["ranking"] and not prioridade["sem_dados"]:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        if prioridade["ranking"]:
            linhas_ranking = []
            for r in prioridade["ranking"]:
                aviso = " ⚠️" if r["amostra_pequena"] else ""
                conf = confianca_por_materia.get(r["materia"])
                linhas_ranking.append({
                    "Matéria": r["materia"],
                    "Recorrência": f"{r['percentual_recorrencia']}%",
                    "Sua taxa de acerto": f"{r['taxa_acerto_pct']}%" + aviso,
                    "Confiança recente": _RÓTULO_CONFIANCA.get(conf["confianca"], "—") if conf else "—",
                    "Tentativas": r["total_tentativas"],
                    "Prioridade": r["score_prioridade"],
                })
            ui_theme.tabela_html(linhas_ranking)
            st.caption(
                "Prioridade = cai bastante E você erra bastante. Quanto maior, mais vale estudar agora. "
                f"⚠️ = menos de {db.MIN_AMOSTRA_CONFIAVEL} tentativas — ordem pode mudar com mais dado. "
                "Confiança recente = só as últimas tentativas (não a média desde sempre) — separa "
                "\"sempre errei, mas melhorando\" de \"sempre acertei, mas piorando agora\", que a taxa "
                "de acerto acumulada sozinha não distingue."
            )

            topo = prioridade["ranking"][0]
            with st.expander(f"🔍 Por que \"{topo['materia']}\" está no topo? (a conta, não só o número)"):
                exp = topo["explicacao"]
                st.write(
                    f"**Prioridade {topo['score_prioridade']}/100** = "
                    f"{exp['contribuicao_recorrencia']} pontos de recorrência "
                    f"({topo['percentual_recorrencia']}% das provas × peso {exp['peso_recorrencia']}) "
                    f"+ {exp['contribuicao_taxa_erro']} pontos de taxa de erro "
                    f"({100 - topo['taxa_acerto_pct']:.1f}% de erro × peso {1 - exp['peso_recorrencia']:.1f})."
                )
                conf_topo = confianca_por_materia.get(topo["materia"])
                if conf_topo:
                    st.write(
                        f"Confiança recente: **{conf_topo['confianca']}** "
                        f"(últimas {conf_topo['tentativas_consideradas']}: {' '.join(conf_topo['sequencia_recente'])})"
                    )
        if prioridade["sem_dados"]:
            materias = ", ".join(
                f"{s['materia']} ({s['percentual_recorrencia']}%)" for s in prioridade["sem_dados"]
            )
            st.warning(f"Recorrentes mas você nunca respondeu ainda, sem prioridade calculável: {materias}")

    st.divider()

    st.subheader("📈 Evolução semanal")
    evolucao = db.evolucao_semanal_por_materia(area_analise)
    if len(evolucao["semanas"]) < 2:
        st.caption("Ainda não há semanas suficientes com atividade nessa área pra montar uma tendência.")
    else:
        st.caption(
            f"Primeira metade x segunda metade das últimas {len(evolucao['semanas'])} semana(s) com "
            "atividade real (semana sem tentativa nenhuma não conta como uma das N). Só aparece destaque "
            f"pra matéria com pelo menos {db.MIN_AMOSTRA_CONFIAVEL} tentativas em CADA metade — sem isso, "
            "1 acerto isolado viraria \"100% de evolução\" sem dado nenhum por trás."
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            if evolucao["maior_evolucao"]:
                e = evolucao["maior_evolucao"]
                st.metric("📈 Maior evolução", e["materia"], f"+{e['delta_pct']}pp")
            else:
                st.caption("Maior evolução: sem candidato com amostra suficiente ainda.")
        with col2:
            if evolucao["maior_risco"]:
                e = evolucao["maior_risco"]
                st.metric("📉 Maior risco", e["materia"], f"{e['delta_pct']}pp")
            else:
                st.caption("Maior risco: sem candidato com amostra suficiente ainda.")
        with col3:
            if evolucao["estagnado"]:
                e = evolucao["estagnado"]
                st.metric("⏸️ Estagnado", e["materia"], f"{e['delta_pct']}pp", delta_color="off")
            else:
                st.caption("Estagnado: sem candidato com amostra suficiente ainda.")

    st.divider()

    st.subheader("Por que você erra")
    por_erro = db.analise_por_tipo_erro(area_analise)
    if not por_erro:
        st.caption("Ainda sem dado suficiente — classifique o motivo do erro no cartão-resposta pra essa análise aparecer.")
    else:
        linhas_erro = [
            {"Matéria": r["materia"], "Tipo de erro": db.TIPOS_ERRO[r["tipo_erro"]], "Quantidade": r["quantidade"]}
            for r in por_erro
        ]
        ui_theme.tabela_html(linhas_erro)

    st.divider()

    st.subheader("Recorrência por matéria")
    recorrencia = db.recorrencia_por_materia(area_analise)
    if not recorrencia:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        total_provas = recorrencia[0]["total_provas_na_base"]
        st.caption(
            f"Base atual: {total_provas} prova(s) cadastrada(s), cobrindo só as posições de caderno "
            "que você já carregou — não a prova inteira. Percentual reflete essa amostra, não o ENEM completo."
        )
        ui_theme.tabela_html([
            {"Matéria": r["materia"], "Provas com a matéria": r["provas_com_materia"], "%": r["percentual"]}
            for r in recorrencia
        ])

    st.subheader("Seu desempenho por matéria")
    desempenho = db.taxa_acerto_por_materia(area_analise)
    if not desempenho:
        st.info("Responda alguma prova no cartão-resposta pra essa tabela aparecer.")
        return

    linhas = []
    for d in desempenho:
        amostra_pequena = d["total_tentativas"] < db.MIN_AMOSTRA_CONFIAVEL
        linhas.append({
            "Matéria": d["materia"],
            "Tentativas": d["total_tentativas"],
            "Acertos": d["acertos"],
            "Taxa de acerto": f"{d['taxa_acerto']*100:.0f}%" + (" ⚠️" if amostra_pequena else ""),
        })
    ui_theme.tabela_html(linhas)


_FASE_PRINCIPIO = {
    "fase1_fundacao": "Ainda não sabemos o ponto de partida real em Natureza. Meta numérica sem linha de base é chute — a ação desta fase é estabelecer essa linha de base (corrigir 2019 + 1 prova nova, categorizando cada erro), não bater um número.",
    "fase2_consolidacao": "500 em Natureza não é número arbitrário — é o corte mínimo eliminatório que você levantou pros seus alvos (IME e Politécnica-USP). Ficar abaixo elimina essas opções, independente da média final.",
    "fase3_blindagem": "Tempo aprendendo algo do zero agora compete com consolidar o que já foi estudado. Nas últimas semanas, retenção do que já é familiar rende mais que abrir tópico novo — por isso zero conteúdo pesado novo, só revisão dirigida e simulado.",
}

_FASE_METAS = {
    "fase1_fundacao": {
        "Matemática": "24-26/45 (53-58%)", "Ciências da Natureza": "estabelecer linha de base",
        "Redação": "manter 700 (confirmado)", "Humanas/Linguagens": "1 simulado completo cada, linha de base",
    },
    "fase2_consolidacao": {
        "Matemática": "28-32/45 (62-71%)", "Ciências da Natureza": "acima do corte de 500",
        "Redação": "manter 700+, erro ortográfico perto de zero", "Humanas/Linguagens": "65%+",
    },
    "fase3_blindagem": {
        "Matemática": "32-36/45 (71-80%)", "Ciências da Natureza": "500-550+",
        "Redação": "750+", "Humanas/Linguagens": "70%+",
    },
}

_FASE_ROTINA = {
    "fase1_fundacao": [
        "3 dias — Natureza: corrige prova antiga (2019, depois 2020) + pra cada questão \"não sabia o conteúdo\", disseca ela por completo em voz alta até dominar o tema (seu método já validado) + 10 questões do mesmo tema em outras provas.",
        "1 dia — Matemática: ciclo já validado (prova → corrige → foca fácil/médio), priorizando Geometria, Funções e Financeira.",
        "1 dia — Humanas + Linguagens: 1 simulado parcial (bloco de 45) + correção rápida.",
        "1 dia — Simulado completo (sábado), alternando Matemática/Natureza como foco principal.",
        "Redação: 1x/semana cronometrada + 10-15min/dia de repertório + revisão ortográfica logo depois de escrever.",
    ],
    "fase2_consolidacao": [
        "Repete o ciclo 2019-2025 em Natureza e Matemática, agora com 2 simulados completos por semana (sábado + 1 dia de meio de semana).",
        "Todas as áreas entram no ciclo de correção com categorização de erro.",
        "Redação mantém 1x/semana.",
    ],
    "fase3_blindagem": [
        "3 simulados completos por semana, crescente até a prova.",
        "Revisão dirigida só nos temas que ainda aparecerem como erro recorrente.",
        "Redação 1x/semana, mantendo estrutura — sem mudar repertório essa perto da prova.",
    ],
}

_METRICAS_ALERTA = [
    "Se Natureza não subir pelo menos 15-20 pontos (TRI estimado) até o fim da Fase 1 → o volume de conteúdo novo (vídeo/dissecação) precisa aumentar, não só volume de questão.",
    "Se um simulado completo cair mais de 15% abaixo da sua média móvel → cheque cansaço/ansiedade antes de assumir que é lacuna de conteúdo.",
    "Se erro ortográfico na redação não cair depois de 3 semanas de revisão pós-escrita → considere buscar correção externa focada nisso.",
]


def render_calendario() -> None:
    plano = db.plano_periodizacao()

    if plano["fase"] == "pos_prova":
        st.success("A prova já passou. Se ainda quiser treinar, o resto do app continua aqui.")
        return
    if plano["fase"] == "prova":
        st.success("🍀 Hoje é o dia. O trabalho já foi feito — agora é confiar nele.")
        return

    data_prova_fmt = f"{plano['data_prova'][8:10]}/{plano['data_prova'][5:7]}/{plano['data_prova'][:4]}"
    fase1_fmt = f"{plano['fase1_fim'][8:10]}/{plano['fase1_fim'][5:7]}"
    fase2_fmt = f"{plano['fase2_fim'][8:10]}/{plano['fase2_fim'][5:7]}"

    st.subheader(f"🗓️ {plano['dias_restantes']} dias até {data_prova_fmt}")
    st.caption(f"**{plano['fase_label']}** · Fase 1 até {fase1_fmt} · Fase 2 até {fase2_fmt} · Fase 3 até a prova")
    st.info(_FASE_PRINCIPIO[plano["fase"]])

    st.divider()
    st.subheader("📋 Plano de hoje")
    st.caption(
        "Divide o tempo que você tem agora entre revisão atrasada, prática geral por área e um bloco "
        "isolado na sua maior fraqueza -- recalculado a cada tentativa nova, nunca uma grade fixa."
    )
    minutos_plano = st.slider(
        "Quanto tempo você tem hoje?", min_value=30, max_value=240, step=10,
        value=st.session_state.get("plano_minutos", db.MINUTOS_TOTAIS_PADRAO),
        key="plano_minutos",
    )
    plano_estudo = db.gerar_plano_de_estudo(minutos_plano)
    if not plano_estudo["blocos"]:
        st.info("Sem dado suficiente ainda pra montar um plano -- responda algumas questões primeiro.")
    else:
        if plano_estudo["minutos_alocados"] < plano_estudo["minutos_totais"]:
            st.caption(
                f"Alocados {plano_estudo['minutos_alocados']} de {plano_estudo['minutos_totais']} min pedidos "
                "-- ainda sem dado suficiente pra preencher o resto."
            )
        for bloco in plano_estudo["blocos"]:
            titulo = bloco["titulo"]
            if "area" in bloco:
                titulo += f" — {RÓTULO_AREA[bloco['area']]}"
            with st.container(border=True):
                st.write(f"**{bloco['minutos']} min — {titulo}**")
                extra = []
                if bloco.get("materias_sugeridas"):
                    extra.append("foco: " + ", ".join(f"`{m}`" for m in bloco["materias_sugeridas"]))
                if bloco.get("questoes_sugeridas"):
                    extra.append(f"~{bloco['questoes_sugeridas']} questões")
                if extra:
                    st.caption(" · ".join(extra))
                st.caption(bloco["motivo"])

    st.divider()
    st.subheader("📊 Sua média móvel (últimos simulados) vs. meta desta fase")
    st.caption(
        "Nota varia por prova, cansaço, tema sorteado — o que importa é a TENDÊNCIA da média móvel, não o "
        "resultado de um simulado isolado. \"Simulado\" aqui = qualquer dia com 15+ questões respondidas na área; "
        "se você fizer mais de um no mesmo dia, contam como um só."
    )
    metas_fase = _FASE_METAS[plano["fase"]]
    for area, chave_area in (("Matemática", "matematica"), ("Ciências da Natureza", "ciencias_natureza")):
        mm = db.media_movel_simulados(chave_area)
        col1, col2 = st.columns([1, 2])
        with col1:
            if mm["tem_dado"]:
                st.metric(area, f"{mm['media_pct']}%", help=f"média dos últimos {mm['n_simulados']} simulado(s)")
            else:
                st.metric(area, "sem dado")
        with col2:
            st.caption(f"Meta desta fase: **{metas_fase[area]}**")
            if area == "Ciências da Natureza":
                st.caption("(meta em escala TRI/nota — % de acerto é uma medida diferente, sirva de tendência, não comparação direta.)")

    ultima_redacao = next(iter(db.listar_redacoes()), None)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Redação", f"{ultima_redacao['nota']}" if ultima_redacao and ultima_redacao["nota"] is not None else "sem nota", help="última redação com nota registrada")
    with col2:
        st.caption(f"Meta desta fase: **{metas_fase['Redação']}**")
        st.caption("Humanas/Linguagens: meta desta fase é **" + metas_fase["Humanas/Linguagens"] + "** — este app não tem banco de questões dessas áreas, registre seu resultado por fora.")

    st.divider()
    st.subheader("🎯 Ataque às fraquezas — o que atacar agora")
    st.caption(
        "Não é uma lista fixa por semana — é sempre a matéria que mais cai E você mais erra, recalculada "
        "a cada tentativa nova. Conforme melhora numa matéria, ela sai do topo sozinha."
    )
    for area in ("matematica", "ciencias_natureza"):
        prioridade = db.prioridade_de_estudo(area)
        top = prioridade["ranking"][:3]
        st.write(f"**{RÓTULO_AREA[area]}**")
        if not top:
            st.caption("Ainda sem dado suficiente pra priorizar — responda mais questões dessa área primeiro.")
            continue
        for r in top:
            aviso = " ⚠️ *(amostra pequena, pode mudar)*" if r["amostra_pequena"] else ""
            st.write(f"- `{r['materia']}` — cai em {r['percentual_recorrencia']}% das provas, você acerta {r['taxa_acerto_pct']}%{aviso}")
    st.caption("→ Treine cada uma isolada em \"Praticar por matéria\", no Cartão-resposta.")

    st.divider()
    st.subheader("📋 Checklist de simulados e correção")
    st.caption(
        "\"Feito\" = 80%+ da prova respondida. \"Corrigido\" = toda questão errada já tem motivo classificado "
        "(Cartão-resposta → questão errada → \"Por que errou?\") — sabemos que sua correção de Natureza é mais "
        "profunda e demora mais que a de Matemática, então é normal \"Feito\" chegar bem antes de \"Corrigido\"."
    )
    progresso = sorted(db.progresso_simulados(), key=lambda x: x["cobertura_pct"])
    if not progresso:
        st.info("Nenhum ano com Matemática + Ciências completos ainda.")
    for p in progresso:
        feito = "✅" if p["feito"] else "⬜"
        if p["erradas_total"] == 0:
            corrigido = "—"
        elif p["correcao_completa"]:
            corrigido = "✅"
        else:
            corrigido = f"⬜ {p['erradas_corrigidas']}/{p['erradas_total']}"
        rotulo_caderno = (
            p["caderno_matematica"] if p["caderno_matematica"] == p["caderno_ciencias"]
            else f"Mat. {p['caderno_matematica']} / Ciê. {p['caderno_ciencias']}"
        )
        st.write(f"{feito} **{p['ano']} — {rotulo_caderno}** — {p['respondidas']}/{p['total_questoes']} respondidas ({p['cobertura_pct']:.0f}%) · correção: {corrigido}")

    st.divider()
    st.subheader("📆 Rotina desta fase")
    for linha in _FASE_ROTINA[plano["fase"]]:
        st.write(f"- {linha}")

    st.divider()
    st.subheader("⚠️ Quando revisar o plano")
    for linha in _METRICAS_ALERTA:
        st.write(f"- {linha}")

    st.divider()
    st.caption(
        "Matemática e Ciências da Natureza são medidas com dado real deste app. Redação é registrada (não "
        "corrigida por aqui). Humanas e Linguagens precisam do próprio controle — este app não tem banco de "
        "questões dessas áreas. Isto não é previsão de aprovação — nota de corte real só existe depois da prova."
    )


PASTA_VISION_BOARD = Path(__file__).parent / "vision_board"


def render_objetivos() -> None:
    prova = db.dias_ate_prova()

    if prova["ja_passou"]:
        st.success("A prova já passou.")
    else:
        # Cores do token atual (--tema-lime/--tema-amber/--tema-coral,
        # ver ui_theme.py) -- hex direto (não var()) porque o truque de
        # glow abaixo concatena "66" de alpha na própria string da cor,
        # o que var() não permite. Antes disso: leftover do tema
        # "fluorescente" anterior ao redesign Grafite & Lima (#39FF14/
        # #E0A542/#FF7A6B não correspondem a nenhum token atual).
        cor_urgencia = "#6EE12B" if prova["dias_restantes"] > 14 else "#FFC42E" if prova["dias_restantes"] > 4 else "#FF6B4A"
        st.markdown(
            f'<div style="text-align:center; padding:0.5rem 0 1.5rem">'
            f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:4rem; font-weight:700; '
            f'color:{cor_urgencia}; text-shadow:0 0 28px {cor_urgencia}66; line-height:1">{prova["dias_restantes"]}</div>'
            f'<div style="color:var(--tema-ink-2); font-weight:700; letter-spacing:0.08em; margin-top:0.3rem">DIAS ATÉ O ENEM</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Por que eu quero passar")
    motivo_atual = db.obter_configuracao("motivo_pessoal", "")
    motivo = st.text_area(
        "Escreva pra você mesmo — o que muda quando você passar. Releia nos dias ruins.",
        value=motivo_atual, height=140, key="motivo_pessoal_input",
    )
    if st.button("Salvar", key="salvar_motivo") and motivo != motivo_atual:
        db.definir_configuracao("motivo_pessoal", motivo)
        st.success("Salvo.")

    st.divider()

    st.subheader("Metas de nota")
    st.caption(
        "Meta é aspiracional, não previsão — nota TRI não é a mesma coisa que % de acerto no treino. "
        "As duas métricas abaixo medem coisas diferentes de propósito."
    )
    col1, col2 = st.columns(2)
    with col1:
        meta_mat = st.number_input(
            "Meta Matemática (0-1000)", min_value=0, max_value=1000,
            value=int(float(db.obter_configuracao("meta_nota_matematica", "700"))), key="meta_nota_mat",
        )
    with col2:
        meta_nat = st.number_input(
            "Meta Ciências da Natureza (0-1000)", min_value=0, max_value=1000,
            value=int(float(db.obter_configuracao("meta_nota_natureza", "600"))), key="meta_nota_nat",
        )
    if st.button("Salvar metas", key="salvar_metas_nota"):
        db.definir_configuracao("meta_nota_matematica", str(int(meta_mat)))
        db.definir_configuracao("meta_nota_natureza", str(int(meta_nat)))
        st.success("Metas salvas.")

    def _media_geral(grande_area: str):
        desempenho = db.taxa_acerto_por_materia(grande_area)
        total = sum(d["total_tentativas"] for d in desempenho)
        acertos = sum(d["acertos"] for d in desempenho)
        return round(acertos / total * 100, 1) if total else None

    media_mat, media_nat = _media_geral("matematica"), _media_geral("ciencias_natureza")
    col1, col2 = st.columns(2)
    col1.metric("Sua taxa de acerto no treino — Matemática", f"{media_mat}%" if media_mat is not None else "sem dado ainda")
    col2.metric("Sua taxa de acerto no treino — Ciências", f"{media_nat}%" if media_nat is not None else "sem dado ainda")

    st.divider()

    st.subheader("🖼️ Quadro de motivação")
    st.caption("Fotos suas, de amigos, de quem te inspira — o que fizer você lembrar por que está fazendo isso.")
    PASTA_VISION_BOARD.mkdir(exist_ok=True)

    if "vision_upload_geracao" not in st.session_state:
        st.session_state["vision_upload_geracao"] = 0

    novas_imagens = st.file_uploader(
        "Adicionar imagem(ns)", type=["png", "jpg", "jpeg"], accept_multiple_files=True,
        key=f"vision_upload_{st.session_state['vision_upload_geracao']}",
    )
    # O upload salva só quando este botão é clicado -- nunca sozinho no
    # rerun. st.file_uploader mantém o valor entre reruns até a key
    # mudar; sem esse botão como porta de entrada, o st.rerun() logo
    # abaixo reprocessaria o MESMO arquivo pra sempre (empilhando cópia
    # atrás de cópia a cada rerun -- foi exatamente isso que aconteceu
    # testando: 1 upload virou ~500 arquivos em segundos). Trocar a key
    # depois de salvar reseta o widget visualmente também.
    if novas_imagens and st.button("Adicionar ao quadro", key="vision_upload_confirmar"):
        for img in novas_imagens:
            extensao = Path(img.name).suffix or ".jpg"
            destino = PASTA_VISION_BOARD / f"{int(datetime.now().timestamp() * 1000)}{extensao}"
            with open(destino, "wb") as f:
                f.write(img.getbuffer())
        st.session_state["vision_upload_geracao"] += 1
        st.success(f"{len(novas_imagens)} imagem(ns) adicionada(s).")
        st.rerun()

    imagens = sorted(
        (p for p in PASTA_VISION_BOARD.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")),
        reverse=True,
    )
    if not imagens:
        st.info("Nenhuma imagem ainda.")
    else:
        cols = st.columns(3)
        for i, caminho in enumerate(imagens):
            with cols[i % 3]:
                st.image(str(caminho), use_container_width=True)
                if st.button("Remover", key=f"remover_vision_{caminho.name}"):
                    caminho.unlink()
                    st.rerun()


PASTA_REDACOES = Path(__file__).parent / "redacoes_arquivos"


def render_redacao() -> None:
    """Só guarda redação -- não corrige (o sistema não tem como avaliar
    redação de verdade). Nota e erro ortográfico vêm de correção
    própria, externa ou oficial, digitados aqui depois."""
    st.subheader("✍️ Nova redação")

    temas_usados = db.temas_redacoes_usados()
    if temas_usados:
        modo_tema = st.radio("Tema", ["Novo tema", "Reusar tema já usado"], horizontal=True, key="redacao_modo_tema")
    else:
        modo_tema = "Novo tema"
    if modo_tema == "Reusar tema já usado":
        tema = st.selectbox("Escolha o tema", temas_usados, key="redacao_tema_existente")
    else:
        tema = st.text_input("Tema (cole o enunciado ou um resumo curto)", key="redacao_tema_novo")

    col1, col2 = st.columns(2)
    with col1:
        data_escrita = st.date_input("Data", value=date.today(), key="redacao_data")
    with col2:
        fonte = st.selectbox("Correção", ["ainda sem correção", "própria", "externa", "oficial"], key="redacao_fonte")

    texto = st.text_area("Texto (se digitou)", height=200, key="redacao_texto")

    if "redacao_upload_geracao" not in st.session_state:
        st.session_state["redacao_upload_geracao"] = 0
    arquivo = st.file_uploader(
        "Foto ou PDF da redação escrita à mão (opcional)", type=["png", "jpg", "jpeg", "pdf"],
        key=f"redacao_arquivo_{st.session_state['redacao_upload_geracao']}",
    )

    col1, col2 = st.columns(2)
    with col1:
        nota = st.number_input("Nota (0-1000, se já corrigida)", min_value=0, max_value=1000, value=0, key="redacao_nota")
    with col2:
        erros_ortograficos = st.number_input("Erros ortográficos", min_value=0, max_value=100, value=0, key="redacao_erros")

    observacoes = st.text_area("Observações (opcional)", height=80, key="redacao_obs")

    if st.button("Salvar redação", type="primary", key="redacao_salvar"):
        if not tema or not tema.strip():
            st.warning("Preencha o tema antes de salvar.")
        elif not texto.strip() and arquivo is None:
            st.warning("Cole o texto ou anexe uma foto/PDF antes de salvar.")
        else:
            caminho_arquivo = None
            if arquivo is not None:
                PASTA_REDACOES.mkdir(exist_ok=True)
                extensao = Path(arquivo.name).suffix or ".pdf"
                caminho_arquivo = str(PASTA_REDACOES / f"{int(datetime.now().timestamp() * 1000)}{extensao}")
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo.getbuffer())

            db.salvar_redacao(
                tema=tema, data_escrita=data_escrita.isoformat(), texto=texto.strip() or None,
                arquivo_path=caminho_arquivo, nota=int(nota) or None,
                erros_ortograficos=int(erros_ortograficos) if erros_ortograficos else None,
                fonte_correcao=None if fonte == "ainda sem correção" else fonte,
                observacoes=observacoes.strip() or None,
            )
            st.session_state["redacao_upload_geracao"] += 1
            st.success("Redação salva.")
            st.rerun()

    st.divider()
    st.subheader("📚 Suas redações")
    redacoes = db.listar_redacoes()
    if not redacoes:
        st.info("Nenhuma redação guardada ainda.")
        return

    notas_validas = [r["nota"] for r in redacoes if r["nota"] is not None]
    if notas_validas:
        st.caption(f"{len(redacoes)} redação(ões) guardada(s) · última nota registrada: {notas_validas[0]} · melhor: {max(notas_validas)}")
    else:
        st.caption(f"{len(redacoes)} redação(ões) guardada(s), nenhuma com nota ainda.")

    for r in redacoes:
        tema_curto = r["tema"] if len(r["tema"]) <= 60 else r["tema"][:60] + "…"
        rotulo = f"{r['data_escrita']} — {tema_curto}"
        if r["nota"] is not None:
            rotulo += f" — nota {r['nota']}"
        with st.expander(rotulo):
            detalhes = []
            if r["fonte_correcao"]:
                detalhes.append(f"correção {r['fonte_correcao']}")
            if r["erros_ortograficos"] is not None:
                detalhes.append(f"{r['erros_ortograficos']} erro(s) ortográfico(s)")
            if detalhes:
                st.caption(" · ".join(detalhes))
            if r["texto"]:
                st.write(r["texto"])
            if r["arquivo_path"] and Path(r["arquivo_path"]).exists():
                if r["arquivo_path"].lower().endswith(".pdf"):
                    st.caption(f"📎 Arquivo: `{Path(r['arquivo_path']).name}` (PDF — abra pelo Explorador de Arquivos, o app só mostra imagem inline)")
                else:
                    st.image(r["arquivo_path"], use_container_width=True)
            if r["observacoes"]:
                st.caption(r["observacoes"])

            col_editar, col_apagar = st.columns(2)
            with col_editar:
                with st.popover("✏️ Editar", key=f"popover_editar_redacao_{r['id']}"):
                    st.caption("Pra quando a correção sai depois de já ter salvo a redação sem nota.")
                    novo_tema = st.text_input("Tema", value=r["tema"], key=f"editar_tema_{r['id']}")
                    nova_data = st.date_input(
                        "Data", value=date.fromisoformat(r["data_escrita"]), key=f"editar_data_{r['id']}"
                    )
                    novo_texto = st.text_area("Texto", value=r["texto"] or "", height=150, key=f"editar_texto_{r['id']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nova_nota = st.number_input(
                            "Nota (0-1000)", min_value=0, max_value=1000,
                            value=r["nota"] or 0, key=f"editar_nota_{r['id']}",
                        )
                    with col_b:
                        novos_erros = st.number_input(
                            "Erros ortográficos", min_value=0, max_value=100,
                            value=r["erros_ortograficos"] or 0, key=f"editar_erros_{r['id']}",
                        )
                    opcoes_fonte = ["ainda sem correção", "própria", "externa", "oficial"]
                    fonte_atual = r["fonte_correcao"] or "ainda sem correção"
                    nova_fonte = st.selectbox(
                        "Correção", opcoes_fonte, index=opcoes_fonte.index(fonte_atual), key=f"editar_fonte_{r['id']}"
                    )
                    novas_obs = st.text_area("Observações", value=r["observacoes"] or "", height=80, key=f"editar_obs_{r['id']}")
                    if st.button("Salvar edição", type="primary", key=f"salvar_editar_redacao_{r['id']}"):
                        db.atualizar_redacao(
                            r["id"], tema=novo_tema, data_escrita=nova_data.isoformat(),
                            texto=novo_texto or None, nota=int(nova_nota) or None,
                            erros_ortograficos=int(novos_erros) or None,
                            fonte_correcao=None if nova_fonte == "ainda sem correção" else nova_fonte,
                            observacoes=novas_obs or None,
                        )
                        st.rerun()
            with col_apagar:
                if st.button("🗑️ Apagar", key=f"apagar_redacao_{r['id']}"):
                    if r["arquivo_path"] and Path(r["arquivo_path"]).exists():
                        Path(r["arquivo_path"]).unlink()
                    db.apagar_redacao(r["id"])
                    st.rerun()


def render_admin() -> None:
    st.subheader("💾 Backup do banco")
    st.caption(
        "reconstruir_base.py já faz backup sozinho antes de atualizar a base. "
        "Use o botão abaixo pra tirar uma cópia extra antes de qualquer outra coisa arriscada "
        "(carregar um CSV colado errado, por exemplo)."
    )

    dias = backup_db.dias_desde_ultimo_backup()
    if dias is None:
        st.warning("Nenhum backup ainda. Os backups ficam só nesta máquina — sem um, um HD morto leva tudo junto.")
    elif dias >= 7:
        st.warning(f"Último backup local foi há {dias} dia(s). Baixe uma cópia recente pra algum lugar fora desta máquina (Drive, e-mail).")
    else:
        st.caption(f"Último backup local: há {dias} dia(s). Lembre de baixar uma cópia pra fora da máquina de vez em quando — backups/ não protege contra HD/SSD morto.")

    col_backup1, col_backup2 = st.columns([1, 2])
    with col_backup1:
        if st.button("📦 Fazer backup agora", type="primary"):
            caminho = backup_db.fazer_backup()
            st.session_state["ultimo_backup"] = str(caminho)
            st.success(f"Backup criado: {caminho.name}")
            st.rerun()

    backups = backup_db.listar_backups()
    if backups:
        with st.expander(f"Backups existentes ({len(backups)})"):
            for caminho in backups:
                tamanho_mb = caminho.stat().st_size / 1_000_000
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"`{caminho.name}` — {tamanho_mb:.2f} MB")
                with c2:
                    with open(caminho, "rb") as f:
                        st.download_button(
                            "⬇️ Baixar", data=f.read(), file_name=caminho.name,
                            mime="application/octet-stream", key=f"baixar_{caminho.name}",
                        )
    else:
        st.info("Nenhum backup ainda — vale fazer um agora, principalmente antes de carregar gabarito novo em lote.")

    st.divider()

    st.subheader("🎯 Meta diária")
    meta_atual = db.progresso_meta_diaria()["meta"]
    nova_meta = st.number_input(
        "Questões por dia", min_value=1, max_value=200, value=meta_atual, key="admin_meta_diaria",
    )
    if st.button("Salvar meta", key="admin_salvar_meta"):
        db.definir_configuracao("meta_diaria", str(int(nova_meta)))
        st.success(f"Meta diária atualizada pra {int(nova_meta)} questões.")
        st.rerun()

    st.divider()

    st.subheader("🗓️ Data da prova")
    st.caption("Alimenta a contagem regressiva e as fases do Calendário. Mudar isso reancora o início do plano.")
    data_atual = date.fromisoformat(db.obter_configuracao("data_prova", db.DATA_PROVA_PADRAO))
    nova_data = st.date_input("Data do ENEM (o dia que este app cobre: Matemática + Ciências)", value=data_atual, key="admin_data_prova")
    if st.button("Salvar data", key="admin_salvar_data_prova"):
        db.definir_configuracao("data_prova", nova_data.isoformat())
        db.definir_configuracao("data_inicio_plano", date.today().isoformat())
        st.success(f"Data da prova atualizada pra {nova_data.isoformat()}. Plano reancorado a partir de hoje.")
        st.rerun()

    st.divider()

    st.subheader("Colar gabarito direto (sem arquivo)")
    st.caption(
        "Cola um CSV com colunas numero,materia,gabarito (a primeira linha tem que ser esse cabeçalho). "
        "Coluna grande_area é opcional, por linha, se não usar o campo abaixo."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        ano_colar = st.number_input("Ano", min_value=2009, max_value=2100, value=2019, key="admin_ano")
    with col2:
        caderno_colar = st.text_input("Caderno", value="Azul", key="admin_caderno")
    with col3:
        grande_area_colar = st.selectbox("Grande área padrão", ["matematica", "ciencias_natureza"], key="admin_area")

    texto_csv = st.text_area(
        "Cole o CSV aqui", height=200, key="admin_csv_texto",
        placeholder="numero,materia,gabarito\n136,geometria_espacial,E\n137,logaritmo,E",
    )
    sobrescrever_colar = st.checkbox("Sobrescrever se já existir (recalcula tentativas afetadas)", value=True, key="admin_sobrescrever")

    if st.button("Carregar", type="primary", key="admin_carregar"):
        if not texto_csv.strip():
            st.warning("Cola o CSV primeiro.")
        else:
            try:
                resumo = db.carregar_gabarito_texto(
                    texto_csv, ano=int(ano_colar), caderno=caderno_colar,
                    grande_area_padrao=grande_area_colar, sobrescrever=sobrescrever_colar,
                )
            except ValueError as e:
                st.error(str(e))
            else:
                st.success(f"{resumo['classificadas']} classificada(s).")
                if resumo["nao_classificadas"]:
                    st.warning(f"{len(resumo['nao_classificadas'])} foram pra triagem: " + ", ".join(resumo["nao_classificadas"]))
                if resumo["erros"]:
                    st.error("Linhas com erro: " + "; ".join(resumo["erros"]))

    st.divider()

    st.subheader("🧠 Banco de prática (questões fora do ENEM oficial)")
    st.caption(
        "Pra trazer questões que você praticou em outro lugar (ex: uma sessão de treino de Óptica "
        "com o Gemini) e treiná-las aqui com o mesmo sistema de revisão espaçada/prioridade das "
        "questões reais do ENEM. Cola uma ou várias questões de uma vez, separadas por uma linha "
        "só com `---`. Formato de cada questão:"
    )
    st.code(
        "Enunciado da questão (pode ter várias linhas).\n"
        "A) alternativa A\n"
        "B) alternativa B\n"
        "C) alternativa C\n"
        "D) alternativa D\n"
        "E) alternativa E\n"
        "GABARITO: C",
        language=None,
    )
    st.caption("Letra da alternativa aceita ')', '.', ':' ou '-' depois e não liga pra maiúscula/minúscula.")

    col_pa, col_pm, col_pf = st.columns(3)
    with col_pa:
        area_pratica = st.selectbox(
            "Grande área", ["matematica", "ciencias_natureza"],
            format_func=lambda a: RÓTULO_AREA.get(a, a), key="admin_pratica_area",
        )
    with col_pm:
        materia_pratica = st.selectbox("Matéria", db.materias_validas(area_pratica), key="admin_pratica_materia")
    with col_pf:
        fonte_pratica = st.text_input("Fonte (opcional)", placeholder="gemini, chatgpt, autoral...", key="admin_pratica_fonte")

    texto_pratica = st.text_area(
        "Cole a(s) questão(ões) aqui", height=220, key="admin_pratica_texto",
        placeholder="Um raio de luz incide sobre um espelho plano...\nA) ...\nB) ...\nC) ...\nD) ...\nE) ...\nGABARITO: A",
    )

    if st.button("Importar pro banco de prática", type="primary", key="admin_pratica_importar"):
        if not texto_pratica.strip():
            st.warning("Cola a(s) questão(ões) primeiro.")
        elif not materia_pratica:
            st.warning("Selecione uma matéria antes de importar.")
        else:
            resumo_pratica = db.importar_questoes_praticas_texto(
                texto_pratica, grande_area=area_pratica, materia=materia_pratica,
                fonte=fonte_pratica.strip() or None,
            )
            if resumo_pratica["inseridas"]:
                st.success(f"{len(resumo_pratica['inseridas'])} questão(ões) importada(s) pro banco de prática.")
            if resumo_pratica["erros"]:
                st.error(f"{len(resumo_pratica['erros'])} bloco(s) com problema (não foram importados):")
                for erro in resumo_pratica["erros"]:
                    st.caption(f"• {erro}")
            if resumo_pratica["inseridas"]:
                st.rerun()

    banco_pratica_atual = db.listar_banco_pratica()
    if banco_pratica_atual:
        with st.expander(f"📦 Questões já no banco de prática ({len(banco_pratica_atual)})"):
            for q in banco_pratica_atual:
                aviso = " ⚠️ não classificado" if q["status_classificacao"] == "nao_classificado" else ""
                fonte_txt = f" · fonte: {q['fonte']}" if q["fonte"] else ""
                col_txt, col_del = st.columns([5, 1])
                with col_txt:
                    st.write(f"**{q['id_questao']}** — {q['materia']} — gabarito {q['alternativa_correta']}{fonte_txt}{aviso}")
                    st.caption(q["enunciado_texto"][:150] + ("..." if len(q["enunciado_texto"]) > 150 else ""))
                with col_del:
                    if st.button("🗑️", key=f"admin_pratica_apagar_{q['id_questao']}", help="Apagar esta questão"):
                        db.apagar_questao(q["id_questao"])
                        st.rerun()

    st.divider()

    st.subheader("🗑️ Apagar prova (irreversível)")
    st.caption("Remove uma prova inteira — útil pra limpar carga acidental, tipo CSV colado no ano errado.")

    provas_existentes = db.listar_provas()
    if not provas_existentes:
        st.info("Nenhuma prova cadastrada.")
    else:
        RÓTULO_AREA_ADMIN = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}
        opcoes_apagar = {
            f"{ano} — {caderno} — {RÓTULO_AREA_ADMIN.get(area, area)}": (ano, caderno, area)
            for ano, caderno, area in provas_existentes
        }
        escolha_apagar = st.selectbox("Prova a apagar", list(opcoes_apagar.keys()), key="admin_apagar_prova")
        ano_del, caderno_del, area_del = opcoes_apagar[escolha_apagar]

        confirmar = st.checkbox(
            f"Confirmo que quero apagar {escolha_apagar} permanentemente, junto com tentativas e resoluções ligadas a ela.",
            key="admin_confirmar_apagar",
        )
        if st.button("Apagar prova", type="primary", disabled=not confirmar, key="admin_apagar_botao"):
            resultado = db.apagar_prova(ano_del, caderno_del, area_del)
            st.success(
                f"{resultado['apagadas']} questão(ões) apagada(s). "
                f"{resultado['tentativas_perdidas']} tentativa(s) e "
                f"{resultado['resolucoes_perdidas']} resolução(ões) perdidas junto."
            )
            st.rerun()

    st.divider()

    st.subheader("✏️ Editar ou apagar uma questão específica")
    st.caption(
        "Pra corrigir/remover UMA questão sem mexer na prova inteira -- ex: linha extra ou "
        "número digitado errado num CSV colado. A Triagem só cobre questão ainda pendente; "
        "aqui dá pra corrigir mesmo uma já classificada."
    )
    provas_para_questao = db.listar_provas()
    if not provas_para_questao:
        st.info("Nenhuma prova cadastrada.")
    else:
        RÓTULO_AREA_ADMIN2 = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}
        opcoes_prova_q = {
            f"{ano} — {caderno} — {RÓTULO_AREA_ADMIN2.get(area, area)}": (ano, caderno, area)
            for ano, caderno, area in provas_para_questao
        }
        escolha_prova_q = st.selectbox("Prova", list(opcoes_prova_q.keys()), key="admin_questao_prova")
        ano_q, caderno_q, area_q = opcoes_prova_q[escolha_prova_q]

        numero_q = st.number_input("Número da questão", min_value=1, max_value=200, value=1, key="admin_questao_numero")
        id_questao_sel = db.gerar_id_canonico(int(ano_q), caderno_q, int(numero_q))
        detalhe = db.detalhe_questao(id_questao_sel)

        if detalhe is None:
            st.warning(f"`{id_questao_sel}` não existe nessa prova.")
        else:
            st.caption(f"`{id_questao_sel}` — status atual: {detalhe['status_classificacao']}")
            materias_area = db.materias_validas(area_q)
            col_mat, col_gab = st.columns(2)
            with col_mat:
                materia_atual = detalhe["materia"] if detalhe["materia"] in materias_area else None
                nova_materia = st.selectbox(
                    "Matéria", materias_area,
                    index=materias_area.index(materia_atual) if materia_atual else None,
                    placeholder=f"atual (fora da taxonomia): {detalhe['materia']}",
                    key=f"admin_questao_materia_{id_questao_sel}",
                )
            with col_gab:
                opcoes_letra_q = ["A", "B", "C", "D", "E"]
                novo_gabarito = st.selectbox(
                    "Gabarito", opcoes_letra_q,
                    index=opcoes_letra_q.index(detalhe["alternativa_correta"]),
                    key=f"admin_questao_gabarito_{id_questao_sel}",
                )
            if st.button("Salvar questão", type="primary", key=f"admin_questao_salvar_{id_questao_sel}"):
                if not nova_materia:
                    st.warning("Selecione uma matéria antes de salvar.")
                else:
                    db.inserir_questao(
                        ano=int(ano_q), caderno=caderno_q, numero=int(numero_q),
                        grande_area=area_q, materia=nova_materia,
                        alternativa_correta=novo_gabarito, sobrescrever=True,
                    )
                    st.success(f"`{id_questao_sel}` atualizada.")
                    st.rerun()

            with st.popover("🗑️ Apagar esta questão"):
                st.caption("Remove só essa questão (e tentativas/resoluções ligadas a ela), não a prova inteira.")
                confirmar_q = st.checkbox(
                    f"Confirmo apagar {id_questao_sel} permanentemente", key=f"admin_questao_confirmar_{id_questao_sel}"
                )
                if st.button("Apagar questão", type="primary", disabled=not confirmar_q, key=f"admin_questao_apagar_{id_questao_sel}"):
                    resultado_q = db.apagar_questao(id_questao_sel)
                    st.success(
                        f"`{id_questao_sel}` apagada. {resultado_q['tentativas_perdidas']} tentativa(s) e "
                        f"{resultado_q['resolucoes_perdidas']} resolução(ões) perdidas junto."
                    )
                    st.rerun()

    st.divider()

    st.subheader("Histórico de alterações")
    st.caption(
        "Toda vez que um gabarito ou matéria já cadastrados são corrigidos, fica registrado aqui — "
        "incluindo quantas tentativas antigas tiveram o resultado recalculado por causa da correção."
    )
    historico = db.historico_alteracoes()
    if not historico:
        st.info("Nenhuma alteração registrada ainda.")
        return
    linhas = [
        {
            "Questão": h["id_questao"], "Campo": h["campo"],
            "De": h["valor_antigo"], "Para": h["valor_novo"],
            "Quando": h["data_alteracao"][:16],
            "Tentativas recalculadas": h["tentativas_recalculadas"],
        }
        for h in historico
    ]
    ui_theme.tabela_html(linhas)


def render_guia_estudante() -> None:
    sub = st.radio(
        "Conteúdo",
        ["Mentalidade & Prioridade", "Tutor Socrático (Ciências)", "Extração de Gabarito (outra IA)",
         "Banco de Prática (outra IA)"],
        horizontal=True,
    )
    nomes_arquivo = {
        "Mentalidade & Prioridade": "manual_prioridade_de_estudo.md",
        "Tutor Socrático (Ciências)": "guia_estudante.md",
        "Extração de Gabarito (outra IA)": "prompt_extracao_gabarito.md",
        "Banco de Prática (outra IA)": "prompt_banco_pratica.md",
    }
    nome_arquivo = nomes_arquivo[sub]
    caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning(f"{nome_arquivo} não encontrado em core/. Salve o arquivo lá primeiro.")


def _tagline_contagem_regressiva() -> str:
    prova = db.dias_ate_prova()
    if prova["ja_passou"]:
        return "treino com prova real, corrigido na hora"
    if prova["dias_restantes"] == 0:
        return "é hoje. boa prova 🍀"
    return f"treino com prova real, corrigido na hora · 🗓️ {prova['dias_restantes']} dias até o ENEM"


# Calendário/Objetivos/Redação/Triagem tirados da navegação (pedido do
# usuário, 2026-09-11): simplificação deliberada pra o app girar em
# torno do miolo real -- fazer questão, fazer simulado -- alinhado com
# o que já existe no app mobile. Nenhuma delas foi apagada: as funções
# (render_calendario, render_objetivos, render_redacao,
# triagem.render_triagem) continuam inteiras mais abaixo/no módulo
# triagem.py, só não tem mais link nenhum que leve até elas -- mesmo
# padrão reversível já usado pra tirar a barra "Modo" de Provas ENEM
# nesta mesma rodada. Motivo específico da Redação: só faz sentido
# voltar quando tiver correção por IA -- sem isso, é uma tela sem
# função real no ciclo "responder → simulado" que o app agora foca.
# Admin FICA (pedido explícito), só marcado pra uma organizada futura.
_PAGINAS = [
    ("cartao", "📝", "Cartão-resposta"),
    ("provas_enem", "🗒️", "Provas ENEM"),
    ("analise", "📊", "Minha análise"),
    ("simulados", "🗂️", "Simulados já feitos"),
    ("coletar", "🔗", "Coletar vídeos"),
    ("admin", "🔐", "Admin"),
    ("guia", "📚", "Guia do Estudante"),
]

# Ícone (nome de enem_theme._ICONS) por página, pro cabeçalho com badge
# de ui_theme.hero(icone=...) -- título vem de _PAGINAS (fonte única),
# só o ícone mora aqui. Substitui o hero genérico ("📝 Cartão-resposta
# digital" fixo em toda página que não é a Home) que sobrou de antes da
# 3a rodada do handoff mover a trilha pra "cartao" -- cada página passa
# a mostrar o título e ícone que são realmente dela.
_ICONE_PAGINA = {
    "provas_enem": "file-text",
    "analise": "bar-chart",
    "simulados": "archive",
    "calendario": "calendar",
    "objetivos": "target",
    "redacao": "pen",
    "coletar": "link",
    "triagem": "tag",
    "admin": "shield",
    "guia": "book",
}


if __name__ == "__main__":
    st.set_page_config(page_title="Cartão-resposta", page_icon="📝", layout="wide")
    db.inicializar_banco()
    # Tema (claro/escuro) mora na própria URL (?tema=), não em
    # session_state -- mesmo raciocínio zero-JS do ?pagina= (ver
    # comentário de navegacao_lateral): sobrevive a um link normal do
    # menu sem precisar reidratar estado nenhum. Lido aqui uma vez;
    # render_banco_pratica() (única outra chamadora de injetar tema,
    # pra sua própria página com enem_theme.inject()) lê de novo
    # direto de st.query_params -- é um proxy global, não precisa
    # passar por parâmetro de função.
    tema_atual = st.query_params.get("tema", "escuro")
    if tema_atual not in ("escuro", "claro"):
        tema_atual = "escuro"
    ui_theme.injetar_tema(tema_atual)

    # Navegação por query param (?pagina=...) em vez de st.sidebar.radio()
    # de propósito -- a sidebar nativa do Streamlit abre FECHADA por
    # padrão em tela estreita, e o botão pra abrir ficou inacessível no
    # celular do Gabriel mesmo depois de ajustar o CSS (reportado em
    # produção 2x). Um menu implementado do zero com <a href="?pagina=..">
    # simples não depende de nenhum comportamento responsivo interno do
    # Streamlit que eu não consigo testar de verdade nesta sessão --
    # funciona igual em qualquer largura de tela, verificável via DOM
    # sem precisar simular celular.
    valores_validos = {chave for chave, _, _ in _PAGINAS}
    pagina_atual = st.query_params.get("pagina", "cartao")
    # "banco_pratica" era o item de 1a classe antes da 3a rodada do
    # handoff (design_handoff_enem_gamificado/RELATORIO-RODADA-2.md,
    # seção "Mudança estrutural") -- agora é só um alias que redireciona
    # pra "cartao" (a nova home), pra não quebrar um link/favorito salvo
    # com a chave antiga.
    if pagina_atual == "banco_pratica":
        pagina_atual = "cartao"
    # "prova_beta" era página própria no menu -- 10a rodada (2026-09)
    # juntou "Prova com enunciado" como mais um "Modo" dentro de
    # "Provas ENEM" (pedido do usuário: mesma aba do gabarito CSV).
    # Alias de redirect, mesmo padrão de "banco_pratica" acima, pra não
    # quebrar link/favorito salvo com a chave antiga -- não reabre
    # exatamente no modo "Prova com enunciado" (essa escolha é um
    # widget de sessão, não dá pra linkar direto), só na página certa.
    if pagina_atual == "prova_beta":
        pagina_atual = "provas_enem"
    if pagina_atual not in valores_validos:
        pagina_atual = "cartao"

    # ui_theme.navegacao_lateral() (gaveta de texto + hambúrguer) SAIU
    # de __main__ -- pedido do usuário, 2026-09-11: "substitua cartão
    # resposta, prova enem e tudo aquele menu por aqueles ícones".
    # barra_navegacao_icones() é a navegação real agora, sem o
    # rodapé "dias até o ENEM" que a gaveta antiga tinha (não sobra
    # espaço numa barra de 82px só de ícones) -- essa contagem
    # regressiva continua visível em outros lugares da página (cena
    # de Provas ENEM, Objetivos), não sumiu do app, só deste rodapé
    # específico. navegacao_lateral() continua definida, só não é mais
    # chamada -- mesmo padrão reversível de toda esta rodada.
    ui_theme.barra_navegacao_icones(_PAGINAS, pagina_atual, tema_atual=tema_atual)
    if pagina_atual not in ("cartao", "provas_enem"):
        # "Cartão-resposta" (agora a home, com a trilha gamificada --
        # ver render_banco_pratica) usa o header próprio do enem_theme
        # (ícone + título + streak/rank, ver design_handoff_enem_
        # gamificado/README.md seção "Home"). As outras páginas usam
        # ui_theme.hero(icone=...) -- mesma linguagem de badge, sem os
        # pills de streak/XP (não fazem sentido fora da Home). Título
        # vem de _PAGINAS e ícone de _ICONE_PAGINA (chave única, cada
        # página com o próprio, em vez do "📝 Cartão-resposta digital"
        # fixo que sobrava de antes da 3a rodada do handoff mover a
        # trilha pra cá). O hambúrguer/gaveta acima continua igual em
        # toda página: é navegação entre as seções do app, não faz
        # parte do redesign de nenhum mockup específico.
        #
        # "provas_enem" também PULA este hero genérico (pedido do
        # usuário, 2026-09-11): a cena panorâmica que abre a própria
        # página (_renderizar_cena_mesa(), dentro de render_cartao_
        # resposta()) já mostra título e "dias até o ENEM" -- manter o
        # hero aqui em cima duplicava a mesma informação e "poluía" o
        # topo que devia começar direto no cenário escuro, igual à
        # referência de design.
        titulo_pagina = next(rotulo for chave, _, rotulo in _PAGINAS if chave == pagina_atual)
        ui_theme.hero(
            titulo_pagina, _tagline_contagem_regressiva(),
            icone=_ICONE_PAGINA.get(pagina_atual),
        )

    if pagina_atual == "cartao":
        render_banco_pratica()
    elif pagina_atual == "provas_enem":
        render_cartao_resposta()
    elif pagina_atual == "analise":
        render_analise()
    elif pagina_atual == "simulados":
        render_simulados_feitos()
    elif pagina_atual == "calendario":
        render_calendario()
    elif pagina_atual == "objetivos":
        render_objetivos()
    elif pagina_atual == "redacao":
        render_redacao()
    elif pagina_atual == "coletar":
        coletar_videos.render_coletar_videos()
    elif pagina_atual == "triagem":
        triagem.render_triagem()
    elif pagina_atual == "admin":
        render_admin()
    elif pagina_atual == "guia":
        render_guia_estudante()