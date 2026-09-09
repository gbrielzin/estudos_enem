import { Feather, Ionicons } from '@expo/vector-icons';
import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Mascote } from '@/components/mascote';
import { MissoesCard } from '@/components/missoes-card';
import { Seletor } from '@/components/seletor';
import { StatusHeader } from '@/components/status-header';
import { TrilhaPath } from '@/components/trilha-path';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import {
  GrandeArea,
  MissaoDoDia,
  Nivel,
  NoTrilha,
  ResultadoTentativa,
  Streak,
  getFontesBancoPratica,
  getMaterias,
  getMissoesDoDia,
  getNivel,
  getStreak,
  getTrilha,
  registrarTentativa,
} from '@/lib/api';
import { separarAlternativas } from '@/lib/alternativas';

const ROTULO_AREA: Record<GrandeArea, string> = {
  matematica: 'Matemática',
  ciencias_natureza: 'Ciências da Natureza',
};
const AREAS: GrandeArea[] = ['matematica', 'ciencias_natureza'];
const LETRAS = ['A', 'B', 'C', 'D', 'E'] as const;

type Tela = { tipo: 'mapa' } | { tipo: 'exercicio'; noIndice: number; posicao: number };

/**
 * Fase 1 do plano de app nativo: Banco de Questões / trilha estilo
 * Duolingo. Visual alinhado ao mockup de referência trazido pelo
 * usuário (redesign-banco-de-questoes.html) -- tema escuro, roxo de
 * marca, cards com badge de ícone colorido (ver constants/brand.ts).
 * Máquina de estados (mapa <-> nó ativo <-> pergunta a pergunta com
 * feedback imediato) idêntica à versão anterior/à do app web
 * (core/cartao_resposta.py render_banco_pratica) -- só a casca visual
 * mudou aqui, nenhuma regra de negócio nova.
 */
