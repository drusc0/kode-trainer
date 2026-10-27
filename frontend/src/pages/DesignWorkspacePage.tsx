import { Excalidraw, exportToBlob, getSceneVersion, serializeAsJSON } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";
import type { ExcalidrawImperativeAPI } from "@excalidraw/excalidraw/types";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type DesignChatAttachment, type DesignDetail, designChatPath } from "../api";
import ChatPanel from "../components/ChatPanel";
import { DifficultyTag } from "../components/ui";
import { fundamentalTitle } from "../content/design";
import { useSession, useThemeValue } from "../session";

// Fonts are copied next to the app in the Docker build; Excalidraw falls back to its CDN when they're missing (dev).
(window as unknown as { EXCALIDRAW_ASSET_PATH: string }).EXCALIDRAW_ASSET_PATH = "/";

const INTERVIEWER_STARTERS = [
  "Review my design so far",
  "Start the deep dive: ask me follow-up questions",
  "What am I missing from the requirements?",
  "Challenge my estimates",
  "Grade me like a real interview",
];

const blobToBase64 = (blob: Blob) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string).split(",")[1] ?? "");
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(blob);
  });

export default function DesignWorkspacePage() {
  const { slug = "" } = useParams();
  const { current } = useSession();
  const sessionId = current?.id ?? "";
  const theme = useThemeValue();
  const [design, setDesign] = useState<DesignDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"brief" | "chat">("brief");
  const [sideOpen, setSideOpen] = useState(true);
  const [notes, setNotes] = useState("");
  const [saveState, setSaveState] = useState<"" | "saving" | "saved" | "error">("");
  const excalidraw = useRef<ExcalidrawImperativeAPI | null>(null);
  const notesRef = useRef("");
  const savedVersion = useRef<number | null>(null);
  const saveTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    api.design(slug, sessionId).then(
      (d) => {
        setDesign(d);
        setNotes(d.notes);
        notesRef.current = d.notes;
      },
      (e: Error) => setError(e.message),
    );
  }, [slug, sessionId]);

  const save = useCallback(async () => {
    const ex = excalidraw.current;
    if (!ex) return;
    window.clearTimeout(saveTimer.current);
    saveTimer.current = undefined;
    const elements = ex.getSceneElementsIncludingDeleted();
    savedVersion.current = getSceneVersion(elements);
    setSaveState("saving");
    try {
      const scene = serializeAsJSON(elements, ex.getAppState(), ex.getFiles(), "local");
      await api.saveDesignDraft(sessionId, slug, { scene, notes: notesRef.current });
      setSaveState("saved");
    } catch {
      setSaveState("error");
    }
  }, [sessionId, slug]);

  const scheduleSave = useCallback(() => {
    window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => void save(), 1500);
  }, [save]);

  // Flush a pending save when leaving the page, so the last strokes aren't lost.
  useEffect(
    () => () => {
      if (saveTimer.current !== undefined) void save();
    },
    [save],
  );

  const attach = useCallback(async (): Promise<DesignChatAttachment> => {
    const ex = excalidraw.current;
    const elements = ex?.getSceneElements() ?? [];
    if (!ex || elements.length === 0) return { notes: notesRef.current };
    const blob = await exportToBlob({
      elements,
      appState: { ...ex.getAppState(), exportBackground: true, exportWithDarkMode: false, viewBackgroundColor: "#fff" },
      files: ex.getFiles(),
      mimeType: "image/png",
      maxWidthOrHeight: 1568, // Claude downsizes anything larger
    });
    return { notes: notesRef.current, diagram: await blobToBase64(blob) };
  }, []);

  if (error)
    return (
      <main className="page">
        <div className="notice fail">{error}</div>
        <Link to="/design">Back to system design</Link>
      </main>
    );
  if (!design)
    return (
      <main className="page">
        <p className="muted">Loading…</p>
      </main>
    );

  return (
    <main className={`design-ws${sideOpen ? "" : " side-closed"}`}>
      <div className="design-canvas">
        <Excalidraw
          theme={theme}
          initialData={design.scene ? JSON.parse(design.scene) : null}
          excalidrawAPI={(a) => {
            excalidraw.current = a;
          }}
          onChange={(elements) => {
            const v = getSceneVersion(elements);
            if (savedVersion.current === null) savedVersion.current = v;
            else if (v !== savedVersion.current) scheduleSave();
          }}
        />
        {!sideOpen && (
          <button type="button" className="btn side-toggle" onClick={() => setSideOpen(true)}>
            Brief & interviewer
          </button>
        )}
      </div>

      <aside className="panel design-side" hidden={!sideOpen}>
        <div className="tabs">
          <button type="button" className={tab === "brief" ? "on" : ""} onClick={() => setTab("brief")}>
            Brief
          </button>
          <button type="button" className={tab === "chat" ? "on" : ""} onClick={() => setTab("chat")}>
            Interviewer
          </button>
          <div className="grow" />
          <span className="save-state">
            {saveState === "saving"
              ? "Saving…"
              : saveState === "saved"
                ? "Saved"
                : saveState === "error"
                  ? "Not saved"
                  : ""}
          </span>
          <button type="button" className="ghost" onClick={() => setSideOpen(false)} title="More room to draw">
            Hide
          </button>
          <Link to="/design" className="back">
            ← All
          </Link>
        </div>
        <div className="panel-body">
          {tab === "brief" && (
            <article className="statement">
              <h1 className="ptitle-lg">{design.title}</h1>
              <div className="meta">
                <DifficultyTag d={design.difficulty} />
                {design.tags.map((t) => (
                  <span key={t} className="chip">
                    {t}
                  </span>
                ))}
              </div>
              <p>{design.prompt}</p>
              <h3>Functional requirements</h3>
              <ul className="constraints">
                {design.functional.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
              <h3>Non-functional requirements</h3>
              <ul className="constraints">
                {design.non_functional.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
              <h3>Scale</h3>
              <ul className="constraints">
                {design.scale.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
              <h3>Prep first</h3>
              <div className="meta">
                {design.fundamentals.map((f) => (
                  <Link key={f} to={`/design/learn/${f}`} className="chip">
                    {fundamentalTitle(f)}
                  </Link>
                ))}
              </div>
              <label className="field">
                <span>
                  Notes <em>requirements, estimates, API, data model: shared with the interviewer</em>
                </span>
                <textarea
                  className="design-notes"
                  value={notes}
                  onChange={(e) => {
                    setNotes(e.target.value);
                    notesRef.current = e.target.value;
                    scheduleSave();
                  }}
                  placeholder={"QPS: …\nStorage: …\nPOST /…"}
                />
              </label>
            </article>
          )}
          <ChatPanel
            key={slug}
            path={designChatPath(sessionId, slug)}
            attach={attach}
            hidden={tab !== "chat"}
            intro="Draw your design, then ask for a review. Every message sends a snapshot of the whiteboard and your notes, so the interviewer always sees your latest version and will dig into it with follow-up questions."
            placeholder="Explain your design or answer the interviewer… (Enter to send)"
            suggestions={INTERVIEWER_STARTERS}
          />
        </div>
      </aside>
    </main>
  );
}
