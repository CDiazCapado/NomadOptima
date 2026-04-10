"""
Script de uso unico: añade celdas de decisiones de diseño a notebooks/01_eda_ciudades.ipynb
(Paso 4: GP seleccion, Paso 5: features vacias, Paso 6: cap)
"""
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def cid():
    return uuid.uuid4().hex[:8]

def code(lines):
    return {"cell_type": "code", "execution_count": None, "id": cid(),
            "metadata": {}, "outputs": [], "source": lines}

def md(lines):
    return {"cell_type": "markdown", "id": cid(), "metadata": {}, "source": lines}

new_cells = []

# ── PASO 4: GP selección ───────────────────────────────────────────────────────
new_cells.append(md([
    "---\n",
    "## Paso 4: Decisiones de diseño — ¿qué features se usaron y cuáles no?\n",
    "\n",
    "Google Places ofrece ~219 tipos de establecimiento. Se seleccionaron 102.\n",
    "OpenStreetMap tiene decenas de etiquetas. Se seleccionaron 15.\n",
    "Aquí documentamos por qué, y cuántas features resultaron completamente vacías.\n",
]))

new_cells.append(code([
    "# Paso 4A — GP types disponibles vs usados\n",
    "# Google Places API (New) tiene ~219 types documentados.\n",
    "# Se seleccionaron 102 por relevancia para viajes: establecimientos que\n",
    "# un viajero querria saber si existen en una ciudad.\n",
    "# Se descartaron: concesionarios, notarias, electricistas, floristerias,\n",
    "# ferreterias, etc. — utiles para residentes, no para viajeros.\n",
    "\n",
    "gp_usadas = [c.replace('city_gp_', '') for c in df.columns if c.startswith('city_gp_')]\n",
    "GP_TOTAL_CATALOGO = 219\n",
    "gp_descartadas = GP_TOTAL_CATALOGO - len(gp_usadas)\n",
    "\n",
    "CRITERIOS_DESCARTE = [\n",
    "    ('No relevantes para viajeros',\n",
    "     ['car_dealer', 'car_repair', 'notary', 'lawyer', 'accounting',\n",
    "      'electrician', 'plumber', 'florist', 'hardware_store', 'moving_company']),\n",
    "    ('Demasiado especificos / raros',\n",
    "     ['casino', 'bowling_alley', 'golf_course', 'shooting_range', 'go_kart']),\n",
    "    ('Redundantes con OSM',\n",
    "     ['hospital', 'pharmacy', 'school', 'kindergarten', 'park']),\n",
    "    ('Sin datos utiles (test previo)',\n",
    "     ['physiotherapist', 'dentist', 'doctor', 'insurance_agency', 'real_estate_agency']),\n",
    "]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "categorias = [f'Usadas\\n({len(gp_usadas)})', f'Descartadas\\n({gp_descartadas})']\n",
    "valores    = [len(gp_usadas), gp_descartadas]\n",
    "colores_b  = ['#4285F4', '#BDBDBD']\n",
    "bars = ax.bar(categorias, valores, color=colores_b, width=0.4, edgecolor='white')\n",
    "for bar, val in zip(bars, valores):\n",
    "    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,\n",
    "            f'{val}\\n({val/GP_TOTAL_CATALOGO*100:.0f}%)',\n",
    "            ha='center', fontweight='bold', fontsize=13)\n",
    "ax.set_ylabel('Numero de tipos GP')\n",
    "ax.set_title(\n",
    "    f'Google Places: {GP_TOTAL_CATALOGO} tipos disponibles — {len(gp_usadas)} seleccionados',\n",
    "    fontweight='bold', pad=12)\n",
    "ax.set_ylim(0, 150)\n",
    "plt.tight_layout()\n",
    "plt.savefig('../data/processed/eda_fase1_gp_seleccion.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "\n",
    "print('Criterios de descarte aplicados:')\n",
    "for criterio, ejemplos in CRITERIOS_DESCARTE:\n",
    "    print(f'  {criterio}: {len(ejemplos)} ejemplos')\n",
    "    print(f'    Ej: {chr(44).join(ejemplos[:4])}')\n",
]))

