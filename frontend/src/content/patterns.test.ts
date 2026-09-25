import { describe, expect, it } from "vitest";
import { APPROACH_GUIDE, PATTERNS, patternBody } from "./patterns";

describe("pattern guides", () => {
  // patternBody falls back to "" for a missing file, so a renamed .md would otherwise ship a blank page.
  it.each(PATTERNS.map((p) => p.slug))("%s has a guide", (slug) => {
    expect(patternBody(slug).trim()).not.toBe("");
  });

  it("includes the approach guide", () => {
    expect(APPROACH_GUIDE.trim()).not.toBe("");
  });
});
