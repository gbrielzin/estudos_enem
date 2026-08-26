"""
cartao_resposta.py — MVP do cartão-resposta digital.

Fluxo: escolhe uma prova já cadastrada -> marca A/B/C/D/E por questão
-> corrige contra o gabarito em questoes -> grava em
tentativas_usuario e agenda a próxima revisão (Leitner), tudo via
registrar_tentativa() do db.py. Não duplica nenhuma lógica de correção
aqui — a tela só coleta e mostra.

Pré-requisito: a prova (ano+caderno) já precisa ter as questões
inseridas via inserir_questao() (com gabarito), senão não aparece
no seletor. Este arquivo não cadastra questão nenhuma.

Rodar isolado:  streamlit run cartao_resposta.py
Ou copiar o conteúdo da função render_cartao_resposta() como uma
nova aba dentro do app.py existente, junto das outras abas.
"""

import os
import tempfile
from datetime import date, datetime
from pathlib import Path

import streamlit as st

import db
import coletar_videos
import triagem
import backup_db
import ui_theme


def render_carregar_gabarito() -> None:
    with st.expander("➕ Carregar gabarito de uma prova nova (CSV)"):
        st.caption("Colunas obrigatórias: numero, materia, gabarito. Opcional: grande_area.")
        col1, col2, col3 = st.columns(3)
        with col1:
            ano = st.number_input("Ano da prova", min_value=2009, max_value=2100, value=2024, step=1)
        with col2:
            caderno = st.text_input("Caderno", value="Azul")
        with col3:
            grande_area = st.selectbox("Grande área padrão", ["matematica", "ciencias_natureza"])
        arquivo = st.file_uploader("Arquivo CSV", type="csv")
        if arquivo is not None and st.button("Carregar"):
            with tempfile.TemporaryDirectory() as pasta_temp:
                caminho_temp = os.path.join(pasta_temp, arquivo.name)
                with open(caminho_temp, "wb") as f:
                    f.write(arquivo.getbuffer())
                try:
                    resumo = db.carregar_gabarito_csv(caminho_temp, ano=int(ano), caderno=caderno, grande_area_padrao=grande_area)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.success(f"{resumo['classificadas']} questão(ões) classificada(s).")
                    if resumo["nao_classificadas"]:
                        st.warning(
                            f"{len(resumo['nao_classificadas'])} foram pra triagem (matéria fora da taxonomia): "
                            + ", ".join(resumo["nao_classificadas"])
                        )
                    if resumo["erros"]:
                        st.error("Linhas com erro: " + "; ".join(resumo["erros"]))
                    st.rerun()


RÓTULO_AREA = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}


def render_cartao_resposta() -> None:
    db.inicializar_banco()
    render_carregar_gabarito()

    provas = db.listar_provas()
    if not provas:
        st.info("Nenhuma prova cadastrada ainda — insira questões (com gabarito) antes de responder.")
        return

    modo = st.radio(
        "Modo",
        ["Uma prova por vez", "Simulado completo (Matemática + Ciências)",
         "Revisão de hoje", "Praticar por matéria"],
        horizontal=True,
    )

    if modo == "Simulado completo (Matemática + Ciências)":
        _render_simulado_completo()
        return

    if modo == "Revisão de hoje":
        render_revisao_hoje()
        return

    if modo == "Praticar por matéria":
        render_praticar_por_materia()
        return

    areas_disponiveis = sorted({area for _, _, area in provas})
    area_sel = st.radio(
        "Área", areas_disponiveis, format_func=lambda a: RÓTULO_AREA.get(a, a), horizontal=True,
    )

    opcoes = {
        f"{ano} — {caderno}": (ano, caderno, area)
        for ano, caderno, area in provas
        if area == area_sel
    }
    if not opcoes:
        st.info(f"Nenhuma prova de {RÓTULO_AREA.get(area_sel, area_sel)} cadastrada ainda.")
        return
    escolha = st.selectbox("Prova", list(opcoes.keys()))
    ano_sel, caderno_sel, area_sel = opcoes[escolha]

    _renderizar_bloco_prova(ano_sel, caderno_sel, area_sel)


def _render_simulado_completo() -> None:
    """Faz Matemática e Ciências da Natureza do mesmo ano em sequência,
    cada uma na sua aba. Corrige, guarda e mostra o resultado de cada
    área separadamente — nunca mistura as duas na mesma grade nem no
    mesmo cálculo, mesma regra do resto do sistema. Cada área usa o
    PRÓPRIO caderno (ver db.simulados_completos_disponiveis) -- 2023
    é matemática/Azul + ciências/Cinza, cadernos diferentes no mesmo
    ano, um padrão real do INEP que a versão antiga desta função
    (agrupava por ano+caderno igual pras duas áreas) deixava invisível."""
    combinacoes = db.simulados_completos_disponiveis()
    if not combinacoes:
        st.info(
            "Nenhum ano tem as duas áreas cadastradas ainda — "
            "o simulado completo só aparece quando Matemática e Ciências "
            "da mesma prova já foram carregadas."
        )
        return

    opcoes = {f"{c['ano']}": c for c in combinacoes}
    escolha = st.selectbox("Simulado", list(opcoes.keys()))
    combo = opcoes[escolha]

    aba_mat, aba_ciencias = st.tabs(["📐 Matemática", "🔬 Ciências da Natureza"])
    with aba_mat:
        _renderizar_bloco_prova(combo["ano"], combo["caderno_matematica"], "matematica")
    with aba_ciencias:
        _renderizar_bloco_prova(combo["ano"], combo["caderno_ciencias"], "ciencias_natureza")


