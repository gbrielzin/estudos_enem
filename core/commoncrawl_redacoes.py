"""Procura páginas de redação nota alta no índice do Common Crawl.

O Common Crawl varre a web todo mês e publica um índice aberto de URLs. Em vez
de visitar sites, consultamos esse índice por domínio (o servidor não aceita
"a internet inteira" de uma vez) com um filtro de URL, em vários meses de
coleta, e guardamos só a lista de URLs candidatas. Ler o HTML arquivado é um
passo separado (fica pra quando a lista mostrar que vale).

Uso (da pasta core/):
    python commoncrawl_redacoes.py ../docs/redacao_pesquisa/banco_1000/commoncrawl_urls.csv
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import time

INDICE = "https://index.commoncrawl.org/{colecao}-index"
COLECOES = ["CC-MAIN-2026-34", "CC-MAIN-2026-30", "CC-MAIN-2026-25", "CC-MAIN-2025-51"]
DOMINIOS = [
    "g1.globo.com", "querobolsa.com.br", "vestibulares.estrategia.com", "blog.imaginie.com.br", "coredacao.com",
    "www.redacaonline.com.br", "brasilescola.uol.com.br", "vestibular.brasilescola.uol.com.br", "www.todamateria.com.br",
    "educacao.uol.com.br", "www.cnnbrasil.com.br", "www.terra.com.br", "guiadoestudante.abril.com.br", "blogdoenem.com.br",
    "www.infoenem.com.br", "www.projetoredacao.com.br", "www.imaginie.com.br", "descomplica.com.br", "www.stoodi.com.br",
    "www.estuda.com", "estuda.com", "www.poliedro.com.br", "www.bernoulli.com.br", "www.correiobraziliense.com.br",
    "www.metropoles.com", "www.otempo.com.br", "agenciabrasil.ebc.com.br", "www.gov.br",
]
# URL com cara de redação de nota alta (900-1000)
FILTRO = r"~url:.*reda.*(9[0-8]0|nota-mil|nota-1000|nota-1-000|1000|nota-maxima).*"


def consultar(colecao: str, dominio: str, tentativas: int = 3) -> list[str]:
    """URLs do domínio que casam com o filtro nessa coleta. O índice às vezes
    responde 502/504 sob carga: tenta de novo e, se não der, devolve vazio."""
    for t in range(tentativas):
        r = subprocess.run(
            ["curl", "-s", "--max-time", "90", "-G", INDICE.format(colecao=colecao),
             "--data-urlencode", f"url={dominio}/*", "--data-urlencode", f"filter={FILTRO}",
             "--data-urlencode", "output=json", "--data-urlencode", "fl=url,status"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        corpo = r.stdout.strip()
        if corpo.startswith("{"):
            urls = []
            for linha in corpo.splitlines():
                try:
                    reg = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                if "url" in reg and reg.get("status", "200") == "200":
                    urls.append(reg["url"])
            return urls
        time.sleep(2 * (t + 1))
    return []


def normalizar_url(url: str) -> str:
    return re.sub(r"[?#].*$", "", url).rstrip("/").replace("http://", "https://")


def main(saida: str) -> None:
    achadas: dict[str, set[str]] = {}
    for dominio in DOMINIOS:
        total = 0
        for colecao in COLECOES:
            for url in consultar(colecao, dominio):
                achadas.setdefault(normalizar_url(url), set()).add(colecao)
                total += 1
        print(f"{dominio}: {total} capturas", file=sys.stderr)
    with open(saida, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url", "colecoes"])
        for url in sorted(achadas):
            w.writerow([url, " ".join(sorted(achadas[url]))])
    print(f"{len(achadas)} URLs únicas -> {saida}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
