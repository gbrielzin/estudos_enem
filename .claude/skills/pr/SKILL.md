---
name: pr
description: Leva uma mudança do ENEM GI até o master pelo fluxo combinado com o Gabriel (branch, lint, testes, /code-review, PR com descrição no padrão, resposta aos comentários, merge só com CI verde e "pode mergear"). Use quando ele pedir /pr, "abre o PR", "sobe isso", "manda pro GitHub" ou quando um trabalho de código/doc estiver pronto pra virar PR.
---

# /pr — do trabalho pronto ao merge

Fluxo acordado em 2026-09-26 (PR #22). Cada etapa existe por um motivo; se alguma falhar, **pare e conte**, não pule.

| Etapa | Por que existe |
|---|---|
| Branch própria | master só recebe o que foi revisado |
| Lint + testes locais | pegar regressão antes de gastar a revisão dele |
| `/code-review` antes do PR | a IA pega bug de lógica que teste não cobre; no #22 achou 21 testes que quebrariam |
| Descrição no padrão | ele revisa pelo celular: precisa saber o que olhar |
| Responder todo comentário | pergunta dele é aprendizado e às vezes acha limite real (força bruta no #22) |
| CI verde + "pode mergear" | nada entra no master sem máquina limpa e sem o ok dele |

## 1. Preparar

1. `git status` e `git branch --show-current`. Se estiver em `master`, crie `feat-<assunto>` / `fix-<assunto>` / `docs-<assunto>` a partir de `origin/master`.
2. **1 PR = 1 assunto.** Se o working tree mistura assuntos (ex.: código + pesquisa), separe em branches/PRs diferentes e diga quais.
3. **Nunca adicionar**: `.env`, `mobile/.env`, `core/enem.db`, `core/corpus_analise.db`, `docs/registro_estudo.csv`, `docs/sessao_estudo_chat.md`, `docs/plano_*`, `docs/linkedin_projeto.md`, `docs/redacao_pesquisa/banco_1000/`, `docs/redacao_pesquisa/cartilhas/`. Confira com `git status --short` e `git check-ignore` antes do `git add` (adicione por caminho, nunca `git add -A`).

## 2. Checagens locais (as mesmas do CI em `.github/workflows/`)

- Mexeu em `core/`: `cd core && python -m ruff check . --select F,E9` e `python -m unittest discover -p "test_*.py"`.
- Mexeu em `mobile/`: `cd mobile && npx tsc --noEmit && npm test`.
- Código novo sem teste: escreva o teste (dado sintético, nunca dado de terceiro) ou diga no PR por que não tem.
- Falhou → conserte ou pare e explique. Não abra PR vermelho.

## 3. Revisão automática

Rode a skill `code-review` sobre a branch. Achado real → corrija, rode as checagens de novo, e registre no PR ("achado do /code-review, corrigido em <hash>"). Achado que você discorda → explique no PR.

## 4. Commit e PR

- Commit em Conventional Commits, português, curto (`feat(redacao): ...`), com as linhas de atribuição da sessão.
- `git push -u origin <branch>`.
- `gh pr create --base master` com este corpo:

```
## O que muda
- (bullets do que o revisor vai ver no diff)

## Por quê
(o problema, com o caso real que motivou)

## Como foi testado
- (comandos rodados e resultado; teste novo e o que ele cobre)

## Pontos pra revisar
1. (onde vale ele olhar: decisão discutível, limite conhecido, regra de negócio)

## Gancho de conteúdo
(uma frase que vira vídeo/post, pra skill /conteudo)
```

Depois, mande o link e diga **o que olhar primeiro** e as 6 perguntas do revisor iniciante (e se vier vazio? tem teste? o que muda pra quem já usava? o comentário bate com o código? tem segredo no diff? dá pra quebrar?).

## 5. Revisão dele

- Ele comenta pelo celular e avisa "comentei". A revisão pode estar **pendente** (rascunho): se `gh api repos/{owner}/{repo}/pulls/<n>/reviews` mostrar `PENDING`, peça pra ele enviar ("Review changes" → "Comment" → "Submit").
- Leia: `gh api repos/{owner}/{repo}/pulls/<n>/comments`.
- Responda **cada** comentário na própria thread (`gh api -X POST .../pulls/<n>/comments/<id>/replies -f body=...`), em português simples, explicando o conceito quando for pergunta. Se for bug: commit novo no mesmo PR + resposta com o hash.
- Resuma no chat o que ele aprendeu com as perguntas.

## 6. Merge

Só quando **as duas** condições valem:
1. `gh pr checks <n>` todo verde;
2. ele disse, no chat, "pode mergear" (ou equivalente claro) **para este PR**.

Então: `gh pr merge <n> --merge --delete-branch`, `git switch master && git pull`, e confira se sobrou commit que chegou depois do merge (se sim, vira PR novo). Sugira rodar `/conteudo <n>`.
