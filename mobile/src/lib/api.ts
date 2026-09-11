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

class ErroApi extends Error {}

async function buscarJson<T>(caminho: string): Promise<T> {
  const url = `${getApiBaseUrl()}${caminho}`;
  let resposta: Response;
  try {
    resposta = await fetch(url);
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

export function getTrilha(grandeArea: GrandeArea, materia: string, fonte: string | null): Promise<NoTrilha[]> {
  const query = new URLSearchParams({ grande_area: grandeArea, materia });
  if (fonte) query.set('fonte', fonte);
  return buscarJson(`/trilha?${query.toString()}`);
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

export async function registrarTentativa(idQuestao: string, respostaEscolhida: string | null): Promise<ResultadoTentativa> {
  const url = `${getApiBaseUrl()}/tentativas`;
  const resposta = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_questao: idQuestao, resposta_escolhida: respostaEscolhida }),
  });
  if (!resposta.ok) {
    throw new ErroApi(`Backend respondeu ${resposta.status} ao registrar a tentativa.`);
  }
  return resposta.json();
}
