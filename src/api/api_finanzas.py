import requests
from datetime import datetime
from typing import Dict, Any
import os
from src.utils.exceptions import (
    APIError, APIRateLimitError, APIConnectionError,
    InvalidDataError
)

class FinanceAPI:
    """
    Cliente para la API de Polygon.io
    """
    def __init__(self):
        self.base_url = "https://api.polygon.io/v2"
        # La API key debería venir de variables de entorno
        
        self.api_key = os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise APIError("POLYGON_API_KEY no está configurada en las variables de entorno")

    def get_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """
        Obtiene los detalles de un ticker desde Polygon.io
        
        Args:
            ticker (str): Símbolo del ticker (ej: AAPL)
            
        Returns:
            Dict[str, Any]: Detalles del ticker
            
        Raises:
            APIRateLimitError: Si se excede el límite de la API
            APIConnectionError: Si hay problemas de conexión
            APIError: Si hay otros errores de la API
            InvalidDataError: Si la respuesta no tiene el formato esperado
        """
        try:
            url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={self.api_key}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 429:
                raise APIRateLimitError(f"Límite de API excedido para {ticker}")
                
            if data.get('status') == 'ERROR':
                raise APIError(f"Error de API para {ticker}: {data.get('error')}")
                
            if not isinstance(data, dict):
                raise InvalidDataError(f"Respuesta inválida de la API para {ticker}")
                
            return data
                
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Error de conexión con la API: {str(e)}")
        except ValueError as e:
            raise InvalidDataError(f"Error al procesar la respuesta JSON: {str(e)}")
        except (APIError, APIRateLimitError, APIConnectionError, InvalidDataError):
            raise
        except Exception as e:
            raise APIError(f"Error inesperado al obtener detalles de {ticker}: {str(e)}")

    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Obtiene datos históricos de acciones desde Polygon.io
        
        Args:
            ticker (str): Símbolo del ticker (ej: AAPL)
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD
            
        Returns:
            Dict[str, Any]: Datos históricos de la acción
            
        Raises:
            APIRateLimitError: Si se excede el límite de la API
            APIConnectionError: Si hay problemas de conexión
            APIError: Si hay otros errores de la API
            InvalidDataError: Si la respuesta no tiene el formato esperado
        """
        try:
            # Construir URL
            endpoint = f"/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
            url = f"{self.base_url}{endpoint}?apiKey={self.api_key}"
            
            # Realizar request
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 429:
                raise APIRateLimitError(f"Límite de API excedido para {ticker}")
                
            if data.get('status') == 'ERROR':
                raise APIError(f"Error de API para {ticker}: {data.get('error')}")
                
            if not data.get('results'):
                raise InvalidDataError(f"No se encontraron datos para {ticker} en el período {start_date} a {end_date}")
                
            if not isinstance(data['results'], list):
                raise InvalidDataError(f"Formato de respuesta inválido para {ticker}")
                
            return data
                
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Error de conexión con la API: {str(e)}")
        except ValueError as e:
            raise InvalidDataError(f"Error al procesar la respuesta JSON: {str(e)}")
        except (APIError, APIRateLimitError, APIConnectionError, InvalidDataError):
            raise
        except Exception as e:
            raise APIError(f"Error inesperado al obtener datos de {ticker}: {str(e)}")
