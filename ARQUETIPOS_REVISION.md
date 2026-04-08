# Arquetipos de Usuario — Para revisión de Carlos
> Generado: 08/04/2026 | Revisar antes de aprobar el dataset final

Este archivo describe los arquetipos usados para generar los 5.000 perfiles
sintéticos del training dataset. Cada arquetipo tiene dimensiones altas (>0.75)
y el resto bajo (<0.30) para que las ciudades nicho (Tarifa, Fuerteventura,
Tbilisi, etc.) puedan competir con las grandes capitales.

---

## Por qué arquetipos y no perfiles aleatorios

**Problema detectado:** Con perfiles 100% aleatorios (beta independiente por dimensión),
la suma media de importancias es 12.99/26. Casi todos los usuarios tienen muchas
dimensiones altas simultáneamente → las grandes ciudades con "algo de todo" (Berlín,
Warsaw, Amsterdam) siempre ganan → Tarifa y Fuerteventura nunca aparecen en el top.

**Solución:** 70% de perfiles basados en arquetipos (dimensiones coherentes),
30% de perfiles mixtos aleatorios (para que el modelo aprenda transiciones).

---

## Los 14 arquetipos (70% del dataset = 3.500 usuarios)

| # | Nombre | % | Usuarios | Ciudades esperadas en top |
|---|--------|---|----------|--------------------------|
| 1 | Kite & Surf | 6% | 300 | Tarifa, Fuerteventura, Las Palmas |
| 2 | Nómada Digital Barato | 10% | 500 | Tbilisi, Sofia, Krakow, Bucharest |
| 3 | Nómada Digital Premium | 6% | 300 | Barcelona, Amsterdam, Berlin, Lisbon |
| 4 | Cultura & Arte | 8% | 400 | Paris, Vienna, Prague, Athens |
| 5 | Gastronomía & Vida Social | 7% | 350 | San Sebastian, Barcelona, Bologna* |
| 6 | Familia con hijos | 8% | 400 | Valencia, Alicante, Malaga, Munich |
| 7 | Ski & Montaña | 5% | 250 | Andorra, Chamonix, Innsbruck |
| 8 | Bienestar & Naturaleza | 7% | 350 | Faro, Granada, Ljubljana |
| 9 | Vida Nocturna & Social | 5% | 250 | Belgrade, Berlin, Budapest |
| 10 | Jubilado Activo (cálido) | 7% | 350 | Malaga, Alicante, Fuerteventura |
| 11 | Mochilero Barato | 5% | 250 | Medellin, Cartagena, Mexico City |
| 12 | Cosmopolita Urbano | 6% | 300 | London, Paris, Milan, Amsterdam |
| 13 | Mascotas & Naturaleza | 4% | 200 | Granada, Faro, Ljubljana |
| 14 | Comprador & Servicios | 6% | 300 | Madrid, Barcelona, Brussels |

*ciudades marcadas con * no están en el dataset actual pero pueden añadirse

---

## Detalle de cada arquetipo

### 1. Kite & Surf
```
ALTO (0.80-0.99):  deporte_agua, naturaleza, clima, autenticidad
MEDIO (0.40-0.65): movilidad, coste, social_media
BAJO (0.05-0.25):  familia, educacion, comunidad, servicios,
                   arte_visual, cultura, nomada, bienestar
```
Ciudades esperadas en top 5: Tarifa, Fuerteventura, Las Palmas, Alicante, Faro

---

### 2. Nómada Digital Barato
```
ALTO (0.80-0.99):  nomada, coste, calidad_vida, clima
MEDIO (0.40-0.65): movilidad, gastronomia, vida_nocturna, autenticidad
BAJO (0.05-0.25):  familia, educacion, comunidad, deporte_agua,
                   deporte_montana, mascotas, arte_visual
```
Ciudades esperadas en top 5: Tbilisi, Sofia, Krakow, Bucharest, Belgrade

---

### 3. Nómada Digital Premium
```
ALTO (0.80-0.99):  nomada, calidad_vida, gastronomia, cultura
MEDIO (0.40-0.65): coste, movilidad, vida_nocturna, bienestar
BAJO (0.05-0.25):  familia, educacion, comunidad, deporte_agua,
                   deporte_montana, mascotas
```
Ciudades esperadas en top 5: Barcelona, Amsterdam, Berlin, Lisbon, Milan

---

### 4. Cultura & Arte
```
ALTO (0.80-0.99):  cultura, arte_visual, turismo, gastronomia
MEDIO (0.40-0.65): movilidad, calidad_vida, vida_nocturna
BAJO (0.05-0.25):  deporte_agua, deporte_montana, mascotas,
                   familia, comunidad, nomada, coste
```
Ciudades esperadas en top 5: Paris, Vienna, Prague, Athens, Milan

---

### 5. Gastronomía & Vida Social
```
ALTO (0.80-0.99):  gastronomia, vida_nocturna, social_media, autenticidad
MEDIO (0.40-0.65): turismo, cultura, movilidad, calidad_vida
BAJO (0.05-0.25):  deporte_agua, deporte_montana, familia,
                   educacion, comunidad, mascotas, nomada
```
Ciudades esperadas en top 5: San Sebastian, Seville, Barcelona, Porto, Malaga

---

