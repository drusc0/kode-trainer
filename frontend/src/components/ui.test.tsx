import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResultStrip, verdictTone } from "./ui";

const cellsOf = (container: HTMLElement) => [...container.querySelectorAll("i.c")].map((el) => el.className);

describe("ResultStrip", () => {
  it("renders one cell per test and announces the pass count", () => {
    const { container } = render(<ResultStrip cells={["pass", "fail", "skip"]} />);
    expect(cellsOf(container)).toEqual(["c pass", "c fail", "c skip"]);
    expect(container.querySelector(".strip")?.getAttribute("aria-label")).toBe("1 of 3 passed");
  });

  it("compresses long runs to 60 cells without hiding a failure", () => {
    const cells = Array.from({ length: 600 }, (_, i) => (i === 599 ? "fail" : "pass") as "pass" | "fail");
    const { container } = render(<ResultStrip cells={cells} />);
    const shown = cellsOf(container);
    expect(shown).toHaveLength(60);
    expect(shown.at(-1)).toBe("c fail");
    expect(shown.filter((c) => c === "c fail")).toHaveLength(1);
  });
});

describe("verdictTone", () => {
  it.each([
    ["Accepted", "pass"],
    ["Invalid Input", "warn"],
    ["Wrong Answer", "fail"],
    ["Time Limit Exceeded", "fail"],
  ])("%s -> %s", (verdict, tone) => {
    expect(verdictTone(verdict)).toBe(tone);
  });
});
