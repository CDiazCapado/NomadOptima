"""
NomadOptima — Generador de HTML EDA interactivo para la matriz de ciudades
scripts/generate_eda_html.py

Genera data/processed/city_features_eda.html con:
- Tabla interactiva de 38 ciudades × 131 features
- Tabs por categoría
- Valores con escala de color (heat map por columna)
- Ordenación por columna al hacer clic
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "processed" / "city_features.csv"
OUT_PATH = ROOT / "data" / "processed" / "city_features_eda.html"

# ── Definición de tabs: (nombre_tab, emoji, [columnas]) ──────────────────────
TABS = [
    ("Todas", "🌍", None),  # None = todas las columnas
    ("Coste de vida", "💶", [
        "city_coste_vida_estimado", "city_alquiler_1br_centro",
        "city_transport_monthly", "city_meal_cheap",
    ]),
    ("Clima", "☀️", [
        "city_temp_media_anual", "city_dias_sol_anual",
        "city_temp_actual_c", "city_temp_media_norm", "city_dias_sol_norm",
    ]),
    ("Gastronomía", "🍽️", [
        "city_restaurants", "city_cafes", "city_gp_fine_dining",
        "city_gp_vegan", "city_gp_vegetarian", "city_gp_tapas",
        "city_gp_seafood", "city_gp_coffee_shop", "city_gp_bakery",
        "city_gp_wine_bar", "city_gp_market",
    ]),
    ("Vida Nocturna", "🌙", [
        "city_gp_night_club", "city_gp_bar", "city_gp_pub",
        "city_gp_cocktail_bar", "city_gp_karaoke",
    ]),
    ("Cultura", "🏛️", [
        "city_gp_museum", "city_gp_historical_landmark",
        "city_gp_monument", "city_gp_cultural_center",
        "city_gp_performing_arts",
    ]),
    ("Arte Visual", "🎨", [
        "city_gp_art_gallery", "city_gp_art_studio", "city_gp_sculpture",
    ]),
    ("Música", "🎵", [
        "city_gp_concert_hall", "city_gp_live_music", "city_gp_jazz_club",
        "city_gp_folk_music", "city_gp_opera",
    ]),
    ("Naturaleza", "🌿", [
        "city_beaches", "city_parks", "city_gp_beach",
        "city_gp_park", "city_gp_national_park",
        "city_gp_nature_reserve", "city_gp_hiking_area",
    ]),
    ("Deporte", "⚽", [
        "city_gyms", "city_gp_gym", "city_gp_fitness_center",
        "city_gp_surf_school", "city_gp_kitesurfing", "city_gp_windsurfing",
        "city_gp_wingfoil", "city_gp_ski_resort", "city_gp_snowpark",
        "city_gp_ski_touring", "city_gp_climbing_gym", "city_gp_tennis_court",
        "city_gp_cycling_park", "city_gp_adventure_sports",
        "city_gp_swimming_pool", "city_gp_marina", "city_gp_kayak",
        "city_gp_snorkeling", "city_gp_sports_complex",
    ]),
    ("Bienestar", "🧘", [
        "city_gp_spa", "city_gp_wellness", "city_gp_yoga_studio",
        "city_gp_sauna", "city_gp_massage", "city_gp_thermal_bath",
    ]),
    ("Social Media", "📸", [
        "city_gp_rooftop_bar", "city_gp_beach_club", "city_gp_street_art",
        "city_gp_photo_spot", "city_gp_observation_deck",
    ]),
    ("Familia", "👨‍👩‍👧", [
        "city_playgrounds", "city_schools", "city_kindergartens",
        "city_childcare", "city_gp_preschool", "city_gp_international_school",
        "city_gp_amusement_park", "city_gp_zoo", "city_gp_aquarium",
    ]),
    ("Mascotas", "🐾", [
        "city_dog_areas", "city_gp_dog_park",
        "city_gp_vet", "city_gp_pet_store",
    ]),
    ("Nómada Digital", "💻", [
        "city_coworking_osm", "city_gp_coworking", "city_gp_coliving",
        "city_gp_tech_hub", "city_internet_mbps",
        "city_gp_internet_cafe", "city_gp_library",
    ]),
    ("Alojamiento", "🏨", [
        "city_gp_hostel", "city_gp_extended_stay", "city_gp_bed_breakfast",
    ]),
    ("Movilidad", "🚇", [
        "city_public_transport", "city_bicycle_lanes",
        "city_gp_subway", "city_gp_train_station",
        "city_gp_bus_station", "city_gp_bicycle_rental",
    ]),
    ("Compras", "🛒", [
        "city_gp_supermarket", "city_gp_grocery",
        "city_gp_shopping_mall", "city_gp_convenience",
    ]),
    ("Servicios", "✂️", [
        "city_gp_barber", "city_gp_beauty_salon",
        "city_gp_laundry", "city_pharmacies",
    ]),
    ("Salud", "🏥", [
        "city_hospitals", "city_gp_dental",
        "city_gp_physiotherapist", "city_gp_mental_health",
    ]),
    ("Turismo", "📍", [
        "city_gp_tourist_attraction", "city_gp_scenic_point",
        "city_gp_tour_operator",
    ]),
    ("Educación", "📚", [
        "city_gp_university", "city_gp_language_school",
    ]),
    ("Comunidad", "⛪", [
        "city_gp_community_center", "city_gp_church",
        "city_gp_mosque", "city_gp_synagogue",
    ]),
    ("País / Idioma", "🏳️", [
        "city_idioma_nativo",
        "city_schengen", "city_moneda_eur",
        "city_idioma_espanol", "city_idioma_ingles",
        "city_idioma_frances", "city_idioma_aleman", "city_idioma_portugues",
        "city_quality_of_life",
    ]),
]

# Colores para el heatmap (de verde claro a verde oscuro)
HEAT_COLORS = [
    "#ffffff", "#e8f5e9", "#c8e6c9", "#a5d6a7",
    "#81c784", "#66bb6a", "#4caf50", "#43a047",
    "#388e3c", "#2e7d32",
]

# Para columnas de coste: invertido (más bajo = mejor = más verde)
COST_COLS = {"city_coste_vida_estimado", "city_alquiler_1br_centro",
             "city_transport_monthly", "city_meal_cheap"}

# Columnas booleanas (0/1)
BOOL_COLS = {"city_schengen", "city_moneda_eur",
             "city_idioma_espanol", "city_idioma_ingles"}


def heat_color(val, col_min, col_max, invert=False):
    """Devuelve un color de fondo proporcional al valor."""
    if col_max == col_min:
        return "#f5f5f5"
    ratio = (val - col_min) / (col_max - col_min)
    if invert:
        ratio = 1 - ratio
    idx = min(int(ratio * (len(HEAT_COLORS) - 1)), len(HEAT_COLORS) - 1)
    return HEAT_COLORS[idx]


def fmt_val(val, col):
    """Formatea un valor para mostrar en la tabla."""
    if pd.isna(val):
        return "—"
    if col in BOOL_COLS:
        return "Sí" if val == 1 else "No"
    if col in {"city_coste_vida_estimado", "city_alquiler_1br_centro",
               "city_transport_monthly", "city_meal_cheap"}:
        return f"{val:,.0f}€"
    if col == "city_internet_mbps":
        return f"{val:.0f} Mb"
    if col in {"city_temp_media_anual", "city_temp_actual_c"}:
        return f"{val:.1f}°C"
    if col in {"city_temp_media_norm", "city_dias_sol_norm",
               "city_coste_invertido"}:
        return f"{val:.2f}"
    if col == "city_dias_sol_anual":
        return f"{val:.0f}d"
    if col == "city_quality_of_life":
        return f"{val:.1f}"
    # Columnas de texto (ej: city_idioma_nativo)
    if isinstance(val, str):
        return val
    return f"{val:.0f}"


def build_table(df, cols):
    """Genera el HTML de una tabla con heatmap."""
    display_cols = [c for c in cols if c in df.columns]

    # Columnas de texto — mostrar pero sin heatmap
    TEXT_COLS = {"city_idioma_nativo"}

    # Calcular min/max por columna para el heatmap
    stats = {}
    for col in display_cols:
        if col in BOOL_COLS or col in TEXT_COLS:
            continue
        if df[col].dtype == object:
            continue
        stats[col] = (df[col].min(), df[col].max())

    # Cabecera — nombres limpios
    def clean_name(c):
        return c.replace("city_gp_", "").replace("city_", "").replace("_", " ").title()

    rows_html = []
    for _, row in df.iterrows():
        cells = [f'<td class="city-name">{row["city"]}</td>']
        for col in display_cols:
            val = row[col]
            raw = fmt_val(val, col)
            if col in TEXT_COLS or (isinstance(val, str) and col not in BOOL_COLS):
                # Texto plano: fondo neutro, texto oscuro
                cells.append(f'<td style="background:#f8fafc;color:#1e3a5f;font-weight:600;text-align:left;padding-left:8px">{raw}</td>')
            elif col in BOOL_COLS:
                bg = "#c8e6c9" if val == 1 else "#ffebee"
                color = "#2e7d32" if val == 1 else "#c62828"
                cells.append(f'<td style="background:{bg};color:{color};font-weight:600">{raw}</td>')
            elif pd.isna(val):
                cells.append(f'<td style="background:#f5f5f5;color:#9e9e9e">—</td>')
            else:
                mn, mx = stats[col]
                inv = col in COST_COLS
                bg = heat_color(val, mn, mx, invert=inv)
                cells.append(f'<td style="background:{bg}" data-val="{val:.4f}">{raw}</td>')
        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    header_cells = ['<th onclick="sortTable(this)">Ciudad ↕</th>']
    for col in display_cols:
        header_cells.append(f'<th onclick="sortTable(this)" title="{col}">{clean_name(col)} ↕</th>')

    return f"""
