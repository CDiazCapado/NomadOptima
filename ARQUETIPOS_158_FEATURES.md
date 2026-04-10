# Arquetipos × 158 Features
> Versión: 1.0 | Fecha: 09/04/2026
> Para uso en v2 del modelo — generación de perfiles sintéticos con variabilidad real
> NO se usa en la presentación MVP actual

---

## Escala 0.0 → 1.0

| Valor | Significado |
|-------|-------------|
| `0.0` | Exclusión activa — solo casos extremos e indiscutibles |
| `0.3–0.4` | No le interesa pero no penaliza |
| `0.5` | Neutro |
| `0.6–0.7` | Lo valora |
| `0.8–0.9` | Muy importante |
| `1.0` | Esencial / requisito |

**Regla de uso:** `0.0` solo cuando es incompatible por definición con el arquetipo.
En la matriz de perfiles sintéticos es donde vive la variabilidad y las exclusiones reales del usuario.

---

## Las 158 features

### Features de ciudad (140)
Del dataset `city_features.csv` — prefijo `city_` eliminado para legibilidad.

### Features de idioma nuevas (18)
**Idioma nativo** (lengua materna de los locales):
`idioma_nativo_italiano` · `idioma_nativo_griego` · `idioma_nativo_holandes` · `idioma_nativo_checo`
`idioma_nativo_hungaro` · `idioma_nativo_rumano` · `idioma_nativo_georgiano` · `idioma_nativo_bulgaro`
`idioma_nativo_polaco` · `idioma_nativo_serbio` · `idioma_nativo_tailandes` · `idioma_nativo_catalan`

**Idioma hablado con facilidad** (ya existen 5, se añaden):
`idioma_hablado_italiano` · `idioma_hablado_griego` · `idioma_hablado_holandes`
`idioma_hablado_checo` · `idioma_hablado_hungaro` · `idioma_hablado_rumano`

*(Los 5 existentes — español, inglés, francés, alemán, portugués — se renombran a `idioma_hablado_*`)*

---

## Los 21 arquetipos

---

### 01. Kite / Surf / Viento

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **DEPORTES AGUA** | | **DEPORTES MONTAÑA** | |
| gp_surf_school | 0.9 | gp_ski_resort | 0.3 |
| gp_kitesurfing | 1.0 | gp_snowpark | 0.2 |
| gp_windsurfing | 1.0 | gp_ski_touring | 0.2 |
| gp_wingfoil | 0.9 | gp_climbing_gym | 0.3 |
| gp_snorkeling | 0.6 | gp_hiking_area | 0.5 |
| gp_kayak | 0.5 | gp_adventure_sports | 0.6 |
| gp_marina | 0.7 | gp_cycling_park | 0.4 |
| gp_beach | 0.9 | gp_sports_complex | 0.3 |
| gp_beach_club | 0.6 | gp_tennis_court | 0.3 |
| beaches | 0.9 | **DEPORTE URBANO** | |
| gp_swimming_pool | 0.4 | gyms | 0.4 |
| **NATURALEZA** | | gp_gym | 0.4 |
| parks | 0.5 | gp_fitness_center | 0.4 |
| gp_park | 0.5 | **GASTRONOMÍA** | |
| gp_national_park | 0.5 | restaurants | 0.5 |
| gp_nature_reserve | 0.6 | cafes | 0.5 |
| gp_scenic_point | 0.7 | gp_restaurant | 0.5 |
| gp_photo_spot | 0.6 | gp_cafe | 0.5 |
| gp_observation_deck | 0.4 | gp_fine_dining | 0.3 |
| **CLIMA** | | gp_vegan | 0.4 |
| temp_media_anual | 0.9 | gp_vegetarian | 0.4 |
| dias_sol_anual | 0.9 | gp_market | 0.6 |
| temp_media_norm | 0.9 | gp_tapas | 0.5 |
| dias_sol_norm | 0.9 | gp_seafood | 0.6 |
| temp_actual_c | 0.7 | gp_coffee_shop | 0.5 |
| **VIDA NOCTURNA** | | gp_bakery | 0.4 |
| gp_night_club | 0.4 | gp_wine_bar | 0.4 |
| gp_bar | 0.5 | **NÓMADA DIGITAL** | |
| gp_pub | 0.4 | coworking_osm | 0.5 |
| gp_cocktail_bar | 0.4 | gp_coworking | 0.5 |
| gp_karaoke | 0.3 | gp_coliving | 0.5 |
| **CULTURA** | | gp_tech_hub | 0.4 |
| gp_museum | 0.3 | internet_mbps | 0.6 |
| gp_historical_landmark | 0.4 | gp_internet_cafe | 0.4 |
| gp_monument | 0.3 | gp_library | 0.3 |
| gp_cultural_center | 0.3 | **COSTE** | |
| gp_performing_arts | 0.3 | coste_invertido | 0.7 |
| **ARTE VISUAL** | | coste_vida_estimado | 0.6 |
| gp_art_gallery | 0.3 | alquiler_1br_centro | 0.6 |
| gp_art_studio | 0.3 | meal_cheap | 0.6 |
| gp_sculpture | 0.3 | transport_monthly | 0.5 |
| **BIENESTAR** | | **MOVILIDAD** | |
| gp_spa | 0.4 | public_transport | 0.5 |
| gp_wellness | 0.4 | bicycle_lanes | 0.6 |
| gp_yoga_studio | 0.5 | gp_subway | 0.4 |
| gp_sauna | 0.4 | gp_train_station | 0.4 |
| gp_massage | 0.5 | gp_bus_station | 0.4 |
| gp_thermal_bath | 0.4 | gp_bicycle_rental | 0.6 |
| **FAMILIA** | | **COMPRAS** | |
| playgrounds | 0.3 | gp_supermarket | 0.6 |
| schools | 0.3 | gp_grocery | 0.6 |
| kindergartens | 0.3 | gp_shopping_mall | 0.3 |
| childcare | 0.3 | gp_convenience | 0.5 |
| gp_preschool | 0.3 | **SERVICIOS** | |
| gp_international_school | 0.3 | gp_barber | 0.4 |
| gp_amusement_park | 0.3 | gp_beauty_salon | 0.4 |
| gp_zoo | 0.3 | gp_laundry | 0.5 |
| gp_aquarium | 0.3 | pharmacies | 0.5 |
| **MASCOTAS** | | **SALUD** | |
| dog_areas | 0.4 | hospitals | 0.4 |
| gp_dog_park | 0.4 | gp_dental | 0.4 |
| gp_vet | 0.4 | gp_physiotherapist | 0.4 |
| gp_pet_store | 0.4 | gp_mental_health | 0.4 |
| **TURISMO** | | **EDUCACIÓN** | |
| gp_tourist_attraction | 0.4 | gp_university | 0.3 |
| gp_tour_operator | 0.4 | gp_language_school | 0.4 |
| **SOCIAL MEDIA** | | **COMUNIDAD** | |
| gp_rooftop_bar | 0.6 | gp_community_center | 0.4 |
| gp_street_art | 0.5 | gp_church | 0.4 |
| **MÚSICA** | | gp_mosque | 0.3 |
| gp_concert_hall | 0.3 | gp_synagogue | 0.3 |
| gp_live_music | 0.4 | **CIUDAD** | |
| gp_jazz_club | 0.3 | population | 0.3 |
| gp_folk_music | 0.4 | population_density | 0.3 |
| gp_opera | 0.2 | area_km2 | 0.4 |
| **AUTENTICIDAD** | | quality_of_life | 0.6 |
| gp_market | 0.6 | schengen | 0.5 |
| gp_community_center | 0.4 | moneda_eur | 0.5 |
| gp_language_school | 0.4 | **ALOJAMIENTO** | |
| **IDIOMA NATIVO** | | gp_hostel | 0.6 |
| idioma_nativo_espanol | 0.6 | gp_extended_stay | 0.5 |
| idioma_nativo_ingles | 0.5 | gp_bed_breakfast | 0.5 |
| idioma_nativo_frances | 0.4 | gp_coliving | 0.5 |
| idioma_nativo_aleman | 0.3 | **IDIOMA HABLADO** | |
| idioma_nativo_portugues | 0.5 | idioma_hablado_espanol | 0.6 |
| idioma_nativo_italiano | 0.4 | idioma_hablado_ingles | 0.7 |
| idioma_nativo_griego | 0.5 | idioma_hablado_frances | 0.3 |
| idioma_nativo_holandes | 0.3 | idioma_hablado_aleman | 0.3 |
| idioma_nativo_checo | 0.4 | idioma_hablado_portugues | 0.4 |
| idioma_nativo_hungaro | 0.4 | idioma_hablado_italiano | 0.4 |
| idioma_nativo_rumano | 0.4 | idioma_hablado_griego | 0.4 |
| idioma_nativo_georgiano | 0.5 | idioma_hablado_holandes | 0.3 |
| idioma_nativo_bulgaro | 0.4 | idioma_hablado_checo | 0.3 |
| idioma_nativo_polaco | 0.4 | idioma_hablado_hungaro | 0.3 |
| idioma_nativo_serbio | 0.4 | idioma_hablado_rumano | 0.3 |
| idioma_nativo_tailandes | 0.3 | | |
| idioma_nativo_catalan | 0.5 | | |

