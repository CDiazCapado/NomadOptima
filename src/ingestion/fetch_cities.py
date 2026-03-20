"""
NomadOptima - Data Ingestion v5
Fuentes: Numbeo + wttr.in + Wikipedia + RestCountries + OpenStreetMap + Google Places + Speedtest

Mejoras v5:
  - Place Types oficiales de Google Places API (New) en lugar de Text Search libre
  - Sistema de cadencia inteligente: cada fuente se actualiza solo cuando toca
    · weather       → cada 7 días
    · numbeo        → cada 30 días
    · google_places → cada 90 días
    · osm           → cada 90 días
    · speedtest     → cada 90 días
    · wikipedia     → cada 180 días
    · country       → cada 180 días
  - needs_refresh(): lee fetched_at del JSON existente antes de llamar a la API
  - 31 place types: 27 oficiales (Nearby Search) + 4 sin type oficial (Text Search)
  - Resumen final de qué fuentes se actualizaron y cuáles se saltaron

Run: python src/ingestion/fetch_cities.py
"""

import requests
import json
import time
import os
import re
from datetime import datetime
from urllib.parse import unquote
from bs4 import BeautifulSoup

# ── CARGAR .env ───────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ .env cargado")
except ImportError:
    print("⚠  python-dotenv no instalado. Ejecuta: pip install python-dotenv")

# ── CONFIG ────────────────────────────────────────────────────────────────────

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Cadencia de actualización por fuente (en días)
REFRESH_CADENCE = {
    "weather":       7,    # meteorología cambia semanalmente
    "numbeo":        30,   # precios se mueven mensualmente
    "google_places": 90,   # infraestructura de ciudad es muy estable
    "osm":           90,   # infraestructura urbana es muy estable
    "speedtest":     90,   # índice Speedtest se publica trimestralmente
    "wikipedia":     180,  # datos descriptivos casi no cambian
    "country":       180,  # idioma, zona horaria, Schengen — casi nunca
}

CITIES = [
    {
        "name":       "Malaga",
        "display":    "Málaga",
        "slug":       "Malaga",
        "lat":        36.7213,
        "lon":        -4.4214,
        "country":    "Spain",
        "numbeo":     "Malaga",
        "wiki":       "Málaga",
        "google":     "Málaga, Spain",
        "osm_area":   "Málaga",
        "osm_admin":  "8",
    },
    {
        "name":       "Paris",
        "display":    "París",
        "slug":       "Paris",
        "lat":        48.8566,
        "lon":         2.3522,
        "country":    "France",
        "numbeo":     "Paris",
        "wiki":       "Paris",
        "google":     "Paris, France",
        "osm_area":   "Paris",
        "osm_admin":  "8",
    },
]

# ── GOOGLE PLACE TYPES ────────────────────────────────────────────────────────
# Fuente oficial: developers.google.com/maps/documentation/places/web-service/place-types
#
# Estrategia:
#   - Types con equivalente oficial → Nearby Search (New) con includedTypes
#     Más preciso, reproducible y consistente entre ciudades.
#   - Conceptos sin type oficial → Text Search (New) como fallback
#     Marcados con "text_search": True
#
# Agrupados por dimensión del perfil de usuario de NomadOptima.

