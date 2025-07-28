import streamlit as st
import os
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---

st.set_page_config(
    page_title="Biblioteca de juegos",
    page_icon="🔖",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- CONSTANTES ---
DOCS_DIR = "documents"

# --- FUNCIONES AUXILIARES ---

def slugify(text: str) -> str:
    """
    Convierte una cadena de texto en un 'slug' amigable para URLs,
    replicando el comportamiento de anclaje automático de Streamlit.
    Ej: "1. Resumen del Juego" -> "1-resumen-del-juego"
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Elimina caracteres no alfanuméricos
    text = re.sub(r'[-\s]+', '-', text).strip('-') # Reemplaza espacios/guiones con un solo guión
    return text

def get_toc(markdown_content: str) -> list[dict]:
    """
    Extrae los encabezados de un texto Markdown para generar una tabla de contenidos.
    No modifica el contenido, solo lo analiza.
    """
    toc_items = []
    for line in markdown_content.split('\n'):
        match = re.match(r'^(#+)\s+(.*)', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            slug = slugify(title)
            toc_items.append({'level': level, 'title': title, 'slug': slug})
    return toc_items

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
# Se usa para rastrear qué documento está seleccionado.
if 'selected_doc' not in st.session_state:
    st.session_state.selected_doc = None

# --- FUNCIONES DE NAVEGACIÓN ---

def show_document_list():
    """Muestra la página de inicio con la lista de documentos."""
    st.title("📚 Listado de documentos de juego")
    st.write("Selecciona un documento de la lista para ver su contenido.")

    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        st.info(f"Se ha creado la carpeta '{DOCS_DIR}'. Añade tus archivos .md allí.")
        return

    doc_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]

    if not doc_files:
        st.warning(f"No se encontraron archivos `.md` en la carpeta `{DOCS_DIR}`.")
        return

    # Muestra un botón para cada documento. Al hacer clic, se actualiza el estado.
    for doc_file in sorted(doc_files):
        display_name = os.path.splitext(doc_file)[0].replace('_', ' ')
        if st.button(display_name, key=doc_file, use_container_width=True):
            st.session_state.selected_doc = doc_file
            st.rerun() # Fuerza la re-ejecución del script para mostrar el documento

def show_document_view(doc_name: str):
    """Muestra el contenido de un documento y su tabla de contenidos."""
    doc_path = os.path.join(DOCS_DIR, doc_name)

    try:
        with open(doc_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        st.error(f"Error: El archivo '{doc_name}' no fue encontrado.")
        st.session_state.selected_doc = None # Resetea el estado
        st.button("← Volver al listado") # st.rerun() es implícito al pulsar
        return

    # Extrae la tabla de contenidos del markdown original
    toc_items = get_toc(content)

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        # Botón para volver al listado principal
        if st.button("← Volver al listado"):
            st.session_state.selected_doc = None
            st.rerun()

        # Construye la tabla de contenidos como una única cadena de Markdown
        toc_lines = []
        for item in toc_items:
            indentation = "  " * (item['level'] - 1)
            toc_lines.append(f"{indentation}- [{item['title']}](#{item['slug']})")
        
        # Renderiza la tabla de contenidos completa en un solo llamado a st.markdown
        if toc_lines:
            st.markdown("\n".join(toc_lines))

    # --- VISTA PRINCIPAL ---
    # Renderiza el contenido Markdown directamente.
    # Streamlit genera automáticamente los IDs de los encabezados para los anclajes.
    st.markdown(content)


# --- LÓGICA PRINCIPAL DE LA APLICACIÓN ---
if st.session_state.selected_doc:
    show_document_view(st.session_state.selected_doc)
else:
    show_document_list()