import Feather from '@expo/vector-icons/Feather';
import { NativeTabs } from 'expo-router/unstable-native-tabs';

import { Brand } from '@/constants/brand';

/** Barra de abas nativa (iOS/Android) -- rebrand pra tirar o boilerplate
 * "Expo Starter" (ícones PNG genéricos, cores de constants/theme.ts) e
 * usar os tokens reais do app (constants/brand.ts) + ícones Feather via
 * NativeTabs.Trigger.VectorIcon, a mesma biblioteca já usada em
 * seletor.tsx -- API confirmada lendo
 * node_modules/expo-router/build/native-tabs/common/elements.d.ts antes
 * de escrever isto, já que unstable-native-tabs muda entre versões do
 * Expo (ver mobile/AGENTS.md). 3ª aba "Perfil" -- ver src/app/perfil.tsx. */
export default function AppTabs() {
  return (
    <NativeTabs
      backgroundColor={Brand.bgCard}
      tintColor={Brand.roxo}
      iconColor={Brand.textoApagado}
      indicatorColor={Brand.roxoBg}
      labelStyle={{ selected: { color: Brand.texto } }}>
      <NativeTabs.Trigger name="index">
        <NativeTabs.Trigger.Label>Home</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon
          src={<NativeTabs.Trigger.VectorIcon family={Feather} name="home" />}
        />
      </NativeTabs.Trigger>

      <NativeTabs.Trigger name="explore">
        <NativeTabs.Trigger.Label>Explore</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon
          src={<NativeTabs.Trigger.VectorIcon family={Feather} name="compass" />}
        />
      </NativeTabs.Trigger>

      <NativeTabs.Trigger name="perfil">
        <NativeTabs.Trigger.Label>Perfil</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon
          src={<NativeTabs.Trigger.VectorIcon family={Feather} name="user" />}
        />
      </NativeTabs.Trigger>
    </NativeTabs>
  );
}
