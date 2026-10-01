"""criar_banco_usuario.py — cria o banco de uma pessoa nova para a API
com várias pessoas (ver adr/0010 e api.usuarios_configurados()).

Copia o enem.db (questões, gabaritos, enunciados, parâmetros TRI,
resoluções) e APAGA tudo que é pessoal de quem já usa: tentativas,
fila de revisão, redações, nomes de simulado, relatos e o histórico de
correções. Também zera o "motivo pessoal" das configurações. O banco
novo começa como o de alguém que nunca respondeu nada.

Não sobrescreve um banco que já existe (perderia o histórico da pessoa)
sem --sobrescrever.

Uso (de dentro de core/):
    python criar_banco_usuario.py amigo1                 # cria bancos/amigo1.db
    python criar_banco_usuario.py amigo1 --pasta /data   # outra pasta (ex: volume da hospedagem)
"""
import argparse
import re
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

import db

TABELAS_PESSOAIS = (
    "tentativas_usuario", "estado_revisao", "redacoes", "nomes_tentativas",
    "relatos_questao", "historico_alteracoes",
)
CONFIGURACOES_PESSOAIS = ("motivo_pessoal", "data_inicio_plano")


def criar_banco(nome: str, pasta: Path, origem: Path | None = None, sobrescrever: bool = False) -> Path:
    if not re.fullmatch(r"[a-z0-9_]{1,40}", nome):
        raise SystemExit("Nome só com a-z, 0-9 e _ (é o mesmo nome usado em API_USUARIOS).")
    origem = origem or db.DB_PATH
    destino = pasta / f"{nome}.db"
    if destino.exists() and not sobrescrever:
        raise SystemExit(f"{destino} já existe -- não sobrescrevo o histórico de ninguém (use --sobrescrever).")
    pasta.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".tmp")
    shutil.copy2(origem, temporario)
    with closing(sqlite3.connect(temporario)) as conn, conn:
        tabelas = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for tabela in TABELAS_PESSOAIS:
            if tabela in tabelas:
                conn.execute(f"DELETE FROM {tabela}")
        if "sqlite_sequence" in tabelas:
            # o contador de AUTOINCREMENT entregaria quantas tentativas/redações o dono já fez
            conn.executemany("DELETE FROM sqlite_sequence WHERE name = ?", [(t,) for t in TABELAS_PESSOAIS])
        if "configuracoes" in tabelas:
            conn.executemany("DELETE FROM configuracoes WHERE chave = ?", [(c,) for c in CONFIGURACOES_PESSOAIS])
    with closing(sqlite3.connect(temporario)) as conn:
        conn.execute("VACUUM")  # não deixa dado apagado sobrando nas páginas livres do arquivo
    temporario.replace(destino)
    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("nome")
    parser.add_argument("--pasta", type=Path, default=Path(__file__).parent / "bancos")
    parser.add_argument("--origem", type=Path, default=None)
    parser.add_argument("--sobrescrever", action="store_true")
    args = parser.parse_args()
    destino = criar_banco(args.nome, args.pasta, args.origem, args.sobrescrever)
    with closing(sqlite3.connect(destino)) as conn:
        n = conn.execute("SELECT COUNT(*) FROM questoes").fetchone()[0]
    print(f"Criado {destino} com {n} questões e nenhum dado pessoal.")


if __name__ == "__main__":
    main()
