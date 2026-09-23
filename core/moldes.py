"""
moldes.py — "molde" de questão: uma questão oficial do ENEM (a âncora) vira
um gerador de variações com números trocados, pra repetir o MESMO raciocínio
até sair sozinho.

Nasceu de uma sessão de estudo real (2026-09-23, ver
docs/metodo_e_aprendizados.md seção 6): questões que o aluno não conseguia
nem montar (carro elétrico, aquário, frenagem) saíram sozinhas depois de 2-3
variações com números novos. O caminho que funcionou foi
questão oficial -> kit (fórmula + gatilho + apelido) -> variações -> revisão.

Por construção, não repete dois erros que aconteceram à mão naquela sessão:
  - a resposta certa é CALCULADA a partir dos parâmetros sorteados, então
    nunca fica fora das alternativas;
  - as alternativas erradas não são aleatórias: cada uma é o resultado de
    um erro típico ("passo pela metade", unidade esquecida, sinal trocado),
    com o motivo guardado em `distratores`, o mesmo tipo de armadilha que o
    ENEM usa.

Módulo puro (só stdlib, não toca no banco): a âncora é referenciada pelo
id_questao, mas nada aqui lê ou grava enem.db. api.py expõe via /moldes.
"""
from __future__ import annotations

import random

LETRAS = "ABCDE"


def _fmt(valor: float) -> str:
    """Número no formato de alternativa do ENEM: vírgula decimal, no
    máximo 2 casas, sem zeros sobrando (0.90 -> '0,9', 5.0 -> '5')."""
    texto = f"{round(valor, 2):.2f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def _montar_alternativas(correta: float, candidatos: list[tuple[float, str]], rng: random.Random) -> dict:
    """1 correta + 4 distratores distintos (pelo texto formatado), em
    ordem crescente como no ENEM. Se os erros típicos coincidirem entre
    si ou com a correta pra esses números, completa com múltiplos da
    correta, pra sempre ter 5 alternativas diferentes."""
    usados = {_fmt(correta)}
    distratores: list[tuple[float, str]] = []
    for valor, motivo in candidatos:
        # round(valor, 2) == 0 descarta erro que dá número minúsculo: viraria
        # uma alternativa "0", que não parece resposta de ENEM.
        if round(valor, 2) > 0 and _fmt(valor) not in usados and len(distratores) < 4:
            usados.add(_fmt(valor))
            distratores.append((valor, motivo))
    fator = 2
    while len(distratores) < 4:
        valor = correta * fator if fator % 2 == 0 else correta / fator
        if _fmt(valor) not in usados:
            usados.add(_fmt(valor))
            distratores.append((valor, "valor de preenchimento (sem erro típico associado)"))
        fator += 1

    todas = sorted([(correta, None)] + distratores, key=lambda par: par[0])
    alternativas, motivos, letra_correta = {}, {}, None
    for letra, (valor, motivo) in zip(LETRAS, todas):
        alternativas[letra] = _fmt(valor)
        if motivo is None:
            letra_correta = letra
        else:
            motivos[letra] = motivo
    return {"alternativas": alternativas, "correta": letra_correta, "distratores": motivos}


# ------------------------------------------------------------
# Molde 1 — carro elétrico (âncora 2021_azul_128)
# ------------------------------------------------------------

def _carro_eletrico(p: dict) -> dict:
    energia = p["distancia_km"] / p["desempenho"]  # kWh
    potencia_kw = p["tensao"] * p["corrente"] / 1000
    tempo = energia / potencia_kw
    return {
        "enunciado": (
            f"Após percorrer {_fmt(p['distancia_km'])} km, um motorista vai recarregar seu carro elétrico, "
            f"de desempenho médio {_fmt(p['desempenho'])} km/kWh, num carregador ideal de "
            f"{_fmt(p['tensao'])} V percorrido por uma corrente de {_fmt(p['corrente'])} A. "
            "Quantas horas são necessárias para recarregar a energia usada no percurso?"
        ),
        "resposta": tempo,
        "passos": [
            f"Energia gasta: {_fmt(p['distancia_km'])} ÷ {_fmt(p['desempenho'])} = {_fmt(energia)} kWh",
            f"Potência (PiVI): {_fmt(p['tensao'])} × {_fmt(p['corrente'])} = {_fmt(potencia_kw * 1000)} W = {_fmt(potencia_kw)} kW",
            f"Tempo (É Pt, tampando o t): {_fmt(energia)} ÷ {_fmt(potencia_kw)} = {_fmt(tempo)} h",
        ],
        "candidatos": [
            (energia / (p["tensao"] * p["corrente"]), "não converteu W para kW"),
            (p["distancia_km"] / potencia_kw, "usou a distância no lugar da energia"),
            (energia * potencia_kw, "multiplicou em vez de dividir"),
            (potencia_kw / energia, "inverteu a divisão (potência ÷ energia)"),
            (tempo * 60, "deu a resposta em minutos"),
        ],
    }


