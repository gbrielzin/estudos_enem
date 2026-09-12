import { Feather } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useState } from 'react';
import { Animated, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Mascote } from '@/components/mascote';
import { TelaBilhete } from '@/components/tela-bilhete';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { interpolarSombraBotao, useInteracaoBotao } from '@/hooks/use-interacao-botao';

/**
 * Tela "Montar simulado" (barra de baixo, ver components/tab-bar.tsx)
 * -- projeto de design atualizado, importado ao vivo via DesignSync
 * (App ENEM.dc.html, "TURNO 5 — SIMULADO NO CELULAR", tela 5a
 * "Escolher a prova", 2026-09-11), seguido de "Seu bilhete" (2a tela
 * do mesmo fluxo 5a, components/tela-bilhete.tsx) ao apertar "Emitir
 * bilhete".
 *
 * As duas telas vivem no MESMO componente, alternadas por `fase`
 * (state local) -- MESMO padrão que app/index.tsx já usa pra
 * Apresentação ↔ Trilha ↔ Exercício. Uma 1a tentativa registrou "Seu
 * bilhete" como rota de verdade (app/bilhete.tsx + <TabTrigger>
 * escondido), mas o sistema de Tabs customizado deste app (expo-
 * router/ui) despacha troca de tela via `JUMP_TO` de navegação nativa,
 * e esse JUMP_TO nunca foi reconhecido pelo navigator de verdade
 * ("The action 'JUMP_TO'... was not handled by any navigator", erro
 * visto ao vivo no console mesmo com o TabTrigger registrado igual aos
 * outros 6 -- ver histórico de commits/comentário removido daqui).
 * `fase` local evita brigar com essa API interna pra uma tela que nem
 * precisa de URL própria.
 *
 * TUDO aqui é estado local/decorativo por enquanto, sem API nova: o
 * backend não tem NENHUM endpoint pra "quais provas reais existem" ou
 * "status por ano" pro celular ainda (core/api.py hoje só cobre banco
 * de prática/trilha/missões/perfil -- o equivalente real mora em
 * db.listar_provas()/db.dias_ate_prova() e só é exposto no lado
 * Streamlit). Anos/status abaixo são um exemplo fixo copiado do
 * próprio mockup (2025 nunca feita, 2024 parou no meio, 2023/2022/2021
 * já feitas, 2020 não abriu) -- os toques trocam qual ano fica em
 * destaque (interativo de verdade), mas nenhum dado é real ainda.
 * Conectar isso a um endpoint de verdade é o próximo passo, não algo
 * pra inventar agora.
 */
type StatusAno = 'feito' | 'parcial' | 'nunca';

const ANOS: { ano: number; status: StatusAno }[] = [
  { ano: 2025, status: 'nunca' },
  { ano: 2024, status: 'parcial' },
  { ano: 2023, status: 'feito' },
  { ano: 2022, status: 'feito' },
  { ano: 2021, status: 'feito' },
  { ano: 2020, status: 'nunca' },
];

const COR_STATUS: Record<StatusAno, string> = {
  feito: Brand.verde,
  parcial: Brand.ouro,
  nunca: Brand.bordaForte,
};

const TEXTO_STATUS: Record<StatusAno, string> = {
  feito: 'já feita',
  parcial: 'parou no meio',
  nunca: 'nunca feita',
};

type Area = 'natureza' | 'matematica' | 'humanas' | 'linguagens' | 'ambas';

const ROTULO_AREA: Record<Exclude<Area, 'ambas'>, string> = {
  natureza: 'Natureza',
  matematica: 'Matemática',
  humanas: 'Humanas',
  linguagens: 'Linguagens',
};

type Modo = 'cronometro' | 'livre' | 'resolvendo';
const ROTULO_MODO: Record<Modo, string> = {
  cronometro: 'Com cronômetro',
  livre: 'Sem pressa',
  resolvendo: 'Corrige a cada questão',
};

