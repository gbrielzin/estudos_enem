"""
reconstruir_base.py — carrega/atualiza o banco a partir de fontes
verificadas: gabarito oficial (PDF do INEP) + as respostas reais do
usuário na prova de Matemática 2019 + correções manuais de triagem já
feitas antes.

Pensado pra ser reexecutado sempre que houver gabarito novo —
idempotente: NÃO apaga enem.db (só faz backup e atualiza em cima do que
já existe), então rodar de novo não perde tentativa de outras provas
nem correção manual de triagem já feita.

############################################################
# Histórico: até 2026-08 este script apagava enem.db e reconstruía do
# zero. Verificado então que isso destruía de verdade: tentativas de
# qualquer prova fora do bloco hardcoded de 2019 abaixo, e matéria já
# corrigida manualmente na triagem (o rebuild antigo não repetia esse
# passo, então tudo voltava a pendente).
#
# A partir daqui: sem DELETE do banco. inicializar_banco() é
# idempotente por design (só CREATE TABLE IF NOT EXISTS). O passo de
# tentativas de 2019 confere o que já existe antes de inserir, pra
# rodar de novo sem duplicar. Ainda assim faz backup automático no
# início, porque "idempotente na teoria" não vale tanto quanto ter um
# arquivo pra voltar caso algo saia diferente do esperado.
#
# 2026-09-15: removido o passo que ligava resoluções em vídeo a partir
# de questoes_enem.csv (scraping de canal do YouTube) -- descontinuado
# por decisão de produto (ver adr/0008-descontinuar-vinculo-youtube.md).
# O arquivo questoes_enem.csv foi removido do repositório junto.
############################################################
"""
import csv
import glob
import re
from pathlib import Path

import db
import backup_db

PASTA = Path(__file__).parent
db.DB_PATH = PASTA / "enem.db"

if db.DB_PATH.exists():
    caminho_backup = backup_db.fazer_backup()
    print(f"Backup de segurança criado antes de atualizar: {caminho_backup.name}\n")

db.inicializar_banco()

# ============================================================
# 1. GABARITO OFICIAL (2019-2025)
# ============================================================
print("=== Carregando gabarito oficial ===")
resumo_total = {"classificadas": 0, "nao_classificadas": 0}

for caminho in sorted(glob.glob(str(PASTA / "gabaritos_reais" / "gabarito_*_OFICIAL.csv"))):
    nome = Path(caminho).stem
    if "_CIENCIAS_" in nome:
        # Padrão: gabarito_<ano>_<caderno>_CIENCIAS_OFICIAL.csv -- mesma
        # prova/caderno da Matemática daquele ano, só que grande_area
        # ciencias_natureza. Trata à parte pra não confundir "CIENCIAS"
        # com o nome do caderno no regex genérico abaixo.
        m = re.match(r"gabarito_(\d{4})_(\w+)_CIENCIAS_OFICIAL", nome)
        ano, caderno, area = int(m.group(1)), m.group(2), "ciencias_natureza"
        resumo = db.carregar_gabarito_csv(
            caminho, ano=ano, caderno=caderno, grande_area_padrao=area, sobrescrever=True,
            preservar_materia_classificada=True,
        )
    else:
        m = re.match(r"gabarito_(\d{4})_(\w+)_OFICIAL", nome)
        ano, caderno, area = int(m.group(1)), m.group(2), "matematica"
        resumo = db.carregar_gabarito_csv(
            caminho, ano=ano, caderno=caderno, sobrescrever=True,
            preservar_materia_classificada=True,
        )
    resumo_total["classificadas"] += resumo["classificadas"]
    resumo_total["nao_classificadas"] += len(resumo["nao_classificadas"])
    print(f"  {ano} ({caderno}, {area}): {resumo['classificadas']} classificadas, "
          f"{len(resumo['nao_classificadas'])} em triagem, {len(resumo['erros'])} erro(s)")

print(f"TOTAL: {resumo_total['classificadas']} classificadas, {resumo_total['nao_classificadas']} em triagem")

