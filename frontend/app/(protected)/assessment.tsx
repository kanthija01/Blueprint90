// Multi-step assessment screen — a single route that internally swaps step
// components. Reanimated handles the slide/fade transition.

import { useCallback, useEffect } from "react";
import { Alert, StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import Animated, { FadeInRight } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";
import { Pressable } from "react-native";

import { ProgressBar, Screen, Text } from "@/src/components";
import { submitAssessment } from "@/src/api/assessment";
import { draftToPayload } from "@/src/lib/assessment-validation";
import { TOTAL_STEPS, useAssessmentStore } from "@/src/stores/assessment";
import { ApiError } from "@/src/api/client";
import { StepBasicInfo } from "@/src/screens/assessment/StepBasicInfo";
import { StepGoal } from "@/src/screens/assessment/StepGoal";
import { StepLifestyle } from "@/src/screens/assessment/StepLifestyle";
import { StepDietWorkout } from "@/src/screens/assessment/StepDietWorkout";
import { StepProblems } from "@/src/screens/assessment/StepProblems";
import { StepStruggle } from "@/src/screens/assessment/StepStruggle";
import { StepReview } from "@/src/screens/assessment/StepReview";
import { colors, hitSlop, spacing } from "@/src/theme";

export default function AssessmentScreen() {
  const router = useRouter();
  const step = useAssessmentStore((s) => s.step);
  const setStep = useAssessmentStore((s) => s.setStep);
  const next = useAssessmentStore((s) => s.next);
  const prev = useAssessmentStore((s) => s.prev);
  const draft = useAssessmentStore((s) => s.draft);
  const hydrate = useAssessmentStore((s) => s.hydrate);
  const reset = useAssessmentStore((s) => s.reset);
  const setSubmitting = useAssessmentStore((s) => s.setSubmitting);
  const setSubmitError = useAssessmentStore((s) => s.setSubmitError);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  const handleBack = useCallback(() => {
    if (step === 1) {
      router.back();
    } else {
      prev();
    }
  }, [step, prev, router]);

  const handleSubmit = useCallback(async () => {
    setSubmitError(null);
    try {
      const payload = draftToPayload(draft);
      setSubmitting(true);
      const result = await submitAssessment(payload);
      setSubmitting(false);
      await reset();
      Alert.alert(
        "Blueprint ready",
        "Your 90-day blueprint has been generated and saved.",
        [
          {
            text: "Back to dashboard",
            onPress: () => router.replace("/dashboard"),
          },
        ],
      );
      // Mark the blueprint id in console for the next phase to consume.
      console.log("[blueprint] created", result.blueprint_id);
    } catch (e) {
      setSubmitting(false);
      const msg =
        e instanceof ApiError
          ? e.message || `Server error (${e.status})`
          : (e as Error).message;
      setSubmitError(msg);
    }
  }, [draft, reset, router, setSubmitError, setSubmitting]);

  return (
    <Screen scroll padded contentContainerStyle={styles.body}>
      <View style={styles.header}>
        <Pressable
          onPress={handleBack}
          hitSlop={hitSlop}
          accessibilityRole="button"
          accessibilityLabel="Back"
          testID="back"
        >
          <Ionicons name="chevron-back" size={26} color={colors.text} />
        </Pressable>
        <Text variant="overline" color={colors.textMuted}>
          Assessment
        </Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.progressBlock}>
        <ProgressBar step={step} total={TOTAL_STEPS} />
      </View>

      <Animated.View
        key={step}
        entering={FadeInRight.duration(280)}
        style={styles.stepBlock}
      >
        {step === 1 && <StepBasicInfo onNext={next} />}
        {step === 2 && <StepGoal onNext={next} />}
        {step === 3 && <StepLifestyle onNext={next} />}
        {step === 4 && <StepDietWorkout onNext={next} />}
        {step === 5 && <StepProblems onNext={next} />}
        {step === 6 && <StepStruggle onNext={next} />}
        {step === 7 && (
          <StepReview onSubmit={handleSubmit} onEdit={setStep} />
        )}
      </Animated.View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { paddingBottom: spacing.xxxl },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  headerSpacer: { width: 26 },
  progressBlock: { marginBottom: spacing.xl },
  stepBlock: { flex: 1 },
});
