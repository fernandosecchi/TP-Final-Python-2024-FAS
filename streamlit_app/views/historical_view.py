import streamlit as st
import pandas as pd
from datetime import datetime
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
    # Aseguramos que los timestamps sean numéricos antes de la conversión
    df['start_date'] = pd.to_datetime(pd.to_numeric(df['start_date']), unit='ms').dt.strftime('%d/%m/%Y')
    df['end_date'] = pd.to_datetime(pd.to_numeric(df['end_date']), unit='ms').dt.strftime('%d/%m/%Y')
    
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
                # Obtener la fila correspondiente al ticker seleccionado
                ticker_row = df[df['ticker'] == selected_ticker].iloc[0]
                
                try:
                    # Obtener los timestamps originales del DataFrame antes de la conversión a formato de fecha
                    original_df = pd.DataFrame(stored_tickers)
                    original_row = original_df[original_df['ticker'] == selected_ticker].iloc[0]
                    
                    # Convertir timestamps a datetime asegurando que sean enteros
                    start_timestamp = int(float(original_row['start_date']))
                    end_timestamp = int(float(original_row['end_date']))
                    
                    # Usar los timestamps originales para la consulta
                    latest_data = service.get_ticker_data(
                        ticker=selected_ticker,
                        start_date=datetime.fromtimestamp(start_timestamp/1000),
                        end_date=datetime.fromtimestamp(end_timestamp/1000)
                    )
                    
                    if latest_data is None:
                        st.warning(f"No se encontraron datos para {selected_ticker} en el período seleccionado. Por favor, intente con otro período o verifique el símbolo del ticker.")
                        return
                    
                    processed_data = service.process_ticker_data(latest_data)
                    
                    # Mostrar información del período consultado
                    st.info(f"Mostrando datos históricos para {selected_ticker} del período: {ticker_row['start_date']} al {ticker_row['end_date']}")
                    
                    # Mostrar resumen
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Precio Promedio", f"${processed_data['summary']['avg_price']:.2f}")
                        st.metric("Precio Mínimo", f"${processed_data['summary']['min_price']:.2f}")
                    with col2:
                        st.metric("Precio Máximo", f"${processed_data['summary']['max_price']:.2f}")
                        st.metric("Volumen Total", f"{processed_data['summary']['total_volume']:,.0f}")
                    
                    # Mostrar gráfico de precios
                    st.subheader("Gráfico de Precios")
                    df_plot = processed_data['data']
                    st.line_chart(df_plot['close'])
                    
                except ValueError as e:
                    st.error(f"Error al procesar los datos: {str(e)}")
                    return
                except Exception as e:
                    st.error(f"Error inesperado al obtener datos de {selected_ticker}: {str(e)}")
                    return
            except Exception as e:
                st.error(f"Error al cargar los datos detallados: {str(e)}")
