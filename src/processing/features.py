"""
NomadOptima — Capa 1: Content-Based Filtering con Cosine Similarity
src/processing/features.py  v2  (24 categorías, 36+ ciudades)

¿QUÉ HACE ESTA CAPA?
---------------------
Construye el vector numérico de cada ciudad a partir de los datos reales
(Google Places, OSM, Numbeo, Speedtest, wttr.in) y calcula cuánto se
parece el perfil de un usuario a cada ciudad usando Cosine Similarity.

CAMBIOS v2 vs v1
-----------------
- 24 dimensiones de usuario (antes 11)
- Lee JSONs individuales por ciudad (antes un solo cities_raw.json)
- Añade features de: música, kite/ski, social media, autenticidad, coliving
- TEMP_MEDIA y DIAS_SOL ampliados a las 36 ciudades actuales
"""

import json
import os
import glob
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

# ── TEMPERATURA MEDIA ANUAL (°C) — no disponible en wttr.in histórico ─────────
TEMP_MEDIA = {
    "Malaga": 18.5, "Paris": 12.3, "Valencia": 18.0, "Porto": 15.5,
    "Bordeaux": 13.5, "Barcelona": 16.5, "Madrid": 14.5, "Sevilla": 19.0,
    "Granada": 15.0, "Alicante": 18.2, "Tarifa": 17.8, "Fuerteventura": 21.0,
    "Las_Palmas": 21.5, "Faro": 17.5, "Lisboa": 16.5, "Atenas": 17.5,
    "Roma": 15.5, "Milan": 13.0, "Napoles": 16.5, "Amsterdam": 10.5,
    "Berlin": 10.0, "Munich": 9.5, "Vienna": 10.5, "Prague": 9.5,
    "Warsaw": 8.5, "Krakow": 8.5, "Budapest": 11.0, "Bucharest": 11.0,
    "Sofia": 11.5, "Belgrade": 12.0, "Stockholm": 8.0, "Dublin": 10.0,
    "London": 11.5, "Chamonix": 5.0, "Innsbruck": 8.5, "Andorra": 7.0,
    "Tbilisi": 13.5, "Bangkok": 28.5, "Bali": 27.0, "Chiang_Mai": 26.0,
    "Da_Nang": 26.5, "Kuala_Lumpur": 27.5, "Dubai": 27.0,
    "Marrakech": 19.5, "Dakhla": 20.5, "Essaouira": 18.5,
    "Medellin": 22.0, "Bogota": 14.0, "Cartagena": 28.0,
    "Lima": 18.5, "Santiago": 14.5, "Buenos_Aires": 17.5,
    "Montevideo": 16.5, "Mexico_City": 16.0, "Playa_del_Carmen": 26.5,
    "Tallinn": 6.5,
}

DIAS_SOL = {
    "Malaga": 320, "Paris": 170, "Valencia": 310, "Porto": 220,
    "Bordeaux": 200, "Barcelona": 270, "Madrid": 280, "Sevilla": 320,
    "Granada": 300, "Alicante": 310, "Tarifa": 300, "Fuerteventura": 320,
    "Las_Palmas": 310, "Faro": 300, "Lisboa": 280, "Atenas": 300,
    "Roma": 270, "Milan": 220, "Napoles": 270, "Amsterdam": 175,
    "Berlin": 185, "Munich": 195, "Vienna": 200, "Prague": 195,
    "Warsaw": 185, "Krakow": 185, "Budapest": 210, "Bucharest": 220,
    "Sofia": 210, "Belgrade": 215, "Stockholm": 185, "Dublin": 160,
    "London": 165, "Chamonix": 220, "Innsbruck": 230, "Andorra": 250,
    "Tbilisi": 250, "Bangkok": 270, "Bali": 250, "Chiang_Mai": 260,
    "Da_Nang": 250, "Kuala_Lumpur": 240, "Dubai": 340,
    "Marrakech": 300, "Dakhla": 310, "Essaouira": 285,
    "Medellin": 240, "Bogota": 200, "Cartagena": 280,
    "Lima": 150, "Santiago": 270, "Buenos_Aires": 240,
    "Montevideo": 235, "Mexico_City": 230, "Playa_del_Carmen": 280,
    "Tallinn": 170,
}

