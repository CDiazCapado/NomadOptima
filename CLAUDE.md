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
│       ├── user_profiles.csv          ← 5.000 perfiles × 26 dims — output notebook 02
│       ├── training_dataset.csv       ← 270k filas × 175 features — output notebook 03 (etiquetas por producto escalar)
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

### Fase MVP — estado real a 09/04/2026

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | fetch_cities.py — ingesta 6 fuentes, 36+ ciudades | ✅ v9 |
| 2a | EDA datos crudos (Fase 1) — revisar fuentes, features, decisiones | ⏳ pendiente |
| 2b | EDA ciudades completo (Fase 2) — gráficos estándar con notas educativas | ⏳ pendiente |
| 2c | EDA arquetipos (Fase 3) — validar diferenciación entre los 21 arquetipos | ⏳ pendiente |
| 2d | EDA perfiles sintéticos (Fase 4) — validar distribuciones generadas | ⏳ pendiente |
| 3 | Perfiles sintéticos — notebook 02_v3 (arquetipos actualizados, pendiente ejecutar) | ⏳ pendiente ejecutar |
| 4 | LightGBM Ranker — notebook 03_train_model | ⏳ pendiente |
| 5 | SHAP explainability | ⏳ pendiente |
| 6 | MLflow tracking | ⏳ pendiente |
| 7 | FastAPI endpoint /recommend | ⏳ pendiente |
| 8 | Streamlit demo | ⏳ pendiente |
| 9 | Docker Compose | ⏳ pendiente |

**REGLA CRÍTICA para el EDA:** avanzar UNA FASE a la vez. No pasar a la siguiente sin consultar a Carlos y recibir aprobación explícita.

### Problemas pendientes de fix

| Problema | Impacto | Prioridad |
|----------|---------|-----------|
| Numbeo key_prices vacío (key_map sin match) | ALTO — sin precios de alquiler | 🔴 Urgente |
| OSM hospitals Málaga = 0 (posible error etiquetado) | MEDIO — feature sanitaria | 🟡 Alta |
| Google Places API (New) no activada en GCloud | ALTO — 46 categorías sin datos | 🔴 Urgente |

---

## 6. Arquetipos de usuario (para contexto del modelo)

**VERSIÓN ACTUAL (v2): 21 arquetipos** definidos en `ARQUETIPOS_REVISION.md` y cargados en `notebooks/02_synthetic_profiles_v3.ipynb` celda `57fea91a`.
Los arquetipos se puntúan en 26 dimensiones `user_imp_*`. Los % suman ~86% (14% mixtos).
Escalado proporcional aplicado (Opción A): porcentajes originales sumaban 106%, escalados a 86%.

| Nombre | pct | Dimensiones HIGH |
|--------|-----|-----------------|
| `kite_surf` | 4.87% | deporte_agua, naturaleza, clima |
| `deportista_outdoor` | 4.87% | naturaleza, deporte_montana, deporte_urbano, clima |
| `ski_nieve` | 3.25% | deporte_montana, naturaleza |
| `nomada_barato` | 6.49% | nomada, coste, calidad_vida |
| `nomada_premium` | 4.87% | nomada, calidad_vida, gastronomia, deporte_urbano |
| `nomada_mujer_activa` | 4.06% | nomada, bienestar, deporte_urbano, comunidad |
| `cultura_arte` | 5.68% | cultura, arte_visual, turismo, gastronomia |
| `musico_festivales` | 3.25% | musica, cultura, vida_nocturna, comunidad |
| `gastronomia_vino` | 4.06% | gastronomia, autenticidad, turismo |
| `antiturístico` | 4.06% | autenticidad, gastronomia, naturaleza |
| `influencer` | 3.25% | social_media, turismo, vida_nocturna, gastronomia |
| `familia_bebe` | 3.25% | familia, salud, movilidad, calidad_vida |
| `familia_ninos` | 4.87% | familia, educacion, salud, movilidad, calidad_vida |
| `fiesta_social` | 4.06% | vida_nocturna, musica, social_media, gastronomia |
| `bienestar_retiro` | 4.06% | bienestar, naturaleza, clima, calidad_vida |
| `jubilado_activo` | 4.87% | clima, calidad_vida, salud, bienestar, gastronomia |
| `senior_accesibilidad` | 2.43% | salud, calidad_vida, servicios, movilidad, clima |
| `mochilero_barato` | 4.06% | coste, autenticidad, naturaleza, movilidad |
| `cosmopolita_urbano` | 4.06% | cultura, gastronomia, movilidad, calidad_vida |
| `gamer_nomada_tech` | 3.25% | nomada, calidad_vida, comunidad |
| `mascotas_naturaleza` | 2.43% | mascotas, naturaleza, bienestar, calidad_vida |

