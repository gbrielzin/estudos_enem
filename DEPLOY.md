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

Free, incluindo repositório **privado** (importante — seu `enem.db` tem
seus dados reais de desempenho, não é algo pra deixar público). O que
eu já deixei pronto:

- `requirements.txt` na raiz, completo.
- `main.py` (usado por `core/coletar_videos.py`) já lê a API key dos
  **Secrets** do Streamlit Cloud quando existem, e cai pro `.env` local
  quando não — mesmo código funciona nos dois lugares.
- `.env` está no `.gitignore` — sua API key não vai pro GitHub junto.

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
- "New app" → escolhe o repositório `enem_gi` → branch `master` →
  **main file path**: `core/cartao_resposta.py`.
- Deploy.

### 3. Configurar a API key

- No painel do app recém-criado → ⚙️ Settings → Secrets → cola:
  ```toml
  YOUTUBE_API_KEY = "sua_chave_aqui"
  ```
- Salva. O app reinicia sozinho.

### Bom saber

- O plano gratuito **hiberna o app depois de um tempo sem visita** — a
  primeira abertura do dia pode demorar uns segundos pra "acordar".
  Normal, não é bug.
- Todo `git push` novo pro GitHub atualiza o app na nuvem sozinho.
- `core/enem.db` vai junto no push (é como o banco chega no servidor
  da nuvem) — por isso o repositório **precisa** ser privado.

Se quiser, eu te acompanho passo a passo enquanto você faz o login —
só não consigo fazer o login por você.
