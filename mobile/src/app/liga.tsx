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
 * Tela "Liga" (barra de baixo, ver components/tab-bar.tsx) -- pedido
 * do usuário, 2026-09-11: "pegar o que tá no gatinho [Perfil] e
 * colocar na Liga, como está no design" -- o mockup de referência
 * (design_handoff_enem_gamificado/screens/07-perfil-ligas.png) é UMA
 * tela só (cabeçalho com nome/avatar/rank + 3 blocos de estatística +
 * a Liga + card do mascote), mas uma rodada anterior tinha dividido
 * isso em duas ABAS separadas (Perfil ficou com o cabeçalho, Liga só
 * com a tabela, ver git blame/docstring antiga desta função). Esta
 * versão traz o cabeçalho de volta pra cá, igual ao mockup -- Perfil
 * (app/perfil.tsx) NÃO foi tocado nem esvaziado, o mesmo conteúdo
 * simplesmente também passou a existir aqui (mesmo raciocínio já usado
 * pra Missões: reversível, nada apagado, só duplicado até decidir se
 * uma das duas abas muda de function pra valer).
 *
 * Nome "Gabriel" fixo (não vem de nenhuma configuração -- este app é
 * de um usuário só, não existe campo "nome" em `configuracoes` nem
 * endpoint pra isso ainda) -- mesma letra "G" que o avatar já usava
 * antes, só deixando o nome de verdade visível como o mockup mostra,
 * em vez do genérico "Seu perfil" que estava aqui.
 *
 * "Liga Diamante" continua decorativa/fictícia de propósito -- sistema
 * é single-user (ver core/CLAUDE.md), sem como ter ranking real de
 * outros alunos sem um redesenho de multiusuário, fora de escopo. Só a
 * linha "Você" usa XP real; as outras duas posições são fixas, mesma
 * decisão já tomada na versão web (Streamlit) e nas versões anteriores
 * desta seção.
 */
export default function LigaScreen() {
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
              <Text style={styles.nome}>Gabriel</Text>
              {nivel && <Text style={styles.rank}>{nivel.rank} · {nivel.xp} XP</Text>}
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
                  <View style={[styles.ligaAvatar, { backgroundColor: Brand.laranja }]}>
                    <Text style={styles.ligaAvatarLetra}>M</Text>
                  </View>
                  <Text style={styles.ligaNome}>Marina S.</Text>
                  <Text style={styles.textoSuave}>6120</Text>
                </View>
                <View style={styles.ligaLinha}>
                  <Text style={styles.ligaPosicao}>2</Text>
                  <View style={[styles.ligaAvatar, { backgroundColor: Brand.teal }]}>
                    <Text style={styles.ligaAvatarLetra}>C</Text>
                  </View>
                  <Text style={styles.ligaNome}>Caio R.</Text>
                  <Text style={styles.textoSuave}>5480</Text>
                </View>
                <View style={[styles.ligaLinha, styles.ligaLinhaVoce]}>
                  <Text style={[styles.ligaPosicao, { color: '#0D2705' }]}>3</Text>
                  <View style={[styles.ligaAvatar, { backgroundColor: Brand.roxo }]}>
                    <Text style={[styles.ligaAvatarLetra, { color: Brand.roxoClaro }]}>G</Text>
                  </View>
                  <Text style={[styles.ligaNome, { color: '#0D2705' }]}>Você</Text>
                  <Text style={{ fontFamily: Fontes.corpoExtraNegrito, color: '#0D2705' }}>{nivel!.xp}</Text>
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
  scroll: { padding: 16, paddingBottom: 96, gap: 18 },
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
  textoSuave: {
    fontFamily: Fontes.corpo,
    fontSize: 12,
    color: Brand.textoSuave,
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
  // Avatar quadrado + inicial do nome (mockup 07-perfil-ligas.png --
  // pedido do usuário, 2026-09-11: "faltou aquela fotinha com a letra
  // inicial do nome", pra bater com o mesmo tratamento do avatar "G"
  // roxo lá em cima do cabeçalho, não ficar só posição+nome+XP crus).
  ligaAvatar: {
    width: 32,
    height: 32,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  ligaAvatarLetra: {
    fontFamily: Fontes.titulo,
    fontSize: 14,
    color: '#FFFFFF',
  },
  ligaNome: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14,
    color: Brand.texto,
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
