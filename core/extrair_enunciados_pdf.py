"""
extrair_enunciados_pdf.py — extrai o TEXTO completo de cada questão
(enunciado + alternativas A-E) de um PDF de PROVA do INEP (2º dia,
aplicação regular/impressa), quebrando por "Questão N".

Só texto nesta primeira versão -- de propósito. O ENEM desenha
figura/gráfico/tabela como vetor dentro do PDF, não como "objeto de
imagem" (confirmado: page.get_image_info() volta vazio em página com
figura visível), então não tem como simplesmente "localizar a imagem
mais próxima". Detectar isso via espaçamento vertical incomum entre
blocos de texto é possível, mas é uma heurística que precisa de mais
teste visual antes de confiar -- fica pra uma segunda etapa, depois
de validar que a extração de texto (a parte de maior valor: dá pra
responder a prova sem o PDF aberto do lado) está correta. Testado
contra um PDF real (2020 azul, 90 questões): ~39% citam figura/
gráfico/tabela no texto -- essas ganham um aviso ⚠️ no início do
enunciado (ver _PADRAO_CITA_FIGURA) pra sinalizar "confere contra o
PDF" em vez de confiar cego; não detecta o caso raro de uma imagem
pura sem nenhuma palavra derivada dela no texto (ex: uma tirinha).

Não decide gabarito nem classifica matéria -- só o enunciado bruto,
pra popular questoes.enunciado_texto via db.atualizar_enunciado() (a
mesma função que o editor manual em Cartão-resposta já usa --
COALESCE, nunca sobrescreve o que já existe sem --sobrescrever).

Ordem de leitura: page.get_text() do PyMuPDF já reconstrói o layout de
duas colunas do ENEM corretamente (confirmado manualmente contra um
PDF real: 91→180 em sequência perfeita, sem embaralhar) -- ao
contrário do pdftotext -layout usado em extrair_gabarito_pdf.py, que
preserva posição visual literal e por isso intercala colunas.

Uso: python extrair_enunciados_pdf.py <arquivo.pdf> <ano> <caderno> [--aplicar] [--sobrescrever]
Sem --aplicar: só gera um relatório (scratch_enunciados_<ano>_<caderno>.txt,
na pasta do script) pra revisão manual -- não grava nada no banco. Com
--aplicar: grava via db.atualizar_enunciado() pra cada questão que
existe no banco (ano/caderno/numero), avisando quem não existe.
"""
import re
import sys
from pathlib import Path

import pymupdf

import db

_PADRAO_QUESTAO = re.compile(r"quest[ãa]o\s+(\d+)\s*\n", re.IGNORECASE)
_PADRAO_CABECALHO_PAGINA = re.compile(r"(CN|MT|LC|CH|CN|MT) - 2° dia \| Caderno \d+ - \w+ - Página \d+\n?")
_PADRAO_BARCODE = re.compile(r"\*\d+\w*\*\n?")
_PADRAO_SECAO = re.compile(r"(CIÊNCIAS DA NATUREZA|MATEMÁTICA)( E SUAS TECNOLOGIAS)?\nQuestões de \d+ a \d+\n?")
_PADRAO_ALTERNATIVA = re.compile(r"^[A-E]\s")
_PADRAO_FIM_FRASE = re.compile(r"[.:;?!]$")
_PADRAO_LIGADURA = re.compile(r"\b(fi|fl) (?=[a-zà-úA-ZÀ-Ú])")


def _limpar_ruido_pagina(texto: str) -> str:
    """Remove cabeçalho de página, código de barras e header de seção
    que o PyMuPDF intercala no meio do texto entre uma questão e a
    próxima -- não é conteúdo da questão, é ruído da diagramação."""
    texto = _PADRAO_CABECALHO_PAGINA.sub("", texto)
    texto = _PADRAO_BARCODE.sub("", texto)
    texto = _PADRAO_SECAO.sub("", texto)
    return texto.strip()


