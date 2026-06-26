// Refund & Cancellation Policy — mandatory for Razorpay live activation.
// Must be clearly visible and linked before the checkout opens.

import { StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import { colors, spacing } from "@/src/theme";

type Section = { heading: string; body: string };

const SECTIONS: Section[] = [
  {
    heading: "1. Nature of the Product",
    body:
      "Blueprint 90 provides personalised digital fitness blueprints. Each blueprint " +
      "is generated uniquely for you based on your assessment data, immediately " +
      "after payment is confirmed. Because the product is a digital good that is " +
      "created and delivered instantly, our refund policy is limited as described below.",
  },
  {
    heading: "2. No Refunds After Delivery",
    body:
      "Once your blueprint has been generated and is visible in your dashboard, " +
      "the purchase is considered complete and no refund will be issued. " +
      "This applies regardless of whether you have read or downloaded the blueprint.",
  },
  {
    heading: "3. Eligible Refund Situations",
    body:
      "A full refund will be issued in the following situations:\n\n" +
      "• You were charged but no blueprint was generated (technical failure).\n" +
      "• You were charged more than once for the same blueprint.\n" +
      "• A verifiable billing error occurred on our side.\n\n" +
      "To request a refund, email kaicontentagency@gmail.com within 7 days of " +
      "the payment date with your registered email address and Razorpay payment ID.",
  },
  {
    heading: "4. Refund Process",
    body:
      "Approved refunds will be processed within 5–7 business days back to the " +
      "original payment method. Razorpay may take an additional 3–5 business days " +
      "to reflect the amount in your account, depending on your bank.",
  },
  {
    heading: "5. Cancellation",
    body:
      "There is no subscription to cancel — Blueprint 90 is a one-time purchase. " +
      "You may close your account at any time by emailing kaicontentagency@gmail.com. " +
      "Account deletion does not entitle you to a refund for previously purchased blueprints.",
  },
  {
    heading: "6. Disputes",
    body:
      "If you have a dispute about a charge, please contact us at " +
      "kaicontentagency@gmail.com before initiating a chargeback with your bank. " +
      "We are committed to resolving issues quickly and fairly.",
  },
  {
    heading: "7. Contact",
    body:
      "For all refund and cancellation requests:\n" +
      "Email: kaicontentagency@gmail.com\n" +
      "Response time: within 1 business day.",
  },
];

export default function RefundScreen() {
  const router = useRouter();

  return (
    <Screen scroll padded contentContainerStyle={styles.container}>
      <View style={styles.backRow}>
        <Button
          label="Back"
          variant="ghost"
          onPress={() => router.back()}
          iconLeft={
            <Ionicons name="chevron-back" size={16} color={colors.textMuted} />
          }
        />
      </View>

      <View style={styles.header}>
        <Text variant="overline" color={colors.primary}>
          Legal
        </Text>
        <Text variant="h1" style={styles.title}>
          Refund &amp; Cancellation Policy
        </Text>
        <Text variant="caption" color={colors.textDim} style={styles.date}>
          Last updated: 26 June 2026
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.intro}>
          This policy describes when and how you can request a refund for a
          Blueprint 90 purchase.
        </Text>
      </View>

      {/* Key summary card */}
      <View style={styles.summaryCard}>
        <Text variant="overline" color={colors.primary}>
          Summary
        </Text>
        <Text variant="body" color={colors.text} style={styles.summaryLine}>
          • One-time payment of ₹499 per blueprint
        </Text>
        <Text variant="body" color={colors.text} style={styles.summaryLine}>
          • No refunds after blueprint is generated and delivered
        </Text>
        <Text variant="body" color={colors.text} style={styles.summaryLine}>
          • Refunds available for billing errors or failed delivery
        </Text>
        <Text variant="body" color={colors.text} style={styles.summaryLine}>
          • Contact support within 7 days of payment
        </Text>
      </View>

      <View style={styles.sections}>
        {SECTIONS.map((s) => (
          <View key={s.heading} style={styles.section}>
            <Text variant="h3" style={styles.sectionHeading}>
              {s.heading}
            </Text>
            <Text variant="body" color={colors.textMuted} style={styles.sectionBody}>
              {s.body}
            </Text>
          </View>
        ))}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: { paddingBottom: spacing.huge },
  backRow: {
    marginBottom: spacing.md,
    alignSelf: "flex-start",
    marginLeft: -spacing.md,
  },
  header: { gap: spacing.sm, marginBottom: spacing.xxl },
  title: { marginTop: spacing.xs },
  date: { marginTop: spacing.xs },
  intro: { marginTop: spacing.sm, maxWidth: 600 },
  summaryCard: {
    backgroundColor: colors.primaryMuted,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.primary,
    padding: spacing.lg,
    gap: spacing.sm,
    marginBottom: spacing.xxl,
  },
  summaryLine: { marginTop: spacing.xs },
  sections: { gap: spacing.xl },
  section: { gap: spacing.sm },
  sectionHeading: { color: colors.text },
  sectionBody: { lineHeight: 26 },
});