# ── MAPA DE DIMENSIONES: 24 categorías ────────────────────────────────────────
# Cada entrada: (nombre_dimension, user_key, [city_feature_keys])
# El vector de usuario se proyecta sobre estas city features para cosine sim.
DIMENSION_MAP = [
    # 1. GASTRONOMÍA
    ("gastronomia",   "user_imp_gastronomia",   [
        "city_restaurants", "city_cafes",
        "city_gp_restaurant", "city_gp_cafe",  # GP genérico — fallback cuando OSM falla (islas, pueblos)
        "city_gp_fine_dining", "city_gp_vegan", "city_gp_market",
        "city_gp_seafood", "city_gp_coffee_shop",
    ]),
    # 2. VIDA NOCTURNA
    ("vida_nocturna", "user_imp_vida_nocturna",  [
        "city_gp_night_club", "city_gp_bar", "city_gp_pub",
        "city_gp_cocktail_bar", "city_gp_karaoke",
    ]),
    # 3. CULTURA
    ("cultura",       "user_imp_cultura",         [
        "city_gp_museum", "city_gp_historical_landmark",
        "city_gp_monument", "city_gp_cultural_center",
        "city_gp_performing_arts",
    ]),
    # 4. ARTE VISUAL
    ("arte_visual",   "user_imp_arte_visual",     [
        "city_gp_art_gallery", "city_gp_art_studio",
        "city_gp_sculpture",
    ]),
    # 5. NATURALEZA & OUTDOOR
    ("naturaleza",    "user_imp_naturaleza",       [
        "city_parks", "city_beaches", "city_gp_park",
        "city_gp_national_park",
        "city_gp_hiking_area",
    ]),
    # 6a. DEPORTE AGUA — kite, surf, windsurf, snorkel, vela, kayak
    # Ciudades ganadoras: Tarifa, Fuerteventura, Dakhla, Essaouira, Bali, Da Nang
    ("deporte_agua",   "user_imp_deporte_agua",    [
        "city_gp_surf_school", "city_gp_kitesurfing", "city_gp_windsurfing",
        "city_gp_wingfoil", "city_gp_snorkeling",
        "city_gp_marina", "city_beaches", "city_gp_beach",
    ]),
    # 6b. DEPORTE MONTAÑA — ski, snowboard, escalada, senderismo, aventura
    # Ciudades ganadoras: Chamonix, Innsbruck, Andorra, Granada
    ("deporte_montana", "user_imp_deporte_montana", [
        "city_gp_ski_resort", "city_gp_snowpark", "city_gp_ski_touring",
        "city_gp_hiking_area", "city_gp_adventure_sports",
    ]),
    # 6c. DEPORTE URBANO — gym, fitness, tenis, piscina, ciclismo
    # Ciudades ganadoras: grandes metrópolis con buena infraestructura deportiva
    ("deporte_urbano", "user_imp_deporte_urbano",  [
        "city_gyms", "city_gp_gym", "city_gp_fitness_center",
        "city_gp_tennis_court", "city_gp_swimming_pool",
        "city_gp_cycling_park", "city_gp_sports_complex",
    ]),
    # 7. BIENESTAR
    ("bienestar",     "user_imp_bienestar",        [
        "city_gp_spa", "city_gp_wellness", "city_gp_yoga_studio",
        "city_gp_sauna", "city_gp_massage", "city_gp_thermal_bath",
    ]),
    # 8. FAMILIA
    ("familia",       "user_imp_familia",          [
        "city_playgrounds", "city_schools", "city_kindergartens",
        "city_childcare", "city_gp_preschool", "city_gp_international_school",
        "city_gp_amusement_park", "city_gp_zoo", "city_gp_aquarium",
    ]),
    # 9. MASCOTAS
    ("mascotas",      "user_imp_mascotas",         [
        "city_dog_areas", "city_gp_dog_park",
        "city_gp_vet", "city_gp_pet_store",
    ]),
    # 10. NÓMADA DIGITAL
    ("nomada",        "user_imp_nomada",           [
        "city_coworking_osm", "city_gp_coworking", "city_gp_coliving",
        "city_gp_tech_hub",
        "city_gp_internet_cafe", "city_gp_library",
    ]),
    # 11. ALOJAMIENTO
    ("alojamiento",   "user_imp_alojamiento",      [
        "city_gp_hostel", "city_gp_extended_stay",
        "city_gp_bed_breakfast", "city_gp_coliving",
    ]),
    # 12. MOVILIDAD
    ("movilidad",     "user_imp_movilidad",        [
        "city_public_transport", "city_bicycle_lanes",
        "city_gp_subway", "city_gp_train_station",
        "city_gp_bus_station",
    ]),
    # 13. COMPRAS ESENCIALES
    ("compras",       "user_imp_compras",          [
        "city_gp_supermarket", "city_gp_grocery",
        "city_gp_shopping_mall", "city_gp_convenience",
    ]),
    # 14. SERVICIOS PERSONALES
    ("servicios",     "user_imp_servicios",        [
        "city_gp_barber", "city_gp_beauty_salon",
        "city_gp_laundry", "city_pharmacies",
    ]),
    # 15. SALUD
    ("salud",         "user_imp_salud",            [
        "city_hospitals", "city_pharmacies",
        "city_gp_dental", "city_gp_physiotherapist",
    ]),
    # 16. TURISMO
    ("turismo",       "user_imp_turismo",          [
        "city_gp_tourist_attraction", "city_gp_observation_deck",
    ]),
    # 17. EDUCACIÓN ADULTOS
    ("educacion",     "user_imp_educacion",        [
        "city_gp_university", "city_gp_language_school",
        "city_gp_library",
    ]),
    # 18. COMUNIDAD & RELIGIÓN
    ("comunidad",     "user_imp_comunidad",        [
        "city_gp_community_center", "city_gp_church",
        "city_gp_mosque", "city_gp_synagogue",
    ]),
    # 19. COSTE DE VIDA (inverso — ciudad barata = mejor para quien lo valora)
    ("coste",         "user_imp_coste",            [
        "city_coste_invertido",   # 1 - coste_normalizado
    ]),
    # 20. CLIMA
    ("clima",         "user_imp_clima",            [
        "city_temp_media_norm", "city_dias_sol_norm",
    ]),
    # 21. CALIDAD DE VIDA
    ("calidad_vida",  "user_imp_calidad_vida",     [
        "city_quality_of_life",
    ]),
    # 22. IMPACTO VISUAL / SOCIAL MEDIA
    ("social_media",  "user_imp_social_media",     [
        "city_gp_rooftop_bar", "city_gp_beach_club",
        "city_gp_street_art", "city_gp_photo_spot",
        "city_gp_observation_deck",
    ]),
    # 23. MÚSICA & FESTIVALES
    ("musica",        "user_imp_musica",           [
        "city_gp_concert_hall", "city_gp_live_music",
        "city_gp_jazz_club", "city_gp_folk_music",
        "city_gp_opera",
    ]),
    # 24. AUTENTICIDAD / ANTI-TURÍSTICO
    ("autenticidad",  "user_imp_autenticidad",     [
        "city_gp_folk_music", "city_gp_market",
        "city_gp_community_center", "city_gp_language_school",
    ]),
]

