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
    
    # Configurar fechas por defecto
    fecha_fin_default = date.today()
    # Si es lunes, usar el viernes anterior como fecha fin por defecto
    if fecha_fin_default.weekday() == 0:  # 0 = Lunes
        fecha_fin_default = fecha_fin_default - timedelta(days=3)
    # Si es domingo, usar el viernes anterior
    elif fecha_fin_default.weekday() == 6:  # 6 = Domingo
        fecha_fin_default = fecha_fin_default - timedelta(days=2)
    # Si es sábado, usar el viernes
    elif fecha_fin_default.weekday() == 5:  # 5 = Sábado
        fecha_fin_default = fecha_fin_default - timedelta(days=1)
    
    # Fecha inicio por defecto: 3 meses atrás
    fecha_inicio_default = fecha_fin_default - timedelta(days=90)
    
    # En la primera columna: fecha de inicio
    with col1:
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=fecha_inicio_default,
            max_value=fecha_fin_default,
            help="Seleccione la fecha de inicio del análisis",
            format="DD/MM/YYYY"  # Formato argentino
        )
    
    # En la segunda columna: fecha de fin
    with col2:
        fecha_fin = st.date_input(
            "Fecha de fin",
            value=fecha_fin_default,
            min_value=fecha_inicio,
            max_value=date.today(),
            help="Seleccione la fecha final del análisis (días hábiles)",
            format="DD/MM/YYYY"  # Formato argentino
        )

    # Validar las fechas
    if not validate_dates(fecha_inicio, fecha_fin):
        st.error("⚠️ La fecha de inicio debe ser anterior a la fecha final")
        return None, None
        
    return fecha_inicio, fecha_fin
