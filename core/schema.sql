-- schema.sql
-- Banco relacional do sistema de estudo ENEM.
-- Substitui o CSV único (questoes_enem_classificadas.csv) por 4 tabelas.
-- O SQLite garante schema e tipo centralmente — o bug de colisão que
-- tínhamos entre main.py e teste.py (dois esquemas diferentes gravando
-- no mesmo arquivo) deixa de ser possível por construção.

PRAGMA foreign_keys = ON;

-- Referência fechada de taxonomia (grande_area, materia). É o que
-- impede a fragmentação de string que achamos na auditoria original
-- ("Matemática Básica" vs "Matemática básica", "Geometria Espacial"
-- vs "Geometria espacial (Esfera)", etc). A lista completa vive no
-- Python (TAXONOMIA_VALIDA em db.py) — esta tabela espelha ela pra
-- quem quiser consultar/alterar direto no banco.
CREATE TABLE IF NOT EXISTS topicos_validos (
    grande_area TEXT NOT NULL CHECK(grande_area IN ('matematica', 'ciencias_natureza')),
    materia     TEXT NOT NULL,
    PRIMARY KEY (grande_area, materia)
);

-- Questão canônica. Uma linha por questão real de uma prova real.
-- ID no formato 'ano_caderno_numero' (ex: '2024_azul_136') substitui
-- o link do YouTube como chave — uma questão não deixa de ser a
-- mesma questão só porque ganhou uma segunda resolução em vídeo.
CREATE TABLE IF NOT EXISTS questoes (
    id_questao             TEXT PRIMARY KEY,
    ano                    INTEGER NOT NULL,
    caderno                TEXT NOT NULL,
    numero_questao         INTEGER NOT NULL,
    grande_area            TEXT NOT NULL,
    materia                TEXT NOT NULL,
    topico                 TEXT,
    enunciado_texto        TEXT,
    enunciado_imagem_path  TEXT,
    alternativa_correta    TEXT NOT NULL CHECK(alternativa_correta IN ('A','B','C','D','E')),
    status_classificacao   TEXT NOT NULL DEFAULT 'classificado'
                            CHECK(status_classificacao IN ('classificado','nao_classificado')),
    origem                  TEXT NOT NULL DEFAULT 'enem_oficial'
                            CHECK(origem IN ('enem_oficial','banco_pratica')),
    fonte                   TEXT,
    criado_em               TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    -- Sem FOREIGN KEY pra topicos_validos de propósito: uma questão
    -- com matéria fora da taxonomia precisa ser GRAVADA (com
    -- status_classificacao='nao_classificado' pra triagem), não
    -- rejeitada pelo banco. A validação é feita em db.py, antes do
    -- insert; o schema só garante que status_classificacao reflita
    -- o veredito.
    --
    -- origem distingue questão real de prova ENEM ('enem_oficial',
    -- default -- ano/caderno/numero_questao são a identidade real de
    -- uma prova) de questão do banco de prática ('banco_pratica' --
    -- ex: trazida de uma sessão de estudo com IA sobre um assunto
    -- específico). Questão de banco_pratica usa ano=0/caderno=
    -- 'banco_pratica' como sentinela (nunca colide com ano real de
    -- prova) só pra satisfazer as colunas NOT NULL -- ela não é uma
    -- prova de verdade, então fica de fora de toda função que
    -- enumera/agrupa "provas" (listar_provas, simulados_feitos,
    -- recorrencia_por_materia etc., ver db.py) pra não virar um
    -- simulado fantasma nem inflar a recorrência real de um tema.
    -- Ainda assim passa pelas MESMAS tentativas_usuario/estado_revisao/
    -- Leitner/prioridade_de_estudo que questão real -- só a
    -- identidade de "prova" é diferente, o pipeline de estudo é o
    -- mesmo, de propósito (decisão do usuário: quer que errar uma
    -- questão de prática agende revisão igual e conte na prioridade
    -- por matéria).
    --
    -- fonte é texto livre, só relevante quando origem='banco_pratica'
    -- (ex: 'gemini', 'chatgpt', 'autoral') -- filtro auxiliar dentro
    -- do banco de prática, não faz parte da identidade da questão.
);

