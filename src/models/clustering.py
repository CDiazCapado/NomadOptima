"""
NomadOptima — Capas 2 y 3: User Clustering + City Clustering
src/models/clustering.py

=============================================================
QUE HACEN ESTAS DOS CAPAS?
=============================================================

CAPA 2 - User Clustering
    Agrupa los 5.000 perfiles de usuario en arquetipos automaticos.
    Si dos usuarios tienen preferencias similares -> mismo cluster.
    Asi el modelo aprende que "los nomadas digitales siempre prefieren
    ciudades con coworking barato" -> generaliza mejor.

    Pipeline: PCA -> UMAP -> HDBSCAN

    Por que 3 algoritmos encadenados y no uno solo?
    Los 26 features de usuario tienen dimensiones mixtas y relaciones
    no lineales. PCA los preprocesa, UMAP captura la geometria no lineal,
    HDBSCAN encuentra los clusters sin asumir su forma ni numero.

CAPA 3 - City Clustering (automatico, UMAP+HDBSCAN)
    Con 42 ciudades ya podemos usar clustering automatico.
    El pipeline es identico al de usuarios pero sobre las features
    de ciudad: clima, coste, naturaleza, coworking, ocio, etc.
    Los clusters emergen de los datos, no los definimos a mano.

    Ejemplos de clusters esperados:
        "costa_kite_atlantica"    -> Tarifa, Fuerteventura, Essaouira
        "metropoli_cosmopolita"   -> Paris, Amsterdam, Berlin, Vienna
        "ciudad_media_cultural"   -> Granada, Porto, Krakow, Ljubljana
        "destino_barato_digital"  -> Tbilisi, Sofia, Bucharest, Belgrade

FEATURE CLAVE: afinidad_uc_cc
    La interaccion entre cluster de usuario y cluster de ciudad es
    potencialmente la feature mas potente del modelo:
    "los nomadas digitales prefieren ciudades de bajo coste con coworking"
    Esta afinidad se aprende de los datos, no se hardcodea.

=============================================================
OUTPUTS QUE GENERA ESTA CAPA (features para LightGBM)
=============================================================
    user_cluster_id        -> que cluster de usuario pertenece este perfil
    user_cluster_strength  -> que tan central esta en su cluster (0-1)
    city_cluster_id        -> que cluster de ciudad pertenece esta ciudad
    city_cluster_strength  -> que tan representativa es del cluster (0-1)
    afinidad_uc_cc         -> afinidad entre user_cluster y city_cluster (0-1)
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import umap
import hdbscan
import warnings
warnings.filterwarnings("ignore")


# ── FEATURES DE USUARIO PARA CLUSTERING (26 dimensiones) ─────────────────────
# Son exactamente las 26 importancias del formulario de usuario.
# No incluimos query_id ni label — son metadatos, no preferencias.
USER_CLUSTER_FEATURES = [
    "user_imp_gastronomia",
    "user_imp_vida_nocturna",
    "user_imp_cultura",
    "user_imp_arte_visual",
    "user_imp_naturaleza",
    "user_imp_deporte_agua",
    "user_imp_deporte_montana",
    "user_imp_deporte_urbano",
    "user_imp_bienestar",
    "user_imp_familia",
    "user_imp_mascotas",
    "user_imp_nomada",
    "user_imp_alojamiento",
    "user_imp_movilidad",
    "user_imp_compras",
    "user_imp_servicios",
    "user_imp_salud",
    "user_imp_turismo",
    "user_imp_educacion",
    "user_imp_comunidad",
    "user_imp_coste",
    "user_imp_clima",
    "user_imp_calidad_vida",
    "user_imp_social_media",
    "user_imp_musica",
    "user_imp_autenticidad",
]

# ── FEATURES DE CIUDAD PARA CLUSTERING ───────────────────────────────────────
# Usamos un subconjunto representativo de las 136 features.
# No incluimos todas para evitar el "curse of dimensionality" en UMAP.
# Elegimos las mas discriminativas entre ciudades.
CITY_CLUSTER_FEATURES = [
    # Coste de vida
    "feat_city_city_alquiler_1br_centro",
    "feat_city_city_coste_vida_estimado",
    "feat_city_city_coste_invertido",
    # Clima
    "feat_city_city_temp_media_anual",
    "feat_city_city_dias_sol_anual",
    "feat_city_city_temp_media_norm",
    "feat_city_city_dias_sol_norm",
    # Naturaleza y playa
    "feat_city_city_beaches",
    "feat_city_city_gp_beach",
    "feat_city_city_gp_hiking_area",
    "feat_city_city_gp_national_park",
    # Deportes de agua
    "feat_city_city_gp_surf_school",
    "feat_city_city_gp_kitesurfing",
    "feat_city_city_gp_windsurfing",
    "feat_city_city_gp_marina",
    # Deportes de montana
    "feat_city_city_gp_ski_resort",
    "feat_city_city_gp_climbing_gym",
    # Gastronomia y ocio
    "feat_city_city_restaurants",
    "feat_city_city_gp_fine_dining",
    "feat_city_city_gp_night_club",
    "feat_city_city_gp_bar",
    # Cultura
    "feat_city_city_gp_museum",
    "feat_city_city_gp_art_gallery",
    "feat_city_city_gp_performing_arts",
    # Nomada digital
    "feat_city_city_gp_coworking",
    "feat_city_city_internet_mbps",
    "feat_city_city_gp_coliving",
    # Bienestar
    "feat_city_city_gp_spa",
    "feat_city_city_gp_yoga_studio",
    "feat_city_city_gp_thermal_bath",
    # Familia
    "feat_city_city_schools",
    "feat_city_city_playgrounds",
    "feat_city_city_gp_international_school",
    # Calidad de vida
    "feat_city_city_quality_of_life",
    "feat_city_city_hospitals",
    "feat_city_city_public_transport",
    # Pais
    "feat_city_city_schengen",
    "feat_city_city_moneda_eur",
]


class UserClusterer:
    """
    Agrupa perfiles de usuario en clusters usando PCA -> UMAP -> HDBSCAN.

    Cada cluster representa un arquetipo de usuario con comportamiento
    similar de cara a la recomendacion de ciudad.

    Pipeline detallado:
    +------------------------------------------------------------------+
    | 1. StandardScaler: estandariza cada feature a media=0, std=1    |
    |    Por que: todas las importancias estan en [0,1] pero con       |
    |    distribuciones muy distintas. Estandarizar iguala su peso.   |
    |                                                                  |
    | 2. PCA (n_components=15): reduce de 26 a 15 dimensiones          |
    |    Por que: UMAP funciona mejor con menos dimensiones y menos    |
    |    ruido. Mantenemos ~95% de la varianza explicada.              |
    |                                                                  |
    | 3. UMAP (n_components=2): proyeccion no lineal a 2D              |
    |    Por que: captura relaciones no lineales que PCA no puede.     |
    |    El resultado es un mapa 2D donde usuarios similares           |
    |    quedan cerca en el espacio.                                   |
    |                                                                  |
    | 4. HDBSCAN: clustering de densidad sobre el mapa 2D              |
    |    Por que: no requiere especificar el numero de clusters.       |
    |    Los clusters emergen de la geometria de los datos.            |
    |    Los puntos en regiones de baja densidad -> cluster -1         |
    |    (ruido/outliers). Los asignamos al cluster mas cercano.       |
    +------------------------------------------------------------------+
    """

    def __init__(self,
                 n_pca_components: int = 15,
                 umap_n_neighbors: int = 30,
                 umap_min_dist: float = 0.1,
                 hdbscan_min_cluster_size: int = 150,
                 random_state: int = 42):
        """
        Args:
            n_pca_components:         numero de componentes PCA (recomendado: 10-20)
            umap_n_neighbors:         vecinos para UMAP (mayor = estructura global)
            umap_min_dist:            distancia minima entre puntos en embedding
            hdbscan_min_cluster_size: minimo puntos para ser cluster (mayor = menos clusters)
            random_state:             semilla para reproducibilidad
        """
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_pca_components, random_state=random_state)
        self.umap_model = umap.UMAP(
            n_components=2,
            n_neighbors=umap_n_neighbors,
            min_dist=umap_min_dist,
            random_state=random_state,
            verbose=False
        )
        self.hdbscan_model = hdbscan.HDBSCAN(
            min_cluster_size=hdbscan_min_cluster_size,
            prediction_data=True  # necesario para predecir nuevos puntos
        )
        self.n_clusters = None
        self.centroids_2d = None   # centros de cada cluster en el espacio UMAP 2D
        self.fitted = False
        self._X_umap_train = None
        self._labels_train = None
        self._query_ids = None

    def fit(self, df: pd.DataFrame) -> "UserClusterer":
        """
        Entrena el pipeline PCA -> UMAP -> HDBSCAN sobre perfiles de usuario.

        IMPORTANTE: usamos perfiles unicos (query_id unicos), no las 210.000
        filas del training_dataset. Cada perfil aparece 42 veces (una por
        ciudad) — necesitamos solo una instancia de cada perfil.

        Args:
            df: training_dataset.csv completo

        Returns:
            self (encadenable)
        """
        # Perfiles unicos: un perfil por usuario
        avail_features = [f for f in USER_CLUSTER_FEATURES if f in df.columns]
        df_users = df.drop_duplicates(subset="query_id")[avail_features].copy()
        print(f"[UserClusterer] Entrenando sobre {len(df_users):,} perfiles unicos "
              f"con {len(avail_features)} features...")

        # Paso 1: Estandarizacion
        X_scaled = self.scaler.fit_transform(df_users)
        print(f"  [OK] StandardScaler: media~0, std~1")

        # Paso 2: PCA
        X_pca = self.pca.fit_transform(X_scaled)
        var_explained = self.pca.explained_variance_ratio_.sum()
        print(f"  [OK] PCA: {X_scaled.shape[1]}D -> {X_pca.shape[1]}D "
              f"({var_explained:.1%} varianza explicada)")

        # Paso 3: UMAP — proyeccion a 2D (puede tardar 1-3 min)
        print(f"  [..] UMAP: reduciendo a 2D (puede tardar 1-3 min)...")
        X_umap = self.umap_model.fit_transform(X_pca)
        print(f"  [OK] UMAP: {X_pca.shape[1]}D -> 2D")

        # Paso 4: HDBSCAN — clustering
        self.hdbscan_model.fit(X_umap)
        labels = self.hdbscan_model.labels_

        n_noise = (labels == -1).sum()
        self.n_clusters = len(set(labels) - {-1})
        print(f"  [OK] HDBSCAN: {self.n_clusters} clusters encontrados "
              f"({n_noise} outliers -> asignados al cluster mas cercano)")

        # Calcular centroides en espacio 2D (para medir cluster_strength)
        self.centroids_2d = {}
        for label in sorted(set(labels)):
            if label >= 0:
                mask = labels == label
                self.centroids_2d[label] = X_umap[mask].mean(axis=0)

        # Guardar para visualizacion posterior
        self._X_umap_train = X_umap
        self._labels_train = labels
        self._query_ids = df.drop_duplicates(subset="query_id")["query_id"].values
        self._avail_features = avail_features

        self.fitted = True
        print(f"  [OK] UserClusterer entrenado")
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Asigna cluster_id y cluster_strength a cada perfil del dataset.

        cluster_strength: que tan "central" esta el perfil dentro de su cluster.
        Se calcula como 1 / (1 + distancia_al_centroide_2d).
        Un perfil en el centro del cluster -> strength ~1.0
        Un perfil en el borde del cluster  -> strength ~0.3-0.5

        Args:
            df: DataFrame con columna query_id y las features USER_CLUSTER_FEATURES

        Returns:
            df con columnas adicionales: user_cluster_id, user_cluster_strength
        """
        assert self.fitted, "Llama a .fit() antes de .predict()"

        avail_features = self._avail_features
        df_users = df.drop_duplicates(subset="query_id")[["query_id"] + avail_features].copy()
        X_scaled = self.scaler.transform(df_users[avail_features])
        X_pca    = self.pca.transform(X_scaled)
        X_umap   = self.umap_model.transform(X_pca)

        # approximate_predict maneja puntos nuevos que no estaban en el training
        labels, probs = hdbscan.approximate_predict(self.hdbscan_model, X_umap)

        # Outliers (-1) -> asignar al cluster mas cercano como fallback
        noise_mask = labels == -1
        if noise_mask.any() and self.centroids_2d:
            for i in np.where(noise_mask)[0]:
                pt = X_umap[i]
                closest = min(self.centroids_2d,
                              key=lambda c: np.linalg.norm(pt - self.centroids_2d[c]))
                labels[i] = closest

        # cluster_strength = proximidad al centroide del cluster
        cluster_strength = np.zeros(len(labels))
        for i, (label, pt) in enumerate(zip(labels, X_umap)):
            if label in self.centroids_2d:
                dist = np.linalg.norm(pt - self.centroids_2d[label])
                cluster_strength[i] = 1.0 / (1.0 + dist)
            else:
                cluster_strength[i] = 0.5

        # Mapear de query_id a label/strength
        qid_to_cluster  = dict(zip(df_users["query_id"], labels))
        qid_to_strength = dict(zip(df_users["query_id"], cluster_strength))

        df = df.copy()
        df["user_cluster_id"]       = df["query_id"].map(qid_to_cluster).astype(int)
        df["user_cluster_strength"] = df["query_id"].map(qid_to_strength).round(4)

        n_clusters_found = df["user_cluster_id"].nunique()
        print(f"[UserClusterer.predict] {n_clusters_found} clusters asignados")
        for cid in sorted(df["user_cluster_id"].unique()):
            n = (df["user_cluster_id"] == cid).sum() // df["city"].nunique()
            print(f"  Cluster {cid}: {n:,} perfiles")

        return df

    @property
    def embeddings_2d(self):
        """Devuelve los embeddings UMAP 2D del training set para visualizacion."""
        assert self.fitted, "Llama a .fit() primero"
        return self._X_umap_train, self._labels_train


