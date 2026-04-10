"""
app/streamlit_app.py — NomadOptima v3

Dos modos de entrada:
  1. Categorías clickables con subcategorías expandibles
  2. Texto libre → mapeo automático a dimensiones

Filtros:
  - Presupuesto: rango ideal ±300€ (soft — penaliza, no elimina)
  - Idioma: multiselect (boost, no hard filter)
  - Continente: opcional

Motor: Cosine Similarity (Capa 1) sobre city_features.csv
       LightGBM disponible cuando model_v2/ esté entrenado.

Ejecutar:
    streamlit run app/streamlit_app.py
"""

import html as html_lib
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.processing.features import CityFeatureBuilder, DIMENSION_MAP
from app.city_content import get_city_content, LANG_LABELS, SUPPORTED_LANGS
from app.city_carousel import render_city_carousel

try:
    from src.models.ranker import NomadRanker
    _RANKER_AVAILABLE = True
except Exception:
    _RANKER_AVAILABLE = False

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="NomadOptima",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CITY_FEATURES_CSV = ROOT / "data" / "processed" / "city_features.csv"

# ── Continente por ciudad ────────────────────────────────────────────────────
CITY_CONTINENT: dict[str, str] = {
    "Alicante": "Europa", "Amsterdam": "Europa", "Andorra": "Europa",
    "Atenas": "Europa", "Barcelona": "Europa", "Belgrade": "Europa",
    "Berlin": "Europa", "Bordeaux": "Europa", "Bucharest": "Europa",
    "Budapest": "Europa", "Chamonix": "Europa", "Dublin": "Europa",
    "Faro": "Europa", "Fuerteventura": "Europa", "Granada": "Europa",
    "Innsbruck": "Europa", "Krakow": "Europa", "Las_Palmas": "Europa",
    "Lisboa": "Europa", "London": "Europa", "Malaga": "Europa",
    "Milan": "Europa", "Munich": "Europa", "Napoles": "Europa",
    "Paris": "Europa", "Porto": "Europa", "Prague": "Europa",
    "Roma": "Europa", "Sevilla": "Europa", "Sofia": "Europa",
    "Stockholm": "Europa", "Tallinn": "Europa", "Tarifa": "Europa",
    "Valencia": "Europa", "Vienna": "Europa", "Warsaw": "Europa",
    "Tbilisi": "Cáucaso",
    "Buenos_Aires": "Latinoamérica", "Cartagena": "Latinoamérica",
    "Medellin": "Latinoamérica", "Mexico_City": "Latinoamérica",
    "Montevideo": "Latinoamérica",
}
CONTINENTES = sorted(set(CITY_CONTINENT.values()))

CITY_DISPLAY: dict[str, str] = {
    "Alicante": "Alicante", "Amsterdam": "Ámsterdam", "Andorra": "Andorra",
    "Atenas": "Atenas", "Barcelona": "Barcelona", "Belgrade": "Belgrado",
    "Berlin": "Berlín", "Bordeaux": "Burdeos", "Bucharest": "Bucarest",
    "Budapest": "Budapest", "Chamonix": "Chamonix", "Dublin": "Dublín",
    "Faro": "Faro", "Fuerteventura": "Fuerteventura", "Granada": "Granada",
    "Innsbruck": "Innsbruck", "Krakow": "Cracovia", "Las_Palmas": "Las Palmas",
    "Lisboa": "Lisboa", "London": "Londres", "Malaga": "Málaga",
    "Milan": "Milán", "Munich": "Múnich", "Napoles": "Nápoles",
    "Paris": "París", "Porto": "Porto", "Prague": "Praga",
    "Roma": "Roma", "Sevilla": "Sevilla", "Sofia": "Sofía",
    "Stockholm": "Estocolmo", "Tallinn": "Tallin", "Tarifa": "Tarifa",
    "Tbilisi": "Tbilisi", "Valencia": "Valencia", "Vienna": "Viena",
    "Warsaw": "Varsovia", "Buenos_Aires": "Buenos Aires",
    "Cartagena": "Cartagena", "Medellin": "Medellín",
    "Mexico_City": "Ciudad de México", "Montevideo": "Montevideo",
}
CITY_FLAG: dict[str, str] = {
    "Alicante": "🇪🇸", "Amsterdam": "🇳🇱", "Andorra": "🇦🇩",
    "Atenas": "🇬🇷", "Barcelona": "🇪🇸", "Belgrade": "🇷🇸",
    "Berlin": "🇩🇪", "Bordeaux": "🇫🇷", "Bucharest": "🇷🇴",
    "Budapest": "🇭🇺", "Chamonix": "🇫🇷", "Dublin": "🇮🇪",
    "Faro": "🇵🇹", "Fuerteventura": "🇪🇸", "Granada": "🇪🇸",
    "Innsbruck": "🇦🇹", "Krakow": "🇵🇱", "Las_Palmas": "🇪🇸",
    "Lisboa": "🇵🇹", "London": "🇬🇧", "Malaga": "🇪🇸",
    "Milan": "🇮🇹", "Munich": "🇩🇪", "Napoles": "🇮🇹",
    "Paris": "🇫🇷", "Porto": "🇵🇹", "Prague": "🇨🇿",
    "Roma": "🇮🇹", "Sevilla": "🇪🇸", "Sofia": "🇧🇬",
    "Stockholm": "🇸🇪", "Tallinn": "🇪🇪", "Tarifa": "🇪🇸",
    "Tbilisi": "🇬🇪", "Valencia": "🇪🇸", "Vienna": "🇦🇹",
    "Warsaw": "🇵🇱", "Buenos_Aires": "🇦🇷", "Cartagena": "🇨🇴",
    "Medellin": "🇨🇴", "Mexico_City": "🇲🇽", "Montevideo": "🇺🇾",
}
IDIOMA_COLS: dict[str, str] = {
    "Español": "city_idioma_espanol",
    "Inglés": "city_idioma_ingles",
    "Francés": "city_idioma_frances",
    "Alemán": "city_idioma_aleman",
    "Portugués": "city_idioma_portugues",
}

