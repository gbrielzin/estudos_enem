import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { Nivel, getNivel } from '@/lib/api';

/**
 * Tela "Liga" -- nova aba própria da barra de baixo (ver components/
 * tab-bar.tsx), extraída do card que morava dentro de Perfil (mesmo
 * conteúdo, só mudou de tela). "Liga Diamante" continua decorativa/
 * fictícia de propósito -- sistema é single-user (ver core/CLAUDE.md),
 * sem como ter ranking real de outros alunos sem um redesenho de
 * multiusuário, fora de escopo. Só a linha "Você" usa XP real; as
 * outras duas posições são fixas, mesma decisão já tomada na versão
 * web (Streamlit) e na versão anterior desta seção dentro de Perfil.
 */
export default function LigaScreen() {
  const [nivel, setNivel] = useState<Nivel | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getNivel()
      .then(setNivel)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.titulo}>Liga</Text>

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          {!nivel && !erro && <ActivityIndicator color={Brand.verde} />}

          {nivel && (
            <View style={styles.ligaCard}>
              <View style={styles.ligaHeader}>
                <Feather name="shield" size={18} color={Brand.azul} />
                <View style={styles.ligaHeaderTextos}>
                  <Text style={styles.ligaTitulo}>Liga Diamante</Text>
                  <Text style={styles.textoSuave}>Ilustrativo por enquanto — vira liga de verdade com mais alunos</Text>
                </View>
              </View>
              <View style={styles.ligaLinha}>
                <Text style={styles.ligaPosicao}>1</Text>
                <Text style={styles.ligaNome}>Marina S.</Text>
                <Text style={styles.textoSuave}>6120</Text>
              </View>
              <View style={styles.ligaLinha}>
                <Text style={styles.ligaPosicao}>2</Text>
                <Text style={styles.ligaNome}>Caio R.</Text>
                <Text style={styles.textoSuave}>5480</Text>
              </View>
              <View style={[styles.ligaLinha, styles.ligaLinhaVoce]}>
                <Text style={[styles.ligaPosicao, { color: '#0D2705' }]}>3</Text>
                <Text style={[styles.ligaNome, { color: '#0D2705' }]}>Você</Text>
                <Text style={{ fontFamily: Fontes.corpoExtraNegrito, color: '#0D2705' }}>{nivel.xp}</Text>
              </View>
            </View>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 96, gap: 16 },
  titulo: {
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: Brand.texto,
  },
  textoSuave: {
    fontFamily: Fontes.corpo,
    fontSize: 12,
    color: Brand.textoSuave,
  },
  avisoErro: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: Brand.laranjaBg,
    borderWidth: 1,
    borderColor: '#5C3320',
  },
  avisoErroTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 13,
    color: Brand.laranja,
  },
  ligaCard: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 18,
    gap: 10,
  },
  ligaHeader: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 6,
  },
  ligaHeaderTextos: { flex: 1, gap: 2 },
  ligaTitulo: {
    fontFamily: Fontes.tituloSemibold,
    fontSize: 16,
    color: Brand.texto,
  },
  ligaLinha: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 11,
    paddingVertical: 9,
    paddingHorizontal: 11,
    borderRadius: 14,
    backgroundColor: Brand.bgCardEscuro,
  },
  ligaLinhaVoce: {
    backgroundColor: Brand.verde,
  },
  ligaPosicao: {
    width: 20,
    fontFamily: Fontes.titulo,
    fontSize: 13,
    color: Brand.textoApagado,
  },
  ligaNome: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14,
    color: Brand.texto,
  },
});
