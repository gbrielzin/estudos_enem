/**
 * Equivalente TypeScript de _separar_alternativas_banco_pratica em
 * core/cartao_resposta.py, estendido para as provas OFICIAIS. Confia só
 * nas ÚLTIMAS 5 linhas não-vazias, na ordem estrita A,B,C,D,E (protege
 * contra um enunciado fora do formato -- nesse caso devolve o texto
 * inteiro sem separar nada, degradando para texto corrido).
 *
 * Três formatos aceitos, todos vistos no banco:
 *   - "A) texto"   -- banco de prática (importar_questoes_praticas_texto)
 *   - "A\t texto"  -- prova extraída do PDF (extrair_enunciados_pdf.py, ~650
 *                     questões). O PDF ainda deixa a letra da PRÓXIMA
 *                     alternativa no fim da linha ("... esgoto. C"), a letra
 *                     "A" no fim do enunciado ("... é o(a) A") e, às vezes,
 *                     uma linha só com a letra antes da alternativa: os três
 *                     restos são removidos aqui.
 *   - "A  texto"   -- prova vinda da API enem.dev (~300 questões)
 * Antes de tudo, tira as linhas de rodapé/marca-d'água do PDF.
 */

const LETRAS = ['A', 'B', 'C', 'D', 'E'] as const;
const PADROES = [/^([A-E])\)\s*(.+)$/, /^([A-E])\t\s*(.+)$/, /^([A-E])\s+(.+)$/];
const SO_A_LETRA = /^[A-E]$/;
// Rodapé e marca-d'água que a extração do PDF deixou no meio do texto:
// "ENEM 2022 ENEM 2022 ...", "2025ENEM2025ENEM...", "5 CN • 2º DIA • CADERNO 6 • CINZA",
// "MATEMÁTICA E SUAS TECNOLOGIAS | 2º DIA | CADERNO 7 | AZUL 19".
const LINHA_DE_RODAPE = [/(ENEM\s?\d{4}\s*){3,}/i, /(\d{4}\s?ENE[MN]\s?){3,}/i, /\bDIA\b.*\bCADERNO\b/i];

/** Tira do texto as linhas que são rodapé/marca-d'água do PDF da prova. */
export function limparRodapePdf(texto: string): string {
  return texto
    .split('\n')
    .filter((linha) => !LINHA_DE_RODAPE.some((padrao) => padrao.test(linha)))
    .join('\n');
}

export interface AlternativasSeparadas {
  corpo: string;
  alternativas: Partial<Record<'A' | 'B' | 'C' | 'D' | 'E', string>>;
}

function separarComPadrao(linhas: string[], padrao: RegExp, formatoPdf: boolean): AlternativasSeparadas | null {
  const ultimasCinco = linhas.slice(-5);
  const alternativas: AlternativasSeparadas['alternativas'] = {};
  for (let i = 0; i < 5; i++) {
    const match = padrao.exec(ultimasCinco[i].trim());
    if (!match || match[1] !== LETRAS[i]) return null;
    let texto = match[2].trim();
    // Só o PDF gruda a letra seguinte no fim; nos outros formatos, um "ponto B" é texto de verdade.
    if (formatoPdf && i < 4) texto = texto.replace(new RegExp(`\\s+${LETRAS[i + 1]}$`), '');
    alternativas[LETRAS[i]] = texto;
  }
  return { corpo: linhas.slice(0, -5).join('\n').trim(), alternativas };
}

export function separarAlternativas(textoOriginal: string): AlternativasSeparadas {
  const texto = limparRodapePdf(textoOriginal);
  const naoVazias = texto.split('\n').filter((linha) => linha.trim().length > 0);
  const semLetraSolta = naoVazias.filter((linha) => !SO_A_LETRA.test(linha.trim()));

  for (const [indice, padrao] of PADROES.entries()) {
    // O formato "A) texto" do banco de prática nunca tem letra solta;
    // só os das provas oficiais.
    const linhas = indice === 0 ? naoVazias : semLetraSolta;
    if (linhas.length < 5) continue;
    const separado = separarComPadrao(linhas, padrao, indice === 1);
    if (separado) {
      if (indice === 1) separado.corpo = separado.corpo.replace(/\s+A$/, '');
      return separado;
    }
  }
  return { corpo: texto, alternativas: {} };
}