def _sortear_carro_eletrico(rng: random.Random) -> dict:
    desempenho = rng.choice([4, 5, 6, 8])
    energia = rng.randrange(10, 41, 2)
    return {
        "distancia_km": energia * desempenho,
        "desempenho": desempenho,
        "tensao": rng.choice([110, 127, 200, 220, 250]),
        "corrente": rng.choice([10, 16, 20, 25, 32]),
    }


# ------------------------------------------------------------
# Molde 2 — aquário / calorimetria (âncora 2020_azul_128)
# ------------------------------------------------------------

CALOR_ESPECIFICO_AGUA = 4.0  # kJ/(kg·°C), valor dado no enunciado original


def _aquario(p: dict) -> dict:
    massa = p["volume_l"]  # densidade 1 kg/L
    segundos = p["horas"] * 3600
    calor_kj = p["potencia_w"] * segundos / 1000
    delta_t = calor_kj / (massa * CALOR_ESPECIFICO_AGUA)
    return {
        "enunciado": (
            f"Um aquário tem {_fmt(p['volume_l'])} L de água (densidade 1 kg/L, calor específico "
            f"{_fmt(CALOR_ESPECIFICO_AGUA)} kJ/kg·°C). Seu aquecedor de {_fmt(p['potencia_w'])} W compensa "
            f"exatamente a perda de calor da água. Se o aquecedor for desligado por {_fmt(p['horas'])} h, "
            "qual a redução da temperatura da água, em °C?"
        ),
        "resposta": delta_t,
        "passos": [
            f"Massa: {_fmt(p['volume_l'])} L = {_fmt(massa)} kg",
            f"Energia perdida (É Pt, W = J/s): {_fmt(p['potencia_w'])} × {_fmt(segundos)} s = {_fmt(calor_kj)} kJ",
            f"ΔT (Que macete, tampando o ΔT): {_fmt(calor_kj)} ÷ ({_fmt(massa)} × {_fmt(CALOR_ESPECIFICO_AGUA)}) = {_fmt(delta_t)} °C",
        ],
        "candidatos": [
            (calor_kj / massa, "esqueceu o calor específico"),
            (calor_kj / (massa + CALOR_ESPECIFICO_AGUA), "somou massa e calor específico em vez de multiplicar"),
            (calor_kj / CALOR_ESPECIFICO_AGUA, "esqueceu de dividir pela massa"),
            (p["potencia_w"] * p["horas"] * 60 / 1000 / (massa * CALOR_ESPECIFICO_AGUA), "converteu horas só para minutos (× 60), não para segundos"),
            (calor_kj * 1000 / (massa * CALOR_ESPECIFICO_AGUA), "deixou a energia em J (não converteu para kJ)"),
        ],
    }


def _sortear_aquario(rng: random.Random) -> dict:
    return {
        "volume_l": rng.choice([20, 40, 50, 60, 80, 100]),
        "potencia_w": rng.choice([25, 50, 100, 150, 200]),
        "horas": rng.choice([1, 2, 3]),
    }


# ------------------------------------------------------------
# Molde 3 — frenagem com tempo de reação (âncora 2017_azul_131)
# ------------------------------------------------------------

def _frenagem(p: dict) -> dict:
    v0, a, d, dt = p["v_atento"], p["aceleracao"], p["desaceleracao"], p["segundos_a_mais"]
    v1 = v0 + a * dt
    trecho_extra = (v1 ** 2 - v0 ** 2) / (2 * a)
    freio_atento = v0 ** 2 / (2 * d)
    freio_desatento = v1 ** 2 / (2 * d)
    resposta = trecho_extra + freio_desatento - freio_atento
    return {
        "enunciado": (
            f"Dois motoristas aceleram seus carros a {_fmt(a)} m/s². Numa emergência, freiam com "
            f"desaceleração de {_fmt(d)} m/s². O atento aciona o freio a {_fmt(v0)} m/s; o desatento, "
            f"distraído com o celular, leva {_fmt(dt)} s a mais para começar a frear. Que distância, em "
            "metros, o desatento percorre a mais que o atento até a parada total?"
        ),
        "resposta": resposta,
        "passos": [
            f"Velocidade do desatento ao frear (Vovô Ateu): {_fmt(v0)} + {_fmt(a)} × {_fmt(dt)} = {_fmt(v1)} m/s",
            f"Trecho extra acelerando (Torricelli, a positivo): ({_fmt(v1)}² − {_fmt(v0)}²) ÷ (2 × {_fmt(a)}) = {_fmt(trecho_extra)} m",
            f"Frenagens (Torricelli, a negativo): atento {_fmt(freio_atento)} m, desatento {_fmt(freio_desatento)} m",
            f"Total: ({_fmt(trecho_extra)} + {_fmt(freio_desatento)}) − {_fmt(freio_atento)} = {_fmt(resposta)} m",
        ],
        "candidatos": [
            (freio_desatento - freio_atento, "só a diferença das frenagens (esqueceu o trecho extra)"),
            (trecho_extra, "só o trecho extra (esqueceu as frenagens)"),
            (trecho_extra + freio_desatento, "distância total do desatento (esqueceu de subtrair o atento)"),
            (v0 * dt, "trecho extra como se fosse velocidade constante, sem as frenagens"),
            (freio_desatento, "só a frenagem do desatento"),
        ],
    }


