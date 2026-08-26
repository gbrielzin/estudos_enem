"""
coletar_videos.py — liga vídeo (ou texto) de resolução às questões do
enem.db. Não escreve em CSV nenhum -- é o substituto direto dos 4 modos
de coleta que existiam no app.py legado da raiz (playlist, lote, junção,
avulso), reescritos aqui pra gravar direto no banco.

Reaproveita autenticação e busca do main.py (mesma lógica testada da v1)
— não duplica isso aqui.

Um modo do legado ficou de fora de propósito: "busca automática" (busca
por palavra-chave, vários canais) existia pra minerar vídeos cujo texto
da descrição citasse um "nível de dificuldade" -- e dificuldade não é
mais um atributo salvo da questão aqui (ver o comentário de
normalizar_nivel() em db.py: ela é derivada do desempenho real do
usuário, não de opinião de vídeo). Sem esse conceito, a busca automática
não tem uma tradução direta pro modelo atual -- ficou só no app.py
legado, sem equivalente aqui.
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


def _extrair_numero_generico(texto: str):
    """Igual extrair_numero(), mas aceita 'Questão' sem exigir que seja
    o único número na string -- usado nas linhas coladas de um
    vídeo-resumo, que costumam vir como 'Questão 136;Probabilidade'."""
    return extrair_numero(texto)


def processar_lote_resumo(video_id: str, ano: int, canal: str, texto: str, caderno: str = CADERNO_PADRAO) -> dict:
    """Um vídeo-resumo cobre VÁRIAS questões de uma prova inteira de
    uma vez (ao contrário do modo playlist acima, que é 1 vídeo = 1
    questão) -- o mesmo link é ligado a cada questão mencionada.

    Formato esperado, uma linha por questão: 'Questão N;Matéria'. Um
    terceiro campo (nível) é aceito e ignorado por compatibilidade com
    o texto que a IA do YouTube já devolve nesse formato de 3 colunas
    -- dificuldade não é mais um atributo salvo da questão (ver
    TAXONOMIA_VALIDA/normalizar_nivel em db.py), só a matéria importa
    aqui. Ano vem de fora (um vídeo-resumo é sempre de UMA prova só) em
    vez de tentar extrair do texto colado, que não traz essa
    informação de forma confiável."""
    link = f"https://www.youtube.com/watch?v={video_id}"
    resultado = {"ligados": [], "materia_atualizada": [], "linha_invalida": [], "sem_questao": []}

    for linha in texto.strip().split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        partes = [p.strip() for p in linha.split(";")]
        if len(partes) < 2:
            resultado["linha_invalida"].append(linha)
            continue

        numero = _extrair_numero_generico(partes[0])
        materia = partes[1]
        if not numero or not materia:
            resultado["linha_invalida"].append(linha)
            continue

        id_q = db.gerar_id_canonico(ano, caderno, numero)
        try:
            db.inserir_resolucao(id_q, "video", link, canal=canal or None)
        except ValueError:
            resultado["sem_questao"].append(id_q)
            continue
        resultado["ligados"].append(id_q)

        with db._conectar() as conn:
            atual = conn.execute(
                "SELECT alternativa_correta, grande_area, status_classificacao "
                "FROM questoes WHERE id_questao=?", (id_q,)
            ).fetchone()
        if atual and atual[2] == "nao_classificado":
            gabarito_atual, grande_area_atual, _ = atual
            db.inserir_questao(
                ano=ano, caderno=caderno, numero=numero,
                grande_area=grande_area_atual, materia=materia,
                alternativa_correta=gabarito_atual, sobrescrever=True,
            )
            resultado["materia_atualizada"].append(id_q)

    return resultado


def processar_juncao(videos_playlist: list, ano: int, texto_resumo: str, caderno: str = CADERNO_PADRAO) -> dict:
    """Junta duas fontes da MESMA prova: uma playlist com o vídeo de
    RESOLUÇÃO INDIVIDUAL de cada questão (link real, um vídeo por
    questão) e um vídeo-resumo colado como texto (matéria de cada
    questão, sem link individual confiável). A chave de junção é o
    NÚMERO da questão -- por isso só serve pra UMA prova por vez, nunca
    misturando anos (daí o parâmetro ano vir de fora, explícito)."""
    videos_por_numero: dict[int, dict] = {}
    for video in videos_playlist:
        titulo = video["snippet"]["title"]
        video_id = video["snippet"]["resourceId"]["videoId"]
        canal = video["snippet"].get("videoOwnerChannelTitle", "")
        numero = extrair_numero(titulo)
        if numero:
            videos_por_numero[numero] = {
                "titulo": titulo,
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "canal": canal,
            }

    resultado = {"ligados": [], "materia_atualizada": [], "linha_invalida": [], "sem_video_individual": [], "sem_questao": []}

    for linha in texto_resumo.strip().split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        partes = [p.strip() for p in linha.split(";")]
        if len(partes) < 2:
            resultado["linha_invalida"].append(linha)
            continue

        numero = _extrair_numero_generico(partes[0])
        materia = partes[1]
        if not numero or not materia:
            resultado["linha_invalida"].append(linha)
            continue
        if numero not in videos_por_numero:
            resultado["sem_video_individual"].append(f"Questão {numero}")
            continue

        info = videos_por_numero[numero]
        id_q = db.gerar_id_canonico(ano, caderno, numero)
        try:
            db.inserir_resolucao(id_q, "video", info["link"], canal=info["canal"])
        except ValueError:
            resultado["sem_questao"].append(id_q)
            continue
        resultado["ligados"].append(id_q)

        with db._conectar() as conn:
            atual = conn.execute(
                "SELECT alternativa_correta, grande_area, status_classificacao "
                "FROM questoes WHERE id_questao=?", (id_q,)
            ).fetchone()
        if atual and atual[2] == "nao_classificado":
            gabarito_atual, grande_area_atual, _ = atual
            db.inserir_questao(
                ano=ano, caderno=caderno, numero=numero,
                grande_area=grande_area_atual, materia=materia,
                alternativa_correta=gabarito_atual, sobrescrever=True,
            )
            resultado["materia_atualizada"].append(id_q)

    return resultado


def render_lote_resumo() -> None:
    st.subheader("Colar um vídeo-resumo (várias questões, um vídeo só)")
    st.caption(
        "Pra quando um único vídeo comenta várias questões da mesma prova (ex: um vídeo-resumo "
        "gerado pela IA do YouTube). Formato por linha: Questão N;Matéria — o mesmo link é ligado a todas."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        video_id = st.text_input("ID do vídeo (depois de 'v=' no link)", key="lote_video_id")
    with col2:
        ano = st.number_input("Ano", min_value=2009, max_value=2100, value=2024, key="lote_ano")
    with col3:
        caderno = st.text_input("Caderno", value=CADERNO_PADRAO, key="lote_caderno")
    canal = st.text_input("Canal (opcional)", key="lote_canal")
    texto = st.text_area(
        "Cole as linhas aqui", height=200, key="lote_texto",
        placeholder="Questão 136;Probabilidade\nQuestão 137;Estatística",
    )

    if st.button("Processar lote", type="primary", key="lote_botao"):
        if not video_id or not texto.strip():
            st.warning("Preencha o ID do vídeo e cole ao menos uma linha.")
            return
        resultado = processar_lote_resumo(video_id, int(ano), canal, texto, caderno=caderno)
        st.success(
            f"{len(resultado['ligados'])} resolução(ões) ligada(s) | "
            f"{len(resultado['materia_atualizada'])} matéria(s) atualizada(s)"
        )
        if resultado["sem_questao"]:
            with st.expander(f"⚠️ {len(resultado['sem_questao'])} sem gabarito cadastrado ainda"):
                st.write(resultado["sem_questao"])
        if resultado["linha_invalida"]:
            with st.expander(f"⚠️ {len(resultado['linha_invalida'])} linha(s) fora do formato"):
                st.write(resultado["linha_invalida"])


def render_juncao() -> None:
    st.subheader("Juntar link real da resolução + matéria do vídeo-resumo")
    st.caption(
        "Pra quando a matéria vem de um vídeo-resumo, mas o link de cada questão está numa playlist "
        "separada com a resolução individual. Usa o NÚMERO da questão pra casar os dois — cole uma prova por vez."
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        link_playlist = st.text_input("Link ou ID da playlist com resoluções individuais", key="juncao_playlist")
    with col2:
        ano = st.number_input("Ano", min_value=2009, max_value=2100, value=2024, key="juncao_ano")
    caderno = st.text_input("Caderno", value=CADERNO_PADRAO, key="juncao_caderno")
    texto_resumo = st.text_area(
        "Cole as linhas do vídeo-resumo: Questão;Matéria", height=200, key="juncao_texto",
        placeholder="Questão 136;Probabilidade\nQuestão 137;Estatística",
    )

    if st.button("Fazer junção", type="primary", key="juncao_botao"):
        if not link_playlist or not texto_resumo.strip():
            st.warning("Cole o link da playlist e o texto do vídeo-resumo primeiro.")
            return
        with st.spinner("Buscando vídeos individuais..."):
            youtube = coletor_youtube.autenticar_youtube()
            playlist_id = coletor_youtube.extrair_playlist_id(link_playlist)
            videos = coletor_youtube.buscar_todos_os_videos(youtube, playlist_id)
            resultado = processar_juncao(videos, int(ano), texto_resumo, caderno=caderno)

        st.success(
            f"{len(resultado['ligados'])} resolução(ões) ligada(s) | "
            f"{len(resultado['materia_atualizada'])} matéria(s) atualizada(s)"
        )
        if resultado["sem_video_individual"]:
            with st.expander(f"⚠️ {len(resultado['sem_video_individual'])} sem vídeo individual correspondente na playlist"):
                st.write(resultado["sem_video_individual"])
        if resultado["sem_questao"]:
            with st.expander(f"⚠️ {len(resultado['sem_questao'])} sem gabarito cadastrado ainda"):
                st.write(resultado["sem_questao"])
        if resultado["linha_invalida"]:
            with st.expander(f"⚠️ {len(resultado['linha_invalida'])} linha(s) fora do formato"):
                st.write(resultado["linha_invalida"])


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
    render_lote_resumo()
    st.divider()
    render_juncao()
    st.divider()
    st.subheader("Coletar vídeos e ligar às questões (playlist)")
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