"""
extrair_gabarito_pdf.py — extrai o gabarito oficial de Matemática
(questões 136-180) de um PDF de gabarito do INEP (2º dia, aplicação
regular/impressa).

Não confia em transcrição manual: lê o texto real do PDF via pdftotext
e faz uma checagem de sanidade — toda questão de 136 a 180 precisa
aparecer OU com uma letra (A-E) OU na lista de anuladas (via nota de
rodapé "Questão N Anulada"). Se sobrar alguma sem explicação, o
script avisa em vez de seguir com dado incompleto.

Uso: python extrair_gabarito_pdf.py <arquivo.pdf> <ano>
Gera: gabaritos_reais/gabarito_<ano>_azul_OFICIAL.csv (numero,materia,gabarito;
materia sai como placeholder 'SEM_VIDEO_PENDENTE' -- o PDF não traz assunto,
só resposta. Pronto pra reconstruir_base.py pegar na próxima execução.)
"""
import csv
import re
import subprocess
import sys
from pathlib import Path


def extrair_gabarito_matematica(caminho: str, area_inicio: int = 136, area_fim: int = 180) -> tuple[dict, set]:
    texto = subprocess.run(
        ["pdftotext", "-layout", caminho, "-"], capture_output=True, text=True, check=True
    ).stdout

    gabarito = {}
    for numero_str, letra in re.findall(r"\b(\d{2,3})\s+([A-E])\b", texto):
        numero = int(numero_str)
        if area_inicio <= numero <= area_fim:
            gabarito[numero] = letra

    # Dois formatos observados nos PDFs oficiais do INEP:
    # 2019/2020: nota de rodapé "* Questão N Anulada"
    # 2021-2025: marcação inline, direto na linha da tabela ("N  Anulada"/"Anulado")
    anuladas = set()
    for n in re.findall(r"Quest[ãa]o\s+(\d{2,3})\s+Anulad[ao]", texto, re.IGNORECASE):
        if area_inicio <= int(n) <= area_fim:
            anuladas.add(int(n))
    for n in re.findall(r"\b(\d{2,3})\s+[Aa]nulad[ao]\b", texto):
        if area_inicio <= int(n) <= area_fim:
            anuladas.add(int(n))

    faltando = set(range(area_inicio, area_fim + 1)) - set(gabarito) - anuladas
    if faltando:
        raise ValueError(
            f"Questões sem gabarito nem marcação de anulada: {sorted(faltando)}. "
            "Não vou gerar CSV incompleto sem confirmação manual — confere o PDF direto."
        )

    return gabarito, anuladas


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python extrair_gabarito_pdf.py <arquivo.pdf> <ano>")
        sys.exit(1)

    caminho, ano = sys.argv[1], sys.argv[2]
    gabarito, anuladas = extrair_gabarito_matematica(caminho)

    # Nome e colunas no formato que carregar_gabarito_csv() exige e que
    # reconstruir_base.py varre (gabarito_<ano>_<caderno>_OFICIAL.csv,
    # com numero,materia,gabarito). O PDF do INEP não traz matéria —
    # cada linha nasce com o mesmo placeholder que o resto do pipeline
    # já usa pra "ainda não sei a matéria desta questão", pra
    # reconstruir_base.py (com preservar_materia_classificada=True)
    # não tratar isso como uma classificação de verdade.
    destino = Path(__file__).parent / "gabaritos_reais" / f"gabarito_{ano}_azul_OFICIAL.csv"
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["numero", "materia", "gabarito"])
        for numero in sorted(gabarito):
            w.writerow([numero, "SEM_VIDEO_PENDENTE", gabarito[numero]])

    print(f"{destino}: {len(gabarito)} questões, {len(anuladas)} anulada(s) {sorted(anuladas)}")
    print("Matéria de cada questão fica pendente até vídeo (coletar_videos.py) ou triagem manual.")
