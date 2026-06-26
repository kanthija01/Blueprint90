// BlueprintSectionCard — the outer container for one preview section.
// Fades in on scroll-into-view via reanimated entering animation.

import { ReactNode } from "react";
import { StyleSheet, View, ViewStyle } from "react-native";
import Animated, { FadeInUp } from "react-native-reanimated";

import { Card } from "./Card";
import { Text } from "./Text";
import { colors, spacing } from "@/src/theme";

type Props = {
  letter?: string; // "A" / "B" / ...
  eyebrow: string;
  title: string;
  subtitle?: string;
  emptyLabel?: string;
  empty?: boolean;
  delay?: number;
  children?: ReactNode;
  style?: ViewStyle;
  testID?: string;
};

export function BlueprintSectionCard({
  letter,
  eyebrow,
  title,
  subtitle,
  emptyLabel,
  empty,
  delay = 0,
  children,
  style,
  testID,
}: Props) {
  return (
    <Animated.View
      entering={FadeInUp.delay(delay).duration(420)}
      style={[styles.wrapper, style]}
      testID={testID}
    >
      <Card>
        <View style={styles.header}>
          {letter ? (
            <View style={styles.letter}>
              <Text variant="overline" color={colors.primary}>
                {letter}
              </Text>
            </View>
          ) : null}
          <View style={styles.headerText}>
            <Text variant="overline" color={colors.textMuted}>
              {eyebrow}
            </Text>
            <Text variant="h3" style={styles.title}>
              {title}
            </Text>
            {subtitle ? (
              <Text
                variant="caption"
                color={colors.textMuted}
                style={styles.subtitle}
              >
                {subtitle}
              </Text>
            ) : null}
          </View>
        </View>
        {empty ? (
          <Text
            variant="caption"
            color={colors.textDim}
            style={styles.empty}
          >
            {emptyLabel ?? "Nothing to show in this section yet."}
          </Text>
        ) : (
          <View style={styles.body}>{children}</View>
        )}
      </Card>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: spacing.lg },
  header: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  letter: {
    width: 32,
    height: 32,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  headerText: { flex: 1, gap: spacing.xs },
  title: { marginTop: spacing.xs },
  subtitle: { marginTop: spacing.xs },
  body: { gap: spacing.md },
  empty: { fontStyle: "italic" },
});
