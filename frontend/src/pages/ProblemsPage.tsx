import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Difficulty, type ProblemSummary, TARGET_LABEL } from "../api";
import { DifficultyTag, Progress, StatusMark } from "../components/ui";
import { patternTitle } from "../content/patterns";
import { useSession } from "../session";

type StatusFilter = "all" | "todo" | "attempted" | "solved";

export default function ProblemsPage() {
  const { current } = useSession();
  const [problems, setProblems] = useState<ProblemSummary[] | null>(null);
  const [patterns, setPatterns] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState<"all" | Difficulty>("all");
  const [pattern, setPattern] = useState("all");
  const [company, setCompany] = useState<string>("all");
  const [status, setStatus] = useState<StatusFilter>("all");

  // biome-ignore lint/correctness/useExhaustiveDependencies: reset filters only when switching sessions, not on every session update
  useEffect(() => {
    if (!current) return;
    setCompany(current.target === "general" ? "all" : current.target); // a Google session starts on Google questions
    api
      .problems(current.id)
      .then((r) => {
        setProblems(r.problems);
        setPatterns(r.patterns);
      })
      .catch((e: Error) => setError(e.message));
  }, [current?.id]);

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return (problems ?? []).filter(
      (p) =>
        (difficulty === "all" || p.difficulty === difficulty) &&
        (pattern === "all" || p.pattern === pattern) &&
        (company === "all" || p.companies.includes(company)) &&
        (status === "all" || (status === "todo" ? !p.status : p.status === status)) &&
        (!q || p.title.toLowerCase().includes(q) || p.topics.some((t) => t.toLowerCase().includes(q))),
    );
  }, [problems, search, difficulty, pattern, company, status]);

  if (error)
    return (
      <main className="page">
        <div className="notice fail">{error}</div>
      </main>
    );
  if (!problems || !current)
    return (
      <main className="page">
        <p className="muted">Loading problems…</p>
      </main>
    );

  const scope = problems.filter((p) => company === "all" || p.companies.includes(company));
  const solved = (d?: Difficulty) => scope.filter((p) => p.status === "solved" && (!d || p.difficulty === d)).length;
  const total = (d?: Difficulty) => scope.filter((p) => !d || p.difficulty === d).length;

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">
            {current.name} · {TARGET_LABEL[current.target]}
          </p>
          <h1>Problems</h1>
        </div>
        <div className="progress-grid">
          <Progress
            label={company === "all" ? "All problems" : `${TARGET_LABEL[company as "google" | "meta"]} set`}
            value={solved()}
            total={total()}
          />
          <Progress label="Easy" value={solved("Easy")} total={total("Easy")} tone="easy" />
          <Progress label="Medium" value={solved("Medium")} total={total("Medium")} tone="medium" />
          <Progress label="Hard" value={solved("Hard")} total={total("Hard")} tone="hard" />
        </div>
      </div>

      <div className="filters">
        <input
          className="search"
          placeholder="Search titles or topics"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={company} onChange={(e) => setCompany(e.target.value)} aria-label="Company">
          <option value="all">All companies</option>
          <option value="google">Google</option>
          <option value="meta">Meta</option>
        </select>
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value as "all" | Difficulty)}
          aria-label="Difficulty"
        >
          <option value="all">Any difficulty</option>
          <option>Easy</option>
          <option>Medium</option>
          <option>Hard</option>
        </select>
        <select value={pattern} onChange={(e) => setPattern(e.target.value)} aria-label="Pattern">
          <option value="all">All patterns</option>
          {patterns.map((p) => (
            <option key={p} value={p}>
              {patternTitle(p)}
            </option>
          ))}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value as StatusFilter)} aria-label="Status">
          <option value="all">Any status</option>
          <option value="todo">To do</option>
          <option value="attempted">Attempted</option>
          <option value="solved">Solved</option>
        </select>
      </div>

      <div className="table-wrap">
        <table className="ptable">
          <thead>
            <tr>
              <th aria-label="Status" />
              <th>Title</th>
              <th>Pattern</th>
              <th>Companies</th>
              <th>Difficulty</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((p) => (
              <tr key={p.slug}>
                <td>
                  <StatusMark status={p.status} />
                </td>
                <td>
                  <Link to={`/problems/${p.slug}`} className="ptitle">
                    {p.title}
                  </Link>
                  <div className="topics">{p.topics.slice(0, 3).join(" · ")}</div>
                </td>
                <td>
                  <Link to={`/patterns/${p.pattern}`} className="chip">
                    {patternTitle(p.pattern)}
                  </Link>
                </td>
                <td className="companies">
                  {p.companies.map((c) => (
                    <span key={c} className={`co ${c}`}>
                      {TARGET_LABEL[c as "google" | "meta"]}
                    </span>
                  ))}
                </td>
                <td>
                  <DifficultyTag d={p.difficulty} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {visible.length === 0 && <p className="empty">No problems match these filters.</p>}
      </div>
    </main>
  );
}
