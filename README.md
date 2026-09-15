# ENEM GI — sistema pessoal de estudo pro ENEM

Ferramenta pessoal do Gabriel pra treinar questões reais do ENEM (2019–2025,
Matemática e Ciências da Natureza), com correção automática, repetição
espaçada (Leitner), resolução (texto) ligada a questão errada, análise de
prioridade de estudo por matéria, calendário de reta final e quadro de
objetivos. Prova em 08/11/2026.

## Rodar o app

```
cd core
python -m streamlit run cartao_resposta.py
```

Esse é **o app de verdade** — cartão-resposta, análise de desempenho,
triagem e admin, tudo em `core/`. Veja `core/CLAUDE.md` para a
arquitetura completa.

## ⚠️ Antes de rodar `reconstruir_base.py`

**Faça um backup primeiro** (ele já faz isso sozinho, mas uma cópia
extra sua não faz mal): botão "📦 Fazer backup agora" na tela Admin do
cartão-resposta, ou `python backup_db.py` de dentro de `core/`.

`reconstruir_base.py` não apaga mais `enem.db` — atualiza em cima do
que já existe, sem perder tentativa registrada nem correção manual de
triagem. Detalhes no aviso no topo do próprio arquivo.

## Rodar de qualquer lugar (celular, sem notebook ligado)

Ver `DEPLOY.md` — tem uma opção que já funciona agora (mesma wifi, zero
configuração) e uma de deploy de verdade, de graça (Streamlit Community
Cloud), com os passos que só você pode fazer (login em conta) separados
do que já está pronto no código.
