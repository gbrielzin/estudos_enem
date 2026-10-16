-- =============================================================
-- 04 — Usuário só de LEITURA para o Power BI (privilégio mínimo)
-- O Power BI não precisa (e não deve) entrar como ACCOUNTADMIN.
-- Se a senha deste usuário vazar, ele só consegue LER as views.
-- Rode no Snowsight como ACCOUNTADMIN.
-- >>> Troque o texto da senha por uma sua (14+ caracteres, com
--     maiúscula, minúscula e número). Não salve a senha neste arquivo.
-- =============================================================
USE ROLE ACCOUNTADMIN;

-- 1) Papel (role) que só lê o schema ESTUDO e usa o warehouse.
CREATE ROLE IF NOT EXISTS LEITOR_ENEM;
GRANT USAGE  ON WAREHOUSE ENEM_WH              TO ROLE LEITOR_ENEM;
GRANT USAGE  ON DATABASE  ENEM_GI              TO ROLE LEITOR_ENEM;
GRANT USAGE  ON SCHEMA    ENEM_GI.ESTUDO       TO ROLE LEITOR_ENEM;
GRANT SELECT ON ALL VIEWS IN SCHEMA ENEM_GI.ESTUDO TO ROLE LEITOR_ENEM;

-- 2) Usuário do Power BI com esse papel como padrão.
CREATE USER IF NOT EXISTS POWERBI_LEITOR
  PASSWORD          = 'TROQUE-POR-UMA-SENHA-SUA'
  DEFAULT_ROLE      = LEITOR_ENEM
  DEFAULT_WAREHOUSE = ENEM_WH
  DEFAULT_NAMESPACE = ENEM_GI.ESTUDO
  COMMENT           = 'Somente leitura, usado pelo Power BI Desktop';
GRANT ROLE LEITOR_ENEM TO USER POWERBI_LEITOR;

-- 3) Conferência: o que esse papel pode fazer (só USAGE e SELECT).
SHOW GRANTS TO ROLE LEITOR_ENEM;
