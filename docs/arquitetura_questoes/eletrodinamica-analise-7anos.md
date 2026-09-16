# Eletrodinâmica/Eletromagnetismo — análise de padrão (ENEM 2019-2025)

Análise feita em cima de questões REAIS do ENEM, cobrindo **aplicação regular
E PPL** (segunda aplicação/reaplicação, provas de fato diferentes, não a
mesma prova reordenada — ver observação sobre "cor de caderno" no fim), 2019 a
2025. PDFs baixados direto de `download.inep.gov.br` e processados com
`extrair_enunciados_pdf.py` (corrigido nesta sessão: o regex de `Questão N`
só reconhecia a grafia mista usada em 2019-2021; 2022-2024 imprimem `QUESTÃO
N` em caixa alta — sem o fix, a extração vinha vazia para esses anos).

**12 provas no total**: aplicação regular de 2019 (azul), 2020 (azul), 2021
(azul), 2022 (azul), 2023 (cinza), 2024 (amarelo), 2025 (azul) + PPL de 2019,
2020, 2021, 2022, 2023, 2024 (2025 PPL ainda não publicada no site do INEP).
2021 PPL tem uma falha de fonte no PDF original que corrompe parte do texto
extraído (`scratch_enunciados_2021_ppl.txt`) — dá pra ler o suficiente pra
identificar o padrão, mas não confiar no texto literal daquelas questões.

Todos os enunciados da aplicação regular já foram gravados no `enem.db`
(`enunciado_texto`, via `atualizar_enunciado()`) — 318 questões no total, sem
sobrescrever nada que já existia. Os da PPL ficaram só nos arquivos de
scratch (`core/scratch_enunciados_<ano>_ppl.txt`, gitignored) porque **o
projeto ainda não carrega gabarito de PPL** — não tem onde persistir isso no
banco ainda (precisaria de uma CSV `gabarito_<ano>_ppl_CIENCIAS_OFICIAL.csv` e
uma decisão de produto sobre se PPL vira conteúdo praticável no app ou só
fonte de análise). Por ora é só fonte de análise de padrão.

## Padrões encontrados, por frequência e custo de domínio

| # | Padrão | Ocorrências (12 provas) | Exemplos | Custo pra dominar |
|---|---|---|---|---|
| **1** | **Conta de energia/consumo elétrico** (kWh, tarifa, potência×tempo, tempo de recarga de bateria) | **12x** — de longe o mais recorrente; aparece em praticamente toda prova analisada | 2019 Q179, 2021 Q128, 2025 Q94 (regular); 2020 Q180, 2021 Q111/Q121/Q125/Q170, 2022 Q92/Q154/Q175, 2024 Q166 (PPL) | **Baixo** — fórmula direta (E=P×t, ou proporção linear numa tabela/gráfico) |
| **2** | **Lâmpadas em série/paralelo — "o que acontece quando uma queima/sai"** | **6x** | 2019 Q126, 2023 Q128 (regular); 2020 Q95 (cordão de Natal, clássica), 2022 Q118, 2024 Q132 (PPL) | **Baixo-médio se souber a lógica** — é o mesmo princípio de "seguir o caminho" que você descreveu do seu professor, só que aplicado a "o que continua com corrente" em vez de "qual chave liga o quê" |
| 3 | Associação de resistores com cálculo pesado (divisor de tensão, resistência equivalente) | 8x | 2019 Q126, 2020 Q116, 2022 Q116/Q119, 2023 Q128, 2024 Q110 (regular); 2019 Q128, 2022 Q111, 2023 Q117 (PPL) | **Alto** — mais frequente em volume bruto, mas exige conta de verdade |
| 4 | Proteção elétrica conceitual (fusível, disjuntor, aterramento, gaiola de Faraday) | 4x | 2019 Q92, 2020 Q133 (regular); 2024 Q122 (PPL) | **Baixo** — decoreba, zero conta |
| 5 | Indução eletromagnética conceitual (campo variável → corrente/tensão) | 3x | 2020 Q98, 2023 Q93, 2025 Q122 (regular) | **Baixo** — uma frase decorada resolve |
| 6 | Instrumento de medida (onde ligar amperímetro/voltímetro) | 3x | 2020 Q93, 2024 Q110 (regular); 2022 Q105 (PPL) | Médio |
| 7 | Topologia/ligação certa (qual desenho liga do jeito pedido) | 2x confirmadas | 2021 Q126 (2 interruptores — a questão do seu print), 2024 Q109 (LED) | Baixo se souber ler o desenho, mas é onde mais gente erra |
| 8 | Contextos exóticos com fórmula (resistividade de fio, "trânsito como circuito", ECG) | 3x | 2021 Q109/Q131, 2022 Q128 | Médio-alto, pouco repetível |
| 9 | Outliers isolados (eletroquímica de bateria, força magnética/regra da mão direita) | 3x | 2019 Q118, 2021 Q105, 2025 Q130 | Alto, baixa recorrência |

