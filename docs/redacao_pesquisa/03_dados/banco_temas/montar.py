"""Monta D1, D2 e conclusão dos temas com o modelo e testa cada lacuna (hipóteses de padrão)."""
import json, re
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
temas = json.loads((AQUI / "temas.json").read_text(encoding="utf-8"))
CRASE = {"educação": "à", "saúde": "à", "alimentação": "à", "moradia": "à", "segurança": "à",
         "informação": "à", "cultura": "à", "trabalho": "ao", "lazer": "ao", "transporte": "ao"}
ATITUDE = {"preconceito": "o preconceito", "desinformação": "a desinformação",
           "indiferença": "a indiferença", "naturalização": "o conformismo"}
MEIO = {"Ministério da Educação": "órgão responsável pela formação cidadã e pela difusão de valores na sociedade",
        "Governo Federal": "instância responsável pela gestão das políticas públicas nacionais"}

def sem_pronome(juizo, grupo):  # o juízo começa pelo grupo, não por "ele/ela" (referente ambíguo)
    return re.sub(r"^(ele|ela) ", grupo + " ", juizo)

saida, testes = [], Counter()
for t in temas:
    g, d = t["grupo"], t["direito"]
    plural = g.split()[0] in ("os", "as")
    testes["grupo no plural"] += plural
    testes["cena D1 com 'tenta … mas'"] += bool(re.search(r"\btenta\b.*\bmas\b", t["cena_d1"]))
    testes["cena D1 com 'mas'"] += " mas " in t["cena_d1"]
    testes["ação começa com verbo no infinitivo"] += bool(re.match(r"\w+r\b", t["acao"]))
    testes[f"agente {t['agente']} | falha {t['falha']}"] += 1
    d1 = (f"Em primeira análise, é imperativo correlacionar a problemática que envolve {t['nucleo']} à omissão do Poder Público. "
          "De fato, essa postura estatal reflete a tese do jornalista Gilberto Dimenstein, em sua obra \"O Cidadão de Papel\", "
          "na qual o autor argumenta que os direitos previstos em lei frequentemente não se aplicam à realidade prática. "
          f"Prova disso é que {t['cena_d1']}. Dessa forma, o direito {CRASE[d]} {d}, garantido pela Constituição, não chega a uma parcela significativa da população. "
          f"Tal omissão é grave, pois {sem_pronome(t['juizo_d1'], g)}.")
    d2 = (f"Ademais, é igualmente preciso apontar {ATITUDE[t['atitude']]} do corpo social como fator agravante dessa problemática. "
          "Nesse contexto, Noam Chomsky, em \"A Fabricação do Consenso\", defende que estruturas hegemônicas moldam a opinião pública para gerar passividade e conformidade. "
          f"Exemplo disso ocorre quando {t['cena_d2']}. Dessa maneira, esse problema passa a ser tratado como algo normal. "
          f"Tal postura é grave, uma vez que {sem_pronome(t['juizo_d2'], g)}.")
    meio = ("palestras, oficinas e material didático" if t["agente"] == "Ministério da Educação"
            else "da destinação de verbas e de parcerias com estados e municípios")
    conc = (f"Portanto, medidas urgentes são necessárias para mitigar esse impasse. Para tanto, o {t['agente']}, {MEIO[t['agente']]}, "
            f"deve {t['acao']}, por meio de {meio}, para que {g} {'tenham' if plural else 'tenha'} acesso efetivo {CRASE[d]} {d} e, "
            f"consequentemente, o corpo social supere {ATITUDE[t['atitude']]}. Com essas ações, o Brasil poderá, finalmente, afastar-se do cenário de "
            "\"cidadão de papel\" e consolidar a dignidade garantida pela Constituição Federal de 1988.")
    conc = conc.replace("por meio de da", "por meio da")
    saida.append(f"## {t['id']}. {t['tema']}\n\n**D1.** {d1}\n\n**D2.** {d2}\n\n**Conclusão.** {conc}\n")

(AQUI / "redacoes_montadas.md").write_text("# 109 temas montados no modelo (gerado por montar.py)\n\n" + "\n".join(saida), encoding="utf-8")
for k, v in sorted(testes.items()):
    print(f"{v:4d}  {k}")
