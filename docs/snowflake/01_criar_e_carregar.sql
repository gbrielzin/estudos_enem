-- =============================================================
-- 01 — Cria o banco, as tabelas e carrega os CSVs no Snowflake
-- Rode numa SQL Worksheet do Snowsight, de cima para baixo
-- (Ctrl+Enter roda a linha/bloco onde está o cursor;
--  Ctrl+Shift+Enter roda tudo).
-- =============================================================

-- Warehouse = o "motor" que executa a consulta (cobra por tempo ligado).
-- XSMALL + auto_suspend 60s = gasta o mínimo dos créditos do trial.
CREATE WAREHOUSE IF NOT EXISTS ENEM_WH
  WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
USE WAREHOUSE ENEM_WH;

-- Database > Schema > Tabela (no SQLite não existe essa hierarquia).
CREATE DATABASE IF NOT EXISTS ENEM_GI;
CREATE SCHEMA IF NOT EXISTS ENEM_GI.ESTUDO;
USE SCHEMA ENEM_GI.ESTUDO;

-- Tipos: TEXT no SQLite vira VARCHAR; REAL vira FLOAT; data vira TIMESTAMP_NTZ
-- (NTZ = sem fuso, igual ao que o app grava: hora local).
CREATE OR REPLACE TABLE QUESTOES (
  ID_QUESTAO          VARCHAR PRIMARY KEY,   -- no Snowflake PK/FK são só informativas: NÃO são impostas
  ANO                 INTEGER NOT NULL,
  CADERNO             VARCHAR NOT NULL,
  NUMERO_QUESTAO      INTEGER NOT NULL,
  GRANDE_AREA         VARCHAR NOT NULL,
  MATERIA             VARCHAR NOT NULL,
  ALTERNATIVA_CORRETA VARCHAR(1) NOT NULL,
  ORIGEM              VARCHAR NOT NULL,
  TRI_A               FLOAT,
  TRI_B               FLOAT,
  TRI_C               FLOAT,
  HABILIDADE          INTEGER
);

CREATE OR REPLACE TABLE TENTATIVAS (
  ID_TENTATIVA        INTEGER PRIMARY KEY,
  ID_QUESTAO          VARCHAR NOT NULL REFERENCES QUESTOES(ID_QUESTAO),
  DATA_TENTATIVA      TIMESTAMP_NTZ NOT NULL,
  RESPOSTA_ESCOLHIDA  VARCHAR(1),            -- NULL = deixou em branco
  RESULTADO           VARCHAR NOT NULL,
  DURACAO_SEGUNDOS    INTEGER
);

-- Formato do arquivo: CSV com cabeçalho, campo vazio = NULL.
CREATE OR REPLACE FILE FORMAT CSV_ENEM
  TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  EMPTY_FIELD_AS_NULL = TRUE NULL_IF = ('');

-- Stage = "pasta" do Snowflake onde o arquivo fica antes de virar tabela.
CREATE OR REPLACE STAGE CARGA FILE_FORMAT = CSV_ENEM;

-- >>> PARE AQUI e suba os 2 CSVs no stage pela interface:
--     Catalog (ou Data) > Databases > ENEM_GI > ESTUDO > Stages > CARGA
--     > botão "+ Files" > arraste questoes.csv e tentativas.csv > Upload.
-- Depois confira:
LIST @CARGA;

-- COPY INTO = o "INSERT em lote" do Snowflake, do stage para a tabela.
COPY INTO QUESTOES   FROM @CARGA/questoes.csv;
COPY INTO TENTATIVAS FROM @CARGA/tentativas.csv;

-- Conferência: tem que dar 1514 e 1067 (os mesmos números do SQLite).
SELECT 'questoes' AS tabela, COUNT(*) AS linhas FROM QUESTOES
UNION ALL
SELECT 'tentativas', COUNT(*) FROM TENTATIVAS;

-- Como PK/FK não são impostas, a integridade se confere com consulta:
-- tentativa apontando para questão que não existe (tem que dar 0).
SELECT COUNT(*) AS tentativas_orfas
FROM TENTATIVAS t LEFT JOIN QUESTOES q ON q.ID_QUESTAO = t.ID_QUESTAO
WHERE q.ID_QUESTAO IS NULL;
