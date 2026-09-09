# Como pedir mudanças visuais pro Claude Code

Guia curto de briefing + prompts prontos. Escrito depois de dois pedidos que deram trabalho:
"comece o app pela trilha, não pelo Banco de Questões" e "troque o gato pelo Pipoco branco
que deixei na pasta".

---

## 1. Por que aqueles dois pedidos falharam

Nos dois casos o pedido era claro **pra você** e ambíguo **pro código**.

**"Deixa a trilha como página principal."**
O agente não sabe se "página principal" é a rota `/`, a primeira aba do menu inferior,
o componente que o `App` renderiza por padrão, ou o estado inicial de um `st.session_state`.
Ele escolhe uma e você vê outra.

**"Troca pelo gatinho branco, o arquivo está na pasta do projeto."**
Faltam três coisas: o **caminho exato** do arquivo, **onde no código** a imagem antiga é
referenciada, e o que fazer com a antiga (apagar? manter?). "Está na pasta" pode significar
20 pastas diferentes num repo.

A regra que resolve os dois: **todo pedido visual precisa de um alvo no código, não só um
alvo na tela.**

---

## 2. O template de pedido

Cinco campos. Cabe em oito linhas e resolve 90% das idas e voltas.

```
ONDE      arquivo(s) ou rota exata
HOJE      o que está acontecendo agora
QUERO     o resultado, em uma frase
REFERÊNCIA  caminho do print/mock que mostra o resultado
ACEITE    como eu vou conferir que ficou certo
```

Exemplo real, do pedido da trilha:

```
ONDE      app/main.py (ou o arquivo que define a navegação)
HOJE      ao abrir o app cai em "Banco de Questões"
QUERO     abrir direto na trilha de Ciências da Natureza (Óptica)
REFERÊNCIA docs/design/screens/02-trilha.png
ACEITE    dar F5 na raiz e ver a trilha; "Banco de Questões" continua
          acessível pelo menu, só não é mais o padrão
```

O campo **ACEITE** é o que mais economiza tempo: dá ao agente um teste que ele mesmo roda
antes de dizer "pronto".

---

## 3. Como entregar imagens de forma eficaz

Claude Code **lê arquivos de imagem do disco**. Não precisa colar print no chat.

1. Crie `docs/design/` na raiz do repositório.
2. Jogue os PNGs desta pasta `screens/` lá dentro, mantendo os nomes numerados.
3. No pedido, **cite o caminho relativo**: `veja docs/design/screens/02-trilha.png`.

Nomeie o arquivo com o nome que a tela tem **no código**, não com o nome que ela tem na sua
cabeça. Se o componente se chama `TrackView`, o print ideal é `docs/design/TrackView.png`.
Aí o agente liga print ↔ arquivo sozinho.

Quando o print sozinho não basta (cor exata, espaçamento, fonte), mande o print **mais** o
trecho de spec correspondente do `README.md` deste pacote. Print mostra a intenção; a spec
tem os números.

---

## 4. Contexto permanente: CLAUDE.md

Coisas que valem pra sempre não devem ser repetidas a cada pedido. Crie um `CLAUDE.md` na
raiz do repo — o Claude Code lê automaticamente em toda conversa. Sugestão de conteúdo pro
seu projeto:

```markdown
# Contexto do projeto

App de estudos pro ENEM, gamificado. Backend pronto; o trabalho atual é visual.

## Regras de UI
- A tela inicial é a TRILHA (Ciências da Natureza / Óptica). Banco de Questões é uma aba
  secundária, nunca a rota padrão.
- O mascote é o Pipoco: gato BRANCO. Arte em assets/pipoco/. Nunca substituir por outro
  animal, outra cor, ou emoji.
- Paleta: fundo #0A0C10 · texto #F2F4F7 · ação #6EE12B · progresso #7C5CFF · recompensa #FFC42E
- Fontes: Baloo 2 (títulos) e Nunito (texto).
- Ícones em SVG traço 2px. Nada de emoji na interface.
- Botões têm sombra sólida embaixo (3–5px), sem gradiente.

## Referências visuais
Os PNGs em docs/design/screens/ são a fonte da verdade do layout.
```

Com esse arquivo no lugar, "troca o gato" volta a funcionar, porque a regra "o mascote é
branco e mora em assets/pipoco/" já está no contexto.

---

## 5. Prompts prontos

### 5.1 Trocar a tela inicial

> Quero que o app abra na trilha, não no Banco de Questões.
>
> Antes de mudar qualquer coisa: me diga em qual arquivo e em qual linha a tela inicial é
> decidida hoje, e liste todas as telas registradas na navegação. Não edite ainda.
>
> Depois que eu confirmar, faça a troca mantendo o Banco de Questões acessível pelo menu.
> Referência do resultado: docs/design/screens/02-trilha.png

O "não edite ainda" é o truque. Você vê o mapa antes dele mexer, e corrige o alvo se ele
apontou pro arquivo errado.

### 5.2 Trocar o mascote

> Substitua a arte do mascote pelo Pipoco (gato branco).
>
> Arquivo novo: assets/pipoco/pipoco-neutro.png  ← confirme que esse caminho existe
> antes de começar; se não existir, liste o que tem em assets/ e pare.
>
> 1. Rode um grep por todas as referências à imagem antiga do mascote e me mostre a lista.
> 2. Troque todas por Pipoco.
> 3. Não apague a arte antiga; mova para assets/_deprecated/.
>
> Referência: docs/design/screens/09-pipoco-cenarios.png

### 5.3 Aplicar o visual novo numa tela

> Recrie a tela X seguindo docs/design/screens/0N-x.png.
>
> Use os componentes e o sistema de estilo que já existem no projeto — não crie CSS novo
> paralelo se já houver um tema. Cores, fontes e espaçamentos exatos estão em
> docs/design/README.md, seção "Design Tokens".
>
> Faça uma tela por vez. Ao terminar, me mostre um print antes de seguir pra próxima.

---

## 6. Erros comuns (e a correção)

| Em vez de | Peça |
|---|---|
| "deixa mais bonito" | "aumente o espaçamento entre os cards de 8 pra 16px" |
| "o gato tá errado" | "o mascote deve ser o PNG em assets/pipoco/, veja print 09" |
| "arruma a home" | "na home: 1) remover X, 2) mover Y pro topo, 3) trocar cor de Z" |
| "usa o arquivo da pasta" | "usa assets/pipoco/pipoco-neutro.png" |
| pedir 6 mudanças de uma vez | uma mudança por mensagem, conferindo entre elas |

E o mais importante: **quando ele errar, não reformule o pedido — pergunte por que ele fez
daquele jeito.** "Por que você mudou o arquivo A e não o B?" costuma revelar que o repo tem
duas definições de tela, e aí o problema real aparece.

---

## 7. O que já está pronto neste pacote

- `screens/` — 9 PNGs em 2x das telas e da ficha do mascote
- `README.md` — spec completa: tokens, medidas, comportamento
- `RELATORIO-RODADA-2.md` — decisões de layout e as regras de overflow da trilha
- `reference/` — os protótipos HTML de origem
- `streamlit/` — tema pronto (`enem_theme.py`, `theme.css`) se o app for Streamlit

Copie `screens/` e `README.md` pra `docs/design/` no repositório e aponte o Claude Code
pra lá.
