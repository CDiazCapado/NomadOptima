# CLAUDE.md — Instrucciones permanentes para Claude Code
# NomadOptima — Motor de Matching Ciudad-Perfil de Vida

Este archivo es leído automáticamente por Claude Code al iniciar cada sesión.
Define cómo comportarse, qué archivos mantener y con qué formato.

---

## 1. Contexto del proyecto

NomadOptima es un Hybrid Recommender System formulado como Learning to Rank.
Autor: Carlos Díaz Capado
Repo: github.com/CDiazCapado/NomadOptima
Stack: Python 3.12.10, LightGBM 4.6.0, SHAP 0.51.0, MLflow 3.10.1, FastAPI 0.135.2, Streamlit 1.55.0, PostgreSQL, Docker

### Fuentes de datos activas
| Fuente | Qué aporta | Prefijo features |
|--------|-----------|-----------------|
| Google Places New API | Lugares por tipo en radio urbano (~150 types) | `gp_` |
| Numbeo | Coste de vida, precios, índices de calidad | `numbeo_` |
| OpenStreetMap (Overpass) | Infraestructura urbana etiquetada | `osm_` |
| wttr.in | Clima puntual (solo día de descarga, no histórico) | `weather_` |
| Speedtest (Ookla) | Velocidad de internet por país | `speedtest_` |
| RestCountries | Idioma, zona horaria, Schengen, UE | `country_` |

### Fuentes futuras planificadas
Open-Meteo (clima histórico) · OSM sport=* (surf, padel, kitesurf, esquí) · OpenAQ (calidad del aire) · Numbeo Crime Index · Meetup API · Equaldex (LGBTQ+)

### Categorías del formulario de usuario (20 categorías, diseño orientado al usuario)
Gastronomía · Vida nocturna · Cultura · Naturaleza & Outdoor · Deporte activo · Bienestar · Familia · Mascotas · Nómada digital · Alojamiento · Movilidad · Compras esenciales · Servicios personales · Salud · Turismo · Educación adultos · Comunidad & Religión · Coste de vida · Clima · Calidad de vida
Ver detalle completo en LEARNING.md sección 22.

**Antes de hacer cualquier cosa**, lee estos tres archivos en orden:
1. `PROJECT_STATUS.md` — estado actual, último paso, próximo paso
2. `LEARNING.md` — arquitectura completa y decisiones técnicas tomadas
3. `ERRORS_LOG.md` — errores conocidos y sus soluciones

Si alguno no existe todavía, créalo siguiendo el formato de este archivo.

---

## 2. Reglas de comportamiento

### Al crear o modificar archivos
- Trabaja siempre dentro del entorno virtual `.venv` activado
- Nunca toques `.env` — contiene API keys reales
- Nunca hagas commit automático — el usuario decide qué sube a Git
- Si un archivo ya existe, léelo completo antes de modificarlo
- Usa siempre UTF-8 con encoding explícito al leer/escribir archivos Python

### Al escribir código Python
- Sigue el estilo del proyecto: prefijos por fuente (`osm_`, `gp_`, `numbeo_`)
- Añade docstrings en español a todas las funciones nuevas
- Añade comentarios explicativos — el usuario está aprendiendo
- Usa `np.nan` para valores ausentes, nunca `None` en DataFrames
- Loggea con el sistema existente en `fetch_cities.py` (logger de dos niveles)

### Al responder
- Explica siempre el concepto técnico antes del código
- Usa el nombre técnico correcto de cada concepto
- Si detectas un error nuevo, avisa antes de corregirlo

### REGLA CRÍTICA — Aprobación explícita antes de ejecutar CUALQUIER cosa
**Esta regla se aplica a ABSOLUTAMENTE TODO, sin excepciones.**

Antes de ejecutar cualquier acción (código, comando, modificación de archivo, git,
llamada a API, instalación de paquete, borrado de archivo, etc.):

1. **Analiza** la situación y los problemas que detectas
2. **Explica** qué opciones existen y cuáles son las consecuencias de cada una
3. **Propón** la solución que consideras mejor, con justificación
4. **Espera** a que Carlos diga explícitamente que proceda

