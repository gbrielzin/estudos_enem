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
    mesmo cálculo, mesma regra do resto do sistema. Um ano pode ter
    mais de um caderno completo (ex: 2024 azul E amarelo) -- cada
    combinação vira sua própria opção no seletor, rotulada por cor pra
    não colidir (ver db.simulados_completos_disponiveis)."""
    combinacoes = db.simulados_completos_disponiveis()
    if not combinacoes:
        st.info(
            "Nenhum ano tem as duas áreas cadastradas ainda — "
            "o simulado completo só aparece quando Matemática e Ciências "
            "da mesma prova já foram carregadas."
        )
        return

    def _rotulo(c: dict) -> str:
        if c["caderno_matematica"] == c["caderno_ciencias"]:
            return f"{c['ano']} — {c['caderno_matematica']}"
        return f"{c['ano']} — Mat. {c['caderno_matematica']} / Ciê. {c['caderno_ciencias']}"

    opcoes = {_rotulo(c): c for c in combinacoes}
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
        nomes = db.nomes_tentativas(ano_sel, caderno_sel, area_sel)
        with st.expander(f"📈 Histórico de tentativas dessa prova ({len(historico)})", expanded=True):
            for h in historico:
                pct = f"{h['taxa_acerto']*100:.0f}%" if h["taxa_acerto"] is not None else "—"
                nome_atual = nomes.get(h["tentativa"], "")
                rotulo = f"Tentativa {h['tentativa']}" + (f" — {nome_atual}" if nome_atual else "")
                col_txt, col_nome = st.columns([3, 2])
                with col_txt:
                    st.write(f"**{rotulo}**: {h['acertos']}/{h['total']} ({pct}) — {h['inicio'][:10]}")
                with col_nome:
                    novo_nome = st.text_input(
                        "Nome", value=nome_atual, placeholder="ex: fiz cansado à noite",
                        key=f"nome_tentativa_{sufixo}_{h['tentativa']}", label_visibility="collapsed",
                    )
                    if novo_nome != nome_atual and novo_nome.strip():
                        db.nomear_tentativa(ano_sel, caderno_sel, area_sel, h["tentativa"], novo_nome)
                        st.rerun()

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


def render_prova_beta() -> None:
    """Faz a prova inteira lendo o enunciado direto no site, sem
    precisar do PDF aberto do lado -- separado de 'Uma prova por vez'
    de propósito (pedido do usuário): a extração de enunciado por PDF
    é nova e ~40% das questões citam figura/gráfico/tabela que a
    extração de texto não captura (o ENEM desenha isso como vetor, não
    como imagem separada -- ver extrair_enunciados_pdf.py), marcadas
    com ⚠️ no início do texto. Mesmo mecanismo de correção/tracking de
    'Uma prova por vez' por baixo (_renderizar_grade_questoes) -- só a
    origem das questões (só prova com enunciado carregado) e o aviso
    são diferentes."""
    st.warning(
        "🧪 **Beta** -- lê o enunciado extraído automaticamente do PDF oficial. "
        "~40% das questões citam figura/gráfico/tabela que a extração de texto sozinha não "
        "captura (aparecem com ⚠️ no início) -- confere contra o PDF nessas. O resto "
        "funciona igual ao Cartão-resposta normal (mesma correção, mesmo histórico)."
    )

    provas = db.provas_com_enunciado()
    if not provas:
        st.info("Nenhuma prova com enunciado carregado ainda -- rode extrair_enunciados_pdf.py primeiro.")
        return

    opcoes = {
        f"{ano} — {caderno} — {RÓTULO_AREA.get(area, area)} ({com_enunciado}/{total} com enunciado)": (ano, caderno, area)
        for ano, caderno, area, com_enunciado, total in provas
    }
    escolha = st.selectbox("Prova", list(opcoes.keys()), key="beta_prova_sel")
    ano_sel, caderno_sel, area_sel = opcoes[escolha]

    questoes = db.listar_questoes_da_prova(ano_sel, caderno_sel, area_sel)
    _renderizar_grade_questoes(questoes, sufixo=f"beta_{ano_sel}_{caderno_sel}_{area_sel}", estilo_exame=True)


def render_simulados_feitos() -> None:
    """Lista toda prova com ao menos uma tentativa registrada -- pra
    responder 'quais provas eu já fiz' sem precisar abrir cada uma
    em 'Uma prova por vez' e olhar o expander de histórico ali dentro.
    Cada rodada é a mesma numeração que resumo_por_tentativa() já
    deriva (não inventa sessão nova) -- só reúne isso por prova e
    permite nomear/rever mais fácil, num lugar só."""
    simulados = db.simulados_feitos()
    if not simulados:
        st.info("Nenhum simulado respondido ainda -- assim que você corrigir a primeira prova, ela aparece aqui.")
        return

    st.caption(f"{len(simulados)} prova(s) com pelo menos uma tentativa registrada.")

    for s in simulados:
        ultima = s["rodadas"][-1]
        cobertura = f"{ultima['total']}/{s['total_questoes']}"
        titulo = f"{s['ano']} — {s['caderno']} — {RÓTULO_AREA.get(s['grande_area'], s['grande_area'])}"
        pct_ultima = f"{ultima['taxa_acerto']*100:.0f}%" if ultima["taxa_acerto"] is not None else "—"

        with st.expander(f"{titulo} — última tentativa: {ultima['acertos']}/{ultima['total']} ({pct_ultima}) — cobertura {cobertura}"):
            for r in s["rodadas"]:
                pct = f"{r['taxa_acerto']*100:.0f}%" if r["taxa_acerto"] is not None else "—"
                rotulo = f"Tentativa {r['tentativa']}" + (f" — {r['nome']}" if r["nome"] else "")
                sufixo_rodada = f"{s['ano']}_{s['caderno']}_{s['grande_area']}_{r['tentativa']}"

                col_txt, col_nome = st.columns([3, 2])
                with col_txt:
                    st.write(f"**{rotulo}**: {r['acertos']}/{r['total']} ({pct}) — {r['inicio'][:10]}")
                with col_nome:
                    novo_nome = st.text_input(
                        "Nome", value=r["nome"], placeholder="ex: fiz cansado à noite",
                        key=f"nome_simulados_feitos_{sufixo_rodada}", label_visibility="collapsed",
                    )
                    if novo_nome != r["nome"] and novo_nome.strip():
                        db.nomear_tentativa(s["ano"], s["caderno"], s["grande_area"], r["tentativa"], novo_nome)
                        st.rerun()

                with st.expander("📋 Ver detalhes (pra colar na IA)"):
                    detalhe_texto = db.detalhe_rodada(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                    linhas_texto = [f"{titulo} — {rotulo}", f"{r['acertos']}/{r['total']} acertos", ""]
                    for item in detalhe_texto:
                        if item["resposta_escolhida"] is None:
                            linhas_texto.append(f"Q{item['numero_questao']}: NÃO RESPONDI — gabarito {item['alternativa_correta']}")
                        elif item["resultado"] == "acertou":
                            linhas_texto.append(f"Q{item['numero_questao']}: acertei (marquei {item['resposta_escolhida']})")
                        else:
                            linhas_texto.append(f"Q{item['numero_questao']}: ERREI — marquei {item['resposta_escolhida']}, gabarito {item['alternativa_correta']}")
                    st.code("\n".join(linhas_texto), language=None)

                col_editar, col_excluir = st.columns(2)
                with col_editar:
                    with st.popover("✏️ Editar respostas", key=f"popover_editar_{sufixo_rodada}"):
                        detalhe = db.detalhe_rodada(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                        opcoes_letra = ["— (não respondida)", "A", "B", "C", "D", "E"]
                        alteracoes = {}
                        for item in detalhe:
                            valor_atual = item["resposta_escolhida"] or "— (não respondida)"
                            nova = st.selectbox(
                                f"Q{item['numero_questao']} (gabarito {item['alternativa_correta']})",
                                opcoes_letra,
                                index=opcoes_letra.index(valor_atual),
                                key=f"editar_{sufixo_rodada}_{item['id_tentativa']}",
                            )
                            if nova != valor_atual:
                                alteracoes[item["id_tentativa"]] = None if nova == "— (não respondida)" else nova
                        if st.button(
                            f"Salvar {len(alteracoes)} alteração(ões)" if alteracoes else "Nenhuma alteração",
                            disabled=not alteracoes, key=f"salvar_editar_{sufixo_rodada}",
                        ):
                            for id_tentativa, nova_resposta in alteracoes.items():
                                db.editar_resposta_tentativa(id_tentativa, nova_resposta)
                            st.rerun()
                with col_excluir:
                    with st.popover("🗑️ Excluir esta rodada", key=f"popover_excluir_{sufixo_rodada}"):
                        st.caption(
                            "Apaga essa rodada inteira (todas as respostas dela) e recalcula a revisão "
                            "espaçada de cada questão como se essa rodada nunca tivesse acontecido. "
                            "Não desfaz -- pra reenvio duplicado ou rodada errada, não pra 'não gostei do resultado'."
                        )
                        confirmar = st.checkbox(
                            f"Confirmo apagar a Tentativa {r['tentativa']} de {titulo}",
                            key=f"confirmar_excluir_{sufixo_rodada}",
                        )
                        if st.button("Apagar rodada", type="primary", disabled=not confirmar, key=f"excluir_{sufixo_rodada}"):
                            db.apagar_rodada_tentativa(s["ano"], s["caderno"], s["grande_area"], r["tentativa"])
                            st.rerun()
                st.divider()
            if ultima["total"] < s["total_questoes"]:
                st.caption(f"{s['total_questoes'] - ultima['total']} questão(ões) dessa prova ainda sem tentativa nenhuma.")


def _renderizar_grade_questoes(questoes: list[dict], sufixo: str, estilo_exame: bool = False) -> None:
    """Núcleo compartilhado por prova única, simulado, revisão do dia,
    prática por matéria e a prova beta com enunciado: grade de
    resposta A-E, correção contra o gabarito via registrar_tentativa(),
    classificação de erro e vídeo de resolução. Todo mundo que monta
    uma lista de questões (não importa a origem) cai aqui — não
    duplica essa lógica em cada modo.

    estilo_exame=True troca só a PARTE DE ENTRADA (como a questão é
    exibida antes de responder) pro layout "uma embaixo da outra, com
    o enunciado inteiro visível antes da resposta", pedido explícito
    do usuário pra prova beta parecer com o PDF do ENEM em vez do
    cartão-resposta compacto -- esconde também o preenchimento rápido
    (não faz sentido colar sequência numa prova que você está lendo
    pela primeira vez, é ferramenta de transcrever prova já feita no
    papel). Tudo depois de responder (corrigir, desfazer, ver o que
    marcou, erros) continua idêntico nos dois estilos."""
    _renderizar_editor_enunciado(questoes, sufixo)

    if not estilo_exame:
        with st.expander("⚡ Preenchimento rápido (cola a sequência de letras)"):
            st.caption(
                "Cola as letras na ordem das questões, sem espaço nem pontuação (ex: ABCDEBAACD...). "
                "Use * ou deixa em branco pra pular uma questão que você não respondeu."
            )
            sequencia = st.text_input("Sequência de respostas", key=f"sequencia_rapida_{sufixo}")
            if st.button("Aplicar sequência", key=f"aplicar_seq_{sufixo}"):
                aplicadas = 0
                for i, q in enumerate(questoes):
                    letra = sequencia[i].upper() if i < len(sequencia) else "*"
                    chave_resp = f"resp_{q['id_questao']}"
                    if letra in "ABCDE":
                        st.session_state[chave_resp] = letra
                        aplicadas += 1
                    else:
                        # * (ou string mais curta que a prova) LIMPA a
                        # resposta de propósito -- sem isso, colar uma
                        # sequência corrigida com * numa posição que já
                        # tinha letra de uma aplicação anterior deixava a
                        # letra velha lá (só escrevia em cima de A-E, nunca
                        # apagava), então "pular" não pulava de verdade se
                        # já tinha algo marcado ali antes.
                        st.session_state[chave_resp] = "—"
                st.success(f"{aplicadas} resposta(s) aplicada(s) — confere a grade abaixo antes de corrigir.")

    mostrar_ano = len({q["ano"] for q in questoes}) > 1

    with st.form(f"cartao_resposta_form_{sufixo}"):
        if estilo_exame:
            # Uma questão por "linha", enunciado inteiro visível ANTES
            # da resposta -- igual abrir o caderno de prova de verdade:
            # lê a questão, só depois marca a letra. O grid compacto
            # (radio primeiro, enunciado escondido num expander depois)
            # faz sentido pra revisão rápida, não pra ler uma prova
            # pela primeira vez.
            for q in questoes:
                rotulo = f"Questão {q['numero_questao']}" + (f" · {q['ano']}" if mostrar_ano else "")
                if q["status_classificacao"] == "nao_classificado":
                    rotulo += " ⚠️"
                st.markdown(f"##### {rotulo}")
                _mostrar_enunciado_exame(q)
                st.radio(
                    "Resposta", ["—", "A", "B", "C", "D", "E"],
                    horizontal=True, key=f"resp_{q['id_questao']}", label_visibility="collapsed",
                )
                st.divider()
        else:
            # Uma st.columns(3) NOVA por linha de 3, em vez de uma só pra
            # grade inteira -- com uma única chamada, cols[i % 3] distribui
            # "por coluna" (Q1,Q4,Q7... na coluna 0, Q2,Q5,Q8... na coluna
            # 1...), e no celular, onde o Streamlit empilha as colunas na
            # vertical, cada coluna renderiza seu bloco inteiro antes da
            # próxima -- a leitura vira 1,4,7,10...,2,5,8,11...,3,6,9,12...,
            # parecendo que questão foi pulada. Uma st.columns(3) por linha
            # preserva a ordem sequencial mesmo empilhada.
            for inicio in range(0, len(questoes), 3):
                cols = st.columns(3)
                for col, q in zip(cols, questoes[inicio:inicio + 3]):
                    with col:
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
            q["id_questao"]: st.session_state.get(f"resp_{q['id_questao']}", "—")
            for q in questoes
        }
        if not any(resp != "—" for resp in respostas.values()):
            st.warning("Marque pelo menos uma resposta antes de corrigir.")
            return
        # Questão em branco ("—") registra como None, não fica de fora
        # -- é uma tentativa de verdade (sempre errou, ver
        # registrar_tentativa), não um "pular" que sumia de toda
        # estatística baseada em tentativas_usuario.
        st.session_state[chave_resultado] = [
            db.registrar_tentativa(id_q, None if resp == "—" else resp)
            for id_q, resp in respostas.items()
        ]

    resultados = st.session_state.get(chave_resultado)
    if not resultados:
        return

    # total é o tamanho da prova INTEIRA -- agora toda questão (branca
    # ou não) vira uma tentativa, então len(resultados) já é
    # len(questoes) sempre, mas manter a variável explícita deixa a
    # intenção clara caso os dois algum dia divirjam de novo.
    acertos = sum(1 for r in resultados if r["resultado"] == "acertou")
    total = len(questoes)

    st.success(f"{acertos}/{total} acertos ({acertos / total * 100:.0f}%)")

    with st.popover("↩️ Desfazer essa correção"):
        st.caption(
            "Pra quando você marcou errado por engano agora e quer corrigir de novo -- "
            "só desfaz questão que ainda não tinha nenhuma tentativa antes desta."
        )
        if st.button("Confirmar desfazer", key=f"desfazer_confirmar_{sufixo}"):
            resultado_desfazer = db.desfazer_tentativas([r["id_tentativa"] for r in resultados])
            del st.session_state[chave_resultado]
            n_ok = len(resultado_desfazer["desfeitas"])
            n_puladas = len(resultado_desfazer["puladas_com_historico"])
            if n_puladas:
                st.session_state[f"desfazer_aviso_{sufixo}"] = (
                    f"{n_ok} tentativa(s) desfeita(s). {n_puladas} não foram desfeitas "
                    "porque já tinham tentativa anterior a esta (desfazer exigiria mexer "
                    "no histórico de revisão dela, não fiz isso automaticamente)."
                )
            st.rerun()

    aviso_desfazer = st.session_state.pop(f"desfazer_aviso_{sufixo}", None)
    if aviso_desfazer:
        st.warning(aviso_desfazer)

    numero_por_id = {q["id_questao"]: q["numero_questao"] for q in questoes}
    resultado_por_id = {r["id_questao"]: r for r in resultados}

    with st.expander(f"📋 Ver o que você marcou (prova inteira, {total} questões)"):
        for q in questoes:
            numero = q["numero_questao"]
            r = resultado_por_id[q["id_questao"]]
            if r["resposta_escolhida"] is None:
                st.write(f"⬜ **Q{numero}** — não respondida (conta como erro), gabarito é **{r['alternativa_correta']}**")
                continue
            marca = "✅" if r["resultado"] == "acertou" else "❌"
            st.write(
                f"{marca} **Q{numero}** — você marcou **{r['resposta_escolhida']}**, "
                f"gabarito é **{r['alternativa_correta']}**"
            )

    erros = [r for r in resultados if r["resultado"] == "errou"]
    if erros:
        with st.expander(f"⚠️ {len(erros)} questão(ões) errada(s) — já agendadas pra revisão", expanded=True):
            for r in erros:
                numero = numero_por_id.get(r["id_questao"], r["id_questao"])
                marcou = f"você marcou **{r['resposta_escolhida']}**" if r["resposta_escolhida"] is not None else "**não respondida**"
                st.write(
                    f"**Q{numero}** — {marcou}, "
                    f"gabarito é **{r['alternativa_correta']}** — próxima revisão: {r['proxima_revisao']}"
                )

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
                    col_res, col_del = st.columns([5, 1])
                    with col_res:
                        if res["tipo"] == "video":
                            st.video(res["conteudo"])
                        else:
                            st.caption(f"Resolução em texto ({res['canal'] or 'sem canal'}): {res['conteudo']}")
                    with col_del:
                        if st.button("🗑️", key=f"apagar_res_{res['id_resolucao']}", help="Remover essa resolução (link errado/quebrado)"):
                            db.apagar_resolucao(res["id_resolucao"])
                            st.rerun()

    n_brancas = sum(1 for r in resultados if r["resposta_escolhida"] is None)
    if n_brancas:
        st.caption(
            f"{n_brancas} questão(ões) deixada(s) em branco -- contam como erro no total acima "
            "e já entraram na fila de revisão, igual questão errada com letra marcada."
        )


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


def _mostrar_enunciado_exame(q: dict) -> None:
    """Enunciado SEMPRE visível (nunca escondido num expander) --
    versão pra estilo_exame=True, onde o objetivo é ler a questão
    igual um caderno de prova de verdade, não esconder o texto atrás
    de um clique. st.container(border=True) + st.write() em vez de
    markdown com HTML de propósito -- o texto vem de extração de PDF e
    questão de matemática frequentemente tem '<'/'>' de verdade
    (ex: "x < 5"), que markdown com unsafe_allow_html interpretaria
    como tag HTML e quebraria a exibição."""
    texto = q.get("enunciado_texto")
    imagem = q.get("enunciado_imagem_path")
    if not texto and not imagem:
        st.caption("Sem enunciado carregado pra essa questão ainda.")
        return
    with st.container(border=True):
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


_FASE_PRINCIPIO = {
    "fase1_fundacao": "Ainda não sabemos o ponto de partida real em Natureza. Meta numérica sem linha de base é chute — a ação desta fase é estabelecer essa linha de base (corrigir 2019 + 1 prova nova, categorizando cada erro), não bater um número.",
    "fase2_consolidacao": "500 em Natureza não é número arbitrário — é o corte mínimo eliminatório que você levantou pros seus alvos (IME e Politécnica-USP). Ficar abaixo elimina essas opções, independente da média final.",
    "fase3_blindagem": "Tempo aprendendo algo do zero agora compete com consolidar o que já foi estudado. Nas últimas semanas, retenção do que já é familiar rende mais que abrir tópico novo — por isso zero conteúdo pesado novo, só revisão dirigida e simulado.",
}

_FASE_METAS = {
    "fase1_fundacao": {
        "Matemática": "24-26/45 (53-58%)", "Ciências da Natureza": "estabelecer linha de base",
        "Redação": "manter 700 (confirmado)", "Humanas/Linguagens": "1 simulado completo cada, linha de base",
    },
    "fase2_consolidacao": {
        "Matemática": "28-32/45 (62-71%)", "Ciências da Natureza": "acima do corte de 500",
        "Redação": "manter 700+, erro ortográfico perto de zero", "Humanas/Linguagens": "65%+",
    },
    "fase3_blindagem": {
        "Matemática": "32-36/45 (71-80%)", "Ciências da Natureza": "500-550+",
        "Redação": "750+", "Humanas/Linguagens": "70%+",
    },
}

_FASE_ROTINA = {
    "fase1_fundacao": [
        "3 dias — Natureza: corrige prova antiga (2019, depois 2020) + pra cada questão \"não sabia o conteúdo\", disseca ela por completo em voz alta até dominar o tema (seu método já validado) + 10 questões do mesmo tema em outras provas.",
        "1 dia — Matemática: ciclo já validado (prova → corrige → foca fácil/médio), priorizando Geometria, Funções e Financeira.",
        "1 dia — Humanas + Linguagens: 1 simulado parcial (bloco de 45) + correção rápida.",
        "1 dia — Simulado completo (sábado), alternando Matemática/Natureza como foco principal.",
        "Redação: 1x/semana cronometrada + 10-15min/dia de repertório + revisão ortográfica logo depois de escrever.",
    ],
    "fase2_consolidacao": [
        "Repete o ciclo 2019-2025 em Natureza e Matemática, agora com 2 simulados completos por semana (sábado + 1 dia de meio de semana).",
        "Todas as áreas entram no ciclo de correção com categorização de erro.",
        "Redação mantém 1x/semana.",
    ],
    "fase3_blindagem": [
        "3 simulados completos por semana, crescente até a prova.",
        "Revisão dirigida só nos temas que ainda aparecerem como erro recorrente.",
        "Redação 1x/semana, mantendo estrutura — sem mudar repertório essa perto da prova.",
    ],
}

_METRICAS_ALERTA = [
    "Se Natureza não subir pelo menos 15-20 pontos (TRI estimado) até o fim da Fase 1 → o volume de conteúdo novo (vídeo/dissecação) precisa aumentar, não só volume de questão.",
    "Se um simulado completo cair mais de 15% abaixo da sua média móvel → cheque cansaço/ansiedade antes de assumir que é lacuna de conteúdo.",
    "Se erro ortográfico na redação não cair depois de 3 semanas de revisão pós-escrita → considere buscar correção externa focada nisso.",
]


def render_calendario() -> None:
    plano = db.plano_periodizacao()

    if plano["fase"] == "pos_prova":
        st.success("A prova já passou. Se ainda quiser treinar, o resto do app continua aqui.")
        return
    if plano["fase"] == "prova":
        st.success("🍀 Hoje é o dia. O trabalho já foi feito — agora é confiar nele.")
        return

    data_prova_fmt = f"{plano['data_prova'][8:10]}/{plano['data_prova'][5:7]}/{plano['data_prova'][:4]}"
    fase1_fmt = f"{plano['fase1_fim'][8:10]}/{plano['fase1_fim'][5:7]}"
    fase2_fmt = f"{plano['fase2_fim'][8:10]}/{plano['fase2_fim'][5:7]}"

    st.subheader(f"🗓️ {plano['dias_restantes']} dias até {data_prova_fmt}")
    st.caption(f"**{plano['fase_label']}** · Fase 1 até {fase1_fmt} · Fase 2 até {fase2_fmt} · Fase 3 até a prova")
    st.info(_FASE_PRINCIPIO[plano["fase"]])

    st.divider()
    st.subheader("📊 Sua média móvel (últimos simulados) vs. meta desta fase")
    st.caption(
        "Nota varia por prova, cansaço, tema sorteado — o que importa é a TENDÊNCIA da média móvel, não o "
        "resultado de um simulado isolado. \"Simulado\" aqui = qualquer dia com 15+ questões respondidas na área; "
        "se você fizer mais de um no mesmo dia, contam como um só."
    )
    metas_fase = _FASE_METAS[plano["fase"]]
    for area, chave_area in (("Matemática", "matematica"), ("Ciências da Natureza", "ciencias_natureza")):
        mm = db.media_movel_simulados(chave_area)
        col1, col2 = st.columns([1, 2])
        with col1:
            if mm["tem_dado"]:
                st.metric(area, f"{mm['media_pct']}%", help=f"média dos últimos {mm['n_simulados']} simulado(s)")
            else:
                st.metric(area, "sem dado")
        with col2:
            st.caption(f"Meta desta fase: **{metas_fase[area]}**")
            if area == "Ciências da Natureza":
                st.caption("(meta em escala TRI/nota — % de acerto é uma medida diferente, sirva de tendência, não comparação direta.)")

    ultima_redacao = next(iter(db.listar_redacoes()), None)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Redação", f"{ultima_redacao['nota']}" if ultima_redacao and ultima_redacao["nota"] is not None else "sem nota", help="última redação com nota registrada")
    with col2:
        st.caption(f"Meta desta fase: **{metas_fase['Redação']}**")
        st.caption("Humanas/Linguagens: meta desta fase é **" + metas_fase["Humanas/Linguagens"] + "** — este app não tem banco de questões dessas áreas, registre seu resultado por fora.")

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
        "(Cartão-resposta → questão errada → \"Por que errou?\") — sabemos que sua correção de Natureza é mais "
        "profunda e demora mais que a de Matemática, então é normal \"Feito\" chegar bem antes de \"Corrigido\"."
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
        rotulo_caderno = (
            p["caderno_matematica"] if p["caderno_matematica"] == p["caderno_ciencias"]
            else f"Mat. {p['caderno_matematica']} / Ciê. {p['caderno_ciencias']}"
        )
        st.write(f"{feito} **{p['ano']} — {rotulo_caderno}** — {p['respondidas']}/{p['total_questoes']} respondidas ({p['cobertura_pct']:.0f}%) · correção: {corrigido}")

    st.divider()
    st.subheader("📆 Rotina desta fase")
    for linha in _FASE_ROTINA[plano["fase"]]:
        st.write(f"- {linha}")

    st.divider()
    st.subheader("⚠️ Quando revisar o plano")
    for linha in _METRICAS_ALERTA:
        st.write(f"- {linha}")

    st.divider()
    st.caption(
        "Matemática e Ciências da Natureza são medidas com dado real deste app. Redação é registrada (não "
        "corrigida por aqui). Humanas e Linguagens precisam do próprio controle — este app não tem banco de "
        "questões dessas áreas. Isto não é previsão de aprovação — nota de corte real só existe depois da prova."
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


PASTA_REDACOES = Path(__file__).parent / "redacoes_arquivos"


def render_redacao() -> None:
    """Só guarda redação -- não corrige (o sistema não tem como avaliar
    redação de verdade). Nota e erro ortográfico vêm de correção
    própria, externa ou oficial, digitados aqui depois."""
    st.subheader("✍️ Nova redação")

    temas_usados = db.temas_redacoes_usados()
    if temas_usados:
        modo_tema = st.radio("Tema", ["Novo tema", "Reusar tema já usado"], horizontal=True, key="redacao_modo_tema")
    else:
        modo_tema = "Novo tema"
    if modo_tema == "Reusar tema já usado":
        tema = st.selectbox("Escolha o tema", temas_usados, key="redacao_tema_existente")
    else:
        tema = st.text_input("Tema (cole o enunciado ou um resumo curto)", key="redacao_tema_novo")

    col1, col2 = st.columns(2)
    with col1:
        data_escrita = st.date_input("Data", value=date.today(), key="redacao_data")
    with col2:
        fonte = st.selectbox("Correção", ["ainda sem correção", "própria", "externa", "oficial"], key="redacao_fonte")

    texto = st.text_area("Texto (se digitou)", height=200, key="redacao_texto")

    if "redacao_upload_geracao" not in st.session_state:
        st.session_state["redacao_upload_geracao"] = 0
    arquivo = st.file_uploader(
        "Foto ou PDF da redação escrita à mão (opcional)", type=["png", "jpg", "jpeg", "pdf"],
        key=f"redacao_arquivo_{st.session_state['redacao_upload_geracao']}",
    )

    col1, col2 = st.columns(2)
    with col1:
        nota = st.number_input("Nota (0-1000, se já corrigida)", min_value=0, max_value=1000, value=0, key="redacao_nota")
    with col2:
        erros_ortograficos = st.number_input("Erros ortográficos", min_value=0, max_value=100, value=0, key="redacao_erros")

    observacoes = st.text_area("Observações (opcional)", height=80, key="redacao_obs")

    if st.button("Salvar redação", type="primary", key="redacao_salvar"):
        if not tema or not tema.strip():
            st.warning("Preencha o tema antes de salvar.")
        elif not texto.strip() and arquivo is None:
            st.warning("Cole o texto ou anexe uma foto/PDF antes de salvar.")
        else:
            caminho_arquivo = None
            if arquivo is not None:
                PASTA_REDACOES.mkdir(exist_ok=True)
                extensao = Path(arquivo.name).suffix or ".pdf"
                caminho_arquivo = str(PASTA_REDACOES / f"{int(datetime.now().timestamp() * 1000)}{extensao}")
                with open(caminho_arquivo, "wb") as f:
                    f.write(arquivo.getbuffer())

            db.salvar_redacao(
                tema=tema, data_escrita=data_escrita.isoformat(), texto=texto.strip() or None,
                arquivo_path=caminho_arquivo, nota=int(nota) or None,
                erros_ortograficos=int(erros_ortograficos) if erros_ortograficos else None,
                fonte_correcao=None if fonte == "ainda sem correção" else fonte,
                observacoes=observacoes.strip() or None,
            )
            st.session_state["redacao_upload_geracao"] += 1
            st.success("Redação salva.")
            st.rerun()

    st.divider()
    st.subheader("📚 Suas redações")
    redacoes = db.listar_redacoes()
    if not redacoes:
        st.info("Nenhuma redação guardada ainda.")
        return

    notas_validas = [r["nota"] for r in redacoes if r["nota"] is not None]
    if notas_validas:
        st.caption(f"{len(redacoes)} redação(ões) guardada(s) · última nota registrada: {notas_validas[0]} · melhor: {max(notas_validas)}")
    else:
        st.caption(f"{len(redacoes)} redação(ões) guardada(s), nenhuma com nota ainda.")

    for r in redacoes:
        tema_curto = r["tema"] if len(r["tema"]) <= 60 else r["tema"][:60] + "…"
        rotulo = f"{r['data_escrita']} — {tema_curto}"
        if r["nota"] is not None:
            rotulo += f" — nota {r['nota']}"
        with st.expander(rotulo):
            detalhes = []
            if r["fonte_correcao"]:
                detalhes.append(f"correção {r['fonte_correcao']}")
            if r["erros_ortograficos"] is not None:
                detalhes.append(f"{r['erros_ortograficos']} erro(s) ortográfico(s)")
            if detalhes:
                st.caption(" · ".join(detalhes))
            if r["texto"]:
                st.write(r["texto"])
            if r["arquivo_path"] and Path(r["arquivo_path"]).exists():
                if r["arquivo_path"].lower().endswith(".pdf"):
                    st.caption(f"📎 Arquivo: `{Path(r['arquivo_path']).name}` (PDF — abra pelo Explorador de Arquivos, o app só mostra imagem inline)")
                else:
                    st.image(r["arquivo_path"], use_container_width=True)
            if r["observacoes"]:
                st.caption(r["observacoes"])

            col_editar, col_apagar = st.columns(2)
            with col_editar:
                with st.popover("✏️ Editar", key=f"popover_editar_redacao_{r['id']}"):
                    st.caption("Pra quando a correção sai depois de já ter salvo a redação sem nota.")
                    novo_tema = st.text_input("Tema", value=r["tema"], key=f"editar_tema_{r['id']}")
                    nova_data = st.date_input(
                        "Data", value=date.fromisoformat(r["data_escrita"]), key=f"editar_data_{r['id']}"
                    )
                    novo_texto = st.text_area("Texto", value=r["texto"] or "", height=150, key=f"editar_texto_{r['id']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nova_nota = st.number_input(
                            "Nota (0-1000)", min_value=0, max_value=1000,
                            value=r["nota"] or 0, key=f"editar_nota_{r['id']}",
                        )
                    with col_b:
                        novos_erros = st.number_input(
                            "Erros ortográficos", min_value=0, max_value=100,
                            value=r["erros_ortograficos"] or 0, key=f"editar_erros_{r['id']}",
                        )
                    opcoes_fonte = ["ainda sem correção", "própria", "externa", "oficial"]
                    fonte_atual = r["fonte_correcao"] or "ainda sem correção"
                    nova_fonte = st.selectbox(
                        "Correção", opcoes_fonte, index=opcoes_fonte.index(fonte_atual), key=f"editar_fonte_{r['id']}"
                    )
                    novas_obs = st.text_area("Observações", value=r["observacoes"] or "", height=80, key=f"editar_obs_{r['id']}")
                    if st.button("Salvar edição", type="primary", key=f"salvar_editar_redacao_{r['id']}"):
                        db.atualizar_redacao(
                            r["id"], tema=novo_tema, data_escrita=nova_data.isoformat(),
                            texto=novo_texto or None, nota=int(nova_nota) or None,
                            erros_ortograficos=int(novos_erros) or None,
                            fonte_correcao=None if nova_fonte == "ainda sem correção" else nova_fonte,
                            observacoes=novas_obs or None,
                        )
                        st.rerun()
            with col_apagar:
                if st.button("🗑️ Apagar", key=f"apagar_redacao_{r['id']}"):
                    if r["arquivo_path"] and Path(r["arquivo_path"]).exists():
                        Path(r["arquivo_path"]).unlink()
                    db.apagar_redacao(r["id"])
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

    st.subheader("✏️ Editar ou apagar uma questão específica")
    st.caption(
        "Pra corrigir/remover UMA questão sem mexer na prova inteira -- ex: linha extra ou "
        "número digitado errado num CSV colado. A Triagem só cobre questão ainda pendente; "
        "aqui dá pra corrigir mesmo uma já classificada."
    )
    provas_para_questao = db.listar_provas()
    if not provas_para_questao:
        st.info("Nenhuma prova cadastrada.")
    else:
        RÓTULO_AREA_ADMIN2 = {"matematica": "Matemática", "ciencias_natureza": "Ciências da Natureza"}
        opcoes_prova_q = {
            f"{ano} — {caderno} — {RÓTULO_AREA_ADMIN2.get(area, area)}": (ano, caderno, area)
            for ano, caderno, area in provas_para_questao
        }
        escolha_prova_q = st.selectbox("Prova", list(opcoes_prova_q.keys()), key="admin_questao_prova")
        ano_q, caderno_q, area_q = opcoes_prova_q[escolha_prova_q]

        numero_q = st.number_input("Número da questão", min_value=1, max_value=200, value=1, key="admin_questao_numero")
        id_questao_sel = db.gerar_id_canonico(int(ano_q), caderno_q, int(numero_q))
        detalhe = db.detalhe_questao(id_questao_sel)

        if detalhe is None:
            st.warning(f"`{id_questao_sel}` não existe nessa prova.")
        else:
            st.caption(f"`{id_questao_sel}` — status atual: {detalhe['status_classificacao']}")
            materias_area = db.materias_validas(area_q)
            col_mat, col_gab = st.columns(2)
            with col_mat:
                materia_atual = detalhe["materia"] if detalhe["materia"] in materias_area else None
                nova_materia = st.selectbox(
                    "Matéria", materias_area,
                    index=materias_area.index(materia_atual) if materia_atual else None,
                    placeholder=f"atual (fora da taxonomia): {detalhe['materia']}",
                    key=f"admin_questao_materia_{id_questao_sel}",
                )
            with col_gab:
                opcoes_letra_q = ["A", "B", "C", "D", "E"]
                novo_gabarito = st.selectbox(
                    "Gabarito", opcoes_letra_q,
                    index=opcoes_letra_q.index(detalhe["alternativa_correta"]),
                    key=f"admin_questao_gabarito_{id_questao_sel}",
                )
            if st.button("Salvar questão", type="primary", key=f"admin_questao_salvar_{id_questao_sel}"):
                if not nova_materia:
                    st.warning("Selecione uma matéria antes de salvar.")
                else:
                    db.inserir_questao(
                        ano=int(ano_q), caderno=caderno_q, numero=int(numero_q),
                        grande_area=area_q, materia=nova_materia,
                        alternativa_correta=novo_gabarito, sobrescrever=True,
                    )
                    st.success(f"`{id_questao_sel}` atualizada.")
                    st.rerun()

            with st.popover("🗑️ Apagar esta questão"):
                st.caption("Remove só essa questão (e tentativas/resoluções ligadas a ela), não a prova inteira.")
                confirmar_q = st.checkbox(
                    f"Confirmo apagar {id_questao_sel} permanentemente", key=f"admin_questao_confirmar_{id_questao_sel}"
                )
                if st.button("Apagar questão", type="primary", disabled=not confirmar_q, key=f"admin_questao_apagar_{id_questao_sel}"):
                    resultado_q = db.apagar_questao(id_questao_sel)
                    st.success(
                        f"`{id_questao_sel}` apagada. {resultado_q['tentativas_perdidas']} tentativa(s) e "
                        f"{resultado_q['resolucoes_perdidas']} resolução(ões) perdidas junto."
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


_PAGINAS = [
    ("cartao", "📝", "Cartão-resposta"),
    ("analise", "📊", "Minha análise"),
    ("simulados", "🗂️", "Simulados já feitos"),
    ("prova_beta", "🧪", "Prova com enunciado (beta)"),
    ("calendario", "📅", "Calendário"),
    ("objetivos", "🎯", "Objetivos"),
    ("redacao", "✍️", "Redação"),
    ("coletar", "🔗", "Coletar vídeos"),
    ("triagem", "🏷️", "Triagem"),
    ("admin", "🔐", "Admin"),
    ("guia", "📚", "Guia do Estudante"),
]


if __name__ == "__main__":
    st.set_page_config(page_title="Cartão-resposta", page_icon="📝", layout="wide")
    db.inicializar_banco()
    ui_theme.injetar_tema()

    # Navegação por query param (?pagina=...) em vez de st.sidebar.radio()
    # de propósito -- a sidebar nativa do Streamlit abre FECHADA por
    # padrão em tela estreita, e o botão pra abrir ficou inacessível no
    # celular do Gabriel mesmo depois de ajustar o CSS (reportado em
    # produção 2x). Um menu implementado do zero com <a href="?pagina=..">
    # simples não depende de nenhum comportamento responsivo interno do
    # Streamlit que eu não consigo testar de verdade nesta sessão --
    # funciona igual em qualquer largura de tela, verificável via DOM
    # sem precisar simular celular.
    valores_validos = {chave for chave, _, _ in _PAGINAS}
    pagina_atual = st.query_params.get("pagina", "cartao")
    if pagina_atual not in valores_validos:
        pagina_atual = "cartao"

    if pagina_atual == "prova_beta":
        ui_theme.injetar_tema_exame_claro()

    ui_theme.navegacao_lateral(_PAGINAS, pagina_atual)
    ui_theme.hero("📝 Cartão-resposta digital", _tagline_contagem_regressiva())

    if pagina_atual == "cartao":
        render_cartao_resposta()
    elif pagina_atual == "analise":
        render_analise()
    elif pagina_atual == "simulados":
        render_simulados_feitos()
    elif pagina_atual == "prova_beta":
        render_prova_beta()
    elif pagina_atual == "calendario":
        render_calendario()
    elif pagina_atual == "objetivos":
        render_objetivos()
    elif pagina_atual == "redacao":
        render_redacao()
    elif pagina_atual == "coletar":
        coletar_videos.render_coletar_videos()
    elif pagina_atual == "triagem":
        triagem.render_triagem()
    elif pagina_atual == "admin":
        render_admin()
    elif pagina_atual == "guia":
        render_guia_estudante()