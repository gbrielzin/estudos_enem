# ADR-0001: Monolito Streamlit em vez de API + front separado

Status: superado por ADR-0007 (2026-09-15) — ver nota abaixo
Data: 2026-09-12 (retroativo — decisão já em vigor desde a criação de `core/`)

> **Nota (2026-09-15):** o "Custa" desta decisão, descrito abaixo, já se
> concretizou — o app mobile (`mobile/`) precisou ler os mesmos dados do
> Streamlit, e isso disparou exatamente o gatilho de "quando revisitar"
> que este documento já previa. `core/db.py` ganhou uma API REST por cima
> (`core/api.py`) sem precisar ser reescrito. Ver ADR-0007 para a decisão
> nova; este documento continua valendo como registro de por que o
> monolito foi a escolha certa NAQUELE momento (1 usuário, sem cliente
> além do próprio navegador) — não foi um erro, foi uma decisão que
> cumpriu seu prazo de validade.

## Contexto

O sistema precisa de UI (grade de resposta, correção, dashboards) e de um
lugar pra rodar a lógica de negócio (Leitner, prioridade de estudo), servindo
1 usuário (Gabriel), sem verba/motivo pra manter infraestrutura própria. O
objetivo explícito (`DEPLOY.md`) é rodar "de qualquer lugar, do celular, sem
notebook ligado" — de graça.

## Decisão

Um processo Python só: `streamlit run cartao_resposta.py`. `cartao_resposta.py`
importa `db.py` direto (chamada de função Python, sem HTTP, sem
serialização). Streamlit é ao mesmo tempo front-end e servidor HTTP.

## Alternativas consideradas

- **API REST (FastAPI) + front separado (React/Next)** — resolveria um
  problema de escala (múltiplos clientes, múltiplos usuários) que o projeto
  não tem hoje. Custaria deploy de 2 serviços, autenticação entre eles, e
  contrato de API versionado pra manter — tudo isso é complexidade sem
  benefício quando o "cliente" é só o próprio navegador do Gabriel.
- **App desktop nativo** — perderia o objetivo de acesso remoto do celular
  sem notebook ligado, que é justamente o motivo do deploy em nuvem já
  escolhido.

## Consequências

Ganha: deploy trivial (`git push` atualiza sozinho via Streamlit Community
Cloud), zero custo de serialização entre "front" e "back", debug de 1 stack
trace só. Custa: nenhum outro processo (um app mobile nativo, por exemplo)
consegue ler os mesmos dados sem reimplementar uma API por cima de `db.py` —
essa é a limitação que o app mobile em construção (`mobile/`) já está
esbarrando.

## Quando revisitar

Quando o app mobile precisar ler/escrever no mesmo `enem.db` que o Streamlit
usa hoje — nesse momento `db.py` precisa ficar atrás de uma API real (ver
seção "Escalabilidade" da Central ENEM GI, Estágio 2). Não antes disso.