No ejecutes nada hasta recibir aprobación. Ni aunque parezca obvio. Ni aunque sea
un cambio pequeño. Ni aunque el usuario haya aprobado algo similar antes.

La única excepción es si Carlos dice explícitamente "hazlo", "ejecuta", "procede",
"adelante" o similar — y solo para esa acción concreta, no para las siguientes.

---

## 3. Archivos a mantener actualizados

Estos tres archivos son la memoria del proyecto.
Actualízalos cada vez que ocurra algo relevante, sin que el usuario tenga que pedírtelo.

### PROJECT_STATUS.md
Actualizar cuando:
- Se complete un paso del roadmap
- Cambie el estado de un archivo importante
- Aparezca un nuevo problema pendiente
- Se resuelva un problema existente

### ERRORS_LOG.md
Actualizar cuando:
- Se detecte un error nuevo (aunque sea pequeño)
- Se resuelva un error existente (cambiar estado a ✅ Resuelto)
- Se descubra la causa raíz de un problema pendiente

Formato de cada error:
```
## #N — Título descriptivo del error
Fecha | Archivo | Etiquetas: [CATEGORIA] [SUBCATEGORIA]
### Mensaje de error exacto
### Qué estaba pasando
### Explicación del concepto técnico (desde cero, para alguien aprendiendo)
### Causa raíz
### Solución aplicada con código
### Para recordar en una entrevista
```

### LEARNING.md
Actualizar cuando:
- Se implemente una técnica nueva (clustering, normalización, etc.)
- Se tome una decisión de arquitectura importante
- Se complete un notebook nuevo

Formato de cada sección:
```
# N. Título del concepto
## Concepto (explicación desde cero)
## Cómo lo usamos en NomadOptima
## Código de ejemplo
## Por qué esta decisión y no otra
```

---

## 4. Estructura del proyecto

```
nomadoptima/                           estado: 06/04/2026
├── CLAUDE.md                          ← instrucciones para Claude Code (este archivo)
├── PROJECT_STATUS.md                  ← estado actual + limitaciones conocidas
├── LEARNING.md                        ← cuaderno aprendizaje (19 secciones + apéndice)
├── ERRORS_LOG.md                      ← errores y soluciones
├── requirements.txt                   ← dependencias Python
├── .env                               ← API keys (NUNCA tocar)
├── .gitignore
│
├── data/
│   ├── raw/                           ← JSONs de fetch_cities.py (en .gitignore)
│   │   ├── cities_raw.json            ← ENTRADA PRINCIPAL del sistema (5 ciudades)
│   │   └── *_raw.json                 ← un JSON por ciudad
│   └── processed/
│       ├── training_dataset.csv       ← 150k filas × 88 cols — notebook 02 (54MB)
│       ├── training_dataset_enriched.csv ← 150k × 94 cols — notebook 04 (60MB)
│       ├── model_v2/                  ← 6 artefactos del modelo en producción ✅
│       │   ├── lgbm_ranker.txt        ← LightGBM (32 árboles, 90 features)
│       │   ├── user_clusterer.joblib  ← PCA+UMAP+HDBSCAN (22 clusters)
│       │   ├── city_clusterer.joblib  ← 3 clusters manuales de ciudad
│       │   ├── feature_builder.joblib ← CityFeatureBuilder + MinMaxScaler
│       │   ├── feature_cols.json      ← orden exacto de las 90 features
│       │   └── affinity_table.csv     ← tabla 22×3 afinidad user×city cluster
│       └── *.png                      ← gráficos generados por notebooks
│
├── notebooks/
│   ├── 01_eda_5ciudades.ipynb         ← EDA 5 ciudades + perfiles sintéticos ✅
│   ├── 02_synthetic_profiles.ipynb    ← 150k perfiles sintéticos + labels ✅
│   ├── 03_lightgbm_ranker.ipynb       ← modelo v1, 84 features (referencia) ✅
│   ├── 04_clustering_ranker.ipynb     ← modelo v2, 90 features (ACTUAL) ✅
│   └── mlruns/                        ← experimentos MLflow (4 runs)
│
├── src/
│   ├── ingestion/
│   │   └── fetch_cities.py            ← v9: 6 APIs, offset GP, 5 ciudades ✅
│   ├── processing/
│   │   └── features.py                ← CityFeatureBuilder + cosine_sim (Capa 1) ✅
│   └── models/
│       ├── clustering.py              ← UserClusterer + CityClusterer (Capas 2+3) ✅
│       ├── ranker.py                  ← NomadRanker producción (Capa 4) ✅
│       └── explainer.py               ← PENDIENTE (Capa 5: SHAP + MMR)
│
├── app/
│   └── streamlit_app.py               ← PENDIENTE (demo visual)
│
├── api/
│   └── main.py                        ← PENDIENTE (FastAPI /recommend)
│
└── scripts/                           ← scripts de apoyo (borrar los de uso único)
    ├── add_eda_sections.py            ← BORRAR — uso único, trabajo hecho
    ├── create_notebook_04.py          ← BORRAR — uso único, trabajo hecho
    └── fetch_gp_raw.py                ← MANTENER — herramienta EDA reutilizable (todos los GP types)
```

