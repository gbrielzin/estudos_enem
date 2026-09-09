/**
 * Equivalente TypeScript de _separar_alternativas_banco_pratica em
 * core/cartao_resposta.py. O enunciado_texto de uma questão do banco
 * de prática SEMPRE termina com as 5 alternativas no formato
 * "A) texto" (ver importar_questoes_praticas_texto em core/db.py, que
 * monta esse formato na hora de gravar) -- confia só nas ÚLTIMAS 5
 * linhas não-vazias, na ordem estrita A,B,C,D,E, mesma rede de
 * segurança do lado Python (protege contra um enunciado editado na
 * mão fora do formato -- nesse caso devolve o texto inteiro sem
 * separar nada, degradando pra exibição de texto corrido).
 */

const PADRAO_ALTERNATIVA = /^([A-E])\)\s*(.+)$/;

export interface AlternativasSeparadas {
  corpo: string;
  alternativas: Partial<Record<'A' | 'B' | 'C' | 'D' | 'E', string>>;
}

export function separarAlternativas(texto: string): AlternativasSeparadas {
  const linhas = texto.split('\n').filter((linha) => linha.trim().length > 0);
  if (linhas.length < 5) {
    return { corpo: texto, alternativas: {} };
  }

  const letrasEsperadas = ['A', 'B', 'C', 'D', 'E'] as const;
  const ultimasCinco = linhas.slice(-5);
  const alternativas: AlternativasSeparadas['alternativas'] = {};

  for (let i = 0; i < 5; i++) {
    const match = PADRAO_ALTERNATIVA.exec(ultimasCinco[i].trim());
    if (!match || match[1] !== letrasEsperadas[i]) {
      return { corpo: texto, alternativas: {} };
    }
    alternativas[letrasEsperadas[i]] = match[2].trim();
  }

  const corpo = linhas.slice(0, -5).join('\n').trim();
  return { corpo, alternativas };
}
