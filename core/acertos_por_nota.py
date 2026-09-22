"""acertos_por_nota.py — quantos acertos (de ~45) equivalem a cada nota, por área.

Usa os parâmetros TRI dos itens do INEP (core/inep_itens/<ano>_ITENS_PROVA_<ano>.csv),
mesmo modelo de valor_por_questao.py: 3PL, D=1,7, nota = 500 + 100*theta.
Para cada (ano, área) usa UMA prova do caderno AZUL (a de menor CO_PROVA com 40+
itens, sem itens abandonados/adaptados; em LC, sem os itens de espanhol) e soma
P(acerto) no theta da nota. É um valor ESPERADO: a nota oficial pesa a coerência
do padrão de respostas, e cada prova varia (ver a faixa entre anos).

Validação: para CN reproduz exatamente a tabela de docs/plano_50_dias_v1.md.

Uso: python acertos_por_nota.py [ano_ini] [ano_fim]   (padrão 2020 2025)
"""
import csv
import math
import statistics as st
import sys
from collections import defaultdict

D = 1.7
NOTAS = [500, 550, 600, 650, 700, 750, 800]
AREAS = {"CN": "Natureza", "MT": "Matemática", "CH": "Humanas", "LC": "Linguagens"}


def prob(a, b, c, theta):
    return c + (1 - c) / (1 + math.exp(-D * a * (theta - b)))


def itens_da_prova(ano, area):
    rows = csv.DictReader(
        open(f"inep_itens/{ano}_ITENS_PROVA_{ano}.csv", encoding="latin-1"), delimiter=";"
    )
    provas = defaultdict(dict)
    for r in rows:
        if r["SG_AREA"] != area or r["TX_COR"] != "AZUL" or not r["NU_PARAM_A"]:
            continue
        if r["IN_ITEM_ABAN"] == "1" or r["IN_ITEM_ADAPTADO"] == "1":
            continue
        if area == "LC" and r["TP_LINGUA"] == "1":
            continue
        provas[int(r["CO_PROVA"])][r["CO_ITEM"]] = (
            float(r["NU_PARAM_A"]), float(r["NU_PARAM_B"]), float(r["NU_PARAM_C"]),
        )
    cod = min(k for k, v in provas.items() if len(v) >= 40)
    return cod, list(provas[cod].values())


def tabela(ano_ini=2020, ano_fim=2025):
    out = {ar: {n: [] for n in NOTAS} for ar in AREAS}
    for ano in range(ano_ini, ano_fim + 1):
        for ar in AREAS:
            _, itens = itens_da_prova(ano, ar)
            for n in NOTAS:
                theta = (n - 500) / 100
                out[ar][n].append(sum(prob(a, b, c, theta) for a, b, c in itens))
    return out


if __name__ == "__main__":
    ini = int(sys.argv[1]) if len(sys.argv) > 1 else 2020
    fim = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    t = tabela(ini, fim)
    print(f"Acertos esperados (mediana, {ini}-{fim}) | faixa entre anos")
    print("| Nota | " + " | ".join(AREAS.values()) + " |")
    for n in NOTAS:
        cel = [f"{st.median(t[ar][n]):.0f} ({min(t[ar][n]):.0f}-{max(t[ar][n]):.0f})" for ar in AREAS]
        print(f"| {n} | " + " | ".join(cel) + " |")
