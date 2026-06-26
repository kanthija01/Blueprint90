// Auth guard for the protected stack. Bounces the user back to / if not
// authenticated. Shown while bootstrap is still pending.

import { Redirect, Stack } from "expo-router";
import { useEffect } from "react";

import { Screen, Text } from "@/src/components";
import { useAuthStore } from "@/src/stores/auth";
import { colors } from "@/src/theme";

export default function ProtectedLayout() {
  const status = useAuthStore((s) => s.status);

  useEffect(() => {
    console.log("[auth] protected layout status:", status);
  }, [status]);

  if (status === "booting") {
    return (
      <Screen>
        <Text variant="overline" color={colors.textMuted}>
          Loading...
        </Text>
      </Screen>
    );
  }
  if (status === "unauthenticated") {
    return <Redirect href="/" />;
  }
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        animation: "slide_from_right",
      }}
    />
  );
}
