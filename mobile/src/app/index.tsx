import { Feather, Ionicons } from '@expo/vector-icons';
import { useAudioPlayer } from 'expo-audio';
import { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Animated, Easing, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Mascote } from '@/components/mascote';
import { MissoesCard } from '@/components/missoes-card';
import { Seletor } from '@/components/seletor';
import { StatusHeader } from '@/components/status-header';
import { TrilhaFixaPath } from '@/components/trilha-fixa-path';
import { TrilhaPath } from '@/components/trilha-path';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { interpolarSombraBotao, useInteracaoBotao } from '@/hooks/use-interacao-botao';
import { RESUMOS_POR_CHAVE_TRILHA_FIXA, RESUMOS_TRILHA, ResumoTrilha, TopicoResumo } from '@/constants/resumos-trilha';
import {
  GrandeArea,
  MissaoDoDia,
  Nivel,
  NoTrilha,
  NoTrilhaFixa,
  ResultadoTentativa,
  Streak,
  getFontesBancoPratica,
  getMaterias,
  getMateriasComBancoPratica,
  getMissoesDoDia,
  getNivel,
  getResolucoes,
  getStreak,
  getTrilha,
  getTrilhaFixa,
  registrarTentativa,
  reportarQuestao,
  Resolucao,
} from '@/lib/api';

/**
 * Reatribui `indice` de cada bloco pra uma sequência ÚNICA e GLOBAL
 * através de todas as matérias da trilha fixa -- os blocos que vêm da
 * API já têm `indice` correto DENTRO da própria matéria (0, 1, 2...),
 * mas repetido entre matérias diferentes. Precisamos de um índice
 * global porque a tela de exercício/resultado (`tela.noIndice`)
 * endereça um array achatado (`trilhaFlat` abaixo), não a estrutura
 * aninhada por matéria -- sem isso, abrir o nó 0 da 2ª matéria
 * reabriria por engano o nó 0 da 1ª.
 */
function comIndicesGlobais(trilhaFixa: NoTrilhaFixa[]): NoTrilhaFixa[] {
  let contador = 0;
  return trilhaFixa.map((materiaNo) => ({
    ...materiaNo,
    blocos: materiaNo.blocos.map((bloco) => ({ ...bloco, indice: contador++ })),
  }));
}

/**
 * Máscara do modo admin/teste pra trilha fixa: força TODA matéria e
 * TODO bloco a aparecer desbloqueado no mapa, mesmo que a matéria
 * anterior não tenha sido concluída de verdade. `concluido` também
 * vira `false` em todo mundo -- senão uma matéria já 100% feita
 * continuaria colapsando no card resumido (SecaoConcluida em
 * trilha-fixa-path.tsx), escondendo os nós dela. Só afeta o que é
 * RENDERIZADO -- o dado real que veio da API (e o que vai ser
 * persistido ao responder) não muda em nada.
 */
function desbloquearTudoFixa(trilhaFixa: NoTrilhaFixa[]): NoTrilhaFixa[] {
  return trilhaFixa.map((materiaNo) => ({
    ...materiaNo,
    concluido: false,
    desbloqueado: true,
    blocos: materiaNo.blocos.map((bloco) => ({ ...bloco, desbloqueado: true })),
  }));
}

/** Mesma ideia de desbloquearTudoFixa(), só que pra trilha de UMA
 * matéria só (modo antigo, fora de Ciências da Natureza). */
function desbloquearTudoFlat(trilha: NoTrilha[]): NoTrilha[] {
  return trilha.map((bloco) => ({ ...bloco, desbloqueado: true }));
}

import { separarAlternativas } from '@/lib/alternativas';

/**
 * Resumo curado a mostrar em "Apresentação"/"Rever conteúdo base" --
 * tenta primeiro por CHAVE do nó da trilha fixa
 * (RESUMOS_POR_CHAVE_TRILHA_FIXA, granularidade de FASE, ex: só
 * Poluição Atmosférica dentro de Ecologia), e só se não achar cai pro
 * fallback por matéria inteira (RESUMOS_TRILHA, usado pela trilha
 * "solta" fora de Ciências da Natureza, onde não existe conceito de
 * fase). Sem isso, um nó da trilha fixa cujo `nome` de exibição é
 * "Ecologia — Poluição Atmosférica" nunca batia com a chave
 * 'ecologia' de RESUMOS_TRILHA (nem deveria -- RESUMOS_TRILHA é POR
 * MATÉRIA INTEIRA, não por fase) -- achado ao vivo reportando pelo
 * usuário (ver docs/pesquisa_estrategia_de_prova.md §8): o link
 * "Rever conteúdo base" nunca aparecia em Ecologia mesmo já existindo
 * um resumo escrito pra fase 4 (RESUMOS_FASE_ECOLOGIA[4]).
 */
function resumoDoNo(materia: string, chave: string | undefined): ResumoTrilha | undefined {
  return (chave ? RESUMOS_POR_CHAVE_TRILHA_FIXA[chave] : undefined) ?? RESUMOS_TRILHA[materia];
}

const ROTULO_AREA: Record<GrandeArea, string> = {
  matematica: 'Matemática',
  ciencias_natureza: 'Ciências da Natureza',
};
const AREAS: GrandeArea[] = ['matematica', 'ciencias_natureza'];
const LETRAS = ['A', 'B', 'C', 'D', 'E'] as const;

/**
 * `apresentacao` ganhou `retomarNoIndice`/`retomarPosicao` opcionais
 * -- pedido explícito do usuário: no meio de uma questão, se o aluno
 * "esqueceu uma coisa", ele precisa conseguir voltar pro conteúdo
 * base (a mesma TelaApresentacao que já abre antes do Nó 1) e depois
 * voltar pra ESSA questão específica, sem perder acertosNoNo/
 * errosNoNo/temposQuestoesNoNo da rodada em andamento (que abrirNo()
 * zeraria). Quando os dois campos vêm undefined, é a apresentação
 * "de entrada" normal (antes do Nó 1); quando vêm preenchidos, é uma
 * revisão no meio de um nó já aberto.
 */
