import os
import re
import csv
import json
from collections import Counter
from dotenv import load_dotenv
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

# --- Arquivos de persistência ---
CAMINHO_CSV = "questoes_enem_classificadas.csv"
CAMINHO_TABELA_PROBABILIDADES = "tabela_probabilidades.json"

# Regex final, tolerante a variações de escrita já observadas no canal
PADRAO_NIVEL = re.compile(
    r"Nível d[ae]\s+(?:questão|dificuldade):\s*(\w+)",
    re.IGNORECASE
)


# ============================================================
# BLOCO 1: AUTENTICAÇÃO
# ============================================================

def autenticar_youtube():
    """Carrega a API Key do Streamlit secrets primeiro (é onde ela mora
    num deploy na nuvem, tipo Streamlit Community Cloud -- lá não existe
    .env), com fallback pro .env local. Mesmo código funciona rodando
    na sua máquina ou deployado, sem precisar de dois caminhos
    diferentes no resto do projeto."""
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("YOUTUBE_API_KEY")
    except Exception:
        pass  # sem secrets.toml (normal rodando local) -- cai pro .env

    if not api_key:
        load_dotenv(override=True)  # garante que o .env do projeto sempre vence
        api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise ValueError("API Key não encontrada. Verifique seu .env (local) ou os Secrets do app (nuvem).")

    return build("youtube", "v3", developerKey=api_key)


# ============================================================
# BLOCO 2: UTILITÁRIOS DE EXTRAÇÃO
# ============================================================

def extrair_playlist_id(link_ou_id: str) -> str:
    """Aceita link completo ou ID puro da playlist."""
    if "youtube.com" in link_ou_id:
        parsed_url = urlparse(link_ou_id)
        query_params = parse_qs(parsed_url.query)
        playlist_id = query_params.get("list", [None])[0]
        if not playlist_id:
            raise ValueError("Não encontrei o parâmetro 'list' nessa URL. Confira o link.")
        return playlist_id
    return link_ou_id


def extrair_materia(titulo: str) -> str | None:
    """Espera o padrão: 'Questão X - Caderno Azul | Matéria | MATEMÁTICA ENEM ANO'"""
    partes = titulo.split("|")
    if len(partes) >= 2:
        return partes[1].strip()
    return None


def extrair_numero_questao(texto: str) -> str | None:
    """Extrai o número da questão de qualquer texto que contenha 'Questão N'.
    É a CHAVE DE JUNÇÃO entre a playlist de resoluções individuais e o
    vídeo-resumo de dificuldades — os dois falam da mesma questão, só
    identificada pelo número."""
    match = re.search(r"Quest[ãa]o\s+(\d+)", texto, re.IGNORECASE)
    return match.group(1) if match else None


# ============================================================
# BLOCO 3: COLETA VIA PLAYLIST (MODO MANUAL)
# ============================================================

def buscar_todos_os_videos(youtube, playlist_id: str) -> list:
    """Percorre todas as páginas da playlist usando nextPageToken."""
    todos_os_videos = []
    proximo_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=proximo_token
        )
        response = request.execute()
        todos_os_videos.extend(response.get("items", []))
        proximo_token = response.get("nextPageToken")
        print(f"Coletados até agora: {len(todos_os_videos)} vídeos...")
        if not proximo_token:
            break

    return todos_os_videos


def processar_videos(videos: list) -> list[dict]:
    """Usa SOMENTE dados confirmados (regex bate na descrição). Formato playlistItems.list()."""
    resultado = []
    for video in videos:
        titulo = video["snippet"]["title"]
        descricao = video["snippet"]["description"]
        video_id = video["snippet"]["resourceId"]["videoId"]
        canal_titulo = video["snippet"].get("videoOwnerChannelTitle", "")
        canal_id = video["snippet"].get("videoOwnerChannelId", "")

        match = PADRAO_NIVEL.search(descricao)
        if not match:
            print(f"⚠️  Ignorado (sem nível): {titulo}")
            continue

        resultado.append({
            "titulo": titulo,
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "nivel": match.group(1).capitalize(),
            "materia": extrair_materia(titulo),
            "fonte_nivel": "confirmado",
            "canal": canal_titulo,
            "canal_id": canal_id
        })
    return resultado


