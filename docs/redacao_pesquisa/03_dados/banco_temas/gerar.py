"""Lê temas.txt, confere os campos e gera temas.json + padroes.md (contagem do banco de temas)."""
import json
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).parent
CAMPOS = ["tema", "eixo", "nucleo", "grupo", "direito", "falha", "cena_d1", "juizo_d1",
          "atitude", "lugar", "cena_d2", "juizo_d2", "agente", "acao"]
FALHAS = {"N": "não existe na cidade", "F": "fila/espera", "P": "sem profissional",
          "L": "lei sem fiscalização", "E": "escola não ensina"}

temas = []
for n, linha in enumerate((AQUI / "temas.txt").read_text(encoding="utf-8").splitlines(), 1):
    if not linha.strip() or linha.startswith("#"):
        continue
    partes = linha.split("|")
    if len(partes) != len(CAMPOS):
        raise SystemExit(f"linha {n}: {len(partes)} campos")
    t = dict(zip(CAMPOS, partes))
    if t["falha"] not in FALHAS:
        raise SystemExit(f"linha {n}: falha {t['falha']}")
    t["id"] = len(temas) + 1
    temas.append(t)

(AQUI / "temas.json").write_text(json.dumps(temas, ensure_ascii=False, indent=1), encoding="utf-8")

linhas = [f"# Padrões do banco de temas ({len(temas)} temas)\n",
          "Gerado por `gerar.py` a partir de `temas.txt`. As respostas são minhas (modelo do Gabriel), não do INEP.\n"]
for campo, rotulo in [("eixo", "Eixo"), ("direito", "Direito do D1"), ("falha", "Falha do Estado (D1)"),
                      ("atitude", "Atitude do D2"), ("lugar", "Lugar da cena do D2"), ("agente", "Agente da proposta")]:
    c = Counter(FALHAS[t[campo]] if campo == "falha" else t[campo] for t in temas)
    linhas.append(f"\n## {rotulo}\n\n| | Temas |\n|---|---|")
    linhas += [f"| {k} | {v} |" for k, v in c.most_common()]
(AQUI / "padroes.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print(len(temas), "temas")
