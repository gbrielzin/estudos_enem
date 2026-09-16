# Expo HAS CHANGED

Read the exact versioned docs at https://docs.expo.dev/versions/v57.0.0/ before writing any code.

## Git: nunca executar, sempre sugerir

Claude nunca roda `git` (add, commit, push, branch, ou qualquer outro) neste
projeto, em nenhuma pasta — regra vale pro repositório inteiro (ver
`core/CLAUDE.md`), não só `mobile/`. Editar/criar/apagar arquivo continua
normal. Staging, commit e push ficam 100% com o Gabriel.

Toda vez que uma alteração feita na conversa (código, doc, dado) chegar a um
ponto que valeria um commit, sugerir o commit em texto, num bloco de código
pronto pra copiar/colar:

```
git commit -m "tipo: mensagem curta no imperativo"
```

- `tipo` segue Conventional Commits (`feat`, `fix`, `docs`, `refactor`,
  `chore`, `test`, etc.) condizente com o que mudou.
- Mensagem em português, curta, descrevendo o "quê" da mudança.
- Se fizer sentido separar em mais de um commit (mudanças sem relação entre
  si), sugerir os blocos separados, cada um com seu próprio `git add
  <arquivos>` + `git commit -m "..."`.
