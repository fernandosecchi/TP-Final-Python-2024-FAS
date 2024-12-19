import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Tuple
import pandas as pd

from src.api.api_finanzas import FinanceAPI
from src.models.ticker_model import TickerModel
from src.utils.validators import validate_dates
from src.utils.exceptions import (
    DatabaseError, APIError, APIRateLimitError, APIConnectionError,
    InvalidDataError, DataValidationError
)

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
                          end_date: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos históricos del ticker SOLO de la base de datos local.
        No intenta obtener nuevos datos de la API.
        
        Args:
            ticker (str): El ticker a consultar
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha fin en formato YYYY-MM-DD
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con:
                - data: DataFrame con los datos históricos
                - source: Origen de los datos ("db")
                - missing_dates: Lista de fechas sin datos disponibles
                O None si no hay datos
            
        Raises:
            ValueError: Si los parámetros son inválidos
            DatabaseError: Si hay error al acceder a la base de datos
            InvalidDataError: Si los datos no tienen el formato esperado
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
                # Convertir a DataFrame
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df.set_index('date', inplace=True)
                df.name = ticker
                
                # Verificar cobertura de datos
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                date_range = pd.date_range(start=start_dt, end=end_dt, freq='B')
                missing_dates = date_range.difference(df.index)
                
                return {
                    'data': df,
                    'source': 'db',
                    'missing_dates': [d.strftime('%d/%m/%Y') for d in missing_dates] if len(missing_dates) > 0 else []
                }
            
            return None
            
        except DatabaseError as e:
            raise
        except Exception as e:
            raise InvalidDataError(f"Error al obtener datos históricos del ticker: {str(e)}")
            
    def get_ticker_data(self, 
                       ticker: str, 
                       start_date: str, 
                       end_date: str,
                       status_callback=None) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos del ticker para el período especificado.
        Primero busca en la base de datos local, si no encuentra datos
        los solicita a la API y los guarda.
        
        Args:
            ticker (str): El ticker a consultar
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD
            status_callback (Callable[[str], None], optional): Función para reportar el estado del proceso
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con:
                - data: DataFrame con los datos históricos
                - source: Origen de los datos ("db", "api", o "mixed")
                - missing_dates: Lista de fechas sin datos disponibles
                O None si no hay datos
            
        Raises:
            ValueError: Si los parámetros son inválidos
            DatabaseError: Si hay error al acceder a la base de datos
            APIError: Si hay error al obtener datos de la API
            InvalidDataError: Si los datos no tienen el formato esperado
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
            try:
                data = self.model.get_ticker_data(ticker, start_date, end_date)
                source = "db"
            except DatabaseError:
                data = None
            
            # Verificar cobertura de datos
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            date_range = pd.date_range(start=start_dt, end=end_dt, freq='B')  # B for business days
            
            db_data = None
            api_data = None
            source = "db"
            
            # Intentar obtener datos de la base de datos
            if data:
                db_data = pd.DataFrame(data)
                db_data['date'] = pd.to_datetime(db_data['date'])
                db_data.set_index('date', inplace=True)
            
            # Verificar si necesitamos datos de la API
            missing_dates = []
            if db_data is not None:
                missing_dates = date_range.difference(db_data.index)
            else:
                missing_dates = date_range
            
            # Si faltan fechas, intentar obtener de la API
            if len(missing_dates) > 0:
                if status_callback:
                    status_callback(f"Obteniendo datos faltantes de {ticker} desde la API de Polygon.io...")
                
                try:
                    # Convertir las fechas al formato requerido por la API
                    api_start = missing_dates.min().strftime('%Y-%m-%d')
                    api_end = missing_dates.max().strftime('%Y-%m-%d')
                    
                    api_response = self.api.get_stock_data(ticker, api_start, api_end)
                    if api_response and api_response.get('results'):
                        # Guardar nuevos datos
                        self.model.save_ticker_data(ticker, api_response)
                        
                        # Convertir datos de la API a DataFrame
                        new_data = self.model.get_ticker_data(ticker, api_start, api_end)
                        if new_data:
                            api_data = pd.DataFrame(new_data)
                            api_data['date'] = pd.to_datetime(api_data['date'])
                            api_data.set_index('date', inplace=True)
                            source = "api"
                except (APIError, APIRateLimitError, APIConnectionError) as e:
                    # Si hay error con la API pero tenemos algunos datos, continuamos con advertencia
                    if db_data is not None:
                        raise InvalidDataError(f"No se pudieron obtener todos los datos: {str(e)}")
                    else:
                        raise APIError(f"Error al obtener datos de la API: {str(e)}")
            
            # Combinar datos de ambas fuentes si es necesario
            if db_data is not None and api_data is not None:
                df = pd.concat([db_data, api_data]).sort_index()
                df = df[~df.index.duplicated(keep='last')]  # Eliminar duplicados
                source = "mixed"
            elif db_data is not None:
                df = db_data
            elif api_data is not None:
                df = api_data
            else:
                return None
            
            # Verificar cobertura final y preparar resultado
            df.name = ticker
            missing_dates = date_range.difference(df.index)
            
            result = {
                'data': df,
                'source': source,
                'missing_dates': [d.strftime('%d/%m/%Y') for d in missing_dates] if len(missing_dates) > 0 else []
            }
            
            return result
            
        except (DatabaseError, APIError, InvalidDataError) as e:
            raise
        except Exception as e:
            raise ValueError(f"Error inesperado al obtener datos del ticker: {str(e)}")

    def get_company_name(self, ticker: str) -> Optional[str]:
        """
        Obtiene el nombre de la compañía para un ticker.
        
        Args:
            ticker (str): El ticker a consultar
            
        Returns:
            Optional[str]: Nombre de la compañía o None si no se encuentra
            
        Raises:
            APIError: Si hay un error al obtener los datos de la API
            InvalidDataError: Si los datos recibidos no tienen el formato esperado
        """
        try:
            details = self.api.get_ticker_details(ticker)
            if not details or 'results' not in details:
                raise InvalidDataError(f"Datos inválidos recibidos para el ticker {ticker}")
                
            name = details['results'].get('name')
            if not name:
                return None
                
            return name
        except (APIError, InvalidDataError) as e:
            raise
        except Exception as e:
            raise APIError(f"Error inesperado al obtener nombre de compañía: {str(e)}")

    def process_ticker_data(self, df_data: Tuple[pd.DataFrame, str]) -> Dict[str, Any]:
        """
        Procesa los datos del ticker para su visualización.
        
        Args:
            df_data (Tuple[pd.DataFrame, str]): Tupla con (DataFrame, source) donde source indica el origen de los datos
            
        Returns:
            Dict[str, Any]: Datos procesados para visualización
            
        Raises:
            ValueError: Si los datos de entrada son inválidos
            InvalidDataError: Si los datos no tienen el formato esperado
            APIError: Si hay error al obtener el nombre de la compañía
        """
        if df_data is None:
            raise ValueError("No se proporcionaron datos para procesar")
            
        if not isinstance(df_data, tuple) or len(df_data) != 2:
            raise ValueError("Formato de datos inválido")
            
        df, source = df_data
        
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise InvalidDataError("DataFrame vacío o inválido")
            
        try:
            # Validar que el DataFrame tenga las columnas necesarias
            required_columns = ['close', 'low', 'high', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise InvalidDataError(f"Faltan columnas requeridas en el DataFrame: {', '.join(missing_columns)}")
            
            # Obtener el ticker y nombre de la compañía
            ticker = df.name if hasattr(df, 'name') else None
            if not ticker and isinstance(df, pd.DataFrame):
                df.name = df.index.name
                ticker = df.index.name
                
            if not ticker:
                raise InvalidDataError("No se pudo determinar el ticker de los datos")
                
            try:
                company_name = self.get_company_name(ticker) if ticker else None
            except (APIError, InvalidDataError) as e:
                # Si hay error al obtener el nombre de la compañía, continuamos sin él
                company_name = None
            
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
            
        except (ValueError, InvalidDataError, APIError) as e:
            raise
        except Exception as e:
            raise InvalidDataError(f"Error al procesar datos del ticker: {str(e)}")

    def get_stored_tickers_summary(self) -> List[Dict[str, str]]:
        """
        Obtiene un resumen de todos los tickers almacenados
        
        Returns:
            List[Dict[str, str]]: Lista de tickers y sus rangos de fechas
            
        Raises:
            DatabaseError: Si hay un error al acceder a la base de datos
        """
        try:
            return self.model.get_stored_tickers()
        except Exception as e:
            raise DatabaseError(f"Error al obtener el resumen de tickers: {str(e)}")
        
    def delete_ticker_data(self, ticker: str) -> None:
        """
        Elimina todos los datos de un ticker específico
        
        Args:
            ticker (str): El ticker cuyos datos se eliminarán
            
        Raises:
            ValueError: Si el ticker es inválido
            DatabaseError: Si hay un error al eliminar los datos
        """
        is_valid, error_msg = self.validate_ticker(ticker)
        if not is_valid:
            raise ValueError(error_msg)
            
        try:
            self.model.delete_ticker_data(ticker)
        except Exception as e:
            raise DatabaseError(f"Error al eliminar los datos del ticker {ticker}: {str(e)}")