def processar_videos_com_inferencia(videos: list, tabela_probabilidades: dict) -> list[dict]:
    """Usa a descrição quando existir; senão, estima pela tabela de matérias."""
    resultado = []
    for video in videos:
        titulo = video["snippet"]["title"]
        descricao = video["snippet"]["description"]
        video_id = video["snippet"]["resourceId"]["videoId"]
        canal_titulo = video["snippet"].get("videoOwnerChannelTitle", "")
        canal_id = video["snippet"].get("videoOwnerChannelId", "")
        materia = extrair_materia(titulo)

        match = PADRAO_NIVEL.search(descricao)

        if match:
            nivel, fonte = match.group(1).capitalize(), "confirmado"
        elif materia and materia in tabela_probabilidades:
            info = tabela_probabilidades[materia]
            if info["amostras"] < 5:
                print(f"⚠️  Amostra insuficiente para '{materia}' ({info['amostras']}). Pulando: {titulo}")
                continue
            nivel, fonte = info["nivel_estimado"], "inferido"
        else:
            print(f"⚠️  Sem nível nem matéria conhecida: {titulo}")
            continue

        resultado.append({
            "titulo": titulo,
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "nivel": nivel,
            "materia": materia,
            "fonte_nivel": fonte,
            "canal": canal_titulo,
            "canal_id": canal_id
        })
    return resultado


# ============================================================
# BLOCO 4: COLETA VIA BUSCA (MODO AUTOMATIZADO)
# ============================================================

