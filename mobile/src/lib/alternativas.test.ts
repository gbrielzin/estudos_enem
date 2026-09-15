import { separarAlternativas } from './alternativas';

describe('separarAlternativas', () => {
  it('separa corpo e alternativas quando as ultimas 5 linhas sao A-E em ordem', () => {
    const texto = [
      'Qual o resultado de 2 + 2?',
      '',
      'A) 3',
      'B) 4',
      'C) 5',
      'D) 6',
      'E) 7',
    ].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe('Qual o resultado de 2 + 2?');
    expect(alternativas).toEqual({ A: '3', B: '4', C: '5', D: '6', E: '7' });
  });

  it('degrada pro texto inteiro sem separar quando falta uma alternativa', () => {
    const texto = ['Enunciado', 'A) x', 'B) y', 'C) z', 'D) w'].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe(texto);
    expect(alternativas).toEqual({});
  });

  it('degrada pro texto inteiro quando a ordem das letras nao e A,B,C,D,E', () => {
    // mesmo caso que extrair_figuras_pdf.py trata do lado Python:
    // questao com alternativas em diagrama pode nao vir em ordem A->E.
    const texto = [
      'Enunciado',
      'B) primeira',
      'A) segunda',
      'C) terceira',
      'D) quarta',
      'E) quinta',
    ].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe(texto);
    expect(alternativas).toEqual({});
  });

  it('ignora linhas em branco no meio do enunciado ao contar as ultimas 5', () => {
    const texto = [
      'Primeira parte do enunciado.',
      '',
      'Segunda parte, depois de uma linha em branco.',
      '',
      'A) opcao 1',
      'B) opcao 2',
      'C) opcao 3',
      'D) opcao 4',
      'E) opcao 5',
    ].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe(
      'Primeira parte do enunciado.\nSegunda parte, depois de uma linha em branco.'
    );
    expect(alternativas.A).toBe('opcao 1');
    expect(alternativas.E).toBe('opcao 5');
  });

  it('nao separa nada quando o texto tem menos de 5 linhas', () => {
    const texto = 'A) unica\nB) linha';

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe(texto);
    expect(alternativas).toEqual({});
  });
});