type Tela =
  | { tipo: 'mapa' }
  | { tipo: 'apresentacao'; retomarNoIndice?: number; retomarPosicao?: number }
  | { tipo: 'exercicio'; noIndice: number; posicao: number };

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
  // Só preenchido quando area === 'ciencias_natureza': estrutura
  // aninhada por matéria, usada só pra renderizar o mapa
  // (TrilhaFixaPath). `trilha` acima fica com a versão ACHATADA dos
  // mesmos blocos (ver comIndicesGlobais) -- é o que a tela de
  // exercício/resultado usa, sem precisar saber que existe trilha fixa.
  const [trilhaFixa, setTrilhaFixa] = useState<NoTrilhaFixa[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const [tela, setTela] = useState<Tela>({ tipo: 'mapa' });
  const [escolha, setEscolha] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoTentativa | null>(null);
  const [enviando, setEnviando] = useState(false);

  // Modo admin/teste -- pedido explícito do usuário pra conseguir
  // testar o app melhor: com isto ligado, TODO nó/matéria aparece
  // desbloqueado no mapa (mesmo os que dependeriam de terminar algo
  // antes) e a tela de exercício ganha um botão "Pular" que avança pra
  // próxima questão sem responder. Não muda NADA na regra de negócio
  // do backend (db.trilha_fixa()/trilha_banco_pratica() continuam
  // calculando o desbloqueio real) -- é só uma máscara na hora de
  // RENDERIZAR o mapa (ver desbloquearTudoFixa/desbloquearTudoFlat
  // abaixo) e no fluxo de exercício. Responder de verdade (Confirmar)
  // continua chamando confirmarResposta() normalmente -- streak,
  // Leitner, tempo por questão, tudo grava igual; só o "Pular" não
  // registra tentativa nenhuma, de propósito, pra não sujar as
  // estatísticas reais com respostas puladas em teste.
  const [modoAdmin, setModoAdmin] = useState(false);

  const [streak, setStreak] = useState<Streak | null>(null);
  const [nivel, setNivel] = useState<Nivel | null>(null);
  const [missoes, setMissoes] = useState<MissaoDoDia[]>([]);

  // Incrementado pelo banner verde clicável acima da trilha (8.2) pra
  // reabrir o seletor de Matéria sem precisar rolar a tela até o topo.
  const [abrirMateriaSinal, setAbrirMateriaSinal] = useState(0);

  // "Home" (cabeçalho genérico + status + missões + seletores de Área/
  // Matéria/Fonte) só aparece quando pedida -- pedido explícito do
  // usuário, mesma mudança que a versão Streamlit já tinha
  // (_renderizar_tela_trilha entra direto na trilha, Home só existe
  // pra quem quer trocar de matéria via "⬅️ Trocar matéria"). Aqui é
  // um toggle em vez de duas telas separadas porque tudo já vive no
  // mesmo componente. Começa false: o efeito de [area] abaixo tenta
  // escolher uma matéria padrão sozinho: só vira true se não tiver
  // nenhuma matéria pra escolher, ou quando o usuário toca no banner
  // "trocar matéria" da trilha.
  const [mostrarHome, setMostrarHome] = useState(false);

  // Estatísticas da rodada atual do nó (tela "Resultado") -- zeradas
  // toda vez que um nó é aberto, acumuladas conforme cada questão é
  // respondida. XP mostrado usa a MESMA fórmula de
  // db.calcular_nivel_jogador() (10 por acerto + 2 por tentativa), só
  // pro delta desta rodada -- não precisa de outra chamada à API.
  const [acertosNoNo, setAcertosNoNo] = useState(0);
  const [errosNoNo, setErrosNoNo] = useState<number[]>([]);
  const [inicioNo, setInicioNo] = useState<number | null>(null);
  // Tempo gasto (ms) em cada questão JÁ CONFIRMADA neste nó, na ordem
  // em que foram respondidas -- alimenta o cronômetro/estimativa de
  // QuestaoAtual (média das já respondidas × questões restantes).
  // Deliberadamente só em memória (pedido explícito do usuário: não
  // precisa persistir no banco, é só pra dar noção de ritmo durante a
  // sessão) -- some ao trocar de nó ou fechar o app.
  const [temposQuestoesNoNo, setTemposQuestoesNoNo] = useState<number[]>([]);

  function atualizarStatus() {
    getStreak().then(setStreak).catch(() => {});
    getNivel().then(setNivel).catch(() => {});
    getMissoesDoDia().then(setMissoes).catch(() => {});
  }

  useEffect(atualizarStatus, []);

  useEffect(() => {
    setMateria(null);
    setTrilha(null);
    setTrilhaFixa(null);
    if (area === 'ciencias_natureza') {
      // Ciências da Natureza usa a trilha fixa entrelaçada (efeito
      // abaixo) -- não precisa de seletor de matéria, então nem chama
      // getMaterias/getMateriasComBancoPratica aqui.
      return;
    }
    // Mesmo padrão de db._padrao_materia_banco_pratica() (Streamlit):
    // prefere a matéria com MAIS questão de banco de prática já
    // cadastrada, não a 1a em ordem alfabética da taxonomia inteira
    // (a maioria sem nenhuma questão ainda) -- é o que permite entrar
    // direto na trilha sem escolha manual.
    Promise.all([getMaterias(area), getMateriasComBancoPratica(area)])
      .then(([todas, comPratica]) => {
        setMaterias(todas);
        const padrao = comPratica[0] ?? todas[0] ?? null;
        if (padrao) {
          setMateria(padrao);
        } else {
          setMostrarHome(true);
        }
      })
      .catch((e) => {
        setErro(e instanceof Error ? e.message : String(e));
        setMostrarHome(true);
      });
  }, [area]);

  async function carregarTrilhaFixa() {
    setCarregando(true);
    setErro(null);
    try {
      const dados = comIndicesGlobais(await getTrilhaFixa());
      setTrilhaFixa(dados);
      setTrilha(dados.flatMap((materiaNo) => materiaNo.blocos));
      setMostrarHome(false);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
      setTrilhaFixa(null);
      setTrilha(null);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    if (area === 'ciencias_natureza') carregarTrilhaFixa();
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
      if (dados.length > 0) setMostrarHome(false);
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
    setTemposQuestoesNoNo([]);
    setInicioNo(Date.now());
  }

  async function voltarPraTrilha() {
    setTela({ tipo: 'mapa' });
    setEscolha(null);
    setResultado(null);
    if (area === 'ciencias_natureza') {
      await carregarTrilhaFixa();
    } else {
      await carregarTrilha();
    }
  }

  async function confirmarResposta(idQuestao: string, duracaoMs: number) {
    if (!escolha || tela.tipo !== 'exercicio') return;
    setEnviando(true);
    try {
      const r = await registrarTentativa(idQuestao, escolha, duracaoMs / 1000);
      setResultado(r);
      if (r.resultado === 'acertou') {
        setAcertosNoNo((n) => n + 1);
      } else {
        setErrosNoNo((atual) => [...atual, tela.posicao + 1]);
      }
      setTemposQuestoesNoNo((atual) => [...atual, duracaoMs]);
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

  // "Rever conteúdo base" -- pedido explícito do usuário: sai da
  // questão atual pra TelaApresentacao (mesmo componente/conteúdo
  // curado que abre antes do Nó 1) guardando ONDE estava, pra voltar
  // pra essa mesma questão depois (ver Tela acima). Não passa por
  // abrirNo() de propósito -- não pode zerar acertosNoNo/errosNoNo/
  // temposQuestoesNoNo da rodada em andamento.
  function verConteudoBase() {
    if (tela.tipo !== 'exercicio') return;
    setTela({ tipo: 'apresentacao', retomarNoIndice: tela.noIndice, retomarPosicao: tela.posicao });
  }

  function voltarDaRevisaoDeConteudo(noIndice: number, posicao: number) {
    setTela({ tipo: 'exercicio', noIndice, posicao });
  }

  // Só existe com modoAdmin ligado (botão "Pular" em QuestaoAtual):
  // avança sem chamar registrarTentativa -- de propósito, não conta
  // como tentativa de verdade (não mexe em acerto/erro, Leitner nem
  // duracao_segundos). É especificamente pra pular questão que o
  // usuário não quer resolver de verdade só pra testar o resto do
  // fluxo (ex: chegar rápido no fim de um bloco de 10 questões).
  function pularQuestao() {
    if (tela.tipo !== 'exercicio') return;
    setTela({ ...tela, posicao: tela.posicao + 1 });
    setEscolha(null);
    setResultado(null);
  }

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {erro && (
            <View style={styles.avisoErro}>
              <Text style={styles.avisoErroTexto}>⚠️ {erro}</Text>
            </View>
          )}

          {mostrarHome && (
            <>
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
            </>
          )}

          {!mostrarHome && carregando && <ActivityIndicator style={styles.espaco} color={Brand.verde} />}

          {!mostrarHome && tela.tipo === 'mapa' && (trilhaFixa || trilha) && (
            <Pressable style={styles.modoAdminToggle} onPress={() => setModoAdmin((v) => !v)}>
              <Feather name={modoAdmin ? 'unlock' : 'lock'} size={14} color={modoAdmin ? Brand.verde : Brand.textoApagado} />
              <Text style={[styles.modoAdminTexto, modoAdmin && styles.modoAdminTextoAtivo]}>
                Modo teste {modoAdmin ? '(tudo desbloqueado)' : ''}
              </Text>
            </Pressable>
          )}

          {area === 'ciencias_natureza' && trilhaFixa && trilhaFixa.length > 0 && tela.tipo === 'mapa' && (
            <View style={styles.espaco}>
              {/* Mesmo papel do bannerMateria abaixo (voltar pra Home
                  pra trocar de Área), mas sem seletor de Matéria -- a
                  trilha fixa não tem matéria pra escolher, a ordem é
                  fixa entre todas elas (ver TRILHA_FIXA_NOS). */}
              <Pressable style={styles.bannerMateria} onPress={() => setMostrarHome(true)}>
                <View style={styles.bannerMateriaTextos}>
                  <Text style={styles.bannerMateriaLabel}>TRILHA FIXA</Text>
                  <Text style={styles.bannerMateriaTexto}>Ciências da Natureza</Text>
                </View>
                <View style={styles.bannerMateriaBotao}>
                  <Feather name="sliders" size={20} color={Brand.roxoClaro} />
                </View>
              </Pressable>
              <TrilhaFixaPath trilhaFixa={modoAdmin ? desbloquearTudoFixa(trilhaFixa) : trilhaFixa} onAbrirNo={abrirNo} />
            </View>
          )}

          {area !== 'ciencias_natureza' && trilha && trilha.length > 0 && tela.tipo === 'mapa' && (
            <View style={styles.espaco}>
              {/* Banner verde clicável (8.2), visual da tela "Trilha" do
                  projeto de design: reforça o dropdown "Matéria" de cima
                  em vez de substituí-lo -- toca aqui (ou no círculo) e
                  reabre o mesmo seletor, sem precisar rolar a tela pro
                  topo. Também é o único jeito de voltar pra Home agora
                  que ela não é mais a tela inicial (pedido explícito do
                  usuário, mesma mudança que a versão Streamlit já
                  tinha). */}
              <Pressable
                style={styles.bannerMateria}
                onPress={() => {
                  setMostrarHome(true);
                  setAbrirMateriaSinal((n) => n + 1);
                }}>
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
              <TrilhaPath
                trilha={modoAdmin ? desbloquearTudoFlat(trilha) : trilha}
                resumo={materia ? RESUMOS_TRILHA[materia] : undefined}
                onAbrirNo={abrirNo}
                onAbrirResumo={() => setTela({ tipo: 'apresentacao' })}
              />
            </View>
          )}

          {trilha && trilha.length > 0 && tela.tipo === 'apresentacao' && (
            <TelaApresentacaoRoteada
              tela={tela}
              trilha={trilha}
              trilhaFixa={trilhaFixa}
              materia={materia}
              onComecar={() => abrirNo(trilha[0])}
              onVoltarRevisao={voltarDaRevisaoDeConteudo}
              onVoltarMapa={() => setTela({ tipo: 'mapa' })}
            />
          )}

          {trilha && trilha.length > 0 && tela.tipo === 'exercicio' && (
            <TelaExercicio
              no={trilha[tela.noIndice]}
              totalNos={trilha.length}
              posicao={tela.posicao}
              escolha={escolha}
              resultado={resultado}
              enviando={enviando}
              materia={
                materia ??
                trilhaFixa?.find((m) => m.blocos.some((b) => b.indice === tela.noIndice))?.nome ??
                ''
              }
              chave={trilhaFixa?.find((m) => m.blocos.some((b) => b.indice === tela.noIndice))?.chave}
              acertosNoNo={acertosNoNo}
              errosNoNo={errosNoNo}
              temposQuestoesNoNo={temposQuestoesNoNo}
              inicioNo={inicioNo}
              streak={streak}
              modoAdmin={modoAdmin}
              onEscolher={setEscolha}
              onConfirmar={confirmarResposta}
              onContinuar={continuar}
              onPular={pularQuestao}
              onVoltar={voltarPraTrilha}
              onVerConteudo={verConteudoBase}
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
  chave,
  acertosNoNo,
  errosNoNo,
  temposQuestoesNoNo,
  inicioNo,
  streak,
  modoAdmin,
  onEscolher,
  onConfirmar,
  onContinuar,
  onPular,
  onVoltar,
  onVerConteudo,
}: {
  no: NoTrilha;
  totalNos: number;
  posicao: number;
  escolha: string | null;
  resultado: ResultadoTentativa | null;
  enviando: boolean;
  materia: string;
  chave: string | undefined;
  acertosNoNo: number;
  errosNoNo: number[];
  temposQuestoesNoNo: number[];
  inicioNo: number | null;
  streak: Streak | null;
  modoAdmin: boolean;
  onEscolher: (letra: string) => void;
  onConfirmar: (idQuestao: string, duracaoMs: number) => void;
  onContinuar: () => void;
  onPular: () => void;
  onVoltar: () => void;
  onVerConteudo: () => void;
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
        materia={materia}
        chave={chave}
        escolha={escolha}
        resultado={resultado}
        enviando={enviando}
        temposAnteriores={temposQuestoesNoNo}
        modoAdmin={modoAdmin}
        onEscolher={onEscolher}
        onConfirmar={onConfirmar}
        onContinuar={onContinuar}
        onPular={onPular}
        onVerConteudo={onVerConteudo}
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

const CORES_FREQUENCIA: Record<TopicoResumo['frequencia'], { bgIcone: string; cor: string }> = {
  alta: { bgIcone: '#1F2937', cor: Brand.verde },
  media: { bgIcone: Brand.ouroBg, cor: Brand.ouro },
  baixa: { bgIcone: Brand.bgCardEscuro, cor: Brand.textoSuave },
};

/**
 * Roteia `tela.tipo === 'apresentacao'` entre os dois usos da MESMA
 * TelaApresentacao: entrada normal (antes do Nó 1, zera a rodada via
 * abrirNo) ou revisão no meio de uma questão (retomarNoIndice/
 * retomarPosicao preenchidos, ver Tela acima) -- nesse 2º caso "Voltar"
 * e "Entendi" fazem a MESMA coisa (voltar pra questão de onde saiu),
 * então nenhum dos dois pode reiniciar o nó. Sem resumo curado pra
 * essa matéria (RESUMOS_TRILHA não cobre todas ainda), não renderiza
 * nada -- não faz sentido oferecer "rever conteúdo" pra quem não tem
 * conteúdo nenhum escrito.
 */
function TelaApresentacaoRoteada({
  tela,
  trilha,
  trilhaFixa,
  materia,
  onComecar,
  onVoltarRevisao,
  onVoltarMapa,
}: {
  tela: Extract<Tela, { tipo: 'apresentacao' }>;
  trilha: NoTrilha[];
  trilhaFixa: NoTrilhaFixa[] | null;
  materia: string | null;
  onComecar: () => void;
  onVoltarRevisao: (noIndice: number, posicao: number) => void;
  onVoltarMapa: () => void;
}) {
  const emRevisao = tela.retomarNoIndice !== undefined;
  const noFixaAlvo = trilhaFixa?.find((m) => m.blocos.some((b) => b.indice === (tela.retomarNoIndice ?? -1)));
  const materiaAlvo = materia ?? noFixaAlvo?.nome ?? '';
  const resumo = resumoDoNo(materiaAlvo, noFixaAlvo?.chave);
  if (!resumo) return null;

  const voltar = emRevisao
    ? () => onVoltarRevisao(tela.retomarNoIndice as number, tela.retomarPosicao ?? 0)
    : onVoltarMapa;

  return (
    <TelaApresentacao
      resumo={resumo}
      materia={materiaAlvo}
      modoRevisao={emRevisao}
      onComecar={emRevisao ? voltar : onComecar}
      onVoltar={voltar}
    />
  );
}

/**
 * Tela "Apresentação" -- resumo de conceitos que abre a trilha ANTES
 * do Nó 1, pedido explícito do usuário: dar uma base pro aluno antes
 * de jogar ele direto numa "porrada de questão" -- ele lê isto, ganha
 * o vocabulário mínimo (ex: "índice de refração", "Lei de Snell"), e
 * só DEPOIS entra na repetição de verdade dos nós, que continua sendo
 * o grosso do trabalho (a apresentação é 1 tela, não substitui a
 * prática). Conteúdo vem de RESUMOS_TRILHA (constants/resumos-trilha.ts)
 * -- curado à mão por matéria, não derivado do banco. Visual importado
 * do projeto de design do usuário (App ENEM.dc.html, tela
 * "Apresentação").
 *
 * `modoRevisao` (ver TelaApresentacaoRoteada acima) só muda rótulo e
 * texto do botão -- pedido explícito do usuário pra poder voltar pra
 * cá no meio de uma questão ("esqueci uma coisa") e retomar de onde
 * parou, em vez de só ser a tela de abertura do nó.
 */
function TelaApresentacao({
  resumo,
  materia,
  modoRevisao,
  onComecar,
  onVoltar,
}: {
  resumo: ResumoTrilha;
  materia: string;
  modoRevisao?: boolean;
  onComecar: () => void;
  onVoltar: () => void;
}) {
  return (
    <View style={styles.espaco}>
      <View style={styles.apresentacaoPainel}>
        <View style={styles.apresentacaoHeaderRow}>
          <Pressable style={styles.apresentacaoVoltarBtn} onPress={onVoltar}>
            <Feather name="chevron-left" size={18} color={Brand.roxoTextoEscuro} />
          </Pressable>
          <Text style={styles.apresentacaoRotulo}>
            {modoRevisao ? 'CONTEÚDO BASE' : 'APRESENTAÇÃO'} · {materia.toUpperCase()}
          </Text>
          <View style={styles.apresentacaoMinutosPill}>
            <Text style={styles.apresentacaoMinutosTexto}>{resumo.minutos} min</Text>
          </View>
        </View>

        <View style={styles.apresentacaoTituloRow}>
          <View style={styles.apresentacaoTituloTextos}>
            <Text style={styles.apresentacaoTitulo}>{resumo.titulo}</Text>
            <Text style={styles.apresentacaoSubtitulo}>{resumo.subtitulo}</Text>
          </View>
          {/* Pipoco de tuxedo -- variação da tela Apresentação do
              projeto de design (dc-import scene="estudo" pattern=
              "tuxedo"), corpo continua branco, só o "capuz" muda. */}
          <Mascote
            color={Brand.branco}
            shadow={Brand.brancoEscuro}
            beak={Brand.rosa}
            mood="happy"
            size={0.66}
            pattern="tuxedo"
            patch={Brand.mascoteTuxedoMancha}
          />
        </View>
      </View>

      <View style={styles.apresentacaoSecaoTitulo}>
        <Text style={styles.apresentacaoSecaoTexto}>O QUE MAIS CAI NA PROVA</Text>
        <View style={styles.apresentacaoSecaoLinha} />
      </View>

      {resumo.topicos.map((topico) => {
        const cores = CORES_FREQUENCIA[topico.frequencia];
        return (
          <View key={topico.titulo} style={styles.apresentacaoTopicoCard}>
            <View style={[styles.apresentacaoTopicoIcone, { backgroundColor: cores.bgIcone }]}>
              <Ionicons name="ellipse" size={12} color={cores.cor} />
            </View>
            <View style={styles.apresentacaoTopicoTextos}>
              <Text style={styles.apresentacaoTopicoTitulo}>{topico.titulo}</Text>
              <Text style={styles.textoSuave}>{topico.descricao}</Text>
            </View>
            <Text style={[styles.apresentacaoTopicoFrequencia, { color: cores.cor }]}>{topico.frequencia}</Text>
          </View>
        );
      })}

      <View style={styles.apresentacaoEstatistica}>
        <Text style={styles.apresentacaoEstatisticaNumero}>{resumo.estatisticaNumero}</Text>
        <Text style={styles.apresentacaoEstatisticaTexto}>{resumo.estatisticaTexto}</Text>
      </View>

      <BotaoPrimario onPress={onComecar}>
        {modoRevisao ? 'Voltar pra questão' : 'Entendi, começar o Nó 1'}
      </BotaoPrimario>
      {/* Em modoRevisao, onVoltar === onComecar (ver TelaApresentacaoRoteada)
          -- um 2º botão pro mesmo destino só duplicaria a ação. */}
      {!modoRevisao && (
        <Pressable style={styles.apresentacaoReverLink} onPress={onVoltar}>
          <Text style={styles.apresentacaoReverTexto}>Rever depois</Text>
        </Pressable>
      )}
    </View>
  );
}

/**
 * Tela "Resultado" -- importada do projeto de design do usuário
 * (App ENEM.dc.html, tela "Resultado"): mascote comemorando, 3
 * estatísticas da rodada e card de ofensiva. Acertos/tempo são reais
 * (acumulados durante a rodada); XP usa a MESMA fórmula de
 * db.calcular_nivel_jogador() (10 por acerto + 2 por tentativa) só
 * pro delta desta rodada, sem precisar de endpoint novo.
 */
/**
 * "XP sobe" -- padrão de movimento 6a do projeto de design (Claude
 * Design, App ENEM.dc.html, TURNO 6 "Gramática de animação"): no
 * design é um "+320" que sobe e desbota por cima de um total que já
 * existe na tela, some no topo, e SÓ ENTÃO o total antigo troca pro
 * novo -- essa tela de Resultado não tem um "total de XP" visível (só
 * o delta da rodada), então adaptei pra a entrada do próprio número:
 * sobe com uma pequena sobra elástica e FICA (sem a fase de sumir no
 * topo, que não faz sentido aqui -- é o único número de XP da tela,
 * apagar deixaria o card vazio).
 */
function XpSobe({ children }: { children: string }) {
  const entrada = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(entrada, { toValue: 1, duration: 380, easing: Easing.out(Easing.quad), useNativeDriver: false }).start();
  }, [entrada]);
  const translateY = entrada.interpolate({ inputRange: [0, 0.3, 1], outputRange: [14, -4, -10] });
  const scale = entrada.interpolate({ inputRange: [0, 0.3, 1], outputRange: [0.8, 1.08, 1] });
  const opacity = entrada.interpolate({ inputRange: [0, 0.2, 1], outputRange: [0, 1, 1] });
  return (
    <Animated.Text style={[styles.resultadoStatValor, { color: Brand.ouro, opacity, transform: [{ translateY }, { scale }] }]}>
      {children}
    </Animated.Text>
  );
}

/**
 * "Lição destrava" -- padrão de movimento 6a do projeto de design
 * (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de animação"):
 * nó da trilha concluído -- círculo estufa (340ms), depois o tique
 * desenha por cima (180ms), com 3 papéis de confete caindo espaçados
 * (900ms cada, nunca uma chuva -- "o confete cheio fica pro fim da
 * unidade", ainda não construído). Vive na tela de Resultado (não na
 * trilha em si) porque é aqui que o momento "acabei de concluir"
 * acontece de verdade -- a trilha, quando reaberta depois, já mostra
 * o nó concluído parado, sem transição pra animar.
 */
function SeloDestravado() {
  const pop = useRef(new Animated.Value(0)).current;
  const tique = useRef(new Animated.Value(0)).current;
  const confetes = useRef([0, 1, 2].map(() => new Animated.Value(0))).current;

  useEffect(() => {
    Animated.sequence([
      Animated.timing(pop, { toValue: 1, duration: 340, easing: Easing.out(Easing.back(1.6)), useNativeDriver: false }),
      Animated.timing(tique, { toValue: 1, duration: 180, easing: Easing.out(Easing.back(1.4)), useNativeDriver: false }),
    ]).start();
    confetes.forEach((v, i) => {
      Animated.timing(v, { toValue: 1, duration: 900, delay: i * 250, easing: Easing.linear, useNativeDriver: false }).start();
    });
  }, [pop, tique, confetes]);

  const tiqueEscala = tique.interpolate({ inputRange: [0, 1], outputRange: [0.4, 1] });
  const tiqueRotacao = tique.interpolate({ inputRange: [0, 1], outputRange: ['-12deg', '0deg'] });

  return (
    <View style={styles.seloWrap}>
      {confetes.map((v, i) => {
        const translateY = v.interpolate({ inputRange: [0, 0.16, 0.88, 1], outputRange: [-26, -10, 40, 120] });
        const rotacao = v.interpolate({ inputRange: [0, 1], outputRange: ['0deg', '320deg'] });
        const opacidade = v.interpolate({ inputRange: [0, 0.05, 0.16, 0.88, 1], outputRange: [0, 0, 1, 1, 0] });
        const cor = [Brand.verde, Brand.ouro, Brand.roxo][i];
        const deslocamentoX = [-24, -4, 16][i];
        return (
          <Animated.View
            key={i}
            style={[
              styles.confete,
              { backgroundColor: cor, marginLeft: deslocamentoX, opacity: opacidade, transform: [{ translateY }, { rotate: rotacao }] },
            ]}
          />
        );
      })}
      <Animated.View style={[styles.seloCirculo, { transform: [{ scale: pop }] }]}>
        <Animated.View style={{ opacity: tique, transform: [{ scale: tiqueEscala }, { rotate: tiqueRotacao }] }}>
          <Ionicons name="checkmark" size={30} color="#0D2705" />
        </Animated.View>
      </Animated.View>
    </View>
  );
}

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
        <SeloDestravado />
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
            <XpSobe>{`+${xpGanho}`}</XpSobe>
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
            <Text style={styles.textoSuave}>Volte amanhã para manter a sequência. Pipoco fica de olho.</Text>
          </View>
        )}

        {mostrarErros && errosNoNo.length > 0 && (
          <Text style={styles.textoSuave}>Você errou a(s) questão(ões) {errosNoNo.join(', ')} desta rodada.</Text>
        )}
      </View>

      <BotaoPrimario onPress={onVoltar}>CONTINUAR</BotaoPrimario>
      {errosNoNo.length > 0 && (
        <Pressable style={styles.botaoSecundario} onPress={() => setMostrarErros((v) => !v)}>
          <Text style={styles.botaoSecundarioTexto}>{mostrarErros ? 'OCULTAR ERROS' : 'REVER OS ERROS'}</Text>
        </Pressable>
      )}
    </View>
  );
}

