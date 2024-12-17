import sys, os
import streamlit as st

# Add both parent directory and current directory to Python path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.extend([parent_dir, current_dir])

# Import after path modification
from pages import home

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Acciones",
    page_icon="📈",
    layout="wide"
)

def main():
    """
    Punto de entrada principal de la aplicación Streamlit.
    Maneja la navegación entre páginas y la configuración global.
    """
    # Por ahora solo tenemos una página, pero esto permite escalar fácilmente
    pages = {
        "Inicio": home.show
    }
    
    # Sidebar para navegación
    with st.sidebar:
        st.title("Navegación")
        page = st.radio("Ir a", list(pages.keys()))
        
        st.divider()
        
        # Información adicional en el sidebar
        st.markdown("""
        ### Sobre la aplicación
        Esta aplicación permite analizar datos históricos 
        de acciones utilizando datos de mercado en tiempo real.
        
        ### Desarrollado por
        Fernando Secchi
        
        ### Trabajo Práctico
        Trabájo Práctico Final ITBA
        """)
    
    # Renderizar la página seleccionada
    pages[page]()

if __name__ == "__main__":
    main()
