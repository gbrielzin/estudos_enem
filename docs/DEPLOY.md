# Rodar de qualquer lugar, de graça

Duas opções. A primeira já funciona agora, sem fazer nada. A segunda
(deploy de verdade) tem uns passos que só você pode fazer — login em
conta é uma coisa que eu não faço por você.

## Agora mesmo, sem deploy nenhum: mesma wifi

Se seu celular estiver na mesma rede wifi do computador que está
rodando o app:

1. No computador: `cd core` e `python -m streamlit run cartao_resposta.py`
2. O terminal imprime umas linhas tipo:
   ```
   Local URL: http://localhost:8517
   Network URL: http://192.168.1.XXX:8517
   ```
3. Abre a **Network URL** no navegador do celular. Pronto.

Limitação óbvia: só funciona com o computador ligado, rodando o
comando, na mesma rede. Pra usar de qualquer lugar (dados móveis, sem
o notebook ligado), é a opção 2.

## De qualquer lugar, de graça: Streamlit Community Cloud

Free. O que eu já deixei pronto:

- `requirements.txt` na raiz, completo.

> **Nota (2026-09-15):** este documento foi escrito quando `core/enem.db`
> ainda ia junto no `git push` (por isso a recomendação de repositório
> privado abaixo). Isso mudou — `enem.db` não é mais versionado (contém
> dado pessoal de uso real; ver `.gitignore` e `adr/0008`). Rodando este
> passo a passo hoje, o deploy sobe sem banco nenhum — rode
> `python reconstruir_base.py` (de dentro de `core/`, ou via um passo de
> build equivalente no Streamlit Cloud) pra gerar `enem.db` a partir dos
> gabaritos oficiais versionados em `core/gabaritos_reais/`, antes de o
> app funcionar de verdade lá.

O que só você pode fazer (login/conta):

### 1. Criar o repositório no GitHub

- github.com → New repository → **Private** → não inicialize com
  README (você já tem um projeto pronto).
- Depois de criado, o GitHub mostra os comandos — algo como:
  ```
  git remote add origin https://github.com/SEU_USUARIO/enem_gi.git
  git push -u origin master
  ```
  Rode esses dois no terminal, dentro da pasta do projeto (seu branch
  local se chama `master`, não `main` — ajuste se o GitHub sugerir
  `main`).

### 2. Criar a conta no Streamlit Community Cloud

- share.streamlit.io → entrar com a conta do GitHub (mesma conta do
  passo 1).
- **Na tela de autorização do GitHub, antes de confirmar**: procure a
  opção de escolher quais repositórios liberar (geralmente "All
  repositories" ou "Only select repositories"). Se ficar em "Only
  select repositories" e não adicionar o `enem_gi` na lista, o
  Streamlit Cloud nunca vai enxergar ele depois — esse é quase certeza
  o que aconteceu. Escolha "All repositories" (mais simples) ou adicione
  `enem_gi` explicitamente na lista.
- "New app" → escolhe o repositório `enem_gi` → branch `master` →
  **main file path**: `core/cartao_resposta.py`.
- Deploy.

**Se o repositório não aparecer na lista pra escolher** (mesmo depois
de logar de novo): o acesso ficou só nos públicos. Corrija direto no
GitHub, sem precisar desconectar de novo:
- github.com → seu avatar (canto superior direito) → **Settings**
- **Applications** (ou **Integrations** → **Applications**, o nome muda
  um pouco de vez em quando) → aba **Authorized OAuth Apps** *ou*
  **Installed GitHub Apps** (o Streamlit pode aparecer em qualquer um
  dos dois, dependendo de quando sua conta foi criada)
- Ache "Streamlit" na lista → clique nele/em "Configure" → em
  "Repository access", mude pra **All repositories** ou adicione
  `enem_gi` na lista de repositórios selecionados → Save.
- Volta pro share.streamlit.io e tenta "New app" de novo.

### Bom saber

- O plano gratuito **hiberna o app depois de um tempo sem visita** — a
  primeira abertura do dia pode demorar uns segundos pra "acordar".
  Normal, não é bug.
- Todo `git push` novo pro GitHub atualiza o app na nuvem sozinho.
- `core/enem.db` não vai mais junto no push (ver nota no topo deste
  documento) — o deploy precisa rodar `reconstruir_base.py` (ou
  equivalente) pra ter banco.

Se quiser, eu te acompanho passo a passo enquanto você faz o login —
só não consigo fazer o login por você.
