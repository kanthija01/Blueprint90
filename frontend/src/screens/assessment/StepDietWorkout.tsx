// Step 4 — Diet + Workout preference + Time available.
import { StyleSheet, View } from "react-native";

import { Button, Chip, Text } from "@/src/components";
import {
  DIETS,
  DIET_LABELS,
  TIME_MINUTES,
  WORKOUT_PREFERENCES,
  WORKOUT_PREF_LABELS,
} from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepDietWorkout({ onNext }: { onNext: () => void }) {
  const draft = useAssessmentStore((s) => s.draft);
  const patch = useAssessmentStore((s) => s.patch);

  const ready =
    !!draft.diet && !!draft.workout_preference && !!draft.time_available_min;

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Style
        </Text>
        <Text variant="h1" style={styles.title}>
          How do you eat and train?
        </Text>
      </View>

      <View style={styles.section}>
        <Text variant="overline" color={colors.textMuted}>
          Diet
        </Text>
        <View style={styles.row}>
          {DIETS.map((d) => (
            <View key={d} style={styles.cell}>
              <Chip
                testID={`diet-${d}`}
                label={DIET_LABELS[d]}
                selected={draft.diet === d}
                onPress={() => patch({ diet: d })}
              />
            </View>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text variant="overline" color={colors.textMuted}>
          Where will you train?
        </Text>
        <View style={styles.row}>
          {WORKOUT_PREFERENCES.map((w) => (
            <View key={w} style={styles.cell}>
              <Chip
                testID={`workout-${w}`}
                label={WORKOUT_PREF_LABELS[w]}
                selected={draft.workout_preference === w}
                onPress={() => patch({ workout_preference: w })}
              />
            </View>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text variant="overline" color={colors.textMuted}>
          Time per session
        </Text>
        <View style={styles.row}>
          {TIME_MINUTES.map((t) => (
            <View key={t} style={styles.cell}>
              <Chip
                testID={`time-${t}`}
                label={`${t} min`}
                selected={draft.time_available_min === t}
                onPress={() => patch({ time_available_min: t })}
              />
            </View>
          ))}
        </View>
      </View>

      <View style={styles.cta}>
        <Button
          testID="step-next"
          label="Continue"
          fullWidth
          onPress={onNext}
          disabled={!ready}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.lg },
  headerBlock: { gap: spacing.sm, marginBottom: spacing.md },
  title: { marginTop: spacing.xs },
  section: { gap: spacing.sm },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  cell: { flexGrow: 1, flexBasis: "45%" },
  cta: { marginTop: spacing.xl },
});
