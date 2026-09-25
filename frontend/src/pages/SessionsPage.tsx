import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, TARGET_LABEL, timeAgo, type Session, type SessionStats, type Target } from "../api";
import { Progress, verdictTone } from "../components/ui";
import { patternTitle } from "../content/patterns";
import { useSession } from "../session";

export default function SessionsPage() {
  const { sessions, current, switchTo, refresh, create } = useSession();
  const [params, setParams] = useSearchParams();
  const [showForm, setShowForm] = useState(params.get("new") === "1");
  const [stats, setStats] = useState<SessionStats | null>(null);

  useEffect(() => {
    if (!current) return;
    setStats(null);
    api.stats(current.id).then(setStats).catch(() => setStats(null));
  }, [current?.id, current?.solved]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <main className="page">
      <div className="page-head">
        <div>
          <p className="eyebrow">Practice sessions</p>
          <h1>Sessions</h1>
          <p className="lede">Each session is a clean slate with its own drafts, submissions and progress. For example, keep one for Google prep and another for Meta.</p>
        </div>
        {!showForm && <button className="btn primary" onClick={() => setShowForm(true)}>New session</button>}
      </div>

      {showForm && (
        <NewSessionForm
          onCancel={() => { setShowForm(false); setParams({}); }}
          onCreate={async (name, target, notes) => { await create(name, target, notes); setShowForm(false); setParams({}); }}
        />
      )}

      <div className="session-list">
        {sessions.map((s) => (
          <SessionRow key={s.id} s={s} active={s.id === current?.id} onSwitch={() => switchTo(s.id)} onChanged={refresh} canDelete={sessions.length > 1} />
        ))}
      </div>

      {current && (
        <section className="stats">
          <h2>“{current.name}” at a glance</h2>
          {!stats ? <p className="muted">Loading stats…</p> : (
            <div className="stats-grid">
              <div className="card">
                <h3>By difficulty</h3>
                <Progress label="Easy" value={stats.by_difficulty.Easy.solved} total={stats.by_difficulty.Easy.total} tone="easy" />
                <Progress label="Medium" value={stats.by_difficulty.Medium.solved} total={stats.by_difficulty.Medium.total} tone="medium" />
                <Progress label="Hard" value={stats.by_difficulty.Hard.solved} total={stats.by_difficulty.Hard.total} tone="hard" />
                <p className="muted small">
                  {stats.submissions} submissions · {stats.submissions ? Math.round((stats.accepted / stats.submissions) * 100) : 0}% accepted
                </p>
              </div>
              <div className="card">
                <h3>By pattern</h3>
                <div className="pattern-bars">
                  {Object.entries(stats.by_pattern).map(([slug, b]) => (
                    <Link key={slug} to={`/patterns/${slug}`} className="plain">
                      <Progress label={patternTitle(slug)} value={b.solved} total={b.total} />
                    </Link>
                  ))}
                </div>
              </div>
              <div className="card">
                <h3>Recent submissions</h3>
                {stats.recent.length === 0 ? <p className="muted">Nothing yet. <Link to="/problems">Pick a problem</Link>.</p> : (
                  <ul className="recent">
                    {stats.recent.map((r) => (
                      <li key={r.id}>
                        <Link to={`/problems/${r.problem}`}>{r.title}</Link>
                        <span className={`verdict-inline ${verdictTone(r.verdict)}`}>{r.verdict}</span>
                        <span className="muted small">{timeAgo(r.created_at)}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

function NewSessionForm({ onCreate, onCancel }: { onCreate: (n: string, t: Target, notes: string) => Promise<void>; onCancel: () => void }) {
  const [name, setName] = useState("");
  const [target, setTarget] = useState<Target>("google");
  const [notes, setNotes] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const suggested = target === "general" ? "General practice" : `${TARGET_LABEL[target]} prep`;
  return (
    <div className="card new-session">
      <h3>New session</h3>
      <div className="form-row">
        <label>Name<input autoFocus value={name} placeholder={suggested} onChange={(e) => setName(e.target.value)} maxLength={80} /></label>
        <label>Focus
          <select value={target} onChange={(e) => setTarget(e.target.value as Target)}>
            <option value="google">Google</option>
            <option value="meta">Meta</option>
            <option value="general">General</option>
          </select>
        </label>
      </div>
      <label>Notes <span className="muted">(optional: interview date, goals)</span>
        <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} maxLength={2000} />
      </label>
      {err && <p className="notice fail">{err}</p>}
      <div className="form-actions">
        <button className="btn" onClick={onCancel}>Cancel</button>
        <button className="btn primary" onClick={() => onCreate(name.trim() || suggested, target, notes).catch((e: Error) => setErr(e.message))}>
          Create and switch
        </button>
      </div>
    </div>
  );
}

function SessionRow({ s, active, onSwitch, onChanged, canDelete }: {
  s: Session; active: boolean; onSwitch: () => void; onChanged: () => Promise<void>; canDelete: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(s.name);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const save = async () => {
    if (name.trim() && name.trim() !== s.name) await api.updateSession(s.id, { name: name.trim() });
    setEditing(false);
    await onChanged();
  };
  const del = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true);
      setTimeout(() => setConfirmDelete(false), 3000);
      return;
    }
    await api.deleteSession(s.id);
    await onChanged();
  };

  return (
    <div className={`session-row ${active ? "active" : ""}`}>
      <div className="session-main">
        {editing ? (
          <input value={name} autoFocus onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && void save()} onBlur={() => void save()} />
        ) : (
          <b>{s.name}</b>
        )}
        <span className={`co ${s.target}`}>{TARGET_LABEL[s.target]}</span>
        {active && <span className="chip">Current</span>}
        {s.notes && <p className="muted small">{s.notes}</p>}
      </div>
      <div className="session-nums">
        <span><b>{s.solved}</b> solved</span>
        <span className="muted">{s.attempted} attempted</span>
        <span className="muted">active {timeAgo(s.last_active_at)}</span>
      </div>
      <div className="session-actions">
        {!active && <button className="btn" onClick={onSwitch}>Switch</button>}
        <button className="ghost" onClick={() => setEditing(true)}>Rename</button>
        {canDelete && (
          <button className={`ghost ${confirmDelete ? "danger" : ""}`} onClick={() => void del()}>
            {confirmDelete ? "Delete all its data?" : "Delete"}
          </button>
        )}
      </div>
    </div>
  );
}
