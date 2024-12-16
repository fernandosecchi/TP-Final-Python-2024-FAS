import streamlit as st
from datetime import date, timedelta
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Acciones",
    page_icon="📈"
)

st.title("📈 Análisis de Acciones")

# Crear un contenedor para los inputs
with st.container():
    # Input para el ticker con validación
    ticker = st.text_input(
        "Ingrese el símbolo del ticker (ejemplo: AAPL, MSFT, GOOGL)",
        help="Ingrese el símbolo de la acción que desea analizar"
    ).upper()  # Convertir a mayúsculas automáticamente
    
    # Crear dos columnas para las fechas
    col1, col2 = st.columns(2)
    
    # En la primera columna: fecha de inicio
    with col1:
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=date.today() - timedelta(days=365),  # Por defecto, un año atrás
            max_value=date.today(),
            help="Seleccione la fecha de inicio del análisis"
        )
    
    # En la segunda columna: fecha de fin
    with col2:
        fecha_fin = st.date_input(
            "Fecha de fin",
            value=date.today(),
            min_value=fecha_inicio,
            max_value=date.today(),
            help="Seleccione la fecha final del análisis"
        )

# Validación de fechas
if fecha_inicio >= fecha_fin:
    st.error("La fecha de inicio debe ser anterior a la fecha final")
    st.stop()

# Botón para ejecutar el análisis
if st.button("Analizar", type="primary"):
    if not ticker:
        st.warning("⚠️ Por favor, ingrese un símbolo de ticker válido.")
    else:
        with st.spinner(f"Obteniendo datos para {ticker}..."):
            try:
                # Aquí irá la lógica para obtener los datos
                st.success(f"✅ Datos obtenidos exitosamente para {ticker}")
                st.write(f"Período de análisis: {fecha_inicio} hasta {fecha_fin}")
                
                # Placeholder para futuros datos
                st.info("Los datos se mostrarán aquí una vez que se integre la API")
                
            except Exception as e:
                st.error(f"❌ Error al obtener los datos: {str(e)}")

# Agregar información adicional
with st.expander("ℹ️ Información"):
    st.markdown("""
    Esta aplicación permite analizar datos históricos de acciones.
    - Ingrese el símbolo del ticker (por ejemplo, AAPL para Apple)
    - Seleccione el rango de fechas para el análisis
    - Presione 'Analizar' para ver los resultados
    """)
