import { Feather } from '@expo/vector-icons';
import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import {
  ProvaCorrigivel,
  QuestaoErrada,
  ResultadoCorrecao,
  corrigirProva,
  getProvas,
} from '@/lib/api';

/**
 * Aba Simulado: cartão-resposta de prova inteira.
 *
 * A pessoa faz a prova (no papel ou no PDF) e marca aqui o que
 * respondeu. A correção vem de db.corrigir_prova() (POST
 * /provas/corrigir): acertos, nota TRI estimada e as questões erradas,
 * cada uma com a explicação da armadilha quando existe
 * (core/explicacoes/explicacoes.jsonl). Cada resposta também vira
 * tentativa, então as erradas entram na revisão espaçada.
 *
 * Substitui a tela "Montar simulado" + "Seu bilhete", que era só o
 * mockup do design, com anos e status fixos e sem prova nenhuma
 * (a tela-bilhete.tsx foi removida).
 *
 * Três fases no mesmo componente (escolher → cartão → resultado), no
 * mesmo padrão de state local de app/index.tsx: as abas customizadas
 * do app não navegam bem para rotas novas (ver comentário em
 * components/app-tabs.tsx).
 */

const LETRAS = ['A', 'B', 'C', 'D', 'E'] as const;

const ROTULO_AREA: Record<string, string> = {
  ciencias_natureza: 'Natureza',
  matematica: 'Matemática',
};

const ROTULO_NIVEL: Record<string, string> = { facil: 'Fácil', medio: 'Médio', dificil: 'Difícil' };
const ORDEM_NIVEL: Record<string, number> = { facil: 0, medio: 1, dificil: 2 };

// A taxonomia (core/db.py) guarda os nomes sem acento; aqui só para exibir.
const ACENTOS: Record<string, string> = {
  fisica: 'física', quimica: 'química', evolucao: 'evolução', genetica: 'genética', optica: 'óptica',
  eletrodinamica: 'eletrodinâmica', eletrostatica: 'eletrostática', cinematica: 'cinemática', dinamica: 'dinâmica',
  estatica: 'estática', acustica: 'acústica', hidrostatica: 'hidrostática', gravitacao: 'gravitação',
  termologia: 'termologia', endocrino: 'endócrino', imunologico: 'imunológico', circulatorio: 'circulatório',
  botanica: 'botânica', reproducao: 'reprodução', saude: 'saúde', publica: 'pública', separacao: 'separação',
  reacoes: 'reações', quimicas: 'químicas', organica: 'orgânica', inorganica: 'inorgânica', funcoes: 'funções',
  organicas: 'orgânicas', ligacoes: 'ligações', solucoes: 'soluções', eletroquimica: 'eletroquímica',
  cinetica: 'cinética', equilibrio: 'equilíbrio', polimeros: 'polímeros', virus: 'vírus', bacterias: 'bactérias',
  ciclos: 'ciclos', biogeoquimicos: 'biogeoquímicos', estatistica: 'estatística', matematica: 'matemática',
  basica: 'básica', razao: 'razão', proporcao: 'proporção', analise: 'análise', combinatoria: 'combinatória',
  funcao: 'função', equacoes: 'equações', projecao: 'projeção', raciocinio: 'raciocínio', logico: 'lógico',
  geometria: 'geometria', espacial: 'espacial', plana: 'plana', probabilidade: 'probabilidade',
}

