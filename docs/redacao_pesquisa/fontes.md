# Banco de redações nota alta: fontes e regras

Cartão de dados do banco montado por `core/coleta_redacoes.py`. O banco
(`docs/redacao_pesquisa/banco_1000/`) e as cartilhas baixadas
(`docs/redacao_pesquisa/cartilhas/`) ficam **fora do git**: são textos de
terceiros, guardados só pra análise local. No git vão o código, este arquivo
e as conclusões em [padroes_1000.md](padroes_1000.md), sem copiar redação.

## Fontes

| Fonte | Nível | Edições do ENEM | O que tem | Pode guardar o texto localmente? |
|---|---|---|---|---|
| Cartilhas do Participante do INEP (2019, 2020, 2022, 2024, 2025) | oficial | 2018, 2019, 2021, 2023, 2024 | Texto + comentário do INEP | Sim (publicação pública do governo) |
| Cartilha do INEP 2023 | oficial | 2022 | — | Não extraída: fonte embaralhada no PDF |
| Cartilha Redação a Mil 1.0 a 7.0 (Lucas Felpi, com análise do Poliedro) — https://www.lucasfelpi.com.br/redamil | compilação com espelho oficial | 2018-2024 | Texto + foto do espelho oficial da nota de cada aluno | Sim, só local; "todos os direitos reservados": não republicar |
| E-book "Rumo à nota mil" (IFMG, 2023) | instituto federal | 2020, 2021 | Duas 980 e uma 1000 com nota por competência | **Não**: o e-book proíbe armazenamento. Só metadados (nome, ano, tema, nota por competência) |
| Estratégia Vestibulares, coRedação, Quero Bolsa, Imaginie | portal/cursinho | 2013-2025 | Esqueleto feito por nós (abertura, 2 causas, repertórios, proposta) + link | Só o esqueleto (análise nossa), nunca o texto |
| Reportagens (Terra, CNN Brasil, INEP, secretarias, IFs) | imprensa / relato | 2021-2025 | Relatos do que o aluno fez (tabela `relatos`) | Só o resumo + link |

## Descoberta de páginas: Common Crawl

`core/commoncrawl_redacoes.py` consulta o índice aberto do Common Crawl (varredura mensal da web) domínio por domínio, com filtro de URL de redação nota alta, em 4 coletas (2025-51 a 2026-34), e grava só a lista de URLs em `banco_1000/commoncrawl_urls.csv`. Rodada de 2026-09-27: 28 domínios, **197 URLs**, entre elas as páginas por ano do coRedação (2014-2025, que trouxeram as de 2014-2016) e uma página do g1 com 100 notas mil. O índice mais recente (2026-39) respondia 502/504 sob carga; o script tenta de novo e segue.

**g1: não usado.** A ferramenta de leitura de páginas é bloqueada pelo g1; não contornamos o bloqueio por outro caminho.

Não usadas: Reddit, YouTube, X e Instagram (não abrem pelas ferramentas; o
Instagram exige login). Nada de conta comprada, VPN ou contornar bloqueio.

## Cuidado com a nota

- **ENEM 2025**: o INEP informou 10 notas mil, mas a união dos portais dá 15
  nomes. As de portal estão marcadas no `comentario_inep` como "nota alegada".
- Duplicatas entre fontes: mesma edição + dois primeiros nomes. Fica a fonte
  mais confiável (INEP > IFMG > Redação a Mil > portal).

## Como rodar

Pré-requisito: os PDFs em `docs/redacao_pesquisa/cartilhas/` (cartilhas do
INEP) e `docs/redacao_pesquisa/banco_1000/redamil/redamil_v1.pdf` ...
`redamil_v7.pdf`, mais os CSVs feitos à mão em `banco_1000/manual/`
(`esqueletos.csv`, `relatos.csv`, `aberturas_cartilhas.csv`).

```
cd core
python coleta_redacoes.py ../docs/redacao_pesquisa/banco_1000
```

Reconstrói `redacoes_1000.db` do zero e imprime contagem por edição,
causas e repertórios mais citados.

## Adicionar uma edição nova (ex.: janeiro, quando saem as notas 1000)

1. Baixar a cartilha nova do INEP pra `cartilhas/` (e o .txt, se a fonte do PDF estiver ok).
2. Se o layout for igual ao de uma cartilha anterior, só acrescentar o ano em `CARTILHAS_INEP`; se mudar, um extrator novo + teste com texto sintético em `test_coleta_redacoes.py`.
3. Redação a Mil nova: baixar `redamil_vN.pdf` e acrescentar em `EDICOES_REDAMIL`.
4. Rodar o comando acima e atualizar os números de `padroes_1000.md`.
