// Step 3 — Lifestyle.
import { StyleSheet, View } from "react-native";

import { Button, Chip, Text } from "@/src/components";
import { LIFESTYLES, LIFESTYLE_LABELS } from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepLifestyle({ onNext }: { onNext: () => void }) {
  const value = useAssessmentStore((s) => s.draft.lifestyle);
  const patch = useAssessmentStore((s) => s.patch);

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Context
        </Text>
        <Text variant="h1" style={styles.title}>
          Pick the life that fits.
        </Text>
        <Text variant="body" color={colors.textMuted}>
          We tailor timing, meal prep, and workout windows to your day.
        </Text>
      </View>

      <View style={styles.chips}>
        {LIFESTYLES.map((l) => (
          <Chip
            key={l}
            testID={`lifestyle-${l}`}
            label={LIFESTYLE_LABELS[l]}
            selected={value === l}
            onPress={() => patch({ lifestyle: l })}
            fullWidth
          />
        ))}
      </View>

      <View style={styles.cta}>
        <Button
          testID="step-next"
          label="Continue"
          fullWidth
          onPress={onNext}
          disabled={!value}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.lg },
  headerBlock: { gap: spacing.sm, marginBottom: spacing.md },
  title: { marginTop: spacing.xs },
  chips: { gap: spacing.md },
  cta: { marginTop: spacing.xl },
});
