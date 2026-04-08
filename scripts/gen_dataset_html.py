"""Genera HTML interactivo del dataset de entrenamiento."""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data/processed/training_dataset.csv")

n_filas = len(df)
n_cols = len(df.columns)
n_ciudades = df['city'].nunique()
n_usuarios = df['query_id'].nunique()
n_features = len([c for c in df.columns if c.startswith('feat_city_')])
n_dims = len([c for c in df.columns if c.startswith('user_imp_')])
label_dist = df['label'].value_counts().sort_index().to_dict()

# Stats por ciudad
city_stats = df.groupby('city').agg(
    filas=('label','count'),
    label_0=('label', lambda x:(x==0).sum()),
    label_1=('label', lambda x:(x==1).sum()),
    label_2=('label', lambda x:(x==2).sum()),
    label_3=('label', lambda x:(x==3).sum()),
    cosine_media=('cosine_sim','mean'),
    cosine_max=('cosine_sim','max'),
).reset_index().sort_values('cosine_media', ascending=False)

feat_cols = [c for c in df.columns if c.startswith('feat_city_')]
city_feats = df.drop_duplicates('city').set_index('city')[feat_cols].copy()
city_feats.columns = [c.replace('feat_city_','') for c in city_feats.columns]

sample = df.head(200).copy()

def cosine_bar(v):
    pct = int(v * 100)
    color = '#28a745' if v >= 0.5 else '#ffc107' if v >= 0.35 else '#dc3545'
    return f'<div style="background:{color};width:{pct}%;height:14px;border-radius:3px;display:inline-block;min-width:2px"></div> {v:.3f}'

def label_bg(v):
    return {0:'#f8d7da', 1:'#fff3cd', 2:'#d1ecf1', 3:'#d4edda'}.get(int(v), 'white')

# Ciudad rows
city_rows = []
for _, row in city_stats.iterrows():
    bar = cosine_bar(row['cosine_media'])
    city_rows.append(
        f'<tr>'
        f'<td><strong>{row["city"]}</strong></td>'
        f'<td style="text-align:center">{int(row["filas"])}</td>'
        f'<td style="background:#f8d7da;text-align:center">{int(row["label_0"])}</td>'
        f'<td style="background:#fff3cd;text-align:center">{int(row["label_1"])}</td>'
        f'<td style="background:#d1ecf1;text-align:center">{int(row["label_2"])}</td>'
        f'<td style="background:#d4edda;text-align:center">{int(row["label_3"])}</td>'
        f'<td>{bar}</td>'
        f'<td style="text-align:center">{row["cosine_max"]:.3f}</td>'
        f'</tr>'
    )
city_rows_html = '\n'.join(city_rows)

# Feature cols para tabla
feat_display = ['alquiler_1br_centro','coste_vida_estimado','quality_of_life',
                'temp_media_anual','dias_sol_anual','beaches','gp_surf_school',
                'gp_kitesurfing','gp_coworking','internet_mbps','restaurants',
                'gyms','gp_museum','gp_spa','hospitals','schengen']
feat_display = [f for f in feat_display if f in city_feats.columns]
feat_header = ''.join([f'<th>{f}</th>' for f in feat_display])

feat_rows = []
for city, row in city_feats.sort_index().iterrows():
    cells = []
    for f in feat_display:
        v = row[f]
        if pd.isna(v):
            cells.append('<td style="color:#ccc">-</td>')
        elif f == 'schengen':
            cells.append(f'<td style="text-align:center">{"&#10003;" if v==1 else "&#10007;"}</td>')
        elif f == 'alquiler_1br_centro':
            cells.append(f'<td style="text-align:right">&#8364;{v:,.0f}</td>')
        else:
            cells.append(f'<td style="text-align:right">{v:.0f}</td>')
    feat_rows.append(f'<tr><td><strong>{city}</strong></td>{"".join(cells)}</tr>')
feat_rows_html = '\n'.join(feat_rows)

# Sample rows
dim_keys = ['user_imp_gastronomia','user_imp_deporte_agua','user_imp_nomada','user_imp_coste','user_imp_clima']
sample_rows = []
for _, row in sample.iterrows():
    lbg = label_bg(row['label'])
    dims = ' '.join([
        f'<span style="font-size:10px;background:#e9ecef;padding:1px 4px;border-radius:3px">'
        f'{k.replace("user_imp_","")}={row[k]:.2f}</span>'
        for k in dim_keys
    ])
    sample_rows.append(
        f'<tr>'
        f'<td style="text-align:center;color:#666">{int(row["query_id"])}</td>'
        f'<td><strong>{row["city"]}</strong></td>'
        f'<td style="background:{lbg};text-align:center;font-weight:bold">{int(row["label"])}</td>'
        f'<td>{cosine_bar(row["cosine_sim"])}</td>'
        f'<td style="font-size:11px">{dims}</td>'
        f'</tr>'
    )
