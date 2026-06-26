// TrackerTable — horizontally scrollable progress grid. Weeks down the
// left, user-fillable columns to the right. Pure visual; cells stay blank.

import { ScrollView, StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, radius, spacing } from "@/src/theme";

type Props = {
  columns: string[];
  weeks: number[];
  testID?: string;
};

const WEEK_COL_WIDTH = 64;
const DATA_COL_WIDTH = 120;
const ROW_HEIGHT = 44;

export function TrackerTable({ columns, weeks, testID }: Props) {
  return (
    <View style={styles.wrapper} testID={testID}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.scroll}
      >
        <View>
          {/* Header row */}
          <View style={styles.row}>
            <View style={[styles.cell, styles.weekCell, styles.headerCell]}>
              <Text variant="overline" color={colors.textMuted}>
                Week
              </Text>
            </View>
            {columns.map((c) => (
              <View
                key={c}
                style={[styles.cell, styles.dataCell, styles.headerCell]}
              >
                <Text
                  variant="overline"
                  color={colors.primary}
                  numberOfLines={2}
                >
                  {c}
                </Text>
              </View>
            ))}
          </View>

          {/* Body rows */}
          {weeks.map((wk, idx) => (
            <View
              key={wk}
              style={[styles.row, idx % 2 === 0 ? styles.rowEven : null]}
              testID={`tracker-row-${wk}`}
            >
              <View style={[styles.cell, styles.weekCell]}>
                <Text variant="bodyStrong" color={colors.text}>
                  {wk}
                </Text>
              </View>
              {columns.map((c) => (
                <View
                  key={c}
                  style={[styles.cell, styles.dataCell]}
                  testID={`tracker-cell-${wk}-${c}`}
                />
              ))}
            </View>
          ))}
        </View>
      </ScrollView>
      {columns.length === 0 ? (
        <Text
          variant="caption"
          color={colors.textDim}
          style={styles.empty}
        >
          No tracker columns defined for this module.
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: "hidden",
    backgroundColor: colors.cardElevated,
  },
  scroll: { flexGrow: 1 },
  row: { flexDirection: "row", minHeight: ROW_HEIGHT },
  rowEven: { backgroundColor: "rgba(255,255,255,0.02)" },
  cell: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    justifyContent: "center",
    borderRightWidth: StyleSheet.hairlineWidth,
    borderRightColor: colors.divider,
  },
  weekCell: { width: WEEK_COL_WIDTH, alignItems: "flex-start" },
  dataCell: { width: DATA_COL_WIDTH },
  headerCell: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.card,
  },
  empty: { padding: spacing.md },
});