### 6. Familia con Hijos
```
ALTO (0.80-0.99):  familia, salud, movilidad, calidad_vida, educacion
MEDIO (0.40-0.65): compras, servicios, bienestar, clima
BAJO (0.05-0.25):  vida_nocturna, deporte_agua, musica, social_media,
                   nomada, autenticidad, arte_visual
```
Ciudades esperadas en top 5: Valencia, Alicante, Malaga, Munich, Amsterdam

---

### 7. Ski & Montaña
```
ALTO (0.80-0.99):  deporte_montana, naturaleza, clima, bienestar
MEDIO (0.40-0.65): autenticidad, gastronomia, calidad_vida
BAJO (0.05-0.25):  familia, nomada, vida_nocturna, musica,
                   deporte_agua, comunidad, social_media
```
Ciudades esperadas en top 5: Andorra, Chamonix, Innsbruck, Munich, Granada

---

### 8. Bienestar & Naturaleza
```
ALTO (0.80-0.99):  bienestar, naturaleza, clima, calidad_vida
MEDIO (0.40-0.65): deporte_urbano, gastronomia, autenticidad, turismo
BAJO (0.05-0.25):  vida_nocturna, nomada, educacion, comunidad,
                   familia, mascotas, deporte_agua
```
Ciudades esperadas en top 5: Faro, Granada, Ljubljana, Malaga, Montpellier

---

### 9. Vida Nocturna & Social
```
ALTO (0.80-0.99):  vida_nocturna, musica, social_media, gastronomia
MEDIO (0.40-0.65): cultura, arte_visual, autenticidad, movilidad
BAJO (0.05-0.25):  familia, educacion, salud, deporte_montana,
                   mascotas, nomada, coste
```
Ciudades esperadas en top 5: Belgrade, Budapest, Berlin, Barcelona, Amsterdam

---

### 10. Jubilado Activo (cálido)
```
ALTO (0.80-0.99):  clima, calidad_vida, salud, bienestar, gastronomia
MEDIO (0.40-0.65): movilidad, turismo, compras, naturaleza
BAJO (0.05-0.25):  vida_nocturna, nomada, educacion, deporte_montana,
                   social_media, musica, arte_visual
```
Ciudades esperadas en top 5: Malaga, Alicante, Fuerteventura, Las Palmas, Faro

---

### 11. Mochilero Barato
```
ALTO (0.80-0.99):  coste, autenticidad, naturaleza, gastronomia
MEDIO (0.40-0.65): movilidad, vida_nocturna, turismo, social_media
BAJO (0.05-0.25):  familia, educacion, comunidad, servicios,
                   bienestar, deporte_montana, compras
```
Ciudades esperadas en top 5: Medellin, Cartagena, Mexico City, Tbilisi, Belgrade

---

### 12. Cosmopolita Urbano
```
ALTO (0.80-0.99):  cultura, gastronomia, movilidad, compras, arte_visual
MEDIO (0.40-0.65): vida_nocturna, calidad_vida, turismo, servicios
BAJO (0.05-0.25):  deporte_agua, deporte_montana, mascotas,
                   comunidad, naturaleza, autenticidad
```
Ciudades esperadas en top 5: London, Paris, Milan, Amsterdam, Barcelona

---

### 13. Mascotas & Naturaleza
```
ALTO (0.80-0.99):  mascotas, naturaleza, bienestar, calidad_vida
MEDIO (0.40-0.65): deporte_urbano, clima, gastronomia, autenticidad
BAJO (0.05-0.25):  vida_nocturna, nomada, educacion, comunidad,
                   arte_visual, social_media, musica
```
Ciudades esperadas en top 5: Granada, Faro, Ljubljana, Malaga, Valencia

---

### 14. Comprador & Servicios
```
ALTO (0.80-0.99):  compras, servicios, movilidad, salud, calidad_vida
MEDIO (0.40-0.65): gastronomia, familia, turismo
BAJO (0.05-0.25):  deporte_agua, deporte_montana, autenticidad,
                   musica, comunidad, nomada, mascotas
```
Ciudades esperadas en top 5: Madrid, Barcelona, Brussels, Amsterdam, London

---

## Perfiles mixtos (30% = 1.500 usuarios)

Generados con la distribución beta(0.5, 0.5) original pero con un **techo de 0.65**
en cada dimensión para evitar perfiles con demasiadas dimensiones simultáneamente altas.
Representan usuarios con preferencias poco definidas o en transición.

---

## Varianza dentro de cada arquetipo

Para que no todos los usuarios del mismo arquetipo sean idénticos, cada dimensión
se genera con ruido gaussiano ±0.08 dentro de su rango objetivo, garantizando
que los valores se mantienen entre 0 y 1.

Ejemplo para Kite & Surf (deporte_agua objetivo = 0.90 ± 0.08):
- Usuario A: deporte_agua = 0.94
- Usuario B: deporte_agua = 0.86
- Usuario C: deporte_agua = 0.91

---

## Preguntas para revisar

- [ ] ¿Faltan arquetipos importantes para el proyecto?
- [ ] ¿Los porcentajes de cada arquetipo tienen sentido?
- [ ] ¿Las ciudades esperadas en cada top 5 son coherentes con lo que quieres mostrar?
- [ ] ¿Añadimos o quitamos algún arquetipo?
- [ ] ¿El 70/30 entre arquetipos y mixtos es la proporción correcta?

---

*Archivo generado automáticamente para revisión. No tocar hasta que Carlos dé el OK.*
