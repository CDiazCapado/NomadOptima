# PROJECT_STATUS.md — Estado actual de NomadOptima

*Actualizado automáticamente por Claude Code al completar cada paso.*

---

## Estado general

**Fase actual:** MVP completo — LightGBM v3 entrenado + app conectada (10/04/2026)
**Último paso completado:** ranker.py actualizado a model_v3 (175 features, NDCG@5=0.9631) + streamlit_app.py conectado a LightGBM. App lista para presentación.
**Próximo paso (post-presentación):** Fix datos GP para ciudades especializadas (kite/surf) + reemplazar city_internet_mbps con Ookla dataset.

---

## Dimensiones del sistema — 09/04/2026

| Parámetro | Valor anterior | Valor actual |
|-----------|---------------|-------------|
| Ciudades en city_features.csv | 5 | **54** (Da_Nang eliminada por EDA, era 55) |
| Features por ciudad | ~80 | **148 numéricas + 1 texto = 149 total** |
| Dimensiones de usuario | 24 | **26** (split deporte en 3 sub-dimensiones) |
| Filas del dataset de entrenamiento | 150.000 | **pendiente regenerar** (dataset v3 con arquetipos actualizados) |
| Columnas del dataset | ~88 | **pendiente** (actualizar con 149 features × 54 ciudades) |

---

## Decisiones de arquitectura — 08/04/2026

### Categorías del formulario (26 dimensiones de usuario — versión definitiva)
| # | Categoría | Estado |
|---|-----------|--------|
| 1 | Gastronomía | ✅ |
| 2 | Vida nocturna | ✅ |
| 3 | Cultura | ✅ (redefinida — sin arte visual) |
| 4 | Arte Visual | ✅ nueva — separada de Cultura |
| 5 | Naturaleza & Outdoor | ✅ |
| 6 | Deporte activo | ✅ (ampliada: ski, kite, windsurf, snow) |
| 7 | Bienestar | ✅ |
| 8 | Familia | ✅ |
| 9 | Mascotas | ✅ |
| 10 | Nómada digital | ✅ (ampliada: coliving) |
| 11 | Alojamiento | ✅ |
| 12 | Movilidad | ✅ |
| 13 | Compras esenciales | ✅ |
| 14 | Servicios personales | ✅ |
| 15 | Salud | ✅ |
| 16 | Turismo | ✅ |
| 17 | Educación adultos | ✅ |
| 18 | Comunidad & Religión | ✅ |
| 19 | Coste de vida | ✅ |
| 20 | Clima | ✅ |
| 21 | Calidad de vida | ✅ |
| 22 | Impacto visual / Social Media | ✅ **nueva** |
| 23 | Música & Festivales | ✅ **nueva** (incl. folklore/tradicional) |
| 24 | Autenticidad / Anti-turístico | ✅ **nueva** |

**Cambio crítico:** Eliminados los 8 arquetipos fijos. Los perfiles sintéticos ahora tienen 26 dimensiones independientes con pesos libres (0-1). Los arquetipos se mantienen solo como etiqueta descriptiva para el HTML de validación. La dimensión "Deporte activo" se dividió en 3: `deporte_agua`, `deporte_montana`, `deporte_urbano`.

### Nuevas features GP a añadir en fetch_cities.py
- `ski_resort`, `snowpark` (text), `ski_touring` (text)
- `kitesurfing` (text), `windsurfing` (text), `surfing` (text), `snorkeling` (text)
- `rooftop_bar` (text), `beach_club` (text), `street_art` (text), `luxury_hotel`, `photo_spot` (text)
- `concert_hall`, `live_music_venue` (text), `jazz_club` (text), `opera_house`, `music_school`
- `folk_music` (text), `recording_studio` (text)
- `coliving` (text)
- `thermal_bath`, `massage_therapist`

### Feedback loop — arquitectura definida
Módulo `app/feedback/` con tres archivos:
- `collector.py` — guarda texto libre + contexto completo del perfil (implementar en MVP)
- `analyzer.py` — NLP para agrupar frases similares (post-MVP, cuando haya usuarios reales)
- `admin.py` — panel de revisión humana

