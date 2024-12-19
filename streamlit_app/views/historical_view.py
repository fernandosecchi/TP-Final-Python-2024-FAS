import streamlit as st
import pandas as pd
from datetime import datetime
from src.services.ticker_service import TickerService
from src.utils.exceptions import (
    DatabaseError, APIError, InvalidDataError,
    DataValidationError
)

def show():
    """
    Renderiza la página de consultas históricas mostrando los tickers y períodos almacenados en la base de datos.
    """
    st.title("📚 Historial de Consultas")
    
    try:
        # Inicializar el servicio
        service = TickerService()
        
        # Obtener todos los tickers almacenados
        stored_tickers = service.get_stored_tickers_summary()
        
        if not stored_tickers:
            st.info("No hay consultas históricas almacenadas.")
            return
        
        # Preparar datos para visualización
        records = []
        for ticker_info in stored_tickers:
            ticker = ticker_info['ticker']
            for range_info in ticker_info['ranges']:
                records.append({
                    'ticker': ticker,
                    'start_date': range_info['start_date'],
                    'end_date': range_info['end_date'],
                    'created_at': range_info['created_at'],
                    'data_points': range_info['data_points']
                })
                
        # Convertir a DataFrame para mejor manipulación
        df = pd.DataFrame(records)
        
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
                "ticker": st.column_config.TextColumn(
                    "Ticker",
                    help="Símbolo del ticker"
                ),
                "start_date": st.column_config.TextColumn(
                    "Fecha Inicio",
                    help="Fecha de inicio de los datos almacenados"
                ),
                "end_date": st.column_config.TextColumn(
                    "Fecha Fin",
                    help="Fecha final de los datos almacenados"
                ),
                "created_at": st.column_config.TextColumn(
                    "Fecha de Consulta",
                    help="Fecha en que se realizó la consulta"
                ),
                "data_points": st.column_config.NumberColumn(
                    "Puntos de Datos",
                    help="Cantidad de datos almacenados en este rango"
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
                st.metric("Total de Datos", df['data_points'].sum())
            
            # Mostrar datos detallados por ticker seleccionado
            st.subheader("📈 Datos Detallados")
            selected_ticker = st.selectbox(
                "Seleccionar Ticker para ver detalles",
                options=[''] + sorted(df['ticker'].unique().tolist())
            )
            
            if selected_ticker:
                # Obtener todos los rangos disponibles para el ticker seleccionado
                ticker_ranges = df[df['ticker'] == selected_ticker].sort_values('created_at', ascending=False)
                
                # Permitir al usuario seleccionar un rango específico
                range_options = [
                    f"{row['start_date']} a {row['end_date']} ({row['data_points']} datos)"
                    for _, row in ticker_ranges.iterrows()
                ]
                
                selected_range = st.selectbox(
                    "Seleccionar Rango de Fechas",
                    options=range_options,
                    format_func=lambda x: f"Período: {x}"
                )
                
                if selected_range:
                    try:
                        # Obtener el índice del rango seleccionado
                        range_index = range_options.index(selected_range)
                        ticker_row = ticker_ranges.iloc[range_index]
                        
                        # Obtener las fechas del rango seleccionado
                        start_date = ticker_row['start_date']
                        end_date = ticker_row['end_date']
                        
                        # Obtener datos históricos
                        latest_data = service.get_historical_data(
                            ticker=selected_ticker,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        if latest_data is None:
                            st.warning(
                                f"No hay datos históricos almacenados para {selected_ticker} "
                                f"en el período {start_date} al {end_date}"
                            )
                            return
                        
                        # Mostrar advertencia si hay fechas faltantes
                        if latest_data['missing_dates']:
                            st.warning(
                                "⚠️ No hay datos disponibles para las siguientes fechas:\n" +
                                ", ".join(latest_data['missing_dates'])
                            )
                        
                        # Procesar datos para visualización
                        df_data = (latest_data['data'], latest_data['source'])
                        processed_data = service.process_ticker_data(df_data)
                        
                        # Mostrar información del período consultado
                        st.info(
                            f"Mostrando datos históricos para {selected_ticker}\n"
                            f"Período: {ticker_row['start_date']} al {ticker_row['end_date']}\n"
                            f"Consulta realizada: {ticker_row['created_at']}\n"
                            f"Cantidad de datos: {ticker_row['data_points']}"
                        )
                        
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
                        
                    except (DatabaseError, APIError) as e:
                        st.error(f"Error al obtener los datos: {str(e)}")
                    except InvalidDataError as e:
                        st.warning(f"⚠️ {str(e)}")
                    except DataValidationError as e:
                        st.error(f"Error de validación: {str(e)}")
                    except Exception as e:
                        st.error(f"Error inesperado: {str(e)}")
                        
    except (DatabaseError, APIError) as e:
        st.error(f"Error al obtener los datos almacenados: {str(e)}")
    except (KeyError, TypeError) as e:
        st.error(f"Error en el formato de los datos almacenados: {str(e)}")
    except Exception as e:
        st.error(f"Error inesperado al cargar los datos: {str(e)}")
