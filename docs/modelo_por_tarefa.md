# Modelo por tarefa

Fonte única de qual modelo e esforço usar em cada tipo de tarefa. As skills `/estudo`, `/pr` e `/conteudo` leem este arquivo no passo 0 e avisam se a sessão estiver no modelo errado. Mudou de ideia? Edite só aqui.

Combinado em 2026-10-01. Regra geral: **Sonnet com esforço médio como padrão**; Opus com esforço alto só quando a tarefa exige raciocínio; esforço máximo quase nunca.

| Tarefa | Skill | Modelo | Esforço |
|---|---|---|---|
| Sessão de estudo (diagnóstico, molde, explicação de exatas) | `/estudo` | Opus 5.5 | alto |
| PR pequeno (doc, ajuste de UI, CHANGELOG, teste) | `/pr` | Sonnet 5.5 | médio |
| PR que mexe em lógica de vários arquivos, ou `/code-review` antes do merge | `/pr` | Opus 5.5 | alto |
| Roteiro de vídeo e post de LinkedIn | `/conteudo` | Sonnet 5.5 | médio |
| Lote de questões (cadastro, gabarito, explicação) | — | Sonnet 5.5 | médio a alto |
| Decisão de arquitetura, trilha ROI, bug difícil | — | Opus 5.5 | alto |
| Tarefa mecânica (renomear, formatar CSV, git simples) | — | Haiku 4.5 ou Sonnet 5.5 | baixo |
| Transcrição de vídeo/live → notas do projeto | — | Sonnet 5.5 | médio |
| Limpar transcrição (tirar horário, juntar linhas) | — | nenhum: script local | — |

Esforço baixo nunca em gabarito ou explicação de questão: errar gabarito custa mais que o token economizado.

## Como as skills usam (passo 0)

1. Achar a linha da tarefa na tabela.
2. Comparar com o modelo em que a sessão está rodando (o Claude sabe qual é). O esforço o Claude nem sempre sabe; se não souber, cite só o modelo.
3. Se bater, não dizer nada e seguir.
4. Se não bater, avisar em **uma linha** e esperar: "Esta tarefa pede <modelo> com esforço <nível>. Você está no <modelo atual>. Troque com `/model` ou responda 'segue'."
5. Se ele responder "segue", seguir sem repetir o aviso na mesma sessão.

## Transcrição de vídeo e live: como gastar menos token (2026-10-13)

Caso real: a live do PC (3 h) tem 144 KB de texto cru; ler inteira custou ~45 mil tokens de entrada. O vídeo do Vinícius (46 min) é bem menor. Ordem que economiza:

1. **Limpar com script, sem modelo.** Tirar o horário de cada linha e juntar por minuto já tira cerca de 30% do texto (144 KB → 102 KB na live). É `awk`/Python, custa zero token.
2. **Não ler a live inteira se a pergunta é específica.** Ex.: "o que ele fez de animação?" → buscar por palavras (`animação`, `scroll`, `3D`, `prompt`) e ler só em volta. Ler tudo só quando a decisão depende do contexto todo.
3. **Dividir e resumir por pedaço** quando for ler tudo: um agente barato (Haiku 4.5) resume cada bloco de ~30 min com limite de tamanho, e o Sonnet 5.5 faz a síntese final. Saída custa mais que entrada, então pedir resumo com teto de linhas.
4. **Não reenviar a transcrição a cada pergunta.** Pedir as notas uma vez, salvar em `docs/` e daí em diante trabalhar a partir das notas.
5. **Não precisa de Opus** pra isso. Opus só se a transcrição virar decisão de arquitetura.

Limite: o que o modelo "entendeu" do vídeo é só o que está na legenda. Número que o criador fala de si (faturamento, resultado) continua sendo alegação, não fato.

### Ferramentas que já existem pra economizar token (pesquisa de 13/10)

Quase tudo é número que o próprio autor divulga, **sem teste independente**. O que o benchmark mais sério que achei mediu foi 20-43% de redução no total, bem abaixo dos "70-95%" que os autores anunciam.

| Ferramenta | O que faz | Observação |
|---|---|---|
| RTK | proxy que corta comentário, espaço e linha repetida da saída de comando antes de chegar no modelo | open source; é o mais citado no nicho |
| ooples/token-optimizer-mcp | servidor MCP com cache e compressão | MIT; "até 95%" é alegação do autor |
| Magic Compact (aerovato) | compactação sem perda no lugar do resumo genérico do Claude Code | plugin; "2-3x mais duração" é alegação do autor |
| cctx | CLI/MCP que usa modelo local (Ollama) pra indexar e resumir | MIT; "70-90%" é alegação do autor |
| caveman | skill que faz as respostas saírem curtas | mede só token de saída |

Antes de instalar qualquer uma: abrir o repositório, ver se tem teste e quem mantém, e testar numa sessão curta comparando o gasto. Ferramenta que lê toda a saída do terminal merece cuidado (pode ver segredo).

O que a própria documentação e os guias recomendam e não custa instalar nada: escolher o modelo certo por tarefa (esta tabela), compactar o contexto na hora certa em vez de deixar o automático disparar perto do limite (é caro), abrir sessão nova quando o assunto muda, e pedir respostas curtas.
