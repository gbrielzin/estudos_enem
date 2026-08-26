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
import tempfile

import streamlit as st

import db
import coletar_videos
import triagem
import backup_db


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


def render_cartao_resposta() -> None:
    db.inicializar_banco()
    render_carregar_gabarito()

    provas = db.listar_provas()
    if not provas:
        st.info("Nenhuma prova cadastrada ainda — insira questões (com gabarito) antes de responder.")
        return

    modo = st.radio(
        "Modo",
        ["Uma prova por vez", "Simulado completo (Matemática + Ciências)"],
        horizontal=True,
    )

    if modo == "Simulado completo (Matemática + Ciências)":
        _render_simulado_completo(provas)
        return

    areas_disponiveis = sorted({area for _, _, area in provas})
    area_sel = st.radio(
        "Área", areas_disponiveis, format_func=lambda a: RÓTULO_AREA.get(a, a), horizontal=True,
    )

    opcoes = {
        f"{ano} — {caderno}": (ano, caderno, area)
        for ano, caderno, area in provas
        if area == area_sel
    }
    if not opcoes:
        st.info(f"Nenhuma prova de {RÓTULO_AREA.get(area_sel, area_sel)} cadastrada ainda.")
        return
    escolha = st.selectbox("Prova", list(opcoes.keys()))
    ano_sel, caderno_sel, area_sel = opcoes[escolha]

    _renderizar_bloco_prova(ano_sel, caderno_sel, area_sel)


def _render_simulado_completo(provas: list[tuple[int, str, str]]) -> None:
    """Faz Matemática e Ciências da Natureza do mesmo ano+caderno em
    sequência, cada uma na sua aba. Corrige, guarda e mostra o
    resultado de cada área separadamente — nunca mistura as duas na
    mesma grade nem no mesmo cálculo, mesma regra do resto do
    sistema."""
    por_ano_caderno: dict[tuple[int, str], set[str]] = {}
    for ano, caderno, area in provas:
        por_ano_caderno.setdefault((ano, caderno), set()).add(area)

    combinacoes = sorted(
        [
            (ano, caderno)
            for (ano, caderno), areas in por_ano_caderno.items()
            if {"matematica", "ciencias_natureza"} <= areas
        ],
        reverse=True,
    )
    if not combinacoes:
        st.info(
            "Nenhum ano/caderno tem as duas áreas cadastradas ainda — "
            "o simulado completo só aparece quando Matemática e Ciências "
            "da mesma prova já foram carregadas."
        )
        return

    opcoes = {f"{ano} — {caderno}": (ano, caderno) for ano, caderno in combinacoes}
    escolha = st.selectbox("Simulado", list(opcoes.keys()))
    ano_sel, caderno_sel = opcoes[escolha]

    aba_mat, aba_ciencias = st.tabs(["📐 Matemática", "🔬 Ciências da Natureza"])
    with aba_mat:
        _renderizar_bloco_prova(ano_sel, caderno_sel, "matematica")
    with aba_ciencias:
        _renderizar_bloco_prova(ano_sel, caderno_sel, "ciencias_natureza")


