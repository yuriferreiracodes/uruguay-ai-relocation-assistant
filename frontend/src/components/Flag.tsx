// Flags as SVG images instead of emojis: Windows has no flag emojis, so Chrome and Edge
// there show letters ("BR", "UY") in their place. Only the flags we use are imported,
// so the bundle doesn't carry the whole flag-icons set.
import br from "flag-icons/flags/4x3/br.svg";
import de from "flag-icons/flags/4x3/de.svg";
import es from "flag-icons/flags/4x3/es.svg";
import fr from "flag-icons/flags/4x3/fr.svg";
import gb from "flag-icons/flags/4x3/gb.svg";
import it from "flag-icons/flags/4x3/it.svg";
import uy from "flag-icons/flags/4x3/uy.svg";

const FLAGS = { br, de, es, fr, gb, it, uy };

export type Country = keyof typeof FLAGS;

interface Props {
  country: Country;
  className?: string;
}

// Decorative: the language or country name is always written next to it.
export default function Flag({ country, className = "flag" }: Props) {
  return <img className={className} src={FLAGS[country]} alt="" aria-hidden="true" />;
}