---

### 02. Deportista Outdoor / Trail

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **DEPORTES MONTAÑA** | | **NATURALEZA** | |
| gp_hiking_area | 1.0 | parks | 0.8 |
| gp_adventure_sports | 0.9 | gp_park | 0.7 |
| gp_climbing_gym | 0.7 | gp_national_park | 0.9 |
| gp_cycling_park | 0.8 | gp_nature_reserve | 0.9 |
| gp_ski_resort | 0.5 | gp_scenic_point | 0.8 |
| gp_snowpark | 0.4 | gp_photo_spot | 0.6 |
| gp_ski_touring | 0.5 | **CLIMA** | |
| **DEPORTES AGUA** | | temp_media_anual | 0.7 |
| gp_surf_school | 0.4 | dias_sol_anual | 0.7 |
| gp_kitesurfing | 0.3 | temp_media_norm | 0.7 |
| gp_windsurfing | 0.3 | dias_sol_norm | 0.7 |
| gp_kayak | 0.6 | **COSTE** | |
| gp_beach | 0.5 | coste_invertido | 0.6 |
| beaches | 0.5 | coste_vida_estimado | 0.5 |
| **DEPORTE URBANO** | | alquiler_1br_centro | 0.5 |
| gyms | 0.6 | meal_cheap | 0.5 |
| gp_gym | 0.6 | **BIENESTAR** | |
| gp_fitness_center | 0.6 | gp_spa | 0.5 |
| gp_sports_complex | 0.6 | gp_wellness | 0.6 |
| gp_tennis_court | 0.5 | gp_yoga_studio | 0.6 |
| gp_swimming_pool | 0.5 | gp_massage | 0.6 |
| **GASTRONOMÍA** | | gp_physiotherapist | 0.7 |
| restaurants | 0.6 | **MOVILIDAD** | |
| gp_restaurant | 0.6 | bicycle_lanes | 0.7 |
| gp_cafe | 0.5 | gp_bicycle_rental | 0.7 |
| gp_market | 0.6 | public_transport | 0.5 |
| gp_seafood | 0.5 | **AUTENTICIDAD** | |
| **SOCIAL MEDIA** | | gp_market | 0.6 |
| gp_photo_spot | 0.6 | gp_folk_music | 0.5 |
| gp_scenic_point | 0.8 | **VIDA NOCTURNA** | |
| **IDIOMA HABLADO** | | gp_night_club | 0.3 |
| idioma_hablado_espanol | 0.6 | gp_bar | 0.5 |
| idioma_hablado_ingles | 0.7 | gp_pub | 0.4 |
| idioma_hablado_frances | 0.5 | **CIUDAD** | |
| idioma_hablado_aleman | 0.5 | population | 0.3 |
| **IDIOMA NATIVO** | | population_density | 0.3 |
| idioma_nativo_espanol | 0.6 | quality_of_life | 0.6 |
| idioma_nativo_aleman | 0.5 | schengen | 0.5 |
| idioma_nativo_frances | 0.5 | internet_mbps | 0.5 |

---

