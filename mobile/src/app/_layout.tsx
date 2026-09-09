import { Baloo2_700Bold, Baloo2_800ExtraBold } from '@expo-google-fonts/baloo-2';
import { Nunito_400Regular, Nunito_700Bold, Nunito_800ExtraBold, useFonts } from '@expo-google-fonts/nunito';
import { DarkTheme, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';

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

  if (!fontesCarregadas) return null;

  return (
    <ThemeProvider value={DarkTheme}>
      <AnimatedSplashOverlay />
      <AppTabs />
    </ThemeProvider>
  );
}
