// Themed Text wrapper. Always reach for this rather than raw <Text>
// so the type ramp + color tokens stay consistent.

import { Text as RNText, StyleSheet, TextProps, TextStyle } from "react-native";

import { colors, typography, TypographyVariant } from "@/src/theme";

type Props = TextProps & {
  variant?: TypographyVariant;
  color?: string;
  align?: TextStyle["textAlign"];
};

export function Text({
  variant = "body",
  color,
  align,
  style,
  children,
  ...rest
}: Props) {
  return (
    <RNText
      style={[
        styles.base,
        typography[variant],
        color ? { color } : null,
        align ? { textAlign: align } : null,
        style,
      ]}
      {...rest}
    >
      {children}
    </RNText>
  );
}

const styles = StyleSheet.create({
  base: { color: colors.text },
});
