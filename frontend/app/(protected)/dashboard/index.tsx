// Dashboard — shows the signed-in user's blueprints and a CTA to start a new one.

import { useCallback, useEffect, useState } from "react";
import {
  RefreshControl,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import { useRouter, useFocusEffect } from "expo-router";
import Animated, { FadeIn } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";

import { Button, Card, Screen, Text } from "@/src/components";
import { listBlueprints } from "@/src/api/blueprints";
import type { BlueprintListItem } from "@/src/api/blueprints";
import { useAssessmentStore } from "@/src/stores/assessment";
import { useAuthStore } from "@/src/stores/auth";
import { colors, radius, spacing } from "@/src/theme";

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

function prettyGoal(goal: string): string {
  return goal.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function DashboardScreen() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const resetAssessment = useAssessmentStore((s) => s.reset);

  const [items, setItems] = useState<BlueprintListItem[] | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const data = await listBlueprints();
      setItems(data);
    } catch (e) {
      setError((e as Error).message);
      setItems((prev) => prev ?? []);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useFocusEffect(
    useCallback(() => {
      void load();
    }, [load]),
  );

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  const startNew = async () => {
    await resetAssessment();
    router.push("/assessment");
  };

  return (
    <Screen padded={false}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        }
      >
        <Animated.View entering={FadeIn.duration(400)} style={styles.header}>
          <Text variant="overline" color={colors.primary}>
            DASHBOARD
          </Text>
          <Text variant="h1" style={styles.title}>
            {user?.name ? `Welcome, ${user.name.split(" ")[0]}.` : "Welcome."}
          </Text>
          <Text variant="body" color={colors.textMuted}>
            {user?.email}
          </Text>
        </Animated.View>

        <View style={styles.ctaBlock}>
          <Button
            testID="new-blueprint"
            label="New Blueprint"
            fullWidth
            onPress={startNew}
            iconLeft={
              <Ionicons name="add" size={20} color={colors.textOnPrimary} />
            }
          />
        </View>

        {error ? (
          <Text variant="caption" color={colors.danger} style={styles.error}>
            {error}
          </Text>
        ) : null}

        <View style={styles.listHeader}>
          <Text variant="overline" color={colors.textMuted}>
            Your Blueprints
          </Text>
        </View>

        {items === null ? (
          <Text variant="caption" color={colors.textMuted}>
            Loading…
          </Text>
        ) : items.length === 0 ? (
          <Card>
            <View style={styles.empty}>
              <Text variant="h3">No blueprints yet.</Text>
              <Text variant="body" color={colors.textMuted}>
                Generate your first 90-day plan in under 2 minutes.
              </Text>
            </View>
          </Card>
        ) : (
          <View style={styles.list}>
            {items.map((item) => (
              <Card
                key={item.blueprint_id}
                testID={`blueprint-${item.blueprint_id}`}
                onPress={() =>
                  router.push(`/dashboard/${item.blueprint_id}` as never)
                }
              >
                <View style={styles.itemRow}>
                  <View style={styles.itemMain}>
                    <Text variant="overline" color={colors.primary}>
                      {prettyGoal(item.goal)}
                    </Text>
                    <Text variant="h3" style={styles.itemTitle}>
                      {item.primary_module_display_name}
                    </Text>
                    <Text variant="caption" color={colors.textMuted}>
                      {item.module_count} modules · {formatDate(item.created_at)}
                    </Text>
                  </View>
                  <View style={styles.badge}>
                    <Text variant="overline" color={colors.textOnPrimary}>
                      90D
                    </Text>
                  </View>
                </View>
              </Card>
            ))}
          </View>
        )}

        <View style={styles.footer}>
          <Button
            testID="logout"
            label="Sign out"
            variant="ghost"
            onPress={async () => {
              await logout();
              router.replace("/");
            }}
          />
        </View>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  scroll: {
    padding: spacing.xl,
    paddingBottom: spacing.xxxl,
  },
  header: { gap: spacing.sm, marginBottom: spacing.xl },
  title: { marginTop: spacing.xs },
  ctaBlock: { marginBottom: spacing.xxl },
  listHeader: { marginBottom: spacing.md },
  list: { gap: spacing.md },
  itemRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  itemMain: { flex: 1, gap: spacing.xs },
  itemTitle: { marginVertical: spacing.xs },
  badge: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.pill,
  },
  empty: { gap: spacing.sm, alignItems: "flex-start" },
  error: { marginBottom: spacing.md },
  footer: { marginTop: spacing.xxl, alignItems: "center" },
});
