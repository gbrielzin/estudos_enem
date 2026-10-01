"""preparar_servidor.py — roda antes da API subir na hospedagem (ver
Dockerfile e docs/DEPLOY.md).

Para cada pessoa em API_USUARIOS que ainda não tem banco na pasta
API_PASTA_BANCOS (o volume persistente), cria o banco a partir de
banco_semente.db: as questões, sem nenhum dado pessoal (gerado com
`python criar_banco_usuario.py banco_semente --pasta .`). Banco que já
existe nunca é tocado: é o histórico da pessoa.

Depois, em TODOS os bancos (novos e antigos), aplica as migrações e
sincroniza as explicações de core/explicacoes/explicacoes.jsonl (ver
explicacoes.py) -- é assim que explicação nova chega a quem já usa.
"""
from pathlib import Path

import api
import criar_banco_usuario
import db
import explicacoes

SEMENTE = Path(__file__).parent / "banco_semente.db"


def preparar() -> list[str]:
    criados = []
    for nome in api.usuarios_configurados().values():
        caminho = api.caminho_banco_usuario(nome)
        if not caminho.exists():
            criar_banco_usuario.criar_banco(nome, caminho.parent, origem=SEMENTE)
            criados.append(nome)
        with db.usar_banco(caminho):
            db.inicializar_banco()
            explicacoes.sincronizar()
            # Bancos de quem usa pelo site seguem a trilha da semana (db.TRILHA_SEMANA_NOS),
            # a não ser que alguém já tenha escolhido outra para aquele banco.
            if db.obter_configuracao("trilha_ativa") is None:
                db.definir_configuracao("trilha_ativa", "semana")
    return criados


if __name__ == "__main__":
    criados = preparar()
    print(f"Bancos criados: {', '.join(criados) or 'nenhum (todos já existiam)'}.")
