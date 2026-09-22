# Plano: ampliar o banco de estudo com provas antigas e PPL

Status: **plano, nada foi escrito no `enem.db`**. Data: 2026-09-21.

## Situação hoje (medida)

| Base | Cobertura |
|---|---|
| `core/enem.db` (banco de estudo) | Natureza e Matemática, **2019 a 2025**, sem PPL |
| `core/corpus_analise.db` (análises) | 1 prova regular por ano, **2009 a 2025**, sem PPL |

Natureza no corpus, 2009 a 2018: **45 questões por ano, todas com gabarito** (contagem por `indice`, ver `docs/padroes_de_prova_corpus.md` §0.1 para o layout de cada ano). Entre 16 e 25 por ano têm `tem_imagem = 1`.

As análises de padrão de prova usaram o corpus, não o banco de estudo. Por isso "estar nas análises" não significa "estar no banco".

## Restrições do pipeline atual (de `core/CLAUDE.md`)

1. Cada `(ano, caderno, grande_area)` é um simulado independente, com `id_questao` próprio.
2. `extrair_enunciados_pdf.py`, `extrair_figuras_pdf.py` e `importar_enem_dev.py` **só preenchem** questões que já existem. Primeiro entra o gabarito (`carregar_gabarito_csv` / `extrair_gabarito_pdf.py`), depois o texto.
3. `importar_enem_dev.py` cobre 2009 a 2023 e confere o caderno azul antes de gravar. Para PPL, **não confirmado** que a API tenha os dados.

## Decisão (trade-off)

Fazer em duas fases, da mais barata e segura para a mais cara.

### Fase 1: provas regulares 2010 a 2018, Natureza (fonte local, sem rede)
- Fonte: `corpus_analise.db` (texto, alternativas e gabarito já validados contra a estrutura do corpus).
- Custo: baixo, sem download. Ganho: 9 provas x 45 = **405 questões**.
- 2009 fica de fora por enquanto: matriz diferente (mudou em 2009), fica numa segunda rodada.
- **Portão de validação antes de gravar:** (a) comparar o gabarito do corpus com o oficial nos anos em que os dois existem (2019 a 2023) para medir a taxa de divergência; (b) conferir uma amostra de cada ano antigo contra o PDF oficial do INEP. Se a divergência passar de um limite acordado, parar.
- Questões com imagem: entram **marcadas** (⚠️, como no beta de "Prova com enunciado"), e ficam fora de simulados até a figura ser recuperada.

### Fase 2: PPL (fonte externa)
- PPL = Pessoas Privadas de Liberdade. No INEP, os arquivos se chamam `..._reaplicacao_PPL_...`.
- Precisa dos PDFs oficiais do INEP (prova e gabarito). Depois usar os scripts existentes: gabarito primeiro, texto e figuras depois.
- Caderno próprio (`ppl`), para nunca misturar com a prova regular do mesmo ano.
- **Nada é gravado no banco** até a validação; os PDFs ficam em `core/inep_ppl/` (ignorado pelo git).

**Status do download (2026-09-21), confirmado abrindo cada PDF:**

Correção importante: os arquivos `..._reaplicacao_PPL_...` do INEP são, em quase todos os casos, a **2ª aplicação (reaplicação)**, e não a prova de Pessoas Privadas de Liberdade. Lendo as 4 primeiras páginas de cada prova: 2015, 2017 a 2019 e 2021 a 2024 dizem "2ª aplicação"; 2016 diz "3ª aplicação"; só 2020 (cadernos 5 e 6) cita "PPL" no texto. **Não dá para separar PPL de reaplicação pelo nome do arquivo**, e não confirmei se o INEP publicou o PPL como prova própria em cada ano.

| Ano | Provas (PV) | Gabaritos (GB) | Aplicação declarada |
|---|---|---|---|
| 2015 | 4 cadernos (9 a 12), Natureza no dia 1 | 4 baixados (cadernos 1 a 4: azul, amarelo, branco, rosa), **rotulados 2ª aplicação**; **mapeamento entre CD 9 a 12 e cadernos 1 a 4 ainda não conferido** | 2ª aplicação |
| 2016 | 4 cadernos (9 a 12) | 4 (branco 9 a 12) | 3ª aplicação |
| 2017 | cadernos 5 a 8, 11, 17 a 20 | 7 (cadernos 5, 6, 8, 17 a 20); **faltam 7 e 11** | 2ª aplicação |
| 2018 | cadernos 17 a 20 | 4 (17 a 20) | 2ª aplicação |
| 2019 | cadernos 5 a 9 | 4 (5 a 8); **falta 9** | 2ª aplicação |
| 2020 a 2024 | 4 cadernos por ano | 4 por ano | 2ª aplicação (2020 cad. 5/6 citam PPL) |
| 2025 | não encontrado | não encontrado | possivelmente ainda não publicado |

- Total: 66 PDFs de prova (221 MB) em `core/inep_ppl/` e 19 gabaritos antigos em `core/inep_ppl/gabaritos_antigos/`. Tudo ignorado pelo git.
- Padrões de nome dos gabaritos antigos: 2016 `ppl/2016/gabarito_caderno_branco_<n>_2016.pdf`; 2017 `ppl/2017/gabaritos/GAB_ENEM_2017_2_APL_DIA_2_<Cor>_cad_<n>.pdf`; 2018 `gabaritos/2018/GAB_ENEM_2018_DIA_2_P2_<Cor>.pdf`; 2019 `ppl/2019/gabaritos/gabarito_2_dia_caderno_<n>_<cor>_2_aplicacao.pdf`.
- Cadernos extras (2016 CD10 com 64 páginas; 2017 CD11; 2019 CD9 laranja) parecem versões especiais. **Não confirmado.**
- Natureza está no dia 1 em 2015 e 2016 e no dia 2 de 2017 em diante.
- Uma busca web descreveu PPL de forma errada ("pessoas livres"); PPL = Pessoas Privadas de Liberdade.

## Salvaguardas (valem para as duas fases)

1. Backup do `enem.db` antes de qualquer gravação (`core/backup_db.py`).
2. Rodar primeiro em modo de leitura (sem `--aplicar`) e revisar a saída.
3. `origem` distinta nas linhas novas, para as análises poderem incluir ou excluir esse bloco.
4. `topico` fica vazio: a classificação por tópico é um passo separado (a coluna está vazia nas questões de biologia hoje).
5. Antes de importar, avaliar o efeito em `prioridade_de_estudo()`: centenas de questões novas mudam recorrência e ranking.
6. Nenhum número novo sem consulta rodada; toda aproximação registra o limite.

## Riscos abertos

- O gabarito do corpus (fonte `enem.dev`) pode divergir do oficial em casos de questão anulada (já houve um em 2020).
- A ordem das questões do corpus pode não bater com o caderno azul em alguns anos (já observado em 2023).
- Sem figura, cerca de 40% das questões ficam incompletas.
- O PPL depende de fonte que ainda não foi localizada nem baixada.

## Próximos passos

1. Rodar o portão de validação (a) da Fase 1 (só leitura) e registrar a taxa de divergência.
2. Decidir o limite aceitável com base nesse número.
3. Só então gravar, com backup.
4. Localizar os **gabaritos do PPL de 2015 a 2019** (nome antigo, fora do padrão `GB_reaplicacao_PPL`) e confirmar se o PPL de 2025 já saiu.
5. Identificar quais dos cadernos extras são versões especiais e descartá-las.
6. Repetir o processo da Fase 1 (só leitura, validação, backup, gravação) na Fase 2.
