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
export const RESUMOS_TRILHA: Record<string, ResumoTrilha> = {
  optica: {
    minutos: 2,
    titulo: 'O que cai de Óptica',
    subtitulo:
      'Óptica é a parte da Física que estuda a luz: como ela se reflete, se desvia e forma imagens.',
    topicos: [
      {
        titulo: 'Espelhos e lentes',
        descricao: 'Equação de Gauss, aumento, imagem real ou virtual',
        frequencia: 'alta',
      },
      {
        titulo: 'Refração',
        descricao: 'Lei de Snell, índice de refração, reflexão total',
        frequencia: 'alta',
      },
      {
        titulo: 'Olho humano',
        descricao: 'Miopia, hipermetropia e a lente que corrige cada uma',
        frequencia: 'media',
      },
    ],
    estatisticaNumero: '2',
    estatisticaTexto: 'questões de Óptica por prova, em média, nos últimos cinco anos do ENEM.',
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