/**
 * Botão sólido primário (lima) desta tela -- "Confirmar" é literalmente
 * o exemplo do card "Botão afunda" no projeto de design (Claude
 * Design, App ENEM.dc.html, TURNO 6 "Gramática de animação"), reusado
 * aqui pros outros CTAs de mesma cor/peso ("Entendi, começar o Nó 1",
 * "CONTINUAR", "Continuar ➜"). Botões secundários/links (`Rever
 * depois`, `voltarBtn`, alternativas de questão) ficam de fora de
 * propósito -- no design só o botão SÓLIDO ganha a sombra 3D que
 * afunda, o resto continua flat.
 */
function BotaoPrimario({ children, onPress, disabled }: { children: string; onPress?: () => void; disabled?: boolean }) {
  const { deslocamentoY, handlers } = useInteracaoBotao({ desativado: disabled });
  const sombra = interpolarSombraBotao(deslocamentoY, Brand.verdeEscuro);
  return (
    <Pressable onPress={onPress} disabled={disabled} {...handlers}>
      <Animated.View
        style={[
          styles.botao,
          disabled && styles.botaoDesabilitado,
          { boxShadow: sombra, transform: [{ translateY: deslocamentoY }] },
        ]}>
        <Text style={styles.botaoTexto}>{children}</Text>
      </Animated.View>
    </Pressable>
  );
}

