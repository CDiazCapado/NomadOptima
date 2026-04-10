"""
Genera notebooks/03_train_model.ipynb
Arquitectura correcta:
  - Labels: producto escalar directo user_imp × city_features (sin cosine_sim)
  - Features LightGBM: [user_imp_*(26) + city_features_*(148) + cosine_sim(1)] = 175
  - LightGBM LambdaRank
  - Analisis completo + MLflow
"""
import json, random, string
from pathlib import Path

OUT = Path("notebooks/03_train_model.ipynb")

def cell(source, ctype="code", cid=None):
    if cid is None:
        cid = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    if ctype == "markdown":
        return {"cell_type": "markdown", "id": cid, "metadata": {}, "source": source}
    return {"cell_type": "code", "execution_count": None, "id": cid,
            "metadata": {}, "outputs": [], "source": source}

cells = []

# TITULO
cells.append(cell("""# Notebook 03 — Entrenamiento LightGBM LambdaRank
## NomadOptima — arquitectura correcta (10/04/2026)

**Flujo:**
1. Cargar user_profiles.csv (5.000 perfiles) + city_features.csv (54 ciudades)
2. Cruzar → 270.000 pares (usuario, ciudad)
3. Calcular labels por **producto escalar directo** (no cosine_sim — evita circularidad)
4. Features para LightGBM: [user_imp_*(26) + city_features_*(148) + cosine_sim(1)] = 175
5. Entrenar LightGBM LambdaRank con validacion
6. Analisis: curvas, feature importance, SHAP, validacion cualitativa
7. Guardar artefactos del modelo
""", "markdown", "titulo_nb03"))

# PASO 0: IMPORTS
cells.append(cell("""## Paso 0: Imports""", "markdown", "md_paso0"))
cells.append(cell("""\
import sys, os, warnings
sys.path.insert(0, os.path.abspath(".."))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import lightgbm as lgb
import shap
import mlflow
import mlflow.lightgbm
from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import MinMaxScaler

from src.processing.features import CityFeatureBuilder, DIMENSION_MAP

ROOT      = Path("..").resolve()
DATA_DIR  = ROOT / "data" / "processed"
MODEL_DIR = DATA_DIR / "model_v3"
MODEL_DIR.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
np.random.seed(42)

print(f"ROOT: {ROOT}")
print(f"LightGBM: {lgb.__version__}")
print(f"SHAP: {shap.__version__}")
print(f"MLflow: {mlflow.__version__}")
""", "paso0_imports"))

cells.append(cell("""\
**ANOTACIONES:**
- `GroupShuffleSplit`: divide train/val respetando que todas las ciudades de un mismo usuario
  queden en el mismo split — evita que el modelo aprenda "de memoria" usuarios concretos
- `model_v3/`: nueva carpeta para los artefactos con la arquitectura correcta
""", "markdown"))

# PASO 1: CARGAR DATOS
cells.append(cell("""## Paso 1: Cargar datos""", "markdown"))
cells.append(cell("""\
# Cargar perfiles de usuario (output notebook 02)
profiles = pd.read_csv(DATA_DIR / "user_profiles.csv")
print(f"user_profiles.csv: {profiles.shape}")

# Cargar features de ciudad
city_raw = pd.read_csv(DATA_DIR / "city_features.csv", index_col=0)
print(f"city_features.csv: {city_raw.shape}")

# Ajustar CityFeatureBuilder
builder = CityFeatureBuilder()
builder.fit(city_raw)

USER_COLS = [c for c in profiles.columns if c.startswith("user_imp_")]
print(f"\\nDimensiones usuario: {len(USER_COLS)}")
print(f"Features ciudad (numericas): {len(builder.city_features)}")
print(f"Ciudades: {len(city_raw)}")
print(f"Perfiles: {len(profiles)}")
""", "paso1_carga"))

cells.append(cell("""\
**OBSERVACIONES:**
- user_profiles.csv contiene solo perfiles, sin ciudades — arquitectura correcta
- CityFeatureBuilder.fit() aprende el MinMaxScaler sobre las 54 ciudades
- Con 5.000 × 54 = 270.000 pares, el dataset de entrenamiento es suficientemente grande

**DECISION:**
Los labels se generan por producto escalar directo en el siguiente paso,
no por cosine_sim. Esto evita que el modelo aprenda a copiar cosine_sim.
""", "markdown"))

