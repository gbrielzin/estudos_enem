# ENEM GI — sistema pessoal de estudo pro ENEM

Ferramenta pessoal do Gabriel pra treinar questões reais do ENEM (2019–2025,
Matemática e Ciências da Natureza), com correção automática, repetição
espaçada (Leitner), vídeo-resolução ligado a cada questão errada e
análise de prioridade de estudo por matéria.

## Rodar o app

```
cd core
python -m streamlit run cartao_resposta.py
```

Esse é **o app de verdade** — cartão-resposta, análise de desempenho,
coleta de vídeo, triagem e admin, tudo em `core/`. Veja `core/CLAUDE.md`
para a arquitetura completa.

Há também um coletor legado na raiz (`python -m streamlit run app.py`)
com três modos que `core/coletar_videos.py` ainda não reimplementou
(busca por palavra-chave em vários canais, entrada em lote de
vídeo-resumo, e junção link-real + nível-do-resumo) — mantido só por
isso. Não é o produto principal.

## ⚠️ Antes de rodar `reconstruir_base.py`

**Faça um backup primeiro:** botão "📦 Fazer backup agora" na tela Admin
do cartão-resposta, ou `python backup_db.py` de dentro de `core/`.

`reconstruir_base.py` apaga `enem.db` e reconstrói do zero só a partir
dos CSVs de gabarito — ele **não** sabe recriar vídeo coletado depois do
último snapshot, tentativa registrada fora do backfill hardcoded de
2019, nem matéria que só foi preenchida via título de vídeo. Detalhes
completos no aviso no topo do próprio arquivo.

## Configuração

Crie um `.env` na raiz com:

```
YOUTUBE_API_KEY=sua_chave_aqui
```

## Prompt pra IA do YouTube (coleta em lote)

Ao colar um vídeo-resumo de dificuldade no YouTube, peça nesse formato
exato pra depois colar na aba "Lote" do coletor:

```
Liste todas as questões faladas neste vídeo no formato exato:
Questão;Matéria;Nível

Uma linha por questão, sem texto explicativo antes ou depois, sem
numeração extra, sem timestamps. Exemplo do formato esperado:
Questão 137;Probabilidade;Difícil
Questão 138;Estatística;Fácil
```
