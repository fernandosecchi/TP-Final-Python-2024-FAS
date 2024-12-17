import streamlit as st
from datetime import date, timedelta
from src.utils.validators import validate_dates

def render_date_selector():
    """
    Renderiza y maneja la selección de fechas.
    Returns:
        tuple: (fecha_inicio, fecha_fin) o (None, None) si las fechas son inválidas
    """
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

    # Validar las fechas
    if not validate_dates(fecha_inicio, fecha_fin):
        st.error("⚠️ La fecha de inicio debe ser anterior a la fecha final")
        return None, None
        
    return fecha_inicio, fecha_fin