# Lista de user keys (para generar perfiles sintéticos)
USER_IMPORTANCE_KEYS = [dim[1] for dim in DIMENSION_MAP]


# ── CARGA DE DATOS ────────────────────────────────────────────────────────────

def load_all_cities(raw_dir: Path = RAW_DIR) -> dict:
    """
    Lee todos los *_raw.json individuales de data/raw/ y los devuelve
    como dict {nombre_ciudad: datos}.

    Si existe cities_raw.json (las 5 ciudades antiguas), también lo incluye.
    """
    cities = {}

    # Primero cargar JSONs individuales
    for path in sorted(glob.glob(str(raw_dir / "*_raw.json"))):
        fname = os.path.basename(path)
        if fname == "cities_raw.json":
            continue
        city_slug = fname.replace("_raw.json", "")
        # Normalizar a Title_Case
        city_name = "_".join(w.capitalize() for w in city_slug.split("_"))
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Algunos JSONs tienen el nombre como key raíz, otros son el dict directo
            if isinstance(data, dict) and len(data) == 1:
                inner_key = list(data.keys())[0]
                data = data[inner_key]
            cities[city_name] = data
        except Exception as e:
            print(f"  ⚠ Error leyendo {fname}: {e}")

    print(f"[OK] {len(cities)} ciudades cargadas desde JSONs individuales")
    return cities


