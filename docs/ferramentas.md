# Ferramentas pouco conhecidas que resolvem problema de dado

Lista montada em 2026-09-27, a partir do que foi usado de verdade no projeto (✅) e do que vale conhecer pra estágio de dados. Critério: coisa que a maioria dos estudantes não conhece e que muda o que dá pra fazer. Para cada uma: o que é, quando usar, custo.

## 1. Onde achar dado (o que já existe pronto)

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Microdados do INEP** | Resultado individual (anonimizado) de todos os participantes do ENEM, Censo Escolar, SISU | Qualquer pergunta "quantas pessoas...", "em que competência..." | Grátis | ✅ nota de redação por competência de 3,46 mi pessoas (2025) |
| **Hugging Face Datasets** | Biblioteca pública de datasets pra IA (texto, imagem, áudio) | Antes de coletar do zero: alguém pode já ter montado | Grátis (alguns pedem login/aceite) | ✅ 63 notas 1000 do g1/O Globo com nota por competência |
| **Base dos Dados** (basedosdados.org) | Dados públicos brasileiros limpos e ligados entre si, consultáveis em SQL (BigQuery) | Cruzar ENEM com IBGE, renda, escola, município | Grátis até uma cota | — |
| **dados.gov.br** | Catálogo oficial de dados abertos do governo federal | Qualquer dado de órgão federal | Grátis | — |
| **Kaggle** | Datasets + notebooks de outras pessoas | Ver como alguém já analisou um dado parecido | Grátis | — |
| **Google Dataset Search** | Buscador só de datasets | "Existe dataset de X?" | Grátis | — |
| **OpenAlex** | Catálogo aberto de ~250 milhões de artigos científicos | Achar pesquisa com dado sobre um tema (ex.: método de estudo) | Grátis, com API | — |
| **GDELT** | Notícias do mundo inteiro catalogadas desde 2015, com tema e tom | Tendência de assunto (ex.: temas que viram redação) | Grátis | — |

## 2. Como coletar sem visitar site por site

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Common Crawl** | Cópia mensal de bilhões de páginas da web, com índice de URLs aberto | Achar páginas de um assunto sem crawler próprio | Grátis | ✅ 197 páginas de redação em 28 sites |
| **Wayback Machine** (web.archive.org) | Arquivo histórico da web desde os anos 90, com API (CDX) | Recuperar página que saiu do ar; ver como um site era numa data | Grátis | — |
| **Range request (HTTP)** | Baixar só um pedaço de um arquivo remoto | Ler o índice de um ZIP gigante sem baixar tudo | Grátis | ✅ `rz.py`: ler 2 GB do INEP em fluxo |
| **pymupdf** | Extrair texto/imagem de PDF em Python | Qualquer PDF oficial (provas, cartilhas) | Grátis | ✅ cartilhas e provas do INEP |
| **Tesseract (OCR)** | Ler texto de imagem | Foto de redação, espelho, documento escaneado | Grátis | — |

Regra que acompanha todas: só página pública, respeitar bloqueio e termo de uso, não usar conta de terceiros. Coleta que contorna bloqueio é o que derruba a credibilidade de um projeto de dados.

## 3. Como processar dado grande num PC comum

| Ferramenta | O que é | Quando usar | Custo |
|---|---|---|---|
| **DuckDB** | Banco analítico que roda SQL direto em CSV/Parquet, inclusive remoto | Arquivo grande demais pro Excel/pandas; consultar Parquet na internet sem baixar | Grátis |
| **Parquet** | Formato de tabela comprimido e colunar | Guardar dataset grande (10x menor que CSV e muito mais rápido) | Grátis |
| **Polars** | Alternativa ao pandas, muito mais rápida | Tabela com milhões de linhas | Grátis |
| **SQLite + FTS5** | Busca de texto completo dentro do SQLite | "Achar todas as redações que citam Bauman" em milissegundos | Grátis |

## 4. IA aplicada a dado

