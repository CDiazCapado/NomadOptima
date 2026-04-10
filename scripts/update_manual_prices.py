"""
scripts/update_manual_prices.py
Añade key_prices manuales (investigadas de Expatistan/fuentes 2026)
a las ciudades que tienen Numbeo bloqueado hasta mayo 2026.
"""
import json
import os

MANUAL_PRICES = {
    # EUROPA DEL ESTE
    "belgrade":     {"rent_1br_center": 550,  "rent_1br_outside": 380,  "meal_cheap": 8,  "meal_midrange": 25, "coffee": 1.5, "beer": 1.5, "transport_monthly": 35, "gym_monthly": 35, "internet_monthly": 25, "basic_utilities": 90},
    "bucharest":    {"rent_1br_center": 600,  "rent_1br_outside": 420,  "meal_cheap": 7,  "meal_midrange": 22, "coffee": 2.0, "beer": 1.8, "transport_monthly": 30, "gym_monthly": 30, "internet_monthly": 20, "basic_utilities": 100},
    "sofia":        {"rent_1br_center": 650,  "rent_1br_outside": 450,  "meal_cheap": 7,  "meal_midrange": 22, "coffee": 2.0, "beer": 2.0, "transport_monthly": 30, "gym_monthly": 30, "internet_monthly": 20, "basic_utilities": 95},
    "tallinn":      {"rent_1br_center": 900,  "rent_1br_outside": 650,  "meal_cheap": 12, "meal_midrange": 35, "coffee": 2.5, "beer": 3.0, "transport_monthly": 50, "gym_monthly": 45, "internet_monthly": 30, "basic_utilities": 130},
    "tbilisi":      {"rent_1br_center": 500,  "rent_1br_outside": 350,  "meal_cheap": 5,  "meal_midrange": 18, "coffee": 1.5, "beer": 1.5, "transport_monthly": 25, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 80},
    "krakow":       {"rent_1br_center": 650,  "rent_1br_outside": 450,  "meal_cheap": 7,  "meal_midrange": 22, "coffee": 2.0, "beer": 2.0, "transport_monthly": 35, "gym_monthly": 30, "internet_monthly": 20, "basic_utilities": 110},
    # LATINOAMERICA
    "medellin":     {"rent_1br_center": 550,  "rent_1br_outside": 380,  "meal_cheap": 4,  "meal_midrange": 15, "coffee": 1.5, "beer": 1.5, "transport_monthly": 25, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 60},
    "mexico_city":  {"rent_1br_center": 900,  "rent_1br_outside": 600,  "meal_cheap": 5,  "meal_midrange": 20, "coffee": 2.0, "beer": 2.0, "transport_monthly": 25, "gym_monthly": 30, "internet_monthly": 25, "basic_utilities": 70},
    "bogota":       {"rent_1br_center": 600,  "rent_1br_outside": 420,  "meal_cheap": 4,  "meal_midrange": 15, "coffee": 1.5, "beer": 1.5, "transport_monthly": 25, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 65},
    "buenos_aires": {"rent_1br_center": 550,  "rent_1br_outside": 380,  "meal_cheap": 5,  "meal_midrange": 18, "coffee": 1.5, "beer": 1.5, "transport_monthly": 20, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 80},
    "lima":         {"rent_1br_center": 500,  "rent_1br_outside": 350,  "meal_cheap": 3,  "meal_midrange": 15, "coffee": 1.5, "beer": 1.5, "transport_monthly": 20, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 65},
    "santiago":     {"rent_1br_center": 800,  "rent_1br_outside": 550,  "meal_cheap": 7,  "meal_midrange": 22, "coffee": 2.0, "beer": 2.0, "transport_monthly": 40, "gym_monthly": 35, "internet_monthly": 25, "basic_utilities": 90},
    "montevideo":   {"rent_1br_center": 850,  "rent_1br_outside": 600,  "meal_cheap": 8,  "meal_midrange": 25, "coffee": 2.5, "beer": 2.5, "transport_monthly": 40, "gym_monthly": 35, "internet_monthly": 25, "basic_utilities": 100},
    "cartagena":    {"rent_1br_center": 500,  "rent_1br_outside": 350,  "meal_cheap": 4,  "meal_midrange": 15, "coffee": 1.5, "beer": 1.5, "transport_monthly": 20, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 60},
    # ASIA
    "bangkok":      {"rent_1br_center": 650,  "rent_1br_outside": 450,  "meal_cheap": 3,  "meal_midrange": 15, "coffee": 2.0, "beer": 2.0, "transport_monthly": 30, "gym_monthly": 30, "internet_monthly": 20, "basic_utilities": 70},
    "bali":         {"rent_1br_center": 700,  "rent_1br_outside": 500,  "meal_cheap": 3,  "meal_midrange": 15, "coffee": 2.5, "beer": 2.5, "transport_monthly": 30, "gym_monthly": 30, "internet_monthly": 25, "basic_utilities": 80},
    "chiang_mai":   {"rent_1br_center": 400,  "rent_1br_outside": 280,  "meal_cheap": 2,  "meal_midrange": 10, "coffee": 1.5, "beer": 1.5, "transport_monthly": 25, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 60},
    "kuala_lumpur": {"rent_1br_center": 600,  "rent_1br_outside": 420,  "meal_cheap": 3,  "meal_midrange": 15, "coffee": 2.0, "beer": 3.0, "transport_monthly": 35, "gym_monthly": 30, "internet_monthly": 25, "basic_utilities": 80},
    # ORIENTE MEDIO / AFRICA
    "dubai":        {"rent_1br_center": 1800, "rent_1br_outside": 1200, "meal_cheap": 8,  "meal_midrange": 40, "coffee": 4.0, "beer": 0.0, "transport_monthly": 80, "gym_monthly": 70, "internet_monthly": 50, "basic_utilities": 200},
    "marrakech":    {"rent_1br_center": 400,  "rent_1br_outside": 280,  "meal_cheap": 4,  "meal_midrange": 18, "coffee": 1.5, "beer": 3.0, "transport_monthly": 20, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 55},
    # ESPANA / CANARIAS
    "las_palmas":   {"rent_1br_center": 850,  "rent_1br_outside": 650,  "meal_cheap": 10, "meal_midrange": 30, "coffee": 1.8, "beer": 2.0, "transport_monthly": 30, "gym_monthly": 35, "internet_monthly": 30, "basic_utilities": 100},
    "andorra":      {"rent_1br_center": 1300, "rent_1br_outside": 1000, "meal_cheap": 15, "meal_midrange": 45, "coffee": 2.8, "beer": 3.5, "transport_monthly": 0,  "gym_monthly": 45, "internet_monthly": 35, "basic_utilities": 120},
    "sevilla":      {"rent_1br_center": 850,  "rent_1br_outside": 650,  "meal_cheap": 10, "meal_midrange": 30, "coffee": 1.8, "beer": 2.0, "transport_monthly": 35, "gym_monthly": 35, "internet_monthly": 30, "basic_utilities": 110},
    # GRUPO 3 (aprobados antes pero no guardados en JSON)
    "chamonix":     {"rent_1br_center": 1800, "rent_1br_outside": 1200, "meal_cheap": 20, "meal_midrange": 70, "coffee": 3.5, "beer": 5.0, "transport_monthly": 80, "gym_monthly": 50, "internet_monthly": 35, "basic_utilities": 150},
    "essaouira":    {"rent_1br_center": 400,  "rent_1br_outside": 280,  "meal_cheap": 5,  "meal_midrange": 25, "coffee": 1.5, "beer": 3.0, "transport_monthly": 20, "gym_monthly": 25, "internet_monthly": 20, "basic_utilities": 60},
    "fuerteventura":{"rent_1br_center": 750,  "rent_1br_outside": 550,  "meal_cheap": 10, "meal_midrange": 30, "coffee": 1.8, "beer": 2.0, "transport_monthly": 40, "gym_monthly": 30, "internet_monthly": 30, "basic_utilities": 90},
    "playa_del_carmen": {"rent_1br_center": 900, "rent_1br_outside": 600, "meal_cheap": 6, "meal_midrange": 25, "coffee": 2.5, "beer": 2.0, "transport_monthly": 25, "gym_monthly": 30, "internet_monthly": 25, "basic_utilities": 80},
    "tarifa":       {"rent_1br_center": 900,  "rent_1br_outside": 700,  "meal_cheap": 12, "meal_midrange": 35, "coffee": 2.0, "beer": 2.5, "transport_monthly": 30, "gym_monthly": 35, "internet_monthly": 30, "basic_utilities": 100},
}

updated = []
errors = []

for city, prices in MANUAL_PRICES.items():
    fname = f"data/raw/{city}_raw.json"
    if not os.path.exists(fname):
        errors.append(f"NO EXISTE: {city}")
        continue
    with open(fname, encoding="utf-8") as f:
        data = json.load(f)
    data["numbeo"]["key_prices"] = prices
    data["numbeo"]["key_prices_source"] = "manual_research_2026"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    updated.append(city)

print(f"Actualizadas: {len(updated)} ciudades")
for c in updated:
    print(f"  OK {c}")
if errors:
    print()
    for e in errors:
        print(f"  ERROR: {e}")
