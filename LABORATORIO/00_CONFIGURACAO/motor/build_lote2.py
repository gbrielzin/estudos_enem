"""Gera o Lote 2 e o ranking v2 (16 critérios, 17 simulações). Uso: python3 -I build_lote2.py"""
import os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from motor import scenarios
from params_lote2 import P as P2
from sims_texto2 import T as T2, EXP_LOTE1

LAB = B.LAB
AGES = ["19-21", "22-24", "25-27", "28-29"]
for sid in T2:
    for i, c in enumerate(T2[sid]["cap"]):
        c["sit"] = f"{AGES[i]} anos. " + re.sub(r"^\d+-\d+ anos\. ", "", c["sit"])
    B.T[sid] = T2[sid]
    sc = scenarios(P2[sid]); B.R[sid] = sc
    for k in sc: sc[k]["has_co"] = any(v > 0 for v in P2[sid].get("REV", [0]))
from params_lote3 import P as P3
from sims_texto3 import T as T3
for sid in T3:
    for i, c in enumerate(T3[sid]["cap"]):
        c["sit"] = f"{AGES[i]} anos. " + re.sub(r"^\d+-\d+ anos\. ", "", c["sit"])
    B.T[sid] = T3[sid]
    sc = scenarios(P3[sid]); B.R[sid] = sc
    for k in sc: sc[k]["has_co"] = any(v > 0 for v in P3[sid].get("REV", [0]))
from params_lote4 import P as P4
from sims_texto4 import T as T4
for sid in T4:
    for i, c in enumerate(T4[sid]["cap"]):
        c["sit"] = f"{AGES[i]} anos. " + re.sub(r"^\d+-\d+ anos\. ", "", c["sit"])
    B.T[sid] = T4[sid]
    sc = scenarios(P4[sid]); B.R[sid] = sc
    for k in sc: sc[k]["has_co"] = any(v > 0 for v in P4[sid].get("REV", [0]))
B.CRIT.append("Experiência de vida")
for sid in list(T2) + list(T3) + list(T4):
    a = B.auto_scores(sid)
    m = [(int(x.split("|")[0]), x.split("|", 1)[1]) for x in B.T[sid]["notas"]]
    B.SC[sid] = a + m
    assert len(B.SC[sid]) == 16, sid
def equil(vals, w16=1.0):
    v = list(vals)
    for i in (11, 12, 13): v[i] = 10 - v[i]
    w = [1.0]*15 + [w16]
    return sum(a*b for a, b in zip(v, w))/sum(w)
S16 = {}
for sid, sc in B.SC.items():
    v = [n for n, _ in sc]
    if len(v) == 15:
        n, j = EXP_LOTE1[sid].split("|", 1); v.append(int(n))
    S16[sid] = v
B.equilibrio = lambda sid: equil([n for n, _ in B.SC[sid]])
f0, R, T = B.f0, B.R, B.T