Ver detalle completo de dimensiones MEDIUM/LOW en `ARQUETIPOS_REVISION.md`.

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

### REGLA CRÍTICA — separación de responsabilidades entre notebooks
- **Notebook 02:** genera ÚNICAMENTE los perfiles de usuario sintéticos.
  Output: `user_profiles.csv` — 5.000 filas × (26 dims user_imp_* + archetype).
  NO cruza con ciudades. NO genera etiquetas. NO produce training_dataset.
- **Notebook 03:** es responsable del cruce, las etiquetas y el entrenamiento.
  Carga user_profiles.csv + city_features.csv, cruza 5.000 × 54 = 270.000 pares,
  genera etiquetas, construye el feature vector completo y entrena LightGBM.

### REGLA CRÍTICA — origen de las etiquetas (labels)
Las etiquetas NO se generan con cosine_sim. Esto sería circular porque cosine_sim
también es una feature del modelo — el modelo solo aprendería a copiarse a sí mismo.

Las etiquetas se generan con **producto escalar directo**:
```
score = Σ (user_imp_dim_i × city_feature_dim_i)   para cada dimensión i
```
Se rankean las 54 ciudades por score para cada usuario.
Top 10% → label 3 | Top 30% → label 2 | Top 60% → label 1 | Resto → label 0

Este score inicial es transparente, justificable y no circular.

### Capa 1 — Content-Based Filtering (señal de apoyo para el ranker)
- Algoritmo: Cosine Similarity
- Qué hace: calcula similitud normalizada entre el perfil del usuario y cada ciudad
- Rol en el sistema: es UNA feature más que recibe LambdaRank — no la fuente de verdad
- Por qué incluirla como feature: da al modelo un "resumen" de encaje global que acelera
  el aprendizaje. El modelo puede refinarla o ignorarla según lo que aprenda.
- Por qué NO usarla como fuente de etiquetas: sería circular (labels = cosine_sim, feature = cosine_sim)
- Librería: scikit-learn (cosine_similarity)
- Archivo: src/processing/features.py

### Capa 2 — User Clustering (no supervisado)
- Algoritmos: PCA → UMAP → HDBSCAN sobre los 5.000 perfiles sintéticos
- Qué hace: agrupa perfiles similares en clusters
- Por qué: con suficientes perfiles (5.000), HDBSCAN es fiable y encuentra clusters naturales
- Arquetipos esperados: nómada digital, familia con hijos, jubilado activo, deportista outdoor...
- Archivo: src/models/clustering.py

### Capa 3 — Item Clustering (no supervisado, limitado)
- Algoritmos: simplificado — con solo 54 ciudades HDBSCAN no es fiable (pocos puntos)
- Qué hace: agrupa ciudades similares entre sí con clustering manual o k-means simple
- Limitación conocida: con 54 ciudades los clusters son orientativos, no estadísticamente robustos
- Mejora futura: cuando haya 200+ ciudades, migrar a UMAP+HDBSCAN automático
- Archivo: src/models/clustering.py

### Capa 4 — LightGBM Ranker (orquestador)
- Algoritmo: LambdaMART (objective='lambdarank')
- Qué hace: aprende correlaciones no lineales entre pesos de usuario y features de ciudad
- Por qué añade valor sobre cosine_sim: puede descubrir que user_imp_naturaleza importa
  más cuando también user_imp_clima es alto, o que ciertos tipos de infraestructura urbana
  pesan más de lo que el producto escalar simple indicaría
- Features que recibe (175 en total):
    user_imp_* × 26        (preferencias del usuario — dims puras)
    city_features_* × 148  (features brutas de la ciudad)
    cosine_sim × 1         (señal de apoyo — resumen normalizado del encaje global)
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
[Notebook 02] user_profiles.csv — 5.000 perfiles × 26 dims (SIN ciudades)
                    +
              city_features.csv — 54 ciudades × 148 features
                    ↓
[Notebook 03 — paso 1] Cruce: 5.000 × 54 = 270.000 pares (usuario, ciudad)
[Notebook 03 — paso 2] Labels: producto escalar directo → rank → label 0-3
[Notebook 03 — paso 3] Features: [user_imp_*(26) + city_features_*(148) + cosine_sim(1)]
[Notebook 03 — paso 4] LightGBM LambdaMART — aprende correlaciones no lineales
                    ↓
