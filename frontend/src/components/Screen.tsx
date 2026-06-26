// Screen — the standard luxury-black background wrapper. SafeAreaView,
// keyboard avoiding, light status bar. All screens use this.

import { ReactNode } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  View,
  ViewStyle,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";

import { colors, spacing } from "@/src/theme";

type Props = {
  children: ReactNode;
  scroll?: boolean;
  padded?: boolean;
  edges?: Array<"top" | "bottom" | "left" | "right">;
  contentContainerStyle?: ViewStyle;
  testID?: string;
};

export function Screen({
  children,
  scroll = false,
  padded = true,
  edges = ["top", "bottom"],
  contentContainerStyle,
  testID,
}: Props) {
  return (
    <SafeAreaView style={styles.safe} edges={edges} testID={testID}>
      <StatusBar style="light" />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        {scroll ? (
          <ScrollView
            style={styles.flex}
            contentContainerStyle={[
              styles.scrollContent,
              padded && styles.padded,
              contentContainerStyle,
            ]}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            {children}
          </ScrollView>
        ) : (
          <View
            style={[
              styles.inner,
              padded && styles.padded,
              contentContainerStyle,
            ]}
          >
            {children}
          </View>
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  flex: { flex: 1 },
  scrollContent: {
    flexGrow: 1,
  },
  inner: {
    flex: 1,
  },
  padded: {
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.lg,
  },
});