/**
 * "Acerto estufa" / "Erro treme" -- padrões de movimento 6a do
 * projeto de design (Claude Design, App ENEM.dc.html, TURNO 6
 * "Gramática de animação"): o card de feedback da questão já existia
 * (texto + cor por resultado), só ganhou a ENTRADA animada agora.
 *
 * Acerto: aparece com uma pequena "estufada" (escala 0→1.12→1 em
 * ~260ms) mais um anel verde que expande e desbota atrás do card
 * (420ms) -- no design o anel é um círculo em volta de um selo/badge
 * pequeno; aqui o card é um retângulo largo, então o anel virou um
 * contorno arredondado do MESMO formato do card (mesma ideia -- "sai
 * de trás e evapora" -- só adaptada ao card em vez de um badge redondo).
 * Erro: treme só no eixo X, 4 idas com amplitude caindo, ~300ms, e
 * para sozinha -- o card fica parado pro aluno ler, igual o design
 * pede ("nunca em vermelho piscante").
 */
function CardFeedback({ correto, children }: { correto: boolean; children: string }) {
  const entrada = useRef(new Animated.Value(0)).current;
  const anel = useRef(new Animated.Value(0)).current;
  const tremor = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (correto) {
      Animated.sequence([
        Animated.timing(entrada, { toValue: 1.12, duration: 150, easing: Easing.out(Easing.quad), useNativeDriver: false }),
        Animated.timing(entrada, { toValue: 1, duration: 110, easing: Easing.inOut(Easing.quad), useNativeDriver: false }),
      ]).start();
      Animated.timing(anel, { toValue: 1, duration: 420, easing: Easing.out(Easing.quad), useNativeDriver: false }).start();
    } else {
      entrada.setValue(1);
      Animated.sequence(
        [-9, 8, -5, 4, 0].map((v) => Animated.timing(tremor, { toValue: v, duration: 45, easing: Easing.linear, useNativeDriver: false })),
      ).start();
    }
  }, [correto, entrada, anel, tremor]);

  return (
    <View>
      {correto && (
        <Animated.View
          style={[
            styles.anelAcerto,
            { opacity: anel.interpolate({ inputRange: [0, 0.3, 1], outputRange: [0.85, 0.5, 0] }) },
            { transform: [{ scale: anel.interpolate({ inputRange: [0, 1], outputRange: [0.97, 1.06] }) }] },
          ]}
        />
      )}
      <Animated.View
        style={[
          styles.cardFeedback,
          correto ? styles.feedbackCerto : styles.feedbackErrado,
          { transform: [{ scale: entrada }, { translateX: tremor }] },
        ]}>
        <Text style={styles.feedbackTexto}>{children}</Text>
      </Animated.View>
    </View>
  );
}

