import { Feather, Ionicons } from '@expo/vector-icons';
import { StyleSheet, Text, View } from 'react-native';

import { BarraProgresso } from '@/components/barra-progresso';
import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { MissaoDoDia } from '@/lib/api';

/**
 * Visual de cada tipo de missão (design_handoff_enem_gamificado/
 * screens/03-missoes.png) -- ícone/cor/XP por `id`, pedido explícito
 * do usuário 2026-09-11: "a gente vai fazendo visualmente, depois a
 * gente faz a lógica por trás". O XP aqui é só o NÚMERO que o mockup
 * mostra (30/40/15/20) -- db.missoes_do_dia() ainda não calcula XP de
 * verdade pra nenhuma missão (conferido: o dict que ele devolve não
 * tem esse campo), então isto é decoração por enquanto, não uma
 * recompensa que realmente é creditada em calcular_nivel_jogador() --
 * ligar isso de verdade é o próximo passo, não algo pra inventar já.
 */
const VISUAL_POR_ID: Record<string, { bg: string; barra: string; xp: number; Icone: (cor: string) => React.ReactNode }> = {
  meta_diaria: {
    bg: Brand.verde,
    barra: Brand.verde,
    xp: 30,
    Icone: (cor) => <Feather name="zap" size={20} color={cor} />,
  },
  foco_prioridade: {
    bg: Brand.roxo,
    barra: Brand.roxoClaro,
    xp: 40,
    Icone: (cor) => <Feather name="target" size={19} color={cor} />,
  },
  // Duas missões "só visuais" abaixo (pedido do usuário, 2026-09-11):
  // não vêm de GET /missoes-do-dia (db.py só calcula meta_diaria/
  // foco_prioridade de verdade hoje) -- objetos estáticos montados em
  // missoes.tsx, mesmo shape de MissaoDoDia, só pra completar a tela
  // igual ao mockup enquanto a lógica de verdade não existe.
  manter_ofensivo: {
    bg: Brand.laranja,
    barra: Brand.laranja,
    xp: 15,
    Icone: (cor) => <Ionicons name="flame" size={20} color={cor} />,
  },
  revisao_espacada: {
    bg: Brand.bgCardEscuro,
    barra: Brand.textoSuave,
    xp: 20,
    Icone: (cor) => <Feather name="clock" size={18} color={cor} />,
  },
};
const VISUAL_PADRAO = VISUAL_POR_ID.meta_diaria;

/**
 * Expõe db.missoes_do_dia() (+ as 2 missões só-visuais que missoes.tsx
 * acrescenta na mesma lista, ver VISUAL_POR_ID acima) -- decisão
 * deliberada de NÃO ter nenhum mecanismo que bloqueia progresso (sem
 * "vidas" que zeram e travam o app). Cada missão só mostra progresso;
 * completar ou não completar não impede nada no resto do app. Visual
 * do card + ícone colorido + "+XP" + barra de progresso vem do mockup
 * de referência -- trocou o checkbox genérico da 1a versão pelo badge
 * de ícone colorido por missão, que é o que o design de verdade mostra
 * (nenhuma versão anterior tinha "+XP" nem ícone por item, só um
 * checkbox cinza -- pedido explícito do usuário pra copiar o mockup
 * fielmente aqui). Sem cabeçalho "Missões de hoje" próprio (removido
 * a pedido do usuário, 2026-09-11) -- a tela que usa este componente
 * (app/missoes.tsx) já tem "Missões do dia" no topo da página; repetir
 * aqui embaixo era redundante. */
export function MissoesCard({ missoes }: { missoes: MissaoDoDia[] }) {
  if (missoes.length === 0) return null;
  return (
    <View style={styles.container}>
      {missoes.map((m) => {
        const pct = m.progresso_meta > 0 ? Math.min(1, m.progresso_atual / m.progresso_meta) : 0;
        const visual = VISUAL_POR_ID[m.id] ?? VISUAL_PADRAO;
        const corIcone = m.id === 'foco_prioridade' ? '#FFFFFF' : m.id === 'revisao_espacada' ? Brand.texto : Brand.bg;
        return (
          <View key={m.id} style={styles.missao}>
            <View style={[styles.iconeBadge, { backgroundColor: visual.bg }]}>{visual.Icone(corIcone)}</View>
            <View style={styles.missaoCorpo}>
              <View style={styles.missaoTituloRow}>
                <Text style={styles.missaoTitulo}>{m.titulo}</Text>
                <Text style={styles.missaoXp}>+{visual.xp} XP</Text>
              </View>
              <Text style={styles.missaoSub}>{m.descricao}</Text>
              <BarraProgresso pct={pct * 100} cor={visual.barra} altura={11} />
            </View>
          </View>
        );
      })}
    </View>
  );
}

// Tamanhos engordados (pedido do usuário, 2026-09-11: sem o cabeçalho
// "Missões de hoje" redundante, sobrava espaço vazio embaixo na tela --
// em vez de inserir espaço morto entre os blocos, cada elemento cresce
// um pouco pra ocupar a tela de um jeito que pareça intencional, não
// esticado à força).
const styles = StyleSheet.create({
  container: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 22,
  },
  missao: {
    flexDirection: 'row',
    gap: 14,
    marginBottom: 26,
  },
  missaoCorpo: {
    flex: 1,
    gap: 6,
    justifyContent: 'center',
  },
  iconeBadge: {
    width: 52,
    height: 52,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  missaoTituloRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 8,
  },
  missaoTitulo: {
    flex: 1,
    fontFamily: Fontes.corpoNegrito,
    fontSize: 16,
    color: Brand.texto,
  },
  missaoXp: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 14,
    color: Brand.ouro,
  },
  missaoSub: {
    fontFamily: Fontes.corpo,
    fontSize: 13.5,
    color: Brand.textoSuave,
    lineHeight: 18,
    marginBottom: 4,
  },
});
