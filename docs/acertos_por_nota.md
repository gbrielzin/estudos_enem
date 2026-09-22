# Quantos acertos equivalem a cada nota (por área)

Gerado por `core/acertos_por_nota.py` (rodar de dentro de `core/`). Fonte: parâmetros TRI dos itens do INEP (`core/inep_itens/`, ver `docs/inep_parametros_itens.md`), anos 2020 a 2025.

## Método e limites

- Modelo de 3 parâmetros, D = 1,7, nota = 500 + 100 x theta (mesma suposição de `core/valor_por_questao.py`).
- Uma prova do caderno azul por ano e área (menor `CO_PROVA` com 40+ itens; sem itens abandonados ou adaptados; em Linguagens, sem os itens de espanhol). O número de itens fica entre 41 e 45.
- O resultado é **acerto esperado**, não previsão. A nota oficial pesa a coerência do padrão de respostas: acertar difícil e errar fácil rende menos que a soma sugere.
- **Validação:** para Natureza reproduz exatamente a tabela de `docs/plano_50_dias_v1.md` (2020: 10,4 / 14,4 / 21,3 / 29,5 / 36,9 / 40,8).
- A escala 500 + 100 x theta é uma suposição padrão, não a calibração oficial de cada área.

## Resultado (mediana de 2020 a 2025; entre parênteses, a faixa entre anos)

| Nota | Natureza | Matemática | Humanas | Linguagens |
|---|---|---|---|---|
| 500 | 10 (8-12) | 9 (7-10) | 12 (11-16) | 15 (12-17) |
| 550 | 14 (10-16) | 11 (9-12) | 17 (15-23) | 22 (19-24) |
| 600 | 20 (15-22) | 15 (12-16) | 26 (22-33) | 30 (26-33) |
| 650 | 28 (24-30) | 21 (16-22) | 34 (32-38) | 36 (33-40) |
| 700 | 35 (32-37) | 28 (22-31) | 40 (39-42) | 40 (37-43) |
| 750 | 40 (37-42) | 35 (29-38) | 43 (41-43) | 43 (40-44) |
| 800 | 42 (39-44) | 40 (35-42) | 44 (43-44) | 44 (41-45) |

## Leitura

- Entre 600 e 750, cada +50 pontos custa de **6 a 8 acertos** em qualquer área.
- Humanas e Linguagens encostam no teto cedo (42 a 43 acertos já em 750). Natureza e Matemática têm mais espaço para subir.
- A faixa entre anos é de 3 a 6 acertos: uma prova isolada não mede a nota; a média de duas ou mais mede melhor.