// Acima disso o cronômetro por questão muda de cor pra avisar que
// passou do razoável -- 10 minutos, número que o próprio usuário deu
// como teto ao pedir essa métrica (não é um limite que bloqueia nada,
// só um alerta visual).
const LIMITE_AVISO_QUESTAO_MS = 10 * 60 * 1000;

/**
 * Som de acerto -- pedido explícito do usuário ("que nem o Duolingo
 * tem"): um "ding" curto de duas notas quando a resposta está certa
 * (assets/sounds/acerto.wav, sintetizado, sem depender de rede).
 *
 * Isolado num componente PRÓPRIO, montado só quando `Platform.OS ===
 * 'web'` (ver uso em QuestaoAtual), de propósito: expo-audio é um
 * módulo nativo, e o Expo Go do celular não tem esse módulo linkado
 * sem reconstruir o app (custom dev client) -- chamar
 * useAudioPlayer() incondicionalmente já quebrava a tela de questão
 * no celular (relatado pelo usuário: "erro ao abrir as questões"),
 * mesmo com o .play() dentro de try/catch, porque o problema é a
 * PRÓPRIA CHAMADA do hook, não só o play(). Como React permite
 * montar/desmontar COMPONENTES condicionalmente (diferente de pular
 * um hook dentro do mesmo componente, que violaria as regras de
 * hooks), colocar o hook aqui dentro e só renderizar
 * <SomAcerto /> na web tira o módulo nativo do caminho inteiro no
 * celular -- ele nunca é sequer importado/chamado lá.
 */
