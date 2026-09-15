# ADR-0008: Descontinuar a automação de vínculo de vídeo do YouTube

Status: aceito
Data: 2026-09-15

## Contexto

`coletar_videos.py` (500 linhas) automatizava a ligação entre questão e
vídeo-resolução: autenticação OAuth com a YouTube Data API (reaproveitada
de `legacy/main.py`), varredura de playlist, extração de matéria a partir
do título do vídeo, e um parser específico pra um padrão de descrição do
canal (Xequemat) que lista o mesmo número de questão em cada cor de
caderno — permitindo ligar UM vídeo a TODAS as cores de caderno daquela
questão de uma vez. Além disso, `core/questoes_enem.csv` (versionado no
Git) guardava 276 links desse mesmo canal, recarregados a cada
`reconstruir_base.py`. No total, isso resultava em 536 resoluções do tipo
vídeo no banco (`resolucoes`), e a feature tinha página própria no
Streamlit ("Coletar vídeos").

Fazia sentido no momento em que foi construída: era a forma mais rápida de
dar contexto de resolução pra questão errada, sem esforço manual por
questão, num sistema de uso pessoal e não-comercial.

## Decisão

**Remover completamente** — código, dados já coletados, e o arquivo-fonte
de terceiro:

- `core/coletar_videos.py` removido.
- `legacy/` (pasta inteira: `main.py`, `app.py`) removida — só existia
  pra sustentar esta feature e o modo de busca por palavra-chave que
  dependia dela.
- `core/questoes_enem.csv` (276 links de vídeo de terceiro) removido do
  repositório e do histórico do Git (não só do estado atual — ver nota
  de reescrita de histórico abaixo).
- As 536 resoluções do tipo `video` apagadas de `core/enem.db`.
- Dependências `google-api-python-client`, `google-auth-oauthlib` e
  `python-dotenv` removidas de `requirements.txt`; `.env.example`
  removido (não sobra nenhuma variável de ambiente exigida pelo projeto).
- Página "Coletar vídeos" removida de `core/cartao_resposta.py`.

**Motivo concreto** (o que fecha o TODO da versão anterior deste ADR): o
projeto está migrando de ferramenta pessoal pra um produto com múltiplos
usuários e monetização própria (ver `adr/0007`). Redistribuir/vincular
sistematicamente vídeos de terceiros (conteúdo de outro criador, hospedado
fora, coletado via scraping automatizado de canal) dentro de um produto
comercial multiusuário é um risco de direito autoral real que não existia
quando isso era só uso pessoal — a automação deixou de fazer sentido não
por custo de manutenção, mas porque o contexto de uso mudou.

## Alternativas consideradas

- **Manter como está** — descartada: o risco de direito autoral citado
  acima se aplica igualmente aos 536 vínculos já coletados, não só à
  automação de coleta nova.
- **Manter os 536 vínculos já existentes, só parar a coleta automática
  nova** — descartada pelo mesmo motivo: manter vínculos já coletados não
  reduz a exposição, já que o risco está em redistribuir o conteúdo de
  terceiro num produto comercial multiusuário, independente de quando o
  vínculo foi criado.

## Consequências

Ganha: remove toda a superfície de risco de direito autoral relacionada a
conteúdo de terceiro; remove a dependência de `google-api-python-client` +
`google-auth-oauthlib` + `YOUTUBE_API_KEY` (uma chave a menos pra rotacionar
e proteger); reduz superfície de manutenção (500 linhas de `coletar_videos.py`
+ 851 linhas de `legacy/` + a integração OAuth inteira).

Custa: perde as 536 ligações questão↔vídeo que ajudavam a revisão de erro
no Cartão-resposta — nenhuma resolução automática de terceiro substitui
isso hoje. `resolucoes` continua existindo no schema (tabela e funções
`inserir_resolucao()`/`resolucoes_da_questao()`/etc. não foram removidas)
pra uso manual (`tipo='texto'`, ou vídeo adicionado à mão um por um, uma
escolha editorial do próprio usuário, não scraping em escala) e para uma
futura correção/explicação por IA (ver `adr/0006`).

**Isso não é uma perda de portfólio.** A engenharia por trás (fluxo OAuth
completo, parsing de padrão de texto não-óbvio na descrição de vídeo,
resolução de link cruzado entre cadernos) continua sendo evidência técnica
real, com ou sem a feature ativa no produto final — vale continuar citável
em entrevista mesmo depois de removida do código corrente (é exatamente o
tipo de coisa que este ADR existe pra preservar).

## Quando revisitar

Se algum dia o produto voltar a ser uso estritamente pessoal/single-user
(cenário improvável, dado o rumo já tomado) — não antes disso.
