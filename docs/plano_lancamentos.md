# Plano de lançamentos: pós-ENEM 2026 → 2027

Plano de 2026-10-27. Ideia central: **o aluno usa grátis, a escola paga.** Cada lançamento entra no pico de procura do calendário ([marketing/calendario.md](marketing/calendario.md)), e o estudo vem primeiro até a prova (8 e 15/11).

## Cronograma

| Quando | O quê | Status |
|---|---|---|
| Até 8/11 | Estudo + desenho à mão da tela do lançamento 1 + vídeos de bastidor | 💡 |
| 9-14/11 | Se sobrar energia: interface do lançamento 1 a partir do desenho | 💡 |
| Semana do gabarito oficial (dias depois de 15/11) | **Lançamento 1: "Quanto eu tirei?"** | 💡 |
| Janeiro (SISU) | **Lançamento 2: "Onde eu entro" + portas de entrada** | 💡 |
| Fevereiro em diante | Plataforma de questões para quem vai refazer + conversas com escolas | 💡 |

Rotina diária até a prova: bloco de estudo (sem cortar) → no máximo 1 h de código gravando a tela → 1 vídeo curto do que foi feito.

## Lançamento 1: "Quanto eu tirei?"

**Fluxo:** marca o gabarito → nota estimada pela TRI → card bonito pra compartilhar → deixa o contato pra ver onde entra.

- Reaproveita: parâmetros TRI do INEP no banco (`tri_a`, `tri_b`, `tri_c`), correção do cartão-resposta (`core/cartao_resposta.py`).
- **Roda inteiro no navegador:** parâmetros num arquivo, conta feita no celular do aluno. Sem servidor, sem custo, não cai se viralizar.
- Sempre escrito "nota **estimada**": o cálculo do INEP não é público em todos os detalhes.
- O card é o que espalha: precisa ser grátis e bonito.

## Lançamento 2: "Onde eu entro" + portas de entrada

**Promessa (verdadeira):** "Com a sua nota, existem cursos em faculdade pública que você nem sabia que alcança." Nunca "você passa em qualquer pública".

- Simulador "onde eu entro" (protótipo em [ideias_melhorias.md](ideias_melhorias.md) §4): nota ponderada pelos pesos do curso vs corte da cota, filtro por estado e curso.
- Corte mostrado como **referência do ano anterior**, não garantia (varia 10-30 pontos por ano).
- **Portas de entrada**, personalizadas pela nota e pelo estado, com lembrete antes de cada prazo:

| Porta | O que é |
|---|---|
| SISU | Federais e estaduais com a nota do ENEM |
| ProUni | Bolsa em faculdade particular com a nota do ENEM |
| FIES | Financiamento em particular |
| Vestibulares próprios | Fuvest (USP), Unicamp, Unesp, UERJ, outras estaduais |
| Vagas pelo ENEM fora do SISU | Enem-USP; Provão Paulista (escola pública de SP) |
| Institutos Federais | Superior e técnico |
| Isenção de taxa | Prazo próprio, muita gente perde |

- **Só edital oficial**, com a data em que a informação foi conferida. Prazo errado faz aluno perder vaga.
- É produto de ciclo anual: para quem entra em 2027, as portas abertas em jan-fev são principalmente SISU, ProUni e FIES (Fuvest/Unicamp costumam abrir inscrição no meio do ano; conferir). O resto vira lembrete do próximo ciclo.
- O lembrete guarda o contato e traz o aluno de volta todo ano.

## Monetização

Base: **B2B paga a plataforma grátis.** O resto é extra.

| # | Ideia | Quando | Observação |
|---|---|---|---|
| 1 | Relatório da turma pra escolas e cursinhos | fev em diante | onde a turma erra e quanto custou; pico depois de simulados |
| 2 | Orientação pós-ENEM pra escola (portas de entrada da turma) | jan em diante | liga o lançamento 2 ao B2B |
| 3 | "Adote um aluno" | 2027 | empresa paga o plano completo pra alunos de escola pública e associa a marca |
| 4 | Patrocinador do card ("oferecido por...") | lançamento 1 | contador de uso como prova de alcance |
| 5 | "Quanto cada erro custou" avulso, ~R$ 9,90 via Pix | lançamento 1 | compra por impulso logo depois da prova |
| 6 | Pré-venda do Plano 2027 com preço de fundador + mural | lançamento 1 | só prometer o que está quase pronto; reembolso se não entregar |
| 7 | Indicação de bolsas/faculdades particulares | lançamento 2 | útil quando a nota não alcança a pública; deixar claro que é parceria |
| 8 | Receita aberta nos vídeos | sempre | engajamento, não dinheiro |
| 9 | Promessa pública ("se eu tirar X, fica grátis por uma semana") | resultado do ENEM | promessa, não aposta |

## B2B: roteiro das primeiras conversas

- **Público:** escolas particulares pequenas e cursinhos (decidem rápido, dono na reunião). Escola pública compra por secretaria/licitação: depois.
- **Não vender, perguntar.** Meta: 5 conversas. Pergunta central: "qual a parte mais chata de preparar a turma pro ENEM?" Anotar o que se repete.
- Dores prováveis a confirmar: não saber onde a turma erra; aluno sai perdido depois da prova; mostrar resultado pros pais.
- A história (aluno que fez a prova e construiu o app) abre a porta; o que fecha é resolver a dor.
- Timing: escola particular costuma fechar o ano seguinte entre o fim do ano e janeiro. 2027 é apertado; mirar 2º semestre ou 2028.

| Data | Escola/cursinho | Quem | Dor que apareceu | Próximo passo |
|---|---|---|---|---|
| | | | | |

## Cuidados

- **Dados de aluno:** seguir a política de privacidade do app (PR #59). Relatório só agregado; nunca a nota de um aluno pra outro.
- **Receber de empresa** (patrocínio, adote um aluno) exige CNPJ e nota fiscal. Ver com contador qual tipo serve pra software (nem toda atividade de TI cabe no MEI). Pix de pessoa física primeiro.
- **Não esconder autoria** nos posts: "fiz isso em X dias" é o gancho, e vira portfólio.