function SomAcerto({ tocar }: { tocar: boolean }) {
  const player = useAudioPlayer(require('@/assets/sounds/acerto.wav'));
  useEffect(() => {
    if (tocar) {
      try {
        player.seekTo(0);
        player.play();
      } catch {
        // silencioso de propósito -- som é extra, nunca pode quebrar
        // o fluxo de responder questão.
      }
    }
  }, [tocar, player]);
  return null;
}

/**
 * Botão "reportar" -- pedido explícito do usuário: enquanto ele
 * valida o banco de questões pergunta por pergunta, precisa de um
 * jeito de sinalizar "acho que isto está errado" (gabarito, figura
 * faltando, alternativa ambígua etc.) sem sair do fluxo de resolver
 * pra ir mexer no banco na hora -- acumula os relatos (POST
 * /relatos -> tabela relatos_questao, ver core/db.py) pra revisar
 * depois em lote. Caixa de texto some ao enviar com sucesso, de
 * propósito -- confirma visualmente que foi, sem deixar aberto
 * pedindo pra reportar de novo.
 */
function BotaoReportar({ idQuestao }: { idQuestao: string }) {
  const [aberto, setAberto] = useState(false);
  const [texto, setTexto] = useState('');
  const [estado, setEstado] = useState<'ocioso' | 'enviando' | 'enviado' | 'erro'>('ocioso');

  useEffect(() => {
    setAberto(false);
    setTexto('');
    setEstado('ocioso');
  }, [idQuestao]);

  async function enviar() {
    if (!texto.trim()) return;
    setEstado('enviando');
    try {
      await reportarQuestao(idQuestao, texto.trim());
      setEstado('enviado');
      setAberto(false);
      setTexto('');
    } catch {
      setEstado('erro');
    }
  }

  if (!aberto) {
    return (
      <Pressable style={styles.acaoQuestaoBtn} onPress={() => setAberto(true)}>
        <Feather name="flag" size={13} color={Brand.laranja} />
        <Text style={[styles.acaoQuestaoTexto, { color: Brand.laranja }]}>
          {estado === 'enviado' ? 'Relato enviado ✓' : 'Reportar'}
        </Text>
      </Pressable>
    );
  }

  return (
    <View style={styles.relatoCaixa}>
      <Text style={styles.relatoLabel}>O que parece errado nesta questão?</Text>
      <TextInput
        style={styles.relatoInput}
        value={texto}
        onChangeText={setTexto}
        placeholder="ex: gabarito parece trocado, falta a figura..."
        placeholderTextColor={Brand.textoApagado}
        multiline
      />
      <View style={styles.relatoBotoesRow}>
        <Pressable style={styles.relatoBotaoCancelar} onPress={() => setAberto(false)}>
          <Text style={styles.acaoQuestaoTexto}>Cancelar</Text>
        </Pressable>
        <Pressable
          style={[styles.relatoBotaoEnviar, (!texto.trim() || estado === 'enviando') && styles.botaoDesabilitado]}
          disabled={!texto.trim() || estado === 'enviando'}
          onPress={enviar}>
          <Text style={styles.relatoBotaoEnviarTexto}>{estado === 'enviando' ? 'Enviando…' : 'Enviar'}</Text>
        </Pressable>
      </View>
      {estado === 'erro' && <Text style={styles.avisoErroTexto}>Não consegui enviar, tenta de novo.</Text>}
    </View>
  );
}

