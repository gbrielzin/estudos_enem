# ADR-0002: SQLite via stdlib em vez de Postgres/MySQL

Status: aceito
Data: 2026-09-12 (retroativo)

## Contexto

O sistema precisa de um banco relacional (substituindo o CSV único do
sistema legado, que colidia entre scripts e fragmentava taxonomia por
string). 1 usuário, sem escrita concorrente de verdade — cada sessão de
estudo é sequencial (o próprio Gabriel, um navegador por vez).

## Decisão

SQLite via `sqlite3` da standard library, sem ORM, um arquivo (`enem.db`)
versionado no git junto com o resto do repositório.

## Alternativas consideradas

- **Postgres/MySQL** — exigiria um serviço de banco separado rodando (ou
  hospedado), credenciais, string de conexão — complexidade que só se paga
  quando existe escrita concorrente de verdade, que não é o caso aqui.
- **ORM (SQLAlchemy) sobre SQLite** — `db.py` declara explicitamente "zero
  dependência externa, só stdlib" — um ORM quebraria essa garantia sem
  resolver nenhum problema real hoje (as queries já são simples o bastante
  pra SQL puro ser mais legível que a abstração de um ORM).

## Consequências

Ganha: zero servidor de banco pra manter, arquivo único fácil de dar backup
(`backup_db.py`) e versionar no git (necessário porque é assim que o banco
chega no deploy do Streamlit Community Cloud, ver `DEPLOY.md`). Custa: SQLite
permite um único escritor por vez no banco inteiro (nem WAL está configurado
hoje — só `PRAGMA foreign_keys=ON`); pra 1 usuário isso nunca aparece.

## Quando revisitar

Quando existir mais de 1 usuário escrevendo ao mesmo tempo (ver Central ENEM
GI, Estágio 2 de escala) — não antes.
