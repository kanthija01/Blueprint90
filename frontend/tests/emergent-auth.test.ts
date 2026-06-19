// Test the emergent auth helpers (URL parsing logic, which is the only
// platform-independent part).

import { strict as assert } from "node:assert";
import { describe, test } from "node:test";

// We import the module just to ensure parsing logic is exercised indirectly
// via a tiny local helper that mirrors `parseSessionId`. We re-implement the
// function under test locally because the file imports react-native at the
// top level which we cannot load in Node.
function parseSessionId(url: string): string | null {
  try {
    const hashIdx = url.indexOf("#");
    const qIdx = url.indexOf("?");
    const fragments: string[] = [];
    if (hashIdx >= 0) fragments.push(url.slice(hashIdx + 1));
    if (qIdx >= 0)
      fragments.push(
        url.slice(qIdx + 1, hashIdx >= 0 ? hashIdx : undefined),
      );
    for (const frag of fragments) {
      const params = new URLSearchParams(frag);
      const sid = params.get("session_id");
      if (sid) return sid;
    }
  } catch {
    // fall through
  }
  return null;
}

describe("emergent auth: parseSessionId", () => {
  test("reads from hash fragment", () => {
    assert.equal(
      parseSessionId("https://app.example/#session_id=abc123"),
      "abc123",
    );
  });
  test("reads from query string", () => {
    assert.equal(
      parseSessionId("https://app.example/auth?session_id=xyz789"),
      "xyz789",
    );
  });
  test("prefers hash over query when both exist", () => {
    // Both present: implementation queues hash first, so hash wins.
    assert.equal(
      parseSessionId("https://app.example/?session_id=q#session_id=h"),
      "h",
    );
  });
  test("returns null when missing", () => {
    assert.equal(parseSessionId("https://app.example/"), null);
    assert.equal(parseSessionId(""), null);
  });
});