### Archivos a borrar (detectados en revisión 06/04/2026)
- `data/processed/cities_features_raw.csv` — versión obsoleta pre-refactor
- `data/processed/eda_radar_chart.png` — sustituido por eda_radar_5cities.png
- `scripts/add_eda_sections.py` — uso único completado
- `scripts/create_notebook_04.py` — uso único completado

### Entradas pendientes de añadir al `.gitignore`
```
data/processed/training_dataset.csv
data/processed/training_dataset_enriched.csv
data/processed/model_v2/
data/processed/*.png
notebooks/mlruns/
```

---

## 5. Roadmap y estado actual

### Fase MVP (2 ciudades: Málaga y París)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | fetch_cities.py — ingesta 7 fuentes | ✅ v7 |
| 2 | EDA — análisis exploratorio | ✅ notebook 01 |
| 3 | Perfiles sintéticos y pseudo-labeling | ✅ notebook 02 |
| 4 | LightGBM Ranker | ⏳ pendiente |
| 5 | SHAP explainability | ⏳ pendiente |
| 6 | MLflow tracking | ⏳ pendiente |
| 7 | FastAPI endpoint /recommend | ⏳ pendiente |
| 8 | Streamlit demo | ⏳ pendiente |
| 9 | Docker Compose | ⏳ pendiente |

### Problemas pendientes de fix

| Problema | Impacto | Prioridad |
|----------|---------|-----------|
| Numbeo key_prices vacío (key_map sin match) | ALTO — sin precios de alquiler | 🔴 Urgente |
| OSM hospitals Málaga = 0 (posible error etiquetado) | MEDIO — feature sanitaria | 🟡 Alta |
| Google Places API (New) no activada en GCloud | ALTO — 46 categorías sin datos | 🔴 Urgente |

---

## 6. Arquetipos de usuario (para contexto del modelo)

Los 8 arquetipos definidos en notebook 02:
- `nomada_digital` — coworking, internet, bajo coste, clima
- `familia_con_hijos` — colegios, guarderías, parques, seguridad
- `jubilado_activo` — clima cálido, playa, calidad de vida, bienestar
- `estudiante` — bajo coste, vida nocturna, universidad, transporte
- `ejecutivo_cosmopolita` — cultura, gastronomía premium, conectividad
- `deportista_outdoor` — playa, surf, marina, deporte
- `backpacker` — muy bajo coste, autenticidad, movilidad
- `familia_monoparental` — bajo coste, guardería, transporte sin coche

---

## 7. Convenciones de nomenclatura

### Prefijos de features
```
numbeo_    → datos de Numbeo (precios, índices)
weather_   → datos de wttr.in (clima)
osm_       → datos de OpenStreetMap (infraestructura)
gp_        → datos de Google Places (establecimientos)
speedtest_ → datos de Speedtest (internet)
country_   → datos de RestCountries (país)
user_      → features del perfil de usuario
city_      → features de ciudad en el dataset de entrenamiento
```

### Escala de relevancia del modelo
```
0 → Irrelevante
1 → Poco relevante
2 → Relevante
3 → Muy relevante
```

