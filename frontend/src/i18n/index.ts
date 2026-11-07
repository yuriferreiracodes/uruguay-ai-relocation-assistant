import type { Country } from "../components/Flag";
import de from "./de.json";
import en from "./en.json";
import es from "./es.json";
import fr from "./fr.json";
import it from "./it.json";
import ptBR from "./pt-BR.json";

export type LanguageCode = "pt-BR" | "es" | "en" | "fr" | "de" | "it";
export type Translations = typeof en;

export const LANGUAGES: { code: LanguageCode; name: string; flag: Country }[] = [
  { code: "pt-BR", name: "Português", flag: "br" },
  { code: "es", name: "Español", flag: "es" },
  { code: "en", name: "English", flag: "gb" },
  { code: "fr", name: "Français", flag: "fr" },
  { code: "de", name: "Deutsch", flag: "de" },
  { code: "it", name: "Italiano", flag: "it" },
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
