# NomadOptima — Cuaderno de Errores y Soluciones

**Proyecto:** NomadOptima — Motor de Matching Ciudad-Perfil de Vida
**Autor:** Carlos Díaz Capado
**Repositorio:** github.com/CDiazCapado/NomadOptima

Este documento registra cronológicamente todos los errores encontrados durante
el desarrollo del proyecto, con su diagnóstico técnico, causa raíz y solución.

Está pensado con dos objetivos:
1. **Depuración**: poder volver a cualquier error pasado y recordar exactamente
   qué ocurrió y cómo se resolvió.
2. **Entrevistas técnicas**: cada error incluye una explicación del concepto
   técnico detrás del problema, con el nombre correcto que usaría un desarrollador
   profesional al describirlo.

---

## Sistema de etiquetas

Cada error tiene etiquetas en dos niveles:

### Categoría principal
| Etiqueta | Qué significa |
|---|---|
| `[ENV]` | **Environment** — problemas con el entorno de desarrollo: Python, dependencias, rutas, configuración local |
| `[VCS]` | **Version Control System** — problemas con Git, GitHub, control de versiones |
| `[HTTP]` | **HTTP / Networking** — errores en llamadas a APIs externas: códigos de estado, autenticación, rate limits |
| `[SCRAPING]` | **Web Scraping** — extracción de datos de páginas web: HTML, selectores, parsing |
| `[AUTH]` | **Authentication / Authorization** — problemas con API keys, tokens, permisos |
| `[DATA]` | **Data Quality** — problemas con la calidad, formato o estructura de los datos extraídos |
| `[CONFIG]` | **Configuration** — problemas con archivos de configuración, variables de entorno, secrets |
| `[ML]` | **Machine Learning** — problemas con modelos, features, entrenamiento, métricas |
| `[DB]` | **Database** — problemas con base de datos, queries, esquemas |

### Subcategoría
| Etiqueta | Qué significa |
|---|---|
| `[DEPS]` | Dependencies — dependencias Python no instaladas |
| `[ENCODING]` | Encoding — problemas con codificación de caracteres (UTF-8, ASCII, URL encoding) |
| `[RATE-LIMIT]` | Rate Limit — el servidor externo ha bloqueado las peticiones por exceso de velocidad |
| `[TIMEOUT]` | Timeout — la petición tardó demasiado y fue cancelada |
| `[MATCHING]` | String Matching — problemas al buscar o comparar texto |
| `[API-VERSION]` | API Version — conflicto entre versiones de una API externa |
| `[SECRETS]` | Secrets Management — gestión de claves y credenciales sensibles |
| `[BATCH]` | Batch Processing — procesamiento en lote vs peticiones individuales |
| `[USER-AGENT]` | User-Agent — identificación del cliente HTTP en la cabecera de la petición |

---

## Índice de errores

| # | Fecha | Error resumido | Categoría | Subcategoría | Estado |
|---|-------|---------------|-----------|--------------|--------|
| 1 | 20/03/2026 | `ModuleNotFoundError: No module named 'requests'` | `[ENV]` | `[DEPS]` | ✅ Resuelto |
| 2 | 20/03/2026 | `.gitignore` en carpeta incorrecta — `.env` expuesto | `[VCS]` `[CONFIG]` | `[SECRETS]` | ✅ Resuelto |
| 3 | 20/03/2026 | `403 Forbidden` en Wikipedia REST API | `[HTTP]` `[AUTH]` | `[ENCODING]` `[USER-AGENT]` | ✅ Resuelto |
| 4 | 20/03/2026 | `429 Too Many Requests` y `504 Gateway Timeout` en Overpass (OSM) | `[HTTP]` | `[RATE-LIMIT]` `[TIMEOUT]` `[BATCH]` | ✅ Resuelto |
| 5 | 20/03/2026 | `0 key prices` en scraping de Numbeo | `[SCRAPING]` `[DATA]` | `[MATCHING]` | ⚠️ Fix incompleto — ver #7 |
| 6 | 20/03/2026 | `46 errores, 0 lugares` en Google Places API (New) | `[HTTP]` `[AUTH]` | `[API-VERSION]` | ✅ Resuelto |
| 7 | 01/04/2026 | Fix incompleto en `key_map`: `)` del formato antiguo y substring no contiguo en `transport_monthly` | `[SCRAPING]` `[DATA]` | `[MATCHING]` | ✅ Resuelto en v8 |
| 8 | 01/04/2026 | Google Places trunca a 20 resultados por categoría — sin paginación ni offsets geográficos | `[HTTP]` `[DATA]` | `[API-VERSION]` | ✅ Resuelto en v9 |
| 9 | 30/03/2026 | Porto `fixed_download_mbps` = null — `dict.get()` no protege contra None explícito | `[DATA]` | `[MATCHING]` | ✅ Resuelto notebook 02 |
| 10 | 06/04/2026 | Features de idioma binarias no capturan la realidad lingüística — Porto habla portugués, inglés no modelado | `[DATA]` `[DESIGN]` | `[MATCHING]` | ⏳ Solución parcial — pesos manuales |
| 11 | 06/04/2026 | Cards de interés genéricas — Málaga siempre gana por dominancia de `city_gp_hiking` (gain 89.286) | `[ML]` `[UX]` | — | ⏳ Rediseño scoring en curso |
| 12 | 06/04/2026 | HTML crudo en `st.markdown()` renderiza como texto plano — CSS no aplicado | `[UX]` | — | ⏳ Pendiente refactor a componentes nativos |
| 13 | 06/04/2026 | Diseño con tabs es antinatural para una elección de flujo — confunde navegación con decisión | `[UX]` | — | ✅ Rediseñado a flujo de elección con botones |
| 14 | 06/04/2026 | `searchNearby` sin `includedTypes` devuelve 0 para types de infraestructura — sesgo de popularidad | `[HTTP]` `[DATA]` | `[API-VERSION]` | ✅ Resuelto — búsquedas dirigidas |
| 15 | 06/04/2026 | `UnicodeEncodeError` al imprimir `✓` en terminal Windows CP1252 | `[ENV]` | `[ENCODING]` | ✅ Resuelto — `PYTHONUTF8=1` |
| 16 | 08/04/2026 | Pseudo-labels circulares — el modelo aprende nuestras reglas, no la realidad | `[ML]` `[DATA]` | — | ✅ Rediseñado notebook 02 |
| 17 | 08/04/2026 | Arquetipos fijos generan perfiles sintéticos demasiado rígidos | `[ML]` `[DATA]` | — | ✅ Rediseñado a 24 dimensiones libres |
| 18 | 08/04/2026 | Budapest rent_1br_center = 343.396€ — moneda local HUF no convertida a EUR | `[DATA]` | `[MATCHING]` | ✅ Resuelto — diccionario EUR_RATES + función to_eur() |
| 19 | 08/04/2026 | Numbeo HTTP 429 Rate Limit para 12 ciudades | `[HTTP]` | `[RATE-LIMIT]` | ⚠️ Solución temporal — NUMBEO_FALLBACK hardcodeado |
| 20 | 08/04/2026 | Buenos Aires siempre en top 3 para cualquier perfil — coste = 0 → coste_invertido = 1.0 | `[ML]` `[DATA]` | `[MATCHING]` | ✅ Resuelto — añadida a NUMBEO_FALLBACK |
| 21 | 08/04/2026 | Fuerteventura label=0 siempre — OSM Overpass falla en islas, todos features OSM = 0 | `[DATA]` `[ML]` | — | ✅ Resuelto — GP genérico como fallback + capping |
| 22 | 08/04/2026 | Warsaw #1 para perfiles kite/windsurf — dimensión deporte genérica incluye gimnasios urbanos | `[ML]` | — | ✅ Resuelto — split deporte en 3 sub-dimensiones |
| 23 | 08/04/2026 | `background_gradient()` falla en columna de texto `city_idioma_nativo` | `[DATA]` `[ENV]` | — | ✅ Resuelto — `subset=num_cols` en Styler |
| 24 | 08/04/2026 | `UnicodeEncodeError` al imprimir `[OK]` con checkmark en features.py (Windows CP1252) | `[ENV]` | `[ENCODING]` | ✅ Resuelto — reemplazado con `[OK]` |
| 25 | 08/04/2026 | Celdas de notebook sin IDs — NotebookEdit fallaba al intentar editar | `[ENV]` | — | ✅ Resuelto — script que añade UUIDs |
| 26 | 08/04/2026 | Estado de Git inconsistente: archivos staged con versión antigua + modificaciones sin staged | `[VCS]` `[CONFIG]` | — | ✅ Resuelto — git restore --staged + commit limpio |
| 27 | 08/04/2026 | Warsaw #1 para esquí — deporte_montana incluye gp_hiking_area que Warsaw tiene en GP | `[ML]` | — | ⏳ Pendiente |
| 28 | 08/04/2026 | Cargos €404.86 Google Cloud por bucle autónomo de Claude Code durante incidente Anthropic 529 | `[ENV]` `[HTTP]` `[API-VERSION]` | `[RATE-LIMIT]` | ⚠️ Pendiente resolución Google + Anthropic |
| 29 | 09/04/2026 | Sesión Claude Code bloqueada en bucle interno — 21 arquetipos × 158 features nunca escritos | `[ENV]` | — | ✅ Resuelto — archivo recuperado en sesión nueva |
| 30 | 09/04/2026 | ARQUETIPOS_REVISION.md incluía ciudades esperadas hardcodeadas — contradice diseño de no-fijar-ciudades | `[ML]` `[DATA]` | — | ⏳ Pendiente — quitar ciudades del .md |
| 31 | 09/04/2026 | notebook v3 tiene 20 arquetipos con diseño antiguo — no refleja los 21 arquetipos revisados | `[ML]` | — | ⏳ Pendiente — actualizar ARCHETYPES en el notebook |
| 32 | 09/04/2026 | Da_Nang: prácticamente todos los features GP = 0 — GP no devuelve resultados para Vietnam | `[DATA]` | — | ✅ Resuelto — ciudad eliminada del dataset (54 ciudades) |
| 33 | 09/04/2026 | 8 features GP con todos los valores = 0 en las 54 ciudades — sin valor predictivo | `[DATA]` `[ML]` | — | ⏳ POST-PRESENTACION — eliminadas del CSV; investigar types GP en fetch_cities.py |
| 34 | 09/04/2026 | city_internet_mbps: 43/54 ciudades = 0 (dato ausente, no velocidad = 0) — Ookla por país | `[DATA]` | — | ⏳ POST-PRESENTACION — feature eliminada del CSV; sustituir por Ookla Global Fixed |

---
---

# ERRORES DETALLADOS

---

## #1 — `ModuleNotFoundError: No module named 'requests'`

**Fecha:** 20/03/2026
**Archivo:** `src/ingestion/fetch_cities.py`
**Etiquetas:** `[ENV]` `[DEPS]`

---

### Mensaje de error exacto
```
Traceback (most recent call last):
  File "src/ingestion/fetch_cities.py", line 26, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

---

### Qué estaba pasando en ese momento
Se intentó ejecutar el script de ingesta de datos por primera vez después de
crear el entorno virtual `.venv` y activarlo correctamente.

---

### Explicación del concepto técnico

**¿Qué es un entorno virtual en Python?**

Cuando instalas Python en tu ordenador, tienes una instalación "global" con sus
propias librerías. El problema es que si trabajas en varios proyectos a la vez,
cada uno puede necesitar versiones distintas de las mismas librerías (por ejemplo,
el proyecto A necesita `pandas 1.5` y el proyecto B necesita `pandas 2.0`). Si
instalas todo en el Python global, los proyectos se pisarían entre sí.

La solución es el **entorno virtual**: una carpeta (en este caso `.venv`) que
contiene una copia aislada de Python y sus librerías, independiente del sistema
global. Cuando activas el entorno (`.venv\Scripts\activate` en Windows), Python
solo "ve" las librerías instaladas dentro de esa carpeta.

**¿Por qué falló?**

Al crear el entorno virtual con `python -m venv .venv`, la carpeta `.venv` se crea
vacía — solo contiene Python, sin ninguna librería adicional. El script necesita
`requests` (para hacer llamadas HTTP), `beautifulsoup4` (para parsear HTML) y
`python-dotenv` (para leer el archivo `.env`), pero estas librerías no estaban
instaladas dentro del entorno virtual.

```
Sistema global Python     Entorno virtual .venv
─────────────────────     ─────────────────────
requests ✅               (vacío al crearse)
pandas ✅                 Python ✅
numpy ✅                  requests ❌  ← el script lo busca aquí
```

---

### Solución aplicada
```bash
# Con el entorno activado (debes ver (.venv) al inicio del prompt)
pip install requests beautifulsoup4 python-dotenv
```

**¿Por qué estas tres librerías?**
- `requests` — la librería estándar de Python para hacer llamadas HTTP (GET, POST...).
  Sin ella no podemos llamar a ninguna API externa.
- `beautifulsoup4` — librería para parsear (leer y navegar) HTML.
  La usamos para hacer scraping de Numbeo.
- `python-dotenv` — lee el archivo `.env` y carga sus variables en el entorno.
  Sin ella, la API key de Google no se carga automáticamente.

---

### Buena práctica aplicada
Una vez instaladas las dependencias, se documenta todo en `requirements.txt`:
```bash
pip freeze > requirements.txt
```
Así cualquier persona que clone el repo en el futuro puede instalar todo con:
```bash
pip install -r requirements.txt
```

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Cómo gestionas las dependencias en un proyecto Python?"
>
> **Respuesta:** "Uso entornos virtuales para aislar las dependencias de cada proyecto.
> Al crear un entorno nuevo hay que instalar explícitamente las dependencias porque
> el entorno está vacío. Las dependencias se documentan en `requirements.txt` con
> `pip freeze` para que sean reproducibles en cualquier máquina. Para proyectos más
> complejos se puede usar `pyproject.toml` con Poetry o pip-tools para gestión más
> avanzada de versiones."

---
---

## #2 — `.gitignore` en carpeta incorrecta — `.env` expuesto al repositorio

**Fecha:** 20/03/2026
**Contexto:** Configuración inicial del repositorio Git
**Etiquetas:** `[VCS]` `[CONFIG]` `[SECRETS]`

---

### Síntoma
Al ejecutar `git status`, el archivo `.env` (que contiene la API key de Google)
aparecía como candidato a ser commiteado al repositorio público de GitHub.

---

### Qué estaba pasando en ese momento
Se había creado el archivo `.env` con la API key, pero al hacer `git status` el
archivo aparecía en la lista de archivos sin trackear y podría haberse subido
al repositorio público de GitHub.

---

### Explicación del concepto técnico

**¿Qué es un archivo `.env` y por qué es peligroso subirlo a GitHub?**

Un archivo `.env` (abreviatura de "environment variables") contiene variables de
entorno del proyecto: claves de API, contraseñas de base de datos, tokens de
autenticación y otros datos sensibles. Su formato es simple:
```
GOOGLE_API_KEY=AIzaSy...tu_clave_real
POSTGRES_PASSWORD=mi_contraseña_secreta
```

Si subes este archivo a un repositorio público de GitHub, **cualquier persona en
el mundo puede ver tus claves**. Hay bots automatizados que escanean GitHub
continuamente buscando API keys expuestas. En cuestión de minutos alguien podría:
- Usar tu API key de Google Places y generar costes en tu cuenta
- Acceder a tu base de datos de producción
- Suplantar tu identidad en servicios externos

**¿Qué es `.gitignore` y cómo funciona?**

`.gitignore` es un archivo de texto que le dice a Git qué archivos debe ignorar
y nunca incluir en los commits. Cada línea es un patrón:
```gitignore
.env          # ignora el archivo .env
.venv/        # ignora toda la carpeta .venv
*.pkl         # ignora todos los archivos con extensión .pkl
data/raw/     # ignora toda la carpeta data/raw/
```

Git aplica el `.gitignore` solo si está en la **raíz del repositorio**.

**¿Por qué estaba en el sitio equivocado?**

Al crear el entorno virtual con `python -m venv .venv`, Python genera
automáticamente un `.gitignore` dentro de `.venv/` para proteger el contenido
del propio entorno virtual. Ese archivo dice:
```
# This file was generated by virtualenv
*
```
Es un archivo interno del entorno virtual, **no es el `.gitignore` del proyecto**.
Estaba en `.venv/.gitignore`, no en `.gitignore` (raíz del proyecto).

---

### Solución aplicada
```bash
# 1. Crear el .gitignore correcto en la raíz del proyecto
copy .venv\.gitignore .gitignore

