import { Feather } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { ItemKit, Molde, VariacaoMolde, getMoldes, getVariacaoMolde } from '@/lib/api';

const LETRAS = ['A', 'B', 'C', 'D', 'E'];

function novaSeed(): number {
  return Math.floor(Math.random() * 1_000_000_000);
}

/**
 * Treino com moldes (ver core/moldes.py): cada molde parte de uma questão
 * oficial do ENEM e gera variações com números novos, pra repetir o mesmo
 * raciocínio até sair sozinho. É o caminho que funcionou numa sessão de
 * estudo real: kit (fórmula + gatilho + apelido) -> questão -> errou? ver
 * qual passo a alternativa errada representa -> nova variação.
 *
 * Variação não é questão oficial, então NÃO registra tentativa (não entra
 * no Leitner nem nas estatísticas); o placar é só da sessão.
 *
 * Vive dentro da aba Explorar (mesmo padrão de simulado.tsx: duas telas no
 * mesmo componente), porque a barra de baixo tem 6 ícones fixos do design.
 */
export function TelaMoldes({ onVoltar }: { onVoltar: () => void }) {
  const [moldes, setMoldes] = useState<Molde[] | null>(null);
  const [molde, setMolde] = useState<Molde | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getMoldes()
      .then(setMoldes)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, []);

  if (molde) {
    return <TreinoMolde molde={molde} onVoltar={() => setMolde(null)} />;
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <CabecalhoVoltar titulo="Treino com moldes" onVoltar={onVoltar} />
          <Text style={styles.textoSuave}>
            Cada molde parte de uma questão oficial do ENEM e troca os números a cada rodada. Repita até
            resolver sozinho, sem olhar os passos.
          </Text>

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}
          {!moldes && !erro && <ActivityIndicator color={Brand.verde} />}

          {moldes?.map((m) => (
            <Pressable key={m.id_molde} style={styles.cardMolde} onPress={() => setMolde(m)}>
              <View style={styles.cardMoldeTopo}>
                <Text style={styles.cardMoldeTitulo}>{m.titulo}</Text>
                <Feather name="chevron-right" size={18} color={Brand.textoSuave} />
              </View>
              <Text style={styles.meta}>
                {m.materia.replace(/_/g, ' ')} · questão âncora {m.id_questao_ancora.replace(/_/g, ' ')}
              </Text>
              <View style={styles.apelidosRow}>
                {m.kit.map((k) => (
                  <Text key={k.apelido} style={styles.apelido}>
                    {k.apelido}
                  </Text>
                ))}
              </View>
            </Pressable>
          ))}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function TreinoMolde({ molde, onVoltar }: { molde: Molde; onVoltar: () => void }) {
  const [variacao, setVariacao] = useState<VariacaoMolde | null>(null);
  const [escolha, setEscolha] = useState<string | null>(null);
  const [confirmada, setConfirmada] = useState(false);
  const [mostrarPassos, setMostrarPassos] = useState(false);
  const [placar, setPlacar] = useState({ acertos: 0, total: 0 });
  const [erro, setErro] = useState<string | null>(null);

  function carregar(opcoes: { seed?: number; original?: boolean }) {
    setVariacao(null);
    setEscolha(null);
    setConfirmada(false);
    setMostrarPassos(false);
    setErro(null);
    getVariacaoMolde(molde.id_molde, opcoes)
      .then(setVariacao)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }

  useEffect(() => {
    carregar({ seed: novaSeed() });
  }, [molde.id_molde]);

  function confirmar() {
    if (!variacao || !escolha) return;
    setConfirmada(true);
    setPlacar((p) => ({ acertos: p.acertos + (escolha === variacao.correta ? 1 : 0), total: p.total + 1 }));
  }

  const acertou = variacao !== null && escolha === variacao.correta;

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <CabecalhoVoltar titulo={molde.titulo} onVoltar={onVoltar} />
          <Text style={styles.meta}>
            Placar desta sessão: {placar.acertos}/{placar.total} · variações não contam no seu histórico
          </Text>

          <CardKit kit={molde.kit} />

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}
          {!variacao && !erro && <ActivityIndicator color={Brand.verde} />}

          {variacao && (
            <>
              <View style={styles.cardEnunciado}>
                <Text style={styles.enunciado}>{variacao.enunciado}</Text>
              </View>

              {LETRAS.map((letra) => {
                const ehCorreta = confirmada && letra === variacao.correta;
                const ehErradaEscolhida = confirmada && letra === escolha && !acertou;
                return (
                  <Pressable
                    key={letra}
                    disabled={confirmada}
                    onPress={() => setEscolha(letra)}
                    style={[
                      styles.alternativa,
                      !confirmada && escolha === letra && styles.alternativaSelecionada,
                      ehCorreta && styles.alternativaCorreta,
                      ehErradaEscolhida && styles.alternativaErrada,
                    ]}>
                    <Text style={styles.alternativaTexto}>
                      {letra}) {variacao.alternativas[letra]} {variacao.unidade}
                    </Text>
                  </Pressable>
                );
              })}

              {!confirmada ? (
                <Botao onPress={confirmar} disabled={!escolha}>
                  Confirmar
                </Botao>
              ) : (
                <>
                  <View style={[styles.feedback, acertou ? styles.feedbackCerto : styles.feedbackErrado]}>
                    <Text style={styles.feedbackTexto}>
                      {acertou
                        ? `✅ Certo! ${variacao.alternativas[variacao.correta]} ${variacao.unidade}.`
                        : `❌ A certa era ${variacao.correta}) ${variacao.alternativas[variacao.correta]} ${variacao.unidade}.`}
                    </Text>
                    {!acertou && escolha && variacao.distratores[escolha] && (
                      <Text style={styles.feedbackMotivo}>
                        A que você marcou corresponde a: {variacao.distratores[escolha]}.
                      </Text>
                    )}
                  </View>

                  <Pressable onPress={() => setMostrarPassos((v) => !v)} style={styles.linkPassos}>
                    <Feather name={mostrarPassos ? 'chevron-up' : 'chevron-down'} size={16} color={Brand.roxoTextoEscuro} />
                    <Text style={styles.linkPassosTexto}>{mostrarPassos ? 'Esconder' : 'Ver'} o passo a passo</Text>
                  </Pressable>
                  {mostrarPassos && (
                    <View style={styles.cardPassos}>
                      {variacao.passos.map((passo, i) => (
                        <Text key={i} style={styles.passo}>
                          {i + 1}. {passo}
                        </Text>
                      ))}
                    </View>
                  )}

                  <Botao onPress={() => carregar({ seed: novaSeed() })}>
                    {acertou ? 'Próxima variação' : 'Tentar outra variação sozinho'}
                  </Botao>
                </>
              )}

              <Pressable onPress={() => carregar({ original: true })} style={styles.linkOriginal}>
                <Text style={styles.linkOriginalTexto}>Usar os números da questão oficial</Text>
              </Pressable>
            </>
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function CardKit({ kit }: { kit: ItemKit[] }) {
  return (
    <View style={styles.cardKit}>
      <Text style={styles.cardKitTitulo}>Kit</Text>
      {kit.map((k) => (
        <View key={k.apelido} style={styles.kitItem}>
          <Text style={styles.kitFormula}>
            {k.formula} <Text style={styles.kitApelido}>· &quot;{k.apelido}&quot;</Text>
          </Text>
          <Text style={styles.kitGatilho}>Quando usar: {k.gatilho}</Text>
        </View>
      ))}
    </View>
  );
}

function CabecalhoVoltar({ titulo, onVoltar }: { titulo: string; onVoltar: () => void }) {
  return (
    <View style={styles.cabecalho}>
      <Pressable onPress={onVoltar} hitSlop={12}>
        <Feather name="arrow-left" size={22} color={Brand.texto} />
      </Pressable>
      <Text style={styles.titulo}>{titulo}</Text>
    </View>
  );
}

function Botao({ children, onPress, disabled }: { children: string; onPress: () => void; disabled?: boolean }) {
  return (
    <Pressable onPress={onPress} disabled={disabled} style={[styles.botao, disabled && styles.botaoDesabilitado]}>
      <Text style={styles.botaoTexto}>{children}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 96, gap: 12 },
  cabecalho: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  titulo: { fontFamily: Fontes.titulo, fontSize: 22, color: Brand.texto, flexShrink: 1 },
  textoSuave: { fontFamily: Fontes.corpo, fontSize: 13.5, color: Brand.textoSuave },
  meta: { fontFamily: Fontes.corpo, fontSize: 12.5, color: Brand.textoSuave, textTransform: 'none' },
  avisoErro: {
    padding: 12,
    borderRadius: 12,
    backgroundColor: Brand.laranjaBg,
    borderWidth: 1,
    borderColor: '#5C3320',
  },
  avisoErroTexto: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.laranja },
  cardMolde: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 14,
    gap: 6,
  },
  cardMoldeTopo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardMoldeTitulo: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 15.5, color: Brand.texto },
  apelidosRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 2 },
  apelido: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12,
    color: Brand.roxoTextoEscuro,
    backgroundColor: Brand.roxoBgEscuro,
    borderWidth: 1,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: 999,
    paddingVertical: 4,
    paddingHorizontal: 10,
    overflow: 'hidden',
  },
  cardKit: {
    backgroundColor: Brand.roxoBgEscuro,
    borderWidth: 1,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: RaioCard,
    padding: 14,
    gap: 8,
  },
  cardKitTitulo: { fontFamily: Fontes.tituloSemibold, fontSize: 15, color: Brand.roxoTextoEscuro },
  kitItem: { gap: 2 },
  kitFormula: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 14.5, color: Brand.texto },
  kitApelido: { fontFamily: Fontes.corpoNegrito, color: Brand.roxoTextoEscuro },
  kitGatilho: { fontFamily: Fontes.corpo, fontSize: 12.5, color: Brand.roxoTextoSuave },
  cardEnunciado: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 16,
  },
  enunciado: { fontFamily: Fontes.corpo, fontSize: 15, lineHeight: 22, color: Brand.texto },
  alternativa: {
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
    borderRadius: 14,
    padding: 14,
  },
  alternativaSelecionada: { borderColor: Brand.verde, borderWidth: 2 },
  alternativaCorreta: { borderColor: Brand.verde, borderWidth: 2, backgroundColor: '#15250C' },
  alternativaErrada: { borderColor: '#C33F22', borderWidth: 2, backgroundColor: '#2A1414' },
  alternativaTexto: { fontFamily: Fontes.corpo, fontSize: 14.5, color: Brand.texto },
  feedback: { borderWidth: 1, borderRadius: 14, padding: 14, gap: 6 },
  feedbackCerto: { backgroundColor: '#15250C', borderColor: Brand.verdeEscuro },
  feedbackErrado: { backgroundColor: '#2A1414', borderColor: '#5C2323' },
  feedbackTexto: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 14.5, color: Brand.texto },
  feedbackMotivo: { fontFamily: Fontes.corpo, fontSize: 13.5, color: Brand.texto },
  linkPassos: { flexDirection: 'row', alignItems: 'center', gap: 6, alignSelf: 'flex-start' },
  linkPassosTexto: { fontFamily: Fontes.corpoNegrito, fontSize: 13.5, color: Brand.roxoTextoEscuro },
  cardPassos: {
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 14,
    padding: 14,
    gap: 6,
  },
  passo: { fontFamily: Fontes.corpo, fontSize: 13.5, lineHeight: 20, color: Brand.texto },
  botao: {
    backgroundColor: Brand.verde,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 14,
    alignItems: 'center',
  },
  botaoDesabilitado: { opacity: 0.4 },
  botaoTexto: { fontFamily: Fontes.titulo, fontSize: 15, color: '#10230A' },
  linkOriginal: { alignSelf: 'center', paddingVertical: 6 },
  linkOriginalTexto: { fontFamily: Fontes.corpoNegrito, fontSize: 13, color: Brand.textoApagado },
});