# PASO 2: CRUCE Y LABELS
cells.append(cell("""## Paso 2: Cruce usuarios × ciudades y generación de labels""", "markdown"))
cells.append(cell("""\
# Matriz de ciudades normalizada (54 x 148)
city_matrix_norm = builder.transform(city_raw)  # (54, 148) normalizado [0,1]
city_names = list(city_raw.index)

# DIMENSION_MAP: mapea user_imp_X → lista de city_features
# Construimos un vector de ciudad por dimension (26 dims → 148 features)
# Para el producto escalar usamos el mismo mapeo que cosine_sim

def build_user_vector_raw(user_row: pd.Series) -> np.ndarray:
    '''Proyecta user_imp_* al espacio de features de ciudad (148 dims).'''
    vec = np.zeros(len(builder.city_features))
    feat_idx = {name: i for i, name in enumerate(builder.city_features)}
    for _dim, user_key, city_keys in DIMENSION_MAP:
        importancia = float(user_row.get(user_key, 0.0))
        for ck in city_keys:
            if ck in feat_idx:
                vec[feat_idx[ck]] = max(vec[feat_idx[ck]], importancia)
    return vec

print("Generando 270.000 pares (usuario x ciudad)...")
rows = []
n_users = len(profiles)

for i, (_, user_row) in enumerate(profiles.iterrows()):
    if i % 1000 == 0:
        print(f"  {i}/{n_users}...")

    query_id  = int(user_row["query_id"])
    archetype = user_row["archetype"]
    user_vec  = build_user_vector_raw(user_row)  # (148,)

    # Producto escalar directo: user_vec · city_vec para cada ciudad
    # city_matrix_norm es (54, 148) — dot product da (54,) scores
    scores_raw = city_matrix_norm.dot(user_vec)   # (54,)

    # Cosine similarity (feature de apoyo para LightGBM)
    user_prefs = {k: float(user_row[k]) for k in USER_COLS}
    cosine_scores = builder.cosine_scores(user_prefs, city_raw)  # pd.Series (54,)

    # Labels por percentil del producto escalar (NO del cosine_sim)
    n = len(scores_raw)
    rank = pd.Series(scores_raw, index=city_names).rank(ascending=False)
    labels = pd.Series(0, index=city_names, dtype=int)
    labels[rank <= n * 0.10] = 3   # top 10%
    labels[(rank > n * 0.10) & (rank <= n * 0.30)] = 2  # top 30%
    labels[(rank > n * 0.30) & (rank <= n * 0.60)] = 1  # top 60%

    for city in city_names:
        row = {"query_id": query_id, "city": city,
               "archetype": archetype, "label": labels[city],
               "cosine_sim": float(cosine_scores[city])}
        # user_imp_* features
        for k in USER_COLS:
            row[k] = float(user_row[k])
        rows.append(row)

df = pd.DataFrame(rows)
print(f"\\nDataset: {df.shape}")
print(f"Distribucion labels:")
print(df["label"].value_counts().sort_index().to_string())
""", "paso2_cruce"))

cells.append(cell("""\
**ANOTACIONES — por que producto escalar y no cosine_sim para los labels:**

El producto escalar `user_vec · city_vec` y cosine_sim son matematicamente similares,
pero cosine_sim normaliza ambos vectores primero. La diferencia clave es arquitectural:

- Los **labels** vienen del producto escalar → son la "verdad" que el modelo aprende
- **cosine_sim** es una feature → el modelo la usa como señal de apoyo, pero no la copia

Si los labels vinieran de cosine_sim y cosine_sim fuera tambien una feature,
el modelo aprenderia a reproducir exactamente cosine_sim. Seria trivial y circular.

Con esta separacion, LightGBM puede aprender a **refinar** cosine_sim usando las
otras 174 features: por ejemplo, que `user_imp_naturaleza` importa mas cuando
`user_imp_clima` tambien es alto, o que ciertos tipos de infraestructura urbana
pesan mas para arquetipos especificos.
""", "markdown"))