GOOGLE_PLACE_TYPES = {
    # ── Deporte y outdoor ────────────────────────────────────────────────────
    "gym":               {"type": "gym",                    "dimension": "sport"},
    "swimming_pool":     {"type": "swimming_pool",          "dimension": "sport"},
    "sports_club":       {"type": "sports_club",            "dimension": "sport"},
    "adventure_sports":  {"type": "adventure_sports_center","dimension": "sport"},
    "hiking":            {"type": "hiking_area",            "dimension": "sport"},
    "marina":            {"type": "marina",                 "dimension": "sport"},
    "yoga_studio":       {"type": "yoga_studio",            "dimension": "wellness"},
    "cycling_park":      {"type": "cycling_park",           "dimension": "sport"},
    # ── Naturaleza ───────────────────────────────────────────────────────────
    "park":              {"type": "park",                   "dimension": "nature"},
    "beach":             {"type": "beach",                  "dimension": "nature"},
    "dog_park":          {"type": "dog_park",               "dimension": "pets"},
    "national_park":     {"type": "national_park",          "dimension": "nature"},
    # ── Gastronomía ──────────────────────────────────────────────────────────
    "restaurant":        {"type": "restaurant",             "dimension": "gastronomy"},
    "coffee_shop":       {"type": "coffee_shop",            "dimension": "gastronomy"},
    "bar":               {"type": "bar",                    "dimension": "nightlife"},
    "fine_dining":       {"type": "fine_dining_restaurant", "dimension": "gastronomy"},
    "vegan_restaurant":  {"type": "vegan_restaurant",       "dimension": "gastronomy"},
    "market":            {"type": "market",                 "dimension": "gastronomy"},
    # ── Cultura y entretenimiento ────────────────────────────────────────────
    "museum":            {"type": "museum",                 "dimension": "culture"},
    "art_gallery":       {"type": "art_gallery",            "dimension": "culture"},
    "performing_arts":   {"type": "performing_arts_theater","dimension": "culture"},
    "night_club":        {"type": "night_club",             "dimension": "nightlife"},
    "movie_theater":     {"type": "movie_theater",          "dimension": "culture"},
    # ── Bienestar ────────────────────────────────────────────────────────────
    "spa":               {"type": "spa",                    "dimension": "wellness"},
    "wellness_center":   {"type": "wellness_center",        "dimension": "wellness"},
    # ── Movilidad ────────────────────────────────────────────────────────────
    "subway_station":    {"type": "subway_station",         "dimension": "mobility"},
    "train_station":     {"type": "train_station",          "dimension": "mobility"},
    # ── Mascotas ─────────────────────────────────────────────────────────────
    "veterinary_care":   {"type": "veterinary_care",        "dimension": "pets"},
    # ── Educación ────────────────────────────────────────────────────────────
    "university":        {"type": "university",             "dimension": "education"},
    # ── Sin type oficial → Text Search ───────────────────────────────────────
    "coworking":         {"query": "coworking space",        "dimension": "digital_nomad",
                          "text_search": True},
    "surf_school":       {"query": "surf school",            "dimension": "sport",
                          "text_search": True},
    "language_school":   {"query": "language school",        "dimension": "education",
                          "text_search": True},
    "tech_hub":          {"query": "technology startup hub", "dimension": "digital_nomad",
                          "text_search": True},
}

# Headers anti-403 para Numbeo
NUMBEO_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer":         "https://www.numbeo.com/",
    "Connection":      "keep-alive",
}


# ── SISTEMA DE CADENCIA ───────────────────────────────────────────────────────

def needs_refresh(city_name, source):
    """
    Comprueba si una fuente necesita actualizarse comparando su fetched_at
    con la cadencia definida en REFRESH_CADENCE.
    Devuelve True si hay que actualizar, False si los datos son recientes.
    """
    path = os.path.join(OUTPUT_DIR, f"{city_name.lower()}_raw.json")
    if not os.path.exists(path):
        return True  # primera ejecución
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        fetched_str = data.get(source, {}).get("fetched_at")
        if not fetched_str:
            return True
        fetched_dt = datetime.fromisoformat(fetched_str)
        days_old = (datetime.now() - fetched_dt).days
        cadence = REFRESH_CADENCE.get(source, 30)
        if days_old < cadence:
            days_remaining = cadence - days_old
            print(f"    SKIP: datos de hace {days_old}d "
                  f"(cadencia {cadence}d, próxima en {days_remaining}d)")
            return False
        return True
    except Exception:
        return True  # ante cualquier error, refresca