### 03. Ski & Nieve

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **DEPORTES MONTAÑA** | | **CLIMA** | |
| gp_ski_resort | 1.0 | temp_media_anual | 0.3 |
| gp_snowpark | 0.9 | dias_sol_anual | 0.6 |
| gp_ski_touring | 0.8 | **GASTRONOMÍA** | |
| gp_hiking_area | 0.6 | restaurants | 0.6 |
| gp_adventure_sports | 0.7 | gp_restaurant | 0.6 |
| gp_climbing_gym | 0.5 | gp_fine_dining | 0.6 |
| **DEPORTES AGUA** | | gp_cafe | 0.5 |
| gp_surf_school | 0.2 | gp_wine_bar | 0.5 |
| gp_kitesurfing | 0.2 | gp_bar | 0.5 |
| gp_beach | 0.2 | **BIENESTAR** | |
| beaches | 0.2 | gp_spa | 0.7 |
| **NATURALEZA** | | gp_wellness | 0.7 |
| gp_national_park | 0.8 | gp_sauna | 0.7 |
| gp_nature_reserve | 0.8 | gp_thermal_bath | 0.7 |
| gp_scenic_point | 0.8 | gp_massage | 0.6 |
| gp_photo_spot | 0.7 | gp_yoga_studio | 0.5 |
| **COSTE** | | **MOVILIDAD** | |
| coste_invertido | 0.4 | public_transport | 0.6 |
| alquiler_1br_centro | 0.4 | gp_bus_station | 0.6 |
| coste_vida_estimado | 0.4 | **ALOJAMIENTO** | |
| **IDIOMA HABLADO** | | gp_hostel | 0.5 |
| idioma_hablado_ingles | 0.8 | gp_extended_stay | 0.6 |
| idioma_hablado_frances | 0.7 | **CIUDAD** | |
| idioma_hablado_aleman | 0.8 | population | 0.2 |
| idioma_hablado_espanol | 0.5 | population_density | 0.2 |
| **IDIOMA NATIVO** | | quality_of_life | 0.7 |
| idioma_nativo_frances | 0.7 | schengen | 0.6 |
| idioma_nativo_aleman | 0.8 | internet_mbps | 0.5 |
| idioma_nativo_catalan | 0.6 | | |

---

### 04. Nómada Digital Barato

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **NÓMADA DIGITAL** | | **COSTE** | |
| coworking_osm | 0.9 | coste_invertido | 1.0 |
| gp_coworking | 0.9 | coste_vida_estimado | 1.0 |
| gp_coliving | 0.7 | alquiler_1br_centro | 1.0 |
| gp_tech_hub | 0.7 | meal_cheap | 0.9 |
| internet_mbps | 0.9 | transport_monthly | 0.8 |
| gp_internet_cafe | 0.7 | **GASTRONOMÍA** | |
| gp_library | 0.6 | restaurants | 0.6 |
| **VIDA NOCTURNA** | | gp_restaurant | 0.6 |
| gp_bar | 0.6 | gp_cafe | 0.7 |
| gp_pub | 0.6 | gp_coffee_shop | 0.8 |
| gp_night_club | 0.5 | gp_market | 0.6 |
| gp_cocktail_bar | 0.4 | gp_vegan | 0.5 |
| **MOVILIDAD** | | **AUTENTICIDAD** | |
| public_transport | 0.8 | gp_market | 0.7 |
| gp_subway | 0.7 | gp_folk_music | 0.5 |
| gp_bus_station | 0.7 | gp_community_center | 0.6 |
| gp_bicycle_rental | 0.6 | **SOCIAL MEDIA** | |
| bicycle_lanes | 0.6 | gp_photo_spot | 0.4 |
| **ALOJAMIENTO** | | gp_street_art | 0.5 |
| gp_hostel | 0.9 | **CIUDAD** | |
| gp_coliving | 0.7 | population_density | 0.6 |
| gp_extended_stay | 0.6 | quality_of_life | 0.7 |
| **IDIOMA HABLADO** | | schengen | 0.5 |
| idioma_hablado_ingles | 0.9 | **CLIMA** | |
| idioma_hablado_espanol | 0.6 | temp_media_anual | 0.6 |
| idioma_hablado_frances | 0.4 | dias_sol_anual | 0.6 |
| **IDIOMA NATIVO** | | **COMPRAS** | |
| idioma_nativo_georgiano | 0.6 | gp_supermarket | 0.7 |
| idioma_nativo_bulgaro | 0.6 | gp_grocery | 0.7 |
| idioma_nativo_rumano | 0.6 | gp_convenience | 0.6 |
| idioma_nativo_serbio | 0.6 | | |

---

### 05. Nómada Digital Premium

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **NÓMADA DIGITAL** | | **GASTRONOMÍA** | |
| coworking_osm | 0.9 | gp_fine_dining | 0.8 |
| gp_coworking | 0.9 | restaurants | 0.7 |
| gp_coliving | 0.6 | gp_restaurant | 0.7 |
| gp_tech_hub | 0.8 | gp_cafe | 0.7 |
| internet_mbps | 1.0 | gp_coffee_shop | 0.8 |
| **CALIDAD DE VIDA** | | gp_wine_bar | 0.6 |
| quality_of_life | 0.9 | gp_vegan | 0.6 |
| population_density | 0.7 | **VIDA NOCTURNA** | |
| **CULTURA** | | gp_bar | 0.6 |
| gp_museum | 0.7 | gp_cocktail_bar | 0.6 |
| gp_cultural_center | 0.7 | gp_night_club | 0.5 |
| gp_performing_arts | 0.6 | **DEPORTE URBANO** | |
| **MOVILIDAD** | | gyms | 0.7 |
| public_transport | 0.8 | gp_gym | 0.7 |
| gp_subway | 0.8 | gp_fitness_center | 0.7 |
| gp_train_station | 0.7 | gp_swimming_pool | 0.6 |
| **ALOJAMIENTO** | | **BIENESTAR** | |
| gp_coliving | 0.7 | gp_spa | 0.6 |
| gp_extended_stay | 0.8 | gp_wellness | 0.6 |
| **COSTE** | | gp_yoga_studio | 0.6 |
| coste_invertido | 0.5 | **IDIOMA HABLADO** | |
| alquiler_1br_centro | 0.5 | idioma_hablado_ingles | 1.0 |
| coste_vida_estimado | 0.5 | idioma_hablado_espanol | 0.6 |
| **CIUDAD** | | idioma_hablado_frances | 0.6 |
| schengen | 0.7 | idioma_hablado_aleman | 0.5 |
| moneda_eur | 0.6 | idioma_hablado_portugues | 0.6 |

---

### 06. Nómada Digital Mujer Activa

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **NÓMADA DIGITAL** | | **BIENESTAR** | |
| coworking_osm | 0.8 | gp_spa | 0.6 |
| gp_coworking | 0.8 | gp_wellness | 0.7 |
| internet_mbps | 0.9 | gp_yoga_studio | 0.8 |
| gp_coliving | 0.7 | gp_massage | 0.6 |
| **DEPORTE URBANO** | | **MASCOTAS** | |
| gyms | 0.7 | dog_areas | 0.6 |
| gp_gym | 0.7 | gp_dog_park | 0.6 |
| gp_fitness_center | 0.7 | gp_vet | 0.6 |
| gp_yoga_studio | 0.8 | **EDUCACIÓN** | |
| gp_swimming_pool | 0.6 | gp_language_school | 0.7 |
| **NATURALEZA** | | gp_university | 0.5 |
| parks | 0.7 | **COMUNIDAD** | |
| gp_park | 0.7 | gp_community_center | 0.7 |
| gp_nature_reserve | 0.6 | **GASTRONOMÍA** | |
| gp_hiking_area | 0.6 | gp_cafe | 0.7 |
| **DEPORTES AGUA** | | gp_vegan | 0.7 |
| gp_surf_school | 0.5 | gp_vegetarian | 0.7 |
| gp_kayak | 0.5 | gp_coffee_shop | 0.7 |
| gp_beach | 0.6 | restaurants | 0.6 |
| **SEGURIDAD / CALIDAD** | | **MOVILIDAD** | |
| quality_of_life | 0.8 | public_transport | 0.8 |
| hospitals | 0.6 | bicycle_lanes | 0.7 |
| gp_mental_health | 0.6 | gp_bicycle_rental | 0.7 |
| **COSTE** | | **IDIOMA HABLADO** | |
| coste_invertido | 0.6 | idioma_hablado_ingles | 0.9 |
| alquiler_1br_centro | 0.6 | idioma_hablado_espanol | 0.7 |
| **VIDA NOCTURNA** | | idioma_hablado_frances | 0.6 |
| gp_bar | 0.5 | idioma_hablado_portugues | 0.6 |
| gp_night_club | 0.3 | | |

