---
name: conteudo
description: Transforma um PR mergeado do ENEM GI em roteiro de vídeo curto (TikTok/Reels/Shorts) e post de LinkedIn no formato build in public do Gabriel — gancho, problema real, o erro/pergunta dele, solução, número, aprendizado. Use quando ele pedir /conteudo <n>, "vira vídeo", "post do PR", ou logo depois de um merge.
---

# /conteudo <número do PR>

Série "aprendendo a revisar o código do meu próprio app" (ideia dele, 2026-09-26). O que vende é o processo real, com o erro dele à mostra.

## 0. Modelo certo

Antes de tudo, siga o passo 0 de `docs/modelo_por_tarefa.md` com a linha de roteiro e post: se a sessão estiver no modelo errado, avise em uma linha e espere ele trocar com `/model` ou responder "segue". Se estiver certo, não diga nada.

## 1. Juntar o material (só leitura)

- `gh pr view <n> --json title,body,mergedAt,additions,deletions,files` — confirme que está **mergeado**; se não, pare (só publica o que está no master).
- `gh api repos/{owner}/{repo}/pulls/<n>/comments` — as perguntas dele são o melhor gancho.
- Comentários de achado do `/code-review`, números da descrição (testes, contagens, antes/depois).
- Contexto do projeto: `docs/linkedin_projeto.md` seção 7 (roteiros já feitos, pra não repetir).

## 2. Escolher o ângulo (um só)

Ordem de preferência: (1) pergunta dele que achou algo real; (2) bug achado antes do merge; (3) número surpreendente; (4) conceito explicado em 60 s. Nome técnico só depois da ideia.

## 3. Entregar

**Roteiro de vídeo (60-90 s)**

| Tempo | Parte | Fala | Tela |
|---|---|---|---|
| 0-3 s | Gancho | frase que para o dedo (ex.: "Minha API estava aberta pra qualquer um da minha wifi.") | ele falando |
| 3-20 s | Problema | o que estava errado, em português simples | print/diff |
| 20-45 s | O que ele perguntou/errou | a dúvida real, sem vergonha — é o que torna verdadeiro | comentário do PR no celular |
| 45-70 s | Solução + número | o que mudou e o resultado medido | teste passando / antes-depois |
| 70-90 s | Aprendizado | 1 frase + teaser do próximo | ele |

**Post de LinkedIn** (até ~1.300 caracteres): 1ª linha = gancho; 3-5 parágrafos curtos; um número concreto; o que ele aprendeu; link do repo só se estiver público; no máximo 3 hashtags.

## 4. Checklist antes de entregar (obrigatório)

- Nada de token, `.env`, senha, e-mail, nota pessoal que ele não quis mostrar, nome de aluno de terceiros.
- Nada de texto de redação de terceiros (banco_1000) na tela.
- Afirmação técnica conferida no diff/PR (sem inventar número).
- Tom: estudante construindo e aprendendo, não "especialista".

## 5. Guardar

Acrescente o roteiro e o post em `docs/linkedin_projeto.md` (seção 7, arquivo pessoal no .gitignore), com o número do PR e a data. Não commite esse arquivo.