### Etiquetas del ERRORS_LOG
```
Categorías: [ENV] [VCS] [HTTP] [SCRAPING] [AUTH] [DATA] [CONFIG] [ML] [DB]
Subcategorías: [DEPS] [ENCODING] [RATE-LIMIT] [TIMEOUT] [MATCHING]
               [API-VERSION] [SECRETS] [BATCH] [USER-AGENT]
```

---

## 8. Comandos útiles del proyecto

```bash
# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Ejecutar ingesta de datos
python src/ingestion/fetch_cities.py

# Abrir Jupyter
jupyter notebook notebooks/

# Ver logs en tiempo real
Get-Content logs/ingestion.log -Wait  # PowerShell

# MLflow UI
mlflow ui

# Lanzar API (cuando esté lista)
uvicorn api.main:app --reload

# Lanzar Streamlit (cuando esté lista)
streamlit run app/streamlit_app.py
```

---

*Este archivo es la fuente de verdad del proyecto para Claude Code.*
*Actualízalo cuando cambien las instrucciones o la estructura del proyecto.*

---

## 9. Comportamiento automático — sin que el usuario tenga que pedírtelo

Estas acciones las haces SIEMPRE automáticamente como parte del trabajo:

### Después de crear o modificar un notebook
- Añade una sección nueva a LEARNING.md explicando desde cero qué hace ese notebook
- Explica cada concepto técnico como si fuera un profesor hablando a alguien que aprende
- Usa siempre el nombre técnico correcto
- Incluye: qué es el concepto, cómo lo usamos en NomadOptima, código de ejemplo, por qué esta decisión y no otra

### Después de detectar o resolver un error
- Añádelo inmediatamente a ERRORS_LOG.md con el formato establecido
- Si lo resuelves, marca el estado como Resuelto en el índice
- Incluye siempre la sección "Para recordar en una entrevista"

### Después de completar cualquier paso del roadmap
- Actualiza PROJECT_STATUS.md marcando ese paso como completado
- Actualiza el campo "Próximo paso" con el siguiente paso del roadmap
- Si aparece un problema nuevo, añádelo a la tabla de problemas pendientes

### Después de tomar una decisión de arquitectura
- Documéntala en LEARNING.md explicando por qué se eligió esa opción y no otra
- Actualiza la estructura del proyecto en este CLAUDE.md si cambia algo

REGLA DE ORO: nunca termines una tarea sin haber actualizado los tres archivos de memoria.

---

## 10. Estilo de los notebooks

Todos los notebooks del proyecto siguen este formato exacto:

Paso N: Título del paso
[celda de código]

OBSERVACIONES:
- Qué encontramos en los datos
- Qué significa cada resultado
- Qué es llamativo o inesperado

ANOTACIONES:
- Explicación del concepto técnico desde cero
- Por qué usamos esta función y no otra
- Qué significa cada parámetro importante

DECISIÓN: (cuando se toma una decisión)
- Qué decidimos hacer y por qué

DUDA: (cuando algo no está claro)
- Qué necesita investigación adicional

El usuario está aprendiendo Machine Learning. Nunca asumas conocimiento previo.
Explica siempre: qué hace el código, por qué lo hace así, y qué significa el resultado.

---

## 11. Perfil del usuario

- Nombre: Carlos
- Nivel: estudiante de bootcamp de Machine Learning
- Está aprendiendo mientras construye — necesita explicaciones desde cero
- El proyecto es su proyecto final del bootcamp y futuro producto comercial
- Las explicaciones deben servir también para preparar entrevistas técnicas
- Idioma: español siempre

---

*Este archivo es la fuente de verdad del proyecto para Claude Code.*
*Actualízalo cuando cambien las instrucciones o la estructura del proyecto.*

---

## 12. Arquitectura del sistema — 5 capas (CRÍTICO — leer antes de implementar cualquier modelo)

NomadOptima NO es solo LightGBM. Es un Hybrid Recommender System con 5 capas.
Implementar solo LightGBM sin las otras capas es incompleto.

