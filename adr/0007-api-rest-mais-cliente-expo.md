# ADR-0007: Extrair API REST (FastAPI) e reescrever o cliente em Expo/React Native

Status: aceito
Data: 2026-09-15 (retroativo — decisão já em vigor desde a criação de `core/api.py` e `mobile/`)

## Contexto

O ADR-0001 já previa o gatilho: "quando o app mobile precisar ler/escrever
no mesmo `enem.db` que o Streamlit usa hoje — nesse momento `db.py` precisa
ficar atrás de uma API real". Isso aconteceu. Além disso, o objetivo de
produto mudou de "reskin do Streamlit" para "vender um produto visualmente
viciante" — e o Streamlit esbarrou em limitações reais de UI que não têm
solução dentro do próprio framework: seletores CSS que quebram entre
versões, `st.progress`/`st.radio` sem controle visual fino, `<svg>` que não
renderiza dentro de `st.markdown` (impede o desenho da trilha estilo
Duolingo do jeito que o design pedia).

## Decisão

Extrair `db.py` atrás de uma API REST fina em FastAPI (`core/api.py`, hoje
13 endpoints — `/materias`, `/trilha`, `/fases`, `/tentativas`, `/streak`,
`/nivel`, `/missoes-do-dia`, `/dias-ate-prova`, `/resumo-geral`,
`/explorar`, entre outros), e reescrever a camada de apresentação em
Expo/React Native (`mobile/`) — mesmo código rodando em iOS, Android e Web
(via `react-native-web`), substituindo Streamlit como o "produto".
`core/api.py` não duplica nenhuma regra de negócio: só traduz chamada HTTP
em chamada de função Python sobre `db.py`, mesma regra de camadas de sempre
(ver `core/CLAUDE.md`, seção "Layering rule").

## Alternativas consideradas

- **Continuar só no Streamlit, investindo em customização CSS mais
  agressiva** — testado antes desta decisão (ver histórico de commits de
  redesign do tema); as limitações citadas no Contexto são estruturais do
  framework, não de esforço de CSS.
- **Backend em outra linguagem (ex: Spring Boot/Java) por trás do app
  mobile** — trocaria tecnologia sem melhorar nada visível pro usuário
  final; FastAPI já resolve o problema real (expor `db.py` via HTTP) com
  menos superfície nova de aprendizado, mantendo Python em todo o backend.

## Consequências

Ganha: o app mobile e o Streamlit passam a ler o MESMO `enem.db`/`db.py`
sem duplicar regra de negócio nenhuma — a migração não tocou em
`_calcular_leitner()`, `prioridade_de_estudo()` nem na taxonomia, só
adicionou uma camada de tradução HTTP por cima. Web e mobile nativo saem do
mesmo código-fonte (`react-native-web`), sem "implementar de novo pro
desktop" ser um projeto à parte.

Custa: agora existem DUAS superfícies de UI vivas em paralelo (Streamlit +
Expo) até a migração de features estar completa — cada feature nova
potencialmente precisa decidir em qual (ou nas duas) ela entra. A API
(`core/api.py`) hoje não tem autenticação nem controle de acesso — aceitável
enquanto o único cliente é o próprio celular do usuário na mesma wifi
doméstica (mesmo raciocínio do CORS aberto, `allow_origins=["*"]`), mas é
uma dívida técnica explícita, não um descuido — precisa ser resolvida antes
de qualquer cenário multiusuário ou de exposição fora da rede local.

## Quando revisitar

Quando o Streamlit deixar de ser usado como ferramenta pessoal (nesse
ponto, `core/cartao_resposta.py` vira código morto a ser removido, não
mais uma segunda superfície ativa) — ou quando a API precisar sair da wifi
doméstica, momento em que autenticação/CORS restritivo deixam de ser
opcionais.