---

### 07. Cultura & Arte

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **CULTURA** | | **ARTE VISUAL** | |
| gp_museum | 1.0 | gp_art_gallery | 0.9 |
| gp_historical_landmark | 0.9 | gp_art_studio | 0.7 |
| gp_monument | 0.8 | gp_sculpture | 0.7 |
| gp_cultural_center | 0.9 | gp_street_art | 0.7 |
| gp_performing_arts | 0.8 | **MÚSICA** | |
| **TURISMO** | | gp_concert_hall | 0.8 |
| gp_tourist_attraction | 0.8 | gp_opera | 0.8 |
| gp_tour_operator | 0.6 | gp_live_music | 0.7 |
| gp_observation_deck | 0.7 | gp_jazz_club | 0.7 |
| gp_scenic_point | 0.7 | **GASTRONOMÍA** | |
| **SOCIAL MEDIA** | | gp_fine_dining | 0.7 |
| gp_photo_spot | 0.7 | restaurants | 0.7 |
| gp_rooftop_bar | 0.6 | gp_restaurant | 0.7 |
| **CALIDAD DE VIDA** | | gp_wine_bar | 0.6 |
| quality_of_life | 0.8 | gp_market | 0.7 |
| **MOVILIDAD** | | gp_cafe | 0.7 |
| public_transport | 0.7 | **VIDA NOCTURNA** | |
| gp_subway | 0.7 | gp_bar | 0.6 |
| gp_train_station | 0.7 | gp_cocktail_bar | 0.5 |
| **COSTE** | | gp_night_club | 0.4 |
| coste_invertido | 0.5 | **IDIOMA HABLADO** | |
| alquiler_1br_centro | 0.5 | idioma_hablado_ingles | 0.8 |
| **CIUDAD** | | idioma_hablado_frances | 0.7 |
| population_density | 0.7 | idioma_hablado_espanol | 0.6 |
| schengen | 0.6 | idioma_hablado_italiano | 0.5 |
| moneda_eur | 0.5 | idioma_hablado_aleman | 0.5 |
| **DEPORTES** | | **IDIOMA NATIVO** | |
| gp_night_club | 0.4 | idioma_nativo_frances | 0.6 |
| gp_cycling_park | 0.4 | idioma_nativo_italiano | 0.6 |
| gyms | 0.4 | idioma_nativo_aleman | 0.5 |
| gp_yoga_studio | 0.5 | idioma_nativo_griego | 0.6 |

---

### 08. Músico & Festivales

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **MÚSICA** | | **CULTURA** | |
| gp_concert_hall | 1.0 | gp_cultural_center | 0.7 |
| gp_live_music | 1.0 | gp_performing_arts | 0.8 |
| gp_jazz_club | 0.8 | gp_museum | 0.5 |
| gp_folk_music | 0.8 | gp_historical_landmark | 0.5 |
| gp_opera | 0.6 | **ARTE VISUAL** | |
| **VIDA NOCTURNA** | | gp_art_gallery | 0.6 |
| gp_bar | 0.8 | gp_street_art | 0.7 |
| gp_night_club | 0.7 | **AUTENTICIDAD** | |
| gp_pub | 0.7 | gp_market | 0.7 |
| gp_cocktail_bar | 0.6 | gp_community_center | 0.7 |
| **GASTRONOMÍA** | | gp_folk_music | 0.8 |
| restaurants | 0.6 | **COSTE** | |
| gp_cafe | 0.6 | coste_invertido | 0.6 |
| gp_bar | 0.8 | alquiler_1br_centro | 0.6 |
| gp_coffee_shop | 0.6 | meal_cheap | 0.6 |
| **COMUNIDAD** | | **MOVILIDAD** | |
| gp_community_center | 0.7 | public_transport | 0.7 |
| **CIUDAD** | | gp_subway | 0.6 |
| population_density | 0.7 | bicycle_lanes | 0.6 |
| quality_of_life | 0.6 | **ALOJAMIENTO** | |
| **IDIOMA HABLADO** | | gp_hostel | 0.7 |
| idioma_hablado_ingles | 0.8 | gp_coliving | 0.6 |
| idioma_hablado_espanol | 0.7 | **FAMILIA** | |
| idioma_hablado_aleman | 0.6 | playgrounds | 0.3 |
| idioma_hablado_portugues | 0.6 | schools | 0.3 |
| **IDIOMA NATIVO** | | **DEPORTES** | |
| idioma_nativo_aleman | 0.7 | gyms | 0.4 |
| idioma_nativo_espanol | 0.6 | gp_gym | 0.4 |
| idioma_nativo_portugues | 0.6 | gp_yoga_studio | 0.4 |

---

### 09. Gastronomía & Vino

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **GASTRONOMÍA** | | **TURISMO** | |
| gp_fine_dining | 1.0 | gp_tourist_attraction | 0.6 |
| restaurants | 0.9 | gp_tour_operator | 0.5 |
| gp_restaurant | 0.9 | gp_scenic_point | 0.7 |
| gp_seafood | 0.9 | **SOCIAL MEDIA** | |
| gp_tapas | 0.9 | gp_photo_spot | 0.7 |
| gp_wine_bar | 0.9 | gp_rooftop_bar | 0.7 |
| gp_market | 0.9 | **CULTURA** | |
| gp_bakery | 0.8 | gp_museum | 0.6 |
| gp_cafe | 0.8 | gp_historical_landmark | 0.6 |
| gp_coffee_shop | 0.7 | gp_cultural_center | 0.5 |
| gp_vegan | 0.6 | **VIDA NOCTURNA** | |
| gp_vegetarian | 0.6 | gp_bar | 0.7 |
| **AUTENTICIDAD** | | gp_cocktail_bar | 0.6 |
| gp_folk_music | 0.6 | gp_night_club | 0.4 |
| gp_community_center | 0.5 | **MOVILIDAD** | |
| **COSTE** | | public_transport | 0.6 |
| coste_invertido | 0.4 | gp_subway | 0.6 |
| alquiler_1br_centro | 0.4 | **CIUDAD** | |
| coste_vida_estimado | 0.4 | quality_of_life | 0.7 |
| **IDIOMA HABLADO** | | population_density | 0.6 |
| idioma_hablado_espanol | 0.8 | schengen | 0.6 |
| idioma_hablado_frances | 0.8 | moneda_eur | 0.5 |
| idioma_hablado_italiano | 0.7 | **IDIOMA NATIVO** | |
| idioma_hablado_portugues | 0.7 | idioma_nativo_espanol | 0.7 |
| idioma_hablado_ingles | 0.6 | idioma_nativo_frances | 0.7 |
| | | idioma_nativo_italiano | 0.7 |
| | | idioma_nativo_portugues | 0.6 |

