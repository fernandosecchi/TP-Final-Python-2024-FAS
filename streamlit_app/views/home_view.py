import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from streamlit_app.components.ticker_input import render_ticker_input
from streamlit_app.components.date_selector import render_date_selector
from src.services.ticker_service import TickerService
from src.utils.exceptions import (
    DatabaseError, APIError, InvalidDataError,
    DataValidationError
)

def plot_stock_data(data):
    """
    Crea un gráfico de velas (candlestick) con los datos de la acción
    """
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close']
    )])
    
    fig.update_layout(
        title="Gráfico de Precios",
        yaxis_title="Precio",
        xaxis_title="Fecha",
        template="plotly_dark"
    )
    
    return fig

def show_summary(summary, company_name=None):
    """
    Muestra un resumen de los datos del ticker
    """
    # Si tenemos el nombre de la compañía, mostrarlo como subtítulo
    if company_name:
        st.subheader(f"📊 {company_name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Precio Promedio", f"${summary['avg_price']:.2f}")
        st.metric("Precio Mínimo", f"${summary['min_price']:.2f}")
    
    with col2:
        st.metric("Precio Máximo", f"${summary['max_price']:.2f}")
        st.metric("Volumen Total", f"{summary['total_volume']:,.0f}")

def show():
    """
    Renderiza la página principal de la aplicación.
    """
    st.title("🔍 Nueva Consulta")
    
    # Inicializar el servicio
    service = TickerService()
    
    # Crear un contenedor para los inputs
    st.markdown("""
    Ingrese los datos para analizar un nuevo ticker:
    """)
    
    with st.container():
        # Renderizar el input del ticker
        ticker = render_ticker_input()
        
        # Renderizar el selector de fechas
        fecha_inicio, fecha_fin = render_date_selector()
        
        # Botón para ejecutar el análisis
        if st.button("Analizar", type="primary"):
            if not ticker:
                st.warning("⚠️ Por favor, ingrese un símbolo de ticker válido.")
            elif not fecha_inicio or not fecha_fin:
                st.warning("⚠️ Por favor, seleccione fechas válidas.")
            else:
                # Crear un contenedor para el mensaje de estado
                status_container = st.empty()
                
                def update_status(message):
                    status_container.info(message)
                
                try:
                    # Obtener los datos usando el servicio
                    with st.spinner(f"Buscando datos de {ticker}..."):
                        data = service.get_ticker_data(
                            ticker=ticker,
                            start_date=fecha_inicio,
                            end_date=fecha_fin,
                            status_callback=update_status
                        )
                    
                    if data is not None:
                        try:
                            # Procesar y mostrar los datos
                            df_data = (data['data'], data['source'])
                            processed_data = service.process_ticker_data(df_data)
                            
                            # Mostrar mensaje sobre la fuente de los datos
                            source_text = {
                                "db": "la base de datos local",
                                "api": "la API de Polygon.io",
                                "mixed": "múltiples fuentes"
                            }.get(data['source'], "fuente desconocida")
                            
                            st.success(f"✅ Datos obtenidos para {ticker} desde {source_text}")
                            
                            # Mostrar advertencia si hay fechas faltantes
                            if data['missing_dates']:
                                st.warning(
                                    "⚠️ Algunos datos no están disponibles para las siguientes fechas:\n" +
                                    ", ".join(data['missing_dates'])
                                )
                            
                            # Mostrar el gráfico
                            st.plotly_chart(
                                plot_stock_data(processed_data['data']),
                                use_container_width=True
                            )
                            
                            # Mostrar el resumen con el nombre de la compañía
                            show_summary(processed_data['summary'], processed_data.get('company_name'))
                        except (KeyError, TypeError) as e:
                            st.error(f"❌ Error al procesar los datos: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error inesperado al procesar los datos: {str(e)}")
                    else:
                        st.warning("No se encontraron datos para el período seleccionado.")
                except (DatabaseError, APIError) as e:
                    st.error(f"❌ Error al obtener los datos: {str(e)}")
                except InvalidDataError as e:
                    st.warning(f"⚠️ {str(e)}")
                except DataValidationError as e:
                    st.error(f"❌ Error de validación: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")

    # Agregar información adicional
    with st.expander("ℹ️ Información"):
        st.markdown("""
        Esta aplicación permite analizar datos históricos de acciones.
        - Ingrese el símbolo del ticker (por ejemplo, AAPL para Apple)
        - Seleccione el rango de fechas para el análisis
        - Presione 'Analizar' para ver los resultados
        
        Los datos son obtenidos de Polygon.io y almacenados localmente para consultas futuras.
        """)
