import { Feather } from '@expo/vector-icons';
import {
  Tabs,
  TabList,
  TabTrigger,
  TabSlot,
  TabTriggerSlotProps,
  TabListProps,
} from 'expo-router/ui';
import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, useWindowDimensions, View } from 'react-native';

import { Brand, Fontes, RaioCard } from '@/constants/brand';
import { getDiasAteProva } from '@/lib/api';

/** Barra de abas do site (react-native-web). Dois modos, ambos usando os
 * mesmos <Tabs>/<TabList>/<TabTrigger> (só troca o que fica dentro de
 * TabList e o layout ao redor de TabSlot -- README seção "Interactions &
 * Behavior": "a partir de ~1100px entra o layout de três colunas do
 * desktop"):
 *  - Largura < 1100px: pill flutuante embaixo (README seção 1, "Tab bar"),
 *    3 abas ícone+rótulo em coluna, ativa vira pill violeta.
 *  - Largura >= 1100px: sidebar esquerda fixa 268px (README seção 8,
 *    "Desktop") -- marca, pills de navegação (ativa = pill lima), card
 *    "N dias até o ENEM" no rodapé. Sem rail direito por enquanto (o
 *    conteúdo de cada tela, ex. Perfil, já tem os próprios cards). */
const LARGURA_DESKTOP = 1100;

const ITENS_NAV: { nome: string; rotulo: string; href: '/' | '/explore' | '/perfil'; icone: keyof typeof Feather.glyphMap }[] = [
  { nome: 'home', rotulo: 'Home', href: '/', icone: 'home' },
  { nome: 'explore', rotulo: 'Explore', href: '/explore', icone: 'compass' },
  { nome: 'perfil', rotulo: 'Perfil', href: '/perfil', icone: 'user' },
];

export default function AppTabs() {
  const { width } = useWindowDimensions();
  const desktop = width >= LARGURA_DESKTOP;

  if (desktop) {
    return (
      <Tabs style={styles.desktopRoot}>
        <TabList asChild>
          <DesktopSidebar>
            {ITENS_NAV.map((item) => (
              <TabTrigger key={item.nome} name={item.nome} href={item.href} asChild>
                <SidebarItem icone={item.icone}>{item.rotulo}</SidebarItem>
              </TabTrigger>
            ))}
          </DesktopSidebar>
        </TabList>
        <View style={styles.desktopContent}>
          <TabSlot />
        </View>
      </Tabs>
    );
  }

  return (
    <Tabs>
      <TabSlot style={{ height: '100%' }} />
      <TabList asChild>
        <CustomTabList>
          {ITENS_NAV.map((item) => (
            <TabTrigger key={item.nome} name={item.nome} href={item.href} asChild>
              <TabButton icone={item.icone}>{item.rotulo}</TabButton>
            </TabTrigger>
          ))}
        </CustomTabList>
      </TabList>
    </Tabs>
  );
}

// ---------------------------------------------------------- pill (< 1100px)

function TabButton({
  children,
  isFocused,
  icone,
  ...props
}: TabTriggerSlotProps & { icone: keyof typeof Feather.glyphMap }) {
  return (
    <Pressable
      {...props}
      style={({ pressed }) => [
        styles.tabButton,
        isFocused && styles.tabButtonAtivo,
        pressed && styles.pressed,
      ]}>
      <Feather name={icone} size={18} color={isFocused ? Brand.roxoClaro : Brand.textoApagado} />
      <Text style={[styles.tabLabel, isFocused && styles.tabLabelAtivo]}>{children}</Text>
    </Pressable>
  );
}

function CustomTabList(props: TabListProps) {
  return (
    <View {...props} style={styles.tabListContainer}>
      <View style={styles.innerContainer}>{props.children}</View>
    </View>
  );
}

// --------------------------------------------------------- sidebar (>= 1100px)

function SidebarItem({
  children,
  isFocused,
  icone,
  ...props
}: TabTriggerSlotProps & { icone: keyof typeof Feather.glyphMap }) {
  return (
    <Pressable
      {...props}
      style={({ pressed }) => [
        styles.sidebarItem,
        isFocused && styles.sidebarItemAtivo,
        pressed && styles.pressed,
      ]}>
      <Feather name={icone} size={17} color={isFocused ? '#0D2705' : Brand.textoSuave} />
      <Text style={[styles.sidebarItemTexto, isFocused && styles.sidebarItemTextoAtivo]}>{children}</Text>
    </Pressable>
  );
}