def load_existing_source(city_name, source):
    """Devuelve los datos existentes de una fuente desde el JSON en disco."""
    path = os.path.join(OUTPUT_DIR, f"{city_name.lower()}_raw.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get(source, {})
    except Exception:
        return {}


# ── 1. NUMBEO ─────────────────────────────────────────────────────────────────

def fetch_numbeo(city):
    print(f"  [Numbeo] {city['display']}...")
    result = {
        "city":            city["display"],
        "source":          "numbeo",
        "fetched_at":      datetime.now().isoformat(),
        "prices":          {},
        "key_prices":      {},
        "quality_indices": {},
    }
    try:
        url = f"https://www.numbeo.com/cost-of-living/in/{city['numbeo']}"
        r = requests.get(url, headers=NUMBEO_HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "data_wide_table"})
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    item = cols[0].get_text(strip=True)
                    price_text = cols[1].get_text(strip=True)
                    numbers = re.findall(r"[\d]+\.?\d*", price_text.replace(",", ""))
                    if numbers:
                        try:
                            result["prices"][item] = float(numbers[0])
                        except ValueError:
                            pass

        key_map = {
            "rent_1br_center":   "Apartment (1 bedroom) in City Centre",
            "rent_1br_outside":  "Apartment (1 bedroom) Outside of Centre",
            "meal_cheap":        "Meal, Inexpensive Restaurant",
            "meal_midrange":     "Meal for 2 People, Mid-range Restaurant",
            "coffee":            "Cappuccino (regular)",
            "beer":              "Domestic Beer (0.5 liter draught)",
            "transport_monthly": "Monthly Pass (Regular Price)",
            "gym_monthly":       "Fitness Club, Monthly Fee for 1 Adult",
            "internet_monthly":  "Internet (60 Mbps",
            "basic_utilities":   "Basic (Electricity, Heating, Cooling, Water, Garbage)",
        }
        for key, keyword in key_map.items():
            for price_key in result["prices"]:
                if keyword.lower() in price_key.lower():
                    result["key_prices"][key] = result["prices"][price_key]
                    break

        time.sleep(2)

        url2 = f"https://www.numbeo.com/quality-of-life/in/{city['numbeo']}"
        r2 = requests.get(url2, headers=NUMBEO_HEADERS, timeout=20)
        soup2 = BeautifulSoup(r2.text, "html.parser")
        table2 = (
            soup2.find("table", {"class": "table_indices_top"}) or
            soup2.find("table", {"class": "table_indices"})
        )
        if table2:
            for row in table2.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    label = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    numbers = re.findall(r"[\d]+\.?\d*", value)
                    if numbers:
                        result["quality_indices"][label] = float(numbers[0])

        print(f"    OK: {len(result['prices'])} precios, "
              f"{len(result['key_prices'])} key prices, "
              f"{len(result['quality_indices'])} índices")
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        print(f"    ERROR HTTP {status}: {e}")
        result["error"] = f"HTTP {status}"
    except Exception as e:
        print(f"    ERROR: {e}")
        result["error"] = str(e)
    return result


# ── 2. CLIMA (wttr.in) ────────────────────────────────────────────────────────

def fetch_weather(city):
    print(f"  [Weather] {city['display']}...")
    try:
        r = requests.get(f"https://wttr.in/{city['slug']}?format=j1", timeout=15)
        r.raise_for_status()
        data = r.json()
        current = data["current_condition"][0]
        result = {
            "city":       city["display"],
            "source":     "wttr.in",
            "fetched_at": datetime.now().isoformat(),
            "current": {
                "temp_c":       float(current["temp_C"]),
                "feels_like_c": float(current["FeelsLikeC"]),
                "humidity_pct": float(current["humidity"]),
                "description":  current["weatherDesc"][0]["value"],
                "wind_kmph":    float(current["windspeedKmph"]),
                "uv_index":     float(current.get("uvIndex", 0)),
            },
            "forecast": []
        }
        for day in data.get("weather", []):
            result["forecast"].append({
                "date":      day["date"],
                "max_c":     float(day["maxtempC"]),
                "min_c":     float(day["mintempC"]),
                "avg_c":     float(day["avgtempC"]),
                "desc":      day["hourly"][4]["weatherDesc"][0]["value"],
                "sun_hours": float(day.get("sunHour", 0)),
                "uv_index":  float(day.get("uvIndex", 0)),
            })
        print(f"    OK: {result['current']['temp_c']}°C, "
              f"{result['current']['description']}, "
              f"viento {result['current']['wind_kmph']} km/h")
        return result
    except Exception as e:
        print(f"    ERROR: {e}")
        return {"city": city["display"], "source": "wttr.in",
                "fetched_at": datetime.now().isoformat(), "error": str(e)}


# ── 3. WIKIPEDIA ──────────────────────────────────────────────────────────────

