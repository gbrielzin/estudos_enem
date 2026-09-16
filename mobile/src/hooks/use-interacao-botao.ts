import { useEffect, useRef, useState } from 'react';
import { Animated, Easing } from 'react-native';

/**
 * "Botão afunda" -- padrão de movimento 6a do projeto de design
 * (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de animação",
 * card "Botão afunda"): 160ms, desce até a espessura da sombra 3D
 * (5px por padrão, mesmo valor de `quedaPressionado`), com uma curva
 * de sobra elástica na chegada (`cubic-bezier(.34,1.5,.64,1)` no
 * design -- o "1.5" no 2º ponto é o que dá a pequena ultrapassagem).
 * Só translateY, sem escala -- o design separa isso do padrão "Acerto
 * estufa" (que aí sim faz overshoot de escala), não confundir os dois.
 *
 * Web ganha de graça um extra que NÃO está no design (que é
 * mobile-first, sem conceito de mouse -- pedido à parte do usuário
 * "que nem no Duolingo"): passar o cursor por cima já levanta 2px, só
 * quando existe hover de verdade. `onHoverIn`/`onHoverOut` nunca
 * disparam em touch puro (celular), então lá só o apertar anima.
 */
const CURVA_AFUNDA = Easing.bezier(0.34, 1.5, 0.64, 1);

export function useInteracaoBotao({
  desativado = false,
  quedaPressionado = 5,
}: { desativado?: boolean; quedaPressionado?: number } = {}) {
  const [hover, setHover] = useState(false);
  const [pressionado, setPressionado] = useState(false);
  const deslocamentoY = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (desativado) return;
    const alvo = pressionado ? quedaPressionado : hover ? -2 : 0;
    Animated.timing(deslocamentoY, {
      toValue: alvo,
      duration: pressionado ? 160 : 220,
      easing: CURVA_AFUNDA,
      // false, não true: este MESMO deslocamentoY também alimenta
      // interpolarSombraBotao() abaixo, que produz um `boxShadow`
      // (style não suportado pelo driver nativo do Animated) -- misturar
      // native driver num valor que também dirige um style não-nativo
      // gera o aviso "style property 'boxShadow' is not supported by
      // native animated module" no console (funciona mesmo assim, mas
      // suja o log). Roda tudo em JS aqui; é uma animação de ~200ms, sem
      // impacto perceptível de performance.
      useNativeDriver: false,
    }).start();
  }, [hover, pressionado, desativado, quedaPressionado, deslocamentoY]);

  return {
    deslocamentoY,
    handlers: {
      onHoverIn: () => setHover(true),
      onHoverOut: () => {
        setHover(false);
        setPressionado(false);
      },
      onPressIn: () => setPressionado(true),
      onPressOut: () => setPressionado(false),
    },
  };
}

/**
 * Segunda metade do mesmo padrão "botão afunda": a sombra 3D (`box-
 * shadow` sólido, sem blur -- suportado nativamente por esta versão
 * de RN, ver docstring de components/mascote.tsx) encolhe pela MESMA
 * distância que o botão desce, sempre sobrando 1px (nunca fica
 * rente/achatada) -- é o mesmo `deslocamentoY` de `useInteracaoBotao`
 * reaproveitado, os dois nascem do mesmo gesto de apertar.
 */
export function interpolarSombraBotao(deslocamentoY: Animated.Value, corSombra: string, profundidadeRepouso = 6) {
  return deslocamentoY.interpolate({
    inputRange: [0, profundidadeRepouso - 1],
    outputRange: [`0 ${profundidadeRepouso}px 0 ${corSombra}`, `0 1px 0 ${corSombra}`],
    extrapolate: 'clamp',
  });
}
