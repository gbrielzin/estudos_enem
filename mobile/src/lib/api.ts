import Constants from 'expo-constants';

/**
 * Porta onde `uvicorn api:app --host 0.0.0.0 --port 8000` roda no
 * computador (ver core/api.py). Fixa por enquanto -- não muda entre
 * telas/fases, só a lista de endpoints cresce.
 */
const API_PORT = 8000;

/**
 * Descobre o IP do computador que está rodando o Metro bundler (o
 * mesmo que serve o app pro Expo Go) e monta a URL da API nesse
 * mesmo IP -- funciona porque, na Fase 0, o celular só alcança o
 * backend estando na MESMA wifi do computador (ver DEPLOY.md e o
 * plano em .claude/plans), então o IP do Metro e o IP da API são o
 * mesmo. Evita o usuário ter que digitar o IP na mão toda vez que a
 * rede wifi muda.
 *
 * `hostUri` só existe rodando via Expo Go/dev client (ex:
 * "192.168.1.23:8081"); no preview web cai no fallback localhost.
 */
export function getApiBaseUrl(): string {
  const hostUri = Constants.expoConfig?.hostUri;
  if (hostUri) {
    const host = hostUri.split(':')[0];
    return `http://${host}:${API_PORT}`;
  }
  return `http://localhost:${API_PORT}`;
}

/**
 * Header de autenticação da trava simples do backend (ver
 * core/api.py `_verificar_autenticacao` e
 * adr/0009-trava-simples-antes-de-autenticacao-real.md). Lê
 * `EXPO_PUBLIC_API_AUTH_TOKEN` -- prefixo `EXPO_PUBLIC_` é a convenção
 * do próprio Expo pra variável inlined no bundle do cliente (SDK 57,
 * ver docs de Environment Variables); ATENÇÃO: isso significa que o
 * valor fica visível em texto puro no app compilado -- não é segredo
 * de verdade, é só a mesma trava contra acesso não convidado que o
 * backend já documenta como limitação conhecida, não uma credencial
 * de usuário. Sem a variável configurada, não manda header nenhum --
 * mesmo comportamento de hoje (backend aberto).
 */
