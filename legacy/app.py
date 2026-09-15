import os
import streamlit as st
import pandas as pd

# Reaproveita TODA a lógica já construída no main.py — o front não duplica
# nenhuma regra de negócio, só chama as mesmas funções testadas na Etapa 1-5.
from main import (
    autenticar_youtube,
    extrair_playlist_id,
    extrair_numero_questao,
    buscar_todos_os_videos,
    processar_videos,
    processar_videos_com_inferencia,
    expandir_amostra_via_busca,
    adicionar_manual,
    exportar_csv,
    carregar_tabela_probabilidades,
    atualizar_tabela_com_novos_dados,
    CAMINHO_CSV,
    CAMINHO_TABELA_PROBABILIDADES,
)

st.set_page_config(page_title="Coletor ENEM", page_icon="📚", layout="wide")
st.title("📚 Coletor de Questões ENEM")


@st.cache_resource
def get_youtube_client():
    """@st.cache_resource evita reautenticar a cada clique — o cliente
    do YouTube é criado uma vez só e reaproveitado durante a sessão."""
    return autenticar_youtube()


youtube = get_youtube_client()

aba_playlist, aba_busca, aba_lote, aba_juncao, aba_dados = st.tabs(
    ["📋 Playlist", "🔍 Busca automática", "📝 Lote (resumo)", "🔗 Junção", "📊 Dados coletados"]
)


# ============================================================
# ABA 1 — Modo manual (playlist)
# ============================================================
with aba_playlist:
    st.subheader("Coletar vídeos de uma playlist")
    link_playlist = st.text_input("Link ou ID da playlist", key="playlist_link")
    tem_rotulo = st.checkbox("Essa playlist tem 'Nível de dificuldade' na descrição?", value=True)

    if st.button("Coletar playlist", type="primary"):
        if not link_playlist:
            st.warning("Cole um link ou ID primeiro.")
        else:
            with st.spinner("Buscando vídeos..."):
                playlist_id = extrair_playlist_id(link_playlist)
                videos = buscar_todos_os_videos(youtube, playlist_id)

                if tem_rotulo:
                    dados = processar_videos(videos)
                    atualizar_tabela_com_novos_dados(dados)
                else:
                    tabela = carregar_tabela_probabilidades()
                    dados = processar_videos_com_inferencia(videos, tabela)

                exportar_csv(dados)

            st.success(f"{len(dados)} vídeo(s) processado(s) e salvos.")
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)


# ============================================================
# ABA 2 — Modo automático (busca por palavra-chave)
# ============================================================
with aba_busca:
    st.subheader("Buscar vídeos por palavra-chave (múltiplos canais)")
    st.caption("⚠️ Cada query custa 100 unidades de cota da API — use poucas por vez.")

    queries_texto = st.text_area("Uma query por linha", height=100,
                                  placeholder="questão enem matemática nível de dificuldade\nresolução enem matemática dificuldade da questão")

    if st.button("Buscar", type="primary"):
        queries = [q.strip() for q in queries_texto.split("\n") if q.strip()]
        if not queries:
            st.warning("Digite ao menos uma query.")
        else:
            with st.spinner("Buscando na web do YouTube..."):
                dados = expandir_amostra_via_busca(youtube, queries)
                atualizar_tabela_com_novos_dados(dados)
                exportar_csv(dados)

            st.success(f"{len(dados)} vídeo(s) com nível confirmado.")
            if dados:
                st.dataframe(pd.DataFrame(dados), use_container_width=True)


# ============================================================
# ABA 3 — Entrada em lote (vídeo-resumo com IA)
# ============================================================
with aba_lote:
    st.subheader("Colar dados de um vídeo-resumo (IA do YouTube)")
    st.caption("Peça à IA do YouTube no formato: Questão;Matéria;Nível — uma linha por questão.")

    col1, col2 = st.columns(2)
    with col1:
        video_id_lote = st.text_input("ID do vídeo (depois de 'v=' no link)")
    with col2:
        canal_lote = st.text_input("Canal (opcional)")

    lote_texto = st.text_area("Cole as linhas aqui", height=280,
                               placeholder="Questão 136;Probabilidade;Difícil\nQuestão 137;Estatística;Fácil")

    if st.button("Processar lote", type="primary"):
        linhas = [l for l in lote_texto.split("\n") if l.strip()]
        if not video_id_lote:
            st.warning("Informe o ID do vídeo primeiro.")
        elif not linhas:
            st.warning("Cole ao menos uma linha.")
        else:
            validos, invalidos = 0, 0
            for linha in linhas:
                partes = [p.strip() for p in linha.split(";")]
                if len(partes) != 3:
                    invalidos += 1
                    continue
                titulo, materia, nivel = partes
                adicionar_manual(titulo, video_id_lote, nivel, materia, canal_lote)
                validos += 1

            st.success(f"Processadas: {validos} | Inválidas: {invalidos}")