# ============================================================
# 1b. REAPLICA CORREÇÕES MANUAIS DE TRIAGEM (sobrevivem à reconstrução)
# ============================================================
# triagem.py grava aqui toda vez que você classifica uma questão à mão
# na tela de Triagem. Sem isso, a reconstrução acima recria o banco só
# a partir dos CSVs de gabarito oficial -- que nunca souberam da sua
# correção manual -- e a questão volta pra 'nao_classificado' como se
# a triagem nunca tivesse acontecido.
caminho_correcoes = PASTA / "gabaritos_reais" / "correcoes_manuais.csv"
if caminho_correcoes.exists():
    print("\n=== Reaplicando correções manuais de triagem ===")
    aplicadas, nao_encontradas = 0, 0
    with open(caminho_correcoes, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            with db._conectar() as conn:
                atual = conn.execute(
                    "SELECT ano, caderno, numero_questao, grande_area, alternativa_correta "
                    "FROM questoes WHERE id_questao=?", (linha["id_questao"],),
                ).fetchone()
            if atual is None:
                nao_encontradas += 1
                continue
            ano, caderno, numero, grande_area, gabarito = atual
            db.inserir_questao(
                ano=ano, caderno=caderno, numero=numero, grande_area=grande_area,
                materia=linha["materia"], alternativa_correta=gabarito, sobrescrever=True,
            )
            aplicadas += 1
    print(f"  {aplicadas} correção(ões) manual(is) reaplicada(s).")
    if nao_encontradas:
        print(f"  {nao_encontradas} correção(ões) ignorada(s) — questão não existe mais na base atual.")
else:
    print("\n(nenhum correcoes_manuais.csv encontrado ainda — sem correção manual pra reaplicar)")

# ============================================================
# 2. TENTATIVAS REAIS -- Matemática 2019, do gabarito consolidado do usuário
# ============================================================
print("\n=== Registrando tentativas reais (Matemática 2019) ===")

# Questões onde o usuário ACERTOU (resposta = gabarito, por definição)
acertou = [138, 139, 140, 141, 143, 144, 147, 149, 150, 151, 152, 153,
           155, 160, 162, 163, 165, 166, 169, 174, 176, 180]

# Questões onde ERROU, com a alternativa que o usuário marcou (confirmada
# por ele OU resolvida agora contra o gabarito oficial que já tínhamos
# para 159/164/167, que ele ainda marcava como "a confirmar")
errou = {
    142: "A", 145: "E", 148: "A", 156: "A", 158: "D", 161: "A",
    168: "E", 170: "A", 171: "A", 172: "C", 173: "A", 175: "E",
    159: "A", 164: "A", 167: "D",
}

# Ficam de fora, sem inventar resposta: 136, 137(pulou), 146, 154(pulou),
# 157, 178 -- sem alternativa registrada. 177, 179 -- resposta "2"/"5"
# não é uma alternativa A-E válida, não vou adivinhar qual letra era.

# tentativas_usuario é append-only (sem chave única) -- sem essa checagem,
# rodar este script de novo empilharia as mesmas 37 tentativas a cada
# execução. Marcador: se QUALQUER uma das questões do bloco "acertou"
# já tem tentativa registrada, assume que esse backfill já rodou antes
# e pula o bloco inteiro (idempotente por "já rodou", não por linha).
id_marcador = db.gerar_id_canonico(2019, "Azul", acertou[0])
with db._conectar() as conn:
    ja_rodou = conn.execute(
        "SELECT 1 FROM tentativas_usuario WHERE id_questao = ? LIMIT 1", (id_marcador,)
    ).fetchone()

if ja_rodou:
    print("  Backfill de 2019 já tinha rodado antes (tentativas já existem) -- pulando pra não duplicar.")
else:
    registradas, falharam = 0, []
    for numero in acertou:
        id_q = db.gerar_id_canonico(2019, "Azul", numero)
        with db._conectar() as conn:
            gabarito = conn.execute(
                "SELECT alternativa_correta FROM questoes WHERE id_questao=?", (id_q,)
            ).fetchone()
        if not gabarito:
            falharam.append(numero)
            continue
        db.registrar_tentativa(id_q, gabarito[0])
        registradas += 1

    for numero, resposta in errou.items():
        id_q = db.gerar_id_canonico(2019, "Azul", numero)
        try:
            db.registrar_tentativa(id_q, resposta)
            registradas += 1
        except ValueError:
            falharam.append(numero)

    print(f"  Tentativas registradas: {registradas} (esperado: 37)")
    print(f"  Falharam (questão não encontrada): {falharam}")
    print(f"  Fora do escopo, sem resposta confiável: 136, 137, 146, 154, 157, 178, 177(?), 179(?) -- 8 questões")

# ============================================================
# 3. VERIFICAÇÃO FINAL
# ============================================================
print("\n=== Verificação ===")
with db._conectar() as conn:
    total_questoes = conn.execute("SELECT COUNT(*) FROM questoes").fetchone()[0]
    total_resolucoes = conn.execute("SELECT COUNT(*) FROM resolucoes").fetchone()[0]
    total_tentativas = conn.execute("SELECT COUNT(*) FROM tentativas_usuario").fetchone()[0]
    nao_classificadas = conn.execute(
        "SELECT COUNT(*) FROM questoes WHERE status_classificacao='nao_classificado'"
    ).fetchone()[0]

print(f"questoes: {total_questoes} | resolucoes: {total_resolucoes} | "
      f"tentativas_usuario: {total_tentativas} | nao_classificado: {nao_classificadas}")

print("\n=== Sua prioridade de estudo real (não mais simulada) ===")
for area in ("matematica", "ciencias_natureza"):
    print(f"-- {area} --")
    prioridade = db.prioridade_de_estudo(area)
    if not prioridade["ranking"]:
        print("  (sem tentativas suficientes nessa área ainda)")
    for r in prioridade["ranking"]:
        aviso = " (amostra pequena)" if r["amostra_pequena"] else ""
        print(f"  {r['materia']}: recorrência {r['percentual_recorrencia']}% | "
              f"seu acerto {r['taxa_acerto_pct']}% ({r['total_tentativas']} tent.) | "
              f"prioridade {r['score_prioridade']}{aviso}")