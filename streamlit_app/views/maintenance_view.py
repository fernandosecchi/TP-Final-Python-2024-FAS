import streamlit as st
import pandas as pd
from src.services.ticker_service import TickerService
from datetime import datetime
from src.utils.exceptions import (
    DatabaseError, APIError, InvalidDataError,
    DataValidationError
)

def show():
    """
    Renderiza la página de mantenimiento de la base de datos.
    """
    st.title("🔧 Mantenimiento de Base de Datos")
    
    try:
        # Inicializar el servicio
        service = TickerService()
        
        # Obtener todos los tickers almacenados
        stored_tickers = service.get_stored_tickers_summary()
        
        if not stored_tickers:
            st.info("No hay datos almacenados en la base de datos.")
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
        
        # Mostrar resumen de datos almacenados
        st.subheader("📊 Resumen de Datos Almacenados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Tickers", df['ticker'].nunique())
        with col2:
            st.metric("Total de Rangos", len(df))
        with col3:
            st.metric("Total de Datos", df['data_points'].sum())
        
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
                ),
                "created_at": st.column_config.TextColumn(
                    "Fecha de Consulta",
                    help="Fecha en que se realizó la consulta"
                ),
                "data_points": st.column_config.NumberColumn(
                    "Puntos de Datos",
                    help="Cantidad de datos en este rango"
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
            # Mostrar información del ticker seleccionado
            ticker_data = df[df['ticker'] == ticker_to_delete]
            st.info(
                f"Se eliminarán todos los datos de {ticker_to_delete}:\n"
                f"- {len(ticker_data)} rangos de fechas\n"
                f"- {ticker_data['data_points'].sum()} puntos de datos"
            )
            
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
                    except (DatabaseError, APIError) as e:
                        st.error(f"❌ Error al eliminar datos: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")
                        
    except (DatabaseError, APIError) as e:
        st.error(f"Error al obtener los datos almacenados: {str(e)}")
    except (KeyError, TypeError) as e:
        st.error(f"Error en el formato de los datos almacenados: {str(e)}")
    except Exception as e:
        st.error(f"Error inesperado al cargar los datos: {str(e)}")
