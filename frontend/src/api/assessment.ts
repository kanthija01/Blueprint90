// POST /api/assessments — the single endpoint that drives the whole funnel.

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

// The returned `assembled_json` is the full blueprint. Phase 4 only needs
// the IDs for navigation; preview rendering arrives in Phase 5.
export type AssessmentResponse = {
  blueprint_id: string;
  assessment_id: string;
  assembled_json: Record<string, unknown>;
};

export function submitAssessment(
  payload: AssessmentPayload,
): Promise<AssessmentResponse> {
  return apiRequest<AssessmentResponse>("/api/assessments", {
    method: "POST",
    body: payload,
  });
}