## Como isso mudou a recomendação depois da PPL

Antes de incluir a PPL, "conta de energia" e "indução conceitual" pareciam
empatadas (3x cada). Com a PPL, **conta de energia dispara pra 12 ocorrências
em 12 provas** — é o padrão mais estável e recorrente de toda a matéria, não
só "um dos padrões". E surgiu um padrão que não tinha aparecido antes:
**lâmpadas em série/paralelo com uma queimando/saindo** (6x), que é
exatamente o tipo de questão onde a lógica "seguir o caminho e ver o que
continua ligado" (do jeito que seu professor ensinou) se aplica direto.

## Recomendação final de ordem pra Aula Base / banco de questões do Nó 6

1. **Conta de energia/consumo** — de longe o mais recorrente, fórmula direta.
   Abre a trilha.
2. **Lâmpadas em série/paralelo (queima uma, o que sobra aceso)** — segundo
   mais recorrente, e a lógica de "caçar o caminho livre" que você validou
   pessoalmente se aplica direto aqui.
3. **Indução eletromagnética conceitual** + **Proteção elétrica conceitual**
   — agrupar os dois num único bloco "decoreba sem conta" (juntos são 7
   ocorrências, cada um pouco recorrente sozinho mas ambos com custo
   quase zero).
4. **Topologia/interruptores** (a questão original do seu print) — mantém,
   mas mais pro fim da base por ser mais trabalhosa de ensinar bem (exige
   prática de leitura de desenho, não só decorar regra).
5. Reserva/fase 2: associação de resistores com conta pesada (#3 da tabela,
   mais frequente em volume bruto, mas caro) e instrumento de medida (#6).
6. Fora da base: contextos exóticos (#8) e outliers (#9) — raros e sem
   padrão fixo de contexto.

## Sobre "quantas variações de prova tem"

Duas coisas diferentes, importante não confundir:

- **Cor do caderno** (azul/amarelo/cinza/rosa/verde, 4-6 por ano): é a
  **mesma prova**, questões só embaralhadas em ordem diferente pra dificultar
  cola. Baixar mais de uma cor do mesmo ano não traz nenhuma questão nova pra
  análise de padrão — é por isso que o projeto (e esta análise) usa só 1 cor
  por ano.
- **PPL** (aplicação/reaplicação pra quem perdeu a prova regular): é uma
  prova genuinamente diferente, mesma banca e mesma matriz de referência, mas
  com questões próprias. É isso que dobrou a amostra desta análise.

Não existem outras "variações de conteúdo" além dessas duas — a prova regular
(numa cor qualquer) e a PPL são as únicas fontes de questão nova por ano.

## Fontes

PDFs oficiais baixados de `download.inep.gov.br/enem/provas_e_gabaritos/`
(2020-2025) e `download.inep.gov.br/educacao_basica/enem/provas/2019/`.
Gabaritos da aplicação regular batem com
`core/gabaritos_reais/gabarito_<ano>_<cor>_CIENCIAS_OFICIAL.csv` já
existentes no projeto — PPL não tem gabarito carregado ainda. Enunciados
extraídos ficam em `core/scratch_enunciados_<ano>_<caderno>.txt` (gitignored,
scratch de revisão, não fonte de verdade).