---

### 10. Anti-turístico / Auténtico

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **AUTENTICIDAD** | | **GASTRONOMÍA** | |
| gp_folk_music | 0.9 | gp_market | 0.9 |
| gp_market | 0.9 | gp_tapas | 0.7 |
| gp_community_center | 0.8 | gp_seafood | 0.7 |
| gp_language_school | 0.7 | restaurants | 0.6 |
| **TURISMO (penaliza)** | | gp_cafe | 0.6 |
| gp_tourist_attraction | 0.2 | gp_coffee_shop | 0.6 |
| gp_tour_operator | 0.2 | gp_vegan | 0.5 |
| gp_observation_deck | 0.3 | **VIDA NOCTURNA** | |
| **NATURALEZA** | | gp_bar | 0.6 |
| parks | 0.7 | gp_pub | 0.6 |
| gp_national_park | 0.7 | gp_night_club | 0.3 |
| gp_nature_reserve | 0.7 | **MOVILIDAD** | |
| gp_hiking_area | 0.6 | public_transport | 0.6 |
| **CULTURA** | | bicycle_lanes | 0.6 |
| gp_historical_landmark | 0.7 | **COSTE** | |
| gp_cultural_center | 0.6 | coste_invertido | 0.7 |
| gp_monument | 0.6 | alquiler_1br_centro | 0.7 |
| gp_museum | 0.5 | meal_cheap | 0.7 |
| **CIUDAD** | | **IDIOMA HABLADO** | |
| population | 0.3 | idioma_hablado_ingles | 0.4 |
| population_density | 0.4 | idioma_hablado_espanol | 0.6 |
| quality_of_life | 0.6 | idioma_hablado_frances | 0.5 |
| **IDIOMA NATIVO** | | idioma_hablado_georgiano | 0.6 |
| idioma_nativo_georgiano | 0.7 | idioma_hablado_serbio | 0.5 |
| idioma_nativo_espanol | 0.6 | idioma_hablado_portugues | 0.6 |
| idioma_nativo_portugues | 0.6 | | |
| idioma_nativo_griego | 0.6 | | |

---

### 11. Influencer / Creador de Contenido

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **SOCIAL MEDIA** | | **GASTRONOMÍA** | |
| gp_photo_spot | 1.0 | gp_fine_dining | 0.7 |
| gp_rooftop_bar | 0.9 | gp_cafe | 0.7 |
| gp_beach_club | 0.9 | gp_coffee_shop | 0.7 |
| gp_street_art | 0.8 | gp_seafood | 0.6 |
| gp_observation_deck | 0.8 | gp_tapas | 0.6 |
| gp_scenic_point | 0.8 | **VIDA NOCTURNA** | |
| **TURISMO** | | gp_night_club | 0.7 |
| gp_tourist_attraction | 0.8 | gp_cocktail_bar | 0.8 |
| gp_tour_operator | 0.6 | gp_bar | 0.7 |
| gp_historical_landmark | 0.6 | **DEPORTES AGUA** | |
| **ARTE VISUAL** | | gp_surf_school | 0.6 |
| gp_art_gallery | 0.7 | gp_beach | 0.7 |
| gp_sculpture | 0.6 | beaches | 0.7 |
| gp_street_art | 0.8 | gp_beach_club | 0.9 |
| **CULTURA** | | **CLIMA** | |
| gp_museum | 0.6 | temp_media_anual | 0.7 |
| gp_monument | 0.6 | dias_sol_anual | 0.8 |
| **MOVILIDAD** | | **CIUDAD** | |
| public_transport | 0.6 | population_density | 0.6 |
| gp_subway | 0.6 | quality_of_life | 0.6 |
| **COSTE** | | **IDIOMA HABLADO** | |
| coste_invertido | 0.5 | idioma_hablado_ingles | 0.9 |
| alquiler_1br_centro | 0.5 | idioma_hablado_espanol | 0.7 |
| **IDIOMA NATIVO** | | idioma_hablado_frances | 0.6 |
| idioma_nativo_espanol | 0.7 | idioma_hablado_italiano | 0.6 |
| idioma_nativo_frances | 0.6 | | |

---

### 12. Familia con Bebé (<3 años)

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **FAMILIA** | | **SALUD** | |
| playgrounds | 0.8 | hospitals | 0.9 |
| gp_preschool | 0.8 | pharmacies | 0.9 |
| childcare | 0.9 | gp_dental | 0.7 |
| gp_zoo | 0.6 | gp_physiotherapist | 0.7 |
| gp_aquarium | 0.5 | gp_mental_health | 0.6 |
| **MASCOTAS** | | **COMPRAS** | |
| gp_vet | 0.5 | gp_supermarket | 0.8 |
| **MOVILIDAD** | | gp_grocery | 0.8 |
| public_transport | 0.8 | gp_shopping_mall | 0.6 |
| gp_subway | 0.7 | gp_convenience | 0.7 |
| gp_bus_station | 0.7 | **SERVICIOS** | |
| gp_bicycle_rental | 0.5 | gp_beauty_salon | 0.6 |
| bicycle_lanes | 0.6 | gp_laundry | 0.6 |
| **NATURALEZA** | | **GASTRONOMÍA** | |
| parks | 0.8 | restaurants | 0.6 |
| gp_park | 0.8 | gp_restaurant | 0.6 |
| gp_national_park | 0.5 | gp_cafe | 0.6 |
| **BIENESTAR** | | gp_vegan | 0.5 |
| gp_wellness | 0.6 | **CLIMA** | |
| gp_yoga_studio | 0.5 | temp_media_anual | 0.7 |
| **VIDA NOCTURNA (excl.)** | | dias_sol_anual | 0.7 |
| gp_night_club | 0.0 | **CIUDAD** | |
| gp_karaoke | 0.0 | quality_of_life | 0.9 |
| **COSTE** | | schengen | 0.6 |
| coste_invertido | 0.6 | moneda_eur | 0.6 |
| alquiler_1br_centro | 0.6 | **IDIOMA HABLADO** | |
| coste_vida_estimado | 0.6 | idioma_hablado_espanol | 0.8 |
| meal_cheap | 0.6 | idioma_hablado_ingles | 0.7 |
| | | idioma_hablado_frances | 0.5 |
| | | idioma_hablado_aleman | 0.5 |

