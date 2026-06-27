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
    // Hide the splash as soon as fonts are ready — do not wait for the auth
    // bootstrap to complete (backend cold-start on Render can take several
    // seconds, which would show a blank screen on web).
    if (loaded || error || loaded === undefined) {
      SplashScreen.hideAsync();
    }
  }, [loaded, error]);

  // Only block rendering while fonts are genuinely being loaded (Expo Go /
  // StoreClient only — outside Expo Go the font map is always empty and
  // useIconFonts resolves to [true, null] or [] immediately).
  // During static export, expo-font's server build returns [] from useFonts,
  // so `loaded` is undefined — guarding on it causes the layout to return
  // null and the entire screen tree to be omitted from the HTML output.
  const fontsReady = loaded === true || error != null || loaded === undefined;
  if (!fontsReady) return null;

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
