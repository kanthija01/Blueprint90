// Step 1 — Basic info: age, gender, height, weight.
// Uses react-hook-form for field-level validation, then commits to the
// Zustand store on submit.

import { useForm, Controller } from "react-hook-form";
import { StyleSheet, View } from "react-native";

import { Button, Chip, Input, Text } from "@/src/components";
import {
  AGE_MAX,
  AGE_MIN,
  GENDERS,
  GENDER_LABELS,
  HEIGHT_MAX,
  HEIGHT_MIN,
  WEIGHT_MAX,
  WEIGHT_MIN,
} from "@/src/lib/constants";
import type { Gender } from "@/src/lib/constants";
import { useAssessmentStore } from "@/src/stores/assessment";
import { colors, spacing } from "@/src/theme";

type FormShape = {
  age: string;
  height_cm: string;
  weight_kg: string;
  gender: Gender | "";
};

export function StepBasicInfo({ onNext }: { onNext: () => void }) {
  const draft = useAssessmentStore((s) => s.draft);
  const patch = useAssessmentStore((s) => s.patch);

  const {
    control,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormShape>({
    mode: "onChange",
    defaultValues: {
      age: draft.age != null ? String(draft.age) : "",
      height_cm: draft.height_cm != null ? String(draft.height_cm) : "",
      weight_kg: draft.weight_kg != null ? String(draft.weight_kg) : "",
      gender: draft.gender ?? "",
    },
  });

  const onSubmit = (data: FormShape) => {
    patch({
      age: Number(data.age),
      height_cm: Number(data.height_cm),
      weight_kg: Number(data.weight_kg),
      gender: data.gender || null,
    });
    onNext();
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerBlock}>
        <Text variant="overline" color={colors.primary}>
          About you
        </Text>
        <Text variant="h1" style={styles.title}>
          Let&apos;s start with the basics.
        </Text>
        <Text variant="body" color={colors.textMuted}>
          Your blueprint is calibrated to your body. Honest answers, better fit.
        </Text>
      </View>

      <Controller
        control={control}
        name="age"
        rules={{
          required: "Required",
          validate: (v) => {
            const n = Number(v);
            if (!Number.isFinite(n)) return "Numbers only";
            if (n < AGE_MIN || n > AGE_MAX)
              return `Between ${AGE_MIN} and ${AGE_MAX}`;
            return true;
          },
        }}
        render={({ field: { onChange, value, onBlur } }) => (
          <Input
            testID="input-age"
            label="Age"
            keyboardType="number-pad"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            placeholder="e.g. 28"
            error={errors.age?.message}
            returnKeyType="next"
          />
        )}
      />

      <Controller
        control={control}
        name="gender"
        rules={{ required: "Pick one" }}
        render={({ field: { onChange, value } }) => (
          <View style={styles.field}>
            <Text variant="overline" color={colors.textMuted} style={styles.label}>
              Gender
            </Text>
            <View style={styles.chipsRow}>
              {GENDERS.map((g) => (
                <View key={g} style={styles.chipCell}>
                  <Chip
                    testID={`gender-${g}`}
                    label={GENDER_LABELS[g]}
                    selected={value === g}
                    onPress={() => onChange(g)}
                  />
                </View>
              ))}
            </View>
            {errors.gender ? (
              <Text variant="caption" color={colors.danger}>
                {errors.gender.message}
              </Text>
            ) : null}
          </View>
        )}
      />

      <Controller
        control={control}
        name="height_cm"
        rules={{
          required: "Required",
          validate: (v) => {
            const n = Number(v);
            if (!Number.isFinite(n)) return "Numbers only";
            if (n < HEIGHT_MIN || n > HEIGHT_MAX)
              return `Between ${HEIGHT_MIN} and ${HEIGHT_MAX}`;
            return true;
          },
        }}
        render={({ field: { onChange, value, onBlur } }) => (
          <Input
            testID="input-height"
            label="Height (cm)"
            keyboardType="decimal-pad"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            placeholder="e.g. 165"
            error={errors.height_cm?.message}
          />
        )}
      />

      <Controller
        control={control}
        name="weight_kg"
        rules={{
          required: "Required",
          validate: (v) => {
            const n = Number(v);
            if (!Number.isFinite(n)) return "Numbers only";
            if (n < WEIGHT_MIN || n > WEIGHT_MAX)
              return `Between ${WEIGHT_MIN} and ${WEIGHT_MAX}`;
            return true;
          },
        }}
        render={({ field: { onChange, value, onBlur } }) => (
          <Input
            testID="input-weight"
            label="Weight (kg)"
            keyboardType="decimal-pad"
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            placeholder="e.g. 65"
            error={errors.weight_kg?.message}
          />
        )}
      />

      <View style={styles.cta}>
        <Button
          testID="step-next"
          label="Continue"
          fullWidth
          onPress={handleSubmit(onSubmit)}
          disabled={!isValid}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.lg },
  headerBlock: { gap: spacing.sm, marginBottom: spacing.md },
  title: { marginTop: spacing.xs },
  field: { gap: spacing.sm },
  label: { marginBottom: spacing.xs },
  chipsRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  chipCell: { flexGrow: 1, flexBasis: "30%" },
  cta: { marginTop: spacing.xl },
});