def build_city_feature_matrix(cities_raw: dict) -> pd.DataFrame:
    """
    Construye DataFrame con una fila por ciudad y todas las features numéricas.
    Incluye las 24 categorías: música, kite, ski, social media, etc.

    Args:
        cities_raw: dict {nombre_ciudad: datos_json}

    Returns:
        DataFrame con index=nombre_ciudad y columnas city_*
    """
    # ── TIPOS DE CAMBIO A EUR (aproximados, abril 2026) ─────────────────────────
    # Numbeo devuelve los precios en moneda local del país.
    # Necesitamos convertir todo a EUR para poder comparar ciudades entre sí.
    # Fuente: tipos aproximados de mercado (actualizar periódicamente).
    EUR_RATES = {
        "EUR": 1.0,
        "GBP": 1.18,    # 1 GBP = 1.18 EUR (Londres)
        "SEK": 0.089,   # 1 SEK = 0.089 EUR (Estocolmo)
        "CZK": 0.040,   # 1 CZK = 0.040 EUR (Praga)
        "PLN": 0.234,   # 1 PLN = 0.234 EUR (Varsovia, Cracovia)
        "HUF": 0.0026,  # 1 HUF = 0.0026 EUR (Budapest)
        "RON": 0.201,   # 1 RON = 0.201 EUR (Bucarest)
        "BGN": 0.511,   # 1 BGN = 0.511 EUR (Sofía) — lev búlgaro, fijado al EUR
        "RSD": 0.0085,  # 1 RSD = 0.0085 EUR (Belgrado)
        "GEL": 0.338,   # 1 GEL = 0.338 EUR (Tbilisi)
        "MXN": 0.049,   # 1 MXN = 0.049 EUR (Ciudad de México)
        "COP": 0.00022, # 1 COP = 0.00022 EUR (Medellín, Cartagena)
        "USD": 0.92,    # 1 USD = 0.92 EUR (ciudades futuras)
        "THB": 0.026,   # 1 THB = 0.026 EUR (Bangkok, Chiang Mai)
        "IDR": 0.000057,# 1 IDR = 0.000057 EUR (Bali)
        "MYR": 0.208,   # 1 MYR = 0.208 EUR (Kuala Lumpur)
        "VND": 0.000037,# 1 VND = 0.000037 EUR (Da Nang)
        "AED": 0.250,   # 1 AED = 0.250 EUR (Dubai)
        "MAD": 0.092,   # 1 MAD = 0.092 EUR (Marrakech, Dakhla, Essaouira)
        "ARS": 0.00090, # 1 ARS = 0.00090 EUR (Buenos Aires)
        "CLP": 0.00097, # 1 CLP = 0.00097 EUR (Santiago)
        "PEN": 0.244,   # 1 PEN = 0.244 EUR (Lima)
        "UYU": 0.023,   # 1 UYU = 0.023 EUR (Montevideo)
        "CRC": 0.00170, # 1 CRC = 0.00170 EUR (Costa Rica — futuro)
        "INR": 0.011,   # 1 INR = 0.011 EUR (India — futuro)
    }

    # ── FALLBACK NUMBEO — valores reales aproximados en EUR (revisar con Numbeo mañana) ──
    # Para ciudades donde Numbeo devolvió error o no está indexada.
    # Formato: {nombre_ciudad: {rent_1br_center, meal_cheap, transport_monthly, basic_utilities}}
    # PENDIENTE: validar con Numbeo.com el día 09/04/2026
    NUMBEO_FALLBACK = {
        # España
        "Sevilla":       {"rent_1br_center": 850,  "meal_cheap": 12,  "transport_monthly": 40,  "basic_utilities": 100},
        "Tarifa":        {"rent_1br_center": 850,  "meal_cheap": 12,  "transport_monthly": 40,  "basic_utilities": 100},
        "Las_Palmas":    {"rent_1br_center": 900,  "meal_cheap": 12,  "transport_monthly": 50,  "basic_utilities": 100},
        "Fuerteventura": {"rent_1br_center": 900,  "meal_cheap": 15,  "transport_monthly": 50,  "basic_utilities": 100},
        # Francia / Andorra
        "Chamonix":      {"rent_1br_center": 1700, "meal_cheap": 20,  "transport_monthly": 80,  "basic_utilities": 150},
        "Andorra":       {"rent_1br_center": 1300, "meal_cheap": 15,  "transport_monthly": 0,   "basic_utilities": 100},
        # Europa del Este (ya en EUR tras conversión de moneda local)
        "Bucharest":     {"rent_1br_center": 700,  "meal_cheap": 5,   "transport_monthly": 14,  "basic_utilities": 80},
        "Sofia":         {"rent_1br_center": 770,  "meal_cheap": 6,   "transport_monthly": 25,  "basic_utilities": 80},
        "Belgrade":      {"rent_1br_center": 680,  "meal_cheap": 6,   "transport_monthly": 32,  "basic_utilities": 80},
        "Krakow":        {"rent_1br_center": 655,  "meal_cheap": 6,   "transport_monthly": 21,  "basic_utilities": 80},
        "Tbilisi":       {"rent_1br_center": 400,  "meal_cheap": 5,   "transport_monthly": 14,  "basic_utilities": 60},
        "Tallinn":       {"rent_1br_center": 900,  "meal_cheap": 13,  "transport_monthly": 30,  "basic_utilities": 100},
        # Latinoamérica (ya en EUR tras conversión)
        "Medellin":      {"rent_1br_center": 400,  "meal_cheap": 3,   "transport_monthly": 26,  "basic_utilities": 50},
        "Mexico_City":   {"rent_1br_center": 880,  "meal_cheap": 4,   "transport_monthly": 24,  "basic_utilities": 80},
        "Cartagena":     {"rent_1br_center": 550,  "meal_cheap": 3,   "transport_monthly": 26,  "basic_utilities": 50},
        # Buenos Aires: ARS muy devaluado — precios en EUR son bajos (~590€/mes total)
        # 600.000 ARS alquiler × 0.00090 = 540€ | 3.000 ARS comida × 0.00090 = 2.7€
        "Buenos_Aires":  {"rent_1br_center": 540,  "meal_cheap": 3,   "transport_monthly": 14,  "basic_utilities": 36},
    }

    rows = []

    for name, data in cities_raw.items():
        # Da_Nang: GP no devuelve resultados para Vietnam con la config actual
        # (prácticamente todos los features GP = 0). Detectado en EDA Fase 2.
        # POST-MVP: re-incluir cuando mejore cobertura GP para Asia del Sur.
        if name == "Da_Nang":
            continue

        infra    = data.get("osm",           {}).get("infrastructure", {})
        gp_raw   = data.get("google_places", {}).get("categories",     {})
        kp       = data.get("numbeo",        {}).get("key_prices",      {})
        qi       = data.get("numbeo",        {}).get("quality_indices", {})
        spd      = data.get("speedtest",     {})
        country  = data.get("country",       {})
        weather  = data.get("weather",       {}).get("current",         {})
        wikidata = data.get("wikidata",      {})

        # Tipo de cambio a EUR para esta ciudad
        currencies = country.get("currencies", ["EUR"])
        moneda = currencies[0] if currencies else "EUR"
        fx = EUR_RATES.get(moneda, 1.0)  # si no conocemos la moneda, asumimos EUR

        def gp(key):
            """Extrae el count de una categoría GP."""
            val = gp_raw.get(key, {})
            if isinstance(val, dict):
                return val.get("count", 0) or 0
            return 0

        def to_eur(val):
            """Convierte un valor de moneda local a EUR."""
            return (val or 0) * fx

        def cap(val, max_val):
            """Capea un conteo al máximo útil.
            Lógica: más allá de cierto umbral, la diferencia no importa para el usuario.
            37 restaurantes en una isla pequeña = suficiente. No hay que penalizarlo
            frente a una metrópoli con 600. El usuario no necesita 600 restaurantes.
            Futuro: reemplazar conteos por ratings medios (Google Maps, TripAdvisor).
            """
            return min(val or 0, max_val)

        # Si Numbeo no devolvió datos, usar fallback manual
        if not kp and name in NUMBEO_FALLBACK:
            kp = NUMBEO_FALLBACK[name]
            fx = 1.0  # fallback ya está en EUR

        # Coste de vida — convertido a EUR
        alquiler  = to_eur(kp.get("rent_1br_center",  0))
        utilities = to_eur(kp.get("basic_utilities",   0))
        transport = to_eur(kp.get("transport_monthly", 0))
        coste_vida = alquiler + utilities + transport

        rows.append({
            "city": name,

            # ── COSTE (todos en EUR) ───────────────────────────────────────────
            "city_coste_vida_estimado":  coste_vida,
            "city_alquiler_1br_centro":  alquiler,
            "city_transport_monthly":    transport,
            "city_meal_cheap":           to_eur(kp.get("meal_cheap", 0)),
            "city_quality_of_life":      qi.get("Quality of Life Index:", 0) or 0,

            # ── CLIMA ─────────────────────────────────────────────────────────
            "city_temp_actual_c":    weather.get("temp_c",       0) or 0,
            "city_temp_media_anual": TEMP_MEDIA.get(name, 15.0),
            "city_dias_sol_anual":   DIAS_SOL.get(name,   200),

            # ── NATURALEZA ────────────────────────────────────────────────────
            # cap(): limita el máximo para no penalizar ciudades pequeñas vs metrópolis.
            # Ej: 18 playas en Tarifa = suficiente. No hace falta 300 para puntuar 1.0.
            "city_beaches":              cap(infra.get("beaches",  0), 30),
            "city_parks":                cap(infra.get("parks",    0), 80),
            "city_gp_hiking_area":       cap(gp("hiking_area"),       30),
            "city_gp_park":              cap(gp("park"),              30),
            "city_gp_national_park":     gp("national_park"),
            "city_gp_beach":             cap(gp("beach"),             30),

            # ── DEPORTE ───────────────────────────────────────────────────────
            "city_gyms":                 cap(infra.get("gyms", 0),    20),
            "city_gp_gym":               cap(gp("gym"),               20),
            "city_gp_fitness_center":    cap(gp("fitness_center"),    20),
            "city_gp_surf_school":       cap(gp("surf_school"),       30),
            "city_gp_kitesurfing":       cap(gp("kitesurfing"),       30),
            "city_gp_windsurfing":       cap(gp("windsurfing"),       30),
            "city_gp_wingfoil":          cap(gp("wingfoil"),          20),
            "city_gp_ski_resort":        gp("ski_resort"),
            "city_gp_snowpark":          gp("snowpark"),
            "city_gp_ski_touring":       gp("ski_touring"),
            "city_gp_tennis_court":      cap(gp("tennis_court"),      20),
            "city_gp_cycling_park":      cap(gp("cycling_park"),      20),
            "city_gp_adventure_sports":  cap(gp("adventure_sports"),  20),
            "city_gp_swimming_pool":     cap(gp("swimming_pool"),     20),
            "city_gp_marina":            cap(gp("marina"),            15),
            "city_gp_snorkeling":        cap(gp("snorkeling"),        20),
            "city_gp_sports_complex":    cap(gp("sports_complex"),    20),

            # ── GASTRONOMÍA ───────────────────────────────────────────────────
            # city_restaurants/cafes de OSM pueden ser 600 en ciudades grandes.
            # Capeamos para que 50 restaurantes = "suficiente oferta".
            # city_gp_restaurant/cafe son fallback genérico (cubren islas y pueblos).
            "city_restaurants":          cap(infra.get("restaurants", 0), 80),
            "city_cafes":                cap(infra.get("cafes",       0), 60),
            "city_gp_restaurant":        cap(gp("restaurant"),            40),
            "city_gp_cafe":              cap(gp("cafe"),                  40),
            "city_gp_fine_dining":       cap(gp("fine_dining"),           20),
            "city_gp_vegan":             cap(gp("vegan_restaurant"),      20),
            "city_gp_vegetarian":        cap(gp("vegetarian_restaurant"), 20),
            "city_gp_market":            cap(gp("market"),                20),
            "city_gp_seafood":           cap(gp("seafood"),               20),
            "city_gp_coffee_shop":       cap(gp("coffee_shop"),           30),
            "city_gp_bakery":            cap(gp("bakery"),                25),
            "city_gp_wine_bar":          cap(gp("wine_bar"),              20),

            # ── VIDA NOCTURNA ─────────────────────────────────────────────────
            "city_gp_night_club":        cap(gp("night_club"),   20),
            "city_gp_bar":               cap(gp("bar"),          30),
            "city_gp_pub":               cap(gp("pub"),          20),
            "city_gp_cocktail_bar":      cap(gp("cocktail_bar"), 20),
            "city_gp_karaoke":           cap(gp("karaoke"),      10),

            # ── CULTURA ───────────────────────────────────────────────────────
            "city_gp_museum":            cap(gp("museum"),              25),
            "city_gp_historical_landmark": cap(gp("historical_landmark"), 25),
            "city_gp_monument":          cap(gp("monument"),            20),
            "city_gp_cultural_center":   cap(gp("cultural_center"),     20),
            "city_gp_performing_arts":   cap(gp("performing_arts"),     20),

            # ── ARTE VISUAL ───────────────────────────────────────────────────
            "city_gp_art_gallery":       cap(gp("art_gallery"),  20),
            "city_gp_art_studio":        cap(gp("art_studio"),   15),
            "city_gp_sculpture":         cap(gp("sculpture"),    20),

            # ── MÚSICA ────────────────────────────────────────────────────────
            "city_gp_concert_hall":      cap(gp("concert_hall"),    15),
            "city_gp_live_music":        cap(gp("live_music_venue"), 20),
            "city_gp_jazz_club":         cap(gp("jazz_club"),        15),
            "city_gp_folk_music":        cap(gp("folk_music"),       15),
            "city_gp_opera":             cap(gp("opera_house"),      10),

            # ── SOCIAL MEDIA ──────────────────────────────────────────────────
            "city_gp_rooftop_bar":       cap(gp("rooftop_bar"),      20),
            "city_gp_beach_club":        cap(gp("beach_club"),       20),
            "city_gp_street_art":        cap(gp("street_art"),       15),
            "city_gp_photo_spot":        cap(gp("photo_spot"),       15),
            "city_gp_observation_deck":  cap(gp("observation_deck"), 15),

            # ── BIENESTAR ─────────────────────────────────────────────────────
            "city_gp_spa":               cap(gp("spa"),           20),
            "city_gp_wellness":          cap(gp("wellness_center"), 15),
            "city_gp_yoga_studio":       cap(gp("yoga_studio"),   15),
            "city_gp_sauna":             cap(gp("sauna"),         10),
            "city_gp_massage":           cap(gp("massage"),       20),
            "city_gp_thermal_bath":      cap(gp("thermal_bath"),  10),

            # ── FAMILIA ───────────────────────────────────────────────────────
            "city_playgrounds":          cap(infra.get("playgrounds",   0), 30),
            "city_schools":              cap(infra.get("schools",       0), 60),
            "city_kindergartens":        cap(infra.get("kindergartens", 0), 20),
            "city_childcare":            cap(infra.get("childcare",     0), 20),
            "city_gp_preschool":         cap(gp("preschool"),            15),
            "city_gp_international_school": cap(gp("international_school"), 15),
            "city_gp_amusement_park":    cap(gp("amusement_park"),      10),
            "city_gp_zoo":               gp("zoo"),
            "city_gp_aquarium":          gp("aquarium"),

            # ── MASCOTAS ──────────────────────────────────────────────────────
            "city_dog_areas":            cap(infra.get("dog_areas", 0), 15),
            "city_gp_dog_park":          cap(gp("dog_park"),            10),
            "city_gp_vet":               cap(gp("veterinary_care"),     15),
            "city_gp_pet_store":         cap(gp("pet_store"),           10),

            # ── NÓMADA DIGITAL ────────────────────────────────────────────────
            "city_coworking_osm":        cap(infra.get("coworking_osm", 0), 10),
            "city_gp_coworking":         cap(gp("coworking"),               15),
            "city_gp_coliving":          cap(gp("coliving"),                10),
            "city_gp_tech_hub":          cap(gp("tech_hub"),                10),
            # city_internet_mbps: eliminada (09/04/2026) — 43/54 ciudades = 0
            # (dato ausente, no velocidad cero). POST-PRESENTACION: sustituir
            # por Ookla Global Fixed Broadband dataset cuando mejore cobertura.
            "city_gp_internet_cafe":     cap(gp("internet_cafe"),           10),
            "city_gp_library":           cap(gp("library"),                 15),

            # ── ALOJAMIENTO ───────────────────────────────────────────────────
            "city_gp_hostel":            cap(gp("hostel"),             20),
            "city_gp_extended_stay":     cap(gp("extended_stay_hotel"), 15),
            "city_gp_bed_breakfast":     cap(gp("bed_and_breakfast"),  15),

            # ── MOVILIDAD ─────────────────────────────────────────────────────
            "city_public_transport":     cap(infra.get("public_transport", 0), 100),
            "city_bicycle_lanes":        cap(infra.get("bicycle_lanes",   0),  80),
            "city_gp_subway":            cap(gp("subway_station"),  20),
            "city_gp_train_station":     cap(gp("train_station"),   15),
            "city_gp_bus_station":       cap(gp("bus_station"),     15),

            # ── COMPRAS ───────────────────────────────────────────────────────
            "city_gp_supermarket":       cap(gp("supermarket"),    25),
            "city_gp_grocery":           cap(gp("grocery_store"),  25),
            "city_gp_shopping_mall":     cap(gp("shopping_mall"),  10),
            "city_gp_convenience":       cap(gp("convenience_store"), 20),

            # ── SERVICIOS PERSONALES ──────────────────────────────────────────
            "city_gp_barber":            gp("barber_shop"),
            "city_gp_beauty_salon":      gp("beauty_salon"),
            "city_gp_laundry":           gp("laundry"),
            "city_pharmacies":           infra.get("pharmacies", 0),

            # ── SALUD ─────────────────────────────────────────────────────────
            "city_hospitals":            infra.get("hospitals", 0),
            "city_gp_dental":            gp("dental_clinic"),
            "city_gp_physiotherapist":   gp("physiotherapist"),

            # ── TURISMO ───────────────────────────────────────────────────────
            "city_gp_tourist_attraction": gp("tourist_attraction"),

            # ── EDUCACIÓN ADULTOS ─────────────────────────────────────────────
            "city_gp_university":        gp("university"),
            "city_gp_language_school":   gp("language_school"),

            # ── COMUNIDAD ─────────────────────────────────────────────────────
            "city_gp_community_center":  gp("community_center"),
            "city_gp_church":            gp("church"),
            "city_gp_mosque":            gp("mosque"),
            "city_gp_synagogue":         gp("synagogue"),

            # ── TAMAÑO DE CIUDAD (Wikidata) ───────────────────────────────────
            # population_density = habitantes / km² → proxy del "tamaño percibido"
            # Tarifa: ~50 hab/km²  |  Barcelona: ~16.000  |  Berlín: ~4.200
            # Permite al usuario elegir entre pueblo (densidad baja) y metrópoli (alta).
            "city_population":         wikidata.get("population", 0) or 0,
            "city_area_km2":           wikidata.get("area_km2",   np.nan),
            "city_population_density": (
                wikidata["population"] / wikidata["area_km2"]
                if wikidata.get("population") and wikidata.get("area_km2")
                else np.nan
            ),

            # ── PAÍS ──────────────────────────────────────────────────────────
            "city_schengen":         int(country.get("schengen",  False)),
            "city_moneda_eur":       int("EUR" in country.get("currencies", [])),
            # Idioma nativo (texto) — el primer idioma oficial del país
            "city_idioma_nativo":    country.get("languages", ["Desconocido"])[0],

            # ── IDIOMA — 5 columnas originales (mantenidas sin renombrar) ─────
            # DECISIÓN ARQUITECTURA (09/04/2026):
            # Según ARQUETIPOS_158_FEATURES.md estas 5 deberían renombrarse a
            # city_idioma_hablado_* para alinearse con el esquema de 158 features.
            # NO se renombran ahora porque streamlit_app.py v1 y ranker.py las
            # leen con estos nombres exactos (apply_language_boost, filtros).
            # Pendiente: renombrar al construir streamlit v2 + nuevo ranker.
            # Si aparecen KeyError con 'city_idioma_*', revisar este punto.
            "city_idioma_espanol":   int("Spanish"    in country.get("languages", [])),
            "city_idioma_ingles":    int("English"    in country.get("languages", [])),
            "city_idioma_frances":   int("French"     in country.get("languages", [])),
            "city_idioma_aleman":    int("German"     in country.get("languages", [])),
            "city_idioma_portugues": int("Portuguese" in country.get("languages", [])),

            # ── IDIOMA NATIVO — 12 columnas nuevas ───────────────────────────
            # Binario 0/1: el idioma es lengua oficial del país de la ciudad.
            # Fuente: RestCountries API, campo 'languages'.
            "city_idioma_nativo_italiano":  int("Italian"   in country.get("languages", [])),
            "city_idioma_nativo_griego":    int("Greek"     in country.get("languages", [])),
            "city_idioma_nativo_holandes":  int("Dutch"     in country.get("languages", [])),
            "city_idioma_nativo_checo":     int("Czech"     in country.get("languages", [])),
            "city_idioma_nativo_hungaro":   int("Hungarian" in country.get("languages", [])),
            "city_idioma_nativo_rumano":    int("Romanian"  in country.get("languages", [])),
            "city_idioma_nativo_georgiano": int("Georgian"  in country.get("languages", [])),
            "city_idioma_nativo_bulgaro":   int("Bulgarian" in country.get("languages", [])),
            "city_idioma_nativo_polaco":    int("Polish"    in country.get("languages", [])),
            "city_idioma_nativo_serbio":    int("Serbian"   in country.get("languages", [])),
            "city_idioma_nativo_tailandes": int("Thai"      in country.get("languages", [])),
            "city_idioma_nativo_catalan":   int("Catalan"   in country.get("languages", [])),

            # ── IDIOMA HABLADO CON FACILIDAD — 6 columnas nuevas ─────────────
            # MVP: mismo valor que nativo (binario RestCountries).
            # Futuro v2: reemplazar por dato continuo 0-1 (Eurobarómetro u otra
            # fuente de usabilidad real del idioma en la calle).
            "city_idioma_hablado_italiano":  int("Italian"   in country.get("languages", [])),
            "city_idioma_hablado_griego":    int("Greek"     in country.get("languages", [])),
            "city_idioma_hablado_holandes":  int("Dutch"     in country.get("languages", [])),
            "city_idioma_hablado_checo":     int("Czech"     in country.get("languages", [])),
            "city_idioma_hablado_hungaro":   int("Hungarian" in country.get("languages", [])),
            "city_idioma_hablado_rumano":    int("Romanian"  in country.get("languages", [])),
        })

    df = pd.DataFrame(rows).set_index("city")

    # ── Rellenar NaN en features de Wikidata (ciudades sin datos = 0) ─────────
    # city_area_km2 y city_population_density pueden ser NaN si Wikidata no devolvió área.
    # Rellenamos con 0 para que el MinMaxScaler pueda procesar sin errores.
    # En el modelo, densidad=0 significa "dato no disponible", no "ciudad sin habitantes".
    df["city_population"]         = df["city_population"].fillna(0)
    df["city_area_km2"]           = df["city_area_km2"].fillna(0)
    df["city_population_density"] = df["city_population_density"].fillna(0)

    # ── Features derivadas (necesitan el df completo para normalizar) ──────────
    coste = df["city_coste_vida_estimado"].copy()
    coste_min, coste_max = coste.min(), coste.max()
    if coste_max > coste_min:
        coste_norm = (coste - coste_min) / (coste_max - coste_min)
    else:
        coste_norm = pd.Series(0.5, index=df.index)
    df["city_coste_invertido"] = 1.0 - coste_norm   # mayor valor = más barata

    temp = df["city_temp_media_anual"].copy()
    df["city_temp_media_norm"] = (temp - temp.min()) / (temp.max() - temp.min() + 1e-9)

    sol = df["city_dias_sol_anual"].copy()
    df["city_dias_sol_norm"] = (sol - sol.min()) / (sol.max() - sol.min() + 1e-9)

    return df


