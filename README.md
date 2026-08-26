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
com um modo que `core/coletar_videos.py` não reimplementou (busca por
palavra-chave em vários canais — minerava vídeo cuja descrição citasse
"nível de dificuldade", conceito que não existe mais no banco atual) —
mantido só por isso. Os outros dois modos que ele tinha (lote e junção)
já foram portados pra `core/coletar_videos.py`, gravando direto no
banco. `app.py` não é o produto principal.

## ⚠️ Antes de rodar `reconstruir_base.py`

**Faça um backup primeiro** (ele já faz isso sozinho, mas uma cópia
extra sua não faz mal): botão "📦 Fazer backup agora" na tela Admin do
cartão-resposta, ou `python backup_db.py` de dentro de `core/`.

`reconstruir_base.py` não apaga mais `enem.db` — atualiza em cima do
que já existe, sem perder vídeo coletado, tentativa registrada, ou
matéria preenchida via título de vídeo. Detalhes no aviso no topo do
próprio arquivo.

## Configuração

Crie um `.env` na raiz com:

```
YOUTUBE_API_KEY=sua_chave_aqui
```

## Prompt pra IA do YouTube (coleta em lote)

Ao colar um vídeo-resumo no YouTube, peça nesse formato exato pra
depois colar na seção "Colar um vídeo-resumo" do coletor (dentro de
"🔗 Coletar vídeos"):

```
Liste todas as questões faladas neste vídeo no formato exato:
Questão;Matéria

Uma linha por questão, sem texto explicativo antes ou depois, sem
numeração extra, sem timestamps. Exemplo do formato esperado:
Questão 137;Probabilidade
Questão 138;Estatística
```
