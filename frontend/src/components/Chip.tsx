// Chip — selectable pill. Used for single-select (gender, goal, lifestyle,
// diet, workout pref, time) AND multi-select (problems). The caller controls
// which mode via `selected`.

import { Pressable, StyleSheet, View } from "react-native";

import { Text } from "./Text";
import { colors, radius, spacing, minTouchTarget } from "@/src/theme";

type Props = {
  label: string;
  selected: boolean;
  onPress: () => void;
  fullWidth?: boolean;
  testID?: string;
};

export function Chip({ label, selected, onPress, fullWidth, testID }: Props) {
  return (
    <Pressable
      onPress={onPress}
      testID={testID}
      accessibilityRole="button"
      accessibilityState={{ selected }}
      style={({ pressed }) => [
        styles.base,
        {
          backgroundColor: selected ? colors.primaryMuted : colors.card,
          borderColor: selected ? colors.primary : colors.border,
          width: fullWidth ? "100%" : undefined,
          opacity: pressed ? 0.85 : 1,
        },
      ]}
    >
      <View style={styles.inner}>
        <Text
          variant="bodyStrong"
          color={selected ? colors.primary : colors.text}
        >
          {label}
        </Text>
        {selected ? <View style={styles.dot} /> : null}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: minTouchTarget,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
  },
  inner: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: colors.primary,
  },
});