def buscar_videos_por_palavra_chave(youtube, query: str, max_resultados: int = 25, canal_id: str = None) -> list:
    """search.list custa 100 unidades de cota por chamada — usar com moderação."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": min(max_resultados, 50),
        "relevanceLanguage": "pt",
    }
    if canal_id:
        params["channelId"] = canal_id

    request = youtube.search().list(**params)
    response = request.execute()
    return response.get("items", [])


def buscar_detalhes_dos_videos(youtube, video_ids: list) -> list:
    """videos.list devolve a descrição completa (search.list trunca)."""
    if not video_ids:
        return []
    ids_formatados = ",".join(video_ids)
    request = youtube.videos().list(part="snippet", id=ids_formatados)
    response = request.execute()
    return response.get("items", [])


def processar_videos_busca(videos_detalhados: list) -> list[dict]:
    """Formato de videos.list() é ligeiramente diferente de playlistItems.list()."""
    resultado = []
    for video in videos_detalhados:
        titulo = video["snippet"]["title"]
        descricao = video["snippet"]["description"]
        video_id = video["id"]
        canal_titulo = video["snippet"]["channelTitle"]
        canal_id = video["snippet"]["channelId"]

        match = PADRAO_NIVEL.search(descricao)
        if not match:
            continue

        resultado.append({
            "titulo": titulo,
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "nivel": match.group(1).capitalize(),
            "materia": extrair_materia(titulo),
            "fonte_nivel": "confirmado",
            "canal": canal_titulo,
            "canal_id": canal_id
        })
    return resultado


def expandir_amostra_via_busca(youtube, queries: list[str]) -> list[dict]:
    """Roda múltiplas buscas, junta resultados e filtra vídeos com nível confirmado."""
    todos_video_ids = set()

    for query in queries:
        print(f"🔎 Buscando: '{query}'...")
        resultados = buscar_videos_por_palavra_chave(youtube, query)
        for item in resultados:
            todos_video_ids.add(item["id"]["videoId"])

    print(f"\nTotal de vídeos únicos encontrados: {len(todos_video_ids)}")
    print("Buscando descrições completas...")

    detalhes = buscar_detalhes_dos_videos(youtube, list(todos_video_ids))
    dados = processar_videos_busca(detalhes)

    print(f"Vídeos com nível de dificuldade confirmado: {len(dados)}")
    return dados


# ============================================================
# BLOCO 5: TABELA DE PROBABILIDADES (INFERÊNCIA)
# ============================================================

def construir_tabela_probabilidades(dados_com_nivel: list[dict]) -> dict:
    materias_por_nivel = {}
    for item in dados_com_nivel:
        if item["materia"]:
            materias_por_nivel.setdefault(item["materia"], []).append(item["nivel"])

    tabela = {}
    for materia, niveis in materias_por_nivel.items():
        nivel_mais_comum, frequencia = Counter(niveis).most_common(1)[0]
        tabela[materia] = {
            "nivel_estimado": nivel_mais_comum,
            "confianca_percentual": round(frequencia / len(niveis) * 100, 1),
            "amostras": len(niveis)
        }
    return tabela


def salvar_tabela_probabilidades(tabela: dict):
    with open(CAMINHO_TABELA_PROBABILIDADES, "w", encoding="utf-8") as f:
        json.dump(tabela, f, indent=2, ensure_ascii=False)
    print(f"Tabela de probabilidades salva em: {CAMINHO_TABELA_PROBABILIDADES}")


def carregar_tabela_probabilidades() -> dict:
    if not os.path.exists(CAMINHO_TABELA_PROBABILIDADES):
        return {}
    with open(CAMINHO_TABELA_PROBABILIDADES, "r", encoding="utf-8") as f:
        return json.load(f)


def atualizar_tabela_com_novos_dados(dados_confirmados: list[dict]):
    """Recalcula a tabela combinando o que já existia com os dados novos confirmados."""
    tabela_atual = carregar_tabela_probabilidades()
    nova_tabela = construir_tabela_probabilidades(dados_confirmados)
    tabela_atual.update(nova_tabela)
    salvar_tabela_probabilidades(tabela_atual)


# ============================================================
# BLOCO 6: EXPORTAÇÃO COM PROTEÇÃO CONTRA DUPLICADOS
# ============================================================

def carregar_chaves_existentes() -> set:
    """Chave de unicidade = (link, título). Usar só o link não é suficiente
    porque, no modo lote, várias questões diferentes vêm do MESMO vídeo
    (mesmo link) — precisamos diferenciar pelo título também."""
    if not os.path.exists(CAMINHO_CSV):
        return set()
    with open(CAMINHO_CSV, "r", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        return {(linha["link"], linha["titulo"]) for linha in leitor}


def exportar_csv(dados: list[dict]):
    if not dados:
        print("Nada para exportar.")
        return

    chaves_existentes = carregar_chaves_existentes()
    dados_novos = [d for d in dados if (d["link"], d["titulo"]) not in chaves_existentes]
    duplicados = len(dados) - len(dados_novos)

    if not dados_novos:
        print(f"Nada novo para adicionar. ({duplicados} já existiam no CSV)")
        return

    arquivo_ja_existe = os.path.exists(CAMINHO_CSV)
    colunas = dados_novos[0].keys()

    with open(CAMINHO_CSV, mode="a", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        if not arquivo_ja_existe:
            escritor.writeheader()
        escritor.writerows(dados_novos)

    print(f"Adicionados: {len(dados_novos)} | Ignorados (duplicados): {duplicados}")


# ============================================================
# BLOCO 7: ENTRADA MANUAL (FONTES NÃO-AUTOMATIZÁVEIS)
# ============================================================

def adicionar_manual(titulo: str, video_id: str, nivel: str, materia: str, canal: str = ""):
    """Adiciona um único registro manualmente (ex: dados extraídos do painel de IA
    do YouTube, comentários, ou qualquer fonte que não dá pra buscar via API),
    respeitando o mesmo formato e proteção contra duplicados do restante do sistema."""
    registro = {
        "titulo": titulo,
        "link": f"https://www.youtube.com/watch?v={video_id}",
        "nivel": nivel.capitalize(),
        "materia": materia,
        "fonte_nivel": "confirmado_transcricao_ia",
        "canal": canal,
        "canal_id": ""
    }
    exportar_csv([registro])


# ============================================================
# MODOS DE EXECUÇÃO
# ============================================================

def modo_manual(youtube):
    tem_rotulo = input("Essa playlist tem 'Nível de dificuldade' na descrição? (s/n): ").strip().lower()
    link_usuario = input("Cole o link (ou ID) da playlist do YouTube: ").strip()
    playlist_id = extrair_playlist_id(link_usuario)

    videos = buscar_todos_os_videos(youtube, playlist_id)

    if tem_rotulo == "s":
        dados = processar_videos(videos)
        atualizar_tabela_com_novos_dados(dados)
    else:
        tabela = carregar_tabela_probabilidades()
        if not tabela:
            print("⚠️  Ainda não existe tabela de probabilidades treinada.")
        dados = processar_videos_com_inferencia(videos, tabela)

    exportar_csv(dados)


def modo_automatico(youtube):
    queries_texto = input(
        "Digite as queries de busca separadas por ';' (ex: questão enem matemática nível de dificuldade): "
    ).strip()
    queries = [q.strip() for q in queries_texto.split(";") if q.strip()]

    if not queries:
        print("Nenhuma query informada.")
        return

    dados = expandir_amostra_via_busca(youtube, queries)
    atualizar_tabela_com_novos_dados(dados)
    exportar_csv(dados)


def modo_manual_individual():
    """Adiciona registros um por um, digitados na hora (ex: dados vistos no
    painel de IA do YouTube). Digite 'sair' no título para encerrar."""
    print("\n--- Entrada manual de registros ---")
    print("(digite 'sair' no título a qualquer momento para encerrar)\n")

    while True:
        titulo = input("Título do vídeo/questão: ").strip()
        if titulo.lower() == "sair":
            break

        video_id = input("ID do vídeo (o código depois de 'v=' no link): ").strip()
        nivel = input("Nível (Fácil/Média/Difícil): ").strip()
        materia = input("Matéria/assunto: ").strip()
        canal = input("Canal (opcional, aperte Enter para pular): ").strip()

        adicionar_manual(titulo, video_id, nivel, materia, canal)
        print()  # linha em branco para separar visualmente o próximo registro


def modo_juncao(youtube):
    """
    Junta duas fontes da MESMA prova:
    1. Uma playlist com o vídeo de resolução INDIVIDUAL de cada questão (link real)
    2. Um vídeo-resumo com a dificuldade de cada questão falada em voz alta (via IA)

    A junção usa o NÚMERO DA QUESTÃO como chave — por isso só deve ser usado
    com uma prova de cada vez, nunca misturando anos/cadernos diferentes.
    """
    print("\n--- Junção: link real + nível do vídeo-resumo ---")
    print("(use isso com UMA prova por vez — não misture anos diferentes)\n")

    link_playlist = input("Cole o link (ou ID) da playlist com as resoluções individuais: ").strip()
    playlist_id = extrair_playlist_id(link_playlist)

    videos = buscar_todos_os_videos(youtube, playlist_id)

    # Monta um dicionário: número da questão -> dados do vídeo individual (com link real)
    videos_por_numero = {}
    for video in videos:
        titulo = video["snippet"]["title"]
        video_id = video["snippet"]["resourceId"]["videoId"]
        canal_titulo = video["snippet"].get("videoOwnerChannelTitle", "")
        canal_id = video["snippet"].get("videoOwnerChannelId", "")

        numero = extrair_numero_questao(titulo)
        if not numero:
            continue

        videos_por_numero[numero] = {
            "titulo": titulo,
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "canal": canal_titulo,
            "canal_id": canal_id
        }

    print(f"{len(videos_por_numero)} vídeos individuais mapeados por número de questão.\n")

    print(
        "Agora cole as linhas do vídeo-resumo no formato Questão;Matéria;Nível\n"
        "(uma por linha). Deixe uma linha em branco e aperte Enter para terminar.\n"
    )

    linhas = []
    while True:
        linha = input()
        if linha.strip() == "":
            break
        linhas.append(linha)

    registros = []
    nao_encontrados = []

    for linha in linhas:
        partes = [p.strip() for p in linha.split(";")]
        if len(partes) != 3:
            print(f"⚠️  Linha ignorada (formato inválido): {linha}")
            continue

        titulo_lote, materia, nivel = partes
        numero = extrair_numero_questao(titulo_lote)

        if not numero or numero not in videos_por_numero:
            nao_encontrados.append(titulo_lote)
            continue

        info = videos_por_numero[numero]
        registros.append({
            "titulo": info["titulo"],           # título REAL do vídeo individual
            "link": info["link"],                 # link REAL, único por questão
            "nivel": nivel.capitalize(),          # dificuldade vinda da IA/transcrição
            "materia": materia,
            "fonte_nivel": "confirmado_transcricao_ia",
            "canal": info["canal"],
            "canal_id": info["canal_id"]
        })

    exportar_csv(registros)

    if nao_encontrados:
        print(f"\n⚠️  {len(nao_encontrados)} questões do vídeo-resumo sem vídeo individual correspondente:")
        for item in nao_encontrados:
            print(f"   - {item}")


def modo_manual_lote():
    """Recebe várias questões de UM MESMO vídeo-resumo de uma vez, coladas em
    lote no formato 'Questão;Matéria;Nível' (uma por linha) — pensado para
    colar diretamente a saída da IA do YouTube (Gemini) sem digitar uma por uma."""
    print("\n--- Entrada em lote (1 vídeo-resumo, várias questões) ---")

    video_id = input("ID do vídeo (o código depois de 'v=' no link): ").strip()
    canal = input("Canal (opcional, aperte Enter para pular): ").strip()

    print(
        "\nCole as linhas no formato: Questão;Matéria;Nível (uma por linha).\n"
        "Peça à IA do YouTube nesse formato exato. Quando terminar, deixe uma linha em branco e aperte Enter.\n"
    )

    linhas = []
    while True:
        linha = input()
        if linha.strip() == "":
            break
        linhas.append(linha)

    if not linhas:
        print("Nenhuma linha recebida.")
        return

    registros_validos = 0
    registros_invalidos = 0

    for linha in linhas:
        partes = [p.strip() for p in linha.split(";")]
        if len(partes) != 3:
            print(f"⚠️  Linha ignorada (formato inválido, esperado 3 campos): {linha}")
            registros_invalidos += 1
            continue

        titulo, materia, nivel = partes
        adicionar_manual(titulo, video_id, nivel, materia, canal)
        registros_validos += 1

    print(f"\nProcessadas: {registros_validos} | Inválidas: {registros_invalidos}")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    youtube = autenticar_youtube()

    print("\n--- Coletor de Questões ENEM ---")
    print("1. Modo manual (colar link de uma playlist específica)")
    print("2. Modo automático (buscar por palavra-chave em vários canais)")
    print("3. Entrada manual de registros, um por um")
    print("4. Entrada em lote (colar várias questões de um vídeo-resumo de uma vez)")
    print("5. Junção: link real da resolução individual + nível do vídeo-resumo")
    escolha = input("Escolha o modo (1/2/3/4/5): ").strip()

    if escolha == "1":
        modo_manual(youtube)
    elif escolha == "2":
        modo_automatico(youtube)
    elif escolha == "3":
        modo_manual_individual()
    elif escolha == "4":
        modo_manual_lote()
    elif escolha == "5":
        modo_juncao(youtube)
    else:
        print("Opção inválida.")