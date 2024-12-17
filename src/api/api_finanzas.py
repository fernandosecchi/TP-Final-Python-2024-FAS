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

    def get_stock_data(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
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
            # Formatear fechas para la API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Construir URL
            endpoint = f"/aggs/ticker/{ticker}/range/1/day/{start_str}/{end_str}"
            url = f"{self.base_url}{endpoint}?apiKey={self.api_key}"
            
            # Realizar request
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'OK' and data.get('results'):
                return data
            else:
                print(f"No se encontraron datos para {ticker}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {str(e)}")
            return None
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return None
