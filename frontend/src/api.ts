export type Difficulty = "Easy" | "Medium" | "Hard";
export type Target = "google" | "meta" | "general";
export type Status = "solved" | "attempted" | null;

export interface Session {
  id: string;
  name: string;
  target: Target;
  notes: string;
  created_at: string;
  last_active_at: string | null;
  solved: number;
  attempted: number;
}

export interface ProblemSummary {
  slug: string;
  title: string;
  difficulty: Difficulty;
  pattern: string;
  topics: string[];
  companies: string[];
  status: Status;
  attempts: number;
}

export interface ProblemDetail extends ProblemSummary {
  statement: string;
  constraints: string[];
  hints: string[];
  kind: "function" | "design";
  fields: { name: string; type: string }[];
  examples: { args: string[]; output: string | null; note?: string | null }[];
  default_cases: string[][];
  starter_code: string;
  draft: string | null;
}

export interface CaseResult {
  args: string[];
  ok?: boolean;
  output?: string;
  expected?: string | null;
  stdout?: string;
  error?: string | null;
  ms?: number | null;
  input_error?: string;
}

export interface RunResult {
  verdict: string;
  compile_error: string | null;
  cases: CaseResult[];
  passed: number;
  runtime_ms: number | null;
}

export interface SubmitResult {
  submission_id: string;
  verdict: string;
  passed: number;
  total: number;
  compile_error: string | null;
  runtime_ms: number | null;
  failing: (CaseResult & { index: number; is_example: boolean }) | null;
}

export interface Submission {
  id: string;
  verdict: string;
  passed: number;
  total: number;
  runtime_ms: number | null;
  created_at: string;
  code: string;
}

export interface Bucket {
  solved: number;
  total: number;
}

export interface SessionStats {
  by_difficulty: Record<Difficulty, Bucket>;
  by_pattern: Record<string, Bucket>;
  submissions: number;
  accepted: number;
  recent: { id: string; problem: string; title: string; verdict: string; created_at: string; runtime_ms: number | null }[];
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) message = typeof body.detail === "string" ? body.detail : "Check the values you entered.";
    } catch {
      /* not JSON */
    }
    throw new Error(message);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}

const q = (sessionId?: string | null) => (sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : "");
const sp = (sessionId: string, slug: string) => `/sessions/${sessionId}/problems/${slug}`;

export const api = {
  problems: (sessionId?: string | null) => req<{ patterns: string[]; problems: ProblemSummary[] }>(`/problems${q(sessionId)}`),
  problem: (slug: string, sessionId?: string | null) => req<ProblemDetail>(`/problems/${slug}${q(sessionId)}`),

  sessions: () => req<Session[]>("/sessions"),
  createSession: (body: { name: string; target: Target; notes: string }) =>
    req<Session>("/sessions", { method: "POST", body: JSON.stringify(body) }),
  updateSession: (id: string, body: Partial<Pick<Session, "name" | "target" | "notes">>) =>
    req<Session>(`/sessions/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteSession: (id: string) => req<void>(`/sessions/${id}`, { method: "DELETE" }),
  stats: (id: string) => req<SessionStats>(`/sessions/${id}/stats`),

  saveDraft: (sessionId: string, slug: string, code: string) =>
    req<void>(`${sp(sessionId, slug)}/draft`, { method: "PUT", body: JSON.stringify({ code }) }),
  resetDraft: (sessionId: string, slug: string) => req<void>(`${sp(sessionId, slug)}/draft`, { method: "DELETE" }),
  run: (sessionId: string, slug: string, code: string, cases: unknown[][]) =>
    req<RunResult>(`${sp(sessionId, slug)}/run`, { method: "POST", body: JSON.stringify({ code, cases }) }),
  submit: (sessionId: string, slug: string, code: string) =>
    req<SubmitResult>(`${sp(sessionId, slug)}/submit`, { method: "POST", body: JSON.stringify({ code }) }),
  submissions: (sessionId: string, slug: string) => req<Submission[]>(`${sp(sessionId, slug)}/submissions`),
};

export function timeAgo(iso: string | null): string {
  if (!iso) return "never";
  const s = Math.round((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h ago`;
  const d = Math.round(h / 24);
  return d === 1 ? "yesterday" : `${d} days ago`;
}

export const TARGET_LABEL: Record<Target, string> = { google: "Google", meta: "Meta", general: "General" };
