import type { Difficulty, Status } from "../api";

export function DifficultyTag({ d }: { d: Difficulty }) {
  return <span className={`diff ${d.toLowerCase()}`}>{d}</span>;
}

export function StatusMark({ status }: { status: Status }) {
  if (status === "solved") return <span className="status solved" title="Solved in this session">✓</span>;
  if (status === "attempted") return <span className="status attempted" title="Attempted, not solved yet">◐</span>;
  return <span className="status none" aria-hidden="true" />;
}

export function Progress({ value, total, label, tone }: { value: number; total: number; label?: string; tone?: string }) {
  const pct = total ? Math.round((value / total) * 100) : 0;
  return (
    <div className="progress">
      {label && (
        <div className="progress-head">
          <span>{label}</span>
          <span className="mono">{value}/{total}</span>
        </div>
      )}
      <div className="bar"><div className={`fill ${tone ?? ""}`} style={{ width: `${pct}%` }} /></div>
    </div>
  );
}

/** The KodeTrain signature: one cell per test case. */
export function ResultStrip({ cells }: { cells: ("pass" | "fail" | "skip")[] }) {
  const shown = cells.length > 60 ? compress(cells) : cells;
  return (
    <div className="strip" aria-label={`${cells.filter((c) => c === "pass").length} of ${cells.length} passed`}>
      {shown.map((c, i) => <i key={i} className={`c ${c}`} />)}
    </div>
  );
}

function compress(cells: ("pass" | "fail" | "skip")[]) {
  const step = cells.length / 60;
  return Array.from({ length: 60 }, (_, i) => {
    const slice = cells.slice(Math.floor(i * step), Math.floor((i + 1) * step));
    return slice.includes("fail") ? "fail" : slice.includes("skip") ? "skip" : "pass";
  });
}

export function verdictTone(v: string): "pass" | "fail" | "warn" {
  if (v === "Accepted") return "pass";
  if (v === "Invalid Input") return "warn";
  return "fail";
}