| Ferramenta | O que é | Quando usar |
|---|---|---|
| **Extração estruturada com LLM** | Pedir pra IA transformar texto livre em campos (ex.: dica, competência, fonte) | Texto que regra de código não resolve (o banco de dicas) |
| **Embeddings + busca semântica** | Representar texto como vetor pra achar "parecidos" mesmo com palavras diferentes | Agrupar dicas iguais escritas de jeitos diferentes; achar redação parecida com a sua |
| **Agentes em loop / rotinas agendadas** | IA repetindo uma tarefa em intervalo ou na nuvem | Fase de descoberta de fontes (o loop de hoje); coleta mensal |

## 5. Engenharia (o que separa script de projeto)

| Ferramenta | O que é | No projeto |
|---|---|---|
| **Pipeline reprodutível** | Script que refaz o dado do zero com um comando | ✅ `coleta_redacoes.py` |
| **Teste com dado sintético** | Testar o extrator sem pôr dado de terceiro no repo | ✅ `test_coleta_redacoes.py` |
| **Cartão de dados (data card)** | Documento de fontes, licença e limites | ✅ `docs/redacao_pesquisa/fontes.md` |
| **GitHub Actions** | Rodar teste e coleta automática na nuvem | ✅ CI do projeto |
| **ADR** | Registro de decisão de arquitetura | ✅ `adr/` |

## Como usar isso numa entrevista de estágio

Não é listar ferramenta; é contar o problema e por que a ferramenta resolveu. Exemplo pronto: *"Queria saber em que competência quem tira 900+ perde ponto. Os microdados do INEP têm 2 GB por ano; em vez de baixar, li o ZIP em fluxo com range request e guardei só um resumo de 3 KB. Resultado: 96% de quem tira 960-980 não faz 200 em gramática."*

## 6. Skills e plugins pro Claude Code (avaliado em 2026-10-10)

Skill de terceiro é texto de instrução que o Claude passa a seguir: ler o SKILL.md antes de instalar e instalar no projeto (`.claude/skills/`), não no global.

| Ferramenta | O que é | Veredito pro ENEM GI |
|---|---|---|
| **playwright-cli** (Microsoft) | Playwright por linha de comando; grava o estado da página em arquivo em vez de jogar na conversa. `npm install -g @playwright/cli@latest` | **Instalar.** Gasta menos token que o Playwright MCP (já configurado); serve pra conferir `docs/materiais/*.html` e o Expo web |
| **web-design-guidelines** (vercel-labs) | Revisão de UI contra as Web Interface Guidelines da Vercel (acessibilidade, foco, tipografia, movimento) | **Instalar.** Leve, só roda quando pede; regras são de web (cabem nos materiais HTML e no Expo web, menos nas telas nativas) |
| **taste-skill** (Leonxlnx) | Gera UI "sem cara de IA" com 3 controles (variação, movimento, densidade); pensado pra landing page web | **Depois.** Útil numa landing page ou portfólio; o app já tem identidade (Baloo/Nunito, `enem_theme.py`) |
| **awesome-design-md** | Coleção de DESIGN.md imitando marcas (Stripe, Notion, Apple...) | **Pular.** Melhor escrever o DESIGN.md do próprio ENEM GI a partir do tema atual |
| **image-to-code / screenshot-to-code** | Print → código; a do taste-skill gera mockup em imagem antes | **Pular.** Print → código o Claude já faz lendo a imagem |

