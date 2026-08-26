# Extração de Gabarito — prompt para OUTRA IA (não gasta seu token aqui)

Use esse prompt numa IA separada (ChatGPT, Gemini, outro chat de Claude) quando você tiver
o PDF do caderno de questões + o PDF/imagem do gabarito oficial de um ano/caderno que falta.
O objetivo é sair de lá com um CSV pronto pra colar no Admin → "Colar gabarito direto".

## O prompt (copie e cole, e anexe os PDFs na mesma mensagem)

```
Você vai extrair o gabarito oficial e classificar a matéria de cada questão de uma prova do
ENEM (Ciências da Natureza ou Matemática), pra alimentar um sistema Python que carrega CSV
com colunas exatas: numero,materia,gabarito

REGRAS OBRIGATÓRIAS:
1. O gabarito (a letra A-E de cada questão) só pode vir do documento oficial de gabarito que
   eu anexei — nunca resolva a questão você mesmo pra "descobrir" a resposta certa. Se uma
   questão não tiver gabarito nesse documento, não a inclua no CSV, liste separadamente como
   pendente.
2. Questões marcadas como ANULADAS não entram no CSV. Liste-as à parte.
3. A "materia" de cada questão vem da leitura do enunciado no caderno de questões (conteúdo
   real), nunca do número ou de suposição. Classifique CADA questão contra a taxonomia fechada
   abaixo — só use um nome que já exista nessa lista. Se genuinamente não encaixar em nenhum,
   use o fallback genérico da grande área (biologia / quimica / fisica / matematica_basica) e
   marque como "REVISAR" numa coluna observacao à parte (fora do CSV final).
4. Não invente nome de matéria novo. Se um tópico se repetir 3+ vezes sem encaixar na lista,
   me avise no final — eu decido se vira taxonomia nova.
5. Formato de saída: bloco de código com CSV puro, cabeçalho exato "numero,materia,gabarito",
   uma linha por questão, sem comentário dentro do CSV. Comentários e a lista de REVISAR/
   ANULADAS vêm depois, fora do bloco de código.

TAXONOMIA FECHADA (grande_area: materia):

matematica: estatistica, geometria_plana, geometria_analitica, geometria_espacial,
razao_e_proporcao, porcentagem, probabilidade, analise_combinatoria, funcao_1_grau,
funcao_2_grau, funcao_exponencial, logaritmo, trigonometria, progressao_aritmetica,
progressao_geometrica, sistema_de_equacoes, matematica_financeira, raciocinio_logico,
interpretacao_de_grafico, escala, unidade_de_medida, regra_de_tres, aritmetica,
matematica_basica, geometria, inequacao_e_modulo, conjuntos, funcoes, projecao_ortogonal

ciencias_natureza (Biologia): ecologia, genetica, evolucao, citologia, fisiologia_humana,
sistema_nervoso, sistema_imunologico, sistema_circulatorio, sistema_respiratorio,
sistema_digestorio, sistema_endocrino, reproducao_humana, embriologia, botanica, zoologia,
microbiologia, virus_e_bacterias, fungos, biotecnologia, meio_ambiente, saude_publica,
ciclos_biogeoquimicos, biologia (fallback genérico)

ciencias_natureza (Química): quimica_organica, quimica_inorganica, funcoes_organicas,
estequiometria, termoquimica, eletroquimica, cinetica_quimica, equilibrio_quimico, solucoes,
ligacoes_quimicas, tabela_periodica, radioatividade, polimeros, ph_e_poh, gases,
reacoes_quimicas, densidade, separacao_de_misturas, quimica_verde, quimica (fallback genérico)

ciencias_natureza (Física): cinematica, dinamica, estatica, termologia, calorimetria, ondas,
acustica, optica, eletricidade, eletrostatica, eletrodinamica, eletromagnetismo,
energia_e_trabalho, hidrostatica, gravitacao, fisica_moderna, fisica (fallback genérico)

Me diga o ano e o caderno (ex: 2022, Azul) antes de começar, se eu não tiver falado.
```

## Depois de rodar isso na outra IA

1. Confere o CSV rapidamente — se algo parecer estranho, cola aqui no meu chat que eu confirmo.
2. Salva o CSV como `gabarito_<ANO>_<CADERNO>_OFICIAL.csv` (Matemática) ou
   `gabarito_<ANO>_<CADERNO>_CIENCIAS_OFICIAL.csv` (Ciências).
3. Duas opções pra carregar:
   - Cola o conteúdo em Admin → "Colar gabarito direto" (marca `sobrescrever` se a prova já
     existe com matéria placeholder tipo `sem_video_pendente`) — grava automático em
     `gabaritos_reais/` também, não precisa mover arquivo na mão.
   - Ou joga o arquivo direto em `core/gabaritos_reais/` e roda `python reconstruir_base.py`.
4. Roda "Reclassificar com as regras atuais" na Triagem pra pegar sinônimo que a IA externa
   não bateu exatamente com o nome canônico.