# ════════════════════════════════════════════════════════════════════════════
# ESTRUCTURA DE CATEGORÍAS → SUBCATEGORÍAS → DIMENSIONES
# ════════════════════════════════════════════════════════════════════════════

# Cada main cat tiene subcats; cada subcat mapea a user_imp_* con pesos.
# Security es dummy hasta que tengamos crime_index en city_features.csv.

CATEGORIES = [
    {
        "key": "gastronomia", "emoji": "🍽️", "label": "Gastronomía",
        "desc": "Restaurantes, mercados, experiencias culinarias",
        "subcats": [
            {"key": "alta_cocina",  "label": "Alta cocina & fine dining",   "dims": {"user_imp_gastronomia": 1.0}},
            {"key": "comida_local", "label": "Tapas & cocina local típica", "dims": {"user_imp_gastronomia": 0.8, "user_imp_autenticidad": 0.5}},
            {"key": "street_food",  "label": "Street food & mercados",      "dims": {"user_imp_gastronomia": 0.7, "user_imp_autenticidad": 0.6}},
            {"key": "vegan",        "label": "Vegano & vegetariano",        "dims": {"user_imp_gastronomia": 0.7, "user_imp_bienestar": 0.3}},
            {"key": "cafes",        "label": "Cafeterías de especialidad",  "dims": {"user_imp_gastronomia": 0.6, "user_imp_nomada": 0.2}},
        ],
    },
    {
        "key": "nocturna", "emoji": "🌙", "label": "Vida nocturna & social",
        "desc": "Bares, discotecas, conciertos, ambiente nocturno",
        "subcats": [
            {"key": "clubs",    "label": "Discotecas & clubs de música",   "dims": {"user_imp_vida_nocturna": 1.0, "user_imp_musica": 0.5}},
            {"key": "bares",    "label": "Bares & cócteles",               "dims": {"user_imp_vida_nocturna": 0.8, "user_imp_gastronomia": 0.3}},
            {"key": "concerts", "label": "Conciertos & música en directo",  "dims": {"user_imp_musica": 1.0, "user_imp_vida_nocturna": 0.4}},
            {"key": "pubs",     "label": "Pubs & tabernas locales",        "dims": {"user_imp_vida_nocturna": 0.7, "user_imp_autenticidad": 0.4}},
        ],
    },
    {
        "key": "cultura", "emoji": "🎭", "label": "Cultura & Arte",
        "desc": "Museos, historia, arte, arquitectura",
        "subcats": [
            {"key": "museos",      "label": "Museos & exposiciones",         "dims": {"user_imp_cultura": 1.0}},
            {"key": "historia",    "label": "Historia & monumentos",         "dims": {"user_imp_cultura": 0.9, "user_imp_turismo": 0.5}},
            {"key": "arte",        "label": "Arte visual & galerías",        "dims": {"user_imp_arte_visual": 1.0}},
            {"key": "street_art",  "label": "Street art & arte urbano",      "dims": {"user_imp_arte_visual": 0.7, "user_imp_social_media": 0.5}},
            {"key": "teatro",      "label": "Teatro, ópera & artes escénicas","dims": {"user_imp_cultura": 0.8, "user_imp_musica": 0.4}},
            {"key": "festivales",  "label": "Festivales culturales",         "dims": {"user_imp_musica": 0.8, "user_imp_cultura": 0.5}},
        ],
    },
    {
        "key": "naturaleza", "emoji": "🌿", "label": "Naturaleza & Outdoor",
        "desc": "Parques, playas, montaña, reservas naturales",
        "subcats": [
            {"key": "playa",         "label": "Playa & costa",              "dims": {"user_imp_naturaleza": 0.8, "user_imp_clima": 0.5}},
            {"key": "montana_nat",   "label": "Montaña & senderismo",       "dims": {"user_imp_naturaleza": 0.9, "user_imp_deporte_montana": 0.5}},
            {"key": "parques",       "label": "Parques & zonas verdes urbanas","dims": {"user_imp_naturaleza": 0.7}},
            {"key": "reservas",      "label": "Parques naturales & reservas","dims": {"user_imp_naturaleza": 1.0}},
        ],
    },
    {
        "key": "deporte", "emoji": "🏄", "label": "Deportes & Aventura",
        "desc": "Surf, kite, ski, gym, escalada, ciclismo",
        "subcats": [
            {"key": "surf",       "label": "Surf, kite & windsurf",         "dims": {"user_imp_deporte_agua": 1.0, "user_imp_naturaleza": 0.4}},
            {"key": "snorkel",    "label": "Snorkel, buceo & kayak",        "dims": {"user_imp_deporte_agua": 0.8, "user_imp_naturaleza": 0.5}},
            {"key": "ski",        "label": "Esquí & snowboard",             "dims": {"user_imp_deporte_montana": 1.0, "user_imp_naturaleza": 0.5}},
            {"key": "escalada",   "label": "Escalada & alpinismo",          "dims": {"user_imp_deporte_montana": 0.8, "user_imp_naturaleza": 0.6}},
            {"key": "senderismo", "label": "Senderismo & rutas",            "dims": {"user_imp_deporte_montana": 0.6, "user_imp_naturaleza": 0.7}},
            {"key": "gym",        "label": "Gym, fitness & piscinas",       "dims": {"user_imp_deporte_urbano": 1.0}},
            {"key": "ciclismo",   "label": "Ciclismo & running urbano",     "dims": {"user_imp_deporte_urbano": 0.7, "user_imp_movilidad": 0.3}},
        ],
    },
    {
        "key": "bienestar", "emoji": "🧘", "label": "Bienestar",
        "desc": "Spa, yoga, meditación, termas, salud",
        "subcats": [
            {"key": "spa",        "label": "Spa & centros de bienestar",    "dims": {"user_imp_bienestar": 1.0}},
            {"key": "yoga",       "label": "Yoga & meditación",             "dims": {"user_imp_bienestar": 0.9}},
            {"key": "termas",     "label": "Termas & baños termales",       "dims": {"user_imp_bienestar": 0.8, "user_imp_turismo": 0.3}},
            {"key": "salud",      "label": "Sanidad & salud de calidad",    "dims": {"user_imp_salud": 1.0}},
        ],
    },
    {
        "key": "nomada", "emoji": "💻", "label": "Trabajo remoto",
        "desc": "Coworkings, coliving, internet rápido, comunidad tech",
        "subcats": [
            {"key": "coworking",  "label": "Coworkings & espacios de trabajo", "dims": {"user_imp_nomada": 1.0}},
            {"key": "coliving",   "label": "Coliving & comunidades nómadas",   "dims": {"user_imp_nomada": 0.9, "user_imp_alojamiento": 0.6}},
            {"key": "internet",   "label": "Internet ultrarrápido & tech hub", "dims": {"user_imp_nomada": 0.8}},
            {"key": "libraries",  "label": "Bibliotecas & cafés para trabajar","dims": {"user_imp_nomada": 0.6, "user_imp_gastronomia": 0.2}},
        ],
    },
    {
        "key": "familia", "emoji": "👨‍👩‍👧", "label": "Familia & Infancia",
        "desc": "Colegios, parques infantiles, seguridad, actividades para niños",
        "subcats": [
            {"key": "colegios",   "label": "Colegios & guarderías de calidad","dims": {"user_imp_familia": 1.0, "user_imp_educacion": 0.5}},
            {"key": "parques_inf","label": "Parques & zonas de juego",        "dims": {"user_imp_familia": 0.8, "user_imp_naturaleza": 0.3}},
            {"key": "actividades_ninos","label": "Ocio & actividades para niños","dims": {"user_imp_familia": 0.9}},
            {"key": "segura",     "label": "Ciudad segura para familia",      "dims": {"user_imp_familia": 0.7, "user_imp_calidad_vida": 0.5}},
        ],
    },
    {
        "key": "mascotas", "emoji": "🐾", "label": "Mascotas",
        "desc": "Parques para perros, veterinarios, espacios pet-friendly",
        "subcats": [
            {"key": "dog_parks",  "label": "Parques para perros",           "dims": {"user_imp_mascotas": 1.0, "user_imp_naturaleza": 0.3}},
            {"key": "vets",       "label": "Veterinarios & clínicas pet",   "dims": {"user_imp_mascotas": 0.9}},
            {"key": "pet_friendly","label": "Ciudad abierta a mascotas",    "dims": {"user_imp_mascotas": 0.8, "user_imp_calidad_vida": 0.3}},
        ],
    },
    {
        "key": "ciudad", "emoji": "🚌", "label": "Ciudad & Servicios",
        "desc": "Transporte, compras, servicios básicos, calidad urbana",
        "subcats": [
            {"key": "transporte",  "label": "Metro, bus & bicicleta",       "dims": {"user_imp_movilidad": 1.0}},
            {"key": "compras",     "label": "Supermercados & compras básicas","dims": {"user_imp_compras": 1.0}},
            {"key": "servicios",   "label": "Peluquería, lavandería, etc.",  "dims": {"user_imp_servicios": 1.0}},
            {"key": "calidad_urb", "label": "Calidad de vida urbana general","dims": {"user_imp_calidad_vida": 1.0}},
        ],
    },
    {
        "key": "autenticidad", "emoji": "🌿", "label": "Autenticidad",
        "desc": "Anti-turístico, comunidad local, idiomas, folklore",
        "subcats": [
            {"key": "local",       "label": "Barrios locales & sin turistas","dims": {"user_imp_autenticidad": 1.0}},
            {"key": "idiomas",     "label": "Academia de idiomas & cultura", "dims": {"user_imp_educacion": 0.9, "user_imp_autenticidad": 0.4}},
            {"key": "comunidad",   "label": "Comunidad local & expats",      "dims": {"user_imp_comunidad": 1.0}},
            {"key": "folklore",    "label": "Folklore & tradiciones vivas",  "dims": {"user_imp_autenticidad": 0.9, "user_imp_musica": 0.4}},
        ],
    },
    {
        "key": "social", "emoji": "📸", "label": "Estilo & Social Media",
        "desc": "Lugares fotogénicos, rooftops, beach clubs, miradores",
        "subcats": [
            {"key": "rooftops",    "label": "Rooftop bars & miradores",      "dims": {"user_imp_social_media": 1.0, "user_imp_vida_nocturna": 0.4}},
            {"key": "beach_clubs", "label": "Beach clubs & chiringuitos",    "dims": {"user_imp_social_media": 0.8, "user_imp_deporte_agua": 0.3}},
            {"key": "spots",       "label": "Rincones únicos & fotogénicos", "dims": {"user_imp_social_media": 0.9, "user_imp_turismo": 0.4}},
            {"key": "musica_fest", "label": "Festivales de música",          "dims": {"user_imp_musica": 1.0, "user_imp_social_media": 0.5}},
        ],
    },
    {
        "key": "presupuesto", "emoji": "💶", "label": "Presupuesto",
        "desc": "Coste de vida, precios, economía del destino",
        "subcats": [
            {"key": "muy_barato",  "label": "Muy económico (< €900/mes)",   "dims": {"user_imp_coste": 1.0}},
            {"key": "barato",      "label": "Económico (€900–1.400/mes)",   "dims": {"user_imp_coste": 0.9}},
            {"key": "moderado",    "label": "Moderado (€1.400–2.200/mes)",  "dims": {"user_imp_coste": 0.6}},
            {"key": "premium",     "label": "Premium (> €2.200/mes)",       "dims": {"user_imp_coste": 0.2}},
        ],
    },
    {
        "key": "seguridad", "emoji": "🔒", "label": "Seguridad",
        "desc": "Índice de criminalidad, seguridad ciudadana",
        "dummy": True,  # sin datos todavía — mostrar pero no afectar al score
        "subcats": [
            {"key": "alta_seg",    "label": "Alta seguridad",                "dims": {}},
            {"key": "media_seg",   "label": "Seguridad media",               "dims": {}},
            {"key": "flexible_seg","label": "Flexible (acepto zonas con más riesgo)","dims": {}},
        ],
    },
]

