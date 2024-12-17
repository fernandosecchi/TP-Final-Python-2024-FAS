import streamlit as st
from datetime import date, timedelta, datetime
from src.utils.validators import validate_dates

def render_date_selector():
    """
    Renderiza y maneja la selección de fechas.
    Returns:
        tuple: (fecha_inicio, fecha_fin) o (None, None) si las fechas son inválidas
    """
    # Crear dos columnas para las fechas
    col1, col2 = st.columns(2)
    
    # Configurar fechas por defecto (últimos 7 días)
    hoy = date.today()
    fecha_fin_default = hoy - timedelta(days=1)  # ayer
    fecha_inicio_default = hoy - timedelta(days=7)  # hace una semana
    
    # En la primera columna: fecha de inicio
    with col1:
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=fecha_inicio_default,
            max_value=fecha_fin_default,
            help="Seleccione la fecha de inicio del análisis (debe ser anterior a la fecha actual)",
            format="DD/MM/YYYY"  # Formato argentino
        )
    
    # En la segunda columna: fecha de fin
    with col2:
        fecha_fin = st.date_input(
            "Fecha de fin",
            value=fecha_fin_default,
            min_value=fecha_inicio,
            max_value=hoy,  # No permitir fechas futuras
            help="Seleccione la fecha final del análisis (debe ser anterior o igual a la fecha actual)",
            format="DD/MM/YYYY"  # Formato argentino
        )

    # Validar las fechas
    is_valid, error_msg = validate_dates(fecha_inicio, fecha_fin)
    if not is_valid:
        st.error(f"⚠️ {error_msg}")
        return None, None
    
    # Formatear las fechas como strings en formato YYYY-MM-DD
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
        
    return fecha_inicio_str, fecha_fin_str