function nomeMateria(materia: string): string {
  if (materia === 'sem_video_pendente') return 'Sem matéria';
  const texto = materia
    .split('_')
    .map((p) => ACENTOS[p] ?? p)
    .join(' ');
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** Na web a página inteira rola; ao trocar de fase, volta para o topo. */
function useVoltarAoTopo() {
  useEffect(() => {
    if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') window.scrollTo(0, 0);
  }, []);
}

function tituloProva(p: Pick<ProvaCorrigivel, 'ano' | 'grande_area'>): string {
  return `ENEM ${p.ano} · ${ROTULO_AREA[p.grande_area] ?? p.grande_area}`;
}

export default function SimuladoScreen() {
  const [provas, setProvas] = useState<ProvaCorrigivel[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [prova, setProva] = useState<ProvaCorrigivel | null>(null);
  const [resultado, setResultado] = useState<ResultadoCorrecao | null>(null);

  useEffect(() => {
    getProvas()
      .then(setProvas)
      .catch((e) => setErro(e instanceof Error ? e.message : String(e)));
  }, []);

  let conteudo;
  if (resultado) {
    conteudo = (
      <TelaResultado
        resultado={resultado}
        onOutra={() => {
          setResultado(null);
          setProva(null);
        }}
      />
    );
  } else if (prova) {
    conteudo = <TelaCartao prova={prova} onVoltar={() => setProva(null)} onCorrigido={setResultado} />;
  } else {
    conteudo = <TelaEscolher provas={provas} erro={erro} onEscolher={setProva} />;
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>{conteudo}</SafeAreaView>
    </View>
  );
}

function TelaEscolher({
  provas,
  erro,
  onEscolher,
}: {
  provas: ProvaCorrigivel[] | null;
  erro: string | null;
  onEscolher: (p: ProvaCorrigivel) => void;
}) {
  const porAno = useMemo(() => {
    const grupos = new Map<number, ProvaCorrigivel[]>();
    for (const p of provas ?? []) {
      grupos.set(p.ano, [...(grupos.get(p.ano) ?? []), p]);
    }
    return [...grupos.entries()];
  }, [provas]);

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.titulo}>Corrigir simulado</Text>
      <Text style={styles.subtitulo}>
        Fez uma prova do ENEM no papel? Escolha qual foi, marque suas respostas e veja acertos, nota TRI e por que
        errou cada questão.
      </Text>

      {erro && <Text style={styles.erro}>{erro}</Text>}
      {!provas && !erro && <ActivityIndicator color={Brand.verde} style={{ marginTop: 32 }} />}

      {porAno.map(([ano, lista]) => (
        <View key={ano} style={styles.cardAno}>
          <Text style={styles.ano}>{ano}</Text>
          {lista.map((p) => (
            <Pressable key={`${p.caderno}-${p.grande_area}`} style={styles.botaoProva} onPress={() => onEscolher(p)}>
              <View style={{ flex: 1 }}>
                <Text style={styles.botaoProvaTitulo}>{ROTULO_AREA[p.grande_area] ?? p.grande_area}</Text>
                <Text style={styles.botaoProvaDetalhe}>
                  caderno {p.caderno} · {p.total_questoes} questões
                  {p.com_tri < 30 ? ' · sem nota TRI' : ''}
                </Text>
              </View>
              <Feather name="chevron-right" size={18} color={Brand.textoSuave} />
            </Pressable>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}

function TelaCartao({
  prova,
  onVoltar,
  onCorrigido,
}: {
  prova: ProvaCorrigivel;
  onVoltar: () => void;
  onCorrigido: (r: ResultadoCorrecao) => void;
}) {
  useVoltarAoTopo();
  const [respostas, setRespostas] = useState<Record<number, string>>({});
  const [confirmarBranco, setConfirmarBranco] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const marcadas = Object.keys(respostas).length;
  const emBranco = prova.numeros.length - marcadas;

  function marcar(numero: number, letra: string) {
    setConfirmarBranco(false);
    setRespostas((atual) => {
      const novo = { ...atual };
      if (novo[numero] === letra) delete novo[numero];
      else novo[numero] = letra;
      return novo;
    });
  }

  async function corrigir() {
    if (emBranco > 0 && !confirmarBranco) {
      setConfirmarBranco(true);
      return;
    }
    setEnviando(true);
    setErro(null);
    try {
      onCorrigido(await corrigirProva(prova, respostas));
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
      setEnviando(false);
    }
  }

  return (
    <View style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.cabecalho}>
          <Pressable style={styles.voltarBtn} onPress={onVoltar}>
            <Feather name="chevron-left" size={20} color={Brand.texto} />
          </Pressable>
          <View style={{ flex: 1 }}>
            <Text style={styles.tituloMenor}>{tituloProva(prova)}</Text>
            <Text style={styles.subtitulo}>
              caderno {prova.caderno} · {marcadas} de {prova.numeros.length} marcadas · o botão Corrigir fica no fim
            </Text>
          </View>
        </View>

        {prova.numeros.map((numero) => (
          <View key={numero} style={styles.linhaCartao}>
            <Text style={styles.numero}>{numero}</Text>
            {LETRAS.map((letra) => {
              const ativa = respostas[numero] === letra;
              return (
                <Pressable
                  key={letra}
                  onPress={() => marcar(numero, letra)}
                  style={[styles.bolinha, ativa && styles.bolinhaAtiva]}
                  accessibilityLabel={`Questão ${numero}, alternativa ${letra}`}
                >
                  <Text style={[styles.bolinhaLetra, ativa && styles.bolinhaLetraAtiva]}>{letra}</Text>
                </Pressable>
              );
            })}
          </View>
        ))}

        <View style={styles.rodape}>
          {erro && <Text style={styles.erro}>{erro}</Text>}
          <Text style={styles.contador}>
            {marcadas} de {prova.numeros.length} marcadas
            {confirmarBranco ? ` · ${emBranco} vão contar como em branco (errada)` : ''}
          </Text>
          <Pressable style={[styles.botaoPrincipal, enviando && { opacity: 0.6 }]} onPress={corrigir} disabled={enviando}>
            <Text style={styles.botaoPrincipalTexto}>
              {enviando ? 'Corrigindo…' : confirmarBranco ? 'Corrigir mesmo assim' : 'Corrigir'}
            </Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}

function TelaResultado({ resultado, onOutra }: { resultado: ResultadoCorrecao; onOutra: () => void }) {
  useVoltarAoTopo();
  // Fáceis primeiro: na TRI, errar questão fácil derruba mais a nota,
  // então é por elas que vale começar a revisar.
  const erradas = [...resultado.erradas].sort(
    (a, b) => (ORDEM_NIVEL[a.nivel ?? ''] ?? 3) - (ORDEM_NIVEL[b.nivel ?? ''] ?? 3) || a.numero_questao - b.numero_questao,
  );

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.tituloMenor}>{tituloProva(resultado)}</Text>

      <View style={styles.cardPlacar}>
        <View style={styles.placarBloco}>
          <Text style={styles.placarNumero}>
            {resultado.acertos}/{resultado.total}
          </Text>
          <Text style={styles.placarRotulo}>acertos</Text>
        </View>
        <View style={styles.placarBloco}>
          <Text style={[styles.placarNumero, { color: Brand.ouro }]}>{resultado.nota_tri ?? '—'}</Text>
          <Text style={styles.placarRotulo}>nota TRI (estimativa)</Text>
        </View>
      </View>
      {resultado.nota_tri === null && (
        <Text style={styles.aviso}>Esta prova não tem parâmetros TRI suficientes para calcular a nota.</Text>
      )}
      {resultado.em_branco > 0 && (
        <Text style={styles.aviso}>{resultado.em_branco} em branco contaram como erro, igual ao ENEM.</Text>
      )}

      <Text style={styles.secaoTitulo}>O que você errou ({erradas.length})</Text>
      <Text style={styles.aviso}>Comece pelas fáceis: na TRI, são elas que mais derrubam a nota.</Text>

      {erradas.map((q) => (
        <CardErrada key={q.id_questao} questao={q} />
      ))}

      <Pressable style={[styles.botaoPrincipal, { marginTop: 24 }]} onPress={onOutra}>
        <Text style={styles.botaoPrincipalTexto}>Corrigir outra prova</Text>
      </Pressable>
    </ScrollView>
  );
}

function CardErrada({ questao }: { questao: QuestaoErrada }) {
  const [aberto, setAberto] = useState(false);
  return (
    <View style={styles.cardErrada}>
      <View style={styles.cardErradaTopo}>
        <Text style={styles.cardErradaNumero}>Questão {questao.numero_questao}</Text>
        {questao.nivel && <Text style={styles.selo}>{ROTULO_NIVEL[questao.nivel]}</Text>}
      </View>
      <Text style={styles.cardErradaMateria}>{nomeMateria(questao.materia)}</Text>
      <Text style={styles.cardErradaRespostas}>
        Você: {questao.marcada ?? 'em branco'} · Certa: {questao.correta}
      </Text>
      <Pressable onPress={() => setAberto((v) => !v)} style={styles.toggle}>
        <Feather name={aberto ? 'chevron-up' : 'chevron-down'} size={15} color={Brand.roxoTextoEscuro} />
        <Text style={styles.toggleTexto}>{aberto ? 'Ocultar' : '💡 Por que errei'}</Text>
      </Pressable>
      {aberto && (
        <Text style={styles.explicacao}>
          {questao.explicacao ?? 'A explicação desta questão ainda não foi escrita.'}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Brand.bg },
  safeArea: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  titulo: { fontFamily: Fontes.titulo, fontSize: 26, color: Brand.texto },
  tituloMenor: { fontFamily: Fontes.titulo, fontSize: 20, color: Brand.texto },
  subtitulo: { fontFamily: Fontes.corpo, fontSize: 14, color: Brand.textoSuave, marginTop: 4, marginBottom: 16 },
  erro: { fontFamily: Fontes.corpoNegrito, color: Brand.erro, marginVertical: 8 },
  cardAno: {
    backgroundColor: Brand.bgCard,
    borderRadius: RaioCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    padding: 14,
    marginBottom: 12,
  },
  ano: { fontFamily: Fontes.titulo, fontSize: 22, color: Brand.verde, marginBottom: 6 },
  botaoProva: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: Brand.borda,
  },
  botaoProvaTitulo: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 16, color: Brand.texto },
  botaoProvaDetalhe: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.textoSuave, marginTop: 2 },
  cabecalho: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 8 },
  voltarBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Brand.bgCard,
    alignItems: 'center',
    justifyContent: 'center',
  },
  linhaCartao: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: Brand.borda,
  },
  numero: { width: 44, fontFamily: Fontes.corpoExtraNegrito, fontSize: 15, color: Brand.textoSuave },
  bolinha: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: Brand.bordaForte,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  bolinhaAtiva: { backgroundColor: Brand.verde, borderColor: Brand.verde },
  bolinhaLetra: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 15, color: Brand.textoSuave },
  bolinhaLetraAtiva: { color: Brand.bg },
  rodape: { paddingTop: 20 },
  contador: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.textoSuave, marginBottom: 8 },
  botaoPrincipal: { backgroundColor: Brand.verde, borderRadius: 16, paddingVertical: 14, alignItems: 'center' },
  botaoPrincipalTexto: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 16, color: Brand.bg },
  cardPlacar: {
    flexDirection: 'row',
    backgroundColor: Brand.bgCard,
    borderRadius: RaioCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    paddingVertical: 18,
    marginTop: 12,
    marginBottom: 8,
  },
  placarBloco: { flex: 1, alignItems: 'center' },
  placarNumero: { fontFamily: Fontes.titulo, fontSize: 32, color: Brand.verde },
  placarRotulo: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.textoSuave },
  aviso: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.textoSuave, marginBottom: 6 },
  secaoTitulo: { fontFamily: Fontes.tituloSemibold, fontSize: 18, color: Brand.texto, marginTop: 18, marginBottom: 4 },
  cardErrada: {
    backgroundColor: Brand.bgCard,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: Brand.borda,
    padding: 14,
    marginTop: 10,
  },
  cardErradaTopo: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardErradaNumero: { fontFamily: Fontes.corpoExtraNegrito, fontSize: 15, color: Brand.texto },
  selo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    color: Brand.ouro,
    backgroundColor: Brand.ouroBg,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    overflow: 'hidden',
  },
  cardErradaMateria: { fontFamily: Fontes.corpo, fontSize: 13, color: Brand.textoSuave, marginTop: 2 },
  cardErradaRespostas: { fontFamily: Fontes.corpoNegrito, fontSize: 14, color: Brand.texto, marginTop: 6 },
  toggle: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 10 },
  toggleTexto: { fontFamily: Fontes.corpoNegrito, fontSize: 14, color: Brand.roxoTextoEscuro },
  explicacao: { fontFamily: Fontes.corpo, fontSize: 14, lineHeight: 21, color: Brand.texto, marginTop: 8 },
});
