"""
coletar_videos.py — busca vídeos de uma playlist do YouTube e liga como
resolução às questões do enem.db (não escreve mais em CSV nenhum).

Reaproveita autenticação e busca do main.py (mesma lógica testada da v1)
— não duplica isso aqui. A única coisa nova é: extrai número/ano do
título, ignora vídeos DIGITAL, e chama db.inserir_resolucao() em vez de
exportar_csv().
"""
import re
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # pra achar main.py na raiz do projeto
import main as coletor_youtube  # autenticar_youtube, extrair_playlist_id, buscar_todos_os_videos

import db

CADERNO_PADRAO = "Azul"


def extrair_numero(titulo: str):
    m = re.search(r"Quest[ãa]o\s+(\d+)", titulo, re.IGNORECASE)
    return int(m.group(1)) if m else None


def extrair_ano(titulo: str):
    anos = re.findall(r"\b((?:19|20)\d{2})\b", titulo)
    return int(anos[-1]) if anos else None


def eh_digital(titulo: str) -> bool:
    return "DIGITAL" in titulo.upper()


def extrair_materia_do_titulo(titulo: str):
    """Tenta o mesmo padrão 'Questão N - Caderno X | Matéria | ...' que
    os títulos do Xequemat já seguem. Se não bater, retorna None -- não
    inventa matéria a partir de um formato desconhecido."""
    partes = titulo.split("|")
    if len(partes) >= 2:
        return partes[1].strip()
    return None


def processar_playlist(videos: list, caderno: str = CADERNO_PADRAO) -> dict:
    """Recebe a lista de vídeos já buscada (formato da API do YouTube:
    video['snippet']['title'], video['snippet']['resourceId']['videoId'],
    video['snippet'].get('videoOwnerChannelTitle')) e liga cada um à
    questão canônica correspondente, quando existe gabarito pra ela.

    Retorna um resumo detalhado -- nada é escrito silenciosamente."""
    resultado = {
        "ligados": [], "sem_questao": [], "digital_ignorado": [],
        "titulo_nao_reconhecido": [], "materia_atualizada": [], "materia_nao_extraida": [],
    }

    for video in videos:
        titulo = video["snippet"]["title"]
        video_id = video["snippet"]["resourceId"]["videoId"]
        canal = video["snippet"].get("videoOwnerChannelTitle", "")
        link = f"https://www.youtube.com/watch?v={video_id}"

        if eh_digital(titulo):
            resultado["digital_ignorado"].append(titulo)
            continue

        numero = extrair_numero(titulo)
        ano = extrair_ano(titulo)
        if not numero or not ano:
            resultado["titulo_nao_reconhecido"].append(titulo)
            continue

        id_q = db.gerar_id_canonico(ano, caderno, numero)

        try:
            db.inserir_resolucao(id_q, "video", link, canal=canal)
            resultado["ligados"].append({"id_questao": id_q, "titulo": titulo})
        except ValueError:
            resultado["sem_questao"].append({"id_questao": id_q, "titulo": titulo})
            continue  # sem questão cadastrada, não dá nem pra tentar atualizar matéria

        materia = extrair_materia_do_titulo(titulo)
        if not materia:
            resultado["materia_nao_extraida"].append({"id_questao": id_q, "titulo": titulo})
        else:
            with db._conectar() as conn:
                atual = conn.execute(
                    "SELECT alternativa_correta, grande_area, status_classificacao "
                    "FROM questoes WHERE id_questao=?", (id_q,)
                ).fetchone()
            if atual and atual[2] == "nao_classificado":
                # só sobrescreve se a questão ainda estava pendente -- não
                # troca uma matéria já classificada por uma nova adivinhação
                gabarito_atual, grande_area_atual, _ = atual
                _, status = db.inserir_questao(
                    ano=ano, caderno=caderno, numero=numero,
                    grande_area=grande_area_atual, materia=materia,
                    alternativa_correta=gabarito_atual, sobrescrever=True,
                )
                resultado["materia_atualizada"].append(
                    {"id_questao": id_q, "materia_nova": materia, "status": status}
                )

    return resultado


def render_video_avulso() -> None:
    st.subheader("Adicionar um vídeo avulso")
    st.caption(
        "Pra quando o canal principal não tem a questão e você achou a resolução em outro lugar "
        "(outro canal, outro formato). Cola o link direto na questão certa, sem precisar de playlist inteira."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        numero = st.number_input("Número da questão", min_value=1, max_value=200, value=136, key="avulso_numero")
    with col2:
        ano = st.number_input("Ano", min_value=2009, max_value=2100, value=2024, key="avulso_ano")
    with col3:
        caderno = st.text_input("Caderno", value=CADERNO_PADRAO, key="avulso_caderno")

    link = st.text_input("Link do vídeo", key="avulso_link")
    canal = st.text_input("Canal (opcional)", key="avulso_canal")

    if st.button("Ligar vídeo avulso", key="avulso_botao"):
        if not link:
            st.warning("Cola o link do vídeo primeiro.")
            return
        id_q = db.gerar_id_canonico(int(ano), caderno, int(numero))
        try:
            db.inserir_resolucao(id_q, "video", link, canal=canal or None)
        except ValueError as e:
            st.error(str(e))
        else:
            st.success(f"Vídeo ligado a `{id_q}`.")


def render_coletar_videos() -> None:
    render_video_avulso()
    st.divider()
    st.subheader("Coletar vídeos e ligar às questões")
    st.caption(
        "Cola o link/ID de uma playlist com resoluções individuais (uma questão por vídeo). "
        "Vídeos DIGITAL são ignorados automaticamente -- ainda não temos gabarito dessa aplicação."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        link_playlist = st.text_input("Link ou ID da playlist")
    with col2:
        caderno = st.text_input("Caderno", value=CADERNO_PADRAO, key="caderno_coletar_videos")

    if st.button("Buscar e ligar", type="primary"):
        if not link_playlist:
            st.warning("Cole um link ou ID primeiro.")
            return
        with st.spinner("Autenticando e buscando vídeos..."):
            youtube = coletor_youtube.autenticar_youtube()
            playlist_id = coletor_youtube.extrair_playlist_id(link_playlist)
            videos = coletor_youtube.buscar_todos_os_videos(youtube, playlist_id)
            resultado = processar_playlist(videos, caderno=caderno)

        st.success(
            f"{len(resultado['ligados'])} resolução(ões) ligada(s) | "
            f"{len(resultado['materia_atualizada'])} matéria(s) atualizada(s)"
        )

        if resultado["sem_questao"]:
            with st.expander(f"⚠️ {len(resultado['sem_questao'])} sem gabarito cadastrado ainda"):
                for r in resultado["sem_questao"]:
                    st.write(f"`{r['id_questao']}` — {r['titulo']}")

        if resultado["digital_ignorado"]:
            st.caption(f"{len(resultado['digital_ignorado'])} vídeo(s) DIGITAL ignorado(s) de propósito.")

        if resultado["materia_nao_extraida"]:
            with st.expander(f"⚠️ {len(resultado['materia_nao_extraida'])} vídeo(s) ligado(s) mas sem matéria extraída do título"):
                for r in resultado["materia_nao_extraida"]:
                    st.write(f"`{r['id_questao']}` — {r['titulo']}")

        if resultado["titulo_nao_reconhecido"]:
            with st.expander(f"⚠️ {len(resultado['titulo_nao_reconhecido'])} título(s) fora do padrão"):
                for t in resultado["titulo_nao_reconhecido"]:
                    st.write(t)