---

### 13. Familia con Niños (edad escolar)

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **FAMILIA** | | **EDUCACIÓN** | |
| playgrounds | 0.9 | gp_international_school | 0.9 |
| schools | 1.0 | gp_university | 0.5 |
| kindergartens | 0.8 | gp_language_school | 0.7 |
| childcare | 0.8 | gp_library | 0.7 |
| gp_preschool | 0.8 | **TURISMO** | |
| gp_amusement_park | 0.7 | gp_tourist_attraction | 0.6 |
| gp_zoo | 0.8 | gp_tour_operator | 0.5 |
| gp_aquarium | 0.7 | **COMPRAS** | |
| **SALUD** | | gp_supermarket | 0.8 |
| hospitals | 0.9 | gp_shopping_mall | 0.7 |
| pharmacies | 0.8 | gp_grocery | 0.8 |
| gp_dental | 0.7 | **SERVICIOS** | |
| **MOVILIDAD** | | gp_laundry | 0.6 |
| public_transport | 0.9 | pharmacies | 0.8 |
| gp_subway | 0.8 | **BIENESTAR** | |
| gp_bus_station | 0.8 | gp_spa | 0.5 |
| **NATURALEZA** | | gp_wellness | 0.6 |
| parks | 0.8 | **VIDA NOCTURNA (excl.)** | |
| gp_park | 0.8 | gp_night_club | 0.0 |
| gp_national_park | 0.6 | gp_karaoke | 0.2 |
| **COSTE** | | **CLIMA** | |
| coste_invertido | 0.5 | temp_media_anual | 0.7 |
| alquiler_1br_centro | 0.5 | dias_sol_anual | 0.7 |
| **CIUDAD** | | **IDIOMA HABLADO** | |
| quality_of_life | 0.9 | idioma_hablado_espanol | 0.8 |
| schengen | 0.7 | idioma_hablado_ingles | 0.8 |
| moneda_eur | 0.6 | idioma_hablado_frances | 0.6 |
| population_density | 0.6 | idioma_hablado_aleman | 0.6 |

---

### 14. Fiesta + Bienestar Social

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **VIDA NOCTURNA** | | **DEPORTES AGUA** | |
| gp_night_club | 1.0 | gp_beach | 0.7 |
| gp_bar | 0.9 | beaches | 0.7 |
| gp_cocktail_bar | 0.9 | gp_surf_school | 0.5 |
| gp_pub | 0.8 | gp_beach_club | 0.8 |
| gp_karaoke | 0.7 | **BIENESTAR** | |
| **MÚSICA** | | gp_spa | 0.6 |
| gp_live_music | 0.8 | gp_wellness | 0.6 |
| gp_concert_hall | 0.7 | gp_yoga_studio | 0.5 |
| gp_jazz_club | 0.6 | gp_sauna | 0.5 |
| **SOCIAL MEDIA** | | **GASTRONOMÍA** | |
| gp_rooftop_bar | 0.9 | gp_fine_dining | 0.6 |
| gp_photo_spot | 0.7 | restaurants | 0.7 |
| gp_beach_club | 0.8 | gp_cocktail_bar | 0.9 |
| **TURISMO** | | gp_seafood | 0.6 |
| gp_tourist_attraction | 0.6 | **MOVILIDAD** | |
| gp_tour_operator | 0.5 | public_transport | 0.7 |
| **COSTE** | | gp_subway | 0.6 |
| coste_invertido | 0.6 | **CIUDAD** | |
| alquiler_1br_centro | 0.6 | population_density | 0.8 |
| meal_cheap | 0.6 | quality_of_life | 0.6 |
| **CLIMA** | | **IDIOMA HABLADO** | |
| temp_media_anual | 0.7 | idioma_hablado_ingles | 0.9 |
| dias_sol_anual | 0.7 | idioma_hablado_espanol | 0.7 |
| **FAMILIA (excl.)** | | idioma_hablado_aleman | 0.6 |
| schools | 0.3 | idioma_hablado_frances | 0.5 |
| childcare | 0.3 | idioma_hablado_portugues | 0.5 |

---

### 15. Bienestar & Retiro

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **BIENESTAR** | | **NATURALEZA** | |
| gp_spa | 1.0 | parks | 0.8 |
| gp_wellness | 1.0 | gp_park | 0.8 |
| gp_yoga_studio | 0.9 | gp_national_park | 0.8 |
| gp_massage | 0.9 | gp_nature_reserve | 0.8 |
| gp_thermal_bath | 0.8 | gp_scenic_point | 0.7 |
| gp_sauna | 0.8 | gp_hiking_area | 0.7 |
| gp_mental_health | 0.7 | **CLIMA** | |
| **SALUD** | | temp_media_anual | 0.8 |
| hospitals | 0.7 | dias_sol_anual | 0.8 |
| pharmacies | 0.7 | **GASTRONOMÍA** | |
| gp_physiotherapist | 0.8 | gp_vegan | 0.8 |
| **DEPORTE URBANO** | | gp_vegetarian | 0.8 |
| gyms | 0.6 | gp_cafe | 0.6 |
| gp_gym | 0.6 | restaurants | 0.5 |
| gp_fitness_center | 0.6 | gp_market | 0.6 |
| gp_swimming_pool | 0.6 | **VIDA NOCTURNA** | |
| **AUTENTICIDAD** | | gp_night_club | 0.2 |
| gp_market | 0.6 | gp_bar | 0.4 |
| gp_folk_music | 0.5 | **COSTE** | |
| **CIUDAD** | | coste_invertido | 0.6 |
| population | 0.3 | alquiler_1br_centro | 0.6 |
| population_density | 0.3 | **IDIOMA HABLADO** | |
| quality_of_life | 0.8 | idioma_hablado_ingles | 0.7 |
| schengen | 0.5 | idioma_hablado_espanol | 0.7 |
| | | idioma_hablado_portugues | 0.6 |
| | | idioma_hablado_frances | 0.5 |

---

