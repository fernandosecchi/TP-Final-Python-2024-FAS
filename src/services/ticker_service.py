import re
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

from src.api_finanzas import FinanceAPI
from src.models.ticker_model import TickerModel

class TickerService:
    """
    Servicio para manejar la lógica de negocio relacionada con los tickers.
    """
    
    def __init__(self):
        self.api = FinanceAPI()
        self.model = TickerModel()
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Valida que el ticker tenga el formato correcto.
        Args:
            ticker (str): El ticker a validar
        Returns:
            bool: True si el ticker es válido, False en caso contrario
        """
        if not ticker:
            return False
        # Verificar que solo contenga letras mayúsculas y tenga entre 1 y 5 caracteres
        return bool(re.match("^[A-Z]{1,5}$", ticker))

    def get_ticker_data(self, 
                       ticker: str, 
                       start_date: datetime, 
                       end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Obtiene los datos del ticker para el período especificado.
        Primero busca en la base de datos local, si no encuentra datos
        los solicita a la API y los guarda.
        
        Args:
            ticker (str): El ticker a consultar
            start_date (datetime): Fecha de inicio
            end_date (datetime): Fecha de fin
            
        Returns:
            Optional[pd.DataFrame]: DataFrame con los datos o None si hay error
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        if not self.validate_ticker(ticker):
            raise ValueError("Ticker inválido")
            
        try:
            # Primero intentar obtener de la base de datos
            data = self.model.get_ticker_data(ticker, start_date, end_date)
            
            if not data:
                # Si no hay datos en DB, obtener de la API
                api_data = self.api.get_stock_data(ticker, start_date, end_date)
                if api_data:
                    # Guardar en la base de datos
                    self.model.save_ticker_data(ticker, api_data)
                    # Volver a obtener de la base de datos para tener formato consistente
                    data = self.model.get_ticker_data(ticker, start_date, end_date)
            
            if data:
                # Convertir a DataFrame para facilitar visualización
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                return df
                
            return None
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos del ticker: {str(e)}")

    def process_ticker_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Procesa los datos del ticker para su visualización.
        
        Args:
            df (pd.DataFrame): DataFrame con los datos del ticker
            
        Returns:
            Dict[str, Any]: Datos procesados para visualización
            
        Raises:
            ValueError: Si hay error en el procesamiento
        """
        try:
            if df is None or df.empty:
                return None
                
            return {
                'data': df,
                'summary': {
                    'start_date': df.index.min(),
                    'end_date': df.index.max(),
                    'avg_price': df['close'].mean(),
                    'min_price': df['low'].min(),
                    'max_price': df['high'].max(),
                    'total_volume': df['volume'].sum()
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error al procesar datos del ticker: {str(e)}")

    def get_stored_tickers_summary(self) -> List[Dict[str, str]]:
        """
        Obtiene un resumen de todos los tickers almacenados
        
        Returns:
            List[Dict[str, str]]: Lista de tickers y sus rangos de fechas
        """
        return self.model.get_stored_tickers()