# ── CLASE PRINCIPAL ───────────────────────────────────────────────────────────

class CityFeatureBuilder:
    """
    Construye vectores de ciudad normalizados y calcula Cosine Similarity
    entre el perfil de un usuario (24 dimensiones) y cada ciudad.
    """

    def __init__(self):
        self.scaler        = MinMaxScaler()
        self.city_features = None
        self.fitted        = False

    def fit(self, city_df: pd.DataFrame) -> "CityFeatureBuilder":
        """Aprende Min-Max de todas las features numéricas de ciudad.
        Las columnas de texto (city_idioma_nativo, etc.) se guardan aparte.
        """
        # Separar columnas numéricas de columnas de texto
        self.text_features = list(city_df.select_dtypes(include="object").columns)
        numeric_df = city_df.select_dtypes(include="number")
        self.city_features = list(numeric_df.columns)
        self.scaler.fit(numeric_df)
        self.fitted = True
        print(f"CityFeatureBuilder: {len(self.city_features)} features numéricas, "
              f"{len(self.text_features)} columnas de texto, "
              f"{len(city_df)} ciudades")
        return self

    def transform(self, city_df: pd.DataFrame) -> np.ndarray:
        """Normaliza features numéricas a [0,1]."""
        assert self.fitted, "Llama a .fit() primero"
        return self.scaler.transform(city_df[self.city_features])

    def build_user_vector(self, user_prefs: dict) -> np.ndarray:
        """
        Proyecta las 24 importancias del usuario sobre el espacio de features
        de ciudad usando DIMENSION_MAP.

        Para cada dimensión, el peso del usuario se asigna a todas las
        city_features correspondientes. El resultado es un vector del
        mismo tamaño que el vector de ciudad.
        """
        assert self.fitted, "Llama a .fit() primero"
        vec = np.zeros(len(self.city_features))
        feat_idx = {name: i for i, name in enumerate(self.city_features)}

        for _dim_name, user_key, city_keys in DIMENSION_MAP:
            importancia = float(user_prefs.get(user_key, 0.0))
            for ck in city_keys:
                if ck in feat_idx:
                    vec[feat_idx[ck]] = max(vec[feat_idx[ck]], importancia)

        return vec

    def cosine_scores(self, user_prefs: dict, city_df: pd.DataFrame) -> pd.Series:
        """
        Calcula Cosine Similarity entre un usuario y todas las ciudades.

        Returns:
            pd.Series con ciudad como índice y score [0,1]
        """
        city_matrix = self.transform(city_df)
        user_vec    = self.build_user_vector(user_prefs).reshape(1, -1)
        scores      = cosine_similarity(user_vec, city_matrix)[0]
        return pd.Series(scores, index=city_df.index, name="cosine_sim")

    def top_features_for_city(self, user_prefs: dict, city_name: str,
                               city_df: pd.DataFrame, top_n: int = 5) -> list:
        """
        Devuelve las N dimensiones que más contribuyen al score de una ciudad.
        Útil para explicar la recomendación en Streamlit.

        Returns:
            list de (dimension_name, contribución 0-1)
        """
        city_matrix_norm = self.transform(city_df)
        city_idx = list(city_df.index).index(city_name)
        city_vec = city_matrix_norm[city_idx]
        feat_idx = {name: i for i, name in enumerate(self.city_features)}

        contributions = []
        for dim_name, user_key, city_keys in DIMENSION_MAP:
            importancia = float(user_prefs.get(user_key, 0.0))
            if importancia < 0.05:
                continue
            city_vals = [city_vec[feat_idx[ck]]
                         for ck in city_keys if ck in feat_idx]
            city_val = np.mean(city_vals) if city_vals else 0.0
            contrib = importancia * city_val
            contributions.append((dim_name, round(contrib, 4)))

        contributions.sort(key=lambda x: x[1], reverse=True)
        return contributions[:top_n]


# ── SCRIPT DIRECTO ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== features.py v2 — test rápido ===\n")

    cities = load_all_cities()
    city_df = build_city_feature_matrix(cities)
    print(f"Matrix: {city_df.shape[0]} ciudades × {city_df.shape[1]} features\n")

    builder = CityFeatureBuilder().fit(city_df)

    # Guardar matrix para el entrenamiento
    out = ROOT / "data" / "processed" / "city_features.csv"
    city_df.to_csv(out)
    print(f"Guardado: {out}\n")

    # Test: nómada estacional (kite+ski+internet)
    perfil = {
        "user_imp_deporte":   0.95,
        "user_imp_nomada":    0.85,
        "user_imp_naturaleza":0.80,
        "user_imp_coste":     0.65,
        "user_imp_clima":     0.60,
    }
    scores = builder.cosine_scores(perfil, city_df)
    print("Top 10 - Nomada estacional (kite+ski):")
    for city, sc in scores.sort_values(ascending=False).head(10).items():
        bar = "#" * int(sc * 30)
        print(f"  {city:<20}: {sc:.3f}  {bar}")
