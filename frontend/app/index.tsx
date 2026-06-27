// Landing screen. Public. Routes the user based on auth state once mounted.
// While auth is bootstrapping we show a subtle splash-styled state.

import { useEffect, useRef } from "react";
import { Platform, Pressable, StyleSheet, View } from "react-native";
import { Redirect, useRouter } from "expo-router";

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
  const authError = useAuthStore((s) => s.error);
  const loginWithSessionId = useAuthStore((s) => s.loginWithSessionId);
  const oauthHandled = useRef(false);

  useEffect(() => {
    console.log("[auth] index status:", status);
  }, [status]);

  // Web: detect ?session_id / #session_id on first paint and complete login.
  // Mobile: also check the initial deep link in case a sign-in was launched
  // before the app was running.
  useEffect(() => {
    if (oauthHandled.current) return;

    const run = async () => {
      const sid =
        Platform.OS === "web"
          ? readWebSessionIdFromUrl()
          : await readInitialDeepLinkSessionId();

      if (!sid) {
        console.log("[auth] index no session_id found — skipping login");
        return;
      }

      oauthHandled.current = true;
      console.log("[auth] index session_id found, calling loginWithSessionId");

      try {
        await loginWithSessionId(sid);
        console.log("[auth] index router.replace(/dashboard)");
        router.replace("/dashboard");
      } catch (e) {
        console.log("[auth] index login failed:", (e as Error).message);
        oauthHandled.current = false;
      }
    };

    void run();
  }, [loginWithSessionId, router]);

  if (status === "authenticated") {
    console.log("[auth] index Redirect → /dashboard");
    return <Redirect href="/dashboard" />;
  }

  return (
    <Screen edges={["top", "bottom"]}>
      <View style={styles.container}>
        {authError ? (
          <Text variant="caption" color={colors.danger} style={styles.error}>
            Sign-in error: {authError}
          </Text>
        ) : null}
        <View style={styles.brand}>
          <Text variant="overline" color={colors.primary}>
            BLUEPRINT 90
          </Text>
        </View>

        <View style={styles.hero}>
          <Text variant="display" style={styles.heroLine}>
            Engineered fitness.
          </Text>
          <Text variant="display" style={styles.heroLineAccent}>
            Built for you.
          </Text>
        </View>

        <View style={styles.copy}>
          <Text variant="body" color={colors.textMuted}>
            A 90-day, deterministic blueprint covering training, nutrition, and
            psychology — assembled from verified modules. No AI advice. No
            guessing.
          </Text>
        </View>

        <View style={styles.spacer} />

        <View style={styles.cta}>
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
        </View>

        {/* Footer — legal links required for Razorpay live activation */}
        <View style={styles.footer}>
          <View style={styles.footerLinks}>
            <Pressable onPress={() => router.push("/contact" as never)}>
              <Text variant="caption" color={colors.textDim} style={styles.footerLink}>
                Contact
              </Text>
            </Pressable>
            <Text variant="caption" color={colors.textDim}>·</Text>
            <Pressable onPress={() => router.push("/privacy" as never)}>
              <Text variant="caption" color={colors.textDim} style={styles.footerLink}>
                Privacy Policy
              </Text>
            </Pressable>
            <Text variant="caption" color={colors.textDim}>·</Text>
            <Pressable onPress={() => router.push("/terms" as never)}>
              <Text variant="caption" color={colors.textDim} style={styles.footerLink}>
                Terms &amp; Conditions
              </Text>
            </Pressable>
            <Text variant="caption" color={colors.textDim}>·</Text>
            <Pressable onPress={() => router.push("/refund" as never)}>
              <Text variant="caption" color={colors.textDim} style={styles.footerLink}>
                Refund Policy
              </Text>
            </Pressable>
          </View>
          <Text variant="caption" color={colors.textDim} align="center" style={styles.copyright}>
            © {new Date().getFullYear()} Blueprint 90. All rights reserved.
          </Text>
        </View>
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
  error: { marginBottom: spacing.md },
  footer: {
    paddingTop: spacing.lg,
    paddingBottom: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    gap: spacing.sm,
  },
  footerLinks: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.sm,
  },
  footerLink: {
    textDecorationLine: "underline",
  },
  copyright: {
    marginTop: spacing.xs,
  },
});
