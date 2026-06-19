// Assessment form store — Zustand. Persists draft to AsyncStorage so the
// form survives navigation, app backgrounding, and accidental reloads.

import { create } from "zustand";

import type {
  Diet,
  Gender,
  Goal,
  Lifestyle,
  Problem,
  TimeMinutes,
  WorkoutPreference,
} from "@/src/lib/constants";
import { STORAGE_KEYS } from "@/src/lib/constants";
import { storage } from "@/src/utils/storage";

export type AssessmentDraft = {
  // Step 1
  age: number | null;
  gender: Gender | null;
  height_cm: number | null;
  weight_kg: number | null;
  // Step 2
  goal: Goal | null;
  // Step 3
  lifestyle: Lifestyle | null;
  // Step 4
  diet: Diet | null;
  workout_preference: WorkoutPreference | null;
  time_available_min: TimeMinutes | null;
  // Step 5
  problems: Problem[];
  // Step 6
  biggest_struggle: string;
};

export const EMPTY_DRAFT: AssessmentDraft = {
  age: null,
  gender: null,
  height_cm: null,
  weight_kg: null,
  goal: null,
  lifestyle: null,
  diet: null,
  workout_preference: null,
  time_available_min: null,
  problems: [],
  biggest_struggle: "",
};

export const TOTAL_STEPS = 7;

type AssessmentState = {
  step: number; // 1..7
  draft: AssessmentDraft;
  hydrated: boolean;
  submitting: boolean;
  submitError: string | null;

  hydrate: () => Promise<void>;
  setStep: (step: number) => void;
  next: () => void;
  prev: () => void;
  patch: (patch: Partial<AssessmentDraft>) => void;
  reset: () => Promise<void>;
  setSubmitting: (v: boolean) => void;
  setSubmitError: (msg: string | null) => void;
};

const SERIALISED_KEY = STORAGE_KEYS.assessmentDraft;

function persist(draft: AssessmentDraft) {
  // Fire-and-forget; storage helpers swallow their own errors.
  void storage.setItem(SERIALISED_KEY, JSON.stringify(draft));
}

export const useAssessmentStore = create<AssessmentState>((set, get) => ({
  step: 1,
  draft: EMPTY_DRAFT,
  hydrated: false,
  submitting: false,
  submitError: null,

  hydrate: async () => {
    const raw = await storage.getItem<string>(SERIALISED_KEY, "");
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as Partial<AssessmentDraft>;
        set({ draft: { ...EMPTY_DRAFT, ...parsed }, hydrated: true });
        return;
      } catch {
        // fall through to empty
      }
    }
    set({ hydrated: true });
  },

  setStep: (step) => {
    const clamped = Math.max(1, Math.min(TOTAL_STEPS, step));
    set({ step: clamped });
  },
  next: () => {
    const current = get().step;
    if (current < TOTAL_STEPS) set({ step: current + 1 });
  },
  prev: () => {
    const current = get().step;
    if (current > 1) set({ step: current - 1 });
  },

  patch: (patch) => {
    const draft = { ...get().draft, ...patch };
    set({ draft });
    persist(draft);
  },

  reset: async () => {
    await storage.removeItem(SERIALISED_KEY);
    set({ draft: EMPTY_DRAFT, step: 1, submitError: null });
  },

  setSubmitting: (submitting) => set({ submitting }),
  setSubmitError: (submitError) => set({ submitError }),
}));
