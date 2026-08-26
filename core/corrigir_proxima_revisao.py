"""
corrigir_proxima_revisao.py — corrige um dado histórico incorreto em
estado_revisao: hoje (2026-08-26) todas as 82 linhas têm proxima_revisao
igual a ultima_tentativa (mesmo dia), em vez de ultima_tentativa +
intervalo_dias como a fórmula atual do Leitner realmente calcula.

Verificado que o CÓDIGO ATUAL (calcular_proxima_revisao/registrar_
tentativa em db.py) está certo — testei numa base isolada e uma
tentativa nova grava proxima_revisao um dia à frente, corretamente. O
problema é só nessas 82 linhas já gravadas, provavelmente por uma
versão anterior da lógica (não dá pra confirmar qual, não havia git
antes de hoje). Roda uma vez, lê top a baixo antes de rodar de novo —
mesmo padrão dos outros backfills deste projeto (ver classificar_2024.py).

Faz backup antes de mudar qualquer coisa. Idempotente: rodar de novo
numa base já corrigida não muda nada (recalcula e só teria efeito se
o valor estivesse errado de novo).
"""
from datetime import date, timedelta

import db
import backup_db

caminho_backup = backup_db.fazer_backup()
print(f"Backup criado: {caminho_backup.name}\n")

with db._conectar() as conn:
    linhas = conn.execute(
        "SELECT id_questao, intervalo_dias, ultima_tentativa, proxima_revisao FROM estado_revisao"
    ).fetchall()

    corrigidas = 0
    for id_q, intervalo, ultima, proxima_atual in linhas:
        proxima_correta = (date.fromisoformat(ultima) + timedelta(days=intervalo)).isoformat()
        if proxima_correta != proxima_atual:
            conn.execute(
                "UPDATE estado_revisao SET proxima_revisao = ? WHERE id_questao = ?",
                (proxima_correta, id_q),
            )
            corrigidas += 1

print(f"Corrigidas: {corrigidas} de {len(linhas)}")

with db._conectar() as conn:
    print("\nDistribuição de proxima_revisao depois da correção:")
    for row in conn.execute(
        "SELECT proxima_revisao, COUNT(*) FROM estado_revisao GROUP BY proxima_revisao ORDER BY 1"
    ):
        print(" ", row)

    hoje = date.today().isoformat()
    devidas_hoje = conn.execute(
        "SELECT COUNT(*) FROM estado_revisao WHERE proxima_revisao <= ?", (hoje,)
    ).fetchone()[0]
    print(f"\nQuestões devidas para revisão hoje ({hoje}): {devidas_hoje}")
