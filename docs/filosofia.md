# 🗺️ Manifesto de Arquitetura da Trilha: O Algoritmo de Alocação de Tempo por ROI

Este documento estabelece as diretrizes técnicas e decisões de negócios para a ordenação e priorização de conteúdos no aplicativo. O objetivo central é responder à pergunta: **"Se a prova fosse amanhã, o que daria mais pontos para o aluno no menor tempo possível?"**

---

## 🎯 1. Os Três Pilares da Mentalidade ROI

Ao contrário dos cursinhos tradicionais que vendem cronogramas lineares de 1 ano, nossa esteira de progresso é calculada dinamicamente cruzando três variáveis humanas e matemáticas:

1. **Peso da Matéria (Incidência Real Inep):** Assuntos com maior volume histórico de questões no ENEM vêm primeiro. Perder tempo com matérias de baixa incidência faltando 40 dias é desperdício de energia.
2. **Cadeia de Pré-requisitos (Sequenciamento Curricular):** Se a matéria complexa B necessita obrigatoriamente da base da matéria A, a matéria A atua como trava de progressão (*Gating*). O aluno acumula blocos simples antes de subir o degrau.
3. **Curva de Rendimento Decrescente (Teto de ROI por Esforço):** Subir do nível fácil/médio para o difícil em uma mesma matéria exige um esforço de tempo brutal para garantir apenas 1 questão na prova. O sistema força a **Interrupção de Fluxo**: quando o ROI de uma matéria cai, o usuário é transferido para a fase inicial de outra matéria para colher os pontos fáceis e médios pendentes.

---

## 📊 2. Tabela Oficial de Pesos: Ecologia (O Coração de Natureza)

Para o MVP, a árvore do Duolingo dividirá o ecossistema de Ecologia em **6 Fases Estritas**, organizadas por volume de manobra (20 cenários clones por fase, totalizando 120 questões):

| Fase | Título Técnico | Peso de Incidência | Nível de Prioridade na Trilha |
| :---: | :--- | :---: | :--- |
| **F4** | Poluição Atmosférica (Chuva Ácida, Efeito Estufa, Ozônio/CFC) | **28%** | **Máxima (O topo do ROI)** |
| **F3** | Ciclos Biogeoquímicos (Nitrogênio/Carbono) e Pirâmides | **22%** | **Altíssima (Muito recorrente)** |
| **F1** | Cadeias Alimentares e Fluxo de Energia | **18%** | **Alta (Base obrigatória / Pré-requisito)** |
| **F2** | Relações Ecológicas (Harmônicas/Desarmônicas) e Gráficos | **14%** | **Média-Alta (Padrões clones fortes)** |
| **F5** | Saneamento Básico, Lixo e Resíduos (ETA, ETE, Metano) | **10%** | **Média (Interdisciplinar com Química)** |
| **F6** | Impactos Urbanos (Ilhas de Calor, Chuvas de Verão, Albedo) | **8%** | **Estratégica (Pontos rápidos de garantir)** |

---

## 🧠 3. Engenharia de Padrões Clones (O Fator Humano contra a IA Rasia)

Nosso diferencial competitivo contra aplicativos gerados por IAs genéricas e limitadas é a **Calibragem Humana de Nível Fácil e Médio**. 
* O aplicativo **não foca no nível difícil**, pois o teto de ganho de nota na TRI se consolida ao gabaritar as fáceis e médias.
* A esteira de questões é construída trocando apenas a "roupa" (o cenário prático) e mantendo a mecânica idêntica. Ao fazer o **Resgate Ativo com Caderno**, o estudante automatiza o olho para ignorar o texto gigante do Inep e ir direto no gatilho físico/biológico.

---

## 🛠️ 4. Fluxo de Execução do Algoritmo de Transição (A Trilha Intercalada)

O código rodando no `localhost:8502` deve obedecer a seguinte ordem de destravamento de nós, garantindo que o usuário mude de matéria assim que o ROI da atual bater no teto:

```text
[Nó 1: Ecologia F1] ➔ [Nó 2: Óptica F1] ➔ [Nó 3: Ecologia F4 (28%)] ➔ [Nó 4: Cinemática F1] ➔ [Nó 5: Ecologia F3] ➔ [Nó 6: Eletrodinâmica F1 (SVG)]
```

Se o estudante tentar avançar linearmente para uma fase de baixo ROI (ex: Saneamento) antes de garantir a base de uma matéria de alta incidência (ex: Cinemática), o sistema dispara o **Bloqueio Informativo do Pipoco**, redirecionando o usuário para a pista mais lucrativa de pontos.