def _renderizar_bloco_prova(ano_sel: int, caderno_sel: str, area_sel: str) -> None:
    """Corpo real da tela de responder + corrigir UMA PROVA INTEIRA.
    Recebe a área como parâmetro (em vez de pegar de um seletor
    global) pra poder ser chamada duas vezes na mesma página, uma por
    aba, no modo simulado completo — por isso toda chave de widget/
    session_state aqui dentro é sufixada com ano+caderno+área, senão
    colidiria."""
    sufixo = f"{ano_sel}_{caderno_sel}_{area_sel}"

    questoes = db.listar_questoes_da_prova(ano_sel, caderno_sel, area_sel)
    if not questoes:
        st.info("Essa prova não tem questões cadastradas.")
        return

    n_triagem = sum(1 for q in questoes if q["status_classificacao"] == "nao_classificado")
    st.caption(
        f"{len(questoes)} questões cadastradas."
        + (f" {n_triagem} com matéria não classificada (⚠️)." if n_triagem else "")
    )

    historico = db.resumo_por_tentativa(ano_sel, caderno_sel, area_sel)
    if historico:
        with st.expander(f"📈 Histórico de tentativas dessa prova ({len(historico)})", expanded=True):
            for h in historico:
                pct = f"{h['taxa_acerto']*100:.0f}%" if h["taxa_acerto"] is not None else "—"
                st.write(f"**Tentativa {h['tentativa']}**: {h['acertos']}/{h['total']} ({pct}) — {h['inicio'][:10]}")

    _renderizar_grade_questoes(questoes, sufixo)


def render_revisao_hoje() -> None:
    """Fila do dia estilo Anki: só questões cuja proxima_revisao (do
    Leitner simplificado) já chegou. Mistura anos/áreas de propósito
    -- o ponto é revisar o que está atrasado, não fingir que é uma
    prova única."""
    ids = db.questoes_para_revisar()
    if not ids:
        st.success("Nada atrasado pra revisão hoje. 🎉")
        st.caption("Isso só cobre questão já respondida ao menos uma vez — a fila enche conforme você usa o cartão-resposta.")
        return

    st.caption(f"{len(ids)} questão(ões) atrasada(s), das mais atrasadas pras mais recentes.")
    questoes = db.questoes_por_ids(ids)
    _renderizar_grade_questoes(questoes, sufixo="revisao_hoje")


def render_praticar_por_materia() -> None:
    """Pega a matéria mais fraca do painel 'Minha análise' e transforma
    em prática de verdade, misturando questões de qualquer ano/prova
    -- sem isso, 'Prioridade de estudo' é só diagnóstico que não dá pra
    agir em cima na hora."""
    area_sel = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True, key="praticar_materia_area",
    )
    materias = db.materias_validas(area_sel)
    if not materias:
        st.info("Nenhuma matéria válida cadastrada pra essa área.")
        return

    materia_sel = st.selectbox("Matéria", materias, key="praticar_materia_sel")
    questoes = db.questoes_por_materia(area_sel, materia_sel)
    if not questoes:
        st.info(f"Nenhuma questão classificada como '{materia_sel}' ainda.")
        return

    anos = sorted({q["ano"] for q in questoes}, reverse=True)
    st.caption(f"{len(questoes)} questão(ões) de {materia_sel}, de {len(anos)} prova(s) ({', '.join(str(a) for a in anos)}).")
    _renderizar_grade_questoes(questoes, sufixo=f"materia_{area_sel}_{materia_sel}")


