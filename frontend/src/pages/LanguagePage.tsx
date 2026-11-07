import Flag from "../components/Flag";
import { LANGUAGES, type LanguageCode, t } from "../i18n";

interface Props {
  onSelect: (language: LanguageCode) => void;
}

export default function LanguagePage({ onSelect }: Props) {
  const en = t("en");
  return (
    <main className="card language-page">
      <h1>
        {en.title} <Flag country="uy" className="flag title-flag" />
      </h1>
      <p className="muted">{en.tagline}</p>
      <h2>{en.chooseLanguage}</h2>
      <div className="language-grid">
        {LANGUAGES.map((l) => (
          <button key={l.code} className="btn language-btn" onClick={() => onSelect(l.code)}>
            <Flag country={l.flag} /> {l.name}
          </button>
        ))}
      </div>
    </main>
  );
}
