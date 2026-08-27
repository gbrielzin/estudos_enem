"""
importar_enem_dev.py — importa enunciado + alternativas + imagem via
a API pública enem.dev (https://docs.enem.dev), como alternativa ao
pipeline de PDF (extrair_enunciados_pdf.py / extrair_figuras_pdf.py)
pros anos que ela cobre. Confirmado por fetch direto: cobre 2009-2023
(2024 devolve 404 no momento em que isso foi escrito) -- 2024/2025
continuam exigindo o pipeline de PDF.

## Por que existe apesar do pipeline de PDF já funcionar

Validado à mão contra as duas questões mais difíceis que o pipeline de
PDF encontrou este ano (2020 azul): a 91 (tirinha do Garfield -- uma
FOTO de verdade, não vetor -- cluster_drawings() nunca teria como
achar isso, só existe como imagem embutida, não como traço) e a 93
(circuito elétrico, 5 alternativas em diagrama -- o bug de coluna que
extrair_figuras_pdf.py precisou de _duas_colunas_de_verdade() pra
corrigir). A API devolve as duas já com texto/imagem prontos e
corretos, gabarito batendo com o já carregado via
extrair_gabarito_pdf.py -- sem nenhuma das heurísticas frágeis daqui.

## Import só PREENCHE o que já existe, nunca cria questão nova

Só escreve enunciado_texto/enunciado_imagem_path (via
db.atualizar_enunciado(), mesma função dos outros dois scripts de
extração) pra questão que JÁ está no banco (gabarito oficial já
carregado) -- nunca insere questão nova nem mexe em matéria/gabarito/
tópico, porque o campo `discipline` da API só distingue área ampla
(ciencias-natureza/matematica), não a matéria específica (física,
química, ecologia...) que a taxonomia daqui usa; classificar matéria
continua sendo o fluxo de Triagem existente.

## Confirmação de numeração antes de gravar qualquer coisa

A API não documenta qual cor de caderno sua numeração (`index`) segue.
Em vez de assumir, _confirmar_caderno_azul() compara o
correctAlternative de cada questão contra o gabarito AZUL já
carregado localmente (sempre existe -- gabarito é NOT NULL) e só
segue adiante se pelo menos 90% baterem; year com confirmação baixa
aborta sem gravar nada, em vez de gravar enunciado sob o id_questao
errado silenciosamente.

## Filtro de área

Só considera discipline in ("ciencias-natureza", "matematica") -- o
escopo que este projeto rastreia; linguagens/ciencias-humanas vêm na
resposta da API mas são descartadas aqui.

## Imagem: contexto (1 arquivo) vs. alternativa-diagrama (até 5 arquivos)

Quando a figura é do ENUNCIADO (ex: questão 91, `files` preenchido),
baixa e usa direto. Quando são as ALTERNATIVAS que são imagem (ex:
questão 93, cada letra com seu próprio `file`), baixa todas e empilha
verticalmente numa imagem só via Pillow -- mesma limitação de schema
que extrair_figuras_pdf.py já tem (enunciado_imagem_path guarda 1
caminho, não uma lista por questão).

Uso: python importar_enem_dev.py <ano> [--aplicar] [--sobrescrever]
Sem --aplicar: só busca o JSON (leve) e imprime quantas questões
bateriam e por quê -- não baixa imagem nem grava nada no banco. Com
--aplicar: baixa as imagens e grava de verdade.
"""
import io
import re
import sys
import time
from pathlib import Path

import requests
from PIL import Image

import db
from extrair_enunciados_pdf import _AVISO_FIGURA

BASE_URL = "https://api.enem.dev/v1/exams"
AREAS_RASTREADAS = {"ciencias-natureza", "matematica"}
CADERNO = "azul"  # ver docstring: a API não documenta a cor, isso é o que _confirmar_caderno_azul() valida
LIMITE_PAGINA = 50
PAUSA_ENTRE_DOWNLOADS_S = 0.15
PASTA_ENUNCIADOS = Path(__file__).parent / "enunciados"

