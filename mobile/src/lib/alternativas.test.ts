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

  it('prova do PDF: tira a letra da proxima alternativa e o A do fim do enunciado', () => {
    const texto =
      'Uma medida profilática comum a essas duas doenças é o(a) A\n' +
      'A\t incineração do lixo orgânico. B\n' +
      'B\t construção de rede de esgoto. C\n' +
      'C\t uso de vermífugo pela população. D\n' +
      'D\t controle das populações dos vetores. E\n' +
      'E\t consumo de carnes vermelhas bem cozidas.';

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe('Uma medida profilática comum a essas duas doenças é o(a)');
    expect(alternativas).toEqual({
      A: 'incineração do lixo orgânico.',
      B: 'construção de rede de esgoto.',
      C: 'uso de vermífugo pela população.',
      D: 'controle das populações dos vetores.',
      E: 'consumo de carnes vermelhas bem cozidas.',
    });
  });

  it('prova do PDF com a letra sozinha numa linha antes de cada alternativa', () => {
    const texto = ['O sucesso dessa terapia advém de A', 'A\t um.', 'B', 'B\t dois.', 'C', 'C\t três.', 'D', 'D\t quatro.', 'E', 'E\t cinco.'].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe('O sucesso dessa terapia advém de');
    expect(alternativas).toEqual({ A: 'um.', B: 'dois.', C: 'três.', D: 'quatro.', E: 'cinco.' });
  });

  it('prova da enem.dev: letra, espacos e o texto', () => {
    const texto = ['Qual caixa?', 'A  5 caixas do tipo A.', 'B  1 caixa', 'C  3 caixas', 'D  5 caixas', 'E  6 caixas do tipo B.'].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe('Qual caixa?');
    expect(alternativas.A).toBe('5 caixas do tipo A.');
    expect(alternativas.E).toBe('6 caixas do tipo B.');
  });

  it('ignora rodape e marca-dagua do PDF no fim do texto', () => {
    const texto = [
      'Quanto vale?',
      'A\t 1. B',
      'B\t 2. C',
      'C\t 3. D',
      'D\t 4. E',
      'E\t 5.',
      '',
      'CN - 2° dia | Caderno 7 - AZUL - 1ª Aplicação 9 ENEM 2022 ENEM 2022 ENEM 2022 ENEM 2022',
      '5 CN • 2º DIA • CADERNO 6 • CINZA',
    ].join('\n');

    const { corpo, alternativas } = separarAlternativas(texto);

    expect(corpo).toBe('Quanto vale?');
    expect(alternativas.E).toBe('5.');
  });
});

