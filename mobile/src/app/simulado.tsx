import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Rect } from 'react-native-svg';

import { Brand, Fontes } from '@/constants/brand';

/**
 * Tela "Simulado" -- nova aba da barra de baixo (ver components/
 * tab-bar.tsx), ainda sem o modo de verdade implementado (prova
 * completa cronometrada -- o equivalente já existe no lado Streamlit,
 * core/cartao_resposta.py, aba "Simulado completo"). Placeholder
 * simples só pra aba ter uma rota de verdade pra abrir -- decisão do
 * usuário (perguntado explicitamente: construir as 3 abas novas da
 * barra com tela de verdade em vez de deixar desabilitadas), não uma
 * feature fingida.
 */
export default function SimuladoScreen() {
  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.centro}>
          <View style={styles.iconeBadge}>
            <Svg width={34} height={34} viewBox="0 0 24 24">
              <Rect x={3.6} y={3.4} width={16.8} height={18} rx={2.4} fill={Brand.ouro} />
              <Rect x={8.4} y={1.5} width={7.2} height={3.6} rx={1.4} fill={Brand.ouroBorda} />
              <Rect x={6.6} y={8.6} width={10.8} height={2.2} rx={1.1} fill={Brand.bg} />
              <Rect x={6.6} y={13} width={7} height={2.2} rx={1.1} fill={Brand.bg} />
            </Svg>
          </View>
          <Text style={styles.titulo}>Simulado</Text>
          <Text style={styles.texto}>
            Prova completa cronometrada, em breve por aqui. Por enquanto, o modo mais completo de
            simulado mora na versão web (Cartão-resposta → Simulado completo).
          </Text>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  centro: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32, gap: 14 },
  iconeBadge: {
    width: 68,
    height: 68,
    borderRadius: 22,
    backgroundColor: Brand.ouroBg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  titulo: {
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: Brand.texto,
  },
  texto: {
    fontFamily: Fontes.corpo,
    fontSize: 14,
    color: Brand.textoSuave,
    textAlign: 'center',
    lineHeight: 20,
  },
});