### Capa 1 — Content-Based Filtering (baseline, funciona desde día 1)
- Algoritmo: Cosine Similarity
- Qué hace: cruza el vector de preferencias del usuario con las features de cada ciudad
- Por qué: funciona sin usuarios reales — resuelve el cold start total
- Librería: scikit-learn (cosine_similarity)
- Archivo: src/processing/features.py

### Capa 2 — User Clustering (no supervisado)
- Algoritmos: PCA → UMAP → HDBSCAN sobre perfiles de usuario
- Qué hace: agrupa usuarios similares en arquetipos (clusters)
- Por qué: transfiere conocimiento entre usuarios similares — resuelve cold start de usuario
- Librerías: scikit-learn, umap-learn, hdbscan
- Arquetipos esperados: nómada digital, familia con hijos, jubilado activo, deportista outdoor...
- Archivo: src/models/clustering.py

### Capa 3 — Item Clustering (no supervisado)
- Algoritmos: PCA → UMAP → HDBSCAN sobre features de ciudades
- Qué hace: agrupa ciudades similares entre sí
- Por qué: si un usuario eligió Tarifa, puede interesarle Gruissan (mismo cluster)
- Clusters esperados: costa kite atlántica, metrópoli cosmopolita, ciudad media cultural...
- Archivo: src/models/clustering.py (misma clase, distinto objeto)

### Capa 4 — LightGBM Ranker (orquestador)
- Algoritmo: LambdaMART (objective='lambdarank')
- Qué hace: combina señales de las 3 capas anteriores como features y produce el ranking final
- Features clave que recibe:
    cosine_similarity_perfil_ciudad   (Capa 1)
    user_cluster_id                   (Capa 2)
    user_cluster_strength             (Capa 2)
    city_cluster_id                   (Capa 3)
    city_cluster_strength             (Capa 3)
    afinidad_usercluster_citycluster  (interacción entre capas — feature más potente)
- Archivo: src/models/ranker.py

### Capa 5 — Output Layer: SHAP + MMR
- SHAP: explica por qué cada ciudad está en su posición del ranking
- MMR (Maximal Marginal Relevance): diversifica el top-N para evitar ciudades casi idénticas
- Archivo: src/models/explainer.py

### Pre-filtro — Restricciones duras (antes de cualquier capa)
Ciudades que no pasan estos filtros se eliminan antes de entrar al modelo:
- coste_vida > presupuesto_max * 1.15  → eliminada
- temp_media_anual < temp_min_usuario - 3  → eliminada
- tiene_coworking == False si usuario lo requiere  → eliminada
- permite_mascotas == False si usuario viaja con mascota  → eliminada

### Flujo completo
```
Usuario define perfil
    ↓
[Restricciones duras] — elimina incompatibles
    ↓
[Capa 1] Cosine Similarity — baseline
[Capa 2] UMAP+HDBSCAN — user cluster
[Capa 3] UMAP+HDBSCAN — city cluster
    ↓
[Capa 4] LightGBM LambdaMART — ranking final
    ↓
[Capa 5a] SHAP — explicación
[Capa 5b] MMR — diversificación
    ↓
Top-N ciudades con justificación
```

### Fase 3 — Travel Optimizer (meses 5-6, post-MVP)
Cuando el City Matcher esté listo se añaden:
- Activity Selector: Knapsack / Programación Dinámica
- Route Optimizer: TSP con OR-Tools (Google)
- Itinerary Diversifier: Simulated Annealing
- Collaborative Filter: Matrix Factorization ALS (cuando haya usuarios reales)

### Orden de implementación correcto
1. src/processing/features.py — Cosine Similarity baseline (Capa 1)
2. src/models/clustering.py — User Clustering + Item Clustering (Capas 2 y 3)
3. src/models/ranker.py — LightGBM con features de todas las capas (Capa 4)
4. src/models/explainer.py — SHAP + MMR (Capa 5)
5. api/main.py — FastAPI /recommend endpoint
6. app/streamlit_app.py — demo visual

El notebook 03 implementa SOLO la Capa 4 con pseudo-labels directos.
Las Capas 1, 2 y 3 están pendientes de implementar en src/models/.
