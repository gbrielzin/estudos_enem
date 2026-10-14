-- =============================================================
-- 01 — ENEM GI no SQL Server (on premise = roda na SUA máquina)
-- Abra no SSMS conectado em  localhost\SQLEXPRESS  e rode com F5
-- (F5 roda tudo; selecione um trecho e F5 para rodar só ele).
-- "GO" não é SQL: é o separador de lotes do SSMS.
-- Os CSVs ficam em C:\Users\Public\enem_sql porque o serviço do SQL
-- Server não tem permissão de ler a sua Área de Trabalho.
-- =============================================================

IF DB_ID('ENEM_GI') IS NULL CREATE DATABASE ENEM_GI;
GO
USE ENEM_GI;
GO
IF SCHEMA_ID('estudo') IS NULL EXEC('CREATE SCHEMA estudo');
GO

DROP TABLE IF EXISTS estudo.tentativas;   -- filha primeiro (tem FK para questoes)
DROP TABLE IF EXISTS estudo.questoes;
GO

-- Diferente do Snowflake: aqui PK, FK e CHECK SÃO impostas.
CREATE TABLE estudo.questoes (
  id_questao          VARCHAR(40) NOT NULL PRIMARY KEY,
  ano                 INT         NOT NULL,
  caderno             VARCHAR(20) NOT NULL,
  numero_questao      INT         NOT NULL,
  grande_area         VARCHAR(30) NOT NULL,
  materia             VARCHAR(60) NOT NULL,
  alternativa_correta CHAR(1)     NOT NULL CHECK (alternativa_correta IN ('A','B','C','D','E')),
  origem              VARCHAR(20) NOT NULL,
  tri_a               FLOAT       NULL,
  tri_b               FLOAT       NULL,
  tri_c               FLOAT       NULL,
  habilidade          INT         NULL
);

CREATE TABLE estudo.tentativas (
  id_tentativa        INT          NOT NULL PRIMARY KEY,
  id_questao          VARCHAR(40)  NOT NULL
                      CONSTRAINT fk_tentativas_questoes REFERENCES estudo.questoes(id_questao),
  data_tentativa      DATETIME2(0) NOT NULL,
  resposta_escolhida  CHAR(1)      NULL,       -- NULL = deixou em branco
  resultado           VARCHAR(10)  NOT NULL CHECK (resultado IN ('acertou','errou')),
  duracao_segundos    INT          NULL
);
GO

-- BULK INSERT = o COPY INTO do SQL Server.
-- CHECK_CONSTRAINTS: sem ele o BULK INSERT PULA a checagem de FK/CHECK
-- e a constraint fica marcada como "não confiável" (is_not_trusted = 1).
BULK INSERT estudo.questoes
FROM 'C:\Users\Public\enem_sql\questoes.csv'
WITH (FORMAT = 'CSV', FIRSTROW = 2, CODEPAGE = '65001', KEEPNULLS, CHECK_CONSTRAINTS, TABLOCK);

BULK INSERT estudo.tentativas
FROM 'C:\Users\Public\enem_sql\tentativas.csv'
WITH (FORMAT = 'CSV', FIRSTROW = 2, CODEPAGE = '65001', KEEPNULLS, CHECK_CONSTRAINTS, TABLOCK);
GO

-- Conferência 1: tem que dar 1514 e 1067 (igual SQLite e Snowflake).
SELECT 'questoes' AS tabela, COUNT(*) AS linhas FROM estudo.questoes
UNION ALL
SELECT 'tentativas', COUNT(*) FROM estudo.tentativas;

-- Conferência 2: a FK foi validada na carga? (tem que dar is_not_trusted = 0)
SELECT name, is_disabled, is_not_trusted FROM sys.foreign_keys;

-- Prova de que a FK é imposta (no Snowflake isto PASSARIA):
-- descomente as 3 linhas e rode -> erro 547 "conflicted with the FOREIGN KEY constraint".
-- BEGIN TRAN;
-- INSERT INTO estudo.tentativas VALUES (999999, 'nao_existe', '2026-10-13', NULL, 'errou', NULL);
-- ROLLBACK;
