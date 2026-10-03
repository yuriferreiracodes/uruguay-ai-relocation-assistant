from dataclasses import dataclass

ALLOWED_DOMAINS = ("gub.uy", "impo.com.uy", "corteelectoral.gub.uy")

# Categories whose answers must be grounded in official content.
OFFICIAL_CATEGORIES = frozenset(
    {"nationality", "citizenship", "residency", "immigration", "documents", "taxes"}
)


@dataclass(frozen=True)
class OfficialSource:
    title: str
    url: str
    categories: frozenset[str]


SOURCES: tuple[OfficialSource, ...] = (
    OfficialSource(
        "Residencia Legal (gub.uy)",
        "https://www.gub.uy/tramites/residencia-legal",
        frozenset({"residency", "immigration", "documents"}),
    ),
    OfficialSource(
        "Dirección Nacional de Migración",
        "https://www.gub.uy/ministerio-interior/direccion-nacional-migracion",
        frozenset({"residency", "immigration", "documents"}),
    ),
    OfficialSource(
        "Dirección Nacional de Identificación Civil",
        "https://www.gub.uy/ministerio-interior/direccion-nacional-identificacion-civil",
        frozenset({"documents", "residency"}),
    ),
    OfficialSource(
        "Cédula de identidad (gub.uy)",
        "https://www.gub.uy/tramites/cedula-identidad",
        frozenset({"documents"}),
    ),
    OfficialSource(
        "Corte Electoral — Ciudadanía",
        "https://www.corteelectoral.gub.uy",
        frozenset({"citizenship", "nationality"}),
    ),
    OfficialSource(
        "IMPO — Ley 16.021 (ciudadanía)",
        "https://www.impo.com.uy/bases/leyes/16021-1989",
        frozenset({"citizenship", "nationality"}),
    ),
    OfficialSource(
        "Ministerio de Relaciones Exteriores",
        "https://www.gub.uy/ministerio-relaciones-exteriores",
        frozenset({"nationality", "documents", "immigration"}),
    ),
    OfficialSource(
        "IMPO — Normativa vigente",
        "https://www.impo.com.uy",
        frozenset({"taxes", "residency", "nationality", "citizenship"}),
    ),
)


def sources_for(category: str, limit: int = 3) -> list[OfficialSource]:
    return [s for s in SOURCES if category in s.categories][:limit]
