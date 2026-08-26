"""
triagem.py — classifica manualmente as questões que ficaram
'nao_classificado' (matéria fora da taxonomia, ou sem vídeo pra puxar).

Não adivinha nada: mostra a matéria bruta (o que o título/CSV trouxe,
se trouxe algo) como pista, e quem decide a matéria final é a pessoa,
escolhendo de uma lista fechada -- mesma regra de sempre.

Toda classificação manual também é persistida em
gabaritos_reais/correcoes_manuais.csv, além de gravada no banco --
porque reconstruir_base.py apaga e recria enem.db do zero a partir só
dos CSVs de gabarito oficial, que nunca souberam da correção manual.
Sem esse CSV à parte, a triagem "voltava sozinha" toda vez que a base
era reconstruída.
"""
import csv
from pathlib import Path

import streamlit as st

import db

CAMINHO_CORRECOES = Path(__file__).parent / "gabaritos_reais" / "correcoes_manuais.csv"


def _salvar_correcao_manual(id_questao: str, materia: str) -> None:
    """Persiste a classificação manual num CSV à parte -- é a fonte
    que sobrevive a um reconstruir_base.py, que recria o banco do
    zero só a partir dos gabaritos oficiais e não sabe de nada que só
    existiu dentro do enem.db."""
    existentes = {}
    if CAMINHO_CORRECOES.exists():
        with open(CAMINHO_CORRECOES, encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                existentes[linha["id_questao"]] = linha["materia"]
    existentes[id_questao] = materia
    CAMINHO_CORRECOES.parent.mkdir(exist_ok=True)
    with open(CAMINHO_CORRECOES, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id_questao", "materia"])
        writer.writeheader()
        for id_q, mat in sorted(existentes.items()):
            writer.writerow({"id_questao": id_q, "materia": mat})


def render_triagem() -> None:
    pendentes = db.questoes_pendentes_classificacao()

    if not pendentes:
        st.success("Nada pendente de classificação agora.")
        return

    if st.button("🔄 Reclassificar com as regras atuais (roda antes de triar à mão)"):
        resultado = db.reclassificar_pendentes()
        st.success(
            f"{resultado['reclassificadas']} classificada(s) automaticamente. "
            f"{resultado['continuam_pendentes']} continuam pendentes (precisam de escolha manual)."
        )
        st.rerun()

    pendentes = db.questoes_pendentes_classificacao()
    if not pendentes:
        st.success("Tudo classificado agora.")
        return

    st.caption(f"{len(pendentes)} questão(ões) sem matéria classificada.")

    with st.form("form_triagem"):
        escolhas = {}
        for q in pendentes:
            grande_area = q["grande_area"] or "matematica"
            opcoes_materia = [""] + db.materias_validas(grande_area)
            col1, col2 = st.columns([2, 2])
            with col1:
                st.write(f"**{q['id_questao']}**")
                st.caption(f"matéria bruta: {q['materia_bruta']} ({grande_area})")
            with col2:
                escolhas[q["id_questao"]] = st.selectbox(
                    "Matéria correta", opcoes_materia,
                    key=f"triagem_{q['id_questao']}", label_visibility="collapsed",
                )
        salvar = st.form_submit_button("Salvar classificações", type="primary")

    if not salvar:
        return

    by_id = {q["id_questao"]: q for q in pendentes}
    salvos = 0
    for id_questao, materia_escolhida in escolhas.items():
        if not materia_escolhida:
            continue
        q = by_id[id_questao]
        db.inserir_questao(
            ano=q["ano"], caderno=q["caderno"], numero=q["numero_questao"],
            grande_area=q["grande_area"] or "matematica", materia=materia_escolhida,
            alternativa_correta=q["alternativa_correta"], sobrescrever=True,
        )
        _salvar_correcao_manual(id_questao, materia_escolhida)
        salvos += 1

    st.success(f"{salvos} questão(ões) classificada(s).")
    st.rerun()