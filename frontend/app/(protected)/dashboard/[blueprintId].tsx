// Blueprint detail / preview. Pure visual renderer over the cached
// assembled_json from GET /api/blueprints/{id}. Never re-runs assembly.

import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import Animated, { FadeInUp } from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";

import {
  BlueprintSectionCard,
  BulletList,
  Button,
  Card,
  FallbackBadge,
  ModuleBadge,
  Screen,
  Text,
  TrackerTable,
  WeeklyCard,
} from "@/src/components";
import type { BulletRow } from "@/src/components";
import {
  getBlueprint,
  type AssembledBlueprint,
} from "@/src/api/blueprints";
import { ApiError } from "@/src/api/client";
import { createOrder, verifyPayment } from "@/src/api/payments";
import { loadRazorpayScript, openRazorpayCheckout } from "@/src/lib/razorpay-checkout";
import { useBlueprintPdfDownload } from "@/src/lib/use-blueprint-pdf-download";
import { colors, hitSlop, radius, spacing } from "@/src/theme";

function prettyGoal(goal: string): string {
  return goal.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
function prettySlug(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export default function BlueprintDetailScreen() {
  const router = useRouter();
  const { blueprintId } = useLocalSearchParams<{ blueprintId: string }>();

  const [data, setData] = useState<AssembledBlueprint | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentRequired, setPaymentRequired] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [retryStatus, setRetryStatus] = useState<string | null>(null);

  const {
    download: downloadPdf,
    status: pdfStatus,
    error: pdfError,
    busy: pdfBusy,
  } = useBlueprintPdfDownload(blueprintId);

  const load = useCallback(async () => {
    if (!blueprintId) {
      setError("No blueprint id in route.");
      return;
    }
    setError(null);
    setPaymentRequired(false);
    try {
      const bp = await getBlueprint(blueprintId);
      setData(bp);
    } catch (e) {
      if (e instanceof ApiError && e.status === 402) {
        setPaymentRequired(true);
      } else {
        const msg =
          e instanceof ApiError
            ? e.status === 404
              ? "Blueprint not found."
              : e.message
            : (e as Error).message;
        setError(msg);
      }
    }
  }, [blueprintId]);

  useEffect(() => {
    setLoading(true);
    void load().finally(() => setLoading(false));
  }, [load]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  // Complete payment for a blueprint that was previously unpaid.
  // Uses POST /api/payments/create-order (which now expires stuck 'created'
  // records) then runs the same verify flow as the new assessment flow.
  const handleRetryPayment = useCallback(async () => {
    if (!blueprintId) return;

    if (Platform.OS !== "web") {
      Alert.alert(
        "Web only",
        "Payment is available on the website. Please open Blueprint90 in a browser.",
      );
      return;
    }

    setRetrying(true);
    setRetryStatus("Preparing payment…");

    try {
      console.log("[blueprint] retry payment: creating order for", blueprintId);
      await loadRazorpayScript();
      const order = await createOrder(blueprintId);
      console.log("[blueprint] retry payment: order created", order.payment_id);

      setRetryStatus(null);
      const rzResult = await openRazorpayCheckout(order);
      console.log("[blueprint] retry payment: checkout success", rzResult.razorpay_payment_id);

      setRetryStatus("Verifying payment…");
      await verifyPayment({
        payment_id: order.payment_id,
        razorpay_payment_id: rzResult.razorpay_payment_id,
        razorpay_order_id: rzResult.razorpay_order_id,
        razorpay_signature: rzResult.razorpay_signature,
      });
      console.log("[blueprint] retry payment: verified — reloading blueprint");

      setRetryStatus("Payment confirmed. Loading your blueprint…");
      // Reload the blueprint — it should now be accessible.
      await load();
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message || `Server error (${e.status})`
          : (e as Error).message;
      console.log("[blueprint] retry payment error:", msg);
      Alert.alert("Payment not completed", msg || "Unknown error.");
    } finally {
      setRetrying(false);
      setRetryStatus(null);
    }
  }, [blueprintId, load]);

  if (loading && !data) {
    return (
      <Screen testID="blueprint-loading">
        <View style={styles.centered}>
          <ActivityIndicator size="small" color={colors.primary} />
          <Text variant="caption" color={colors.textMuted} style={styles.loadingLabel}>
            Loading your blueprint…
          </Text>
        </View>
      </Screen>
    );
  }

  // Payment required — show a retry flow, not a dead-end.
  if (paymentRequired && !data) {
    return (
      <Screen testID="blueprint-payment-required">
        <View style={styles.errorPad}>
          <Text variant="h3">Complete your payment</Text>
          <Text variant="body" color={colors.textMuted} style={styles.errorMsg}>
            This blueprint is ready — your payment just needs to be confirmed.
          </Text>

          {retrying && retryStatus ? (
            <View style={styles.retryStatus}>
              <ActivityIndicator size="small" color={colors.primary} />
              <Text variant="caption" color={colors.textMuted} style={styles.retryLabel}>
                {retryStatus}
              </Text>
            </View>
          ) : null}

          <Button
            testID="retry-payment"
            label={retrying ? "Processing…" : "Complete Payment"}
            fullWidth
            loading={retrying}
            onPress={() => void handleRetryPayment()}
          />
          <Button
            label="Back to dashboard"
            variant="ghost"
            onPress={() => router.replace("/dashboard")}
          />
        </View>
      </Screen>
    );
  }

  if (error && !data) {
    return (
      <Screen testID="blueprint-error">
        <View style={styles.errorPad}>
          <Text variant="h3">Couldn&apos;t load this blueprint.</Text>
          <Text variant="body" color={colors.textMuted} style={styles.errorMsg}>
            {error}
          </Text>
          <Button
            label="Try again"
            onPress={() => {
              setLoading(true);
              void load().finally(() => setLoading(false));
            }}
          />
          <Button
            label="Back to dashboard"
            variant="ghost"
            onPress={() => router.replace("/dashboard")}
          />
        </View>
      </Screen>
    );
  }

  if (!data) {
    return null;
  }

  const bp = data;
  const cover = bp.cover_page;
  const meta = bp.meta;

  const failedRows: BulletRow[] = bp.why_previous_attempts_failed.map((f) => ({
    label: "TRIED",
    primary: f.solution_tried,
    secondary: f.why_it_failed,
    source: prettySlug(f.source_module),
  }));
  const rootCauseRows: BulletRow[] = bp.root_causes.map((r) => ({
    label: r.category.toUpperCase(),
    primary: r.root_cause,
    source: prettySlug(r.source_module),
  }));
  const targetRows: BulletRow[] = bp.nutrition_strategy.targets.map((t) => ({
    primary: t.field_name,
    secondary: t.field_value,
  }));
  const foodRows: BulletRow[] = bp.nutrition_strategy.foods.map((f) => ({
    label: f.food_type.toUpperCase(),
    primary: f.options,
  }));
  const avoidRows: BulletRow[] = bp.nutrition_strategy.foods_to_avoid.map((f) => ({
    label: "AVOID",
    primary: f.food_type,
    secondary: f.why_avoid,
  }));
  const mealRows: BulletRow[] = bp.nutrition_strategy.meal_ideas.map((m) => ({
    label: m.meal_time.toUpperCase(),
    primary: m.meal_option,
  }));
  const habitRows: BulletRow[] = bp.habit_system.map((h) => ({
    primary: h.habit_name,
    secondary: [h.daily_target, h.how_to_track].filter(Boolean).join(" · "),
    source: prettySlug(h.source_module),
  }));
  const thoughtRows: BulletRow[] = bp.psychology_system.common_thoughts.map(
    (t) => ({
      label: "THOUGHT",
      primary: t.common_thought,
      secondary: [t.emotional_impact, t.solution]
        .filter(Boolean)
        .join("\n→ "),
      source: prettySlug(t.source_module),
    }),
  );
  const techniqueRows: BulletRow[] = bp.psychology_system.techniques.map(
    (t) => ({
      label: "TECHNIQUE",
      primary: t.technique,
      secondary: t.how_to_apply,
      source: prettySlug(t.source_module),
    }),
  );
  const faqRows: BulletRow[] = bp.faqs.map((f) => ({
    label: "Q",
    primary: f.question,
    secondary: f.answer,
    source: prettySlug(f.source_module),
  }));
  const plateauRows: BulletRow[] = bp.plateau_playbook.map((p) => ({
    label: p.trigger_condition.toUpperCase(),
    primary: p.action_to_take,
    secondary: p.timeframe,
    source: prettySlug(p.source_module),
  }));
  const nutritionEmpty =
    targetRows.length === 0 &&
    foodRows.length === 0 &&
    avoidRows.length === 0 &&
    mealRows.length === 0;

  return (
    <Screen padded={false} testID="blueprint-detail">
      <View style={styles.header}>
        <Pressable
          hitSlop={hitSlop}
          onPress={() => router.back()}
          accessibilityRole="button"
          accessibilityLabel="Back"
          testID="back"
        >
          <Ionicons name="chevron-back" size={26} color={colors.text} />
        </Pressable>
        <Text variant="overline" color={colors.textMuted}>
          Blueprint
        </Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        }
      >
        {/* ---- A. Cover ---- */}
        <Animated.View
          entering={FadeInUp.duration(400)}
          style={styles.coverWrap}
        >
          <Card elevated>
            <Text variant="overline" color={colors.primary}>
              YOUR 90-DAY BLUEPRINT
            </Text>
            <Text variant="display" style={styles.coverGoal}>
              {prettyGoal(cover.goal)}
            </Text>
            <Text variant="caption" color={colors.textMuted}>
              Generated {formatDate(cover.generated_at)} · {cover.duration_days} days
            </Text>

            {cover.biggest_struggle ? (
              <View style={styles.quote}>
                <Text variant="overline" color={colors.textMuted}>
                  IN YOUR WORDS
                </Text>
                <Text variant="body" style={styles.quoteText}>
                  “{cover.biggest_struggle}”
                </Text>
              </View>
            ) : null}

            <View style={styles.badges}>
              {meta.modules_used.map((m) => (
                <View
                  key={m.slug}
                  style={styles.badgeWrap}
                  testID={`module-badge-${m.slug}`}
                >
                  <ModuleBadge
                    label={m.display_name}
                    primary={m.slug === meta.primary_module_slug}
                  />
                  {m.is_fallback ? (
                    <FallbackBadge
                      note={m.fallback_note}
                      testID={`fallback-${m.slug}`}
                    />
                  ) : null}
                </View>
              ))}
            </View>
          </Card>
        </Animated.View>

        {/* ---- B. Why previous attempts failed ---- */}
        <BlueprintSectionCard
          letter="B"
          eyebrow="WHY PREVIOUS ATTEMPTS FAILED"
          title="What didn't work, and why."
          delay={60}
          empty={failedRows.length === 0}
          emptyLabel="No prior attempts logged."
          testID="section-why-failed"
        >
          <BulletList rows={failedRows} testID="list-why-failed" />
        </BlueprintSectionCard>

        {/* ---- C. Root causes ---- */}
        <BlueprintSectionCard
          letter="C"
          eyebrow="ROOT CAUSES"
          title="What's actually driving this."
          delay={120}
          empty={rootCauseRows.length === 0}
          testID="section-root-causes"
        >
          <BulletList rows={rootCauseRows} testID="list-root-causes" />
        </BlueprintSectionCard>

        {/* ---- D. Nutrition ---- */}
        <BlueprintSectionCard
          letter="D"
          eyebrow="NUTRITION STRATEGY"
          title={`Engineered for ${prettySlug(bp.nutrition_strategy.diet)}.`}
          subtitle={`Primary module: ${prettySlug(bp.nutrition_strategy.source_module)}`}
          delay={180}
          empty={nutritionEmpty}
          emptyLabel="The primary module for this blueprint doesn't define nutrition targets or meal guidance."
          testID="section-nutrition"
        >
          {targetRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                TARGETS
              </Text>
              <BulletList rows={targetRows} testID="list-targets" />
            </View>
          ) : null}
          {foodRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                FOODS
              </Text>
              <BulletList rows={foodRows} testID="list-foods" />
            </View>
          ) : null}
          {avoidRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                FOODS TO AVOID
              </Text>
              <BulletList rows={avoidRows} testID="list-avoid" />
            </View>
          ) : null}
          {mealRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                MEAL IDEAS
              </Text>
              <BulletList rows={mealRows} testID="list-meals" />
            </View>
          ) : null}
        </BlueprintSectionCard>

        {/* ---- E. Workout ---- */}
        <BlueprintSectionCard
          letter="E"
          eyebrow="WORKOUT PLAN"
          title={
            bp.workout_plan
              ? `${bp.workout_plan.time_minutes} min · ${prettySlug(bp.workout_plan.location)}`
              : "No workout routine"
          }
          subtitle={bp.workout_plan?.routine_label ?? undefined}
          delay={240}
          empty={!bp.workout_plan}
          emptyLabel="The primary module for this blueprint doesn't define a workout routine. See the standalone module if applicable."
          testID="section-workout"
        >
          {bp.workout_plan ? (
            <>
              {bp.workout_plan.exercises.length > 0 ? (
                <View style={styles.subBlock}>
                  <Text variant="overline" color={colors.textMuted}>
                    EXERCISES
                  </Text>
                  <BulletList
                    testID="list-exercises"
                    rows={bp.workout_plan.exercises.map((e) => ({
                      primary: e.exercise_name,
                      secondary: [
                        e.sets && `${e.sets} sets`,
                        e.reps_or_time,
                        e.rest && `rest ${e.rest}`,
                      ]
                        .filter(Boolean)
                        .join(" · "),
                    }))}
                  />
                </View>
              ) : null}
              {bp.workout_plan.constraint_swaps.length > 0 ? (
                <View style={styles.subBlock}>
                  <Text variant="overline" color={colors.textMuted}>
                    CONSTRAINT SWAPS
                  </Text>
                  <BulletList
                    testID="list-constraint-swaps"
                    rows={bp.workout_plan.constraint_swaps.map((c) => ({
                      label: c.constraint_name.toUpperCase(),
                      primary: c.solution,
                      secondary: c.approach,
                    }))}
                  />
                </View>
              ) : null}
              {bp.workout_plan.exercises_to_avoid.length > 0 ? (
                <View style={styles.subBlock}>
                  <Text variant="overline" color={colors.textMuted}>
                    AVOID
                  </Text>
                  <BulletList
                    testID="list-exercise-avoid"
                    rows={bp.workout_plan.exercises_to_avoid.map((e) => ({
                      label: "AVOID",
                      primary: e.exercise_type,
                      secondary: e.why_avoid,
                    }))}
                  />
                </View>
              ) : null}
            </>
          ) : null}
        </BlueprintSectionCard>

        {/* ---- F. Habits ---- */}
        <BlueprintSectionCard
          letter="F"
          eyebrow="HABIT SYSTEM"
          title="The daily moves that compound."
          delay={300}
          empty={habitRows.length === 0}
          testID="section-habits"
        >
          <BulletList rows={habitRows} testID="list-habits" />
        </BlueprintSectionCard>

        {/* ---- G. Psychology ---- */}
        <BlueprintSectionCard
          letter="G"
          eyebrow="PSYCHOLOGY SYSTEM"
          title="What you'll think, and what to do."
          delay={360}
          empty={
            thoughtRows.length === 0 && techniqueRows.length === 0
          }
          testID="section-psychology"
        >
          {thoughtRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                COMMON THOUGHTS
              </Text>
              <BulletList rows={thoughtRows} testID="list-thoughts" />
            </View>
          ) : null}
          {techniqueRows.length > 0 ? (
            <View style={styles.subBlock}>
              <Text variant="overline" color={colors.textMuted}>
                TECHNIQUES
              </Text>
              <BulletList rows={techniqueRows} testID="list-techniques" />
            </View>
          ) : null}
        </BlueprintSectionCard>

        {/* ---- H. FAQs ---- */}
        <BlueprintSectionCard
          letter="H"
          eyebrow="FAQS"
          title="Quick answers to common questions."
          delay={420}
          empty={faqRows.length === 0}
          testID="section-faqs"
        >
          <BulletList rows={faqRows} testID="list-faqs" />
        </BlueprintSectionCard>

        {/* ---- I. Plateau playbook ---- */}
        <BlueprintSectionCard
          letter="I"
          eyebrow="PLATEAU PLAYBOOK"
          title="When progress stalls, do this."
          delay={450}
          empty={plateauRows.length === 0}
          emptyLabel="No plateau actions defined for this module."
          testID="section-plateau"
        >
          <BulletList rows={plateauRows} testID="list-plateau" />
        </BlueprintSectionCard>

        {/* ---- J. Weekly milestones ---- */}
        <BlueprintSectionCard
          letter="J"
          eyebrow="WEEKLY MILESTONES"
          title="The 12-week structure."
          subtitle="Weeks 1, 4, 8 and 12 are review weeks."
          delay={480}
          empty={bp.weekly_milestones.length === 0}
          testID="section-milestones"
        >
          <View style={styles.weeklyGrid} testID="list-milestones">
            {bp.weekly_milestones.map((m) => (
              <WeeklyCard
                key={m.week}
                week={m.week}
                focus={m.focus}
                checklist={m.checklist_items}
                testID={`milestone-${m.week}`}
              />
            ))}
          </View>
        </BlueprintSectionCard>

        {/* ---- K. Progress tracker ---- */}
        <BlueprintSectionCard
          letter="K"
          eyebrow="PROGRESS TRACKER"
          title="Track what matters, week over week."
          subtitle="Scroll right to see all metrics."
          delay={540}
          testID="section-tracker"
        >
          <TrackerTable
            columns={bp.progress_tracker.columns}
            weeks={bp.progress_tracker.weeks}
            testID="tracker"
          />
        </BlueprintSectionCard>

        <View style={styles.footer}>
          <Text variant="caption" color={colors.textDim} align="center">
            Deterministically assembled from {meta.modules_used.length} verified
            modules. No AI advice.
          </Text>
          <Button
            testID="download-pdf"
            label="Download PDF (₹499)"
            fullWidth
            loading={pdfBusy}
            onPress={() => void downloadPdf()}
            iconLeft={
              <Ionicons
                name="download-outline"
                size={20}
                color={colors.textOnPrimary}
              />
            }
          />
          {pdfStatus ? (
            <Text variant="caption" color={colors.textMuted} align="center">
              {pdfStatus}
            </Text>
          ) : null}
          {pdfError ? (
            <Text variant="caption" color={colors.danger} align="center">
              {pdfError}
            </Text>
          ) : null}
          <Button
            label="Back to dashboard"
            variant="ghost"
            onPress={() => router.replace("/dashboard")}
          />
        </View>
      </ScrollView>

      {error ? (
        <View style={styles.toast}>
          <Text variant="caption" color={colors.danger}>
            {error} (showing cached copy)
          </Text>
          <Pressable
            onPress={() =>
              Alert.alert("Network error", error ?? "Unknown error")
            }
            hitSlop={hitSlop}
          >
            <Text variant="caption" color={colors.primary}>
              Details
            </Text>
          </Pressable>
        </View>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.sm,
  },
  loadingLabel: { marginTop: spacing.sm },
  errorPad: { flex: 1, justifyContent: "center", gap: spacing.md },
  errorMsg: { marginBottom: spacing.lg },
  retryStatus: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.sm,
  },
  retryLabel: { flex: 1 },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.md,
    paddingBottom: spacing.sm,
  },
  headerSpacer: { width: 26 },
  scroll: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.huge,
  },
  coverWrap: { marginBottom: spacing.lg },
  coverGoal: { marginTop: spacing.xs, color: colors.primary },
  quote: {
    marginTop: spacing.lg,
    padding: spacing.md,
    borderRadius: radius.md,
    backgroundColor: "rgba(255,214,10,0.06)",
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
  },
  quoteText: { marginTop: spacing.xs, fontStyle: "italic" },
  badges: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  badgeWrap: { gap: spacing.xs },
  subBlock: { gap: spacing.sm },
  weeklyGrid: { gap: spacing.sm },
  footer: { gap: spacing.md, marginTop: spacing.lg, alignItems: "center" },
  toast: {
    position: "absolute",
    bottom: spacing.lg,
    left: spacing.lg,
    right: spacing.lg,
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: colors.card,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
});
