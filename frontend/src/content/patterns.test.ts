import { describe, expect, it } from "vitest";
import { APPROACH_GUIDE, PATTERNS, patternBody } from "./patterns";

describe("pattern guides", () => {
  // patternBody falls back to "" for a missing file, so a renamed .md would otherwise ship a blank page.
  it.each(PATTERNS.map((p) => p.slug))("%s has a guide", (slug) => {
    expect(patternBody(slug).trim()).not.toBe("");
  });

  it.each(PATTERNS.map((p) => p.slug))("%s explains it simply before the code", (slug) => {
    const body = patternBody(slug);
    const order = ["## The idea in plain words", "## Picture it", "## Walk through an example", "## The code"].map(
      (h) => body.indexOf(h),
    );
    expect(order.every((i) => i >= 0)).toBe(true);
    expect(order).toEqual([...order].sort((a, b) => a - b));
  });

  it("includes the approach guide", () => {
    expect(APPROACH_GUIDE.trim()).not.toBe("");
  });
});