[Producción — inferencia]
Usuario define perfil
    ↓
[Restricciones duras] — elimina incompatibles
    ↓
[Capa 1] cosine_sim — feature de apoyo
[Capa 2] user cluster — feature de contexto
[Capa 3] city cluster — feature de contexto (limitado con 54 ciudades)
    ↓
[Capa 4] LightGBM LambdaMART — ranking final con 175 features
    ↓
[Capa 5a] SHAP — explicación
[Capa 5b] MMR — diversificación
    ↓
Top-N ciudades con justificación
```

### Nota para la presentación (beta(3,6) en perfiles sintéticos)
La función generate_archetype_profile() usa beta(3,6) para dimensiones MEDIUM,
que da media ~0.33 en vez de 0.50. Esto significa que HIGH(0.80) y MEDIUM(0.33)
están bien separados, pero MEDIUM(0.33) y LOW(0.08) tienen menos margen.
Mejora futura: cambiar beta(3,6) → beta(4,4) para MEDIUM (media=0.50).
Decisión tomada: dejarlo así para el MVP — LightGBM es suficientemente robusto.

### Fase 3 — Travel Optimizer (meses 5-6, post-MVP)
Cuando el City Matcher esté listo se añaden:
- Activity Selector: Knapsack / Programación Dinámica
- Route Optimizer: TSP con OR-Tools (Google)
- Itinerary Diversifier: Simulated Annealing
- Collaborative Filter: Matrix Factorization ALS (cuando haya usuarios reales)

### Orden de implementación correcto
1. src/processing/features.py — CityFeatureBuilder + cosine_sim como feature (Capa 1)
2. notebooks/02 — SOLO perfiles sintéticos → user_profiles.csv
3. src/models/clustering.py — User Clustering (Capa 2) + City Clustering simplificado (Capa 3)
4. notebooks/03 — cruce + labels (producto escalar) + entrenamiento LightGBM (Capa 4)
5. src/models/explainer.py — SHAP + MMR (Capa 5)
6. api/main.py — FastAPI /recommend endpoint
7. app/streamlit_app.py — demo visual

---

## 13. Historial de conversaciones — cómo recuperar contexto perdido

### Dónde están los archivos de conversación
Claude Code guarda cada sesión como un archivo `.jsonl` en:
```
C:\Users\cri\.claude\projects\D--Proyectos-4geeks-Proyecto-Final-nomadoptima\
  2f1e93fa-9d77-4d0c-87e5-1dca62a323bc.jsonl  ← sesión principal (29MB, ~5000 líneas)
  e8bb7023-89b3-480b-a2c2-508da9190763.jsonl
  e1be5662-aeed-4a24-bc87-78ab18008b75.jsonl
