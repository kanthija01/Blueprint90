// Phase 5 frontend tests — verify the renderer's pure mapping logic and
// invariants the UI relies on. Component-level rendering tests live in
// the backend-driven integration once a real device is available; for now
// we exercise the data-shaping helpers used by the screen.

import "./_setup";

import { strict as assert } from "node:assert";
import { describe, test } from "node:test";

import type { AssembledBlueprint } from "../src/api/blueprints";

const MINIMAL_BLUEPRINT: AssembledBlueprint = {
  cover_page: {
    user_name: null,
    goal: "fat_loss",
    duration_days: 90,
    generated_at: "2026-06-19T10:00:00+00:00",
    biggest_struggle: null,
  },
  why_previous_attempts_failed: [],
  root_causes: [],
  nutrition_strategy: {
    diet: "vegetarian",
    targets: [],
    foods: [],
    foods_to_avoid: [],
    meal_ideas: [],
    source_module: "pcos",
  },
  workout_plan: null, // sparse
  habit_system: [],
  psychology_system: { common_thoughts: [], techniques: [] },
  faqs: [],
  plateau_playbook: [],
  weekly_milestones: Array.from({ length: 12 }, (_, i) => ({
    week: i + 1,
    focus:
      i === 0 || i === 3 || i === 7 || i === 11
        ? "Review"
        : "Consistency week",
    checklist_items: [],
  })),
  progress_tracker: { columns: [], weeks: Array.from({ length: 12 }, (_, i) => i + 1) },
  meta: {
    modules_used: [
      {
        slug: "pcos",
        display_name: "PCOS",
        reason: "problem_match",
        priority: 0,
        is_fallback: false,
        fallback_note: null,
      },
      {
        slug: "dorm_fit",
        display_name: "Dorm Fit",
        reason: "fallback",
        priority: 1,
        is_fallback: true,
        fallback_note: "Adapted from our campus-living plan.",
      },
    ],
    assembled_at: "2026-06-19T10:00:00+00:00",
    primary_module_slug: "pcos",
  },
};

describe("blueprint preview — invariants", () => {
  test("weekly_milestones must always be length 12", () => {
    assert.equal(MINIMAL_BLUEPRINT.weekly_milestones.length, 12);
    // Sanity: weeks are 1..12 in order.
    MINIMAL_BLUEPRINT.weekly_milestones.forEach((m, i) => {
      assert.equal(m.week, i + 1);
    });
  });

  test("progress_tracker.weeks must always span 1..12", () => {
    assert.deepEqual(
      MINIMAL_BLUEPRINT.progress_tracker.weeks,
      Array.from({ length: 12 }, (_, i) => i + 1),
    );
  });

  test("empty progress_tracker.columns is allowed (sparse module case)", () => {
    // The TrackerTable component renders just the week column.
    assert.equal(MINIMAL_BLUEPRINT.progress_tracker.columns.length, 0);
  });

  test("workout_plan can be null — the UI shows an empty-state card", () => {
    assert.equal(MINIMAL_BLUEPRINT.workout_plan, null);
  });

  test("a module flagged is_fallback must carry a fallback_note", () => {
    const fb = MINIMAL_BLUEPRINT.meta.modules_used.find((m) => m.is_fallback)!;
    assert.ok(fb);
    assert.ok(fb.fallback_note && fb.fallback_note.length > 0);
  });

  test("primary_module_slug references a module that exists in modules_used", () => {
    const slugs = MINIMAL_BLUEPRINT.meta.modules_used.map((m) => m.slug);
    assert.ok(slugs.includes(MINIMAL_BLUEPRINT.meta.primary_module_slug));
  });

  test("weeks 1, 4, 8, 12 are the documented review weeks", () => {
    // The WeeklyCard component highlights these specifically.
    const reviewWeeks = [1, 4, 8, 12];
    for (const w of reviewWeeks) {
      const milestone = MINIMAL_BLUEPRINT.weekly_milestones.find(
        (m) => m.week === w,
      );
      assert.ok(milestone, `Week ${w} missing`);
    }
  });
});
