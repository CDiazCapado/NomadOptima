"""
app/city_content.py — Loader de contenido editorial de ciudades.

Los textos (frases, descripciones) están en archivos JSON por idioma:
    app/locales/cities_es.json   ← Español
    app/locales/cities_en.json   ← English
    app/locales/cities_fr.json   ← Français
    app/locales/cities_pt.json   ← Português

La clave photo_search es universal (mismo término para todas las lenguas).

Uso:
    from app.city_content import get_city_content, SUPPORTED_LANGS

    content = get_city_content(lang="es")
    info = content.get("Tarifa", {})
    quote       = info["quote"]        # frase poética
    description = info["description"]  # descripción 2-3 líneas
    photo_search = info["photo_search"] # término Unsplash

Claves de ciudad:
    Corresponden al índice de city_features.csv (Atenas, Lisboa, Sevilla, etc.)
    NO a nombres anglosajones (Athens, Lisbon, Seville).

Idiomas soportados: es, en, fr, pt
"""

import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"

SUPPORTED_LANGS: list[str] = ["es", "en", "fr", "pt"]
DEFAULT_LANG: str = "es"

LANG_LABELS: dict[str, str] = {
    "es": "🇪🇸 Español",
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "pt": "🇵🇹 Português",
}


@lru_cache(maxsize=4)
def get_city_content(lang: str = DEFAULT_LANG) -> dict[str, dict]:
    """
    Carga y cachea el contenido editorial de ciudades para un idioma.

    Args:
        lang: código de idioma — "es" | "en" | "fr" | "pt"

    Returns:
        dict {city_key: {quote, description, photo_search}}

    Raises:
        FileNotFoundError si el archivo del idioma no existe.
        ValueError si el idioma no está soportado.
    """
    if lang not in SUPPORTED_LANGS:
        raise ValueError(
            f"Idioma '{lang}' no soportado. "
            f"Idiomas disponibles: {SUPPORTED_LANGS}"
        )
    path = LOCALES_DIR / f"cities_{lang}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Archivo de idioma no encontrado: {path}\n"
            f"Ejecuta el script de creación de locales si es necesario."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_city_info(city_key: str, lang: str = DEFAULT_LANG) -> dict:
    """
    Devuelve el contenido de una ciudad específica.

    Returns:
        dict con quote, description, photo_search
        o dict vacío si la ciudad no está en el locale.
    """
    content = get_city_content(lang)
    return content.get(city_key, {})


def available_cities(lang: str = DEFAULT_LANG) -> list[str]:
    """Devuelve la lista de ciudades disponibles en un idioma."""
    return sorted(get_city_content(lang).keys())


# ── Retrocompatibilidad — CITY_CONTENT sigue funcionando en español ──────────
# Mantiene compatibilidad con código que ya importaba CITY_CONTENT directamente.
CITY_CONTENT: dict[str, dict] = get_city_content("es")
