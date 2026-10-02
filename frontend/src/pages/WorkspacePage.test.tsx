import { act, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useNavigate } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProblemDetail } from "../api";
import WorkspacePage from "./WorkspacePage";

const saveDraft = vi.fn(() => Promise.resolve());

vi.mock("../api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api")>()),
  api: {
    problem: (slug: string) => Promise.resolve(problem(slug)),
    saveDraft: (...args: unknown[]) => saveDraft(...(args as [])),
  },
}));
vi.mock("../monaco", () => ({}));
vi.mock("../components/ChatPanel", () => ({ default: () => null }));
vi.mock("../session", () => ({
  useSession: () => ({ current: { id: "s1", name: "S", target: "general" }, refresh: () => Promise.resolve() }),
  useThemeValue: () => "light",
}));
vi.mock("@monaco-editor/react", () => ({
  default: ({ value, onChange }: { value: string; onChange: (v: string) => void }) => (
    <textarea aria-label="code" value={value} onChange={(e) => onChange(e.target.value)} />
  ),
}));

function problem(slug: string): ProblemDetail {
  return {
    slug,
    title: slug,
    difficulty: "Easy",
    pattern: "arrays-hashing",
    topics: [],
    companies: [],
    status: null,
    attempts: 0,
    statement: "",
    constraints: [],
    hints: [],
    kind: "function",
    fields: [],
    examples: [],
    default_cases: [],
    starter_code: `# ${slug}`,
    draft: null,
  };
}

let navigate: (to: string) => void = () => undefined;
function NavigateHook() {
  navigate = useNavigate();
  return null;
}

describe("WorkspacePage draft autosave", () => {
  beforeEach(() => saveDraft.mockClear());

  it("saves unsaved edits to the problem being left, not the next one", async () => {
    render(
      <MemoryRouter initialEntries={["/problems/a"]}>
        <NavigateHook />
        <Routes>
          <Route path="/problems/:slug" element={<WorkspacePage />} />
        </Routes>
      </MemoryRouter>,
    );
    fireEvent.change(await screen.findByLabelText("code"), { target: { value: "edited a" } });
    act(() => navigate("/problems/b"));
    expect(await screen.findByDisplayValue("# b")).toBeTruthy();

    expect(saveDraft).toHaveBeenCalledTimes(1);
    expect(saveDraft).toHaveBeenCalledWith("s1", "a", "edited a");
  });
});
