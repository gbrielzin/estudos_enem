import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { MissoesCard } from '@/components/missoes-card';
import { Brand, Fontes } from '@/constants/brand';
import { MissaoDoDia, getMissoesDoDia } from '@/lib/api';

/**
 * Tela "Missões" -- nova aba própria da barra de baixo (ver
 * components/tab-bar.tsx). Mesmo card que já existia embutido na
 * Trilha (components/missoes-card.tsx, GET /missoes-do-dia) -- só
 * ganhou uma tela cheia pra si; nenhuma lógica nova, o card continua
 * aparecendo também na Trilha (não foi tirado de lá, só passou a
 * existir nos dois lugares).
 */
export default function MissoesScreen() {
  const [missoes, setMissoes] = useState<MissaoDoDia[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getMissoesDoDia()
      .then(setMissoes)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.titulo}>Missões do dia</Text>

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          {!missoes && !erro && <ActivityIndicator color={Brand.verde} />}

          {missoes && missoes.length === 0 && <Text style={styles.textoSuave}>Nenhuma missão hoje.</Text>}

          {missoes && missoes.length > 0 && <MissoesCard missoes={missoes} />}
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
    fontSize: 13,
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
});
