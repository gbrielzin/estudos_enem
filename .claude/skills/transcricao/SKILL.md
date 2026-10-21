---
name: transcricao
description: Transforma a transcrição de um vídeo ou live em notas úteis pro ENEM GI: ferramentas, passos do workflow, o que adotar, o que descartar e o que é alegação não conferida. Use quando o Gabriel colar ou anexar uma transcrição (Tactiq, YouTube) ou disser "analisa esse vídeo", "anota isso", "o que serve disso".
---

# /transcricao — do vídeo à decisão

Objetivo: tirar de cada vídeo **workflow, ferramenta e ideia aplicável**, e terminar em decisão. Informação que não vira decisão não entra nas notas.

## 0. Modelo e custo

Linha "Transcrição de vídeo/live" de `docs/modelo_por_tarefa.md` (Sonnet 5.5, médio). Se a sessão estiver em outro modelo, avise em uma linha e espere. Leia também a seção de economia de token do mesmo arquivo.

## 1. Preparar o texto (sem modelo)

Transcrição do Tactiq vem com horário em cada linha. Junte por minuto antes de ler (corta ~30%):

```
awk 'NR>3{t=substr($1,1,5); $1=""; if(t!=last){printf "\n[%s]",t; last=t} printf "%s",$0}' arquivo.txt > limpo.txt
```

Salve no scratchpad, nunca no repositório. Se tiver mais de ~1 h e a pergunta for específica, busque por palavras e leia só em volta. Se for ler tudo, leia em blocos.

## 2. Ler com ceticismo

- Separe **o que o criador ensina e mostra** de **o que ele conta de si** (faturamento, resultado, "já fiz dezenas de vezes"). O segundo é alegação, não fato.
- Se ele vende curso, mentoria ou ferramenta, diga.
- Texto vem com erro de legenda (nomes de ferramenta, sotaque). Nome estranho: escreva "como ele fala na legenda" e não afirme que existe.
- O que só aparece na tela e não é dito não está na transcrição. Peça prints.

## 3. Extrair (sempre neste formato)

| Seção | Conteúdo |
|---|---|
| Fonte | título, canal, duração, data da leitura |
| Quem fala | o que ele faz, o que vende |
| Ferramentas | nome, pra quê, custo se citado, **equivalente que o projeto já tem** |
| Processo | passos na ordem em que ele faz |
| Alegações | números dele, marcados como "não conferido" |
| Adotar | ação concreta, esforço (pequeno/médio/grande), onde entra |
| Não adotar | e por quê (custo, público menor de idade, já temos, só serve a B2B) |

Antes de recomendar uma ferramenta: conferir se ela **já existe no projeto** (`mobile/package.json`, `.claude/skills/`, `docs/ferramentas.md`) e se roda no nosso setup. Conferir licença quando for baixar asset.

## 4. Guardar

1. Uma linha na tabela de `docs/fontes_videos.md` (data, vídeo, o que rendeu, link pras notas).
2. Notas de workflow/ferramenta/animação: `docs/workflow_ia_design.md` (nova seção). Marketing e funil: `docs/marketing/`. Ideia de produto: `docs/ideias_melhorias.md`.
3. Itens "Adotar" ganham status 💡 / 🟡 / ✅ / ❌ nas tabelas dos docs.

Git: seguir a regra do `mobile/AGENTS.md` (sugerir o commit em bloco de código; só executar se o ambiente exigir e dizer que executou).

## 5. Responder

No máximo ~15 linhas: o que rendeu, o que adotar primeiro, o que descartar e por quê, e **uma** próxima ação pergunta ("faço o A7?"). Sem despejar a transcrição de volta.

## Regras

- Nunca instalar ferramenta nem criar conta por conta de um vídeo.
- Não copiar produto de terceiro tela por tela; aprender o que funciona e fazer a versão do ENEM GI.
- Público do ENEM GI inclui menor de idade: cobrança, anúncio e coleta de dado exigem cuidado (ver `docs/pesquisa_produto_visual_regras_marketing.md`).
