"""
scripts/fetch_wikidata.py
Obtiene población y área (km²) de cada ciudad via Wikidata SPARQL API.
Gratis, sin límites agresivos, datos estructurados.

Run: python scripts/fetch_wikidata.py
"""
import json
import os
import time
import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": "NomadOptima/1.0 (student project)",
    "Accept": "application/json",
}

CITY_WIKIDATA = {
    "alicante":          "Alicante",
    "amsterdam":         "Amsterdam",
    "andorra":           "Andorra la Vella",
    "atenas":            "Athens",
    "bali":              "Bali",
    "bangkok":           "Bangkok",
    "barcelona":         "Barcelona",
    "belgrade":          "Belgrade",
    "berlin":            "Berlin",
    "bogota":            "Bogotá",
    "bordeaux":          "Bordeaux",
    "bucharest":         "Bucharest",
    "budapest":          "Budapest",
    "buenos_aires":      "Buenos Aires",
    "cartagena":         "Cartagena",
    "chamonix":          "Chamonix-Mont-Blanc",
    "chiang_mai":        "Chiang Mai",
    "dubai":             "Dubai",
    "dublin":            "Dublin",
    "essaouira":         "Essaouira",
    "faro":              "Faro",
    "fuerteventura":     "Fuerteventura",
    "granada":           "Granada",
    "innsbruck":         "Innsbruck",
    "krakow":            "Kraków",
    "kuala_lumpur":      "Kuala Lumpur",
    "las_palmas":        "Las Palmas de Gran Canaria",
    "lima":              "Lima",
    "lisboa":            "Lisbon",
    "london":            "London",
    "malaga":            "Málaga",
    "marrakech":         "Marrakesh",
    "medellin":          "Medellín",
    "mexico_city":       "Mexico City",
    "milan":             "Milan",
    "montevideo":        "Montevideo",
    "munich":            "Munich",
    "napoles":           "Naples",
    "paris":             "Paris",
    "playa_del_carmen":  "Playa del Carmen",
    "porto":             "Porto",
    "prague":            "Prague",
    "roma":              "Rome",
    "santiago":          "Santiago",
    "sevilla":           "Seville",
    "sofia":             "Sofia",
    "stockholm":         "Stockholm",
    "tallinn":           "Tallinn",
    "tarifa":            "Tarifa",
    "tbilisi":           "Tbilisi",
    "valencia":          "Valencia",
    "vienna":            "Vienna",
    "warsaw":            "Warsaw",
}

def query_wikidata(city_name):
    """Consulta Wikidata buscando el item con ese label que tenga población."""
    query = f"""SELECT ?item ?population ?area WHERE {{
  ?item rdfs:label \"{city_name}\"@en.
  ?item wdt:P1082 ?population.
  OPTIONAL {{ ?item wdt:P2046 ?area. }}
}}
ORDER BY DESC(?population)
LIMIT 1"""
    try:
        r = requests.get(
            SPARQL_URL,
            params={"query": query, "format": "json"},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        bindings = r.json().get("results", {}).get("bindings", [])
        if bindings:
            row = bindings[0]
            population = int(float(row["population"]["value"]))
            area_km2 = round(float(row["area"]["value"]), 2) if "area" in row else None
            return {"population": population, "area_km2": area_km2}
    except Exception as e:
        print(f"ERROR: {e}")
    return None


def main():
    raw_dir = "data/raw"
    ok, sin_datos = [], []

    print(f"Consultando {len(CITY_WIKIDATA)} ciudades en Wikidata...\n")

    for slug, wiki_name in CITY_WIKIDATA.items():
        fname = os.path.join(raw_dir, f"{slug}_raw.json")
        if not os.path.exists(fname):
            print(f"  SKIP {slug} — archivo no existe")
            continue

        print(f"  {slug} ({wiki_name})... ", end="", flush=True)
        result = query_wikidata(wiki_name)
        time.sleep(1.0)

        with open(fname, encoding="utf-8") as f:
            data = json.load(f)

        if result:
            data["wikidata"] = {
                "population": result["population"],
                "area_km2":   result["area_km2"],
                "source":     "wikidata_sparql",
                "wiki_name":  wiki_name,
            }
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"pop={result['population']:,} | area={result['area_km2']} km²")
            ok.append(slug)
        else:
            print("sin datos")
            sin_datos.append(slug)

    print(f"\nResultado: {len(ok)} OK | {len(sin_datos)} sin datos")
    if sin_datos:
        print(f"Sin datos: {sin_datos}")

if __name__ == "__main__":
    main()
