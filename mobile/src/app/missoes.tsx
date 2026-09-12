import { Feather, Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Animated, Easing, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { MissoesCard } from '@/components/missoes-card';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { MissaoDoDia, Streak, getMissoesDoDia, getStreak } from '@/lib/api';

/**
 * Topo da tela (design_handoff_enem_gamificado/screens/03-missoes.png):
 * seta de voltar + título + selo âmbar "Xh restantes" -- cópia fiel do
 * mockup, pedido explícito do usuário 2026-09-11 ("copia a interface
 * na parte superior... do jeito que está"). `router.back()` (não um
 * callback local como TelaApresentacao em index.tsx usa) porque esta
 * tela é uma aba de verdade da barra de baixo (ver tab-bar.tsx), não
 * uma fase dentro da mesma tela -- `canGoBack()` evita um crash/no-op
 * estranho se o usuário abriu "Missões" direto pela aba (sem
 * histórico nenhum pra voltar), caindo pra Trilha nesse caso.
 *
 * "Xh restantes" é hora-a-hora até meia-noite, calculado no aparelho
 * (sem endpoint novo -- é só "quanto falta pro dia acabar", mesmo
 * reset diário que já rege `progresso_meta_diaria`/missões em
 * db.py) -- não pretende ser um cronômetro ao vivo tique-taque, só o
 * mesmo tipo de número estático que o mockup mostra.
 */
function horasRestantesHoje(): number {
  const agora = new Date();
  const meiaNoite = new Date(agora);
  meiaNoite.setHours(24, 0, 0, 0);
  return Math.max(0, Math.ceil((meiaNoite.getTime() - agora.getTime()) / 3_600_000));
}

function CabecalhoMissoes() {
  const horas = horasRestantesHoje();
  return (
    <View style={styles.cabecalho}>
      <Pressable
        style={styles.voltarBtn}
        onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
      >
        <Feather name="chevron-left" size={20} color={Brand.texto} />
      </Pressable>
      <Text style={styles.titulo}>Missões do dia</Text>
      <View style={styles.tempoPill}>
        <Text style={styles.tempoTexto}>{horas}h{'\n'}restantes</Text>
      </View>
    </View>
  );
}

// Segunda a domingo, igual ao mockup ("S T Q Q S HOJE D") -- o rótulo
// do dia atual vira "HOJE" em vez da inicial (ver renderização abaixo),
// nunca os dois ao mesmo tempo.
const INICIAIS_SEMANA = ['S', 'T', 'Q', 'Q', 'S', 'S', 'D'];

function paraISO(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/** Segunda-feira desta semana até domingo, como 7 objetos Date às 00h
 * (comparação por data, não por instante). `Date.getDay()` do
 * JavaScript usa 0=domingo, por isso o ajuste `dia === 0 ? -6 : 1 -
 * dia` pra sempre cair numa segunda-feira, mesmo se hoje for domingo. */
function semanaAtual(): Date[] {
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const dia = hoje.getDay();
  const segunda = new Date(hoje);
  segunda.setDate(hoje.getDate() + (dia === 0 ? -6 : 1 - dia));
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(segunda);
    d.setDate(segunda.getDate() + i);
    return d;
  });
}

/**
 * Card "Ofensivo" (mesmo mockup, logo abaixo do cabeçalho) -- usa
 * GET /streak (db.calcular_ofensiva(), já existia, nenhum endpoint
 * novo) pra saber quais dos últimos 30 dias tiveram tentativa.
 * HOJE aparece sempre verde (ponteiro de "você está aqui", não um
 * troféu de "já terminou hoje" -- o mockup mostra isso mesmo com
 * "Ofensivo: 0 dias" e "0/20 questões hoje" na mesma tela, ou seja,
 * antes de qualquer atividade); dias passados sem tentativa ficam
 * escuros/apagados; dias futuros da mesma semana (ainda não
 * chegaram) ficam com borda tracejada, sem preenchimento.
 */
/**
 * "Ofensiva pulsa" -- padrão de movimento 6a do projeto de design
 * (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de animação"):
 * 1,5s em loop, só enquanto a ofensiva está viva (chama cinza e
 * parada quando não está). Card "Ofensivo" daqui não tinha nenhum
 * ícone de chama antes -- o mockup usa uma forma customizada em CSS,
 * recriada aqui com o ícone "flame" do Ionicons (já é dependência do
 * projeto) em vez de desenhar 2 camadas de View do zero.
 */
function ChamaAnimada({ ativa }: { ativa: boolean }) {
  const t = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (!ativa) return;
    const loop = Animated.loop(Animated.timing(t, { toValue: 1, duration: 1500, easing: Easing.linear, useNativeDriver: true }));
    loop.start();
    return () => loop.stop();
  }, [ativa, t]);
  const scaleX = t.interpolate({ inputRange: [0, 0.28, 0.58, 1], outputRange: [1, 1.13, 0.94, 1] });
  const scaleY = t.interpolate({ inputRange: [0, 0.28, 0.58, 1], outputRange: [1, 0.92, 1.1, 1] });
  const translateY = t.interpolate({ inputRange: [0, 0.28, 0.58, 1], outputRange: [0, 2, -3, 0] });
  return (
    <Animated.View style={{ transform: [{ translateY }, { scaleX }, { scaleY }] }}>
      <Ionicons name="flame" size={18} color={ativa ? Brand.laranja : Brand.textoMuted} />
    </Animated.View>
  );
}