_PADRAO_IMAGEM_MARKDOWN = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def _get_com_retry(url: str, **kwargs) -> requests.Response:
    """Uma tentativa extra em cima de um 429 (rate limit) -- API
    pública e gratuita, sem SLA documentado; melhor esperar um pouco e
    tentar de novo do que abortar o import inteiro por um limite
    momentâneo."""
    resp = requests.get(url, timeout=30, **kwargs)
    if resp.status_code == 429:
        time.sleep(2)
        resp = requests.get(url, timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


def buscar_questoes(ano: int) -> list[dict]:
    """Todas as questões de um ano via paginação (limit/offset/
    hasMore). Deixa requests.HTTPError subir pro chamador -- um 404
    aqui significa que a API ainda não cobre esse ano (2024/2025, no
    momento em que isso foi escrito).

    Dedup por `index` de propósito: a paginação da API tem um bug de
    limite inclusivo -- confirmado buscando 2020 página por página, o
    último item de uma página (ex: índice 50 no offset=0..50) volta
    de novo como PRIMEIRO item da página seguinte (offset=50..100) --
    então toda fronteira de página (a cada LIMITE_PAGINA itens) vem
    duplicada. Inofensivo pro resultado final (atualizar_enunciado é
    idempotente), mas sem o dedup os relatórios/listas impressas
    mostram o mesmo id_questao repetido."""
    por_indice: dict[int, dict] = {}
    offset = 0
    while True:
        resp = _get_com_retry(f"{BASE_URL}/{ano}/questions", params={"limit": LIMITE_PAGINA, "offset": offset})
        corpo = resp.json()
        for q in corpo["questions"]:
            por_indice[q["index"]] = q
        if not corpo["metadata"]["hasMore"]:
            break
        offset += LIMITE_PAGINA
    return list(por_indice.values())


def _confirmar_caderno_azul(ano: int, questoes: list[dict]) -> tuple[int, int]:
    """(acertos, comparáveis) comparando correctAlternative da API
    contra alternativa_correta já carregada localmente pro caderno
    azul -- ver docstring do módulo."""
    acertos = comparaveis = 0
    for q in questoes:
        detalhe = db.detalhe_questao(db.gerar_id_canonico(ano, CADERNO, q["index"]))
        if detalhe is None:
            continue
        comparaveis += 1
        if detalhe["alternativa_correta"] == q["correctAlternative"]:
            acertos += 1
    return acertos, comparaveis


def montar_texto(q: dict) -> str:
    """Mesmo formato que extrair_enunciados_pdf.py produz (corpo,
    depois cada alternativa em 'LETRA texto' na própria linha, em
    ordem A-E) -- pra _separar_alternativas() em cartao_resposta.py
    funcionar igual não importa a origem do enunciado. Alternativa sem
    texto (é imagem, ex: questão 93) vira '(ver imagem)' pra continuar
    batendo com o padrão ^[A-E]\\s+(.+)$ que o parser exige."""
    contexto = _PADRAO_IMAGEM_MARKDOWN.sub("", q.get("context") or "").strip()
    partes = [contexto] if contexto else []
    if q.get("alternativesIntroduction"):
        partes.append(q["alternativesIntroduction"].strip())
    for alt in q["alternatives"]:
        texto_alt = (alt.get("text") or "").strip() or "(ver imagem)"
        partes.append(f"{alt['letter']} {texto_alt}")
    return "\n".join(p for p in partes if p)


def _baixar_imagem(url: str) -> Image.Image:
    resp = _get_com_retry(url)
    time.sleep(PAUSA_ENTRE_DOWNLOADS_S)
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def montar_imagem(q: dict) -> Image.Image | None:
    """Uma imagem só pra enunciado_imagem_path: o arquivo do contexto
    quando existe, ou as imagens de CADA alternativa empilhadas
    verticalmente quando é isso que é imagem -- nunca os dois casos ao
    mesmo tempo na prática (uma questão real não mistura figura no
    enunciado E alternativa-diagrama)."""
    arquivos_contexto = q.get("files") or []
    arquivos_alternativa = [alt["file"] for alt in q["alternatives"] if alt.get("file")]
    arquivos = arquivos_contexto or arquivos_alternativa
    if not arquivos:
        return None

    imagens = [_baixar_imagem(url) for url in arquivos]
    if len(imagens) == 1:
        return imagens[0]

    largura = max(img.width for img in imagens)
    altura_total = sum(img.height for img in imagens) + 8 * (len(imagens) - 1)
    composta = Image.new("RGB", (largura, altura_total), "white")
    y = 0
    for img in imagens:
        composta.paste(img, (0, y))
        y += img.height + 8
    return composta


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_enem_dev.py <ano> [--aplicar] [--sobrescrever]")
        sys.exit(1)

    ano = int(sys.argv[1])
    aplicar = "--aplicar" in sys.argv
    sobrescrever = "--sobrescrever" in sys.argv

    try:
        todas = buscar_questoes(ano)
    except requests.HTTPError as e:
        print(f"Erro buscando o ano {ano} na API (talvez esse ano ainda não esteja coberto): {e}")
        sys.exit(1)

    questoes = [q for q in todas if q.get("discipline") in AREAS_RASTREADAS]
    print(f"{len(questoes)}/{len(todas)} questão(ões) em {sorted(AREAS_RASTREADAS)} pro ano {ano}.")

    acertos, comparaveis = _confirmar_caderno_azul(ano, questoes)
    if comparaveis == 0:
        print(f"Nenhuma questão de {ano} existe no banco (caderno {CADERNO}) pra confirmar a numeração -- carregue o gabarito oficial primeiro (extrair_gabarito_pdf.py). Nada foi gravado.")
        sys.exit(1)
    taxa = acertos / comparaveis
    print(f"Confirmação de numeração (gabarito API x gabarito oficial já carregado): {acertos}/{comparaveis} ({taxa:.0%}).")
    if taxa < 0.9:
        print(f"Taxa de confirmação baixa demais pra confiar que a API segue a numeração do caderno {CADERNO} em {ano}. Abortando -- nada foi gravado.")
        sys.exit(1)

    destino_relatorio = Path(__file__).parent / f"scratch_enunciados_{ano}_{CADERNO}_apidev.txt"
    with destino_relatorio.open("w", encoding="utf-8") as f:
        for q in sorted(questoes, key=lambda q: q["index"]):
            f.write(f"=== Questão {q['index']} ===\n{montar_texto(q)}\n\n")
    print(f"Relatório de revisão: {destino_relatorio}")

    if not aplicar:
        print("Modo revisão (sem --aplicar) -- confere o relatório acima antes de aplicar; nada foi gravado no banco nem baixado.")
        sys.exit(0)

    PASTA_ENUNCIADOS.mkdir(exist_ok=True)
    aplicadas, so_imagem, ja_preenchidas, nao_encontradas, falhas_imagem = 0, 0, [], [], []

    for q in sorted(questoes, key=lambda q: q["index"]):
        id_questao = db.gerar_id_canonico(ano, CADERNO, q["index"])
        detalhe = db.detalhe_questao(id_questao)
        if detalhe is None:
            nao_encontradas.append(id_questao)
            continue

        tem_arquivo = bool(q.get("files")) or any(alt.get("file") for alt in q["alternatives"])
        # Texto já preenchido (pelo pipeline de PDF, por exemplo) não
        # significa que a IMAGEM também está -- ex: questão 91 (tirinha
        # do Garfield) já tinha texto extraído do PDF, mas nenhuma
        # imagem, porque é uma foto embutida, não um traço vetorial que
        # cluster_drawings() teria como achar. Sem esse caso à parte,
        # "já tem enunciado_texto" pularia a questão inteira e nunca
        # preencheria essa imagem que só a API consegue dar.
        falta_so_imagem = bool(detalhe["enunciado_texto"]) and not detalhe["enunciado_imagem_path"] and tem_arquivo
        if detalhe["enunciado_texto"] and not falta_so_imagem and not sobrescrever:
            ja_preenchidas.append(id_questao)
            continue

        # Decide o download ANTES de mexer no texto -- se a imagem
        # falhar, uma incerteza que o texto já sinalizava (aviso de
        # figura) não pode ser removida como se tivesse sido resolvida.
        caminho_imagem = None
        download_falhou = False
        if tem_arquivo:
            try:
                imagem = montar_imagem(q)
                caminho_imagem = str(PASTA_ENUNCIADOS / f"{id_questao}.png")
                imagem.save(caminho_imagem)
            except (requests.RequestException, OSError):
                falhas_imagem.append(id_questao)
                download_falhou = True

        if falta_so_imagem and not sobrescrever:
            # Preserva o texto (já validado) -- só tira o aviso de
            # "pode faltar figura" do extrair_enunciados_pdf.py se
            # estiver lá E a imagem realmente baixou agora, porque é
            # isso que resolve a incerteza que o aviso sinalizava.
            texto_existente = detalhe["enunciado_texto"]
            if not download_falhou and texto_existente.startswith(_AVISO_FIGURA):
                texto = texto_existente.removeprefix(_AVISO_FIGURA)
            else:
                texto = None
        else:
            texto = montar_texto(q)
            if download_falhou:
                texto = "⚠️ Esta questão tem imagem na API que falhou ao baixar -- confere manualmente.\n\n" + texto

        db.atualizar_enunciado(id_questao, texto=texto, imagem_path=caminho_imagem)
        aplicadas += 1
        if falta_so_imagem and not sobrescrever:
            so_imagem += 1

    print(f"{aplicadas} questão(ões) gravada(s) via atualizar_enunciado() ({so_imagem} delas só a imagem, texto já existia).")
    if ja_preenchidas:
        print(f"{len(ja_preenchidas)} já tinham enunciado completo (texto + imagem, se precisava) e foram puladas (rode com --sobrescrever pra forçar): {ja_preenchidas}")
    if nao_encontradas:
        print(f"{len(nao_encontradas)} não existe(m) no banco (gabarito ainda não carregado pra esse caderno): {nao_encontradas}")
    if falhas_imagem:
        print(f"{len(falhas_imagem)} tiveram a imagem marcada com aviso por falha de download -- roda de novo com --sobrescrever pra tentar essas de novo: {falhas_imagem}")
