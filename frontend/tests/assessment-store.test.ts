// Zustand store transitions for the assessment form. Pure logic — no RN.

import "./_setup";

import { strict as assert } from "node:assert";
import { describe, test, beforeEach } from "node:test";

import {
  EMPTY_DRAFT,
  TOTAL_STEPS,
  useAssessmentStore,
} from "../src/stores/assessment";

beforeEach(async () => {
  await useAssessmentStore.getState().reset();
  useAssessmentStore.setState({ step: 1 });
});

describe("assessment store", () => {
  test("starts at step 1 with an empty draft", () => {
    const s = useAssessmentStore.getState();
    assert.equal(s.step, 1);
    assert.deepEqual(s.draft, EMPTY_DRAFT);
  });

  test("next() advances and stops at TOTAL_STEPS", () => {
    for (let i = 0; i < TOTAL_STEPS + 3; i++) {
      useAssessmentStore.getState().next();
    }
    assert.equal(useAssessmentStore.getState().step, TOTAL_STEPS);
  });

  test("prev() rewinds and stops at 1", () => {
    useAssessmentStore.setState({ step: 3 });
    useAssessmentStore.getState().prev();
    useAssessmentStore.getState().prev();
    useAssessmentStore.getState().prev();
    useAssessmentStore.getState().prev();
    assert.equal(useAssessmentStore.getState().step, 1);
  });

  test("setStep clamps to [1, TOTAL_STEPS]", () => {
    useAssessmentStore.getState().setStep(99);
    assert.equal(useAssessmentStore.getState().step, TOTAL_STEPS);
    useAssessmentStore.getState().setStep(-5);
    assert.equal(useAssessmentStore.getState().step, 1);
  });

  test("patch merges fields", () => {
    useAssessmentStore.getState().patch({ age: 33, gender: "female" });
    const d = useAssessmentStore.getState().draft;
    assert.equal(d.age, 33);
    assert.equal(d.gender, "female");
  });

  test("reset restores empty draft", async () => {
    useAssessmentStore.getState().patch({ age: 33 });
    await useAssessmentStore.getState().reset();
    assert.deepEqual(useAssessmentStore.getState().draft, EMPTY_DRAFT);
    assert.equal(useAssessmentStore.getState().step, 1);
  });
});
