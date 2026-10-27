import { describe, expect, it } from "vitest";
import { DESIGN_APPROACH, FUNDAMENTALS, fundamentalBody } from "./design";

describe("system design fundamentals", () => {
  it.each(FUNDAMENTALS.map((f) => f.slug))("%s motivates the topic and ends with self-check questions", (slug) => {
    const body = fundamentalBody(slug);
    const why = body.indexOf("## Why it matters");
    const check = body.indexOf("## Check yourself");
    expect(why).toBe(0);
    expect(check).toBeGreaterThan(why);
  });

  it("includes the interview approach", () => {
    expect(DESIGN_APPROACH).toContain("## 1. Requirements");
  });
});