# Mapa rápido subcat_key → dims para calcular el perfil
SUBCAT_DIMS: dict[str, dict[str, float]] = {
    sc["key"]: sc["dims"]
    for cat in CATEGORIES
    for sc in cat["subcats"]
}

# ── Mapeo de palabras clave → dims (modo texto libre) ────────────────────────
KEYWORD_MAP: list[tuple[list[str], dict[str, float]]] = [
    (["surf", "surfing", "ola", "tabla"],                {"user_imp_deporte_agua": 0.9}),
    (["kite", "kitesurf", "windsurf", "viento", "cometa"], {"user_imp_deporte_agua": 0.95}),
    (["ski", "nieve", "esquí", "snowboard", "pistas"],   {"user_imp_deporte_montana": 0.9, "user_imp_naturaleza": 0.5}),
    (["senderismo", "hiking", "trekking", "montaña"],    {"user_imp_deporte_montana": 0.7, "user_imp_naturaleza": 0.8}),
    (["gym", "fitness", "piscina"],                      {"user_imp_deporte_urbano": 1.0}),
    (["barato", "económico", "budget", "ahorrar"],       {"user_imp_coste": 0.9}),
    (["gastronomía", "comida", "restaurante", "tapas"],  {"user_imp_gastronomia": 0.9}),
    (["fiesta", "discoteca", "bares", "nocturna"],       {"user_imp_vida_nocturna": 0.9}),
    (["cultura", "museo", "historia", "patrimonio"],     {"user_imp_cultura": 0.9}),
    (["arte", "galería", "street art"],                  {"user_imp_arte_visual": 0.9}),
    (["yoga", "spa", "bienestar", "meditación"],         {"user_imp_bienestar": 0.9}),
    (["coworking", "coliving", "nómada", "remoto"],      {"user_imp_nomada": 0.9}),
    (["familia", "niños", "hijos", "colegio"],           {"user_imp_familia": 0.9}),
    (["perro", "mascota", "gato", "pet"],                {"user_imp_mascotas": 0.9}),
    (["playa", "mar", "costa", "beach"],                 {"user_imp_deporte_agua": 0.6, "user_imp_naturaleza": 0.6, "user_imp_clima": 0.5}),
    (["naturaleza", "bosque", "parque nacional"],        {"user_imp_naturaleza": 0.9}),
    (["foto", "instagram", "fotogénico"],                {"user_imp_social_media": 0.8}),
    (["música", "festival", "concierto", "flamenco"],   {"user_imp_musica": 0.9}),
    (["auténtico", "local", "sin turistas"],             {"user_imp_autenticidad": 0.9}),
    (["sol", "calor", "cálido", "clima"],                {"user_imp_clima": 0.9}),
    (["calidad de vida", "seguro", "tranquilo"],         {"user_imp_calidad_vida": 0.9}),
    (["idiomas", "estudiar", "universidad"],             {"user_imp_educacion": 0.8}),
    (["transporte", "metro", "bus", "bici"],             {"user_imp_movilidad": 0.7}),
    (["compras", "supermercado", "mercado"],             {"user_imp_compras": 0.7}),
    (["salud", "hospital", "médico"],                    {"user_imp_salud": 0.8}),
]