def _reformatar_paragrafos(texto: str) -> str:
    """Texto justificado no PDF às vezes vem uma palavra por linha (o
    PyMuPDF interpreta o espaçamento variável da justificação como
    quebra de linha) -- rejunta tudo numa linha só por parágrafo,
    preservando cada alternativa A-E na sua própria linha. Também
    corrige o espaço fantasma que aparece em ligaduras 'fi'/'fl'
    ('signifi cativa' -> 'significativa', 'fl uxo' -> 'fluxo') -- nem
    "fi" nem "fl" existem como palavra sozinha em português, então
    juntar sempre que aparecem seguidas de espaço é seguro."""
    saida = []
    buffer = ""
    for linha_bruta in texto.split("\n"):
        linha = linha_bruta.strip()
        if not linha:
            if buffer:
                saida.append(buffer)
                buffer = ""
            saida.append("")
            continue
        if _PADRAO_ALTERNATIVA.match(linha):
            if buffer:
                saida.append(buffer)
            buffer = linha
        elif buffer:
            buffer += " " + linha
        else:
            buffer = linha
        if _PADRAO_FIM_FRASE.search(linha) and not _PADRAO_ALTERNATIVA.match(linha):
            saida.append(buffer)
            buffer = ""
    if buffer:
        saida.append(buffer)
    resultado = "\n".join(saida)
    return _PADRAO_LIGADURA.sub(r"\1", resultado)


_PADRAO_CITA_FIGURA = re.compile(
    r"figura|gr[aá]fico|esquema|tabela|imagem|tirinha|charge|quadro a seguir|ilustra|estruturas? química",
    re.IGNORECASE,
)
_AVISO_FIGURA = (
    "⚠️ Esta questão pode depender de figura/gráfico/tabela que a extração de texto "
    "não capturou (o ENEM desenha isso como vetor, não como imagem separada) -- "
    "confere contra o PDF original antes de confiar só neste texto.\n\n"
)


def extrair_textos(caminho: str) -> dict[int, str]:
    """{numero_questao: texto_completo} pra todo o PDF. Questão cujo
    texto cita palavra de figura/gráfico/tabela/esquema ganha um aviso
    no início -- heurística por palavra-chave, não detecta 100% dos
    casos (uma questão com imagem pura, tipo uma tirinha sem nenhuma
    palavra derivada dela no texto, passa batido), mas pega a maioria
    sem exigir a etapa mais arriscada de recortar imagem por
    coordenada."""
    doc = pymupdf.open(caminho)
    texto_completo = "\n".join(pagina.get_text() for pagina in doc)
    partes = _PADRAO_QUESTAO.split(texto_completo)
    # re.split com grupo de captura devolve [antes, numero1, depois1, numero2, depois2, ...]
    resultado = {}
    for i in range(1, len(partes), 2):
        numero = int(partes[i])
        texto = _reformatar_paragrafos(_limpar_ruido_pagina(partes[i + 1]))
        if _PADRAO_CITA_FIGURA.search(texto):
            texto = _AVISO_FIGURA + texto
        resultado[numero] = texto
    return resultado


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python extrair_enunciados_pdf.py <arquivo.pdf> <ano> <caderno> [--aplicar] [--sobrescrever]")
        sys.exit(1)

    caminho, ano, caderno = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    aplicar = "--aplicar" in sys.argv
    sobrescrever = "--sobrescrever" in sys.argv

    textos = extrair_textos(caminho)
    print(f"{len(textos)} questões extraídas do PDF (números {min(textos)}-{max(textos)}).")

    destino_relatorio = Path(__file__).parent / f"scratch_enunciados_{ano}_{caderno}.txt"
    with destino_relatorio.open("w", encoding="utf-8") as f:
        for numero in sorted(textos):
            f.write(f"=== Questão {numero} ===\n{textos[numero]}\n\n")
    print(f"Relatório de revisão: {destino_relatorio}")

    if not aplicar:
        print("Modo revisão (sem --aplicar) -- nada foi gravado no banco. Confere o relatório acima antes de aplicar.")
        sys.exit(0)

    aplicadas, nao_encontradas, ja_preenchidas = 0, [], []
    for numero, texto in sorted(textos.items()):
        id_questao = db.gerar_id_canonico(ano, caderno, numero)
        detalhe = db.detalhe_questao(id_questao)
        if detalhe is None:
            nao_encontradas.append(id_questao)
            continue
        if detalhe["enunciado_texto"] and not sobrescrever:
            ja_preenchidas.append(id_questao)
            continue
        db.atualizar_enunciado(id_questao, texto=texto)
        aplicadas += 1

    print(f"{aplicadas} enunciado(s) gravado(s) via atualizar_enunciado().")
    if ja_preenchidas:
        print(f"{len(ja_preenchidas)} questão(ões) já tinham enunciado e foram puladas (rode com --sobrescrever pra forçar): {ja_preenchidas}")
    if nao_encontradas:
        print(f"{len(nao_encontradas)} questão(ões) do PDF não existe(m) no banco (gabarito não carregado ainda): {nao_encontradas}")
