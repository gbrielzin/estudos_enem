-- =============================================================
-- 03 — Camada para o Power BI
-- Regra de negócio fica no WAREHOUSE (uma vez, versionada), não
-- espalhada em cada painel: quem ler a view (Power BI, Tableau,
-- outra pessoa) vê a mesma "faixa TRI" e o mesmo "acertou".
-- Rode no Snowsight (Ctrl+Shift+Enter roda tudo — aqui pode).
-- =============================================================
USE WAREHOUSE ENEM_WH;
USE SCHEMA ENEM_GI.ESTUDO;

-- Dimensão: uma linha por questão, com a faixa TRI já calculada.
CREATE OR REPLACE VIEW VW_DIM_QUESTAO AS
SELECT ID_QUESTAO,
       ANO,
       CADERNO,
       NUMERO_QUESTAO,
       CASE GRANDE_AREA WHEN 'matematica'        THEN 'Matemática'
                        WHEN 'ciencias_natureza' THEN 'Ciências da Natureza'
                        ELSE GRANDE_AREA END                     AS AREA,
       -- marcador da feature do YouTube descontinuada não é matéria
       IFF(MATERIA = 'sem_video_pendente', '(não classificada)', MATERIA) AS MATERIA,
       ORIGEM,
       HABILIDADE,
       TRI_B,
       CASE WHEN TRI_B IS NULL  THEN 'Sem TRI'
            WHEN TRI_B <  1.0   THEN '1. Fácil'
            WHEN TRI_B <= 2.0   THEN '2. Média'
            ELSE                     '3. Difícil' END            AS FAIXA_TRI
FROM QUESTOES;
-- CREATE OR REPLACE recria a view e ela perde o GRANT. Se o papel do 04 já existe
-- (recriação), devolva a permissão; na primeira vez o 04 cuida disso.
-- GRANT SELECT ON VIEW VW_DIM_QUESTAO TO ROLE LEITOR_ENEM;

-- Fato: uma linha por tentativa, com data separada da hora e um
-- indicador 0/1 que vira soma/média direto no Power BI.
CREATE OR REPLACE VIEW VW_FATO_TENTATIVA AS
SELECT ID_TENTATIVA,
       ID_QUESTAO,
       DATA_TENTATIVA,
       DATA_TENTATIVA::DATE                                     AS DATA,
       DATE_TRUNC('WEEK', DATA_TENTATIVA)::DATE                 AS SEMANA,
       RESPOSTA_ESCOLHIDA,
       RESULTADO,
       IFF(RESULTADO = 'acertou', 1, 0)                         AS ACERTOU,
       IFF(RESPOSTA_ESCOLHIDA IS NULL, 1, 0)                    AS EM_BRANCO,
       DURACAO_SEGUNDOS
FROM TENTATIVAS;
-- GRANT SELECT ON VIEW VW_FATO_TENTATIVA TO ROLE LEITOR_ENEM;

-- Conferência: as views têm que ter as mesmas linhas das tabelas.
SELECT (SELECT COUNT(*) FROM VW_DIM_QUESTAO)    AS DIM_QUESTAO,     -- 1514
       (SELECT COUNT(*) FROM VW_FATO_TENTATIVA) AS FATO_TENTATIVA;  -- 1067