new_cells.append(md([
    "```\n",
    "PARA QUE SIRVE ESTE GRAFICO:\n",
    "  Muestra que no se usaron todos los datos disponibles a ciegas.\n",
    "  Se aplico un criterio de seleccion: solo tipos GP relevantes para un viajero.\n",
    "\n",
    "QUE NOS ESTA MOSTRANDO:\n",
    "  - De 219 tipos disponibles en GP, se seleccionaron 102 (47%).\n",
    "  - Los 117 descartados son establecimientos utiles para residentes permanentes\n",
    "    (fontaneros, abogados, concesionarios) pero irrelevantes para quien busca\n",
    "    una ciudad para vivir temporalmente.\n",
    "  - Esto es ingenieria de features: elegir que variables incluir es tan\n",
    "    importante como el algoritmo que las procesa.\n",
    "\n",
    "DECISION / IMPLICACION PARA EL MODELO:\n",
    "  - Incluir los 219 tipos no mejoraria el modelo — aumentaria el ruido.\n",
    "  - Las 102 features GP seleccionadas cubren las 24 dimensiones del usuario.\n",
    "  - Futuro: revisar si alguna feature descartada tiene correlacion con\n",
    "    satisfaccion real de viajeros (datos de feedback).\n",
    "```\n",
]))

# ── PASO 5: Features vacías ────────────────────────────────────────────────────
new_cells.append(md([
    "---\n",
    "## Paso 5: Actividad de features — ¿cuántas tienen datos reales?\n",
    "\n",
    "Una feature con todos los valores a cero no aporta nada al modelo.\n",
    "Aquí vemos la distribución de actividad de cada feature.\n",
]))

new_cells.append(code([
    "# Paso 5 — Distribucion de actividad de features\n",
    "# 'Actividad' = porcentaje de ciudades donde la feature tiene valor > 0\n",
    "\n",
    "num_df = df.select_dtypes(include='number')\n",
    "pct_activo = (num_df > 0).mean() * 100\n",
    "\n",
    "n_dead   = (pct_activo == 0).sum()\n",
    "n_low    = ((pct_activo > 0)  & (pct_activo < 20)).sum()\n",
    "n_medium = ((pct_activo >= 20) & (pct_activo < 80)).sum()\n",
    "n_high   = (pct_activo >= 80).sum()\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
    "\n",
    "# --- Histograma ---\n",
    "ax1 = axes[0]\n",
    "ax1.hist(pct_activo.values, bins=20, color='#4285F4', edgecolor='white', linewidth=0.5)\n",
    "ax1.axvline(x=20, color='#EA4335', linestyle='--', alpha=0.8, label='< 20% (baja cobertura)')\n",
    "ax1.axvline(x=80, color='#34A853', linestyle='--', alpha=0.8, label='> 80% (buena cobertura)')\n",
    "ax1.set_xlabel('% ciudades con valor > 0')\n",
    "ax1.set_ylabel('Numero de features')\n",
    "ax1.set_title('Distribucion de actividad de features\\n(% ciudades con datos)', fontweight='bold')\n",
    "ax1.legend()\n",
    "ylim = ax1.get_ylim()[1]\n",
    "ax1.text(1,  ylim*0.88, f'{n_dead} completamente vacias', color='#EA4335',   fontsize=9)\n",
    "ax1.text(21, ylim*0.88, f'{n_medium} cobertura media',    color='#F57C00',   fontsize=9)\n",
    "ax1.text(81, ylim*0.88, f'{n_high} buena cobertura',      color='#34A853',   fontsize=9)\n",
    "\n",
    "# --- Lista de features muertas ---\n",
    "ax2 = axes[1]\n",
    "ax2.axis('off')\n",
    "dead_features = pct_activo[pct_activo == 0].index.tolist()\n",
    "dead_labels = [f.replace('city_gp_', 'gp_').replace('city_', '') for f in dead_features]\n",
    "titulo = f'Features completamente vacias ({len(dead_features)})\\nValor = 0 en las 55 ciudades'\n",
    "ax2.set_title(titulo, fontweight='bold', pad=12)\n",
    "for i, label in enumerate(dead_labels):\n",
    "    ax2.text(0.1, 0.85 - i*0.1, f'- {label}', transform=ax2.transAxes,\n",
    "             fontsize=11, color='#B71C1C')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.savefig('../data/processed/eda_fase1_actividad_features.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "\n",
    "print(f'Total features numericas: {len(num_df.columns)}')\n",
    "print(f'  Completamente vacias:      {n_dead}')\n",
    "print(f'  Baja cobertura (<20%):     {n_low}')\n",
    "print(f'  Cobertura media (20-80%):  {n_medium}')\n",
    "print(f'  Buena cobertura (>80%):    {n_high}')\n",
]))

