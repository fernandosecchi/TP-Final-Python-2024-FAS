import streamlit as st
import pandas as pd
from src.services.ticker_service import TickerService

def show():
    """
    Renderiza la página de consultas históricas.
    """
    st.title("📚 Historial de Consultas")
    
    # Inicializar el servicio
    service = TickerService()
    
    # Obtener todos los tickers almacenados
    stored_tickers = service.get_stored_tickers_summary()
    
    if not stored_tickers:
        st.info("No hay consultas históricas almacenadas.")
        return
    
    # Convertir a DataFrame para mejor manipulación
    df = pd.DataFrame(stored_tickers)
    
    # Agregar filtros
    col1, col2 = st.columns(2)
    with col1:
        selected_tickers = st.multiselect(
            "Filtrar por Ticker",
            options=sorted(df['ticker'].unique()),
            default=[]
        )
    
    # Aplicar filtros
    if selected_tickers:
        df = df[df['ticker'].isin(selected_tickers)]
    
    # Mostrar datos en una tabla interactiva
    st.dataframe(
        df,
        column_config={
            "ticker": "Ticker",
            "start_date": "Fecha Inicio",
            "end_date": "Fecha Fin"
        },
        hide_index=True
    )
    
    # Mostrar estadísticas
    if not df.empty:
        st.subheader("📊 Estadísticas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Consultas", len(df))
        with col2:
            st.metric("Tickers Únicos", df['ticker'].nunique())
        with col3:
            st.metric("Período más Consultado", 
                     df.groupby(['start_date', 'end_date']).size().idxmax()[0])
        
        # Mostrar datos detallados por ticker seleccionado
        st.subheader("📈 Datos Detallados")
        selected_ticker = st.selectbox(
            "Seleccionar Ticker para ver detalles",
            options=[''] + sorted(df['ticker'].unique().tolist())
        )
        
        if selected_ticker:
            try:
                # Obtener los datos más recientes para este ticker
                latest_data = service.get_ticker_data(
                    ticker=selected_ticker,
                    start_date=df[df['ticker'] == selected_ticker]['start_date'].iloc[0],
                    end_date=df[df['ticker'] == selected_ticker]['end_date'].iloc[0]
                )
                
                if latest_data is not None:
                    processed_data = service.process_ticker_data(latest_data)
                    
                    # Mostrar resumen
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Precio Promedio", f"${processed_data['summary']['avg_price']:.2f}")
                        st.metric("Precio Mínimo", f"${processed_data['summary']['min_price']:.2f}")
                    with col2:
                        st.metric("Precio Máximo", f"${processed_data['summary']['max_price']:.2f}")
                        st.metric("Volumen Total", f"{processed_data['summary']['total_volume']:,.0f}")
            except Exception as e:
                st.error(f"Error al cargar los datos detallados: {str(e)}")
