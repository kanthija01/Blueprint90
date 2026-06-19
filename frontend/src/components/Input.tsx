// Input — numeric + text. Floating label, focus ring in primary yellow.

import React, { useState } from "react";
import {
  StyleSheet,
  TextInput,
  TextInputProps,
  View,
} from "react-native";

import { Text } from "./Text";
import { colors, radius, spacing } from "@/src/theme";

type Props = TextInputProps & {
  label?: string;
  hint?: string;
  error?: string;
  testID?: string;
};

export function Input({
  label,
  hint,
  error,
  style,
  onFocus,
  onBlur,
  testID,
  ...rest
}: Props) {
  const [focused, setFocused] = useState(false);

  const borderColor = error
    ? colors.danger
    : focused
      ? colors.primary
      : colors.border;

  return (
    <View style={styles.wrapper}>
      {label ? (
        <Text variant="overline" color={colors.textMuted} style={styles.label}>
          {label}
        </Text>
      ) : null}
      <TextInput
        {...rest}
        testID={testID}
        placeholderTextColor={colors.textDim}
        selectionColor={colors.primary}
        style={[
          styles.input,
          { borderColor },
          rest.multiline && styles.multiline,
          style,
        ]}
        onFocus={(e) => {
          setFocused(true);
          onFocus?.(e);
        }}
        onBlur={(e) => {
          setFocused(false);
          onBlur?.(e);
        }}
      />
      {hint && !error ? (
        <Text variant="caption" color={colors.textMuted} style={styles.hint}>
          {hint}
        </Text>
      ) : null}
      {error ? (
        <Text variant="caption" color={colors.danger} style={styles.hint}>
          {error}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { width: "100%" },
  label: { marginBottom: spacing.xs },
  input: {
    minHeight: 52,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
    backgroundColor: colors.card,
    color: colors.text,
    fontSize: 16,
    lineHeight: 20,
  },
  multiline: {
    minHeight: 140,
    textAlignVertical: "top",
    paddingTop: spacing.lg,
  },
  hint: { marginTop: spacing.xs },
});
