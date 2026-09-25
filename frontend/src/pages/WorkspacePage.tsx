import Editor, { type OnMount } from "@monaco-editor/react";
import { useCallback, useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api, TARGET_LABEL, timeAgo,
  type CaseResult, type ProblemDetail, type RunResult, type Submission, type SubmitResult,
} from "../api";
import ChatPanel from "../components/ChatPanel";
import Markdown from "../components/Markdown";
import { DifficultyTag, ResultStrip, StatusMark, verdictTone } from "../components/ui";
import { patternTitle } from "../content/patterns";
import { useSession, useThemeValue } from "../session";

type Outcome =
  | { kind: "run"; data: RunResult }
  | { kind: "submit"; data: SubmitResult }
  | { kind: "error"; message: string };

const MAX_CASES = 10;

export default function WorkspacePage() {
  const { slug = "" } = useParams();
  const { current, refresh } = useSession();
  const theme = useThemeValue();
  const sessionId = current!.id;

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [saveState, setSaveState] = useState<"saved" | "saving" | "idle">("idle");
  const [cases, setCases] = useState<string[][]>([]);
  const [activeCase, setActiveCase] = useState(0);
  const [consoleTab, setConsoleTab] = useState<"cases" | "result">("cases");
  const [leftTab, setLeftTab] = useState<"description" | "submissions" | "chat">("description");
  const [busy, setBusy] = useState<"run" | "submit" | null>(null);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [submissions, setSubmissions] = useState<Submission[] | null>(null);
  const [confirmReset, setConfirmReset] = useState(false);
  const [leftPct, setLeftPct] = useState(42);
  const [consolePct, setConsolePct] = useState(36);
  const lastSaved = useRef<string | null>(null);

  // ---------------------------------------------------------------- load
  useEffect(() => {
    let cancelled = false;
    setProblem(null); setOutcome(null); setSubmissions(null); setLeftTab("description"); setConsoleTab("cases");
    api.problem(slug, sessionId)
      .then((p) => {
        if (cancelled) return;
        const initial = p.draft ?? p.starter_code;
        setProblem(p);
        setCode(initial);
        lastSaved.current = initial;
        setCases(p.default_cases.map((c) => [...c]));
        setActiveCase(0);
      })
      .catch((e: Error) => !cancelled && setLoadError(e.message));
    return () => { cancelled = true; };
  }, [slug, sessionId]);

  const loadSubmissions = useCallback(() => {
    api.submissions(sessionId, slug).then(setSubmissions).catch(() => setSubmissions([]));
  }, [sessionId, slug]);

  useEffect(() => {
    if (leftTab === "submissions" && submissions === null) loadSubmissions();
  }, [leftTab, submissions, loadSubmissions]);

  // ---------------------------------------------------------------- autosave draft (per session)
  useEffect(() => {
    if (!problem || code === lastSaved.current) return;
    setSaveState("saving");
    const t = setTimeout(() => {
      api.saveDraft(sessionId, slug, code)
        .then(() => { lastSaved.current = code; setSaveState("saved"); })
        .catch(() => setSaveState("idle"));
    }, 800);
    return () => clearTimeout(t);
  }, [code, problem, sessionId, slug]);

  // ---------------------------------------------------------------- actions
  const run = useCallback(async () => {
    if (!problem || busy) return;
    let parsed: unknown[][];
    try {
      parsed = cases.map((c, i) => c.map((raw, j) => {
        try { return JSON.parse(raw); } catch {
          throw new Error(`Case ${i + 1}, ${problem.fields[j].name}: not valid JSON (use [1,2], "text", true, null)`);
        }
      }));
    } catch (e) {
      setOutcome({ kind: "error", message: (e as Error).message }); setConsoleTab("result");
      return;
    }
    setBusy("run"); setConsoleTab("result");
    try {
      setOutcome({ kind: "run", data: await api.run(sessionId, slug, code, parsed) });
    } catch (e) {
      setOutcome({ kind: "error", message: (e as Error).message });
    } finally {
      setBusy(null);
    }
  }, [problem, busy, cases, sessionId, slug, code]);

  const submit = useCallback(async () => {
    if (!problem || busy) return;
    setBusy("submit"); setConsoleTab("result");
    try {
      const data = await api.submit(sessionId, slug, code);
      lastSaved.current = code;
      setOutcome({ kind: "submit", data });
      setProblem((p) => p && { ...p, status: data.verdict === "Accepted" ? "solved" : p.status ?? "attempted" });
      setSubmissions(null);
      if (leftTab === "submissions") loadSubmissions();
      void refresh();
    } catch (e) {
      setOutcome({ kind: "error", message: (e as Error).message });
    } finally {
      setBusy(null);
    }
  }, [problem, busy, sessionId, slug, code, leftTab, loadSubmissions, refresh]);

  const reset = async () => {
    if (!problem) return;
    if (!confirmReset) {
      setConfirmReset(true);
      setTimeout(() => setConfirmReset(false), 3000);
      return;
    }
    setConfirmReset(false);
    setCode(problem.starter_code);
    lastSaved.current = problem.starter_code;
    await api.resetDraft(sessionId, slug).catch(() => undefined);
  };

  // keep Monaco keybindings pointed at the latest callbacks
  const runRef = useRef(run); runRef.current = run;
  const submitRef = useRef(submit); submitRef.current = submit;
  const onMount: OnMount = (editor, monaco) => {
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => void runRef.current());
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => void submitRef.current());
    editor.focus();
  };

  // ---------------------------------------------------------------- resizing
  const startDrag = (axis: "x" | "y") => (e: ReactPointerEvent<HTMLDivElement>) => {
    const container = (e.currentTarget.parentElement as HTMLElement).getBoundingClientRect();
    const move = (ev: PointerEvent) => {
      if (axis === "x") setLeftPct(clamp(((ev.clientX - container.left) / container.width) * 100, 22, 70));
      else setConsolePct(clamp(((container.bottom - ev.clientY) / container.height) * 100, 14, 75));
    };
    const up = () => { window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); document.body.classList.remove("dragging"); };
    document.body.classList.add("dragging");
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };

  if (loadError) return <main className="page"><div className="notice fail">{loadError}</div></main>;
  if (!problem) return <main className="page"><p className="muted">Loading…</p></main>;

  return (
    <div className="workspace" style={{ gridTemplateColumns: `${leftPct}% 6px 1fr` }}>
      {/* ------------------------------------------------ left: statement */}
      <section className="panel">
        <div className="tabs">
          <button className={leftTab === "description" ? "on" : ""} onClick={() => setLeftTab("description")}>Description</button>
          <button className={leftTab === "submissions" ? "on" : ""} onClick={() => setLeftTab("submissions")}>Submissions</button>
          <button className={leftTab === "chat" ? "on" : ""} onClick={() => setLeftTab("chat")}>Chat</button>
          <div className="grow" />
          <Link to="/problems" className="back">← All problems</Link>
        </div>
        <div className="panel-body">
          {leftTab === "description" ? (
            <article className="statement">
              <h1 className="ptitle-lg"><StatusMark status={problem.status} /> {problem.title}</h1>
              <div className="meta">
                <DifficultyTag d={problem.difficulty} />
                <Link to={`/patterns/${problem.pattern}`} className="chip">Pattern: {patternTitle(problem.pattern)}</Link>
                {problem.companies.map((c) => <span key={c} className={`co ${c}`}>{TARGET_LABEL[c as "google" | "meta"]}</span>)}
              </div>
              <Markdown>{problem.statement}</Markdown>
              {problem.examples.map((ex, i) => (
                <div key={i} className="example">
                  <div className="example-title">Example {i + 1}</div>
                  <pre>
                    <b>Input:</b> {problem.fields.map((f, j) => `${f.name} = ${ex.args[j]}`).join(", ")}{"\n"}
                    <b>Output:</b> {ex.output ?? "…"}
                    {ex.note ? <>{"\n"}<b>Why:</b> {ex.note}</> : null}
                  </pre>
                </div>
              ))}
              <h3>Constraints</h3>
              <ul className="constraints">{problem.constraints.map((c) => <li key={c}>{c}</li>)}</ul>
              {problem.hints.map((h, i) => (
                <details key={i} className="hint"><summary>Hint {i + 1}</summary><p>{h}</p></details>
              ))}
            </article>
          ) : leftTab === "submissions" ? (
            <SubmissionsList subs={submissions} onLoad={(c) => setCode(c)} />
          ) : null}
          <ChatPanel key={slug} sessionId={sessionId} slug={slug} code={code} hidden={leftTab !== "chat"} />
        </div>
      </section>

      <div className="splitter-x" onPointerDown={startDrag("x")} role="separator" aria-orientation="vertical" />

      {/* ------------------------------------------------ right: editor + console */}
      <section className="rightcol" style={{ gridTemplateRows: `1fr 6px ${consolePct}%` }}>
        <div className="panel editor-panel">
          <div className="tabs">
            <span className="lang">Python 3</span>
            <span className={`save-state ${saveState}`}>{saveState === "saving" ? "Saving…" : saveState === "saved" ? "Draft saved" : ""}</span>
            <div className="grow" />
            <button className={`ghost ${confirmReset ? "danger" : ""}`} onClick={reset}>{confirmReset ? "Click again to reset" : "Reset"}</button>
          </div>
          <div className="editor-host">
            <Editor
              language="python"
              theme={theme === "dark" ? "kodetrain-dark" : "kodetrain-light"}
              value={code}
              onChange={(v) => setCode(v ?? "")}
              onMount={onMount}
              options={{
                fontFamily: "'IBM Plex Mono', ui-monospace, monospace", fontSize: 14, minimap: { enabled: false },
                tabSize: 4, insertSpaces: true, scrollBeyondLastLine: false, automaticLayout: true,
                renderLineHighlight: "line", padding: { top: 10 },
              }}
            />
          </div>
        </div>

        <div className="splitter-y" onPointerDown={startDrag("y")} role="separator" aria-orientation="horizontal" />

        <div className="panel console">
          <div className="tabs">
            <button className={consoleTab === "cases" ? "on" : ""} onClick={() => setConsoleTab("cases")}>Test cases</button>
            <button className={consoleTab === "result" ? "on" : ""} onClick={() => setConsoleTab("result")}>Result</button>
            <div className="grow" />
            <span className="kbd-hint">⌘/Ctrl+Enter run · +Shift submit</span>
            <button className="btn" disabled={!!busy} onClick={run}>{busy === "run" ? "Running…" : "Run"}</button>
            <button className="btn primary" disabled={!!busy} onClick={submit}>{busy === "submit" ? "Judging…" : "Submit"}</button>
          </div>
          <div className="panel-body">
            {consoleTab === "cases" ? (
              <CaseEditor
                fields={problem.fields} cases={cases} active={activeCase} setActive={setActiveCase}
                onChange={setCases} onReset={() => { setCases(problem.default_cases.map((c) => [...c])); setActiveCase(0); }}
              />
            ) : (
              <ResultView outcome={outcome} busy={busy} fields={problem.fields} />
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------- test case editor
function CaseEditor(props: {
  fields: { name: string; type: string }[];
  cases: string[][];
  active: number;
  setActive: (i: number) => void;
  onChange: (c: string[][]) => void;
  onReset: () => void;
}) {
  const { fields, cases, active, setActive, onChange, onReset } = props;
  const current = cases[active] ?? cases[0];
  if (!current) return null;
  const update = (j: number, v: string) => onChange(cases.map((c, i) => (i === active ? c.map((x, k) => (k === j ? v : x)) : c)));
  return (
    <div>
      <div className="case-tabs">
        {cases.map((_, i) => (
          <span key={i} className={`case-tab ${i === active ? "on" : ""}`}>
            <button onClick={() => setActive(i)}>Case {i + 1}</button>
            {cases.length > 1 && (
              <button className="x" aria-label={`Remove case ${i + 1}`} onClick={() => {
                onChange(cases.filter((__, k) => k !== i)); setActive(Math.max(0, Math.min(active, cases.length - 2)));
              }}>×</button>
            )}
          </span>
        ))}
        {cases.length < MAX_CASES && (
          <button className="case-add" onClick={() => { onChange([...cases, [...current]]); setActive(cases.length); }} aria-label="Add a test case">+</button>
        )}
        <div className="grow" />
        <button className="linkish" onClick={onReset}>Restore examples</button>
      </div>
      {fields.map((f, j) => (
        <label key={f.name} className="field">
          <span>{f.name} <em>{f.type}</em></span>
          <textarea spellCheck={false} rows={Math.min(6, Math.max(1, Math.ceil((current[j]?.length ?? 0) / 80)))}
            value={current[j] ?? ""} onChange={(e) => update(j, e.target.value)} />
        </label>
      ))}
      <p className="muted small">Values are JSON. Trees and linked lists use LeetCode's level-order arrays, e.g. <code>[1,2,null,3]</code>.</p>
    </div>
  );
}

// ---------------------------------------------------------------- results
function ResultView({ outcome, busy, fields }: { outcome: Outcome | null; busy: "run" | "submit" | null; fields: { name: string }[] }) {
  const [caseIdx, setCaseIdx] = useState(0);
  useEffect(() => setCaseIdx(0), [outcome]);

  if (busy) return <p className="muted">{busy === "run" ? "Running your code in the sandbox…" : "Judging against all hidden tests…"}</p>;
  if (!outcome) return <p className="muted">Run your code to see results here.</p>;
  if (outcome.kind === "error") return <div className="notice fail">{outcome.message}</div>;

  if (outcome.kind === "run") {
    const r = outcome.data;
    const tone = verdictTone(r.verdict);
    const c = r.cases[caseIdx];
    return (
      <div>
        <div className={`verdict ${tone}`}>
          {r.verdict}
          {!r.compile_error && <span className="sub">{r.passed}/{r.cases.length} cases{r.runtime_ms != null ? ` · ${r.runtime_ms} ms` : ""}</span>}
        </div>
        {r.compile_error ? <pre className="errbox">{r.compile_error}</pre> : (
          <>
            <ResultStrip cells={r.cases.map((x) => (x.ok ? "pass" : "fail"))} />
            <div className="case-tabs">
              {r.cases.map((x, i) => (
                <button key={i} className={`case-tab ${i === caseIdx ? "on" : ""} ${x.ok ? "pass" : "fail"}`} onClick={() => setCaseIdx(i)}>
                  <i className={`dot ${x.ok ? "pass" : "fail"}`} /> Case {i + 1}
                </button>
              ))}
            </div>
            {c && <CaseDetail c={c} fields={fields} />}
          </>
        )}
      </div>
    );
  }

  const s = outcome.data;
  const tone = verdictTone(s.verdict);
  const cells = Array.from({ length: s.total }, (_, i) => (i < s.passed ? "pass" : i === s.passed && s.verdict !== "Accepted" ? "fail" : "skip") as "pass" | "fail" | "skip");
  return (
    <div>
      <div className={`verdict ${tone}`}>
        {s.verdict}
        <span className="sub">{s.passed}/{s.total} tests passed{s.runtime_ms != null ? ` · ${s.runtime_ms} ms total` : ""}</span>
      </div>
      {s.compile_error ? <pre className="errbox">{s.compile_error}</pre> : <ResultStrip cells={cells} />}
      {s.verdict === "Accepted" && <p className="muted">Solved in this session. Try another approach, or explain its time and space complexity out loud.</p>}
      {s.failing && (
        <>
          <h4 className="fail-head">
            Failing test {s.failing.index + 1}{s.failing.is_example ? " (an example from the description)" : " (hidden test)"}
          </h4>
          <CaseDetail c={s.failing} fields={fields} />
        </>
      )}
    </div>
  );
}

function CaseDetail({ c, fields }: { c: CaseResult; fields: { name: string }[] }) {
  return (
    <div className="case-detail">
      {fields.map((f, j) => (
        <div key={f.name} className="io"><span>{f.name}</span><pre>{c.args[j]}</pre></div>
      ))}
      {c.error ? (
        <div className="io"><span>Error</span><pre className="errbox">{c.error}</pre></div>
      ) : (
        <div className="io"><span>Output</span><pre className={c.ok ? "" : "bad"}>{c.output ?? "—"}</pre></div>
      )}
      <div className="io"><span>Expected</span><pre>{c.input_error ?? c.expected ?? "—"}</pre></div>
      {c.stdout ? <div className="io"><span>Stdout</span><pre>{c.stdout}</pre></div> : null}
    </div>
  );
}

// ---------------------------------------------------------------- submissions
function SubmissionsList({ subs, onLoad }: { subs: Submission[] | null; onLoad: (code: string) => void }) {
  const [open, setOpen] = useState<string | null>(null);
  if (subs === null) return <p className="muted">Loading submissions…</p>;
  if (subs.length === 0) return <p className="muted">No submissions in this session yet.</p>;
  return (
    <ul className="subs">
      {subs.map((s) => (
        <li key={s.id}>
          <button className="sub-row" onClick={() => setOpen(open === s.id ? null : s.id)}>
            <span className={`verdict-inline ${verdictTone(s.verdict)}`}>{s.verdict}</span>
            <span className="muted">{s.passed}/{s.total}</span>
            <span className="muted">{s.runtime_ms != null ? `${s.runtime_ms} ms` : ""}</span>
            <span className="grow" />
            <span className="muted">{timeAgo(s.created_at)}</span>
          </button>
          {open === s.id && (
            <div className="sub-code">
              <pre>{s.code}</pre>
              <button className="btn" onClick={() => onLoad(s.code)}>Load into editor</button>
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}

function clamp(v: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, v));
}
