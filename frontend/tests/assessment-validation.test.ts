// Validation logic for the assessment form. Exercises every branch.

import "./_setup";
import { strict as assert } from "node:assert";
import { describe, test } from "node:test";

import {
  draftToPayload,
  validateForSubmit,
  validateStep1,
  validateStep2,
  validateStep3,
  validateStep4,
  validateStep6,
} from "../src/lib/assessment-validation";
import { EMPTY_DRAFT } from "../src/stores/assessment";

const VALID = {
  ...EMPTY_DRAFT,
  age: 30,
  gender: "female" as const,
  height_cm: 165,
  weight_kg: 65,
  goal: "fat_loss" as const,
  lifestyle: "working_professional" as const,
  diet: "vegetarian" as const,
  workout_preference: "home" as const,
  time_available_min: 30 as const,
  problems: ["pcos" as const],
  biggest_struggle: "I struggle to be consistent.",
};

describe("assessment validation", () => {
  test("a fully populated draft validates and converts to payload", () => {
    assert.equal(validateForSubmit(VALID), null);
    const payload = draftToPayload(VALID);
    assert.equal(payload.age, 30);
    assert.equal(payload.diet, "vegetarian");
    assert.deepEqual(payload.problems, ["pcos"]);
  });

  test("step1 catches missing fields and bounds", () => {
    assert.match(validateStep1(EMPTY_DRAFT)!, /age/i);
    assert.match(validateStep1({ ...VALID, age: 5 })!, /Age/);
    assert.match(validateStep1({ ...VALID, age: 999 })!, /Age/);
    assert.match(validateStep1({ ...VALID, gender: null })!, /gender/i);
    assert.match(validateStep1({ ...VALID, height_cm: 50 })!, /Height/);
    assert.match(validateStep1({ ...VALID, weight_kg: 1000 })!, /Weight/);
  });

  test("step2 requires a goal", () => {
    assert.match(validateStep2({ ...VALID, goal: null })!, /goal/);
    assert.equal(validateStep2(VALID), null);
  });

  test("step3 requires a lifestyle", () => {
    assert.match(validateStep3({ ...VALID, lifestyle: null })!, /lifestyle/);
  });

  test("step4 requires diet + workout + time", () => {
    assert.match(validateStep4({ ...VALID, diet: null })!, /diet/);
    assert.match(
      validateStep4({ ...VALID, workout_preference: null })!,
      /home or gym/i,
    );
    assert.match(
      validateStep4({ ...VALID, time_available_min: null })!,
      /time/i,
    );
  });

  test("step6 enforces the 500-char limit", () => {
    const long = "x".repeat(501);
    assert.match(
      validateStep6({ ...VALID, biggest_struggle: long })!,
      /500/,
    );
    assert.equal(validateStep6(VALID), null);
  });

  test("draftToPayload throws on invalid input", () => {
    assert.throws(() => draftToPayload({ ...VALID, age: null }));
  });
});
