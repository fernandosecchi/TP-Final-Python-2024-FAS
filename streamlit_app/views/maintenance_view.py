import streamlit as st
import pandas as pd
from src.services.ticker_service import TickerService
from datetime import datetime

def show():
    """
    Renderiza la página de mantenimiento de la base de datos.
    """
    st.title("🔧 Mantenimiento de Base de Datos")
    
    # Inicializar el servicio
    service = TickerService()
    
    # Obtener todos los tickers almacenados
    stored_tickers = service.get_stored_tickers_summary()
    
    if not stored_tickers:
        st.info("No hay datos almacenados en la base de datos.")
        return
    
    # Convertir a DataFrame para mejor manipulación
    df = pd.DataFrame(stored_tickers)
    
    # Convertir timestamps a fechas legibles
    df['start_date'] = pd.to_datetime(pd.to_numeric(df['start_date']), unit='ms').dt.strftime('%d/%m/%Y')
    df['end_date'] = pd.to_datetime(pd.to_numeric(df['end_date']), unit='ms').dt.strftime('%d/%m/%Y')
    
    # Mostrar resumen de datos almacenados
    st.subheader("📊 Resumen de Datos Almacenados")
    st.metric("Total de Tickers", len(df))
    
    # Mostrar datos en una tabla interactiva
    st.subheader("📋 Datos Almacenados")
    st.dataframe(
        df,
        column_config={
            "ticker": st.column_config.TextColumn(
                "Ticker",
                help="Símbolo del ticker"
            ),
            "start_date": st.column_config.TextColumn(
                "Fecha Inicio",
                help="Fecha de inicio de los datos"
            ),
            "end_date": st.column_config.TextColumn(
                "Fecha Fin",
                help="Fecha final de los datos"
            )
        },
        hide_index=True
    )
    
    # Sección para eliminar datos
    st.subheader("🗑️ Eliminar Datos")
    
    # Selector de ticker para eliminar
    ticker_to_delete = st.selectbox(
        "Seleccionar ticker para eliminar",
        options=[''] + sorted(df['ticker'].unique().tolist()),
        format_func=lambda x: 'Seleccione un ticker' if x == '' else x
    )
    
    if ticker_to_delete:
        # Mostrar advertencia y botón de confirmación
        st.warning(f"⚠️ ¿Está seguro que desea eliminar todos los datos de {ticker_to_delete}?")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Eliminar", type="primary"):
                try:
                    service.delete_ticker_data(ticker_to_delete)
                    st.success(f"✅ Datos de {ticker_to_delete} eliminados correctamente")
                    # Recargar la página para actualizar la lista
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar datos: {str(e)}")
