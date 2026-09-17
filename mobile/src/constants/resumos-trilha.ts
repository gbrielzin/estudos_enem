export type FrequenciaTopico = 'alta' | 'media' | 'baixa';

export interface TopicoResumo {
  titulo: string;
  descricao: string;
  frequencia: FrequenciaTopico;
}

export interface ResumoTrilha {
  minutos: number;
  titulo: string;
  subtitulo: string;
  topicos: TopicoResumo[];
  estatisticaNumero: string;
  estatisticaTexto: string;
}

/**
 * Conteúdo do card/tela "Apresentação" que abre uma trilha, ANTES do
 * Nó 1 -- pedido explícito do usuário: dar uma base de conceitos pro
 * aluno antes de jogar ele direto numa "porrada de questão", sem
 * transformar isso num atalho fácil (a trilha em si continua exigindo
 * muita repetição depois). Visual/copy importados do projeto de
 * design (App ENEM.dc.html, tela "Apresentação" -- ver DesignSync,
 * projectId 669f9530-e4b9-4dfb-ab2c-cd90df9199b4).
 *
 * Isto é conteúdo AUTORAL, escrito à mão por matéria -- não é
 * derivado de tentativas_usuario nem de nenhuma tabela do banco (o
 * banco não sabe "o que mais cai" de um jeito pedagógico, só sabe
 * gabarito/materia). Mesma categoria de manual_prioridade_de_estudo.md
 * no core/: conteúdo que o Gabriel escreve, não dado calculado.
 *
 * Só "optica" está preenchido por enquanto. Uma matéria sem entrada
 * aqui simplesmente não mostra o card de Apresentação na trilha (ver
 * trilha-path.tsx) -- degrada pro comportamento de hoje, não quebra
 * nada. De propósito NÃO existe ainda um conceito de "resumo por
 * fase": matérias mais extensas (ex. ecologia, que o usuário já
 * sinalizou que vai precisar de ~6 fases em vez de uma trilha só)
 * provavelmente vão precisar de uma forma diferente daqui, mas essa
 * forma só fica clara quando a segunda matéria for escrita de
 * verdade -- ver a conversa que motivou este arquivo.
 */
export const RESUMOS_TRILHA: Record<string, ResumoTrilha> = {};

/**
 * Resumo por SUBFASE de Óptica/Ondulatória -- substituiu, em
 * 2026-09-17, um único RESUMOS_TRILHA.optica que ensinava "Espelhos e
 * lentes/Refração/Olho humano", conteúdo que não batia com o que o
 * banco de prática de verdade testa (123 questões de óptica + 14 de
 * acústica, geradas a partir de
 * "docs/questoes/Óptica - Fase 1 (PARTE 2).docx", fonte autoral do
 * Gabriel). Esse documento já vem estruturado em 3 subfases -- cada
 * uma testando um POOL FIXO de fenômenos parecidos, variando só o
 * contexto real (pesca, wifi, sonar, holografia) -- e o texto de cada
 * card abaixo é adaptado direto da seção "CONCEITO INICIAL PARA O
 * ALUNO" do documento, não reescrito do zero. Mesma ponte de
 * RESUMOS_POR_CHAVE_TRILHA_FIXA que RESUMOS_FASE_ECOLOGIA já usa, só
 * que aqui a chave da trilha fixa já É por subfase
 * ('optica_ondulatoria_1/2/3', ver core/db.py TRILHA_FIXA_NOS) --
 * não precisa de indireção por fase numérica coincidindo com
 * `chave` como em Ecologia.
 *
 * Contagem real (core/db.py FASES_OPTICA/FASES_ACUSTICA, banco de
 * prática): subfase 1 = 24 questões (polarização 13 + difração 11),
 * subfase 2 = 83 questões (refração 21, reflexão difusa 14, absorção
 * 13, reflexão especular 11, difração* 11 -- não, ver contagem exata
 * em db.py), subfase 3 = 30 questões (efeito Doppler 10, interferência
 * 13, eco 4, reverberação 2, ressonância 1). "Espelhos e lentes" e
 * "Olho humano" (fase antiga) ainda não têm subfase própria no banco
 * -- seguem testados em prova real (ver 2024_amarelo_118), mas sem
 * volume de banco de prática pra virar card aqui ainda.
 */
