import {
  cabecalhosAutenticacao,
  caminhoVariacaoMolde,
  definirTelaAtual,
  registrarEvento,
  registrarTentativa,
  telaDoCaminho,
  urlImagemEnunciado,
} from './api';

describe('telaDoCaminho', () => {
  it('tira a query e fica so com a rota', () => {
    expect(telaDoCaminho('/trilha?grande_area=matematica&materia=x')).toBe('/trilha');
  });

  it('remove caractere que o backend recusa', () => {
    expect(telaDoCaminho('/Simulado <>')).toBe('/simulado');
  });

  it('vazio vira a raiz', () => {
    expect(telaDoCaminho('')).toBe('/');
  });
});

describe('registrarEvento', () => {
  const fetchOriginal = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = fetchOriginal;
  });

  it('manda tipo e tela para /eventos', () => {
    const chamado = jest.fn().mockResolvedValue({ ok: true });
    globalThis.fetch = chamado as unknown as typeof fetch;
    registrarEvento('tela_vista', '/simulado');
    const [url, opcoes] = chamado.mock.calls[0];
    expect(url).toBe('http://localhost:8000/eventos');
    expect(opcoes.method).toBe('POST');
    expect(JSON.parse(opcoes.body)).toEqual({ tipo: 'tela_vista', tela: '/simulado' });
  });

  it('POST que falha manda evento de erro com a tela do app, nao o endpoint', async () => {
    const chamado = jest.fn().mockResolvedValue({ ok: false, status: 500 });
    globalThis.fetch = chamado as unknown as typeof fetch;
    definirTelaAtual('/simulado');
    await expect(registrarTentativa('2024_azul_136', 'A')).rejects.toThrow('500');
    const evento = chamado.mock.calls.find(([url]) => String(url).endsWith('/eventos'));
    expect(JSON.parse(evento![1].body)).toEqual({ tipo: 'erro', tela: '/simulado' });
  });

  it('401 nao vira evento (sem codigo valido nao ha banco onde gravar)', async () => {
    const chamado = jest.fn().mockResolvedValue({ ok: false, status: 401 });
    globalThis.fetch = chamado as unknown as typeof fetch;
    await expect(registrarTentativa('2024_azul_136', 'A')).rejects.toThrow('401');
    expect(chamado.mock.calls.some(([url]) => String(url).endsWith('/eventos'))).toBe(false);
  });

  it('nunca lanca erro, nem com a rede fora', async () => {
    globalThis.fetch = jest.fn().mockRejectedValue(new Error('sem rede')) as unknown as typeof fetch;
    expect(() => registrarEvento('app_aberto')).not.toThrow();
    await Promise.resolve();
  });
});

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

describe('urlImagemEnunciado', () => {
  it('usa so o nome do arquivo, mesmo com caminho absoluto do Windows', () => {
    expect(urlImagemEnunciado('C:\\Users\\x\\core\\enunciados\\2019_azul_91.png')).toBe(
      'http://localhost:8000/enunciados/2019_azul_91.png',
    );
  });

  it('sem caminho devolve null', () => {
    expect(urlImagemEnunciado(null)).toBeNull();
  });
});
