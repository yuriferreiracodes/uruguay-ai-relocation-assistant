import type { Message, Role, Source } from "./api/chat";
import { type LanguageCode, isLanguageCode } from "./i18n";

const STORAGE_KEY = "uruguay-guide";

interface Stored {
  language: LanguageCode | null;
  messages: Message[];
}

const EMPTY: Stored = { language: null, messages: [] };

const isRole = (value: unknown): value is Role => value === "user" || value === "assistant";

function parseSources(value: unknown): Source[] | undefined {
  if (!Array.isArray(value)) return undefined;
  const sources = value.filter(
    (s: unknown): s is Source =>
      typeof s === "object" &&
      s !== null &&
      typeof (s as Source).title === "string" &&
      typeof (s as Source).url === "string",
  );
  return sources.length > 0 ? sources : undefined;
}

function parseMessages(value: unknown): Message[] {
  if (!Array.isArray(value)) return [];
  return (value as unknown[]).flatMap((entry) => {
    if (typeof entry !== "object" || entry === null) return [];
    const { role, content, sources } = entry as Partial<Message>;
    if (!isRole(role) || typeof content !== "string") return [];
    const parsed = parseSources(sources);
    return [parsed ? { role, content, sources: parsed } : { role, content }];
  });
}

export function load(): Stored {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null");
    if (typeof parsed !== "object" || parsed === null) return EMPTY;
    const { language, messages } = parsed as { language?: unknown; messages?: unknown };
    return {
      language: isLanguageCode(language) ? language : null,
      messages: parseMessages(messages),
    };
  } catch {
    return EMPTY;
  }
}

function save(stored: Stored): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
  } catch {
    // storage unavailable (private mode) or quota exceeded: keep the state in memory only
  }
}

export function saveLanguage(language: LanguageCode): void {
  save({ ...load(), language });
}

export function saveMessages(messages: Message[]): void {
  save({ ...load(), messages });
}

export function clearConversation(): void {
  save(EMPTY);
}
