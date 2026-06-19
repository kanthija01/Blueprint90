// Pure runtime test for the theme tokens. Catches accidental colour drift.

import { strict as assert } from "node:assert";
import { describe, test } from "node:test";

import { colors } from "../src/theme/colors";
import { radius, spacing } from "../src/theme/spacing";
import { typography } from "../src/theme/typography";

describe("theme tokens", () => {
  test("colour palette matches the locked brand spec", () => {
    assert.equal(colors.background, "#0B0B0B");
    assert.equal(colors.card, "#141414");
    assert.equal(colors.primary, "#FFD60A");
    assert.equal(colors.primaryPressed, "#F5C518");
    assert.equal(colors.text, "#FFFFFF");
    assert.equal(colors.textMuted, "#A0A0A0");
    assert.equal(colors.border, "#2A2A2A");
  });
  test("spacing follows an 8pt grid", () => {
    for (const value of Object.values(spacing)) {
      assert.equal(value % 4, 0, `${value} not on a 4pt step`);
    }
  });
  test("radius pill is large enough for round buttons", () => {
    assert.ok(radius.pill >= 100);
  });
  test("typography ramp is monotonic in font size", () => {
    const order = [
      typography.caption.fontSize!,
      typography.body.fontSize!,
      typography.h3.fontSize!,
      typography.h2.fontSize!,
      typography.h1.fontSize!,
      typography.display.fontSize!,
    ];
    for (let i = 1; i < order.length; i++) {
      assert.ok(
        order[i] >= order[i - 1],
        `font-size step ${i} regressed: ${order[i - 1]} -> ${order[i]}`,
      );
    }
  });
});
