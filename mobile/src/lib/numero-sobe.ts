/**
 * Conta do "Número sobe" (components/numero-sobe.tsx), separada do
 * componente pra dar pra testar sem renderizar nada.
 *
 * Ideia tirada da live do PC (Money Flow, 2026-10): o saldo "rolando
 * igual número de cassino" quando aparece. Aqui é o placar do simulado
 * (acertos e nota TRI) subindo de 0 até o valor real.
 *
 * Curva: saída rápida e chegada lenta (cúbica), a mesma família do
 * "Barra enche" (barra-progresso.tsx). O número corre no começo e
 * desacelera perto do fim, então o olho consegue ler o valor final
 * antes de ele parar.
 */

export const DURACAO_NUMERO_SOBE_MS = 900;

/** Cúbica de saída: 0 → 0, 1 → 1, rápida no começo. */
export function curvaSaida(t: number): number {
  const p = Math.min(1, Math.max(0, t));
  return 1 - Math.pow(1 - p, 3);
}

/**
 * Valor exibido no instante `t` (0 a 1) de uma contagem até `alvo`.
 * Sempre inteiro e nunca passa do alvo; em `t >= 1` é exatamente o alvo.
 */
export function valorNoInstante(alvo: number, t: number): number {
  if (t >= 1) return alvo;
  return Math.min(alvo, Math.round(alvo * curvaSaida(t)));
}