DIM_LABELS: dict[str, str] = {
    "gastronomia": "🍽️ Gastronomía", "vida_nocturna": "🌙 Nocturna",
    "cultura": "🎭 Cultura", "arte_visual": "🎨 Arte",
    "bienestar": "🧘 Bienestar", "social_media": "📸 Fotogénico",
    "musica": "🎶 Música", "turismo": "🏛️ Turismo",
    "autenticidad": "🌿 Auténtica", "naturaleza": "🌲 Naturaleza",
    "deporte_agua": "🏄 Surf/Kite", "deporte_montana": "⛷️ Montaña",
    "deporte_urbano": "🏋️ Gym/Sport", "nomada": "💻 Nómada",
    "familia": "👨‍👩‍👧 Familia", "mascotas": "🐾 Mascotas",
    "alojamiento": "🏠 Alojamiento", "movilidad": "🚌 Transporte",
    "salud": "🏥 Salud", "educacion": "📚 Idiomas/Ed.",
    "comunidad": "🤝 Comunidad", "coste": "💶 Coste bajo",
    "compras": "🛒 Compras", "servicios": "✂️ Servicios",
    "clima": "☀️ Clima", "calidad_vida": "⭐ Calidad de vida",
}

# ════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Cargando datos de ciudades...")
def load_model() -> tuple[CityFeatureBuilder, pd.DataFrame, object]:
    city_df = pd.read_csv(CITY_FEATURES_CSV, index_col=0)
    builder = CityFeatureBuilder()
    builder.fit(city_df)
    ranker = None
    if _RANKER_AVAILABLE:
        try:
            ranker = NomadRanker()
        except Exception:
            ranker = None
    return builder, city_df, ranker


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def build_prefs_from_subcats(selected_subcats: set[str]) -> dict[str, float]:
    """Agrega los dims de las subcategorías seleccionadas en un perfil."""
    prefs: dict[str, float] = {}
    for sc_key in selected_subcats:
        for dim_key, weight in SUBCAT_DIMS.get(sc_key, {}).items():
            prefs[dim_key] = max(prefs.get(dim_key, 0.0), weight)
    # Dims no mencionados → 0.05
    for _, user_key, _ in DIMENSION_MAP:
        if user_key not in prefs:
            prefs[user_key] = 0.05
    return prefs


