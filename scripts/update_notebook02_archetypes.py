"""
Actualiza la celda 57fea91a del notebook 02_synthetic_profiles_v3.ipynb
con las definiciones de arquetipos v2 (ajustes 10/04/2026).

Ejecutar desde la raíz del proyecto con el entorno virtual activado.
"""
import json
from pathlib import Path

NOTEBOOK_PATH = Path("notebooks/02_synthetic_profiles_v3.ipynb")

# Nuevas definiciones de arquetipos v2 — ajustados para mejorar diferenciación
NEW_ARCHETYPES_SOURCE = '''# ============================================================
# ARQUETIPOS DE USUARIO — v2 (10/04/2026)
# 21 arquetipos × dimensiones HIGH / MEDIUM (resto = LOW automático)
# Escalado proporcional: suma = 86% (14% perfiles mixtos)
# ============================================================

ARCHETYPES = [
    {
        "name": "kite_surf",
        "pct": 0.0487,
        "high": ["user_imp_deporte_agua", "user_imp_naturaleza", "user_imp_clima"],
        "medium": ["user_imp_autenticidad", "user_imp_coste", "user_imp_movilidad", "user_imp_social_media", "user_imp_deporte_urbano"]
    },
    {
        "name": "deportista_outdoor",
        "pct": 0.0487,
        "high": ["user_imp_naturaleza", "user_imp_deporte_montana", "user_imp_deporte_urbano", "user_imp_clima"],
        "medium": ["user_imp_gastronomia", "user_imp_bienestar", "user_imp_autenticidad", "user_imp_movilidad", "user_imp_salud", "user_imp_deporte_agua"]
    },
    {
        "name": "ski_nieve",
        "pct": 0.0325,
        "high": ["user_imp_deporte_montana", "user_imp_naturaleza"],
        "medium": ["user_imp_gastronomia", "user_imp_bienestar", "user_imp_autenticidad", "user_imp_calidad_vida", "user_imp_deporte_urbano", "user_imp_alojamiento", "user_imp_clima"]
    },
    {
        "name": "nomada_barato",
        "pct": 0.0649,
        "high": ["user_imp_nomada", "user_imp_coste", "user_imp_calidad_vida"],
        "medium": ["user_imp_gastronomia", "user_imp_movilidad", "user_imp_autenticidad", "user_imp_vida_nocturna", "user_imp_comunidad", "user_imp_alojamiento"]
    },
    {
        "name": "nomada_premium",
        "pct": 0.0487,
        "high": ["user_imp_nomada", "user_imp_calidad_vida", "user_imp_gastronomia", "user_imp_deporte_urbano", "user_imp_alojamiento"],
        "medium": ["user_imp_movilidad", "user_imp_vida_nocturna", "user_imp_bienestar", "user_imp_cultura"]
    },
    {
        "name": "nomada_mujer_activa",
        "pct": 0.0406,
        "high": ["user_imp_nomada", "user_imp_bienestar", "user_imp_deporte_urbano", "user_imp_comunidad"],
        "medium": ["user_imp_gastronomia", "user_imp_cultura", "user_imp_salud", "user_imp_movilidad", "user_imp_vida_nocturna", "user_imp_calidad_vida"]
    },
    {
        "name": "cultura_arte",
        "pct": 0.0568,
        "high": ["user_imp_cultura", "user_imp_arte_visual", "user_imp_turismo"],
        "medium": ["user_imp_gastronomia", "user_imp_movilidad", "user_imp_calidad_vida", "user_imp_vida_nocturna", "user_imp_musica", "user_imp_autenticidad"]
    },
    {
        "name": "musico_festivales",
        "pct": 0.0325,
        "high": ["user_imp_musica", "user_imp_cultura", "user_imp_vida_nocturna", "user_imp_comunidad"],
        "medium": ["user_imp_gastronomia", "user_imp_turismo", "user_imp_movilidad", "user_imp_autenticidad", "user_imp_arte_visual"]
    },
    {
        "name": "gastronomia_vino",
        "pct": 0.0406,
        "high": ["user_imp_gastronomia", "user_imp_autenticidad", "user_imp_turismo"],
        "medium": ["user_imp_vida_nocturna", "user_imp_calidad_vida", "user_imp_movilidad", "user_imp_musica"]
    },
    {
        "name": "antitur",
        "pct": 0.0406,
        "high": ["user_imp_autenticidad", "user_imp_gastronomia", "user_imp_naturaleza"],
        "medium": ["user_imp_cultura", "user_imp_movilidad", "user_imp_comunidad", "user_imp_calidad_vida", "user_imp_turismo"]
    },
    {
        "name": "influencer",
        "pct": 0.0325,
        "high": ["user_imp_social_media", "user_imp_turismo", "user_imp_vida_nocturna", "user_imp_gastronomia", "user_imp_arte_visual"],
        "medium": ["user_imp_deporte_agua", "user_imp_cultura", "user_imp_movilidad", "user_imp_autenticidad"]
    },
    {
        "name": "familia_bebe",
        "pct": 0.0325,
        "high": ["user_imp_familia", "user_imp_salud", "user_imp_movilidad", "user_imp_calidad_vida", "user_imp_alojamiento"],
        "medium": ["user_imp_gastronomia", "user_imp_compras", "user_imp_servicios", "user_imp_clima", "user_imp_bienestar"]
    },
    {
        "name": "familia_ninos",
        "pct": 0.0487,
        "high": ["user_imp_familia", "user_imp_educacion", "user_imp_salud", "user_imp_movilidad", "user_imp_calidad_vida"],
        "medium": ["user_imp_compras", "user_imp_servicios", "user_imp_bienestar", "user_imp_clima", "user_imp_turismo", "user_imp_comunidad", "user_imp_alojamiento"]
    },
    {
        "name": "fiesta_social",
        "pct": 0.0406,
        "high": ["user_imp_vida_nocturna", "user_imp_musica", "user_imp_social_media", "user_imp_gastronomia"],
        "medium": ["user_imp_bienestar", "user_imp_comunidad", "user_imp_autenticidad", "user_imp_deporte_agua"]
    },
    {
        "name": "bienestar_retiro",
        "pct": 0.0406,
        "high": ["user_imp_bienestar", "user_imp_naturaleza", "user_imp_clima", "user_imp_calidad_vida"],
        "medium": ["user_imp_deporte_urbano", "user_imp_autenticidad", "user_imp_salud"]
    },
    {
        "name": "jubilado_activo",
        "pct": 0.0487,
        "high": ["user_imp_clima", "user_imp_calidad_vida", "user_imp_salud", "user_imp_bienestar", "user_imp_gastronomia", "user_imp_movilidad"],
        "medium": ["user_imp_turismo", "user_imp_compras", "user_imp_naturaleza", "user_imp_comunidad", "user_imp_autenticidad"]
    },
    {
        "name": "senior_accesibilidad",
        "pct": 0.0243,
        "high": ["user_imp_salud", "user_imp_calidad_vida", "user_imp_servicios", "user_imp_movilidad", "user_imp_clima"],
        "medium": ["user_imp_gastronomia", "user_imp_compras", "user_imp_bienestar", "user_imp_comunidad"]
    },
    {
        "name": "mochilero_barato",
        "pct": 0.0406,
        "high": ["user_imp_coste", "user_imp_autenticidad", "user_imp_naturaleza", "user_imp_movilidad"],
        "medium": ["user_imp_cultura", "user_imp_gastronomia", "user_imp_vida_nocturna", "user_imp_comunidad", "user_imp_turismo"]
    },
    {
        "name": "cosmopolita_urbano",
        "pct": 0.0406,
        "high": ["user_imp_cultura", "user_imp_gastronomia", "user_imp_movilidad", "user_imp_calidad_vida"],
        "medium": ["user_imp_vida_nocturna", "user_imp_turismo", "user_imp_compras", "user_imp_arte_visual", "user_imp_bienestar", "user_imp_comunidad"]
    },
    {
        "name": "gamer_nomada_tech",
        "pct": 0.0325,
        "high": ["user_imp_nomada", "user_imp_calidad_vida", "user_imp_comunidad"],
        "medium": ["user_imp_vida_nocturna", "user_imp_cultura", "user_imp_movilidad"]
    },
    {
        "name": "mascotas_naturaleza",
        "pct": 0.0243,
        "high": ["user_imp_mascotas", "user_imp_naturaleza", "user_imp_bienestar", "user_imp_calidad_vida"],
        "medium": ["user_imp_movilidad", "user_imp_autenticidad", "user_imp_clima", "user_imp_gastronomia"]
    },
]

print(f"OK {len(ARCHETYPES)} arquetipos cargados")
print(f"   Suma porcentajes: {sum(a['pct'] for a in ARCHETYPES):.1%}")
'''

def update_cell(notebook_path: Path, cell_id: str, new_source: str) -> None:
    """Reemplaza el source de una celda por su id."""
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    found = False
    for cell in nb["cells"]:
        if cell.get("id") == cell_id:
            # Guardar source como lista de líneas (formato nbformat)
            lines = new_source.splitlines(keepends=True)
            cell["source"] = lines
            # Limpiar outputs anteriores
            cell["outputs"] = []
            cell["execution_count"] = None
            found = True
            print(f"OK Celda '{cell_id}' actualizada ({len(lines)} lineas)")
            break

    if not found:
        raise ValueError(f"Celda '{cell_id}' no encontrada en el notebook")

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"OK Notebook guardado: {notebook_path}")


if __name__ == "__main__":
    update_cell(NOTEBOOK_PATH, "57fea91a", NEW_ARCHETYPES_SOURCE)