Formato de captura definido para que el NLP encaje sin romper nada (ver LEARNING.md sección 23).

### Lista de ciudades — 54 total
- 5 actuales: Málaga, París, Valencia, Porto, Burdeos
- 49 nuevas: ver tabla completa más abajo
- Coste estimado ingesta: ~$34 (Google Places API)

---

## Archivos del proyecto

### Ingesta de datos
| Archivo | Versión | Estado |
|---------|---------|--------|
| `src/ingestion/fetch_cities.py` | v11 | ✅ Actualizado — 169 GP types, 36 ciudades, categorías música + social media |
| `data/raw/*_raw.json` | — | ✅ 36 ciudades generadas |
| `data/raw/cities_raw.json` | — | ✅ Actualizado (36 ciudades) |
| `logs/ingestion.log` | — | ✅ Activo |
| `scripts/refetch_numbeo.py` | — | ✅ Creado — re-fetcha Numbeo con sleep entre peticiones. Ejecutar cuando expire el rate limit. |
| `scripts/generate_eda_html.py` | — | ✅ Creado — genera HTML interactivo con 25 tabs por categoría |

### Notebooks
| Archivo | Estado | Output generado |
|---------|--------|-----------------|
| `notebooks/01_eda_ciudades.ipynb` | ✅ Creado y ejecutado | EDA Fase 1 — 6 gráficos: fuentes, cobertura, correcciones moneda/Numbeo/Wikidata, GP types, dead features, capping |
| `notebooks/01b_eda_fase2_ciudades.ipynb` | ✅ Creado y ejecutado | EDA Fase 2 — 11 gráficos: describe, histogramas, boxplots, correlaciones, scatter, heatmap ciudad×feature, radar, PCA, UMAP, dendrograma, clustering |
| `notebooks/01b_eda_arquetipos.ipynb` | ✅ Creado y ejecutado | EDA Fase 3 — heatmap 21×26, similitud coseno, radar, dendrograma, PCA, varianza. 3 pares aceptados > 0.90 |
| `notebooks/01c_eda_perfiles_sinteticos.ipynb` | ✅ Creado y ejecutado | EDA Fase 4 — 20/20 spot-checks OK, varianza, PCA 33.5%, cero correlaciones > 0.6 |
| `notebooks/02_synthetic_profiles_v3.ipynb` | ✅ Ejecutado | Output: user_profiles.csv — 5.000 perfiles × 26 dims. NO contiene ciudades ni labels. |
| `notebooks/03_train_model.ipynb` | ⚠️ Rediseñar | Debe: cruzar profiles×cities, labels por producto escalar, features=[user_imp_*+city_features_*+cosine_sim], entrenar LightGBM |

### Documentación
| Archivo | Estado |
|---------|--------|
| `CLAUDE.md` | ✅ Activo |
| `PROJECT_STATUS.md` | ✅ Este archivo |
| `LEARNING.md` | ✅ Secciones 1-23 + Apéndice |
| `ERRORS_LOG.md` | ✅ 13 errores documentados |
| `data/processed/nomadoptima_explicacion.html` | ✅ Actualizado 08/04/2026 — Estado final del proyecto: 42 ciudades, 26 dims, 136 features, 210k filas, 5 módulos. Sección "Estado Final" añadida al principio. |

