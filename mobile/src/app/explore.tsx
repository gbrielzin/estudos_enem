import { Feather } from '@expo/vector-icons';
import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BarraProgresso } from '@/components/barra-progresso';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { GrandeArea, MateriaExplorada, getExplorarMaterias } from '@/lib/api';

const ROTULO_AREA: Record<GrandeArea, string> = {
  matematica: 'Matemática',
  ciencias_natureza: 'Ciências da Natureza',
};
const AREAS: GrandeArea[] = ['matematica', 'ciencias_natureza'];

// Ciclo de cor por posição na lista -- o mockup (README seção 6) usa
// lima/violeta/âmbar/coral alternados nos badges de matéria, não uma cor
// fixa por matéria (não há um mapeamento semântico matéria->cor definido
// em nenhum lugar do handoff).
const CORES_BADGE = [
  { cor: Brand.verde, fundo: Brand.verdeEscuro },
  { cor: Brand.roxo, fundo: Brand.roxoEscuro },
  { cor: Brand.ouro, fundo: Brand.ouroBorda },
  { cor: Brand.laranja, fundo: Brand.laranjaEscuro },
];

/**
 * Tela "Explore" do handoff (README seção 6) -- navegar/buscar todas as
 * matérias da taxonomia (banco/db.explorar_materias, novo endpoint
 * GET /explorar), não só as que já têm tentativa. Substitui o tutorial
 * padrão do Expo Starter que vivia neste arquivo antes.
 */
export default function ExploreScreen() {
  const [area, setArea] = useState<GrandeArea>('ciencias_natureza');
  const [materias, setMaterias] = useState<MateriaExplorada[] | null>(null);
  const [busca, setBusca] = useState('');
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    setMaterias(null);
    getExplorarMaterias(area)
      .then(setMaterias)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, [area]);

  const filtradas = useMemo(() => {
    if (!materias) return [];
    const termo = busca.trim().toLowerCase();
    if (!termo) return materias;
    return materias.filter((m) => m.materia.toLowerCase().includes(termo));
  }, [materias, busca]);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.titulo}>Explorar matérias</Text>

          <View style={styles.buscaContainer}>
            <Feather name="search" size={16} color={Brand.textoApagado} />
            <TextInput
              style={styles.buscaInput}
              placeholder="Buscar matéria"
              placeholderTextColor={Brand.textoApagado}
              value={busca}
              onChangeText={setBusca}
            />
          </View>

          <View style={styles.chipsRow}>
            {AREAS.map((a) => (
              <Text
                key={a}
                onPress={() => setArea(a)}
                style={[styles.chip, area === a && styles.chipAtivo]}>
                {ROTULO_AREA[a]}
              </Text>
            ))}
          </View>

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          {!materias && !erro && <ActivityIndicator style={styles.espaco} color={Brand.verde} />}

          {materias && filtradas.length === 0 && (
            <Text style={styles.textoSuave}>Nenhuma matéria encontrada para &quot;{busca}&quot;.</Text>
          )}

          {filtradas.map((m, i) => {
            const bloqueada = m.total_questoes === 0;
            const { cor, fundo } = CORES_BADGE[i % CORES_BADGE.length];
            const pct = m.taxa_acerto !== null ? Math.round(m.taxa_acerto * 100) : null;
            return (
              <View key={m.materia} style={styles.linha}>
                <View style={[styles.badge, bloqueada ? styles.badgeBloqueado : { backgroundColor: cor }]}>
                  <Feather
                    name={bloqueada ? 'lock' : 'book-open'}
                    size={18}
                    color={bloqueada ? Brand.textoMuted : Brand.bg}
                  />
                </View>
                <View style={styles.linhaCorpo}>
                  <Text style={styles.linhaTitulo}>{m.materia.replace(/_/g, ' ')}</Text>
                  <Text style={styles.linhaMeta}>
                    {bloqueada
                      ? 'Sem questões cadastradas ainda'
                      : `${m.total_questoes} questão(ões)${pct !== null ? ` · ${pct}% de acerto` : ' · ainda não praticada'}`}
                  </Text>
                  {!bloqueada && pct !== null && (
                    <View style={{ marginTop: 2 }}>
                      <BarraProgresso pct={pct} cor={cor} altura={8} />
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 96, gap: 14 },
  titulo: {
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: Brand.texto,
  },
  buscaContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  buscaInput: {
    flex: 1,
    fontFamily: Fontes.corpo,
    fontSize: 14.5,
    color: Brand.texto,
  },
  chipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 13,
    color: Brand.textoSuave,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    borderRadius: 999,
    paddingVertical: 8,
    paddingHorizontal: 16,
    overflow: 'hidden',
  },
  chipAtivo: {
    backgroundColor: Brand.verde,
    borderColor: Brand.verde,
    color: '#0D2705',
  },
  espaco: { marginTop: 8 },
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
  linha: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 14,
    alignItems: 'center',
  },
  badge: {
    width: 46,
    height: 46,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeBloqueado: {
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
  },
  linhaCorpo: { flex: 1, gap: 5 },
  linhaTitulo: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 15,
    color: Brand.texto,
    textTransform: 'capitalize',
  },
  linhaMeta: {
    fontFamily: Fontes.corpo,
    fontSize: 12.5,
    color: Brand.textoSuave,
  },
});
