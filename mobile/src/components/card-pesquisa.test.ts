import { devePerguntar } from './card-pesquisa';

describe('devePerguntar', () => {
  it('pergunta para quem nunca respondeu', () => {
    expect(devePerguntar(null)).toBe(true);
  });

  it('nao pergunta de novo antes de 7 dias', () => {
    expect(devePerguntar(5.9)).toBe(false);
  });

  it('pergunta de novo a partir de 7 dias', () => {
    expect(devePerguntar(7)).toBe(true);
  });
});
