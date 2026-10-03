import { useState } from "react";
import { type LanguageCode, isLanguageCode } from "./i18n";
import ChatPage from "./pages/ChatPage";
import LanguagePage from "./pages/LanguagePage";

const STORAGE_KEY = "uruguay-guide";

function loadLanguage(): LanguageCode | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null");
    const language = (parsed as { language?: unknown } | null)?.language;
    return isLanguageCode(language) ? language : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [language, setLanguage] = useState<LanguageCode | null>(loadLanguage);

  function select(next: LanguageCode) {
    setLanguage(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ language: next }));
    } catch {
      // storage unavailable (private mode): keep the choice in memory only
    }
  }

  return language ? (
    <ChatPage language={language} onNewConversation={() => setLanguage(null)} />
  ) : (
    <LanguagePage onSelect={select} />
  );
}