# PASO 3: AÑADIR CITY FEATURES
cells.append(cell("""## Paso 3: Añadir features de ciudad al dataset""", "markdown"))
cells.append(cell("""\
# Unir con features de ciudad (una fila por ciudad, repetida para cada usuario)
city_feats = city_raw.copy().reset_index()
city_feats = city_feats.rename(columns={"index": "city"})

df = df.merge(city_feats, on="city", how="left")
print(f"Dataset con city features: {df.shape}")

# Columnas finales del feature vector
CITY_FEAT_COLS = [c for c in city_feats.columns
                  if c != "city" and c in df.columns
                  and df[c].dtype in [float, int, "float64", "int64"]]

FEATURE_COLS = USER_COLS + CITY_FEAT_COLS + ["cosine_sim"]
print(f"\\nFeatures totales para LightGBM:")
print(f"  user_imp_*:    {len(USER_COLS)}")
print(f"  city_features: {len(CITY_FEAT_COLS)}")
print(f"  cosine_sim:    1")
print(f"  TOTAL:         {len(FEATURE_COLS)}")

# Verificar NaNs
nan_cols = [c for c in FEATURE_COLS if df[c].isna().any()]
print(f"\\nColumnas con NaN: {len(nan_cols)}")
if nan_cols:
    print(f"  {nan_cols[:5]}")
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(0.0)
    print("  -> Rellenados con 0.0")
""", "paso3_city_features"))

# PASO 4: SPLIT TRAIN/VAL
cells.append(cell("""## Paso 4: Split train / validación""", "markdown"))
cells.append(cell("""\
# GroupShuffleSplit: todos los pares de un usuario van al mismo split
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
query_ids = df["query_id"].values
train_idx, val_idx = next(gss.split(df, groups=query_ids))

df_train = df.iloc[train_idx].copy()
df_val   = df.iloc[val_idx].copy()

print(f"Train: {len(df_train):,} filas | {df_train['query_id'].nunique()} usuarios")
print(f"Val:   {len(df_val):,} filas  | {df_val['query_id'].nunique()} usuarios")

# Grupos para LightGBM (numero de ciudades por query)
def make_groups(df_split):
    return df_split.groupby("query_id")["city"].count().values

groups_train = make_groups(df_train)
groups_val   = make_groups(df_val)

X_train = df_train[FEATURE_COLS].values.astype(np.float32)
y_train = df_train["label"].values.astype(np.int32)
X_val   = df_val[FEATURE_COLS].values.astype(np.float32)
y_val   = df_val["label"].values.astype(np.int32)

print(f"\\nX_train: {X_train.shape}")
print(f"X_val:   {X_val.shape}")
print(f"Grupos train (check 54): {groups_train[:5]} ...")
print(f"Todos grupos = 54: {(groups_train == 54).all() and (groups_val == 54).all()}")
""", "paso4_split"))

cells.append(cell("""\
**ANOTACIONES — GroupShuffleSplit:**

En Learning to Rank, la unidad de muestra es la **query** (un usuario),
no la fila individual. Si splitearamos filas al azar, el mismo usuario podria
tener algunas ciudades en train y otras en val, y el modelo memorizaria ese usuario.

`GroupShuffleSplit` garantiza que el 80% de los usuarios van a train y el 20% a val.
El modelo nunca ve en validacion a usuarios que ya vio en entrenamiento.
""", "markdown"))

