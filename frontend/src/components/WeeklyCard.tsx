// WeeklyCard — one row in the 12-week milestone grid.

import { StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, radius, spacing } from "@/src/theme";

type Props = {
  week: number;
  focus: string;
  checklist: string[];
  testID?: string;
};

function isMilestoneWeek(week: number): boolean {
  return week === 1 || week === 4 || week === 8 || week === 12;
}

export function WeeklyCard({ week, focus, checklist, testID }: Props) {
  const milestone = isMilestoneWeek(week);
  return (
    <View
      style={[styles.card, milestone && styles.cardMilestone]}
      testID={testID}
    >
      <View style={styles.head}>
        <View
          style={[styles.badge, milestone && styles.badgeMilestone]}
        >
          <Text
            variant="overline"
            color={milestone ? colors.textOnPrimary : colors.text}
          >
            WK {week}
          </Text>
        </View>
        <Text variant="bodyStrong" style={styles.focus}>
          {focus}
        </Text>
      </View>
      {checklist.length > 0 ? (
        <View style={styles.list}>
          {checklist.map((item, i) => (
            <View key={i} style={styles.itemRow}>
              <Text variant="caption" color={colors.primary}>
                □
              </Text>
              <Text
                variant="caption"
                color={colors.textMuted}
                style={styles.itemText}
              >
                {item}
              </Text>
            </View>
          ))}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.cardElevated,
    padding: spacing.md,
    gap: spacing.sm,
  },
  cardMilestone: {
    borderColor: colors.primary,
  },
  head: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  badge: {
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: colors.border,
  },
  badgeMilestone: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  focus: { flex: 1 },
  list: { gap: spacing.xs, marginTop: spacing.xs },
  itemRow: { flexDirection: "row", alignItems: "flex-start", gap: spacing.sm },
  itemText: { flex: 1 },
});
