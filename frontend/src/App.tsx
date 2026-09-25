import { Navigate, NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { TARGET_LABEL } from "./api";
import PatternPage from "./pages/PatternPage";
import PatternsPage from "./pages/PatternsPage";
import ProblemsPage from "./pages/ProblemsPage";
import SessionsPage from "./pages/SessionsPage";
import WorkspacePage from "./pages/WorkspacePage";
import { ThemeContext, useSession, useTheme } from "./session";

export default function App() {
  const [theme, toggleTheme] = useTheme();
  const { sessions, current, switchTo, loading, error } = useSession();
  const navigate = useNavigate();

  return (
    <ThemeContext.Provider value={theme}>
      <header className="topbar">
        <NavLink to="/problems" className="brand">
          <span className="brand-mark" aria-hidden="true">
            <i className="c pass" /><i className="c pass" /><i className="c fail" />
          </span>
          Kode<b>Train</b>
        </NavLink>
        <nav className="mainnav">
          <NavLink to="/problems">Problems</NavLink>
          <NavLink to="/patterns">Patterns</NavLink>
          <NavLink to="/sessions">Sessions</NavLink>
        </nav>
        <div className="grow" />
        {current && (
          <label className="session-switch" title="Each session has its own code, submissions and progress">
            <span className="muted">Session</span>
            <select
              value={current.id}
              onChange={(e) => {
                if (e.target.value === "__new") navigate("/sessions?new=1");
                else switchTo(e.target.value);
              }}
            >
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} · {TARGET_LABEL[s.target]}
                </option>
              ))}
              <option value="__new">+ New session…</option>
            </select>
          </label>
        )}
        <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle dark mode">
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </header>

      {error ? (
        <main className="page">
          <div className="notice fail">
            <b>Can't reach the KodeTrain API.</b> {error}
            <p className="muted">Is the backend running? Try <code>make up</code>, then reload.</p>
          </div>
        </main>
      ) : loading || !current ? (
        <main className="page"><p className="muted">Loading…</p></main>
      ) : (
        <Routes>
          <Route path="/" element={<Navigate to="/problems" replace />} />
          <Route path="/problems" element={<ProblemsPage />} />
          <Route path="/problems/:slug" element={<WorkspacePage key={current.id} />} />
          <Route path="/patterns" element={<PatternsPage />} />
          <Route path="/patterns/:slug" element={<PatternPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="*" element={<main className="page"><h1>Not found</h1></main>} />
        </Routes>
      )}
    </ThemeContext.Provider>
  );
}
