## 🔀 O fluxo completo, em um só lugar

Consulte esta tabela toda vez que começar ou terminar uma tarefa.
Ela resume os 10 passos, do primeiro comando no terminal até voltar
pra `dev` atualizada.

| # | Onde | Ação |
|---|------|------|
| 1 | Terminal | `git checkout dev` |
| 2 | Terminal | `git pull origin dev` |
| 3 | Terminal | `git checkout -b nome-da-tarefa` |
| 4 | Terminal | Codifica (faz as alterações no código) |
| 5 | Terminal | `git add nome-do-arquivo` |
| 6 | Terminal | `git commit -m "mensagem clara"` |
| 7 | Terminal | `git push -u origin nome-da-tarefa` |
| 8 | Site (GitHub) | Create Pull Request |
| 9 | Site (GitHub) | Merge Pull Request → Confirm Merge |
| 10 | Terminal | `git checkout dev` → `git pull origin dev` |

```
checkout dev ➡️ pull ➡️ checkout -b tarefa ➡️ Codifica ➡️ add ➡️ commit ➡️ push
        ⬇️ (no site)
Create Pull Request ➡️ Merge Pull Request ➡️ Confirm Merge
        ⬇️ (de volta ao terminal)
checkout dev ➡️ pull
```

Depois do passo 10, você está pronta/pronto pra começar a próxima
tarefa — volte ao passo 1 (`checkout -b` de uma nova branch).

---## 🔀 O fluxo completo, em um só lugar

Consulte esta tabela toda vez que começar ou terminar uma tarefa.
Ela resume os 10 passos, do primeiro comando no terminal até voltar
pra `dev` atualizada.

| # | Onde | Ação |
|---|------|------|
| 1 | Terminal | `git checkout master` |
| 2 | Terminal | `git pull origin dev` |
| 3 | Terminal | `git checkout -b nome-da-tarefa` |
| 4 | Terminal | Codifica (faz as alterações no código) |
| 5 | Terminal | `git add nome-do-arquivo` |
| 6 | Terminal | `git commit -m "mensagem clara"` |
| 7 | Terminal | `git push -u origin nome-da-tarefa` |
| 8 | Site (GitHub) | Create Pull Request |
| 9 | Site (GitHub) | Merge Pull Request → Confirm Merge |
| 10 | Terminal | `git checkout dev` → `git pull origin dev` |

```
checkout dev ➡️ pull ➡️ checkout -b tarefa ➡️ Codifica ➡️ add ➡️ commit ➡️ push
        ⬇️ (no site)
Create Pull Request ➡️ Merge Pull Request ➡️ Confirm Merge
        ⬇️ (de volta ao terminal)
checkout dev ➡️ pull
```

Depois do passo 10, você está pronta/pronto pra começar a próxima
tarefa — volte ao passo 1 (`checkout -b` de uma nova branch).

---