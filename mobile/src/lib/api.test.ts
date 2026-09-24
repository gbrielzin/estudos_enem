import { cabecalhosAutenticacao, caminhoVariacaoMolde } from './api';

describe('cabecalhosAutenticacao', () => {
  const originalEnv = process.env.EXPO_PUBLIC_API_AUTH_TOKEN;

  afterEach(() => {
    process.env.EXPO_PUBLIC_API_AUTH_TOKEN = originalEnv;
  });

  it('nao manda header nenhum quando a variavel nao esta configurada', () => {
    delete process.env.EXPO_PUBLIC_API_AUTH_TOKEN;
    expect(cabecalhosAutenticacao()).toEqual({});
  });

  it('manda Authorization Bearer quando a variavel esta configurada', () => {
    process.env.EXPO_PUBLIC_API_AUTH_TOKEN = 'segredo-de-teste';
    expect(cabecalhosAutenticacao()).toEqual({ Authorization: 'Bearer segredo-de-teste' });
  });
});

describe('caminhoVariacaoMolde', () => {
  it('manda a seed quando nao pede o original', () => {
    expect(caminhoVariacaoMolde('frenagem', { seed: 7 })).toBe('/moldes/frenagem/variacao?seed=7');
  });

  it('original ignora a seed', () => {
    expect(caminhoVariacaoMolde('aquario', { seed: 7, original: true })).toBe('/moldes/aquario/variacao?original=true');
  });

  it('sem opcoes nao manda query', () => {
    expect(caminhoVariacaoMolde('carro_eletrico')).toBe('/moldes/carro_eletrico/variacao');
  });
});