function DesktopSidebar(props: TabListProps) {
  const [diasRestantes, setDiasRestantes] = useState<number | null>(null);

  useEffect(() => {
    getDiasAteProva()
      .then((d) => setDiasRestantes(d.ja_passou ? 0 : d.dias_restantes))
      .catch(() => {});
  }, []);

  return (
    <View {...props} style={styles.sidebar}>
      <View style={styles.sidebarMarca}>
        <View style={styles.sidebarMarcaIcone}>
          <Feather name="zap" size={18} color={Brand.roxoClaro} />
        </View>
        <Text style={styles.sidebarMarcaTexto}>Banco de Questões</Text>
      </View>

      <View style={styles.sidebarNav}>{props.children}</View>

      <View style={styles.sidebarRodape} />

      {diasRestantes !== null && (
        <View style={styles.sidebarCardProva}>
          <Text style={styles.sidebarCardProvaValor}>{diasRestantes} dias</Text>
          <Text style={styles.sidebarCardProvaLabel}>até o ENEM</Text>
          <View style={styles.sidebarBarraFundo}>
            <View style={[styles.sidebarBarraProgresso, { width: `${Math.max(4, 100 - diasRestantes)}%` }]} />
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  // pill flutuante (< 1100px)
  tabListContainer: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  innerContainer: {
    flexDirection: 'row',
    gap: 4,
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: 999,
    padding: 6,
  },
  tabButton: {
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 3,
    paddingVertical: 8,
    paddingHorizontal: 18,
    borderRadius: 999,
  },
  tabButtonAtivo: {
    backgroundColor: Brand.roxo,
  },
  pressed: {
    opacity: 0.8,
  },
  tabLabel: {
    fontFamily: Fontes.corpoExtraNegrito,
    fontSize: 11,
    color: Brand.textoApagado,
  },
  tabLabelAtivo: {
    color: Brand.roxoClaro,
  },
  // sidebar (>= 1100px)
  desktopRoot: {
    flex: 1,
    flexDirection: 'row',
  },
  desktopContent: {
    flex: 1,
    height: '100%',
  },
  sidebar: {
    width: 268,
    height: '100%',
    backgroundColor: Brand.bgCardEscuro,
    borderRightWidth: 1,
    borderRightColor: Brand.borda,
    padding: 18,
    gap: 6,
  },
  sidebarMarca: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 18,
    paddingHorizontal: 4,
  },
  sidebarMarcaIcone: {
    width: 32,
    height: 32,
    borderRadius: 11,
    backgroundColor: Brand.roxo,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sidebarMarcaTexto: {
    fontFamily: Fontes.tituloSemibold,
    fontSize: 14.5,
    color: Brand.texto,
    flexShrink: 1,
  },
  sidebarNav: {
    gap: 4,
  },
  sidebarItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 11,
    paddingHorizontal: 14,
    borderRadius: 14,
  },
  sidebarItemAtivo: {
    backgroundColor: Brand.verde,
  },
  sidebarItemTexto: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 14,
    color: Brand.textoSuave,
  },
  sidebarItemTextoAtivo: {
    color: '#0D2705',
  },
  sidebarRodape: {
    flex: 1,
  },
  sidebarCardProva: {
    backgroundColor: Brand.bgCard,
    borderWidth: 1,
    borderColor: Brand.borda,
    borderRadius: RaioCard,
    padding: 14,
    gap: 4,
  },
  sidebarCardProvaValor: {
    fontFamily: Fontes.titulo,
    fontSize: 18,
    color: Brand.texto,
  },
  sidebarCardProvaLabel: {
    fontFamily: Fontes.corpoNegrito,
    fontSize: 11,
    color: Brand.textoApagado,
    marginBottom: 4,
  },
  sidebarBarraFundo: {
    height: 7,
    borderRadius: 999,
    backgroundColor: Brand.bordaForte,
    overflow: 'hidden',
  },
  sidebarBarraProgresso: {
    height: 7,
    borderRadius: 999,
    backgroundColor: Brand.ouro,
  },
});
