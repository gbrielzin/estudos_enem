import { Feather } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { MissaoDoDia } from '@/lib/api';

const COR_BARRA_POR_ID: Record<string, string> = {
  meta_diaria: Brand.verde,
  foco_prioridade: Brand.roxoClaro,
};

/**
 * Expõe db.missoes_do_dia() -- decisão deliberada de NÃO ter nenhum
 * mecanismo que bloqueia progresso (sem "vidas" que zeram e travam o
 * app). Cada missão só mostra progresso; completar ou não completar
 * não impede nada no resto do app. Visual do card + checkbox + barra
 * de progresso vem do mockup de referência.
 */
export function MissoesCard({ missoes }: { missoes: MissaoDoDia[] }) {
  if (missoes.length === 0) return null;
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.iconeBadge}>
          <Feather name="target" size={15} color={Brand.laranja} />
        </View>
        <Text style={styles.titulo}>Missões de hoje</Text>
      </View>
      {missoes.map((m) => {
        const pct = m.progresso_meta > 0 ? Math.min(1, m.progresso_atual / m.progresso_meta) : 0;
        const corBarra = COR_BARRA_POR_ID[m.id] ?? Brand.verde;
        return (
          <View key={m.id} style={styles.missao}>
            <View style={[styles.checkbox, m.concluida && { backgroundColor: corBarra, borderColor: corBarra }]}>
              {m.concluida && <Feather name="check" size={13} color={Brand.bg} />}
            </View>
            <View style={styles.missaoCorpo}>
              <Text style={styles.missaoTitulo}>{m.titulo}</Text>
              <Text style={styles.missaoSub}>{m.descricao}</Text>
              <View style={styles.barraFundo}>
                <View style={[styles.barraProgresso, { width: `${pct * 100}%`, backgroundColor: corBarra }]} />
              </View>
            </View>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 18,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 16,
  },
  iconeBadge: {
    width: 28,
    height: 28,
    borderRadius: 9,
    backgroundColor: Brand.laranjaBg,
    justifyContent: 'center',
    alignItems: 'center',
  },
  titulo: {
    fontFamily: Fontes.tituloSemibold,
    fontSize: 16,
    color: Brand.texto,
  },
  missao: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  missaoCorpo: {
    flex: 1,
    gap: 3,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 7,
    borderWidth: 2,
    borderColor: Brand.bordaForte,
    marginTop: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  missaoTitulo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14.5,
    color: Brand.texto,
  },
  missaoSub: {
    fontFamily: Fontes.corpo,
    fontSize: 12.5,
    color: Brand.textoSuave,
    lineHeight: 17,
    marginBottom: 4,
  },
  barraFundo: {
    height: 9,
    borderRadius: 999,
    backgroundColor: Brand.bordaForte,
    overflow: 'hidden',
  },
  barraProgresso: {
    height: 9,
    borderRadius: 999,
  },
});
