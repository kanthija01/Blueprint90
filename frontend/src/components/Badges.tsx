// ModuleBadge + FallbackBadge — small pill labels surfaced on the cover card.

import { StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, radius, spacing } from "@/src/theme";

export function ModuleBadge({
  label,
  primary,
  testID,
}: {
  label: string;
  primary?: boolean;
  testID?: string;
}) {
  return (
    <View
      style={[
        styles.base,
        primary ? styles.primary : styles.secondary,
      ]}
      testID={testID}
    >
      <Text
        variant="overline"
        color={primary ? colors.textOnPrimary : colors.text}
      >
        {label}
      </Text>
    </View>
  );
}

export function FallbackBadge({
  note,
  testID,
}: {
  note?: string | null;
  testID?: string;
}) {
  return (
    <View style={[styles.base, styles.fallback]} testID={testID}>
      <Text variant="overline" color={colors.warning}>
        FALLBACK{note ? " · " : ""}
      </Text>
      {note ? (
        <Text
          variant="caption"
          color={colors.textMuted}
          style={styles.fallbackNote}
          numberOfLines={2}
        >
          {note}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
    borderWidth: 1,
    gap: spacing.xs,
  },
  primary: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  secondary: {
    backgroundColor: colors.card,
    borderColor: colors.border,
  },
  fallback: {
    backgroundColor: "rgba(255, 176, 32, 0.12)",
    borderColor: colors.warning,
    maxWidth: "100%",
  },
  fallbackNote: { maxWidth: 220 },
});