def _renderizar_bloco_prova(ano_sel: int, caderno_sel: str, area_sel: str) -> None:
    """Corpo real da tela de responder + corrigir uma prova. Recebe a
    área como parâmetro (em vez de pegar de um seletor global) pra
    poder ser chamada duas vezes na mesma página, uma por aba, no modo
    simulado completo — por isso toda chave de widget/session_state
    aqui dentro é sufixada com ano+caderno+área, senão colidiria."""
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
        with st.expander(f"📈 Histórico de tentativas dessa prova ({len(historico)})", expanded=True):
            for h in historico:
                pct = f"{h['taxa_acerto']*100:.0f}%" if h["taxa_acerto"] is not None else "—"
                st.write(f"**Tentativa {h['tentativa']}**: {h['acertos']}/{h['total']} ({pct}) — {h['inicio'][:10]}")

    with st.expander("⚡ Preenchimento rápido (cola a sequência de letras)"):
        st.caption(
            "Cola as letras na ordem das questões, sem espaço nem pontuação (ex: ABCDEBAACD...). "
            "Use * ou deixa em branco pra pular uma questão que você não respondeu."
        )
        sequencia = st.text_input("Sequência de respostas", key=f"sequencia_rapida_{sufixo}")
        if st.button("Aplicar sequência", key=f"aplicar_seq_{sufixo}"):
            aplicadas = 0
            for i, q in enumerate(questoes):
                if i < len(sequencia) and sequencia[i].upper() in "ABCDE":
                    st.session_state[f"resp_{q['id_questao']}"] = sequencia[i].upper()
                    aplicadas += 1
            st.success(f"{aplicadas} resposta(s) aplicada(s) — confere a grade abaixo antes de corrigir.")

    with st.form(f"cartao_resposta_form_{sufixo}"):
        cols = st.columns(5)
        for i, q in enumerate(questoes):
            with cols[i % 5]:
                rotulo = f"Q{q['numero_questao']}"
                if q["status_classificacao"] == "nao_classificado":
                    rotulo += " ⚠️"
                st.radio(
                    rotulo,
                    ["—", "A", "B", "C", "D", "E"],
                    horizontal=True,
                    key=f"resp_{q['id_questao']}",
                )
        enviado = st.form_submit_button("Corrigir", type="primary")

    chave_resultado = f"resultados_{sufixo}"

    if enviado:
        respostas = {
            q["id_questao"]: st.session_state[f"resp_{q['id_questao']}"]
            for q in questoes
            if st.session_state.get(f"resp_{q['id_questao']}", "—") != "—"
        }
        if not respostas:
            st.warning("Marque pelo menos uma resposta antes de corrigir.")
            return
        st.session_state[chave_resultado] = [
            db.registrar_tentativa(id_q, resp) for id_q, resp in respostas.items()
        ]

    resultados = st.session_state.get(chave_resultado)
    if not resultados:
        return

    acertos = sum(1 for r in resultados if r["resultado"] == "acertou")
    total = len(resultados)

    st.success(f"{acertos}/{total} acertos ({acertos / total * 100:.0f}%)")

    erros = [r for r in resultados if r["resultado"] == "errou"]
    if erros:
        with st.expander(f"⚠️ {len(erros)} questão(ões) errada(s) — já agendadas pra revisão", expanded=True):
            for r in erros:
                st.write(f"**{r['id_questao']}** — próxima revisão: {r['proxima_revisao']}")

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
                    if res["tipo"] == "video":
                        st.video(res["conteudo"])
                    else:
                        st.caption(f"Resolução em texto ({res['canal'] or 'sem canal'}): {res['conteudo']}")

    if total < len(questoes):
        st.caption(f"{len(questoes) - total} questão(ões) não foi(ram) respondida(s) e não entrou(aram) no cálculo.")


