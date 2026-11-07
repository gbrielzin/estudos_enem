"""Gera os arquivos do Laboratório (lote 1) a partir do motor + textos. Uso: python3 -I build.py
Não sobrescreve versões existentes: se SIM_NNN/v1.md existir, aborta (criar v2 manualmente)."""
import json, math, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from motor import *
from params_lote1 import P
from sims_texto import T

LAB = os.path.abspath(os.path.join(HERE, "..", ".."))
HOJE = "2026-11-07"
CRIT = ["Patrimônio líquido acumulado","Renda pessoal mensal","Renda pessoal acumulada","Segurança financeira",
        "Potencial de crescimento","Escalabilidade","Liberdade de tempo","Potencial internacional","Diversificação de renda",
        "Independência operacional","Aprendizado e competências","Complexidade de gestão (alta = pior)",
        "Risco financeiro (alta = pior)","Dependência do fundador (alta = pior)","Sustentabilidade pessoal"]
NOMES_TRILHAS = {}
for line in open(os.path.join(LAB, "02_CATALOGO_DE_TRILHAS", "CATALOGO.md"), encoding="utf-8"):
    if line.startswith("| ") and line[2:3].isdigit():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        NOMES_TRILHAS[int(c[0])] = c[1]

def f0(x):
    if abs(x) < 0.5: return "0"
    return f"{x:,.0f}".replace(",", ".")
def pct(x): return f"{x*100:.0f}%"
def clamp(v): return max(0, min(10, int(round(v))))

R = {}
for sid in sorted(P):
    sc = scenarios(P[sid]); R[sid] = sc
    for k in sc: sc[k]["has_co"] = any(v > 0 for v in P[sid].get("REV", [0]))

def auto_scores(sid):
    b = R[sid]["base"]
    s1 = clamp(10*math.log10(max(b["adj"], 10)/10)/math.log10(3000))
    s2 = clamp(10*math.log10(max(b["inc_m"], 2)/2)/math.log10(75))
    s3 = clamp(10*math.log10(max(b["inc_ac"], 100)/100)/math.log10(150))
    j1 = f"Patrimônio ajustado R$ {f0(b['adj'])} mil (escala log: R$10 mil=0; R$30 mi=10)"
    j2 = f"Renda pessoal de R$ {b['inc_m']:.1f} mil/mês no ano 10 (R$2 mil=0; R$150 mil=10)"
    j3 = f"Renda acumulada de R$ {f0(b['inc_ac'])} mil em 10 anos (R$100 mil=0; R$15 mi=10)"
    return [(s1, j1), (s2, j2), (s3, j3)]

SC = {}
for sid in R:
    a = auto_scores(sid)
    m = [(int(x.split("|")[0]), x.split("|", 1)[1]) for x in T[sid]["notas"]]
    SC[sid] = a + m          # 15 itens na ordem dos critérios
assert all(len(v) == 15 for v in SC.values())

def equilibrio(sid):
    v = [n for n, _ in SC[sid]]
    for i in (11, 12, 13): v[i] = 10 - v[i]
    return sum(v)/15

# ---------- arquivos de simulação ----------
def tabela_fin(sid, rows, has_co):
    anos = [f"A{r['ano']}" for r in rows]
    def line(label, key, ac=False, fmt=f0, force_ac=None):
        cells = [fmt(r[key]) for r in rows]
        tot = ""
        if ac: tot = f0(sum(r[key] for r in rows))
        return f"| {label} | " + " | ".join(cells) + f" | {tot} |"
    h = "| Item (R$ mil) | " + " | ".join(anos) + " | Acum. |\n|---|" + "---|"*11 + "\n"
    out = h
    out += "| Idade ao fim do ano | " + " | ".join(str(r["idade"]) for r in rows) + " | |\n"
    if has_co:
        out += line("Faturamento", "fat", True)+"\n"+line("Receita recorrente", "rec", True)+"\n"
        out += line("Lucro bruto", "gp", True)+"\n"
        out += "| Margem bruta | " + " | ".join(pct(r["gm"]) if r["fat"] else "—" for r in rows) + " | |\n"
        out += line("Lucro operacional (após pró-labore)", "lop", True)+"\n"
        out += line("Impostos e provisões", "imp", True)+"\n"+line("Despesa financeira", "juros", True)+"\n"
        out += line("Lucro líquido da empresa", "net", True)+"\n"
        out += line("Fluxo de caixa livre (op.+invest.)", "fcf", True)+"\n"
        out += line("Capital de giro (saldo)", "wc")+"\n"+line("Caixa empresarial (saldo)", "cash")+"\n"
        out += line("Pró-labore líquido", "pl", True)+"\n"+line("Dividendos", "div", True)+"\n"
    out += line("Renda pessoal total", "inc", True)+"\n"+line("Custo de vida", "living", True)+"\n"
    out += line("Poupança do ano", "sav", True)+"\n"
    out += line("Patrimônio financeiro pessoal", "wealth")+"\n"
    out += line("Outros ativos (imóveis/participações de terceiros)", "assets")+"\n"
    out += line("Dívidas pessoais", "debt_pess")+"\n"
    out += line("Patrimônio pessoal líquido", "pers")+"\n"
    if has_co:
        out += line("Dívida empresarial", "debt_emp")+"\n"
        out += "| Participação societária | " + " | ".join(pct(r["own"]) if r["fat"] or r["val"] else "—" for r in rows) + " | |\n"
        out += line("Valor estimado da empresa (NÃO é caixa)", "val")+"\n"
        out += line("Valor da participação (ilíquido)", "stake")+"\n"
    return out

