import { Tabs, TabList, TabTrigger, TabSlot } from 'expo-router/ui';
import { View } from 'react-native';

import { CustomTabList, ITENS_NAV, TabButton } from '@/components/tab-bar';

/**
 * Barra de abas nativa (iOS/Android) -- MESMA barra do site (ver
 * components/tab-bar.tsx, extraído daqui pra ser a fonte única dos
 * dois lugares), que por sua vez é o visual do projeto de design do
 * usuário no Claude Design (App ENEM.dc.html, rodapé das telas do
 * celular).
 *
 * Antes usava `NativeTabs` (chrome de tab bar do sistema operacional
 * -- Material/iOS nativo) em vez da barra custom que o site já tinha
 * -- pedido explícito do usuário: quer a MESMA barra do design no
 * celular, não o chrome nativo do SO. `Tabs`/`TabList`/`TabTrigger`/
 * `TabSlot` (de `expo-router/ui`, a API de tabs customizável, não a
 * `NativeTabs` antiga) é multiplataforma de verdade -- já confirmado
 * funcionando em app-tabs.web.tsx antes desta troca.
 *
 * Layout em coluna normal (TabSlot ocupa o espaço restante, a barra
 * vem depois, sem overflow) -- diferente da 1a versão desta barra
 * (uma pill flutuante por cima do conteúdo via position:absolute), a
 * barra atual do design fica ENCOSTADA no fundo, sem flutuar.
 */
export default function AppTabs() {
  return (
    <Tabs style={{ flex: 1 }}>
      <View style={{ flex: 1 }}>
        <TabSlot />
      </View>
      <TabList asChild>
        <CustomTabList>
          {ITENS_NAV.map((item) => (
            <TabTrigger key={item.nome} name={item.nome} href={item.href} asChild>
              <TabButton nome={item.nome} rotulo={item.rotulo} />
            </TabTrigger>
          ))}
        </CustomTabList>
      </TabList>
    </Tabs>
  );
}