class CityClusterer:
    """
    Agrupa ciudades en clusters usando PCA -> UMAP -> HDBSCAN.

    Con 42 ciudades ya es posible usar clustering automatico.
    El pipeline es identico al de usuarios pero aplicado sobre las
    features de ciudad: clima, coste, naturaleza, coworking, ocio...

    Por que no manual como antes?
    Con 5 ciudades no tenia sentido — 5 puntos no forman clusters.
    Con 42 ciudades el algoritmo puede descubrir grupos reales:
    ciudades de kite atlantico, metropolis cosmopolitas, etc.
    """

    def __init__(self,
                 n_pca_components: int = 10,
                 umap_n_neighbors: int = 5,
                 umap_min_dist: float = 0.05,
                 hdbscan_min_cluster_size: int = 3,
                 random_state: int = 42):
        """
        Args:
            n_pca_components:         dimensiones PCA (menos que en usuario porque son 38 features)
            umap_n_neighbors:         vecinos UMAP (menos porque hay pocas ciudades: 42)
            umap_min_dist:            distancia minima (menor = clusters mas compactos)
            hdbscan_min_cluster_size: minimo 3 ciudades por cluster
            random_state:             semilla reproducibilidad
        """
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_pca_components, random_state=random_state)
        self.umap_model = umap.UMAP(
            n_components=2,
            n_neighbors=umap_n_neighbors,
            min_dist=umap_min_dist,
            random_state=random_state,
            verbose=False
        )
        self.hdbscan_model = hdbscan.HDBSCAN(
            min_cluster_size=hdbscan_min_cluster_size,
            prediction_data=True
        )
        self.n_clusters = None
        self.centroids_2d = None
        self.fitted = False
        self._city_labels = None   # dict: city_name -> cluster_id
        self._city_strengths = None
        self._X_umap_train = None
        self._avail_features = None

    def fit(self, df: pd.DataFrame) -> "CityClusterer":
        """
        Entrena el pipeline sobre las features de ciudad.

        IMPORTANTE: cada ciudad aparece 5.000 veces en el training_dataset
        (una por cada usuario). Usamos drop_duplicates('city') para tener
        una sola fila por ciudad con sus features reales.

        Args:
            df: training_dataset.csv completo con columnas feat_city_*

        Returns:
            self (encadenable)
        """
        avail_features = [f for f in CITY_CLUSTER_FEATURES if f in df.columns]
        df_cities = df.drop_duplicates(subset="city").set_index("city")[avail_features].copy()
        self._city_names = df_cities.index.tolist()
        self._avail_features = avail_features

        print(f"[CityClusterer] Entrenando sobre {len(df_cities)} ciudades "
              f"con {len(avail_features)} features...")

        # Rellenar NaN con 0 (ciudades sin datos de alguna feature)
        df_cities = df_cities.fillna(0)

        # Paso 1: Estandarizacion
        X_scaled = self.scaler.fit_transform(df_cities)
        print(f"  [OK] StandardScaler aplicado")

        # Paso 2: PCA
        n_comp = min(self.pca.n_components, len(df_cities) - 1, len(avail_features))
        self.pca.n_components = n_comp
        X_pca = self.pca.fit_transform(X_scaled)
        var_explained = self.pca.explained_variance_ratio_.sum()
        print(f"  [OK] PCA: {X_scaled.shape[1]}D -> {X_pca.shape[1]}D "
              f"({var_explained:.1%} varianza explicada)")

        # Paso 3: UMAP
        # Con pocas ciudades n_neighbors debe ser menor que n_ciudades
        n_neighbors = min(self.umap_model.n_neighbors, len(df_cities) - 1)
        self.umap_model.n_neighbors = n_neighbors
        print(f"  [..] UMAP con n_neighbors={n_neighbors}...")
        X_umap = self.umap_model.fit_transform(X_pca)
        print(f"  [OK] UMAP: {X_pca.shape[1]}D -> 2D")

        # Paso 4: HDBSCAN
        self.hdbscan_model.fit(X_umap)
        labels = self.hdbscan_model.labels_

        n_noise = (labels == -1).sum()
        self.n_clusters = len(set(labels) - {-1})
        print(f"  [OK] HDBSCAN: {self.n_clusters} clusters encontrados "
              f"({n_noise} ciudades como outliers)")

        # Centroides en 2D
        self.centroids_2d = {}
        for label in sorted(set(labels)):
            if label >= 0:
                mask = labels == label
                self.centroids_2d[label] = X_umap[mask].mean(axis=0)

        # Calcular strength para cada ciudad
        city_strengths = np.zeros(len(labels))
        for i, (label, pt) in enumerate(zip(labels, X_umap)):
            if label >= 0 and label in self.centroids_2d:
                dist = np.linalg.norm(pt - self.centroids_2d[label])
                city_strengths[i] = 1.0 / (1.0 + dist)
            else:
                # Outlier -> asignar al cluster mas cercano con strength baja
                if self.centroids_2d:
                    closest = min(self.centroids_2d,
                                  key=lambda c: np.linalg.norm(pt - self.centroids_2d[c]))
                    labels[i] = closest
                city_strengths[i] = 0.3

        self._city_labels   = dict(zip(self._city_names, labels))
        self._city_strengths = dict(zip(self._city_names, city_strengths))
        self._X_umap_train  = X_umap

        # Mostrar resultado por cluster
        cluster_contents = {}
        for city, cid in self._city_labels.items():
            cluster_contents.setdefault(cid, []).append(city)
        for cid in sorted(cluster_contents):
            print(f"  Cluster {cid}: {cluster_contents[cid]}")

        self.fitted = True
        self.n_clusters = len(self.centroids_2d)
        print(f"  [OK] CityClusterer entrenado ({self.n_clusters} clusters)")
        return self

    def fit_manual(self, manual_clusters: dict) -> "CityClusterer":
        """
        Asigna clusters de ciudad de forma manual en lugar de usar HDBSCAN.

        Usar cuando el clustering automático produce pocos grupos o grupos
        que no tienen sentido temático. El clustering manual es más explicable
        en una presentación: "Agrupamos las ciudades por perfil de usuario".

        Args:
            manual_clusters: dict {city_name: cluster_id (int)}
                Ejemplo: {"Malaga": 0, "Paris": 1, "Bali": 3, ...}

        Returns:
            self (encadenable)
        """
        self._city_labels    = {city: int(cid) for city, cid in manual_clusters.items()}
        self._city_strengths = {city: 1.0 for city in manual_clusters}
        self._city_names     = list(manual_clusters.keys())
        self.n_clusters      = len(set(manual_clusters.values()))

        # Centroides ficticios para compatibilidad (no se usan en predict manual)
        self.centroids_2d = {cid: np.array([float(cid), 0.0])
                             for cid in set(manual_clusters.values())}

        self.fitted = True

        cluster_contents = {}
        for city, cid in self._city_labels.items():
            cluster_contents.setdefault(cid, []).append(city)

        print(f"[CityClusterer] Modo manual: {self.n_clusters} clusters")
        for cid in sorted(cluster_contents):
            print(f"  Cluster {cid}: {sorted(cluster_contents[cid])}")

        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Asigna city_cluster_id y city_cluster_strength al dataset.

        Args:
            df: DataFrame con columna 'city'

        Returns:
            df con columnas: city_cluster_id, city_cluster_strength
        """
        assert self.fitted, "Llama a .fit() antes de .predict()"
        assert "city" in df.columns, "El DataFrame debe tener columna 'city'"

        df = df.copy()
        df["city_cluster_id"] = df["city"].map(
            lambda c: int(self._city_labels.get(c, -1))
        )
        df["city_cluster_strength"] = df["city"].map(
            lambda c: round(float(self._city_strengths.get(c, 0.5)), 4)
        )

        unknown = df[df["city_cluster_id"] == -1]["city"].unique()
        if len(unknown) > 0:
            print(f"[!] Ciudades sin cluster asignado: {list(unknown)}")

        return df

    def cluster_contents(self) -> dict:
        """Devuelve un dict cluster_id -> [lista de ciudades] para inspeccion."""
        assert self.fitted
        result = {}
        for city, cid in self._city_labels.items():
            result.setdefault(int(cid), []).append(city)
        return result

    @property
    def embeddings_2d(self):
        """Devuelve los embeddings UMAP 2D de ciudades para visualizacion."""
        assert self.fitted
        return self._X_umap_train, list(self._city_labels.values()), self._city_names


def compute_cluster_affinity(df: pd.DataFrame,
                              n_user_clusters: int,
                              n_city_clusters: int) -> pd.DataFrame:
    """
    Calcula la feature de afinidad entre cluster de usuario y cluster de ciudad.

    Esta es potencialmente la feature mas informativa para el modelo:
    captura el patron "usuarios del tipo X prefieren ciudades del tipo Y".

    Metodo:
        Para cada par (user_cluster, city_cluster), calculamos la relevancia
        media observada en el training set. Esa media es la "afinidad aprendida".
        Luego normalizamos a [0, 1].

    Ejemplo esperado:
        user_cluster=0 (nomadas) + city_cluster=0 (kite atlantico) -> alta afinidad
        user_cluster=0 (nomadas) + city_cluster=2 (metropoli cara) -> baja afinidad

    Args:
        df: training_dataset con columnas user_cluster_id, city_cluster_id, label
        n_user_clusters: numero de clusters de usuario
        n_city_clusters: numero de clusters de ciudad

    Returns:
        df con columna adicional 'afinidad_uc_cc' (0-1)
    """
    assert "user_cluster_id" in df.columns, "Ejecuta UserClusterer.predict() primero"
    assert "city_cluster_id" in df.columns, "Ejecuta CityClusterer.predict() primero"
    assert "label" in df.columns, "El DataFrame debe tener columna 'label'"

    # Tabla de afinidad: relevancia media por par (user_cluster, city_cluster)
    affinity_table = (
        df.groupby(["user_cluster_id", "city_cluster_id"])["label"]
          .mean()
          .unstack(fill_value=0)
    )

    # Normalizar a [0, 1]
    max_aff = affinity_table.values.max()
    if max_aff > 0:
        affinity_table = affinity_table / max_aff

    print("[compute_cluster_affinity] Tabla de afinidad (user_cluster x city_cluster):")
    print(affinity_table.round(3).to_string())
    print()

    # Mapear cada fila del dataset a su valor de afinidad
    def lookup_affinity(row):
        uc = row["user_cluster_id"]
        cc = row["city_cluster_id"]
        try:
            return float(affinity_table.loc[uc, cc])
        except KeyError:
            return 0.5

    df = df.copy()
    df["afinidad_uc_cc"] = df.apply(lookup_affinity, axis=1).round(4)

    print(f"[compute_cluster_affinity] Rango: "
          f"{df['afinidad_uc_cc'].min():.3f} - {df['afinidad_uc_cc'].max():.3f}")

    return df, affinity_table


def enrich_dataset(df: pd.DataFrame,
                   user_clusterer: UserClusterer,
                   city_clusterer: CityClusterer = None) -> tuple:
    """
    Enriquece el training_dataset con features de clustering.

    Flujo:
        1. Anade user_cluster_id + user_cluster_strength  (Capa 2 — siempre)
        2. Anade city_cluster_id + city_cluster_strength  (Capa 3 — opcional)
        3. Calcula afinidad_uc_cc entre ambos clusters    (solo si Capa 3 activa)

    DECISION MVP (09/04/2026):
        city_clusterer=None por defecto. Con 55 ciudades el Fuzzy C-Means
        no encuentra estructura util (FPC=0.03 con 30 clusters). La Cosine
        Similarity ya cubre la similitud ciudad-usuario con los 140 features
        reales. City clustering se recupera cuando haya 200+ ciudades.

    Args:
        df: training_dataset.csv
        user_clusterer: UserClusterer ya entrenado (.fit() ejecutado)
        city_clusterer: CityClusterer ya entrenado (opcional — None = sin Capa 3)

    Returns:
        (df_enriched, affinity_table) — affinity_table es None si no hay city clustering
    """
    print("=" * 55)
    print("ENRIQUECIENDO DATASET CON FEATURES DE CLUSTERING")
    print("=" * 55)

    # Capa 2: user clusters (siempre activa)
    df = user_clusterer.predict(df)
    print()

    affinity_table = None

    if city_clusterer is not None:
        # Capa 3: city clusters (opcional)
        df = city_clusterer.predict(df)
        print()

        # Interaccion: afinidad entre ambos clusters
        df, affinity_table = compute_cluster_affinity(
            df,
            n_user_clusters=user_clusterer.n_clusters,
            n_city_clusters=city_clusterer.n_clusters
        )
        print("Nuevas columnas: user_cluster_id, user_cluster_strength, "
              "city_cluster_id, city_cluster_strength, afinidad_uc_cc")
    else:
        print("[INFO] City clustering desactivado (MVP con 55 ciudades).")
        print("       La Cosine Similarity cubre la similitud ciudad-usuario.")
        print("Nuevas columnas: user_cluster_id, user_cluster_strength")

    print(f"\nDataset enriquecido: {df.shape[0]:,} filas x {df.shape[1]} columnas")

    return df, affinity_table
