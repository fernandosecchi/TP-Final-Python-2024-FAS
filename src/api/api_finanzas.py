import requests
from datetime import datetime
from typing import Optional, Dict, Any
import os



class FinanceAPI:
    """
    Cliente para la API de Polygon.io
    """
    def __init__(self):
        self.base_url = "https://api.polygon.io/v2"
        # La API key debería venir de variables de entorno
        
        self.api_key = os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY no está configurada en las variables de entorno")

    def get_ticker_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un ticker desde Polygon.io
        
        Args:
            ticker (str): Símbolo del ticker (ej: AAPL)
            
        Returns:
            Optional[Dict[str, Any]]: Detalles del ticker o None si hay error
        """
        try:
            url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 429:
                print(f"Error: Límite de API excedido para {ticker}")
                return None
                
            if data.get('status') == 'ERROR':
                print(f"Error de API para {ticker}: {data.get('error')}")
                return None
                
            return data
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API: {str(e)}")
            return None
        except ValueError as e:
            print(f"Error al procesar la respuesta JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"Error inesperado al obtener detalles de {ticker}: {str(e)}")
            return None

    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos históricos de acciones desde Polygon.io
        
        Args:
            ticker (str): Símbolo del ticker (ej: AAPL)
            start_date (datetime): Fecha de inicio
            end_date (datetime): Fecha de fin
            
        Returns:
            Optional[Dict[str, Any]]: Datos de la acción o None si hay error
        """
        try:
            # Las fechas ya vienen en formato YYYY-MM-DD
            start_str = start_date
            end_str = end_date
            
            # Construir URL
            endpoint = f"/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}"
            url = f"{self.base_url}{endpoint}?apiKey={self.api_key}"
            
            # Realizar request
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 429:
                print(f"Error: Límite de API excedido para {ticker}")
                return None
                
            if data.get('status') == 'ERROR':
                print(f"Error de API para {ticker}: {data.get('error')}")
                return None
                
            if not data.get('results'):
                print(f"No se encontraron datos para {ticker} en el período {start_str} a {end_str}")
                return None
                
            return data
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API: {str(e)}")
            return None
        except ValueError as e:
            print(f"Error al procesar la respuesta JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"Error inesperado al obtener datos de {ticker}: {str(e)}")
            return None
