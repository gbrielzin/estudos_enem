# ENEM GI — app mobile/web

App Expo (React Native + Expo Router, TypeScript) do ENEM GI. Um único código roda no celular (Expo Go) e no navegador. O app não guarda regra de negócio: tudo o que diz o que estudar, quando revisar e se a resposta está certa vem da API FastAPI em `core/api.py`, que é uma camada fina sobre `core/db.py`. Contexto da decisão em [`adr/0007`](../adr/0007-api-rest-mais-cliente-expo.md).

## Telas (`src/app/`)

| Arquivo | O que faz |
|---|---|
| `index.tsx` | Trilha de estudo (fixa, por matéria), exercício e resultado de cada nó |
| `explore.tsx` | Navegar e buscar todas as matérias da taxonomia (`GET /explorar`) |
| `simulado.tsx` | Montar um simulado ("Escolher a prova") e emitir o bilhete (`components/tela-bilhete.tsx`) |
| `missoes.tsx` | Missões do dia |
| `liga.tsx` / `perfil.tsx` | Nível, XP, dias até a prova, resumo geral. A liga é decorativa: o sistema ainda é de um usuário só |
| `_layout.tsx` | Tema escuro fixo, fontes e navegação por abas (`components/tab-bar.tsx`) |

Toda chamada HTTP passa por `src/lib/api.ts`. As cores e a identidade visual vêm de `src/constants/brand.ts`, seguindo o handoff em `docs/design_handoff_enem_gamificado/`.

## Rodar

A API precisa estar no ar antes do app:

```bash
# na raiz do repo
cd core
uvicorn api:app --host 0.0.0.0 --port 8000
```

Depois, em outro terminal:

```bash
cd mobile
npm install
npx expo start --web     # navegador
npx expo start           # QR code pro Expo Go (celular na MESMA wifi do computador)
```

O app descobre sozinho o endereço da API (`getApiBaseUrl()` em `src/lib/api.ts`). No Expo Go ele usa o IP do computador que roda o Metro, na porta 8000. No navegador usa `localhost:8000`.

### Trava da API (opcional)

Se a API estiver com `API_AUTH_TOKEN` configurado (ver `.env.example` na raiz e [`adr/0009`](../adr/0009-trava-simples-antes-de-autenticacao-real.md)), crie `mobile/.env` com o mesmo valor:

```
EXPO_PUBLIC_API_AUTH_TOKEN=<mesmo valor do API_AUTH_TOKEN>
```

Isso é um token compartilhado, não é login de usuário. Qualquer variável `EXPO_PUBLIC_` vai embutida no bundle do app.

## Testes

```bash
cd mobile
npm test
```

Jest com `jest-expo`. Hoje só `src/lib/` tem teste (`alternativas.test.ts`, `api.test.ts`). Componentes e telas ainda não têm.

## Notas

- Expo SDK 57. A API do Expo mudou bastante entre versões: consulte a doc da versão exata (https://docs.expo.dev/versions/v57.0.0/) antes de mexer (ver `AGENTS.md`).
- `npm run reset-project` é resto do template do `create-expo-app`. Ele **move `src/` inteiro para `example/` e deixa um app vazio**. Não rode.
