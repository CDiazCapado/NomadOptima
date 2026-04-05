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
nomadoptima/
├── CLAUDE.md              ← este archivo (instrucciones para Claude Code)
├── PROJECT_STATUS.md      ← estado actual del proyecto
├── LEARNING.md            ← cuaderno de aprendizaje acumulativo
├── ERRORS_LOG.md          ← registro de errores y soluciones
├── .env                   ← API keys (NUNCA modificar ni leer el contenido)
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/               ← JSONs de fetch_cities.py
│   └── processed/         ← datasets procesados para el modelo
├── notebooks/
│   ├── 01_eda_malaga_paris.ipynb
│   ├── 02_synthetic_profiles.ipynb
│   └── 03_lightgbm_ranker.ipynb   ← pendiente
├── src/
│   ├── ingestion/
│   │   └── fetch_cities.py        ← v7 actual
│   ├── processing/
│   │   ├── features.py            ← pendiente
│   │   └── normalize.py           ← pendiente
│   └── models/
│       ├── clustering.py          ← pendiente
│       ├── ranker.py              ← pendiente
│       └── explainer.py           ← pendiente
├── api/
│   └── main.py                    ← pendiente
├── app/
│   └── streamlit_app.py           ← pendiente
├── logs/
│   ├── ingestion.log              ← generado automáticamente
│   └── ingestion_structured.jsonl ← generado automáticamente
└── mlruns/                        ← generado por MLflow
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
