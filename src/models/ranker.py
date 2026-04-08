"""
NomadOptima — Capa 4: NomadRanker (produccion)
src/models/ranker.py

Wrapper que encapsula las 5 capas del sistema de recomendacion:
  Capa 1: CityFeatureBuilder -> cosine_sim entre perfil y ciudad
  Capa 2: UserClusterer      -> PCA->UMAP->HDBSCAN sobre perfil de usuario
  Capa 3: CityClusterer      -> PCA->UMAP->HDBSCAN sobre features de ciudad
  Capa 4: LightGBM LambdaMART -> ranking final con todas las features
  Pre-filtros: restricciones duras antes de puntuar

Uso tipico:
    from src.models.ranker import NomadRanker

    ranker = NomadRanker()
    results = ranker.rank(user_profile, top_n=5)
    # -> pd.DataFrame con rank, city, score, cosine_sim, ...

Perfil de usuario esperado (dict):
    Las 26 dimensiones con prefijo user_imp_* (valores 0.0-1.0):
    user_imp_gastronomia, user_imp_vida_nocturna, user_imp_cultura,
    user_imp_arte_visual, user_imp_naturaleza, user_imp_deporte_agua,
    user_imp_deporte_montana, user_imp_deporte_urbano, user_imp_bienestar,
    user_imp_familia, user_imp_mascotas, user_imp_nomada, user_imp_alojamiento,
    user_imp_movilidad, user_imp_compras, user_imp_servicios, user_imp_salud,
    user_imp_turismo, user_imp_educacion, user_imp_comunidad, user_imp_coste,
    user_imp_clima, user_imp_calidad_vida, user_imp_social_media,
    user_imp_musica, user_imp_autenticidad

    Opcionales para pre-filtros:
    necesita_coworking (bool), viaja_con_mascota (bool)
"""

import json
import sys
from pathlib import Path
from typing import Optional

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.models.clustering import USER_CLUSTER_FEATURES
from src.processing.features import (
    CityFeatureBuilder, load_all_cities, build_city_feature_matrix
)

# Rutas por defecto
MODEL_DIR = ROOT / "data" / "processed" / "model_v2"
CITY_FEATURES_CSV = ROOT / "data" / "processed" / "city_features.csv"