def escreve_sim(sid):
    t = T[sid]; sc = R[sid]; b = sc["base"]; rows = b["rows"]; has = b["has_co"]
    d = os.path.join(LAB, "03_SIMULACOES", sid); os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, "v1.md")
    if os.path.exists(fp): raise SystemExit(f"{fp} já existe: não sobrescrevo (crie v2).")
    tr = ", ".join(f"{n} ({NOMES_TRILHAS[n]})" for n in t["trilhas"])
    md = [f"# {sid} — {t['nome']} (v1)\n",
          f"- **Data:** {HOJE} · **Horizonte:** 10 anos (19→29 anos) · **Moeda:** R$ mil nominais\n- **Trilhas:** {tr}\n- **Hipótese estratégica:** {t['hip']}\n- **Estratégia inicial:** {t['estrategia']}\n- **Probabilidade subjetiva do desfecho-base:** {pct(t['prob'])} (estimativa do laboratório, sem base estatística)\n",
          "> Os números vêm do motor financeiro (`00_CONFIGURACAO/motor`). São cenários de simulação, não previsão.\n",
          "## 1. Premissas\n- Personagem-base fictício: ver `01_PERFIL_E_PREMISSAS/A_personagem_base.md`.\n- Aprovação no ENEM com bolsa em SP **assumida** (variável de controle; teste sem bolsa em `08_CENARIOS_ALTERNATIVOS`).\n- Inflação 4,5% a.a.; retorno da carteira pessoal 10% a.a. líquido; dívida empresarial 14%; dívida pessoal 12%.\n- Desconto de iliquidez de 30% sobre participação em empresa privada no cálculo do patrimônio ajustado.\n- Pró-labore com 15% de encargos; dividendos tributados em 10% apenas acima de R$600 mil/ano (simplificação).\n"]
    md.append("## 2. Histórico cronológico\n")
    spans = [(0, 2), (2, 5), (5, 8), (8, 10)]
    for i, (a, z) in enumerate(spans):
        c = t["cap"][i]; last = rows[z-1]
        md.append(f"### Capítulo {i+1} — anos {a+1} a {z} (termina aos {last['idade']} anos)\n")
        md.append(f"- **Situação e objetivos:** {c['sit']}\n- **Decisões tomadas:** {c['dec']}\n- **Alternativas descartadas:** {c['desc']}\n- **Operação (técnica, equipe, clientes):** {c['op']}\n- **Problemas, crises e oportunidades:** {c['crise']}\n- **Competências adquiridas:** {c['comp']}")
        ln = f"- **Números ao fim do capítulo (base):** renda pessoal R$ {f0(last['inc'])} mil/ano · patrimônio pessoal líquido R$ {f0(last['pers'])} mil"
        if has: ln += f" · faturamento R$ {f0(last['fat'])} mil · caixa empresarial R$ {f0(last['cash'])} mil · valor da participação (ilíquido) R$ {f0(last['stake'])} mil"
        md.append(ln + "\n")
    md.append("## 3. Arquitetura e padrão técnico\n" + t["tecnica"] + "\n")
    md.append("## 4. Resultados financeiros — cenário base\n" + tabela_fin(sid, rows, has))
    md.append("\n### Métricas de unidade e negócio\n" + "\n".join("- " + x for x in t["metricas"]) + "\n")
    md.append("## 5. Cenários\n| Cenário | Patrimônio pessoal líquido | Valor da participação (ilíquido) | Patrimônio ajustado | Ajustado em R$ de hoje | Renda mensal ano 10 | Renda acumulada | Caixa empresarial |\n|---|---|---|---|---|---|---|---|")
    for k in ("pessimista", "base", "otimista"):
        x = sc[k]
        md.append(f"| {k} | {f0(x['pers'])} | {f0(x['stake'])} | {f0(x['adj'])} | {f0(x['adj_real'])} | {x['inc_m']:.1f} | {f0(x['inc_ac'])} | {f0(x['cash'])} |")
    md.append("\nMultiplicadores: pessimista (receita ×0,6; margem −5 p.p.; salário ×0,88; múltiplo ×0,6) · otimista (receita ×1,5; margem +4 p.p.; salário ×1,15; múltiplo ×1,4).\n")
    md.append("## 6. Falhas, acertos, competências, riscos e conclusões\n")
    for lab, key in (("Falhas", "falhas"), ("Acertos", "acertos"), ("Riscos", "riscos"), ("Conclusões", "conclusoes")):
        md.append(f"**{lab}**\n" + "\n".join("- " + x for x in t[key]) + "\n")
    md.append(f"**Competências adquiridas:** {t['comp']}\n\n**Sacrifícios exigidos:** {t['sacrificios']}\n")
    md.append("## 7. Avaliação (0–10)\nNos critérios 12, 13 e 14 nota alta = pior.\n\n| # | Critério | Nota | Justificativa |\n|---|---|---|---|")
    for i, (n, j) in enumerate(SC[sid]): md.append(f"| {i+1} | {CRIT[i]} | {n} | {j} |")
    md.append(f"\n**Equilíbrio geral (média dos 15 critérios, com 12–14 invertidos):** {equilibrio(sid):.2f}\n")
    open(fp, "w", encoding="utf-8").write("\n".join(md))
    json.dump({k: [{kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in r.items()} for r in sc[k]["rows"]] for k in sc},
              open(os.path.join(d, "dados_v1.json"), "w"), ensure_ascii=False, indent=1)

