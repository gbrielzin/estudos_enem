"""
extrair_figuras_pdf.py — recorta a FIGURA/GRÁFICO/TABELA de cada
questão (quando existe) direto do PDF oficial do INEP, usando
page.cluster_drawings() (nativo da PyMuPDF -- agrupa os traços
vetoriais próximos num retângulo, sem precisar de nenhum serviço
externo nem modelo de ML). Complementa extrair_enunciados_pdf.py, que
só cobre o TEXTO -- esse aqui cobre exatamente os ~40% de questões que
o outro script sinaliza com ⚠️ por citar figura/gráfico/tabela sem
conseguir extraí-la.

Validado manualmente contra um PDF real (2020 azul, 32 páginas) antes
de virar código de produção: dos recortes plausíveis (2%-70% da área
da página), a esmagadora maioria era mesmo diagrama/gráfico/tabela de
verdade (conferido abrindo os PNGs um por um) -- o único falso
positivo era o logo "enem2020" da contracapa, uma página sem nenhum
"Questão N" e com pouquíssimo texto (código de barras + cabeçalho),
o que a checagem de MIN_TEXTO_PAGINA abaixo já descarta. Mesmo assim,
uma rodada real pegou um caso mais sério que a checagem PNG-por-PNG
não capturou de primeira -- ver _duas_colunas_de_verdade abaixo -- que
não era "figura faltando" (inofensivo, já tem o aviso ⚠️ de
extrair_enunciados_pdf.py) e sim "figura da questão ERRADA" (silencioso
e enganoso); qualquer prova nova rodada por este script vale uma
segunda conferida pontual antes de confiar de olhos fechados,
principalmente em questão com alternativa em forma de diagrama (física
com circuito, química com estrutura molecular).

## Como associa recorte -> questão

O ENEM imprime em 2 colunas por página, várias questões por página.
page.get_text() já reconstrói a ordem de leitura correta (esquerda de
cima a baixo, depois direita de cima a baixo -- confirmado em
extrair_enunciados_pdf.py), mas cluster_drawings() devolve só
retângulos soltos, sem saber "isso pertence à questão X". Pra ligar um
no outro: acha a posição de cada marcador "Questão N" na página via
page.search_for() (retorna o retângulo exato do texto), define uma
chave de leitura (coluna, y0) pra marcador E pra cluster -- coluna 0
(esquerda) sempre vem antes da coluna 1 (direita), dentro da mesma
coluna ordena por y0 -- e atribui cada cluster ao ÚLTIMO marcador cuja
chave antecede a dele. Cluster sem nenhum marcador antes dele NA
MESMA página herda a questão corrente (a última vista, de uma página
anterior) -- necessário porque uma figura grande às vezes desliza pro
topo da página seguinte -- mas só em página com conteúdo real
(ver MIN_TEXTO_PAGINA); página de capa/divisória não herda nada, pra
não grudar o cluster errado na última questão da página anterior.

EXCEÇÃO descoberta numa questão real (93 do 2020 azul, física de
circuito elétrico): quando as 5 alternativas são desenho (não texto),
o INEP às vezes imprime a questão INTEIRA usando a largura da página
toda em vez de respeitar a coluna esquerda/direita do texto corrido --
2 das 5 imagens ficavam no lado "direito" mesmo a questão sendo só
coluna esquerda. Como a chave (coluna, y0) trata qualquer coisa da
coluna 1 como "depois de tudo" da coluna 0, essas 2 imagens grudavam
na QUESTÃO SEGUINTE (cujo marcador também é coluna esquerda, só que
mais abaixo) em vez de ficar na 93 -- um recorte incompleto numa
questão e um recorte com a figura ERRADA na outra, sem aviso nenhum.
_duas_colunas_de_verdade() detecta isso olhando só os marcadores
"Questão N" da própria página: se todos caem na mesma coluna, não
existe uma coluna 2 de verdade AQUI, então a atribuição usa y0 puro
(_chave_pagina_unica) em vez de (coluna, y0) -- se os marcadores usam
as duas colunas de verdade (o normal), mantém (coluna, y0)
(_chave_leitura) como antes.

Questão com mais de um cluster na MESMA página vira um recorte só (uni
ão dos retângulos). Questão cujos clusters caem em páginas DIFERENTES
(caso raro) fica só com o grupo de maior área total -- o schema atual
(questoes.enunciado_imagem_path) guarda um caminho só por questão, não
uma lista.

Uso: python extrair_figuras_pdf.py <arquivo.pdf> <ano> <caderno> [--aplicar] [--sobrescrever]
Sem --aplicar: só gera os PNGs em core/enunciados/ e imprime um
relatório -- não grava nada no banco (mesma convenção de
extrair_enunciados_pdf.py). Com --aplicar: além de gerar os PNGs,
grava o caminho em enunciado_imagem_path via db.atualizar_enunciado()
pra cada questão que existe no banco (ano/caderno/numero).
"""
import re
import sys
from pathlib import Path