export function cabecalhosAutenticacao(): HeadersInit {
  const token = process.env.EXPO_PUBLIC_API_AUTH_TOKEN;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ============================================================
// Tipos -- espelham os dicts que core/db.py já devolve (ver
// _linha_para_questao_grade e trilha_banco_pratica em db.py). Nenhuma
// forma nova, só a tipagem do que a API já repassa direto.
// ============================================================

export type GrandeArea = 'matematica' | 'ciencias_natureza';

export interface Questao {
  id_questao: string;
  numero_questao: number;
  materia: string;
  status_classificacao: 'classificado' | 'nao_classificado';
  ano: number;
  caderno: string;
  grande_area: GrandeArea;
  enunciado_texto: string | null;
  enunciado_imagem_path: string | null;
  origem: 'enem_oficial' | 'banco_pratica';
  fonte: string | null;
  ja_respondida: boolean;
}

export interface NoTrilha {
  indice: number;
  questoes: Questao[];
  concluido: boolean;
  desbloqueado: boolean;
}

/**
 * Um nó da trilha fixa entrelaçada entre matérias (ver db.trilha_fixa()
 * / db.TRILHA_FIXA_NOS em core/db.py) -- diferente de NoTrilha, que é
 * um mini-bloco de 5 questões DENTRO de uma matéria só. Aqui 'chave'
 * identifica o nó (ex: 'ecologia_poluicao_atmosferica') e 'blocos' é a
 * lista de NoTrilha daquela matéria/fase.
 */
export interface NoTrilhaFixa {
  chave: string;
  nome: string;
  concluido: boolean;
  desbloqueado: boolean;
  blocos: NoTrilha[];
}

export interface FaseInfo {
  fase: number;
  nome: string;
  total: number;
  respondidas: number;
  concluida: boolean;
}

export interface ResultadoTentativa {
  id_tentativa: number;
  id_questao: string;
  resultado: 'acertou' | 'errou';
  resposta_escolhida: string | null;
  alternativa_correta: string;
  intervalo_dias: number;
  streak_acertos: number;
  proxima_revisao: string;
}

export interface Streak {
  atual: number;
  melhor: number;
  calendario_30_dias: { data: string; ativo: boolean }[];
}

export interface Nivel {
  xp: number;
  rank: string;
  proximo_rank: string | null;
  xp_para_proximo: number | null;
  total_tentativas: number;
  acertos: number;
}

export interface MissaoDoDia {
  id: string;
  titulo: string;
  descricao: string;
  progresso_atual: number;
  progresso_meta: number;
  concluida: boolean;
}

export interface DiasAteProva {
  data_prova: string;
  dias_restantes: number;
  ja_passou: boolean;
}

export interface ResumoGeral {
  total_tentativas: number;
  acertos: number;
  taxa_acerto: number | null;
}

export interface MateriaExplorada {
  materia: string;
  total_questoes: number;
  total_tentativas: number;
  taxa_acerto: number | null;
}

export interface Resolucao {
  id_resolucao: number;
  tipo: 'video' | 'texto';
  conteudo: string;
  canal: string | null;
}

class ErroApi extends Error {}

async function buscarJson<T>(caminho: string): Promise<T> {
  const url = `${getApiBaseUrl()}${caminho}`;
  let resposta: Response;
  try {
    // cache: 'no-store' -- sem isso, o navegador pode servir uma
    // resposta antiga do cache HTTP em vez de bater na API de novo
    // (mais visível na versão web, que roda dentro do próprio Chrome;
    // o app nativo no celular não usa esse cache do jeito que o
    // fetch() do navegador usa). Como toda tela desta trilha depende
    // de progresso ATUAL (nó desbloqueado, questão já respondida),
    // uma resposta em cache é literalmente a causa de "a web ficou
    // atrasada em relação ao celular" -- os dois batem no mesmo
    // backend/enem.db, só um dos dois estava lendo cache velho.
    resposta = await fetch(url, { headers: cabecalhosAutenticacao(), cache: 'no-store' });
  } catch (erro) {
    const mensagem = erro instanceof Error ? erro.message : String(erro);
    throw new ErroApi(`Não consegui alcançar o backend em ${url} (${mensagem}). Confere se está na mesma wifi do computador e se o servidor está rodando.`);
  }
  if (!resposta.ok) {
    throw new ErroApi(`Backend respondeu ${resposta.status} em ${caminho}.`);
  }
  return resposta.json() as Promise<T>;
}

export function getMaterias(grandeArea: GrandeArea): Promise<string[]> {
  return buscarJson(`/materias?grande_area=${grandeArea}`);
}

export function getFontesBancoPratica(): Promise<string[]> {
  return buscarJson(`/fontes-banco-pratica`);
}

export function getMateriasComBancoPratica(grandeArea: GrandeArea): Promise<string[]> {
  return buscarJson(`/materias-com-banco-pratica?grande_area=${grandeArea}`);
}

export function getTrilha(
  grandeArea: GrandeArea,
  materia: string,
  fonte: string | null,
  fase?: number | null,
): Promise<NoTrilha[]> {
  const query = new URLSearchParams({ grande_area: grandeArea, materia });
  if (fonte) query.set('fonte', fonte);
  if (fase != null) query.set('fase', String(fase));
  return buscarJson(`/trilha?${query.toString()}`);
}

/**
 * Trilha fixa entrelaçada entre matérias de Ciências da Natureza, na
 * ordem de ROI definida em
 * docs/arquitetura_questoes/arquitetura-trilha.docx -- sem parâmetro
 * de matéria (ao contrário de getTrilha), porque a ordem/composição
 * dos nós é fixa no backend (db.TRILHA_FIXA_NOS).
 */
export function getTrilhaFixa(): Promise<NoTrilhaFixa[]> {
  return buscarJson(`/trilha-fixa`);
}

/**
 * Fases de uma matéria (hoje só ecologia tem -- ver
 * core/db.py FASES_ECOLOGIA). Devolve lista vazia pra matéria sem
 * fase mapeada (ex: 'optica') -- UI só deve oferecer o seletor de
 * fase quando esta lista não vier vazia.
 */
export function getFases(grandeArea: GrandeArea, materia: string, fonte?: string | null): Promise<FaseInfo[]> {
  const query = new URLSearchParams({ grande_area: grandeArea, materia });
  if (fonte) query.set('fonte', fonte);
  return buscarJson(`/fases?${query.toString()}`);
}

export function getStreak(): Promise<Streak> {
  return buscarJson(`/streak`);
}

export function getNivel(): Promise<Nivel> {
  return buscarJson(`/nivel`);
}

export function getMissoesDoDia(): Promise<MissaoDoDia[]> {
  return buscarJson(`/missoes-do-dia`);
}

export function getDiasAteProva(): Promise<DiasAteProva> {
  return buscarJson(`/dias-ate-prova`);
}

export function getResumoGeral(): Promise<ResumoGeral> {
  return buscarJson(`/resumo-geral`);
}

export function getExplorarMaterias(grandeArea: GrandeArea): Promise<MateriaExplorada[]> {
  return buscarJson(`/explorar?grande_area=${grandeArea}`);
}

/**
 * duracaoSegundos é OPCIONAL, de propósito -- pedido explícito do
 * usuário: "quanto tempo eu gasto numa questão" precisa ficar
 * registrado no banco pra virar métrica depois, não só mostrado ao
 * vivo na tela (ver o cronômetro em app/index.tsx, QuestaoAtual).
 * Quem chama sem medir tempo (nenhum caller hoje, mas a assinatura
 * fica pronta pra isso) simplesmente não manda o campo.
 */
export async function registrarTentativa(
  idQuestao: string,
  respostaEscolhida: string | null,
  duracaoSegundos?: number,
): Promise<ResultadoTentativa> {
  const url = `${getApiBaseUrl()}/tentativas`;
  const resposta = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...cabecalhosAutenticacao() },
    body: JSON.stringify({
      id_questao: idQuestao,
      resposta_escolhida: respostaEscolhida,
      ...(duracaoSegundos != null ? { duracao_segundos: Math.round(duracaoSegundos) } : {}),
    }),
  });
  if (!resposta.ok) {
    throw new ErroApi(`Backend respondeu ${resposta.status} ao registrar a tentativa.`);
  }
  return resposta.json();
}

