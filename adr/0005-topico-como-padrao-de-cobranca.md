# ADR-0005: Reusar a coluna `topico` como "padrão de cobrança da banca"

Status: aceito
Data: 2026-09-12

## Contexto

A hipótese central de produto (ver Central ENEM GI, seção "Hipótese central
de produto") é que repetição concentrada num padrão específico de como a
banca cobra um conteúdo — não a matéria inteira — é o que ensina o aluno a
reconhecer o distrator típico. Testar isso exige um nível de granularidade
abaixo de `materia`, hoje inexistente em qualquer lugar consultável.

Uma revisão externa do projeto sugeriu construir um modelo de domínio
hierárquico completo (`Questão → Conteúdo → Habilidade → Padrão de cobrança
→ Domínio`). Investigando o schema atual (`schema.sql`), a coluna
`questoes.topico` (TEXT, nullable) já existe desde antes — já é aceita por
`inserir_questao()` e `inserir_questao_pratica()` — mas nunca foi lida por
nenhuma função analítica nem exposta em nenhuma tela.

## Decisão

Reusar `questoes.topico` como o campo de "padrão de cobrança", em vez de
criar uma tabela nova ou uma hierarquia completa. Adicionado:
`atualizar_topico(id_questao, topico)` (marcar/limpar sem passar por
`inserir_questao`/`historico_alteracoes`, mesmo padrão de `atualizar_enunciado()`)
e `desempenho_por_topico(grande_area, materia)` (taxa de acerto agrupada por
`topico` dentro de uma matéria, mesmo estilo de `taxa_acerto_por_materia()`).

## Alternativas consideradas

- **Modelo de domínio completo** (`Skill`/`Pattern`/`Mastery` como tabelas
  novas, com `mastery_score`, `error_streak` etc.) — construiria estrutura
  pra uma hipótese que ainda não foi validada nem uma vez. Se a hipótese cair
  no piloto (ver plano da semana), esse investimento inteiro teria sido
  descartado.
- **Nova tabela `padroes_cobranca` com FK pra `questoes`** — mais "correto"
  no papel, mas `topico` já resolve o mesmo problema hoje sem migração de
  schema nenhuma, e o projeto já tem um precedente de campo texto-livre não
  validado por taxonomia fechada (`fonte`, em `banco_pratica`).

## Consequências

Ganha: zero migração de schema, reaproveita infraestrutura de teste já
existente, pode começar a marcar questões hoje mesmo. Custa: `topico` é
texto livre, sem normalização — duas grafias diferentes do "mesmo" padrão
aparecem como entradas distintas no ranking (documentado explicitamente no
docstring de `desempenho_por_topico()`); isso é aceitável enquanto o
vocabulário de padrões ainda está sendo descoberto à mão, não seria
aceitável em escala.

## Quando revisitar

Se o piloto confirmar a hipótese E o número de padrões distintos crescer o
bastante pra normalização manual (comparar strings por matéria) virar
gargalo real — nesse momento, migrar pra uma tabela com identidade própria
(FK, não texto livre) faz sentido. Não antes de ter pelo menos 1 matéria
com a hipótese validada.
