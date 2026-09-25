import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type ProblemSummary } from "../api";
import Markdown from "../components/Markdown";
import { Progress } from "../components/ui";
import { APPROACH_GUIDE, PATTERNS } from "../content/patterns";
import { useSession } from "../session";

export default function PatternsPage() {
  const { current } = useSession();
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [showGuide, setShowGuide] = useState(false);

  useEffect(() => {
    api
      .problems(current?.id)
      .then((r) => setProblems(r.problems))
      .catch(() => setProblems([]));
  }, [current?.id]);

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">Learn</p>
          <h1>Coding interview patterns</h1>
          <p className="lede">
            Most interview questions are variations on about fifteen patterns. Learn to spot the signals, keep a Python
            template in your head, then practise the linked problems until the pattern is automatic.
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
            <b>How to approach any interview problem</b>
            <span className="muted">
              {" "}
              — clarify, brute force, optimise, code, verify, plus a complexity cheat sheet
            </span>
          </span>
          <span>{showGuide ? "−" : "+"}</span>
        </button>
        {showGuide && (
          <div className="guide-body">
            <Markdown>{APPROACH_GUIDE}</Markdown>
          </div>
        )}
      </section>

      <div className="pattern-grid">
        {PATTERNS.map((p, i) => {
          const list = problems.filter((x) => x.pattern === p.slug);
          const solved = list.filter((x) => x.status === "solved").length;
          return (
            <Link key={p.slug} to={`/patterns/${p.slug}`} className="pattern-card">
              <span className="num mono">{String(i + 1).padStart(2, "0")}</span>
              <h3>{p.title}</h3>
              <p>{p.summary}</p>
              <p className="signals">
                <b>Signals:</b> {p.signals.join(" · ")}
              </p>
              <Progress
                value={solved}
                total={list.length}
                label={`${list.length} practice problem${list.length === 1 ? "" : "s"}`}
              />
            </Link>
          );
        })}
      </div>
    </main>
  );
}
