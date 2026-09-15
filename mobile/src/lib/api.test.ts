import { cabecalhosAutenticacao } from './api';

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
