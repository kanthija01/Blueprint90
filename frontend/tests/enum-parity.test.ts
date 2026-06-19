// Verify the frontend enum literals match the backend Pydantic Literals.
// Any drift here = the API will 422 — better to catch in CI.

import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { test, describe } from "node:test";

import {
  DIETS,
  GENDERS,
  GOALS,
  LIFESTYLES,
  PROBLEMS,
  TIME_MINUTES,
  WORKOUT_PREFERENCES,
} from "../src/lib/constants";

const BACKEND_TYPES = readFileSync(
  join(__dirname, "../../backend/rules_engine/types.py"),
  "utf-8",
);
const BACKEND_PROBLEM_MAP = readFileSync(
  join(__dirname, "../../backend/rules_engine/maps/problem_module_map.py"),
  "utf-8",
);

function extractLiteral(name: string, source: string): string[] {
  const re = new RegExp(`${name}\\s*=\\s*Literal\\[([^\\]]+)\\]`);
  const match = source.match(re);
  if (!match) throw new Error(`Literal ${name} not found in source`);
  return Array.from(match[1].matchAll(/["']([^"']+)["']/g)).map((m) => m[1]);
}

describe("frontend↔backend enum parity", () => {
  test("Gender", () => {
    assert.deepEqual(
      [...GENDERS].sort(),
      extractLiteral("Gender", BACKEND_TYPES).sort(),
    );
  });
  test("Goal", () => {
    assert.deepEqual(
      [...GOALS].sort(),
      extractLiteral("Goal", BACKEND_TYPES).sort(),
    );
  });
  test("Lifestyle", () => {
    assert.deepEqual(
      [...LIFESTYLES].sort(),
      extractLiteral("Lifestyle", BACKEND_TYPES).sort(),
    );
  });
  test("Diet", () => {
    assert.deepEqual(
      [...DIETS].sort(),
      extractLiteral("Diet", BACKEND_TYPES).sort(),
    );
  });
  test("WorkoutPreference", () => {
    assert.deepEqual(
      [...WORKOUT_PREFERENCES].sort(),
      extractLiteral("WorkoutPreference", BACKEND_TYPES).sort(),
    );
  });
  test("TimeMinutes", () => {
    const backend = Array.from(
      BACKEND_TYPES.match(/TimeMinutes\s*=\s*Literal\[([^\]]+)\]/)![1].matchAll(
        /\d+/g,
      ),
    ).map((m) => Number(m[0]));
    assert.deepEqual([...TIME_MINUTES].sort(), backend.sort());
  });
  test("Every Problem slug is mapped in backend PROBLEM_MODULE_MAP", () => {
    for (const p of PROBLEMS) {
      assert.ok(
        new RegExp(`["']${p}["']\\s*:`).test(BACKEND_PROBLEM_MAP),
        `Problem "${p}" missing in PROBLEM_MODULE_MAP`,
      );
    }
  });
});
