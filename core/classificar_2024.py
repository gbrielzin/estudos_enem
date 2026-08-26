"""
classificar_2024.py — aplica classificação de matéria lida diretamente
do enunciado real das questões (não do título de vídeo) nas posições
de 2024 que ainda estavam pendentes. Roda uma vez, de dentro de core/.
"""
import db

classificacoes_2024 = {
    150: "geometria_plana", 156: "funcao_1_grau", 161: "interpretacao_de_grafico",
    163: "geometria_plana", 165: "probabilidade", 166: "razao_e_proporcao",
    167: "aritmetica", 168: "interpretacao_de_grafico", 169: "probabilidade",
    170: "logaritmo", 171: "geometria_plana", 172: "razao_e_proporcao",
    173: "probabilidade", 174: "geometria_espacial", 180: "analise_combinatoria",
}

for numero, materia in classificacoes_2024.items():
    id_q = db.gerar_id_canonico(2024, "Azul", numero)
    with db._conectar() as conn:
        gabarito = conn.execute(
            "SELECT alternativa_correta, grande_area FROM questoes WHERE id_questao=?", (id_q,)
        ).fetchone()
    if not gabarito:
        print(f"{numero}: questão não encontrada, pulei")
        continue
    _, status = db.inserir_questao(
        ano=2024, caderno="Azul", numero=numero,
        grande_area=gabarito[1] or "matematica", materia=materia,
        alternativa_correta=gabarito[0], sobrescrever=True,
    )
    print(f"{numero}: {materia} -> {status}")