### Módulos de producción
| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `src/processing/features.py` | ✅ v2 | Capa 1 — CityFeatureBuilder + cosine_similarity + conversión moneda + capping + fallbacks. 26 dimensiones. |
| `src/models/clustering.py` | ✅ Reescrito | Capas 2+3 — USER_CLUSTER_FEATURES actualizado a 26 dims (user_imp_*), CityClusterer con UMAP+HDBSCAN automático para 42 ciudades |
| `src/models/ranker.py` | ✅ v3 (10/04) | Capa 4 — model_v3: 175 features, NDCG@5=0.9631, 43 árboles. Sin user_clusterer/city_clusterer (Capa 3 pendiente post-presentación). |
| `src/models/explainer.py` | ⏳ Pendiente | Capa 5 — SHAP + MMR |
| `src/processing/keyword_matcher.py` | 🔴 Pendiente | Catálogo de actividades + keyword matching + scoring directo |
| `api/main.py` | ⏳ Pendiente | FastAPI /recommend |
| `app/streamlit_app.py` | ✅ v3 (10/04) | Motor LightGBM conectado — sustituye cosine_sim baseline por ranker.scores_series(). Fallback a cosine_sim si ranker no disponible. |
| `app/city_carousel.py` | ✅ Creado | Carrusel de fotos por ciudad (streamlit-image-carousel) |
| `app/assets/cities/*/` | ✅ Estructura creada | 43 carpetas con AQUI_TUS_FOTOS.txt — faltan las fotos |
| `app/city_content.py` | ✅ Creado (esta sesión) | Diccionario CITY_CONTENT con quote + description + photo_search para 43 ciudades |
| `scripts/gen_dataset_html.py` | ✅ Creado (esta sesión) | Genera HTML interactivo del training dataset con 4 tabs |
| `ARQUETIPOS_REVISION.md` | ✅ Creado (esta sesión) | Especificación de 14 arquetipos para revisión de Carlos |
| `scripts/fetch_gp_raw.py` | ✅ Creado | Herramienta EDA: descarga general sin filtros, exporta HTML interactivo |
| `scripts/generate_eda_html.py` | ✅ Creado | Genera HTML interactivo con 25 tabs por categoría de ciudad |
| `scripts/refetch_numbeo.py` | ✅ Creado | Re-fetcha Numbeo para ciudades con rate limit. Ejecutar cuando expire el límite. |
| `data/processed/city_features.csv` | ✅ Generado | 54 ciudades × 149 features — output de features.py v2. Da_Nang excluida, 9 features eliminadas (8 GP muertas + internet_mbps). |
| `data/processed/city_features_eda.html` | ✅ Generado | HTML interactivo con heatmap de colores y 25 tabs por categoría |
| `data/processed/user_profiles.csv` | ✅ Generado (10/04) | 5.000 perfiles × 28 cols (26 user_imp_* + query_id + archetype). Notebook 02 corregido: sin cruce con ciudades. |
| `data/processed/training_dataset.csv` | ✅ Generado (10/04) | 270.000 filas × 177 cols. Labels por producto escalar directo (no cosine_sim). Notebook 03 arquitectura correcta. |
| `data/processed/model_v3/` | ✅ Generado (10/04) | lgbm_ranker_v3.txt, feature_builder_v3.joblib, feature_cols_v3.json, model_metrics_v3.json. NDCG@5=0.9631. |
| `data/processed/training_dataset_overview.html` | ✅ Generado | 218 KB, 4 tabs interactivos — resumen del dataset generado por gen_dataset_html.py |
| `data/processed/hitos_proyecto.html` | ✅ Actualizado (08/04/2026) | 100 hitos, checkboxes HTML reales con tachado al marcar, contador dinámico JS |
| `data/processed/gp_all_types_raw.json` | ✅ Generado | EDA de types GP — 219 types detectados |
| `data/processed/gp_all_types.html` | ✅ Generado | Tabla EDA interactiva ciudad × type |
| `data/processed/gp_types_catalog.html` | ✅ Generado | Catálogo de ~200 types oficiales GP |

---

## Lista de ciudades — 54 total (aprobada 08/04/2026)

### 5 ciudades actuales
Málaga, París, Valencia, Porto, Burdeos

### 49 ciudades nuevas pendientes de ingestar