def render_analise() -> None:
    nivel = db.calcular_nivel_jogador()
    ofensiva = db.calcular_ofensiva()

    col1, col2, col3 = st.columns(3)
    col1.metric("Rank", nivel["rank"], f"{nivel['xp']} XP")
    col2.metric("🔥 Ofensiva atual", f"{ofensiva['atual']} dia(s)")
    col3.metric("Melhor ofensiva", f"{ofensiva['melhor']} dia(s)")

    if nivel["proximo_rank"]:
        st.caption(f"Faltam {nivel['xp_para_proximo']} XP pro {nivel['proximo_rank']}.")

    st.caption("Últimos 30 dias:")
    dias = ofensiva["calendario_30_dias"]
    linha_html = "".join("🟩" if d["ativo"] else "⬜" for d in dias)
    st.markdown(f"<div style='font-size:20px;letter-spacing:2px'>{linha_html}</div>", unsafe_allow_html=True)

    st.divider()

    area_analise = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True, key="area_analise",
    )

    st.subheader("Prioridade de estudo")
    prioridade = db.prioridade_de_estudo(area_analise)

    if not prioridade["ranking"] and not prioridade["sem_dados"]:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        if prioridade["ranking"]:
            linhas_ranking = []
            for r in prioridade["ranking"]:
                aviso = " ⚠️" if r["amostra_pequena"] else ""
                linhas_ranking.append({
                    "Matéria": r["materia"],
                    "Recorrência": f"{r['percentual_recorrencia']}%",
                    "Sua taxa de acerto": f"{r['taxa_acerto_pct']}%" + aviso,
                    "Tentativas": r["total_tentativas"],
                    "Prioridade": r["score_prioridade"],
                })
            st.dataframe(linhas_ranking, hide_index=True, use_container_width=True)
            st.caption(
                "Prioridade = cai bastante E você erra bastante. Quanto maior, mais vale estudar agora. "
                f"⚠️ = menos de {db.MIN_AMOSTRA_CONFIAVEL} tentativas — ordem pode mudar com mais dado."
            )
        if prioridade["sem_dados"]:
            materias = ", ".join(
                f"{s['materia']} ({s['percentual_recorrencia']}%)" for s in prioridade["sem_dados"]
            )
            st.warning(f"Recorrentes mas você nunca respondeu ainda, sem prioridade calculável: {materias}")

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
        st.dataframe(linhas_erro, hide_index=True, use_container_width=True)

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
        st.dataframe(
            [
                {"Matéria": r["materia"], "Provas com a matéria": r["provas_com_materia"], "%": r["percentual"]}
                for r in recorrencia
            ],
            hide_index=True,
            use_container_width=True,
        )

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
    st.dataframe(linhas, hide_index=True, use_container_width=True)


def render_admin() -> None:
    st.subheader("💾 Backup do banco")
    st.caption(
        "Ninguém reconstrói a base do zero sem um backup na mão primeiro — "
        "reconstruir_base.py não sabe recriar vídeo coletado nem tentativa respondida "
        "fora do que já está congelado em CSV. Clique aqui antes de mexer em qualquer coisa arriscada."
    )
    col_backup1, col_backup2 = st.columns([1, 2])
    with col_backup1:
        if st.button("📦 Fazer backup agora", type="primary"):
            caminho = backup_db.fazer_backup()
            st.session_state["ultimo_backup"] = str(caminho)
            st.success(f"Backup criado: {caminho.name}")

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
    st.dataframe(linhas, hide_index=True, use_container_width=True)


def render_guia_estudante() -> None:
    st.title("📚 Guia do Estudante")
    sub = st.radio(
        "Conteúdo",
        ["Tutor Socrático (Ciências)", "Extração de Gabarito (outra IA)"],
        horizontal=True,
    )
    nome_arquivo = "guia_estudante.md" if sub.startswith("Tutor") else "prompt_extracao_gabarito.md"
    caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning(f"{nome_arquivo} não encontrado em core/. Salve o arquivo lá primeiro.")


if __name__ == "__main__":
    st.set_page_config(page_title="Cartão-resposta", page_icon="📝", layout="wide")
    st.title("📝 Cartão-resposta digital")

    pagina = st.sidebar.radio(
        "Menu",
        ["📝 Cartão-resposta", "📊 Minha análise", "🔗 Coletar vídeos", "🏷️ Triagem", "🔐 Admin", "📚 Guia do Estudante"],
    )

    if pagina == "📝 Cartão-resposta":
        render_cartao_resposta()
    elif pagina == "📊 Minha análise":
        render_analise()
    elif pagina == "🔗 Coletar vídeos":
        coletar_videos.render_coletar_videos()
    elif pagina == "🏷️ Triagem":
        triagem.render_triagem()
    elif pagina == "🔐 Admin":
        render_admin()
    elif pagina == "📚 Guia do Estudante":
        render_guia_estudante()