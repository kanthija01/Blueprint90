// Landing screen. Public. Routes the user based on auth state once mounted.
// While auth is bootstrapping we show a subtle splash-styled state.

import { useEffect } from "react";
import { Platform, StyleSheet, View } from "react-native";
import { Redirect, useRouter } from "expo-router";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";

import { Button, Screen, Text } from "@/src/components";
import {
  readInitialDeepLinkSessionId,
  readWebSessionIdFromUrl,
} from "@/src/lib/emergent-auth";
import { useAuthStore } from "@/src/stores/auth";
import { colors, spacing } from "@/src/theme";

export default function LandingScreen() {
  const router = useRouter();
  const status = useAuthStore((s) => s.status);
  const loginWithSessionId = useAuthStore((s) => s.loginWithSessionId);

  // Web: detect ?session_id / #session_id on first paint and complete login.
  // Mobile: also check the initial deep link in case a sign-in was launched
  // before the app was running.
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      const sid =
        Platform.OS === "web"
          ? readWebSessionIdFromUrl()
          : await readInitialDeepLinkSessionId();
      if (!sid || cancelled) return;
      try {
        await loginWithSessionId(sid);
      } catch {
        // already surfaced via store.error
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, [loginWithSessionId]);

  if (status === "authenticated") {
    return <Redirect href="/dashboard" />;
  }

  return (
    <Screen edges={["top", "bottom"]}>
      <View style={styles.container}>
        <Animated.View entering={FadeInUp.duration(600)} style={styles.brand}>
          <Text variant="overline" color={colors.primary}>
            BLUEPRINT 90
          </Text>
        </Animated.View>

        <Animated.View
          entering={FadeInDown.delay(120).duration(700)}
          style={styles.hero}
        >
          <Text variant="display" style={styles.heroLine}>
            Engineered fitness.
          </Text>
          <Text variant="display" style={styles.heroLineAccent}>
            Built for you.
          </Text>
        </Animated.View>

        <Animated.View
          entering={FadeInDown.delay(280).duration(700)}
          style={styles.copy}
        >
          <Text variant="body" color={colors.textMuted}>
            A 90-day, deterministic blueprint covering training, nutrition, and
            psychology — assembled from verified modules. No AI advice. No
            guessing.
          </Text>
        </Animated.View>

        <View style={styles.spacer} />

        <Animated.View
          entering={FadeInDown.delay(440).duration(700)}
          style={styles.cta}
        >
          <Button
            testID="start-cta"
            label="Start Your Blueprint"
            fullWidth
            onPress={() => router.push("/sign-in")}
          />
          <Text
            variant="caption"
            color={colors.textDim}
            align="center"
            style={styles.legal}
          >
            By continuing you agree to a deterministic, content-driven plan.
          </Text>
        </Animated.View>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "flex-start" },
  brand: { marginTop: spacing.md, marginBottom: spacing.xxl },
  hero: { gap: spacing.xs },
  heroLine: {},
  heroLineAccent: { color: colors.primary },
  copy: { marginTop: spacing.xl, maxWidth: 540 },
  spacer: { flex: 1, minHeight: spacing.xxxl },
  cta: { gap: spacing.md, marginBottom: spacing.lg },
  legal: { marginTop: spacing.sm },
});
