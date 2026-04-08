"""
scripts/fetch_gp_raw.py — EDA de Google Places SIN filtros (todos los types)

PROPÓSITO:
    Herramienta de exploración. Descarga lugares cercanos al centro de cada
    ciudad SIN especificar ningún type (la API devuelve los más populares),
    y extrae TODOS los types del campo types[] de cada resultado.
    Así vemos qué types aparecen naturalmente en cada ciudad.

ESTRATEGIA (coste mínimo):
    - 5 llamadas por ciudad (5 centros desplazados ~4 km)
    - 20 resultados por llamada → hasta 100 lugares únicos por ciudad
    - Cada lugar tiene un campo types[] con TODOS sus tipos
    - Contamos cuántos lugares tienen cada type → tabla ciudad × type
    - TOTAL: 5 ciudades × 5 llamadas = 25 llamadas ≈ $0.10 USD

LIMITACIÓN:
    La API devuelve solo los lugares "más relevantes/populares" cerca del centro.
    Un type con count=0 puede existir pero no aparecer en los 100 más populares.
    Un type con count=8 significa que 8 de los 100 lugares más populares lo tienen.
    Esto es señal de presencia, no conteo exhaustivo.

SALIDA:
    data/processed/gp_all_types_raw.json — lugares brutos con todos sus campos
    data/processed/gp_all_types.csv      — DataFrame ciudad × type (conteos)
    data/processed/gp_all_types.html     — Tabla interactiva para EDA

Run:
    python scripts/fetch_gp_raw.py
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from collections import Counter

# ── CARGAR .env ───────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ .env cargado")
except ImportError:
    print("⚠  python-dotenv no instalado.")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# ── CIUDADES ──────────────────────────────────────────────────────────────────
CITIES = [
    {"name": "Malaga",   "display": "Málaga",   "lat": 36.7213, "lon": -4.4214},
    {"name": "Paris",    "display": "París",    "lat": 48.8566, "lon":  2.3522},
    {"name": "Valencia", "display": "Valencia", "lat": 39.4699, "lon": -0.3763},
    {"name": "Porto",    "display": "Porto",    "lat": 41.1579, "lon": -8.6291},
    {"name": "Bordeaux", "display": "Burdeos",  "lat": 44.8378, "lon": -0.5792},
]

# Centros desplazados ~4 km para cubrir más área de la ciudad
# Con 5 × 20 resultados = hasta 100 lugares únicos por ciudad (deduplicados por id)
DELTA = 0.04   # ≈ 4.4 km en latitud / ≈ 3.5 km en longitud a lat 40°N
OFFSETS = [
    (0,       0),       # centro
    (+DELTA,  0),       # norte
    (-DELTA,  0),       # sur
    (0,      +DELTA),   # este
    (0,      -DELTA),   # oeste
]

# Types de Tabla B y C de Google Places (solo aparecen en results[], no filtrables).
# Los listamos aquí para poder identificarlos en la salida pero NO los usamos como filtro.
# Los types de Tabla A son los que se pueden usar en includedTypes — son los que
# aparecen en nuestro conteo final.

NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"
RADIUS_M   = 8_000   # 8 km desde cada punto → cubre bien el área urbana

# Agrupación de types por categoría (para colorear el HTML)
# Fuente: developers.google.com/maps/documentation/places/web-service/place-types
TYPE_CATEGORIES = {
    # Automoción
    "car_dealer": "automotive", "car_rental": "automotive", "car_repair": "automotive",
    "car_wash": "automotive", "electric_vehicle_charging_station": "automotive",
    "gas_station": "automotive", "parking": "automotive",
    # Cultura
    "art_gallery": "culture", "art_studio": "culture", "auditorium": "culture",
    "cultural_center": "culture", "historical_landmark": "culture",
    "library": "culture", "monument": "culture", "movie_theater": "culture",
    "museum": "culture", "performing_arts_theater": "culture", "sculpture": "culture",
    # Educación
    "child_care_agency": "education", "driving_school": "education",
    "language_school": "education", "preschool": "education",
    "primary_school": "education", "school": "education",
    "secondary_school": "education", "university": "education",
    # Entretenimiento
    "amusement_center": "entertainment", "amusement_park": "entertainment",
    "aquarium": "entertainment", "banquet_hall": "entertainment",
    "bowling_alley": "entertainment", "casino": "entertainment",
    "childrens_camp": "entertainment", "comedy_club": "entertainment",
    "community_center": "entertainment", "convention_center": "entertainment",
    "dog_park": "entertainment", "escape_room": "entertainment",
    "garden": "entertainment", "hiking_area": "entertainment",
    "historical_place": "entertainment", "internet_cafe": "entertainment",
    "karaoke": "entertainment", "marina": "entertainment",
    "mini_golf": "entertainment", "national_park": "entertainment",
    "night_club": "entertainment", "observation_deck": "entertainment",
    "park": "entertainment", "skateboard_park": "entertainment",
    "tourist_attraction": "entertainment", "video_arcade": "entertainment",
    "visitor_center": "entertainment", "wedding_venue": "entertainment",
    "wildlife_park": "entertainment", "wildlife_refuge": "entertainment",
    "zoo": "entertainment",
    # Finanzas
    "accounting": "finance", "atm": "finance", "bank": "finance",
    "currency_exchange": "finance", "financial_planner": "finance",
    "insurance_agency": "finance",
    # Comida y bebida
    "acai_shop": "food", "afghani_restaurant": "food", "african_restaurant": "food",
    "american_restaurant": "food", "asian_fusion_restaurant": "food",
    "bagel_shop": "food", "bakery": "food", "bar": "food", "bar_and_grill": "food",
    "barbecue_restaurant": "food", "breakfast_restaurant": "food",
    "brunch_restaurant": "food", "bubble_tea_store": "food",
    "buffet_restaurant": "food", "cafe": "food", "cafeteria": "food",
    "chinese_restaurant": "food", "coffee_shop": "food", "deli": "food",
    "dessert_restaurant": "food", "dessert_shop": "food", "diner": "food",
    "fast_food_restaurant": "food", "fine_dining_restaurant": "food",
    "food_court": "food", "french_restaurant": "food", "greek_restaurant": "food",
    "hamburger_restaurant": "food", "ice_cream_shop": "food",
    "indian_restaurant": "food", "indonesian_restaurant": "food",
    "italian_restaurant": "food", "japanese_restaurant": "food",
    "juice_shop": "food", "korean_restaurant": "food", "lebanese_restaurant": "food",
    "market": "food", "meal_delivery": "food", "meal_takeaway": "food",
    "mediterranean_restaurant": "food", "mexican_restaurant": "food",
    "middle_eastern_restaurant": "food", "pizza_restaurant": "food",
    "pub": "food", "ramen_restaurant": "food", "restaurant": "food",
    "sandwich_shop": "food", "seafood_restaurant": "food",
    "spanish_restaurant": "food", "steak_house": "food",
    "sushi_restaurant": "food", "tapas_bar": "food", "tea_house": "food",
    "thai_restaurant": "food", "turkish_restaurant": "food",
    "vegan_restaurant": "food", "vegetarian_restaurant": "food",
    "vietnamese_restaurant": "food", "wine_bar": "food",
    # Gobierno
    "city_hall": "government", "courthouse": "government", "embassy": "government",
    "fire_station": "government", "local_government_office": "government",
    "police": "government", "post_office": "government",
    # Salud y bienestar
    "chiropractor": "health", "dental_clinic": "health", "dentist": "health",
    "doctor": "health", "drugstore": "health", "gym": "health",
    "hospital": "health", "massage": "health", "medical_lab": "health",
    "mental_health_practitioner": "health", "nutritionist": "health",
    "optician": "health", "pharmacy": "health", "physiotherapist": "health",
    "sauna": "health", "spa": "health", "swimming_pool": "health",
    "wellness_center": "health", "yoga_studio": "health",
    # Alojamiento
    "bed_and_breakfast": "lodging", "campground": "lodging",
    "camping_cabin": "lodging", "cottage": "lodging",
    "extended_stay_hotel": "lodging", "farm_stay": "lodging",
    "hotel": "lodging", "hostel": "lodging", "motel": "lodging",
    "resort_hotel": "lodging", "rv_park": "lodging",
    # Naturaleza
    "beach": "nature", "forest": "nature", "lake": "nature",
    "nature_reserve": "nature", "river": "nature",
    "waterfall": "nature", "wetland": "nature",
    # Lugares de culto
    "church": "worship", "hindu_temple": "worship",
    "mosque": "worship", "synagogue": "worship",
    # Servicios
    "barber_shop": "services", "beauty_salon": "services",
    "dry_cleaning": "services", "electrician": "services",
    "funeral_home": "services", "hair_care": "services",
    "hair_salon": "services", "laundry": "services", "locksmith": "services",
    "nail_salon": "services", "pet_boarding_service": "services",
    "pet_grooming": "services", "pet_store": "services", "plumber": "services",
    "real_estate_agency": "services", "storage": "services", "tailor": "services",
    "telecommunications_service_provider": "services", "travel_agency": "services",
    "veterinary_care": "services",
    # Compras
    "bicycle_store": "shopping", "book_store": "shopping",
    "camera_store": "shopping", "clothing_store": "shopping",
    "convenience_store": "shopping", "department_store": "shopping",
    "discount_store": "shopping", "electronics_store": "shopping",
    "florist": "shopping", "furniture_store": "shopping",
    "gift_shop": "shopping", "grocery_store": "shopping",
    "hardware_store": "shopping", "home_goods_store": "shopping",
    "jewelry_store": "shopping", "liquor_store": "shopping",
    "mobile_phone_store": "shopping", "outdoor_furniture_store": "shopping",
    "shoe_store": "shopping", "shopping_mall": "shopping",
    "sporting_goods_store": "shopping", "supermarket": "shopping",
    "toy_store": "shopping", "wholesaler": "shopping",
    # Deporte
    "adventure_sports_center": "sport", "athletic_field": "sport",
    "climbing_gym": "sport", "cycling_park": "sport",
    "fitness_center": "sport", "golf_course": "sport",
    "golf_driving_range": "sport", "ice_skating_rink": "sport",
    "kayak_rental": "sport", "playground": "sport", "ski_resort": "sport",
    "sports_activity_location": "sport", "sports_club": "sport",
    "sports_coaching": "sport", "sports_complex": "sport",
    "stadium": "sport", "tennis_court": "sport", "water_park": "sport",
    # Transporte
    "airport": "transport", "bicycle_rental": "transport",
    "bus_station": "transport", "bus_stop": "transport",
    "ferry_terminal": "transport", "heliport": "transport",
    "light_rail_station": "transport", "subway_station": "transport",
    "taxi_stand": "transport", "train_station": "transport",
    "transit_depot": "transport", "transit_station": "transport",
    # Turismo
    "information_center": "tourism", "scenic_point": "tourism",
    "tourist_attraction": "tourism", "tour_operator": "tourism",
    # Types de Tabla B (aparecen en results pero no filtrables)
    "point_of_interest": "meta", "establishment": "meta",
    "premise": "meta", "political": "meta", "locality": "meta",
    "route": "meta", "street_address": "meta",
}


# ── FUNCIÓN DE DESCARGA ───────────────────────────────────────────────────────

def fetch_city_places(city: dict) -> list[dict]:
    """
    Descarga hasta 100 lugares populares de una ciudad haciendo 5 búsquedas
    generales (sin filtro de type) desde 5 puntos desplazados ~4 km.

    La API devuelve los lugares más relevantes/populares en cada punto.
    Cada lugar incluye un campo types[] con todos sus types oficiales.

    Args:
        city: diccionario con name, display, lat, lon

    Returns:
        Lista de dicts con los datos de cada lugar (deduplicados por id)
    """
    seen_ids = set()
    places   = []

    for i, (dlat, dlon) in enumerate(OFFSETS):
        payload = {
            # Sin includedTypes → la API devuelve todo tipo de lugares populares
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude":  city["lat"] + dlat,
                        "longitude": city["lon"] + dlon,
                    },
                    "radius": float(RADIUS_M),
                }
            },
            "maxResultCount": 20,
        }
        headers = {
            "Content-Type":     "application/json",
            "X-Goog-Api-Key":   GOOGLE_API_KEY,
            # Pedimos: id (para deduplicar), nombre, tipos, valoración y dirección
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.types,"
                "places.rating,places.userRatingCount,"
                "places.formattedAddress,places.location"
            ),
        }
        try:
            r = requests.post(NEARBY_URL, json=payload, headers=headers, timeout=20)
            r.raise_for_status()
            batch = r.json().get("places", [])
            new_this_call = 0
            for p in batch:
                pid = p.get("id", "")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    places.append(p)
                    new_this_call += 1
            print(f"    Offset {i+1}/5: {len(batch)} resultados, {new_this_call} nuevos "
                  f"(total únicos: {len(places)})")
        except requests.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            print(f"    ⚠ Offset {i+1}/5 ERROR HTTP {status}")
        except Exception as e:
            print(f"    ⚠ Offset {i+1}/5 ERROR: {e}")

        time.sleep(0.5)

    return places


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY no encontrada en .env — abortando.")
        return

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 65}")
    print("NomadOptima — Google Places EDA (búsqueda general, coste mínimo)")
    print(f"Ciudades: {len(CITIES)} | Llamadas por ciudad: {len(OFFSETS)}")
    print(f"Total llamadas: {len(CITIES) * len(OFFSETS)} ≈ $0.10 USD")
    print("Estrategia: sin filtro de type → extraemos types[] de cada resultado")
    print(f"{'=' * 65}\n")

    # Recoger todos los lugares por ciudad, con todos sus types
    all_city_data = {}   # {city_name: [place_dict, ...]}

    for city in CITIES:
        print(f"\n{'─' * 50}")
        print(f"  {city['display'].upper()}")
        print(f"{'─' * 50}")
        places = fetch_city_places(city)
        all_city_data[city["name"]] = places
        print(f"  → {len(places)} lugares únicos descargados")

    # ── GUARDAR JSON RAW ──────────────────────────────────────────────────────
    raw_path = out_dir / "gp_all_types_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_city_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ JSON raw guardado: {raw_path}")

    # ── CONSTRUIR TABLA DE FRECUENCIAS type × ciudad ──────────────────────────
    # Para cada ciudad: contamos cuántos lugares tienen cada type en su lista types[]
    # Esto nos dice "de los 100 lugares más populares, ¿cuántos son de este tipo?"

    # Recoger todos los types vistos en cualquier ciudad
    all_types_seen = set()
    city_type_counts = {}   # {city_name: Counter(type → count)}
    city_type_places = {}   # {city_name: {type → [lugar1, lugar2, ...]}} para top-3

    for city in CITIES:
        places = all_city_data[city["name"]]
        counter = Counter()
        type_places_map = {}

        for place in places:
            for t in place.get("types", []):
                counter[t] += 1
                all_types_seen.add(t)
                if t not in type_places_map:
                    type_places_map[t] = []
                if len(type_places_map[t]) < 3:
                    type_places_map[t].append({
                        "name":    place.get("displayName", {}).get("text", ""),
                        "rating":  place.get("rating"),
                        "reviews": place.get("userRatingCount"),
                        "address": place.get("formattedAddress", ""),
                        "types":   place.get("types", []),
                    })

        city_type_counts[city["name"]] = counter
        city_type_places[city["name"]] = type_places_map

    # Construir DataFrame: filas = types, columnas = ciudades
    rows = []
    for t in sorted(all_types_seen):
        cat = TYPE_CATEGORIES.get(t, "other")
        row = {"type": t, "categoria": cat}
        total = 0
        for city in CITIES:
            count = city_type_counts[city["name"]].get(t, 0)
            row[city["name"]] = count
            total += count
        row["total"] = total
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values(["categoria", "total"], ascending=[True, False]).reset_index(drop=True)

    # Guardar CSV
    csv_path = out_dir / "gp_all_types.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"✓ CSV guardado: {csv_path} ({len(df)} types distintos encontrados)")

    # ── EXPORTAR HTML ──────────────────────────────────────────────────────────
    html_path = out_dir / "gp_all_types.html"
    _export_html(df, city_type_places, html_path)
    print(f"✓ HTML guardado: {html_path}")
    print(f"\n  → {len(df)} types distintos encontrados en {sum(len(p) for p in all_city_data.values())} lugares totales")
    print("  → Abre el HTML en tu navegador para hacer EDA")
    print("  → Los números indican en cuántos de los ~100 lugares más populares")
    print("     aparece ese type en su campo types[]\n")


def _export_html(df: pd.DataFrame, city_type_places: dict, output_path: Path) -> None:
    """
    Genera archivo HTML interactivo para explorar los types de Google Places.

    Tabla: filas = types, columnas = ciudades
    Color: escala de verde según presencia (0=gris, máx=verde)
    Click en celda: muestra los lugares con ese type en esa ciudad
    Filtros: por categoría y búsqueda de texto
    """
    ciudad_display = {c["name"]: c["display"] for c in CITIES}
    cities_list    = [c["name"] for c in CITIES]

    # JSON para el JS del HTML
    top3_json = {}
    for city_name, type_map in city_type_places.items():
        top3_json[city_name] = {}
        for t, places in type_map.items():
            top3_json[city_name][t] = places

    def count_color(n, max_n=15):
        """Verde más intenso cuanto mayor es el conteo."""
        if n == 0:
            return "#f0f0f0"
        ratio = min(n / max_n, 1.0)
        r = int(255 - ratio * (255 - 25))
        g = int(255 - ratio * (255 - 135))
        b = int(255 - ratio * (255 - 84))
        return f"rgb({r},{g},{b})"

    # Construir filas de la tabla
    rows_html = []
    for _, row in df.iterrows():
        t   = row["type"]
        cat = row["categoria"]
        cells = f"""
            <td class="type-col"><code>{t}</code></td>
            <td><span class="cat-badge cat-{cat}">{cat}</span></td>"""
        for city_name in cities_list:
            count = row[city_name]
            color = count_color(int(count))
            cells += f"""
            <td class="count-cell"
                style="background:{color}; cursor:pointer;"
                onclick="showPlaces('{city_name}','{t}')"
                title="{ciudad_display[city_name]} — {t}: {int(count)}">{int(count)}</td>"""
        cells += f'<td class="total-col">{int(row["total"])}</td>'
        rows_html.append(f'<tr data-cat="{cat}">{cells}</tr>')

    rows_str = "\n".join(rows_html)

    # Botones de categoría
    cats = sorted(df["categoria"].unique())
    cat_btns = '<button class="cat-btn active" onclick="filterCat(\'all\')">Todas</button>\n'
    for c in cats:
        n = len(df[df["categoria"] == c])
        cat_btns += f'<button class="cat-btn" onclick="filterCat(\'{c}\')">{c} ({n})</button>\n'

    city_headers = "".join(
        f'<th style="text-align:center">{ciudad_display[c]}</th>' for c in cities_list
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>NomadOptima — Google Places EDA</title>
<style>
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  body {{ font-family:'Segoe UI',sans-serif; background:#f0f2f5; color:#333; font-size:13px; }}

  header {{
    background:linear-gradient(135deg,#1a1a2e,#16213e);
    color:white; padding:1.2rem 2rem;
  }}
  header h1 {{ font-size:1.25rem; margin-bottom:.3rem; }}
  header p  {{ font-size:.8rem; opacity:.7; }}

  .info-bar {{
    background:white; padding:.7rem 2rem;
    border-bottom:1px solid #e0e0e0;
    font-size:.8rem; color:#555;
    display:flex; gap:2rem; flex-wrap:wrap;
  }}
  .info-bar strong {{ color:#1a1a2e; }}

  .controls {{
    background:white; padding:.8rem 2rem;
    border-bottom:1px solid #e0e0e0;
    display:flex; gap:.4rem; flex-wrap:wrap; align-items:center;
  }}
  .controls label {{ font-size:.82rem; font-weight:600; margin-right:.3rem; }}
  .cat-btn {{
    padding:.25rem .65rem; border:1px solid #ccc;
    background:#f8f9fa; border-radius:20px;
    cursor:pointer; font-size:.75rem; transition:all .15s;
  }}
  .cat-btn.active, .cat-btn:hover {{ background:#1a1a2e; color:white; border-color:#1a1a2e; }}
  .search-input {{
    padding:.3rem .75rem; border:1px solid #ccc;
    border-radius:20px; font-size:.8rem; width:200px; margin-left:auto;
  }}

  .table-wrap {{ overflow-x:auto; padding:1rem 2rem; }}
  table {{
    border-collapse:collapse; width:100%; background:white;
    border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.08);
  }}
  th {{
    background:#1a1a2e; color:white;
    padding:.6rem .5rem; text-align:left;
    position:sticky; top:0; z-index:10; white-space:nowrap;
  }}
  td {{ padding:.35rem .5rem; border-bottom:1px solid #f0f0f0; }}
  tr:hover td {{ background:#f5f7ff !important; }}
  tr.hidden {{ display:none; }}

  .type-col  {{ white-space:nowrap; }}
  .type-col code {{ color:#1a1a2e; font-size:.78rem; }}
  .count-cell {{ text-align:center; font-weight:700; min-width:60px; }}
  .total-col  {{ text-align:center; font-weight:700; color:#1a1a2e; background:#f8f9fa!important; }}

  /* Badges categoría */
  .cat-badge {{
    font-size:.7rem; padding:.15rem .45rem;
    border-radius:12px; font-weight:600; white-space:nowrap;
  }}
  .cat-automotive    {{ background:#fff3cd; color:#856404; }}
  .cat-culture       {{ background:#e8d5ff; color:#5a2d82; }}
  .cat-education     {{ background:#cfe2ff; color:#084298; }}
  .cat-entertainment {{ background:#d1ecf1; color:#0c5460; }}
  .cat-finance       {{ background:#d4edda; color:#155724; }}
  .cat-food          {{ background:#ffe5d0; color:#7d3c00; }}
  .cat-government    {{ background:#f8d7da; color:#721c24; }}
  .cat-health        {{ background:#d4f5e9; color:#155724; }}
  .cat-lodging       {{ background:#fde8c8; color:#7d4b00; }}
  .cat-nature        {{ background:#c3e6cb; color:#155724; }}
  .cat-services      {{ background:#e2e3e5; color:#383d41; }}
  .cat-shopping      {{ background:#ffddd2; color:#7d2a00; }}
  .cat-sport         {{ background:#d0f0fd; color:#004085; }}
  .cat-tourism       {{ background:#fff9c4; color:#6d5a00; }}
  .cat-transport     {{ background:#e2e3e5; color:#383d41; }}
  .cat-worship       {{ background:#f0e6ff; color:#5a2d82; }}
  .cat-meta          {{ background:#ececec; color:#666; }}
  .cat-other         {{ background:#f5f5f5; color:#888; }}

  /* Panel lateral */
  #side-panel {{
    display:none; position:fixed; top:20px; right:20px;
    width:360px; background:white; border-radius:12px;
    box-shadow:0 8px 24px rgba(0,0,0,.15); z-index:1000; overflow:hidden;
  }}
  #side-header {{
    background:#1a1a2e; color:white; padding:.8rem 1rem;
    display:flex; justify-content:space-between; align-items:center;
  }}
  #side-header h3 {{ font-size:.88rem; }}
  #side-close {{ background:none; border:none; color:white; font-size:1.1rem; cursor:pointer; }}
  #side-body  {{ padding:1rem; max-height:70vh; overflow-y:auto; }}
  .place-item {{ padding:.5rem 0; border-bottom:1px solid #f0f0f0; }}
  .place-item:last-child {{ border-bottom:none; }}
  .place-name {{ font-weight:600; font-size:.85rem; color:#1a1a2e; }}
  .place-meta {{ font-size:.75rem; color:#666; margin-top:.2rem; }}
  .place-addr {{ font-size:.72rem; color:#999; }}
  .place-types {{ font-size:.68rem; color:#bbb; margin-top:.2rem; font-style:italic; }}
</style>
</head>
<body>

<header>
  <h1>NomadOptima — Google Places EDA (todos los types)</h1>
  <p>Generado {datetime.now().strftime('%d/%m/%Y %H:%M')} ·
     Estrategia: búsqueda general sin filtro de type ·
     {len(df)} types distintos encontrados</p>
</header>

<div class="info-bar">
  <span><strong>Lectura:</strong> cada número = cuántos de los ~100 lugares más populares de esa ciudad tienen ese type en su campo types[]</span>
  <span><strong>0</strong> = no aparece en el top-100 (puede existir pero ser menos popular)</span>
  <span><strong>Click en un número</strong> para ver ejemplos de lugares con ese type</span>
</div>

<div class="controls">
  <label>Categoría:</label>
  {cat_btns}
  <input type="text" class="search-input" placeholder="Buscar type..." oninput="filterSearch(this.value)">
</div>

<div class="table-wrap">
<table id="main-table">
  <thead>
    <tr>
      <th>Type oficial</th>
      <th>Categoría</th>
      {city_headers}
      <th>Total</th>
    </tr>
  </thead>
  <tbody>
    {rows_str}
  </tbody>
</table>
</div>

<div id="side-panel">
  <div id="side-header">
    <h3 id="side-title">Lugares</h3>
    <button id="side-close" onclick="document.getElementById('side-panel').style.display='none'">✕</button>
  </div>
  <div id="side-body"></div>
</div>

<script>
const TOP3 = {json.dumps(top3_json, ensure_ascii=False)};
const CITY_DISPLAY = {json.dumps(ciudad_display, ensure_ascii=False)};
let activeCat = 'all';

function filterCat(cat) {{
  activeCat = cat;
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  applyFilters();
}}
function filterSearch(val) {{ applyFilters(val); }}
function applyFilters(searchVal) {{
  const q = (searchVal !== undefined
    ? searchVal
    : document.querySelector('.search-input').value).toLowerCase();
  document.querySelectorAll('#main-table tbody tr').forEach(row => {{
    const catOk    = activeCat === 'all' || row.dataset.cat === activeCat;
    const searchOk = q === '' || row.textContent.toLowerCase().includes(q);
    row.classList.toggle('hidden', !(catOk && searchOk));
  }});
}}
function showPlaces(cityName, typeKey) {{
  const places = (TOP3[cityName] || {{}})[typeKey] || [];
  const cityLabel = CITY_DISPLAY[cityName] || cityName;
  document.getElementById('side-title').textContent = cityLabel + ' — ' + typeKey;
  const body = document.getElementById('side-body');
  if (!places.length) {{
    body.innerHTML = '<p style="color:#999;font-size:.85rem;">Sin ejemplos para este type.</p>';
  }} else {{
    body.innerHTML = places.map((p,i) => `
      <div class="place-item">
        <div class="place-name">${{i+1}}. ${{p.name || 'Sin nombre'}}</div>
        <div class="place-meta">${{p.rating ? '⭐ '+p.rating+' ('+p.reviews+' reseñas)' : 'Sin valoración'}}</div>
        <div class="place-addr">${{p.address || ''}}</div>
        <div class="place-types">${{(p.types||[]).join(' · ')}}</div>
      </div>`).join('');
  }}
  document.getElementById('side-panel').style.display = 'block';
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
