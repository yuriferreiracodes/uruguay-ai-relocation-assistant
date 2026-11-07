import { useState } from "react";
import type { LanguageCode } from "./i18n";
import ChatPage from "./pages/ChatPage";
import LanguagePage from "./pages/LanguagePage";

// Older versions saved the language and conversation here. Nothing is stored anymore,
// so remove any leftover data from the browser.
try {
  localStorage.removeItem("uruguay-guide");
} catch {
  // storage unavailable (private mode): nothing to clean up
}

// Every visit starts at the language picker with an empty conversation.
export default function App() {
  const [language, setLanguage] = useState<LanguageCode | null>(null);

  return language ? (
    <ChatPage language={language} onNewConversation={() => setLanguage(null)} />
  ) : (
    <LanguagePage onSelect={setLanguage} />
  );
}
