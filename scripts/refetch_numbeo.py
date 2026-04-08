"""
NomadOptima — Re-fetch Numbeo para ciudades con key_prices vacío
scripts/refetch_numbeo.py

Detecta automáticamente qué ciudades tienen key_prices={} en sus JSONs
y re-fetcha solo la parte de Numbeo (coste de vida + quality of life).
Actualiza los JSONs existentes sin tocar el resto de datos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'ingestion'))

import json
import requests
import time
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

NUMBEO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

KEY_MAP = {
    "rent_1br_center":   "Bedroom Apartment in City Centre",
    "rent_1br_outside":  "Bedroom Apartment Outside",
    "meal_cheap":        "Inexpensive Restaurant",
    "meal_midrange":     "Mid-range Restaurant",
    "coffee":            "Cappuccino",
    "beer":              "Domestic Beer",
    "transport_monthly": "Transport Pass",
    "gym_monthly":       "Fitness Club",
    "internet_monthly":  "Internet",
    "basic_utilities":   "Electricity, Heating",
}

# Mapeo ciudad → slug Numbeo (solo las que tienen slug)
NUMBEO_SLUGS = {
    "Sevilla":      "Seville",
    "Bucharest":    "Bucharest",
    "Sofia":        "Sofia",
    "Belgrade":     "Belgrade",
    "Krakow":       "Krakow",
    "Tbilisi":      "Tbilisi",
    "Tallinn":      "Tallinn",
    "Las_Palmas":   "Las-Palmas-de-Gran-Canaria",
    "Medellin":     "Medellin",
    "Mexico_City":  "Mexico-City",
    "Cartagena":    "Cartagena",
    "Andorra":      "Andorra-la-Vella",
    "Granada":      "Granada",
    "Faro":         "Faro",
}


def fetch_numbeo_for_city(slug: str) -> dict:
    """Fetcha precios y calidad de vida de Numbeo para un slug dado."""
    result = {"prices": {}, "key_prices": {}, "quality_indices": {}}

    try:
        # 1. Precios
        url = f"https://www.numbeo.com/cost-of-living/in/{slug}"
        print(f"    GET {url}")
        r = requests.get(url, headers=NUMBEO_HEADERS, timeout=25)
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

        # Extraer key_prices con matching parcial
        for key, keyword in KEY_MAP.items():
            for price_key in result["prices"]:
                if keyword.lower() in price_key.lower():
                    result["key_prices"][key] = result["prices"][price_key]
                    break

        time.sleep(3)

        # 2. Quality of life
        url2 = f"https://www.numbeo.com/quality-of-life/in/{slug}"
        print(f"    GET {url2}")
        r2 = requests.get(url2, headers=NUMBEO_HEADERS, timeout=25)
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

        time.sleep(3)

        print(f"    OK: {len(result['key_prices'])} key_prices, "
              f"{len(result['quality_indices'])} quality indices")

    except requests.HTTPError as e:
        print(f"    ERROR HTTP: {e}")
        result["error"] = f"HTTP {e}"
    except Exception as e:
        print(f"    ERROR: {e}")
        result["error"] = str(e)

    return result


def needs_refetch(json_path: Path) -> bool:
    """Devuelve True si el JSON tiene key_prices vacío."""
    try:
        with open(json_path, encoding="utf-8") as f:
            d = json.load(f)
        kp = d.get("numbeo", {}).get("key_prices", {})
        return len(kp) == 0
    except Exception:
        return False


def main():
    print("=== Re-fetch Numbeo para ciudades con datos faltantes ===\n")

    # Detectar ciudades que necesitan re-fetch
    to_refetch = []
    for city_name, slug in NUMBEO_SLUGS.items():
        fname = city_name.lower().replace(" ", "_") + "_raw.json"
        json_path = RAW_DIR / fname
        if json_path.exists() and needs_refetch(json_path):
            to_refetch.append((city_name, slug, json_path))
        elif not json_path.exists():
            print(f"  Sin JSON: {city_name} (se omite)")

    print(f"Ciudades que necesitan re-fetch: {len(to_refetch)}")
    for city_name, slug, _ in to_refetch:
        print(f"  - {city_name} (slug: {slug})")

    if not to_refetch:
        print("\nTodas las ciudades con slug ya tienen datos. Nada que hacer.")
        return

    print()
    ok = 0
    failed = []

    for city_name, slug, json_path in to_refetch:
        print(f"\n[{city_name}] — slug: {slug}")
        numbeo_data = fetch_numbeo_for_city(slug)

        # Actualizar el JSON existente
        with open(json_path, encoding="utf-8") as f:
            city_json = json.load(f)

        city_json["numbeo"]["key_prices"]      = numbeo_data["key_prices"]
        city_json["numbeo"]["quality_indices"] = numbeo_data["quality_indices"]
        city_json["numbeo"]["prices"]          = numbeo_data["prices"]
        city_json["numbeo"]["fetched_at"]      = datetime.now().isoformat()
        if "error" in numbeo_data:
            city_json["numbeo"]["error"] = numbeo_data["error"]
        elif "error" in city_json["numbeo"]:
            del city_json["numbeo"]["error"]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(city_json, f, ensure_ascii=False, indent=2)

        if numbeo_data["key_prices"]:
            ok += 1
            print(f"  Guardado: {json_path.name}")
        else:
            failed.append(city_name)
            print(f"  FALLIDO: {city_name} — sin key_prices")

    print(f"\n=== Resultado: {ok}/{len(to_refetch)} ciudades actualizadas ===")
    if failed:
        print(f"Fallidas (necesitan hardcode manual): {failed}")


if __name__ == "__main__":
    main()