def fetch_wikipedia(city):
    print(f"  [Wikipedia] {city['display']}...")
    try:
        wiki_title = unquote(city["wiki"])
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}",
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        result = {
            "city":        city["display"],
            "source":      "wikipedia",
            "fetched_at":  datetime.now().isoformat(),
            "description": data.get("description", ""),
            "extract":     data.get("extract", "")[:800],
            "lat":         city["lat"],
            "lon":         city["lon"],
            "country":     city["country"],
            "wiki_url":    data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
        print(f"    OK: '{result['description']}'")
        return result
    except Exception as e:
        print(f"    ERROR: {e}")
        return {"city": city["display"], "source": "wikipedia",
                "fetched_at": datetime.now().isoformat(), "error": str(e)}


# ── 4. REST COUNTRIES ─────────────────────────────────────────────────────────

def fetch_country_data(city):
    print(f"  [RestCountries] {city['country']}...")
    try:
        r = requests.get(
            f"https://restcountries.com/v3.1/name/{city['country']}?fullText=true",
            timeout=10
        )
        r.raise_for_status()
        data = r.json()[0]
        result = {
            "city":       city["display"],
            "source":     "restcountries",
            "fetched_at": datetime.now().isoformat(),
            "country":    city["country"],
            "capital":    data.get("capital", [None])[0],
            "languages":  list(data.get("languages", {}).values()),
            "currencies": list(data.get("currencies", {}).keys()),
            "timezone":   data.get("timezones", [None])[0],
            "region":     data.get("region", ""),
            "subregion":  data.get("subregion", ""),
            "population": data.get("population", 0),
            "schengen":   city["country"] in [
                "Spain", "France", "Portugal", "Germany",
                "Italy", "Netherlands", "Belgium"
            ],
            "eu_member":  city["country"] in [
                "Spain", "France", "Portugal", "Germany",
                "Italy", "Netherlands", "Belgium"
            ],
        }
        print(f"    OK: langs={result['languages']}, "
              f"tz={result['timezone']}, schengen={result['schengen']}")
        return result
    except Exception as e:
        print(f"    ERROR: {e}")
        return {"city": city["display"], "source": "restcountries",
                "fetched_at": datetime.now().isoformat(), "error": str(e)}


# ── 5. OPENSTREETMAP (Overpass API) ───────────────────────────────────────────

def fetch_osm(city):
    print(f"  [OpenStreetMap] {city['display']}...")
    overpass_url = "https://overpass-api.de/api/interpreter"

    osm_queries = {
        "bicycle_lanes":    'way["highway"="cycleway"](area.searchArea);',
        "parks":            'way["leisure"="park"](area.searchArea);',
        "public_transport": 'node["public_transport"="stop_position"](area.searchArea);',
        "coworking_osm":    'node["amenity"="coworking_space"](area.searchArea);',
        "universities":     '(node["amenity"="university"](area.searchArea);'
                            ' way["amenity"="university"](area.searchArea););',
        "hospitals":        'node["amenity"="hospital"](area.searchArea);',
        "dog_areas":        'node["leisure"="dog_park"](area.searchArea);',
        "bike_parking":     'node["amenity"="bicycle_parking"](area.searchArea);',
        "restaurants":      'node["amenity"="restaurant"](area.searchArea);',
        "cafes":            'node["amenity"="cafe"](area.searchArea);',
        "gyms":             'node["leisure"="fitness_centre"](area.searchArea);',
        "beaches":          'way["natural"="beach"](area.searchArea);',
    }

    result = {
        "city":           city["display"],
        "source":         "openstreetmap",
        "fetched_at":     datetime.now().isoformat(),
        "infrastructure": {},
    }

    for category, query in osm_queries.items():
        try:
            full_query = f"""
            [out:json][timeout:30];
            area[name="{city['osm_area']}"]["admin_level"="{city['osm_admin']}"]->.searchArea;
            ({query});
            out count;
            """
            r = requests.post(overpass_url, data={"data": full_query}, timeout=40)
            r.raise_for_status()
            data = r.json()
            count = data.get("elements", [{}])[0].get("tags", {}).get("total", 0)
            result["infrastructure"][category] = int(count)
            time.sleep(1.5)
        except Exception as e:
            result["infrastructure"][category] = None
            print(f"      WARN [{category}]: {e}")

    found = sum(v for v in result["infrastructure"].values() if v is not None)
    print(f"    OK: {len(result['infrastructure'])} categorías, "
          f"{found} elementos totales")
    return result


# ── 6. GOOGLE PLACES API (New) ────────────────────────────────────────────────

def fetch_google_places(city):
    print(f"  [Google Places] {city['display']}...")

    if not GOOGLE_API_KEY:
        print("    SKIP: GOOGLE_API_KEY no encontrada.")
        print("    → Añade GOOGLE_API_KEY=tu_key en el archivo .env")
        return {
            "city":       city["display"],
            "source":     "google_places",
            "fetched_at": datetime.now().isoformat(),
            "skipped":    True,
            "reason":     "GOOGLE_API_KEY not set",
        }

    result = {
        "city":       city["display"],
        "source":     "google_places",
        "fetched_at": datetime.now().isoformat(),
        "categories": {},
    }

    nearby_url = "https://places.googleapis.com/v1/places:searchNearby"
    text_url   = "https://places.googleapis.com/v1/places:searchText"

    for category_key, config in GOOGLE_PLACE_TYPES.items():
        try:
            if config.get("text_search"):
                # Text Search para tipos sin equivalente oficial
                payload = {
                    "textQuery": f"{config['query']} in {city['google']}",
                    "locationBias": {
                        "circle": {
                            "center": {"latitude": city["lat"], "longitude": city["lon"]},
                            "radius": 20000.0,
                        }
                    },
                    "maxResultCount": 20,
                }
                headers = {
                    "Content-Type":    "application/json",
                    "X-Goog-Api-Key":  GOOGLE_API_KEY,
                    "X-Goog-FieldMask": "places.displayName,places.rating,places.formattedAddress",
                }
                r = requests.post(text_url, json=payload, headers=headers, timeout=15)

            else:
                # Nearby Search (New) con type oficial — más preciso y reproducible
                payload = {
                    "includedTypes": [config["type"]],
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": city["lat"], "longitude": city["lon"]},
                            "radius": 20000.0,
                        }
                    },
                    "maxResultCount": 20,
                }
                headers = {
                    "Content-Type":    "application/json",
                    "X-Goog-Api-Key":  GOOGLE_API_KEY,
                    "X-Goog-FieldMask": "places.displayName,places.rating,"
                                        "places.formattedAddress,places.types",
                }
                r = requests.post(nearby_url, json=payload, headers=headers, timeout=15)

            r.raise_for_status()
            data    = r.json()
            places  = data.get("places", [])
            ratings = [p["rating"] for p in places if "rating" in p]

            result["categories"][category_key] = {
                "count":      len(places),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "dimension":  config["dimension"],
                "method":     "text_search" if config.get("text_search") else "nearby_search",
                "top_3": [
                    {
                        "name":    p.get("displayName", {}).get("text", ""),
                        "rating":  p.get("rating"),
                        "address": p.get("formattedAddress", ""),
                    }
                    for p in places[:3]
                ],
            }
            time.sleep(0.3)

        except requests.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            result["categories"][category_key] = {
                "count": 0, "error": f"HTTP {status}", "dimension": config["dimension"],
            }
        except Exception as e:
            result["categories"][category_key] = {
                "count": 0, "error": str(e), "dimension": config["dimension"],
            }

    total    = sum(v.get("count", 0) for v in result["categories"].values())
    errors   = sum(1 for v in result["categories"].values() if "error" in v)
    official = sum(1 for v in result["categories"].values()
                   if v.get("method") == "nearby_search")
    text     = sum(1 for v in result["categories"].values()
                   if v.get("method") == "text_search")
    print(f"    OK: {total} lugares | "
          f"{official} types oficiales, {text} text search | {errors} errores")
    return result