# PASO 5: ENTRENAR LIGHTGBM
cells.append(cell("""## Paso 5: Entrenar LightGBM LambdaRank""", "markdown"))
cells.append(cell("""\
train_set = lgb.Dataset(X_train, label=y_train, group=groups_train,
                        feature_name=FEATURE_COLS)
val_set   = lgb.Dataset(X_val,   label=y_val,   group=groups_val,
                        reference=train_set)

params = {
    "objective":        "lambdarank",
    "metric":           "ndcg",
    "ndcg_eval_at":     [1, 3, 5],
    "learning_rate":    0.05,
    "num_leaves":       63,
    "min_data_in_leaf": 20,
    "max_depth":        -1,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq":     5,
    "lambdarank_truncation_level": 10,
    "verbose":          -1,
    "seed":             42,
}

evals_result = {}

print("Entrenando LightGBM LambdaRank...")
print(f"  Features: {len(FEATURE_COLS)}")
print(f"  Usuarios train: {df_train['query_id'].nunique()}")
print(f"  Usuarios val:   {df_val['query_id'].nunique()}")
print()

model = lgb.train(
    params,
    train_set,
    num_boost_round=500,
    valid_sets=[train_set, val_set],
    valid_names=["train", "val"],
    callbacks=[
        lgb.early_stopping(stopping_rounds=30, verbose=True),
        lgb.record_evaluation(evals_result),
        lgb.log_evaluation(period=50),
    ],
)

print(f"\\nMejor iteracion: {model.best_iteration}")
print(f"Mejor NDCG@5 val: {max(evals_result['val']['ndcg@5']):.4f}")
""", "paso5_train"))

cells.append(cell("""\
**ANOTACIONES — LambdaRank:**

LambdaRank es un algoritmo de Learning to Rank que aprende directamente a ordenar,
no a predecir valores absolutos. En cada iteracion calcula gradientes que penalizan
los **intercambios de orden incorrectos**, ponderados por el impacto en NDCG.

NDCG@5 (Normalized Discounted Cumulative Gain at 5): mide la calidad del top-5.
Una ciudad en posicion #1 vale mas que en posicion #5.
Valor maximo = 1.0 (ranking perfecto). Valor > 0.85 es muy bueno.

`early_stopping(30)`: si NDCG@5 no mejora en 30 iteraciones, para.
Evita sobreentrenamiento sin necesidad de fijar el numero de arboles manualmente.
""", "markdown"))

# PASO 6: CURVAS DE APRENDIZAJE
cells.append(cell("""## Paso 6: Curvas de aprendizaje""", "markdown"))
cells.append(cell("""\
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
metrics = ["ndcg@1", "ndcg@3", "ndcg@5"]

for ax, metric in zip(axes, metrics):
    train_vals = evals_result["train"][metric]
    val_vals   = evals_result["val"][metric]
    iters = range(1, len(train_vals) + 1)

    ax.plot(iters, train_vals, label="Train",      color="steelblue", linewidth=1.5)
    ax.plot(iters, val_vals,   label="Validacion", color="crimson",   linewidth=1.5)
    ax.axvline(model.best_iteration, color="green", linestyle="--",
               alpha=0.7, label=f"Best iter={model.best_iteration}")

    ax.set_title(f"{metric.upper()}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Iteracion")
    ax.set_ylabel("NDCG")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1)

    best_val = max(val_vals)
    ax.annotate(f"Max val: {best_val:.4f}",
                xy=(model.best_iteration, best_val),
                xytext=(model.best_iteration + 10, best_val - 0.05),
                fontsize=8, color="crimson",
                arrowprops=dict(arrowstyle="->", color="crimson", lw=1))

plt.suptitle("Curvas de aprendizaje — LightGBM LambdaRank", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(DATA_DIR / "nb03_curvas_aprendizaje.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"NDCG@1 val: {max(evals_result['val']['ndcg@1']):.4f}")
print(f"NDCG@3 val: {max(evals_result['val']['ndcg@3']):.4f}")
print(f"NDCG@5 val: {max(evals_result['val']['ndcg@5']):.4f}")
""", "paso6_curvas"))

cells.append(cell("""\
**PARA QUE SIRVE ESTE GRAFICO:**
Las curvas de aprendizaje muestran si el modelo esta aprendiendo correctamente.

- **Train sube, Val sube**: aprendizaje correcto
- **Train sube, Val baja**: sobreentrenamiento (memoriza en vez de generalizar)
- **Ambas se estabilizan**: el modelo ha convergido — early stopping correcto

**QUE ESPERAMOS:** NDCG@5 val > 0.80 con gap train-val < 0.10.
""", "markdown"))

