# NomadOptima — Motor de Matching Ciudad-Perfil de Vida

NomadOptima es un **Hybrid Recommender System** formulado como **Learning to Rank** que recomienda ciudades del mundo según el perfil de vida del usuario.

El sistema no responde a la pregunta "¿qué ciudad es mejor?", sino a "¿qué ciudad encaja mejor contigo?". Combina cinco capas algorítmicas: filtrado basado en contenido, clustering de usuarios, clustering de ciudades, un ranker LightGBM LambdaMART y una capa de explicabilidad con SHAP.

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje | Python | 3.12.10 |
| Modelo de ranking | LightGBM | 4.6.0 |
| Explicabilidad | SHAP | 0.51.0 |
| Experimentos | MLflow | 3.10.1 |
| API REST | FastAPI | 0.135.2 |
| Demo visual | Streamlit | 1.55.0 |
| Base de datos | PostgreSQL | — |
| Contenedores | Docker | — |
| Clustering | HDBSCAN + UMAP | — |
| Reducción dimensional | scikit-learn (PCA) | 1.8.0 |

---

## Arquitectura del sistema — 5 capas

```
Usuario define perfil (26 dimensiones de preferencias)
    |
    v
[Pre-filtro] Restricciones duras (presupuesto, clima mínimo, coworking, mascotas)
    |
    v
[Capa 1] Content-Based Filtering — cosine_similarity entre perfil y ciudad
[Capa 2] User Clustering — PCA + UMAP + HDBSCAN sobre 5.000 perfiles
[Capa 3] City Clustering — agrupación de ciudades similares
    |
    v
[Capa 4] LightGBM LambdaMART — ranking con 175 features
    |
    v
[Capa 5] SHAP (explicación) + MMR (diversificación del top-N)
    |
    v
Top-N ciudades con justificación por dimensión
```

### Descripción de cada capa

**Capa 1 — Content-Based Filtering**
Calcula la similitud del coseno entre el vector de preferencias del usuario (26 dimensiones) y el vector de features de cada ciudad (148 features). Actúa como señal de apoyo para el ranker, no como fuente de etiquetas.

**Capa 2 — User Clustering**
Agrupa los 5.000 perfiles sintéticos con PCA → UMAP → HDBSCAN. Permite al modelo generalizar por tipo de viajero: nómada digital, familia con hijos, jubilado activo, deportista outdoor, etc.

**Capa 3 — City Clustering**
Agrupa las 54 ciudades por similitud de features. Con 54 ciudades los clusters son orientativos; se migrará a UMAP+HDBSCAN automático cuando haya 200+ ciudades.

**Capa 4 — LightGBM LambdaMART**
Aprende correlaciones no lineales entre las preferencias del usuario y las características de las ciudades. Recibe 175 features: 26 preferencias de usuario + 148 features de ciudad + 1 cosine_sim. Resultado actual: **NDCG@5 = 0.9631**, 43 árboles, 54 ciudades.

**Capa 5 — SHAP + MMR**
SHAP explica por qué cada ciudad ocupa su posición en el ranking. MMR (Maximal Marginal Relevance) diversifica el top-N para evitar recomendar ciudades casi idénticas.

---

## Fuentes de datos

| Fuente | Qué aporta | Prefijo de features |
|--------|-----------|---------------------|
| Google Places New API | Establecimientos por tipo en radio urbano (~150 tipos) | `gp_` |
| Numbeo | Coste de vida, precios, índices de calidad | `numbeo_` |
| OpenStreetMap (Overpass) | Infraestructura urbana etiquetada | `osm_` |
| wttr.in | Clima puntual | `weather_` |
| Speedtest (Ookla) | Velocidad de internet por país | `speedtest_` |
| RestCountries | Idioma, zona horaria, espacio Schengen, UE | `country_` |

---

## Requisitos previos

- Python 3.12
- pip
- virtualenv (incluido en Python 3.12 con `venv`)
- Git

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/CDiazCapado/NomadOptima.git
cd NomadOptima
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

El repositorio no incluye el archivo `.env` porque contiene API keys reales. Crea uno en la raíz del proyecto:

```bash
cp .env.example .env
```

Abre `.env` y rellena las siguientes claves:

```
GOOGLE_PLACES_API_KEY=tu_clave_aqui
NUMBEO_API_KEY=tu_clave_aqui
```

> El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.

---

## Datos necesarios

Para que la app y el modelo funcionen se necesitan dos artefactos que no están incluidos en el repositorio (están en `.gitignore` por su tamaño):

| Archivo | Descripción |
|---------|-------------|
| `data/processed/city_features.csv` | 54 ciudades × 149 features — generado por `src/processing/features.py` |
| `data/processed/model_v3/` | 4 artefactos del modelo entrenado (lgbm_ranker_v3.txt, feature_builder_v3.joblib, feature_cols_v3.json, model_metrics_v3.json) |

