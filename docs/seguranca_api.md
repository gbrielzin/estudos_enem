# Segurança da API contra abuso e robô

Até aqui a API tinha uma trava só: a chave (código de acesso de cada pessoa
ou a chave do admin), conferida com `hmac.compare_digest`. Ela barra quem
não tem a chave, mas não barra quem tenta muitas vezes. Um robô podia
chutar chave sem parar, martelar o `/tentativas` ou baixar o app web mil
vezes por minuto, e eu nem ia ficar sabendo. Esta página explica o que
coloquei na frente disso, os números que escolhi e como eu atacaria a
própria API para conferir que funciona.

O código está em `core/seguranca.py` (o mecanismo) e em `core/api.py` (a
ligação com as rotas). Os testes estão em `core/test_api.py`, nas classes
que começam com `TestLimite`, `TestForcaBruta`, `TestIpAtrasDoProxy`,
`TestHeadersDeSeguranca` e `TestLogDeSegurancaNoAdmin`.

## 1. Limite de requisições (rate limit)

Cada requisição cai em um de quatro tipos, e cada tipo tem a própria cota
por minuto:

| Tipo | Rotas | Limite | Por quê |
|---|---|---|---|
| leitura | `GET` da API (`/trilha`, `/streak`, `/health`...) | 240/min | A trilha abre várias telas seguidas; 4 por segundo sobra para gente de verdade |
| escrita | `POST` da API (`/tentativas`, `/relatos`, `/eventos`...) | 60/min | Responder mais de 1 questão por segundo, o minuto inteiro, não é estudo, é script |
| admin | tudo em `/admin` | 20/min | Sou só eu olhando o painel |
| arquivos | app web, figuras das questões, `/legal` | 600/min | Abrir uma tela carrega dezenas de arquivos de uma vez |

Estourou: a resposta é **429** com o header **`Retry-After`** dizendo
quantos segundos faltam para abrir vaga. Quem respeita o header (o
navegador, um cliente bem feito) espera o tempo certo em vez de ficar
tentando.

**De quem é a cota.** Quando a requisição traz um código de acesso
válido, a cota é da pessoa; quando não traz, é do IP. Isso importa porque
uma escola ou uma casa inteira sai na internet com o mesmo IP: se a cota
fosse só por IP, uma pessoa estudando rápido travaria a colega da mesma
wifi. O painel de admin conta sempre por IP.

**Janela deslizante, não minuto fixo.** Guardo o horário de cada
requisição aceita e conto as dos últimos 60 segundos. Com o minuto fixo
("zera no segundo 0"), daria para mandar 60 escritas no fim de um minuto e
mais 60 no começo do seguinte: 120 em 2 segundos.

**Por que não usei biblioteca (`slowapi`).** O que eu precisava era
contar por pessoa, e só a minha API sabe quem é a pessoa a partir do
código. Com uma lib eu ia escrever essa parte de qualquer jeito, e ainda
ganhar uma dependência nova. O contador próprio tem umas 60 linhas e
testes que controlam o relógio.

**Limite conhecido: memória de um processo.** Os contadores ficam na
memória do servidor. Hoje roda uma réplica só na Railway, então funciona.
Com duas réplicas, cada uma contaria sozinha e o limite real dobraria; aí
o contador precisa ir para um Redis (mesma lógica, outro lugar de
guardar). Para um ataque com milhares de IPs não encher a memória, guardo
no máximo 20 mil chaves e descarto as mais antigas.

## 2. Força bruta na chave

Na minha API não existe tela de login com senha: o código de acesso é a
credencial. Então "força bruta" aqui é chutar código. A trava:

- toda resposta **401** (chave errada) conta como erro para aquele IP;
- **10 erros em 15 minutos** bloqueiam o IP: daí em diante, qualquer rota
  com chave (API e admin) responde 429 até a janela passar;
- o bloqueio vale **mesmo se o próximo chute estiver certo**. Se a chave
  certa passasse, o robô saberia que acertou pelo 200 no meio dos 429.

Por que 10 em 15 min: uma pessoa que digita o código errado erra 2 ou 3
vezes, não 10. E o código tem pelo menos 16 caracteres aleatórios, então
mesmo sem trava ninguém acerta no chute; a trava é a segunda camada, e o
log (abaixo) me avisa que alguém está tentando.

O `/health` também passa pela chave, então entrou na conta como leitura.
Rota com chave e sem limite seria a porta dos fundos para chutar à
vontade.

## 3. IP real atrás do proxy da Railway

O servidor não fala direto com o celular: a borda da Railway recebe a
conexão e repassa. O IP que o servidor vê é o da Railway, igual para
todo mundo. O IP de verdade chega num header, e header é texto que
qualquer um pode escrever. Se eu confiasse cegamente, um robô mandaria
`X-Forwarded-For: 1.2.3.4`, depois `1.2.3.5`, e teria cota nova a cada
requisição.

A decisão:

- **Atrás da Railway** uso o `X-Real-IP`. A documentação da Railway diz
  que a borda preenche esse header com o IP do cliente. Header ausente ou
  que não é um IP válido cai no IP da conexão.
- **Não uso o `X-Forwarded-For`**, nem atrás da Railway. Nesse header o
  cliente pode escrever o que quiser na frente, e a Railway não documenta
  se ela sobrescreve ou só acrescenta no fim. Um teste garante que trocar
  o `X-Forwarded-For` a cada requisição não dá cota nova.
- **Fora da Railway** (meu PC, outro servidor) nenhum header é lido: vale
  o IP da conexão TCP, que não dá para falsificar.

Como o código sabe que está na Railway: ela injeta `RAILWAY_PROJECT_ID` e
`RAILWAY_ENVIRONMENT_ID` em todo deploy. A variável `API_CONFIAR_PROXY`
força a escolha (`1` confia, `0` nunca confia), se um dia eu mudar de
hospedagem.