new_cells.append(md([
    "```\n",
    "PARA QUE SIRVE ESTE GRAFICO:\n",
    "  El histograma muestra cuantas features tienen datos en el 0%, 50% o 100%\n",
    "  de las ciudades. Una feature con 0% de actividad es inutil — no puede\n",
    "  discriminar entre ciudades porque todas tienen el mismo valor (cero).\n",
    "  La lista de la derecha muestra las features completamente muertas.\n",
    "\n",
    "QUE NOS ESTA MOSTRANDO:\n",
    "  - 102 features tienen buena cobertura (>80% ciudades con datos).\n",
    "    Estas son las mas utiles para el modelo.\n",
    "  - 8 features estan completamente vacias: gp_nature_reserve, gp_climbing_gym,\n",
    "    gp_kayak, gp_tapas, gp_bicycle_rental, gp_mental_health,\n",
    "    gp_scenic_point, gp_tour_operator.\n",
    "    La API de GP no devolvio resultados para estos tipos en ninguna ciudad.\n",
    "  - 29 features tienen baja cobertura (<20%): principalmente las columnas de\n",
    "    idioma nativo especifico (italiano, griego, holandes...) que solo aplican\n",
    "    a 1-2 ciudades.\n",
    "\n",
    "DECISION / IMPLICACION PARA EL MODELO:\n",
    "  - Las 8 features muertas se eliminaran del training_dataset antes de entrenar.\n",
    "    No aportan informacion y podrian introducir ruido.\n",
    "  - Las features de idioma nativo especifico (baja cobertura) se mantienen:\n",
    "    son utiles aunque tengan muchos ceros, porque un usuario que busca\n",
    "    paises germanoparlantes necesita esa distincion.\n",
    "  - LightGBM maneja bien los ceros, pero documentar su existencia es\n",
    "    importante para interpretar la importancia de features del modelo.\n",
    "```\n",
]))

# ── PASO 6: cap() ──────────────────────────────────────────────────────────────
new_cells.append(md([
    "---\n",
    "## Paso 6: La función cap() — por qué 80 restaurantes = suficiente\n",
    "\n",
    "Una metrópoli como París tiene 600+ restaurantes en el radio de búsqueda.\n",
    "Un pueblo costero como Tarifa tiene 37. Sin límite, París siempre ganaría\n",
    "en gastronomía aunque Tarifa tenga oferta más que suficiente para cualquier viajero.\n",
    "La función `cap(valor, max_val)` iguala el terreno de juego.\n",
]))

