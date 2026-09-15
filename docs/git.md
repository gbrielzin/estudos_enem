## 🔀 O fluxo completo:

# Git — Fluxo de Trabalho

## 1. O que é Git?

Git é um sistema de controle de versão distribuído.

Ele permite registrar a evolução de um projeto ao longo do tempo,
acompanhar alterações, voltar para estados anteriores e trabalhar
de forma organizada com outras pessoas.

O Git funciona localmente na minha máquina.
O GitHub é usado como repositório remoto para armazenar e compartilhar
esse histórico.

---

# 2. Modelo mental

Meu fluxo principal é:

Working Directory
        ↓
     git add
        ↓
 Staging Area
        ↓
   git commit
        ↓
 Local Repository
        ↓
    git push
        ↓
 Remote Repository (GitHub)

Para trazer alterações do remoto:

GitHub
   ↓
git pull
   ↓
Meu repositório local

---

# 3. Working Directory

É o estado atual dos arquivos do projeto na minha máquina.

Quando crio, edito, removo ou reorganizo arquivos, estou modificando
o Working Directory.

Exemplo:

Eu reorganizei:

DEPLOY.md
↓
docs/DEPLOY.md

Essa alteração primeiro existe no meu computador.

---

# 4. git status

Comando:

git status

Serve para verificar o estado atual do repositório.

Ele mostra principalmente:

- branch atual;
- arquivos modificados;
- arquivos deletados;
- arquivos novos não rastreados;
- alterações preparadas para commit;
- situação em relação ao repositório remoto.

Pergunta que o comando responde:

"Como está meu projeto neste momento?"

---

# 5. Staging Area

A Staging Area é uma área intermediária entre as alterações
do meu projeto e o próximo commit.

Quando uso:

git add arquivo.py

estou dizendo:

"Quero incluir esta alteração no próximo commit."

Também posso usar:

git add .

para adicionar todas as alterações elegíveis.

IMPORTANTE:

git add NÃO cria um commit.

Ele apenas prepara as alterações.

---

# 6. git diff

Comando:

git diff

Mostra as diferenças entre o estado atual dos arquivos e a última
versão registrada, considerando alterações que ainda não foram
colocadas no staging.

É útil para revisar o que eu alterei antes de criar um commit.

Pergunta que responde:

"O que eu mudei e ainda não preparei?"

---

# 7. git diff --staged

Comando:

git diff --staged

Mostra as alterações que já estão na Staging Area.

Pergunta que responde:

"O que exatamente vai entrar no meu próximo commit?"

Isso é importante para revisar o commit antes de criá-lo.

---

# 8. Commit

Comando:

git commit -m "mensagem"

Um commit registra uma versão do projeto no histórico local do Git.

Um commit deve representar uma unidade lógica de trabalho.

Exemplos:

feat: adiciona sistema de ranking
fix: corrige cálculo da pontuação
refactor: reorganiza serviço de questões
chore: reorganiza estrutura do projeto
docs: adiciona documentação do Git

Um commit NÃO é a mesma coisa que um push.

Commit = registra localmente.
Push = envia os commits para o repositório remoto.

---

# 9. git push

Comando:

git push

Envia os commits do meu repositório local para o repositório remoto.

Fluxo:

Meu computador
     ↓
   commit
     ↓
Histórico local
     ↓
    push
     ↓
GitHub

---

# 10. git pull

Comando:

git pull

Busca alterações do repositório remoto e atualiza meu repositório
local.

É importante quando outras pessoas também estão trabalhando no projeto
ou quando o repositório remoto foi alterado.

---

# 11. git log

Comando:

git log --oneline

Mostra o histórico de commits de forma resumida.

Exemplo:

abc1234 feat: adiciona sistema de ranking
def5678 fix: corrige pontuação
ghi9012 chore: reorganiza estrutura

Isso permite entender como o projeto evoluiu.

---

# 12. Tipos de Conventional Commits

Esses prefixos são uma convenção para deixar o histórico mais
organizado e legível.

## feat

Nova funcionalidade.

feat: adiciona sistema de ranking

## fix

Correção de um problema ou bug.

fix: corrige cálculo da pontuação

## refactor

Reorganização ou melhoria interna do código sem alterar
sua finalidade.

refactor: separa serviço de questões

## chore

Tarefas de manutenção do projeto.

chore: reorganiza estrutura de pastas

## docs

Alterações relacionadas à documentação.

docs: adiciona documentação do Git

## test

Criação ou alteração de testes.

test: adiciona testes para pontuação

IMPORTANTE:

Esses tipos não são comandos do Git.
São uma convenção de escrita das mensagens de commit.

---

# 13. Meu fluxo de trabalho padrão

Sempre que começo uma tarefa:

1. Verifico o estado atual:

git status

2. Faço uma mudança com um objetivo definido.

3. Testo a mudança.

4. Verifico o que foi alterado:

git status
git diff

5. Preparo as alterações:

git add arquivo

ou:

git add .

quando todas as alterações pertencem à mesma tarefa.

6. Reviso o que será commitado:

git diff --staged

7. Crio o commit:

git commit -m "tipo: descrição"

8. Envio para o GitHub:

git push

9. Se necessário, verifico o histórico:

git log --oneline

---

# 14. Regra principal

Um commit deve representar uma unidade lógica de trabalho.

Não devo criar commits apenas para aumentar o número de contribuições
do GitHub.

O objetivo é construir um histórico útil e compreensível.

Qualidade do histórico > quantidade de commits.

---

# 15. Exemplo real no projeto

Problema:

A estrutura do projeto ficou desorganizada.

Decisão:

Separar documentação e arquivos antigos.

Alterações:

DEPLOY.md → docs/DEPLOY.md
REVISAO_PROJETO.md → docs/REVISAO_PROJETO.md
app.py → legacy/app.py

Depois:

git status

Reviso:

git diff

Preparo:

git add .

Confiro:

git diff --staged

Commit:

git commit -m "chore: reorganiza estrutura do projeto"

Envio:

git push

Resultado:

A alteração fica registrada no histórico local e também disponível
no GitHub.