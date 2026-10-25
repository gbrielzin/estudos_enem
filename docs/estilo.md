# Estilo visual do ENEM GI (regras para a IA seguir)

Fonte da verdade dos valores: `mobile/src/constants/brand.ts` (paleta "1a — Grafite & Lima", do projeto de design) e
`mobile/src/constants/theme.ts` (espaçamentos). Este arquivo não inventa valor novo: resume o que já existe e fixa as
regras que faltavam (animação, contraste, o que evitar). Criado em 20/10/2026 a partir de vídeos de design com IA
(regras destiladas de apps bons, em vez de "faça bonito").

Quem pede mudança visual (Claude ou outra IA) lê este arquivo antes e usa só estes tokens.

## 1. Cores (tema escuro único)

| Papel | Token | Hex | Uso |
|---|---|---|---|
| Fundo | `bg` | `#0A0C10` | Fundo de toda tela |
| Cartão | `bgCard` | `#171B24` | Cartões, painéis |
| Borda | `borda` / `bordaForte` | `#232733` / `#2C3342` | Divisórias, contorno de cartão |
| Texto | `texto` | `#F2F4F7` | Texto principal |
| Texto secundário | `textoSuave` | `#7C8494` | Legendas, avisos |
| **Ação** | `verde` (lima) | `#6EE12B` | Botão principal, link, acerto |
| **Progresso** | `roxo` | `#7C5CFF` | Barra de progresso, trilha |
| **Recompensa** | `ouro` | `#FFC42E` | XP, streak, conquista |
| Erro / alerta | `laranja` / `erro` | `#FF6B4A` | Erro, aviso |
| Info / apoio | `azul`, `teal` | `#4FA6FF`, `#3ED9B0` | Destaques secundários |

Regra de ouro: **lima = ação, violeta = progresso, âmbar = recompensa.** Uma cor de destaque por tela; o resto é neutro.

## 2. Contraste (medido em 20/10/2026, mínimo AA: 4,5:1 texto normal)

| Combinação | Razão | Situação |
|---|---|---|
| `texto` sobre `bg` | 17,8 | ok |
| `verde` sobre `bg` | 11,6 | ok |
| `ouro` sobre `bg` | 12,3 | ok |
| `laranja` sobre `bg` | 7,0 | ok |
| `textoSuave` sobre `bg` | 5,2 | ok |
| `textoSuave` sobre `bgCard` | 4,6 | ok, no limite |
| `roxo` sobre `bg` | 4,5 | no limite: usar só para elementos grandes, não texto pequeno |
| `textoApagado` sobre `bg` | 3,3 | **reprova para texto**; só decoração ou texto grande |
| `textoMuted` sobre `bg` | 2,5 | **reprova**; nunca para texto que precisa ser lido |

Consequência: texto que a pessoa precisa ler usa `texto` ou `textoSuave`. O aviso de privacidade do perfil foi movido de
`textoApagado` para `textoSuave` por isso.

## 3. Tipografia

- Títulos e rótulos com peso: **Baloo 2** (`Fontes.titulo`, `tituloSemibold`).
- Texto corrido: **Nunito** (`Fontes.corpo`, `corpoNegrito`).
- Uma família por função, no máximo 3 a 4 tamanhos por tela. Texto corrido nunca abaixo de 12 px; avisos legais 12 a 13 px.

## 4. Espaçamento e forma

- Escala fixa (`Spacing`): 2, 4, 8, 16, 24, 32, 64. Não usar valor fora dela.
- Raio de cartão: `RaioCard` = 22. Botões com "degrau 3D" (sombra sólida embaixo), como já é no app.
- Largura máxima de conteúdo: 800 (`MaxContentWidth`).
- Mais espaço do que parece necessário; uma coisa grande por tela, o resto menor (hierarquia).

## 5. Movimento (regras novas, valores objetivos)

Eu (IA) não consigo julgar o ritmo olhando print, então o ritmo vai fixo aqui:

- Transição de interface (botão, cartão, troca de estado): **150 a 250 ms**, curva `ease-out`.
- Feedback de acerto/erro: até **400 ms**, uma vez, sem repetir.
- Nada pisca nem repete em loop numa tela de questão (a pessoa está lendo).
- Respeitar `prefers-reduced-motion` (reduzir ou desligar animação).
- Animar só `opacity` e `transform`.

## 6. O que evitar

- Gradiente roxo "padrão de IA", sombras pesadas e emoji como ícone principal.
- Mais de uma cor de destaque competindo.
- Dark patterns: contagem falsa de urgência, botão de sair escondido, culpa na notificação.
- Texto cinza claro sobre fundo escuro com contraste abaixo de 4,5.
- Promessa de nota ("suba X pontos") na interface.

## 7. Acessibilidade mínima

- Todo botão/ícone só com símbolo leva `accessibilityLabel`; link leva `accessibilityRole="link"`.
- Toda imagem de questão com texto alternativo curto.
- Tudo alcançável por teclado, com foco visível.

## 8. Referências (preencher)

Apps cujo espírito o Gabriel quer copiar (hierarquia e espaçamento, não as cores). Colocar prints em
`docs/materiais/referencias_visuais/` e uma linha aqui: app, o que copiar, o que não copiar.

- (vazio por enquanto)

## 9. Como pedir mudança visual à IA

1. Diga a tela e o estado (normal, erro, acerto, vazio, carregando).
2. Cite o token deste arquivo, não a cor ("botão `verde`", não "verde bonito").
3. Mande print do que não gostou + a referência, e diga o que copiar.
4. Peça captura antes/depois. A IA diz o que conferiu e o que só o seu olho julga (ritmo da animação, detalhe fino).
