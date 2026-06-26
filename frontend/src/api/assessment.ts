// POST /api/assessments — submits the assessment after payment is confirmed.
// The backend verifies the payment_id is paid before generating the blueprint.

import { apiRequest } from "./client";
import type {
  Diet,
  Gender,
  Goal,
  Lifestyle,
  Problem,
  TimeMinutes,
  WorkoutPreference,
} from "@/src/lib/constants";

export type AssessmentPayload = {
  // Payment verification — must reference a paid pre-assessment payment.
  payment_id: string;
  // Assessment fields
  age: number;
  gender: Gender;
  height_cm: number;
  weight_kg: number;
  goal: Goal;
  lifestyle: Lifestyle;
  diet: Diet;
  workout_preference: WorkoutPreference;
  time_available_min: TimeMinutes;
  problems: Problem[];
  biggest_struggle: string;
};

// assembled_json is no longer returned — client fetches via GET /api/blueprints/{id}.
export type AssessmentResponse = {
  blueprint_id: string;
  assessment_id: string;
};

export function submitAssessment(
  payload: AssessmentPayload,
): Promise<AssessmentResponse> {
  return apiRequest<AssessmentResponse>("/api/assessments", {
    method: "POST",
    body: payload,
  });
}