if __name__ == "__main__":
    for sid in sorted(T4): B.escreve_sim(sid)
    ids = sorted(R)
    # consolidado lote 2
    L = ["# Resultados financeiros consolidados — Lote 4 (cenário base, R$ mil nominais)\n",
         "Dividendos proporcionais à participação (div_share=True); participação valorada como valor da empresa − dívida líquida (ev_net_debt=True). Patrimônio ajustado = pessoal líquido + 70% do valor da participação.\n",
         "| ID | Trajetória | Patrimônio pessoal líquido | Valor da participação | Patrimônio ajustado | Ajustado (R$ de hoje) | Renda mensal A10 | Renda acumulada | Menor patrimônio pessoal no caminho | Pessimista (ajust.) | Otimista (ajust.) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for sid in sorted(T4):
        b = R[sid]["base"]; mn = min(r["pers"] for r in b["rows"])
        L.append(f"| {sid} | {T[sid]['nome']} | {f0(b['pers'])} | {f0(b['stake'])} | {f0(b['adj'])} | {f0(b['adj_real'])} | {b['inc_m']:.1f} | {f0(b['inc_ac'])} | {f0(mn)} | {f0(R[sid]['pessimista']['adj'])} | {f0(R[sid]['otimista']['adj'])} |")
    open(os.path.join(LAB, "04_RESULTADOS_FINANCEIROS", "consolidado_lote4.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # ranking v2
    def top(key, n=3): return sorted(ids, key=key, reverse=True)[:n]
    eq1 = lambda s: equil(S16[s]); eq2 = lambda s: equil(S16[s], 2.0)
    out = ["# Rankings v4 — 29 simulações, 16 critérios (inclui Experiência de vida)\n",
           "O critério 16 é novo. As 10 simulações do Lote 1 receberam a nota 16 a posteriori (`notas_criterio16_lote1.md`) e seus arquivos v1 não foram alterados. Peso padrão: igual aos demais critérios. Para teste de sensibilidade, o ranking com peso 2× também é mostrado.\n"]
    rows = [("equilíbrio geral (peso igual, 16 critérios)", eq1, lambda s: f"{eq1(s):.2f}"),
            ("equilíbrio geral com experiência em peso 2×", eq2, lambda s: f"{eq2(s):.2f}"),
            ("experiência de vida (nota 16; desempate: renda mensal)", lambda s: (S16[s][15], R[s]["base"]["inc_m"]), lambda s: f"nota {S16[s][15]}"),
            ("patrimônio ajustado (base)", lambda s: R[s]["base"]["adj"], lambda s: f"R$ {f0(R[s]['base']['adj'])} mil"),
            ("patrimônio pessoal líquido (realizável)", lambda s: R[s]["base"]["pers"], lambda s: f"R$ {f0(R[s]['base']['pers'])} mil"),
            ("renda pessoal mensal no ano 10", lambda s: R[s]["base"]["inc_m"], lambda s: f"R$ {R[s]['base']['inc_m']:.1f} mil/mês"),
            ("segurança (nota 4; desempate: pior cenário)", lambda s: (S16[s][3], R[s]["pessimista"]["adj"]), lambda s: f"nota {S16[s][3]}; pess. R$ {f0(R[s]['pessimista']['adj'])} mil")]
    for name, key, show in rows:
        out.append(f"## TOP 3 por {name}\n")
        for i, sid in enumerate(top(key), 1): out.append(f"{i}. **{sid}** — {T[sid]['nome']} — {show(sid)}")
        out.append("")
    out.append("## Compromisso patrimônio × experiência (cenário base)\n\n| ID | Trajetória | Patrimônio ajustado | Pessoal líquido | Renda mensal A10 | Experiência (16) | Equilíbrio (peso 1×) | Equilíbrio (2×) | Prob. subjetiva |\n|---|---|---|---|---|---|---|---|---|")
    for sid in sorted(ids, key=lambda s: -eq1(s)):
        b = R[sid]["base"]; out.append(f"| {sid} | {T[sid]['nome']} | {f0(b['adj'])} | {f0(b['pers'])} | {b['inc_m']:.1f} | {S16[sid][15]} | {eq1(sid):.2f} | {eq2(sid):.2f} | {int(T[sid]['prob']*100)}% |")
    out.append("\n## Notas completas (0–10), 16 critérios\n\n| ID | " + " | ".join(str(i+1) for i in range(16)) + " |\n|---|" + "---|"*16)
    for sid in ids: out.append(f"| {sid} | " + " | ".join(map(str, S16[sid])) + " |")
    out.append("\nColunas: " + "; ".join(f"{i+1} {B.CRIT[i]}" for i in range(16)) + ". Em 12, 13 e 14 nota alta = pior (invertidas no equilíbrio).")
    open(os.path.join(LAB, "06_RANKINGS", "ranking_v4_29_simulacoes.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    # índice
    L = ["# Índice geral de simulações\n", "| ID | Nome | Lote | Trilhas | Horizonte | Versão | Status | Patrimônio ajustado (base, R$ mil) | Experiência (16) | Equilíbrio v4 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for sid in ids:
        L.append(f"| [{sid}](03_SIMULACOES/{sid}/v1.md) | {T[sid]['nome']} | {1 if sid<='SIM_010' else (2 if sid<='SIM_017' else (3 if sid<='SIM_020' else 4))} | {', '.join(map(str, T[sid]['trilhas']))} | 10 anos | v1 | concluída | {f0(R[sid]['base']['adj'])} | {S16[sid][15]} | {eq1(sid):.2f} |")
    L.append("\nRankings v4: [06_RANKINGS/ranking_v4_29_simulacoes.md](06_RANKINGS/ranking_v4_29_simulacoes.md) · Ranking v3 (20 simulações): [06_RANKINGS/ranking_v3_20_simulacoes.md](06_RANKINGS/ranking_v3_20_simulacoes.md) · Ranking v2 (17 simulações): [06_RANKINGS/ranking_v2_com_experiencia.md](06_RANKINGS/ranking_v2_com_experiencia.md) · Ranking v1 (Lote 1, 15 critérios): [06_RANKINGS/ranking_lote1_v1.md](06_RANKINGS/ranking_lote1_v1.md) · Consolidados: [Lote 1](04_RESULTADOS_FINANCEIROS/consolidado_lote1.md), [Lote 2](04_RESULTADOS_FINANCEIROS/consolidado_lote2.md), [Lote 3](04_RESULTADOS_FINANCEIROS/consolidado_lote3.md), [Lote 4](04_RESULTADOS_FINANCEIROS/consolidado_lote4.md)")
    open(os.path.join(LAB, "INDICE.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # catálogo
    uso = {n: [] for n in B.NOMES_TRILHAS}
    for sid in ids:
        for n in T[sid]["trilhas"]: uso[n].append(sid)
    L = ["# Catálogo de trilhas (v2)\n", "Trilhas são categorias; cada uma admite vários modelos de execução.\n", "| # | Trilha | Simulações que a usam |", "|---|---|---|"]
    for n in sorted(uso): L.append(f"| {n} | {B.NOMES_TRILHAS[n]} | {', '.join(uso[n]) if uso[n] else '—'} |")
    open(os.path.join(LAB, "02_CATALOGO_DE_TRILHAS", "CATALOGO.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("trilhas sem uso:", [n for n in uso if not uso[n]])
    for sid in sorted(ids, key=lambda s: -eq1(s)): print(sid, f"{eq1(sid):.2f} {eq2(sid):.2f}", S16[sid][15], f0(R[sid]['base']['adj']), f0(R[sid]['base']['pers']), round(R[sid]['base']['inc_m'],1))
