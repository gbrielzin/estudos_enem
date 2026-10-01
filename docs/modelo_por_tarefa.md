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

Esforço baixo nunca em gabarito ou explicação de questão: errar gabarito custa mais que o token economizado.

## Como as skills usam (passo 0)

1. Achar a linha da tarefa na tabela.
2. Comparar com o modelo em que a sessão está rodando (o Claude sabe qual é). O esforço o Claude nem sempre sabe; se não souber, cite só o modelo.
3. Se bater, não dizer nada e seguir.
4. Se não bater, avisar em **uma linha** e esperar: "Esta tarefa pede <modelo> com esforço <nível>. Você está no <modelo atual>. Troque com `/model` ou responda 'segue'."
5. Se ele responder "segue", seguir sem repetir o aviso na mesma sessão.
