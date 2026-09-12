import { Feather, Ionicons } from '@expo/vector-icons';
import { useEffect, useRef } from 'react';
import { Animated, Easing, Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import Svg, { Path } from 'react-native-svg';

import { Mascote } from '@/components/mascote';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { ResumoTrilha } from '@/constants/resumos-trilha';
import { Spacing } from '@/constants/theme';
import { useInteracaoBotao } from '@/hooks/use-interacao-botao';
import { NoTrilha } from '@/lib/api';

const AMPLITUDE = 80;
const ESPACAMENTO_VERTICAL = 130;
const DIAMETRO_NO_ATUAL = 78;
const DIAMETRO_NO_PADRAO = 70;
const ALTURA_SOMBRA = 7;
const PADDING_TOPO = 50;

interface TrilhaPathProps {
  trilha: NoTrilha[];
  resumo?: ResumoTrilha;
  onAbrirNo: (no: NoTrilha) => void;
  onAbrirResumo?: () => void;
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
export function TrilhaPath({ trilha, resumo, onAbrirNo, onAbrirResumo }: TrilhaPathProps) {
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
    <View style={{ width: larguraContainer, alignSelf: 'center', gap: 14 }}>
      {resumo && onAbrirResumo && <CardApresentacao resumo={resumo} onPress={onAbrirResumo} />}

      <View style={[styles.container, { width: larguraContainer, height: alturaTotal }]}>
        {/* pointerEvents="none": decorativo, cobre o container inteiro
            (StyleSheet.absoluteFill) por cima dos nós -- sem isto, o
            <svg> real que react-native-web renderiza intercepta o
            clique no react-native-web (mesmo com os nós vindo depois
            no JSX), suspeito nº1 do "os botões não vão no site, só no
            celular" (RN nativo não tem esse problema de hit-testing de
            DOM, só a versão web). */}
        <Svg style={StyleSheet.absoluteFill} width={larguraContainer} height={alturaTotal} pointerEvents="none">
          <Path d={caminhoD} stroke={Brand.bordaForte} strokeWidth={12} fill="none" strokeLinecap="round" strokeDasharray="1 26" />
        </Svg>

        {pontoMascote && (
          <View style={[styles.mascoteSlot, { left: Math.min(larguraContainer - 82, pontoMascote.x + 70), top: pontoMascote.y - 30 }]}>
            {/* Pipoco "areia" com manchas -- variação da tela Trilha do
                projeto de design (dc-import scene="fogueira" pattern=
                "patches"), substituindo o Pipoco branco liso genérico
                daqui. Pedido explícito do usuário: o gatinho muda de
                cara conforme a matéria/tela, não é sempre o mesmo. */}
            <Mascote
              color={Brand.gatoAreia}
              shadow={Brand.gatoAreiaSombra}
              beak={Brand.rosa}
              mood="happy"
              size={0.78}
              pattern="patches"
              patch={Brand.gatoAreiaMancha}
            />
            <Text style={styles.mascoteTag}>Pipoco</Text>
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
            </View>
          );
        })}
      </View>
    </View>
  );
}

/**
 * Card "Apresentação" -- resumo de conceitos que abre a trilha ANTES
 * do Nó 1 (ver constants/resumos-trilha.ts pro porquê). Visual
 * importado do projeto de design, tela "Trilha": card roxo-escuro
 * full-width com ícone de livro, acima da serpentina, distinto de
 * propósito dos nós circulares de questão -- não é um nó de prática,
 * é uma parada de leitura.
 */
function CardApresentacao({ resumo, onPress }: { resumo: ResumoTrilha; onPress: () => void }) {
  const { deslocamentoY, handlers } = useInteracaoBotao({ quedaPressionado: 3 });

  return (
    <Pressable onPress={onPress} {...handlers}>
      <Animated.View style={[styles.cardApresentacao, { transform: [{ translateY: deslocamentoY }] }]}>
        <View style={styles.cardApresentacaoIcone}>
          <Ionicons name="book" size={22} color={Brand.roxoClaro} />
        </View>
        <View style={styles.cardApresentacaoTextos}>
          <Text style={styles.cardApresentacaoRotulo}>
            APRESENTAÇÃO · {resumo.minutos} MIN
          </Text>
          <Text style={styles.cardApresentacaoTitulo}>{resumo.titulo}</Text>
          <Text style={styles.cardApresentacaoSubtitulo}>Bata o olho antes de começar os nós</Text>
        </View>
        <View style={styles.cardApresentacaoBotao}>
          <Text style={styles.cardApresentacaoBotaoTexto}>VER</Text>
        </View>
      </Animated.View>
    </Pressable>
  );
}

function NoCirculo({ no, ehAtual, diametro, onPress }: { no: NoTrilha; ehAtual: boolean; diametro: number; onPress: () => void }) {
  const pulso = useRef(new Animated.Value(1)).current;
  const { deslocamentoY, handlers } = useInteracaoBotao({ desativado: !no.desbloqueado, quedaPressionado: ALTURA_SOMBRA });

  useEffect(() => {
    if (!ehAtual) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulso, { toValue: 1.08, duration: 700, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(pulso, { toValue: 1, duration: 700, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [ehAtual, pulso]);

  const corFundo = no.concluido ? Brand.ouro : ehAtual ? Brand.verde : '#1F2531';
  const corSombra = no.concluido ? '#8A6300' : ehAtual ? Brand.verdeEscuro : '#14181F';
  const corIcone = no.concluido ? '#3A2C00' : ehAtual ? '#0D2705' : Brand.textoMuted;
  const raio = diametro / 2;

  return (
    <Pressable disabled={!no.desbloqueado} onPress={onPress} style={{ width: diametro, height: diametro + ALTURA_SOMBRA }} {...handlers}>
      {/* camada de baixo = "sombra" sólida, cria o efeito de botão 3D pressionado */}
      <View style={[styles.circuloSombra, { top: ALTURA_SOMBRA, width: diametro, height: diametro, borderRadius: raio, backgroundColor: corSombra }]} />
      <Animated.View
        style={[
          styles.circulo,
          { width: diametro, height: diametro, borderRadius: raio, backgroundColor: corFundo },
          !no.desbloqueado && styles.circuloBloqueadoBorda,
          { transform: [{ translateY: deslocamentoY }, { scale: pulso }] },
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
  cardApresentacao: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.roxoBgEscuro,
    borderWidth: 1.5,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: RaioCard,
    padding: 14,
  },
  cardApresentacaoIcone: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: Brand.roxo,
    boxShadow: `0 4px 0 ${Brand.roxoEscuro}`,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardApresentacaoTextos: {
    flex: 1,
    gap: 2,
  },
  cardApresentacaoRotulo: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    letterSpacing: 1.4,
    color: Brand.roxoTextoEscuro,
  },
  cardApresentacaoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 17,
    color: Brand.texto,
  },
  cardApresentacaoSubtitulo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11.5,
    color: Brand.textoSuave,
  },
  cardApresentacaoBotao: {
    backgroundColor: Brand.texto,
    boxShadow: '0 3px 0 #A6AEBD',
    borderRadius: 11,
    paddingVertical: 7,
    paddingHorizontal: 12,
  },
  cardApresentacaoBotaoTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 12,
    color: Brand.bg,
  },
});
