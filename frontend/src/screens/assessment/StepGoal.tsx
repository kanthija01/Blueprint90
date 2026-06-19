// Step 2 — Goal selection.
import { StyleSheet, View } from "react-native";

import { Button, Chip, Text } from "@/src/components";
import { GOAL_LABELS, GOALS } from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepGoal({ onNext }: { onNext: () => void }) {
  const goal = useAssessmentStore((s) => s.draft.goal);
  const patch = useAssessmentStore((s) => s.patch);

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Outcome
        </Text>
        <Text variant="h1" style={styles.title}>
          What are we aiming for?
        </Text>
        <Text variant="body" color={colors.textMuted}>
          One primary outcome — the blueprint is engineered around it.
        </Text>
      </View>

      <View style={styles.chips}>
        {GOALS.map((g) => (
          <Chip
            key={g}
            testID={`goal-${g}`}
            label={GOAL_LABELS[g]}
            selected={goal === g}
            onPress={() => patch({ goal: g })}
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
          disabled={!goal}
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