# 2. Editarlo para incluir todo lo que no debe subir a GitHub
```

Contenido del `.gitignore` correcto en la raíz:
```gitignore
# Entorno virtual — nunca al repositorio
.venv/

# Variables de entorno y API keys — NUNCA al repositorio
.env

# Python — archivos compilados, no necesarios en el repo
__pycache__/
*.pyc
*.pyo

# Datos crudos — pueden ser pesados o sensibles
data/raw/

# MLflow — experimentos locales
mlruns/

# Modelos entrenados — archivos binarios pesados
models/*.pkl
models/*.bin
```

```bash
# 3. Verificar que .env NO aparece en git status
git status
# Si .env no aparece en ningún lado, está protegido ✅
```

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Cómo gestionas las credenciales y secretos en un proyecto?"
>
> **Respuesta:** "Nunca hardcodeo credenciales en el código. Las guardo en variables
> de entorno en un archivo `.env` que está en el `.gitignore` del proyecto, por lo
> que nunca se sube al repositorio. En producción, las variables de entorno se
> configuran directamente en el servidor o en el sistema de CI/CD (GitHub Actions,
> por ejemplo). Para compartir qué variables son necesarias sin exponer los valores,
> mantengo un archivo `.env.example` en el repo con los nombres de las variables
> pero sin valores."

---
---

## #3 — `403 Forbidden` en Wikipedia REST API

**Fecha:** 20/03/2026
**Archivo:** `src/ingestion/fetch_cities.py` — función `fetch_wikipedia()`
**Etiquetas:** `[HTTP]` `[AUTH]` `[ENCODING]` `[USER-AGENT]`

---

### Mensaje de error exacto
```
ERROR: 403 Client Error: Forbidden for url:
https://en.wikipedia.org/api/rest_v1/page/summary/M%C3%A1laga
```

---

### Qué significa el código HTTP 403

Los códigos de estado HTTP son números que el servidor devuelve para indicar
qué ocurrió con tu petición. Es importante conocerlos:

| Código | Nombre | Significa |
|--------|--------|-----------|
| `200` | OK | Todo fue bien, aquí tienes los datos |
| `400` | Bad Request | Tu petición tiene un error de formato |
| `401` | Unauthorized | No estás autenticado (falta API key) |
| `403` | Forbidden | Estás autenticado pero no tienes permiso |
| `404` | Not Found | El recurso que buscas no existe |
| `429` | Too Many Requests | Has enviado demasiadas peticiones |
| `500` | Internal Server Error | Error en el servidor, no en tu código |
| `504` | Gateway Timeout | El servidor tardó demasiado en responder |

En este caso el **403 Forbidden** significa que el servidor de Wikipedia entiende
la petición pero decide rechazarla — en este caso por dos razones combinadas.

---

### Causa raíz — dos problemas combinados

**Problema A: URL Encoding automático de la librería `requests`**

Cuando usas una f-string para construir una URL con `requests`, la librería
convierte automáticamente los caracteres especiales (tildes, ñ, espacios...)
a su representación codificada para URLs. Esto se llama **percent-encoding** o
**URL encoding**.

La `á` de "Málaga" se convierte en `%C3%A1`:
```python
# Lo que escribe el programador:
wiki_title = "Málaga"
url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
# → https://en.wikipedia.org/api/rest_v1/page/summary/M%C3%A1laga  ← 403

# Lo que necesita Wikipedia:
# → https://en.wikipedia.org/api/rest_v1/page/summary/Málaga  ← 200 ✅
```

La API REST de Wikipedia acepta caracteres Unicode directamente en la URL
(como `á`, `é`, `ñ`) y rechaza la versión percent-encoded con 403.

**Problema B: User-Agent requerido**

El **User-Agent** es una cabecera HTTP que identifica quién está haciendo la
petición. Los navegadores web siempre envían un User-Agent (por ejemplo:
`Mozilla/5.0 (Windows NT 10.0...)` para Chrome en Windows).

Cuando haces una petición con `requests` sin especificar User-Agent, envía
por defecto `python-requests/2.x.x`. Wikipedia y muchas APIs rechazan peticiones
con User-Agents genéricos de bots para evitar abusos, devolviendo 403.

---

### Solución aplicada
```python
# ✅ Construir la URL concatenando strings en lugar de f-string
# → requests NO encodea los caracteres cuando concatenas directamente
wiki_title = city["wiki"].replace(" ", "_")  # solo los espacios se reemplazan por _
r = requests.get(
    "https://en.wikipedia.org/api/rest_v1/page/summary/" + wiki_title,
    headers={"User-Agent": "NomadOptima/1.0 (educational project)"},
    timeout=10
)
```

---

### Resultado tras el fix
```
[Wikipedia] Málaga...
  OK: 'Municipality in Andalusia, Spain'
[Wikipedia] París...
  OK: 'Capital of France'
```

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Has tenido problemas con llamadas a APIs externas?
> ¿Cómo los diagnosticaste?"
>
> **Respuesta:** "Sí. Tuve un 403 Forbidden en la API de Wikipedia que tenía dos
> causas: la librería `requests` estaba aplicando URL encoding automático a los
> caracteres con tilde, y no estaba enviando un User-Agent en la cabecera HTTP.
> Lo diagnostiqué imprimiendo la URL construida antes de la llamada y comparándola
> con la URL esperada. El fix fue construir la URL por concatenación de strings
> en lugar de f-string, y añadir el User-Agent requerido en los headers."

---
---

## #4 — `429 Too Many Requests` y `504 Gateway Timeout` en Overpass API (OSM)

**Fecha:** 20/03/2026
**Archivo:** `src/ingestion/fetch_cities.py` — función `fetch_osm()`
**Etiquetas:** `[HTTP]` `[RATE-LIMIT]` `[TIMEOUT]` `[BATCH]`

---

### Mensajes de error exactos
```
WARN [coworking_osm]: 429 Client Error: Too Many Requests
WARN [universities]: 504 Server Error: Gateway Timeout
WARN [hospitals]:    504 Server Error: Gateway Timeout
WARN [restaurants]:  429 Client Error: Too Many Requests
... (13 de 20 categorías fallaron)
```

---

### Qué significan estos dos códigos HTTP

**429 Too Many Requests — Rate Limiting**

El servidor ha contado cuántas peticiones has enviado en un periodo de tiempo y
ha decidido bloquearte temporalmente porque has superado su límite. Esto se llama
**rate limiting** (limitación de tasa) y es una medida de protección que usan
todos los servicios públicos gratuitos para evitar que un solo usuario colapse
el servidor.

Ejemplo real: Overpass API permite aproximadamente 1-2 peticiones por segundo
desde la misma IP. Si mandas 20 peticiones en 30 segundos, las últimas son
rechazadas con 429.

**504 Gateway Timeout**

El servidor que recibió tu petición intentó procesar la consulta pero tardó
demasiado y canceló la conexión antes de devolver una respuesta. En el caso de
Overpass, ocurre cuando el servidor está sobrecargado por muchos usuarios
simultáneos o cuando la query es muy pesada para el servidor en ese momento.

---

### Causa raíz — diseño ineficiente de N queries

El código original hacía **una llamada HTTP separada por cada categoría**:
```python
# ❌ Diseño original: 20 queries separadas × 2 ciudades = 40 llamadas HTTP
for category, query in osm_queries.items():   # 20 iteraciones
    r = requests.post(overpass_url, ...)       # 1 llamada HTTP por iteración
    time.sleep(1.5)                            # solo 1.5 segundos de pausa
```

Con 20 categorías y 1.5 segundos de pausa, las 20 queries tardaban ~30 segundos.
Overpass API veía 20 peticiones desde la misma IP en 30 segundos y bloqueaba
con 429 a partir de la 3ª o 4ª petición.

**¿Por qué se diseñó así inicialmente?**

Es el diseño más intuitivo cuando empiezas: "necesito el dato X, hago la llamada
para X; necesito el dato Y, hago la llamada para Y". El problema es que no escala
cuando tienes muchas categorías.

---

### Solución aplicada — Query Batch (una sola petición)

En lugar de 20 queries separadas, se reescribió la función para hacer
**una sola query** que recupera todos los elementos de la ciudad en una petición,
y luego clasificarlos en Python:

```python
# ✅ Diseño nuevo: 1 query batch × 2 ciudades = 2 llamadas HTTP totales
batch_query = f"""
[out:json][timeout:60];
area[name="{city['osm_area']}"]["admin_level"="{city['osm_admin']}"]->.searchArea;
(
  way["highway"="cycleway"](area.searchArea);
  way["leisure"="park"](area.searchArea);
  node["amenity"="restaurant"](area.searchArea);
  node["amenity"="pharmacy"](area.searchArea);
  node["leisure"="playground"](area.searchArea);
  ... todos los tipos en una sola query ...
);
out tags;
"""

# Luego clasificar en Python contando por tags
for elemento in elementos:
    tags = elemento.get("tags", {})
    if tags.get("amenity") == "restaurant":
        counts["restaurants"] += 1
    elif tags.get("leisure") == "playground":
        counts["playgrounds"] += 1
    ...
```

**Resultado:** de 40 llamadas HTTP a **2 llamadas totales**. El servidor de
Overpass ya no ve ningún rate limit superado.

Se añadió también un sistema de **reintentos con espera progresiva** por si
la única llamada falla:
```python
for intento in range(3):           # hasta 3 intentos
    try:
        r = requests.post(...)
        break                      # éxito, salir del bucle
    except Exception as e:
        wait = 20 * (intento + 1)  # 20s en el 1er reintento, 40s en el 2º
        time.sleep(wait)
```

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Cómo optimizas el rendimiento de un pipeline de ingesta
> de datos con múltiples fuentes externas?"
>
> **Respuesta:** "Una de las optimizaciones más importantes es reducir el número
> de llamadas HTTP agrupando peticiones en batch cuando la API lo permite. En
> NomadOptima tenía un diseño inicial que hacía 40 llamadas HTTP a Overpass API
> y recibía errores 429 de rate limiting. Lo resolví reescribiendo la función para
> hacer una sola query union que traía todos los datos en una petición y clasificaba
> los resultados localmente en Python. Esto redujo las llamadas de 40 a 2, eliminó
> los rate limit errors y redujo el tiempo de ejecución de OSM de ~5 minutos a
> ~30 segundos."

---
---

## #5 — `0 key prices, 1 índices` en scraping de Numbeo

**Fecha:** 20/03/2026
**Archivo:** `src/ingestion/fetch_cities.py` — función `fetch_numbeo()`
**Etiquetas:** `[SCRAPING]` `[DATA]` `[MATCHING]`

---

### Síntoma
```
[Numbeo] Málaga...
  OK: 54 precios, 0 key prices, 1 índices
```
El scraping funcionó correctamente (54 precios extraídos) pero el mapeo
a las variables clave para el modelo devolvió 0 resultados.

---

### Qué es el scraping y por qué es frágil

**Web Scraping** es la técnica de extraer datos de una página web leyendo su HTML
en lugar de usar una API oficial. Es útil cuando el sitio no tiene API, pero tiene
un problema fundamental: **el scraping depende de la estructura HTML de la web**,
y esa estructura puede cambiar en cualquier momento sin avisar.

En este caso, Numbeo no tiene API pública gratuita, así que extraemos los datos
leyendo las tablas de su web con BeautifulSoup.

---

### Causa raíz — String matching demasiado estricto

El código tenía un diccionario `key_map` que buscaba los nombres exactos y
completos de las filas de la tabla de Numbeo:

```python
# ❌ Matching exacto — frágil ante cambios de Numbeo
key_map = {
    "rent_1br_center":   "Apartment (1 bedroom) in City Centre",
    "gym_monthly":       "Fitness Club, Monthly Fee for 1 Adult",
    "internet_monthly":  "Internet (60 Mbps or More, Unlimited Data, Cable/ADSL)",
}

# La comparación era:
if keyword.lower() in price_key.lower():
    result["key_prices"][key] = result["prices"][price_key]
```

El problema: si Numbeo cambia "City Centre" por "City Center", o actualiza la
descripción de "Internet (60 Mbps..." a "Internet (100 Mbps...", el matching
falla silenciosamente devolviendo 0 resultados sin ningún error visible.

Esto es un **silent failure** (fallo silencioso): el código no lanza una excepción,
simplemente devuelve un resultado vacío. Es especialmente peligroso en pipelines
de datos porque puede llegar al modelo con features a 0 sin que nadie se dé cuenta.

---

### Solución aplicada — Keywords cortas y robustas
```python
# ✅ Keywords parciales cortas — funcionan aunque Numbeo cambie el texto
key_map = {
    "rent_1br_center":   "1 bedroom) in City",  # ← más corto y estable
    "rent_1br_outside":  "1 bedroom) Outside",
    "meal_cheap":        "Inexpensive Restaurant",
    "meal_midrange":     "Mid-range Restaurant",
    "coffee":            "Cappuccino",
    "beer":              "Domestic Beer",
    "transport_monthly": "Monthly Pass",
    "gym_monthly":       "Fitness Club",
    "internet_monthly":  "Internet",             # ← muy corto, siempre presente
    "basic_utilities":   "Electricity, Heating",
}
```

La idea es usar la parte más estable del texto: "Fitness Club" es más estable
que "Fitness Club, Monthly Fee for 1 Adult" porque Numbeo puede cambiar la parte
descriptiva pero raramente cambia el nombre del servicio.

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Cómo validas la calidad de los datos en un pipeline de
> ingesta?"
>
> **Respuesta:** "El scraping tiene el problema de los fallos silenciosos: el código
> no lanza error pero devuelve datos vacíos o incorrectos. La estrategia que uso
> tiene dos partes: primero, usar keywords de matching robustas y parciales en lugar
> de strings exactos que son frágiles ante cambios del sitio. Segundo, añadir
> validaciones de calidad de datos después de la ingesta que detecten cuando una
> feature clave tiene valor 0 o None de forma inesperada, y generen alertas antes
> de que esos datos lleguen al modelo."

---
---

## #6 — `46 errores, 0 lugares` en Google Places API (New)

**Fecha:** 20/03/2026 | **Resuelto:** ~20/03/2026 (confirmado 01/04/2026)
**Archivo:** `src/ingestion/fetch_cities.py` — función `fetch_google_places()`
**Etiquetas:** `[HTTP]` `[AUTH]` `[API-VERSION]`
**Estado:** ✅ **Resuelto** — API activada en Google Cloud Console

---

### Síntoma
```
[Google Places] Málaga...
  OK: 0 lugares | 0 types oficiales, 0 text search | 46 errores
[Google Places] París...
  OK: 0 lugares | 0 types oficiales, 0 text search | 46 errores
```

---

### Qué es una API y qué significa tener "versiones"

Una **API (Application Programming Interface)** es un conjunto de reglas que
define cómo un programa puede comunicarse con un servicio externo. Es como
un contrato: "si me mandas una petición en este formato, te devuelvo los datos
en este otro formato".

Las APIs evolucionan con el tiempo y las empresas publican **versiones** nuevas
que pueden tener endpoints (URLs) diferentes, autenticación diferente y formato
de respuesta diferente. A veces mantienen las versiones antiguas funcionando
durante un tiempo (esto se llama **backward compatibility**) y otras veces las
eliminan (esto se llama **deprecation**).

---

### Causa raíz — API (New) vs API legacy

Google tiene **dos versiones** de su API de Places funcionando en paralelo:

| | Places API (legacy) | Places API (New) |
|---|---|---|
| URL base | `maps.googleapis.com/maps/api/place/` | `places.googleapis.com/v1/places/` |
| Autenticación | Parámetro `?key=` en la URL | Header `X-Goog-Api-Key` |
| Activación | En Google Cloud Console | En Google Cloud Console (API separada) |
| Endpoints | `/textsearch/json`, `/nearbysearch/json` | `:searchText`, `:searchNearby` |
| Campos | `results[].name`, `results[].rating` | `places[].displayName.text`, `places[].rating` |

El script usa la **Places API (New)** porque tiene tipos oficiales más precisos
y mejores resultados. Pero la API key obtenida solo tenía permisos para la
**Places API legacy** — son dos APIs distintas en Google Cloud Console y hay
que activar cada una por separado.

**¿Por qué no hubo un error claro de autenticación?**

Cuando mandas una petición a la Places API (New) con una key que no tiene permisos,
Google devuelve un error HTTP que el código capturaba como "error" silenciosamente
sin mostrar el mensaje real del servidor. El fix pendiente incluye mejorar el
logging para mostrar el mensaje de error exacto de la respuesta.

---

### Solución requerida (acción en Google Cloud Console)

1. Ir a [console.cloud.google.com](https://console.cloud.google.com)
2. Menú izquierdo: **APIs y servicios → Biblioteca**
3. Buscar exactamente: **"Places API (New)"**
   ⚠️ Es una API diferente a "Places API" — tienen nombres casi idénticos
4. Clicar en ella y pulsar **Activar**
5. Ir a **Credenciales → tu API key → Editar → Restricciones de API**
6. Añadir "Places API (New)" a la lista de APIs permitidas para esa key

---

### Estado
✅ **Resuelto.** Confirmado el 01/04/2026 inspeccionando `data/raw/malaga_raw.json`:

```
Google Places fetched_at: 2026-03-20T13:16:41
Categorías con datos: 44 / 46
Total lugares encontrados: 753
```

Los 2 zeros restantes (`national_park`, `aquarium`) son ceros reales de Málaga,
no errores de API. El error había sido resuelto activando la API en Google Cloud
Console pero no se había documentado como resuelto en este log.

---

### Para recordar en una entrevista
> **Pregunta típica:** "¿Has trabajado con APIs externas? ¿Qué problemas has
> encontrado?"
>
> **Respuesta:** "Sí. Un caso concreto fue con Google Places. Google tiene dos
> versiones paralelas de su API de Places — la legacy y la New — que tienen
> URLs base, sistema de autenticación y formato de respuesta completamente
> distintos. Aunque tenía una API key válida, no funcionaba con la versión
> nueva porque son APIs separadas en Google Cloud Console con activación
> independiente. El diagnóstico fue comparar la URL del endpoint que usaba
> el código con la documentación oficial de cada versión, lo que reveló
> inmediatamente la discrepancia."

---
---

---
---

## #7 — `0 key prices` persiste tras el fix de error #5 — Fix incompleto en key_map

**Fecha:** 01/04/2026
**Archivo:** `src/ingestion/fetch_cities.py` — `key_map` dentro de `fetch_numbeo()`
**Etiquetas:** `[SCRAPING]` `[DATA]` `[MATCHING]`
**Estado:** ✅ **Resuelto** — `fetch_cities.py` v8

---

### Mensaje de error exacto
No hay excepción visible. El síntoma es silencioso:
```
[Numbeo] Málaga...
  OK: 54 precios, 0 key prices, 1 índices
```
`key_prices` sigue vacío aunque el error #5 ya estaba supuestamente resuelto.
Los valores de alquiler y transporte en el feature store de notebook 02 son
valores hardcodeados (Málaga=1200€, París=2200€) en lugar de datos reales de Numbeo.

---

### Qué estaba pasando

Durante el diagnóstico de notebook 03, se detectó que `city_coste_vida_estimado`
y `city_alquiler_1br_centro` tenían el mismo valor constante para todos los
registros del training dataset. Esto confirmó que `key_prices` nunca se había
llenado correctamente.

Se inspeccionó el JSON crudo:
```python
with open('data/raw/malaga_raw.json', encoding='utf-8') as f:
    data = json.load(f)
print(list(data['numbeo']['prices'].keys())[:5])
# ['Meal at an Inexpensive Restaurant',
#  'Meal for Two at a Mid-Range Restaurant (Three Courses, Without Drinks)',
#  ...
#  '1 Bedroom Apartment in City Centre',         ← formato actual de Numbeo
#  '1 Bedroom Apartment Outside of City Centre']
```

Los nombres reales de las filas de Numbeo NO contienen paréntesis con el formato
`(1 bedroom)`. El formato antiguo era `Apartment (1 bedroom) in City Centre`,
pero Numbeo lo cambió a `1 Bedroom Apartment in City Centre`.

---

### Explicación del concepto técnico — Web Scraping y Degradación Silenciosa

La solución de error #5 usó keywords más cortas para ser más robusta:
`"1 bedroom) in City"`. Pero al acortar el string, mantuvo el carácter `)`
que pertenecía al formato antiguo de Numbeo. El matching parcial buscaba
`"1 bedroom)"` como substring, y ese substring simplemente no existe
en ninguna fila del HTML actual de Numbeo.

Esto es un ejemplo de **fix incompleto**: la solución atacó el síntoma correcto
(matching demasiado largo y frágil) pero no verificó la solución contra los datos
reales antes de considerarla resuelta.

La lección: **una solución de scraping solo está resuelta cuando se verifica
ejecutando el matching contra el JSON real**, no solo revisando el código.

Para `transport_monthly` había un error distinto pero relacionado:
- Keyword usada: `"Monthly Pass"`
- Nombre real en Numbeo: `"Monthly Public Transport Pass (Regular Price)"`
- Problema: `"monthly pass"` NO es substring de `"monthly public transport pass"`
  porque entre "monthly" y "pass" hay "public transport" en el medio.
  Python's `in` busca el substring contiguo, no palabras aisladas.

```python
# Demostración del bug
keyword = "monthly pass"
precio  = "monthly public transport pass (regular price)"
print(keyword in precio)  # False ← porque no es contiguo
```

---

### Causa raíz

Tres keywords con bugs de matching:

| Key | Keyword incorrecta | Problema | Keyword correcta |
|-----|--------------------|----------|-----------------|
| `rent_1br_center` | `"1 bedroom) in City Centre"` | `)` no existe en formato actual de Numbeo | `"Bedroom Apartment in City Centre"` |
| `rent_1br_outside` | `"1 bedroom) Outside"` | `)` no existe en formato actual de Numbeo | `"Bedroom Apartment Outside"` |
| `transport_monthly` | `"Monthly Pass"` | No es substring contiguo del nombre real | `"Transport Pass"` |

---

### Solución aplicada

```python
# ❌ Antes — keywords con formato antiguo de Numbeo y substring no contiguo
key_map = {
    "rent_1br_center":   "1 bedroom) in City Centre",   # ← ) no existe
    "rent_1br_outside":  "1 bedroom) Outside",           # ← ) no existe
    "transport_monthly": "Monthly Pass",                 # ← no es substring contiguo
    ...
}

# ✅ Después — keywords verificadas contra el JSON real (fetch_cities.py v8)
key_map = {
    "rent_1br_center":   "Bedroom Apartment in City Centre",
    "rent_1br_outside":  "Bedroom Apartment Outside",
    "transport_monthly": "Transport Pass",               # ← sí es substring contiguo
    ...
}
```

Verificación ejecutada contra `data/raw/malaga_raw.json`:
```
key_prices encontrados: 10/10
  rent_1br_center       : 1160.0 EUR/mes
  rent_1br_outside      :  857.54 EUR/mes
  transport_monthly     :   23.95 EUR/mes
  ...
TODOS los keys tienen match OK
```

---

### Impacto en el modelo

Antes de este fix, el feature store en notebook 02 usaba valores hardcodeados:
```python
'coste_vida_estimado': 1200 if name == 'Malaga' else 2200,
'alquiler_1br_centro': 950  if name == 'Malaga' else 1800,
```

Después del fix, estos valores vendrán de Numbeo directamente:
- Málaga: alquiler 1BR en centro = **1160€**, fuera = 857€, salario neto medio = 1563€
- París: pendiente de verificar con re-ejecución de la ingesta

El impacto en NDCG es esperado: Precision@1 debería subir porque el filtro de
presupuesto ahora trabaja con datos reales en lugar de constantes arbitrarias.

---

### Para recordar en una entrevista

> **Pregunta típica:** "¿Cómo detectas errores silenciosos en un pipeline de datos?"
>
> **Respuesta:** "Los fallos silenciosos son los más peligrosos en ML porque el
> pipeline termina sin excepción pero produce datos incorrectos que llegan al modelo
> sin que nadie lo sepa. Mi estrategia tiene tres partes: primero, añado assertions
> después de cada paso crítico — por ejemplo, `assert len(key_prices) == len(key_map)`
> lanzaría error inmediatamente en lugar de continuar silenciosamente. Segundo,
> verifico las soluciones de scraping siempre contra datos reales, no solo leyendo
> el código. Tercero, en el feature store añado valores de sanity check: si el
> alquiler en ciudad española es exactamente 1200 siempre, ese valor constante es
> una señal de alarma."

---
---

---
---

## #8 — Google Places devuelve máximo 20 resultados por categoría — datos truncados

**Fecha:** 01/04/2026
**Archivo:** `src/ingestion/fetch_cities.py` — función `fetch_google_places()`
**Etiquetas:** `[HTTP]` `[DATA]` `[API-VERSION]`
**Estado:** ✅ **Resuelto** — `fetch_cities.py` v9

---

### Síntoma
Todas las categorías populares (gym, restaurant, museum, coworking...) devuelven
exactamente `count=20`. Málaga tiene cientos de restaurantes, pero el dataset
solo registraba 20. Las features del modelo no podían distinguir ciudades con
20 opciones de las que tienen 200.

```
gym                 count=20   ← cap, no el total real
restaurant          count=20   ← cap
museum              count=20   ← cap
coworking           count=20   ← cap
```

---

### Qué estaba pasando

La Places API (New) tiene un parámetro `maxResultCount` con un **límite duro de 20**
por llamada. El código hacía exactamente una llamada por categoría y guardaba
el resultado directamente — sin intentar obtener más páginas.

Esto significa que el modelo aprendía que Málaga tiene "20 gimnasios" cuando
en realidad tiene muchos más. Si París también tiene "20 gimnasios", la feature
`city_gp_gym` vale 20 para ambas ciudades → el modelo no puede diferenciarlas.

---

### Explicación del concepto técnico — Paginación en APIs REST

Muchas APIs REST limitan el número de resultados por respuesta para proteger
sus servidores. Para obtener todos los resultados hay que hacer **paginación**:
varias peticiones encadenadas donde cada respuesta indica cómo pedir la siguiente.

Hay dos patrones comunes:

| Patrón | Cómo funciona | Ejemplo |
|--------|---------------|---------|
| **Offset/limit** | `?page=2&limit=20` | La mayoría de APIs REST clásicas |
| **Cursor/token** | La respuesta incluye un `nextPageToken` que usas en la siguiente petición | Google Places, Twitter API |

Google Places (New) usa **cursor-based pagination** con `nextPageToken`:
```
Petición 1 → {places: [...20...], nextPageToken: "abc123"}
Petición 2 con pageToken="abc123" → {places: [...20...], nextPageToken: "def456"}
Petición 3 con pageToken="def456" → {places: [...15...]}  ← no hay más
```

**Importante:** `nextPageToken` debe incluirse en el `X-Goog-FieldMask` o la API
no lo devuelve aunque haya más resultados. Este es otro silent failure frecuente.

---

### Limitación de `searchNearby`

`searchNearby` (el endpoint para tipos oficiales de Google) **no soporta paginación**.
No hay `nextPageToken`. El límite duro es 20 resultados por llamada.

La solución alternativa: hacer **múltiples llamadas con centros geográficos desplazados**
y deduplicar los resultados por `places.id`:

```
Centro ciudad    → 20 resultados
+4 km al norte  → 20 resultados (algunos nuevos, algunos repetidos)
+4 km al sur    → 20 resultados (algunos nuevos)
+4 km al este   → 20 resultados (algunos nuevos)
+4 km al oeste  → 20 resultados (algunos nuevos)
────────────────────────────────────────────
Tras deduplicar → ~60-80 resultados únicos por categoría
```

Esto funciona porque Google ordena los resultados por distancia al centro de búsqueda.
Al mover el centro, los 20 "más cercanos" son distintos.

---

### Causa raíz

Dos problemas independientes:
1. **`searchText`**: no se implementó paginación con `nextPageToken`
2. **`searchNearby`**: no existe paginación en la API — se necesita estrategia alternativa

---

### Solución aplicada (v9)

```python
DELTA = 0.04   # ≈ 4.4 km
SEARCH_OFFSETS = [(0,0), (+DELTA,0), (-DELTA,0), (0,+DELTA), (0,-DELTA)]

# searchText: paginación con nextPageToken (hasta 3 páginas = 60 resultados)
seen_ids, places, page_token = set(), [], None
for _ in range(3):
    payload = {"textQuery": ..., "maxResultCount": 20}
    if page_token:
        payload["pageToken"] = page_token
    # IMPORTANTE: nextPageToken debe estar en el FieldMask
    headers["X-Goog-FieldMask"] = "places.id,...,nextPageToken"
    r = requests.post(text_url, json=payload, headers=headers)
    for p in r.json().get("places", []):
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"]); places.append(p)
    page_token = r.json().get("nextPageToken")
    if not page_token: break

# searchNearby: 5 centros desplazados + deduplicación por id
seen_ids, places = set(), []
for dlat, dlon in SEARCH_OFFSETS:
    payload["locationRestriction"]["circle"]["center"] = {
        "latitude": city["lat"] + dlat, "longitude": city["lon"] + dlon
    }
    for p in requests.post(nearby_url, ...).json().get("places", []):
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"]); places.append(p)
```

**Resultado esperado tras re-ejecutar la ingesta:**
- `searchNearby`: hasta ~80-100 resultados únicos por categoría (vs 20 antes)
- `searchText`: hasta 60 resultados únicos por categoría (vs 20 antes)

---

### Coste en llamadas a la API

| Método | Antes | Después |
|--------|-------|---------|
| `searchNearby` (39 categorías × 2 ciudades) | 78 llamadas | 390 llamadas (×5 offsets) |
| `searchText` (7 categorías × 2 ciudades) | 14 llamadas | ≤42 llamadas (×3 páginas) |
| **Total** | **92 llamadas** | **≤432 llamadas** |

Google Places API (New) tiene un free tier de 200 USD/mes ≈ miles de llamadas
gratuitas. Para 2 ciudades en desarrollo esto es perfectamente viable.

---

### Para recordar en una entrevista

> **Pregunta típica:** "¿Cómo obtienes más de N resultados cuando una API tiene
> paginación?"
>
> **Respuesta:** "Depende del tipo de paginación. Si la API usa cursor-based
> pagination (como Google Places con nextPageToken), encadenas peticiones usando
> el token de cada respuesta como parámetro de la siguiente. Si el endpoint no
> tiene paginación (como searchNearby), la alternativa es hacer múltiples
> peticiones con parámetros de filtro distintos — en este caso, desplazando el
> centro geográfico — y deduplicar los resultados por un identificador único
> como el places.id. En ambos casos hay que tener en cuenta el coste en llamadas
> a la API y añadir pausas para respetar los rate limits."

---

## #9 — `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'` en notebook 02
30/03/2026 | `notebooks/02_synthetic_profiles.ipynb` | Etiquetas: [DATA] [MATCHING]

### Mensaje de error exacto
```
TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'
```
En la función `compute_relevance`, línea:
```python
score += min(ciudad['internet_download_mbps'] / 200, 1.0) * perfil['importancia_internet']
```

### Qué estaba pasando
Al expandir de 2 a 5 ciudades y ejecutar el notebook 02, la función `compute_relevance` falló
porque `ciudad['internet_download_mbps']` era `None` para Porto.
El feature store obtenía ese valor así:
```python
'internet_download_mbps': spd.get('fixed_download_mbps', 0)
```
Pero en `porto_raw.json` el campo `fixed_download_mbps` existía con valor `null`:
```json
"speedtest": {"fixed_download_mbps": null, ...}
```
Cuando `.get(key, default)` encuentra la clave pero su valor es `None`, devuelve `None` —
el `default` solo se usa si la clave **no existe**. El operador `/` no puede dividir `None`.

### Explicación del concepto técnico
**dict.get(key, default)** en Python tiene un comportamiento sutil: el valor por defecto
solo se aplica si la clave está **ausente** (`KeyError`). Si la clave existe con valor `None`
(equivalente al `null` de JSON), `.get()` devuelve `None`. Esto es distinto de JavaScript
donde `null` y `undefined` tienen semánticas diferentes. La solución idiomática en Python
para "usa 0 si el valor es None O si la clave no existe" es el patrón `or`:
```python
value = d.get('key') or 0
```
Esto funciona porque `None or 0` → `0`, y `0 or 0` → `0`, pero OJO: `0 or 0` también da `0`
(no hay ambigüedad en este caso porque Mbps = 0 y Mbps = None significan lo mismo: sin dato).

### Causa raíz
La API de Speedtest (o el módulo que la consume en `fetch_cities.py`) devuelve `null`
para Porto en lugar de omitir el campo. Porto comparte índice de velocidad con España/Francia
pero la fuente puede no tener datos desagregados por ciudad.

### Solución aplicada
```python
# ANTES (roto con None):
'internet_download_mbps': spd.get('fixed_download_mbps', 0),

# DESPUÉS (robusto a None explícito):
'internet_download_mbps': spd.get('fixed_download_mbps') or 0,
```

### Para recordar en una entrevista
> "Al leer datos de una API o JSON, distingue entre clave ausente y clave con valor null.
> En Python, `dict.get(key, default)` no protege contra `None` explícito — solo contra
> clave ausente. Para ambos casos usa `d.get(key) or default`, pero ten cuidado si `0`
> es un valor válido distinto de `None`: en ese caso usa `val if val is not None else default`."

---

*Última actualización: 30/03/2026*
*Script en producción: fetch_cities.py v9*

---

## #10 — Features de idioma binarias no capturan la realidad lingüística

**Fecha:** 06/04/2026
**Archivo:** `src/processing/features.py`, `app/streamlit_app.py`
**Etiquetas:** `[DATA]` `[DESIGN]`

---

### Qué estaba pasando
Al diseñar el formulario de la app, se intentó añadir "idioma" como filtro. Las features disponibles eran `city_idioma_espanol` y `city_idioma_frances` — flags binarios (0 o 1). Porto habla portugués: no modelado. El inglés lo habla parte de la población en todas las ciudades, pero con niveles muy distintos: Málaga y Porto son muy English-friendly, París no. Nada de esto estaba capturado.

### Explicación del concepto técnico
Este es un problema clásico de **feature engineering para variables categóricas con gradiente**. Hay tres formas de codificar "idioma":
- **Binario**: `idioma_español = 1/0` — pierde toda la gradación
- **Nominal one-hot**: una columna por idioma oficial — pierde idiomas no oficiales
- **Ordinal/continuo**: `english_friendliness = 0-10` — captura la realidad lingüística real

El error fue elegir la codificación más simple (binaria) cuando la variable tiene una dimensión continua importante: cuánto inglés te va a funcionar en la calle.

### Causa raíz
Al construir `features.py`, el idioma se codificó como idioma oficial del país (España → español, Francia → francés). Esto ignora tres realidades: (1) ciudades turísticas tienen alta penetración de inglés independientemente del idioma oficial; (2) Portugal tiene uno de los niveles de inglés más altos de Europa del Sur pese a no tener inglés como oficial; (3) la resistencia cultural francesa al inglés no está capturada por ningún dato del país.

### Solución aplicada
Sistema de dos dimensiones manuales por ciudad, escalable en el futuro:
- `city_native_language` (string): idioma oficial de la ciudad
- `city_english_friendliness` (0-10): facilidad real para vivir con solo inglés

| Ciudad | Nativo | English-friendly | Razonamiento |
|--------|--------|-----------------|--------------|
| Málaga | Español | 8 | Costa del Sol, comunidad expat grande, muy internacional |
| Valencia | Español | 6 | Internacional pero más local que Málaga |
| Porto | Portugués | 8 | Portugal top 10 Europa en EF EPI, generación joven muy anglófona |
| Burdeos | Francés | 4 | Más abierto que París pero cultura francesa arraigada |
| París | Francés | 3 | Cultura del idioma muy fuerte, resistencia activa al inglés |

**Fuentes para escalar** cuando haya más ciudades:
- **EF English Proficiency Index** (ef.com/epi): ranking anual de 113 países, gratis
- **InterNations Expat City Ranking**: encuesta anual de expats por ciudad, incluye facilidad de integración lingüística
- **Eurostat Language Survey**: competencia en idiomas extranjeros por región EU, datos oficiales y gratuitos

Fórmula de escalado propuesta: `english_score = EF_EPI_país × (1 + tourism_index × 0.3) × cultural_multiplier`

### Para recordar en una entrevista
> "La codificación de variables categóricas es una decisión de diseño con consecuencias en todo el pipeline. Un flag binario `habla_español=1` es correcto si la variable es verdaderamente binaria. Pero si hay gradiente — como el nivel de inglés en una ciudad — necesitas una variable continua. El error más común es usar la codificación más fácil de implementar en lugar de la más fiel a la realidad."

---

## #11 — Cards genéricas: Málaga gana siempre por dominancia de `city_gp_hiking`

**Fecha:** 06/04/2026
**Archivo:** `app/streamlit_app.py`, `src/models/ranker.py`
**Etiquetas:** `[ML]` `[UX]`

---

### Qué estaba pasando
Al probar la Streamlit app, independientemente de lo que el usuario seleccionara en las cards de interés, Málaga aparecía en #1. Un usuario que seleccionaba "Cultura y Arte" + "Gastronomía" esperaría París. Un usuario que seleccionaba "Vino y gastronomía" esperaría Porto o Burdeos. El resultado era siempre Málaga.

### Explicación del concepto técnico
Esto es **feature importance dominance** en modelos de árboles de decisión. LightGBM asigna a cada feature un "gain" — cuánto mejora el NDCG cada vez que esa feature se usa en un split. El gain de `city_gp_hiking` es **89.286 puntos**, el doble que la segunda feature. Esto significa que el modelo aprendió que "tener senderos de senderismo" es el predictor más fuerte de si una ciudad va a ser elegida — y ese valor es una propiedad fija de la ciudad que no cambia según las preferencias del usuario.

Segundo problema compuesto: el formulario modificaba `user_importancia_playa`, `user_importancia_cultura` (features del usuario), pero el modelo apenas usaba esas features comparado con las de ciudad. El usuario movía palancas que el modelo casi no escucha.

### Causa raíz
Dos causas compuestas:
1. **Pseudo-labels sesgados hacia senderismo**: las reglas que generaron los labels en el notebook 02 puntuaban fuertemente el hiking para los arquetipos más frecuentes. El modelo aprendió eso y lo generalizó a todas las predicciones.
2. **Desacoplamiento entre UI y modelo**: el formulario exponía `user_importancia_*` como si fueran el driver principal del ranking, pero el modelo usa mayoritariamente features de ciudad fijas. El usuario tenía la ilusión de control sin control real.

### Solución aplicada
Rediseño de la capa de scoring: el usuario selecciona **actividades concretas** (senderismo, surf, gym, museos...) que se mapean directamente a las features de ciudad (`city_gp_hiking`, `city_gp_surf_school`, `city_gp_museum`...). El score de cada ciudad es una suma ponderada de sus valores reales en esas features específicas. Los pre-filtros de presupuesto y clima siguen aplicándose.

### Para recordar en una entrevista
> "NDCG=0.9995 en datos sintéticos no garantiza que el modelo sea útil. Si los pseudo-labels se generaron con reglas que sobrepesan una feature, el modelo aprende esas reglas perfectamente — no las preferencias reales de usuarios. Este es el problema del 'metric hacking': optimizas la métrica correcta sobre datos incorrectos. Un modelo realmente validado necesita A/B test con usuarios reales midiendo si reservan en la ciudad recomendada."

---

## #12 — HTML crudo en Streamlit renderiza como texto plano

**Fecha:** 06/04/2026
**Archivo:** `app/streamlit_app.py`
**Etiquetas:** `[UX]`

---

### Qué estaba pasando
Los result cards de la app Streamlit, diseñados con HTML y CSS personalizados dentro de `st.markdown(..., unsafe_allow_html=True)`, se mostraban como texto plano con las etiquetas HTML visibles en pantalla. El bloque `<style>` no se aplicaba.

### Explicación del concepto técnico
Streamlit tiene su propio sistema de estilos basado en React y una **política de sandboxing de CSS**. El parámetro `unsafe_allow_html=True` permite insertar HTML básico, pero no garantiza que CSS complejo (grids, gradientes, variables CSS) funcione en todos los contextos. Streamlit inyecta sus propios estilos con alta especificidad que pueden sobreescribir los personalizados. En ciertas versiones o en el modo de desarrollo, el HTML puede no renderizarse por razones de seguridad XSS.

### Causa raíz
El diseño intentó construir una interfaz visual rica usando HTML/CSS puro dentro de `st.markdown()`. Este enfoque funciona para elementos simples pero es frágil para layouts complejos porque: (1) Streamlit no garantiza estabilidad del HTML interno entre versiones; (2) el CSS de Streamlit usa alta especificidad y puede colisionar; (3) el modo desarrollo puede sanitizar el HTML de forma distinta al modo producción.

### Solución aplicada
Reemplazar los HTML cards por componentes nativos de Streamlit: `st.metric()` para estadísticas, `st.columns()` para layout, `st.progress()` para barras de score. El CSS personalizado se limita al header y títulos de sección — elementos simples donde el riesgo de conflicto es bajo.

### Para recordar en una entrevista
> "Al construir data apps con Streamlit, siempre prioriza los componentes nativos sobre HTML personalizado. Los componentes nativos son estables entre versiones, responsive por defecto y no colisionan con el sistema de estilos interno. El HTML personalizado es una vía de escape para casos muy específicos, no una herramienta de diseño general."

---

## #13 — Diseño de UI con tabs es antinatural para una decisión de flujo

**Fecha:** 06/04/2026
**Archivo:** `app/streamlit_app.py`
**Etiquetas:** `[UX]`

---

### Qué estaba pasando
Se propuso un diseño con dos tabs (`st.tabs()`) para ofrecer al usuario la opción de rellenar un formulario o escribir texto libre. El usuario rechazó el diseño porque no es natural: las tabs implican navegación libre entre opciones equivalentes, no una elección de flujo.

### Explicación del concepto técnico
Los **tabs** son un patrón de navegación: el usuario puede cambiar entre vistas en cualquier momento, lo que implica que ambas opciones son comparables y simultáneamente disponibles. Una **elección de flujo** es diferente: el usuario toma una decisión inicial que determina su camino. El patrón correcto para este caso es un **wizard de onboarding**: se hace una pregunta, el usuario elige, y aparece el formulario correspondiente. Las tabs transmiten el mensaje "puedes usar las dos cosas a la vez", que no es cierto aquí.

### Causa raíz
Pensamiento orientado a implementación en lugar de pensamiento orientado al usuario. `st.tabs()` es la forma más sencilla de mostrar dos opciones en Streamlit — una línea de código. La facilidad de implementación llevó a elegir el patrón técnicamente más sencillo sin preguntarse cuál sería el modelo mental del usuario al enfrentarse a la pantalla.

### Solución aplicada
Flujo de elección con dos botones grandes y una pregunta directa:
```
¿Cómo prefieres contarnos qué buscas?
[📋 Prefiero elegir]    [✍️ Prefiero escribirlo]
```
Al pulsar uno, aparece el formulario correspondiente. Es un patrón de decisión, no de navegación.

### Para recordar en una entrevista
> "En UX, distingue entre patrones de navegación (tabs, sidebars) y patrones de decisión (wizards, onboarding flows). Los primeros permiten moverse libremente entre estados. Los segundos guían al usuario por un camino. Usar el patrón equivocado crea fricción aunque técnicamente funcione. Siempre pregúntate: ¿el usuario necesita navegar o necesita decidir?"

---

---

## #14 — `searchNearby` sin `includedTypes` devuelve 0 para types de infraestructura
Fecha: 06/04/2026 | Archivo: `scripts/fetch_gp_raw.py` | Etiquetas: `[HTTP]` `[DATA]` `[API-VERSION]`

### Mensaje de error exacto
No hay error de código. El problema es silencioso: París aparece con 0 gasolineras, 0 supermercados, 0 farmacias cuando claramente tiene cientos.

### Qué estaba pasando
Se usó la estrategia "coste mínimo" para EDA: `searchNearby` sin especificar `includedTypes` (sin filtro de tipo). La API devuelve los 20 lugares más "prominentes" cerca de cada punto. Al hacer 5 llamadas con offsets se obtienen hasta ~100 lugares únicos por ciudad. Luego se extraen sus `types[]` y se cuentan.

El resultado: París tiene 100 lugares pero ninguno es una gasolinera — son museos, restaurantes, atracciones turísticas. Todas las ciudades muestran 0 en `gas_station`, `supermarket`, `pharmacy`, `atm`, `bank`.

### Explicación del concepto técnico
Google Places New API ordena los resultados de `searchNearby` por **prominencia** (*prominence*). La prominencia es una combinación de:
- Número de reseñas en Google Maps
- Valoración media
- Relevancia para búsquedas de usuarios

Una gasolinera en París tiene ~40 reseñas. El Louvre tiene ~300.000. La API devuelve el Louvre.

Esto es un **sesgo de popularidad** (*popularity bias*): la API refleja lo que los turistas y usuarios de Google Maps reseñan, no lo que existe geográficamente. Los lugares de infraestructura diaria (gasolineras, supermercados, farmacias, cajeros) son abundantes pero invisibles en este tipo de búsqueda.

### Causa raíz
La estrategia de búsqueda general sin filtro de type asume que la muestra de 100 lugares es representativa de todos los types. No lo es: está sesgada hacia lugares turísticos y gastronómicos con muchas reseñas.

### Qué tipos de datos se ven afectados

| Tipo de feature | ¿Funciona con búsqueda general? | Por qué |
|-----------------|--------------------------------|---------|
| Museos, restaurantes, bares, hoteles, spas, gimnasios | ✅ Sí | Tienen muchas reseñas — aparecen en el top-100 |
| Atracciones, parques, playas, mercados | ✅ Sí | La gente los reseña activamente |
| Gasolineras, farmacias, supermercados, bancos, paradas de bus | ❌ No | Pocas reseñas — no aparecen entre los más prominentes |
| Lavanderías, tintoreras, cerrajeros | ❌ No | Mismo motivo |

### Solución
Para features de infraestructura que importan en el modelo (modo "vivir una temporada"), usar **búsquedas dirigidas** con `includedTypes=[type]` específico. Solo se necesita para ~10-15 types clave:
`supermarket`, `pharmacy`, `hospital`, `atm`, `bank`, `bus_stop`, `subway_station`, `train_station`, `grocery_store`, `convenience_store`.

Para el resto (cultura, ocio, deporte, gastronomía), la búsqueda general es suficiente.

### Para recordar en una entrevista
> "Cuando uses APIs de lugares de interés como Google Places, ten en cuenta el sesgo de popularidad: la API no devuelve los lugares que existen sino los que los usuarios reseñan. Para features de infraestructura cotidiana (farmacias, supermercados, transporte) necesitas búsquedas dirigidas por tipo. Para features de ocio, cultura y gastronomía, una búsqueda general es suficiente porque esos lugares tienen alta densidad de reseñas. Siempre valida tus datos mirando si ciudades conocidas tienen valores razonables para tipos básicos."

---

## #15 — `UnicodeEncodeError` al ejecutar script con emojis en terminal Windows (CP1252)
Fecha: 06/04/2026 | Archivo: `scripts/fetch_gp_raw.py` | Etiquetas: `[ENV]` `[ENCODING]`

### Mensaje de error exacto
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 0: character maps to <undefined>
```

### Qué estaba pasando
El script usa `print("✓ .env cargado")`. El terminal de Windows usa por defecto la codificación CP1252 (Windows Latin-1). El símbolo `✓` (U+2713) no existe en CP1252. Python intenta convertirlo y falla.

### Explicación del concepto técnico
**Encoding** (codificación de caracteres) es el estándar que define cómo se representa un carácter como bytes en memoria/disco.

- **ASCII**: 128 caracteres (letras inglesas, números, símbolos básicos). No incluye tildes ni emojis.
- **CP1252** (Windows Latin-1): 256 caracteres. Añade tildes y caracteres europeos occidentales. No incluye símbolos como `✓`.
- **UTF-8**: hasta 1.112.064 caracteres. Incluye todos los idiomas, emojis y símbolos especiales. Es el estándar universal en sistemas modernos.

En Linux/Mac, el terminal usa UTF-8 por defecto. En Windows, el terminal (CMD/PowerShell) usa CP1252 por razones históricas de compatibilidad. Python hereda el encoding del terminal para la salida estándar (`stdout`).

### Causa raíz
Terminal Windows con encoding CP1252 + `print()` con caracteres fuera del rango CP1252.

### Solución aplicada
Añadir la variable de entorno `PYTHONUTF8=1` antes de ejecutar el script:
```bash
PYTHONUTF8=1 python scripts/fetch_gp_raw.py
```
Esta variable fuerza a Python a usar UTF-8 para todas las operaciones de I/O (entrada/salida), independientemente del encoding del sistema.

### Para recordar en una entrevista
> "En proyectos Python que corren en Windows, el encoding del terminal puede causar errores silenciosos o crashes al imprimir caracteres Unicode. La solución más limpia es `PYTHONUTF8=1` o `python -X utf8`. En producción (Linux/Docker), esto no es problema porque el sistema usa UTF-8 por defecto. Es un problema específico del entorno de desarrollo Windows."

---

## #16 — Pseudo-labels circulares — el modelo aprende nuestras reglas, no la realidad
Fecha: 08/04/2026 | Archivo: `notebooks/02_synthetic_profiles.ipynb` | Etiquetas: `[ML]` `[DATA]`

### Mensaje de error exacto
No es un error de código — es un error de diseño conceptual detectado en revisión.

### Qué estaba pasando
La función `compute_relevance()` calculaba el label (0-3) de cada par (usuario, ciudad) usando reglas manuales como:
```python
if perfil['importancia_coworking'] > 0.4:
    score += min(ciudad['coworkings'] / 20, 1.0) * perfil['importancia_coworking'] * 2
```
El modelo LightGBM entrenaba con esos labels y aprendía exactamente esas reglas. Al hacer predicciones, reproducía las reglas manuales — no descubría patrones nuevos en los datos.

### Explicación del concepto técnico
**Label leakage circular** ocurre cuando las etiquetas de entrenamiento están definidas por las mismas reglas que el modelo va a aprender. El modelo no aprende nada nuevo — memoriza la lógica del generador de labels.

Es como enseñarle matemáticas a alguien dándole las respuestas ya calculadas y pidiéndole que adivine la fórmula. Si las respuestas vienen de una calculadora que hace `a × 2`, el alumno aprende `a × 2`, no matemáticas reales.

En sistemas de recomendación, esto es especialmente peligroso porque el NDCG puede ser muy alto (≥0.99) y parecer que el modelo funciona bien, cuando en realidad solo está reproduciendo las reglas del diseñador.

### Causa raíz
Las etiquetas de entrenamiento se generaban con heurísticas manuales inventadas por el desarrollador, no con datos de comportamiento real de usuarios (clicks, reservas, ratings).

### Solución aplicada
Rediseño del notebook 02 (pendiente de implementar):
1. Eliminar los multiplicadores manuales (`× 2`, `/20`, `/10`)
2. Los labels se calculan como **ranking directo** de ciudades por sus datos reales
3. La ciudad con más features relevantes para un perfil gana label=3, sin reglas de ponderación inventadas
4. Los arquetipos fijos (8) se reemplazan por 24 dimensiones libres con pesos aleatorios

### Para recordar en una entrevista
> "Detectamos circular label leakage en nuestro sistema de pseudo-labels: el modelo aprendía las reglas heurísticas que definimos nosotros, no patrones reales de preferencias. El NDCG=0.9995 medía coherencia interna, no utilidad real. Lo documentamos como limitación conocida y rediseñamos el sistema de labels para derivarlos de rankings objetivos sobre datos reales, sin multiplicadores manuales."

---

## #17 — Arquetipos fijos generan perfiles sintéticos demasiado rígidos
Fecha: 08/04/2026 | Archivo: `notebooks/02_synthetic_profiles.ipynb` | Etiquetas: `[ML]` `[DATA]`

### Mensaje de error exacto
No es un error de código — es un error de diseño conceptual detectado al analizar perfiles reales de usuarios.

### Qué estaba pasando
El sistema generaba perfiles sintéticos basados en 8 arquetipos fijos: `nomada_digital`, `deportista_outdoor`, `familia_con_hijos`, etc. Cada arquetipo tenía pesos predefinidos para 11 dimensiones.

Al revisar perfiles reales de usuarios, se identificaron necesidades no representadas:
- Un nómada que sigue deportes de viento (kite en verano, ski en invierno)
- Alguien que elige ciudades por festivales de música o folklore
- Personas que valoran la autenticidad sobre el turismo masivo
- Influencers o creadores de contenido que priorizan el impacto visual

Ninguno de estos perfiles cabe en los 8 arquetipos originales.

### Explicación del concepto técnico
**Cobertura del espacio de preferencias** — un sistema de recomendación solo puede aprender a recomendar para los tipos de usuarios que ha visto durante el entrenamiento. Si los perfiles sintéticos solo cubren 8 arquetipos, el modelo no sabrá qué recomendar a usuarios que combinan características de varios arquetipos o tienen preferencias no representadas.

En Machine Learning esto se llama **distribución del entrenamiento vs distribución de producción**: si los datos de entrenamiento no representan bien la variedad de usuarios reales, el modelo tendrá bajo rendimiento con usuarios reales aunque tenga métricas altas en el dataset sintético.

### Causa raíz
Los 8 arquetipos se definieron antes de hablar con usuarios reales. Representaban intuiciones del diseñador, no la diversidad real de preferencias.

### Solución aplicada
Rediseño del sistema de perfiles (pendiente de implementar):
- Eliminar los 8 arquetipos como restricción de los pesos
- Pasar a 24 dimensiones independientes con pesos libres (0-1)
- Los arquetipos se mantienen solo como etiqueta descriptiva
- Los perfiles sintéticos se generan con combinaciones aleatorias de pesos, sin que el arquetipo restrinja qué dimensiones pueden tener valores altos

### Para recordar en una entrevista
> "Los arquetipos fijos en el entrenamiento crean un sesgo de distribución: el modelo aprende bien para los arquetipos que definimos pero puede fallar con usuarios reales que combinan características de múltiples arquetipos. La solución es generar perfiles sintéticos con dimensiones independientes y pesos libres, de modo que el espacio de entrenamiento cubra la diversidad real de combinaciones posibles."

---

---

## #18 — Budapest rent_1br_center = 343.396€ — moneda local HUF sin convertir a EUR

**Fecha:** 08/04/2026
**Archivo:** `src/processing/features.py`
**Etiquetas:** `[DATA]` `[MATCHING]`

---

### Mensaje de error exacto
No hay error de código. El problema es silencioso: Budapest aparece como la ciudad más cara del mundo con un alquiler de 343.396€/mes.

---

### Qué estaba pasando
Numbeo devuelve los precios en la moneda local de cada ciudad. Para Budapest, el florín húngaro (HUF). El campo `rent_1br_center` llegaba con un valor como `343396` (HUF) y el código lo trataba directamente como si fueran euros.

---

### Explicación del concepto técnico

**Normalización de moneda** es un paso obligatorio cuando se consolidan datos de precios de distintos países en un único DataFrame de comparación. Si no se hace esta conversión, los valores numéricos son incomparables: 100 HUF no es lo mismo que 100 EUR.

Los tipos de cambio son el ratio de conversión entre monedas:
```
100 HUF × (1 EUR / 400 HUF) = 0.25 EUR
```

En un proyecto de datos, hay dos enfoques:
- **API de tasas de cambio en tiempo real** (Fixer.io, Open Exchange Rates): preciso pero requiere clave y conexión.
- **Diccionario hardcodeado de tasas aproximadas**: suficiente si los datos no requieren precisión financiera y las tasas no cambian drásticamente (caso de NomadOptima).

---

### Causa raíz
El código en `features.py` asumía que todos los valores de Numbeo estaban ya en EUR. Esta asunción es correcta para ciudades de la eurozona (España, Francia, Portugal) pero incorrecta para países fuera de la eurozona (Hungría, Polonia, Serbia, Georgia, etc.).

---

### Solución aplicada

```python
# Diccionario de tasas de cambio a EUR (aproximadas, suficientes para comparación)
EUR_RATES = {
    "EUR": 1.0,
    "HUF": 0.00255,   # florín húngaro
    "PLN": 0.233,     # zloty polaco
    "CZK": 0.041,     # corona checa
    "RON": 0.201,     # leu rumano
    "BGN": 0.511,     # lev búlgaro
    "RSD": 0.0085,    # dinar serbio
    "GEL": 0.345,     # lari georgiano
    "USD": 0.92,      # dólar americano
    "MXN": 0.053,     # peso mexicano
    "COP": 0.00022,   # peso colombiano
    "ARS": 0.00095,   # peso argentino
    "UYU": 0.023,     # peso uruguayo
    "CLP": 0.00097,   # peso chileno
    "PEN": 0.247,     # sol peruano
    "GBP": 1.17,      # libra esterlina
    "SEK": 0.086,     # corona sueca
    "THB": 0.026,     # baht tailandés
    "IDR": 0.000057,  # rupia indonesia
    "MYR": 0.205,     # ringgit malayo
    "MAD": 0.091,     # dirham marroquí
    "AED": 0.250,     # dirham emiratí
    "VND": 0.000037,  # dong vietnamita
}

def to_eur(value, currency):
    """Convierte un valor de moneda local a EUR usando tasas aproximadas."""
    rate = EUR_RATES.get(currency, 1.0)
    return value * rate
```

---

### Para recordar en una entrevista

> "Cuando integras datos de precios de múltiples países en un mismo modelo, la conversión de moneda es un paso obligatorio de preprocessing. Sin ella, el modelo trata 343.396 HUF y 1.200 EUR como si fueran la misma magnitud — lo que hace que Budapest parezca miles de veces más cara que Madrid. La solución más pragmática para un MVP es un diccionario de tasas aproximadas hardcodeado, que es suficiente para comparaciones relativas entre ciudades. Para un producto financiero necesitarías tasas en tiempo real."

---

---

## #19 — Numbeo HTTP 429 Rate Limit para 12 ciudades

**Fecha:** 08/04/2026
**Archivo:** `src/ingestion/fetch_cities.py`, `scripts/refetch_numbeo.py`
**Etiquetas:** `[HTTP]` `[RATE-LIMIT]`

---

### Mensaje de error exacto
```
HTTP 429 Too Many Requests
```
Ciudades afectadas: Sevilla, Bucarest, Sofía, Belgrado, Cracovia, Tbilisi, Tallinn, Las Palmas, Medellín, Ciudad de México, Cartagena, Andorra.

---

### Qué estaba pasando
Al ingestar 36 ciudades seguidas, Numbeo detectó un volumen de peticiones superior al límite permitido por IP y devolvió 429 para las últimas 12 ciudades de la lista. El scraping se realizó demasiado rápido, sin pausas suficientes entre peticiones.

---

### Explicación del concepto técnico

**Rate Limiting** es un mecanismo de protección que los servidores implementan para evitar que un cliente haga demasiadas peticiones en un período de tiempo. Cuando se supera el límite, el servidor devuelve HTTP 429 (Too Many Requests).

Los rate limits pueden operar sobre distintos ejes:
- **Por IP**: X peticiones por segundo/minuto/hora desde la misma IP
- **Por API key**: X peticiones por día con la misma credencial
- **Por endpoint**: algunos endpoints tienen límites más estrictos que otros

Para Numbeo (que es scraping web, no una API oficial), el rate limit es por IP y se resetea cada 24 horas.

**Estrategias para manejar rate limits:**
1. **Backoff exponencial**: reintentar después de 2s, 4s, 8s, 16s...
2. **Sleep entre peticiones**: `time.sleep(2)` entre cada petición
3. **Fallback hardcodeado**: valores aproximados cuando la petición falla
4. **Retry al día siguiente**: programar re-ejecución cuando el límite se resetee

---

### Causa raíz
El script de ingesta hacía peticiones a Numbeo demasiado rápido al procesar 36 ciudades. El sleep entre peticiones era insuficiente para el volumen total.

---

### Solución aplicada

**Solución temporal (inmediata):** diccionario `NUMBEO_FALLBACK` con valores reales hardcodeados en EUR para las 12 ciudades afectadas.

```python
NUMBEO_FALLBACK = {
    "sevilla":       {"rent_1br_center": 1050, "meal_cheap": 12,  "quality_of_life": 168},
    "bucharest":     {"rent_1br_center": 620,  "meal_cheap": 7,   "quality_of_life": 175},
    "sofia":         {"rent_1br_center": 580,  "meal_cheap": 6,   "quality_of_life": 162},
    "belgrade":      {"rent_1br_center": 620,  "meal_cheap": 7,   "quality_of_life": 155},
    "krakow":        {"rent_1br_center": 680,  "meal_cheap": 7,   "quality_of_life": 170},
    "tbilisi":       {"rent_1br_center": 480,  "meal_cheap": 5,   "quality_of_life": 148},
    "tallinn":       {"rent_1br_center": 850,  "meal_cheap": 10,  "quality_of_life": 172},
    "las_palmas":    {"rent_1br_center": 950,  "meal_cheap": 11,  "quality_of_life": 165},
    "medellin":      {"rent_1br_center": 430,  "meal_cheap": 4,   "quality_of_life": 145},
    "mexico_city":   {"rent_1br_center": 510,  "meal_cheap": 5,   "quality_of_life": 142},
    "cartagena":     {"rent_1br_center": 380,  "meal_cheap": 4,   "quality_of_life": 135},
    "andorra":       {"rent_1br_center": 1100, "meal_cheap": 13,  "quality_of_life": 180},
}
```

**Solución definitiva (pendiente):** ejecutar `scripts/refetch_numbeo.py` cuando el rate limit se resetee (24 horas después). El script incluye `time.sleep(5)` entre peticiones.

---

### Para recordar en una entrevista

> "Al hacer scraping o llamadas masivas a APIs externas, el rate limiting es un problema inevitable que hay que diseñar desde el principio. Las buenas prácticas son: añadir sleep entre peticiones, implementar backoff exponencial en los reintentos, y siempre tener un fallback para cuando la fuente externa falle. En NomadOptima usamos un diccionario de valores aproximados hardcodeados como fallback de Numbeo — suficiente para un MVP donde los valores de coste no necesitan precisión financiera."

---

---

## #20 — Buenos Aires siempre en top 3 para cualquier perfil — coste_invertido = 1.0

**Fecha:** 08/04/2026
**Archivo:** `src/processing/features.py`, `notebooks/02_synthetic_profiles_v2.ipynb`
**Etiquetas:** `[ML]` `[DATA]` `[MATCHING]`

---

### Mensaje de error exacto
No hay error de código. El síntoma: para cualquier perfil de usuario (nómada digital, familia, deportista...), Buenos Aires aparece en el top 3 independientemente del perfil.

---

### Qué estaba pasando
El feature `coste_invertido` se calculaba como `1 - (coste / presupuesto_max)`. Cuando el coste de una ciudad es 0 (Buenos Aires no tenía datos en Numbeo), el resultado es `1 - 0 = 1.0`: la puntuación máxima posible en la dimensión de coste. El modelo interpretaba Buenos Aires como "la ciudad más barata del mundo".

---

### Explicación del concepto técnico

**Valores faltantes en features numéricas** son uno de los problemas más comunes en ML. El error típico es no distinguir entre:
- **0 como valor real**: "esta ciudad tiene 0 coworkings" (dato real)
- **0 como dato faltante**: "no tenemos datos de coste para esta ciudad" (ausencia de dato)

Cuando se aplica una transformación matemática sobre un 0-como-ausencia, el resultado puede ser extremo. En este caso, `1 - 0/2000 = 1.0` da la puntuación máxima posible, que es incorrecta.

La solución correcta es distinguir explícitamente ambos casos:
- Si el dato está disponible → calcular `1 - (coste / presupuesto)`
- Si el dato no está disponible → imputar un valor por defecto antes de calcular

---

### Causa raíz
Buenos Aires no tenía datos en `cities_raw.json` para las features de Numbeo. La función `compute_features()` usaba `ciudad.get('numbeo_rent_1br', 0)` — y como el key no existía, devolvía 0. Ese 0 se propagaba al cálculo de `coste_invertido`.

---

### Solución aplicada
Añadir Buenos Aires al diccionario `NUMBEO_FALLBACK` con valores reales aproximados:

```python
NUMBEO_FALLBACK["buenos_aires"] = {
    "rent_1br_center": 540,   # USD convertidos a EUR, aproximado 2024
    "meal_cheap": 4,
    "quality_of_life": 115    # índice bajo por inflación e inestabilidad
}
```

Y añadir un valor centinela para detectar ciudades sin datos:
```python
coste = ciudad.get('numbeo_rent_1br')
if coste is None or coste == 0:
    coste = NUMBEO_FALLBACK.get(ciudad['nombre'], {}).get('rent_1br_center', 1000)
```

---

### Para recordar en una entrevista

> "Los valores faltantes que se imputan como 0 son uno de los bugs más peligrosos en ML porque no producen errores — producen predicciones incorrectas que parecen válidas. La regla de oro es: nunca uses 0 como valor por defecto para datos faltantes en features continuas. Usa `np.nan` para marcar ausencias, luego decide la estrategia de imputación (media, mediana, valor de negocio) de forma explícita y documentada."

---

---

## #21 — Fuerteventura label=0 siempre — OSM Overpass falla en islas

**Fecha:** 08/04/2026
**Archivo:** `src/ingestion/fetch_cities.py`, `src/processing/features.py`
**Etiquetas:** `[DATA]` `[ML]`

---

### Mensaje de error exacto
No hay error de código. El síntoma: Fuerteventura recibe label=0 (irrelevante) para todos los perfiles, incluso perfiles de kite/windsurf donde debería ser la ciudad más relevante.

---

### Qué estaba pasando
Las queries de OpenStreetMap (Overpass API) para Fuerteventura devolvían 0 en todas las features `osm_*`: 0 hospitales, 0 bares, 0 restaurantes, 0 parques. El problema no es que Fuerteventura no tenga esas cosas — es que la query de OSM fallaba silenciosamente para el área geográfica de la isla.

---

### Explicación del concepto técnico

**Dependencia de una sola fuente de datos** es un riesgo de diseño en pipelines de ML. Cuando una fuente falla, todas las features derivadas de esa fuente valen 0 — y el modelo interpreta esos ceros como "esta ciudad no tiene nada", no como "no tenemos datos de esta ciudad".

En el caso de islas, Overpass API puede fallar por:
- El área de búsqueda no coincide exactamente con el polígono de la isla
- El servidor Overpass tiene timeouts para áreas geográficas complejas
- La ciudad está en una isla pero la query busca en un radio que incluye agua

---

### Causa raíz
La query de Overpass usa un radio fijo en kilómetros desde el centro de la ciudad. Para Fuerteventura, ese radio incluía mucha área de oceáno, lo que podía causar timeout o resultados vacíos.

---

### Solución aplicada

**Dos cambios en paralelo:**

1. **Google Places como fuente secundaria para features críticas:**
```python
# Cuando OSM falla (todos = 0), usar GP genérico como proxy
if city_osm_restaurant == 0:
    city_gp_restaurant = gp_data.get('restaurant', {}).get('count', 0)
```

2. **Capping de features (Feature Clamping):**
```python
# Sin capping: Madrid(600) vs Fuerteventura(37) → siempre Madrid
# Con capping: min(600, 80) = 80 = min(80, 80) = 80 → empate en "suficientes"
city_gp_restaurant_capped = min(city_gp_restaurant, 80)
city_gp_coworking_capped  = min(city_gp_coworking, 15)
city_gp_bar_capped        = min(city_gp_bar, 60)
```

**Resultado:** similitud de Fuerteventura para perfil kite mejoró de 0.34 a 0.39.

---

### Para recordar en una entrevista

> "En pipelines de datos con múltiples fuentes, siempre tenemos una fuente primaria y una fuente secundaria para features críticas. Cuando la fuente primaria falla silenciosamente (devuelve 0 en lugar de error), el modelo interpreta la ausencia como 'esta ciudad es mala', no como 'no tenemos datos'. El patrón correcto es: detectar la ausencia explícitamente, y si la fuente primaria falla, activar el fallback a la fuente secundaria."

---

---

## #22 — Warsaw #1 para perfiles kite/windsurf — dimensión deporte demasiado genérica

**Fecha:** 08/04/2026
**Archivo:** `src/processing/features.py`, `notebooks/02_synthetic_profiles_v2.ipynb`
**Etiquetas:** `[ML]`

---

### Mensaje de error exacto
No hay error de código. El síntoma: para un perfil con alta importancia de kite y windsurf, Warsaw aparece en #1 y Tarifa en #3.

---

### Qué estaba pasando
La dimensión `user_imp_deporte` era genérica e incluía todos los deportes: gym, fitness, yoga, kite, surf, esquí, tenis, ciclismo. Warsaw tiene muchos centros deportivos urbanos (gimnasios, piscinas, tenis). Al activar la dimensión "deporte", el modelo activaba también las features de gym para Warsaw, que es una ciudad con muchos gimnasios modernos.

---

### Explicación del concepto técnico

**Granularidad de features** es una decisión crítica en el diseño de sistemas de recomendación. Una feature demasiado genérica agrupa contextos muy distintos bajo el mismo número. El modelo no puede distinguir si el usuario quiere deporte en el agua o deporte en un gimnasio.

Este problema se llama **feature aliasing**: dos cosas diferentes (kitesurf y gym) tienen el mismo nombre en el modelo, y por tanto el modelo las trata como equivalentes.

La solución es **decomposición de dimensiones**: dividir una dimensión genérica en sub-dimensiones específicas que capturen las distintas intenciones del usuario.

---

### Causa raíz
Al diseñar las 24 dimensiones del formulario, "Deporte activo" se modeló como una sola dimensión numérica. Esto era insuficiente porque los deportes de agua, montaña y urbanos tienen features de ciudad completamente distintas y son incompatibles entre sí.

---

### Solución aplicada

Split de la dimensión deporte en 3 sub-dimensiones:

```python
# ANTES — una sola dimensión
"user_imp_deporte": 0.9   # ¿deporte? → activa gym, kite, ski, ciclismo... todo

# DESPUÉS — tres sub-dimensiones independientes
"user_imp_deporte_agua":    0.9   # kite, surf, windsurf, snorkel, kayak, playa
"user_imp_deporte_montana": 0.0   # ski, escalada, senderismo, aventura
"user_imp_deporte_urbano":  0.1   # gym, fitness, tenis, piscina, ciclismo
```

Cada sub-dimensión se cruza solo con las features de ciudad relevantes:
- `deporte_agua` → `city_gp_surf_school`, `city_gp_marina`, `city_gp_beach`
- `deporte_montana` → `city_gp_ski_resort`, `city_gp_snowpark`, `city_osm_hiking`
- `deporte_urbano` → `city_gp_gym`, `city_gp_fitness_center`, `city_gp_tennis`

**Resultado:** Tarifa #1 (cosine_sim=0.5054), Fuerteventura #2 (0.4864) para perfil kite ✓

---

### Para recordar en una entrevista

> "La granularidad de las dimensiones es crítica para la precisión de un sistema de recomendación. Si agrupas bajo 'deporte' tanto el kitesurf como el gimnasio, el modelo no puede distinguir qué tipo de deporte importa al usuario. La solución es decomposición de dimensiones: dividir una categoría genérica en sub-categorías semánticamente homogéneas. Esto aumenta el número de features pero mejora drásticamente la precisión para perfiles específicos."

---

---

## #23 — `background_gradient()` falla en columna de texto `city_idioma_nativo`

**Fecha:** 08/04/2026
**Archivo:** `scripts/generate_eda_html.py`, `notebooks/01_eda_36ciudades.ipynb`
**Etiquetas:** `[DATA]` `[ENV]`

---

### Mensaje de error exacto
```
TypeError: unsupported operand type(s) for -: 'str' and 'float'
```
O variante:
```
ValueError: could not convert string to float: 'Español'
```

---

### Qué estaba pasando
Al intentar generar el heatmap de colores con `df.style.background_gradient()`, pandas intentaba calcular gradientes de color para todas las columnas del DataFrame. La columna `city_idioma_nativo` contiene strings ('Español', 'Francés', 'Portugués'...) y pandas no puede calcular un gradiente numérico sobre texto.

---

### Explicación del concepto técnico

**Pandas Styler** es una API de pandas que permite aplicar estilos visuales (colores, formatos) a DataFrames para su exportación a HTML. La función `background_gradient()` calcula el color de cada celda en función de su valor numérico relativo al mínimo y máximo de la columna.

Cuando hay columnas de texto, pandas no puede calcular ese ratio y lanza un error de tipo, porque intentar restar o dividir strings genera TypeError.

---

### Causa raíz
Al añadir `city_idioma_nativo` como columna de texto al DataFrame de features, el código de generación de HTML que aplicaba `background_gradient()` a todo el DataFrame no estaba preparado para columnas no numéricas.

---

### Solución aplicada

```python
# Separar columnas numéricas de columnas de texto
num_cols = df.select_dtypes(include='number').columns.tolist()

# Aplicar gradient solo a columnas numéricas
styled = (
    df.style
    .background_gradient(cmap='RdYlGn', subset=num_cols)
    .format({col: '{:.2f}' for col in num_cols})
)
```

---

### Para recordar en una entrevista

> "Al trabajar con DataFrames mixtos (columnas numéricas + texto), siempre segmenta las operaciones por tipo de dato. Pandas permite hacer esto con `df.select_dtypes(include='number')`. El error típico es aplicar una operación numérica a todo el DataFrame sin filtrar. En producción, añadir una validación de tipos antes de cualquier operación de estilo o normalización evita que un campo de texto nuevo rompa silenciosamente el pipeline."

---

---

## #24 — `UnicodeEncodeError` al imprimir símbolo checkmark en features.py (Windows CP1252)

**Fecha:** 08/04/2026
**Archivo:** `src/processing/features.py`
**Etiquetas:** `[ENV]` `[ENCODING]`

---

### Mensaje de error exacto
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 0: character maps to <undefined>
```

---

### Qué estaba pasando
El archivo `features.py` usaba el símbolo `✓` (U+2713) en mensajes de log como `print("✓ Features construidas")`. En el terminal de Windows (CP1252), este símbolo no existe y Python lanzaba UnicodeEncodeError al intentar imprimirlo.

Este error es idéntico conceptualmente al #15 (mismo símbolo, mismo encoding), pero ocurrió en un archivo distinto (`features.py` vs `fetch_gp_raw.py`).

---

### Causa raíz
Uso de símbolo Unicode fuera del rango CP1252 en código Python que se ejecuta desde terminal Windows.

---

### Solución aplicada
Reemplazar el símbolo `✓` con texto ASCII equivalente `[OK]`:

```python
# ANTES
print("✓ Features construidas correctamente")

# DESPUÉS
print("[OK] Features construidas correctamente")
```

El texto `[OK]` es semánticamente equivalente, compatible con todos los encodings y legible en cualquier terminal.

---

### Para recordar en una entrevista

> "En proyectos que deben ejecutarse en Windows y Linux, evita símbolos Unicode decorativos (checkmarks, emojis, flechas especiales) en los mensajes de consola. Usa ASCII puro para los logs del sistema. Los emojis están bien en notebooks Jupyter (que abren el archivo con UTF-8), pero en scripts que se ejecutan desde terminal Windows pueden causar UnicodeEncodeError que rompe la ejecución."

---

---

## #25 — Celdas de notebook sin IDs — NotebookEdit fallaba al editar

**Fecha:** 08/04/2026
**Archivo:** `notebooks/01_eda_36ciudades.ipynb`, `notebooks/02_synthetic_profiles_v2.ipynb`
**Etiquetas:** `[ENV]`

---

### Mensaje de error exacto
```
KeyError: 'id'
```
O variante:
```
ValueError: Cell does not have an 'id' field required by nbformat >= 4.5
```

---

### Qué estaba pasando
Al intentar editar celdas específicas de un notebook con la herramienta NotebookEdit, el proceso fallaba porque las celdas no tenían el campo `id` requerido por el formato nbformat 4.5+. Los notebooks creados programáticamente (con scripts Python que generaban el JSON directamente) no incluían este campo obligatorio.

---

### Explicación del concepto técnico

**nbformat** es el estándar de formato para los archivos `.ipynb` (Jupyter Notebooks). El formato es JSON con una estructura definida. A partir de la versión 4.5 del estándar (Jupyter 6.0+), cada celda debe tener un campo `id` — un identificador único UUID de 8 caracteres.

Sin este campo, las herramientas que manipulan notebooks (JupyterLab, nbformat, herramientas de edición automatizadas) no pueden identificar de forma única cada celda para editar, mover o referenciar.

---

### Causa raíz
Los notebooks se crearon con scripts Python que construían el JSON directamente sin usar la librería `nbformat`, que añade automáticamente los IDs. El JSON resultante era válido pero incompleto para el estándar 4.5+.

---

### Solución aplicada
Script Python que recorre todas las celdas del notebook y añade UUIDs donde faltan:

```python
import json, uuid

def add_cell_ids(notebook_path):
    """Añade IDs únicos a todas las celdas del notebook que no los tengan."""
    with open(notebook_path, encoding='utf-8') as f:
        nb = json.load(f)

    modified = False
    for cell in nb.get('cells', []):
        if 'id' not in cell:
            cell['id'] = str(uuid.uuid4())[:8]
            modified = True

    if modified:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"[OK] IDs añadidos a {notebook_path}")
    else:
        print(f"[OK] {notebook_path} ya tenía IDs en todas las celdas")
```

---

### Para recordar en una entrevista

> "Cuando creas notebooks programáticamente con Python, usa siempre la librería `nbformat` en lugar de construir el JSON manualmente. `nbformat` gestiona automáticamente los campos obligatorios del estándar (versión, IDs de celda, metadata). El JSON manual puede parecer válido pero fallar en herramientas que requieren el estándar completo. Si heredas notebooks sin IDs, el fix es simple: recorrer las celdas y añadir UUIDs con `uuid.uuid4()`."

---

---

## #26 — Sesgo hacia ciudades grandes en perfiles sintéticos v2

**Fecha:** 08/04/2026
**Archivo:** `notebooks/02_synthetic_profiles_v2.ipynb`
**Etiquetas:** `[ML]` `[DATA]`

---

### Mensaje de error exacto

No es un error de código sino un error conceptual de diseño. No hay traceback — el código ejecutaba sin fallos pero las recomendaciones eran incorrectas.

---

### Qué estaba pasando

Los perfiles sintéticos usaban `beta(0.5, 0.5)` independiente por cada una de las 26 dimensiones de usuario. La distribución beta con alpha=0.5 y beta=0.5 tiene forma de U: concentra los valores cerca de 0 y cerca de 1, con pocos valores en el rango medio. Con 26 dimensiones independientes, la suma media de importancias era ~12.99/26 (~50%). La mayoría de usuarios tenían entre 10 y 15 dimensiones simultáneamente con valores altos.

Síntoma observable: ciudades grandes con buena cobertura general (Berlín, Warsaw, Budapest) aparecían en el top para casi todos los perfiles de usuario, incluyendo kite surfers y esquiadores. Tarifa y Fuerteventura nunca aparecían.

---

### Explicación del concepto técnico (desde cero)

En sistemas de recomendación, el **cosine similarity** mide el ángulo entre dos vectores: el vector de preferencias del usuario y el vector de features de la ciudad. La fórmula es:

```
cosine_sim(u, c) = (u · c) / (||u|| × ||c||)
```

Donde `u · c` es el producto punto: suma de `u[i] × c[i]` para cada dimensión `i`.

El problema con vectores de usuario "densos" (muchas dimensiones altas):

- Tarifa tiene scores **altos** en 4-6 features de deporte acuático: `gp_surf_school`, `gp_beach`, `gp_marina`, `gp_snorkeling`. En el resto de dimensiones tiene valores bajos.
- Berlín tiene scores **medios** en 40-50 features distintas: `gp_restaurant`, `gp_museum`, `gp_gym`, `gp_park`, `gp_coworking`...

Cuando el usuario tiene 13 dimensiones altas simultáneamente (gastronomía=0.8, cultura=0.9, naturaleza=0.7, deporte=0.8, ocio=0.9...), el producto punto acumula más puntos en Berlín porque tiene "algo de todo" en muchas dimensiones, aunque en ninguna destaque. Tarifa solo acumula puntos en 4-6 dimensiones, aunque en esas sea la mejor del mundo.

Este fenómeno tiene nombre técnico: **popularity bias** combinado con **complexity bias** — el modelo aprende a favorecer items con alta cobertura dimensional sobre items especializados.

---

### Causa raíz

Independencia de las 26 dimensiones + distribución U-shaped (`beta(0.5, 0.5)`) = perfiles de usuario estadísticamente incoherentes. En la realidad, un usuario que ama el kite surf no tiene simultáneamente 12 otras prioridades igualmente altas. El diseño sintético no modelaba la **coherencia interna del perfil**.

---

### Solución aplicada

`notebooks/02_synthetic_profiles_v3.ipynb` con 14 arquetipos de usuario. Cada arquetipo define explícitamente qué dimensiones son HIGH, MEDIUM o LOW:

```python
ARQUETIPOS = {
    "kite_surf": {
        "distribucion": {
            "HIGH":   ["deporte_agua", "clima", "naturaleza"],         # beta(8, 2) → 0.75-0.99
            "MEDIUM": ["gastronomia", "movilidad", "alojamiento"],     # beta(4, 4) → 0.35-0.65
            "LOW":    ["cultura", "vida_nocturna", "educacion_adultos"] # beta(1.5, 6) → 0.05-0.30
        },
        "proporcion": 0.07   # 7% de los usuarios generados
    },
    # ... 13 arquetipos más
}
```

El 70% de los usuarios generados tienen un arquetipo definido. El 30% restante son perfiles mixtos con un techo máximo de 0.65 en cualquier dimensión.

Resultado esperado tras ejecutar v3:
- Tarifa → top 3 para usuarios kite_surf
- Chamonix → top 3 para usuarios ski
- Tbilisi → top 3 para usuarios nomada_barato
- Berlín → top 3 para usuarios cultura_arte y ejecutivo_cosmopolita

---

### Para recordar en una entrevista

> "En sistemas de recomendación basados en contenido, la calidad del dataset sintético es tan crítica como el algoritmo. Un perfil de usuario generado con distribuciones independientes por dimensión no es realista: en la práctica, los usuarios tienen preferencias coherentes y especializadas, no 13 prioridades altas simultáneas. El problema resultante se llama popularity bias o complexity bias: el modelo aprende a recomendar items con alta cobertura dimensional (ciudades grandes) sobre items especializados (destinos nicho). La solución es diseñar perfiles sintéticos con arquetipos explícitos donde cada dimensión tiene una distribución condicionada al perfil del usuario."

---

## #27 — Estado de Git inconsistente: archivos staged con versión antigua + modificaciones encima sin staged
08/04/2026 | Repo NomadOptima | Etiquetas: [VCS] [CONFIG]

### Síntomas
- `git status` mostraba los mismos archivos en "Changes to be committed" Y en "Changes not staged"
- Si se hacía commit, se hubieran subido versiones antiguas de los archivos
- Archivos generados (city_features.csv, HTMLs, notebooks) sin proteger en .gitignore
- 1 commit local sin pushear encima del que había nuevas capas sin commitear

### Qué estaba pasando
Se hizo `git add` de varios archivos en un punto del desarrollo. Luego se siguió trabajando sobre esos mismos archivos durante horas sin volver a ejecutar `git add`. El resultado es que el staging area (zona de preparación) tenía una versión desactualizada de los archivos mientras que el working directory tenía la versión real.

### Explicación del concepto técnico
Git tiene tres zonas: **working directory** (tus archivos reales), **staging area** (lo que has marcado para el próximo commit con `git add`) y **repositorio** (los commits ya guardados). Cuando modificas un archivo después de haberlo añadido al staging, Git no actualiza el staging automáticamente. Tienes que volver a hacer `git add` para que el staging refleje la versión actual. Si no lo haces y haces commit, el commit contiene la versión antigua.

### Causa raíz
Sesión de desarrollo larga con `git add` inicial y muchas modificaciones posteriores sin actualizarlo.

### Solución aplicada
Ver sección 18 de LEARNING.md — método completo paso a paso.

### Para recordar en una entrevista
> "El staging area de Git es una fotografía, no un enlace vivo. Cuando modificas un archivo ya añadido al staging, tienes que volver a hacer `git add` para que la fotografía se actualice. Un `git status` siempre antes de commitear te evita subir versiones antiguas."

---

## #28 — Cargos €404.86 en Google Cloud por bucle autónomo de Claude Code durante incidente Anthropic

08/04/2026 | `src/ingestion/fetch_cities.py` | Etiquetas: [ENV] [HTTP] [API-VERSION] [RATE-LIMIT]

### Mensaje de error exacto

No hay traceback Python. El incidente se manifestó como cargos en Google Cloud y errores en los logs de Claude Code:
```
{"type":"error","error":{"type":"overloaded_error","message":"Overloaded"}}
HTTP 529 — Anthropic API overloaded
```

### Qué estaba pasando

Claude Code ejecutó `fetch_cities.py` de forma autónoma durante ~6 horas mientras Carlos dormía. Ejecuciones registradas en el JSONL de sesión:

| Hora España | Evento |
|-------------|--------|
| 19:12 | 1ª ejecución — inicio normal |
| 19:13 | 2ª ejecución — reintento automático 39 segundos después |
| 02:10 | 3ª ejecución — mientras Carlos dormía |
| 08:30 | Error 529 "overloaded_error" de Anthropic |
| 08:35 | Segundo error 529 |
| 08:37 | Carlos interrumpió manualmente |

Coste previsto: ~€42 (cubierto por créditos gratuitos). Coste real: **€404.86** (Nearby Search €395.45 + Text Search €9.41). Los datos no se completaron: `da_nang` vacío, `dakhla` parcial.

### Explicación del concepto técnico

**HTTP 529 Overloaded:** código de error propio de Anthropic que indica que sus servidores están saturados. Diferente del 429 (rate limit del cliente) — el 529 viene del lado del servidor. Cuando el agente recibió el 529, perdió capacidad de tomar decisiones pero el proceso `fetch_cities.py` ya lanzado continuó en segundo plano acumulando cargos.

**Budget Alert vs Budget Cap:** Google Cloud permite configurar alertas de presupuesto, pero por defecto solo envían notificaciones por email. Para que realmente corten el gasto hay que conectar la alerta a una Cloud Function via Pub/Sub que desactive la Billing Account automáticamente. Carlos tenía la alerta configurada pero no el corte automático.

### Causa raíz

Tres factores simultáneos:
1. Claude Code sin límite de reintentos configurado
2. Incidente de servicio Anthropic (529) que dejó el proceso sin supervisión
3. Budget Alert de Google Cloud sin mecanismo de corte automático

### Solución aplicada

- Billing de Google Cloud desactivado como emergencia
- Reclamación abierta ante Google Cloud y Anthropic con logs de sesión como evidencia
- `da_nang` excluido del dataset definitivamente
- Nueva regla en memoria: cero reintentos automáticos, scripts de APIs de pago los ejecuta Carlos

### Para recordar en una entrevista

> "Uno de los riesgos reales de los agentes de IA autónomos es el bucle de ejecución involuntario sobre APIs de pago. Las buenas prácticas son tres: primero, configurar un Budget Cap real en Google Cloud (no solo una alerta); segundo, implementar un contador de peticiones en el propio script que lance una excepción al superar un máximo; tercero, prohibir reintentos automáticos en el agente sin aprobación explícita del usuario. En este proyecto, un incidente de servicio de Anthropic (HTTP 529) dejó un proceso sin supervisión durante 6 horas generando €404 de cargos — la combinación de tres fallos independientes que por separado eran manejables pero juntos fueron costosos."

---

---

## #32 — Da_Nang: GP devuelve 0 en todos los features para Vietnam

**Fecha:** 09/04/2026
**Archivo:** `data/processed/city_features.csv`, `src/processing/features.py`
**Etiquetas:** `[DATA]`

---

### Mensaje de error exacto
No hay error explícito — el dato es silenciosamente incorrecto:
```
Da_Nang: todos los features GP = 0 (gp_restaurant=0, gp_bar=0, gp_gym=0...)
```
Detectado en EDA Fase 2: notebook `01b_eda_fase2_ciudades.ipynb`, bloque de "zeros heatmap".

---

### Qué estaba pasando

Da_Nang fue añadida al dataset como ciudad representativa de Vietnam (playa, barata, surf). Al ingestar los datos con `fetch_cities.py`, la Google Places API no devolvió resultados para prácticamente ninguna categoría. El JSON de Da_Nang existe en `data/raw/` pero sus secciones de `google_places` están vacías o con count=0.

Los datos de OSM y Numbeo sí funcionaron parcialmente, pero sin GP las features clave (restaurantes, coworkings, deportes) quedan a cero.

---

### Explicación del concepto técnico

**¿Por qué GP no devuelve resultados para algunas ciudades?**

Google Places API usa una query de búsqueda por radio desde las coordenadas de la ciudad. En ciudades asiáticas con nombres en caracteres locales, la geocodificación puede fallar o devolver un radio demasiado pequeño que no cubre la zona urbana real. Además, la cobertura de datos de GP no es uniforme globalmente — las ciudades del sudeste asiático tienen sistemáticamente menos Places indexados que las europeas o americanas.

**¿Qué es un "fallo silencioso" en un pipeline de ML?**

Un fallo silencioso ocurre cuando el dato parece estar presente (el JSON existe, los campos existen con valor 0) pero el valor es incorrecto (0 no significa "no tiene restaurantes", significa "la API no los encontró"). Es el tipo de error más peligroso en ML porque el modelo lo interpreta como señal real, no como dato ausente.

---

### Causa raíz

La Google Places API (New) no tiene cobertura suficiente en Vietnam para el radio de búsqueda configurado en `fetch_cities.py`. El tipo de búsqueda `searchNearby` con radio 5.000m no captura los establecimientos de Da_Nang.

---

### Solución aplicada

Ciudad eliminada del dataset en `src/processing/features.py`:
```python
for name, data in cities_raw.items():
    # Da_Nang: GP no devuelve resultados para Vietnam con la config actual
    if name == "Da_Nang":
        continue
```

Dataset resultante: **54 ciudades × 149 features** (antes 55 × 158).

### Para recordar en una entrevista

> "Los fallos silenciosos son el tipo de error más peligroso en pipelines de ML porque no generan excepciones — simplemente introducen datos incorrectos que el modelo aprende como si fueran reales. En NomadOptima, Da_Nang tenía todos los features de Google Places a cero, no porque fuera una ciudad sin infraestructura sino porque la API no encontró resultados. Sin un proceso de validación de calidad (EDA: porcentaje de ceros por ciudad y feature), este dato habría sesgado el modelo hacia ciudades con mejor cobertura de API."

---

## #33 — 8 features GP con todos los valores = 0 en las 54 ciudades

**Fecha:** 09/04/2026
**Archivo:** `data/processed/city_features.csv`, `src/processing/features.py`
**Etiquetas:** `[DATA]` `[ML]`

---

### Features afectadas

```
city_gp_nature_reserve   → gp("nature_reserve")
city_gp_climbing_gym     → gp("climbing_gym")
city_gp_kayak            → gp("kayak_rental")
city_gp_tapas            → gp("tapas_bar")
city_gp_bicycle_rental   → gp("bicycle_rental")
city_gp_mental_health    → gp("mental_health")
city_gp_scenic_point     → gp("scenic_point")
city_gp_tour_operator    → gp("tour_operator")
```

---

### Qué estaba pasando

En EDA Fase 2 se identificó que estas 8 features tenían `sum() == 0` en las 54 ciudades del dataset. Ninguna ciudad registraba un solo establecimiento en ninguna de estas categorías.

---

### Explicación del concepto técnico

**¿Por qué una feature con todos los valores = 0 es un problema para ML?**

Una feature constante (siempre el mismo valor) tiene **varianza = 0**. No aporta información al modelo porque no puede discriminar entre ciudades. En términos matemáticos: si `f(ciudad_A) = f(ciudad_B) = 0` para todas las ciudades, esa feature no contribuye al gradiente en LightGBM y no puede mover el ranking.

Además, en Cosine Similarity, una feature a 0 en todas las ciudades no afecta al score (multiplicar por 0 da 0), pero ocupa espacio y puede confundir si en el futuro se añaden ciudades con valor no-nulo.

**Causa probable:** Los GP types usados (`nature_reserve`, `climbing_gym`, `kayak_rental`, etc.) no existen como categorías reconocibles en la Google Places API o se buscan con nombres distintos a los que la API espera. La API devuelve 0 resultados cuando el `type` no está en el catálogo oficial.

---

### Solución aplicada

**En el MVP:** eliminadas del `rows.append({})` en `features.py` y del `DIMENSION_MAP`. Dataset reducido de 158 a 149 features.

**POST-PRESENTACION** (no urgente): investigar los GP types correctos en la API documentation y añadir las búsquedas correctas a `fetch_cities.py`. Por ejemplo:
- `kayak_rental` → probar `water_sports_equipment_rental`
- `tapas_bar` → probar `spanish_restaurant` + text search
- `nature_reserve` → probar como OSM `leisure=nature_reserve` en lugar de GP

### Para recordar en una entrevista

> "Una de las validaciones más básicas del pipeline de features es verificar la varianza de cada feature: si una columna tiene varianza = 0 (todos los valores iguales), no aporta señal al modelo. En un pipeline con múltiples fuentes de datos externas, esto ocurre frecuentemente cuando los tipos de búsqueda en la API no coinciden exactamente con el catálogo oficial. La detección se hace en el EDA con un simple `df[col].sum() == 0`."

---

## #34 — city_internet_mbps: 43/54 ciudades = 0 (dato ausente, no velocidad = 0)

**Fecha:** 09/04/2026
**Archivo:** `data/processed/city_features.csv`, `src/processing/features.py`
**Etiquetas:** `[DATA]`

---

### El problema

```python
"city_internet_mbps": spd.get("fixed_download_mbps") or 0
```

`spd` es el dict de Speedtest (Ookla). Solo devuelve datos para el 20% de las ciudades del dataset porque la fuente de datos de Ookla es a nivel de **país**, no de ciudad.

Resultado: `city_internet_mbps = 0` para 43/54 ciudades. Como 0 es un valor legítimo en la escala de velocidad, el modelo interpreta "dato no disponible" como "internet = 0 Mbps" — lo que penaliza incorrectamente ciudades como Budapest, Tbilisi o Chiang Mai (conocidas por tener buen internet para nómadas).

---

### Explicación del concepto técnico

**¿Cuál es la diferencia entre "dato ausente" y "valor = 0"?**

Este es uno de los problemas más comunes en feature engineering con datos reales:
- **Valor = 0**: la ciudad realmente tiene 0 de esa propiedad (playa = 0 significa "no tiene playa")
- **Dato ausente / NaN**: no tenemos información sobre ese valor — podría ser 0, podría ser 100

Cuando rellenamos un NaN con 0 sin documentarlo, estamos imponiendo una suposición falsa que el modelo aprende como real.

---

### Por qué ocurre

La API de Speedtest (Ookla) que se usa en `fetch_cities.py` devuelve estadísticas agregadas por país. El campo `fixed_download_mbps` solo aparece en el JSON cuando Ookla tiene suficientes mediciones de velocidad fija para ese país. Para muchos países con menos usuarios de la app Ookla (Marruecos, Vietnam, Colombia, Georgia), el campo está ausente.

---

### Solución aplicada

**En el MVP:** feature eliminada de `features.py`. El nomada digital ya tiene señal a través de `city_gp_coworking`, `city_gp_tech_hub` y `city_coworking_osm`.

**POST-PRESENTACION** (no urgente): sustituir por **Ookla Global Fixed Broadband dataset** (dataset CSV descargable en SpeedTest.net/Insights/Research, disponible por tile geográfico). Permite asignar velocidad media por coordenadas de ciudad, con cobertura global mucho mejor.

### Para recordar en una entrevista

> "Un error clásico en preprocessing: rellenar valores ausentes con cero cuando el cero tiene un significado real en esa feature. Si la velocidad de internet es 0 Mbps puede significar 'sin internet' (valor real) o 'no tenemos el dato' (ausente). Sin documentar la diferencia, el modelo penaliza ciudades por falta de datos en lugar de por falta de infraestructura. La solución correcta es usar `np.nan` para datos ausentes y solo usar 0 para ausencia real confirmada."

---

## #35 — Validación cualitativa kite_surf: recomienda Buenos Aires y Berlin en lugar de Tarifa y Fuerteventura

**Fecha:** 10/04/2026
**Archivo:** `data/processed/city_features.csv`, `notebooks/03_train_model.ipynb`
**Etiquetas:** `[DATA]` `[ML]`

### Mensaje de error exacto

No es un error de código, sino de validación cualitativa. Perfil `kite_surf` (deporte_agua=0.99, naturaleza=0.90, clima=0.85):
```
Ranking esperado: Tarifa, Fuerteventura, Dakhla, Essaouira, Bali
Ranking real:     Buenos_Aires, Berlin, Lima, Warsaw, Amsterdam
```

### Qué estaba pasando

El modelo (`NDCG@5 = 0.9631`) aprende a rankear ciudades a partir del **producto escalar entre el perfil de usuario y las features de ciudad**. Si las features de ciudad no capturan bien el kite/surf, el modelo no puede recomendar las ciudades correctas aunque sus métricas sean excelentes.

Tarifa y Fuerteventura son ciudades pequeñas y especializadas. Sus features de Google Places (`gp_surf_spot`, `gp_kite_school`, `gp_water_sports`) devuelven pocos resultados o cero porque:
- Google Places New API no tiene cobertura completa para actividades de nicho en poblaciones pequeñas
- Los tags de OSM para surf/kite están incompletos para estas ciudades en el dataset actual

### Explicación del concepto técnico

**El problema de cobertura en datos geoespaciales**: Las APIs de puntos de interés (Google Places, OpenStreetMap) tienen sesgos de cobertura — las grandes ciudades cosmopolitas tienen mejor cobertura que destinos especializados pequeños. Un kite school en Tarifa puede no aparecer en GP porque no está registrado o tiene nombre en otro idioma.

**Garbage in, garbage out**: Con `NDCG@5 = 0.9631`, el modelo aprende perfectamente de los datos que tiene. Si los datos de entrada son incorrectos (Tarifa parece pobre en actividades acuáticas por falta de datos GP), el modelo aprende esa "verdad incorrecta".

**Validación cualitativa vs cuantitativa**: NDCG mide si el modelo ordena correctamente dado su entrenamiento. No detecta si los labels de entrenamiento reflejan la realidad. Por eso la validación cualitativa es esencial — es la única forma de detectar problemas en los datos de entrada.

### Causa raíz

**Datos de entrada incompletos**, no error del modelo:
- `city_gp_surf_spot`, `city_gp_kite_school`, `city_gp_water_sports` = 0 para Tarifa y Fuerteventura en el dataset actual
- Las features que capturan kite/surf no tienen señal para las ciudades donde el kite/surf existe de verdad
- Buenos Aires y Berlin tienen valores altos en otras features que correlacionan con el perfil (coste razonable, calidad de vida, infraestructura) → salen arriba aunque no tengan surf

### Solución aplicada

**No aplicada en MVP (presentación)** — el impacto en NDCG es 0 (métricas correctas dada la data). Documentado como deuda técnica post-presentación:

1. **Fix de datos GP**: re-ejecutar `fetch_cities.py` con queries más amplias para kite/surf/water sports en ciudades especializadas pequeñas
2. **Fuentes adicionales para nicho**: añadir IKO (International Kiteboarding Organization) como fuente de spots oficiales
3. **Feature engineering**: añadir feature binaria `es_destino_surf_conocido` basada en lista curada para los ~10 destinos top globales
4. **OSM sport=**: añadir queries Overpass para `sport=kite`, `sport=surfing`, `sport=windsurfing`

### Para recordar en una entrevista

> "En sistemas de recomendación, distinguir entre errores del modelo y errores en los datos de entrada es crítico. Un NDCG@5 = 0.9631 excelente con una validación cualitativa fallida no significa que el modelo esté mal — significa que los datos de entrenamiento no capturan la señal correcta. El modelo aprende perfectamente de lo que le das. Si los datos son incorrectos, el modelo los aprende correctamente. Por eso en producción siempre combinamos métricas automáticas (NDCG, precisión) con validación humana de casos representativos. El NDCG mide coherencia interna; la validación cualitativa mide alineación con la realidad."

---

*Última actualización: 10/04/2026 — #35 kite_surf validación cualitativa, ranker v3 + app conectados*