def _renderizar_grade_questoes(questoes: list[dict], sufixo: str) -> None:
    """Núcleo compartilhado por prova única, simulado, revisão do dia
    e prática por matéria: grade de resposta A-E, correção contra o
    gabarito via registrar_tentativa(), classificação de erro e vídeo
    de resolução. Todo mundo que monta uma lista de questões (não
    importa a origem) cai aqui — não duplica essa lógica em cada modo."""
    _renderizar_editor_enunciado(questoes, sufixo)

    with st.expander("⚡ Preenchimento rápido (cola a sequência de letras)"):
        st.caption(
            "Cola as letras na ordem das questões, sem espaço nem pontuação (ex: ABCDEBAACD...). "
            "Use * ou deixa em branco pra pular uma questão que você não respondeu."
        )
        sequencia = st.text_input("Sequência de respostas", key=f"sequencia_rapida_{sufixo}")
        if st.button("Aplicar sequência", key=f"aplicar_seq_{sufixo}"):
            aplicadas = 0
            for i, q in enumerate(questoes):
                if i < len(sequencia) and sequencia[i].upper() in "ABCDE":
                    st.session_state[f"resp_{q['id_questao']}"] = sequencia[i].upper()
                    aplicadas += 1
            st.success(f"{aplicadas} resposta(s) aplicada(s) — confere a grade abaixo antes de corrigir.")

    mostrar_ano = len({q["ano"] for q in questoes}) > 1

    with st.form(f"cartao_resposta_form_{sufixo}"):
        cols = st.columns(3)
        for i, q in enumerate(questoes):
            with cols[i % 3]:
                rotulo = f"Q{q['numero_questao']} · {q['ano']}" if mostrar_ano else f"Q{q['numero_questao']}"
                if q["status_classificacao"] == "nao_classificado":
                    rotulo += " ⚠️"
                st.radio(
                    rotulo,
                    ["—", "A", "B", "C", "D", "E"],
                    horizontal=True,
                    key=f"resp_{q['id_questao']}",
                )
                _mostrar_enunciado_leitura(q)
        enviado = st.form_submit_button("Corrigir", type="primary")

    chave_resultado = f"resultados_{sufixo}"

    if enviado:
        respostas = {
            q["id_questao"]: st.session_state[f"resp_{q['id_questao']}"]
            for q in questoes
            if st.session_state.get(f"resp_{q['id_questao']}", "—") != "—"
        }
        if not respostas:
            st.warning("Marque pelo menos uma resposta antes de corrigir.")
            return
        st.session_state[chave_resultado] = [
            db.registrar_tentativa(id_q, resp) for id_q, resp in respostas.items()
        ]

    resultados = st.session_state.get(chave_resultado)
    if not resultados:
        return

    acertos = sum(1 for r in resultados if r["resultado"] == "acertou")
    total = len(resultados)

    st.success(f"{acertos}/{total} acertos ({acertos / total * 100:.0f}%)")

    erros = [r for r in resultados if r["resultado"] == "errou"]
    if erros:
        with st.expander(f"⚠️ {len(erros)} questão(ões) errada(s) — já agendadas pra revisão", expanded=True):
            for r in erros:
                st.write(f"**{r['id_questao']}** — próxima revisão: {r['proxima_revisao']}")

                opcoes_erro = ["—"] + list(db.TIPOS_ERRO.values())
                escolha_erro = st.selectbox(
                    "Por que errou? (opcional)", opcoes_erro,
                    key=f"tipo_erro_{r['id_tentativa']}", label_visibility="collapsed",
                )
                if escolha_erro != "—":
                    chave_tipo = next(k for k, v in db.TIPOS_ERRO.items() if v == escolha_erro)
                    db.atualizar_tipo_erro(r["id_tentativa"], chave_tipo)

                resolucoes = db.resolucoes_da_questao(r["id_questao"])
                if not resolucoes:
                    st.caption("Sem vídeo de resolução ligado a essa questão ainda.")
                for res in resolucoes:
                    if res["tipo"] == "video":
                        st.video(res["conteudo"])
                    else:
                        st.caption(f"Resolução em texto ({res['canal'] or 'sem canal'}): {res['conteudo']}")

    if total < len(questoes):
        st.caption(f"{len(questoes) - total} questão(ões) não foi(ram) respondida(s) e não entrou(aram) no cálculo.")


PASTA_ENUNCIADOS = Path(__file__).parent / "enunciados"


def _mostrar_enunciado_leitura(q: dict) -> None:
    """Exibição só-leitura dentro da grade (dentro do st.form — por
    isso não tem botão nenhum aqui, só texto/imagem)."""
    texto = q.get("enunciado_texto")
    imagem = q.get("enunciado_imagem_path")
    if not texto and not imagem:
        return
    with st.expander("📄 Enunciado"):
        if texto:
            st.write(texto)
        if imagem and Path(imagem).exists():
            st.image(imagem)


def _renderizar_editor_enunciado(questoes: list[dict], sufixo: str) -> None:
    """Adicionar enunciado (texto e/ou imagem) fica FORA do st.form da
    grade de propósito -- st.form só permite um botão de envio (o
    'Corrigir'), então salvar enunciado por questão precisa do próprio
    botão, independente. Só aparece a questão de cada vez, escolhida
    num seletor, pra não virar 44 uploaders na tela ao mesmo tempo."""
    sem_enunciado = [q for q in questoes if not q.get("enunciado_texto") and not q.get("enunciado_imagem_path")]
    if not sem_enunciado:
        return

    with st.expander(f"📄 Adicionar enunciado ({len(sem_enunciado)} questão(ões) ainda sem)"):
        opcoes = {f"Q{q['numero_questao']} — {q['id_questao']}": q["id_questao"] for q in sem_enunciado}
        escolha = st.selectbox("Questão", list(opcoes.keys()), key=f"enun_sel_{sufixo}")
        id_q = opcoes[escolha]

        texto = st.text_area(
            "Texto do enunciado (pode deixar em branco se for só imagem)",
            key=f"enun_texto_{sufixo}_{id_q}", height=120,
        )
        imagem = st.file_uploader(
            "Imagem do enunciado (opcional)", type=["png", "jpg", "jpeg"],
            key=f"enun_imagem_{sufixo}_{id_q}",
        )

        if st.button("Salvar enunciado", key=f"enun_salvar_{sufixo}_{id_q}"):
            caminho_imagem = None
            if imagem is not None:
                PASTA_ENUNCIADOS.mkdir(exist_ok=True)
                extensao = Path(imagem.name).suffix or ".png"
                caminho_imagem = str(PASTA_ENUNCIADOS / f"{id_q}{extensao}")
                with open(caminho_imagem, "wb") as f:
                    f.write(imagem.getbuffer())

            if not texto.strip() and not caminho_imagem:
                st.warning("Cole um texto ou uma imagem antes de salvar.")
            else:
                db.atualizar_enunciado(id_q, texto=texto.strip() or None, imagem_path=caminho_imagem)
                st.success(f"Enunciado salvo pra {id_q}.")
                st.rerun()