def cleanup_gitkeep():
    for d in ("03_SIMULACOES", "04_RESULTADOS_FINANCEIROS", "05_COMPARACOES", "06_RANKINGS", "07_APRENDIZADOS", "08_CENARIOS_ALTERNATIVOS"):
        g = os.path.join(LAB, d, ".gitkeep")
        if os.path.exists(g): os.remove(g)

def top3(key, rev=True):
    return sorted(R, key=key, reverse=rev)[:3]

if __name__ == "__main__":
    for sid in sorted(R): escreve_sim(sid)
    cleanup_gitkeep()
    # consolidado
    L = ["# Resultados financeiros consolidados — Lote 1 (cenário base, R$ mil nominais)\n",
         "Patrimônio ajustado = patrimônio pessoal líquido + 70% do valor da participação societária (desconto de iliquidez). Valuation não é dinheiro disponível.\n",
         "| ID | Trajetória | Patrimônio pessoal líquido | Valor da participação | Patrimônio ajustado | Ajustado (R$ de hoje) | Renda mensal A10 | Renda acumulada | Caixa empresarial A10 | Faturamento A10 | Pessimista (ajust.) | Otimista (ajust.) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sid in sorted(R):
        b = R[sid]["base"]
        L.append(f"| {sid} | {T[sid]['nome']} | {f0(b['pers'])} | {f0(b['stake'])} | {f0(b['adj'])} | {f0(b['adj_real'])} | {b['inc_m']:.1f} | {f0(b['inc_ac'])} | {f0(b['cash'])} | {f0(b['fat'])} | {f0(R[sid]['pessimista']['adj'])} | {f0(R[sid]['otimista']['adj'])} |")
    open(os.path.join(LAB, "04_RESULTADOS_FINANCEIROS", "consolidado_lote1.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    with open(os.path.join(LAB, "04_RESULTADOS_FINANCEIROS", "consolidado_lote1.csv"), "w", encoding="utf-8") as fh:
        fh.write("id;nome;pers;stake;adj;adj_real;renda_mensal_a10;renda_acum;caixa_emp;fat_a10;adj_pess;adj_otim;equilibrio\n")
        for sid in sorted(R):
            b = R[sid]["base"]
            fh.write(f"{sid};{T[sid]['nome']};{b['pers']:.0f};{b['stake']:.0f};{b['adj']:.0f};{b['adj_real']:.0f};{b['inc_m']:.1f};{b['inc_ac']:.0f};{b['cash']:.0f};{b['fat']:.0f};{R[sid]['pessimista']['adj']:.0f};{R[sid]['otimista']['adj']:.0f};{equilibrio(sid):.2f}\n")
    # rankings
    rk = {"patrimônio (ajustado, base)": (lambda s: R[s]["base"]["adj"], lambda s: f"R$ {f0(R[s]['base']['adj'])} mil"),
          "renda pessoal mensal (ano 10, base)": (lambda s: R[s]["base"]["inc_m"], lambda s: f"R$ {R[s]['base']['inc_m']:.1f} mil/mês"),
          "segurança (nota 4; desempate: pior cenário)": (lambda s: (SC[s][3][0], R[s]["pessimista"]["adj"]), lambda s: f"nota {SC[s][3][0]}; pessimista R$ {f0(R[s]['pessimista']['adj'])} mil"),
          "liberdade (nota 7; desempate: independência operacional e baixa dependência do fundador)": (lambda s: (SC[s][6][0], SC[s][9][0], -SC[s][13][0]), lambda s: f"nota {SC[s][6][0]}; indep. {SC[s][9][0]}; dep. fundador {SC[s][13][0]}"),
          "potencial internacional (nota 8)": (lambda s: (SC[s][7][0], SC[s][4][0]), lambda s: f"nota {SC[s][7][0]}"),
          "equilíbrio geral (média dos 15 critérios, 12–14 invertidos)": (lambda s: equilibrio(s), lambda s: f"{equilibrio(s):.2f}")}
    L = ["# Rankings — Lote 1 (10 simulações)\n", "Os rankings mudam conforme o critério. Nenhuma nota única substitui os componentes (ver cada `SIM_NNN/v1.md`).\n"]
    for name, (key, show) in rk.items():
        L.append(f"## TOP 3 por {name}\n")
        for i, sid in enumerate(top3(key), 1): L.append(f"{i}. **{sid}** — {T[sid]['nome']} — {show(sid)}")
        L.append("")
    L.append("## Tabela completa de notas (0–10)\n\n| ID | " + " | ".join(str(i+1) for i in range(15)) + " | Equilíbrio |\n|---|" + "---|"*16)
    for sid in sorted(R): L.append(f"| {sid} | " + " | ".join(str(n) for n, _ in SC[sid]) + f" | {equilibrio(sid):.2f} |")
    L.append("\nLegenda das colunas: " + "; ".join(f"{i+1} {CRIT[i]}" for i in range(15)) + ".")
    open(os.path.join(LAB, "06_RANKINGS", "ranking_lote1_v1.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # índice
    L = ["# Índice geral de simulações\n", "| ID | Nome | Trilhas | Horizonte | Versão | Status | Patrimônio ajustado (base, R$ mil) | Equilíbrio |", "|---|---|---|---|---|---|---|---|"]
    for sid in sorted(R):
        L.append(f"| [{sid}](03_SIMULACOES/{sid}/v1.md) | {T[sid]['nome']} | {', '.join(map(str, T[sid]['trilhas']))} | 10 anos | v1 | concluída | {f0(R[sid]['base']['adj'])} | {equilibrio(sid):.2f} |")
    L.append("\nRankings: [06_RANKINGS/ranking_lote1_v1.md](06_RANKINGS/ranking_lote1_v1.md) · Consolidado: [04_RESULTADOS_FINANCEIROS/consolidado_lote1.md](04_RESULTADOS_FINANCEIROS/consolidado_lote1.md)")
    open(os.path.join(LAB, "INDICE.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # catálogo (uso)
    uso = {n: [] for n in NOMES_TRILHAS}
    for sid in sorted(R):
        for n in T[sid]["trilhas"]: uso[n].append(sid)
    L = ["# Catálogo de trilhas (v1)\n", "Trilhas são categorias; cada uma admite vários modelos de execução.\n", "| # | Trilha | Simulações que a usam |", "|---|---|---|"]
    for n in sorted(NOMES_TRILHAS): L.append(f"| {n} | {NOMES_TRILHAS[n]} | {', '.join(uso[n]) if uso[n] else '—'} |")
    open(os.path.join(LAB, "02_CATALOGO_DE_TRILHAS", "CATALOGO.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("ok", {k: round(equilibrio(k), 2) for k in sorted(R)})
    print("trilhas sem uso:", [n for n in uso if not uso[n]])
