import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { api, type ChatMessage } from "../api";
import Markdown from "./Markdown";

// Stays mounted while hidden so an in-flight reply (or its error and the restored draft) survives tab switches.
export default function ChatPanel({ sessionId, slug, code, hidden }: { sessionId: string; slug: string; code: string; hidden: boolean }) {
  const [messages, setMessages] = useState<ChatMessage[] | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    api.chat(sessionId, slug).then(
      (h) => !cancelled && setMessages(h.messages),
      (e: Error) => !cancelled && setError(e.message),
    );
    return () => { cancelled = true; };
  }, [sessionId, slug]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages, busy, hidden]);

  const send = async () => {
    const text = draft.trim();
    if (!text || busy) return;
    setBusy(true);
    setError(null);
    setDraft("");
    setMessages((m) => [...(m ?? []), { role: "user", content: text }]);
    try {
      const { message } = await api.sendChat(sessionId, slug, text, code);
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
    await api.clearChat(sessionId, slug);
    setMessages([]);
  };

  return (
    <div className="chat" hidden={hidden}>
      {messages === null && !error && <p className="muted">Loading chat…</p>}
      {messages?.length === 0 && (
        <p className="muted">
          Talk the problem through: ask for a hint, another example, edge cases, or feedback on your code.
          Your current code is shared with every message.
        </p>
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
          placeholder="Ask your colleague… (Enter to send, Shift+Enter for a new line)"
          aria-label="Message"
          disabled={busy}
        />
        <div className="chat-actions">
          <button className="btn primary" onClick={() => void send()} disabled={busy || !draft.trim()}>Send</button>
          <div className="grow" />
          {!!messages?.length && <button className="linkish" onClick={() => void clear()} disabled={busy}>Clear chat</button>}
        </div>
      </div>
    </div>
  );
}
