"""
NomadOptima - Data Ingestion v10
Fuentes: Numbeo + wttr.in + Wikipedia + RestCountries + OpenStreetMap + Google Places + Speedtest

Fixes v10 (07/04/2026):
  - GOOGLE_PLACE_TYPES: ampliado de 46 a ~115 types organizados por categorías NomadOptima
  - Campos "dimension" reemplazados por "cat" + "subcat" (categorización propia, no la de Google)
  - Nuevas categorías: vida_nocturna, naturaleza, bienestar, mascotas, nomada, alojamiento,
    movilidad, compras, servicios, salud, turismo, educacion, comunidad, finanzas
  - Nuevos types: tourist_attraction, hostel, wine_bar, tapas_bar, climbing_gym, tennis_court,
    kayak_rental, sauna, massage, hospital, dental_clinic, observation_deck, scenic_point,
    supermarket, grocery_store, convenience_store, shopping_mall y muchos más

Fixes v9 (01/04/2026):
  - Numbeo key_map: corregidas 3 keywords rotas por cambio de formato HTML de Numbeo
      · "1 bedroom) in City Centre" → "Bedroom Apartment in City Centre"
      · "1 bedroom) Outside"        → "Bedroom Apartment Outside"
      · "Monthly Pass"              → "Transport Pass" (no era substring contiguo)
  - Google Places searchText: paginación con nextPageToken (hasta 3 páginas = 60 resultados)
      · Afecta a 7 categorías: coworking, surf_school, language_school, tech_hub,
        international_school, pediatrician, pediatric_hospital
      · searchNearby mantiene límite duro de 20 (restricción de la API, sin paginación)

Fixes v8 (incorporado en v9):
  - Numbeo key_map: keywords actualizadas al formato actual de Numbeo

Heredado de v7:
  - Wikipedia: URL construida manualmente para evitar percent-encoding de tildes (403)
               + User-Agent requerido por la API de Wikipedia
  - OSM: reintentos automáticos (3 intentos) + pausa 4s entre queries
         + espera progresiva 15s/30s en caso de 429/504
  - Perfil FAMILIA completo (4 sub-perfiles, 4 dimensiones)
  - 46 place types Google + 20 categorías OSM
  - Sistema de cadencia inteligente por fuente

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
    "google_places": 90,   # días entre re-fetches de Google Places
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
    {
        "name":       "Valencia",
        "display":    "Valencia",
        "slug":       "Valencia",
        "lat":        39.4699,
        "lon":        -0.3763,
        "country":    "Spain",
        "numbeo":     "Valencia",
        "wiki":       "Valencia",
        "google":     "Valencia, Spain",
        "osm_area":   "Valencia",
        "osm_admin":  "8",
    },
    {
        "name":       "Porto",
        "display":    "Porto",
        "slug":       "Porto",
        "lat":        41.1579,
        "lon":        -8.6291,
        "country":    "Portugal",
        "numbeo":     "Porto",
        "wiki":       "Porto",
        "google":     "Porto, Portugal",
        "osm_area":   "Porto",
        "osm_admin":  "8",
    },
    {
        "name":       "Bordeaux",
        "display":    "Burdeos",
        "slug":       "Bordeaux",
        "lat":        44.8378,
        "lon":        -0.5792,
        "country":    "France",
        "numbeo":     "Bordeaux",
        "wiki":       "Bordeaux",
        "google":     "Bordeaux, France",
        "osm_area":   "Bordeaux",
        "osm_admin":  "8",
    },

    # ── EUROPA SUR / MEDITERRÁNEO ─────────────────────────────────────────────
    {
        "name": "Barcelona", "display": "Barcelona", "slug": "Barcelona",
        "lat": 41.3851, "lon": 2.1734, "country": "Spain",
        "numbeo": "Barcelona", "wiki": "Barcelona", "google": "Barcelona, Spain",
        "osm_area": "Barcelona", "osm_admin": "8",
    },
    {
        "name": "Sevilla", "display": "Sevilla", "slug": "Sevilla",
        "lat": 37.3891, "lon": -5.9845, "country": "Spain",
        "numbeo": "Seville", "wiki": "Seville", "google": "Seville, Spain",
        "osm_area": "Sevilla", "osm_admin": "8",
    },
    {
        "name": "Alicante", "display": "Alicante", "slug": "Alicante",
        "lat": 38.3452, "lon": -0.4815, "country": "Spain",
        "numbeo": "Alicante", "wiki": "Alicante", "google": "Alicante, Spain",
        "osm_area": "Alicante", "osm_admin": "8",
    },
    {
        "name": "Las_Palmas", "display": "Las Palmas de Gran Canaria", "slug": "Las_Palmas",
        "lat": 28.1235, "lon": -15.4362, "country": "Spain",
        "numbeo": "Las-Palmas-de-Gran-Canaria", "wiki": "Las Palmas de Gran Canaria",
        "google": "Las Palmas de Gran Canaria, Spain",
        "osm_area": "Las Palmas de Gran Canaria", "osm_admin": "8",
    },
    {
        "name": "Tarifa", "display": "Tarifa", "slug": "Tarifa",
        "lat": 36.0141, "lon": -5.6065, "country": "Spain",
        "numbeo": None,  # ciudad pequeña, no indexada en Numbeo
        "wiki": "Tarifa", "google": "Tarifa, Spain",
        "osm_area": "Tarifa", "osm_admin": "8",
    },
    {
        "name": "Fuerteventura", "display": "Fuerteventura", "slug": "Fuerteventura",
        "lat": 28.3587, "lon": -14.0537, "country": "Spain",
        "numbeo": None,  # isla pequeña, no indexada en Numbeo
        "wiki": "Fuerteventura", "google": "Puerto del Rosario, Fuerteventura, Spain",
        "osm_area": "Fuerteventura", "osm_admin": "6",
    },
    {
        "name": "Granada", "display": "Granada", "slug": "Granada",
        "lat": 37.1773, "lon": -3.5986, "country": "Spain",
        "numbeo": "Granada", "wiki": "Granada", "google": "Granada, Spain",
        "osm_area": "Granada", "osm_admin": "8",
    },
    {
        "name": "Lisboa", "display": "Lisboa", "slug": "Lisboa",
        "lat": 38.7223, "lon": -9.1393, "country": "Portugal",
        "numbeo": "Lisbon", "wiki": "Lisbon", "google": "Lisbon, Portugal",
        "osm_area": "Lisboa", "osm_admin": "8",
    },
    {
        "name": "Faro", "display": "Faro", "slug": "Faro",
        "lat": 37.0194, "lon": -7.9322, "country": "Portugal",
        "numbeo": "Faro", "wiki": "Faro, Portugal", "google": "Faro, Portugal",
        "osm_area": "Faro", "osm_admin": "8",
    },
    {
        "name": "Atenas", "display": "Atenas", "slug": "Atenas",
        "lat": 37.9838, "lon": 23.7275, "country": "Greece",
        "numbeo": "Athens", "wiki": "Athens", "google": "Athens, Greece",
        "osm_area": "Athens", "osm_admin": "8",
    },
    {
        "name": "Roma", "display": "Roma", "slug": "Roma",
        "lat": 41.9028, "lon": 12.4964, "country": "Italy",
        "numbeo": "Rome", "wiki": "Rome", "google": "Rome, Italy",
        "osm_area": "Roma", "osm_admin": "8",
    },
    {
        "name": "Milan", "display": "Milán", "slug": "Milan",
        "lat": 45.4654, "lon": 9.1866, "country": "Italy",
        "numbeo": "Milan", "wiki": "Milan", "google": "Milan, Italy",
        "osm_area": "Milano", "osm_admin": "8",
    },
    {
        "name": "Napoles", "display": "Nápoles", "slug": "Napoles",
        "lat": 40.8518, "lon": 14.2681, "country": "Italy",
        "numbeo": "Naples", "wiki": "Naples", "google": "Naples, Italy",
        "osm_area": "Napoli", "osm_admin": "8",
    },

    # ── EUROPA NORTE / OESTE ──────────────────────────────────────────────────
    {
        "name": "Berlin", "display": "Berlín", "slug": "Berlin",
        "lat": 52.5200, "lon": 13.4050, "country": "Germany",
        "numbeo": "Berlin", "wiki": "Berlin", "google": "Berlin, Germany",
        "osm_area": "Berlin", "osm_admin": "4",
    },
    {
        "name": "Munich", "display": "Múnich", "slug": "Munich",
        "lat": 48.1351, "lon": 11.5820, "country": "Germany",
        "numbeo": "Munich", "wiki": "Munich", "google": "Munich, Germany",
        "osm_area": "München", "osm_admin": "8",
    },
    {
        "name": "Amsterdam", "display": "Ámsterdam", "slug": "Amsterdam",
        "lat": 52.3676, "lon": 4.9041, "country": "Netherlands",
        "numbeo": "Amsterdam", "wiki": "Amsterdam", "google": "Amsterdam, Netherlands",
        "osm_area": "Amsterdam", "osm_admin": "8",
    },
    {
        "name": "Vienna", "display": "Viena", "slug": "Vienna",
        "lat": 48.2082, "lon": 16.3738, "country": "Austria",
        "numbeo": "Vienna", "wiki": "Vienna", "google": "Vienna, Austria",
        "osm_area": "Wien", "osm_admin": "4",
    },
    {
        "name": "Dublin", "display": "Dublín", "slug": "Dublin",
        "lat": 53.3498, "lon": -6.2603, "country": "Ireland",
        "numbeo": "Dublin", "wiki": "Dublin", "google": "Dublin, Ireland",
        "osm_area": "Dublin", "osm_admin": "6",
    },
    {
        "name": "London", "display": "Londres", "slug": "London",
        "lat": 51.5074, "lon": -0.1278, "country": "United Kingdom",
        "numbeo": "London", "wiki": "London", "google": "London, United Kingdom",
        "osm_area": "London", "osm_admin": "6",
    },
    {
        "name": "Stockholm", "display": "Estocolmo", "slug": "Stockholm",
        "lat": 59.3293, "lon": 18.0686, "country": "Sweden",
        "numbeo": "Stockholm", "wiki": "Stockholm", "google": "Stockholm, Sweden",
        "osm_area": "Stockholm", "osm_admin": "8",
    },
    {
        "name": "Chamonix", "display": "Chamonix", "slug": "Chamonix",
        "lat": 45.9237, "lon": 6.8694, "country": "France",
        "numbeo": None,  # ciudad pequeña de montaña, no indexada en Numbeo
        "wiki": "Chamonix", "google": "Chamonix, France",
        "osm_area": "Chamonix-Mont-Blanc", "osm_admin": "8",
    },
    {
        "name": "Innsbruck", "display": "Innsbruck", "slug": "Innsbruck",
        "lat": 47.2692, "lon": 11.4041, "country": "Austria",
        "numbeo": "Innsbruck", "wiki": "Innsbruck", "google": "Innsbruck, Austria",
        "osm_area": "Innsbruck", "osm_admin": "8",
    },
    {
        "name": "Andorra", "display": "Andorra la Vella", "slug": "Andorra",
        "lat": 42.5063, "lon": 1.5218, "country": "Andorra",
        "numbeo": "Andorra-la-Vella", "wiki": "Andorra la Vella",
        "google": "Andorra la Vella, Andorra",
        "osm_area": "Andorra la Vella", "osm_admin": "7",
    },

    # ── EUROPA ESTE / BALCANES ────────────────────────────────────────────────
    {
        "name": "Prague", "display": "Praga", "slug": "Prague",
        "lat": 50.0755, "lon": 14.4378, "country": "Czech Republic",
        "numbeo": "Prague", "wiki": "Prague", "google": "Prague, Czech Republic",
        "osm_area": "Praha", "osm_admin": "6",
    },
    {
        "name": "Budapest", "display": "Budapest", "slug": "Budapest",
        "lat": 47.4979, "lon": 19.0402, "country": "Hungary",
        "numbeo": "Budapest", "wiki": "Budapest", "google": "Budapest, Hungary",
        "osm_area": "Budapest", "osm_admin": "8",
    },
    {
        "name": "Warsaw", "display": "Varsovia", "slug": "Warsaw",
        "lat": 52.2297, "lon": 21.0122, "country": "Poland",
        "numbeo": "Warsaw", "wiki": "Warsaw", "google": "Warsaw, Poland",
        "osm_area": "Warszawa", "osm_admin": "8",
    },
    {
        "name": "Krakow", "display": "Cracovia", "slug": "Krakow",
        "lat": 50.0647, "lon": 19.9450, "country": "Poland",
        "numbeo": "Krakow", "wiki": "Kraków", "google": "Krakow, Poland",
        "osm_area": "Kraków", "osm_admin": "8",
    },
    {
        "name": "Bucharest", "display": "Bucarest", "slug": "Bucharest",
        "lat": 44.4268, "lon": 26.1025, "country": "Romania",
        "numbeo": "Bucharest", "wiki": "Bucharest", "google": "Bucharest, Romania",
        "osm_area": "București", "osm_admin": "4",
    },
    {
        "name": "Sofia", "display": "Sofía", "slug": "Sofia",
        "lat": 42.6977, "lon": 23.3219, "country": "Bulgaria",
        "numbeo": "Sofia", "wiki": "Sofia", "google": "Sofia, Bulgaria",
        "osm_area": "Sofia", "osm_admin": "8",
    },
    {
        "name": "Belgrade", "display": "Belgrado", "slug": "Belgrade",
        "lat": 44.8176, "lon": 20.4569, "country": "Serbia",
        "numbeo": "Belgrade", "wiki": "Belgrade", "google": "Belgrade, Serbia",
        "osm_area": "Beograd", "osm_admin": "6",
    },
    {
        "name": "Tbilisi", "display": "Tiflis", "slug": "Tbilisi",
        "lat": 41.6938, "lon": 44.8015, "country": "Georgia",
        "numbeo": "Tbilisi", "wiki": "Tbilisi", "google": "Tbilisi, Georgia",
        "osm_area": "Tbilisi", "osm_admin": "4",
    },
    {
        "name": "Tallinn", "display": "Tallin", "slug": "Tallinn",
        "lat": 59.4370, "lon": 24.7536, "country": "Estonia",
        "numbeo": "Tallinn", "wiki": "Tallinn", "google": "Tallinn, Estonia",
        "osm_area": "Tallinn", "osm_admin": "8",
    },

    # ── AMÉRICA LATINA ────────────────────────────────────────────────────────
    {
        "name": "Mexico_City", "display": "Ciudad de México", "slug": "Mexico_City",
        "lat": 19.4326, "lon": -99.1332, "country": "Mexico",
        "numbeo": "Mexico-City", "wiki": "Mexico City", "google": "Mexico City, Mexico",
        "osm_area": "Ciudad de México", "osm_admin": "4",
    },
    {
        "name": "Medellin", "display": "Medellín", "slug": "Medellin",
        "lat": 6.2442, "lon": -75.5812, "country": "Colombia",
        "numbeo": "Medellin", "wiki": "Medellín", "google": "Medellín, Colombia",
        "osm_area": "Medellín", "osm_admin": "8",
    },
    {
        "name": "Cartagena", "display": "Cartagena de Indias", "slug": "Cartagena",
        "lat": 10.3910, "lon": -75.4794, "country": "Colombia",
        "numbeo": "Cartagena", "wiki": "Cartagena, Colombia", "google": "Cartagena, Colombia",
        "osm_area": "Cartagena de Indias", "osm_admin": "8",
    },
    {
        "name": "Buenos_Aires", "display": "Buenos Aires", "slug": "Buenos_Aires",
        "lat": -34.6037, "lon": -58.3816, "country": "Argentina",
        "numbeo": "Buenos-Aires", "wiki": "Buenos Aires", "google": "Buenos Aires, Argentina",
        "osm_area": "Buenos Aires", "osm_admin": "4",
    },
    {
        "name": "Montevideo", "display": "Montevideo", "slug": "Montevideo",
        "lat": -34.9011, "lon": -56.1645, "country": "Uruguay",
        "numbeo": "Montevideo", "wiki": "Montevideo", "google": "Montevideo, Uruguay",
        "osm_area": "Montevideo", "osm_admin": "8",
    },
    {
        "name": "Santiago", "display": "Santiago de Chile", "slug": "Santiago",
        "lat": -33.4489, "lon": -70.6693, "country": "Chile",
        "numbeo": "Santiago", "wiki": "Santiago", "google": "Santiago, Chile",
        "osm_area": "Santiago", "osm_admin": "8",
    },
    {
        "name": "Lima", "display": "Lima", "slug": "Lima",
        "lat": -12.0464, "lon": -77.0428, "country": "Peru",
        "numbeo": "Lima", "wiki": "Lima", "google": "Lima, Peru",
        "osm_area": "Lima", "osm_admin": "4",
    },
    {
        "name": "Playa_del_Carmen", "display": "Playa del Carmen", "slug": "Playa_del_Carmen",
        "lat": 20.6296, "lon": -87.0739, "country": "Mexico",
        "numbeo": None,  # ciudad pequeña turística, no indexada en Numbeo
        "wiki": "Playa del Carmen", "google": "Playa del Carmen, Mexico",
        "osm_area": "Playa del Carmen", "osm_admin": "8",
    },
    {
        "name": "Bogota", "display": "Bogotá", "slug": "Bogota",
        "lat": 4.7110, "lon": -74.0721, "country": "Colombia",
        "numbeo": "Bogota", "wiki": "Bogotá", "google": "Bogotá, Colombia",
        "osm_area": "Bogotá", "osm_admin": "4",
    },

    # ── ÁFRICA / ORIENTE MEDIO ────────────────────────────────────────────────
    {
        "name": "Essaouira", "display": "Esauira", "slug": "Essaouira",
        "lat": 31.5085, "lon": -9.7595, "country": "Morocco",
        "numbeo": None,  # ciudad pequeña, no indexada en Numbeo
        "wiki": "Essaouira", "google": "Essaouira, Morocco",
        "osm_area": "Essaouira", "osm_admin": "8",
    },
    {
        "name": "Dakhla", "display": "Dajla", "slug": "Dakhla",
        "lat": 23.7137, "lon": -15.9350, "country": "Morocco",
        "numbeo": None,  # ciudad muy pequeña, no indexada en Numbeo
        "wiki": "Dakhla, Western Sahara", "google": "Dakhla, Morocco",
        "osm_area": "Dakhla", "osm_admin": "8",
    },
    {
        "name": "Marrakech", "display": "Marrakech", "slug": "Marrakech",
        "lat": 31.6295, "lon": -7.9811, "country": "Morocco",
        "numbeo": "Marrakech", "wiki": "Marrakesh", "google": "Marrakech, Morocco",
        "osm_area": "Marrakech", "osm_admin": "8",
    },
    {
        "name": "Dubai", "display": "Dubái", "slug": "Dubai",
        "lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates",
        "numbeo": "Dubai", "wiki": "Dubai", "google": "Dubai, United Arab Emirates",
        "osm_area": "Dubai", "osm_admin": "4",
    },

    # ── ASIA ──────────────────────────────────────────────────────────────────
    {
        "name": "Chiang_Mai", "display": "Chiang Mai", "slug": "Chiang_Mai",
        "lat": 18.7883, "lon": 98.9853, "country": "Thailand",
        "numbeo": "Chiang-Mai", "wiki": "Chiang Mai", "google": "Chiang Mai, Thailand",
        "osm_area": "Chiang Mai", "osm_admin": "8",
    },
    {
        "name": "Bangkok", "display": "Bangkok", "slug": "Bangkok",
        "lat": 13.7563, "lon": 100.5018, "country": "Thailand",
        "numbeo": "Bangkok", "wiki": "Bangkok", "google": "Bangkok, Thailand",
        "osm_area": "Bangkok", "osm_admin": "4",
    },
    {
        "name": "Bali", "display": "Bali (Denpasar)", "slug": "Bali",
        "lat": -8.4095, "lon": 115.1889, "country": "Indonesia",
        "numbeo": "Denpasar", "wiki": "Bali", "google": "Bali, Indonesia",
        "osm_area": "Bali", "osm_admin": "4",
    },
    {
        "name": "Kuala_Lumpur", "display": "Kuala Lumpur", "slug": "Kuala_Lumpur",
        "lat": 3.1390, "lon": 101.6869, "country": "Malaysia",
        "numbeo": "Kuala-Lumpur", "wiki": "Kuala Lumpur", "google": "Kuala Lumpur, Malaysia",
        "osm_area": "Kuala Lumpur", "osm_admin": "4",
    },
    {
        "name": "Da_Nang", "display": "Da Nang", "slug": "Da_Nang",
        "lat": 16.0544, "lon": 108.2022, "country": "Vietnam",
        "numbeo": "Da-Nang", "wiki": "Da Nang", "google": "Da Nang, Vietnam",
        "osm_area": "Đà Nẵng", "osm_admin": "2",
    },
]

# ── GOOGLE PLACE TYPES ────────────────────────────────────────────────────────
# Fuente oficial: developers.google.com/maps/documentation/places/web-service/place-types
#
# Estrategia:
#   - Types con equivalente oficial → Nearby Search (New) con includedTypes
#   - Sin type oficial → Text Search (New) marcado con "text_search": True
#
# Organizados por las categorías de NomadOptima (no las de Google).
# Campos: "cat" = categoría NomadOptima, "subcat" = subcategoría
#
# v11 (08/04/2026): 54 ciudades (era 5), ~170 types GP (era ~115)
# Nuevas categorías: social_media, musica. Nuevos types: ski, kite, windsurf,
# coliving, rooftop_bar, beach_club, concert_hall, jazz_club, folk_music...
# Ver LEARNING.md secciones 23-26 para el razonamiento completo

GOOGLE_PLACE_TYPES = {

    # ── GASTRONOMÍA ───────────────────────────────────────────────────────────
    # Subcat: alta_cocina
    "fine_dining":              {"type": "fine_dining_restaurant",   "cat": "gastronomia", "subcat": "alta_cocina"},
    "seafood":                  {"type": "seafood_restaurant",        "cat": "gastronomia", "subcat": "alta_cocina"},
    # Subcat: cocinas_mundo
    "spanish_restaurant":       {"type": "spanish_restaurant",        "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "italian_restaurant":       {"type": "italian_restaurant",        "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "french_restaurant":        {"type": "french_restaurant",         "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "japanese_restaurant":      {"type": "japanese_restaurant",       "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "chinese_restaurant":       {"type": "chinese_restaurant",        "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "indian_restaurant":        {"type": "indian_restaurant",         "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "mexican_restaurant":       {"type": "mexican_restaurant",        "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "thai_restaurant":          {"type": "thai_restaurant",           "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "mediterranean_restaurant": {"type": "mediterranean_restaurant",  "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "middle_eastern_restaurant":{"type": "middle_eastern_restaurant", "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "vegan_restaurant":         {"type": "vegan_restaurant",          "cat": "gastronomia", "subcat": "cocinas_mundo"},
    "vegetarian_restaurant":    {"type": "vegetarian_restaurant",     "cat": "gastronomia", "subcat": "cocinas_mundo"},
    # Subcat: tapas_casual
    "tapas_bar":                {"type": "tapas_bar",                 "cat": "gastronomia", "subcat": "tapas_casual"},
    "restaurant":               {"type": "restaurant",                "cat": "gastronomia", "subcat": "tapas_casual"},
    "fast_food":                {"type": "fast_food_restaurant",      "cat": "gastronomia", "subcat": "tapas_casual"},
    "market":                   {"type": "market",                    "cat": "gastronomia", "subcat": "tapas_casual"},
    "bakery":                   {"type": "bakery",                    "cat": "gastronomia", "subcat": "tapas_casual"},
    # Subcat: cafes_desayunos
    "coffee_shop":              {"type": "coffee_shop",               "cat": "gastronomia", "subcat": "cafes_desayunos"},
    "cafe":                     {"type": "cafe",                      "cat": "gastronomia", "subcat": "cafes_desayunos"},
    "breakfast_restaurant":     {"type": "breakfast_restaurant",      "cat": "gastronomia", "subcat": "cafes_desayunos"},
    "brunch_restaurant":        {"type": "brunch_restaurant",         "cat": "gastronomia", "subcat": "cafes_desayunos"},
    # Subcat: vinos_bares
    "wine_bar":                 {"type": "wine_bar",                  "cat": "gastronomia", "subcat": "vinos_bares"},
    "bar":                      {"type": "bar",                       "cat": "gastronomia", "subcat": "vinos_bares"},
    "pub":                      {"type": "pub",                       "cat": "gastronomia", "subcat": "vinos_bares"},

    # ── VIDA NOCTURNA ─────────────────────────────────────────────────────────
    "night_club":               {"type": "night_club",                "cat": "vida_nocturna", "subcat": "discotecas"},
    "karaoke":                  {"type": "karaoke",                   "cat": "vida_nocturna", "subcat": "ocio_nocturno"},
    "casino":                   {"type": "casino",                    "cat": "vida_nocturna", "subcat": "ocio_nocturno"},
    "comedy_club":              {"type": "comedy_club",               "cat": "vida_nocturna", "subcat": "ocio_nocturno"},

    # ── CULTURA ───────────────────────────────────────────────────────────────
    "museum":                   {"type": "museum",                    "cat": "cultura", "subcat": "museos"},
    "art_gallery":              {"type": "art_gallery",               "cat": "cultura", "subcat": "arte"},
    "art_studio":               {"type": "art_studio",                "cat": "cultura", "subcat": "arte"},
    "sculpture":                {"type": "sculpture",                 "cat": "cultura", "subcat": "arte"},
    "performing_arts":          {"type": "performing_arts_theater",   "cat": "cultura", "subcat": "teatro_musica"},
    "auditorium":               {"type": "auditorium",                "cat": "cultura", "subcat": "teatro_musica"},
    "movie_theater":            {"type": "movie_theater",             "cat": "cultura", "subcat": "cine"},
    "historical_landmark":      {"type": "historical_landmark",       "cat": "cultura", "subcat": "historia"},
    "monument":                 {"type": "monument",                  "cat": "cultura", "subcat": "historia"},
    "historical_place":         {"type": "historical_place",          "cat": "cultura", "subcat": "historia"},
    "cultural_center":          {"type": "cultural_center",           "cat": "cultura", "subcat": "historia"},

    # ── NATURALEZA & OUTDOOR ──────────────────────────────────────────────────
    "beach":                    {"type": "beach",                     "cat": "naturaleza", "subcat": "playas"},
    "hiking_area":              {"type": "hiking_area",               "cat": "naturaleza", "subcat": "senderismo"},
    "park":                     {"type": "park",                      "cat": "naturaleza", "subcat": "parques"},
    "national_park":            {"type": "national_park",             "cat": "naturaleza", "subcat": "parques"},
    "garden":                   {"type": "garden",                    "cat": "naturaleza", "subcat": "parques"},
    "nature_reserve":           {"type": "nature_reserve",            "cat": "naturaleza", "subcat": "reservas"},
    "wildlife_park":            {"type": "wildlife_park",             "cat": "naturaleza", "subcat": "reservas"},
    "wildlife_refuge":          {"type": "wildlife_refuge",           "cat": "naturaleza", "subcat": "reservas"},

    # ── DEPORTE ACTIVO ────────────────────────────────────────────────────────
    "gym":                      {"type": "gym",                       "cat": "deporte", "subcat": "fitness"},
    "fitness_center":           {"type": "fitness_center",            "cat": "deporte", "subcat": "fitness"},
    "swimming_pool":            {"type": "swimming_pool",             "cat": "deporte", "subcat": "acuatico"},
    "marina":                   {"type": "marina",                    "cat": "deporte", "subcat": "acuatico"},
    "kayak_rental":             {"type": "kayak_rental",              "cat": "deporte", "subcat": "acuatico"},
    "water_park":               {"type": "water_park",                "cat": "deporte", "subcat": "acuatico"},
    "climbing_gym":             {"type": "climbing_gym",              "cat": "deporte", "subcat": "aventura"},
    "adventure_sports":         {"type": "adventure_sports_center",   "cat": "deporte", "subcat": "aventura"},
    "skateboard_park":          {"type": "skateboard_park",           "cat": "deporte", "subcat": "aventura"},
    "tennis_court":             {"type": "tennis_court",              "cat": "deporte", "subcat": "raqueta"},
    "cycling_park":             {"type": "cycling_park",              "cat": "deporte", "subcat": "ciclismo"},
    "ski_resort":               {"type": "ski_resort",                "cat": "deporte", "subcat": "nieve"},
    "ice_skating_rink":         {"type": "ice_skating_rink",          "cat": "deporte", "subcat": "nieve"},
    "sports_club":              {"type": "sports_club",               "cat": "deporte", "subcat": "instalaciones"},
    "sports_complex":           {"type": "sports_complex",            "cat": "deporte", "subcat": "instalaciones"},
    "stadium":                  {"type": "stadium",                   "cat": "deporte", "subcat": "instalaciones"},
    "golf_course":              {"type": "golf_course",               "cat": "deporte", "subcat": "golf"},
    # Text search — sin type oficial en GP
    "surf_school":              {"query": "surf school",              "cat": "deporte", "subcat": "acuatico",
                                 "text_search": True},

    # ── BIENESTAR ─────────────────────────────────────────────────────────────
    "spa":                      {"type": "spa",                       "cat": "bienestar", "subcat": "spa"},
    "yoga_studio":              {"type": "yoga_studio",               "cat": "bienestar", "subcat": "yoga"},
    "sauna":                    {"type": "sauna",                     "cat": "bienestar", "subcat": "spa"},
    "wellness_center":          {"type": "wellness_center",           "cat": "bienestar", "subcat": "bienestar"},
    "massage":                  {"type": "massage",                   "cat": "bienestar", "subcat": "spa"},

    # ── FAMILIA ───────────────────────────────────────────────────────────────
    # Subcat: parques_infantiles
    "playground":               {"type": "playground",                "cat": "familia", "subcat": "parques_infantiles"},
    # Subcat: ocio_familiar
    "amusement_park":           {"type": "amusement_park",            "cat": "familia", "subcat": "ocio_familiar"},
    "amusement_center":         {"type": "amusement_center",          "cat": "familia", "subcat": "ocio_familiar"},
    "zoo":                      {"type": "zoo",                       "cat": "familia", "subcat": "ocio_familiar"},
    "aquarium":                 {"type": "aquarium",                  "cat": "familia", "subcat": "ocio_familiar"},
    "bowling_alley":            {"type": "bowling_alley",             "cat": "familia", "subcat": "ocio_familiar"},
    "childrens_camp":           {"type": "childrens_camp",            "cat": "familia", "subcat": "ocio_familiar"},
    "mini_golf":                {"type": "mini_golf",                 "cat": "familia", "subcat": "ocio_familiar"},
    # Subcat: educacion_infantil
    "preschool":                {"type": "preschool",                 "cat": "familia", "subcat": "educacion_infantil"},
    "primary_school":           {"type": "primary_school",            "cat": "familia", "subcat": "educacion_infantil"},
    "school":                   {"type": "school",                    "cat": "familia", "subcat": "educacion_infantil"},
    "secondary_school":         {"type": "secondary_school",          "cat": "familia", "subcat": "educacion_infantil"},
    "child_care_agency":        {"type": "child_care_agency",         "cat": "familia", "subcat": "educacion_infantil"},
    "international_school":     {"query": "international school",     "cat": "familia", "subcat": "educacion_infantil",
                                 "text_search": True},
    # Subcat: sanidad_infantil
    "pediatrician":             {"query": "pediatrician",             "cat": "familia", "subcat": "sanidad_infantil",
                                 "text_search": True},
    "pediatric_hospital":       {"query": "pediatric hospital",       "cat": "familia", "subcat": "sanidad_infantil",
                                 "text_search": True},

    # ── MASCOTAS ──────────────────────────────────────────────────────────────
    "dog_park":                 {"type": "dog_park",                  "cat": "mascotas", "subcat": "parques_perros"},
    "veterinary_care":          {"type": "veterinary_care",           "cat": "mascotas", "subcat": "veterinarios"},
    "pet_store":                {"type": "pet_store",                 "cat": "mascotas", "subcat": "servicios_mascotas"},
    "pet_boarding":             {"type": "pet_boarding_service",      "cat": "mascotas", "subcat": "servicios_mascotas"},
    "pet_grooming":             {"type": "pet_grooming",              "cat": "mascotas", "subcat": "servicios_mascotas"},

    # ── NÓMADA DIGITAL ────────────────────────────────────────────────────────
    "internet_cafe":            {"type": "internet_cafe",             "cat": "nomada", "subcat": "conectividad"},
    "convention_center":        {"type": "convention_center",         "cat": "nomada", "subcat": "networking"},
    "library":                  {"type": "library",                   "cat": "nomada", "subcat": "trabajo"},
    "coworking":                {"query": "coworking space",          "cat": "nomada", "subcat": "trabajo",
                                 "text_search": True},
    "tech_hub":                 {"query": "technology startup hub",   "cat": "nomada", "subcat": "networking",
                                 "text_search": True},

    # ── ALOJAMIENTO ───────────────────────────────────────────────────────────
    "hotel":                    {"type": "hotel",                     "cat": "alojamiento", "subcat": "hoteles"},
    "hostel":                   {"type": "hostel",                    "cat": "alojamiento", "subcat": "hostels"},
    "bed_and_breakfast":        {"type": "bed_and_breakfast",         "cat": "alojamiento", "subcat": "bb"},
    "extended_stay_hotel":      {"type": "extended_stay_hotel",       "cat": "alojamiento", "subcat": "larga_estancia"},
    "campground":               {"type": "campground",                "cat": "alojamiento", "subcat": "rural"},
    "cottage":                  {"type": "cottage",                   "cat": "alojamiento", "subcat": "rural"},
    "resort_hotel":             {"type": "resort_hotel",              "cat": "alojamiento", "subcat": "hoteles"},

    # ── MOVILIDAD ─────────────────────────────────────────────────────────────
    "subway_station":           {"type": "subway_station",            "cat": "movilidad", "subcat": "metro_tren"},
    "train_station":            {"type": "train_station",             "cat": "movilidad", "subcat": "metro_tren"},
    "light_rail_station":       {"type": "light_rail_station",        "cat": "movilidad", "subcat": "metro_tren"},
    "transit_station":          {"type": "transit_station",           "cat": "movilidad", "subcat": "metro_tren"},
    "bus_station":              {"type": "bus_station",               "cat": "movilidad", "subcat": "autobus"},
    "bus_stop":                 {"type": "bus_stop",                  "cat": "movilidad", "subcat": "autobus"},
    "bicycle_rental":           {"type": "bicycle_rental",            "cat": "movilidad", "subcat": "bicicleta"},
    "airport":                  {"type": "airport",                   "cat": "movilidad", "subcat": "aeropuerto"},
    "ferry_terminal":           {"type": "ferry_terminal",            "cat": "movilidad", "subcat": "ferry"},
    "taxi_stand":               {"type": "taxi_stand",                "cat": "movilidad", "subcat": "taxi"},
    "parking":                  {"type": "parking",                   "cat": "movilidad", "subcat": "coche"},
    "car_rental":               {"type": "car_rental",                "cat": "movilidad", "subcat": "coche"},
    "electric_vehicle":         {"type": "electric_vehicle_charging_station", "cat": "movilidad", "subcat": "coche"},
    "gas_station":              {"type": "gas_station",               "cat": "movilidad", "subcat": "coche"},

    # ── COMPRAS ESENCIALES ────────────────────────────────────────────────────
    "supermarket":              {"type": "supermarket",               "cat": "compras", "subcat": "alimentacion"},
    "grocery_store":            {"type": "grocery_store",             "cat": "compras", "subcat": "alimentacion"},
    "convenience_store":        {"type": "convenience_store",         "cat": "compras", "subcat": "alimentacion"},
    "shopping_mall":            {"type": "shopping_mall",             "cat": "compras", "subcat": "centros_comerciales"},

    # ── SERVICIOS PERSONALES ──────────────────────────────────────────────────
    "barber_shop":              {"type": "barber_shop",               "cat": "servicios", "subcat": "belleza"},
    "beauty_salon":             {"type": "beauty_salon",              "cat": "servicios", "subcat": "belleza"},
    "hair_salon":               {"type": "hair_salon",                "cat": "servicios", "subcat": "belleza"},
    "nail_salon":               {"type": "nail_salon",                "cat": "servicios", "subcat": "belleza"},
    "laundry":                  {"type": "laundry",                   "cat": "servicios", "subcat": "cotidiano"},

    # ── SALUD ─────────────────────────────────────────────────────────────────
    "hospital":                 {"type": "hospital",                  "cat": "salud", "subcat": "hospitales"},
    "dental_clinic":            {"type": "dental_clinic",             "cat": "salud", "subcat": "especialistas"},
    "dentist":                  {"type": "dentist",                   "cat": "salud", "subcat": "especialistas"},
    "chiropractor":             {"type": "chiropractor",              "cat": "salud", "subcat": "especialistas"},
    "physiotherapist":          {"type": "physiotherapist",           "cat": "salud", "subcat": "especialistas"},
    "mental_health":            {"type": "mental_health_practitioner","cat": "salud", "subcat": "salud_mental"},

    # ── TURISMO ───────────────────────────────────────────────────────────────
    "tourist_attraction":       {"type": "tourist_attraction",        "cat": "turismo", "subcat": "atracciones"},
    "observation_deck":         {"type": "observation_deck",          "cat": "turismo", "subcat": "miradores"},
    "scenic_point":             {"type": "scenic_point",              "cat": "turismo", "subcat": "miradores"},
    "tour_operator":            {"type": "tour_operator",             "cat": "turismo", "subcat": "tours"},
    "visitor_center":           {"type": "visitor_center",            "cat": "turismo", "subcat": "informacion"},

    # ── EDUCACIÓN ADULTOS ─────────────────────────────────────────────────────
    "university":               {"type": "university",                "cat": "educacion", "subcat": "universidad"},
    "language_school":          {"query": "language school",          "cat": "educacion", "subcat": "idiomas",
                                 "text_search": True},

    # ── COMUNIDAD & RELIGIÓN ──────────────────────────────────────────────────
    "church":                   {"type": "church",                    "cat": "comunidad", "subcat": "religion"},
    "mosque":                   {"type": "mosque",                    "cat": "comunidad", "subcat": "religion"},
    "synagogue":                {"type": "synagogue",                 "cat": "comunidad", "subcat": "religion"},
    "hindu_temple":             {"type": "hindu_temple",              "cat": "comunidad", "subcat": "religion"},
    "community_center":         {"type": "community_center",          "cat": "comunidad", "subcat": "comunidad"},

    # ── FINANZAS ──────────────────────────────────────────────────────────────
    "atm":                      {"type": "atm",                       "cat": "finanzas", "subcat": "efectivo"},
    "currency_exchange":        {"type": "currency_exchange",         "cat": "finanzas", "subcat": "cambio"},

    # ── DEPORTE — NIEVE (ampliado de ski_resort) ──────────────────────────────
    # ski_resort ya existe arriba. Añadimos los subtipos de nieve/freeride:
    "snowpark":                 {"query": "snowpark freeride snow",   "cat": "deporte", "subcat": "nieve",
                                 "text_search": True},
    "ski_touring":              {"query": "ski touring backcountry",  "cat": "deporte", "subcat": "nieve",
                                 "text_search": True},

    # ── DEPORTE — VIENTO Y AGUA (nueva subcategoría) ──────────────────────────
    # Nota: surf_school ya existe arriba como text_search
    "kitesurfing":              {"query": "kitesurfing school kite",  "cat": "deporte", "subcat": "viento_agua",
                                 "text_search": True},
    "windsurfing":              {"query": "windsurfing school",       "cat": "deporte", "subcat": "viento_agua",
                                 "text_search": True},
    "wingfoil":                 {"query": "wingfoil school wing foil","cat": "deporte", "subcat": "viento_agua",
                                 "text_search": True},
    "snorkeling":               {"query": "snorkeling diving center", "cat": "deporte", "subcat": "acuatico",
                                 "text_search": True},

    # ── VIDA NOCTURNA (ampliado) ──────────────────────────────────────────────
    "cocktail_bar":             {"type": "cocktail_bar",              "cat": "vida_nocturna", "subcat": "bares_copas"},

    # ── IMPACTO VISUAL / SOCIAL MEDIA (nueva categoría) ──────────────────────
    # Decisión 08/04/2026: perfiles de creadores de contenido e influencers
    # necesitan ciudades fotogénicas y aspiracionales — no existía antes
    "rooftop_bar":              {"query": "rooftop bar terrace view", "cat": "social_media", "subcat": "fotogenico",
                                 "text_search": True},
    "beach_club":               {"query": "beach club",               "cat": "social_media", "subcat": "fotogenico",
                                 "text_search": True},
    "street_art":               {"query": "street art mural graffiti","cat": "social_media", "subcat": "arte_urbano",
                                 "text_search": True},
    "photo_spot":               {"query": "instagram photo spot",     "cat": "social_media", "subcat": "puntos_foto",
                                 "text_search": True},
    "luxury_hotel":             {"query": "luxury 5 star hotel",      "cat": "social_media", "subcat": "lujo",
                                 "text_search": True},

    # ── MÚSICA & FESTIVALES (nueva categoría) ─────────────────────────────────
    # Decisión 08/04/2026: perfiles de músicos y melómanos (ej: Essaouira por
    # el festival Gnawa) necesitan ciudades con escena musical fuerte
    "concert_hall":             {"type": "concert_hall",              "cat": "musica", "subcat": "salas_concierto"},
    "opera_house":              {"query": "opera house teatro opera",  "cat": "musica", "subcat": "salas_concierto",
                                 "text_search": True},
    "live_music_venue":         {"query": "live music venue sala",    "cat": "musica", "subcat": "musica_directa",
                                 "text_search": True},
    "jazz_club":                {"query": "jazz club bar",            "cat": "musica", "subcat": "musica_directa",
                                 "text_search": True},
    "music_school":             {"type": "music_school",              "cat": "musica", "subcat": "formacion"},
    "folk_music":               {"query": "folk music traditional flamenco fado", "cat": "musica", "subcat": "folk_tradicional",
                                 "text_search": True},
    "recording_studio":         {"query": "recording studio estudio grabacion", "cat": "musica", "subcat": "industria",
                                 "text_search": True},

    # ── NÓMADA DIGITAL (ampliado) ─────────────────────────────────────────────
    # coliving: vivienda compartida para nómadas — diferente a coworking (trabajo)
    "coliving":                 {"query": "coliving space",           "cat": "nomada", "subcat": "vivienda_nomada",
                                 "text_search": True},

    # ── BIENESTAR (ampliado) ──────────────────────────────────────────────────
    # termas: diferente a spa — balnearios con aguas termales naturales
    "thermal_bath":             {"query": "thermal bath termas balneario", "cat": "bienestar", "subcat": "termas",
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
    if not city.get("numbeo"):
        print(f"    SKIP: ciudad sin slug Numbeo (datos de coste se imputarán manualmente)")
        return {
            "city": city["display"], "source": "numbeo",
            "fetched_at": datetime.now().isoformat(),
            "prices": {}, "key_prices": {}, "quality_indices": {},
            "note": "Sin datos Numbeo — ciudad demasiado pequeña o no indexada",
        }
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

        # key_map con keywords cortas y robustas para matching parcial
        # Numbeo cambia el texto exacto de las filas entre versiones
        key_map = {
            "rent_1br_center":   "Bedroom Apartment in City Centre",  # v8: Numbeo eliminó el formato "(1 bedroom)"
            "rent_1br_outside":  "Bedroom Apartment Outside",          # v8: idem
            "meal_cheap":        "Inexpensive Restaurant",
            "meal_midrange":     "Mid-range Restaurant",
            "coffee":            "Cappuccino",
            "beer":              "Domestic Beer",
            "transport_monthly": "Transport Pass",                     # v8: "Monthly Pass" no es substring de "Monthly Public Transport Pass"
            "gym_monthly":       "Fitness Club",
            "internet_monthly":  "Internet",
            "basic_utilities":   "Electricity, Heating",
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
        # FIX: construir URL manualmente para evitar que requests
        # re-encodee los caracteres especiales (tildes → %C3%A1 → 403)
        wiki_title = city["wiki"].replace(" ", "_")
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + wiki_title,
            headers={"User-Agent": "NomadOptima/1.0 (educational project)"},
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
    """
    v7: Una sola query batch por ciudad en lugar de 20 queries separadas.
    Esto reduce de 40 llamadas a 2 llamadas totales (una por ciudad),
    evitando el rate limit 429 de Overpass API pública.

    Estrategia: query union que recupera todos los elementos de golpe,
    luego contamos por tag en el resultado.
    """
    print(f"  [OpenStreetMap] {city['display']}...")
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Una sola query que trae todos los elementos relevantes de la ciudad
    # Usamos 'out tags;' para poder filtrar por tipo en Python
    batch_query = f"""
    [out:json][timeout:60];
    area[name="{city['osm_area']}"]["admin_level"="{city['osm_admin']}"]->.searchArea;
    (
      way["highway"="cycleway"](area.searchArea);
      way["leisure"="park"](area.searchArea);
      node["public_transport"="stop_position"](area.searchArea);
      node["amenity"="coworking_space"](area.searchArea);
      node["amenity"="university"](area.searchArea);
      way["amenity"="university"](area.searchArea);
      node["amenity"="hospital"](area.searchArea);
      node["leisure"="dog_park"](area.searchArea);
      node["amenity"="bicycle_parking"](area.searchArea);
      node["amenity"="restaurant"](area.searchArea);
      node["amenity"="cafe"](area.searchArea);
      node["leisure"="fitness_centre"](area.searchArea);
      way["natural"="beach"](area.searchArea);
      node["leisure"="playground"](area.searchArea);
      node["leisure"="swimming_pool"]["access"="public"](area.searchArea);
      node["amenity"="childcare"](area.searchArea);
      node["amenity"="kindergarten"](area.searchArea);
      node["amenity"="school"](area.searchArea);
      way["amenity"="school"](area.searchArea);
      node["amenity"="pharmacy"](area.searchArea);
      way["highway"="footway"]["wheelchair"="yes"](area.searchArea);
    );
    out tags;
    """

    result = {
        "city":           city["display"],
        "source":         "openstreetmap",
        "fetched_at":     datetime.now().isoformat(),
        "infrastructure": {},
    }

    # Contadores inicializados a 0
    counts = {
        "bicycle_lanes": 0, "parks": 0, "public_transport": 0,
        "coworking_osm": 0, "universities": 0, "hospitals": 0,
        "dog_areas": 0, "bike_parking": 0, "restaurants": 0,
        "cafes": 0, "gyms": 0, "beaches": 0, "playgrounds": 0,
        "public_pools": 0, "childcare": 0, "kindergartens": 0,
        "schools": 0, "pharmacies": 0, "accessible_paths": 0,
    }

    for intento in range(3):
        try:
            r = requests.post(
                overpass_url,
                data={"data": batch_query},
                timeout=90
            )
            r.raise_for_status()
            elements = r.json().get("elements", [])

            # Clasificar cada elemento por sus tags
            for el in elements:
                tags = el.get("tags", {})
                hw  = tags.get("highway", "")
                lei = tags.get("leisure", "")
                ame = tags.get("amenity", "")
                nat = tags.get("natural", "")
                pt  = tags.get("public_transport", "")
                wch = tags.get("wheelchair", "")
                acc = tags.get("access", "")

                if hw == "cycleway":                    counts["bicycle_lanes"]    += 1
                elif lei == "park":                     counts["parks"]            += 1
                elif pt == "stop_position":             counts["public_transport"] += 1
                elif ame == "coworking_space":          counts["coworking_osm"]    += 1
                elif ame == "university":               counts["universities"]      += 1
                elif ame == "hospital":                 counts["hospitals"]        += 1
                elif lei == "dog_park":                 counts["dog_areas"]        += 1
                elif ame == "bicycle_parking":          counts["bike_parking"]     += 1
                elif ame == "restaurant":               counts["restaurants"]      += 1
                elif ame == "cafe":                     counts["cafes"]            += 1
                elif lei == "fitness_centre":           counts["gyms"]             += 1
                elif nat == "beach":                    counts["beaches"]          += 1
                elif lei == "playground":               counts["playgrounds"]      += 1
                elif lei == "swimming_pool" and acc == "public":
                                                        counts["public_pools"]     += 1
                elif ame == "childcare":                counts["childcare"]        += 1
                elif ame == "kindergarten":             counts["kindergartens"]    += 1
                elif ame == "school":                   counts["schools"]          += 1
                elif ame == "pharmacy":                 counts["pharmacies"]       += 1
                elif hw == "footway" and wch == "yes":  counts["accessible_paths"] += 1

            result["infrastructure"] = counts
            total = sum(counts.values())
            print(f"    OK: {len(counts)} categorías, {total} elementos totales "
                  f"({len(elements)} elementos brutos procesados)")
            break  # éxito

        except Exception as e:
            if intento < 2:
                wait = 20 * (intento + 1)  # 20s, luego 40s
                print(f"    REINTENTO OSM intento {intento+1}/3 — espera {wait}s: {e}")
                time.sleep(wait)
            else:
                result["infrastructure"] = counts  # devuelve los que se pudieron
                result["error"] = str(e)
                print(f"    ERROR OSM: {e}")

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

    # Centros geográficos desplazados ~4 km para superar el límite de 20 por llamada.
    # searchNearby no tiene paginación: la única forma de obtener más resultados es
    # llamar desde distintos puntos y deduplicar por places.id.
    DELTA = 0.04   # ≈ 4.4 km en latitud / ≈ 3.5 km en longitud a lat 40°N
    SEARCH_OFFSETS = [
        (0,      0),       # centro de la ciudad
        (+DELTA, 0),       # norte
        (-DELTA, 0),       # sur
        (0,      +DELTA),  # este
        (0,      -DELTA),  # oeste
    ]

    for category_key, config in GOOGLE_PLACE_TYPES.items():
        try:
            if config.get("text_search"):
                # Text Search con paginación via nextPageToken — hasta 3 páginas (60 resultados)
                # nextPageToken debe ir en el FieldMask para que la API lo devuelva
                seen_ids = set()
                places   = []
                page_token = None
                for _ in range(3):
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
                    if page_token:
                        payload["pageToken"] = page_token
                    headers = {
                        "Content-Type":    "application/json",
                        "X-Goog-Api-Key":  GOOGLE_API_KEY,
                        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,"
                                            "places.formattedAddress,nextPageToken",
                    }
                    r = requests.post(text_url, json=payload, headers=headers, timeout=15)
                    r.raise_for_status()
                    data = r.json()
                    for p in data.get("places", []):
                        pid = p.get("id", "")
                        if pid not in seen_ids:
                            seen_ids.add(pid)
                            places.append(p)
                    page_token = data.get("nextPageToken")
                    if not page_token:
                        break
                    time.sleep(0.5)

            else:
                # Nearby Search — límite duro de 20 por llamada, sin paginación.
                # Solución: 5 llamadas con centros desplazados ~4 km + deduplicación por id.
                seen_ids = set()
                places   = []
                for dlat, dlon in SEARCH_OFFSETS:
                    payload = {
                        "includedTypes": [config["type"]],
                        "locationRestriction": {
                            "circle": {
                                "center": {
                                    "latitude":  city["lat"] + dlat,
                                    "longitude": city["lon"] + dlon,
                                },
                                "radius": 20000.0,
                            }
                        },
                        "maxResultCount": 20,
                    }
                    headers = {
                        "Content-Type":    "application/json",
                        "X-Goog-Api-Key":  GOOGLE_API_KEY,
                        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,"
                                            "places.formattedAddress,places.types",
                    }
                    r = requests.post(nearby_url, json=payload, headers=headers, timeout=15)
                    r.raise_for_status()
                    for p in r.json().get("places", []):
                        pid = p.get("id", "")
                        if pid not in seen_ids:
                            seen_ids.add(pid)
                            places.append(p)
                    time.sleep(0.4)

            ratings = [p["rating"] for p in places if "rating" in p]

            result["categories"][category_key] = {
                "count":      len(places),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "cat":        config["cat"],
                "subcat":     config.get("subcat", ""),
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
                "count": 0, "error": f"HTTP {status}",
                "cat": config["cat"], "subcat": config.get("subcat", ""),
            }
        except Exception as e:
            result["categories"][category_key] = {
                "count": 0, "error": str(e),
                "cat": config["cat"], "subcat": config.get("subcat", ""),
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