## 4. Log de segurança

Três eventos viram uma linha de log:

- `limite_excedido`: um 429 (por cota ou por IP bloqueado);
- `chave_errada`: um 401 na API, com a contagem ("7 erro(s) em 15 min",
  e "-> ip bloqueado" no 10º);
- `admin_negado`: um 401 no painel de admin.

Cada linha tem horário (UTC), IP, método, rota, User-Agent e o detalhe.
**Não entra**: o header Authorization (nem o chute errado, que pode ser
uma chave de verdade digitada no lugar errado), a query string e o corpo
da requisição. A rota é gravada sem os parâmetros de propósito.

Onde fica: uma linha JSON no stdout (os logs da Railway guardam) e os
últimos 500 eventos em memória, que aparecem numa tabela nova no painel
`/admin/` (rota `/admin/seguranca`, com a mesma chave do admin). A tabela
zera quando o servidor reinicia; o histórico fica nos logs da Railway.

Um robô martelando geraria milhares de linhas iguais, então o 429 de uma
mesma chave entra no log uma vez por minuto. Chave errada entra toda vez
(no máximo 10 antes do bloqueio).

## 5. Headers de segurança e revisão da autenticação

Toda resposta (inclusive 401 e 429) sai com:

| Header | Valor | O que fecha |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | o navegador "adivinhar" que um arquivo é script |
| `X-Frame-Options` | `DENY` | colocar o app ou o painel dentro de um iframe de outro site (clickjacking) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | mandar a URL completa para outro site num link |
| `Content-Security-Policy` | `frame-ancestors 'none'; base-uri 'self'; object-src 'none'` | iframe (versão moderna do de cima), `<base>` injetado e plugin |

A CSP é mínima de propósito: o app web e o painel usam script e estilo
inline, e uma CSP que restringe script quebraria a tela.

O que conferi na autenticação e já estava certo: toda comparação de chave
usa `hmac.compare_digest` (tempo constante, não dá para descobrir a chave
medindo quanto a resposta demora), a API é fechada por padrão (sem chave
configurada responde 503), a chave do admin é separada dos códigos das
pessoas e precisa ter 16+ caracteres, e o painel não guarda a chave no
`localStorage`. A única mudança foi tirar a comparação de código para uma
função (`_pessoa_pelo_codigo`), que agora serve à trava e ao limite.

O que ficou como próximo passo, sem mexer agora:

1. **Código não expira.** O código de acesso vale até eu trocar a
   variável. Login de verdade com token que expira é o passo previsto no
   adr/0009.
2. **`/docs` e `/openapi.json` abertos.** Não mostram dado nenhum, mas
   entregam o mapa das rotas. Dá para desligar em produção.
3. **HSTS** (`Strict-Transport-Security`). A Railway já serve só HTTPS;
   o header faria o navegador nem tentar HTTP.
4. **Tamanho máximo do corpo.** Um POST gigante ocupa memória antes de
   qualquer validação. Um teto (ex.: 64 KB) resolve.
5. **Política de privacidade.** O log de segurança guarda IP. É
   legítimo (proteção do serviço), mas vale citar na política.

## 6. Como eu testaria um ataque contra isso

Sempre contra a minha própria API, olhando do lado de quem defende: o
objetivo é ver o bloqueio acontecer e aparecer no log.

1. **Martelar uma rota.** Um laço com `curl` em `/streak` com um código
   válido, 300 vezes. Espero 240 respostas 200 e depois 429 com
   `Retry-After`; esperar esse número de segundos e ver voltar a 200.
2. **Chutar chave.** 12 requisições com `Authorization: Bearer chute-N`.
   Espero 10 respostas 401 e depois 429; em seguida mandar o código certo
   e confirmar que **também** vem 429. No painel: 10 linhas
   `chave_errada`, a última com "ip bloqueado".
3. **Trocar de IP pelo header.** Repetir o teste 1 mandando um
   `X-Forwarded-For` diferente em cada requisição, e depois um `X-Real-IP`
   diferente. O bloqueio tem que chegar no mesmo número. Se com o
   `X-Real-IP` trocado eu ganhar cota nova em produção, a Railway não está
   sobrescrevendo o header, e é hora de `API_CONFIAR_PROXY=0`.
4. **Conferir o IP que aparece.** Depois do deploy, errar a chave do
   painel uma vez de propósito e ver no `/admin/` qual IP ficou no log. Tem
   que ser o meu IP de casa, não um da rede interna da Railway.
5. **Separação por pessoa.** Duas pessoas no mesmo wifi: esgotar a cota
   de uma e confirmar que a outra continua respondendo.
6. **Vazamento no log.** Errar a chave com um texto marcado
   (`Bearer NAO-PODE-APARECER`) e procurar esse texto nos logs da Railway.
   Não pode estar lá.

Os passos 1, 2, 3, 5 e 6 já são testes automáticos (com limites pequenos
para rodar rápido); os passos 3 e 4 em produção são os que nenhum teste
local substitui, porque dependem do proxy de verdade.

## Variáveis novas

Nenhuma é obrigatória; sem configurar nada, a proteção já está ligada.

- `API_RATE_LIMIT_DESLIGADO=1`: desliga limite e trava de força bruta.
  Só para teste local (a suíte antiga usa).
- `API_CONFIAR_PROXY`: `1` usa o `X-Real-IP`, `0` nunca usa, vazio =
  automático (liga só na Railway).

Os números (240, 60, 20, 600, 10 em 15 min) ficam no começo de
`core/seguranca.py`, não em variável: mudar limite é decisão que eu quero
ver num PR, não num painel.
