import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import pandas as pd

from src.api.api_finanzas import FinanceAPI
from src.models.ticker_model import TickerModel
from src.utils.validators import validate_dates

class TickerService:
    """
    Servicio para manejar la lógica de negocio relacionada con los tickers.
    """
    
    def __init__(self):
        self.api = FinanceAPI()
        self.model = TickerModel()
    
    def validate_ticker(self, ticker: str) -> tuple[bool, str]:
        """
        Valida que el ticker tenga el formato correcto.
        Args:
            ticker (str): El ticker a validar
        Returns:
            tuple[bool, str]: (True, "") si el ticker es válido, 
                            (False, mensaje_error) en caso contrario
        """
        if not ticker:
            return False, "El ticker no puede estar vacío"
            
        # Convertir a mayúsculas para ayudar al usuario
        ticker = ticker.upper()
        
        # Verificar longitud
        if len(ticker) > 5:
            return False, f"El ticker '{ticker}' es demasiado largo. Debe tener entre 1 y 5 caracteres."
            
        # Verificar caracteres válidos
        if not re.match("^[A-Z]{1,5}$", ticker):
            return False, f"El ticker '{ticker}' contiene caracteres inválidos. Solo se permiten letras mayúsculas."
            
        # Verificar tickers comunes mal escritos
        ticker_corrections = {
            # Empresas tecnológicas
            "APPL": "AAPL",      # Apple
            "MCRSFT": "MSFT",    # Microsoft
            "AMZM": "AMZN",      # Amazon
            "GOGL": "GOOGL",     # Alphabet (Google)
            "TSLE": "TSLA",      # Tesla
            "NVIDA": "NVDA",     # NVIDIA
            "NETFLX": "NFLX",    # Netflix
            "ORCLE": "ORCL",     # Oracle
            "ADOB": "ADBE",      # Adobe
            "PYPAL": "PYPL",     # PayPal

            # Otras grandes empresas
            "MCDN": "MCD",       # McDonald's
            "WLMT": "WMT",       # Walmart
            "DSNY": "DIS",       # Disney
            "COKA": "KO",        # Coca-Cola (Error común: "COKA" en vez de KO)
            "JNJN": "JNJ",       # Johnson & Johnson

            # Sector financiero
            "VS": "V",           # Visa
            "MAST": "MA",        # Mastercard

            # Empresas que cambiaron de nombre/ticker
            "FACEBK": "META",    # Meta (antes Facebook: FB)
            "GGL": "GOOGL",      # Google en vez de GGL

            # Errores comunes por confusión de vocales o consonantes
            "INTL": "INTC"       # Intel (confundiendo la C final)
        }
        
        # Solo sugerir corrección si el ticker está mal escrito
        if ticker in ticker_corrections:
            suggested = ticker_corrections[ticker]
            return False, f"¿Quizás quisiste decir '{suggested}'? El ticker '{ticker}' parece estar mal escrito."
            
        return True, ""

    def get_historical_data(self,
                          ticker: str,
                          start_date: str,
                          end_date: str) -> Optional[tuple]:
        """
        Obtiene los datos históricos del ticker SOLO de la base de datos local.
        No intenta obtener nuevos datos de la API.
        
        Args:
            ticker (str): El ticker a consultar
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha fin en formato YYYY-MM-DD
            
        Returns:
            Optional[tuple]: (DataFrame, source) con los datos o None si no hay datos
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        is_valid, error_msg = self.validate_ticker(ticker)
        if not is_valid:
            raise ValueError(error_msg)
            
        # Validar fechas usando el validador común
        is_valid, error_msg = validate_dates(start_date, end_date)
        if not is_valid:
            raise ValueError(error_msg)
            
        try:
            # Obtener datos solo de la base de datos
            data = self.model.get_ticker_data(ticker, start_date, end_date)
            
            if data:
                # Convertir a DataFrame para facilitar visualización
                df = pd.DataFrame(data)
                # Convertir la columna date a datetime usando el formato correcto
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df.set_index('date', inplace=True)
                # Asignar el ticker como nombre del DataFrame
                df.name = ticker
                return df, "db"
            
            return None
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos históricos del ticker: {str(e)}")
            
    def get_ticker_data(self, 
                       ticker: str, 
                       start_date: str, 
                       end_date: str,
                       status_callback=None) -> Optional[tuple]:
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
        is_valid, error_msg = self.validate_ticker(ticker)
        if not is_valid:
            raise ValueError(error_msg)
            
        # Validar fechas usando el validador común
        is_valid, error_msg = validate_dates(start_date, end_date)
        if not is_valid:
            raise ValueError(error_msg)
            
        try:
            # Primero intentar obtener de la base de datos local
            data = self.model.get_ticker_data(ticker, start_date, end_date)
            source = "db"
            
            if not data:
                # Si no hay datos en DB, obtener de la API
                if status_callback:
                    status_callback(f"Obteniendo datos de {ticker} desde la API de Polygon.io...")
                api_data = self.api.get_stock_data(ticker, start_date, end_date)
                if api_data and api_data.get('results'):
                    # Intentar guardar en la base de datos
                    if self.model.save_ticker_data(ticker, api_data):
                        # Si se guardó correctamente, obtener de la base de datos para formato consistente
                        data = self.model.get_ticker_data(ticker, start_date, end_date)
                        source = "api"
                    else:
                        return None, f"Error al guardar los datos del ticker '{ticker}' en la base de datos."
                else:
                    # Verificar si el ticker es válido
                    if api_data and api_data.get('status') == 'ERROR':
                        return None, f"El ticker '{ticker}' no es válido según la API."
                    return None, f"No se encontraron datos para el ticker '{ticker}' en la API."
            
            if data:
                # Convertir a DataFrame para facilitar visualización
                df = pd.DataFrame(data)
                # Convertir la columna date a datetime usando el formato correcto
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df.set_index('date', inplace=True)
                # Asignar el ticker como nombre del DataFrame
                df.name = ticker
                return df, source
            
            return None
            
        except Exception as e:
            raise ValueError(f"Error al obtener datos del ticker: {str(e)}")

    def get_company_name(self, ticker: str) -> Optional[str]:
        """
        Obtiene el nombre de la compañía para un ticker.
        
        Args:
            ticker (str): El ticker a consultar
            
        Returns:
            Optional[str]: Nombre de la compañía o None si no se encuentra
        """
        try:
            print(f"Obteniendo nombre de compañía para ticker: {ticker}")
            details = self.api.get_ticker_details(ticker)
            print(f"Detalles obtenidos: {details}")
            if details and 'results' in details:
                name = details['results'].get('name')
                print(f"Nombre de compañía encontrado: {name}")
                return name
            print("No se encontraron resultados en los detalles")
            return None
        except Exception as e:
            print(f"Error al obtener nombre de compañía: {str(e)}")
            return None

    def process_ticker_data(self, df_data: tuple) -> Dict[str, Any]:
        """
        Procesa los datos del ticker para su visualización.
        
        Args:
            df_data (tuple): Tupla con (DataFrame, source) donde source indica el origen de los datos
            
        Returns:
            Dict[str, Any]: Datos procesados para visualización
            
        Raises:
            ValueError: Si hay error en el procesamiento
        """
        try:
            if df_data is None or df_data[0].empty:
                return None
                
            df, source = df_data
            # El ticker viene como primer elemento del tuple df_data
            ticker = df.name if hasattr(df, 'name') else None
            # Si no tiene name, intentamos obtenerlo del DataFrame
            if not ticker and isinstance(df, pd.DataFrame):
                df.name = df.index.name
                ticker = df.index.name
            company_name = self.get_company_name(ticker) if ticker else None
            
            return {
                'data': df,
                'source': source,
                'company_name': company_name,
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
        
    def delete_ticker_data(self, ticker: str) -> None:
        """
        Elimina todos los datos de un ticker específico
        
        Args:
            ticker (str): El ticker cuyos datos se eliminarán
            
        Raises:
            ValueError: Si el ticker es inválido o hay un error al eliminar
        """
        is_valid, error_msg = self.validate_ticker(ticker)
        if not is_valid:
            raise ValueError(error_msg)
            
        self.model.delete_ticker_data(ticker)
