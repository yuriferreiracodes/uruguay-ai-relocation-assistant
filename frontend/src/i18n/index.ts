import de from "./de.json";
import en from "./en.json";
import es from "./es.json";
import fr from "./fr.json";
import it from "./it.json";
import ptBR from "./pt-BR.json";

export type LanguageCode = "pt-BR" | "es" | "en" | "fr" | "de" | "it";
export type Translations = typeof en;

export const LANGUAGES: { code: LanguageCode; name: string; flag: string }[] = [
  { code: "pt-BR", name: "Português", flag: "🇧🇷" },
  { code: "es", name: "Español", flag: "🇪🇸" },
  { code: "en", name: "English", flag: "🇬🇧" },
  { code: "fr", name: "Français", flag: "🇫🇷" },
  { code: "de", name: "Deutsch", flag: "🇩🇪" },
  { code: "it", name: "Italiano", flag: "🇮🇹" },
];

const translations: Record<LanguageCode, Translations> = {
  "pt-BR": ptBR,
  es,
  en,
  fr,
  de,
  it,
};

export const t = (language: LanguageCode): Translations => translations[language];

export const isLanguageCode = (value: unknown): value is LanguageCode =>
  LANGUAGES.some((l) => l.code === value);
