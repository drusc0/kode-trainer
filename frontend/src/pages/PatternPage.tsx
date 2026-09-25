import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type ProblemSummary } from "../api";
import Markdown from "../components/Markdown";
import { DifficultyTag, StatusMark } from "../components/ui";
import { PATTERNS, patternBody } from "../content/patterns";
import { useSession } from "../session";

export default function PatternPage() {
  const { slug = "" } = useParams();
  const { current } = useSession();
  const [problems, setProblems] = useState<ProblemSummary[] | null>(null);
  const idx = PATTERNS.findIndex((p) => p.slug === slug);
  const pattern = PATTERNS[idx];

  useEffect(() => {
    api
      .problems(current?.id)
      .then((r) => setProblems(r.problems.filter((p) => p.pattern === slug)))
      .catch(() => setProblems([]));
  }, [current?.id, slug]);

  if (!pattern)
    return (
      <main className="page">
        <h1>Unknown pattern</h1>
        <Link to="/patterns">Back to patterns</Link>
      </main>
    );
  const prev = PATTERNS[idx - 1];
  const next = PATTERNS[idx + 1];

  return (
    <main className="page pattern-page">
      <Link to="/patterns" className="back">
        ← All patterns
      </Link>
      <p className="eyebrow">
        Pattern {idx + 1} of {PATTERNS.length}
      </p>
      <h1>{pattern.title}</h1>
      <p className="lede">{pattern.summary}</p>

      <div className="pattern-layout">
        <article>
          <Markdown>{patternBody(slug)}</Markdown>
        </article>
        <aside className="practice">
          <h3>Practise it</h3>
          {problems === null ? (
            <p className="muted">Loading…</p>
          ) : problems.length === 0 ? (
            <p className="muted">No problems yet.</p>
          ) : (
            <ul>
              {problems.map((p) => (
                <li key={p.slug}>
                  <StatusMark status={p.status} />
                  <Link to={`/problems/${p.slug}`}>{p.title}</Link>
                  <DifficultyTag d={p.difficulty} />
                </li>
              ))}
            </ul>
          )}
          <p className="muted small">Status shown for session “{current?.name}”.</p>
        </aside>
      </div>

      <nav className="pager">
        {prev ? <Link to={`/patterns/${prev.slug}`}>← {prev.title}</Link> : <span />}
        {next ? <Link to={`/patterns/${next.slug}`}>{next.title} →</Link> : <span />}
      </nav>
    </main>
  );
}