import pymupdf

import db

_PADRAO_QUESTAO = re.compile(r"Questão\s+(\d+)\s*\n")
_AREA_MINIMA_PCT = 2.0
_AREA_MAXIMA_PCT = 70.0
_MIN_TEXTO_PAGINA = 200  # abaixo disso, página não tem questão de verdade (capa/contracapa/divisória)
_MARGEM_PT = 4  # folga em volta do retângulo detectado, pra não cortar rente à borda da figura

PASTA_ENUNCIADOS = Path(__file__).parent / "enunciados"


def _coluna(rect: pymupdf.Rect, largura_pagina: float) -> int:
    return 0 if rect.x0 < largura_pagina / 2 else 1


def _chave_leitura(rect: pymupdf.Rect, largura_pagina: float) -> tuple[int, float]:
    """(coluna, y0) -- coluna 0 (esquerda) sempre ordena antes da 1
    (direita), reproduzindo a ordem de leitura de duas colunas do ENEM
    sem precisar reconstruir o layout inteiro feito pelo PyMuPDF."""
    return (_coluna(rect, largura_pagina), rect.y0)


def _chave_pagina_unica(rect: pymupdf.Rect, largura_pagina: float) -> tuple[int, float]:
    """Mesma forma de tupla de _chave_leitura, mas ignorando coluna --
    pra página onde o conteúdo usa a largura toda em vez do layout de
    duas colunas (ver _duas_colunas_de_verdade)."""
    return (0, rect.y0)


def _duas_colunas_de_verdade(marcos: list[tuple[int, pymupdf.Rect]], largura_pagina: float) -> bool:
    """Uma questão cujas 5 alternativas são diagrama (não texto) às
    vezes usa a largura DA PÁGINA TODA pro grid de imagens, em vez de
    respeitar a coluna esquerda/direita do texto corrido -- confirmado
    numa prova real (questão 93 do 2020 azul, circuito elétrico): duas
    das cinco imagens ficam no lado direito da página mesmo a questão
    inteira sendo só coluna esquerda, e como a chave (coluna, y0) trata
    QUALQUER coisa da coluna 1 como "depois" de qualquer coisa da
    coluna 0, essas duas imagens eram atribuídas à streamlit PRÓXIMA
    questão (cujo marcador também está na coluna 0, mas mais abaixo) em
    vez da questão 93 -- um recorte incompleto numa questão e um
    recorte de conteúdo ERRADO na outra.

    Sinal usado pra distinguir os dois casos: se os marcadores "Questão
    N" que aparecem NESTA página usam as duas colunas (o normal — uma
    questão começa na esquerda, a próxima na direita), o layout de duas
    colunas É real, então usa _chave_leitura. Se todos os marcadores
    desta página caem na MESMA coluna, não existe uma "coluna 2" de
    verdade aqui -- qualquer cluster do lado direito é só a figura
    ocupando a largura toda, então usa y0 puro (_chave_pagina_unica)."""
    colunas_dos_marcos = {_coluna(rect, largura_pagina) for _, rect in marcos}
    return len(colunas_dos_marcos) > 1


def localizar_clusters(caminho: str) -> dict[int, list[tuple[int, pymupdf.Rect]]]:
    """{numero_questao: [(indice_pagina, retangulo), ...]} -- um ou
    mais recortes candidatos por questão, ainda não unificados nem
    salvos (ver _consolidar). Só leitura, não grava nada em disco."""
    doc = pymupdf.open(caminho)
    por_questao: dict[int, list[tuple[int, pymupdf.Rect]]] = {}
    questao_atual = None
    ignorados = []

    for indice_pagina in range(len(doc)):
        pagina = doc[indice_pagina]
        texto_pagina = pagina.get_text()
        largura_pagina = pagina.rect.width

        if len(texto_pagina.strip()) < _MIN_TEXTO_PAGINA:
            # Capa/contracapa/divisória -- não tem questão de verdade,
            # não herda estado da página anterior nem aceita cluster.
            continue

        marcos = []
        for numero_str in _PADRAO_QUESTAO.findall(texto_pagina):
            numero = int(numero_str)
            ocorrencias = pagina.search_for(f"Questão {numero}")
            if ocorrencias:
                marcos.append((numero, ocorrencias[0]))

        chave = _chave_leitura if _duas_colunas_de_verdade(marcos, largura_pagina) else _chave_pagina_unica

        area_pagina = pagina.rect.width * pagina.rect.height
        for rect in pagina.cluster_drawings():
            area_pct = (rect.width * rect.height) / area_pagina * 100
            if not (_AREA_MINIMA_PCT < area_pct < _AREA_MAXIMA_PCT):
                continue
            chave_cluster = chave(rect, largura_pagina)
            anteriores = [
                (numero, marco_rect) for numero, marco_rect in marcos
                if chave(marco_rect, largura_pagina) <= chave_cluster
            ]
            if anteriores:
                dono = max(anteriores, key=lambda par: chave(par[1], largura_pagina))[0]
            elif questao_atual is not None:
                dono = questao_atual
            else:
                ignorados.append((indice_pagina + 1, rect))
                continue
            por_questao.setdefault(dono, []).append((indice_pagina, rect))

        if marcos:
            questao_atual = marcos[-1][0]

    if ignorados:
        print(f"{len(ignorados)} cluster(s) ignorado(s) por não ter questão anterior identificável: {ignorados}")

    return por_questao


