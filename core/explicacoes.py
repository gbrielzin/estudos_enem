"""explicacoes.py — explicações de questão ("por que essa resposta e por
que cada alternativa errada atrai"), versionadas no repositório e
copiadas para o banco de cada pessoa.

Fonte única: core/explicacoes/explicacoes.jsonl, uma linha por questão:
    {"id_questao": "2022_azul_91", "texto": "...", "modelo": "...", "data": "AAAA-MM-DD"}
Gerada uma vez (por IA, com o gabarito oficial no contexto) e reaproveitada
por todo mundo -- ver adr/0010 e docs/ideias_melhorias.md.

Grava em `resolucoes` (tipo='texto', canal=CANAL), que o app já mostra em
"Por que essa resposta" depois de responder. Sincronizar é idempotente:
a explicação de canal CANAL da questão é SUBSTITUÍDA pela do arquivo (uma
correção no arquivo chega em todo banco), e resolução escrita à mão
(outro canal) nunca é tocada. Questão que não existe no banco é pulada.

Quem chama: preparar_servidor.py (a cada deploy, para cada pessoa) e,
localmente, `python explicacoes.py` (grava no enem.db).
"""
import json
import sys
from pathlib import Path

import db

ARQUIVO = Path(__file__).parent / "explicacoes" / "explicacoes.jsonl"
CANAL = "explicacao_ia"


def ler(caminho: Path | None = None) -> dict[str, str]:
    """{id_questao: texto}. Linha repetida para a mesma questão: vale a última."""
    caminho = caminho or ARQUIVO
    explicacoes = {}
    if not caminho.exists():
        return explicacoes
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        if not linha.strip():
            continue
        registro = json.loads(linha)
        if not registro.get("id_questao") or not (registro.get("texto") or "").strip():
            raise ValueError(f"{caminho.name}:{numero}: precisa de id_questao e texto")
        explicacoes[registro["id_questao"]] = registro["texto"].strip()
    return explicacoes


def sincronizar(caminho: Path | None = None) -> tuple[int, int]:
    """Grava no banco atual (db.caminho_banco()). Devolve (gravadas, puladas)."""
    gravadas = puladas = 0
    with db._conectar() as conn:
        existentes = {r[0] for r in conn.execute("SELECT id_questao FROM questoes")}
        atuais = dict(conn.execute(
            "SELECT id_questao, conteudo FROM resolucoes WHERE tipo = 'texto' AND canal = ?", (CANAL,)
        ))
        for id_questao, texto in ler(caminho).items():
            if id_questao not in existentes:
                puladas += 1
                continue
            if atuais.get(id_questao) == texto:
                continue
            conn.execute(
                "DELETE FROM resolucoes WHERE id_questao = ? AND tipo = 'texto' AND canal = ?", (id_questao, CANAL)
            )
            conn.execute(
                "INSERT INTO resolucoes (id_questao, tipo, conteudo, canal) VALUES (?, 'texto', ?, ?)",
                (id_questao, texto, CANAL),
            )
            gravadas += 1
    return gravadas, puladas


if __name__ == "__main__":
    db.inicializar_banco()
    gravadas, puladas = sincronizar()
    print(f"{len(ler())} explicações no arquivo: {gravadas} gravadas/atualizadas, {puladas} sem questão no banco.")
    sys.exit(0)
