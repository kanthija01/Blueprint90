// Terms & Conditions — required by Razorpay for live account activation.

import { StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import { colors, spacing } from "@/src/theme";

type Section = { heading: string; body: string };

const SECTIONS: Section[] = [
  {
    heading: "1. Acceptance of Terms",
    body:
      "By accessing or using Blueprint 90 (the \"Service\"), you agree to be bound " +
      "by these Terms & Conditions. If you do not agree, please do not use the Service. " +
      "These terms constitute a legally binding agreement between you and Blueprint 90.",
  },
  {
    heading: "2. Description of Service",
    body:
      "Blueprint 90 is an online platform that generates personalised 90-day fitness " +
      "blueprints covering training, nutrition, and psychology. The blueprints are " +
      "assembled deterministically from verified content modules based on your " +
      "assessment answers. The Service does not provide medical advice, and the " +
      "content is not a substitute for professional medical, dietary, or fitness guidance.",
  },
  {
    heading: "3. Eligibility",
    body:
      "You must be at least 13 years old to use the Service. By using the Service " +
      "you confirm that you meet this requirement and that all information you provide " +
      "is accurate and complete.",
  },
  {
    heading: "4. Account",
    body:
      "Access to the Service requires a Google account. You are responsible for " +
      "maintaining the confidentiality of your account and for all activities that " +
      "occur under it. Notify us immediately at kaicontentagency@gmail.com if you " +
      "suspect unauthorised access.",
  },
  {
    heading: "5. Payment",
    body:
      "Access to your generated blueprint requires a one-time payment of ₹499 (INR). " +
      "Payments are processed securely by Razorpay. By making a payment you authorise " +
      "Blueprint 90 to charge the stated amount. All prices are inclusive of applicable " +
      "taxes unless stated otherwise. The payment is for lifetime access to that specific " +
      "blueprint.",
  },
  {
    heading: "6. Refunds & Cancellations",
    body:
      "Please refer to our Refund & Cancellation Policy for full details. In summary: " +
      "because blueprints are digital goods generated immediately after payment, " +
      "we do not offer refunds once the blueprint has been generated and delivered. " +
      "Technical issues or billing errors may be eligible for a refund — contact " +
      "kaicontentagency@gmail.com within 7 days.",
  },
  {
    heading: "7. Intellectual Property",
    body:
      "All content, design, and code on the Service are owned by Blueprint 90 or its " +
      "licensors and are protected by copyright. Your blueprint is for your personal, " +
      "non-commercial use only. You may not reproduce, distribute, or sell any part " +
      "of the Service without prior written permission.",
  },
  {
    heading: "8. Health Disclaimer",
    body:
      "The fitness and nutrition information provided in your blueprint is for " +
      "informational purposes only. Always consult a qualified physician or dietitian " +
      "before starting any new exercise or diet programme, especially if you have " +
      "a pre-existing medical condition. Blueprint 90 accepts no liability for any " +
      "injury or adverse health outcomes arising from following the content in your blueprint.",
  },
  {
    heading: "9. Limitation of Liability",
    body:
      "To the fullest extent permitted by law, Blueprint 90 and its affiliates shall " +
      "not be liable for any indirect, incidental, special, or consequential damages " +
      "arising from your use of the Service. Our total liability for any claim shall " +
      "not exceed the amount you paid for the relevant blueprint.",
  },
  {
    heading: "10. Governing Law",
    body:
      "These Terms are governed by the laws of India. Any disputes shall be subject " +
      "to the exclusive jurisdiction of the courts in India.",
  },
  {
    heading: "11. Changes to Terms",
    body:
      "We reserve the right to update these Terms at any time. Material changes will " +
      "be communicated via email or an in-app notice. Continued use of the Service " +
      "after the updated Terms take effect constitutes your acceptance.",
  },
  {
    heading: "12. Contact",
    body:
      "For any questions regarding these Terms: kaicontentagency@gmail.com",
  },
];

export default function TermsScreen() {
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
          Terms &amp; Conditions
        </Text>
        <Text variant="caption" color={colors.textDim} style={styles.date}>
          Last updated: 26 June 2026
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.intro}>
          Please read these Terms &amp; Conditions carefully before using Blueprint 90.
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
  sections: { gap: spacing.xl },
  section: { gap: spacing.sm },
  sectionHeading: { color: colors.text },
  sectionBody: { lineHeight: 26 },
});
