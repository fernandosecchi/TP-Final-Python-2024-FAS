import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os
from src.utils.exceptions import (
    DatabaseError, DatabaseConnectionError, DatabaseAccessError,
    InvalidDataError, DataValidationError
)


class TickerModel:
    """
    Modelo para manejar las operaciones de base de datos relacionadas con los tickers
    """
    def __init__(self, db_path: str = "data/tickers.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Inicializa la base de datos y crea las tablas necesarias
        
        Raises:
            DatabaseAccessError: Si no se puede acceder o crear el directorio de la base de datos
            DatabaseConnectionError: Si hay un error al conectar con la base de datos
        """
        if not os.path.exists(os.path.dirname(self.db_path)):
            try:
                os.makedirs(os.path.dirname(self.db_path))
            except OSError as e:
                raise DatabaseAccessError(f"No se pudo crear el directorio de la base de datos: {str(e)}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla para almacenar los datos históricos de los tickers
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticker_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        date TEXT NOT NULL,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        vwap REAL,
                        UNIQUE(ticker, date)
                    )
                ''')
                
                # Tabla para almacenar los rangos de fechas por ticker
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticker_ranges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        start_date INTEGER NOT NULL,
                        end_date INTEGER NOT NULL,
                        created_at INTEGER NOT NULL,
                        UNIQUE(ticker, start_date, end_date)
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Error al conectar con la base de datos: {str(e)}")

    def save_ticker_data(self, ticker: str, data: Dict[str, Any]) -> bool:
        """
        Guarda los datos del ticker en la base de datos
        
        Args:
            ticker (str): Símbolo del ticker
            data (Dict[str, Any]): Datos a guardar
            
        Returns:
            bool: True si los datos se guardaron correctamente
            
        Raises:
            InvalidDataError: Si los datos son inválidos o están corruptos
            DatabaseError: Si hay un error en la base de datos
            DataValidationError: Si los datos no cumplen con el formato esperado
        """
        # Validar entrada
        if not data or not isinstance(data, dict):
            raise InvalidDataError("Los datos proporcionados son inválidos o están vacíos")
            
        # Validar que existan resultados
        if not data.get('results'):
            raise InvalidDataError("No hay resultados en los datos proporcionados")
            
        if not isinstance(data['results'], list) or len(data['results']) == 0:
            raise InvalidDataError("El formato de los resultados es inválido o está vacío")
            
        # Validar estructura de datos
        required_fields = ['t', 'o', 'h', 'l', 'c', 'v', 'vw']
        for result in data['results']:
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                raise DataValidationError(f"Faltan campos requeridos en los datos: {', '.join(missing_fields)}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Preparar los datos para inserción masiva
            data_to_insert = []
            for result in data['results']:
                timestamp = result['t']  # Ya está en milisegundos
                date_str = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')
                
                # Verificar si ya existe un registro para esta fecha
                cursor.execute('''
                    SELECT id FROM ticker_data 
                    WHERE ticker = ? AND date = ?
                ''', (ticker, date_str))
                
                if not cursor.fetchone():
                    # Solo agregar si no existe
                    data_to_insert.append((
                        ticker,
                        date_str,
                        result.get('o'),
                        result.get('h'),
                        result.get('l'),
                        result.get('c'),
                        result.get('v'),
                        result.get('vw')
                    ))
            
            # Insertar todos los nuevos datos de una vez
            if data_to_insert:
                cursor.executemany('''
                    INSERT INTO ticker_data 
                    (ticker, date, open, high, low, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', data_to_insert)
            
            try:
                # Calcular el rango de fechas correcto iterando sobre todos los resultados
                results = data['results']
                
                # Validar que cada resultado tenga un timestamp válido
                timestamps = []
                for result in results:
                    if 't' not in result:
                        raise InvalidDataError(f"Resultado sin timestamp encontrado: {result}")
                    try:
                        timestamps.append(int(result['t']))
                    except (ValueError, TypeError) as e:
                        raise InvalidDataError(f"Error al convertir timestamp: {result['t']}, Error: {str(e)}")
                
                if not timestamps:
                    raise InvalidDataError("No se encontraron timestamps válidos en los resultados")
                
                # Calcular el rango de fechas usando los timestamps válidos
                new_start = min(timestamps)  # Encontrar el timestamp más antiguo
                new_end = max(timestamps)    # Encontrar el timestamp más reciente
                current_time = int(datetime.now().timestamp() * 1000)  # Timestamp actual en milisegundos
                
                # Insertar el nuevo rango de fechas
                cursor.execute('''
                    INSERT OR IGNORE INTO ticker_ranges 
                    (ticker, start_date, end_date, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    ticker,
                    new_start,
                    new_end,
                    current_time
                ))
                
                conn.commit()
                return True
                
            except (KeyError, IndexError, ValueError, TypeError) as e:
                raise DataValidationError(f"Error al procesar datos del ticker {ticker}: {str(e)}")
            except sqlite3.Error as e:
                raise DatabaseError(f"Error de base de datos al guardar datos del ticker {ticker}: {str(e)}")
            except Exception as e:
                raise DatabaseError(f"Error inesperado al guardar datos del ticker {ticker}: {str(e)}")

    def get_ticker_data(self, ticker: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene los datos del ticker para un rango de fechas
        
        Args:
            ticker (str): Símbolo del ticker
            start_date (str): Fecha de inicio en formato YYYY-MM-DD
            end_date (str): Fecha de fin en formato YYYY-MM-DD
            
        Returns:
            Optional[List[Dict[str, Any]]]: Lista de datos o None si no hay datos
            
        Raises:
            DatabaseError: Si hay un error al acceder a la base de datos
            DataValidationError: Si las fechas no tienen el formato correcto
        """
        try:
            # Validar formato de fechas
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError as e:
                raise DataValidationError(f"Formato de fecha inválido: {str(e)}")
                
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM ticker_data
                    WHERE ticker = ? 
                    AND date BETWEEN ? AND ?
                    ORDER BY date ASC
                ''', (
                    ticker,
                    start_date,
                    end_date
                ))
                
                rows = cursor.fetchall()
                if not rows:
                    return None
                    
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Error al acceder a la base de datos: {str(e)}")

    def get_stored_tickers(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen detallado de todos los tickers almacenados y sus rangos de fechas
        
        Returns:
            List[Dict[str, Any]]: Lista de tickers con sus rangos de fechas ordenados cronológicamente
            
        Raises:
            DatabaseError: Si hay un error al acceder a la base de datos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Obtener todos los tickers únicos
                cursor.execute('SELECT DISTINCT ticker FROM ticker_ranges ORDER BY ticker')
                tickers = [row['ticker'] for row in cursor.fetchall()]
                
                result = []
                for ticker in tickers:
                    # Obtener todos los rangos para este ticker
                    cursor.execute('''
                        SELECT 
                            start_date,
                            end_date,
                            created_at,
                            (
                                SELECT COUNT(*)
                                FROM ticker_data td
                                WHERE td.ticker = tr.ticker
                                AND td.date BETWEEN datetime(tr.start_date/1000, 'unixepoch')
                                AND datetime(tr.end_date/1000, 'unixepoch')
                            ) as data_points
                        FROM ticker_ranges tr
                        WHERE ticker = ?
                        ORDER BY created_at DESC
                    ''', (ticker,))
                    
                    ranges = []
                    for row in cursor.fetchall():
                        # Convertir timestamps a fechas legibles
                        start_date = datetime.fromtimestamp(row['start_date']/1000).strftime('%Y-%m-%d')
                        end_date = datetime.fromtimestamp(row['end_date']/1000).strftime('%Y-%m-%d')
                        created_at = datetime.fromtimestamp(row['created_at']/1000).strftime('%Y-%m-%d %H:%M:%S')
                        
                        ranges.append({
                            'start_date': start_date,
                            'end_date': end_date,
                            'created_at': created_at,
                            'data_points': row['data_points']
                        })
                    
                    result.append({
                        'ticker': ticker,
                        'ranges': ranges,
                        'total_ranges': len(ranges),
                        'total_data_points': sum(r['data_points'] for r in ranges)
                    })
                
                return result
                
        except sqlite3.Error as e:
            raise DatabaseError(f"Error al obtener los tickers almacenados: {str(e)}")
            
    def delete_ticker_data(self, ticker: str) -> None:
        """
        Elimina todos los datos de un ticker específico
        
        Args:
            ticker (str): El ticker cuyos datos se eliminarán
            
        Raises:
            DatabaseError: Si hay un error al eliminar los datos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Eliminar datos históricos
                cursor.execute('DELETE FROM ticker_data WHERE ticker = ?', (ticker,))
                
                # Eliminar registro del rango de fechas
                cursor.execute('DELETE FROM ticker_ranges WHERE ticker = ?', (ticker,))
                
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error al eliminar los datos del ticker {ticker}: {str(e)}")
