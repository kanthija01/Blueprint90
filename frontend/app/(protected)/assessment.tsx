// Multi-step assessment screen.
// New flow:
//   1. User completes 7-step form.
//   2. On "Continue to Payment": Razorpay opens.
//   3. If payment fails/cancelled → nothing generated, user stays on review.
//   4. After payment success, backend webhook confirms status="paid".
//   5. Client polls until payment confirmed, then submits assessment.
//   6. Loading overlay shown during generation.
//   7. Navigate to /dashboard/[blueprintId] on success.

import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  StyleSheet,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { ProgressBar, Screen, Text } from "@/src/components";
import { submitAssessment } from "@/src/api/assessment";
import {
  createPreAssessmentOrder,
  verifyPayment,
  pollPaymentStatus,
} from "@/src/api/payments";
import { draftToPayload } from "@/src/lib/assessment-validation";
import { TOTAL_STEPS, useAssessmentStore } from "@/src/stores/assessment";
import { ApiError } from "@/src/api/client";
import {
  loadRazorpayScript,
  openRazorpayCheckout,
} from "@/src/lib/razorpay-checkout";
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

  // Generating overlay state
  const [generatingStatus, setGeneratingStatus] = useState<string | null>(null);

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
    console.log("[assessment] starting payment-first flow");
    setSubmitError(null);

    if (Platform.OS !== "web") {
      Alert.alert(
        "Web only",
        "Payment is available on the website. Please open Blueprint90 in a browser.",
      );
      return;
    }

    try {
      // Validate draft before opening payment — don't let user pay then fail.
      draftToPayload(draft, "__validate_only__");
    } catch (e) {
      setSubmitError((e as Error).message);
      return;
    }

    setSubmitting(true);

    try {
      // Step 1: create a pre-assessment Razorpay order.
      setGeneratingStatus("Preparing payment…");
      await loadRazorpayScript();
      const order = await createPreAssessmentOrder();

      // Step 2: open Razorpay checkout — resolves with success params,
      // rejects on cancel/fail.
      setGeneratingStatus(null);
      let razorpayResult;
      try {
        razorpayResult = await openRazorpayCheckout(order);
        console.log("[payment] checkout success, razorpay_payment_id:", razorpayResult.razorpay_payment_id);
      } catch (paymentError) {
        // User cancelled or payment failed — do not generate anything.
        setSubmitting(false);
        const msg =
          paymentError instanceof Error
            ? paymentError.message
            : "Payment was not completed.";
        setSubmitError(msg);
        Alert.alert("Payment not completed", msg);
        return;
      }

      // Step 3: verify payment on the backend using the Razorpay callback
      // params. This works in local dev without needing a public webhook URL.
      setGeneratingStatus("Verifying payment…");
      console.log("[payment] calling /api/payments/verify");
      try {
        await verifyPayment({
          payment_id: order.payment_id,
          razorpay_payment_id: razorpayResult.razorpay_payment_id,
          razorpay_order_id: razorpayResult.razorpay_order_id,
          razorpay_signature: razorpayResult.razorpay_signature,
        });
        console.log("[payment] verify succeeded");
      } catch (verifyError) {
        // Verify endpoint failed — fall back to polling in case webhook arrived.
        console.warn("[payment] verify failed, falling back to poll:", verifyError);
        setGeneratingStatus("Confirming payment…");
        await pollPaymentStatus(order.payment_id, setGeneratingStatus);
      }

      // Step 4: submit assessment with the verified payment_id.
      setGeneratingStatus("Generating your blueprint…");
      const payload = draftToPayload(draft, order.payment_id);
      const result = await submitAssessment(payload);

      console.log("[assessment] blueprint generated:", result.blueprint_id);

      setSubmitting(false);
      setGeneratingStatus(null);
      await reset();

      // Navigate directly to the blueprint preview.
      router.replace(`/dashboard/${result.blueprint_id}` as never);
    } catch (e) {
      console.log("[assessment] ERROR:", e);
      setSubmitting(false);
      setGeneratingStatus(null);

      const msg =
        e instanceof ApiError
          ? e.message || `Server error (${e.status})`
          : (e as Error).message;

      setSubmitError(msg);
      Alert.alert("Something went wrong", msg || "Unknown error occurred.");
    }
  }, [draft, reset, router, setSubmitError, setSubmitting]);

  // Full-screen generating overlay — shown while payment is being confirmed
  // and while the blueprint is being assembled on the backend.
  if (generatingStatus !== null) {
    return (
      <Screen>
        <View style={styles.overlay}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text variant="h3" style={styles.overlayTitle}>
            {generatingStatus.includes("blueprint")
              ? "Building your blueprint"
              : "Processing payment"}
          </Text>
          <Text variant="body" color={colors.textMuted} align="center">
            {generatingStatus}
          </Text>
          <Text variant="caption" color={colors.textDim} align="center" style={styles.overlayHint}>
            This takes a few seconds. Don&apos;t close the app.
          </Text>
        </View>
      </Screen>
    );
  }

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

      <View
        key={step}
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
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: {
    paddingBottom: spacing.xxxl,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  headerSpacer: {
    width: 26,
  },
  progressBlock: {
    marginBottom: spacing.xl,
  },
  stepBlock: {
    flexShrink: 0,
  },
  overlay: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.lg,
    paddingHorizontal: spacing.xxl,
  },
  overlayTitle: {
    marginTop: spacing.md,
    textAlign: "center",
  },
  overlayHint: {
    marginTop: spacing.sm,
  },
});
