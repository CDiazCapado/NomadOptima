"""
app/city_carousel.py — Carrusel de fotos por ciudad

Carga automáticamente las imágenes de app/assets/cities/{city_key}/
y las muestra con streamlit-image-carousel.

Si la carpeta no tiene fotos (solo el .txt placeholder), muestra
un mensaje informativo en lugar de fallar.

Uso:
    from app.city_carousel import render_city_carousel
    render_city_carousel("malaga")
"""

from pathlib import Path
from streamlit_image_carousel import image_carousel

# Ruta base de assets
ASSETS_DIR = Path(__file__).parent / "assets" / "cities"

# Extensiones de imagen aceptadas
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Clave interna → nombre de carpeta
CITY_FOLDER = {
    "Malaga":   "malaga",
    "Paris":    "paris",
    "Valencia": "valencia",
    "Porto":    "porto",
    "Bordeaux": "bordeaux",
}

# Foto sugerida por ciudad (se muestra cuando no hay imágenes reales)
CITY_PLACEHOLDER_HINT = {
    "Malaga":   "📷 Sugerencia: La Alcazaba con el puerto al fondo",
    "Paris":    "📷 Sugerencia: Los quais del Sena al atardecer",
    "Valencia": "📷 Sugerencia: La Ciudad de las Artes y las Ciencias de noche",
    "Porto":    "📷 Sugerencia: El Puente Dom Luís con el Duero",
    "Bordeaux": "📷 Sugerencia: La Place de la Bourse en el Miroir d'eau",
}


def get_city_images(city_key: str) -> list[Path]:
    """
    Devuelve la lista de imágenes disponibles para una ciudad.

    Busca en app/assets/cities/{city_folder}/ todos los archivos
    con extensión de imagen, ordenados por nombre.

    Args:
        city_key: nombre interno de la ciudad (ej. "Malaga")

    Returns:
        Lista de Path a las imágenes encontradas (vacía si no hay ninguna)
    """
    folder_name = CITY_FOLDER.get(city_key, city_key.lower())
    folder = ASSETS_DIR / folder_name

    if not folder.exists():
        return []

    images = sorted([
        f for f in folder.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    ])
    return images


def render_city_carousel(city_key: str) -> None:
    """
    Renderiza el carrusel de fotos de una ciudad en Streamlit.

    Si hay imágenes en app/assets/cities/{city}/: las muestra en carrusel.
    Si no hay imágenes: muestra un placeholder con la foto sugerida.

    Args:
        city_key: nombre interno de la ciudad (ej. "Malaga", "Paris"...)
    """
    import streamlit as st

    images = get_city_images(city_key)

    if not images:
        # Sin fotos todavía — placeholder informativo
        hint = CITY_PLACEHOLDER_HINT.get(city_key, "📷 Añade fotos en app/assets/cities/")
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea22, #764ba222);
                border: 2px dashed #667eea55;
                border-radius: 12px;
                padding: 2rem;
                text-align: center;
                color: #888;
                font-size: 0.9rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏙️</div>
                <div>{hint}</div>
                <div style="font-size: 0.75rem; margin-top: 0.5rem;">
                    Añade fotos en <code>app/assets/cities/{CITY_FOLDER.get(city_key, '')}/</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Con fotos — carrusel dinámico
    # streamlit-image-carousel espera una lista de dicts con clave "img"
    items = [{"img": str(img)} for img in images]

    image_carousel(
        items=items,
        width=700,
    )