function OfensivaSemana({ streak }: { streak: Streak | null }) {
  const semana = semanaAtual();
  const hojeISO = paraISO(new Date());
  const ativos = new Set((streak?.calendario_30_dias ?? []).filter((c) => c.ativo).map((c) => c.data));

  return (
    <View style={styles.ofensivaCard}>
      <View style={styles.ofensivaHeader}>
        <Text style={styles.ofensivaTitulo}>Ofensivo</Text>
        <View style={styles.ofensivaDiasRow}>
          <ChamaAnimada ativa={(streak?.atual ?? 0) > 0} />
          <Text style={styles.ofensivaDias}>{streak?.atual ?? 0} dias</Text>
        </View>
      </View>
      <View style={styles.semanaRow}>
        {semana.map((d, i) => {
          const iso = paraISO(d);
          const isHoje = iso === hojeISO;
          const isFuturo = iso > hojeISO;
          const isAtivo = ativos.has(iso);
          return (
            <View key={iso} style={styles.diaColuna}>
              <View
                style={[
                  styles.diaBox,
                  isHoje || isAtivo ? styles.diaBoxAtivo : isFuturo ? styles.diaBoxFuturo : styles.diaBoxInativo,
                ]}
              />
              <Text style={[styles.diaLabel, isHoje && styles.diaLabelHoje]}>
                {isHoje ? 'HOJE' : INICIAIS_SEMANA[i]}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

/**
 * Tela "Missões" -- nova aba própria da barra de baixo (ver
 * components/tab-bar.tsx). Mesmo card que já existia embutido na
 * Trilha (components/missoes-card.tsx, GET /missoes-do-dia) -- só
 * ganhou uma tela cheia pra si; nenhuma lógica nova, o card continua
 * aparecendo também na Trilha (não foi tirado de lá, só passou a
 * existir nos dois lugares).
 */
// As 2 missões que faltavam pra bater com o mockup (03-missoes.png)
// -- "Mantenha o ofensivo" e "Revisão espaçada" -- NÃO existem em
// db.missoes_do_dia() ainda (só meta_diaria/foco_prioridade são reais
// hoje). Pedido explícito do usuário, 2026-09-11: "pode deixar só
// visualmente ali mesmo... depois a gente implementa o backend
// certinho" -- objetos estáticos, mesmo formato de MissaoDoDia, só pra
// completar a tela visualmente. Progresso ficou parado (0 e ~1/3) só
// pra ilustrar os dois estados que o mockup mostra (barra vazia vs.
// parcialmente cheia) -- nenhum dos dois números vem de tentativa real
// nenhuma, por isso a descrição evita inventar uma contagem específica.
const MISSOES_VISUAIS_ESTATICAS: MissaoDoDia[] = [
  {
    id: 'manter_ofensivo',
    titulo: 'Mantenha o ofensivo',
    descricao: 'Conclua 1 nó hoje',
    progresso_atual: 0,
    progresso_meta: 1,
    concluida: false,
  },
  {
    id: 'revisao_espacada',
    titulo: 'Revisão espaçada',
    descricao: 'Questões atrasadas te esperando',
    progresso_atual: 1,
    progresso_meta: 3,
    concluida: false,
  },
];

export default function MissoesScreen() {
  const [missoes, setMissoes] = useState<MissaoDoDia[] | null>(null);
  const [streak, setStreak] = useState<Streak | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getMissoesDoDia()
      .then((reais) => setMissoes([...reais, ...MISSOES_VISUAIS_ESTATICAS]))
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
    getStreak().then(setStreak).catch(() => {});
  }, []);

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <CabecalhoMissoes />

          <OfensivaSemana streak={streak} />

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
  scroll: { padding: 16, paddingBottom: 96, gap: 22 },
  cabecalho: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
  },
  voltarBtn: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    alignItems: 'center',
    justifyContent: 'center',
  },
  titulo: {
    flex: 1,
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: Brand.texto,
  },
  tempoPill: {
    backgroundColor: Brand.ouroBg,
    borderWidth: 1,
    borderColor: Brand.ouroBorda,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  tempoTexto: {
    fontFamily: Fontes.tituloSemibold,
    fontSize: 13,
    lineHeight: 16,
    color: Brand.ouro,
    textAlign: 'center',
  },
  ofensivaCard: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 20,
    gap: 18,
  },
  ofensivaHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  ofensivaTitulo: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 16,
    color: Brand.texto,
  },
  ofensivaDiasRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  ofensivaDias: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14,
    color: Brand.textoSuave,
  },
  semanaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  diaColuna: {
    alignItems: 'center',
    gap: 9,
  },
  diaBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
  },
  diaBoxAtivo: {
    backgroundColor: Brand.verde,
  },
  diaBoxInativo: {
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.borda,
  },
  diaBoxFuturo: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: Brand.bordaForte,
    borderStyle: 'dashed',
  },
  diaLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11,
    color: Brand.textoApagado,
  },
  diaLabelHoje: {
    color: Brand.verde,
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
