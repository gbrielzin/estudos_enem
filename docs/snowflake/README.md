# ENEM GI no Snowflake

O mesmo banco do app (SQLite) levado para um data warehouse em nuvem, para
praticar o SQL de ambiente corporativo e comparar os dialetos.

| Arquivo | O que faz |
|---|---|
| `01_criar_e_carregar.sql` | warehouse XSMALL com auto-suspend, database/schema, tabelas, file format, stage, `COPY INTO` e conferência de volume e integridade |
| `02_indicadores.sql` | 4 indicadores (acerto por matéria, evolução semanal, top 3 por área com `QUALIFY`, acerto por faixa TRI) com o equivalente em SQLite e SQL Server em comentário |

## Como reproduzir

1. Exportar as duas tabelas do `enem.db` para CSV (de dentro de `core/`):

   ```python
   import csv, sqlite3
   conn = sqlite3.connect("enem.db")
   consultas = {
       "questoes": "SELECT id_questao, ano, caderno, numero_questao, grande_area, materia,"
                   " alternativa_correta, origem, tri_a, tri_b, tri_c, habilidade FROM questoes",
       "tentativas": "SELECT id_tentativa, id_questao, data_tentativa, resposta_escolhida,"
                     " resultado, duracao_segundos FROM tentativas_usuario",
   }
   for nome, sql in consultas.items():
       cur = conn.execute(sql)
       with open(f"{nome}.csv", "w", newline="", encoding="utf-8") as f:
           w = csv.writer(f)
           w.writerow([d[0] for d in cur.description])
           w.writerows(cur)
   ```

   Os CSVs são histórico pessoal de estudo e **não** vão para o repositório.
2. Numa SQL worksheet do Snowsight, rodar `01_criar_e_carregar.sql` até o `CREATE STAGE`.
3. Subir os CSVs no stage `ENEM_GI.ESTUDO.CARGA` (Catalog → Stages → CARGA → Upload Files).
4. Rodar o resto do `01` e conferir: contagem igual à do SQLite e 0 tentativas órfãs.
5. Rodar `02_indicadores.sql` uma consulta por vez e comparar com o mesmo SQL no SQLite.

## O que muda do SQLite para o Snowflake (e o SQL Server)

| Assunto | SQLite | Snowflake | SQL Server |
|---|---|---|---|
| Contar condição | `SUM(cond)` | `COUNT_IF(cond)` | `SUM(CASE WHEN cond THEN 1 ELSE 0 END)` |
| Limitar linhas | `LIMIT n` | `LIMIT n` | `TOP n` / `FETCH NEXT n ROWS ONLY` |
| Filtrar window function | CTE | `QUALIFY` | CTE |
| Truncar para semana | `strftime('%Y-%W', d)` | `DATE_TRUNC('WEEK', d)` | `DATETRUNC(week, d)` (2022+) |
| Apelido no `GROUP BY` | aceita | aceita | não aceita |
| PK / FK | impostas (com `PRAGMA foreign_keys`) | **só informativas** — conferir órfãos com `LEFT JOIN` | impostas |
| `TEXT PRIMARY KEY` aceita NULL? | sim (só `INTEGER PRIMARY KEY` não) | `NOT NULL` é a única restrição imposta — declare explícito | não (PK implica NOT NULL) |
| Custo | arquivo local | warehouse cobra por tempo ligado (`AUTO_SUSPEND`) | servidor/licença |
