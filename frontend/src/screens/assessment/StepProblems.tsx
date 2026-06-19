// Step 5 — Problems (multi-select).
import { StyleSheet, View } from "react-native";

import { Button, Chip, Text } from "@/src/components";
import { PROBLEMS, PROBLEM_LABELS } from "@/src/lib/constants";
import type { Problem } from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepProblems({ onNext }: { onNext: () => void }) {
  const selected = useAssessmentStore((s) => s.draft.problems);
  const patch = useAssessmentStore((s) => s.patch);

  const toggle = (p: Problem) => {
    const set = new Set(selected);
    if (set.has(p)) set.delete(p);
    else set.add(p);
    patch({ problems: Array.from(set) });
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Friction
        </Text>
        <Text variant="h1" style={styles.title}>
          What are you up against?
        </Text>
        <Text variant="body" color={colors.textMuted}>
          Select any that apply. Each one unlocks a dedicated module in your blueprint.
        </Text>
      </View>

      <View style={styles.row}>
        {PROBLEMS.map((p) => (
          <View key={p} style={styles.cell}>
            <Chip
              testID={`problem-${p}`}
              label={PROBLEM_LABELS[p]}
              selected={selected.includes(p)}
              onPress={() => toggle(p)}
            />
          </View>
        ))}
      </View>

      <View style={styles.cta}>
        <Button
          testID="step-next"
          label={selected.length === 0 ? "Skip & continue" : "Continue"}
          variant={selected.length === 0 ? "secondary" : "primary"}
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
  row: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  cell: { flexGrow: 1, flexBasis: "45%" },
  cta: { marginTop: spacing.xl },
});