/**
 * "Por que essa resposta" -- pedido explícito do usuário: depois de
 * responder, mostrar SÓ o necessário (a estratégia/pegadinha, não um
 * passo a passo inteiro) e deixar recolhido por padrão pra não virar
 * leitura obrigatória em toda questão. Reaproveita `resolucoes`
 * (tipo='texto'), o mesmo dado que o Cartão-resposta (Streamlit) já
 * usa pra explicação -- sem tabela nova. Só aparece quando existe
 * pelo menos uma resolução de texto pra esta questão; nenhuma questão
 * ainda validada tem isso preenchido, então em silêncio (sem erro
 * visível) é o comportamento certo pra maioria das questões hoje.
 */
function ExplicacaoQuestao({ idQuestao }: { idQuestao: string }) {
  const [resolucoes, setResolucoes] = useState<Resolucao[] | null>(null);
  const [aberto, setAberto] = useState(false);

  useEffect(() => {
    setResolucoes(null);
    setAberto(false);
    getResolucoes(idQuestao)
      .then((r) => setResolucoes(r.filter((res) => res.tipo === 'texto')))
      .catch(() => setResolucoes([]));
  }, [idQuestao]);

  if (!resolucoes || resolucoes.length === 0) return null;

  return (
    <View style={styles.explicacaoBox}>
      <Pressable style={styles.explicacaoToggle} onPress={() => setAberto((v) => !v)}>
        <Feather name={aberto ? 'chevron-up' : 'chevron-down'} size={15} color={Brand.roxoClaro} />
        <Text style={styles.explicacaoToggleTexto}>{aberto ? 'Ocultar explicação' : '💡 Por que essa resposta'}</Text>
      </Pressable>
      {aberto &&
        resolucoes.map((r) => (
          <Text key={r.id_resolucao} style={styles.explicacaoTexto}>
            {r.conteudo}
          </Text>
        ))}
    </View>
  );
}