/**
 * Resoluções (texto/vídeo) já cadastradas pra uma questão -- mesma
 * db.resolucoes_da_questao() que o Cartão-resposta (Streamlit) já
 * usa. Lista vazia é o caso comum (nem toda questão tem uma
 * resolução escrita ainda); a tela de exercício só mostra a seção
 * "por que essa resposta" quando isto vier não-vazio.
 */
export function getResolucoes(idQuestao: string): Promise<Resolucao[]> {
  return buscarJson(`/resolucoes?id_questao=${encodeURIComponent(idQuestao)}`);
}

/**
 * Botão "reportar" da tela de exercício -- pedido explícito do
 * usuário pra acumular sinal ("acho que o gabarito está errado",
 * "falta uma figura" etc.) enquanto ele valida o banco de questões
 * pergunta por pergunta, sem sair do fluxo de resolver pra corrigir
 * na hora.
 */
export async function reportarQuestao(idQuestao: string, comentario: string): Promise<void> {
  const url = `${getApiBaseUrl()}/relatos`;
  const resposta = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...cabecalhosAutenticacao() },
    body: JSON.stringify({ id_questao: idQuestao, comentario }),
  });
  if (!resposta.ok) {
    throw new ErroApi(`Backend respondeu ${resposta.status} ao enviar o relato.`);
  }
}
