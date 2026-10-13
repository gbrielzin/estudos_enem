import { curvaSaida, valorNoInstante } from './numero-sobe';

describe('curvaSaida', () => {
  it('começa em 0, termina em 1 e corre mais no começo', () => {
    expect(curvaSaida(0)).toBe(0);
    expect(curvaSaida(1)).toBe(1);
    // na metade do tempo já passou bem da metade do caminho
    expect(curvaSaida(0.5)).toBeGreaterThan(0.8);
  });

  it('prende t fora de 0..1', () => {
    expect(curvaSaida(-1)).toBe(0);
    expect(curvaSaida(2)).toBe(1);
  });
});

describe('valorNoInstante', () => {
  it('vai de 0 até o alvo exato', () => {
    expect(valorNoInstante(612, 0)).toBe(0);
    expect(valorNoInstante(612, 1)).toBe(612);
  });

  it('é sempre inteiro e nunca passa do alvo', () => {
    for (let i = 0; i <= 20; i++) {
      const v = valorNoInstante(37, i / 20);
      expect(Number.isInteger(v)).toBe(true);
      expect(v).toBeLessThanOrEqual(37);
    }
  });

  it('nunca desce enquanto o tempo anda', () => {
    let anterior = -1;
    for (let i = 0; i <= 30; i++) {
      const v = valorNoInstante(45, i / 30);
      expect(v).toBeGreaterThanOrEqual(anterior);
      anterior = v;
    }
  });

  it('alvo 0 fica em 0', () => {
    expect(valorNoInstante(0, 0.5)).toBe(0);
  });
});