export default function TrilhaScreen() {
  const [area, setArea] = useState<GrandeArea>('ciencias_natureza');
  const [materias, setMaterias] = useState<string[]>([]);
  const [materia, setMateria] = useState<string | null>(null);
  const [fontes, setFontes] = useState<string[]>([]);
  const [fonte, setFonte] = useState<string | null>(null);

  const [trilha, setTrilha] = useState<NoTrilha[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const [tela, setTela] = useState<Tela>({ tipo: 'mapa' });
  const [escolha, setEscolha] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoTentativa | null>(null);
  const [enviando, setEnviando] = useState(false);

  const [streak, setStreak] = useState<Streak | null>(null);
  const [nivel, setNivel] = useState<Nivel | null>(null);
  const [missoes, setMissoes] = useState<MissaoDoDia[]>([]);

  // Incrementado pelo banner verde clicável acima da trilha (8.2) pra
  // reabrir o seletor de Matéria sem precisar rolar a tela até o topo.
  const [abrirMateriaSinal, setAbrirMateriaSinal] = useState(0);

  // Estatísticas da rodada atual do nó (tela "Resultado") -- zeradas
  // toda vez que um nó é aberto, acumuladas conforme cada questão é
  // respondida. XP mostrado usa a MESMA fórmula de
  // db.calcular_nivel_jogador() (10 por acerto + 2 por tentativa), só
  // pro delta desta rodada -- não precisa de outra chamada à API.
  const [acertosNoNo, setAcertosNoNo] = useState(0);
  const [errosNoNo, setErrosNoNo] = useState<number[]>([]);
  const [inicioNo, setInicioNo] = useState<number | null>(null);

  function atualizarStatus() {
    getStreak().then(setStreak).catch(() => {});
    getNivel().then(setNivel).catch(() => {});
    getMissoesDoDia().then(setMissoes).catch(() => {});
  }

  useEffect(atualizarStatus, []);

  useEffect(() => {
    setMateria(null);
    setTrilha(null);
    getMaterias(area)
      .then(setMaterias)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, [area]);

  useEffect(() => {
    getFontesBancoPratica()
      .then(setFontes)
      .catch(() => {});
  }, []);

  async function carregarTrilha() {
    if (!materia) return;
    setCarregando(true);
    setErro(null);
    try {
      const dados = await getTrilha(area, materia, fonte);
      setTrilha(dados);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
      setTrilha(null);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    if (materia) carregarTrilha();
  }, [materia, fonte]);

  function abrirNo(no: NoTrilha) {
    const primeiraNaoRespondida = no.questoes.findIndex((q) => !q.ja_respondida);
    setTela({ tipo: 'exercicio', noIndice: no.indice, posicao: primeiraNaoRespondida === -1 ? 0 : primeiraNaoRespondida });
    setEscolha(null);
    setResultado(null);
    setAcertosNoNo(0);
    setErrosNoNo([]);
    setInicioNo(Date.now());
  }

  async function voltarPraTrilha() {
    setTela({ tipo: 'mapa' });
    setEscolha(null);
    setResultado(null);
    await carregarTrilha();
  }

  async function confirmarResposta(idQuestao: string) {
    if (!escolha || tela.tipo !== 'exercicio') return;
    setEnviando(true);
    try {
      const r = await registrarTentativa(idQuestao, escolha);
      setResultado(r);
      if (r.resultado === 'acertou') {
        setAcertosNoNo((n) => n + 1);
      } else {
        setErrosNoNo((atual) => [...atual, tela.posicao + 1]);
      }
      atualizarStatus();
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setEnviando(false);
    }
  }

  function continuar() {
    if (tela.tipo !== 'exercicio') return;
    setTela({ ...tela, posicao: tela.posicao + 1 });
    setEscolha(null);
    setResultado(null);
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <View style={styles.headerRow}>
            <View style={styles.appIcone}>
              <Ionicons name="sparkles" size={20} color={Brand.roxoClaro} />
            </View>
            <Text style={styles.appTitulo}>Banco de Questões</Text>
            <View style={styles.gearBtn}>
              <Feather name="settings" size={18} color={Brand.textoApagado} />
            </View>
          </View>

          {/* Indicador de "curso" -- placeholder pro dia em que existir
              mais de um vestibular pra escolher (mesmo espaço que o
              Duolingo usa pra bandeira do idioma). Sem lógica de troca
              por enquanto, só o elemento visual no lugar certo. */}
          <View style={styles.cursoPill}>
            <Text style={styles.cursoPillTexto}>🎓 ENEM</Text>
          </View>

          <StatusHeader streak={streak} nivel={nivel} />

          <MissoesCard missoes={missoes} />

          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          <Seletor
            rotulo="Área"
            valor={area}
            opcoes={AREAS.map((a) => ({ valor: a, texto: ROTULO_AREA[a] }))}
            aoSelecionar={(v) => setArea(v as GrandeArea)}
            icone="crosshair"
            corIcone={Brand.azul}
            fundoIcone={Brand.azulBg}
          />
          <Seletor
            rotulo="Matéria"
            valor={materia}
            placeholder="Escolha uma matéria"
            opcoes={materias.map((m) => ({ valor: m, texto: m }))}
            aoSelecionar={setMateria}
            icone="file-text"
            corIcone={Brand.teal}
            fundoIcone={Brand.tealBg}
            abrirSinal={abrirMateriaSinal}
          />
          {fontes.length > 0 && (
            <Seletor
              rotulo="Fonte"
              valor={fonte}
              placeholder="Todas"
              opcoes={[{ valor: '', texto: 'Todas' }, ...fontes.map((f) => ({ valor: f, texto: f }))]}
              aoSelecionar={(v) => setFonte(v || null)}
              icone="circle"
              corIcone={Brand.roxoClaro}
              fundoIcone={Brand.roxoBg}
            />
          )}

          {carregando && <ActivityIndicator style={styles.espaco} color={Brand.verde} />}

          {!carregando && materia && trilha !== null && trilha.length === 0 && (
            <Text style={[styles.textoSuave, styles.espaco]}>
              Nenhuma questão do banco de prática ainda em &quot;{materia}&quot;. Adicione em Admin → 🧠 Banco
              de prática (no app web).
            </Text>
          )}

          {trilha && trilha.length > 0 && tela.tipo === 'mapa' && (
            <View style={styles.espaco}>
              {/* Banner verde clicável (8.2), visual da tela "Trilha" do
                  projeto de design: reforça o dropdown "Matéria" de cima
                  em vez de substituí-lo -- toca aqui (ou no círculo) e
                  reabre o mesmo seletor, sem precisar rolar a tela pro
                  topo. */}
              <Pressable style={styles.bannerMateria} onPress={() => setAbrirMateriaSinal((n) => n + 1)}>
                <View style={styles.bannerMateriaTextos}>
                  <Text style={styles.bannerMateriaLabel}>{ROTULO_AREA[area].toUpperCase()}</Text>
                  <Text style={styles.bannerMateriaTexto}>{materia}</Text>
                </View>
                <View style={styles.bannerMateriaBotao}>
                  <Feather name="sliders" size={20} color={Brand.roxoClaro} />
                </View>
              </Pressable>
              <Text style={styles.progressoTexto}>
                {trilha.filter((n) => n.concluido).length} de {trilha.length} nó(s) concluído(s)
              </Text>
              <TrilhaPath trilha={trilha} onAbrirNo={abrirNo} />
            </View>
          )}

          {trilha && trilha.length > 0 && tela.tipo === 'exercicio' && (
            <TelaExercicio
              no={trilha[tela.noIndice]}
              totalNos={trilha.length}
              posicao={tela.posicao}
              escolha={escolha}
              resultado={resultado}
              enviando={enviando}
              materia={materia ?? ''}
              acertosNoNo={acertosNoNo}
              errosNoNo={errosNoNo}
              inicioNo={inicioNo}
              streak={streak}
              onEscolher={setEscolha}
              onConfirmar={confirmarResposta}
              onContinuar={continuar}
              onVoltar={voltarPraTrilha}
            />
          )}
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

function TelaExercicio({
  no,
  totalNos,
  posicao,
  escolha,
  resultado,
  enviando,
  materia,
  acertosNoNo,
  errosNoNo,
  inicioNo,
  streak,
  onEscolher,
  onConfirmar,
  onContinuar,
  onVoltar,
}: {
  no: NoTrilha;
  totalNos: number;
  posicao: number;
  escolha: string | null;
  resultado: ResultadoTentativa | null;
  enviando: boolean;
  materia: string;
  acertosNoNo: number;
  errosNoNo: number[];
  inicioNo: number | null;
  streak: Streak | null;
  onEscolher: (letra: string) => void;
  onConfirmar: (idQuestao: string) => void;
  onContinuar: () => void;
  onVoltar: () => void;
}) {
  if (posicao >= no.questoes.length) {
    return (
      <TelaResultado
        no={no}
        totalNos={totalNos}
        materia={materia}
        acertosNoNo={acertosNoNo}
        errosNoNo={errosNoNo}
        inicioNo={inicioNo}
        streak={streak}
        onVoltar={onVoltar}
      />
    );
  }

  return (
    <View style={styles.espaco}>
      <Pressable style={styles.voltarLink} onPress={onVoltar}>
        <Feather name="arrow-left" size={16} color={Brand.textoSuave} />
        <Text style={styles.voltarTexto}>Voltar pra trilha</Text>
      </Pressable>
      <QuestaoAtual
        questao={no.questoes[posicao]}
        posicao={posicao}
        total={no.questoes.length}
        escolha={escolha}
        resultado={resultado}
        enviando={enviando}
        onEscolher={onEscolher}
        onConfirmar={onConfirmar}
        onContinuar={onContinuar}
      />
    </View>
  );
}

function formatarTempo(ms: number): string {
  const segundosTotais = Math.max(0, Math.round(ms / 1000));
  const minutos = Math.floor(segundosTotais / 60);
  const segundos = segundosTotais % 60;
  return `${minutos}:${String(segundos).padStart(2, '0')}`;
}

/**
 * Tela "Resultado" -- importada do projeto de design do usuário
 * (App ENEM.dc.html, tela "Resultado"): mascote comemorando, 3
 * estatísticas da rodada e card de ofensiva. Acertos/tempo são reais
 * (acumulados durante a rodada); XP usa a MESMA fórmula de
 * db.calcular_nivel_jogador() (10 por acerto + 2 por tentativa) só
 * pro delta desta rodada, sem precisar de endpoint novo.
 */
function TelaResultado({
  no,
  totalNos,
  materia,
  acertosNoNo,
  errosNoNo,
  inicioNo,
  streak,
  onVoltar,
}: {
  no: NoTrilha;
  totalNos: number;
  materia: string;
  acertosNoNo: number;
  errosNoNo: number[];
  inicioNo: number | null;
  streak: Streak | null;
  onVoltar: () => void;
}) {
  const [mostrarErros, setMostrarErros] = useState(false);
  const total = no.questoes.length;
  const xpGanho = acertosNoNo * 10 + total * 2;
  const tempo = inicioNo ? formatarTempo(Date.now() - inicioNo) : '--:--';
  const haProximoNo = no.indice + 1 < totalNos;

  return (
    <View style={styles.espaco}>
      <View style={styles.resultadoContainer}>
        <Mascote color={Brand.branco} shadow={Brand.brancoEscuro} beak={Brand.rosa} mood="cheer" size={1.4} />
        <View style={styles.resultadoTitulo}>
          <Text style={styles.resultadoTituloTexto}>Nó {no.indice + 1} concluído!</Text>
          <Text style={styles.textoSuave}>
            {materia} {haProximoNo ? `· você destravou o Nó ${no.indice + 2}` : '· última leva desta matéria'}
          </Text>
        </View>

        <View style={styles.resultadoStatsRow}>
          <View style={styles.resultadoStatCard}>
            <Text style={styles.resultadoStatValor}>
              {acertosNoNo}/{total}
            </Text>
            <Text style={styles.resultadoStatLabel}>ACERTOS</Text>
          </View>
          <View style={[styles.resultadoStatCard, styles.resultadoStatCardOuro]}>
            <Text style={[styles.resultadoStatValor, { color: Brand.ouro }]}>+{xpGanho}</Text>
            <Text style={[styles.resultadoStatLabel, { color: '#B08A2A' }]}>XP</Text>
          </View>
          <View style={styles.resultadoStatCard}>
            <Text style={styles.resultadoStatValor}>{tempo}</Text>
            <Text style={styles.resultadoStatLabel}>TEMPO</Text>
          </View>
        </View>

        {streak && (
          <View style={styles.resultadoOfensivoCard}>
            <View style={styles.resultadoOfensivoTopo}>
              <Text style={styles.cardConcluidoTitulo}>Ofensivo</Text>
              <Text style={[styles.resultadoStatLabel, { color: Brand.laranja }]}>
                {streak.atual} dia{streak.atual === 1 ? '' : 's'}
              </Text>
            </View>
            <Text style={styles.textoSuave}>Volte amanhã para manter a sequência. Pipo fica de olho.</Text>
          </View>
        )}

        {mostrarErros && errosNoNo.length > 0 && (
          <Text style={styles.textoSuave}>Você errou a(s) questão(ões) {errosNoNo.join(', ')} desta rodada.</Text>
        )}
      </View>

      <Pressable style={styles.botao} onPress={onVoltar}>
        <Text style={styles.botaoTexto}>CONTINUAR</Text>
      </Pressable>
      {errosNoNo.length > 0 && (
        <Pressable style={styles.botaoSecundario} onPress={() => setMostrarErros((v) => !v)}>
          <Text style={styles.botaoSecundarioTexto}>{mostrarErros ? 'OCULTAR ERROS' : 'REVER OS ERROS'}</Text>
        </Pressable>
      )}
    </View>
  );
}

function QuestaoAtual({
  questao,
  posicao,
  total,
  escolha,
  resultado,
  enviando,
  onEscolher,
  onConfirmar,
  onContinuar,
}: {
  questao: NoTrilha['questoes'][number];
  posicao: number;
  total: number;
  escolha: string | null;
  resultado: ResultadoTentativa | null;
  enviando: boolean;
  onEscolher: (letra: string) => void;
  onConfirmar: (idQuestao: string) => void;
  onContinuar: () => void;
}) {
  const { corpo, alternativas } = separarAlternativas(questao.enunciado_texto ?? '');
  const temAlternativas = Object.keys(alternativas).length === 5;

  return (
    <View>
      <Text style={styles.progressoTexto}>
        Questão {posicao + 1} de {total}
      </Text>

      <View style={styles.cardEnunciado}>
        {questao.fonte && <Text style={styles.fonteTexto}>🧠 Banco de prática · fonte: {questao.fonte}</Text>}
        <Text style={styles.enunciadoTexto}>{corpo || questao.enunciado_texto}</Text>
      </View>

      {!resultado ? (
        <>
          {LETRAS.map((letra) => (
            <Pressable
              key={letra}
              style={[styles.alternativa, escolha === letra && styles.alternativaSelecionada]}
              onPress={() => onEscolher(letra)}>
              <Text style={[styles.alternativaTexto, escolha === letra && styles.alternativaTextoSelecionado]}>
                {letra}) {temAlternativas ? alternativas[letra] : ''}
              </Text>
            </Pressable>
          ))}
          <Pressable
            style={[styles.botao, (!escolha || enviando) && styles.botaoDesabilitado]}
            disabled={!escolha || enviando}
            onPress={() => onConfirmar(questao.id_questao)}>
            <Text style={styles.botaoTexto}>{enviando ? 'Enviando…' : 'Confirmar'}</Text>
          </Pressable>
        </>
      ) : (
        <>
          <View style={[styles.cardFeedback, resultado.resultado === 'acertou' ? styles.feedbackCerto : styles.feedbackErrado]}>
            <Text style={styles.feedbackTexto}>
              {resultado.resultado === 'acertou'
                ? `✅ Certo! A resposta era ${resultado.alternativa_correta}.`
                : `❌ Você marcou ${resultado.resposta_escolhida ?? '— (em branco)'}. A resposta certa era ${resultado.alternativa_correta}.`}
            </Text>
          </View>
          <Pressable style={styles.botao} onPress={onContinuar}>
            <Text style={styles.botaoTexto}>Continuar ➜</Text>
          </Pressable>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Brand.bg,
  },
  safeArea: {
    flex: 1,
  },
  scroll: {
    padding: 16,
    gap: 16,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  appIcone: {
    width: 42,
    height: 42,
    borderRadius: 14,
    backgroundColor: Brand.roxo,
    justifyContent: 'center',
    alignItems: 'center',
  },
  appTitulo: {
    flex: 1,
    fontFamily: Fontes.titulo,
    fontSize: 21,
    color: Brand.texto,
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
  cursoPill: {
    alignSelf: 'flex-start',
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 999,
    paddingVertical: 5,
    paddingHorizontal: 12,
  },
  cursoPillTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12.5,
    color: Brand.textoSuave,
  },
  bannerMateria: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: Brand.verde,
    borderRadius: RaioCard,
    paddingVertical: 16,
    paddingHorizontal: 18,
  },
  bannerMateriaTextos: {
    flex: 1,
  },
  bannerMateriaLabel: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12,
    letterSpacing: 1.2,
    color: '#2A5A10',
  },
  bannerMateriaTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 24,
    color: '#0D2705',
    textTransform: 'capitalize',
  },
  bannerMateriaBotao: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: Brand.roxo,
    justifyContent: 'center',
    alignItems: 'center',
  },
  espaco: {
    marginTop: 8,
    gap: 8,
  },
  textoSuave: {
    fontFamily: Fontes.corpo,
    fontSize: 13,
    color: Brand.textoSuave,
  },
  progressoTexto: {
    fontFamily: Fontes.corpoNegrito,
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
  voltarLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  voltarTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14,
    color: Brand.textoSuave,
  },
  cardConcluido: {
    padding: 18,
    borderRadius: RaioCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
    gap: 14,
  },
  cardConcluidoTitulo: {
    fontFamily: Fontes.tituloSemibold,
    fontSize: 15,
    color: Brand.texto,
  },
  resultadoContainer: {
    alignItems: 'center',
    gap: 16,
  },
  resultadoTitulo: {
    alignItems: 'center',
    gap: 4,
    marginTop: 8,
  },
  resultadoTituloTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 28,
    color: Brand.verde,
    textAlign: 'center',
  },
  resultadoStatsRow: {
    flexDirection: 'row',
    gap: 10,
    width: '100%',
  },
  resultadoStatCard: {
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
  resultadoStatCardOuro: {
    backgroundColor: Brand.ouroBg,
    borderColor: Brand.ouroBorda,
  },
  resultadoStatValor: {
    fontFamily: Fontes.titulo,
    fontSize: 22,
    color: Brand.texto,
  },
  resultadoStatLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11,
    letterSpacing: 0.5,
    color: Brand.textoApagado,
  },
  resultadoOfensivoCard: {
    width: '100%',
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 16,
    gap: 8,
  },
  resultadoOfensivoTopo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  botaoSecundario: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: RaioCard,
    alignItems: 'center',
  },
  botaoSecundarioTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 14,
    color: Brand.textoSuave,
  },
  cardEnunciado: {
    padding: 18,
    borderRadius: RaioCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
    gap: 8,
    marginVertical: 8,
  },
  fonteTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    color: Brand.roxoClaro,
  },
  enunciadoTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 15,
    color: Brand.texto,
    lineHeight: 22,
  },
  cardFeedback: {
    padding: 16,
    borderRadius: RaioCard,
    marginVertical: 8,
    borderWidth: 1,
  },
  feedbackTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14.5,
    color: Brand.texto,
  },
  feedbackCerto: {
    backgroundColor: '#12230C',
    borderColor: Brand.verdeEscuro,
  },
  feedbackErrado: {
    backgroundColor: '#2A1414',
    borderColor: '#5C2323',
  },
  alternativa: {
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
  },
  alternativaSelecionada: {
    borderColor: Brand.verde,
    borderWidth: 2,
  },
  alternativaTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 14.5,
    color: Brand.texto,
  },
  alternativaTextoSelecionado: {
    fontFamily: Fontes.corpoExtraNegrito,
    color: Brand.verdeClaro,
  },
  botao: {
    backgroundColor: Brand.verde,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 4,
  },
  botaoDesabilitado: {
    opacity: 0.4,
  },
  botaoTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 15,
    color: '#10230A',
  },
});