Fontes: [playwright-cli README](https://glama.ai/mcp/servers/@microsoft/playwright-mcp/blob/cd9819d0e885bbfed879b7316a088ab369a2a21f/packages/playwright-cli/README.md), [web-design-guidelines](https://claudemarketplaces.com/skills/vercel-labs/claude-skills/web-design-guidelines), [taste-skill](https://claudemarketplaces.com/skills/leonxlnx/taste-skill/design-taste-frontend), [awesome-design-md](https://www.mindstudio.ai/blog/awesome-design-md-github-claude-code-brand-systems).

## 7. Estilos visuais pra pedir ao Claude (reel @millee.md, 2026-10-10)

Não é plugin: é vocabulário. Basta pedir "faz em estilo X". Lista completa: particles, liquid morph, holographic, neon glow, wireframe 3D, glassmorphism, kinetic type, isometric, clay 3D, ASCII art, gradient mesh, comic book, split-flap, retro VHS, halftone, Bauhaus, pixel art, blueprint, art deco, neo-brutalism.

| Estilo | Onde usar |
|---|---|
| **Blueprint** (fundo azul, traço branco de planta técnica) | Cadernos de física: circuito, óptica, vetores, plano inclinado |
| **Isometric** (3D sem perspectiva) | Geometria espacial, sólidos, moléculas |
| **Kinetic type** (texto que entra em sequência) | Passo a passo de resolução ("lê o comando → acha o dado → aplica") |
| **Split-flap** (painel de aeroporto) | Contagem regressiva pro ENEM, placar de acertos |
| **Neo-brutalism / Comic book** | Carrossel do ENEM Pipoco, thumbnails, posts de LinkedIn |

Regra: em página de estudo, movimento só quando explica algo (corrente circulando, etapa aparecendo); efeito decorativo atrapalha a leitura.

## 8. Checklist "cara de vibecoded" (reel @millee.md, 2026-10-10)

Sinais de app feito por IA sem revisão: gradiente roxo→azul; texto de título em gradiente; emoji nos títulos; fonte Inter em tudo; card com borda colorida; card de vidro (glassmorphism); modo escuro com pouco contraste; 3 caixinhas de ícone lado a lado; selo acima do título; ícones Lucide em tudo; shadcn sem personalizar; fade-in ao rolar; brilho seguindo o cursor; botão que só esmaece no hover; espaçamento inconsistente; travessão (—) em todo texto; texto de marketing genérico; detalhe em serifa itálica; par Space Grotesk + Instrument Serif; granulado por cima de gradiente.

Uso: rodar como revisão antes de PR de UI ou de publicar material ("confere essa tela contra o checklist §8").

**Auditoria do app em 10/10/2026 (mobile/src):** passa na maioria — fonte própria (Baloo 2 + Nunito via `Fontes`), sem Lucide, sem shadcn, sem gradiente roxo, sem glass. Pontos a olhar:
- Emoji como ícone em texto de UI (~19: ⚠️ nos avisos de erro, 💡, 🧠, 🎓, ✅/❌ no resultado) → trocar os repetidos por ícone do `@expo/vector-icons` com a cor do tema.
- ~10 travessões (—) em textos.
- `components/animated-icon*.tsx` é sobra do template do Expo (gradiente azul `#3C9FFE`, usado em `_layout.tsx`) → substituir pelo Pipoco ou remover.

## 9. Pesquisa de concorrência por anúncio (2026-10-10)

| Ferramenta | O que é | Quando usar |
|---|---|---|
| **Biblioteca de Anúncios da Meta** (facebook.com/ads/library) | Mostra todos os anúncios ativos de qualquer página no Facebook/Instagram, com data de início e variações | Ver o que ProEnem, Bernoulli, Kuadro etc. estão testando, há quanto tempo um anúncio roda (rodando há semanas = está dando resultado) |
| **Parâmetros UTM do link** | O trecho depois do `?` (utm_campaign, utm_content, utm_term) | Ler a campanha: público, teste A/B, objetivo (lead ou venda) |
| **Arquivo de referências** ("swipe file") | Lista acumulada dos anúncios que aparecem, com o padrão de cada um | Já começou em docs/ideias_melhorias.md (Medly, Kuadro, PraticAI, UniBF, ProEnem, Anti-Atraso) |

## 10. Prospecção B2B de escolas e CRM (2026-10-23)

Achado em busca no GitHub + teste real. A lista de escolas vem do INEP; ferramenta de fora só completa contato. Chave única de cada escola: **Código INEP** (`CO_ENTIDADE`); Google `place_id` e CNPJ entram como colunas da mesma linha, nunca como linha nova.

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Censo Escolar + ENEM (microdados INEP)** | Toda escola ativa (nome, telefone, matrículas) + presença e nota por escola | Decidir *quais* escolas abordar | Grátis | ✅ `Desktop/dados_inep/ranking_prospeccao.py`: 8.901 privadas com médio → 5.189 alvo → 1.823 quentes; planilha `prospeccao_escolas.xlsx` |
| **google-maps-scraper-kit** (Mahanaicoach, 1,7 mil★, MIT) | Wrapper do `gosom/google-maps-scraper` (6,8 mil★) em Docker: site, e-mail, Instagram, avaliação | Completar contato de escola já escolhida, buscando pelo nome; lotes de 30-50/dia | Grátis; risco de bloqueio do IP pelo Google | ✅ teste Vitória: 32 escolas, 31 com telefone, 16 com e-mail. Trocar `lang` para pt-BR; vem creche/faculdade no meio |
| **omkarcloud/google-maps-scraper** (3,8 mil★) | Alternativa ao gosom | Se o gosom quebrar | Grátis | — |
| **Dados abertos do CNPJ (Receita Federal)** | Cadastro de toda empresa, com CNAE, e-mail e telefone | E-mail de escola sem site; CNAE 8520-1/00 = ensino médio | Grátis | ✅ `Desktop/dados_inep/cnpj_escolas.py` + `cruzar_cnpj.py` (out/2026): 86.693 escolas ativas no CNPJ; 2.952 das 5.189 alvo ligadas com confiança alta, 1.621 com e-mail que não é de contador |
| **rictom/cnpj-sqlite** (240★, MIT) | Carrega a base do CNPJ num SQLite local | Consultar a base inteira offline | Grátis | — |
| **cuducos/minha-receita** (1,6 mil★) | API própria de consulta de CNPJ | Consultar CNPJ por API dentro do app | Grátis | — |
| **Twenty** (twentyhq/twenty, 59 mil★) | CRM open source estilo Salesforce, Docker, API REST/GraphQL | Quando o funil passar de ~50 escolas ativas | Grátis self-host | — |
| Krayin, EspoCRM, SuiteCRM | CRMs open source em PHP | Não recomendado: outra linguagem pra manter | Grátis | — |
| **Excel (aba Funil)** | Status por escola com lista fixa + contagem automática | Até as primeiras ~50 escolas contatadas | Grátis | ✅ |

Cuidado: e-mail do CNPJ às vezes é o do contador; telefone do Censo 2024 pode estar velho. Dado de sócio (nome de pessoa) é dado pessoal na LGPD: usar só o contato institucional.

## 11. Acesso de agente a outras plataformas (2026-10-23)

| Ferramenta | O que é | Quando usar | Custo | No projeto |
|---|---|---|---|---|
| **Agent Reach** (Panniantong/Agent-Reach, 101 mil★, MIT) | CLI que dá ao agente leitura de YouTube (legenda/transcrição), LinkedIn (vagas), Reddit, X, Instagram, GitHub etc. Só lê, nunca posta | Depois de 15/11, só canais **sem login**: vagas do LinkedIn (busca de emprego) e legendas do YouTube (pesquisa de redação, fluxo vídeo + transcrição) | Grátis; transcrição de áudio pede chave Groq/OpenAI | ✅ testado 24/10 (v1.6.0, sem `setup`, sem login): **LinkedIn funciona** (busca pública via Exa, ~1-2 s, traz descrição + nº de candidaturas; filtro de cidade fraco). **YouTube falhou** (429 do yt-dlp nas 2 tentativas): seguir com o transcritor próprio |

Cuidados: canais com login copiam a sessão do Chrome (conta principal) e a plataforma pode bloquear conta usada em automação: usar conta secundária, nunca a @brazilian.dev. A instalação oficial é o agente seguir um `install.md` remoto: ler o arquivo inteiro antes. O pacote `agent-reach` do PyPI **não** é esse projeto. Instagram/Facebook são experimentais: não usar pra prospecção de escolas (CNPJ + Google Maps já cobrem, seção 10).