### 16. Jubilado Activo Cálido

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **CLIMA** | | **SALUD** | |
| temp_media_anual | 1.0 | hospitals | 0.9 |
| dias_sol_anual | 1.0 | pharmacies | 0.9 |
| temp_media_norm | 1.0 | gp_dental | 0.8 |
| dias_sol_norm | 1.0 | gp_physiotherapist | 0.7 |
| **BIENESTAR** | | gp_mental_health | 0.6 |
| gp_spa | 0.7 | **COMPRAS** | |
| gp_wellness | 0.7 | gp_supermarket | 0.8 |
| gp_massage | 0.7 | gp_shopping_mall | 0.6 |
| gp_thermal_bath | 0.6 | gp_grocery | 0.8 |
| gp_yoga_studio | 0.6 | gp_convenience | 0.7 |
| **GASTRONOMÍA** | | **SERVICIOS** | |
| restaurants | 0.8 | gp_beauty_salon | 0.6 |
| gp_fine_dining | 0.7 | gp_barber | 0.6 |
| gp_restaurant | 0.8 | gp_laundry | 0.6 |
| gp_cafe | 0.7 | pharmacies | 0.9 |
| gp_seafood | 0.7 | **NATURALEZA** | |
| gp_market | 0.7 | gp_beach | 0.7 |
| **MOVILIDAD** | | beaches | 0.7 |
| public_transport | 0.8 | parks | 0.7 |
| gp_bus_station | 0.8 | gp_scenic_point | 0.6 |
| gp_subway | 0.6 | **VIDA NOCTURNA** | |
| **CALIDAD DE VIDA** | | gp_night_club | 0.2 |
| quality_of_life | 0.9 | gp_bar | 0.4 |
| schengen | 0.7 | **COSTE** | |
| moneda_eur | 0.7 | coste_invertido | 0.7 |
| **COMUNIDAD** | | alquiler_1br_centro | 0.6 |
| gp_community_center | 0.6 | **IDIOMA HABLADO** | |
| gp_church | 0.5 | idioma_hablado_espanol | 0.9 |
| **TURISMO** | | idioma_hablado_ingles | 0.7 |
| gp_tourist_attraction | 0.6 | idioma_hablado_frances | 0.5 |
| gp_tour_operator | 0.6 | idioma_hablado_portugues | 0.6 |

---

### 17. Senior Gran Accesibilidad

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **SALUD** | | **MOVILIDAD** | |
| hospitals | 1.0 | public_transport | 0.9 |
| pharmacies | 1.0 | gp_subway | 0.8 |
| gp_dental | 0.9 | gp_bus_station | 0.9 |
| gp_physiotherapist | 0.9 | **COMPRAS** | |
| gp_mental_health | 0.7 | gp_supermarket | 0.9 |
| **CLIMA** | | gp_shopping_mall | 0.7 |
| temp_media_anual | 0.8 | gp_grocery | 0.9 |
| dias_sol_anual | 0.8 | gp_convenience | 0.8 |
| **SERVICIOS** | | **GASTRONOMÍA** | |
| gp_barber | 0.7 | restaurants | 0.7 |
| gp_beauty_salon | 0.7 | gp_restaurant | 0.7 |
| gp_laundry | 0.7 | gp_cafe | 0.7 |
| **CALIDAD DE VIDA** | | gp_fine_dining | 0.6 |
| quality_of_life | 1.0 | gp_seafood | 0.6 |
| schengen | 0.7 | **COMUNIDAD** | |
| moneda_eur | 0.7 | gp_community_center | 0.7 |
| **NATURALEZA** | | gp_church | 0.6 |
| parks | 0.7 | **COSTE** | |
| gp_park | 0.7 | coste_invertido | 0.5 |
| gp_beach | 0.6 | alquiler_1br_centro | 0.5 |
| beaches | 0.6 | **VIDA NOCTURNA (excl.)** | |
| **IDIOMA HABLADO** | | gp_night_club | 0.0 |
| idioma_hablado_espanol | 0.9 | gp_karaoke | 0.0 |
| idioma_hablado_ingles | 0.7 | **DEPORTES EXTREMOS (excl.)** | |
| idioma_hablado_frances | 0.5 | gp_ski_resort | 0.0 |
| idioma_hablado_aleman | 0.5 | gp_adventure_sports | 0.0 |
| idioma_hablado_portugues | 0.6 | gp_kitesurfing | 0.0 |

---

### 18. Mochilero Barato

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **COSTE** | | **AUTENTICIDAD** | |
| coste_invertido | 1.0 | gp_folk_music | 0.7 |
| coste_vida_estimado | 1.0 | gp_market | 0.8 |
| alquiler_1br_centro | 1.0 | gp_community_center | 0.6 |
| meal_cheap | 1.0 | gp_language_school | 0.6 |
| transport_monthly | 0.9 | **TURISMO** | |
| **MOVILIDAD** | | gp_tourist_attraction | 0.5 |
| public_transport | 0.9 | gp_tour_operator | 0.4 |
| gp_bus_station | 0.8 | gp_historical_landmark | 0.6 |
| gp_train_station | 0.8 | **NATURALEZA** | |
| gp_subway | 0.7 | parks | 0.6 |
| bicycle_lanes | 0.7 | gp_hiking_area | 0.6 |
| gp_bicycle_rental | 0.7 | gp_beach | 0.6 |
| **ALOJAMIENTO** | | beaches | 0.6 |
| gp_hostel | 1.0 | **VIDA NOCTURNA** | |
| gp_coliving | 0.7 | gp_bar | 0.7 |
| **GASTRONOMÍA** | | gp_pub | 0.6 |
| gp_market | 0.8 | gp_night_club | 0.5 |
| gp_cafe | 0.6 | **CIUDAD** | |
| gp_coffee_shop | 0.6 | population_density | 0.5 |
| gp_vegan | 0.5 | quality_of_life | 0.5 |
| gp_vegetarian | 0.5 | schengen | 0.4 |
| **IDIOMA HABLADO** | | **NÓMADA** | |
| idioma_hablado_ingles | 0.9 | internet_mbps | 0.6 |
| idioma_hablado_espanol | 0.6 | gp_internet_cafe | 0.6 |
| idioma_hablado_frances | 0.5 | gp_library | 0.5 |
| **IDIOMA NATIVO** | | **SERVICIOS** | |
| idioma_nativo_georgiano | 0.6 | gp_laundry | 0.7 |
| idioma_nativo_bulgaro | 0.6 | pharmacies | 0.6 |
| idioma_nativo_serbio | 0.6 | | |

---

