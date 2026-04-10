"""
NomadOptima — Capa 4: NomadRanker v3 (produccion)
src/models/ranker.py

Wrapper que encapsula las capas del sistema de recomendacion:
  Capa 1: CityFeatureBuilder -> cosine_sim entre perfil y ciudad (feature)
  Capa 4: LightGBM LambdaMART -> ranking final con 175 features
  Pre-filtros: restricciones duras antes de puntuar

Cambios v3 vs v2:
  - Usa model_v3 (lgbm_ranker_v3.txt + feature_builder_v3.joblib)
  - 175 features: user_imp_*(26) + city_*(148) + cosine_sim(1)
  - Sin user_clusterer/city_clusterer (Capa 3 simplificada con 54 ciudades)
  - Labels generados con producto escalar directo (no cosine_sim circular)
  - NDCG@5 = 0.9631 en validacion

Uso tipico:
    from src.models.ranker import NomadRanker

    ranker = NomadRanker()
    results = ranker.rank(user_profile, top_n=5)
    # -> pd.DataFrame con rank, city_key, display_name, score, cosine_sim

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
    presupuesto_max (float, euros/mes), temp_min_c (float)
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

from src.processing.features import CityFeatureBuilder

# Rutas por defecto
MODEL_DIR = ROOT / "data" / "processed" / "model_v3"
CITY_FEATURES_CSV = ROOT / "data" / "processed" / "city_features.csv"

# Las 26 dimensiones de usuario con prefijo user_imp_
USER_IMPORTANCE_KEYS = [
    "user_imp_gastronomia", "user_imp_vida_nocturna", "user_imp_cultura",
    "user_imp_arte_visual", "user_imp_naturaleza", "user_imp_deporte_agua",
    "user_imp_deporte_montana", "user_imp_deporte_urbano", "user_imp_bienestar",
    "user_imp_familia", "user_imp_mascotas", "user_imp_nomada", "user_imp_alojamiento",
    "user_imp_movilidad", "user_imp_compras", "user_imp_servicios", "user_imp_salud",
    "user_imp_turismo", "user_imp_educacion", "user_imp_comunidad", "user_imp_coste",
    "user_imp_clima", "user_imp_calidad_vida", "user_imp_social_media",
    "user_imp_musica", "user_imp_autenticidad",
]


class NomadRanker:
    """
    Wrapper de produccion sobre el modelo LightGBM v3 de NomadOptima.

    Carga los 3 artefactos del model_v3 y expone el metodo rank()
    que produce el ranking de ciudades para un perfil de usuario.

    El modelo usa 175 features:
      - 26 importancias de usuario (user_imp_*)
      - 148 features de ciudad (city_*)
      - 1 cosine_sim (baseline de Capa 1, como feature para LightGBM)

    Parametros
    ----------
    model_dir : Path, opcional
        Directorio con los artefactos del model_v3.
        Por defecto: data/processed/model_v3/
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
        "Lisboa":                "Lisboa",
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
        "Atenas":                "Atenas",
        "Reykjavik":             "Reykjavik",
        "Tbilisi":               "Tbilisi",
        "Andorra":               "Andorra la Vella",
        "Medellin":              "Medellin",
        "Mexico_City":           "Ciudad de Mexico",
        "Cartagena":             "Cartagena de Indias",
        "Bali":                  "Bali",
        "Bangkok":               "Bangkok",
        "Bogota":                "Bogota",
        "Buenos_Aires":          "Buenos Aires",
        "Chamonix":              "Chamonix",
        "Chiang_Mai":            "Chiang Mai",
        "Dakhla":                "Dakhla",
        "Dubai":                 "Dubai",
        "Dublin":                "Dublin",
        "Essaouira":             "Essaouira",
        "Innsbruck":             "Innsbruck",
        "Kuala_Lumpur":          "Kuala Lumpur",
        "Las_Palmas":            "Las Palmas de Gran Canaria",
        "Lima":                  "Lima",
        "Marrakech":             "Marrakech",
        "Montevideo":            "Montevideo",
        "Munich":                "Munich",
        "Napoles":               "Napoles",
        "Playa_Del_Carmen":      "Playa del Carmen",
        "Roma":                  "Roma",
        "Santiago":              "Santiago de Chile",
        "Vienna":                "Viena",
        "Warsaw":                "Varsovia",
    }

    def __init__(self, model_dir: Optional[Path] = None):
        """
        Inicializa el ranker cargando los 3 artefactos del model_v3.

        Lanza FileNotFoundError si los artefactos no existen todavia.
        Para generarlos, ejecuta notebooks/03_train_model.ipynb primero.
        """
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR

        self.lgbm_model      = None
        self.feature_builder = None
        self.feature_cols    = None
        self.city_df         = None

        self._load_artifacts()
        self._build_city_df()

    # ──────────────────────────────────────────────────────────────────────────
    # Carga de artefactos
    # ──────────────────────────────────────────────────────────────────────────

    def _load_artifacts(self):
        """
        Carga los 3 artefactos del model_v3 desde disco.

        Artefactos generados por notebooks/03_train_model.ipynb:
          - lgbm_ranker_v3.txt         : modelo LightGBM serializado
          - feature_builder_v3.joblib  : CityFeatureBuilder ajustado con 54 ciudades
          - feature_cols_v3.json       : orden exacto de las 175 features del training
        """
        files = {
            "lgbm":       self.model_dir / "lgbm_ranker_v3.txt",
            "feat_build": self.model_dir / "feature_builder_v3.joblib",
            "feat_cols":  self.model_dir / "feature_cols_v3.json",
        }
        for name, p in files.items():
            if not p.exists():
                raise FileNotFoundError(
                    f"Artefacto no encontrado: {p}\n"
                    "Ejecuta primero notebooks/03_train_model.ipynb"
                )

        self.lgbm_model      = lgb.Booster(model_file=str(files["lgbm"]))
        self.feature_builder = joblib.load(files["feat_build"])

        with open(files["feat_cols"], "r", encoding="utf-8") as f:
            self.feature_cols = json.load(f)

        print(f"[NomadRanker v3] Artefactos cargados desde {self.model_dir.name}/")
        print(f"  LightGBM: {self.lgbm_model.num_trees()} arboles")
        print(f"  Features: {len(self.feature_cols)} "
              f"({len([c for c in self.feature_cols if c.startswith('user_imp_')])} usuario + "
              f"{len([c for c in self.feature_cols if c.startswith('city_')])} ciudad + cosine_sim)")

    # ──────────────────────────────────────────────────────────────────────────
    # Construccion del DataFrame de ciudades
    # ──────────────────────────────────────────────────────────────────────────

    def _build_city_df(self):
        """
        Carga y cachea el DataFrame de features de todas las ciudades.

        city_features.csv contiene las 148 features (city_*) normalizadas
        generadas por CityFeatureBuilder durante el entrenamiento.
        """
        if not CITY_FEATURES_CSV.exists():
            raise FileNotFoundError(
                f"No encontrado: {CITY_FEATURES_CSV}\n"
                "Ejecuta primero notebooks/03_train_model.ipynb"
            )
        self.city_df = pd.read_csv(CITY_FEATURES_CSV, index_col=0)
        print(f"[NomadRanker v3] city_df: {len(self.city_df)} ciudades x "
              f"{len(self.city_df.columns)} features")

    # ──────────────────────────────────────────────────────────────────────────
    # Pre-filtros duros
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_hard_filters(self, user_profile: dict, cities: list) -> list:
        """
        Elimina ciudades incompatibles con el perfil ANTES de puntuar.

        Restricciones:
        - Presupuesto: city_coste_vida_estimado > presupuesto_max * 1.15 -> eliminada
        - Temperatura: city_temp_media_norm demasiado fria (relativo) -> eliminada
        - Coworking: si el usuario lo necesita y la ciudad tiene 0 -> eliminada

        Si todos los candidatos son eliminados, devuelve todas (sin filtrar).
        """
        presupuesto_max = user_profile.get("presupuesto_max", 9999)
        necesita_cowork = bool(user_profile.get("necesita_coworking", False))

        candidatos = []
        for city in cities:
            if city not in self.city_df.index:
                continue
            row = self.city_df.loc[city]

            # Presupuesto
            coste = row.get("city_coste_vida_estimado", 0)
            if coste > 0 and coste > presupuesto_max * 1.15:
                continue

            # Coworking
            if necesita_cowork:
                cow_cols = ["city_gp_coworking", "city_coworking_osm"]
                cow_val  = max([row.get(c, 0) for c in cow_cols if c in row.index] or [0])
                if cow_val == 0:
                    continue

            candidatos.append(city)

        return candidatos if candidatos else cities

    # ──────────────────────────────────────────────────────────────────────────
    # Metodo principal: rank()
    # ──────────────────────────────────────────────────────────────────────────

    def rank(
        self,
        user_profile: dict,
        top_n: int = 5,
        apply_filters: bool = True,
        candidate_cities: Optional[list] = None,
    ) -> pd.DataFrame:
        """
        Produce el ranking de ciudades para un perfil de usuario.

        Flujo:
          1. Aplicar pre-filtros duros (elimina incompatibles)
          2. Cosine similarity perfil <-> ciudad (Capa 1 — como feature)
          3. Construir matrix de 175 features en el orden exacto del training
          4. Predecir con LightGBM LambdaMART (Capa 4)
          5. Ordenar y retornar top_n ciudades

        Parametros
        ----------
        user_profile : dict
            Preferencias del usuario. Claves: user_imp_* (0.0-1.0).
        top_n : int
            Numero de ciudades a retornar (0 = todas).
        apply_filters : bool
            Si True, aplica pre-filtros duros antes de puntuar.
        candidate_cities : list, opcional
            Subconjunto de ciudades a rankear. Si None, usa todas.

        Retorna
        -------
        pd.DataFrame con columnas:
            rank, city_key, display_name, score, cosine_sim
        """
        # 1. Candidatos
        all_cities = (
            candidate_cities
            if candidate_cities is not None
            else self.city_df.index.tolist()
        )
        # Solo ciudades que existen en city_df
        all_cities = [c for c in all_cities if c in self.city_df.index]

        candidates = (
            self._apply_hard_filters(user_profile, all_cities)
            if apply_filters else all_cities
        )

        cand_df = self.city_df.loc[candidates].copy()

        # 2. Cosine similarity (Capa 1 — como feature para LightGBM)
        city_num_cols = [c for c in self.feature_builder.city_features
                         if c in cand_df.columns]
        cosine_scores = self.feature_builder.cosine_scores(
            user_profile, cand_df[city_num_cols]
        )
        cand_df["cosine_sim"] = cosine_scores.values

        # 3. Construir matrix de features en el orden exacto del training
        # user_imp_* tienen el mismo valor para todas las filas (mismo usuario)
        for feat in USER_IMPORTANCE_KEYS:
            cand_df[feat] = float(user_profile.get(feat, 0.05))

        # Rellenar columnas que faltan con 0
        missing_cols = [c for c in self.feature_cols if c not in cand_df.columns]
        for c in missing_cols:
            cand_df[c] = 0.0

        X = cand_df[self.feature_cols].astype(float).values

        # 4. Prediccion LightGBM (Capa 4)
        scores = self.lgbm_model.predict(X)
        cand_df["score"] = scores

        # 5. Ordenar y formatear resultado
        result = (
            cand_df
            .sort_values("score", ascending=False)
            .reset_index()
        )
        # El indice se llama "city" en city_features.csv
        idx_col = result.columns[0]  # primer columna tras reset_index = el indice
        if idx_col != "city_key":
            result = result.rename(columns={idx_col: "city_key"})

        if top_n > 0:
            result = result.head(top_n)

        result["rank"] = range(1, len(result) + 1)
        result["display_name"] = result["city_key"].map(
            lambda k: self.DISPLAY_NAMES.get(k, k)
        )

        return result[["rank", "city_key", "display_name", "score", "cosine_sim"]]

    def scores_series(
        self,
        user_profile: dict,
        candidate_cities: Optional[list] = None,
        apply_filters: bool = False,
    ) -> pd.Series:
        """
        Devuelve los scores como pd.Series(score, index=city_key).

        Util para integracion directa con la logica de filtrado de streamlit_app.py.
        """
        result = self.rank(
            user_profile,
            top_n=0,
            apply_filters=apply_filters,
            candidate_cities=candidate_cities,
        )
        return pd.Series(result["score"].values, index=result["city_key"].values)

    def explain(self, user_profile: dict, city_key: str, top_n: int = 5) -> list:
        """
        Devuelve las dimensiones que mas contribuyen al score de una ciudad.
        Util para mostrar la explicacion en Streamlit.

        Returns:
            list de (dimension_name, contribucion 0-1)
        """
        city_num_cols = [c for c in self.feature_builder.city_features
                         if c in self.city_df.columns]
        return self.feature_builder.top_features_for_city(
            user_profile, city_key, self.city_df[city_num_cols], top_n=top_n
        )


# ── CLI rapido para probar el ranker ─────────────────────────────────────────
if __name__ == "__main__":
    print("Cargando NomadRanker v3...")
    try:
        ranker = NomadRanker()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        import sys
        sys.exit(1)

    print("Artefactos cargados.\n")

    # Perfil: nomada digital
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

    # Perfil: deportista kite
    perfil_kite = {
        "user_imp_deporte_agua":  0.99,
        "user_imp_naturaleza":    0.90,
        "user_imp_clima":         0.85,
        "user_imp_coste":         0.60,
        "user_imp_nomada":        0.10,
    }
    print("=== PERFIL: Deportista kite/surf ===")
    print(ranker.rank(perfil_kite, top_n=5).to_string(index=False))
