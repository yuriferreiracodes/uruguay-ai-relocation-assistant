import type { ReactNode } from "react";
import type { Message } from "../api/chat";
import type { Translations } from "../i18n";

interface Props {
  message: Message;
  text: Translations;
}

// **bold** or [label](http(s)://url). Only http(s) links, so "javascript:" URLs never render.
const INLINE = /\*\*(.+?)\*\*|\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/gs;

// Turns **bold** and [links](url) into React elements without using innerHTML.
function renderInline(content: string, keyPrefix = ""): ReactNode[] {
  const nodes: ReactNode[] = [];
  let last = 0;
  for (const match of content.matchAll(INLINE)) {
    const start = match.index ?? 0;
    if (start > last) nodes.push(content.slice(last, start));
    const key = `${keyPrefix}${start}`;
    const [, bold, label, url] = match;
    if (bold !== undefined) {
      nodes.push(<strong key={key}>{renderInline(bold, `${key}-`)}</strong>);
    } else {
      nodes.push(
        <a key={key} href={url} target="_blank" rel="noopener noreferrer">
          {label}
        </a>,
      );
    }
    last = start + match[0].length;
  }
  if (last < content.length) nodes.push(content.slice(last));
  return nodes;
}

// "2026-11-05" -> "11/05/2026" (US format). Parsed by hand to avoid time zone shifts.
function formatUsDate(isoDate: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(isoDate);
  return match ? `${match[2]}/${match[3]}/${match[1]}` : isoDate;
}

export default function MessageBubble({ message, text }: Props) {
  return (
    <div className={`bubble ${message.role}`}>
      <p>{renderInline(message.content)}</p>
      {message.sources && message.sources.length > 0 && (
        <div className="sources">
          <strong>{text.officialSources}</strong>
          <ul>
            {message.sources.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  {s.title}
                </a>
                {s.retrieved_at && (
                  <span className="muted">
                    {" "}
                    · {text.retrievedOn.replace("{date}", formatUsDate(s.retrieved_at))}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
