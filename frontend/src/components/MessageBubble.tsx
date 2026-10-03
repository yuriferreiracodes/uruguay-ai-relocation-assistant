import type { Message } from "../api/chat";
import type { Translations } from "../i18n";

interface Props {
  message: Message;
  text: Translations;
}

// Turns **bold** markers into <strong> without using innerHTML.
function renderBold(content: string) {
  return content
    .split(/\*\*(.+?)\*\*/gs)
    .map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

export default function MessageBubble({ message, text }: Props) {
  return (
    <div className={`bubble ${message.role}`}>
      <p>{renderBold(message.content)}</p>
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
                  <span className="muted"> · {text.retrievedOn.replace("{date}", s.retrieved_at)}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
