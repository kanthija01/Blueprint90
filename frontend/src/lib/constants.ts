// Enum-equivalent values — MUST mirror backend Pydantic literals exactly.
// `rules_engine/types.py` is the source of truth on the backend.

export const GENDERS = ["male", "female", "other"] as const;
export type Gender = (typeof GENDERS)[number];

export const GOALS = ["fat_loss", "muscle_gain", "maintenance"] as const;
export type Goal = (typeof GOALS)[number];

export const LIFESTYLES = [
  "student",
  "working_professional",
  "busy_mother",
  "night_shift_worker",
] as const;
export type Lifestyle = (typeof LIFESTYLES)[number];

export const DIETS = ["vegetarian", "non_vegetarian", "vegan"] as const;
export type Diet = (typeof DIETS)[number];

export const WORKOUT_PREFERENCES = ["home", "gym"] as const;
export type WorkoutPreference = (typeof WORKOUT_PREFERENCES)[number];

export const TIME_MINUTES = [15, 30, 45, 60] as const;
export type TimeMinutes = (typeof TIME_MINUTES)[number];

// Problem slugs MUST exist in backend rules_engine/maps/problem_module_map.py.
export const PROBLEMS = [
  "pcos",
  "thyroid",
  "plateau",
  "consistency",
  "emotional_eating",
  "knee_pain",
  "back_pain",
  "stress",
] as const;
export type Problem = (typeof PROBLEMS)[number];

// UI labels (decoupled from backend slugs so we can rephrase without breaking).
export const PROBLEM_LABELS: Record<Problem, string> = {
  pcos: "PCOS",
  thyroid: "Thyroid",
  plateau: "Plateau",
  consistency: "Consistency",
  emotional_eating: "Emotional Eating",
  knee_pain: "Knee Pain",
  back_pain: "Back Pain",
  stress: "Stress",
};

export const GENDER_LABELS: Record<Gender, string> = {
  male: "Male",
  female: "Female",
  other: "Other",
};

export const GOAL_LABELS: Record<Goal, string> = {
  fat_loss: "Fat Loss",
  muscle_gain: "Muscle Gain",
  maintenance: "Maintenance",
};

export const LIFESTYLE_LABELS: Record<Lifestyle, string> = {
  student: "Student",
  working_professional: "Working Professional",
  busy_mother: "Busy Mother",
  night_shift_worker: "Night Shift Worker",
};

export const DIET_LABELS: Record<Diet, string> = {
  vegetarian: "Vegetarian",
  non_vegetarian: "Non-Vegetarian",
  vegan: "Vegan",
};

export const WORKOUT_PREF_LABELS: Record<WorkoutPreference, string> = {
  home: "Home",
  gym: "Gym",
};

// Numeric input bounds (mirror Pydantic Field constraints).
export const AGE_MIN = 13;
export const AGE_MAX = 100;
export const HEIGHT_MIN = 100;
export const HEIGHT_MAX = 250;
export const WEIGHT_MIN = 30;
export const WEIGHT_MAX = 300;
export const STRUGGLE_MAX_LEN = 500;

export const STORAGE_KEYS = {
  sessionToken: "bp90.session_token",
  assessmentDraft: "bp90.assessment_draft",
} as const;
