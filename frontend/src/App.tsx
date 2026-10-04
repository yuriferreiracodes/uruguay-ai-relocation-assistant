import { useState } from "react";
import type { LanguageCode } from "./i18n";
import ChatPage from "./pages/ChatPage";
import LanguagePage from "./pages/LanguagePage";
import { clearConversation, load, saveLanguage } from "./storage";

export default function App() {
  const [language, setLanguage] = useState<LanguageCode | null>(() => load().language);

  function select(next: LanguageCode) {
    setLanguage(next);
    saveLanguage(next);
  }

  // Starting over also drops the stored conversation, so a reload cannot bring it back.
  function newConversation() {
    clearConversation();
    setLanguage(null);
  }

  return language ? (
    <ChatPage language={language} onNewConversation={newConversation} />
  ) : (
    <LanguagePage onSelect={select} />
  );
}
