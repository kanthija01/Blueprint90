// Premium primary / secondary / ghost button. Reanimated scale on press.

import React, { useMemo } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  View,
  ViewStyle,
  GestureResponderEvent,
} from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { Text } from "./Text";
import { colors, radius, spacing } from "@/src/theme";

type Variant = "primary" | "secondary" | "ghost";

type Props = {
  label: string;
  onPress?: (e: GestureResponderEvent) => void;
  variant?: Variant;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  style?: ViewStyle;
  testID?: string;
};

export function Button({
  label,
  onPress,
  variant = "primary",
  disabled,
  loading,
  fullWidth,
  iconLeft,
  iconRight,
  style,
  testID,
}: Props) {
  const pressed = useSharedValue(0);
  const animStyle = useAnimatedStyle(() => ({
    transform: [{ scale: 1 - pressed.value * 0.03 }],
    opacity: 1 - pressed.value * 0.05,
  }));

  const palette = useMemo(() => paletteFor(variant), [variant]);
  const isDisabled = disabled || loading;

  return (
    <Animated.View
      style={[
        { width: fullWidth ? "100%" : undefined },
        animStyle,
        style,
      ]}
    >
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ disabled: !!isDisabled, busy: !!loading }}
        testID={testID}
        disabled={isDisabled}
        onPressIn={() => {
          pressed.value = withTiming(1, { duration: 80 });
        }}
        onPressOut={() => {
          pressed.value = withTiming(0, { duration: 140 });
        }}
        onPress={onPress}
        style={[
          styles.base,
          {
            backgroundColor: palette.bg,
            borderColor: palette.border,
            borderWidth: palette.borderWidth,
            opacity: isDisabled ? 0.55 : 1,
          },
        ]}
      >
        {loading ? (
          <ActivityIndicator size="small" color={palette.fg} />
        ) : (
          <View style={styles.content}>
            {iconLeft ? <View style={styles.icon}>{iconLeft}</View> : null}
            <Text variant="button" color={palette.fg}>
              {label}
            </Text>
            {iconRight ? <View style={styles.icon}>{iconRight}</View> : null}
          </View>
        )}
      </Pressable>
    </Animated.View>
  );
}

function paletteFor(variant: Variant) {
  switch (variant) {
    case "primary":
      return {
        bg: colors.primary,
        fg: colors.textOnPrimary,
        border: colors.primary,
        borderWidth: 0,
      };
    case "secondary":
      return {
        bg: colors.card,
        fg: colors.text,
        border: colors.border,
        borderWidth: 1,
      };
    case "ghost":
      return {
        bg: "transparent",
        fg: colors.textMuted,
        border: "transparent",
        borderWidth: 0,
      };
  }
}

const styles = StyleSheet.create({
  base: {
    minHeight: 52,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  icon: { marginHorizontal: spacing.xs },
});
