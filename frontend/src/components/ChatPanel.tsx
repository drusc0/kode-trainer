import { type KeyboardEvent, useEffect, useRef, useState } from "react";
import { api, type ChatMessage } from "../api";
import Markdown from "./Markdown";

// Stays mounted while hidden so an in-flight reply (or its error and the restored draft) survives tab switches.
export default function ChatPanel({
  path,
  code = "",
  hidden = false,
  intro,
  placeholder,
  suggestions = [],
}: {
  path: string;
  code?: string;
  hidden?: boolean;
  intro: string;
  placeholder: string;
  suggestions?: string[];
}) {
  const [messages, setMessages] = useState<ChatMessage[] | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    api.chat(path).then(
      (h) => !cancelled && setMessages(h.messages),
      (e: Error) => !cancelled && setError(e.message),
    );
    return () => {
      cancelled = true;
    };
  }, [path]);

  // Skip the history load itself: below a long pattern guide it would yank the page down to the chat.
  const loaded = useRef(false);
  // biome-ignore lint/correctness/useExhaustiveDependencies: these are re-scroll triggers, not values read inside
  useEffect(() => {
    if (!loaded.current) {
      loaded.current = messages !== null;
      return;
    }
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages, busy, hidden]);

  const send = async (text = draft.trim()) => {
    if (!text || busy) return;
    setBusy(true);
    setError(null);
    setDraft("");
    setMessages((m) => [...(m ?? []), { role: "user", content: text }]);
    try {
      const { message } = await api.sendChat(path, text, code);
      setMessages((m) => [...(m ?? []), message]);
    } catch (e) {
      setMessages((m) => (m ?? []).slice(0, -1));
      setDraft(text);
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const clear = async () => {
    await api.clearChat(path);
    setMessages([]);
  };

  return (
    <div className="chat" hidden={hidden}>
      {messages === null && !error && <p className="muted">Loading chat…</p>}
      {messages?.length === 0 && (
        <>
          <p className="muted">{intro}</p>
          {suggestions.length > 0 && (
            <div className="chat-suggestions">
              {suggestions.map((s) => (
                <button key={s} type="button" className="chip" onClick={() => void send(s)} disabled={busy}>
                  {s}
                </button>
              ))}
            </div>
          )}
        </>
      )}
      {messages?.map((m, i) => (
        <div key={i} className={`chat-msg ${m.role}`}>
          {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
        </div>
      ))}
      {busy && <p className="muted">Thinking…</p>}
      {error && <div className="notice fail">{error}</div>}
      <div ref={endRef} />
      <div className="chat-compose">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          aria-label="Message"
          disabled={busy}
        />
        <div className="chat-actions">
          <button type="button" className="btn primary" onClick={() => void send()} disabled={busy || !draft.trim()}>
            Send
          </button>
          <div className="grow" />
          {!!messages?.length && (
            <button type="button" className="linkish" onClick={() => void clear()} disabled={busy}>
              Clear chat
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