### 19. Cosmopolita Urbano

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **CULTURA** | | **GASTRONOMÍA** | |
| gp_museum | 0.9 | gp_fine_dining | 0.9 |
| gp_cultural_center | 0.9 | restaurants | 0.8 |
| gp_performing_arts | 0.8 | gp_restaurant | 0.8 |
| gp_historical_landmark | 0.8 | gp_wine_bar | 0.8 |
| gp_monument | 0.7 | gp_cocktail_bar | 0.8 |
| **MOVILIDAD** | | gp_seafood | 0.7 |
| public_transport | 0.9 | gp_coffee_shop | 0.7 |
| gp_subway | 0.9 | **VIDA NOCTURNA** | |
| gp_train_station | 0.8 | gp_bar | 0.8 |
| **CIUDAD** | | gp_night_club | 0.6 |
| population_density | 0.9 | gp_cocktail_bar | 0.8 |
| quality_of_life | 0.9 | **COMPRAS** | |
| schengen | 0.7 | gp_shopping_mall | 0.7 |
| moneda_eur | 0.6 | gp_supermarket | 0.7 |
| **ARTE VISUAL** | | **SERVICIOS** | |
| gp_art_gallery | 0.8 | gp_beauty_salon | 0.6 |
| gp_sculpture | 0.6 | gp_barber | 0.6 |
| gp_street_art | 0.6 | **COSTE** | |
| **NATURALEZA (no excluye)** | | coste_invertido | 0.4 |
| parks | 0.5 | alquiler_1br_centro | 0.4 |
| gp_park | 0.5 | **NÓMADA** | |
| gp_national_park | 0.3 | internet_mbps | 0.7 |
| **TURISMO** | | coworking_osm | 0.5 |
| gp_tourist_attraction | 0.7 | **IDIOMA HABLADO** | |
| gp_observation_deck | 0.7 | idioma_hablado_ingles | 0.9 |
| gp_scenic_point | 0.7 | idioma_hablado_frances | 0.7 |
| **SOCIAL MEDIA** | | idioma_hablado_espanol | 0.7 |
| gp_rooftop_bar | 0.7 | idioma_hablado_italiano | 0.6 |
| gp_photo_spot | 0.7 | idioma_hablado_aleman | 0.6 |

---

### 20. Gamer / Nómada Tech

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **NÓMADA DIGITAL** | | **CALIDAD DE VIDA** | |
| internet_mbps | 1.0 | quality_of_life | 0.8 |
| coworking_osm | 0.8 | schengen | 0.5 |
| gp_coworking | 0.8 | moneda_eur | 0.5 |
| gp_tech_hub | 0.9 | **COMUNIDAD** | |
| gp_internet_cafe | 0.7 | gp_community_center | 0.7 |
| gp_library | 0.6 | gp_tech_hub | 0.9 |
| **COSTE** | | **VIDA NOCTURNA** | |
| coste_invertido | 0.7 | gp_bar | 0.6 |
| alquiler_1br_centro | 0.7 | gp_night_club | 0.5 |
| meal_cheap | 0.7 | gp_pub | 0.5 |
| **GASTRONOMÍA** | | **CULTURA** | |
| gp_cafe | 0.7 | gp_museum | 0.5 |
| gp_coffee_shop | 0.8 | gp_cultural_center | 0.5 |
| gp_restaurant | 0.6 | **AUTENTICIDAD** | |
| gp_vegan | 0.5 | gp_market | 0.5 |
| **MOVILIDAD** | | **NATURALEZA** | |
| public_transport | 0.8 | parks | 0.4 |
| gp_subway | 0.7 | gp_park | 0.4 |
| gp_bus_station | 0.7 | **IDIOMA HABLADO** | |
| **CIUDAD** | | idioma_hablado_ingles | 1.0 |
| population_density | 0.7 | idioma_hablado_espanol | 0.5 |
| **DEPORTES** | | idioma_hablado_aleman | 0.5 |
| gyms | 0.5 | idioma_hablado_checo | 0.5 |
| gp_gym | 0.5 | idioma_hablado_holandes | 0.5 |
| gp_fitness_center | 0.5 | **IDIOMA NATIVO** | |
| gp_swimming_pool | 0.4 | idioma_nativo_checo | 0.5 |
| gp_climbing_gym | 0.4 | idioma_nativo_polaco | 0.5 |

---

### 21. Mascotas & Naturaleza

| Feature | Score | Feature | Score |
|---------|-------|---------|-------|
| **MASCOTAS** | | **NATURALEZA** | |
| dog_areas | 1.0 | parks | 0.9 |
| gp_dog_park | 1.0 | gp_park | 0.9 |
| gp_vet | 0.9 | gp_national_park | 0.8 |
| gp_pet_store | 0.8 | gp_nature_reserve | 0.8 |
| **BIENESTAR** | | gp_hiking_area | 0.8 |
| gp_wellness | 0.7 | gp_scenic_point | 0.7 |
| gp_yoga_studio | 0.7 | gp_beach | 0.7 |
| gp_spa | 0.6 | beaches | 0.7 |
| **CLIMA** | | **DEPORTES AGUA** | |
| temp_media_anual | 0.7 | gp_kayak | 0.6 |
| dias_sol_anual | 0.7 | gp_surf_school | 0.5 |
| **DEPORTE URBANO** | | gp_beach | 0.7 |
| gyms | 0.6 | **GASTRONOMÍA** | |
| gp_fitness_center | 0.6 | gp_cafe | 0.6 |
| gp_cycling_park | 0.7 | restaurants | 0.5 |
| gp_bicycle_rental | 0.7 | gp_vegan | 0.6 |
| bicycle_lanes | 0.7 | gp_market | 0.6 |
| **MOVILIDAD** | | **COSTE** | |
| public_transport | 0.6 | coste_invertido | 0.6 |
| **CALIDAD DE VIDA** | | alquiler_1br_centro | 0.6 |
| quality_of_life | 0.8 | **VIDA NOCTURNA** | |
| **CIUDAD** | | gp_night_club | 0.3 |
| population | 0.3 | gp_bar | 0.4 |
| population_density | 0.3 | **IDIOMA HABLADO** | |
| **ALOJAMIENTO** | | idioma_hablado_espanol | 0.7 |
| gp_hostel | 0.5 | idioma_hablado_ingles | 0.7 |
| gp_extended_stay | 0.6 | idioma_hablado_portugues | 0.6 |
| gp_coliving | 0.5 | idioma_hablado_frances | 0.5 |

---

## Notas de uso

- Este archivo es **referencia para v2** — no se usa en el MVP actual
- Cuando se implemente la matriz de perfiles sintéticos, cada arquetipo genera perfiles con variabilidad alrededor de estos valores base
- Las exclusiones activas (`0.0`) solo están en casos extremos e indiscutibles
- Los valores `0.3–0.4` son "no me importa pero no penalizo"
- Los valores `0.5` son neutros
- Para añadir nuevas features al dataset, añadir también la columna correspondiente a cada arquetipo

*Creado: 09/04/2026 — sesión de recuperación tras bloqueo*
