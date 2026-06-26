// GET /api/blueprints + GET /api/blueprints/{id}.
// The detail endpoint returns the cached AssembledBlueprint verbatim —
// the frontend treats it as immutable read-only data and never mutates it.

import { apiRequest } from "./client";

export type BlueprintListItem = {
  blueprint_id: string;
  created_at: string;
  goal: string;
  primary_module_slug: string;
  primary_module_display_name: string;
  module_count: number;
};

// ---- AssembledBlueprint (mirrors backend/models/blueprint.py) ----------
export type CoverPage = {
  user_name: string | null;
  goal: string;
  duration_days: number;
  generated_at: string;
  biggest_struggle: string | null;
};

export type FailedSolutionItem = {
  solution_tried: string;
  why_it_failed: string;
  source_module: string;
};
export type RootCauseItem = {
  category: string;
  root_cause: string;
  source_module: string;
};
export type NutritionTargetItem = { field_name: string; field_value: string };
export type FoodItem = { food_type: string; options: string };
export type FoodToAvoidItem = { food_type: string; why_avoid: string };
export type MealIdeaItem = { meal_time: string; meal_option: string };
export type NutritionStrategy = {
  diet: string;
  targets: NutritionTargetItem[];
  foods: FoodItem[];
  foods_to_avoid: FoodToAvoidItem[];
  meal_ideas: MealIdeaItem[];
  source_module: string;
};
export type WorkoutExerciseItem = {
  exercise_name: string;
  reps_or_time: string | null;
  sets: string | null;
  rest: string | null;
  week_progression: Record<string, string> | null;
};
export type ExerciseAvoidItem = {
  exercise_type: string;
  why_avoid: string;
};
export type ConstraintSwapItem = {
  constraint_name: string;
  solution: string;
  approach: string | null;
};
export type WorkoutPlan = {
  time_minutes: number;
  location: string;
  routine_label: string | null;
  exercises: WorkoutExerciseItem[];
  exercises_to_avoid: ExerciseAvoidItem[];
  constraint_swaps: ConstraintSwapItem[];
  source_module: string;
};
export type HabitItem = {
  habit_name: string;
  daily_target: string | null;
  how_to_track: string | null;
  source_module: string;
};
export type PsychologyThoughtItem = {
  common_thought: string;
  emotional_impact: string | null;
  solution: string;
  source_module: string;
};
export type PsychologyTechniqueItem = {
  technique: string;
  how_to_apply: string;
  source_module: string;
};
export type PsychologySystem = {
  common_thoughts: PsychologyThoughtItem[];
  techniques: PsychologyTechniqueItem[];
};
export type FAQItem = {
  question: string;
  answer: string;
  source_module: string;
};
export type PlateauActionItem = {
  trigger_condition: string;
  action_to_take: string;
  timeframe: string | null;
  source_module: string;
};
export type WeeklyMilestone = {
  week: number;
  focus: string;
  checklist_items: string[];
};
export type ProgressTracker = {
  columns: string[];
  weeks: number[];
};
export type ModuleUsedMeta = {
  slug: string;
  display_name: string;
  reason: string;
  priority: number;
  is_fallback: boolean;
  fallback_note: string | null;
};
export type AssembledMeta = {
  modules_used: ModuleUsedMeta[];
  assembled_at: string;
  primary_module_slug: string;
};

export type AssembledBlueprint = {
  cover_page: CoverPage;
  why_previous_attempts_failed: FailedSolutionItem[];
  root_causes: RootCauseItem[];
  nutrition_strategy: NutritionStrategy;
  workout_plan: WorkoutPlan | null;
  habit_system: HabitItem[];
  psychology_system: PsychologySystem;
  faqs: FAQItem[];
  plateau_playbook: PlateauActionItem[];
  weekly_milestones: WeeklyMilestone[];
  progress_tracker: ProgressTracker;
  meta: AssembledMeta;
};

export function listBlueprints(): Promise<BlueprintListItem[]> {
  return apiRequest<BlueprintListItem[]>("/api/blueprints");
}

export function getBlueprint(id: string): Promise<AssembledBlueprint> {
  return apiRequest<AssembledBlueprint>(`/api/blueprints/${id}`);
}