# ── 7. SPEEDTEST ──────────────────────────────────────────────────────────────

def fetch_speedtest(city):
    print(f"  [Speedtest] {city['display']}...")
    fallback = {
        "Spain":  {"fixed_download_mbps": 213, "fixed_upload_mbps": 196,
                   "mobile_download_mbps": 98,  "mobile_upload_mbps": 15,
                   "fixed_rank_global": 14},
        "France": {"fixed_download_mbps": 185, "fixed_upload_mbps": 170,
                   "mobile_download_mbps": 89,  "mobile_upload_mbps": 12,
                   "fixed_rank_global": 18},
    }
    result = {
        "city":        city["display"],
        "source":      "speedtest_global_index_2024",
        "fetched_at":  datetime.now().isoformat(),
        "country":     city["country"],
        "granularity": "country",
        "note":        "Datos a nivel país (Ookla Speedtest Global Index 2024). "
                       "Para granularidad ciudad usar Numbeo Internet Speed.",
    }
    result.update(fallback.get(city["country"], {
        "fixed_download_mbps": None, "note": "País no disponible en el índice"
    }))
    print(f"    OK: {result.get('fixed_download_mbps')} Mbps download "
          f"({city['country']}, rank #{result.get('fixed_rank_global', '?')} global)")
    return result


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("NomadOptima — Data Ingestion v5")
    print(f"Ciudades: {[c['display'] for c in CITIES]}")
    print(f"Output:   {OUTPUT_DIR}/")
    print("=" * 60)

    if not GOOGLE_API_KEY:
        print("\n⚠️  GOOGLE_API_KEY no configurada.")
        print("   Crea un archivo .env en la raíz con: GOOGLE_API_KEY=tu_key\n")

    summary  = {city["name"]: {"updated": [], "skipped": []} for city in CITIES}
    all_data = {}

    for city in CITIES:
        print(f"\n{'─' * 40}")
        print(f"  {city['display'].upper()}")
        print(f"{'─' * 40}")

        # Cargar JSON existente para reutilizar fuentes que no necesitan refresh
        existing_path = os.path.join(OUTPUT_DIR, f"{city['name'].lower()}_raw.json")
        existing_data = {}
        if os.path.exists(existing_path):
            try:
                with open(existing_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                pass

        city_data = {"meta": city}

        def fetch_or_skip(source_key, fetch_fn, sleep_s=1):
            if needs_refresh(city["name"], source_key):
                result = fetch_fn(city)
                summary[city["name"]]["updated"].append(source_key)
                if sleep_s:
                    time.sleep(sleep_s)
                return result
            else:
                summary[city["name"]]["skipped"].append(source_key)
                return existing_data.get(source_key, {})

        city_data["numbeo"]        = fetch_or_skip("numbeo",        fetch_numbeo,        sleep_s=2)
        city_data["weather"]       = fetch_or_skip("weather",       fetch_weather,       sleep_s=1)
        city_data["wikipedia"]     = fetch_or_skip("wikipedia",     fetch_wikipedia,     sleep_s=1)
        city_data["country"]       = fetch_or_skip("country",       fetch_country_data,  sleep_s=1)
        city_data["osm"]           = fetch_or_skip("osm",           fetch_osm,           sleep_s=2)
        city_data["google_places"] = fetch_or_skip("google_places", fetch_google_places, sleep_s=1)
        city_data["speedtest"]     = fetch_or_skip("speedtest",     fetch_speedtest,     sleep_s=0)

        all_data[city["name"]] = city_data

        with open(existing_path, "w", encoding="utf-8") as f:
            json.dump(city_data, f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ Guardado: {existing_path}")

    # JSON combinado con todas las ciudades
    combined_path = os.path.join(OUTPUT_DIR, "cities_raw.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # ── Resumen final ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("✓ Completado.")
    print(f"\nArchivos en {OUTPUT_DIR}/:")
    for city in CITIES:
        print(f"  {city['name'].lower()}_raw.json")
    print("  cities_raw.json")

    print("\nResumen de actualizaciones:")
    for city in CITIES:
        s = summary[city["name"]]
        print(f"\n  {city['display']}:")
        if s["updated"]:
            print(f"    ✓ Actualizadas : {', '.join(s['updated'])}")
        if s["skipped"]:
            print(f"    ↷ Saltadas     : {', '.join(s['skipped'])}")

    errors_found = [
        f"  {city_name} / {source}: {data['error']}"
        for city_name, city_data in all_data.items()
        for source, data in city_data.items()
        if isinstance(data, dict) and "error" in data
    ]
    if errors_found:
        print("\n⚠️  Errores detectados:")
        for e in errors_found:
            print(e)
    else:
        print("\n✓ Sin errores en ninguna fuente.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