class NomadRanker:
    """
    Wrapper de produccion sobre el modelo LightGBM v2 de NomadOptima.

    Carga los 5 artefactos del model_v2 y expone el metodo rank()
    que produce el ranking de ciudades para un perfil de usuario.

    Parametros
    ----------
    model_dir : Path, opcional
        Directorio con los artefactos del model_v2.
        Por defecto: data/processed/model_v2/
    """

    # Nombres para mostrar en la UI (ciudad_key -> display_name)
    DISPLAY_NAMES = {
        "Malaga":                "Malaga",
        "Paris":                 "Paris",
        "Valencia":              "Valencia",
        "Porto":                 "Porto",
        "Bordeaux":              "Bordeaux",
        "Barcelona":             "Barcelona",
        "Madrid":                "Madrid",
        "Seville":               "Sevilla",
        "Sevilla":               "Sevilla",
        "Granada":               "Granada",
        "Alicante":              "Alicante",
        "Tarifa":                "Tarifa",
        "Fuerteventura":         "Fuerteventura",
        "Las_Palmas":            "Las Palmas de Gran Canaria",
        "San_Sebastian":         "San Sebastian",
        "Bilbao":                "Bilbao",
        "Santiago_de_Compostela":"Santiago de Compostela",
        "Faro":                  "Faro",
        "Lisbon":                "Lisboa",
        "Amsterdam":             "Amsterdam",
        "Berlin":                "Berlin",
        "Brussels":              "Bruselas",
        "London":                "Londres",
        "Brighton":              "Brighton",
        "Copenhagen":            "Copenhague",
        "Stockholm":             "Estocolmo",
        "Milan":                 "Milan",
        "Montpellier":           "Montpellier",
        "Prague":                "Praga",
        "Budapest":              "Budapest",
        "Krakow":                "Cracovia",
        "Bucharest":             "Bucarest",
        "Sofia":                 "Sofia",
        "Belgrade":              "Belgrado",
        "Ljubljana":             "Liubliana",
        "Riga":                  "Riga",
        "Tallinn":               "Tallin",
        "Athens":                "Atenas",
        "Reykjavik":             "Reykjavik",
        "Tbilisi":               "Tbilisi",
        "Andorra":               "Andorra la Vella",
        "Medellin":              "Medellin",
        "Mexico_City":           "Ciudad de Mexico",
        "Cartagena":             "Cartagena de Indias",
    }

    def __init__(self, model_dir: Optional[Path] = None):
        """
        Inicializa el ranker cargando los 5 artefactos del model_v2.

        Lanza FileNotFoundError si los artefactos no existen todavia.
        Para generarlos, ejecuta notebooks/03_train_model.ipynb primero.
        """
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR

        self.lgbm_model     = None
        self.user_clusterer = None
        self.city_clusterer = None
        self.feature_cols   = None
        self.affinity_table = None
        self.city_df        = None
        self.feature_builder = None

        self._load_artifacts()
        self._build_city_df()

    # ──────────────────────────────────────────────────────────────────────────
    # Carga de artefactos
    # ──────────────────────────────────────────────────────────────────────────

    def _load_artifacts(self):
        """
        Carga los 5 artefactos del model_v2 desde disco.

        Los artefactos se generan ejecutando notebooks/03_train_model.ipynb.
        """
        files = {
            "lgbm":       self.model_dir / "lgbm_ranker.txt",
            "user_clust": self.model_dir / "user_clusterer.joblib",
            "city_clust": self.model_dir / "city_clusterer.joblib",
            "feat_cols":  self.model_dir / "feature_cols.json",
            "affinity":   self.model_dir / "affinity_table.csv",
        }
        for name, p in files.items():
            if not p.exists():
                raise FileNotFoundError(
                    f"Artefacto no encontrado: {p}\n"
                    "Ejecuta primero notebooks/03_train_model.ipynb"
                )

        self.lgbm_model     = lgb.Booster(model_file=str(files["lgbm"]))
        self.user_clusterer = joblib.load(files["user_clust"])
        self.city_clusterer = joblib.load(files["city_clust"])

        with open(files["feat_cols"], "r", encoding="utf-8") as f:
            self.feature_cols = json.load(f)

        self.affinity_table = pd.read_csv(files["affinity"], index_col=0)
        # columnas como int (son cluster IDs)
        self.affinity_table.columns = self.affinity_table.columns.astype(int)

        print(f"[NomadRanker] Artefactos cargados desde {self.model_dir.name}/")
        print(f"  LightGBM: {self.lgbm_model.num_trees()} arboles")
        print(f"  Features: {len(self.feature_cols)}")
        print(f"  User clusters: {len(self.affinity_table)}")
        print(f"  City clusters: {len(self.affinity_table.columns)}")

    # ──────────────────────────────────────────────────────────────────────────
    # Construccion del DataFrame de ciudades
    # ──────────────────────────────────────────────────────────────────────────

    def _build_city_df(self):
        """
        Carga y cachea el DataFrame de features de todas las ciudades.

        Intenta cargar desde city_features.csv (ya procesado).
        Si no existe, reconstruye desde los JSONs raw.
        """
        if CITY_FEATURES_CSV.exists():
            self.city_df = pd.read_csv(CITY_FEATURES_CSV, index_col=0)
            print(f"[NomadRanker] city_df: {len(self.city_df)} ciudades x "
                  f"{len(self.city_df.columns)} features (desde CSV)")
        else:
            print("[NomadRanker] Reconstruyendo city_df desde JSONs raw...")
            cities_raw = load_all_cities()
            self.city_df = build_city_feature_matrix(cities_raw)
            print(f"[NomadRanker] city_df: {len(self.city_df)} ciudades x "
                  f"{len(self.city_df.columns)} features (desde JSONs)")

        # Separar columnas numericas de texto
        num_cols = self.city_df.select_dtypes(include="number").columns.tolist()

        # Inicializar y ajustar el CityFeatureBuilder con las ciudades disponibles
        self.feature_builder = CityFeatureBuilder()
        self.feature_builder.fit(self.city_df[num_cols])

        # Anadir clusters de ciudad al city_df
        city_col_df = pd.DataFrame({"city": self.city_df.index.tolist()})
        city_col_df = self.city_clusterer.predict(city_col_df)
        self.city_df["city_cluster_id"]       = city_col_df["city_cluster_id"].values
        self.city_df["city_cluster_strength"] = city_col_df["city_cluster_strength"].values

    # ──────────────────────────────────────────────────────────────────────────
    # Pre-filtros duros
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_hard_filters(self, user_profile: dict, cities: list) -> list:
        """
        Elimina ciudades incompatibles con el perfil ANTES de puntuar.

        Restricciones:
        - Presupuesto: coste_vida_estimado > presupuesto_max * 1.15 -> eliminada
        - Temperatura: temp_media_anual < temp_min_c - 3 -> eliminada
        - Coworking: si el usuario lo necesita y la ciudad tiene 0 -> eliminada
        - Mascotas: si viaja con mascota y la ciudad no tiene espacios -> eliminada

        Si todos los candidatos son eliminados, devuelve todas (sin filtrar).
        """
        presupuesto_max  = user_profile.get("presupuesto_max", 9999)
        temp_min         = user_profile.get("temp_min_c", -99)
        necesita_cowork  = bool(user_profile.get("necesita_coworking", False))
        viaja_mascota    = bool(user_profile.get("viaja_con_mascota", False))

        candidatos = []
        for city in cities:
            if city not in self.city_df.index:
                continue
            row = self.city_df.loc[city]

            # Presupuesto
            coste_col = "city_coste_vida_estimado" if "city_coste_vida_estimado" in row.index else "coste_vida_estimado"
            coste = row.get(coste_col, 0)
            if coste > 0 and coste > presupuesto_max * 1.15:
                continue

            # Temperatura
            temp_col = "city_temp_media_anual" if "city_temp_media_anual" in row.index else "temp_media_anual"
            temp = row.get(temp_col, 99)
            if temp < temp_min - 3:
                continue

            # Coworking
            if necesita_cowork:
                cow_cols = ["city_gp_coworking", "gp_coworking", "city_coworking_osm"]
                cow_val  = max([row.get(c, 0) for c in cow_cols if c in row.index] or [0])
                if cow_val == 0:
                    continue

            candidatos.append(city)

        return candidatos if candidatos else cities

    # ──────────────────────────────────────────────────────────────────────────
    # Lookup de afinidad cluster -> cluster
    # ──────────────────────────────────────────────────────────────────────────

    def _get_affinity(self, user_cluster_id: int, city_cluster_id: int) -> float:
        """
        Devuelve la afinidad aprendida entre un arquetipo de usuario y un tipo de ciudad.

        La tabla de afinidad se genera durante el training como la relevancia
        media normalizada de cada par (user_cluster, city_cluster).
        Si el par no existe en la tabla, devuelve 0.5 (valor neutro).
        """
        uc = int(user_cluster_id)
        cc = int(city_cluster_id)
        try:
            if uc in self.affinity_table.index and cc in self.affinity_table.columns:
                return float(self.affinity_table.loc[uc, cc])
        except (KeyError, TypeError):
            pass
        return 0.5

    # ──────────────────────────────────────────────────────────────────────────
    # Perfil por defecto
    # ──────────────────────────────────────────────────────────────────────────

    def _default_profile(self) -> dict:
        """
        Valores por defecto para features opcionales no presentes en el perfil.
        Todas las importancias en 0.5 (neutral).
        """
        defaults = {key: 0.5 for key in USER_CLUSTER_FEATURES}
        defaults.update({
            "presupuesto_max":   2000.0,
            "temp_min_c":        10.0,
            "necesita_coworking": False,
            "viaja_con_mascota":  False,
        })
        return defaults

    # ──────────────────────────────────────────────────────────────────────────
    # Metodo principal: rank()
    # ──────────────────────────────────────────────────────────────────────────

    def rank(
        self,
        user_profile: dict,
        top_n: int = 5,
        apply_filters: bool = True,
    ) -> pd.DataFrame:
        """
        Produce el ranking de ciudades para un perfil de usuario.

        Flujo completo:
          1. Completar perfil con defaults
          2. Aplicar pre-filtros duros (elimina incompatibles)
          3. Cosine similarity perfil <-> ciudad  (Capa 1)
          4. Cluster del usuario — PCA->UMAP->HDBSCAN  (Capa 2)
          5. Cluster de ciudad (ya calculado en city_df)  (Capa 3)
          6. Afinidad user_cluster x city_cluster  (feature de interaccion)
          7. Predecir con LightGBM  (Capa 4)
          8. Ordenar y retornar top_n ciudades

        Parametros
        ----------
        user_profile : dict
            Preferencias del usuario. Claves: user_imp_* (0.0-1.0).
            Ver docstring del modulo para lista completa.
        top_n : int
            Numero de ciudades a retornar.
        apply_filters : bool
            Si True, aplica pre-filtros duros antes de puntuar.

        Retorna
        -------
        pd.DataFrame con columnas:
            rank, city, display_name, score, cosine_sim,
            user_cluster_id, city_cluster_id,
            coste_vida_estimado, temp_media_anual
        """
        # 1. Perfil completo con defaults
        profile = self._default_profile()
        profile.update(user_profile)

        # 2. Pre-filtros duros
        all_cities = self.city_df.index.tolist()
        candidates = (
            self._apply_hard_filters(profile, all_cities)
            if apply_filters else all_cities
        )

        # DataFrame de ciudades candidatas
        cand_df = self.city_df.loc[candidates].copy()
        cand_df["city"] = cand_df.index

        # 3. Cosine similarity (Capa 1)
        # Necesitamos las columnas numericas sin prefijo feat_city_
        # CityFeatureBuilder trabaja con city_* o directamente con los nombres
        num_cols = self.feature_builder.city_features
        cand_num = cand_df[[c for c in num_cols if c in cand_df.columns]].copy()

        cosine_scores = self.feature_builder.cosine_scores(profile, cand_num)
        cand_df["cosine_sim"] = cosine_scores.values

        # 4. Cluster del usuario (Capa 2)
        # Preparar un DataFrame con las 26 features de usuario (mismo perfil para todas las ciudades)
        n = len(cand_df)
        user_rows = [{feat: float(profile.get(feat, 0.5))
                      for feat in USER_CLUSTER_FEATURES}] * n
        user_df = pd.DataFrame(user_rows)
        user_df["query_id"] = 0  # un solo usuario
        # user_clusterer.predict espera drop_duplicates por query_id -> todos iguales OK
        user_df_pred = self.user_clusterer.predict(user_df)

        cand_df["user_cluster_id"]      = user_df_pred["user_cluster_id"].iloc[0]
        cand_df["user_cluster_strength"] = user_df_pred["user_cluster_strength"].iloc[0]

        # 5. city_cluster_id ya esta en cand_df (calculado en _build_city_df)

        # 6. Afinidad user_cluster x city_cluster
        uid = int(cand_df["user_cluster_id"].iloc[0])
        cand_df["afinidad_uc_cc"] = cand_df["city_cluster_id"].apply(
            lambda cc: self._get_affinity(uid, cc)
        )

        # 7. Construir la matrix de features en el orden exacto del training
        # Las columnas del training tienen prefijo feat_city_
        # Las de city_df pueden tener o no ese prefijo — mapeamos ambas formas
        rename_map = {}
        for col in cand_df.columns:
            feat_name = f"feat_city_{col}"
            if feat_name in self.feature_cols and col not in self.feature_cols:
                rename_map[col] = feat_name

        cand_renamed = cand_df.rename(columns=rename_map)

        # Anadir features de usuario con el prefijo correcto del training
        for feat in USER_CLUSTER_FEATURES:
            cand_renamed[feat] = float(profile.get(feat, 0.5))

        # Rellenar columnas que faltan con 0
        missing = [c for c in self.feature_cols if c not in cand_renamed.columns]
        for c in missing:
            cand_renamed[c] = 0.0

        X = cand_renamed[self.feature_cols].astype(float).values

        # 8. Prediccion LightGBM (Capa 4)
        scores = self.lgbm_model.predict(X)
        cand_df["score"] = scores

        # 9. Ordenar y formatear resultado
        result = (
            cand_df
            .sort_values("score", ascending=False)
            .head(top_n)
            .reset_index()
            .rename(columns={"index": "city_key"})
        )
        result["rank"]         = range(1, len(result) + 1)
        result["display_name"] = result["city_key"].map(
            lambda k: self.DISPLAY_NAMES.get(k, k)
        )

        # Columnas de coste/clima (pueden tener o no prefijo)
        for raw_col, out_col in [
            ("city_coste_vida_estimado", "coste_vida_estimado"),
            ("coste_vida_estimado",      "coste_vida_estimado"),
            ("city_temp_media_anual",    "temp_media_anual"),
            ("temp_media_anual",         "temp_media_anual"),
        ]:
            if raw_col in result.columns and out_col not in result.columns:
                result[out_col] = result[raw_col]

        final_cols = ["rank", "city_key", "display_name", "score", "cosine_sim",
                      "user_cluster_id", "city_cluster_id", "afinidad_uc_cc"]
        for c in ["coste_vida_estimado", "temp_media_anual"]:
            if c in result.columns:
                final_cols.append(c)

        return result[[c for c in final_cols if c in result.columns]]

    def explain(self, user_profile: dict, city_key: str, top_n: int = 5) -> list:
        """
        Devuelve las dimensiones que mas contribuyen al score de una ciudad.
        Util para mostrar la explicacion en Streamlit.

        Returns:
            list de (dimension_name, contribucion 0-1)
        """
        profile = self._default_profile()
        profile.update(user_profile)

        num_cols = self.feature_builder.city_features
        city_num = self.city_df[[c for c in num_cols if c in self.city_df.columns]]

        return self.feature_builder.top_features_for_city(
            profile, city_key, city_num, top_n=top_n
        )


# ── CLI rapido para probar el ranker ─────────────────────────────────────────
if __name__ == "__main__":
    print("Cargando NomadRanker...")
    try:
        ranker = NomadRanker()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        import sys
        sys.exit(1)

    print("Artefactos cargados.\n")

    # Perfil 1: nomada digital
    perfil_nomada = {
        "user_imp_nomada":        0.99,
        "user_imp_coste":         0.95,
        "user_imp_clima":         0.70,
        "user_imp_gastronomia":   0.30,
        "user_imp_deporte_agua":  0.20,
        "user_imp_cultura":       0.40,
        "user_imp_naturaleza":    0.30,
        "necesita_coworking":     True,
    }
    print("=== PERFIL: Nomada digital ===")
    print(ranker.rank(perfil_nomada, top_n=5).to_string(index=False))
    print()

    # Perfil 2: deportista kite
    perfil_kite = {
        "user_imp_deporte_agua":  0.99,
        "user_imp_naturaleza":    0.90,
        "user_imp_clima":         0.85,
        "user_imp_coste":         0.60,
        "user_imp_nomada":        0.10,
    }
    print("=== PERFIL: Deportista kite/surf ===")
    print(ranker.rank(perfil_kite, top_n=5).to_string(index=False))
