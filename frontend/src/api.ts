import type { components } from "./api.gen";

type Schemas = components["schemas"];

export type Session = Schemas["Session"];
export type ProblemSummary = Schemas["ProblemSummary"];
export type ProblemDetail = Schemas["ProblemDetail"];
export type CaseResult = Schemas["CaseResult"];
export type RunResult = Schemas["RunResult"];
export type SubmitResult = Schemas["SubmitResult"];
export type Submission = Schemas["Submission"];
export type Bucket = Schemas["Bucket"];
export type SessionStats = Schemas["SessionStats"];
export type ChatMessage = Schemas["ChatMessage"];
export type Difficulty = ProblemSummary["difficulty"];
export type Target = Session["target"];
export type Status = ProblemSummary["status"];

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

export const problemChatPath = (sessionId: string, slug: string) => `${sp(sessionId, slug)}/chat`;
export const patternChatPath = (sessionId: string, slug: string) => `/sessions/${sessionId}/patterns/${slug}/chat`;

export const api = {
  problems: (sessionId?: string | null) => req<Schemas["ProblemList"]>(`/problems${q(sessionId)}`),
  problem: (slug: string, sessionId?: string | null) => req<ProblemDetail>(`/problems/${slug}${q(sessionId)}`),

  sessions: () => req<Session[]>("/sessions"),
  createSession: (body: Schemas["SessionIn"]) =>
    req<Session>("/sessions", { method: "POST", body: JSON.stringify(body) }),
  updateSession: (id: string, body: Schemas["SessionPatch"]) =>
    req<Session>(`/sessions/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteSession: (id: string) => req<void>(`/sessions/${id}`, { method: "DELETE" }),
  stats: (id: string) => req<SessionStats>(`/sessions/${id}/stats`),

  saveDraft: (sessionId: string, slug: string, code: string) =>
    req<void>(`${sp(sessionId, slug)}/draft`, { method: "PUT", body: JSON.stringify({ code }) }),
  resetDraft: (sessionId: string, slug: string) => req<void>(`${sp(sessionId, slug)}/draft`, { method: "DELETE" }),
  run: (sessionId: string, slug: string, code: string, cases: unknown[][]) =>
    req<RunResult>(`${sp(sessionId, slug)}/run`, {
      method: "POST",
      body: JSON.stringify({ code, cases } satisfies Schemas["RunIn"]),
    }),
  submit: (sessionId: string, slug: string, code: string) =>
    req<SubmitResult>(`${sp(sessionId, slug)}/submit`, { method: "POST", body: JSON.stringify({ code }) }),
  submissions: (sessionId: string, slug: string) => req<Submission[]>(`${sp(sessionId, slug)}/submissions`),
  chat: (path: string) => req<Schemas["ChatHistory"]>(path),
  sendChat: (path: string, message: string, code = "") =>
    req<Schemas["ChatReply"]>(path, {
      method: "POST",
      body: JSON.stringify({ message, code } satisfies Schemas["ChatIn"]),
    }),
  clearChat: (path: string) => req<void>(path, { method: "DELETE" }),
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
