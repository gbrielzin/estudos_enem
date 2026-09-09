import { Feather, Ionicons } from '@expo/vector-icons';
import { useEffect, useRef } from 'react';
import { Animated, Easing, Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import { Mascote } from '@/components/mascote';
import { Brand, Fontes } from '@/constants/brand';
import { Spacing } from '@/constants/theme';
import { NoTrilha } from '@/lib/api';

const AMPLITUDE = 80;
const ESPACAMENTO_VERTICAL = 130;
const DIAMETRO_NO_ATUAL = 78;
const DIAMETRO_NO_PADRAO = 70;
const ALTURA_SOMBRA = 7;
const PADDING_TOPO = 50;

interface TrilhaPathProps {
  trilha: NoTrilha[];
  onAbrirNo: (no: NoTrilha) => void;
}

/**
 * Trilha serpenteada estilo Duolingo, visual importado do projeto de
 * design do usuário no Claude Design ("App ENEM.dc.html", tela
 * "Trilha" -- ver DesignSync, projectId 669f9530-e4b9-4dfb-ab2c-
 * cd90df9199b4): curva SVG pontilhada conectando os nós (bezier
 * cúbica, ponto de controle no Y do meio de cada segmento), nós com
 * sombra sólida 3D (duas camadas empilhadas -- CSS box-shadow de
 * offset sólido não existe em React Native), e o mascote "Pipo" de
 * verdade (mobile/src/components/mascote.tsx, porta de
 * Mascote.dc.html) flutuando ao lado -- substituindo o placeholder
 * anterior.
 */
export function TrilhaPath({ trilha, onAbrirNo }: TrilhaPathProps) {
  const { width: larguraTela } = useWindowDimensions();
  const larguraContainer = larguraTela - Spacing.four * 2;
  const centroX = larguraContainer / 2;

  const pontos = trilha.map((_, i) => ({
    x: centroX + Math.sin((i * Math.PI) / 2.5) * AMPLITUDE,
    y: PADDING_TOPO + i * ESPACAMENTO_VERTICAL,
  }));
  const alturaTotal = PADDING_TOPO * 2 + Math.max(0, trilha.length - 1) * ESPACAMENTO_VERTICAL;

  let caminhoD = '';
  if (pontos.length > 0) {
    caminhoD = `M ${pontos[0].x} ${pontos[0].y}`;
    for (let i = 1; i < pontos.length; i++) {
      const p0 = pontos[i - 1];
      const p1 = pontos[i];
      const meioY = (p0.y + p1.y) / 2;
      caminhoD += ` C ${p0.x} ${meioY}, ${p1.x} ${meioY}, ${p1.x} ${p1.y}`;
    }
  }

  const indiceAtual = trilha.findIndex((n) => n.desbloqueado && !n.concluido);
  const indiceMascote = Math.min(2, trilha.length - 1);
  const pontoMascote = pontos[indiceMascote];

  return (
    <View style={[styles.container, { width: larguraContainer, height: alturaTotal }]}>
      <Svg style={StyleSheet.absoluteFill} width={larguraContainer} height={alturaTotal}>
        <Path d={caminhoD} stroke={Brand.bordaForte} strokeWidth={12} fill="none" strokeLinecap="round" strokeDasharray="1 26" />
      </Svg>

      {pontoMascote && (
        <View style={[styles.mascoteSlot, { left: Math.min(larguraContainer - 82, pontoMascote.x + 70), top: pontoMascote.y - 30 }]}>
          <Mascote color={Brand.branco} shadow={Brand.brancoEscuro} beak={Brand.rosa} mood="happy" size={0.78} />
          <Text style={styles.mascoteTag}>Pipo</Text>
        </View>
      )}

      {trilha.map((no, i) => {
        const { x, y } = pontos[i];
        const ehAtual = i === indiceAtual;
        const diametro = ehAtual ? DIAMETRO_NO_ATUAL : DIAMETRO_NO_PADRAO;
        const jaComecou = no.questoes.some((q) => q.ja_respondida);
        const rotuloAtual = no.concluido ? 'REPETIR' : jaComecou ? 'CONTINUAR' : 'COMEÇAR';

        return (
          <View key={no.indice} style={[styles.no, { left: x - diametro / 2, top: y - diametro / 2, width: diametro }]}>
            {ehAtual && (
              <View style={styles.flag}>
                <Text style={styles.flagTexto}>{rotuloAtual}</Text>
              </View>
            )}
            <NoCirculo no={no} ehAtual={ehAtual} diametro={diametro} onPress={() => onAbrirNo(no)} />
            <Text style={styles.legenda}>
              Nó {no.indice + 1} · {no.questoes.length}q
            </Text>
          </View>
        );
      })}
    </View>
  );
}

function NoCirculo({ no, ehAtual, diametro, onPress }: { no: NoTrilha; ehAtual: boolean; diametro: number; onPress: () => void }) {
  const escala = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!ehAtual) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(escala, { toValue: 1.08, duration: 700, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(escala, { toValue: 1, duration: 700, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [ehAtual, escala]);

  const corFundo = no.concluido ? Brand.ouro : ehAtual ? Brand.verde : '#1F2531';
  const corSombra = no.concluido ? '#8A6300' : ehAtual ? Brand.verdeEscuro : '#14181F';
  const corIcone = no.concluido ? '#3A2C00' : ehAtual ? '#0D2705' : Brand.textoMuted;
  const raio = diametro / 2;

  return (
    <Pressable disabled={!no.desbloqueado} onPress={onPress} style={{ width: diametro, height: diametro + ALTURA_SOMBRA }}>
      {/* camada de baixo = "sombra" sólida, cria o efeito de botão 3D pressionado */}
      <View style={[styles.circuloSombra, { top: ALTURA_SOMBRA, width: diametro, height: diametro, borderRadius: raio, backgroundColor: corSombra }]} />
      <Animated.View
        style={[
          styles.circulo,
          { width: diametro, height: diametro, borderRadius: raio, backgroundColor: corFundo },
          !no.desbloqueado && styles.circuloBloqueadoBorda,
          ehAtual && { transform: [{ scale: escala }] },
        ]}>
        {no.concluido ? (
          <Ionicons name="star" size={26} color={corIcone} />
        ) : no.desbloqueado ? (
          <Ionicons name="play" size={24} color={corIcone} />
        ) : (
          <Feather name="lock" size={20} color={corIcone} />
        )}
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    alignSelf: 'center',
  },
  no: {
    position: 'absolute',
    alignItems: 'center',
    gap: 4,
  },
  circuloSombra: {
    position: 'absolute',
  },
  circulo: {
    position: 'absolute',
    top: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  circuloBloqueadoBorda: {
    borderWidth: 1,
    borderColor: Brand.bordaForte,
  },
  legenda: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    color: Brand.textoSuave,
    marginTop: ALTURA_SOMBRA,
  },
  flag: {
    backgroundColor: Brand.texto,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 10,
    marginBottom: 6,
  },
  flagTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 12.5,
    color: Brand.bg,
  },
  mascoteSlot: {
    position: 'absolute',
    alignItems: 'center',
    gap: 8,
  },
  mascoteTag: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11,
    color: Brand.textoSuave,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
});
