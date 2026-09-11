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