def _consolidar(por_questao: dict[int, list[tuple[int, pymupdf.Rect]]]) -> dict[int, tuple[int, pymupdf.Rect]]:
    """Uma entrada por questão: (indice_pagina, retangulo_unificado).
    Quando os candidatos caem em páginas diferentes, fica só o grupo
    de maior área total (ver docstring do módulo)."""
    resultado = {}
    for numero, entradas in por_questao.items():
        por_pagina: dict[int, list[pymupdf.Rect]] = {}
        for pagina_idx, rect in entradas:
            por_pagina.setdefault(pagina_idx, []).append(rect)

        pagina_escolhida = max(por_pagina, key=lambda p: sum(r.width * r.height for r in por_pagina[p]))
        rects = por_pagina[pagina_escolhida]

        uniao = rects[0]
        for r in rects[1:]:
            uniao |= r
        resultado[numero] = (pagina_escolhida, uniao)
    return resultado


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python extrair_figuras_pdf.py <arquivo.pdf> <ano> <caderno> [--aplicar] [--sobrescrever]")
        sys.exit(1)

    caminho, ano, caderno = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    aplicar = "--aplicar" in sys.argv
    sobrescrever = "--sobrescrever" in sys.argv

    doc = pymupdf.open(caminho)
    bruto = localizar_clusters(caminho)
    consolidado = _consolidar(bruto)
    print(f"{len(consolidado)} questão(ões) com figura/gráfico/tabela candidata encontrada(s).")

    multiplas_paginas = {n: e for n, e in bruto.items() if len({p for p, _ in e}) > 1}
    if multiplas_paginas:
        print(f"{len(multiplas_paginas)} questão(ões) tinham cluster em mais de uma página -- ficou só o grupo maior: {sorted(multiplas_paginas)}")

    PASTA_ENUNCIADOS.mkdir(exist_ok=True)

    salvos, aplicadas, ja_preenchidas, nao_encontradas = [], 0, [], []
    for numero in sorted(consolidado):
        indice_pagina, rect = consolidado[numero]
        id_questao = db.gerar_id_canonico(ano, caderno, numero)

        detalhe = db.detalhe_questao(id_questao)
        if detalhe is None:
            nao_encontradas.append(id_questao)
            continue
        if detalhe["enunciado_imagem_path"] and not sobrescrever:
            ja_preenchidas.append(id_questao)
            continue

        pagina = doc[indice_pagina]
        rect_com_margem = rect + (-_MARGEM_PT, -_MARGEM_PT, _MARGEM_PT, _MARGEM_PT)
        rect_com_margem &= pagina.rect  # nunca estoura o limite da página
        pixmap = pagina.get_pixmap(clip=rect_com_margem, dpi=150)
        destino = PASTA_ENUNCIADOS / f"{id_questao}.png"
        pixmap.save(str(destino))
        salvos.append(id_questao)

        if aplicar:
            db.atualizar_enunciado(id_questao, imagem_path=str(destino))
            aplicadas += 1

    print(f"{len(salvos)} imagem(ns) salva(s) em {PASTA_ENUNCIADOS}: {salvos}")
    if not aplicar:
        print("Modo revisão (sem --aplicar) -- confere os PNGs acima antes de aplicar; nada foi gravado no banco.")
    else:
        print(f"{aplicadas} caminho(s) gravado(s) em enunciado_imagem_path via atualizar_enunciado().")
    if ja_preenchidas:
        print(f"{len(ja_preenchidas)} questão(ões) já tinham imagem e foram puladas (rode com --sobrescrever pra forçar): {ja_preenchidas}")
    if nao_encontradas:
        print(f"{len(nao_encontradas)} questão(ões) do PDF não existe(m) no banco: {nao_encontradas}")
