// Contact page — required by Razorpay for live account activation.

import { Linking, StyleSheet, View } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { Button, Screen, Text } from "@/src/components";
import { colors, spacing } from "@/src/theme";

type ContactRow = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  value: string;
  onPress: () => void;
};

export default function ContactScreen() {
  const router = useRouter();

  const rows: ContactRow[] = [
    {
      icon: "mail-outline",
      label: "Email",
      value: "kaicontentagency@gmail.com",
      onPress: () => Linking.openURL("mailto:kaicontentagency@gmail.com"),
    },
    {
      icon: "globe-outline",
      label: "Website",
      value: "blueprint90.in",
      onPress: () => Linking.openURL("https://blueprint90.in"),
    },
  ];

  return (
    <Screen scroll padded contentContainerStyle={styles.container}>
      {/* Back */}
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

      {/* Header */}
      <View style={styles.header}>
        <Text variant="overline" color={colors.primary}>
          Get in touch
        </Text>
        <Text variant="h1" style={styles.title}>
          Contact Us
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.subtitle}>
          Have a question about your blueprint, payment, or account? We typically
          respond within one business day.
        </Text>
      </View>

      {/* Contact rows */}
      <View style={styles.rows}>
        {rows.map((row) => (
          <View key={row.label} style={styles.card}>
            <View style={styles.iconWrap}>
              <Ionicons name={row.icon} size={22} color={colors.primary} />
            </View>
            <View style={styles.rowText}>
              <Text variant="overline" color={colors.textMuted}>
                {row.label}
              </Text>
              <Text
                variant="bodyStrong"
                color={colors.text}
                onPress={row.onPress}
                style={styles.link}
              >
                {row.value}
              </Text>
            </View>
          </View>
        ))}
      </View>

      {/* Business details */}
      <View style={styles.businessBlock}>
        <Text variant="overline" color={colors.textMuted}>
          Business Details
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.businessLine}>
          Blueprint 90
        </Text>
        <Text variant="body" color={colors.textMuted} style={styles.businessLine}>
          India
        </Text>
        <Text variant="caption" color={colors.textDim} style={styles.businessLine}>
          GST registration: Not yet applicable (under threshold)
        </Text>
      </View>

      {/* Response note */}
      <View style={styles.note}>
        <Text variant="caption" color={colors.textDim} align="center">
          For payment disputes or refund requests, include your registered email
          address and order ID in your message.
        </Text>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingBottom: spacing.huge,
  },
  backRow: {
    marginBottom: spacing.md,
    alignSelf: "flex-start",
    marginLeft: -spacing.md,
  },
  header: {
    gap: spacing.sm,
    marginBottom: spacing.xxl,
  },
  title: {
    marginTop: spacing.xs,
  },
  subtitle: {
    marginTop: spacing.xs,
    maxWidth: 540,
  },
  rows: {
    gap: spacing.md,
    marginBottom: spacing.xxl,
  },
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.lg,
    backgroundColor: colors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  iconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primaryMuted,
    alignItems: "center",
    justifyContent: "center",
  },
  rowText: {
    flex: 1,
    gap: spacing.xs,
  },
  link: {
    textDecorationLine: "underline",
  },
  businessBlock: {
    gap: spacing.sm,
    paddingTop: spacing.xl,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
    marginBottom: spacing.xl,
  },
  businessLine: {
    marginTop: spacing.xs,
  },
  note: {
    paddingTop: spacing.lg,
  },
});
