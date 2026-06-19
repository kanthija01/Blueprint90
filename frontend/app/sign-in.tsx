// Sign-in screen. Single CTA — Continue with Google (Emergent-managed).
import { useEffect, useState } from "react";
import { StyleSheet, View } from "react-native";
import { Redirect, useRouter } from "expo-router";
import Animated, { FadeInDown } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import { startGoogleSignIn } from "@/src/lib/emergent-auth";
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

  useEffect(() => {
    clearError();
  }, [clearError]);

  if (status === "authenticated") {
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
        setBusy(false);
        return;
      }
      await loginWithSessionId(sid);
      router.replace("/dashboard");
    } catch (e) {
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
