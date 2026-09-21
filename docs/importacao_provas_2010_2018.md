# Importação das provas regulares 2010 a 2018 (Natureza, caderno azul)

Executado em 2026-09-21 com `core/importar_corpus_antigo.py` (Fase 1 de `docs/plano_ampliar_banco_provas_antigas_e_ppl.md`).

## O que entrou no `enem.db`

**403 questões** de Ciências da Natureza, caderno azul, 2010 a 2018 (2009 ficou de fora: matriz diferente).

| Ano | Questões | Com aviso ⚠️ (pode faltar figura) |
|---|---|---|
| 2010 | 45 | 16 |
| 2011 | 45 | 21 |
| 2012 | 45 | 17 |
| 2013 | 44 | 20 |
| 2014 | 45 | 22 |
| 2015 | 45 | 18 |
| 2016 | 44 | 22 |
| 2017 | 45 | 23 |
| 2018 | 45 | 25 |

Ficaram de fora 2 questões sem as 5 alternativas no corpus: **2013 nº 64** e **2016 nº 47**.

## Portão de validação (feito antes de gravar)

O gabarito gravado vem do `ITENS_PROVA` oficial do INEP (`core/inep_itens/`), não do corpus. O corpus só foi usado para achar qual prova e posição do INEP correspondem (casamento do gabarito, exigindo 40 de 45 iguais).

| Ano | Prova INEP | Gabarito do corpus igual ao oficial |
|---|---|---|
| 2010 | 89 | 45/45 |
| 2011 | 121 | **44/45** (nº 81: corpus B, INEP D; vale D) |
| 2012 a 2018 | 141, 171, 199, 235, 291, 391, 447 | 45/45 em todos |

Nenhum item anulado nesse intervalo. (Em 2020 há um, o nº 135, que o corpus trazia com gabarito e o INEP marca como anulado: isso não afeta esta importação.)

## Como ficou no banco

- `id_questao`: `<ano>_azul_<índice do caderno azul>` (2010 a 2016: 46 a 90; 2017 e 2018: 91 a 135).
- `origem = enem_oficial` e `fonte = corpus_enem_dev+gabarito_inep`, para as análises poderem incluir ou excluir esse bloco (a coluna `origem` só aceita dois valores fixos, então a marca ficou em `fonte`).
- `materia = sem_video_pendente` (`nao_classificado`): entram na Triagem. Não classifiquei por palavra-chave porque, no corpus, esse método concordou só ~56% com os rótulos do banco.
- Questões que citam figura/tabela levam o mesmo aviso ⚠️ de `extrair_enunciados_pdf.py`; os links de imagem do enem.dev foram removidos do texto. Nesses casos as figuras **não estão** no banco.
- Backup feito antes da gravação (`core/backups/`, ignorado pelo git). `integrity_check` = ok; 104 testes passam.

## Limites (o que ainda não sei)

- O casamento com o gabarito prova que a **ordem e o gabarito** batem com o caderno azul do INEP; não verifiquei o **texto** de cada enunciado contra o PDF.
- ~45% das questões dependem de figura que não foi recuperada: usar como treino de conteúdo, não como simulado fiel, até recuperar as figuras.
- O Cartão-resposta trata cada prova como simulado independente; as 9 provas novas só têm Natureza (sem Matemática do mesmo ano).
- Não avaliei o efeito no ranking `prioridade_de_estudo()` ao classificar essas questões: enquanto ficarem `nao_classificado`, elas não entram nos rankings por matéria.

## Reexecutar

`cd core && python importar_corpus_antigo.py` (só leitura) e `--aplicar` para gravar; idempotente.
