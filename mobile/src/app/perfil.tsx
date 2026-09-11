import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Mascote } from '@/components/mascote';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import {
  DiasAteProva,
  Nivel,
  ResumoGeral,
  Streak,
  getDiasAteProva,
  getNivel,
  getResumoGeral,
  getStreak,
} from '@/lib/api';

/**
 * Tela "Perfil e ligas" do handoff (README seção 7). Stats reais via
 * /nivel, /dias-ate-prova e /resumo-geral (todos já existentes ou
 * expostos na Fase 2 do plano). "Liga Diamante" é decorativa/fictícia
 * de propósito -- sistema é single-user (ver core/CLAUDE.md), não tem
 * como ter ranking real de outros alunos sem um redesenho de
 * multiusuário, fora de escopo. Só a linha "Você" usa XP real; as
 * outras duas posições são fixas, mesma decisão já tomada na versão
 * web (Streamlit) desta mesma tela.
 */
export default function PerfilScreen() {
  const [nivel, setNivel] = useState<Nivel | null>(null);
  const [diasProva, setDiasProva] = useState<DiasAteProva | null>(null);
  const [resumo, setResumo] = useState<ResumoGeral | null>(null);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getNivel(), getDiasAteProva(), getResumoGeral(), getStreak()])
      .then(([n, d, r, s]) => {
        setNivel(n);
        setDiasProva(d);
        setResumo(r);
        setStreak(s);
      })
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, []);

  const carregando = !nivel || !diasProva || !resumo || !streak;
  const moodMascote = streak && streak.atual === 0 ? 'sleep' : 'happy';
  const pctAcerto = resumo?.taxa_acerto !== null && resumo?.taxa_acerto !== undefined ? Math.round(resumo.taxa_acerto * 100) : null;

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.headerRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarLetra}>G</Text>
            </View>
            <View style={styles.headerTextos}>
              <Text style={styles.nome}>Seu perfil</Text>
              {nivel && <Text style={styles.rank}>{nivel.rank}</Text>}
            </View>
            <View style={styles.gearBtn}>
              <Feather name="settings" size={18} color={Brand.textoApagado} />
            </View>
          </View>

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          {carregando && !erro && <ActivityIndicator style={styles.espaco} color={Brand.verde} />}

          {!carregando && (
            <>
              <View style={styles.tilesRow}>
                <View style={styles.tile}>
                  <Text style={styles.tileValor}>{diasProva!.ja_passou ? 0 : diasProva!.dias_restantes}</Text>
                  <Text style={styles.tileLabel}>DIAS P/ ENEM</Text>
                </View>
                <View style={styles.tile}>
                  <Text style={styles.tileValor}>{resumo!.total_tentativas}</Text>
                  <Text style={styles.tileLabel}>QUESTÕES</Text>
                </View>
                <View style={[styles.tile, styles.tileVerde]}>
                  <Text style={[styles.tileValor, { color: Brand.verde }]}>{pctAcerto !== null ? `${pctAcerto}%` : '—'}</Text>
                  <Text style={styles.tileLabel}>ACERTO</Text>
                </View>
              </View>

              <View style={styles.mascoteCard}>
                <Mascote color={Brand.branco} shadow={Brand.brancoEscuro} beak={Brand.rosa} mood={moodMascote} size={0.75} />
                <Text style={styles.mascoteTexto}>
                  {moodMascote === 'sleep'
                    ? '"Faz tempo que a gente não estuda hoje. Bora?" — Pipoco'
                    : '"Boa, sua sequência tá firme. Continua assim!" — Pipoco'}
                </Text>
              </View>
            </>
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
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 22,
    backgroundColor: Brand.roxo,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarLetra: {
    fontFamily: Fontes.titulo,
    fontSize: 26,
    color: Brand.roxoClaro,
  },
  headerTextos: { flex: 1, gap: 2 },
  nome: {
    fontFamily: Fontes.titulo,
    fontSize: 19,
    color: Brand.texto,
  },
  rank: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 13,
    color: Brand.ouro,
  },
  gearBtn: {
    width: 38,
    height: 38,
    borderRadius: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    justifyContent: 'center',
    alignItems: 'center',
  },
  espaco: { marginTop: 8 },
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
  tilesRow: {
    flexDirection: 'row',
    gap: 10,
  },
  tile: {
    flex: 1,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    paddingVertical: 14,
    paddingHorizontal: 8,
    alignItems: 'center',
    gap: 4,
  },
  tileVerde: {
    backgroundColor: Brand.verdeClaro + '22',
  },
  tileValor: {
    fontFamily: Fontes.titulo,
    fontSize: 20,
    color: Brand.texto,
  },
  tileLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 10.5,
    letterSpacing: 0.5,
    color: Brand.textoApagado,
  },
  mascoteCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 14,
  },
  mascoteTexto: {
    flex: 1,
    fontFamily: Fontes.corpo,
    fontSize: 13.5,
    color: Brand.textoSuave,
    lineHeight: 19,
  },
});