CREATE INDEX IF NOT EXISTS idx_questoes_materia ON questoes(materia);
CREATE INDEX IF NOT EXISTS idx_questoes_status ON questoes(status_classificacao);
CREATE INDEX IF NOT EXISTS idx_questoes_origem ON questoes(origem);

-- Resoluções: 1 questão -> N resoluções (vídeo e/ou texto, quantas
-- forem). Essa era a limitação principal do CSV antigo (uma linha =
-- um vídeo = uma questão, sem espaço pra uma segunda fonte).
CREATE TABLE IF NOT EXISTS resolucoes (
    id_resolucao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_questao   TEXT NOT NULL REFERENCES questoes(id_questao) ON DELETE CASCADE,
    tipo         TEXT NOT NULL CHECK(tipo IN ('video', 'texto')),
    conteudo     TEXT NOT NULL,  -- URL do vídeo OU o texto da resolução
    canal        TEXT,
    criado_em    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_resolucoes_questao ON resolucoes(id_questao);

-- Relatos de questão: o botão "reportar" no app mobile (achou o
-- gabarito errado, enunciado cortado, alternativa ambígua etc.)
-- enquanto Gabriel valida o banco de questões pergunta por pergunta.
-- Separado de `resolucoes` (que é conteúdo pra AJUDAR a entender a
-- questão) porque isto é o oposto: um sinal de que algo na questão
-- pode estar ERRADO, pra revisar depois em lote em vez de checar
-- tudo manualmente de novo. `resolvido` deixa marcar como já
-- revisado sem apagar o histórico do relato.
CREATE TABLE IF NOT EXISTS relatos_questao (
    id_relato  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_questao TEXT NOT NULL REFERENCES questoes(id_questao) ON DELETE CASCADE,
    comentario TEXT NOT NULL,
    resolvido  INTEGER NOT NULL DEFAULT 0 CHECK(resolvido IN (0, 1)),
    criado_em  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_relatos_questao ON relatos_questao(id_questao);
CREATE INDEX IF NOT EXISTS idx_relatos_resolvido ON relatos_questao(resolvido);

-- Log de tentativas do usuário. Append-only de propósito — é o
-- histórico de verdade, nunca é sobrescrito nem editado.
-- resposta_escolhida aceita NULL de propósito: questão deixada em
-- branco é uma tentativa de verdade (resultado sempre 'errou', nunca
-- fica de fora da conta) -- não deixar em branco simplesmente não
-- registrar nada escondia isso de toda estatística baseada nesta
-- tabela (taxa de acerto, prioridade de estudo, Leitner).
-- 'localtime' em todo DEFAULT de data/hora deste arquivo (não só aqui) é
-- deliberado, não estilo: sqlite datetime('now')/date('now') sem esse
-- modificador retorna UTC, enquanto todo o Python do projeto usa
-- date.today()/datetime.now() (hora LOCAL). Usuário em UTC-3: das ~21h às
-- 23h59 locais, UTC já virou o dia seguinte -- uma tentativa registrada
-- nesse intervalo gravava com data_tentativa de AMANHÃ (UTC) enquanto
-- toda comparação "hoje" no Python (meta diária, missão do dia, streak)
-- usava HOJE (local), fazendo elas nunca baterem -- bug real, achado
-- rodando os testes à noite, não uma correção cosmética.
CREATE TABLE IF NOT EXISTS tentativas_usuario (
    id_tentativa        INTEGER PRIMARY KEY AUTOINCREMENT,
    id_questao          TEXT NOT NULL REFERENCES questoes(id_questao) ON DELETE CASCADE,
    data_tentativa       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    resposta_escolhida  TEXT CHECK(resposta_escolhida IN ('A','B','C','D','E') OR resposta_escolhida IS NULL),
    resultado           TEXT NOT NULL CHECK(resultado IN ('acertou','errou')),
    intervalo_dias      INTEGER NOT NULL,
    streak_acertos      INTEGER NOT NULL,
    proxima_revisao     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tentativas_questao ON tentativas_usuario(id_questao);
CREATE INDEX IF NOT EXISTS idx_tentativas_data ON tentativas_usuario(data_tentativa);

-- Estado atual da revisão espaçada, 1 linha por questão já tentada.
-- Separado de tentativas_usuario de propósito: tentativas é log
-- histórico imutável, estado_revisao é o ponteiro mutável que o
-- quiz consulta pra saber "o que revisar hoje". Misturar os dois
-- numa tabela só criaria o mesmo tipo de ambiguidade que o
-- .update() do main.py antigo tinha (estado atual vs. histórico).
CREATE TABLE IF NOT EXISTS estado_revisao (
    id_questao        TEXT PRIMARY KEY REFERENCES questoes(id_questao) ON DELETE CASCADE,
    intervalo_dias    INTEGER NOT NULL,
    streak_acertos    INTEGER NOT NULL,
    proxima_revisao   TEXT NOT NULL,
    ultima_tentativa  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_estado_proxima_revisao ON estado_revisao(proxima_revisao);

-- Log de auditoria: toda vez que inserir_questao(sobrescrever=True)
-- muda de fato um campo (matéria ou gabarito), fica registrado aqui
-- quem mudou o quê e quando. Existe pra dar visibilidade de admin
-- sobre correções feitas depois que já havia tentativa registrada.
CREATE TABLE IF NOT EXISTS historico_alteracoes (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_questao               TEXT NOT NULL,
    campo                    TEXT NOT NULL,
    valor_antigo             TEXT,
    valor_novo               TEXT,
    data_alteracao           TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    tentativas_recalculadas  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_historico_questao ON historico_alteracoes(id_questao);

-- Configuração chave-valor de propósito geral (hoje só guarda a meta
-- diária de questões). Tabela solta em vez de coluna fixa em algum
-- lugar porque é o único dado do sistema que não é fato sobre uma
-- questão/tentativa -- é preferência do usuário sobre a própria meta.
CREATE TABLE IF NOT EXISTS configuracoes (
    chave  TEXT PRIMARY KEY,
    valor  TEXT NOT NULL
);

-- Redações: guarda, não corrige. A nota e a contagem de erro
-- ortográfico vêm de correção externa/própria (cursinho, redator, o
-- próprio usuário) -- o sistema não tem como avaliar redação de
-- verdade, só registrar o resultado de quem avaliou.
CREATE TABLE IF NOT EXISTS redacoes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tema                TEXT NOT NULL,
    data_escrita        TEXT NOT NULL DEFAULT (date('now','localtime')),
    texto               TEXT,
    arquivo_path        TEXT,
    nota                INTEGER,
    erros_ortograficos  INTEGER,
    fonte_correcao      TEXT CHECK(fonte_correcao IN ('propria', 'externa', 'oficial') OR fonte_correcao IS NULL),
    observacoes         TEXT,
    criado_em           TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE INDEX IF NOT EXISTS idx_redacoes_data ON redacoes(data_escrita);

-- Nome opcional por tentativa de uma prova (ex: "fiz cansado de noite").
-- numero_tentativa é o mesmo número derivado por resumo_por_tentativa()
-- (ROW_NUMBER por data_tentativa) -- essa tabela só guarda um rótulo
-- pra ele, nunca cria nem controla a numeração em si.
CREATE TABLE IF NOT EXISTS nomes_tentativas (
    ano               INTEGER NOT NULL,
    caderno           TEXT NOT NULL,
    grande_area       TEXT NOT NULL,
    numero_tentativa  INTEGER NOT NULL,
    nome              TEXT NOT NULL,
    PRIMARY KEY (ano, caderno, grande_area, numero_tentativa)
);
