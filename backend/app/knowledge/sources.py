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
    OfficialSource(
        "Dirección General Impositiva (DGI)",
        "https://www.gub.uy/direccion-general-impositiva",
        frozenset({"taxes", "employment"}),
    ),
    OfficialSource(
        "Instituto Nacional de Estadística (INE)",
        "https://www.gub.uy/instituto-nacional-estadistica",
        frozenset({"cost_of_living", "cities", "housing"}),
    ),
    OfficialSource(
        "Ministerio de Economía y Finanzas",
        "https://www.gub.uy/ministerio-economia-finanzas",
        frozenset({"banking", "cost_of_living", "taxes"}),
    ),
    OfficialSource(
        "Ministerio de Salud Pública",
        "https://www.gub.uy/ministerio-salud-publica",
        frozenset({"healthcare"}),
    ),
    OfficialSource(
        "Banco de Previsión Social (BPS)",
        "https://www.bps.gub.uy",
        frozenset({"healthcare", "employment"}),
    ),
    OfficialSource(
        "Ministerio de Educación y Cultura",
        "https://www.gub.uy/ministerio-educacion-cultura",
        frozenset({"education", "culture"}),
    ),
    OfficialSource(
        "Ministerio de Trabajo y Seguridad Social",
        "https://www.gub.uy/ministerio-trabajo-seguridad-social",
        frozenset({"employment"}),
    ),
    OfficialSource(
        "Ministerio de Vivienda y Ordenamiento Territorial",
        "https://www.gub.uy/ministerio-vivienda-ordenamiento-territorial",
        frozenset({"housing"}),
    ),
    OfficialSource(
        "Ministerio de Transporte y Obras Públicas",
        "https://www.gub.uy/ministerio-transporte-obras-publicas",
        frozenset({"transport"}),
    ),
    OfficialSource(
        "Ministerio de Turismo",
        "https://www.gub.uy/ministerio-turismo",
        frozenset({"culture", "cities"}),
    ),
    OfficialSource(
        "Uruguay XXI",
        "https://www.uruguayxxi.gub.uy",
        frozenset({"general_uruguay", "cost_of_living", "banking", "employment"}),
    ),
    OfficialSource(
        "Portal del Estado uruguayo (gub.uy)",
        "https://www.gub.uy",
        frozenset({"general_uruguay"}),
    ),
)

# Shown when a category has no dedicated source, so every in-scope answer still cites something.
FALLBACK_CATEGORY = "general_uruguay"


def sources_for(category: str, limit: int = 3) -> list[OfficialSource]:
    matches = [s for s in SOURCES if category in s.categories]
    if not matches:
        matches = [s for s in SOURCES if FALLBACK_CATEGORY in s.categories]
    return matches[:limit]
