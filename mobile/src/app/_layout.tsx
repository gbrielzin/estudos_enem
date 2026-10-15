import { Baloo2_700Bold, Baloo2_800ExtraBold } from '@expo-google-fonts/baloo-2';
import { Nunito_400Regular, Nunito_700Bold, Nunito_800ExtraBold, useFonts } from '@expo-google-fonts/nunito';
import { DarkTheme, ThemeProvider, usePathname } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect, useRef } from 'react';
import { AppState } from 'react-native';

import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';
import { definirTelaAtual, registrarEvento, telaDoCaminho } from '@/lib/api';

SplashScreen.preventAutoHideAsync();

/**
 * Tema escuro fixo (não segue o sistema) -- identidade visual própria
 * do app mobile, definida pelo mockup de referência (ver
 * constants/brand.ts). Diferente do template original do Expo, que
 * alternava claro/escuro com o SO.
 */
export default function TabLayout() {
  const [fontesCarregadas] = useFonts({
    Baloo2_700Bold,
    Baloo2_800ExtraBold,
    Nunito_400Regular,
    Nunito_700Bold,
    Nunito_800ExtraBold,
  });

  useEffect(() => {
    if (fontesCarregadas) SplashScreen.hideAsync();
  }, [fontesCarregadas]);

  // Eventos de uso para o painel de admin (ver registrarEvento em lib/api.ts):
  // uma abertura por carregamento do app e uma visita por troca de tela.
  const rota = usePathname();
  const rotaAnterior = useRef<string | null>(null);
  useEffect(() => {
    definirTelaAtual(rota);
    // A 1ª tela já vai no app_aberto: tela_vista só nas trocas, sem linha duplicada.
    if (rotaAnterior.current === null) {
      registrarEvento('app_aberto', telaDoCaminho(rota));
    } else if (rotaAnterior.current !== rota) {
      registrarEvento('tela_vista', telaDoCaminho(rota));
    }
    rotaAnterior.current = rota;
  }, [rota]);
  // Voltar do segundo plano (app instalado na tela inicial, aba de volta ao
  // foco) também é abrir: sem isso, quem volta no dia seguinte para a mesma
  // tela não contaria como D1. Na web o AppState usa o visibilitychange.
  useEffect(() => {
    const assinatura = AppState.addEventListener('change', (estado) => {
      if (estado === 'active' && rotaAnterior.current !== null) {
        registrarEvento('app_aberto', telaDoCaminho(rotaAnterior.current));
      }
    });
    return () => assinatura.remove();
  }, []);

  if (!fontesCarregadas) return null;

  return (
    <ThemeProvider value={DarkTheme}>
      <AnimatedSplashOverlay />
      <AppTabs />
    </ThemeProvider>
  );
}
