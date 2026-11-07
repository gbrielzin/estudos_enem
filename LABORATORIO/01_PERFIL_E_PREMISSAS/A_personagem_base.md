# A. Personagem-base (fictício) — v1, 2026-11-07

Usado em todas as simulações. Construído a partir da entrevista inicial; **não contém patrimônio real do usuário**.

| Campo | Valor |
|---|---|
| Idade inicial | 19 anos |
| Cidade de partida | Vitória (ES); muda para São Paulo se aprovado com bolsa |
| Situação | Faz o ENEM para tentar bolsa em faculdade de São Paulo |
| Capital inicial | R$ 1.000 |
| Renda inicial | Freelance de programação: ~R$ 100/mês |
| Habilidade comercial | Compra e revenda de iPhone (OLX/Facebook): negocia preço baixo e revende |
| Programação | Autodidata, nível universitário; usa IA (Claude) para acelerar a maior parte do trabalho |
| Inglês | Intermediário |
| Apetite a risco | Médio: aceita mudar de estado e assumir incerteza, mas não é um perfil de risco extremo |
| Traços | Muita curiosidade; pesquisa a fundo; quando a solução exige outra habilidade, aprende ou busca a solução |
| Objetivo | Equilíbrio entre renda, patrimônio, liberdade de tempo e aprendizado |
| Horizonte | 10 anos (19→29 anos) |

## Premissas globais assumidas pelo laboratório (marcadas como minhas, não informadas por você)
- Aprovação com bolsa em SP é **variável de controle** (igual em todas as simulações). O caso sem bolsa está em `08_CENARIOS_ALTERNATIVOS`.
- Bolsa/permanência de R$ 600/mês nos 4 primeiros anos (**PENDENTE confirmar**).
- Sem apoio familiar financeiro (**PENDENTE confirmar**).
- Custo de vida em SP: R$ 24 mil/ano no ano 1 até R$ 108 mil/ano no ano 10 (crescimento com a idade), com ajuste por estilo de vida da trajetória.
- Inflação 4,5% a.a.; carteira pessoal 10% a.a. líquido; dívida empresarial 14%; dívida pessoal 12%.
- Cenários: pessimista, base e otimista por multiplicadores explícitos (ver `00_CONFIGURACAO/motor/motor.py`).
