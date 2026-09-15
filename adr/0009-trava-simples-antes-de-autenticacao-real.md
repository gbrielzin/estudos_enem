# ADR-0009: Trava simples por chave compartilhada, antes de autenticação de usuário de verdade

Status: aceito
Data: 2026-09-16

## Contexto

`core/api.py` não tinha nenhuma proteção (ver `adr/0007`, seção
Consequências: "não tem autenticação nem controle de acesso"). Isso era
aceitável enquanto o único cliente era o próprio celular do usuário na
mesma wifi doméstica — mas o produto está migrando pra multiusuário com
monetização própria (mesmo motivo de negócio do `adr/0008`), o que torna
"qualquer um na rede acessa e grava dado" um problema real, não hipotético.

Autenticação de usuário de verdade (login, sessão, JWT por conta) não tem
onde pendurar dado ainda: não existe nenhuma tabela de usuário no schema,
nenhuma coluna `user_id` em lugar nenhum de `core/schema.sql`, e todo o
banco (`enem.db`) é um arquivo único, sem nenhuma noção de "de quem é essa
tentativa". Construir login antes de ter esse modelo de dado seria
autenticar usuário pra um sistema que ainda trata todo mundo como a mesma
pessoa por baixo.

## Decisão

Uma trava simples por chave compartilhada (*shared secret*), não um
sistema de conta:

- Backend (`core/api.py`, `_verificar_autenticacao`): dependency do
  FastAPI aplicada a TODOS os endpoints (inclusive `/health` — sem razão
  pra abrir exceção num app de uso pessoal), checando o header
  `Authorization: Bearer <valor>` contra a variável de ambiente
  `API_AUTH_TOKEN`, lida via `python-dotenv` (`load_dotenv()`, reintroduzido
  nas dependências só pra isso).
- **Opcional por padrão**: sem a variável configurada, a API roda ABERTA
  — mesmo comportamento de hoje. Configurar a variável é o que liga a
  trava; ninguém que já usa o projeto localmente é afetado até decidir
  ativar.
- Cliente (`mobile/src/lib/api.ts`, `cabecalhosAutenticacao()`): lê
  `EXPO_PUBLIC_API_AUTH_TOKEN` e manda o mesmo header quando configurado.

## Alternativas consideradas

- **JWT/sessão de usuário completo agora** — descartada: exigiria criar
  tabela de usuário, fluxo de login/cadastro, e adaptar toda query de
  `db.py` pra filtrar por usuário — trabalho real de modelo de dado, não
  de "preparar o terreno". Fora de escopo até o projeto decidir virar
  multiusuário de fato, não só de intenção.
- **Basic Auth** — equivalente em nível de segurança ao Bearer token
  compartilhado; Bearer é a convenção mais comum pra API JSON consumida
  por um cliente que não é navegador, sem ganho real na alternativa.
- **Deixar como está até ter usuário de verdade** — descartada: é
  exatamente o gap que motivou este ADR: hoje qualquer um na mesma rede
  já pode gravar tentativa (`POST /tentativas`) sem nenhuma barreira.

## Consequências

Ganha: para de ser "totalmente aberto pra rede" sem esperar o modelo de
usuário inteiro ficar pronto; mecanismo ponta a ponta (backend + app)
já existe pronto pra ligar quando fizer sentido (ex: assim que o app sair
da wifi doméstica).

Custa, e isso precisa ficar claro em qualquer lugar que descreva isso —
**não é autenticação de verdade**:
- Não distingue QUEM está chamando — só se tem ou não tem o segredo certo.
  Um usuário mal-intencionado com o token vaza o mesmo acesso que
  qualquer outro.
- `EXPO_PUBLIC_API_AUTH_TOKEN` fica visível em texto puro no app
  compilado (comportamento documentado do próprio Expo pra qualquer
  variável com esse prefixo) — não serve pra distribuir o app publicamente
  com um token "secreto" embutido, só pra um punhado de dispositivos de
  confiança do próprio usuário.
- CORS continua aberto (`allow_origins=["*"]`, ver `adr/0007`) — este ADR
  não resolve isso, de propósito (ver "não tentar consertar CORS/auth só
  pra impressionar", princípio já adotado nesta sessão de preparação pro
  GitHub).

## Quando revisitar

Quando existir uma tabela de usuário de verdade e um motivo real de
diferenciar quem está pedindo o quê (não só "tem o segredo ou não") —
nesse momento, substituir a trava por login/sessão de verdade, mantendo
os mesmos endpoints (só troca o que valida a requisição, não a forma da
API).
