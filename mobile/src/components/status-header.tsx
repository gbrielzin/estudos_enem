import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { Brand, Fontes } from '@/constants/brand';
import { Nivel, Streak } from '@/lib/api';

interface StatusHeaderProps {
  streak: Streak | null;
  nivel: Nivel | null;
}

/**
 * Badges de topo (ofensiva + rank/XP) -- expõe db.calcular_ofensiva()
 * e db.calcular_nivel_jogador(), que já existiam e já eram usados na
 * versão Streamlit ("Minha análise"). Puramente informativo -- não
 * bloqueia nada, não é gasto/perdido. Visual: pill do mockup de
 * referência (cinza apagado quando streak=0, laranja quando ativo).
 */
export function StatusHeader({ streak, nivel }: StatusHeaderProps) {
  if (!streak && !nivel) return null;
  const streakAtivo = !!streak && streak.atual > 0;

  return (
    <View style={styles.container}>
      {streak && (
        <View style={[styles.pill, streakAtivo ? styles.pillStreakOn : styles.pillStreakOff]}>
          <Ionicons name={streakAtivo ? 'flame' : 'flame-outline'} size={16} color={streakAtivo ? Brand.laranja : Brand.textoApagado} />
          <Text style={[styles.pillTexto, { color: streakAtivo ? Brand.laranja : Brand.textoApagado }]}>{streak.atual}</Text>
        </View>
      )}
      {nivel && (
        <View style={[styles.pill, styles.pillRank]}>
          <Ionicons name="star" size={15} color={Brand.ouro} />
          <Text style={[styles.pillTexto, { color: Brand.ouro }]}>
            {nivel.rank} · {nivel.xp} XP
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 10,
  },
  pill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
  },
  pillStreakOff: {
    backgroundColor: Brand.bgCard,
    borderColor: Brand.bordaForte,
  },
  pillStreakOn: {
    backgroundColor: Brand.laranjaBg,
    borderColor: '#5C3320',
  },
  pillRank: {
    backgroundColor: Brand.ouroBg,
    borderColor: Brand.ouroBorda,
  },
  pillTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 14,
  },
});
