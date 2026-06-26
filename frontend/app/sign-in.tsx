// Sign-in screen. Single CTA — Continue with Google (Emergent-managed).
import { useEffect, useRef, useState } from "react";
import { Platform, StyleSheet, View } from "react-native";
import { Redirect, useRouter } from "expo-router";
import Animated, { FadeInDown } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import {
  readWebSessionIdFromUrl,
  startGoogleSignIn,
} from "@/src/lib/emergent-auth";
import { useAuthStore } from "@/src/stores/auth";
import { colors, spacing } from "@/src/theme";

export default function SignInScreen() {
  const router = useRouter();
  const status = useAuthStore((s) => s.status);
  const loginWithSessionId = useAuthStore((s) => s.loginWithSessionId);
  const storeError = useAuthStore((s) => s.error);
  const clearError = useAuthStore((s) => s.clearError);

  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const oauthHandled = useRef(false);

  useEffect(() => {
    clearError();
  }, [clearError]);

  useEffect(() => {
    console.log("[auth] sign-in status:", status);
  }, [status]);

  // Web OAuth may return here if redirect URL ever points at /sign-in.
  useEffect(() => {
    if (Platform.OS !== "web" || oauthHandled.current) return;

    const sid = readWebSessionIdFromUrl();
    if (!sid) return;

    oauthHandled.current = true;
    console.log("[auth] sign-in session_id found, calling loginWithSessionId");

    void (async () => {
      try {
        await loginWithSessionId(sid);
        console.log("[auth] sign-in router.replace(/dashboard)");
        router.replace("/dashboard");
      } catch (e) {
        console.log("[auth] sign-in login failed:", (e as Error).message);
        oauthHandled.current = false;
      }
    })();
  }, [loginWithSessionId, router]);

  if (status === "authenticated") {
    console.log("[auth] sign-in Redirect → /dashboard");
    return <Redirect href="/dashboard" />;
  }

  const onPress = async () => {
    setLocalError(null);
    setBusy(true);
    try {
      const sid = await startGoogleSignIn();
      if (!sid) {
        // On web the browser is redirecting; on mobile this means the user
        // cancelled or no session_id was returned.
        console.log("[auth] sign-in startGoogleSignIn returned null (web redirect or cancel)");
        setBusy(false);
        return;
      }
      console.log("[auth] sign-in mobile session_id found, calling loginWithSessionId");
      await loginWithSessionId(sid);
      console.log("[auth] sign-in router.replace(/dashboard)");
      router.replace("/dashboard");
    } catch (e) {
      console.log("[auth] sign-in onPress failed:", (e as Error).message);
      setLocalError((e as Error).message || "Sign-in failed.");
      setBusy(false);
    }
  };

  const error = localError || storeError;

  return (
    <Screen edges={["top", "bottom"]}>
      <View style={styles.container}>
        <Animated.View entering={FadeInDown.duration(500)}>
          <Text variant="overline" color={colors.primary}>
            ACCOUNT
          </Text>
          <Text variant="h1" style={styles.title}>
            Sign in to continue.
          </Text>
          <Text variant="body" color={colors.textMuted} style={styles.subtitle}>
            We use Google so you don&apos;t manage another password. Your data
            is private and never used to train models.
          </Text>
        </Animated.View>

        <View style={styles.spacer} />

        <Animated.View entering={FadeInDown.delay(200).duration(500)}>
          {error ? (
            <Text
              variant="caption"
              color={colors.danger}
              style={styles.error}
            >
              {error}
            </Text>
          ) : null}
          <Button
            testID="google-signin"
            label="Continue with Google"
            fullWidth
            loading={busy}
            onPress={onPress}
            iconLeft={
              <Ionicons
                name="logo-google"
                size={18}
                color={colors.textOnPrimary}
              />
            }
          />
          <Button
            label="Back"
            variant="ghost"
            fullWidth
            onPress={() => router.back()}
            style={styles.back}
          />
        </Animated.View>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  title: { marginTop: spacing.sm },
  subtitle: { marginTop: spacing.md, maxWidth: 520 },
  spacer: { flex: 1 },
  error: { marginBottom: spacing.md },
  back: { marginTop: spacing.sm },
});
