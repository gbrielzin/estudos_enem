import { useEffect, useRef, useState } from 'react';
import { Animated, Easing, StyleSheet, View } from 'react-native';

import { Brand } from '@/constants/brand';

/**
 * "Barra enche" -- padrão de movimento 6a do projeto de design
 * (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de animação"):
 * 420ms, saída rápida e chegada lenta, mais um brilho que atravessa
 * UMA VEZ a barra preenchida pro olho acompanhar até o novo fim.
 * Reusa a MESMA barra que já existia em missoes-card.tsx e explore.tsx
 * (fundo escuro + preenchimento colorido, cantos arredondados) -- só
 * trocou o `<View style={{width: pct%}}>` estático por isso.
 *
 * O brilho é um retângulo branco semi-transparente que desliza (sem
 * gradiente de verdade -- este projeto não tem `expo-linear-gradient`
 * como dependência, e não vale a pena adicionar uma lib só por isto),
 * com fade-in/fade-out na opacidade nas pontas pra suavizar a borda
 * dura em vez de um corte seco. Desliza em PIXELS reais (medidos via
 * `onLayout`), não em porcentagem -- suporte a `transform: [{
 * translateX: '10%' }]` (percentual) é recente/incerto nesta versão
 * de RN, então evitei depender disso (mesma cautela do AGENTS.md deste
 * projeto: checar em vez de supor).
 */
export function BarraProgresso({ pct, cor, altura = 11 }: { pct: number; cor: string; altura?: number }) {
  const [largura, setLargura] = useState(0);
  const progresso = useRef(new Animated.Value(0)).current;
  const brilho = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(progresso, { toValue: pct, duration: 420, easing: Easing.out(Easing.cubic), useNativeDriver: false }).start();
    brilho.setValue(0);
    // false, não true: `progresso` (acima) já roda em JS de propósito
    // (anima `width` em %, propriedade não suportada pelo driver
    // nativo) -- rodar `brilho` em native driver AO MESMO TEMPO, no
    // mesmo componente, é o que disparava "Attempting to run JS
    // driven animation on animated node that has been moved to
    // 'native' earlier" no New Architecture (Fabric) desta versão de
    // RN/Expo (achado ao vivo: tela de questão travava com esse erro
    // assim que a barra de progresso entrava em cena). Manter TODO
    // Animated.timing deste app em `false` evita misturar os dois
    // modos na mesma árvore de render -- ver mesmo raciocínio já
    // aplicado em use-interacao-botao.ts.
    Animated.timing(brilho, { toValue: 1, duration: 420, delay: 60, easing: Easing.out(Easing.quad), useNativeDriver: false }).start();
  }, [pct, progresso, brilho]);

  const larguraAnimada = progresso.interpolate({ inputRange: [0, 100], outputRange: ['0%', '100%'] });
  const larguraBrilho = Math.max(24, largura * 0.3);
  const translateX = brilho.interpolate({ inputRange: [0, 1], outputRange: [-larguraBrilho, largura + larguraBrilho] });
  const opacidade = brilho.interpolate({ inputRange: [0, 0.15, 0.85, 1], outputRange: [0, 0.55, 0.55, 0] });

  return (
    <View style={[styles.fundo, { height: altura }]} onLayout={(e) => setLargura(e.nativeEvent.layout.width)}>
      <Animated.View style={[styles.preenchido, { height: altura, width: larguraAnimada, backgroundColor: cor }]}>
        {largura > 0 && (
          <Animated.View
            style={[
              styles.brilho,
              { height: altura, width: larguraBrilho, opacity: opacidade, transform: [{ translateX }] },
            ]}
          />
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  fundo: {
    borderRadius: 999,
    backgroundColor: Brand.bordaForte,
    overflow: 'hidden',
  },
  preenchido: {
    borderRadius: 999,
    overflow: 'hidden',
  },
  brilho: {
    position: 'absolute',
    top: 0,
    backgroundColor: '#FFFFFF',
  },
});