<table class="data-table" id="table-{'_'.join(display_cols[:2])}">
  <thead><tr>{"".join(header_cells)}</tr></thead>
  <tbody>{"".join(rows_html)}</tbody>
</table>
"""


def generate_html(df):
    all_cols = [c for c in df.columns if c != "city"]
    n_cities = len(df)
    n_features = len(all_cols)

    # Construir contenido de cada tab
    tab_buttons = []
    tab_contents = []

    for i, (name, emoji, cols) in enumerate(TABS):
        active_btn = "active" if i == 0 else ""
        active_div = "active" if i == 0 else ""
        tab_id = f"tab{i}"
        tab_buttons.append(
            f'<button class="tab-btn {active_btn}" onclick="showTab(\'{tab_id}\')">'
            f'{emoji} {name}</button>'
        )
        use_cols = all_cols if cols is None else cols
        table_html = build_table(df, use_cols)
        ncols = len([c for c in (use_cols if cols else all_cols) if c in df.columns])
        tab_contents.append(f"""
<div id="{tab_id}" class="tab-content {active_div}">
  <p class="tab-info">{n_cities} ciudades · {ncols} features en esta categoría</p>
  <div class="table-wrap">{table_html}</div>
</div>
""")

    # Estadísticas globales
    zero_counts = (df[all_cols] == 0).sum()
    top_zeros = zero_counts.sort_values(ascending=False).head(10)
    zero_rows = "".join(
        f'<tr><td>{c.replace("city_gp_","").replace("city_","").replace("_"," ").title()}</td>'
        f'<td>{v} / {n_cities} ciudades</td></tr>'
        for c, v in top_zeros.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NomadOptima — Matriz de Ciudades EDA</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }}

    header {{
      background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
      color: white; padding: 24px 32px;
    }}
    header h1 {{ font-size: 1.8rem; font-weight: 700; }}
    header p {{ margin-top: 6px; opacity: 0.85; font-size: 0.95rem; }}

    .summary-bar {{
      background: white; padding: 16px 32px;
      display: flex; gap: 32px; border-bottom: 2px solid #e2e8f0;
      flex-wrap: wrap;
    }}
    .stat-box {{ text-align: center; }}
    .stat-box .num {{ font-size: 2rem; font-weight: 700; color: #1e3a5f; }}
    .stat-box .lbl {{ font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }}

    .tabs-container {{ background: white; padding: 0 32px; border-bottom: 3px solid #e2e8f0; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
    .tabs-scroll {{ display: flex; gap: 4px; overflow-x: auto; padding: 8px 0 0; scrollbar-width: thin; }}
    .tab-btn {{
      background: none; border: none; padding: 10px 16px; cursor: pointer;
      font-size: 0.82rem; font-weight: 500; color: #64748b;
      border-bottom: 3px solid transparent; white-space: nowrap;
      transition: all 0.2s; border-radius: 6px 6px 0 0;
    }}
    .tab-btn:hover {{ background: #f1f5f9; color: #1e3a5f; }}
    .tab-btn.active {{ color: #1e3a5f; border-bottom-color: #2d6a9f; background: #eff6ff; font-weight: 700; }}

    .tab-content {{ display: none; padding: 20px 32px 40px; }}
    .tab-content.active {{ display: block; }}
    .tab-info {{ font-size: 0.82rem; color: #64748b; margin-bottom: 12px; }}

    .table-wrap {{ overflow-x: auto; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
    .data-table {{ border-collapse: collapse; min-width: 100%; font-size: 0.8rem; }}
    .data-table thead tr {{ background: #1e3a5f; color: white; }}
    .data-table th {{
      padding: 10px 12px; text-align: center; cursor: pointer;
      white-space: nowrap; font-weight: 600; font-size: 0.75rem;
      user-select: none;
    }}
    .data-table th:hover {{ background: #2d6a9f; }}
    .data-table td {{
      padding: 7px 10px; text-align: center; border: 1px solid #e2e8f0;
      white-space: nowrap; font-size: 0.78rem;
    }}
    .data-table td.city-name {{
      text-align: left; font-weight: 600; background: #f8fafc !important;
      color: #1e3a5f; min-width: 110px; position: sticky; left: 0;
      border-right: 2px solid #cbd5e1;
    }}
    .data-table tbody tr:hover td {{ filter: brightness(0.93); }}
    .data-table tbody tr:nth-child(even) td.city-name {{ background: #f1f5f9 !important; }}

    .legend {{ display: flex; align-items: center; gap: 6px; margin: 12px 0; font-size: 0.78rem; color: #64748b; }}
    .legend-bar {{ display: flex; gap: 2px; }}
    .legend-bar span {{ width: 18px; height: 14px; display: inline-block; border-radius: 2px; }}

    .bottom-section {{ background: white; margin: 24px 32px; border-radius: 12px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    .bottom-section h2 {{ font-size: 1.1rem; color: #1e3a5f; margin-bottom: 16px; }}
    .zero-table {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; }}
    .zero-table th {{ background: #f1f5f9; padding: 8px 12px; text-align: left; color: #475569; }}
    .zero-table td {{ padding: 7px 12px; border-bottom: 1px solid #e2e8f0; }}
    .zero-table tr:hover td {{ background: #f8fafc; }}

    footer {{ text-align: center; padding: 20px; font-size: 0.75rem; color: #94a3b8; }}
  </style>
</head>
<body>

<header>
  <h1>NomadOptima — Matriz de Ciudades</h1>
  <p>Datos reales de {n_cities} ciudades × {n_features} features · Fuentes: Google Places, OSM, Numbeo, Speedtest, wttr.in, RestCountries</p>
</header>

<div class="summary-bar">
  <div class="stat-box"><div class="num">{n_cities}</div><div class="lbl">Ciudades</div></div>
  <div class="stat-box"><div class="num">{n_features}</div><div class="lbl">Features totales</div></div>
  <div class="stat-box"><div class="num">{n_cities * n_features:,}</div><div class="lbl">Datos totales</div></div>
  <div class="stat-box"><div class="num">24</div><div class="lbl">Categorías</div></div>
  <div class="stat-box"><div class="num">6</div><div class="lbl">Fuentes de datos</div></div>
</div>

<div class="tabs-container">
  <div class="tabs-scroll">
    {"".join(tab_buttons)}
  </div>
</div>

{"".join(tab_contents)}

<div class="bottom-section">
  <h2>Features con más ceros (posibles huecos en los datos)</h2>
  <p style="font-size:0.82rem;color:#64748b;margin-bottom:12px;">
    Un valor 0 puede significar que la ciudad realmente no tiene ese tipo de lugar, o que la API no encontró resultados.
    Features con muchos ceros son poco discriminativas para el modelo.
  </p>
  <table class="zero-table">
    <thead><tr><th>Feature</th><th>Ciudades con valor 0</th></tr></thead>
    <tbody>{zero_rows}</tbody>
  </table>
</div>

<div class="legend" style="padding: 0 32px 16px;">
  <span>Escala de color:</span>
  <div class="legend-bar">
    {"".join(f'<span style="background:{c}"></span>' for c in HEAT_COLORS)}
  </div>
  <span>Bajo</span>→<span>Alto</span>
  &nbsp;&nbsp;
  <span style="background:#c8e6c9;padding:2px 8px;border-radius:4px;font-size:0.75rem;color:#2e7d32">Sí</span>
  <span style="background:#ffebee;padding:2px 8px;border-radius:4px;font-size:0.75rem;color:#c62828">No</span>
  (para columnas booleanas)
  &nbsp;&nbsp;
  <em>Nota: en Coste de vida, verde = más barato</em>
</div>

<footer>NomadOptima · Generado automáticamente · {n_cities} ciudades descargadas</footer>

<script>
function showTab(id) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}

function sortTable(th) {{
  const table = th.closest('table');
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const idx = Array.from(th.parentNode.children).indexOf(th);
  const asc = th.dataset.asc !== 'true';
  th.dataset.asc = asc;

  rows.sort((a, b) => {{
    const aCell = a.children[idx];
    const bCell = b.children[idx];
    const aVal = aCell.dataset.val !== undefined ? parseFloat(aCell.dataset.val) : aCell.textContent.trim();
    const bVal = bCell.dataset.val !== undefined ? parseFloat(bCell.dataset.val) : bCell.textContent.trim();
    if (typeof aVal === 'number' && typeof bVal === 'number') {{
      return asc ? aVal - bVal : bVal - aVal;
    }}
    return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
  }});

  rows.forEach(r => tbody.appendChild(r));
}}
</script>
</body>
</html>"""
    return html


def main():
    print("Cargando city_features.csv...")
    df = pd.read_csv(CSV_PATH)
    print(f"  {len(df)} ciudades x {len(df.columns)-1} features")

    print("Generando HTML...")
    html = generate_html(df)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Guardado: {OUT_PATH}")
    print(f"Tamano: {size_kb:.1f} KB")
    print(f"Abre en tu navegador: {OUT_PATH}")


if __name__ == "__main__":
    main()
