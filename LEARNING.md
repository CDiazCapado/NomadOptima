# NomadOptima — Cuaderno de Aprendizaje

**Autor:** Carlos Díaz Capado  
**Proyecto:** NomadOptima — Motor de Matching Ciudad-Perfil de Vida  
**Propósito:** Entender paso a paso qué estamos haciendo, por qué lo hacemos así,  
y qué conceptos técnicos hay detrás de cada decisión.

Este documento se actualiza cada vez que avanzamos en el proyecto.  
Está escrito como si fuera un profesor explicándote cada cosa desde cero,  
con el nombre técnico correcto para que puedas usarlo en entrevistas.

---

## Índice

| # | Tema | Sección |
|---|------|---------|
| 1 | Qué es un pipeline de datos y por qué lo necesitamos | [→](#1-qué-es-un-pipeline-de-datos) |
| 2 | Cómo funciona la ingesta de datos (fetch_cities.py) | [→](#2-ingesta-de-datos) |
| 3 | Qué es un JSON y cómo lo usamos | [→](#3-qué-es-un-json) |
| 4 | Qué es el EDA y para qué sirve | [→](#4-qué-es-el-eda) |
| 5 | Cómo construimos el DataFrame | [→](#5-construcción-del-dataframe) |
| 6 | Auditoría de calidad de datos | [→](#6-auditoría-de-calidad-de-datos) |
| 7 | Análisis de separabilidad | [→](#7-análisis-de-separabilidad) |

---
---

# 1. Qué es un pipeline de datos

## Concepto

Un **pipeline de datos** (tubería de datos) es una secuencia de pasos automatizados  
que transforma datos en bruto en datos listos para ser usados por un modelo de Machine Learning.

Se llama "pipeline" (tubería) porque los datos fluyen de un paso al siguiente,  
como el agua en una cañería: entran sucios por un extremo y salen limpios por el otro.

```
Fuentes externas          Pipeline                    Modelo ML
──────────────────        ────────────────────────    ──────────
Numbeo          ──→       1. Ingesta (fetch)      ──→
wttr.in         ──→       2. Limpieza             ──→  LightGBM
Wikipedia       ──→       3. Transformación       ──→  LambdaMART
OpenStreetMap   ──→       4. Feature engineering  ──→
Google Places   ──→       5. Normalización        ──→
```

## Por qué es importante

Sin un pipeline bien diseñado, el modelo recibe datos inconsistentes y sus  
predicciones son poco fiables. En Machine Learning existe un principio fundamental:

> **"Garbage in, garbage out"**  
> Si entran datos de mala calidad, salen predicciones de mala calidad.

## En NomadOptima

Nuestro pipeline tiene estas fases:

```
Fase 1 — Ingesta:        fetch_cities.py lee 7 APIs/webs y guarda JSONs
Fase 2 — EDA:            01_eda_malaga_paris.ipynb explora y valida los datos
Fase 3 — Processing:     construimos el DataFrame con features limpias
Fase 4 — Synthetic data: generamos perfiles sintéticos de usuario
Fase 5 — Training:       entrenamos LightGBM con esos datos
Fase 6 — Evaluation:     medimos la calidad del modelo con NDCG@k
Fase 7 — Serving:        FastAPI sirve predicciones en tiempo real
```

Cada notebook corresponde a una fase. Así el trabajo está organizado  
y es reproducible: cualquier persona puede ejecutar los notebooks en orden  
y obtener el mismo resultado.

---
---

# 2. Ingesta de datos

## Concepto: ¿Qué es una API?

Una **API (Application Programming Interface)** es un contrato entre dos programas.  
Define cómo un programa puede pedir datos a otro programa.

Imagina que entras a un restaurante. Tú no vas a la cocina a coger la comida —  
le dices al camarero (la API) lo que quieres, y él te lo trae en el formato correcto  
(el plato, no los ingredientes en crudo).

```
Tu programa                 API                    Servidor
──────────────    →    ──────────────    →    ──────────────────
"dame el clima          GET /weather            base de datos
 de Málaga"             ?city=Malaga            del servidor
                   ←                    ←
                        { "temp": 18.5,
                          "desc": "Sunny" }
```

## Tipos de petición HTTP que usamos

| Método | Para qué sirve | Ejemplo en nuestro proyecto |
|--------|---------------|---------------------------|
| `GET`  | Pedir datos (leer) | wttr.in, Wikipedia, RestCountries |
| `POST` | Enviar datos para obtener respuesta | Overpass (OSM), Google Places (New) |

**¿Por qué Google Places usa POST y Wikipedia usa GET?**  
Wikipedia solo necesita saber el nombre de la ciudad (va en la URL).  
Google Places necesita enviar un objeto JSON complejo con coordenadas,  
radio de búsqueda y tipos de lugar — demasiado para una URL, así que va en el body del POST.

## Códigos de respuesta HTTP — la señalética de internet

Cuando haces una petición HTTP, el servidor siempre responde con un código numérico  
que indica qué ocurrió. Es como los semáforos: hay un idioma estándar universal.

| Rango | Significado general | Ejemplos clave |
|-------|--------------------|-|
| 2xx | **Éxito** — todo fue bien | `200 OK`, `201 Created` |
| 4xx | **Error del cliente** — tu petición tiene un problema | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `429 Too Many Requests` |
| 5xx | **Error del servidor** — el servidor tiene un problema | `500 Internal Server Error`, `504 Gateway Timeout` |

**Los más importantes para recordar:**
- `200` — perfecto, aquí tienes los datos
- `403` — el servidor te entiende pero te rechaza (sin permiso o mal formateado)
- `404` — el recurso que pides no existe
- `429` — has enviado demasiadas peticiones, el servidor te bloquea temporalmente
- `504` — el servidor tardó demasiado y canceló la conexión

## Cómo funciona fetch_cities.py

El script tiene 7 funciones, una por fuente de datos.  
Cada función sigue siempre el mismo patrón:

```python
def fetch_wikipedia(city):
    # 1. Construir la URL con los parámetros de la ciudad
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + city["wiki"]
    
    # 2. Hacer la petición HTTP
    r = requests.get(url, headers={"User-Agent": "NomadOptima/1.0"})
    
    # 3. Verificar que no hubo error (lanza excepción si hay código 4xx o 5xx)
    r.raise_for_status()
    
    # 4. Parsear la respuesta JSON
    data = r.json()
    
    # 5. Extraer solo los campos que necesitamos
    result = {
        "description": data.get("description", ""),
        "extract":     data.get("extract", "")[:800],
    }
    
    # 6. Devolver el resultado
    return result
```

## El sistema de cadencia — por qué no llamamos a las APIs siempre

Las ciudades no cambian cada día. El precio del alquiler en Málaga  
es prácticamente el mismo hoy que hace dos semanas.  
Llamar a Numbeo cada vez que ejecutamos el script sería:
- Ineficiente (coste de tiempo)
- Irrespetuoso con el servidor (que es gratuito)
- Potencialmente bloqueante (rate limiting)

La solución es el **sistema de cadencia**: cada fuente tiene un período de validez.  
Si los datos son más recientes que ese período, los reutilizamos del JSON guardado.

```python
REFRESH_CADENCE = {
    "weather":       7,    # El tiempo cambia semanalmente
    "numbeo":        30,   # Los precios cambian mensualmente
    "google_places": 90,   # La infraestructura de una ciudad cambia poco
    "wikipedia":     180,  # La descripción de una ciudad casi nunca cambia
}

# Antes de llamar a la API, comprobamos:
# ¿Cuántos días hace que actualizamos esta fuente?
# Si es menos que la cadencia → reutilizamos el JSON
# Si es más → llamamos a la API y actualizamos
```

## Scraping vs API — diferencia importante

| | API oficial | Scraping |
|---|---|---|
| **Qué es** | El sitio web te da los datos en formato estructurado (JSON) | Lees el HTML de la página como lo haría un navegador |
| **Estabilidad** | Alta — el formato está documentado y es estable | Baja — si la web cambia su diseño, el scraping se rompe |
| **Ejemplo en el proyecto** | wttr.in, Wikipedia, RestCountries, Google Places | Numbeo (no tiene API gratuita) |
| **Herramienta** | `requests` | `requests` + `BeautifulSoup` |

**BeautifulSoup** es una librería de Python que convierte HTML en una estructura  
navegable. En lugar de leer el HTML como texto crudo, puedes decirle:  
"dame todas las filas de la tabla con clase `data_wide_table`".

---
---

# 3. Qué es un JSON

## Concepto

**JSON (JavaScript Object Notation)** es un formato de texto para representar  
datos estructurados. Es el "idioma universal" de las APIs: casi todas las APIs  
del mundo devuelven sus datos en JSON.

Es legible por humanos (puedes abrirlo con cualquier editor de texto)  
y fácil de parsear por máquinas.

## Estructura básica

```json
{
  "nombre": "Málaga",
  "pais": "España",
  "temperatura": 18.5,
  "tiene_playa": true,
  "idiomas": ["español", "inglés"],
  "coordenadas": {
    "lat": 36.7213,
    "lon": -4.4214
  }
}
```

Los elementos básicos de JSON:
- `{ }` — objeto (equivale a un diccionario de Python)
- `[ ]` — array (equivale a una lista de Python)
- `"texto"` — string
- `18.5` — número
- `true / false` — booleano

## Cómo lo usamos en el proyecto

Cada ciudad tiene su propio archivo JSON en `data/raw/`:

```
data/raw/
├── malaga_raw.json      ← todos los datos de Málaga
├── paris_raw.json       ← todos los datos de París
└── cities_raw.json      ← ambas ciudades en un solo archivo
```

El JSON de Málaga tiene esta estructura:

```json
{
  "meta": { "name": "Malaga", "lat": 36.7213, ... },
  "numbeo": {
    "prices": { "Apartment (1 bedroom) in City Centre": 950.0, ... },
    "key_prices": { "rent_1br_center": 950.0, ... },
    "quality_indices": { "Quality of Life Index:": 180.35 }
  },
  "weather": {
    "current": { "temp_c": 16.0, "humidity_pct": 72.0, ... },
    "forecast": [ { "date": "2026-03-20", "avg_c": 15.5, ... }, ... ]
  },
  "osm": {
    "infrastructure": {
      "restaurants": 599,
      "beaches": 18,
      "playgrounds": 21,
      ...
    }
  }
}
```

## Cómo leer un JSON en Python

```python
import json

# Leer el archivo
with open('data/raw/malaga_raw.json', encoding='utf-8') as f:
    data = json.load(f)

# Acceder a los datos
temp = data['weather']['current']['temp_c']      # → 16.0
restaurantes = data['osm']['infrastructure']['restaurants']  # → 599

# Si una clave puede no existir, usamos .get() con valor por defecto
alquiler = data['numbeo']['key_prices'].get('rent_1br_center', None)
```

---
---

# 4. Qué es el EDA

## Concepto

**EDA (Exploratory Data Analysis)** significa Análisis Exploratorio de Datos.  
Es el paso que hacemos **siempre antes de entrenar cualquier modelo**.

El objetivo es simple: entender los datos antes de usarlos.  
Es como leer el mapa antes de empezar a conducir.

## Por qué es obligatorio

Si entrenas un modelo sin hacer EDA primero, corres estos riesgos:

**1. Data leakage** (fuga de datos)  
Una feature contiene información del futuro que no estaría disponible en producción.  
El modelo aprende a "hacer trampa" y funciona perfectamente en entrenamiento  
pero falla completamente en producción.

**2. Features con mala calidad sin detectar**  
Columnas con todos los valores a 0, o con valores imposibles (temperatura de 500°C),  
o con el 90% de valores vacíos (NaN). El modelo las usaría sin saber que son basura.

**3. Escala muy diferente entre features**  
Si una feature va de 0 a 1 y otra va de 0 a 10.000, la segunda domina el modelo  
aunque no sea más importante. Hay que normalizarlas.

**4. Features correlacionadas**  
Si tienes "temperatura en Celsius" y "temperatura en Fahrenheit", son la misma  
información dos veces. El modelo se confunde y puede dar peores resultados.

## Las preguntas que responde el EDA

```
1. ¿Qué datos tenemos? (estructura, tipos, tamaño)
2. ¿Faltan datos? ¿Dónde y cuántos? (NaN, nulls)
3. ¿Los datos tienen sentido? (valores imposibles, errores)
4. ¿Cómo se distribuyen los valores? (media, mediana, outliers)
5. ¿Qué features están correlacionadas entre sí?
6. ¿Qué features distinguen mejor entre ciudades? (separabilidad)
7. ¿Qué hay que arreglar antes de entrenar el modelo?
```

## Herramientas que usamos

| Librería | Para qué | Ejemplo |
|----------|---------|---------|
| `pandas` | Manipular tablas de datos (DataFrames) | `df.describe()`, `df.isna()` |
| `numpy` | Operaciones matemáticas sobre arrays | `np.mean()`, `np.nan` |
| `matplotlib` | Crear gráficos | `plt.bar()`, `plt.hist()` |

---
---

# 5. Construcción del DataFrame

## Concepto: ¿Qué es un DataFrame?

Un **DataFrame** es una tabla de datos, como una hoja de Excel pero dentro de Python.  
Es la estructura de datos central de pandas y la que usa LightGBM para entrenar.

```
         ciudad    temp_c    restaurants    beaches    quality_of_life
         ──────    ──────    ───────────    ───────    ───────────────
         Málaga      16.0            599         18             180.35
         París       16.0           8726          2             147.23
```

Cada **fila** es una observación (en este caso, una ciudad).  
Cada **columna** es una feature (una variable que describe la ciudad).

## Por qué no usamos el JSON directamente

El JSON tiene una estructura anidada y heterogénea:  
- Algunos datos están en `data['weather']['current']['temp_c']`  
- Otros están en `data['osm']['infrastructure']['restaurants']`  
- Otros pueden no existir y hay que manejar el caso con `.get()`

El modelo necesita una tabla plana: **una fila por ciudad, una columna por feature**.  
La función `build_city_features()` hace exactamente esa transformación.

## Cómo funciona build_city_features()

```python
def build_city_features(city_name, data):
    """
    Toma el JSON crudo de una ciudad y devuelve un diccionario plano
    con todas las features que necesita el modelo.
    """
    row = {'ciudad': city_name}   # empezamos con el nombre de la ciudad

    # ── Extraemos features de Numbeo ──────────────────────────────────────
    numbeo = data.get('numbeo', {})          # si 'numbeo' no existe → {}
    kp = numbeo.get('key_prices', {})         # si 'key_prices' no existe → {}

    row['numbeo_rent_1br_center'] = kp.get('rent_1br_center', np.nan)
    #                                                            ↑
    #                                          np.nan = "no hay dato"
    #                                          Es el estándar de pandas para valores ausentes

    # ── Extraemos features de OSM ─────────────────────────────────────────
    infra = data.get('osm', {}).get('infrastructure', {})
    for key, val in infra.items():
        row[f'osm_{key}'] = val if val is not None else np.nan
        #   ↑
        #   Prefijo 'osm_' para saber de qué fuente viene cada feature
        #   Ejemplo: 'osm_restaurants', 'osm_beaches', 'osm_playgrounds'

    return row

# Construir el DataFrame con todas las ciudades
rows = [build_city_features(name, data) for name, data in cities.items()]
df = pd.DataFrame(rows).set_index('ciudad')
```

## NaN — el valor especial para "dato ausente"

`NaN` significa **Not a Number** y es el estándar de pandas para representar  
que un dato no existe o no fue posible obtenerlo.

```python
import numpy as np
import pandas as pd

# NaN en la práctica
df.isna()           # tabla de True/False indicando dónde hay NaN
df.isna().sum()     # cuántos NaN hay por columna
df.dropna()         # eliminar filas con cualquier NaN
df.fillna(0)        # rellenar NaN con 0 (cuidado: no siempre es correcto)
```

**¿Por qué no usamos simplemente 0 cuando falta un dato?**

Porque 0 tiene significado propio. Si `osm_hospitals = 0` significa  
"hay 0 hospitales en esta ciudad" — eso es información real.  
Si usamos 0 para "no tenemos dato", el modelo no puede distinguir  
entre "ciudad sin hospitales" y "no sé cuántos hospitales hay".

NaN le dice al modelo explícitamente: "no tenemos información aquí".

## Prefijos de fuente — convención de nomenclatura

Una buena práctica es añadir un prefijo a cada feature para saber de dónde viene.  
Esto facilita el debugging y el análisis:

```
numbeo_rent_1br_center     → precio de alquiler (Numbeo)
weather_temp_c             → temperatura (wttr.in)
osm_restaurants            → restaurantes (OpenStreetMap)
gp_gym                     → gimnasios (Google Places)
speedtest_fixed_download   → velocidad internet (Speedtest)
country_schengen           → si está en zona Schengen (RestCountries)
```

## El problema del cap de Google Places

La Places API devuelve máximo 20 resultados por categoría.  
Si una ciudad tiene más de 20 gimnasios, la API devuelve 20 y para.  
Esto crea un problema de comparabilidad:

```
Málaga:  20 gimnasios según Google Places  (¿son 20? ¿o son 200 y está capeado?)
París:   20 gimnasios según Google Places  (¿son 20? ¿o son 2000 y está capeado?)
```

Para el MVP lo tratamos así:
- Si el valor es 20 → lo marcamos como "capped" y lo convertimos en flag binario
- Si el valor es < 20 → es el conteo real y es comparable

```python
# Flag de cap: 1 si está capeado, 0 si es conteo real
row[f'gp_{key}_capped'] = int(count == 20)

# En el modelo usamos:
# - gp_gym_capped = 0 → el conteo es real → usamos el número
# - gp_gym_capped = 1 → el conteo no es real → usamos solo si existe (>0)
```

---
---

# 6. Auditoría de calidad de datos

## Concepto

La **auditoría de calidad de datos** (data quality audit) es el proceso de  
revisar sistemáticamente cada fuente de datos para detectar problemas  
antes de que lleguen al modelo.

Es como la inspección técnica de un coche: primero compruebas que todo funciona,  
luego lo conduces.

## Tipos de problemas que buscamos

### 1. Datos ausentes (Missing values)
Fuentes que no devolvieron nada o devolvieron error.

```python
# Detectar fuentes con error
source = data.get('numbeo', {})
has_error = 'error' in source     # True si la fuente falló
```

### 2. Silent failures (fallos silenciosos)
El código no lanza error pero devuelve datos vacíos o incorrectos.  
Es el tipo de problema más peligroso porque no se ve en los logs.

```
Ejemplo real en el proyecto:
  fetch_numbeo() devuelve: {"prices": {54 items}, "key_prices": {}}
  
  El código funcionó sin error ✅
  Pero key_prices está vacío ❌ — el matching de nombres falló silenciosamente
```

**¿Cómo detectarlo?**
```python
# Validación explícita después de la extracción
if len(result['key_prices']) == 0 and len(result['prices']) > 0:
    logger.warning(f"key_prices vacío para {city_name} — revisar key_map")
```

### 3. Datos capeados (Capped values)
Valores que han alcanzado el límite máximo de la API y no representan el valor real.

```python
# Detectar valores capeados en Google Places
capped = {k: v['count'] for k, v in cats.items() if v.get('count') == 20}
```

### 4. Datos de granularidad incorrecta
Los datos existen pero no son lo suficientemente específicos.

```
Ejemplo: Speedtest Global Index da velocidad de internet por PAÍS, no por ciudad.
         España tiene 213 Mbps según el índice, pero Málaga puede ser diferente.
         
Impacto: usamos el dato sabiendo su limitación, documentamos la fuente,
         y en fases posteriores buscamos datos a nivel ciudad.
```

## Qué hicimos en el EDA de NomadOptima

```
Fuente              Estado      Problema encontrado
──────────────────  ──────────  ─────────────────────────────────────────────
numbeo              ⚠️ Parcial  key_prices vacío — key_map no hace match
weather             ✅ OK       Datos actuales, no históricos anuales
wikipedia           ✅ OK       Solo descripción corta — suficiente para MVP
country             ✅ OK       Todos los campos presentes
osm                 ✅ OK       19 categorías con conteos reales
google_places       ⚠️ Parcial  La mayoría de categorías capeadas a 20
speedtest           ⚠️ Parcial  Granularidad país, no ciudad
```

---
---

# 7. Análisis de separabilidad

## Concepto

La **separabilidad** de una feature mide cuánto ayuda a distinguir entre ciudades.  
Si una feature tiene el mismo valor en Málaga y en París, no sirve para diferenciarlas  
y el modelo no aprenderá nada útil de ella.

Imagina que intentas distinguir manzanas de naranjas usando el color:  
- El color es muy separable (rojo vs naranja) → feature útil
- El peso medio es poco separable (similar en ambas) → feature menos útil

## La métrica que usamos

Para cada feature calculamos el **ratio de diferencia normalizado**:

```
separabilidad = |valor_malaga - valor_paris| / (valor_malaga + valor_paris)
```

El resultado es siempre entre 0 y 1:
- **0** → ambas ciudades tienen exactamente el mismo valor (feature inútil)
- **1** → una ciudad tiene el valor y la otra tiene 0 (feature perfectamente discriminativa)
- **> 0.5** → diferencia significativa, feature probablemente útil para el modelo

```python
# Ejemplo con datos reales
malaga_beaches = 18
paris_beaches  = 2

sep_beaches = abs(18 - 2) / (18 + 2) = 16/20 = 0.8   ← muy separable ✅

malaga_temp = 16.0
paris_temp  = 16.0

sep_temp = abs(16.0 - 16.0) / (16.0 + 16.0) = 0/32 = 0.0  ← nada separable ❌
# (porque tomamos la temperatura el mismo día — en invierno sería muy diferente)
```

## Hallazgos del EDA de NomadOptima

Las features más discriminativas entre Málaga y París según el análisis:

```
Feature más separable     Málaga    París    Separabilidad    Interpretación
────────────────────────  ──────    ─────    ─────────────    ──────────────
osm_hospitals                  0       18         1.00        París domina (metrópoli)
osm_universities               1       98         0.98        París domina (capital)
osm_kindergartens             17      298         0.89        París domina (densidad)
osm_schools                  212     1292         0.72        París domina (tamaño)
osm_beaches                   18        2         0.80        Málaga domina (costera)
osm_bicycle_lanes            216     5399         0.92        París domina (infraestructura)
numbeo_quality_of_life      180.3    147.2        0.10        Málaga mejor calidad de vida
```

**Conclusión del análisis:**  
Las features de OSM son las más discriminativas porque capturan diferencias  
estructurales reales entre una ciudad costera mediana (Málaga) y una gran  
metrópoli continental (París). Esto es exactamente lo que queremos.

## Por qué importa la separabilidad para el modelo

LightGBM LambdaMART aprende a ordenar ciudades según su relevancia para un perfil.  
Para hacer eso bien necesita features que varíen entre ciudades.

```
Feature con separabilidad 0 → el modelo no puede aprender nada de ella
                            → ocupa espacio en memoria sin aportar valor
                            → puede añadir ruido y empeorar el modelo

Feature con separabilidad alta → el modelo puede aprender:
                               "cuando beaches es alto y el usuario quiere playa
                                → esa ciudad es más relevante"
```

En fases posteriores haremos un análisis más formal con **SHAP feature importance**,  
que nos dirá exactamente cuánto contribuye cada feature a las predicciones del modelo.

---
---

---
---

# 8. Organización del código — por qué separamos features.py del notebook

## El problema de tener todo en el notebook

Cuando empezamos el EDA escribimos `build_city_features()` directamente  
en una celda del notebook. Funciona, pero tiene un problema importante:

```
notebooks/
└── 01_eda_malaga_paris.ipynb     ← build_city_features() está aquí
notebooks/
└── 02_synthetic_profiles.ipynb  ← necesita build_city_features() → ¿la copio?
notebooks/
└── 04_lightgbm_ranker.ipynb     ← necesita build_city_features() → ¿la copio otra vez?
```

Si la función está copiada en tres sitios y hay que cambiar algo  
(por ejemplo, cuando arreglemos el key_map de Numbeo), hay que  
cambiarla en tres sitios. Eso es una fuente segura de errores.

## El principio DRY

**DRY significa "Don't Repeat Yourself"** (No te repitas).  
Es uno de los principios fundamentales de ingeniería de software.

> Si el mismo código aparece en más de un sitio, es una señal de que  
> debería estar en una función o módulo compartido.

La solución es mover `build_city_features()` a un módulo Python  
que todos los notebooks pueden importar:

```
src/
├── ingestion/
│   └── fetch_cities.py          ← extrae datos de APIs → JSONs
└── processing/
    └── features.py              ← transforma JSONs → DataFrame
```

Ahora cualquier notebook importa la función en una línea:

```python
from src.processing.features import build_city_features
```

Si hay que cambiar algo, se cambia en `features.py` y todos  
los notebooks reciben el cambio automáticamente.

## Qué contiene features.py

El módulo está organizado en cuatro partes:

### 1. Funciones privadas de extracción (una por fuente)

```python
def _extract_numbeo(row, data):      # extrae precios e índices de Numbeo
def _extract_weather(row, data):     # extrae clima de wttr.in
def _extract_country(row, data):     # extrae datos de RestCountries
def _extract_speedtest(row, data):   # extrae velocidad internet de Speedtest
def _extract_osm(row, data):         # extrae infraestructura de OpenStreetMap
def _extract_google_places(row, data): # extrae POIs de Google Places
```

Son **privadas** (empiezan con `_`) porque solo las usa `build_city_features()`  
internamente. Nadie debería llamarlas directamente desde fuera del módulo.

### 2. Features derivadas (_extract_derived)

Las **features derivadas** no vienen de ninguna API — las calculamos nosotros  
combinando múltiples fuentes para crear indicadores compuestos:

```python
def _extract_derived(row):
    # family_friendliness_score — combina playgrounds + kindergartens +
    #                             schools + pharmacies + hospitals
    # digital_nomad_score       — combina coworking + internet + transporte
    # outdoor_score             — combina beaches + parks + gyms + bicycle_lanes
```

¿Por qué son útiles para el modelo?  
Porque sintetizan información de múltiples fuentes en un solo número.  
El modelo puede aprender: "cuando digital_nomad_score es alto Y el  
presupuesto encaja → la ciudad es relevante para ese perfil".

### 3. Función principal (build_city_features)

```python
def build_city_features(city_name, data):
    row = {'ciudad': city_name}
    _extract_numbeo(row, data)
    _extract_weather(row, data)
    _extract_country(row, data)
    _extract_speedtest(row, data)
    _extract_osm(row, data)
    _extract_google_places(row, data)
    _extract_derived(row)    # siempre al final — usa features ya extraídas
    return row
```

Es simple a propósito: solo llama a las funciones de extracción en orden.  
La lógica de cada fuente está encapsulada en su propia función.

### 4. Utilidades (get_feature_groups, audit_features)

```python
def get_feature_groups():
    # Devuelve las features agrupadas por dimensión del perfil
    # Útil para análisis SHAP y para entender qué features
    # corresponden a qué dimensión del perfil de usuario
    return {
        "economico":    ["numbeo_rent_1br_center", ...],
        "clima":        ["weather_temp_c", ...],
        "familia":      ["osm_playgrounds", "gp_pediatrician", ...],
        "conectividad": ["speedtest_fixed_download_mbps", ...],
        ...
    }

def audit_features(df):
    # Imprime un resumen de calidad del DataFrame
    # Detecta NaN, features capeadas y features con varianza 0
```

## Cómo usar features.py desde un notebook

```python
import json
import pandas as pd
from src.processing.features import build_city_features, audit_features

# Cargar JSONs
malaga = json.load(open('../data/raw/malaga_raw.json'))
paris  = json.load(open('../data/raw/paris_raw.json'))
cities = {'Málaga': malaga, 'París': paris}

# Construir DataFrame — 3 líneas en lugar de 80
rows = [build_city_features(name, data) for name, data in cities.items()]
df   = pd.DataFrame(rows).set_index('ciudad')

# Auditar calidad
audit_features(df)
```

## Para que Python encuentre src/ desde los notebooks

Los notebooks están en `notebooks/` y el módulo está en `src/`.  
Para que Python pueda hacer `from src.processing.features import ...`  
hay que añadir la raíz del proyecto al path de Python:

```python
# Primera celda de cada notebook
import sys
import os
sys.path.insert(0, os.path.abspath('..'))   # sube un nivel: notebooks/ → raíz/
# Ahora Python puede encontrar src/processing/features.py
```

---
---

# 9. Perfiles sintéticos y pseudo-labeling

## El problema del cold start

Un modelo supervisado necesita datos etiquetados para aprender.  
En nuestro caso, necesita pares del tipo:

```
(perfil_usuario, ciudad, relevancia)

Ejemplo:
  perfil:    {"presupuesto": 1200, "quiere_playa": True, "tiene_perro": True}
  ciudad:    Málaga
  relevancia: 3  (muy relevante)

  perfil:    {"presupuesto": 1200, "quiere_playa": True, "tiene_perro": True}
  ciudad:    París
  relevancia: 0  (no relevante — muy cara y sin playa)
```

Sin usuarios reales, no tenemos estas etiquetas.  
El **pseudo-labeling** las fabrica de forma programática usando lógica de dominio.

## La escala de relevancia

Usamos 4 niveles, que es el estándar en Learning to Rank:

```
0 — Irrelevante    Ciudad claramente incompatible con el perfil
1 — Bajo           Ciudad posible pero con fricciones importantes
2 — Relevante      Ciudad que encaja bien con el perfil
3 — Muy relevante  Ciudad casi perfecta para ese perfil
```

Este tipo de escala se llama **relevance grade** o **judgment** en terminología  
de Information Retrieval (la disciplina que estudia sistemas de búsqueda y ranking).

## Cómo funciona el pseudo-labeling

Para cada par (perfil, ciudad) el sistema evalúa dimensión por dimensión:

```python
# Pseudo-código del sistema de scoring
def calcular_relevancia(perfil, ciudad_features):
    puntos = 0
    puntos_max = 0

    # Dimensión económica
    if perfil['presupuesto_max'] is not None:
        puntos_max += 1
        coste = ciudad_features.get('numbeo_rent_1br_center', 1500)
        if coste <= perfil['presupuesto_max']:
            puntos += 1

    # Dimensión playa
    if perfil['quiere_playa']:
        puntos_max += 1
        playas = ciudad_features.get('osm_beaches', 0)
        if playas >= 5:
            puntos += 1

    # Dimensión familia
    if perfil['tiene_hijos']:
        puntos_max += 1
        family_score = ciudad_features.get('family_friendliness_score', 0)
        if family_score >= 0.5:
            puntos += 1

    # Convertir puntos a escala 0-3
    ratio = puntos / puntos_max if puntos_max > 0 else 0
    if ratio >= 0.9:   return 3
    elif ratio >= 0.7: return 2
    elif ratio >= 0.4: return 1
    else:              return 0
```

## Cómo generamos 30.000 perfiles distintos

No se crean 30.000 perfiles a mano.  
Se definen **8 arquetipos base** y se generan variaciones añadiendo  
**ruido gaussiano** a los valores numéricos:

```python
# Arquetipo base
ARQUETIPOS = {
    "nomada_digital": {
        "presupuesto_max":        1500,   # media
        "presupuesto_std":         200,   # desviación estándar
        "quiere_playa":           0.7,    # probabilidad de que quiera playa
        "necesita_coworking":     0.9,    # prob. de que necesite coworking
        "tiene_hijos":            0.05,   # prob. muy baja de tener hijos
        "tiene_mascota":          0.2,
    },
    "familia_hijos": {
        "presupuesto_max":        2500,
        "presupuesto_std":         400,
        "quiere_playa":           0.6,
        "necesita_coworking":     0.3,
        "tiene_hijos":            1.0,    # siempre tiene hijos
        "tiene_mascota":          0.4,
    },
    ...
}

# Generar variaciones con ruido gaussiano
for arquetipo_nombre, params in ARQUETIPOS.items():
    n_perfiles = 30000 // len(ARQUETIPOS)   # reparto equitativo
    for i in range(n_perfiles):
        perfil = {
            "arquetipo":      arquetipo_nombre,
            "presupuesto_max": np.random.normal(
                params["presupuesto_max"],
                params["presupuesto_std"]
            ),
            "quiere_playa":   np.random.random() < params["quiere_playa"],
            "tiene_hijos":    np.random.random() < params["tiene_hijos"],
            ...
        }
```

## Por qué funciona aunque sea sintético

El modelo no aprende que "Málaga es buena para nómadas digitales" directamente.  
Aprende la **relación entre features y relevancia**:

```
alta relevancia correlaciona con:
  coste_vida bajo   cuando presupuesto_max es bajo
  beaches alto      cuando quiere_playa es True
  coworking alto    cuando necesita_coworking es True
  family_score alto cuando tiene_hijos es True
```

Cuando lleguen usuarios reales, el modelo ya sabe qué combinación de features  
predice relevancia — solo mejora con datos más precisos y reales.

## La limitación honesta

```
Riesgo:      Si las reglas heurísticas tienen sesgos, el modelo los aprenderá.
             Ejemplo: si asumimos que todos los jubilados quieren calor,
             el modelo penalizará ciudades frías para jubilados aunque
             algunos prefieran climas templados.

Mitigación:
  1. Validar las reglas manualmente contra conocimiento real del dominio
  2. Añadir suficiente variación (std alto) para que el modelo no memorice
  3. Sustituir progresivamente con datos reales conforme lleguen usuarios
  4. Comparar predicciones del modelo con opiniones de personas reales
```

## Las 60.000 filas — la matemática

```
8 arquetipos × 3.750 variaciones cada uno = 30.000 perfiles únicos
30.000 perfiles × 2 ciudades              = 60.000 filas en el dataset

Cada fila tiene:
  - Las features del perfil (presupuesto, preferencias, estilo de vida)
  - Las features de la ciudad (OSM, clima, Google Places...)
  - La etiqueta de relevancia (0, 1, 2 o 3)
  - El query_id (identificador del perfil, para que LightGBM sepa
    qué filas pertenecen a la misma "búsqueda")
```

El `query_id` es fundamental en Learning to Rank: le dice al modelo  
que las filas 1 y 2 son el mismo usuario evaluando dos ciudades distintas,  
y que debe aprender a ordenar esas dos ciudades entre sí, no en abstracto.

---
---

*Última actualización: 23/03/2026*  
*Próxima sección: LightGBM LambdaMART — cómo funciona el algoritmo de ranking*

---
---

# 8. Perfiles Sintéticos y Pseudo-Labeling

## El problema del cold start

**Cold start** es el problema de arrancar un sistema de recomendación sin datos.
Un modelo supervisado necesita ejemplos etiquetados para aprender:

```
(perfil_usuario, ciudad) → relevancia
```

Sin usuarios reales no tenemos esas etiquetas. La solución es el **pseudo-labeling**:
fabricar etiquetas de forma programática usando lógica de dominio (conocimiento experto).

Es como si un experto dijera: "Para un nómada digital con 1.500€/mes, Málaga es más
relevante que París porque es más barata y tiene buen internet y coworking."

El modelo no aprende que "Málaga es buena para nómadas" directamente.
Aprende la **relación entre features y relevancia**:

```
alta relevancia correlaciona con:
  → coste_vida bajo cuando presupuesto_max es bajo
  → coworking_count alto cuando importancia_coworking es alto
  → beach_count alto cuando importancia_playa es alto
```

Cuando lleguen usuarios reales, el modelo ya conoce esas relaciones
y solo las refina con datos más precisos.

---

## La escala de relevancia

Usamos una escala ordinal de 4 niveles, estándar en Learning to Rank:

```
0 — Irrelevante    ciudad incompatible con el perfil
1 — Bajo           ciudad posible pero con fricciones importantes
2 — Relevante      ciudad que encaja bien
3 — Muy relevante  ciudad casi perfecta para ese perfil
```

Por qué 4 niveles y no solo 0/1: el modelo necesita saber no solo
"relevante o no" sino cuánto MÁS relevante es una ciudad respecto a otra.
Con solo 0/1 no podría distinguir entre "muy buena" y "mediocre".

---

## Cómo se generan 30.000 perfiles distintos

### Paso 1: Definir 8 arquetipos base

Un arquetipo es un tipo de usuario idealizado con sus preferencias medias:

```
nomada_digital        presupuesto ~1.500EUR, prioridad coworking e internet
familia_con_hijos     presupuesto ~2.500EUR, prioridad familia y colegios
jubilado_activo       presupuesto ~1.800EUR, prioridad clima y calidad de vida
estudiante            presupuesto ~900EUR,   prioridad bajo coste y vida social
ejecutivo_cosmopolita presupuesto ~4.000EUR, prioridad cultura y gastronomia
deportista_outdoor    presupuesto ~1.600EUR, prioridad playa y deporte
backpacker            presupuesto ~700EUR,   prioridad bajo coste y autenticidad
familia_monoparental  presupuesto ~1.100EUR, prioridad bajo coste y guarderia
```

### Paso 2: Ruido gaussiano — variaciones dentro del arquetipo

Tomamos cada arquetipo y generamos variaciones añadiendo ruido gaussiano:

```python
# Arquetipo: nomada_digital tiene presupuesto medio de 1.500EUR
for i in range(3750):
    presupuesto = np.random.normal(1500, 200)
    # La mayoria de perfiles tendran entre 1.100 y 1.900EUR
```

La distribucion gaussiana (campana de Gauss) es la forma mas habitual de
variacion natural: la mayoria de personas estan cerca de la media de su
arquetipo, y hay menos personas en los extremos.

Resultado: 8 arquetipos x 3.750 variaciones = 30.000 perfiles
           30.000 perfiles x 2 ciudades     = 60.000 filas de entrenamiento

---

## Cómo se calcula la relevancia sintética

Para cada par (perfil, ciudad), se evaluan 11 dimensiones y se suman puntos:

### 1. Restricciones duras (eliminatorias)

```python
if ciudad['coste_vida'] > perfil['presupuesto_max'] * 1.15:
    return 0  # demasiado cara -> irrelevante directamente

if ciudad['temp_media_anual'] < perfil['temp_min_c'] - 3:
    return 0  # demasiado fria -> irrelevante directamente
```

### 2. Puntuacion por dimensiones (ejemplo: playa)

```python
if perfil['importancia_playa'] > 0.5:
    playa_score = (
        min(ciudad['beaches'] / 10.0, 1.0)  # normalizar a [0,1]
        * perfil['importancia_playa']         # ponderar por importancia del usuario
        * 2                                   # escalar a rango util
    )
    score += playa_score
```

Las 11 dimensiones: coste de vida, clima, playa, deporte outdoor, nomada
digital, cultura, gastronomia, movilidad, familia, mascotas, bienestar.

### 3. Conversion a escala 0-3

```python
relevance = int(np.clip(round(score / 15.0 * 3.0), 0, 3))
```

---

## Validacion de coherencia geografica

Tras generar el dataset, comprobamos que las etiquetas tienen sentido real:

```
OK  Nomada digital prefiere Malaga (mas barata y calida)
OK  Ejecutivo cosmopolita puede preferir Paris (cultura premium)
OK  Deportista outdoor prefiere Malaga (playa, surf, kitesurf)
OK  Backpacker prefiere Malaga (Paris demasiado cara para ese presupuesto)
```

Si alguna comprobacion falla, las reglas tienen un sesgo y hay que revisarlas.

---

## La limitacion honesta — modelo de bootstrapping

Si las reglas heurísticas tienen sesgos, el modelo los aprenderá como verdad.

Mitigacion en NomadOptima:
1. Validar las reglas contra conocimiento geografico real
2. Comparar predicciones con opiniones de personas reales
3. Sustituir progresivamente con datos reales conforme lleguen usuarios

Esto se llama **modelo de bootstrapping**: arrancar con datos sinteticos
y mejorar iterativamente con datos reales. Es la estrategia estandar para
cold start en sistemas de recomendacion.

---

*Ultima actualizacion: 23/03/2026*
*Proxima seccion: LightGBM LambdaMART — como entrenamos el modelo de ranking*

---

# 9. Learning to Rank con LightGBM LambdaRank

## Concepto (desde cero)

**Learning to Rank (LTR)** es una categoría de problemas de ML donde el objetivo
no es predecir un valor ni una clase, sino **ordenar** una lista de elementos
dados un contexto (llamado *query*).

Imagina que Google recibe la búsqueda "restaurante italiano cerca". Tiene 1000 webs
posibles. No le importa el número exacto de relevancia de cada web, le importa
que las mejores aparezcan primeras. Eso es LTR.

En NomadOptima: el *query* es el perfil del usuario, los *documentos* son las ciudades,
y la tarea es ordenar las ciudades de más a menos relevante para ese perfil.

### Los tres enfoques de LTR

| Enfoque | Cómo funciona | Ejemplo |
|---------|---------------|---------|
| **Pointwise** | Trata cada (query, doc) como si fuera regresión o clasificación independiente | Predice relevance=2.3 para (perfil, Málaga) |
| **Pairwise** | Aprende qué documento es mejor de cada par | ¿Málaga > París para este perfil? |
| **Listwise** | Optimiza directamente la calidad de toda la lista | Maximiza NDCG de toda la lista |

**LambdaRank es listwise.** Es el más sofisticado y el que mejores resultados da.

## Cómo lo usamos en NomadOptima

- **Query:** cada perfil de usuario (30.000 perfiles únicos)
- **Documentos:** Málaga y París (2 ciudades, expandible a N en el futuro)
- **Label:** relevance ∈ {0, 1, 2, 3} — calculado con pseudo-labeling en notebook 02
- **Grupos:** array `[2, 2, 2, ...]` que le dice a LightGBM que cada query tiene 2 docs

```python
train_set = lgb.Dataset(
    X_train, label=y_train,
    group=groups_train,        # [2, 2, 2, ...] — docs por query
    feature_name=FEATURE_COLS
)
model = lgb.train(
    params={'objective': 'lambdarank', 'metric': 'ndcg', 'eval_at': [1, 2]},
    train_set=train_set,
    valid_sets=[val_set],
    callbacks=[lgb.early_stopping(50)],
)
```

## Por qué LambdaRank y no regresión simple

Con regresión predecimos el valor de relevancia (0-3). Pero si el modelo predice
Málaga=1.8 y París=2.1, la ciudad ganadora es París — aunque ambas predicciones
estén "equivocadas" respecto al label real. Lo que importa es el *orden relativo*.

LambdaRank calcula gradientes que penalizan específicamente los *intercambios de orden*
que reducen el NDCG. Así el modelo aprende a ordenar bien en lugar de predecir valores exactos.

---

# 10. NDCG — Normalized Discounted Cumulative Gain

## Concepto (desde cero)

**NDCG** es la métrica estándar para evaluar sistemas de ranking.
Mide cuán bien ordenados están los resultados, dando más peso a las posiciones altas.

### Cálculo paso a paso

**DCG@k (Discounted Cumulative Gain):**
```
DCG@2 = rel_pos1 / log2(2) + rel_pos2 / log2(3)
      = rel_pos1 / 1.0    + rel_pos2 / 1.585
```

Si la ciudad más relevante (rel=3) está en posición 1: DCG = 3/1 + 1/1.585 = 3.63
Si la ciudad más relevante (rel=3) está en posición 2: DCG = 1/1 + 3/1.585 = 2.89

**IDCG@k:** el DCG máximo posible (ordenamiento perfecto)

**NDCG@k = DCG@k / IDCG@k** → siempre entre 0 y 1

Con NDCG=1.0 el modelo ordena perfectamente. Con NDCG=0.5 la mitad de las veces
coloca el documento equivocado en primera posición.

## Cómo lo usamos en NomadOptima

Con solo 2 ciudades, NDCG@1 y NDCG@2 son las métricas relevantes:
- **NDCG@1:** ¿acertamos qué ciudad poner primera?
- **NDCG@2:** calidad del ordenamiento completo (con 2 docs = NDCG@3 = NDCG@5)

```python
from sklearn.metrics import ndcg_score
ndcg = ndcg_score(true_rel.reshape(1,-1), pred_score.reshape(1,-1), k=2)
```

## Por qué NDCG y no accuracy o RMSE

- **Accuracy** no distingue entre "casi acertó" y "falló por mucho"
- **RMSE** penaliza por igual errores en posición 1 y posición 10
- **NDCG** penaliza más los errores en las primeras posiciones — exactamente
  lo que importa en un sistema de recomendación donde el usuario ve primero
  las posiciones altas

---

# 11. SHAP — Explicabilidad del modelo

## Concepto (desde cero)

**SHAP (SHapley Additive exPlanations)** es un método para explicar cuánto
contribuye cada feature a una predicción específica de un modelo.

Está basado en los **valores de Shapley** de la teoría de juegos cooperativos.
La idea: si varias features "cooperan" para producir una predicción, ¿cómo
repartimos el "mérito" de forma justa entre ellas?

### Ejemplo intuitivo

Predicción media del modelo: relevance = 1.5
Predicción para (nomada_digital, Málaga): relevance = 2.8

Diferencia: +1.3. Los SHAP values descomponen esta diferencia:
- `city_coste_vida_estimado` bajo → +0.5 (Málaga es barata)
- `user_importancia_coworking` alto + `city_coworking_osm` disponible → +0.3
- `city_temp_media_anual` alta → +0.2
- `city_beaches` disponibles → +0.1
- Otros features → +0.2

Suma = +1.3 ✓

## Cómo lo usamos en NomadOptima

```python
explainer   = shap.TreeExplainer(model)   # exacto para árboles
shap_values = explainer.shap_values(X)    # shape: (n_muestras, n_features)

# Summary plot global
shap.summary_plot(shap_values, X, feature_names=FEATURE_COLS, max_display=20)

# Waterfall por perfil específico
sv = explainer.shap_values(X[i:i+1])[0]
top8 = np.argsort(np.abs(sv))[-8:]        # top 8 features por impacto absoluto
```

## Por qué SHAP es clave en producción

En el endpoint `/recommend` de FastAPI, el usuario no solo recibirá "Te recomendamos Málaga"
sino también "Porque: tu presupuesto de 1200€ encaja (+0.5), hay coworking disponible (+0.3),
el clima supera tu mínimo de 14°C (+0.2)".

Esta explicabilidad convierte una caja negra en un sistema de confianza.
En entrevistas: demuestra que no solo sabes que el modelo funciona, sino por qué.

---

# 12. MLflow — Tracking de experimentos de ML

## Concepto (desde cero)

**MLflow** es una plataforma open-source para gestionar el ciclo de vida completo
de modelos de ML: experimentos, reproducibilidad, deployment y registro de versiones.

Problema que resuelve: cuando entrenas muchos modelos con distintos hiperparámetros,
¿cómo sabes cuál fue el mejor? Sin MLflow: apuntes en papel o en Excel.
Con MLflow: todo queda registrado automáticamente, comparable en una UI web.

### Los 4 componentes principales

| Componente | Para qué sirve |
|------------|----------------|
| **Tracking** | Registra parámetros, métricas y artefactos de cada run |
| **Projects** | Empaqueta el código para reproducibilidad |
| **Models** | Formato estándar para servir modelos en producción |
| **Registry** | Gestión de versiones (staging → production) |

## Cómo lo usamos en NomadOptima

```python
mlflow.set_experiment('NomadOptima_LightGBM_Ranker')

with mlflow.start_run(run_name='lgbm_ranker_v1'):
    mlflow.log_params({'num_leaves': 31, 'learning_rate': 0.05, ...})
    mlflow.log_metrics({'ndcg_at_2': 0.87, 'precision_at_1': 0.82})
    mlflow.lightgbm.log_model(model, 'lgbm_ranker_model')
    mlflow.log_artifact('shap_summary.png')
```

Para ver los resultados: `mlflow ui` → http://127.0.0.1:5000

## Por qué MLflow y no otras opciones

- **Weights & Biases / Comet:** requieren cuenta externa, tienen costes
- **MLflow:** 100% open-source, instalable localmente, integración nativa con LightGBM
- Para un MVP y portafolio de bootcamp: MLflow es la elección correcta

---

*Ultima actualizacion: 30/03/2026*
*Proxima seccion: FastAPI — como construimos el endpoint /recommend*

---

# 13. Conversión de Moneda — Normalización de precios entre países

## Concepto (desde cero)

Cuando comparamos datos de precios de distintos países en un mismo DataFrame, hay un problema fundamental: los números no son comparables si están en monedas distintas.

Imagina que tienes estos datos de Numbeo:
- Madrid: alquiler 1BR = 1.200 (euros)
- Budapest: alquiler 1BR = 343.396 (forintos húngaros)
- Buenos Aires: alquiler 1BR = 480.000 (pesos argentinos)

Sin conversión de moneda, el modelo vería Budapest como la ciudad más cara del mundo (343.396 >> 1.200) y Buenos Aires como algo inclasificable. Los números son incomparables porque no están en la misma unidad.

La solución es la **normalización de moneda**: convertir todos los valores a una moneda de referencia común (en nuestro caso, EUR) antes de cualquier procesamiento.

La fórmula es simple:
```
valor_en_EUR = valor_en_moneda_local × tasa_de_cambio
```

Donde la tasa de cambio es "cuántos euros vale 1 unidad de esa moneda":
- 1 HUF ≈ 0.00255 EUR  → 343.396 HUF × 0.00255 = 876 EUR ✓
- 1 ARS ≈ 0.00095 EUR  → 480.000 ARS × 0.00095 = 456 EUR ✓

## Cómo lo usamos en NomadOptima

En `src/processing/features.py` creamos un diccionario con las tasas de cambio aproximadas para las 25 monedas de nuestras ciudades, y una función `to_eur()` que aplica la conversión:

```python
EUR_RATES = {
    "EUR": 1.0,
    "HUF": 0.00255,   # florín húngaro
    "PLN": 0.233,     # zloty polaco
    "CZK": 0.041,     # corona checa
    "RON": 0.201,     # leu rumano
    "GEL": 0.345,     # lari georgiano
    "USD": 0.92,      # dólar americano
    "MXN": 0.053,     # peso mexicano
    "ARS": 0.00095,   # peso argentino
    # ... 16 monedas más
}

def to_eur(value, currency):
    """Convierte un valor de moneda local a EUR."""
    rate = EUR_RATES.get(currency, 1.0)
    return value * rate
```

Numbeo devuelve los precios acompañados del código de moneda de cada país. El pipeline:
1. Lee `numbeo_currency` del JSON de cada ciudad
2. Aplica `to_eur(price, currency)` a todos los campos de precios
3. Guarda el resultado ya en EUR para que el modelo compare manzanas con manzanas

## Por qué esta decisión y no otra

Hay dos opciones para obtener tasas de cambio:

| Opción | Ventajas | Desventajas |
|--------|----------|-------------|
| **API de tasas en tiempo real** (Fixer.io, ECB) | Precisión exacta | Requiere clave API, coste, dependencia externa |
| **Diccionario hardcodeado** | Sin dependencias, siempre funciona, suficiente para comparaciones | Desactualizado si una moneda se devalúa mucho |

Para NomadOptima elegimos el diccionario hardcodeado porque:
- No necesitamos precisión financiera — comparamos ciudades, no hacemos transacciones
- Las tasas no cambian tanto mes a mes en monedas estables (EUR, GBP, USD)
- Para monedas volátiles (ARS, TRY), la comparación relativa entre ciudades sigue siendo válida aunque la tasa exacta varíe un 10%

**Nota:** Si en algún momento NomadOptima evoluciona a hacer cálculos de presupuesto reales para el usuario, habría que pasar a tasas de cambio en tiempo real.

## Para recordar en una entrevista

> "Cuando integras datos de precios de múltiples países, la conversión de moneda es un paso obligatorio de preprocessing que va antes de cualquier normalización o feature engineering. Sin ella, el modelo trata 343.396 HUF y 1.200 EUR como si fueran la misma magnitud. La solución más pragmática para un sistema de recomendación es un diccionario de tasas aproximadas — suficiente para comparaciones relativas entre ciudades."

---

# 14. Capping de Features (Feature Clamping)

## Concepto (desde cero)

**Feature clamping** (también llamado winsorization o capping) es una técnica de preprocessing que consiste en limitar el valor máximo que puede tomar una feature:

```
valor_capped = min(valor_original, max_val)
```

Imagina que tienes la feature "número de restaurantes" para estas ciudades:
- Madrid: 612 restaurantes
- Fuerteventura: 37 restaurantes
- Berlín: 580 restaurantes
- Tarifa: 28 restaurantes

Si el modelo usa estos valores directamente, Madrid y Berlín siempre ganan en la dimensión "gastronomía" simplemente por ser ciudades grandes — aunque tanto Fuerteventura como Tarifa tengan suficientes restaurantes para satisfacer a cualquier viajero.

El problema es que el número absoluto de restaurantes captura "tamaño de la ciudad" más que "disponibilidad de gastronomía". A partir de un cierto umbral, más restaurantes no mejoran la experiencia del usuario.

Con capping de 80:
- Madrid: min(612, 80) = **80**
- Fuerteventura: min(37, 80) = **37**
- Berlín: min(580, 80) = **80**
- Tarifa: min(28, 80) = **28**

Ahora Madrid y Berlín empatan en "suficientes restaurantes" y no aplastan a las ciudades pequeñas.

## Cómo lo usamos en NomadOptima

En `src/processing/features.py` aplicamos capping a todos los count features de Google Places y OSM:

```python
CAPS = {
    'gp_restaurant':     80,   # 80+ = "ciudad con buena oferta gastronómica"
    'gp_bar':            60,   # 60+ = "buena vida nocturna"
    'gp_coworking':      15,   # 15+ = "hub de nómadas"
    'gp_museum':         20,   # 20+ = "ciudad cultural"
    'gp_gym':            30,   # 30+ = "suficientes opciones deportivas"
    'gp_hotel':          50,   # 50+ = "buena oferta de alojamiento"
    'osm_bicycle_lanes': 200,  # en km
    'osm_parks':         40,
}

for col, cap in CAPS.items():
    if col in df.columns:
        df[col] = df[col].clip(upper=cap)
```

Los umbrales se eligieron basándose en análisis del EDA: ¿a partir de qué número una ciudad ya tiene "suficiente" de ese tipo de lugar para cualquier viajero?

## Por qué esta decisión y no otra

Sin capping, el modelo aprendería a usar las features de count simplemente como proxy de "tamaño de ciudad". Esto penaliza sistemáticamente:
- Las islas (Fuerteventura, Ibiza, Bali)
- Las ciudades pequeñas (Tarifa, Chamonix, Essaouira)
- Los destinos emergentes (Tbilisi, Da Nang)

Con capping, el modelo puede diferenciar ciudades por sus características reales (¿tiene playa? ¿tiene coworking? ¿tiene pistas de ski?) sin que el tamaño de la ciudad domine el resultado.

**Alternativa descartada:** Normalización logarítmica `log(1 + count)`. También reduce el efecto de valores extremos pero es menos interpretable (¿qué significa un valor de 4.12 en la escala logarítmica?). El capping es más intuitivo: hay un umbral que significa "suficiente".

## Para recordar en una entrevista

> "Feature clamping o winsorization es una técnica para limitar el impacto de valores extremos en features de conteo. En un sistema de recomendación geográfico, sin capping las ciudades grandes siempre ganan en features de infraestructura solo por tener más oferta en términos absolutos. El capping convierte la pregunta de '¿cuántos restaurantes tiene?' a '¿tiene suficientes restaurantes?', que es lo que realmente le importa al usuario."

---

# 15. Feature Fallbacks — Fuente Secundaria cuando la Primaria Falla

## Concepto (desde cero)

Un **feature fallback** es una estrategia de diseño de pipelines de datos: cuando la fuente primaria de datos falla o devuelve valores inválidos, activar automáticamente una fuente secundaria en lugar de dejar el valor como 0 o NaN.

El patrón es:
```
1. Intentar obtener el dato de la fuente primaria
2. Si la fuente primaria falla (0, None, timeout, error) → usar fuente secundaria
3. Si la fuente secundaria también falla → usar valor por defecto de negocio
```

Este patrón se llama **graceful degradation** en ingeniería de software: el sistema "degrada" su funcionamiento de forma elegante cuando algo falla, en lugar de crashear o producir datos incorrectos.

## El problema que resolvemos: OSM falla en islas

OpenStreetMap (Overpass API) es nuestra fuente primaria para features de infraestructura urbana: restaurantes, bares, hospitales, parques, etc.

Para ciudades en islas (Fuerteventura, Bali, Da Nang), la query de Overpass devuelve 0 en todos los campos. No es que esas ciudades no tengan bares y restaurantes — es que la query falla silenciosamente por la geometría de la isla.

Resultado sin fallback: Fuerteventura tiene `osm_restaurant = 0` → el modelo la ignora para cualquier perfil gastronómico.

## Cómo lo usamos en NomadOptima

Google Places tiene tipos genéricos (`restaurant`, `cafe`, `bar`) que funcionan correctamente incluso en islas porque usa geocodificación diferente a OSM.

```python
def build_city_features(city_data):
    """Construye el vector de features de una ciudad con fallbacks."""

    # Feature primaria: OSM
    n_restaurantes = city_data.get('osm_restaurant', 0)

    # Si OSM falla (devuelve 0), usar Google Places como fallback
    if n_restaurantes == 0:
        n_restaurantes = city_data.get('gp_restaurant', {}).get('count', 0)

    # Si ambos fallan, usar el valor de negocio por defecto
    if n_restaurantes == 0:
        n_restaurantes = 10  # "cualquier ciudad tiene al menos 10 restaurantes"

    return min(n_restaurantes, CAPS['gp_restaurant'])  # aplicar capping
```

**Resultado medible:** Fuerteventura pasó de cosine_similarity=0.34 a 0.39 para perfiles de playa/kite simplemente por tener features no-cero en gastronomía.

## La lección sobre diseño de pipelines

Siempre deberías tener al menos dos fuentes para features críticas. En NomadOptima:

| Feature | Fuente primaria | Fuente secundaria | Fallback de negocio |
|---------|----------------|-------------------|---------------------|
| Restaurantes | OSM `amenity=restaurant` | GP `restaurant` | 10 |
| Bares | OSM `amenity=bar` | GP `bar` | 5 |
| Hospitales | OSM `amenity=hospital` | GP `hospital` | 1 |
| Coworking | GP `coworking_space` | OSM `office=coworking` | 0 |
| Coste alquiler | Numbeo scraping | NUMBEO_FALLBACK dict | 1000 EUR |

## Para recordar en una entrevista

> "En pipelines de ML con múltiples fuentes de datos externas, siempre diseñamos con fallbacks en cascada: fuente primaria → fuente secundaria → valor de negocio por defecto. Los fallos silenciosos (la fuente devuelve 0 en lugar de error) son los más peligrosos porque el modelo los interpreta como 'esta ciudad no tiene nada', lo que produce recomendaciones incorrectas. El patrón de fallback es una forma de graceful degradation: el sistema sigue funcionando con datos de menor calidad en lugar de fallar completamente."

---

# 16. Decomposición de Dimensiones — Split de Features Genéricas

## Concepto (desde cero)

La **decomposición de dimensiones** (o feature decomposition) es una técnica de feature engineering donde dividimos una dimensión genérica en varias sub-dimensiones específicas, cada una con semántica propia.

El problema que resuelve: cuando una categoría como "Deporte activo" agrupa actividades que no tienen nada en común y se modelan con features de ciudad completamente distintas, el modelo no puede distinguir entre ellas.

Ejemplo concreto del problema que tuvimos:
- User profile: `user_imp_deporte = 0.9` (le encanta el deporte)
- Madrid: muchos gimnasios, piscinas, tenis → `city_gp_gym = 60`, `city_gp_tennis = 15`
- Tarifa: kite capital mundial → `city_gp_surf_school = 8`, playa `city_gp_beach = 1`

Con una sola dimensión, `user_imp_deporte = 0.9` se multiplica por las features de ciudad de todos los tipos de deporte. Madrid gana porque tiene más features deportivas absolutas (60 gimnasios > 8 escuelas de surf). Tarifa pierde aunque sea la mejor opción para el usuario que quiere kite.

El problema tiene nombre técnico: **feature aliasing** — estamos usando el mismo número para representar cosas semánticamente distintas.

## La solución: 3 sub-dimensiones independientes

```python
# ANTES — una dimensión genérica
user_profile = {
    "user_imp_deporte": 0.9   # ¿qué tipo? el modelo no lo sabe
}

# DESPUÉS — tres dimensiones con semántica propia
user_profile = {
    "user_imp_deporte_agua":    0.9,  # kite, surf, windsurf, snorkel, kayak, playa
    "user_imp_deporte_montana": 0.0,  # ski, escalada, senderismo, aventura
    "user_imp_deporte_urbano":  0.1,  # gym, fitness, tenis, piscina, ciclismo
}
```

Cada sub-dimensión se cruza exclusivamente con las features de ciudad relevantes:

| Sub-dimensión | Features de ciudad asociadas |
|--------------|------------------------------|
| `deporte_agua` | `gp_surf_school`, `gp_marina`, `gp_beach`, `gp_snorkeling`, `gp_kayaking` |
| `deporte_montana` | `gp_ski_resort`, `gp_snowpark`, `osm_hiking_routes`, `gp_climbing` |
| `deporte_urbano` | `gp_gym`, `gp_fitness_center`, `gp_tennis`, `gp_swimming_pool`, `gp_cycling` |

Con esto, el usuario que quiere kite activa solo `deporte_agua = 0.9` y el modelo multiplica eso por las features de playa y surf, ignorando los gimnasios de Warsaw.

## Cómo lo usamos en NomadOptima

En el formulario de usuario, en lugar de un slider "Deporte activo" mostramos tres preguntas específicas:

```
¿Qué tipo de deporte practicas?
[🏄 Deportes de agua]  → user_imp_deporte_agua
[🏔️ Montaña / aventura] → user_imp_deporte_montana
[🏋️ Deporte urbano]    → user_imp_deporte_urbano
```

En `features.py`, la puntuación de una ciudad para un usuario se calcula así:

```python
score_deporte = (
    user['deporte_agua']    * ciudad['score_agua']    +
    user['deporte_montana'] * ciudad['score_montana'] +
    user['deporte_urbano']  * ciudad['score_urbano']
)
```

**Resultado medible:** Después del split, para perfil kite/windsurf:
- Tarifa: #1 (cosine_sim = 0.5054) ✓
- Fuerteventura: #2 (cosine_sim = 0.4864) ✓
- Warsaw: desapareció del top 5 ✓

## Por qué esta decisión y no otra

La alternativa sería crear una feature de ciudad por cada actividad deportiva específica y dejarlo todo en una dimensión genérica. Pero eso requeriría que el usuario especificara exactamente qué actividad quiere con mucha granularidad. La decomposición en 3 grupos es un compromiso entre:
- **Granularidad del usuario**: 3 preguntas en el formulario, no 20
- **Precisión del modelo**: suficiente para distinguir kite vs gym vs ski
- **Extensibilidad futura**: cada sub-dimensión puede ampliarse con más features de ciudad sin cambiar la interfaz de usuario

## Para recordar en una entrevista

> "La granularidad de las dimensiones es crítica en sistemas de recomendación. Si una dimensión como 'deporte' agrupa actividades semánticamente distintas (kite vs gym), el modelo no puede distinguir qué tipo de deporte quiere el usuario. La técnica se llama feature decomposition o dimensionality split: dividir una dimensión genérica en sub-dimensiones específicas, cada una activando solo las features de item relevantes. El resultado directo fue que Warsaw dejó de aparecer en #1 para perfiles de kitesurf y Tarifa pasó a #1 donde debía estar."

---

# 17. Diseño de Perfiles Sintéticos con Arquetipos

## Concepto (desde cero)

Un **arquetipo de usuario** es un perfil tipo que representa un grupo de personas con preferencias coherentes y específicas. En lugar de generar preferencias de forma aleatoria e independiente, los arquetipos definen qué dimensiones son importantes para ese tipo de usuario y cuáles no.

La alternativa (lo que hacíamos en v2) es generar cada dimensión de forma independiente con una distribución estadística. El problema: la independencia entre dimensiones produce perfiles que nadie representaría en el mundo real. Un usuario que ama el kite surf no tiene simultáneamente gastronomía=0.9, cultura=0.85, vida nocturna=0.88, y 10 otras prioridades igualmente altas.

## El problema que resuelven los arquetipos: popularity bias

En sistemas de recomendación, el **popularity bias** (sesgo por popularidad) ocurre cuando el modelo aprende a recomendar items que tienen buena cobertura en muchas dimensiones en lugar de items que son excepcionales en pocas dimensiones.

Con perfiles densos (muchas dimensiones altas), una ciudad como Berlín acumula puntos en 40 features distintas aunque en ninguna sea excepcional. Una ciudad nicho como Tarifa acumula puntos solo en 4-6 features de deporte acuático, pero en esas features es la mejor del mundo. Resultado: Berlín siempre gana aunque el usuario quiera kite surf.

Los arquetipos resuelven esto creando perfiles donde la especialización es real: el usuario kite surf tiene `deporte_agua = 0.95` y `cultura = 0.12`. El producto punto con Tarifa es alto. El producto punto con Berlín es bajo.

## Cómo lo usamos en NomadOptima

En `notebooks/02_synthetic_profiles_v3.ipynb` definimos 14 arquetipos:

| Arquetipo | Dimensiones HIGH | Proporción |
|-----------|-----------------|------------|
| kite_surf | deporte_agua, clima, naturaleza | 7% |
| nomada_barato | coste_vida, nomada_digital, movilidad | 8% |
| nomada_premium | nomada_digital, calidad_vida, gastronomia | 6% |
| ski | deporte_montana, clima, naturaleza | 5% |
| cultura_arte | cultura, arte_visual, turismo | 9% |
| ejecutivo_cosmopolita | calidad_vida, gastronomia, cultura | 7% |
| familia_hijos | familia, salud, movilidad | 8% |
| jubilado_activo | clima, bienestar, naturaleza | 7% |
| estudiante | coste_vida, vida_nocturna, movilidad | 8% |
| deportista_outdoor | naturaleza, deporte_agua, deporte_montana | 6% |
| backpacker | coste_vida, movilidad, autenticidad | 7% |
| bienestar_yoga | bienestar, naturaleza, clima | 6% |
| lgbtq_friendly | vida_nocturna, comunidad, cultura | 5% |
| fotografia_viaje | impacto_visual, turismo, cultura | 6% |

El 70% de los usuarios generados se asignan aleatoriamente a uno de estos arquetipos. El 30% restante son **perfiles mixtos** generados con distribución uniforme pero con techo en 0.65 para evitar perfiles extremadamente densos.

## Código de ejemplo

```python
def generar_perfil_arquetipo(arquetipo_def, dimensiones):
    """
    Genera un vector de preferencias coherente para un arquetipo dado.
    
    Las dimensiones HIGH usan beta(8,2) → valores concentrados en 0.75-0.99
    Las dimensiones MEDIUM usan beta(4,4) → valores concentrados en 0.35-0.65
    Las dimensiones LOW usan beta(1.5,6) → valores concentrados en 0.05-0.30
    """
    perfil = {}
    high_dims   = arquetipo_def.get("HIGH", [])
    medium_dims = arquetipo_def.get("MEDIUM", [])
    low_dims    = arquetipo_def.get("LOW", [])
    
    for dim in dimensiones:
        if dim in high_dims:
            perfil[dim] = np.random.beta(8, 2)    # 0.75 - 0.99
        elif dim in medium_dims:
            perfil[dim] = np.random.beta(4, 4)    # 0.35 - 0.65
        elif dim in low_dims:
            perfil[dim] = np.random.beta(1.5, 6)  # 0.05 - 0.30
        else:
            # Dimensiones no especificadas: valor bajo-medio por defecto
            perfil[dim] = np.random.beta(2, 5)    # 0.10 - 0.45
    return perfil
```

## Por qué esta decisión y no otra

La alternativa más simple sería seguir con distribuciones independientes pero reducir el número de dimensiones altas por perfil (por ejemplo, forzando que solo 3-5 dimensiones superen 0.7). El problema es que esto seguiría siendo arbitrario y no reflejaría coherencia semántica.

Los arquetipos son mejores porque:
1. **Coherencia semántica**: un kite surfer real tiene su preferencia de deporte_agua correlacionada con clima (necesita viento y calor). Los arquetipos capturan esta correlación implícita.
2. **Validación cualitativa**: podemos validar manualmente que Tarifa aparece en top 3 para el arquetipo kite_surf. Con perfiles aleatorios, no hay forma de saber qué "debería" salir.
3. **Cobertura de ciudades nicho**: los arquetipos garantizan que habrá suficientes usuarios para los que Tarifa o Dakhla son la mejor opción → el modelo recibe ejemplos de entrenamiento donde esas ciudades tienen label alto.

El riesgo de los arquetipos es que el modelo aprende a recomendar según nuestras reglas predefinidas (qué perfiles hemos definido y con qué pesos), no según preferencias de usuarios reales. Esto se llama **data-driven bias by design**: diseñamos los datos para que reflejen nuestras hipótesis. La validación final tiene que hacerse con usuarios reales en producción.

## Para recordar en una entrevista

> "Los datos sintéticos son una herramienta poderosa cuando no tienes datos reales, pero su diseño es tan crítico como el algoritmo. En NomadOptima, la v1 de perfiles sintéticos usaba distribuciones independientes por dimensión, lo que generaba perfiles incoherentes y producía popularity bias: el modelo recomendaba ciudades grandes con cobertura global en lugar de destinos especializados como Tarifa para kite surf. La solución fue diseñar arquetipos de usuario con distribuciones condicionales: las dimensiones relevantes para ese arquetipo usan beta(8,2), el resto usan beta(1.5,6). Esto garantiza coherencia semántica y que ciudades nicho reciban etiquetas altas en los ejemplos de entrenamiento correspondientes."

---

# 18. Control de versiones con Git — Cómo hacer un commit limpio después de una sesión larga

## Concepto
Git tiene tres zonas que hay que entender bien:
- **Working directory**: tus archivos reales en el disco
- **Staging area**: la "fotografía" que has preparado para el próximo commit (con `git add`)
- **Repositorio**: los commits ya guardados definitivamente

El error más común en sesiones largas: haces `git add` al principio, sigues trabajando horas, y al final el staging tiene versiones antiguas. Si commiteas en ese estado, subes código viejo.

## El problema que tuvimos en NomadOptima
Después de una sesión de desarrollo larga:
- Los mismos archivos aparecían en "staged" Y en "not staged" simultáneamente
- Archivos generados (city_features.csv, HTMLs) sin proteger en .gitignore
- 1 commit local sin pushear con capas de cambios encima sin commitear

## Método — Cómo hacer un commit limpio (hazlo tú sola)

### Paso 1: Diagnóstico — entiende el estado actual
```bash
git status          # ver qué está staged, modificado y sin seguimiento
git log --oneline -5  # ver los últimos commits
git stash list      # ver si hay trabajo guardado en stash
```
Antes de tocar nada, **lee el output completo**. Identifica:
- ¿Hay archivos staged que no deberían estar?
- ¿Hay archivos modificados que sí deberían subir?
- ¿Hay archivos sin seguimiento que deberían estar en .gitignore?

### Paso 2: Desescenifica todo (limpia el staging sin perder nada)
```bash
git restore --staged .
```
Esto saca todo del staging area pero **NO toca tus archivos**. Tu código sigue intacto. Solo limpia la "fotografía" para empezar desde cero.

### Paso 3: Actualiza .gitignore antes de añadir nada
Abre `.gitignore` y asegúrate de que están protegidos:
- Archivos generados grandes (`*.csv` en data/, `*.html` en data/processed/, notebooks grandes)
- Carpetas de entorno (`.venv/`, `__pycache__/`, `.env`)
- Carpetas de herramientas locales (`.claude/`)

Comprueba que un archivo está ignorado con:
```bash
git check-ignore -v nombre_del_archivo
```

### Paso 4: Añade solo lo que debe subir al repo
Nunca uses `git add .` o `git add -A` — añade archivos específicos o carpetas concretas:
```bash
git add src/
git add app/
git add scripts/
git add CLAUDE.md LEARNING.md ERRORS_LOG.md PROJECT_STATUS.md
git add requirements.txt .gitignore
```
Regla: **sube código, documentación y configuración. No subas datos generados ni archivos de tu máquina.**

### Paso 5: Revisa qué vas a commitear
```bash
git diff --cached --stat
```
Esto muestra exactamente qué está en el staging. Léelo antes de commitear. Si ves algo raro, usa `git restore --staged nombre_archivo` para sacarlo.

### Paso 6: Commit con mensaje claro
```bash
git commit -m "descripción concisa de qué cambia y por qué"
```
Buenas prácticas para el mensaje:
- Usa verbos en presente: "añade", "corrige", "refactoriza", "amplía"
- Describe el QUÉ y el POR QUÉ, no el CÓMO
- Si es mucho, usa la primera línea como resumen y añade detalle después

### Paso 7: Push
```bash
git push origin main
```
Si hay un commit anterior sin pushear y este también, ambos subirán juntos. Git los enviará en orden.

### Paso 8: Verifica
```bash
git status          # debe decir "nothing to commit, working tree clean"
git log --oneline -3  # el nuevo commit debe aparecer
```

## Señales de alerta — cuándo revisar antes de commitear
- El mismo archivo aparece en "staged" y en "not staged" → versión antigua en staging
- Archivos muy grandes en "Untracked files" → probablemente deberían ir a .gitignore
- `git diff --cached` muestra miles de líneas → puede haber datos generados colados

## Por qué esta decisión y no otra
Usar `git restore --staged .` como primer paso es más seguro que `git reset HEAD` o `git reset --hard` porque:
- **No modifica el working directory** — tus archivos no cambian
- **Solo afecta al staging** — deshace los `git add` sin perder trabajo
- Es completamente reversible si te equivocas

---

*Última actualización: 08/04/2026 — sección 18 git método commit limpio*