# PASO 7: IMPORTANCIA DE FEATURES
cells.append(cell("""## Paso 7: Importancia de features""", "markdown"))
cells.append(cell("""\
importances = pd.Series(
    model.feature_importance(importance_type="gain"),
    index=FEATURE_COLS
).sort_values(ascending=False)

top30 = importances.head(30)
bottom10 = importances.tail(10)

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Top 30
colors = ["#667eea" if "user_imp" in f else
          "#e74c3c" if f == "cosine_sim" else "#2ecc71"
          for f in top30.index]
top30.plot(kind="barh", ax=axes[0], color=colors[::-1])
axes[0].invert_yaxis()
axes[0].set_title("Top 30 features por importancia (gain)", fontsize=12, fontweight="bold")
axes[0].set_xlabel("Importancia (gain)")

# Leyenda de colores
from matplotlib.patches import Patch
legend = [Patch(color="#667eea", label="user_imp_* (preferencias usuario)"),
          Patch(color="#e74c3c", label="cosine_sim (señal apoyo)"),
          Patch(color="#2ecc71", label="city_features_* (features ciudad)")]
axes[0].legend(handles=legend, fontsize=8, loc="lower right")

# Importancia por grupo
groups_imp = {
    "user_imp_*": importances[[f for f in importances.index if f.startswith("user_imp_")]].sum(),
    "city_features_*": importances[[f for f in importances.index if f not in [f2 for f2 in importances.index if "user_imp" in f2 or f2 == "cosine_sim"]]].sum(),
    "cosine_sim": importances.get("cosine_sim", 0),
}
pd.Series(groups_imp).plot(kind="pie", ax=axes[1], autopct="%1.1f%%",
                            colors=["#667eea", "#2ecc71", "#e74c3c"],
                            startangle=90)
axes[1].set_title("Importancia por grupo de features", fontsize=12, fontweight="bold")
axes[1].set_ylabel("")

plt.suptitle("Feature Importance — LightGBM LambdaRank", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(DATA_DIR / "nb03_feature_importance.png", dpi=150, bbox_inches="tight")
plt.show()

print("Top 10 features mas importantes:")
for feat, val in importances.head(10).items():
    tipo = "USER" if "user_imp" in feat else ("COSINE" if feat == "cosine_sim" else "CITY")
    print(f"  [{tipo}] {feat:<35} {val:>10.1f}")
""", "paso7_importancia"))

cells.append(cell("""\
**PARA QUE SIRVE ESTE GRAFICO:**
La importancia (gain) mide cuanto mejora el NDCG cada vez que el modelo usa una feature
para dividir un nodo. Features con gain alto son las mas utiles para el modelo.

**QUE ESPERAMOS:**
- Si `cosine_sim` domina completamente → el modelo solo aprende a copiar cosine_sim
- Si `user_imp_*` y `city_features_*` tienen peso significativo → el modelo aprende
  correlaciones reales entre preferencias y caracteristicas urbanas
- El pie chart debe mostrar distribucion equilibrada entre los 3 grupos
""", "markdown"))

# PASO 8: SHAP
cells.append(cell("""## Paso 8: SHAP — explicabilidad""", "markdown"))
cells.append(cell("""\
print("Calculando SHAP values (muestra de 500 usuarios val)...")
sample_idx = np.random.choice(len(X_val), min(500 * 54, len(X_val)), replace=False)
X_sample = X_val[sample_idx]

explainer    = shap.TreeExplainer(model)
shap_values  = explainer.shap_values(X_sample)

# Si shap_values es lista, tomar el relevante (label alto = label 2 o 3)
if isinstance(shap_values, list):
    sv = shap_values[-1]  # ultimo = mayor relevancia
else:
    sv = shap_values

# Beeswarm plot — top 20 features
plt.figure(figsize=(12, 8))
shap.summary_plot(
    sv, X_sample,
    feature_names=FEATURE_COLS,
    max_display=20,
    show=False
)
plt.title("SHAP Summary — impacto de cada feature en el ranking", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(DATA_DIR / "nb03_shap_summary.png", dpi=150, bbox_inches="tight")
plt.show()
print("Guardado: nb03_shap_summary.png")
""", "paso8_shap"))

