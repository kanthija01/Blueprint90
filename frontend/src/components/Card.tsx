// Card — generic rounded container. Used for dashboard items, review
// summaries, info blocks.

import { ReactNode } from "react";
import { Pressable, StyleSheet, View, ViewStyle } from "react-native";

import { colors, radius, spacing } from "@/src/theme";

type Props = {
  children: ReactNode;
  onPress?: () => void;
  elevated?: boolean;
  style?: ViewStyle;
  testID?: string;
};

export function Card({ children, onPress, elevated, style, testID }: Props) {
  const content = (
    <View
      style={[
        styles.base,
        { backgroundColor: elevated ? colors.cardElevated : colors.card },
        style,
      ]}
    >
      {children}
    </View>
  );
  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        testID={testID}
        android_ripple={{ color: colors.borderStrong }}
      >
        {content}
      </Pressable>
    );
  }
  return <View testID={testID}>{content}</View>;
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
});