def render_analise() -> None:
    nivel = db.calcular_nivel_jogador()
    ofensiva = db.calcular_ofensiva()

    col1, col2, col3 = st.columns(3)
    col1.metric("Rank", nivel["rank"], f"{nivel['xp']} XP")
    col2.metric("🔥 Ofensiva atual", f"{ofensiva['atual']} dia(s)")
    col3.metric("Melhor ofensiva", f"{ofensiva['melhor']} dia(s)")

    if nivel["proximo_rank"]:
        st.caption(f"Faltam {nivel['xp_para_proximo']} XP pro {nivel['proximo_rank']}.")

    meta = db.progresso_meta_diaria()
    fracao = min(1.0, meta["feitas_hoje"] / meta["meta"]) if meta["meta"] else 0.0
    st.progress(fracao)
    if meta["atingida"]:
        st.caption(f"✅ Meta de hoje batida: {meta['feitas_hoje']}/{meta['meta']} questões.")
    else:
        st.caption(f"Meta de hoje: {meta['feitas_hoje']}/{meta['meta']} questões — faltam {meta['restantes']}.")

    st.caption("Últimos 30 dias:")
    dias = ofensiva["calendario_30_dias"]
    quadrados = "".join(
        f'<span class="dia-ativo" title="{d["data"]}"></span>' if d["ativo"]
        else f'<span class="dia-inativo" title="{d["data"]}"></span>'
        for d in dias
    )
    st.markdown(f'<div class="app-streak-calendar">{quadrados}</div>', unsafe_allow_html=True)

    st.divider()

    area_analise = st.radio(
        "Área", ["matematica", "ciencias_natureza"],
        format_func=lambda a: RÓTULO_AREA[a], horizontal=True, key="area_analise",
    )

    st.subheader("Prioridade de estudo")
    prioridade = db.prioridade_de_estudo(area_analise)

    if not prioridade["ranking"] and not prioridade["sem_dados"]:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        if prioridade["ranking"]:
            linhas_ranking = []
            for r in prioridade["ranking"]:
                aviso = " ⚠️" if r["amostra_pequena"] else ""
                linhas_ranking.append({
                    "Matéria": r["materia"],
                    "Recorrência": f"{r['percentual_recorrencia']}%",
                    "Sua taxa de acerto": f"{r['taxa_acerto_pct']}%" + aviso,
                    "Tentativas": r["total_tentativas"],
                    "Prioridade": r["score_prioridade"],
                })
            st.dataframe(linhas_ranking, hide_index=True, use_container_width=True)
            st.caption(
                "Prioridade = cai bastante E você erra bastante. Quanto maior, mais vale estudar agora. "
                f"⚠️ = menos de {db.MIN_AMOSTRA_CONFIAVEL} tentativas — ordem pode mudar com mais dado."
            )
        if prioridade["sem_dados"]:
            materias = ", ".join(
                f"{s['materia']} ({s['percentual_recorrencia']}%)" for s in prioridade["sem_dados"]
            )
            st.warning(f"Recorrentes mas você nunca respondeu ainda, sem prioridade calculável: {materias}")

    st.divider()

    st.subheader("Por que você erra")
    por_erro = db.analise_por_tipo_erro(area_analise)
    if not por_erro:
        st.caption("Ainda sem dado suficiente — classifique o motivo do erro no cartão-resposta pra essa análise aparecer.")
    else:
        linhas_erro = [
            {"Matéria": r["materia"], "Tipo de erro": db.TIPOS_ERRO[r["tipo_erro"]], "Quantidade": r["quantidade"]}
            for r in por_erro
        ]
        st.dataframe(linhas_erro, hide_index=True, use_container_width=True)

    st.divider()

    st.subheader("Recorrência por matéria")
    recorrencia = db.recorrencia_por_materia(area_analise)
    if not recorrencia:
        st.info("Nenhuma questão cadastrada ainda.")
    else:
        total_provas = recorrencia[0]["total_provas_na_base"]
        st.caption(
            f"Base atual: {total_provas} prova(s) cadastrada(s), cobrindo só as posições de caderno "
            "que você já carregou — não a prova inteira. Percentual reflete essa amostra, não o ENEM completo."
        )
        st.dataframe(
            [
                {"Matéria": r["materia"], "Provas com a matéria": r["provas_com_materia"], "%": r["percentual"]}
                for r in recorrencia
            ],
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Seu desempenho por matéria")
    desempenho = db.taxa_acerto_por_materia(area_analise)
    if not desempenho:
        st.info("Responda alguma prova no cartão-resposta pra essa tabela aparecer.")
        return

    linhas = []
    for d in desempenho:
        amostra_pequena = d["total_tentativas"] < db.MIN_AMOSTRA_CONFIAVEL
        linhas.append({
            "Matéria": d["materia"],
            "Tentativas": d["total_tentativas"],
            "Acertos": d["acertos"],
            "Taxa de acerto": f"{d['taxa_acerto']*100:.0f}%" + (" ⚠️" if amostra_pequena else ""),
        })
    st.dataframe(linhas, hide_index=True, use_container_width=True)


_FASE_DESCRICAO = {
    "diagnostico": "Retomar o ritmo e mapear onde você está de verdade — não pra confirmar o que já sabe, pra achar exatamente onde dói.",
    "ataque_fraquezas": "A fase mais longa e mais importante: repetição deliberada nas matérias que mais caem E mais você erra, até o erro parar de se repetir.",
    "simulados_intensivos": "Menos conteúdo novo, mais prova inteira cronometrada — treinar o corpo e a cabeça pras horas de prova, não só o conteúdo.",
    "taper": "Reduzir, não aumentar. O ganho de conteúdo já foi feito — o que resta agora é chegar descansado, não mais cansado.",
}

_FASE_RITMO_TEMPO = {
    "diagnostico": (
        "Essa semana: 1 simulado completo, de um ano que você ainda não tocou (veja o checklist abaixo) — "
        "sem estudar pra ele antes, é diagnóstico, não prova. Nos outros dias, classifique o motivo de cada "
        "erro que já está em aberto na correção (ver checklist).",
        "Reserve um bloco livre pro simulado — é longo de propósito. Se não tiver isso essa semana, "
        "um dia só de Matemática OU só Ciências já serve pra começar.",
    ),
    "ataque_fraquezas": (
        "Segunda a sexta: sessões curtas em \"Praticar por matéria\" (Cartão-resposta), nas matérias do "
        "topo da lista abaixo. Um dia do fim de semana: 1 simulado completo, priorizando o ano com menor "
        "cobertura no checklist. Classifique os erros no MESMO dia — a lembrança de por que errou some rápido.",
        "Uma rotina diária curta e sustentável por 6 semanas rende mais que sessões maratona esporádicas "
        "que você abandona na 2ª semana. Se um dia não der, não compense dobrando no outro — só continue.",
    ),
    "simulados_intensivos": (
        "Pouca matéria nova. Foco: simulados completos cronometrados, o mais parecido possível com o dia "
        "real (mesmo horário do dia, sem pausa, celular longe). Entre um e outro, revise só o que errou.",
        "Reserve o tempo real de prova pro simulado — confirme a duração exata no seu cartão de confirmação "
        "de inscrição (historicamente girou perto de 5h pro dia de Matemática + Ciências, mas isso pode mudar ano a ano).",
    ),
    "taper": (
        "Sem matéria nova agora. Reveja só o que você já errou antes (\"Por que você erra\", em Minha "
        "análise). Separe documento e o que for levar hoje, não na véspera.",
        "Revisão leve, pouco tempo. O resto é descanso de verdade — ansiedade de última hora custa mais "
        "ponto do que qualquer conteúdo novo aprendido nesses últimos dias.",
    ),
}


def render_calendario() -> None:
    plano = db.plano_periodizacao()

    if plano["fase"] == "pos_prova":
        st.success("A prova já passou. Se ainda quiser treinar, o resto do app continua aqui.")
        return
    if plano["fase"] == "prova":
        st.success("🍀 Hoje é o dia. O trabalho já foi feito — agora é confiar nele.")
        return

    data_prova_fmt = f"{plano['data_prova'][8:10]}/{plano['data_prova'][5:7]}/{plano['data_prova'][:4]}"
    st.subheader(f"🗓️ {plano['dias_restantes']} dias até {data_prova_fmt}")
    st.caption(f"Fase atual: **{plano['fase_label']}** — dia {plano['dias_decorridos']} de um plano de {plano['dias_totais_plano']} dias.")
    st.progress(min(1.0, plano["dias_decorridos"] / plano["dias_totais_plano"]))
    st.info(_FASE_DESCRICAO[plano["fase"]])

    st.divider()
    st.subheader("🎯 Ataque às fraquezas — o que atacar agora")
    st.caption(
        "Não é uma lista fixa por semana — é sempre a matéria que mais cai E você mais erra, recalculada "
        "a cada tentativa nova. Conforme melhora numa matéria, ela sai do topo sozinha."
    )
    for area in ("matematica", "ciencias_natureza"):
        prioridade = db.prioridade_de_estudo(area)
        top = prioridade["ranking"][:3]
        st.write(f"**{RÓTULO_AREA[area]}**")
        if not top:
            st.caption("Ainda sem dado suficiente pra priorizar — responda mais questões dessa área primeiro.")
            continue
        for r in top:
            aviso = " ⚠️ *(amostra pequena, pode mudar)*" if r["amostra_pequena"] else ""
            st.write(f"- `{r['materia']}` — cai em {r['percentual_recorrencia']}% das provas, você acerta {r['taxa_acerto_pct']}%{aviso}")
    st.caption("→ Treine cada uma isolada em \"Praticar por matéria\", no Cartão-resposta.")

    st.divider()
    st.subheader("📋 Checklist de simulados e correção")
    st.caption(
        "\"Feito\" = 80%+ da prova respondida. \"Corrigido\" = toda questão errada já tem motivo classificado "
        "(Cartão-resposta → questão errada → \"Por que errou?\") — é aí que a engenharia reversa acontece de "
        "verdade: sem isso você só sabe QUE errou, não POR QUÊ."
    )
    progresso = sorted(db.progresso_simulados(), key=lambda x: x["cobertura_pct"])
    if not progresso:
        st.info("Nenhum ano com Matemática + Ciências completos ainda.")
    for p in progresso:
        feito = "✅" if p["feito"] else "⬜"
        if p["erradas_total"] == 0:
            corrigido = "—"
        elif p["correcao_completa"]:
            corrigido = "✅"
        else:
            corrigido = f"⬜ {p['erradas_corrigidas']}/{p['erradas_total']}"
        st.write(f"{feito} **{p['ano']}** — {p['respondidas']}/{p['total_questoes']} respondidas ({p['cobertura_pct']:.0f}%) · correção: {corrigido}")

    st.divider()
    st.subheader("📆 Ritmo da semana, nesta fase")
    ritmo, tempo = _FASE_RITMO_TEMPO[plano["fase"]]
    st.write(ritmo)
    st.divider()
    st.subheader("⏱️ Quanto tempo, de verdade")
    st.write(tempo)

    st.divider()
    st.caption(
        "Este plano cobre só Matemática e Ciências da Natureza (o que este app tem dado pra apoiar). "
        "Linguagens, Humanas e Redação precisam do próprio plano, em outro lugar."
    )


PASTA_VISION_BOARD = Path(__file__).parent / "vision_board"


def render_objetivos() -> None:
    prova = db.dias_ate_prova()

    if prova["ja_passou"]:
        st.success("A prova já passou.")
    else:
        cor_urgencia = "#39FF14" if prova["dias_restantes"] > 14 else "#E0A542" if prova["dias_restantes"] > 4 else "#FF7A6B"
        st.markdown(
            f'<div style="text-align:center; padding:0.5rem 0 1.5rem">'
            f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:4rem; font-weight:700; '
            f'color:{cor_urgencia}; text-shadow:0 0 28px {cor_urgencia}66; line-height:1">{prova["dias_restantes"]}</div>'
            f'<div style="color:#8FE39A; letter-spacing:0.08em; margin-top:0.3rem">DIAS ATÉ O ENEM</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Por que eu quero passar")
    motivo_atual = db.obter_configuracao("motivo_pessoal", "")
    motivo = st.text_area(
        "Escreva pra você mesmo — o que muda quando você passar. Releia nos dias ruins.",
        value=motivo_atual, height=140, key="motivo_pessoal_input",
    )
    if st.button("Salvar", key="salvar_motivo") and motivo != motivo_atual:
        db.definir_configuracao("motivo_pessoal", motivo)
        st.success("Salvo.")

    st.divider()

    st.subheader("Metas de nota")
    st.caption(
        "Meta é aspiracional, não previsão — nota TRI não é a mesma coisa que % de acerto no treino. "
        "As duas métricas abaixo medem coisas diferentes de propósito."
    )
    col1, col2 = st.columns(2)
    with col1:
        meta_mat = st.number_input(
            "Meta Matemática (0-1000)", min_value=0, max_value=1000,
            value=int(float(db.obter_configuracao("meta_nota_matematica", "700"))), key="meta_nota_mat",
        )
    with col2:
        meta_nat = st.number_input(
            "Meta Ciências da Natureza (0-1000)", min_value=0, max_value=1000,
            value=int(float(db.obter_configuracao("meta_nota_natureza", "600"))), key="meta_nota_nat",
        )
    if st.button("Salvar metas", key="salvar_metas_nota"):
        db.definir_configuracao("meta_nota_matematica", str(int(meta_mat)))
        db.definir_configuracao("meta_nota_natureza", str(int(meta_nat)))
        st.success("Metas salvas.")

    def _media_geral(grande_area: str):
        desempenho = db.taxa_acerto_por_materia(grande_area)
        total = sum(d["total_tentativas"] for d in desempenho)
        acertos = sum(d["acertos"] for d in desempenho)
        return round(acertos / total * 100, 1) if total else None

    media_mat, media_nat = _media_geral("matematica"), _media_geral("ciencias_natureza")
    col1, col2 = st.columns(2)
    col1.metric("Sua taxa de acerto no treino — Matemática", f"{media_mat}%" if media_mat is not None else "sem dado ainda")
    col2.metric("Sua taxa de acerto no treino — Ciências", f"{media_nat}%" if media_nat is not None else "sem dado ainda")

    st.divider()

    st.subheader("🖼️ Quadro de motivação")
    st.caption("Fotos suas, de amigos, de quem te inspira — o que fizer você lembrar por que está fazendo isso.")
    PASTA_VISION_BOARD.mkdir(exist_ok=True)

    if "vision_upload_geracao" not in st.session_state:
        st.session_state["vision_upload_geracao"] = 0

    novas_imagens = st.file_uploader(
        "Adicionar imagem(ns)", type=["png", "jpg", "jpeg"], accept_multiple_files=True,
        key=f"vision_upload_{st.session_state['vision_upload_geracao']}",
    )
    # O upload salva só quando este botão é clicado -- nunca sozinho no
    # rerun. st.file_uploader mantém o valor entre reruns até a key
    # mudar; sem esse botão como porta de entrada, o st.rerun() logo
    # abaixo reprocessaria o MESMO arquivo pra sempre (empilhando cópia
    # atrás de cópia a cada rerun -- foi exatamente isso que aconteceu
    # testando: 1 upload virou ~500 arquivos em segundos). Trocar a key
    # depois de salvar reseta o widget visualmente também.
    if novas_imagens and st.button("Adicionar ao quadro", key="vision_upload_confirmar"):
        for img in novas_imagens:
            extensao = Path(img.name).suffix or ".jpg"
            destino = PASTA_VISION_BOARD / f"{int(datetime.now().timestamp() * 1000)}{extensao}"
            with open(destino, "wb") as f:
                f.write(img.getbuffer())
        st.session_state["vision_upload_geracao"] += 1
        st.success(f"{len(novas_imagens)} imagem(ns) adicionada(s).")
        st.rerun()

    imagens = sorted(
        (p for p in PASTA_VISION_BOARD.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")),
        reverse=True,
    )
    if not imagens:
        st.info("Nenhuma imagem ainda.")
    else:
        cols = st.columns(3)
        for i, caminho in enumerate(imagens):
            with cols[i % 3]:
                st.image(str(caminho), use_container_width=True)
                if st.button("Remover", key=f"remover_vision_{caminho.name}"):
                    caminho.unlink()
                    st.rerun()


def render_admin() -> None:
    st.subheader("💾 Backup do banco")
    st.caption(
        "reconstruir_base.py já faz backup sozinho antes de atualizar a base. "
        "Use o botão abaixo pra tirar uma cópia extra antes de qualquer outra coisa arriscada "
        "(carregar um CSV colado errado, por exemplo)."
    )

    dias = backup_db.dias_desde_ultimo_backup()
    if dias is None:
        st.warning("Nenhum backup ainda. Os backups ficam só nesta máquina — sem um, um HD morto leva tudo junto.")
    elif dias >= 7:
        st.warning(f"Último backup local foi há {dias} dia(s). Baixe uma cópia recente pra algum lugar fora desta máquina (Drive, e-mail).")
    else:
        st.caption(f"Último backup local: há {dias} dia(s). Lembre de baixar uma cópia pra fora da máquina de vez em quando — backups/ não protege contra HD/SSD morto.")

    col_backup1, col_backup2 = st.columns([1, 2])
    with col_backup1:
        if st.button("📦 Fazer backup agora", type="primary"):
            caminho = backup_db.fazer_backup()
            st.session_state["ultimo_backup"] = str(caminho)
            st.success(f"Backup criado: {caminho.name}")
            st.rerun()

    backups = backup_db.listar_backups()
    if backups:
        with st.expander(f"Backups existentes ({len(backups)})"):
            for caminho in backups:
                tamanho_mb = caminho.stat().st_size / 1_000_000
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"`{caminho.name}` — {tamanho_mb:.2f} MB")
                with c2:
                    with open(caminho, "rb") as f:
                        st.download_button(
                            "⬇️ Baixar", data=f.read(), file_name=caminho.name,
                            mime="application/octet-stream", key=f"baixar_{caminho.name}",
                        )
    else:
        st.info("Nenhum backup ainda — vale fazer um agora, principalmente antes de carregar gabarito novo em lote.")

    st.divider()

    st.subheader("🎯 Meta diária")
    meta_atual = db.progresso_meta_diaria()["meta"]
    nova_meta = st.number_input(
        "Questões por dia", min_value=1, max_value=200, value=meta_atual, key="admin_meta_diaria",
    )
    if st.button("Salvar meta", key="admin_salvar_meta"):
        db.definir_configuracao("meta_diaria", str(int(nova_meta)))
        st.success(f"Meta diária atualizada pra {int(nova_meta)} questões.")
        st.rerun()

    st.divider()

    st.subheader("🗓️ Data da prova")
    st.caption("Alimenta a contagem regressiva e as fases do Calendário. Mudar isso reancora o início do plano.")
    data_atual = date.fromisoformat(db.obter_configuracao("data_prova", db.DATA_PROVA_PADRAO))
    nova_data = st.date_input("Data do ENEM (o dia que este app cobre: Matemática + Ciências)", value=data_atual, key="admin_data_prova")
    if st.button("Salvar data", key="admin_salvar_data_prova"):
        db.definir_configuracao("data_prova", nova_data.isoformat())
        db.definir_configuracao("data_inicio_plano", date.today().isoformat())
        st.success(f"Data da prova atualizada pra {nova_data.isoformat()}. Plano reancorado a partir de hoje.")
        st.rerun()

    st.divider()

    st.subheader("Colar gabarito direto (sem arquivo)")
    st.caption(
        "Cola um CSV com colunas numero,materia,gabarito (a primeira linha tem que ser esse cabeçalho). "
        "Coluna grande_area é opcional, por linha, se não usar o campo abaixo."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        ano_colar = st.number_input("Ano", min_value=2009, max_value=2100, value=2019, key="admin_ano")
    with col2:
        caderno_colar = st.text_input("Caderno", value="Azul", key="admin_caderno")
    with col3:
        grande_area_colar = st.selectbox("Grande área padrão", ["matematica", "ciencias_natureza"], key="admin_area")

    texto_csv = st.text_area(
        "Cole o CSV aqui", height=200, key="admin_csv_texto",
        placeholder="numero,materia,gabarito\n136,geometria_espacial,E\n137,logaritmo,E",
    )
    sobrescrever_colar = st.checkbox("Sobrescrever se já existir (recalcula tentativas afetadas)", value=True, key="admin_sobrescrever")

    if st.button("Carregar", type="primary", key="admin_carregar"):
        if not texto_csv.strip():
            st.warning("Cola o CSV primeiro.")
        else:
            try:
                resumo = db.carregar_gabarito_texto(
                    texto_csv, ano=int(ano_colar), caderno=caderno_colar,
                    grande_area_padrao=grande_area_colar, sobrescrever=sobrescrever_colar,
                )
            except ValueError as e:
                st.error(str(e))
            else:
                st.success(f"{resumo['classificadas']} classificada(s).")
                if resumo["nao_classificadas"]:
                    st.warning(f"{len(resumo['nao_classificadas'])} foram pra triagem: " + ", ".join(resumo["nao_classificadas"]))
                if resumo["erros"]:
                    st.error("Linhas com erro: " + "; ".join(resumo["erros"]))

    st.divider()

    st.subheader("🗑️ Apagar prova (irreversível)")
    st.caption("Remove uma prova inteira — útil pra limpar carga acidental, tipo CSV colado no ano errado.")

    provas_existentes = db.listar_provas()
    if not provas_existentes:
        st.info("Nenhuma prova cadastrada.")
    else:
        RÓTULO_AREA_ADMIN = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}
        opcoes_apagar = {
            f"{ano} — {caderno} — {RÓTULO_AREA_ADMIN.get(area, area)}": (ano, caderno, area)
            for ano, caderno, area in provas_existentes
        }
        escolha_apagar = st.selectbox("Prova a apagar", list(opcoes_apagar.keys()), key="admin_apagar_prova")
        ano_del, caderno_del, area_del = opcoes_apagar[escolha_apagar]

        confirmar = st.checkbox(
            f"Confirmo que quero apagar {escolha_apagar} permanentemente, junto com tentativas e resoluções ligadas a ela.",
            key="admin_confirmar_apagar",
        )
        if st.button("Apagar prova", type="primary", disabled=not confirmar, key="admin_apagar_botao"):
            resultado = db.apagar_prova(ano_del, caderno_del, area_del)
            st.success(
                f"{resultado['apagadas']} questão(ões) apagada(s). "
                f"{resultado['tentativas_perdidas']} tentativa(s) e "
                f"{resultado['resolucoes_perdidas']} resolução(ões) perdidas junto."
            )
            st.rerun()

    st.divider()

    st.subheader("Histórico de alterações")
    st.caption(
        "Toda vez que um gabarito ou matéria já cadastrados são corrigidos, fica registrado aqui — "
        "incluindo quantas tentativas antigas tiveram o resultado recalculado por causa da correção."
    )
    historico = db.historico_alteracoes()
    if not historico:
        st.info("Nenhuma alteração registrada ainda.")
        return
    linhas = [
        {
            "Questão": h["id_questao"], "Campo": h["campo"],
            "De": h["valor_antigo"], "Para": h["valor_novo"],
            "Quando": h["data_alteracao"][:16],
            "Tentativas recalculadas": h["tentativas_recalculadas"],
        }
        for h in historico
    ]
    st.dataframe(linhas, hide_index=True, use_container_width=True)


def render_guia_estudante() -> None:
    st.title("📚 Guia do Estudante")
    sub = st.radio(
        "Conteúdo",
        ["Tutor Socrático (Ciências)", "Extração de Gabarito (outra IA)"],
        horizontal=True,
    )
    nome_arquivo = "guia_estudante.md" if sub.startswith("Tutor") else "prompt_extracao_gabarito.md"
    caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning(f"{nome_arquivo} não encontrado em core/. Salve o arquivo lá primeiro.")


def _tagline_contagem_regressiva() -> str:
    prova = db.dias_ate_prova()
    if prova["ja_passou"]:
        return "treino com prova real, corrigido na hora"
    if prova["dias_restantes"] == 0:
        return "é hoje. boa prova 🍀"
    return f"treino com prova real, corrigido na hora · 🗓️ {prova['dias_restantes']} dias até o ENEM"


if __name__ == "__main__":
    st.set_page_config(page_title="Cartão-resposta", page_icon="📝", layout="wide")
    db.inicializar_banco()
    ui_theme.injetar_tema()
    ui_theme.hero("📝 Cartão-resposta digital", _tagline_contagem_regressiva())

    pagina = st.sidebar.radio(
        "Menu",
        ["📝 Cartão-resposta", "📊 Minha análise", "📅 Calendário", "🎯 Objetivos",
         "🔗 Coletar vídeos", "🏷️ Triagem", "🔐 Admin", "📚 Guia do Estudante"],
    )

    if pagina == "📝 Cartão-resposta":
        render_cartao_resposta()
    elif pagina == "📊 Minha análise":
        render_analise()
    elif pagina == "📅 Calendário":
        render_calendario()
    elif pagina == "🎯 Objetivos":
        render_objetivos()
    elif pagina == "🔗 Coletar vídeos":
        coletar_videos.render_coletar_videos()
    elif pagina == "🏷️ Triagem":
        triagem.render_triagem()
    elif pagina == "🔐 Admin":
        render_admin()
    elif pagina == "📚 Guia do Estudante":
        render_guia_estudante()