import streamlit as st
from src.services.ticker_service import TickerService

def render_ticker_input():
    """
    Renderiza y maneja el input del ticker.
    Returns:
        str: El ticker validado o None si es inválido
    """
    ticker = st.text_input(
        "Ingrese el símbolo del ticker (ejemplo: AAPL, MSFT, GOOGL)",
        help="Ingrese el símbolo de la acción que desea analizar"
    ).upper()
    
    if ticker:
        service = TickerService()
        if not service.validate_ticker(ticker):
            st.error("⚠️ Ticker inválido. Debe contener entre 1 y 5 letras mayúsculas.")
            return None
    return ticker