cells.append(cell("""\
**PARA QUE SIRVE ESTE GRAFICO:**
SHAP (SHapley Additive exPlanations) explica la contribucion de cada feature
a la prediccion del modelo. Es el estandar de explicabilidad en ML.

Cada punto es un par (usuario, ciudad). El eje X muestra si esa feature
empujo el score hacia arriba (derecha = beneficia la ciudad) o hacia abajo.
El color muestra el valor de la feature (rojo = alto, azul = bajo).

**QUE ESPERAMOS:**
- `user_imp_naturaleza` alto (rojo) → efecto positivo en ciudades con naturaleza
- `cosine_sim` alto → siempre positivo (como esperamos)
- Features de ciudad relevantes para arquetipos especificos aparecen en el top
""", "markdown"))

# PASO 9: VALIDACION CUALITATIVA
cells.append(cell("""## Paso 9: Validación cualitativa — ¿recomienda bien?""", "markdown"))
cells.append(cell("""\
def recomendar(user_prefs: dict, top_n: int = 8) -> pd.DataFrame:
    \"\"\"Genera recomendaciones para un perfil de usuario.\"\"\"
    # Construir vector de usuario
    dim_defaults = {k: 0.05 for k in USER_COLS}
    for k, v in user_prefs.items():
        if f"user_imp_{k}" in dim_defaults:
            dim_defaults[f"user_imp_{k}"] = v

    # Cosine sim (feature de apoyo)
    cosine_s = builder.cosine_scores(dim_defaults, city_raw)

    # Construir feature matrix (1 fila por ciudad)
    city_feats_mat = city_raw.copy()
    rows_inf = []
    for city in city_names:
        row = {k: dim_defaults[k] for k in USER_COLS}
        row["cosine_sim"] = float(cosine_s[city])
        for feat in CITY_FEAT_COLS:
            row[feat] = float(city_raw.loc[city, feat]) if feat in city_raw.columns else 0.0
        rows_inf.append(row)

    X_inf = pd.DataFrame(rows_inf)[FEATURE_COLS].values.astype(np.float32)
    scores = model.predict(X_inf)

    result = pd.DataFrame({"city": city_names, "score": scores, "cosine_sim": cosine_s.values})
    return result.sort_values("score", ascending=False).head(top_n)


# --- Test 1: kite_surf
print("=" * 55)
print("KITE SURF: deporte_agua=0.9, naturaleza=0.8, clima=0.8")
print("Esperamos: Tarifa, Fuerteventura, Las_Palmas")
rec = recomendar({"deporte_agua": 0.9, "naturaleza": 0.8, "clima": 0.8,
                   "coste": 0.5, "movilidad": 0.5})
print(rec[["city", "score", "cosine_sim"]].to_string(index=False))

# --- Test 2: ski_nieve
print()
print("=" * 55)
print("SKI: deporte_montana=0.95, naturaleza=0.7")
print("Esperamos: Chamonix, Innsbruck")
rec = recomendar({"deporte_montana": 0.95, "naturaleza": 0.7, "clima": 0.3})
print(rec[["city", "score", "cosine_sim"]].to_string(index=False))

# --- Test 3: nomada_barato
print()
print("=" * 55)
print("NOMADA BARATO: nomada=0.9, coste=0.9, calidad_vida=0.7")
print("Esperamos: Tbilisi, Sofia, Krakow, Medellin")
rec = recomendar({"nomada": 0.9, "coste": 0.9, "calidad_vida": 0.7,
                   "movilidad": 0.6, "comunidad": 0.5})
print(rec[["city", "score", "cosine_sim"]].to_string(index=False))

# --- Test 4: jubilado activo
print()
print("=" * 55)
print("JUBILADO ACTIVO: clima=0.9, salud=0.85, gastronomia=0.8, calidad_vida=0.85")
print("Esperamos: Malaga, Valencia, Alicante, Lisboa")
rec = recomendar({"clima": 0.9, "salud": 0.85, "gastronomia": 0.8,
                   "calidad_vida": 0.85, "movilidad": 0.8})
print(rec[["city", "score", "cosine_sim"]].to_string(index=False))

# --- Test 5: familia con ninos
print()
print("=" * 55)
print("FAMILIA NINOS: familia=0.9, educacion=0.8, salud=0.8, calidad_vida=0.85")
print("Esperamos: ciudades medianas europeas seguras")
rec = recomendar({"familia": 0.9, "educacion": 0.8, "salud": 0.8,
                   "calidad_vida": 0.85, "movilidad": 0.7})
print(rec[["city", "score", "cosine_sim"]].to_string(index=False))
""", "paso9_validacion"))

