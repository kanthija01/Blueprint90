// BulletList — small, semantic list used inside section cards. Each row has
// an optional "primary" label (yellow), main text, and optional source badge.

import { StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, spacing } from "@/src/theme";

export type BulletRow = {
  /** A short caps label shown on the yellow accent line. Optional. */
  label?: string;
  /** Primary line. */
  primary: string;
  /** Optional secondary line below. */
  secondary?: string | null;
  /** Optional provenance (module slug or "From module" badge). */
  source?: string;
  /** Stable testID. */
  testID?: string;
};

type Props = {
  rows: BulletRow[];
  testID?: string;
};

export function BulletList({ rows, testID }: Props) {
  return (
    <View style={styles.list} testID={testID}>
      {rows.map((row, i) => (
        <View
          key={i}
          style={[styles.row, i > 0 && styles.rowDivider]}
          testID={row.testID}
        >
          <View style={styles.dot} />
          <View style={styles.content}>
            {row.label ? (
              <Text variant="overline" color={colors.primary}>
                {row.label}
              </Text>
            ) : null}
            <Text variant="bodyStrong" style={styles.primary}>
              {row.primary}
            </Text>
            {row.secondary ? (
              <Text
                variant="body"
                color={colors.textMuted}
                style={styles.secondary}
              >
                {row.secondary}
              </Text>
            ) : null}
            {row.source ? (
              <Text
                variant="caption"
                color={colors.textDim}
                style={styles.source}
              >
                from {row.source}
              </Text>
            ) : null}
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  list: { gap: 0 },
  row: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: spacing.md,
    paddingVertical: spacing.md,
  },
  rowDivider: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.divider,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
    marginTop: 10,
  },
  content: { flex: 1, gap: spacing.xs },
  primary: {},
  secondary: {},
  source: { marginTop: spacing.xs },
});