sample_rows_html = '\n'.join(sample_rows)

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>NomadOptima - Dataset de Entrenamiento</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f4f6f9; color: #2d3748; }
  .hero { background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); color: white; padding: 48px 40px; }
  .hero h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 8px; }
  .hero p { opacity: 0.8; font-size: 1rem; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; padding: 32px 40px; }
  .stat-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }
  .stat-card .num { font-size: 2rem; font-weight: 800; color: #4299e1; line-height: 1; }
  .stat-card .label { font-size: 0.78rem; color: #718096; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
  .section { padding: 0 40px 40px; }
  .section h2 { font-size: 1.3rem; font-weight: 700; margin-bottom: 16px; padding-top: 32px; border-top: 2px solid #e2e8f0; color: #2d3748; }
  .tab-bar { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
  .tab { padding: 8px 18px; border-radius: 20px; border: none; cursor: pointer; font-size: 0.85rem; font-weight: 600; transition: all 0.2s; background: #e2e8f0; color: #4a5568; }
  .tab.active { background: #4299e1; color: white; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); font-size: 0.875rem; }
  th { background: #2d3748; color: white; padding: 10px 12px; text-align: left; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; }
  td { padding: 8px 12px; border-bottom: 1px solid #edf2f7; vertical-align: middle; }
  tr:hover td { background: #f7fafc; }
  tr:last-child td { border-bottom: none; }
  .legend { display: flex; gap: 16px; margin-bottom: 16px; font-size: 0.82rem; flex-wrap: wrap; }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-dot { width: 14px; height: 14px; border-radius: 3px; }
  .overflow-x { overflow-x: auto; }
  .info-box { background: #ebf8ff; border-left: 4px solid #4299e1; padding: 16px 20px; border-radius: 0 8px 8px 0; margin-bottom: 24px; font-size: 0.9rem; line-height: 1.6; }
</style>
</head>
<body>
''')

html_parts.append(f'''<div class="hero">
  <h1>NomadOptima &mdash; Dataset de Entrenamiento</h1>
  <p>Generado: 08/04/2026 &nbsp;&middot;&nbsp; 5,000 perfiles sint&eacute;ticos &times; 42 ciudades &nbsp;&middot;&nbsp; Learning to Rank (LambdaMART)</p>
</div>

<div class="stats-grid">
  <div class="stat-card"><div class="num">{n_filas:,}</div><div class="label">Filas totales</div></div>
  <div class="stat-card"><div class="num">{n_cols}</div><div class="label">Columnas</div></div>
  <div class="stat-card"><div class="num">{n_ciudades}</div><div class="label">Ciudades</div></div>
  <div class="stat-card"><div class="num">{n_usuarios:,}</div><div class="label">Usuarios sint&eacute;ticos</div></div>
  <div class="stat-card"><div class="num">{n_features}</div><div class="label">Features ciudad</div></div>
  <div class="stat-card"><div class="num">{n_dims}</div><div class="label">Dimensiones usuario</div></div>
  <div class="stat-card"><div class="num">{label_dist.get(0,0):,}</div><div class="label">Label 0 Irrelevante</div></div>
  <div class="stat-card"><div class="num">{label_dist.get(1,0):,}</div><div class="label">Label 1 Poco</div></div>
  <div class="stat-card"><div class="num">{label_dist.get(2,0):,}</div><div class="label">Label 2 Relevante</div></div>
  <div class="stat-card"><div class="num">{label_dist.get(3,0):,}</div><div class="label">Label 3 Muy relevante</div></div>
</div>
''')

html_parts.append(f'''<div class="section">
  <div class="tab-bar">
    <button class="tab active" onclick="showTab('tab-resumen',this)">Resumen por ciudad</button>
    <button class="tab" onclick="showTab('tab-features',this)">Features de ciudad</button>
    <button class="tab" onclick="showTab('tab-muestra',this)">Muestra del dataset</button>
    <button class="tab" onclick="showTab('tab-info',this)">Glosario de columnas</button>
  </div>

  <div id="tab-resumen" class="tab-content active">
    <h2>Ranking de ciudades por similitud coseno media</h2>
    <div class="info-box">
      La <strong>similitud coseno media</strong> indica qu&eacute; tan bien encaja cada ciudad con los 5,000 perfiles de usuario en promedio.
      No significa que la ciudad sea "mejor" &mdash; significa que es m&aacute;s vers&aacute;til. El label 3 indica cu&aacute;ntos usuarios la valoraron como "muy relevante".
    </div>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:#f8d7da"></div> Label 0 &mdash; Irrelevante</div>
      <div class="legend-item"><div class="legend-dot" style="background:#fff3cd"></div> Label 1 &mdash; Poco relevante</div>
      <div class="legend-item"><div class="legend-dot" style="background:#d1ecf1"></div> Label 2 &mdash; Relevante</div>
      <div class="legend-item"><div class="legend-dot" style="background:#d4edda"></div> Label 3 &mdash; Muy relevante</div>
    </div>
    <div class="overflow-x">
    <table>
      <thead><tr>
        <th>Ciudad</th><th>Filas</th>
        <th>Label 0</th><th>Label 1</th><th>Label 2</th><th>Label 3</th>
        <th>Cosine Sim Media</th><th>Cosine Sim M&aacute;x</th>
      </tr></thead>
      <tbody>{city_rows_html}</tbody>
    </table>
    </div>
  </div>

  <div id="tab-features" class="tab-content">
    <h2>Features clave por ciudad (136 features num&eacute;ricas en total)</h2>
    <div class="info-box">
      Se muestran 16 columnas clave. El CSV completo tiene <strong>136 features num&eacute;ricas</strong> + idioma nativo.
      Todas las features est&aacute;n normalizadas [0,1] con MinMaxScaler y capping aplicado.
    </div>
    <div class="overflow-x">
    <table>
      <thead><tr><th>Ciudad</th>{feat_header}</tr></thead>
      <tbody>{feat_rows_html}</tbody>
    </table>
    </div>
  </div>

  <div id="tab-muestra" class="tab-content">
    <h2>Primeras 200 filas del dataset de entrenamiento</h2>
    <div class="info-box">
      Cada fila es un par <strong>(usuario, ciudad)</strong>. El label indica qu&eacute; tan bien encaja esa ciudad con las preferencias del usuario.
      La similitud coseno ya est&aacute; calculada &mdash; es la feature m&aacute;s importante para el modelo.
    </div>
    <div class="overflow-x">
    <table>
      <thead><tr>
        <th>Usuario (query_id)</th><th>Ciudad</th><th>Label</th>
        <th>Cosine Sim</th><th>Muestra de preferencias</th>
      </tr></thead>
      <tbody>{sample_rows_html}</tbody>
    </table>
    </div>
  </div>

  <div id="tab-info" class="tab-content">
    <h2>Glosario de columnas (166 en total)</h2>
    <div class="info-box">
      El dataset combina el perfil del usuario con las caracter&iacute;sticas de la ciudad. Cada par genera una fila con su label de relevancia.
    </div>
    <table>
      <thead><tr><th>Grupo</th><th>Prefijo</th><th>N&deg; cols</th><th>Qu&eacute; contiene</th></tr></thead>
      <tbody>
        <tr><td><strong>Metadata</strong></td><td>query_id, city, label</td><td>3</td>
            <td>ID del usuario sint&eacute;tico, nombre de ciudad, relevancia 0-3</td></tr>
        <tr><td><strong>Similitud coseno</strong></td><td>cosine_sim</td><td>1</td>
            <td>Feature calculada: &aacute;ngulo entre el vector de preferencias del usuario y el vector de features de la ciudad</td></tr>
        <tr><td><strong>Preferencias usuario</strong></td><td>user_imp_*</td><td>26</td>
            <td>Pesos de importancia: gastronom&iacute;a, kite/surf, nómada digital, coste, clima... (valores 0-1, distribuci&oacute;n beta bimodal U-shaped)</td></tr>
        <tr><td><strong>Features ciudad</strong></td><td>feat_city_*</td><td>136</td>
            <td>Caracter&iacute;sticas de la ciudad: alquiler, restaurantes, coworking, playas, gimnasios, museos... (normalizadas 0-1)</td></tr>
      </tbody>
    </table>
    <br>
    <table>
      <thead><tr><th>Label</th><th>Criterio de asignaci&oacute;n</th><th>Filas</th><th>% del total</th></tr></thead>
      <tbody>
        <tr style="background:#f8d7da"><td><strong>0 &mdash; Irrelevante</strong></td>
            <td>Posici&oacute;n > 60% del ranking de cada usuario</td>
            <td>{label_dist.get(0,0):,}</td><td>{label_dist.get(0,0)/n_filas*100:.1f}%</td></tr>
        <tr style="background:#fff3cd"><td><strong>1 &mdash; Poco relevante</strong></td>
            <td>Posici&oacute;n 31-60% del ranking</td>
            <td>{label_dist.get(1,0):,}</td><td>{label_dist.get(1,0)/n_filas*100:.1f}%</td></tr>
        <tr style="background:#d1ecf1"><td><strong>2 &mdash; Relevante</strong></td>
            <td>Posici&oacute;n 11-30% del ranking</td>
            <td>{label_dist.get(2,0):,}</td><td>{label_dist.get(2,0)/n_filas*100:.1f}%</td></tr>
        <tr style="background:#d4edda"><td><strong>3 &mdash; Muy relevante</strong></td>
            <td>Top 10% del ranking de cada usuario</td>
            <td>{label_dist.get(3,0):,}</td><td>{label_dist.get(3,0)/n_filas*100:.1f}%</td></tr>
      </tbody>
    </table>
  </div>

</div>

''' + '''<script>
function showTab(id, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}
</script>
</body>
</html>''')

out = ROOT / "data/processed/training_dataset_overview.html"
with open(out, 'w', encoding='utf-8') as f:
    f.write(''.join(html_parts))

print(f"HTML generado: {out}")
print(f"Tamano: {out.stat().st_size / 1024:.1f} KB")
