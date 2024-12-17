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
    
    # Convertir timestamps (milisegundos) a fechas formateadas
    df['start_date'] = pd.to_datetime(df['start_date'].astype(float), unit='ms').dt.strftime('%d/%m/%Y')
    df['end_date'] = pd.to_datetime(df['end_date'].astype(float), unit='ms').dt.strftime('%d/%m/%Y')
    
    # Mostrar datos en una tabla interactiva
    st.dataframe(
        df,
        column_config={
            "ticker": st.column_config.TextColumn(
                "Ticker",
                help="Símbolo del ticker"
            ),
            "start_date": st.column_config.TextColumn(
                "Fecha Inicio",
                help="Fecha de inicio de la consulta"
            ),
            "end_date": st.column_config.TextColumn(
                "Fecha Fin",
                help="Fecha final de la consulta"
            )
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
            periodo_mas_consultado = df.groupby(['start_date', 'end_date']).size().idxmax()[0]
            st.metric("Período más Consultado", periodo_mas_consultado)
        
        # Mostrar datos detallados por ticker seleccionado
        st.subheader("📈 Datos Detallados")
        selected_ticker = st.selectbox(
            "Seleccionar Ticker para ver detalles",
            options=[''] + sorted(df['ticker'].unique().tolist())
        )
        
        if selected_ticker:
            try:
                # Obtener los datos más recientes para este ticker
                # Convertir las fechas de string a datetime y asegurar que sean datetime, no date
                start_date = pd.to_datetime(df[df['ticker'] == selected_ticker]['start_date'].iloc[0], format='%d/%m/%Y').to_pydatetime()
                end_date = pd.to_datetime(df[df['ticker'] == selected_ticker]['end_date'].iloc[0], format='%d/%m/%Y').to_pydatetime()
                
                latest_data = service.get_ticker_data(
                    ticker=selected_ticker,
                    start_date=start_date,
                    end_date=end_date
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
