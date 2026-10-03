import { type FormEvent, useEffect, useRef, useState } from "react";
import { type Message, sendChat } from "../api/chat";
import MessageBubble from "../components/MessageBubble";
import { LANGUAGES, type LanguageCode, t } from "../i18n";

interface Props {
  language: LanguageCode;
  onChangeLanguage: (language: LanguageCode) => void;
}

interface Pending {
  text: string;
  history: Message[];
}

export default function ChatPage({ language, onChangeLanguage }: Props) {
  const text = t(language);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState<Pending | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, failed]);

  async function run(pending: Pending) {
    setLoading(true);
    setFailed(null);
    try {
      const res = await sendChat(language, pending.text, pending.history);
      setMessages((m) => [...m, { role: "assistant", content: res.answer, sources: res.sources }]);
    } catch {
      setFailed(pending);
    } finally {
      setLoading(false);
    }
  }

  function send(raw: string) {
    const question = raw.trim();
    if (!question || loading) return;
    setInput("");
    const pending = { text: question, history: messages };
    setMessages([...messages, { role: "user", content: question }]);
    void run(pending);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    send(input);
  }

  function reset() {
    setMessages([]);
    setFailed(null);
    setInput("");
  }

  return (
    <main className="card chat-page">
      <header className="chat-header">
        <div>
          <h1>{text.title} 🇺🇾</h1>
          <p className="muted">{text.tagline}</p>
        </div>
        <div className="header-actions">
          <select
            aria-label={text.language}
            value={language}
            onChange={(e) => onChangeLanguage(e.target.value as LanguageCode)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.flag} {l.name}
              </option>
            ))}
          </select>
          <button className="btn small" onClick={reset} disabled={loading}>
            {text.newConversation}
          </button>
        </div>
      </header>

      {messages.length === 0 && (
        <section className="chips-section">
          <p className="muted">{text.suggested}</p>
          <div className="chips">
            {text.chips.map((c) => (
              <button key={c.label} className="btn chip" onClick={() => send(c.question)}>
                {c.label}
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="messages" aria-live="polite">
        <div className="bubble assistant">
          <p>{text.greeting}</p>
        </div>
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} text={text} />
        ))}
        {loading && <div className="bubble assistant loading">{text.thinking}</div>}
        {failed && (
          <div className="error" role="alert">
            {text.error}{" "}
            <button className="btn small" onClick={() => void run(failed)}>
              {text.retry}
            </button>
          </div>
        )}
        <div ref={bottomRef} />
      </section>

      <form className="composer" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={text.placeholder}
          maxLength={2000}
          aria-label={text.placeholder}
        />
        <button className="btn primary" type="submit" disabled={loading || !input.trim()}>
          {text.send}
        </button>
      </form>
      <p className="disclaimer muted">{text.disclaimer}</p>
    </main>
  );
}
