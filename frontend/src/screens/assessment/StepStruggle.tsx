// Step 6 — Biggest struggle (free text, 500 chars).
import { StyleSheet, View } from "react-native";

import { Button, Input, Text } from "@/src/components";
import { STRUGGLE_MAX_LEN } from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepStruggle({ onNext }: { onNext: () => void }) {
  const value = useAssessmentStore((s) => s.draft.biggest_struggle);
  const patch = useAssessmentStore((s) => s.patch);

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Story
        </Text>
        <Text variant="h1" style={styles.title}>
          What&apos;s the biggest thing in your way?
        </Text>
        <Text variant="body" color={colors.textMuted}>
          Optional, but powerful. The plan adapts to the words you choose.
        </Text>
      </View>

      <Input
        testID="input-struggle"
        label="Your story"
        value={value}
        onChangeText={(t) =>
          patch({ biggest_struggle: t.slice(0, STRUGGLE_MAX_LEN) })
        }
        placeholder="e.g. I can never stay consistent past 3 weeks..."
        multiline
        maxLength={STRUGGLE_MAX_LEN}
        hint={`${value.length} / ${STRUGGLE_MAX_LEN}`}
      />

      <View style={styles.cta}>
        <Button
          testID="step-next"
          label={value.trim().length === 0 ? "Skip & continue" : "Continue"}
          variant={value.trim().length === 0 ? "secondary" : "primary"}
          fullWidth
          onPress={onNext}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.lg },
  headerBlock: { gap: spacing.sm, marginBottom: spacing.md },
  title: { marginTop: spacing.xs },
  cta: { marginTop: spacing.xl },
});
