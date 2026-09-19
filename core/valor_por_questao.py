"""valor_por_questao.py — aproxima quantos pontos de nota vale acertar cada
item do ENEM, dado o nível atual do aluno, usando os parâmetros TRI do
INEP (core/inep_itens/itens_ligados_ao_corpus.csv).

Modelo (3PL, D=1,7; nota = 500 + 100*theta, suposição padrão da escala):
    P_i(theta) = c + (1-c) / (1 + exp(-D*a*(theta-b)))
A derivada da log-verossimilhança em theta contribui com peso
    w_i = D*a*(P_i - c) / (P_i*(1-c))
por (u_i - P_i). Trocar um erro por acerto no item i muda theta em
aproximadamente w_i / I, onde I = soma da informação de Fisher dos itens.
O valor esperado de dominar o item = (1 - P_i) * w_i / I * 100 pontos.

É uma aproximação de primeira ordem: a nota oficial usa a verossimilhança
do padrão inteiro de respostas, não esta linearização. Serve pra ORDENAR
itens e matérias, não pra prever a nota exata.

Uso: python valor_por_questao.py [nota_atual] [area]   (padrão 600, CN)
"""
import csv
import math
import sys
from collections import defaultdict

D = 1.7
CSV_ITENS = "inep_itens/itens_ligados_ao_corpus.csv"


def prob(a, b, c, theta):
    return c + (1 - c) / (1 + math.exp(-D * a * (theta - b)))


def valor_itens(itens, nota):
    """itens: lista de (a, b, c). Devolve lista de dicts com P e pontos."""
    theta = (nota - 500) / 100
    ps = [prob(a, b, c, theta) for a, b, c in itens]
    # P' = D*a*(P-c)*(1-P)/(1-c); I_i = P'^2 / (P*(1-P))
    info = sum(
        (D * a * (p - c) * (1 - p) / (1 - c)) ** 2 / (p * (1 - p))
        for (a, b, c), p in zip(itens, ps)
    )
    out = []
    for (a, b, c), p in zip(itens, ps):
        w = D * a * (p - c) / (p * (1 - c))
        out.append({
            "p_acerto": p,
            "pts_por_acerto": 100 * w / info,
            "pts_esperados": 100 * w / info * (1 - p),
        })
    return out


def carregar(area="CN"):
    por_ano = defaultdict(list)
    with open(CSV_ITENS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["area"] == area and r["b"] and r["aban"] == "0" and r["cor"] == "AZUL":
                por_ano[int(r["ano"])].append(
                    (int(r["indice"]), float(r["a"]), float(r["b"]), float(r["c"])))
    return por_ano


if __name__ == "__main__":
    nota = float(sys.argv[1]) if len(sys.argv) > 1 else 600
    area = sys.argv[2] if len(sys.argv) > 2 else "CN"
    for ano, itens in sorted(carregar(area).items()):
        v = valor_itens([(a, b, c) for _, a, b, c in itens], nota)
        pts = sorted(x["pts_por_acerto"] for x in v)
        print(ano, len(v), "itens | pts por acerto min/mediana/max:",
              round(pts[0], 1), round(pts[len(pts) // 2], 1), round(pts[-1], 1))
