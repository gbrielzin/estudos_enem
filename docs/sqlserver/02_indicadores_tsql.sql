-- =============================================================
-- 02 — Os mesmos 4 indicadores, em T-SQL (dialeto do SQL Server)
-- Selecione uma consulta e aperte F5. Os números têm que bater
-- com o Snowflake (ver LEIA.md).
-- =============================================================
USE ENEM_GI;
GO

-- -------------------------------------------------------------
-- 1) Taxa de acerto por matéria (10+ tentativas)
-- -------------------------------------------------------------
SELECT TOP 5                                   -- no lugar do LIMIT 5
       q.grande_area,
       q.materia,
       COUNT(*) AS tentativas,
       CAST(100.0 * SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END) / COUNT(*)
            AS DECIMAL(5,1)) AS pct_acerto     -- 100.0: com 100 seria divisão INTEIRA
FROM estudo.tentativas t
JOIN estudo.questoes q ON q.id_questao = t.id_questao
GROUP BY q.grande_area, q.materia
HAVING COUNT(*) >= 10
ORDER BY pct_acerto ASC;                       -- apelido vale no ORDER BY, não no GROUP BY


-- -------------------------------------------------------------
-- 2) Evolução semanal
-- PEGADINHA: o SQL Server (configuração americana) começa a semana
-- no DOMINGO. Snowflake e SQLite começam na segunda. Sem o
-- SET DATEFIRST 1, as 80 tentativas feitas em domingos caem na
-- semana errada e os números não batem.
-- -------------------------------------------------------------
SET DATEFIRST 1;   -- 1 = segunda-feira
SELECT CAST(DATETRUNC(week, t.data_tentativa) AS DATE) AS semana,     -- DATETRUNC: SQL Server 2022+
       COUNT(*) AS tentativas,
       CAST(100.0 * SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END) / COUNT(*)
            AS DECIMAL(5,1)) AS pct_acerto
FROM estudo.tentativas t
GROUP BY CAST(DATETRUNC(week, t.data_tentativa) AS DATE)              -- repete a expressão: GROUP BY não aceita apelido
ORDER BY semana;


-- -------------------------------------------------------------
-- 3) Top 3 matérias com mais erro por área
-- Não existe QUALIFY no SQL Server: filtra a window function numa CTE.
-- -------------------------------------------------------------
WITH por_materia AS (
    SELECT q.grande_area,
           q.materia,
           COUNT(*) AS tentativas,
           CAST(100.0 * SUM(CASE WHEN t.resultado = 'errou' THEN 1 ELSE 0 END) / COUNT(*)
                AS DECIMAL(5,1)) AS pct_erro
    FROM estudo.tentativas t
    JOIN estudo.questoes q ON q.id_questao = t.id_questao
    GROUP BY q.grande_area, q.materia
    HAVING COUNT(*) >= 10
),
ranking AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY grande_area ORDER BY pct_erro DESC) AS posicao
    FROM por_materia
)
SELECT * FROM ranking
WHERE posicao <= 3
ORDER BY grande_area, posicao;


-- -------------------------------------------------------------
-- 4) Acerto por faixa de dificuldade TRI
-- CROSS APPLY (VALUES ...) calcula a faixa UMA vez e dá um nome
-- que pode ser usado no GROUP BY — truque clássico de T-SQL.
-- -------------------------------------------------------------
SELECT f.faixa_tri,
       COUNT(*) AS tentativas,
       CAST(100.0 * SUM(CASE WHEN t.resultado = 'acertou' THEN 1 ELSE 0 END) / COUNT(*)
            AS DECIMAL(5,1)) AS pct_acerto
FROM estudo.tentativas t
JOIN estudo.questoes q ON q.id_questao = t.id_questao
CROSS APPLY (VALUES (CASE WHEN q.tri_b <  1.0 THEN '1_facil'
                          WHEN q.tri_b <= 2.0 THEN '2_media'
                          ELSE                     '3_dificil' END)) AS f(faixa_tri)
WHERE q.tri_b IS NOT NULL
GROUP BY f.faixa_tri
ORDER BY f.faixa_tri;


-- -------------------------------------------------------------
-- Bônus) Plano de execução: Ctrl+M liga "Include Actual Execution
-- Plan"; rode a consulta 1 de novo e veja a aba "Execution plan"
-- (Clustered Index Scan, Hash Match...). Pergunta clássica de entrevista.
-- -------------------------------------------------------------