```

### Cómo exportarlos a formato legible
```bash
cd "d:\Proyectos\4geeks\Proyecto Final\nomadoptima"
.venv\Scripts\activate
python scripts/export_conversation.py
```

Genera dos tipos de archivo:
- **HTML completo** → `data/processed/conversations/conversacion_<id>.html` — para que Carlos relea la conversación entera con Ctrl+F
- **MD de decisiones** → `memory/decisions_log_<id>.md` — condensado con solo las decisiones importantes, para que Claude lo lea al iniciar una sesión nueva

### Cuándo ejecutar este script
- Al inicio de una sesión nueva tras una sesión interrumpida
- Cuando Carlos diga "no recuerdo qué decidimos sobre X"
- Cuando Claude necesite contexto de decisiones de arquitectura no documentadas en PROJECT_STATUS.md

### Qué hacer al inicio de sesión si hay decisions_log en memory/
Leer los archivos `memory/decisions_log_*.md` además de PROJECT_STATUS.md y LEARNING.md.
Estos archivos contienen decisiones de sesiones anteriores que pueden no estar aún en los docs principales.

---

## 14. Plan de EDA — estructura y reglas (CRITICO — leer antes de tocar notebooks)

El EDA de NomadOptima tiene proposito DOBLE: cientifico (validar datos para el modelo)
y DOCENTE (mostrar el proceso de ML a una audiencia que aprende).

### Regla de avance: UNA FASE A LA VEZ
No avanzar a la siguiente fase sin consultar a Carlos y recibir aprobacion explicita.
Cada fase es un bloque autonomo que se aprueba antes de iniciar el siguiente.

---

### Fase 1 — EDA de datos crudos (historico de decisiones)
> "De donde vienen los datos y que decisiones tomo Carlos sobre las features?"

Notebook: revisar/ampliar `01_eda_36ciudades.ipynb`

Contenido:
- Tabla de las 6 fuentes de datos y que aporta cada una (gp_, numbeo_, osm_, weather_, speedtest_, country_)
- Cuantas features entro cada fuente al principio vs. cuantas quedaron
- Decisiones de Carlos: que se incluyo, que se descarto y por que (documentadas en LEARNING.md)
- Grafico: bar chart "features por fuente" con nota explicativa

---

### Fase 2 — EDA del dataset completo de ciudades
> "Que nos dicen los datos reales de las 36+ ciudades?"

Notebook: revisar/ampliar `01_eda_36ciudades.ipynb`

Graficos estandar para datos de comparacion entre entidades (cada uno con NOTA AL PIE):

| Grafico | Para que sirve | Nota al pie incluye |
|---------|---------------|---------------------|
| describe() + tabla resumen | Estadisticas basicas (media, std, min/max) | Que es cada estadistico |
| Missing data heatmap | Detectar features vacias por ciudad | Que significa un cero en este dataset |
| Histogramas + KDE por feature | Distribucion de cada feature | Que es KDE, que nos dice la forma |
| Box plots agrupados por categoria | Variabilidad entre ciudades | Que es un boxplot, que es un outlier |
| Violin plots | Distribucion + densidad simultaneas | Diferencia con boxplot |
| Heatmap correlaciones (Pearson) | Features redundantes | Que es correlacion, multicolinealidad |
| Scatter plot coste vs calidad | Relacion precio-valor | Por que este par es importante |
| Heatmap ciudad x feature (normalizado 0-1) | Separabilidad entre ciudades | Que pasaria si todo fuera igual |
| Radar charts (5-6 ciudades clave) | Perfil multidimensional comparado | Que es un radar chart |
| PCA biplot | Que features separan mas las ciudades | Que es PCA, que es un biplot |
| Parallel coordinates plot | Ver todas las dimensiones a la vez | Cuando usar este grafico |

NOTA EN CADA GRAFICO (formato estandar en el notebook):
```
PARA QUE SIRVE ESTE GRAFICO:
<explicacion del tipo de grafico desde cero>

QUE NOS ESTA MOSTRANDO PARA NUESTROS DATOS:
<interpretacion especifica de lo que vemos>

DECISION/IMPLICACION PARA EL MODELO:
<que hacemos con esta informacion>
```

---

### Fase 3 — EDA de Arquetipos
> "Los 21 arquetipos estan bien diferenciados entre si?"

Notebook nuevo: `01b_eda_arquetipos.ipynb`

Contenido:
- Heatmap 21 arquetipos x 26 dimensiones (high=0.85, medium=0.50, low=0.10)
- Radar charts para cada arquetipo (o grupos de arquetipos similares)
- Mapa de similitud entre arquetipos (cosine similarity entre perfiles)
- Pregunta clave: hay arquetipos demasiado parecidos que el modelo confundira?

---

### Fase 4 — EDA de Perfiles Sinteticos
> "Los 5.000 perfiles generados tienen sentido estadistico?"

Notebook nuevo: `01c_eda_perfiles_sinteticos.ipynb`
Depende de: notebook 02_v3 ejecutado (genera los 5.000 perfiles)

Contenido:
- Distribucion de cada dimension en los 5.000 perfiles (histogramas)
- Visualizacion UMAP/PCA de los perfiles coloreados por arquetipo
- Validacion spot-check: kite_surf debe tener deporte_agua > 0.75 en la media

---

### Notebooks implicados

| Notebook | Fase | Estado |
|----------|------|--------|
| `01_eda_36ciudades.ipynb` | Fases 1 + 2 | Existe parcialmente — revisar y ampliar |
| `01b_eda_arquetipos.ipynb` | Fase 3 | No existe — crear |
| `01c_eda_perfiles_sinteticos.ipynb` | Fase 4 | No existe — crear (depende de 02_v3) |

---

### Estado actual del EDA (09/04/2026)
- Fase 1: PENDIENTE — aprobada por Carlos, no ejecutada
- Fase 2: PENDIENTE — aprobada por Carlos, no ejecutada
- Fase 3: PENDIENTE — esperando aprobacion de Carlos tras Fase 2
- Fase 4: PENDIENTE — esperando aprobacion de Carlos tras Fase 3

**Siguiente accion: esperar instruccion de Carlos para iniciar Fase 1.**
