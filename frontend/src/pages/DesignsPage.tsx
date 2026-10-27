import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type DesignSummary } from "../api";
import Markdown from "../components/Markdown";
import { DifficultyTag } from "../components/ui";
import { DESIGN_APPROACH, FUNDAMENTALS } from "../content/design";

export default function DesignsPage() {
  const [designs, setDesigns] = useState<DesignSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    api.designs().then(setDesigns, (e: Error) => setError(e.message));
  }, []);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">System design</p>
          <h1>System design interviews</h1>
          <p className="lede">
            Prep the fundamentals first, then sketch a design on the whiteboard (it works with an Apple Pencil) and let
            the AI interviewer review it and push you through deep-dive follow-ups.
          </p>
        </div>
      </div>

      <section className="guide">
        <button
          type="button"
          className="guide-toggle"
          onClick={() => setShowGuide((v) => !v)}
          aria-expanded={showGuide}
        >
          <span>
            <b>How to run a system design interview</b>
            <span className="muted"> — requirements, estimates, API, high-level design, deep dives, wrap-up</span>
          </span>
          <span>{showGuide ? "−" : "+"}</span>
        </button>
        {showGuide && (
          <div className="guide-body">
            <Markdown>{DESIGN_APPROACH}</Markdown>
          </div>
        )}
      </section>

      <h2>Prep the fundamentals</h2>
      <div className="pattern-grid">
        {FUNDAMENTALS.map((f, i) => (
          <Link key={f.slug} to={`/design/learn/${f.slug}`} className="pattern-card">
            <span className="num mono">{String(i + 1).padStart(2, "0")}</span>
            <h3>{f.title}</h3>
            <p>{f.summary}</p>
          </Link>
        ))}
      </div>

      <h2>Design questions</h2>
      {error && <div className="notice fail">{error}</div>}
      <div className="table-wrap">
        <table className="ptable">
          <thead>
            <tr>
              <th>Question</th>
              <th>Technologies</th>
              <th>Difficulty</th>
            </tr>
          </thead>
          <tbody>
            {designs?.map((d) => (
              <tr key={d.slug}>
                <td>
                  <Link to={`/design/${d.slug}`} className="ptitle">
                    {d.title}
                  </Link>
                  <div className="topics">{d.summary}</div>
                </td>
                <td className="topics">{d.tags.join(" · ")}</td>
                <td>
                  <DifficultyTag d={d.difficulty} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {designs === null && !error && <p className="empty">Loading…</p>}
      </div>
    </main>
  );
}
