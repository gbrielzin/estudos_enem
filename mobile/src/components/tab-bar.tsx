import { TabListProps, TabTriggerSlotProps } from 'expo-router/ui';
import { Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Svg, { Circle, Ellipse, Path, Rect } from 'react-native-svg';

/**
 * Barra de baixo do app -- 6 ícones sem rótulo, visual importado do
 * projeto de design do usuário no Claude Design (App ENEM.dc.html,
 * rodapé das telas do celular, atualizado depois da 1a versão desta
 * barra: aquela era uma pill flutuante de 3 abas com rótulo em texto
 * -- Home/Explore/Perfil, ver git blame -- o usuário trocou o design
 * pra uma barra fixa (encostada no fundo, sem flutuar) de 6 ícones
 * coloridos sem texto: Trilha/Explorar/Simulado/Missões/Liga/Pipoco).
 * Substituiu tanto a pill antiga (app-tabs.web.tsx) quanto a barra
 * nativa do sistema operacional que o app usava antes disso
 * (`NativeTabs`, ver app-tabs.tsx) -- fonte única pros dois lugares
 * que renderizam a barra (app-tabs.tsx sempre, app-tabs.web.tsx só
 * abaixo de 1100px).
 *
 * Cada ícone é um <svg> multi-cor próprio (não um ícone de biblioteca
 * de traço único como Feather) -- os paths/formas abaixo são cópia
 * direta dos <svg> do arquivo de design, não uma aproximação.
 */
export const ITENS_NAV: { nome: string; rotulo: string; href: '/' | '/explore' | '/simulado' | '/missoes' | '/liga' | '/perfil' }[] = [
  { nome: 'trilha', rotulo: 'Trilha', href: '/' },
  { nome: 'explorar', rotulo: 'Explorar', href: '/explore' },
  { nome: 'simulado', rotulo: 'Simulado', href: '/simulado' },
  { nome: 'missoes', rotulo: 'Missões', href: '/missoes' },
  { nome: 'liga', rotulo: 'Liga', href: '/liga' },
  { nome: 'pipoco', rotulo: 'Pipoco', href: '/perfil' },
];

/**
 * Cor da borda/fundo quando a aba está ativa -- mesma cor do fill
 * principal do próprio ícone (confirmado nos 4 estados ativos que o
 * arquivo de design mostra: Trilha, Explorar, Missões e Liga cada um
 * ativo numa tela diferente). Simulado e Pipoco nunca aparecem ativos
 * em nenhuma das telas do design -- a cor deles aqui é inferida pelo
 * MESMO padrão (cor dominante do próprio ícone), não copiada de um
 * exemplo ativo real.
 */
export const COR_ATIVA: Record<string, string> = {
  trilha: '#6EE12B',
  explorar: '#7C5CFF',
  simulado: '#FFC42E',
  missoes: '#FF5A45',
  liga: '#FFC42E',
  pipoco: '#FDFEFF',
};

function IconeTrilha() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Rect x={5.4} y={3} width={2.6} height={18.4} rx={1.2} fill="#8B93A7" />
      <Path d="M8.6 4h10.6l-2.7 3.7 2.7 3.7H8.6z" fill="#6EE12B" />
    </Svg>
  );
}

function IconeExplorar() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Circle cx={12} cy={12} r={9.6} fill="#7C5CFF" />
      <Path d="M16.4 7.6l-2.3 6.5-6.5 2.3 2.3-6.5z" fill="#FFFFFF" />
    </Svg>
  );
}

function IconeSimulado() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Rect x={3.6} y={3.4} width={16.8} height={18} rx={2.4} fill="#FFC42E" />
      <Rect x={8.4} y={1.5} width={7.2} height={3.6} rx={1.4} fill="#D99A16" />
      <Rect x={6.6} y={8.6} width={10.8} height={2.2} rx={1.1} fill="#FFFFFF" />
      <Rect x={6.6} y={13} width={7} height={2.2} rx={1.1} fill="#FFFFFF" />
    </Svg>
  );
}

function IconeMissoes() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Circle cx={12} cy={12} r={9.6} fill="#FF5A45" />
      <Circle cx={12} cy={12} r={6} fill="#FFF1EE" />
      <Circle cx={12} cy={12} r={2.7} fill="#FF5A45" />
    </Svg>
  );
}

function IconeLiga() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Path d="M6.4 3.6h11.2v4.2a5.6 5.6 0 0 1-11.2 0z" fill="#FFC42E" />
      <Path d="M6.4 5.2H4v1.9a3.4 3.4 0 0 0 2.4 3.2zM17.6 5.2H20v1.9a3.4 3.4 0 0 1-2.4 3.2z" fill="#D99A16" />
      <Rect x={10.8} y={12.6} width={2.4} height={3.9} fill="#D99A16" />
      <Rect x={7.4} y={16.4} width={9.2} height={2.8} rx={1} fill="#FFC42E" />
    </Svg>
  );
}

function IconePipoco() {
  return (
    <Svg width={29} height={29} viewBox="0 0 24 24">
      <Path d="M5.6 8.4L4.4 3.2l4.8 2.6zM18.4 8.4l1.2-5.2-4.8 2.6z" fill="#FDFEFF" />
      <Ellipse cx={12} cy={13.4} rx={8} ry={7.2} fill="#FDFEFF" />
      <Ellipse cx={9.2} cy={12.4} rx={1.25} ry={1.6} fill="#2A3140" />
      <Ellipse cx={14.8} cy={12.4} rx={1.25} ry={1.6} fill="#2A3140" />
      <Path d="M12 15.4l-1.5-1.3h3z" fill="#FF8FA3" />
    </Svg>
  );
}

const ICONES: Record<string, () => React.JSX.Element> = {
  trilha: IconeTrilha,
  explorar: IconeExplorar,
  simulado: IconeSimulado,
  missoes: IconeMissoes,
  liga: IconeLiga,
  pipoco: IconePipoco,
};

export function TabButton({ nome, rotulo, isFocused, ...props }: TabTriggerSlotProps & { nome: string; rotulo: string }) {
  const Icone = ICONES[nome];
  return (
    <Pressable
      {...props}
      accessibilityLabel={rotulo}
      style={[styles.slot, isFocused && { borderColor: COR_ATIVA[nome] ?? '#FFFFFF', backgroundColor: '#141821' }]}>
      <Icone />
    </Pressable>
  );
}

export function CustomTabList(props: TabListProps) {
  return (
    <SafeAreaView edges={['bottom']} style={styles.fundo}>
      <View {...props} style={styles.barra}>
        {props.children}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  fundo: {
    backgroundColor: '#0A0C10',
  },
  barra: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
    borderTopWidth: 1.5,
    borderTopColor: '#1D222B',
    paddingHorizontal: 8,
    paddingTop: 6,
    paddingBottom: 4,
  },
  slot: {
    flex: 1,
    height: 52,
    borderWidth: 2,
    borderColor: 'transparent',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