| Ciudad | País | Región | Razón |
|--------|------|--------|-------|
| Barcelona | España | Europa Sur | Referencia cara, cosmopolita |
| Sevilla | España | Europa Sur | Calor, cultura andaluza, flamenco |
| Alicante | España | Europa Sur | Barata, playa, retirados |
| Las Palmas | España | Europa Sur | Clima eterno, isla, nómadas |
| Tarifa | España | Europa Sur | Kite/windsurf capital mundial |
| Fuerteventura | España | Europa Sur | Kite, windsurf, surf |
| Granada | España | Europa Sur | Ski + playa, flamenco |
| Lisboa | Portugal | Europa Sur | Referencia nómadas |
| Faro | Portugal | Europa Sur | Playa, surf, retirados UK |
| Atenas | Grecia | Europa Sur | Barata, historia, Mediterráneo |
| Roma | Italia | Europa Sur | Cara, cultura máxima |
| Milán | Italia | Europa Sur | Negocios, moda |
| Nápoles | Italia | Europa Sur | Barata, gastronomía |
| Berlín | Alemania | Europa Norte | Media precio, arte, techno, nómadas |
| Múnich | Alemania | Europa Norte | Cara, calidad de vida alta |
| Ámsterdam | Países Bajos | Europa Norte | Cara, bicicletas, cosmopolita |
| Viena | Austria | Europa Norte | Música clásica, cultura |
| Dublín | Irlanda | Europa Norte | Inglés, tech, cara |
| Londres | UK | Europa Norte | Fuera UE, referencia mundial |
| Estocolmo | Suecia | Europa Norte | Cara, calidad vida, nórdica |
| Chamonix | Francia | Europa Norte | Ski, alpinismo |
| Innsbruck | Austria | Europa Norte | Ski + montaña |
| Andorra | Andorra | Europa Norte | Ski, sin impuestos |
| Praga | Rep. Checa | Europa Este | Barata, historia, turismo |
| Budapest | Hungría | Europa Este | Muy barata, termas, nómadas |
| Varsovia | Polonia | Europa Este | Barata, en crecimiento |
| Cracovia | Polonia | Europa Este | Muy barata, cultura |
| Bucarest | Rumanía | Europa Este | Muy barata, internet rápido |
| Sofía | Bulgaria | Europa Este | Muy barata, montaña |
| Belgrado | Serbia | Europa Este | Fuera Schengen, barata, nocturna |
| Tbilisi | Georgia | Europa Este | Fuera Schengen, nómadas, baratísima |
| Tallinn | Estonia | Europa Este | Digital, tech |
| Ciudad de México | México | Latam | Enorme, barata, gastronomía |
| Medellín | Colombia | Latam | Nómadas, clima eterno |
| Cartagena | Colombia | Latam | Playa, turismo, calor |
| Buenos Aires | Argentina | Latam | Cultura, barata |
| Montevideo | Uruguay | Latam | Segura, calidad de vida |
| Santiago | Chile | Latam | Cara para Latam, montaña |
| Lima | Perú | Latam | Gastronomía mundial, barata |
| Playa del Carmen | México | Latam | Playa, nómadas |
| Bogotá | Colombia | Latam | Montaña, fría, grande |
| Essaouira | Marruecos | África/Oriente | Windsurf, festival Gnawa |
| Dakhla | Marruecos | África/Oriente | Kite — destino legendario |
| Marrakech | Marruecos | África/Oriente | Cultura, fotografía, autenticidad |
| Chiang Mai | Tailandia | Asia | Clásico nómada, baratísima |
| Bangkok | Tailandia | Asia | Enorme, calor, barata |
| Bali | Indonesia | Asia | Surf, yoga, nómadas |
| Kuala Lumpur | Malasia | Asia | Barata, moderna |
| ~~Da Nang~~ | ~~Vietnam~~ | ~~Asia~~ | ~~Playa, barata, surf~~ — **ELIMINADA** (GP = 0, ver error #32) |
| Dubái | EAU | Asia | Cara, sin impuestos, lujo |

---

## Problemas pendientes

| # | Problema | Impacto | Prioridad | Estado |
|---|---------|---------|-----------|--------|
| 1 | Numbeo key_prices vacío — key_map no hace match con nombres reales | ALTO | 🔴 Urgente | ✅ Resuelto v9 (01/04/2026) |
| 2 | OSM hospitals Málaga = 0 — posible error de etiquetado en OpenStreetMap | MEDIO | 🟡 Alta | ⏳ Pendiente |
| 3 | Google Places API (New) no activada en Google Cloud Console | ALTO | 🔴 Urgente | ✅ Resuelto (~20/03/2026) |
| 4 | Weather: datos puntuales (día de descarga), no históricos anuales | MEDIO | 🟡 Alta | ⏳ Pendiente |
| 9 | Porto speedtest `fixed_download_mbps` = null (None explícito) | BAJO | 🟢 Baja | ✅ Resuelto notebook 02 (30/03/2026) |
| 10 | Features de idioma binarias — Porto habla portugués, inglés no modelado | MEDIO | 🟡 Alta | ✅ Solución parcial — `city_idioma_nativo` + `city_english_friendliness` |
| 11 | Cards de interés genéricas — Málaga siempre gana por dominancia de city_gp_hiking | ALTO | 🔴 Urgente | ⏳ Rediseño scoring en curso |
| 12 | HTML crudo en Streamlit renderiza como texto — CSS no aplicado | MEDIO | 🟡 Alta | ⏳ Pendiente refactor |
| 18 | Budapest rent_1br_center = 343.396€ — HUF sin convertir a EUR | ALTO | 🔴 Urgente | ✅ Resuelto — diccionario EUR_RATES + to_eur() |
| 19 | Numbeo HTTP 429 para 12 ciudades (Sevilla, Bucarest, Sofía, Belgrado, Cracovia, Tbilisi, Tallinn, Las Palmas, Medellín, CDMX, Cartagena, Andorra) | ALTO | 🔴 Urgente | ⚠️ Temporal — NUMBEO_FALLBACK. Pendiente: re-ejecutar refetch_numbeo.py |
| 20 | Buenos Aires siempre top 3 — coste=0 → coste_invertido=1.0 | ALTO | 🔴 Urgente | ✅ Resuelto — añadida a NUMBEO_FALLBACK |
| 21 | Fuerteventura label=0 siempre — OSM falla en islas | ALTO | 🔴 Urgente | ✅ Resuelto — GP genérico como fallback + capping |
| 22 | Warsaw #1 para kite/windsurf — deporte genérico incluía gimnasios | ALTO | 🔴 Urgente | ✅ Resuelto — split deporte en 3 sub-dimensiones |
| 25 | Perfiles sintéticos v2 sesgados hacia ciudades grandes — beta(0.5,0.5) independiente genera usuarios con 12-13 dims altas → Berlín/Warsaw siempre ganan | ALTO | 🔴 Urgente | ✅ Resuelto en v3 con 14 arquetipos coherentes (08/04/2026) |
| 26 | Warsaw aún #1 para esquí — deporte_montana incluye hiking_area que Warsaw tiene en GP | MEDIO | 🟡 Alta | ⏳ Pendiente — revisar features de OSM ski vs GP hiking |
| 27 | Buenos Aires quality_of_life = 0 — solo tiene coste en fallback | BAJO | 🟢 Baja | ⏳ Pendiente — completar fallback con quality_of_life |
| 28 | 16 ciudades sin ingestar aún (Bali, Bangkok, Bogotá, etc.) | MEDIO | 🟡 Alta | ⏳ Pendiente |

---

## Limitaciones conocidas del modelo (06/04/2026)

Estas limitaciones son conocidas y están documentadas. No son bugs — son decisiones
tomadas conscientemente dado el tiempo disponible y el estado del MVP.

### Limitaciones de datos

| ID | Limitación | Qué afecta | Solución futura |
|----|-----------|-----------|----------------|
| L1 | `gp_hiking` casi igual en todas las ciudades (24-30) — GP no captura calidad de senderos | Búsquedas de senderismo | OSM `route=hiking` — contar rutas GR/PR reales |
| L2 | `surf_school` ≠ zonas de wingfoil/kitesurf — son deportes distintos (olas vs viento) | Deportes acuáticos específicos | Open-Meteo viento histórico + OSM `sport=kitesurfing` |
| L3 | Clima = datos del día de descarga, no histórico anual | Recomendaciones de temperatura | Open-Meteo API histórica (gratis) |
| L4 | `temp_media_anual` y `dias_sol_anual` son valores hardcodeados en el código | Precisión climática | Open-Meteo histórico por coordenadas |
| L5 | `gp_pet_friendly` no existe — no tenemos datos de espacios para mascotas | Filtro de mascotas | Añadir a fetch_cities.py |
| L6 | OSM hospitals Málaga = 0 — error de etiquetado en OpenStreetMap | Feature sanitaria | Revisar query OSM (amenity=hospital) |
| L7 | Coworking capeado en 60 para todas las ciudades — no discrimina | Feature coworking | Usar OSM `office=coworking` como complemento |

### Limitaciones del modelo

| ID | Limitación | Qué afecta | Solución futura |
|----|-----------|-----------|----------------|
| M1 | 30.000 perfiles sintéticos ≠ usuarios reales | Calidad de todos los clusters y labels | Recopilar datos reales de usuarios |
| M2 | Pseudo-labels definidos por reglas heurísticas — el modelo aprende nuestras reglas, no preferencias reales | NDCG alto pero validez incierta | Feedback explícito de usuarios (clicks, reservas) |
| M3 | City clustering manual con solo 3 grupos (5 ciudades son muy pocas para HDBSCAN) | Señal de afinidad ciudad-ciudad débil | Más ciudades → clustering automático |
| M4 | 22 user clusters aprendidos de perfiles sintéticos | Asignación de usuarios nuevos puede ser incorrecta | Re-entrenar con usuarios reales |
| M5 | Actividades específicas (wingfoil, bici de montaña, padel) no tienen features propias | Búsquedas específicas dan resultados genéricos | Fuentes de datos especializadas |

### Lo que el NDCG=0.9995 NO garantiza

- Que las recomendaciones sean útiles para usuarios reales
- Que el modelo distinga bien actividades específicas (surf vs wingfoil)
- Que los datos de Google Places capturen la calidad real de las ciudades
- Que los clusters de usuario reflejen arquetipos reales de nómadas

El modelo está aprendiendo a reproducir las reglas que definimos nosotros.
Un modelo realmente validado necesitaría un A/B test con usuarios reales
midiendo si la ciudad recomendada en #1 es donde el usuario acaba reservando.

---

## Fuentes de datos

### Fuentes actuales (MVP)

| Fuente | Qué aporta | Features generadas | Estado |
|--------|-----------|-------------------|--------|
| **Google Places New API** | Lugares e infraestructura urbana por tipo | `gp_*_count`, `gp_*_rating` — ~50 types actualmente | ✅ Activo — ampliando a ~150 types |
| **Numbeo** | Coste de vida, precios reales, índices de calidad | `numbeo_rent_1br`, `numbeo_meal_cheap`, `numbeo_quality_of_life`... | ✅ Activo |
| **OpenStreetMap (Overpass)** | Infraestructura urbana etiquetada geográficamente | `osm_bicycle_lanes`, `osm_parks`, `osm_hospitals`... | ✅ Activo |
| **wttr.in** | Clima puntual (día de descarga) | `weather_temp_c`, `weather_humidity`... | ✅ Activo — solo dato puntual, no histórico |
| **Speedtest (Ookla)** | Velocidad de internet por país | `speedtest_download_mbps`, `speedtest_rank_global` | ✅ Activo — granularidad país, no ciudad |
| **RestCountries** | Idioma oficial, zona horaria, Schengen, UE | `country_languages`, `country_schengen`, `country_timezone` | ✅ Activo |

### Fuentes futuras — roadmap

| Fuente | Qué aportaría | Features nuevas | Necesidad que cubre |
|--------|--------------|----------------|---------------------|
| **Open-Meteo API** | Clima histórico real por coordenadas (gratis) | `weather_temp_media_anual`, `weather_dias_sol_anual`, `weather_precipitacion_anual` | Reemplaza los valores hardcodeados de clima |
| **OSM `sport=*`** | Instalaciones deportivas específicas etiquetadas | `osm_surf_spots`, `osm_kitesurf`, `osm_padel`, `osm_ski_pistas` | Surf, kitesurf, padel, esquí — no tienen type en GP |
| **OSM `route=hiking`** | Rutas de senderismo reales (GR, PR, senderos) | `osm_rutas_senderismo`, `osm_km_rutas_gr` | Calidad real de senderismo — GP solo cuenta tiendas |
| **OpenAQ API** | Calidad del aire histórica por ciudad (gratis) | `air_quality_pm25_anual`, `air_quality_index` | Feature de calidad de vida muy relevante |
| **Numbeo Crime Index** | Índice de criminalidad y seguridad | `numbeo_crime_index`, `numbeo_safety_index` | Seguridad — muy pedida por familias y mujeres solas |
| **Idealista / Airbnb** | Precio real de alquiler mensual por ciudad | `rent_real_1br`, `rent_real_studio`, `airbnb_avg_night` | Coste de vida más preciso que Numbeo |
| **Meetup API** | Eventos tech, nómadas, idiomas, deporte | `meetup_tech_events_month`, `meetup_nomad_groups` | Comunidad — feature clave para nómadas |
| **Eventbrite API** | Eventos culturales, festivales, conciertos | `events_cultura_month`, `events_festival_season` | Agenda cultural real |
| **Equaldex / ILGA** | Índice LGBTQ+ de derechos y aceptación por país | `lgbtq_index`, `lgbtq_legal_status` | Seguridad para viajeros LGBTQ+ |
| **InterNations / Expat Insider** | Comunidad de expats y nómadas | `expat_community_size`, `expat_satisfaction_index` | Integración social para larga estancia |

### Lo que no tiene API (dato difícil)

| Necesidad | Por qué es difícil | Alternativa parcial |
|-----------|-------------------|---------------------|
| Ruido / tranquilidad | No existe API pública | OSM `landuse=residential` como proxy |
| Vibe / ambiente | Subjetivo, no estructurado | Análisis de reviews de Google Maps (NLP) |
| Comunidad gay-friendly real | Las APIs dan datos legales, no sociales | Número de bares gay en GP como proxy |
| Facilidad para encontrar piso | Depende del mercado local en tiempo real | Idealista scraping |

---

## Dataset de entrenamiento

| Parámetro | v2 (2c) | v3 (5c) | **v4 (36c, actual)** |
|-----------|---------|---------|----------------------|
| Filas totales | 60.000 | 150.000 | **205.000** |
| Ciudades | 2 | 5 | **41** (36 + duplicados prueba) |
| Perfiles sintéticos | 30.000 | 30.000 | **5.000** |
| Dimensiones usuario | 11 | 16 | **26** |
| Features por fila | 84 | 88 | **162** |
| Features ciudad | 68 | 72 | **136 numéricas + 1 texto** |
| Archivo | training_dataset.csv | training_dataset.csv | `data/processed/training_dataset.csv` |

### Evolución del modelo
| Métrica | v1 (2c, hardcoded) | v2 (2c, reales) | v3 (5c, 84 feat) | v4 (5c, 90 feat) | **v5 (36c) — pendiente** |
|---------|-------------------|-----------------|------------------|------------------|--------------------------|
| NDCG@1 | 0.9998 | 0.9998 | 0.9986 | 0.9995 | **⏳** |
| NDCG@2 | 1.0000 | 0.9999 | 0.9981 | 0.9992 | **⏳** |
| Precision@1 | 0.6237 | 0.5805 | 0.5913 | 0.6073 | **⏳** |
| Árboles | 15 | 14 | 2 | 32 | **⏳** |
| Top feature | coste_vida | coste_vida | quality_of_life | gp_hiking | **⏳** |

**Top 5 features v4 (referencia — 5 ciudades):**
1. `city_gp_hiking` — 89.286 pts
2. `afinidad_uc_cc` — 30.071 pts
3. `city_gp_cycling_park` — 21.219 pts
4. `user_temp_min_c` — 21.217 pts
5. `user_presupuesto_max` — 20.249 pts

---

## Arquitectura pendiente — 5 capas

```
[Capa 1] src/processing/features.py  ← SIGUIENTE
         Cosine Similarity entre perfil y ciudad

[Capa 2+3] src/models/clustering.py
           User Clustering + City Clustering (UMAP+HDBSCAN)
           ⚠ Con solo 5 ciudades, city clustering no tiene sentido — posponer

[Capa 4] src/models/ranker.py
         NomadRanker wrapper sobre LightGBM entrenado

[Capa 5] src/models/explainer.py
         SHAP + MMR diversification

[API] api/main.py
      FastAPI POST /recommend

[APP] app/streamlit_app.py
      Demo visual con formulario de usuario + resultados
```

---

## Próximos pasos en orden

```
✅ 1.  Ingestar 36 ciudades con fetch_cities.py v11
✅ 2.  src/processing/features.py v2 — 26D, conversión moneda, capping, fallbacks GP
✅ 3.  notebooks/01_eda_36ciudades.ipynb — EDA completo 9 pasos
✅ 4.  notebooks/02_synthetic_profiles_v2.ipynb — 5.000 perfiles × 41 ciudades = 205.000 filas
       Dataset listo: data/processed/training_dataset.csv (205.000 × 162)

✅ 5.  notebooks/02_synthetic_profiles_v3.ipynb — creado con 14 arquetipos coherentes
✅ 6.  notebooks/03_train_model.ipynb — creado con 8 pasos de entrenamiento
✅ 7.  src/models/clustering.py — reescrito: 26 dims (user_imp_*), CityClusterer UMAP+HDBSCAN automático
✅ 8.  src/models/ranker.py — reescrito: dinámico, usa user_imp_*, carga ciudades desde CSV

⏳ SIGUIENTE: Ejecutar notebooks/02_synthetic_profiles_v3.ipynb
         - Validar que Tarifa aparece en top de perfil kite_surf
         - Validar que Chamonix aparece en top de perfil ski
         - Confirmar que Buenos Aires gana en nomada_barato
         - Si OK → ejecutar notebooks/03_train_model.ipynb

⏳ 8.  src/models/explainer.py — Capa 5: SHAP + MMR diversificación

⏳ 9.  app/streamlit_app.py — demo visual con flujo de elección + resultados + SHAP

⏳ 10. api/main.py (si tiempo) — FastAPI POST /recommend

⏳ 11. Ejecutar scripts/refetch_numbeo.py — datos reales para 12 ciudades con fallback temporal
```

---

## Problemas nuevos detectados — 08/04/2026

| # | Problema | Impacto | Estado |
|---|----------|---------|--------|
| 28 | Cargos €404.86 Google Cloud — bucle autónomo Claude Code durante incidente Anthropic 529 | ALTO — billing desactivado | ⚠️ Reclamación en curso |
| 29 | Numbeo bloqueado hasta mayo 2026 — rate limit mensual agotado | ALTO — 28 ciudades sin precios | ✅ Parcial — precios manuales Expatistan para 28+5 ciudades. Refetch completo mayo 2026 |
| 30 | Crime Index no implementado en ninguna ciudad | ALTO — modelo sin señal de seguridad | ⏳ Pendiente scraper Numbeo (mayo 2026) |
| 31 | area_km² y population por ciudad no disponibles | MEDIO — gp_score densidad + city size | ✅ Resuelto — fetch_wikidata.py ejecutado, 53/53 ciudades. 7 áreas incorrectas: corrección manual pendiente |
| 31b | 7 áreas Wikidata incorrectas (área provincia/metro en vez de ciudad) | BAJO — population_density sesgada | ⏳ Corrección manual pendiente: Dublin 117, Lisboa 85, Porto 41, Chiang Mai 40, London 1572, Playa Carmen 45 km² |
| 32 | Walkability no implementada | MEDIO — feature importante para nómadas | ⏳ Pendiente expandir OSM (POST-MVP) |
| 33 | Da_Nang sin datos GP — excluida del dataset | BAJO — 54 ciudades operativas | ✅ Resuelto — ver error #32 |
| 34 | gp_score modo densidad/volumen — POST-MVP | BAJO — formula definida, no implementada | ⏳ POST-MVP — implementar tras MVP con más ciudades |
| 35 | City clustering eliminado del MVP — Fuzzy C-Means requiere ~300 ciudades para 30 clusters | BAJO — Cosine Similarity cubre la funcionalidad | ✅ Decisión tomada — recuperar con 200+ ciudades |

---

| 36 | 8 features GP muertas (todos ceros 54 ciudades) — eliminadas del CSV | BAJO — sin impacto modelo actual | ⏳ POST-PRESENTACION — fix en fetch_cities.py (ver error #33) |
| 37 | city_internet_mbps: 43/54 = 0 (dato ausente) — eliminada del CSV | BAJO — feature cubierta por gp_coworking | ⏳ POST-PRESENTACION — sustituir por Ookla Global Fixed (ver error #34) |

---

*Última actualización: 09/04/2026 — EDA Fases 1+2 completadas, dataset limpio 54×149, documentados #32-34*
