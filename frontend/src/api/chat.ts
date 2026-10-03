import type { LanguageCode } from "../i18n";

export type Role = "user" | "assistant";

export interface Source {
  title: string;
  url: string;
  retrieved_at?: string | null;
}

export interface Message {
  role: Role;
  content: string;
  sources?: Source[];
}

interface ChatResponse {
  answer: string;
  sources: Source[];
  category: string;
}

const HISTORY_LIMIT = 6;

export async function sendChat(
  language: LanguageCode,
  message: string,
  history: Message[],
): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      language,
      message,
      history: history.slice(-HISTORY_LIMIT).map(({ role, content }) => ({ role, content })),
    }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()) as ChatResponse;
}