### Cómo generarlos desde cero

Ejecutar los notebooks en orden:

```bash
# Abrir Jupyter
jupyter notebook notebooks/

# Ejecutar en este orden:
# 1. notebooks/01_eda_ciudades.ipynb       — EDA y validación de datos
# 2. notebooks/02_synthetic_profiles_v3.ipynb  — genera user_profiles.csv
# 3. notebooks/03_train_model.ipynb        — entrena LightGBM, genera model_v3/
```

Alternativamente, ejecutar la ingesta de datos primero:

```bash
python src/ingestion/fetch_cities.py
```

> La ingesta llama a Google Places API y Numbeo, que tienen coste por petición. Revisar los límites antes de ejecutar.

---

## Cómo arrancar la app

```bash
streamlit run app/streamlit_app.py
```

La app se abre en `http://localhost:8501`.

El usuario define su perfil en 20 categorías y el sistema devuelve un ranking de ciudades con puntuación y justificación por dimensión.

Si los artefactos de `model_v3/` no están disponibles, la app cae al modo de fallback con cosine similarity.

---

## Estructura del proyecto

```
nomadoptima/
├── data/
│   ├── raw/                        <- JSONs de ingesta (en .gitignore)
│   └── processed/
│       ├── city_features.csv       <- 54 ciudades × 149 features
│       ├── user_profiles.csv       <- 5.000 perfiles × 26 dims
│       ├── training_dataset.csv    <- 270.000 filas × 177 cols (en .gitignore)
│       └── model_v3/               <- artefactos del modelo (en .gitignore)
│
├── notebooks/
│   ├── 01_eda_ciudades.ipynb       <- EDA Fase 1 — fuentes y decisiones
│   ├── 01b_eda_fase2_ciudades.ipynb <- EDA Fase 2 — análisis completo
│   ├── 01b_eda_arquetipos.ipynb    <- EDA Fase 3 — validación arquetipos
│   ├── 01c_eda_perfiles_sinteticos.ipynb <- EDA Fase 4 — validación perfiles
│   ├── 02_synthetic_profiles_v3.ipynb   <- generación de perfiles sintéticos
│   └── 03_train_model.ipynb        <- entrenamiento LightGBM
│
├── src/
│   ├── ingestion/
│   │   └── fetch_cities.py         <- ingesta 6 APIs, 54 ciudades
│   ├── processing/
│   │   └── features.py             <- CityFeatureBuilder + cosine_sim (Capa 1)
│   └── models/
│       ├── clustering.py           <- UserClusterer + CityClusterer (Capas 2+3)
│       ├── ranker.py               <- NomadRanker LightGBM (Capa 4)
│       └── explainer.py            <- SHAP + MMR (Capa 5, pendiente)
│
├── app/
│   ├── streamlit_app.py            <- demo visual conectada a LightGBM
│   └── city_content.py             <- contenido editorial de 54 ciudades
│
├── api/
│   └── main.py                     <- FastAPI /recommend (pendiente)
│
├── scripts/                        <- herramientas auxiliares
├── requirements.txt
└── .env                            <- API keys (NO incluido en el repo)
```

---

## Resultados del modelo

| Métrica | Valor |
|---------|-------|
| NDCG@5 | **0.9631** |
| Árboles | 43 |
| Features de entrada | 175 |
| Ciudades en el catálogo | 54 |
| Perfiles de entrenamiento | 5.000 |
| Pares de entrenamiento | 270.000 |

---

## Comandos útiles

```bash
# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Ingesta de datos de las 54 ciudades
python src/ingestion/fetch_cities.py

# Abrir notebooks
jupyter notebook notebooks/

# MLflow — revisar experimentos
mlflow ui

# API REST (cuando esté lista)
uvicorn api.main:app --reload

# Demo visual
streamlit run app/streamlit_app.py
```

---

## Roadmap

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | Ingesta de datos — 6 fuentes, 54 ciudades | Completado |
| 2 | EDA — 4 fases (datos, ciudades, arquetipos, perfiles) | Completado |
| 3 | Perfiles sintéticos — 5.000 perfiles × 26 dimensiones | Completado |
| 4 | LightGBM Ranker — NDCG@5=0.9631 | Completado |
| 5 | SHAP explicabilidad | Pendiente |
| 6 | MLflow tracking | Pendiente |
| 7 | FastAPI endpoint /recommend | Pendiente |
| 8 | Streamlit demo conectada | Completado (v3) |
| 9 | Docker Compose | Pendiente |

---

## Autor

Carlos Díaz Capado — Proyecto final del bootcamp de Machine Learning, 4Geeks Academy.

Repositorio: [github.com/CDiazCapado/NomadOptima](https://github.com/CDiazCapado/NomadOptima)
