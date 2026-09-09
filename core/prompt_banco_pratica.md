# Banco de Prática — prompt para OUTRA IA (gerar questões formatadas)

Use esse prompt numa IA separada (Gemini, ChatGPT, outro chat de Claude) quando quiser treinar
um assunto específico que você já identificou como fraco (ex: Óptica) até fixar de verdade. O
objetivo é sair de lá com o texto já no formato exato que o Admin → "🧠 Banco de prática" espera
pra colar e importar de uma vez — sem precisar reformatar nada na mão.

⚠️ **Diferença importante em relação ao prompt de Extração de Gabarito**: ali o gabarito vem de
um PDF oficial do INEP, então é confiável por definição. Aqui o gabarito é a própria IA
resolvendo a questão que ela mesma inventou — ela pode errar a conta ou a alternativa certa
sem perceber. Confira a resolução de cada questão antes de importar, principalmente nas que
"pareceram fáceis demais" pra IA — costuma ser onde ela erra escondido.

## O prompt (copie e cole, troque ASSUNTO e QUANTIDADE, e ajuste a matéria se não for Óptica)

```
Você vai gerar QUANTIDADE questões de múltipla escolha no estilo ENEM sobre ASSUNTO
(matéria: optica, dentro de ciencias_natureza — troque se o assunto for outro, usando só um
nome da taxonomia fechada abaixo), pra eu treinar até fixar esse conteúdo.

REGRAS DE CONTEÚDO:
1. Estilo ENEM de verdade: cada questão parte de uma situação-problema contextualizada
   (fenômeno do cotidiano, experimento, texto curto, gráfico descrito em palavras) — nunca só
   "calcule X" com fórmula pelada. Isso é o que o ENEM cobra e é o que eu preciso treinar.
2. As 5 alternativas precisam ser plausíveis — cada alternativa errada representa um erro
   conceitual real e comum (ex: trocar a fórmula, inverter uma unidade, esquecer um sinal),
   nunca uma opção obviamente absurda só pra preencher espaço.
3. Resolva CADA questão você mesma(o) com calma antes de fechar o gabarito, e confira a conta
   duas vezes — um gabarito errado aqui vira um erro meu de verdade sendo "confirmado" como
   acerto, o oposto do que eu quero. Se ficar em dúvida genuína entre duas alternativas numa
   questão, não invente confiança: pule essa questão e gere outra no lugar.
4. Varie a dificuldade e o ângulo do assunto ao longo das QUANTIDADE questões (não repita a
   mesma ideia com números trocados).

FORMATO DE SAÍDA (obrigatório, sem exceção):
- Cada questão é um bloco de texto assim, nessa ordem exata:

Enunciado da questão aqui, pode ter várias linhas de texto corrido.
A) texto da alternativa A
B) texto da alternativa B
C) texto da alternativa C
D) texto da alternativa D
E) texto da alternativa E
GABARITO: X

  (X é a letra certa, A a E)
- Separe cada bloco de questão do próximo com uma linha contendo SÓ três traços: ---
- NÃO escreva nada fora desse formato: sem introdução ("aqui estão as questões..."), sem
  numeração de questão, sem explicação da resolução, sem resumo no final, sem bloco de código
  markdown (` ``` `) em volta. Só os blocos de questão, um atrás do outro, separados por ---.
- Cada alternativa começa com a letra seguida de ")" e um espaço, exatamente como no exemplo
  acima — não use "a.", "a-" nem deixe a letra minúscula misturada com maiúscula no mesmo bloco.

TAXONOMIA FECHADA (troque a matéria do início do prompt por uma dessas se o assunto não for
Óptica — mesma taxonomia usada no resto do sistema):

matematica: estatistica, geometria_plana, geometria_analitica, geometria_espacial,
razao_e_proporcao, porcentagem, probabilidade, analise_combinatoria, funcao_1_grau,
funcao_2_grau, funcao_exponencial, logaritmo, trigonometria, progressao_aritmetica,
progressao_geometrica, sistema_de_equacoes, matematica_financeira, raciocinio_logico,
interpretacao_de_grafico, escala, unidade_de_medida, regra_de_tres, aritmetica,
matematica_basica, geometria, inequacao_e_modulo, conjuntos, funcoes, projecao_ortogonal

ciencias_natureza (Biologia): ecologia, genetica, evolucao, citologia, fisiologia_humana,
sistema_nervoso, sistema_imunologico, sistema_circulatorio, sistema_respiratorio,
sistema_digestorio, sistema_endocrino, reproducao_humana, embriologia, botanica, zoologia,
microbiologia, virus_e_bacterias, fungos, biotecnologia, meio_ambiente, saude_publica,
ciclos_biogeoquimicos, biologia (fallback genérico)

ciencias_natureza (Química): quimica_organica, quimica_inorganica, funcoes_organicas,
estequiometria, termoquimica, eletroquimica, cinetica_quimica, equilibrio_quimico, solucoes,
ligacoes_quimicas, tabela_periodica, radioatividade, polimeros, ph_e_poh, gases,
reacoes_quimicas, densidade, separacao_de_misturas, quimica_verde, quimica (fallback genérico)

ciencias_natureza (Física): cinematica, dinamica, estatica, termologia, calorimetria, ondas,
acustica, optica, eletricidade, eletrostatica, eletrodinamica, eletromagnetismo,
energia_e_trabalho, hidrostatica, gravitacao, fisica_moderna, fisica (fallback genérico)

Comece agora, gerando as QUANTIDADE questões.
```

## Depois de rodar isso na outra IA

1. **Confere o gabarito antes de importar** — pelo menos as questões que você não teria certeza
   de resolver sozinho. Esse é o passo que não existe no prompt de Extração de Gabarito (lá o
   gabarito já vem confirmado do PDF oficial); aqui é a IA se auto-corrigindo, então pode falhar.
2. Copia a resposta inteira da IA (todos os blocos, já separados por `---`) sem editar nada.
3. Cola em Admin → "🧠 Banco de prática": escolhe a grande área e a matéria (ex: Ciências da
   Natureza / optica), preenche "Fonte" com o nome da IA usada (ex: `gemini`) — isso é só pra
   você conseguir filtrar depois de onde veio cada leva — e clica "Importar pro banco de
   prática". Bloco malformado (gabarito faltando, alternativa faltando) não trava a importação
   dos outros, só é reportado à parte pra você corrigir e colar de novo só aquele.
4. Pra treinar só essas: Cartão-resposta → "Praticar por matéria" → escolhe a matéria → filtro
   "Fonte das questões" = "Só banco de prática (IA)". Errar uma dessas agenda revisão espaçada
   igual a uma questão real do ENEM — o objetivo é fixar de verdade, não só responder uma vez.
