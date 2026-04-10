"""
Corrige notebook 02: elimina cruce con ciudades, guarda solo user_profiles.csv.
Celdas que se reemplazan: 85b65581, 79de0bcf, 6519b64e, cf678741, 7b11d6d7, b07c03ca
Celdas que se eliminan (markdown obsoletos): 16 (f7ba90e9), 19 (159e7e8e), 21 (45166cbc)
"""
import json
from pathlib import Path

NB = Path("notebooks/02_synthetic_profiles_v3.ipynb")

REPLACEMENTS = {
    # Paso 1: ya no cargamos ciudades — solo necesitamos USER_IMPORTANCE_KEYS
    "85b65581": '''\
# Paso 1: Confirmar dimensiones de usuario disponibles
# (Las ciudades se cargan en notebook 03 — aqui solo generamos perfiles)
print(f"Dimensiones de usuario: {len(USER_IMPORTANCE_KEYS)}")
print(f"Dimensiones: {USER_IMPORTANCE_KEYS}")
''',
    # Paso 5: eliminamos cosine_sim y labels — solo generamos df_users
    "79de0bcf": '''\
# Paso 5: Verificar perfiles generados
print(f"Perfiles generados: {len(df_users)}")
print(f"Columnas: {list(df_users.columns)}")
print(f"\\nDistribucion por arquetipo:")
print(df_users["archetype"].value_counts().to_string())
''',
    # Paso 6: ya no unimos con ciudad
    "6519b64e": '''\
# Paso 6: Resumen estadistico de los perfiles
user_cols = [c for c in df_users.columns if c.startswith("user_imp_")]
print("\\nEstadisticas de las 26 dimensiones:")
print(df_users[user_cols].describe().round(3).to_string())
''',
    # Paso 7: validacion simplificada sin ciudad
    "cf678741": '''\
# Paso 7: Validacion spot-check — medias por arquetipo
means = df_users.groupby("archetype")[user_cols].mean()
print("\\nTop dimensiones por arquetipo (media > 0.60):")
for arch in means.index:
    top = means.loc[arch][means.loc[arch] > 0.60]
    if len(top):
        dims = ", ".join(f"{d.replace('user_imp_','')}={v:.2f}" for d,v in top.items())
        print(f"  {arch:<25} {dims}")
''',
    # Grafico 1: distribucion arquetipos — cambiar df_full por df_users
    "28684fd1": '''\
# Grafico 1: distribucion de usuarios por arquetipo
arch_counts = df_users["archetype"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

colors = plt.cm.tab20(np.linspace(0, 1, len(arch_counts)))
arch_counts.plot(kind="barh", ax=axes[0], color=colors)
axes[0].set_title("Perfiles por arquetipo", fontsize=12, fontweight="bold")
axes[0].set_xlabel("Numero de perfiles")

axes[1].pie(arch_counts.values, labels=arch_counts.index, autopct="%1.1f%%",
            colors=colors, startangle=90, textprops={"fontsize": 7})
axes[1].set_title("Distribucion porcentual", fontsize=12, fontweight="bold")

plt.suptitle(f"5.000 perfiles sinteticos — {len(arch_counts)} arquetipos", fontweight="bold")
plt.tight_layout()
out = ROOT / "data/processed/nb02_distribucion_arquetipos.png"
plt.savefig(out, dpi=120, bbox_inches="tight")
plt.show()
print(f"Guardado: {out.name}")
''',
    # Grafico 2: sin ciudad no hay heatmap — reemplazar con histogramas
    "7b11d6d7": '''\
import warnings
warnings.filterwarnings("ignore")

# Grafico 2: distribucion de las 26 dimensiones en todos los perfiles
fig, axes = plt.subplots(4, 7, figsize=(20, 12))
axes = axes.flatten()
for i, col in enumerate(user_cols):
    dim = col.replace("user_imp_", "")
    axes[i].hist(df_users[col], bins=25, color="steelblue", alpha=0.7, edgecolor="white")
    axes[i].axvline(df_users[col].mean(), color="red", linestyle="--", alpha=0.7, linewidth=1)
    axes[i].set_title(dim, fontsize=8, fontweight="bold")
    axes[i].set_xlabel("", fontsize=6)
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)
plt.suptitle("Distribucion de las 26 dimensiones en 5.000 perfiles sinteticos",
             fontsize=13, fontweight="bold")
plt.tight_layout()
out = ROOT / "data/processed/nb02_histogramas_perfiles.png"
plt.savefig(out, dpi=120, bbox_inches="tight")
plt.show()
print(f"Guardado: {out.name}")
''',
    # Paso 9: guardar user_profiles.csv en lugar de training_dataset.csv
    "b07c03ca": '''\
# Paso 9: Guardar user_profiles.csv (SIN ciudades — notebook 03 hace el cruce)
out_path = ROOT / "data/processed/user_profiles.csv"
df_users.to_csv(out_path, index=False)

size_kb = out_path.stat().st_size / 1024
print(f"Guardado: {out_path.name}")
print(f"Shape:    {df_users.shape}")
print(f"Tamano:   {size_kb:.1f} KB")
print()
print("SIGUIENTE PASO: notebook 03 cargara user_profiles.csv + city_features.csv")
print("y generara el training_dataset.csv con la arquitectura correcta.")
''',
}

# Markdown cells to neutralize (content no longer valid)
MARKDOWN_UPDATES = {
    "f7ba90e9": "## Paso 5: Verificar perfiles generados\n",
    "159e7e8e": "## Paso 6: Resumen estadístico de los perfiles\n",
    "45166cbc": "## Paso 7: Validación — spot-check por arquetipo\n",
}

nb = json.load(open(NB, encoding="utf-8"))

updated = 0
for cell in nb["cells"]:
    cid = cell.get("id", "")
    if cid in REPLACEMENTS:
        lines = REPLACEMENTS[cid].splitlines(keepends=True)
        cell["source"] = lines
        cell["outputs"] = []
        cell["execution_count"] = None
        updated += 1
    elif cid in MARKDOWN_UPDATES:
        cell["source"] = [MARKDOWN_UPDATES[cid]]
        updated += 1

json.dump(nb, open(NB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OK notebook 02 corregido — {updated} celdas actualizadas")
print(f"   Guarda user_profiles.csv, no training_dataset.csv")
