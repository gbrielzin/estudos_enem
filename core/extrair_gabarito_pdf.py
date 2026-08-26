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
Gera: gabarito_oficial_<ano>_azul.csv (numero,gabarito)
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

    destino = Path(f"gabarito_oficial_{ano}_azul.csv")
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["numero", "gabarito"])
        for numero in sorted(gabarito):
            w.writerow([numero, gabarito[numero]])

    print(f"{destino}: {len(gabarito)} questões, {len(anuladas)} anulada(s) {sorted(anuladas)}")
