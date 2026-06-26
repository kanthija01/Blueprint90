// Step 7 — Review + submit. Surfaces every field as a summary card so the
// user can fix anything before the assessment hits the backend.

import { StyleSheet, View } from "react-native";

import { Button, Card, Text } from "@/src/components";
import {
  DIET_LABELS,
  GENDER_LABELS,
  GOAL_LABELS,
  LIFESTYLE_LABELS,
  PROBLEM_LABELS,
  WORKOUT_PREF_LABELS,
} from "@/src/lib/constants";
import { validateForSubmit } from "@/src/lib/assessment-validation";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

export function StepReview({
  onSubmit,
  onEdit,
}: {
  onSubmit: () => void;
  onEdit: (step: number) => void;
}) {
  const draft = useAssessmentStore((s) => s.draft);
  const submitting = useAssessmentStore((s) => s.submitting);
  const submitError = useAssessmentStore((s) => s.submitError);
  const validationError = validateForSubmit(draft);

  const rows: { label: string; value: string; step: number }[] = [
    {
      step: 1,
      label: "Basic info",
      value:
        draft.age != null && draft.gender && draft.height_cm && draft.weight_kg
          ? `${draft.age} · ${GENDER_LABELS[draft.gender]} · ${draft.height_cm} cm · ${draft.weight_kg} kg`
          : "Incomplete",
    },
    {
      step: 2,
      label: "Goal",
      value: draft.goal ? GOAL_LABELS[draft.goal] : "Incomplete",
    },
    {
      step: 3,
      label: "Lifestyle",
      value: draft.lifestyle ? LIFESTYLE_LABELS[draft.lifestyle] : "Incomplete",
    },
    {
      step: 4,
      label: "Diet & training",
      value:
        draft.diet && draft.workout_preference && draft.time_available_min
          ? `${DIET_LABELS[draft.diet]} · ${WORKOUT_PREF_LABELS[draft.workout_preference]} · ${draft.time_available_min} min`
          : "Incomplete",
    },
    {
      step: 5,
      label: "Problems",
      value:
        draft.problems.length > 0
          ? draft.problems.map((p) => PROBLEM_LABELS[p]).join(", ")
          : "None selected",
    },
    {
      step: 6,
      label: "Biggest struggle",
      value:
        draft.biggest_struggle.trim().length > 0
          ? draft.biggest_struggle.trim()
          : "Not shared",
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          Review
        </Text>
        <Text variant="h1" style={styles.title}>
          Looks good?
        </Text>
        <Text variant="body" color={colors.textMuted}>
          Tap any card to fix it. Once you continue, payment opens and your
          blueprint is generated after confirmation.
        </Text>
      </View>

      <View style={styles.cards}>
        {rows.map((row) => (
          <Card
            key={row.label}
            testID={`review-${row.step}`}
            onPress={() => onEdit(row.step)}
          >
            <View style={styles.cardRow}>
              <View style={styles.cardText}>
                <Text variant="overline" color={colors.textMuted}>
                  {row.label}
                </Text>
                <Text variant="bodyStrong" style={styles.value}>
                  {row.value}
                </Text>
              </View>
              <Text variant="caption" color={colors.primary}>
                EDIT
              </Text>
            </View>
          </Card>
        ))}
      </View>

      {validationError ? (
        <Text variant="caption" color={colors.danger}>
          {validationError}
        </Text>
      ) : null}
      {submitError ? (
        <Text variant="caption" color={colors.danger}>
          {submitError}
        </Text>
      ) : null}

      <View style={styles.cta}>
        <Button
          testID="submit-assessment"
          label="Continue to Payment"
          fullWidth
          onPress={onSubmit}
          loading={submitting}
          disabled={!!validationError}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.lg },
  headerBlock: { gap: spacing.sm, marginBottom: spacing.md },
  title: { marginTop: spacing.xs },
  cards: { gap: spacing.md },
  cardRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  cardText: { flex: 1, gap: spacing.xs },
  value: { color: colors.text },
  cta: { marginTop: spacing.xl },
});
