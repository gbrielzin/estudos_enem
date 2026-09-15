# ADRs — ENEM GI

Architecture Decision Records: um arquivo por decisão de arquitetura/produto
que valha a pena lembrar *por quê* foi tomada, não só *o quê* foi feito. O
código já mostra o "o quê"; um ADR existe pra guardar o raciocínio e as
alternativas descartadas, que o `git log` sozinho não guarda.

## Quando abrir um ADR novo

Abra um ADR quando a decisão:
- for difícil de reverter depois (schema, escolha de banco, biblioteca central);
- tiver pelo menos uma alternativa real que foi descartada, não óbvia;
- for algo que "por que fizemos assim?" vai ser perguntado de novo (em
  entrevista, ou por você mesmo daqui a 6 meses).

Não abra ADR pra decisão pequena/reversível (nome de variável, ordem de
função) — isso é ruído, não registro.

## Numeração e status

`000N-titulo-curto.md`, sequencial, nunca reordenar nem reciclar número —
mesmo um ADR "superado" fica no histórico (aponte pra ele pelo Status).

Status possíveis:
- **proposto** — decisão ainda não implementada, registrando o raciocínio antes de agir
- **aceito** — decisão tomada e em vigor
- **superado por ADR-000N** — decisão trocada depois; nunca apague o arquivo antigo

## Lista

| ADR | Título | Status |
|---|---|---|
| [0001](0001-monolito-streamlit.md) | Monolito Streamlit em vez de API separada | superado por ADR-0007 |
| [0002](0002-sqlite-em-vez-de-postgres.md) | SQLite via stdlib em vez de Postgres | aceito |
| [0003](0003-heuristica-em-vez-de-ml.md) | Heurística (Leitner + prioridade ponderada) em vez de ML | aceito |
| [0004](0004-log-imutavel-e-estado-projetado.md) | Log imutável + estado projetado, em vez de 1 tabela só | aceito |
| [0005](0005-topico-como-padrao-de-cobranca.md) | Reusar a coluna `topico` como padrão de cobrança da banca | aceito |
| [0006](0006-ia-hospedada-para-proxima-integracao.md) | IA hospedada (não local) para a próxima integração | proposto |
| [0007](0007-api-rest-mais-cliente-expo.md) | API REST (FastAPI) + cliente Expo/React Native, em vez do monolito | aceito |
| [0008](0008-descontinuar-vinculo-youtube.md) | Descontinuar a automação de vínculo de vídeo do YouTube | proposto |

Template pra um ADR novo: [`0000-template.md`](0000-template.md).
