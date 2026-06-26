import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { useEffect } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StyleSheet } from "react-native";

import { captureWebOAuthSession } from "@/src/lib/emergent-auth";
import { useIconFonts } from "@/src/hooks/use-icon-fonts";
import { useAuthStore } from "@/src/stores/auth";
import { colors } from "@/src/theme";

// Stash OAuth session_id before expo-router can strip query params.
captureWebOAuthSession();

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useIconFonts();
  const bootstrap = useAuthStore((s) => s.bootstrap);
  const status = useAuthStore((s) => s.status);

  useEffect(() => {
    console.log("[auth] root layout calling bootstrap()");
    void bootstrap();
  }, [bootstrap]);

  useEffect(() => {
    if ((loaded || error) && status !== "booting") {
      SplashScreen.hideAsync();
    }
  }, [loaded, error, status]);

  if (!loaded && !error) return null;

  return (
    <GestureHandlerRootView style={styles.flex}>
      <SafeAreaProvider>
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: colors.background },
            animation: "fade",
          }}
        />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
});
