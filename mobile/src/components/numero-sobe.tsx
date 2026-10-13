import { useEffect, useState } from 'react';
import { AccessibilityInfo, StyleProp, Text, TextStyle } from 'react-native';

import { DURACAO_NUMERO_SOBE_MS, valorNoInstante } from '@/lib/numero-sobe';

/**
 * "Número sobe": o número conta de 0 até `valor` quando a tela abre
 * (a conta está em lib/numero-sobe.ts). Usado no placar do simulado.
 *
 * Roda num laço de requestAnimationFrame em vez de Animated: o que
 * muda é o TEXTO, não um estilo, e Animated não interpola texto. São
 * ~54 quadros e o resto da tela está parado, então re-renderizar só
 * este <Text> não pesa.
 *
 * Com "reduzir movimento" ligado no aparelho, mostra o valor final
 * direto, sem contar. O leitor de tela sempre recebe o valor final
 * (accessibilityLabel), nunca os números intermediários.
 */
export function NumeroSobe({
  valor,
  sufixo = '',
  style,
}: {
  valor: number;
  sufixo?: string;
  style?: StyleProp<TextStyle>;
}) {
  const [exibido, setExibido] = useState(0);

  useEffect(() => {
    let quadro = 0;
    let cancelado = false;

    AccessibilityInfo.isReduceMotionEnabled()
      .catch(() => false)
      .then((reduzir) => {
        if (cancelado) return;
        if (reduzir) {
          setExibido(valor);
          return;
        }
        const inicio = Date.now();
        const passo = () => {
          const t = (Date.now() - inicio) / DURACAO_NUMERO_SOBE_MS;
          setExibido(valorNoInstante(valor, t));
          if (t < 1) quadro = requestAnimationFrame(passo);
        };
        quadro = requestAnimationFrame(passo);
      });

    return () => {
      cancelado = true;
      cancelAnimationFrame(quadro);
    };
  }, [valor]);

  return (
    <Text style={style} accessibilityLabel={`${valor}${sufixo}`}>
      {exibido}
      {sufixo}
    </Text>
  );
}