export const RESUMOS_FASE_OPTICA: Record<number, ResumoTrilha> = {
  1: {
    minutos: 2,
    titulo: 'Óptica/Ondulatória — Polarização e Difração',
    subtitulo:
      'A banca troca o cenário (pesca, wifi, rádio, som) mas o par que você precisa diferenciar é sempre o mesmo: filtrar direção vs. contornar obstáculo.',
    topicos: [
      {
        titulo: 'Polarização',
        descricao:
          'Filtra/bloqueia a luz que vibra numa direção específica -- elimina reflexo e brilho excessivo (óculos polarizados, tela anti-reflexo). Só acontece com ondas TRANSVERSAIS (luz) -- NUNCA com som',
        frequencia: 'alta',
      },
      {
        titulo: 'Difração',
        descricao:
          'Qualquer onda contorna obstáculos, quinas ou passa por frestas estreitas (wifi atravessando parede, som saindo por porta entreaberta, rádio AM contornando montanha)',
        frequencia: 'alta',
      },
    ],
    estatisticaNumero: '24',
    estatisticaTexto: 'questões do banco de prática treinam exatamente esse par (polarização x difração).',
  },
  2: {
    minutos: 3,
    titulo: 'Óptica/Ondulatória — Refração, Dispersão, Absorção e Reflexão',
    subtitulo:
      'A maior subfase do banco -- 5 fenômenos que se confundem porque todos envolvem luz "mudando de comportamento" ao encontrar um meio ou superfície diferente.',
    topicos: [
      {
        titulo: 'Refração',
        descricao:
          'Muda de meio de propagação -- altera velocidade e comprimento de onda, mas a FREQUÊNCIA nunca muda (canudo "quebrado" no copo, miragem no asfalto quente)',
        frequencia: 'alta',
      },
      {
        titulo: 'Reflexão especular vs. difusa',
        descricao:
          'Especular: superfície lisa/polida, retorno organizado, imagem nítida (espelho). Difusa: superfície áspera, retorno espalhado em vários ângulos (asfalto, papel fosco)',
        frequencia: 'alta',
      },
      {
        titulo: 'Absorção',
        descricao: 'A superfície retém a energia da onda e vira calor (roupa escura esquentando no sol)',
        frequencia: 'alta',
      },
      {
        titulo: 'Dispersão',
        descricao:
          'Luz branca se separa nas cores componentes ao mudar de meio -- cada cor viaja numa velocidade diferente (prisma, arco-íris)',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '83',
    estatisticaTexto: 'questões do banco de prática -- de longe a subfase com mais volume hoje.',
  },
  3: {
    minutos: 2,
    titulo: 'Óptica/Ondulatória — Eco, Reverberação, Doppler e Interferência',
    subtitulo:
      'Aqui a pegadinha é TEMPO e FREQUÊNCIA, não mais "tipo de superfície" -- distância até o obstáculo e movimento relativo da fonte.',
    topicos: [
      {
        titulo: 'Eco vs. Reverberação',
        descricao:
          'Eco: obstáculo longe (>17m), o som volta separado, ouve-se duas vezes. Reverberação: obstáculo perto (<17m), o som volta rápido e "borra"/prolonga o original',
        frequencia: 'alta',
      },
      {
        titulo: 'Efeito Doppler',
        descricao:
          'A frequência aparente muda com o movimento relativo: aproximação comprime a onda (mais agudo/azul), afastamento estica (mais grave/vermelho) -- sirene, radar, redshift',
        frequencia: 'alta',
      },
      {
        titulo: 'Interferência',
        descricao:
          'Duas ondas se cruzam: somam (construtiva, mais volume/brilho) ou cancelam (destrutiva, silêncio/escuro) -- fone com cancelamento de ruído, holografia',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '30',
    estatisticaTexto: 'questões do banco de prática treinam esse trio.',
  },
};

/**
 * Resumo por FASE, pra matérias cuja trilha é dividida em fases (ver
 * docs/filosofia.md) em vez de uma trilha única -- ecologia é a
 * primeira, confirmando a dúvida que o comentário de RESUMOS_TRILHA
 * acima deixou em aberto ("só fica clara quando a segunda matéria for
 * escrita de verdade"). Cada fase ganha sua própria tela de
 * Apresentação antes do Nó 1 DAQUELA fase, não uma única tela pra
 * ecologia inteira (são ~6 fases com pesos de incidência bem
 * diferentes -- ver a tabela em docs/filosofia.md).
 *
 * Ainda NÃO está plugado em trilha-path.tsx/index.tsx: falta decidir
 * onde uma fase começa/termina dentro da lista flat de NoTrilha que a
 * API devolve hoje (getTrilha() não tem conceito de fase nenhum ainda
 * -- ver core/api.ts), o que depende de como as questões de
 * banco_pratica de ecologia forem carregadas e ordenadas no banco.
 * Isto aqui é só o conteúdo pedagógico (autoral, mesma categoria do
 * resumo de óptica acima), pronto pra ser consumido assim que essa
 * divisão por fase existir de verdade na trilha.
 */
export const RESUMOS_FASE_ECOLOGIA: Record<number, ResumoTrilha> = {
  /**
   * Adicionado em 2026-09-17, depois da fase 4 já existir -- achado
   * ao vivo: na amostra de 11 questões oficiais de Ecologia já
   * classificadas, Relações Ecológicas empatou como o padrão MAIS
   * recorrente (com magnificação trófica) e Poluição Atmosférica
   * teve ZERO ocorrência (ver docs/pesquisa_estrategia_de_prova.md).
   *
   * Dividido em 3 (fases 2/7/8, mesmo dia) depois de outro relato ao
   * vivo: um resumo só com os 14 padrões virou "muito coisa", e
   * dinâmica populacional (capacidade de suporte) misturada com
   * relação ENTRE espécies diferentes confundiu ("apareceu do nada").
   * Harmônicas (fase 2) mantém o número original; Desarmônicas e
   * População/Sucessão ganharam fase 7/8 pra não renumerar as fases
   * 3-6 que já existiam (ver FASES_ECOLOGIA em core/db.py).
   */
  2: {
    minutos: 2,
    titulo: 'O que cai de Relações Ecológicas Harmônicas',
    subtitulo:
      'Os dois lados nunca perdem aqui -- pelo menos um ganha, e o outro no pior caso fica igual. A pegadinha é confundir "não incomoda" (inquilinismo/epifitismo) com "também ganha algo" (comensalismo).',
    topicos: [
      {
        titulo: 'Mutualismo (+/+) e Protocooperação (+/+)',
        descricao:
          'Os dois lados ganham. Mutualismo: dependem um do outro pra sobreviver (cupim e protozoário no intestino). Protocooperação: ganham juntos, mas sobrevivem separados (crocodilo e palito-de-dente/ave)',
        frequencia: 'alta',
      },
      {
        titulo: 'Comensalismo (+/0)',
        descricao: 'Um ganha, o outro nem ganha nem perde -- aproveita resto de comida (urubu e leão, peixe-piloto e tubarão)',
        frequencia: 'media',
      },
      {
        titulo: 'Inquilinismo (+/0)',
        descricao:
          'Um ANIMAL aproveita abrigo/transporte/sustentação de outro ser vivo, sem disputar recurso nem prejudicar (rêmora no tubarão, ave fazendo ninho em árvore)',
        frequencia: 'media',
      },
      {
        titulo: 'Epifitismo (+/0)',
        descricao:
          'Caso específico de "carona" entre PLANTAS: uma planta cresce sobre outra usando-a só como suporte físico pra ficar mais perto da luz -- sem tirar seiva nem nutriente da planta que serve de apoio (orquídea/bromélia no galho de árvore)',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '5',
    estatisticaTexto: 'padrões diferentes cabem aqui -- todos com pelo menos um lado ganhando.',
  },
  7: {
    minutos: 2,
    titulo: 'O que cai de Relações Ecológicas Desarmônicas',
    subtitulo:
      'Aqui sempre tem um lado perdendo (ou os dois). Competição interespecífica empatou como o padrão mais recorrente da amostra real, junto com sucessão ecológica.',
    topicos: [
      {
        titulo: 'Competição Interespecífica (-/-)',
        descricao:
          'Duas espécies DIFERENTES disputam o MESMO recurso limitado (comida, território, abrigo) e as duas saem perdendo -- espécie invasora ocupando nicho de espécie nativa é o exemplo clássico',
        frequencia: 'alta',
      },
      {
        titulo: 'Predação (+/-)',
        descricao: 'Um mata e come o outro na hora (leão e zebra) -- diferente de parasitismo, que não mata de imediato',
        frequencia: 'alta',
      },
      {
        titulo: 'Parasitismo (+/-)',
        descricao: 'Um vive associado ao outro tirando proveito, geralmente sem matar na hora (verme, pulga, carrapato)',
        frequencia: 'media',
      },
      {
        titulo: 'Amensalismo (-/0)',
        descricao:
          'Um atrapalha o outro sem ganhar nada com isso (fungo que libera substância que inibe bactéria por perto, sem se beneficiar diretamente)',
        frequencia: 'alta',
      },
    ],
    estatisticaNumero: '2x',
    estatisticaTexto:
      'competição interespecífica foi um dos padrões que mais se repetiu na amostra de provas oficiais já classificadas.',
  },
  8: {
    minutos: 2,
    titulo: 'O que cai de População e Sucessão Ecológica',
    subtitulo:
      'Diferente das fases anteriores -- aqui não é relação ENTRE espécies diferentes, é sobre COMO uma população/comunidade muda ao longo do tempo ou do espaço.',
    topicos: [
      {
        titulo: 'Sucessão Ecológica (primária x secundária)',
        descricao:
          'Primária: começa do zero, sem solo (rocha nua, lava vulcânica). Secundária: já existia solo/vida antes de uma perturbação (área queimada, pasto abandonado) -- por isso é mais rápida',
        frequencia: 'alta',
      },
      {
        titulo: 'Capacidade de Suporte',
        descricao:
          'O limite máximo de indivíduos que um ambiente sustenta com os recursos disponíveis -- população cresce rápido no início e estabiliza (curva em "S") quando bate nesse teto',
        frequencia: 'media',
      },
      {
        titulo: 'Potencial Biótico e Canibalismo',
        descricao:
          'Potencial biótico: capacidade máxima de reprodução de uma espécie SEM limitação nenhuma (raramente atingida na natureza). Canibalismo: predação dentro da MESMA espécie, geralmente ligada a escassez de recurso',
        frequencia: 'baixa',
      },
    ],
    estatisticaNumero: '2x',
    estatisticaTexto:
      'sucessão ecológica foi um dos padrões que mais se repetiu na amostra de provas oficiais já classificadas -- à frente de Poluição Atmosférica (0x).',
  },
  4: {
    minutos: 2,
    titulo: 'O que cai de Poluição Atmosférica',
    subtitulo:
      'A banca adora trocar as gavetas: CO₂ retém calor, CFC deixa o raio UV entrar. Misturar essas duas é o distrator que mais derruba candidato nessa fase.',
    topicos: [
      {
        titulo: 'Chuva Ácida',
        descricao:
          'Queima de carvão/combustíveis libera óxidos de enxofre (SOx) e nitrogênio (NOx), que reagem com a água da chuva e formam ácido -- corrói estátuas de pedra calcária e queima folhas a km de distância da indústria',
        frequencia: 'alta',
      },
      {
        titulo: 'Destruição da Camada de Ozônio',
        descricao:
          'CFC (geladeiras e aerossóis antigos) quebra o ozônio (O₃) na alta atmosfera, abrindo passagem pra radiação ultravioleta (UV) -- câncer de pele. Sem relação com retenção de calor',
        frequencia: 'alta',
      },
      {
        titulo: 'Efeito Estufa e Aquecimento Global',
        descricao:
          'CO₂ e metano (CH₄) da queima, desmatamento e decomposição do lixo funcionam como um cobertor, retendo calor no planeta',
        frequencia: 'alta',
      },
      {
        titulo: 'Inversão Térmica',
        descricao:
          'Fenômeno natural de madrugadas frias: ar frio e denso fica preso perto do chão, tranca a fumaça das chaminés/escapamentos na altura em que a população respira',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '28%',
    estatisticaTexto:
      'do peso de Ecologia no ENEM é Poluição Atmosférica -- a fase de maior prioridade da matéria (ver docs/filosofia.md).',
  },
};

/**
 * Resumo por fase de Cinemática, adicionado em 2026-09-17 junto com a
 * inserção dos 2 padrões novos no banco (MRUV/Lançamento Horizontal --
 * ver docs/questoes/moldes_novos_padroes_2026-09-17.md). Fase 1
 * (Velocidade Média/MRU, 15 questões já existentes) ainda sem resumo
 * -- degrada normalmente, sem "Rever conteúdo base" nessa fase.
 */
export const RESUMOS_FASE_CINEMATICA: Record<number, ResumoTrilha> = {
  2: {
    minutos: 2,
    titulo: 'O que cai de MRUV',
    subtitulo: 'Mesma família de fórmula do MRU, só que agora a velocidade MUDA a uma taxa constante.',
    topicos: [
      {
        titulo: 'v = v₀ + a·t',
        descricao: 'Velocidade em função do tempo -- sinal de "a" positivo acelera, negativo freia',
        frequencia: 'alta',
      },
      {
        titulo: 'v² = v₀² + 2·a·Δs',
        descricao: 'Velocidade em função do espaço percorrido, sem precisar calcular o tempo',
        frequencia: 'alta',
      },
      {
        titulo: 'Lançamento vertical -- pegadinha',
        descricao: 'No ponto mais alto, v = 0, mas a aceleração continua sendo g (nunca fica zero)',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '2x',
    estatisticaTexto: 'foi o padrão mais recorrente de Cinemática na amostra de provas oficiais já classificadas.',
  },
  3: {
    minutos: 2,
    titulo: 'O que cai de Lançamento Horizontal',
    subtitulo: 'Dois movimentos ACONTECENDO JUNTOS, mas independentes: horizontal é MRU, vertical é queda livre.',
    topicos: [
      {
        titulo: 'Eixo horizontal (x)',
        descricao: 'MRU puro -- velocidade constante, a mesma que o objeto tinha ao sair',
        frequencia: 'alta',
      },
      {
        titulo: 'Eixo vertical (y)',
        descricao: 'Queda livre (MRUV com a = g), começando do repouso NESSE eixo -- só a altura decide o tempo de queda',
        frequencia: 'alta',
      },
      {
        titulo: 'Pegadinha clássica',
        descricao: 'A velocidade horizontal NÃO afeta quanto tempo o objeto leva pra cair -- só a altura importa',
        frequencia: 'alta',
      },
    ],
    estatisticaNumero: '2x',
    estatisticaTexto: 'apareceu na amostra de provas oficiais já classificadas, empatado com MRUV.',
  },
};

/**
 * Resumo por fase de Fisiologia Humana, adicionado em 2026-09-17
 * junto com a inserção dos 2 padrões novos no banco (Bioacumulação em
 * Tecido Adiposo/Fibras Musculares). Fase 1 (Vacina vs. Soro, 15
 * questões já existentes) ainda sem resumo -- degrada normalmente.
 */
export const RESUMOS_FASE_FISIOLOGIA_HUMANA: Record<number, ResumoTrilha> = {
  2: {
    minutos: 2,
    titulo: 'O que cai de Bioacumulação em Tecido Adiposo',
    subtitulo: 'Mesma lógica da magnificação trófica que você já viu em Ecologia, só que aplicada dentro do corpo.',
    topicos: [
      {
        titulo: 'Lipossolúvel acumula em gordura',
        descricao:
          'Substância que se dissolve em gordura (não em água) não é eliminada fácil pela urina -- o corpo guarda no tecido adiposo',
        frequencia: 'alta',
      },
      {
        titulo: 'Bioacumulação x Magnificação trófica',
        descricao:
          'Bioacumulação: acumula DENTRO de um organismo ao longo do tempo. Magnificação trófica: acumula AO LONGO da cadeia alimentar -- não confundir os dois nomes',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: 'novo',
    estatisticaTexto: 'padrão adicionado a partir da classificação de questões oficiais (ver docs/pesquisa_estrategia_de_prova.md).',
  },
  3: {
    minutos: 2,
    titulo: 'O que cai de Fibras Musculares',
    subtitulo: 'Distinção binária, tipo tabela: fibra lenta x fibra rápida.',
    topicos: [
      {
        titulo: 'Fibra Lenta (vermelha)',
        descricao: 'Muita mitocôndria, bem irrigada, metabolismo AERÓBICO -- favorece esporte de LONGA duração (maratona, ciclismo de estrada)',
        frequencia: 'alta',
      },
      {
        titulo: 'Fibra Rápida (branca)',
        descricao: 'Pouca mitocôndria, metabolismo ANAERÓBICO -- favorece esporte de EXPLOSÃO curta (salto, levantamento de peso, sprint)',
        frequencia: 'alta',
      },
    ],
    estatisticaNumero: 'novo',
    estatisticaTexto: 'padrão adicionado a partir da classificação de questões oficiais (ver docs/pesquisa_estrategia_de_prova.md).',
  },
};

/**
 * Ponte entre RESUMOS_FASE_ECOLOGIA (chave = número da fase) e a
 * trilha fixa entrelaçada (`core/db.py TRILHA_FIXA_NOS`, chave =
 * string tipo 'ecologia_poluicao_atmosferica') -- é o que faltava pra
 * "plugar" o comentário de RESUMOS_FASE_ECOLOGIA acima
 * ("ainda NÃO está plugado em trilha-path.tsx/index.tsx"). Cada nó da
 * trilha fixa já tem sua própria `chave` estável (ver
 * NoTrilhaFixa['chave'] em lib/api.ts); mapear POR ELA em vez de por
 * `materia` evita colidir com RESUMOS_TRILHA (que é indexado por
 * matéria inteira, não por fase) e funciona mesmo pra um nó que
 * combina mais de uma matéria (ex: 'optica_ondulatoria' juntando
 * óptica + acústica).
 *
 * 'optica_ondulatoria_1/2/3' apontam pra RESUMOS_FASE_OPTICA -- só
 * existem aqui explicitamente porque o `nome` de exibição de cada nó
 * (ex: "Óptica/Ondulatória — Polarização e Difração") nunca bateria
 * com nenhuma chave de RESUMOS_TRILHA (mesmo bug que a Ecologia tinha,
 * achado ao vivo pelo usuário -- ver
 * docs/pesquisa_estrategia_de_prova.md §8): sem esta entrada, "Rever
 * conteúdo base" nunca apareceria em Óptica/Ondulatória.
 *
 * Um nó sem entrada aqui cai pro fallback por matéria em index.tsx
 * (RESUMOS_TRILHA[materia]), que também pode não ter nada, e aí a
 * tela de Apresentação simplesmente não aparece pra esse nó, mesmo
 * comportamento de sempre.
 */
export const RESUMOS_POR_CHAVE_TRILHA_FIXA: Record<string, ResumoTrilha> = {
  ecologia_poluicao_atmosferica: RESUMOS_FASE_ECOLOGIA[4],
  ecologia_relacoes_harmonicas: RESUMOS_FASE_ECOLOGIA[2],
  ecologia_relacoes_desarmonicas: RESUMOS_FASE_ECOLOGIA[7],
  ecologia_populacao_sucessao: RESUMOS_FASE_ECOLOGIA[8],
  optica_ondulatoria_1: RESUMOS_FASE_OPTICA[1],
  optica_ondulatoria_2: RESUMOS_FASE_OPTICA[2],
  optica_ondulatoria_3: RESUMOS_FASE_OPTICA[3],
  cinematica_mruv: RESUMOS_FASE_CINEMATICA[2],
  cinematica_lancamento_horizontal: RESUMOS_FASE_CINEMATICA[3],
  fisiologia_bioacumulacao: RESUMOS_FASE_FISIOLOGIA_HUMANA[2],
  fisiologia_fibras_musculares: RESUMOS_FASE_FISIOLOGIA_HUMANA[3],
};