def parse_text_prompt(texto: str) -> dict[str, float]:
    """Convierte texto libre a importancias user_imp_*."""
    texto_lower = texto.lower()
    prefs: dict[str, float] = {}
    for keywords, weights in KEYWORD_MAP:
        if any(kw in texto_lower for kw in keywords):
            for key, val in weights.items():
                prefs[key] = max(prefs.get(key, 0.0), val)
    for _, user_key, _ in DIMENSION_MAP:
        if user_key not in prefs:
            prefs[user_key] = 0.05
    return prefs


def filter_by_budget(
    city_df: pd.DataFrame,
    presupuesto: int,
    margen: float = 0.30,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide las ciudades en dos grupos según el presupuesto.

    El presupuesto es un FILTRO DURO — las ciudades que lo superan
    no compiten en el ranking principal. Las características determinan
    el orden; el precio solo descalifica.

    Margen del 30%: si el usuario pone €800, acepta hasta €1.040.
    Por encima de ese tope → fuera del ranking principal.

    Returns:
        (dentro_budget, fuera_budget) — dos DataFrames separados
    """
    tope = presupuesto * (1 + margen)
    coste_col = "city_coste_vida_estimado"

    dentro = city_df[
        city_df[coste_col].isna() |
        (city_df[coste_col] <= 0) |
        (city_df[coste_col] <= tope)
    ]
    fuera = city_df[
        city_df[coste_col].notna() &
        (city_df[coste_col] > 0) &
        (city_df[coste_col] > tope)
    ]
    return dentro, fuera


def apply_language_boost(
    scores: pd.Series,
    city_df: pd.DataFrame,
    idiomas_seleccionados: list[str],
    boost: float = 0.12,
) -> pd.Series:
    """Añade un boost al score de ciudades que hablan el idioma preferido."""
    if not idiomas_seleccionados:
        return scores
    scores = scores.copy()
    for city in scores.index:
        if city not in city_df.index:
            continue
        for idioma in idiomas_seleccionados:
            col = IDIOMA_COLS.get(idioma)
            if col and col in city_df.columns:
                if city_df.loc[city, col] == 1:
                    scores[city] = min(1.0, scores[city] + boost)
                    break
    return scores


# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.main > div { padding-top: 1rem; }

/* ── Header ──────────────────────────────────────────────── */
.nomad-header { text-align:center; padding:1rem 0 0.3rem 0; }
.nomad-header h1 {
    font-size:2.6rem; font-weight:900;
    background:linear-gradient(135deg,#667eea,#764ba2);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin:0;
}
.nomad-header p { font-size:1rem; color:#888; margin:0; }

/* ── Category cards ──────────────────────────────────────── */
div[data-testid="stButton"] button {
    width:100%; text-align:left; border-radius:12px;
    border:1px solid #e0e0e0; background:white;
    padding:0.6rem 0.8rem; font-size:0.88rem; font-weight:600;
    transition:all 0.15s; cursor:pointer; color:#2c3e50;
}
div[data-testid="stButton"] button:hover {
    border-color:#667eea; background:#f5f7ff; color:#667eea;
}

/* ── Result cards ────────────────────────────────────────── */
.city-card {
    background:white; border-radius:16px; padding:1.2rem 1.4rem;
    margin-bottom:1.2rem; box-shadow:0 4px 20px rgba(0,0,0,0.07);
    border:1px solid #eee;
}
.city-card.rank1 { border:2px solid #667eea; box-shadow:0 8px 30px rgba(102,126,234,0.15); }
.rank-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:2.2rem; height:2.2rem; border-radius:50%;
    font-weight:900; font-size:0.95rem; margin-right:0.6rem; flex-shrink:0;
}
.gold   { background:linear-gradient(135deg,#f7971e,#ffd200); color:#5a3900; }
.silver { background:linear-gradient(135deg,#bdc3c7,#95a5a6); color:white; }
.bronze { background:linear-gradient(135deg,#cd7f32,#a0522d); color:white; }
.other  { background:#eee; color:#555; }
.city-name { font-size:1.5rem; font-weight:800; color:#1a1a2e; }
.city-quote { font-style:italic; color:#555; font-size:0.92rem; margin:0.5rem 0; border-left:3px solid #667eea; padding-left:0.7rem; }
.city-desc  { color:#666; font-size:0.87rem; line-height:1.5; }
.stat-pill {
    display:inline-block; background:#f5f7ff; border:1px solid #dce3ff;
    border-radius:20px; padding:0.2rem 0.6rem; font-size:0.8rem;
    font-weight:600; color:#4a5568; margin:0.2rem 0.15rem 0 0;
}
.dim-tag {
    display:inline-block; background:rgba(102,126,234,0.1); border:1px solid rgba(102,126,234,0.25);
    border-radius:12px; padding:0.1rem 0.5rem; font-size:0.77rem;
    font-weight:600; color:#5a47a8; margin:0.15rem 0.1rem 0 0;
}
.match-bar-bg { background:#eee; border-radius:6px; height:5px; margin:0.3rem 0; overflow:hidden; }
.match-bar-fill { height:5px; border-radius:6px; background:linear-gradient(90deg,#667eea,#764ba2); }
.dummy-badge {
    display:inline-block; background:#fff3e0; border:1px solid #ffb74d;
    border-radius:8px; padding:0.15rem 0.5rem; font-size:0.72rem;
    color:#e65100; font-weight:700; margin-left:0.4rem;
}
.model-note {
    background:#f0f4ff; border-left:4px solid #667eea; border-radius:6px;
    padding:0.6rem 1rem; font-size:0.8rem; color:#3a3a6a; margin-top:1.5rem;
}
.section-hdr {
    font-size:1.05rem; font-weight:700; color:#2c3e50;
    margin:1.5rem 0 0.4rem 0; padding-bottom:0.3rem;
    border-bottom:2px solid #667eea; display:inline-block;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# RESULTADO: RENDER DE UNA CIUDAD
# ════════════════════════════════════════════════════════════════════════════

def render_city_card(
    rank: int,
    city_key: str,
    score: float,
    max_score: float,
    city_df: pd.DataFrame,
    builder: CityFeatureBuilder,
    prefs: dict,
    city_content: dict,
) -> None:
    badge_cls = {1: "gold", 2: "silver", 3: "bronze"}.get(rank, "other")
    card_cls  = "city-card rank1" if rank == 1 else "city-card"
    display   = CITY_DISPLAY.get(city_key, city_key)
    flag      = CITY_FLAG.get(city_key, "📍")
    continent = CITY_CONTINENT.get(city_key, "")
    pct       = int((score / max_score) * 100) if max_score > 0 else 0

    # Stats
    row   = city_df.loc[city_key] if city_key in city_df.index else {}
    coste = row.get("city_coste_vida_estimado", None)
    temp  = row.get("city_temp_media_anual", None)
    sol   = row.get("city_dias_sol_anual", None)
    cow   = row.get("city_coworking_osm", row.get("city_gp_coworking", None))
    idiom = row.get("city_idioma_nativo", "")

    coste_txt = f"€{int(coste):,}/mes" if pd.notna(coste) and coste > 0 else ""
    temp_txt  = f"{int(temp)}°C" if pd.notna(temp) else ""
    sol_txt   = f"{int(sol)} días sol/año" if pd.notna(sol) else ""
    cow_txt   = f"{int(cow)} coworking" if pd.notna(cow) and cow > 0 else ""

    stats_parts = [
        f'<span class="stat-pill">💰 {coste_txt}</span>' if coste_txt else "",
        f'<span class="stat-pill">🌡️ {temp_txt}</span>' if temp_txt else "",
        f'<span class="stat-pill">☀️ {sol_txt}</span>' if sol_txt else "",
        f'<span class="stat-pill">💻 {cow_txt}</span>' if cow_txt else "",
        f'<span class="stat-pill">🗣️ {idiom}</span>' if idiom else "",
    ]
    stats_html = "".join(s for s in stats_parts if s)

    # Dimensiones que más contribuyen
    top_dims = builder.top_features_for_city(prefs, city_key, city_df, top_n=4)
    dims_html = "".join(
        f'<span class="dim-tag">{DIM_LABELS.get(d, d)}</span>'
        for d, _ in top_dims
    )

    # Contenido editorial — escapar caracteres especiales antes de insertar en HTML
    info  = city_content.get(city_key, {})
    quote = html_lib.escape(info.get("quote", ""))
    desc  = html_lib.escape(info.get("description", ""))
    quote_html   = f'<p class="city-quote">{quote}</p>' if quote else ""
    dims_section = f"<div style='margin-top:0.4rem;'>{dims_html}</div>" if dims_html else ""

    # Cabecera del card
    st.markdown(
        f"""
        <div class="{card_cls}">
            <div style="display:flex;align-items:center;margin-bottom:0.6rem;">
                <span class="rank-badge {badge_cls}">#{rank}</span>
                <span class="city-name">{flag} {display}</span>
                <span style="color:#aaa;font-size:0.82rem;margin-left:0.5rem;">— {continent}</span>
            </div>
            {quote_html}
            <div style="margin:0.4rem 0;">
                <span style="font-size:0.8rem;color:#888;">Compatibilidad: <strong style="color:#667eea;">{pct}%</strong></span>
                <div class="match-bar-bg"><div class="match-bar-fill" style="width:{pct}%;"></div></div>
            </div>
            <div style="margin:0.5rem 0;">{stats_html}</div>
            {dims_section}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Foto y descripción en expander
    with st.expander(f"📷 Fotos & descripción — {display}"):
        render_city_carousel(city_key)
        if desc:
            st.markdown(html_lib.unescape(desc))


# ════════════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def main():
    try:
        builder, city_df, ranker = load_model()
    except FileNotFoundError:
        st.error("❌ city_features.csv no encontrado. Ejecuta `src/processing/features.py`.")
        return

    # Inicializar estado de sesión
    if "selected_cats" not in st.session_state:
        st.session_state.selected_cats = set()
    if "selected_subcats" not in st.session_state:
        st.session_state.selected_subcats = set()
    if "app_lang" not in st.session_state:
        st.session_state.app_lang = "es"

    # ── Selector de idioma de la app (top right) ──────────────────────────
    col_hdr, col_lang = st.columns([4, 1])
    with col_hdr:
        st.markdown("""
        <div class="nomad-header">
            <h1>🌍 NomadOptima</h1>
            <p>Encuentra tu ciudad ideal</p>
        </div>
        """, unsafe_allow_html=True)
    with col_lang:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        lang = st.selectbox(
            "Idioma app",
            options=SUPPORTED_LANGS,
            index=SUPPORTED_LANGS.index(st.session_state.app_lang),
            format_func=lambda x: LANG_LABELS[x],
            label_visibility="collapsed",
            key="lang_selector",
        )
        st.session_state.app_lang = lang

    city_content = get_city_content(lang)

    # ── FILTROS PRINCIPALES ───────────────────────────────────────────────
    st.markdown('<div class="section-hdr">1️⃣ ¿Qué necesitas sí o sí?</div>', unsafe_allow_html=True)
    st.caption("El idioma y el presupuesto son los filtros más importantes. El idioma boost las ciudades que lo hablan; el presupuesto penaliza (no elimina) las que se pasan.")

    col_idioma, col_pres = st.columns([1, 1])

    with col_idioma:
        idiomas_sel = st.multiselect(
            "🗣️ Idioma con el que te quieres mover",
            options=list(IDIOMA_COLS.keys()),
            default=[],
            placeholder="Cualquier idioma",
            help="Las ciudades donde se hable ese idioma subirán en el ranking.",
        )

    with col_pres:
        presupuesto = st.slider(
            "💰 Presupuesto mensual ideal",
            min_value=500, max_value=5000, value=2000, step=100, format="€%d",
        )
        # Preview rápido
        n_dentro = sum(
            1 for c in city_df.index
            if city_df.loc[c, "city_coste_vida_estimado"] <= presupuesto * 1.35
        )
        st.caption(f"≈ {n_dentro} ciudades dentro del rango €{presupuesto-300:,}–€{int(presupuesto*1.35):,}")

    with st.expander("🌐 Filtrar por continente (opcional)"):
        continentes_sel = st.multiselect(
            "Continente", options=CONTINENTES, default=[], label_visibility="collapsed"
        )

    # ── SELECCIÓN DE CATEGORÍAS ───────────────────────────────────────────
    st.markdown('<div class="section-hdr">2️⃣ ¿Qué buscas en tu ciudad?</div>', unsafe_allow_html=True)
    st.caption("Haz clic en las categorías que te interesan. Luego elige las subcategorías específicas.")

    tab_cats, tab_text = st.tabs(["🎯 Por categorías", "✍️ Texto libre"])

    run_search = False
    prefs_finales: dict[str, float] = {}

    with tab_cats:
        # Grid de categorías (4 por fila)
        N_COLS = 4
        cat_rows = [CATEGORIES[i:i+N_COLS] for i in range(0, len(CATEGORIES), N_COLS)]

        for row in cat_rows:
            cols = st.columns(N_COLS)
            for col, cat in zip(cols, row):
                with col:
                    is_active = cat["key"] in st.session_state.selected_cats
                    dummy_badge = " *(próximamente)*" if cat.get("dummy") else ""
                    label = f"{'✅ ' if is_active else ''}{cat['emoji']} {cat['label']}{dummy_badge}"
                    if st.button(label, key=f"cat_{cat['key']}", use_container_width=True):
                        if cat["key"] in st.session_state.selected_cats:
                            st.session_state.selected_cats.discard(cat["key"])
                            # Quitar subcats de esta cat
                            sc_keys = {sc["key"] for sc in cat["subcats"]}
                            st.session_state.selected_subcats -= sc_keys
                        else:
                            st.session_state.selected_cats.add(cat["key"])
                        st.rerun()

        # Subcategorías de las categorías activas
        if st.session_state.selected_cats:
            st.markdown("---")
            st.markdown("**Elige qué te interesa exactamente:**")
            for cat in CATEGORIES:
                if cat["key"] not in st.session_state.selected_cats:
                    continue
                st.markdown(f"**{cat['emoji']} {cat['label']}**")
                if cat.get("dummy"):
                    st.caption("⚠️ Sin datos todavía — tu selección se guardará pero no afectará al ranking ahora.")
                sc_cols = st.columns(min(3, len(cat["subcats"])))
                for i, sc in enumerate(cat["subcats"]):
                    with sc_cols[i % 3]:
                        checked = st.checkbox(
                            sc["label"],
                            key=f"sc_{sc['key']}",
                            value=sc["key"] in st.session_state.selected_subcats,
                        )
                        if checked:
                            st.session_state.selected_subcats.add(sc["key"])
                        else:
                            st.session_state.selected_subcats.discard(sc["key"])

        # Campo "¿Nos falta algo?"
        st.markdown("---")
        falta = st.text_area(
            "💬 ¿Nos falta algo? Cuéntanos qué más buscas",
            placeholder="Ej: busco una ciudad donde haya comunidad de expats y buenos médicos, y que no sea muy turística...",
            height=80,
            key="falta_texto",
        )

        buscar_cats = st.button(
            "🔍 Buscar mi ciudad ideal",
            type="primary", use_container_width=True, key="btn_cats",
        )

        if buscar_cats:
            prefs_finales = build_prefs_from_subcats(st.session_state.selected_subcats)
            # Si hay texto adicional, fusionarlo
            if falta.strip():
                extra = parse_text_prompt(falta)
                for k, v in extra.items():
                    prefs_finales[k] = max(prefs_finales.get(k, 0.0), v)
            if not st.session_state.selected_subcats and not falta.strip():
                st.warning("Selecciona al menos una subcategoría o escribe qué buscas.")
            else:
                run_search = True

    with tab_text:
        st.caption("Describe en tus palabras qué buscas y el sistema mapeará tus preferencias.")
        texto = st.text_area(
            "✍️ Describe qué buscas",
            placeholder="Quiero una ciudad cálida y barata donde pueda hacer kite, con buen coworking porque trabajo remoto...",
            height=130, key="texto_libre",
        )

        if texto.strip():
            detected = {k: v for k, v in parse_text_prompt(texto).items() if v > 0.2}
            if detected:
                dim_display = {d[1]: f"{DIM_LABELS.get(d[0], d[0])}" for d in DIMENSION_MAP}
                resumen = " · ".join(
                    f"**{dim_display.get(k, k)}** ({v:.0%})"
                    for k, v in sorted(detected.items(), key=lambda x: -x[1])
                    if v > 0.2
                )
                st.markdown(f"Detectado: {resumen}")

        buscar_text = st.button(
            "🔍 Buscar con este texto",
            type="primary", use_container_width=True, key="btn_text",
            disabled=not bool(texto.strip()),
        )

        if buscar_text and texto.strip():
            prefs_finales = parse_text_prompt(texto)
            run_search = True

    # ── RESULTADOS ────────────────────────────────────────────────────────
    if run_search and prefs_finales:
        # 1. Filtro de continente
        if continentes_sel:
            ciudades_cont = {c for c, cont in CITY_CONTINENT.items() if cont in continentes_sel}
            city_df_base = city_df[city_df.index.isin(ciudades_cont)]
        else:
            city_df_base = city_df

        if len(city_df_base) == 0:
            st.error("❌ Ninguna ciudad en los continentes seleccionados.")
            return

        # 2. Filtro duro de presupuesto — separa dentro/fuera sin mezclar rankings
        city_dentro, city_fuera = filter_by_budget(city_df_base, presupuesto)

        with st.spinner("Calculando ranking..."):
            if ranker is not None:
                # LightGBM LambdaMART (Capa 4) — 175 features
                candidate_keys = city_dentro.index.tolist()
                scores = ranker.scores_series(prefs_finales, candidate_cities=candidate_keys)
            else:
                # Fallback: Cosine Similarity (Capa 1)
                scores = builder.cosine_scores(prefs_finales, city_dentro)
            scores = apply_language_boost(scores, city_dentro, idiomas_sel)

        top_n  = min(8, len(scores))
        top    = scores.sort_values(ascending=False).head(top_n)
        max_sc = top.iloc[0]

        n_excluidas = len(city_fuera)

        st.markdown('<div class="section-hdr">🏆 Tu ranking personalizado</div>', unsafe_allow_html=True)
        st.caption(
            f"Top {len(top)} ciudades ordenadas por compatibilidad con tu perfil. "
            f"{'⚠️ ' + str(n_excluidas) + ' ciudades excluidas por presupuesto.' if n_excluidas > 0 else ''}"
        )

        for rank, (city_key, score) in enumerate(top.items(), start=1):
            render_city_card(rank, city_key, score, max_sc, city_dentro, builder, prefs_finales, city_content)

        # Mostrar excluidas por presupuesto (informativo, no ranking)
        if n_excluidas > 0 and len(city_fuera) <= 15:
            with st.expander(f"🚫 {n_excluidas} ciudades fuera de tu presupuesto (€{int(presupuesto * 1.30):,}/mes)"):
                if ranker is not None:
                    excl_keys = city_fuera.index.tolist()
                    excl_scores = ranker.scores_series(prefs_finales, candidate_cities=excl_keys)
                else:
                    excl_scores = builder.cosine_scores(prefs_finales, city_fuera)
                excl_top = excl_scores.sort_values(ascending=False).head(5)
                st.caption("Serían buenas opciones de perfil, pero superan tu presupuesto:")
                for city_key, score in excl_top.items():
                    coste = city_fuera.loc[city_key, "city_coste_vida_estimado"]
                    display = CITY_DISPLAY.get(city_key, city_key)
                    flag = CITY_FLAG.get(city_key, "📍")
                    pct_match = int((score / max_sc) * 100) if max_sc > 0 else 0
                    st.markdown(
                        f"**{flag} {display}** — €{int(coste):,}/mes "
                        f"*(compatibilidad perfil: {pct_match}%)*"
                    )

        motor_txt = (
            "🔬 <strong>Motor:</strong> LightGBM LambdaMART (Capa 4) — "
            "175 features · NDCG@5 = 0.9631 · 43 árboles · "
            "Google Places · Numbeo · OpenStreetMap · Clima · Internet · RestCountries."
            if ranker is not None else
            "🔬 <strong>Motor:</strong> Cosine Similarity (Capa 1) — "
            "el orden lo determinan las características del perfil."
        )
        st.markdown(
            f'<div class="model-note">{motor_txt}</div>',
            unsafe_allow_html=True,
        )

    else:
        st.info(
            "👆 **Cómo usar NomadOptima:**\n\n"
            "• **Por categorías** → haz clic en las que te interesan y elige subcategorías\n\n"
            "• **Texto libre** → escribe qué buscas y el sistema lo interpreta"
        )


if __name__ == "__main__":
    main()
