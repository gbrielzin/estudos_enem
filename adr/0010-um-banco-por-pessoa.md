# ADR-0010: Um banco SQLite por pessoa, escolhido pelo código de acesso

Status: aceito
Data: 2026-10-01

## Contexto

Um amigo vai testar o app pelo celular até o ENEM (08 e 15/11/2026). O
sistema é de uma pessoa só: `tentativas_usuario` e `estado_revisao` não têm
dono (ver adr/0009), então duas pessoas no mesmo `enem.db` misturariam
acertos, revisão espaçada e nota TRI. Falta pouco mais de um mês para a
prova, e o tempo do Gabriel tem que ir para o estudo.

## Decisão

Cada pessoa tem o próprio arquivo, `<API_PASTA_BANCOS>/<nome>.db`, criado
por `criar_banco_usuario.py`: uma cópia do `enem.db` com todo dado pessoal
apagado. `API_USUARIOS="nome:codigo,..."` liga cada código de acesso
(Bearer) a um nome. A trava em `api.py` escolhe o banco da requisição, e
`db.py` usa esse banco via `ContextVar` (`db.usar_banco`, `caminho_banco()`).
Sem `API_USUARIOS`, tudo funciona como antes (adr/0009).

## Alternativas consideradas

- **Coluna `id_usuario` em todas as tabelas pessoais** — é o modelo certo
  para muitos usuários, mas obriga a mexer em quase toda consulta de
  `db.py` (Leitner, prioridade, trilha, estatísticas) e nos testes. Não
  cabe antes da prova.
- **Uma instância do app por pessoa** — isola igual, mas multiplica custo
  e deploy a cada amigo.
- **Login de verdade (conta, senha, sessão)** — sem tabela de usuário para
  pendurar, ainda não tem para que servir. O código de acesso funciona como
  um link secreto.

## Consequências

- O isolamento vem de graça: nenhuma consulta muda, e um bug de filtro
  não vaza dado de uma pessoa para outra.
- A questão nova ou corrigida precisa ir para cada banco (rodar o script
  de importação com `db.usar_banco`, ou recriar o banco de quem ainda não
  usou).
- O código é a credencial. Quem tiver o link entra. Serve para 2–5 pessoas
  conhecidas, não para o público.
- O dependency de autenticação é `async` de propósito. Um dependency
  síncrono roda numa thread com cópia do contexto, e o banco escolhido não
  chegaria ao endpoint (há teste cobrindo isso).

## Quando revisitar

Antes de passar de ~5 pessoas, ou antes de abrir para quem não seja
conhecido (ex.: tráfego pago em fevereiro/2027). Nesse ponto, migrar para
`id_usuario` mais login de verdade, com um banco só.