export default function SimuladoScreen() {
  const [anoSel, setAnoSel] = useState(2025);
  const [areaSel, setAreaSel] = useState<Area>('natureza');
  const [modoSel, setModoSel] = useState<Modo>('cronometro');
  const [fase, setFase] = useState<'montar' | 'bilhete'>('montar');

  const anoAtual = ANOS.find((a) => a.ano === anoSel) ?? ANOS[0];
  const outrosAnos = ANOS.filter((a) => a.ano !== anoSel);
  const emitir = useInteracaoBotao();
  const emitirSombra = interpolarSombraBotao(emitir.deslocamentoY, Brand.ouroEscuro);

  if (fase === 'bilhete') {
    return (
      <View style={styles.container}>
        <SafeAreaView style={styles.safeArea}>
          <TelaBilhete ano={anoSel} area={areaSel} modo={modoSel} onVoltar={() => setFase('montar')} />
        </SafeAreaView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.cabecalho}>
            <Pressable
              style={styles.voltarBtn}
              onPress={() => (router.canGoBack() ? router.back() : router.replace('/'))}
            >
              <Feather name="chevron-left" size={20} color={Brand.texto} />
            </Pressable>
            <View style={styles.cabecalhoTextos}>
              <Text style={styles.titulo}>Montar simulado</Text>
              <Text style={styles.subtitulo}>ano · área · modo</Text>
            </View>
          </View>

          <View style={styles.secao}>
            <Text style={styles.rotuloSecao}>ANO DA PROVA</Text>
            <View style={styles.anoDestaque}>
              <Text style={styles.anoDestaqueNumero}>{anoSel}</Text>
              <Text style={styles.anoDestaqueStatus}>
                {TEXTO_STATUS[anoAtual.status]} · caderno azul completo
              </Text>
              <View style={styles.anoDestaqueCheck}>
                <Feather name="check" size={13} color={Brand.roxo} />
              </View>
            </View>
            <View style={styles.anoRow}>
              {outrosAnos.map((a) => (
                <Pressable key={a.ano} style={styles.anoBox} onPress={() => setAnoSel(a.ano)}>
                  <Text style={styles.anoBoxNumero}>{String(a.ano).slice(2)}</Text>
                  <View style={[styles.anoBoxDot, { backgroundColor: COR_STATUS[a.status] }]} />
                </Pressable>
              ))}
              <View style={styles.anoBoxMais}>
                <Feather name="chevron-right" size={16} color={Brand.textoApagado} />
              </View>
            </View>
            <View style={styles.legendaRow}>
              <View style={styles.legendaItem}>
                <View style={[styles.legendaDot, { backgroundColor: Brand.verde }]} />
                <Text style={styles.legendaTexto}>já fez</Text>
              </View>
              <View style={styles.legendaItem}>
                <View style={[styles.legendaDot, { backgroundColor: Brand.ouro }]} />
                <Text style={styles.legendaTexto}>parou no meio</Text>
              </View>
              <View style={styles.legendaItem}>
                <View style={[styles.legendaDot, { backgroundColor: Brand.bordaForte }]} />
                <Text style={styles.legendaTexto}>não abriu</Text>
              </View>
            </View>
          </View>

          <View style={styles.secao}>
            <Text style={styles.rotuloSecao}>ÁREA</Text>
            <View style={styles.areaGrid}>
              <Pressable
                style={[styles.areaCard, areaSel === 'natureza' && styles.areaCardSelecionada]}
                onPress={() => setAreaSel('natureza')}
              >
                <Mascote mood="happy" collar={Brand.verde} size={0.33} animado={false} />
                <View style={styles.areaCardTextos}>
                  <Text style={styles.areaCardTitulo}>Natureza</Text>
                  <Text style={[styles.areaCardSub, areaSel === 'natureza' && { color: Brand.roxoTextoEscuro }]}>
                    45q · 1h30
                  </Text>
                </View>
              </Pressable>
              <Pressable
                style={[styles.areaCard, areaSel === 'matematica' && styles.areaCardSelecionada]}
                onPress={() => setAreaSel('matematica')}
              >
                <Mascote mood="sad" color="#3A4152" shadow="#232A38" beak="#8B93A7" size={0.33} animado={false} />
                <View style={styles.areaCardTextos}>
                  <Text style={styles.areaCardTitulo}>Matemática</Text>
                  <Text style={styles.areaCardSubApagado}>ponto fraco</Text>
                </View>
              </Pressable>
              <Pressable
                style={[styles.areaCard, styles.areaCardSemMascote, areaSel === 'humanas' && styles.areaCardSelecionada]}
                onPress={() => setAreaSel('humanas')}
              >
                <Text style={styles.areaCardTitulo}>Humanas</Text>
                <Text style={styles.areaCardSubApagado}>45q · 1h30</Text>
              </Pressable>
              <Pressable
                style={[styles.areaCard, styles.areaCardSemMascote, areaSel === 'linguagens' && styles.areaCardSelecionada]}
                onPress={() => setAreaSel('linguagens')}
              >
                <Text style={styles.areaCardTitulo}>Linguagens</Text>
                <Text style={styles.areaCardSubApagado}>45q + redação</Text>
              </Pressable>
            </View>
            <Pressable
              style={[styles.juntarAreas, areaSel === 'ambas' && styles.juntarAreasSelecionada]}
              onPress={() => setAreaSel('ambas')}
            >
              <Feather name="plus" size={17} color={Brand.ouro} />
              <Text style={styles.juntarAreasTexto}>Juntar duas áreas — 90q, 3h, como no dia real</Text>
            </Pressable>
          </View>

          <View style={styles.secao}>
            <Text style={styles.rotuloSecao}>MODO</Text>
            <View style={styles.modoRow}>
              {(['cronometro', 'livre', 'resolvendo'] as Modo[]).map((m) => (
                <Pressable
                  key={m}
                  style={[styles.modoPill, modoSel === m && styles.modoPillSelecionado]}
                  onPress={() => setModoSel(m)}
                >
                  <Text style={[styles.modoPillTexto, modoSel === m && styles.modoPillTextoSelecionado]}>
                    {m === 'cronometro' ? 'Cronômetro' : m === 'livre' ? 'Livre' : 'Resolvendo'}
                  </Text>
                </Pressable>
              ))}
            </View>
          </View>
        </ScrollView>

        <View style={styles.rodape}>
          <View>
            <Text style={styles.rodapeLabel}>SEU BILHETE</Text>
            <Text style={styles.rodapeValor}>
              {anoSel} · {areaSel === 'ambas' ? 'As duas' : ROTULO_AREA[areaSel]}
            </Text>
          </View>
          <Pressable style={styles.emitirBtnToque} onPress={() => setFase('bilhete')} {...emitir.handlers}>
            <Animated.View
              style={[
                styles.emitirBtn,
                { boxShadow: emitirSombra, transform: [{ translateY: emitir.deslocamentoY }] },
              ]}>
              <Text style={styles.emitirBtnTexto}>Emitir bilhete</Text>
            </Animated.View>
          </Pressable>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 24, gap: 22 },
  cabecalho: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  voltarBtn: {
    width: 40,
    height: 40,
    borderRadius: 13,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cabecalhoTextos: { flex: 1, gap: 1 },
  titulo: {
    fontFamily: Fontes.titulo,
    fontSize: 21,
    lineHeight: 24,
    color: Brand.texto,
  },
  subtitulo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    color: Brand.textoSuave,
  },
  secao: { gap: 9 },
  rotuloSecao: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    letterSpacing: 1.2,
    color: Brand.textoSuave,
  },
  anoDestaque: {
    backgroundColor: Brand.roxo,
    borderRadius: 20,
    paddingVertical: 14,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  anoDestaqueNumero: {
    fontFamily: Fontes.titulo,
    fontSize: 28,
    lineHeight: 30,
    color: '#FFFFFF',
  },
  anoDestaqueStatus: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    lineHeight: 16,
    color: Brand.roxoClaro,
  },
  anoDestaqueCheck: {
    width: 22,
    height: 22,
    borderRadius: 999,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  anoRow: {
    flexDirection: 'row',
    gap: 7,
  },
  anoBox: {
    flex: 1,
    height: 62,
    borderRadius: 16,
    backgroundColor: Brand.bgCard,
    borderWidth: 1.5,
    borderColor: Brand.borda,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  anoBoxNumero: {
    fontFamily: Fontes.titulo,
    fontSize: 16,
    // Baloo 2 corta o topo do número sem lineHeight explícito (achado
    // ao vivo: "2024" saía com o topo do "2" raspado) -- mesmo ajuste
    // que anoDestaqueNumero já usa, só nunca tinha sido aplicado aqui.
    lineHeight: 20,
    color: Brand.brancoEscuro,
  },
  anoBoxDot: {
    width: 7,
    height: 7,
    borderRadius: 999,
  },
  anoBoxMais: {
    width: 36,
    height: 62,
    borderRadius: 16,
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1.5,
    borderColor: Brand.borda,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
  },
  legendaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 13,
  },
  legendaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  legendaDot: {
    width: 7,
    height: 7,
    borderRadius: 999,
  },
  legendaTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11,
    color: Brand.textoApagado,
  },
  areaGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  areaCard: {
    width: '48%',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 9,
    backgroundColor: Brand.bgCard,
    borderWidth: 2,
    borderColor: Brand.borda,
    borderRadius: 16,
    padding: 11,
  },
  areaCardSemMascote: {
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: 1,
  },
  areaCardSelecionada: {
    backgroundColor: Brand.roxoBgEscuro,
    borderColor: Brand.roxo,
  },
  areaCardTextos: { flex: 1, gap: 1 },
  areaCardTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 14.5,
    lineHeight: 17,
    color: Brand.texto,
  },
  areaCardSub: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 10.5,
    color: Brand.textoApagado,
  },
  areaCardSubApagado: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 10.5,
    color: Brand.textoApagado,
  },
  juntarAreas: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderStyle: 'dashed',
    borderRadius: 16,
    padding: 12,
  },
  juntarAreasSelecionada: {
    borderColor: Brand.ouro,
    borderStyle: 'solid',
  },
  juntarAreasTexto: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11.5,
    lineHeight: 16,
    color: Brand.brancoEscuro,
  },
  modoRow: {
    flexDirection: 'row',
    gap: 7,
  },
  modoPill: {
    flex: 1,
    backgroundColor: Brand.bgCard,
    borderWidth: 2,
    borderColor: Brand.borda,
    borderRadius: 16,
    paddingVertical: 11,
    alignItems: 'center',
  },
  modoPillSelecionado: {
    backgroundColor: '#16241A',
    borderColor: Brand.verde,
  },
  modoPillTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 12.5,
    lineHeight: 15,
    color: Brand.textoSuave,
  },
  modoPillTextoSelecionado: {
    color: Brand.verdeClaro,
  },
  rodape: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: Brand.borda,
  },
  rodapeLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 10,
    letterSpacing: 0.8,
    color: Brand.textoApagado,
  },
  rodapeValor: {
    fontFamily: Fontes.titulo,
    fontSize: 15,
    lineHeight: 18,
    color: Brand.texto,
  },
  emitirBtnToque: {
    flex: 1,
  },
  emitirBtn: {
    backgroundColor: Brand.ouro,
    borderRadius: 18,
    paddingVertical: 15,
    alignItems: 'center',
  },
  emitirBtnTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 16,
    lineHeight: 19,
    color: '#3D2C00',
  },
});
