import { devePerguntar } from './card-pesquisa';

describe('devePerguntar', () => {
  const agora = new Date('2026-10-20T12:00:00');

  it('pergunta para quem nunca respondeu', () => {
    expect(devePerguntar(null, agora)).toBe(true);
  });

  it('nao pergunta de novo antes de 7 dias', () => {
    expect(devePerguntar('2026-10-15 12:00:00', agora)).toBe(false);
  });

  it('pergunta de novo depois de 7 dias', () => {
    expect(devePerguntar('2026-10-13 11:00:00', agora)).toBe(true);
  });

  it('data estranha nao trava a pesquisa', () => {
    expect(devePerguntar('ontem', agora)).toBe(true);
  });
});