# ============================================================
# ABA 4 — Junção (link real + nível do resumo)
# ============================================================
with aba_juncao:
    st.subheader("Juntar link real da resolução + nível do vídeo-resumo")
    st.caption("Use com UMA prova por vez — não misture anos diferentes.")

    link_playlist_juncao = st.text_input("Link ou ID da playlist com resoluções individuais", key="juncao_playlist")
    lote_juncao = st.text_area("Cole as linhas do vídeo-resumo: Questão;Matéria;Nível", height=280, key="juncao_lote")

    if st.button("Fazer junção", type="primary"):
        if not link_playlist_juncao:
            st.warning("Cole o link da playlist primeiro.")
        else:
            with st.spinner("Buscando vídeos individuais..."):
                playlist_id = extrair_playlist_id(link_playlist_juncao)
                videos = buscar_todos_os_videos(youtube, playlist_id)

            videos_por_numero = {}
            for video in videos:
                titulo = video["snippet"]["title"]
                video_id_v = video["snippet"]["resourceId"]["videoId"]
                canal_titulo = video["snippet"].get("videoOwnerChannelTitle", "")
                canal_id = video["snippet"].get("videoOwnerChannelId", "")
                numero = extrair_numero_questao(titulo)
                if numero:
                    videos_por_numero[numero] = {
                        "titulo": titulo,
                        "link": f"https://www.youtube.com/watch?v={video_id_v}",
                        "canal": canal_titulo,
                        "canal_id": canal_id,
                    }

            st.info(f"{len(videos_por_numero)} vídeo(s) individual(is) mapeado(s) por número.")

            linhas = [l for l in lote_juncao.split("\n") if l.strip()]
            registros, nao_encontrados = [], []

            for linha in linhas:
                partes = [p.strip() for p in linha.split(";")]
                if len(partes) != 3:
                    continue
                titulo_lote, materia, nivel = partes
                numero = extrair_numero_questao(titulo_lote)
                if not numero or numero not in videos_por_numero:
                    nao_encontrados.append(titulo_lote)
                    continue
                info = videos_por_numero[numero]
                registros.append({
                    "titulo": info["titulo"],
                    "link": info["link"],
                    "nivel": nivel.capitalize(),
                    "materia": materia,
                    "fonte_nivel": "confirmado_transcricao_ia",
                    "canal": info["canal"],
                    "canal_id": info["canal_id"],
                })

            exportar_csv(registros)
            st.success(f"{len(registros)} questão(ões) unida(s) e salva(s).")

            if nao_encontrados:
                with st.expander(f"⚠️ {len(nao_encontrados)} sem correspondência"):
                    st.write(nao_encontrados)

            if registros:
                st.dataframe(pd.DataFrame(registros), use_container_width=True)


# ============================================================
# ABA 5 — Visualização e gerenciamento dos dados
# ============================================================
def _render_dados_csv(df: pd.DataFrame):
    """Renderiza filtros, tabela, download e opção de apagar — chamada só
    quando o CSV foi lido com sucesso (sem erro de formato)."""
    st.write(f"**Total de registros:** {len(df)}")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_materia = st.multiselect("Filtrar por matéria", options=sorted(df["materia"].dropna().unique()))
    with col_f2:
        filtro_nivel = st.multiselect("Filtrar por nível", options=sorted(df["nivel"].dropna().unique()))

    df_filtrado = df.copy()
    if filtro_materia:
        df_filtrado = df_filtrado[df_filtrado["materia"].isin(filtro_materia)]
    if filtro_nivel:
        df_filtrado = df_filtrado[df_filtrado["nivel"].isin(filtro_nivel)]

    st.dataframe(df_filtrado, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Baixar CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="questoes_enem.csv",
            mime="text/csv",
        )
    with col2:
        if "confirmar_delete_csv" not in st.session_state:
            st.session_state.confirmar_delete_csv = False

        if not st.session_state.confirmar_delete_csv:
            if st.button("🗑️ Apagar CSV"):
                st.session_state.confirmar_delete_csv = True
                st.rerun()
        else:
            st.warning("Tem certeza? Essa ação não pode ser desfeita.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Sim, apagar", type="primary"):
                    os.remove(CAMINHO_CSV)
                    st.session_state.confirmar_delete_csv = False
                    st.success("CSV apagado.")
                    st.rerun()
            with c2:
                if st.button("❌ Cancelar"):
                    st.session_state.confirmar_delete_csv = False
                    st.rerun()


with aba_dados:
    st.subheader("Dados coletados")

    if os.path.exists(CAMINHO_CSV):
        try:
            df = pd.read_csv(CAMINHO_CSV, encoding="utf-8-sig")
        except pd.errors.ParserError as erro:
            st.error(
                "⚠️ O CSV está com formato inconsistente (colunas diferentes em linhas diferentes) "
                "e não pôde ser lido inteiro."
            )
            st.code(str(erro))
            st.info(
                "Isso costuma acontecer quando registros de fases diferentes do projeto "
                "(com colunas diferentes) foram misturados no mesmo arquivo. "
                "O mais simples é apagar e recomeçar a coleta com o formato atual."
            )
            if st.button("🗑️ Apagar CSV corrompido"):
                os.remove(CAMINHO_CSV)
                st.success("CSV apagado. Recarregue a página ou colete novos dados.")
                st.rerun()
            df = None
        else:
            _render_dados_csv(df)
    else:
        st.info("Nenhum CSV encontrado ainda. Colete dados nas abas acima.")

    st.divider()
    st.subheader("Tabela de probabilidades (inferência)")

    tabela = carregar_tabela_probabilidades()
    if tabela:
        st.json(tabela)
        if st.button("🗑️ Apagar tabela de probabilidades"):
            os.remove(CAMINHO_TABELA_PROBABILIDADES)
            st.success("Tabela apagada.")
            st.rerun()
    else:
        st.info("Nenhuma tabela de probabilidades ainda.")