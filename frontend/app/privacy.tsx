// Privacy Policy — required by Google OAuth and Razorpay.

import { StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import { colors, spacing } from "@/src/theme";

type Section = { heading: string; body: string };

const SECTIONS: Section[] = [
  {
    heading: "1. Who We Are",
    body:
      "Blueprint 90 (\"we\", \"us\", \"our\") is an online fitness platform that " +
      "generates personalised 90-day training and nutrition plans. We are based " +
      "in India. Contact: kaicontentagency@gmail.com",
  },
  {
    heading: "2. Information We Collect",
    body:
      "• Account information: your name and email address, provided via Google OAuth.\n" +
      "• Assessment data: age, gender, height, weight, fitness goal, lifestyle, " +
      "diet preference, workout preference, health conditions, and your self-described " +
      "biggest fitness struggle.\n" +
      "• Payment information: we do not store card details. Payments are processed " +
      "entirely by Razorpay. We store only the payment status and Razorpay order/payment IDs.\n" +
      "• Usage data: standard server logs (IP address, browser/device, timestamps).",
  },
  {
    heading: "3. How We Use Your Information",
    body:
      "• To create and display your personalised 90-day blueprint.\n" +
      "• To process your payment and verify access to your blueprint.\n" +
      "• To send transactional emails (e.g. receipt, support replies).\n" +
      "• To improve the product (aggregated, anonymised analytics only).\n" +
      "We do not sell, rent, or share your personal data with third parties " +
      "for marketing purposes.",
  },
  {
    heading: "4. Third-Party Services",
    body:
      "• Google OAuth — used for sign-in. Governed by Google's Privacy Policy.\n" +
      "• Razorpay — used for payment processing. Governed by Razorpay's Privacy Policy.\n" +
      "• MongoDB Atlas — used for data storage on servers located in Mumbai, India.\n" +
      "Each third party handles your data under their own terms.",
  },
  {
    heading: "5. Data Retention",
    body:
      "Your account and blueprint data is retained for as long as your account is " +
      "active. You may request deletion at any time by emailing kaicontentagency@gmail.com. " +
      "We will delete your data within 30 days of a verified request.",
  },
  {
    heading: "6. Security",
    body:
      "We use HTTPS for all data in transit. Passwords are not stored — " +
      "authentication is handled entirely by Google. Session tokens are stored " +
      "securely and expire automatically.",
  },
  {
    heading: "7. Your Rights",
    body:
      "You have the right to access, correct, or delete your personal data. " +
      "To exercise these rights, email kaicontentagency@gmail.com with the subject " +
      "line \"Data Request\". We will respond within 30 days.",
  },
  {
    heading: "8. Cookies",
    body:
      "The web application uses sessionStorage to temporarily hold OAuth state " +
      "during sign-in. We do not use third-party tracking cookies or advertising cookies.",
  },
  {
    heading: "9. Children",
    body:
      "Blueprint 90 is not directed at children under 13. We do not knowingly " +
      "collect data from children. If you believe a child has provided us with " +
      "personal data, please contact kaicontentagency@gmail.com.",
  },
  {
    heading: "10. Changes to This Policy",
    body:
      "We may update this policy from time to time. Material changes will be " +
      "communicated via email or a prominent notice on the app. Continued use " +
      "after the effective date constitutes acceptance.",
  },
  {
    heading: "11. Contact",
    body:
      "For any privacy-related questions: kaicontentagency@gmail.com",
  },
];

export default function PrivacyScreen() {
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
          Privacy Policy
        </Text>
        <Text variant="caption" color={colors.textDim} style={styles.date}>
          Last updated: 26 June 2026
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.intro}>
          This policy explains how Blueprint 90 collects, uses, and protects your
          personal information when you use our service.
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