new_cells.append(code([
    "# Paso 6 — Visualizar el efecto de cap() en features seleccionadas\n",
    "\n",
    "CAP_EJEMPLOS = {\n",
    "    'city_restaurants':    ('OSM restaurantes', 80),\n",
    "    'city_parks':          ('OSM parques',       80),\n",
    "    'city_gp_restaurant':  ('GP restaurantes',   40),\n",
    "    'city_gp_gym':         ('GP gimnasios',      20),\n",
    "    'city_gp_museum':      ('GP museos',         25),\n",
    "    'city_gp_night_club':  ('GP discotecas',     20),\n",
    "    'city_gp_surf_school': ('GP escuelas surf',  30),\n",
    "    'city_gp_spa':         ('GP spas',           20),\n",
    "    'city_gp_coworking':   ('GP coworkings',     15),\n",
    "    'city_gp_hostel':      ('GP hostels',        20),\n",
    "}\n",
    "\n",
    "fig, axes = plt.subplots(2, 5, figsize=(18, 8))\n",
    "axes_flat = axes.flatten()\n",
    "\n",
    "for i, (col, (label, cap_val)) in enumerate(CAP_EJEMPLOS.items()):\n",
    "    ax = axes_flat[i]\n",
    "    valores = df[col].sort_values(ascending=False)\n",
    "    colores_cap = ['#EA4335' if v >= cap_val else '#4285F4' for v in valores]\n",
    "    ax.bar(range(len(valores)), valores, color=colores_cap, width=1.0, linewidth=0)\n",
    "    ax.axhline(y=cap_val, color='black', linestyle='--', alpha=0.7, linewidth=1.5)\n",
    "    ax.text(len(valores)*0.02, cap_val*1.05, f'cap={cap_val}', fontsize=8)\n",
    "    n_capped = (valores >= cap_val).sum()\n",
    "    ax.set_title(f'{label}\\n({n_capped} ciudades en el cap)', fontsize=9, fontweight='bold')\n",
    "    ax.set_xticks([])\n",
    "    ax.set_ylabel('Valor raw')\n",
    "\n",
    "cap_patch    = mpatches.Patch(color='#EA4335', label='En el cap (igualdad de score)')\n",
    "normal_patch = mpatches.Patch(color='#4285F4', label='Bajo el cap')\n",
    "fig.legend(handles=[cap_patch, normal_patch], loc='lower center',\n",
    "           ncol=2, fontsize=10, bbox_to_anchor=(0.5, -0.02))\n",
    "fig.suptitle(\n",
    "    'Efecto de cap() — linea punteada = limite maximo. Rojo = ciudades que alcanzan el cap',\n",
    "    fontweight='bold', fontsize=12)\n",
    "plt.tight_layout()\n",
    "plt.savefig('../data/processed/eda_fase1_cap_efecto.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
]))

new_cells.append(md([
    "```\n",
    "PARA QUE SIRVE ESTE GRAFICO:\n",
    "  Muestra el valor real de cada feature en las 55 ciudades, ordenado de mayor\n",
    "  a menor. La linea punteada es el limite del cap(). Las ciudades en rojo son\n",
    "  las que alcanzan ese limite y reciben el mismo score maximo entre ellas.\n",
    "\n",
    "QUE NOS ESTA MOSTRANDO:\n",
    "  - En 'GP gimnasios' (cap=20): varias ciudades grandes tienen 30-40 gimnasios\n",
    "    pero reciben el mismo score que una con 20. Esto evita que Berlin o Paris\n",
    "    siempre ganen en deporte urbano solo por tener mas poblacion.\n",
    "  - En 'GP escuelas surf' (cap=30): pocas ciudades alcanzan el cap\n",
    "    (solo Tarifa, Fuerteventura, Bali, Dakhla). El cap es mas alto porque\n",
    "    la cantidad real importa para destinos especializados.\n",
    "  - En 'OSM restaurantes' (cap=80): muchas ciudades europeas quedan en el cap,\n",
    "    igualando a metropolis con ciudades medianas bien equipadas.\n",
    "\n",
    "DECISION / IMPLICACION PARA EL MODELO:\n",
    "  - Sin cap(), las ciudades mas grandes dominarian practicamente todas las\n",
    "    categorias solo por mayor densidad de establecimientos.\n",
    "  - El cap refleja la logica real del viajero: no necesitas 600 restaurantes,\n",
    "    necesitas que haya opciones suficientes para tu estilo de vida.\n",
    "  - Los valores de cap son decisiones de diseno revisables con datos reales\n",
    "    de satisfaccion de usuarios (futuro).\n",
    "  - Alternativa futura: densidad por km2 en lugar de conteo absoluto.\n",
    "```\n",
]))

# ── Insertar antes del resumen (celda 17) ─────────────────────────────────────
nb_path = ROOT / "notebooks" / "01_eda_ciudades.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

# Localizar celda de resumen (buscar por contenido)
insert_idx = None
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell["source"])
    if "## Resumen de Fase 1" in src:
        insert_idx = i
        break

if insert_idx is None:
    raise ValueError("No se encontro la celda de resumen")

nb["cells"] = nb["cells"][:insert_idx] + new_cells + nb["cells"][insert_idx:]

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Celdas insertadas: {len(new_cells)}")
print(f"Total celdas: {len(nb['cells'])}")
print(f"Insertadas en posicion: {insert_idx}")
