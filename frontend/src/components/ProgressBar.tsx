// Progress bar — thin, yellow accent, animated width via reanimated.

import { useEffect } from "react";
import { StyleSheet, View } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { colors, radius, spacing } from "@/src/theme";
import { Text } from "./Text";

type Props = {
  step: number;
  total: number;
  label?: string;
};

export function ProgressBar({ step, total, label }: Props) {
  const pct = Math.max(0, Math.min(1, step / total));
  const value = useSharedValue(pct);

  useEffect(() => {
    value.value = withTiming(pct, { duration: 320 });
  }, [pct, value]);

  const fillStyle = useAnimatedStyle(() => ({
    width: `${value.value * 100}%`,
  }));

  return (
    <View style={styles.wrapper}>
      <View style={styles.row}>
        <Text variant="overline" color={colors.textMuted}>
          {label ?? "Step"} {step} / {total}
        </Text>
        <Text variant="overline" color={colors.primary}>
          {Math.round(pct * 100)}%
        </Text>
      </View>
      <View style={styles.track}>
        <Animated.View style={[styles.fill, fillStyle]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { width: "100%" },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.sm,
  },
  track: {
    height: 6,
    backgroundColor: colors.border,
    borderRadius: radius.pill,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    backgroundColor: colors.primary,
    borderRadius: radius.pill,
  },
});
