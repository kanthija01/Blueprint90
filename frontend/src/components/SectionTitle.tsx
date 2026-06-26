// SectionTitle — the standard "OVERLINE + h2 + optional subtitle" pattern
// used at the top of every preview section.

import { StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, spacing } from "@/src/theme";

type Props = {
  eyebrow: string;
  title: string;
  subtitle?: string;
  testID?: string;
};

export function SectionTitle({ eyebrow, title, subtitle, testID }: Props) {
  return (
    <View style={styles.wrapper} testID={testID}>
      <Text variant="overline" color={colors.primary}>
        {eyebrow}
      </Text>
      <Text variant="h2" style={styles.title}>
        {title}
      </Text>
      {subtitle ? (
        <Text variant="body" color={colors.textMuted} style={styles.subtitle}>
          {subtitle}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: spacing.lg },
  title: { marginTop: spacing.xs },
  subtitle: { marginTop: spacing.sm, maxWidth: 600 },
});