cells.append(cell("""\
**PARA QUE SIRVE ESTA VALIDACION:**
El test cualitativo es la "prueba de la realidad": independientemente de las metricas
NDCG, el modelo debe recomendar ciudades que tengan sentido para cada perfil.

Si Tarifa no aparece en top-3 para kite_surf, hay un problema — aunque NDCG@5 sea alto.
Esto puede ocurrir porque las features de ciudad no capturan bien ese atributo,
o porque el modelo ha aprendido un patron incorrecto.

**DECISION:** si alguna validacion falla claramente, documentarla en ERRORS_LOG.md
y analizar que feature esta fallando antes de conectar a la app.
""", "markdown"))

# PASO 10: COMPARACION LGB vs COSINE_SIM
cells.append(cell("""## Paso 10: Comparación LightGBM vs cosine_sim baseline""", "markdown"))
cells.append(cell("""\
from sklearn.metrics import ndcg_score

def ndcg_k(df_split, score_col, k=5):
    \"\"\"NDCG@k medio sobre todos los usuarios del split.\"\"\"
    ndcgs = []
    for qid, grp in df_split.groupby("query_id"):
        y_true = grp["label"].values
        y_score = grp[score_col].values
        if y_true.max() == 0:
            continue
        n = min(k, len(y_true))
        ndcgs.append(ndcg_score([y_true], [y_score], k=n))
    return np.mean(ndcgs)

# LightGBM predictions en val
X_val_full = df_val[FEATURE_COLS].values.astype(np.float32)
df_val = df_val.copy()
df_val["lgbm_score"] = model.predict(X_val_full)

print("COMPARACION NDCG@5 — val set:")
print(f"  cosine_sim baseline: {ndcg_k(df_val, 'cosine_sim', k=5):.4f}")
print(f"  LightGBM LambdaRank: {ndcg_k(df_val, 'lgbm_score', k=5):.4f}")

# Por arquetipo
print("\\nNDCG@5 por arquetipo (LightGBM vs cosine_sim):")
print(f"{'Arquetipo':<25} {'cosine_sim':>12} {'LightGBM':>10} {'Mejora':>8}")
print("-" * 60)
for arch, grp in df_val.groupby("archetype"):
    ndcg_cos  = ndcg_k(grp, "cosine_sim", k=5)
    ndcg_lgbm = ndcg_k(grp, "lgbm_score", k=5)
    mejora = ndcg_lgbm - ndcg_cos
    arrow = "+" if mejora >= 0 else ""
    print(f"  {arch:<25} {ndcg_cos:>12.4f} {ndcg_lgbm:>10.4f} {arrow}{mejora:>7.4f}")
""", "paso10_comparacion"))

cells.append(cell("""\
**PARA QUE SIRVE ESTA COMPARACION:**
Si LightGBM no mejora sobre cosine_sim, el modelo no esta anadiendo valor.
En ese caso, la Capa 1 (cosine_sim) sola seria suficiente y mas simple.

**LO QUE ESPERAMOS:**
- LightGBM > cosine_sim en la mayoria de arquetipos
- Arquetipos con muchas dimensiones HIGH (ej. jubilado_activo con 6 dims HIGH)
  deberan mejorar mas, porque el modelo puede aprender ponderaciones especificas
- Arquetipos simples (ej. ski_nieve con 2 dims HIGH) pueden mejorar poco
  porque cosine_sim ya es suficientemente preciso
""", "markdown"))

