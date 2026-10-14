-- =============================================================
-- 02 — 4 indicadores do ENEM GI no Snowflake
-- Cada consulta tem embaixo, em comentário, o jeito de escrever a
-- mesma coisa no SQLite (meu projeto) e no SQL Server — é isso que
-- a vaga chama de "SQL on premise (SQL Server/Oracle/DB2) e nuvem".
-- =============================================================
USE WAREHOUSE ENEM_WH;
USE SCHEMA ENEM_GI.ESTUDO;

-- -------------------------------------------------------------
-- 1) Taxa de acerto por matéria (só matéria com 10+ tentativas)
--    Pergunta de negócio: onde eu mais erro?
-- -------------------------------------------------------------
SELECT q.GRANDE_AREA,
       q.MATERIA,
       COUNT(*)                                                        AS TENTATIVAS,
       ROUND(100 * COUNT_IF(t.RESULTADO = 'acertou') / COUNT(*), 1)    AS PCT_ACERTO
FROM TENTATIVAS t
JOIN QUESTOES q ON q.ID_QUESTAO = t.ID_QUESTAO
GROUP BY q.GRANDE_AREA, q.MATERIA
HAVING COUNT(*) >= 10
ORDER BY PCT_ACERTO ASC
LIMIT 5;
-- Snowflake: COUNT_IF(condição) conta só as linhas verdadeiras.
-- SQLite:    SUM(t.resultado = 'acertou')  (comparação vira 0/1)            ... LIMIT 5
-- SQL Server: SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END)
--             e no lugar de LIMIT 5:  SELECT TOP 5 ...  (ou OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY)
-- Atenção SQL Server: 100 * inteiro / inteiro = divisão INTEIRA -> use 100.0


-- -------------------------------------------------------------
-- 2) Evolução semanal (volume e % de acerto por semana)
--    Pergunta de negócio: estou melhorando ou só fazendo mais?
-- -------------------------------------------------------------
SELECT DATE_TRUNC('WEEK', t.DATA_TENTATIVA)::DATE                     AS SEMANA,
       COUNT(*)                                                        AS TENTATIVAS,
       ROUND(100 * COUNT_IF(t.RESULTADO = 'acertou') / COUNT(*), 1)    AS PCT_ACERTO
FROM TENTATIVAS t
GROUP BY SEMANA
ORDER BY SEMANA;
-- Snowflake: DATE_TRUNC('WEEK', data) = segunda-feira da semana; pode usar o apelido SEMANA no GROUP BY.
-- SQLite:    strftime('%Y-%W', data_tentativa)  (texto 'ano-nºsemana', também começa na segunda)
-- SQL Server 2022+: DATETRUNC(week, data)  | antigos: DATEADD(week, DATEDIFF(week, 0, data), 0)
--            e SQL Server NÃO aceita apelido no GROUP BY: repita a expressão inteira.


-- -------------------------------------------------------------
-- 3) Top 3 matérias com mais erro POR ÁREA (window function)
--    Pergunta de negócio: o que estudar primeiro em cada área?
-- -------------------------------------------------------------
SELECT q.GRANDE_AREA,
       q.MATERIA,
       COUNT(*)                                                        AS TENTATIVAS,
       ROUND(100 * COUNT_IF(t.RESULTADO = 'errou') / COUNT(*), 1)      AS PCT_ERRO,
       ROW_NUMBER() OVER (PARTITION BY q.GRANDE_AREA ORDER BY PCT_ERRO DESC) AS POSICAO
FROM TENTATIVAS t
JOIN QUESTOES q ON q.ID_QUESTAO = t.ID_QUESTAO
GROUP BY q.GRANDE_AREA, q.MATERIA
HAVING COUNT(*) >= 10
QUALIFY POSICAO <= 3
ORDER BY q.GRANDE_AREA, POSICAO;
-- Snowflake: QUALIFY filtra pelo resultado da window function, sem subconsulta.
-- SQLite e SQL Server NÃO têm QUALIFY: precisa de CTE.
--   WITH por_materia AS (... GROUP BY ... HAVING ...),
--        ranking AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY grande_area ORDER BY pct_erro DESC) AS posicao
--                    FROM por_materia)
--   SELECT * FROM ranking WHERE posicao <= 3;


-- -------------------------------------------------------------
-- 4) Acerto por faixa de dificuldade TRI (parâmetro b do INEP)
--    Pergunta de negócio: eu acerto as fáceis? (no TRI, errar
--    fácil e acertar difícil derruba a nota — "incoerência")
-- -------------------------------------------------------------
SELECT CASE
         WHEN q.TRI_B <  1.0 THEN '1_facil'
         WHEN q.TRI_B <= 2.0 THEN '2_media'
         ELSE                     '3_dificil'
       END                                                             AS FAIXA_TRI,
       COUNT(*)                                                        AS TENTATIVAS,
       ROUND(100 * COUNT_IF(t.RESULTADO = 'acertou') / COUNT(*), 1)    AS PCT_ACERTO
FROM TENTATIVAS t
JOIN QUESTOES q ON q.ID_QUESTAO = t.ID_QUESTAO
WHERE q.TRI_B IS NOT NULL
GROUP BY FAIXA_TRI
ORDER BY FAIXA_TRI;
-- Mesmos cortes de db.nivel_tri() no projeto (CORTE_TRI_FACIL=1.0, CORTE_TRI_DIFICIL=2.0).
-- CASE é igual nos três bancos; só muda o COUNT_IF (ver consulta 1).


-- -------------------------------------------------------------
-- Bônus) Quanto custou: histórico das consultas que você rodou
-- -------------------------------------------------------------
SELECT QUERY_TEXT, TOTAL_ELAPSED_TIME AS MS, BYTES_SCANNED
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
ORDER BY START_TIME DESC
LIMIT 10;