def _sortear_frenagem(rng: random.Random) -> dict:
    return {
        "v_atento": rng.choice([8, 10, 12, 14, 16, 20]),
        "aceleracao": rng.choice([1, 2]),
        "desaceleracao": rng.choice([4, 5]),
        "segundos_a_mais": rng.choice([1, 2]),
    }


# ------------------------------------------------------------
# Catálogo
# ------------------------------------------------------------

MOLDES: dict[str, dict] = {
    "carro_eletrico": {
        "titulo": "Recarga de carro elétrico",
        "materia": "eletrodinamica",
        "id_questao_ancora": "2021_azul_128",
        "kit": [
            {"formula": "P = V × I", "apelido": "PiVI", "gatilho": "tem volts e ampères, pede potência"},
            {"formula": "E = P × t", "apelido": "É Pt", "gatilho": "tem kWh, horas ou consumo"},
        ],
        "unidade": "h",
        "original": {"distancia_km": 110, "desempenho": 5, "tensao": 220, "corrente": 20},
        "resposta_original": 5.0,
        "calcular": _carro_eletrico,
        "sortear": _sortear_carro_eletrico,
    },
    "aquario": {
        "titulo": "Aquário sem aquecedor",
        "materia": "termologia",
        "id_questao_ancora": "2020_azul_128",
        "kit": [
            {"formula": "E = P × t (W = J/s)", "apelido": "É Pt", "gatilho": "aparelho em watts ligado/desligado por um tempo"},
            {"formula": "Q = m × c × ΔT", "apelido": "Que macete", "gatilho": "tem calor específico, pede quanto a temperatura muda"},
        ],
        "unidade": "°C",
        "original": {"volume_l": 50, "potencia_w": 50, "horas": 1},
        "resposta_original": 0.9,
        "calcular": _aquario,
        "sortear": _sortear_aquario,
    },
    "frenagem": {
        "titulo": "Frenagem com o celular",
        "materia": "cinematica",
        "id_questao_ancora": "2017_azul_131",
        "kit": [
            {"formula": "v = v₀ + a × t", "apelido": "Vovô Ateu", "gatilho": "tem tempo e velocidade"},
            {"formula": "v² = v₀² + 2 × a × Δs", "apelido": "Torricelli", "gatilho": "sem tempo, pede distância (frenagem)"},
        ],
        "unidade": "m",
        "original": {"v_atento": 14, "aceleracao": 1, "desaceleracao": 5, "segundos_a_mais": 1},
        "resposta_original": 17.4,
        "calcular": _frenagem,
        "sortear": _sortear_frenagem,
    },
}


def listar_moldes() -> list[dict]:
    """Metadados + kit de cada molde (sem gerar variação)."""
    return [
        {
            "id_molde": id_molde,
            "titulo": m["titulo"],
            "materia": m["materia"],
            "id_questao_ancora": m["id_questao_ancora"],
            "kit": m["kit"],
        }
        for id_molde, m in MOLDES.items()
    ]


def gerar_variacao(id_molde: str, seed: int | None = None, original: bool = False) -> dict:
    """Gera uma variação do molde. `seed` fixa o sorteio (mesma seed = mesma
    questão, pra poder refazer exatamente a mesma variação); `original=True`
    usa os números da questão âncora, o que serve pra conferir que o molde
    reproduz o gabarito oficial. ValueError se o molde não existe."""
    if id_molde not in MOLDES:
        raise ValueError(f"Molde '{id_molde}' não existe.")
    molde = MOLDES[id_molde]
    rng = random.Random(seed)
    parametros = dict(molde["original"]) if original else molde["sortear"](rng)
    calculado = molde["calcular"](parametros)
    montagem = _montar_alternativas(calculado["resposta"], calculado["candidatos"], rng)
    return {
        "id_molde": id_molde,
        "id_questao_ancora": molde["id_questao_ancora"],
        "seed": seed,
        "parametros": parametros,
        "enunciado": calculado["enunciado"],
        "unidade": molde["unidade"],
        "alternativas": montagem["alternativas"],
        "correta": montagem["correta"],
        "distratores": montagem["distratores"],
        "passos": calculado["passos"],
        "kit": molde["kit"],
    }
