// AssessmentDraft -> AssessmentPayload mapping + validators that mirror
// backend Pydantic constraints. Used by the review screen before submit.

import type { AssessmentDraft } from "@/src/stores/assessment";
import {
  AGE_MAX,
  AGE_MIN,
  HEIGHT_MAX,
  HEIGHT_MIN,
  STRUGGLE_MAX_LEN,
  WEIGHT_MAX,
  WEIGHT_MIN,
} from "@/src/lib/constants";
import type { AssessmentPayload } from "@/src/api/assessment";

export function validateStep1(d: AssessmentDraft): string | null {
  if (d.age == null || !Number.isFinite(d.age)) return "Enter your age.";
  if (d.age < AGE_MIN || d.age > AGE_MAX)
    return `Age must be between ${AGE_MIN} and ${AGE_MAX}.`;
  if (!d.gender) return "Select your gender.";
  if (d.height_cm == null || !Number.isFinite(d.height_cm))
    return "Enter your height in cm.";
  if (d.height_cm < HEIGHT_MIN || d.height_cm > HEIGHT_MAX)
    return `Height must be between ${HEIGHT_MIN} and ${HEIGHT_MAX} cm.`;
  if (d.weight_kg == null || !Number.isFinite(d.weight_kg))
    return "Enter your weight in kg.";
  if (d.weight_kg < WEIGHT_MIN || d.weight_kg > WEIGHT_MAX)
    return `Weight must be between ${WEIGHT_MIN} and ${WEIGHT_MAX} kg.`;
  return null;
}
export function validateStep2(d: AssessmentDraft): string | null {
  return d.goal ? null : "Pick a goal.";
}
export function validateStep3(d: AssessmentDraft): string | null {
  return d.lifestyle ? null : "Pick the lifestyle that fits best.";
}
export function validateStep4(d: AssessmentDraft): string | null {
  if (!d.diet) return "Pick your diet.";
  if (!d.workout_preference) return "Choose home or gym.";
  if (!d.time_available_min) return "Pick how much time you have.";
  return null;
}
export function validateStep5(_d: AssessmentDraft): string | null {
  return null; // Problems list is optional.
}
export function validateStep6(d: AssessmentDraft): string | null {
  if (d.biggest_struggle.length > STRUGGLE_MAX_LEN)
    return `Keep it under ${STRUGGLE_MAX_LEN} characters.`;
  return null;
}

export function validateForSubmit(d: AssessmentDraft): string | null {
  return (
    validateStep1(d) ||
    validateStep2(d) ||
    validateStep3(d) ||
    validateStep4(d) ||
    validateStep5(d) ||
    validateStep6(d)
  );
}

/** Convert a fully-valid draft into the API payload. Throws if invalid. */
export function draftToPayload(
  d: AssessmentDraft,
  paymentId: string,
): AssessmentPayload {
  const err = validateForSubmit(d);
  if (err) throw new Error(err);
  return {
    payment_id: paymentId,
    age: d.age!,
    gender: d.gender!,
    height_cm: d.height_cm!,
    weight_kg: d.weight_kg!,
    goal: d.goal!,
    lifestyle: d.lifestyle!,
    diet: d.diet!,
    workout_preference: d.workout_preference!,
    time_available_min: d.time_available_min!,
    problems: d.problems,
    biggest_struggle: d.biggest_struggle.trim(),
  };
}
