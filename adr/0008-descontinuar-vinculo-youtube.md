# ADR-0008: Descontinuar a automação de vínculo de vídeo do YouTube

Status: proposto — decisão ainda não finalizada nem implementada (ver nota)
Data: 2026-09-15

## Contexto

`coletar_videos.py` (500 linhas) automatiza a ligação entre questão e
vídeo-resolução: autenticação OAuth com a YouTube Data API (reaproveitada
de `main.py`, ver a exceção sancionada de camada em `core/CLAUDE.md`),
varredura de playlist, extração de matéria a partir do título do vídeo, e
um parser específico pra um padrão de descrição do canal (Xequemat) que
lista o mesmo número de questão em cada cor de caderno — permitindo ligar
UM vídeo a TODAS as cores de caderno daquela questão de uma vez
(`extrair_cadernos_da_descricao()`, documentado em `core/CLAUDE.md`, seção
"Cross-caderno video linking"). Hoje existem **536 resoluções do tipo
vídeo** vinculadas no banco (`resolucoes`, todas `tipo='video'`), e a
feature tem página própria no Streamlit ("Coletar vídeos").

Fazia sentido no momento em que foi construída: era a forma mais rápida de
dar contexto de resolução pra questão errada, sem esforço manual por
questão.

## Decisão

**Ainda em aberto.** A direção apontada é descontinuar essa automação — o
próprio autor avalia que o motivo original que justificava a feature não
se sustenta mais, sem que isso torne o trabalho anterior menos válido.

> **TODO (preencher antes de fechar este ADR):** qual é o motivo concreto
> pelo qual isso deixou de fazer sentido? (ex: substituído por outra forma
> de resolução — tutor por IA, texto explicativo próprio; custo de
> manutenção da chave/OAuth não compensa mais; baixo uso real da feature;
> outro.) Um ADR sem essa frase não cumpre o propósito do próprio
> `adr/README.md` — "guardar o raciocínio", não só o "o quê".

## Alternativas consideradas

- **Manter como está** — descartada (ver Decisão acima), mas ainda é a
  opção vigente até este ADR ser fechado como "aceito".
- **Manter os 536 vínculos já existentes, só parar de rodar a coleta
  automática pra questão nova** — provavelmente a opção de menor
  atrito: não perde o dado já coletado nem exige decidir o que fazer com
  `resolucoes` existentes, só descontinua `coletar_videos.py` e a página
  "Coletar vídeos" pra frente.
- **Remover tudo** (código + dado já coletado) — mais radical, só faz
  sentido se o motivo de descontinuar for algo como "essas resoluções não
  são mais confiáveis/relevantes", não só "não quero manter a automação".

## Consequências

Ganha (se descontinuada): remove a dependência de `google-api-python-client`
+ `google-auth-oauthlib` + `YOUTUBE_API_KEY` do projeto (uma chave a menos
pra rotacionar/proteger antes de publicar), reduz superfície de manutenção
(500 linhas + a integração OAuth que só um projeto com essa feature
precisa).

Custa: se remover os dados já coletados junto, perde as 536 ligações
questão↔vídeo que hoje ajudam a revisão de erro no Cartão-resposta —
mitigável mantendo o dado e só descontinuando a coleta nova (ver
Alternativas).

**Isso não é uma perda de portfólio.** A engenharia por trás (fluxo OAuth
completo, parsing de padrão de texto não-óbvio na descrição de vídeo,
resolução de link cruzado entre cadernos) continua sendo evidência técnica
real, com ou sem a feature ativa no produto final — vale continuar citável
em entrevista mesmo depois de removida do código corrente (é exatamente o
tipo de coisa que este ADR existe pra preservar).

## Quando revisitar

Assim que o motivo do TODO acima for preenchido — nesse momento o status
muda pra "aceito" (com a alternativa escolhida) ou o ADR é descartado se a
decisão for de fato manter a feature.
