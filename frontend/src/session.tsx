import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { api, type Session, type Target } from "./api";

const CURRENT_KEY = "kodetrain:session";

interface SessionCtx {
  sessions: Session[];
  current: Session | null;
  loading: boolean;
  error: string | null;
  switchTo: (id: string) => void;
  refresh: () => Promise<void>;
  create: (name: string, target: Target, notes: string) => Promise<Session>;
}

const Ctx = createContext<SessionCtx | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(() => localStorage.getItem(CURRENT_KEY));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const creatingDefault = useRef(false);

  const refresh = useCallback(async () => {
    try {
      let list = await api.sessions();
      if (list.length === 0 && !creatingDefault.current) {
        creatingDefault.current = true; // StrictMode runs effects twice; only create one default session
        list = [await api.createSession({ name: "General practice", target: "general", notes: "" })];
      }
      setSessions(list);
      setCurrentId((id) => (id && list.some((s) => s.id === id) ? id : list[0]?.id ?? null));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (currentId) localStorage.setItem(CURRENT_KEY, currentId);
  }, [currentId]);

  const create = useCallback(async (name: string, target: Target, notes: string) => {
    const s = await api.createSession({ name, target, notes });
    setSessions((list) => [s, ...list]);
    setCurrentId(s.id);
    return s;
  }, []);

  const current = sessions.find((s) => s.id === currentId) ?? null;
  return (
    <Ctx.Provider value={{ sessions, current, loading, error, switchTo: setCurrentId, refresh, create }}>
      {children}
    </Ctx.Provider>
  );
}

export function useSession(): SessionCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useSession must be used inside SessionProvider");
  return ctx;
}

// ---------------------------------------------------------------- theme
const THEME_KEY = "kodetrain:theme";
type Theme = "light" | "dark";

function systemTheme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function useTheme(): [Theme, () => void] {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem(THEME_KEY) as Theme | null) ?? systemTheme());
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);
  return [theme, () => setTheme((t) => (t === "dark" ? "light" : "dark"))];
}

export const ThemeContext = createContext<Theme>("light");
export const useThemeValue = () => useContext(ThemeContext);