# PASO 11: MLFLOW
cells.append(cell("""## Paso 11: MLflow — registro del experimento""", "markdown"))
cells.append(cell("""\
mlflow.set_tracking_uri(str(ROOT / "notebooks" / "mlruns"))
mlflow.set_experiment("nomadoptima_lambdarank")

best_ndcg5 = max(evals_result["val"]["ndcg@5"])
best_ndcg3 = max(evals_result["val"]["ndcg@3"])
best_ndcg1 = max(evals_result["val"]["ndcg@1"])

with mlflow.start_run(run_name="v3_producto_escalar_175features"):
    # Parametros
    mlflow.log_params({
        "n_usuarios":      len(profiles),
        "n_ciudades":      len(city_raw),
        "n_features":      len(FEATURE_COLS),
        "n_user_features": len(USER_COLS),
        "n_city_features": len(CITY_FEAT_COLS),
        "label_method":    "producto_escalar_directo",
        "num_leaves":      params["num_leaves"],
        "learning_rate":   params["learning_rate"],
        "feature_fraction":params["feature_fraction"],
        "best_iteration":  model.best_iteration,
    })
    # Metricas
    mlflow.log_metrics({
        "ndcg_at_1_val": best_ndcg1,
        "ndcg_at_3_val": best_ndcg3,
        "ndcg_at_5_val": best_ndcg5,
    })
    # Graficos
    mlflow.log_artifact(str(DATA_DIR / "nb03_curvas_aprendizaje.png"))
    mlflow.log_artifact(str(DATA_DIR / "nb03_feature_importance.png"))
    mlflow.log_artifact(str(DATA_DIR / "nb03_shap_summary.png"))
    # Modelo
    mlflow.lightgbm.log_model(model, "lgbm_ranker")

    run_id = mlflow.active_run().info.run_id
    print(f"MLflow run_id: {run_id}")

print(f"\\nExperimento registrado en notebooks/mlruns/")
print(f"Para ver: mlflow ui --backend-store-uri notebooks/mlruns")
""", "paso11_mlflow"))

# PASO 12: GUARDAR ARTEFACTOS
cells.append(cell("""## Paso 12: Guardar artefactos del modelo""", "markdown"))
cells.append(cell("""\
import joblib, json as json_lib

# 1. Modelo LightGBM
model_path = MODEL_DIR / "lgbm_ranker_v3.txt"
model.save_model(str(model_path))
print(f"Modelo: {model_path.name}")

# 2. CityFeatureBuilder (incluye MinMaxScaler fitteado)
builder_path = MODEL_DIR / "feature_builder_v3.joblib"
joblib.dump(builder, builder_path)
print(f"Builder: {builder_path.name}")

# 3. Lista de features en orden exacto (critico para inferencia)
features_path = MODEL_DIR / "feature_cols_v3.json"
with open(features_path, "w", encoding="utf-8") as f:
    json_lib.dump(FEATURE_COLS, f, indent=2)
print(f"Features: {features_path.name} ({len(FEATURE_COLS)} features)")

# 4. Metricas del modelo
metrics_path = MODEL_DIR / "model_metrics_v3.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json_lib.dump({
        "ndcg_at_1_val": best_ndcg1,
        "ndcg_at_3_val": best_ndcg3,
        "ndcg_at_5_val": best_ndcg5,
        "best_iteration": model.best_iteration,
        "n_features": len(FEATURE_COLS),
        "n_users_train": df_train["query_id"].nunique(),
        "label_method": "producto_escalar_directo",
        "fecha": "2026-04-10",
    }, f, indent=2)
print(f"Metricas: {metrics_path.name}")

print(f"\\nTodos los artefactos guardados en: {MODEL_DIR}")
print("\\nRESUMEN FINAL:")
print(f"  NDCG@1: {best_ndcg1:.4f}")
print(f"  NDCG@3: {best_ndcg3:.4f}")
print(f"  NDCG@5: {best_ndcg5:.4f}")
print(f"  Iteraciones: {model.best_iteration}")
print(f"  Features: {len(FEATURE_COLS)}")
""", "paso12_guardar"))

# NOTEBOOK JSON
nb = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.10"}
    },
    "cells": cells
}

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook generado: {OUT}")
print(f"Celdas: {len(cells)}")