function QuestaoAtual({
  questao,
  posicao,
  total,
  materia,
  chave,
  escolha,
  resultado,
  enviando,
  temposAnteriores,
  modoAdmin,
  onEscolher,
  onConfirmar,
  onContinuar,
  onPular,
  onVerConteudo,
}: {
  questao: NoTrilha['questoes'][number];
  posicao: number;
  total: number;
  materia: string;
  chave: string | undefined;
  escolha: string | null;
  resultado: ResultadoTentativa | null;
  enviando: boolean;
  temposAnteriores: number[];
  modoAdmin: boolean;
  onEscolher: (letra: string) => void;
  onConfirmar: (idQuestao: string, duracaoMs: number) => void;
  onContinuar: () => void;
  onPular: () => void;
  onVerConteudo: () => void;
}) {
  const { corpo, alternativas } = separarAlternativas(questao.enunciado_texto ?? '');
  const temAlternativas = Object.keys(alternativas).length === 5;

  // Cronômetro por questão -- pedido explícito do usuário: saber
  // quanto tempo está gastando em CADA questão (não só no nó inteiro,
  // que já existia via `inicioNo`/TelaResultado), com aviso visual
  // passando de 10min e uma estimativa de quanto falta pro fim do
  // bloco baseada na média das já respondidas. Só em memória, de
  // propósito (ver decisão do usuário: não precisa persistir).
  const inicioQuestaoRef = useRef(Date.now());
  const [agora, setAgora] = useState(Date.now());
  useEffect(() => {
    inicioQuestaoRef.current = Date.now();
    setAgora(Date.now());
    const id = setInterval(() => setAgora(Date.now()), 1000);
    return () => clearInterval(id);
  }, [questao.id_questao]);

  const decorridoMs = agora - inicioQuestaoRef.current;
  const passouDoLimite = !resultado && decorridoMs > LIMITE_AVISO_QUESTAO_MS;
  const mediaMs =
    temposAnteriores.length > 0 ? temposAnteriores.reduce((soma, t) => soma + t, 0) / temposAnteriores.length : null;
  // Estimativa cobre a questão atual + as que ainda faltam depois
  // dela -- por isso `total - posicao`, não `total - posicao - 1`.
  const restantesMs = mediaMs !== null ? mediaMs * (total - posicao) : null;

  // "Questão entra" -- padrão de movimento 6a do projeto de design
  // (Claude Design, App ENEM.dc.html, TURNO 6 "Gramática de
  // animação"): 240ms, entra pela direita. O design também prevê
  // "voltar inverte o sentido" (sai pela esquerda), mas esta trilha
  // ainda não tem como voltar pra uma questão anterior (`posicao` só
  // anda pra frente, ver TelaExercicio) -- só a metade "entra pela
  // direita" se aplica de verdade hoje, o resto fica pronto pra
  // quando existir um "voltar" de verdade entre questões.
  const entrada = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    entrada.setValue(0);
    Animated.timing(entrada, { toValue: 1, duration: 240, easing: Easing.out(Easing.cubic), useNativeDriver: false }).start();
  }, [questao.id_questao, entrada]);
  const translateX = entrada.interpolate({ inputRange: [0, 1], outputRange: [46, 0] });

  return (
    <Animated.View style={{ opacity: entrada, transform: [{ translateX }] }}>
      {Platform.OS === 'web' && <SomAcerto tocar={resultado?.resultado === 'acertou'} />}
      <View style={styles.progressoLinha}>
        <Text style={styles.progressoTexto}>
          Questão {posicao + 1} de {total}
        </Text>
        {!resultado && (
          <Text style={[styles.cronometroTexto, passouDoLimite && styles.cronometroTextoAviso]}>
            ⏱ {formatarTempo(decorridoMs)}
          </Text>
        )}
      </View>
      {mediaMs !== null && restantesMs !== null && !resultado && (
        <Text style={styles.estimativaTexto}>
          média {formatarTempo(mediaMs)}/questão · faltam ~{formatarTempo(restantesMs)} pro fim do bloco
        </Text>
      )}

      <View style={styles.acoesQuestaoRow}>
        {resumoDoNo(materia, chave) && (
          <Pressable style={styles.acaoQuestaoBtn} onPress={onVerConteudo}>
            <Feather name="book-open" size={13} color={Brand.roxoClaro} />
            <Text style={styles.acaoQuestaoTexto}>Rever conteúdo base</Text>
          </Pressable>
        )}
        <BotaoReportar idQuestao={questao.id_questao} />
      </View>

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
          <BotaoPrimario
            disabled={!escolha || enviando}
            onPress={() => onConfirmar(questao.id_questao, Date.now() - inicioQuestaoRef.current)}>
            {enviando ? 'Enviando…' : 'Confirmar'}
          </BotaoPrimario>
          {modoAdmin && (
            <Pressable style={styles.botaoPular} onPress={onPular}>
              <Feather name="fast-forward" size={14} color={Brand.textoApagado} />
              <Text style={styles.botaoPularTexto}>Pular (não conta tentativa)</Text>
            </Pressable>
          )}
        </>
      ) : (
        <>
          <CardFeedback correto={resultado.resultado === 'acertou'}>
            {resultado.resultado === 'acertou'
              ? `✅ Certo! A resposta era ${resultado.alternativa_correta}.`
              : `❌ Você marcou ${resultado.resposta_escolhida ?? '— (em branco)'}. A resposta certa era ${resultado.alternativa_correta}.`}
          </CardFeedback>
          <ExplicacaoQuestao idQuestao={questao.id_questao} />
          <BotaoPrimario onPress={onContinuar}>Continuar ➜</BotaoPrimario>
        </>
      )}
    </Animated.View>
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
  progressoLinha: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cronometroTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 13,
    color: Brand.textoSuave,
  },
  cronometroTextoAviso: {
    color: Brand.laranja,
  },
  estimativaTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 12,
    color: Brand.textoApagado,
    marginTop: -4,
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
  seloWrap: {
    width: 90,
    height: 90,
    alignItems: 'center',
    justifyContent: 'center',
  },
  seloCirculo: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: Brand.verde,
    boxShadow: `0 6px 0 ${Brand.verdeEscuro}`,
    alignItems: 'center',
    justifyContent: 'center',
  },
  confete: {
    position: 'absolute',
    top: 24,
    left: '50%',
    width: 8,
    height: 12,
    borderRadius: 2,
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
  modoAdminToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
  },
  modoAdminTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11.5,
    color: Brand.textoApagado,
  },
  modoAdminTextoAtivo: {
    color: Brand.verde,
  },
  botaoPular: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 10,
    marginTop: 4,
  },
  botaoPularTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12.5,
    color: Brand.textoApagado,
  },
  acoesQuestaoRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 2,
  },
  acaoQuestaoBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: Brand.borda,
    backgroundColor: Brand.bgCard,
  },
  acaoQuestaoTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11.5,
    color: Brand.roxoClaro,
  },
  relatoCaixa: {
    flex: 1,
    minWidth: '100%',
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 14,
    padding: 12,
    gap: 8,
  },
  relatoLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12,
    color: Brand.textoSuave,
  },
  relatoInput: {
    fontFamily: Fontes.corpo,
    fontSize: 13,
    color: Brand.texto,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 10,
    padding: 10,
    minHeight: 60,
    textAlignVertical: 'top',
  },
  relatoBotoesRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
  },
  relatoBotaoCancelar: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  relatoBotaoEnviar: {
    backgroundColor: Brand.laranja,
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  relatoBotaoEnviarTexto: {
    fontFamily: Fontes.titulo,
    fontSize: 13,
    color: '#2A1400',
  },
  explicacaoBox: {
    backgroundColor: Brand.roxoBgEscuro,
    borderWidth: 1,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: 14,
    padding: 12,
    gap: 8,
    marginVertical: 4,
  },
  explicacaoToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  explicacaoToggleTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12.5,
    color: Brand.roxoTextoEscuro,
  },
  explicacaoTexto: {
    fontFamily: Fontes.corpo,
    fontSize: 13.5,
    lineHeight: 19,
    color: Brand.roxoTextoSuave,
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
  anelAcerto: {
    position: 'absolute',
    top: 8,
    left: 0,
    right: 0,
    bottom: 8,
    borderRadius: RaioCard,
    borderWidth: 3,
    borderColor: Brand.verde,
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
  apresentacaoPainel: {
    backgroundColor: Brand.roxoBgEscuro,
    borderWidth: 1.5,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: RaioCard,
    padding: 16,
    gap: 14,
  },
  apresentacaoHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  apresentacaoVoltarBtn: {
    width: 34,
    height: 34,
    borderRadius: 11,
    backgroundColor: Brand.roxoBg,
    borderWidth: 1,
    borderColor: Brand.roxoBordaEscura,
    justifyContent: 'center',
    alignItems: 'center',
  },
  apresentacaoRotulo: {
    flex: 1,
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    letterSpacing: 1.4,
    color: Brand.roxoTextoEscuro,
  },
  apresentacaoMinutosPill: {
    backgroundColor: Brand.roxoBg,
    borderWidth: 1,
    borderColor: Brand.roxoBordaEscura,
    borderRadius: 999,
    paddingVertical: 5,
    paddingHorizontal: 11,
  },
  apresentacaoMinutosTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12,
    color: Brand.roxoTextoEscuro,
  },
  apresentacaoTituloRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
  },
  apresentacaoTituloTextos: {
    flex: 1,
    gap: 5,
  },
  apresentacaoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 24,
    color: Brand.texto,
    lineHeight: 28,
  },
  apresentacaoSubtitulo: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 13,
    color: Brand.roxoTextoSuave,
    lineHeight: 18,
  },
  apresentacaoSecaoTitulo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  apresentacaoSecaoTexto: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    letterSpacing: 1.4,
    color: Brand.textoApagado,
  },
  apresentacaoSecaoLinha: {
    flex: 1,
    height: 1,
    backgroundColor: Brand.borda,
  },
  apresentacaoTopicoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 18,
    padding: 13,
  },
  apresentacaoTopicoIcone: {
    width: 42,
    height: 42,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  apresentacaoTopicoTextos: {
    flex: 1,
    gap: 2,
  },
  apresentacaoTopicoTitulo: {
    fontFamily: Fontes.titulo,
    fontSize: 15,
    color: Brand.texto,
  },
  apresentacaoTopicoFrequencia: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 12.5,
  },
  apresentacaoEstatistica: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: Brand.bgCardEscuro,
    borderWidth: 1,
    borderColor: Brand.bordaForte,
    borderStyle: 'dashed',
    borderRadius: 18,
    padding: 14,
  },
  apresentacaoEstatisticaNumero: {
    fontFamily: Fontes.titulo,
    fontSize: 30,
    color: Brand.roxo,
  },
  apresentacaoEstatisticaTexto: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 12.5,
    color: Brand.textoSuave,
    lineHeight: 18,
  },
  apresentacaoReverLink: {
    alignItems: 'center',
    paddingVertical: 6,
  },
  apresentacaoReverTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 13,
    color: Brand.textoApagado,
  },
});
