# Changelog

O que mudou no projeto, PR por PR, da mais recente pra mais antiga. Cada
item leva ao PR com a descrição completa (o quê, por quê e como foi testado).

## Semana de 28/09 a 04/10/2026

- **feat(redacao):** busca de vídeos de redação no YouTube-Commons (163 GB lidos
  direto da internet com DuckDB). A validação mostrou que 471 linhas eram 76 vídeos
  em tradução automática, sem transcrição em português; filtro corrigido e retomada
  segura. ([#26](https://github.com/gbrielzin/estudos_enem/pull/26))

## Semana de 21 a 27/09/2026

- **chore(claude):** skills `/pr` (fluxo de PR até o merge) e `/conteudo` (PR vira
  roteiro de vídeo e post). ([#24](https://github.com/gbrielzin/estudos_enem/pull/24))
- **feat(redacao):** pipeline do banco de redações nota 1000 (vários formatos de fonte,
  duplicatas entre fontes, estatísticas) e análise de padrões de 245 redações; testes
  só com texto inventado. ([#23](https://github.com/gbrielzin/estudos_enem/pull/23))
- **fix(api):** API fechada por padrão sem token, comparação em tempo constante
  (`hmac.compare_digest`) e CORS restrito. ([#22](https://github.com/gbrielzin/estudos_enem/pull/22))
- **chore(claude):** skill `/estudo`, hook que roda os testes do core a cada edição
  e fila de pesquisa. ([#21](https://github.com/gbrielzin/estudos_enem/pull/21))
- **docs:** simulador "onde eu entro" na faculdade e plano do Radar de Estágios.
  ([#20](https://github.com/gbrielzin/estudos_enem/pull/20))
- **docs:** backlog acumulativo de ideias de produto e UI.
  ([#19](https://github.com/gbrielzin/estudos_enem/pull/19))
- **feat(moldes):** molde do pedágio; Claude passa a poder commitar no branch de
  trabalho. ([#18](https://github.com/gbrielzin/estudos_enem/pull/18))
- **docs:** ciclo kit → molde → questão original como regra candidata do produto.
  ([#17](https://github.com/gbrielzin/estudos_enem/pull/17))
- **feat(mobile):** tela de treino com moldes.
  ([#16](https://github.com/gbrielzin/estudos_enem/pull/16))
- **feat:** moldes de questão: variações de questões oficiais com a resposta calculada
  e distratores de erro típico, expostos na API.
  ([#15](https://github.com/gbrielzin/estudos_enem/pull/15))
- **feat:** 2024 azul recuperado de outro caderno pelo mapeamento oficial do INEP,
  195 figuras importadas e **CI** com testes, lint e `tsc`.
  ([#14](https://github.com/gbrielzin/estudos_enem/pull/14))
- **feat:** importação de Natureza 2010–2018 (azul) com gabarito oficial do INEP.
  ([#13](https://github.com/gbrielzin/estudos_enem/pull/13))
- **feat:** tabela de acertos esperados por nota e área (aproximação TRI 3PL).
  ([#12](https://github.com/gbrielzin/estudos_enem/pull/12))
- **docs:** status do download dos PDFs do PPL.
  ([#11](https://github.com/gbrielzin/estudos_enem/pull/11))
- **docs:** plano para ampliar o banco com provas antigas e PPL.
  ([#10](https://github.com/gbrielzin/estudos_enem/pull/10))
- **docs:** método e aprendizados de uma sessão real de estudo.
  ([#9](https://github.com/gbrielzin/estudos_enem/pull/9))

## Semana de 14 a 20/09/2026

- **feat:** corpus de análise das provas, valor por questão e parâmetros TRI do INEP.
  ([#8](https://github.com/gbrielzin/estudos_enem/pull/8))
- **feat:** extração de enunciados do PDF, análise de eletrodinâmica em 7 anos e
  validação das matérias existentes. ([#7](https://github.com/gbrielzin/estudos_enem/pull/7))
- **docs:** arquitetura da trilha e questões de banco de prática por fase.
  ([#6](https://github.com/gbrielzin/estudos_enem/pull/6))
- **feat:** `filosofia.md` (pesos da trilha) e banco de prática de Natureza na API.
  ([#5](https://github.com/gbrielzin/estudos_enem/pull/5))
- **refactor:** pastas renomeadas e documentação reorganizada em `docs/`.
  ([#4](https://github.com/gbrielzin/estudos_enem/pull/4))
- **docs:** primeiros ADRs (monolito Streamlit, SQLite, heurística em vez de ML,
  log imutável, IA hospedada). ([#3](https://github.com/gbrielzin/estudos_enem/pull/3))

## Semana de 07 a 13/09/2026

- **feat(mobile):** animações e telas do app gamificado (missões, liga, simulado).
  ([#2](https://github.com/gbrielzin/estudos_enem/pull/2))
- **feat:** nova interface (tema claro, design do app gamificado).
  ([#1](https://github.com/gbrielzin/estudos_enem/pull/1))
