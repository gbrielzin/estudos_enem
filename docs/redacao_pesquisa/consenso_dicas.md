# Consenso das dicas de redação (banco de dicas, 2026-09-27)

**Base:** 186 dicas extraídas de 23 páginas públicas de dica de redação ENEM (achadas pelo Common Crawl; ver [fontes.md](fontes.md)), de coRedação, Quero Bolsa, CNN Brasil, Redação Online, Blog do Enem, Imaginie, Metrópoles, Stoodi, Toda Matéria e Estratégia. Cada dica foi reescrita em uma frase (sem copiar texto), marcada com a competência e com **quem disse** (INEP citado, aluno nota 1000, professor/coordenador, ou blog sem autor), e agrupada com as equivalentes. 177 de 186 caíram num grupo. Banco local: tabelas `dicas` e `dicas_grupos` em `banco_1000/redacoes_1000.db`.

**Como ler:** "fontes" = páginas diferentes que dão a mesma dica. Não é pesquisa científica; é o consenso de quem ensina. Mesma matéria republicada (CNN e Agência Brasil) conta uma vez só. A coluna INEP diz se a dica bate com a cartilha oficial (arquivos em `cartilhas/`).

## Top 25 por número de fontes

| # | Dica | Comp. | Fontes | Quem disse | Bate com o INEP? |
|---|---|---|---|---|---|
| 1 | Planeje antes: tese, argumentos, repertório e proposta (projeto de texto) | C3 | 10 | aluno 1000, professor, blog | Sim ("projeto de texto" é critério da C3) |
| 2 | Use repertório legitimado e variado (lei, dado, obra, pensador, arte) | C2 | 10 | aluno 1000, professor, blog | Sim |
| 3 | **Ligue o repertório ao tema/argumento e explique-o; nunca solto** | C2 | 8 | aluno 1000, professor, blog | **Sim, é o ponto central das cartilhas 2025/2026** |
| 4 | Escreva com frequência (1+ por semana) | rotina | 7 | aluno 1000, professor, blog | — |
| 5 | Tese clara e visão autoral defendida pelos argumentos | C3 | 6 | INEP, aluno 1000, professor | Sim ("autoria") |
| 6 | Use conectivos variados e evite repetição | C4 | 6 | professor, blog | Sim |
| 7 | Treine com correção e estude os seus erros | rotina | 6 | aluno 1000, professor, blog | — |
| 8 | Acompanhe notícias; estude eixos temáticos | rotina | 5 | professor, blog | — |
| 9 | Não copie os textos motivadores | C2 | 4 | professor, blog | Sim (linha copiada não conta) |
| 10 | Sublinhe as palavras-chave e delimite o recorte do tema | C2 | 4 | professor, blog | Sim (tangenciar derruba C2/C3/C5) |
| 11 | Proposta com agente, ação, meio, finalidade e detalhamento | C5 | 4 | INEP, professor, blog | Sim |
| 12 | Respeite os direitos humanos na proposta | C5 | 4 | INEP, professor, blog | Sim |
| 13 | 4 parágrafos: introdução, 2 desenvolvimentos, conclusão | geral | 4 | professor, blog | Não exige (mas é o padrão das notas 1000) |
| 14 | Leia com regularidade | rotina | 4 | aluno 1000, professor, blog | — |
| 15 | Leia tema e motivadores com atenção logo no início | prova | 4 | professor, blog | Sim |
| 16 | Detalhe a proposta; nada vago | C5 | 3 | professor, blog | Sim |
| 17 | Proposta clara, viável e coerente com a tese | C5 | 3 | INEP, professor, blog | Sim ("articulada à discussão") |
| 18 | Retome na conclusão a referência/tese da introdução; sem argumento novo | C3 | 3 | professor, blog | Sim (elogiado nas notas 1000 comentadas) |
| 19 | Reserve 60-90 min pra redação e não deixe por último | prova | 3 | professor, blog | — |
| 20 | Faça rascunho e passe a limpo com letra legível | prova | 3 | professor | Sim (letra ilegível pode zerar) |
| 21 | Sono, alimentação, exercício e calma | rotina | 3 | aluno 1000, professor | — |
| 22 | Organize os argumentos por causa e consequência | C3 | 2 | professor | Não fala (é o esqueleto das notas 1000) |
| 23 | Comece cada parágrafo com tópico frasal claro | C3 | 2 | professor, blog | Não fala |
| 24 | Escreva em 3ª pessoa, linguagem impessoal | C1 | 2 | professor, blog | Não exige |
| 25 | Revise a gramática no fim da prova | C1 | 2 | professor | Sim (desvio só como exceção, sem reincidência) |

## Contradições entre fontes (e com o INEP)

| Dica que circula | Quem diz | O que o INEP diz | Veredito |
|---|---|---|---|
| "Use título que dialogue com a argumentação" | blog (análise de notas 1000) | Título **não pontua** em nenhuma competência e pode levar a nota zero se tiver algo passível de anulação | **Não use título.** Risco sem ganho |
| "Nota 200 em C1 tolera no máximo 1 desvio" | professora (Redação Online) | Desvio aceito "somente como excepcionalidade e quando não caracterizar reincidência" — **sem número** | O número é interpretação dela. A regra real: nenhum erro repetido |
| "Distribua a proposta em vários parágrafos" | professora (Metrópoles) | Pode aparecer em qualquer parte, mas **só a proposta mais completa pontua** | Pode espalhar, mas **uma** delas tem de ter os 5 elementos |
| "Proponha ação inédita, não algo que já existe" | coordenador (Quero Bolsa) | Pede ação concreta, detalhada e ligada à discussão; **não exige ineditismo** | Opcional. O que pontua é estar completa e ligada às causas |
| "Dê nome ao projeto de intervenção" | professora (CNN) | Não exige | Opcional; pode ajudar no detalhamento |
| "Vá do argumento mais fraco pro mais forte" | coordenador (Quero Bolsa) | Não fala | Preferência de estilo, sem evidência |

## O que isso muda no modelo do Gabriel

O molde dele (2 estruturas fixas, D1 = Estado, D2 = sociedade/mídia, CF/88 na abertura) já cumpre as dicas de maior consenso de **estrutura** (#1 projeto de texto, #13 quatro parágrafos, #22 causa e consequência, #23 tópico frasal). O que o consenso cobra e o molde ainda não entrega sozinho:

1. **#3 é a dica mais importante pra ele** (8 fontes + cartilha): repertório explicado e ligado ao recorte. No molde, é a frase logo depois do repertório ("Isso ocorre porque...") com um fato do tema — o que as notas 1000 com Mbembe/Chomsky tinham e a redação 2 dele não.
2. **#10 recorte**: o teste de 2 minutos (sublinhar as palavras do tema e pôr cada uma na tese, no início de D1 e D2 e na proposta) — protege o molde do tangenciamento.
3. **#11, #16, #17 proposta completa**: 2 ações (uma por causa), cada uma com os 5 elementos; o erro mais caro é a ação parecer finalidade.
4. **#7 e #25 correção e revisão da C1**: confirma o dado dos microdados de 2025 (96% dos 960-980 não tiram 200 em C1). Caçar só os erros recorrentes dele.
5. **Não adotar**: título, "ação inédita" como regra e contagem de "1 desvio" — não pontuam ou não são regra oficial.

Relacionados: [padroes_1000.md](padroes_1000.md) (o que as 342 redações e os microdados mostram), [metodo_960.md](metodo_960.md), [dicas_obscuras.md](dicas_obscuras.md), [atalhos_e_repertorios.md](atalhos_e_repertorios.md).
