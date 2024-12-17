import sys, os
import streamlit as st

# Add both parent directory and current directory to Python path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.extend([parent_dir, current_dir])

# Import views
from views import home_view, historical_view, maintenance_view

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Acciones",
    page_icon="📈",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

def main():
    """
    Punto de entrada principal de la aplicación Streamlit.
    Maneja la navegación entre páginas y la configuración global.
    """
    # Definir las páginas disponibles con sus íconos
    pages = {
        "🏠 Inicio": home_view.show,
        "📚 Historial": historical_view.show,
        "🔧 Mantenimiento": maintenance_view.show
    }
    
    # Sidebar para navegación
    with st.sidebar:
        st.title("📈 Análisis de Acciones")
        
        # Navegación
        st.subheader("Menú")
        page = st.radio(
            "Seleccione una página",
            options=list(pages.keys()),
            label_visibility="collapsed",
            key="navigation"
        )
        
        st.divider()
        
        # Información adicional en el sidebar
        st.markdown("""
        ### ℹ️ Sobre la aplicación
        Análisis de datos históricos de acciones 
        utilizando datos de mercado en tiempo real.
        
        ### 👨‍💻 Desarrollado por
        Fernando Secchi
        
        ### 📋 Trabajo Práctico
        Trabajo Práctico Final ITBA
        """)
    
    # Renderizar la página seleccionada
    pages[page]()

if __name__ == "__main__":
    main()
