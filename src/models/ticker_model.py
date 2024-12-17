import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class TickerModel:
    """
    Modelo para manejar las operaciones de base de datos relacionadas con los tickers
    """
    def __init__(self, db_path: str = "data/tickers.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
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
            
            # Tabla para almacenar el rango de fechas por ticker (usando timestamps en milisegundos)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticker_ranges (
                    ticker TEXT PRIMARY KEY,
                    start_date INTEGER NOT NULL,
                    end_date INTEGER NOT NULL
                )
            ''')
            
            conn.commit()

    def save_ticker_data(self, ticker: str, data: Dict[str, Any]):
        """
        Guarda los datos del ticker en la base de datos
        
        Args:
            ticker (str): Símbolo del ticker
            data (Dict[str, Any]): Datos a guardar
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Guardar cada punto de datos
            for result in data['results']:
                timestamp = result['t']  # Ya está en milisegundos
                date_str = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')
                cursor.execute('''
                    INSERT OR REPLACE INTO ticker_data 
                    (ticker, date, open, high, low, close, volume, vwap)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    date_str,
                    result.get('o'),
                    result.get('h'),
                    result.get('l'),
                    result.get('c'),
                    result.get('v'),
                    result.get('vw')
                ))
            
            # Actualizar o insertar el rango de fechas usando timestamps en milisegundos
            start_timestamp = data['results'][0]['t']  # Ya está en milisegundos
            end_timestamp = data['results'][-1]['t']   # Ya está en milisegundos
            
            cursor.execute('''
                INSERT OR REPLACE INTO ticker_ranges (ticker, start_date, end_date)
                VALUES (?, ?, ?)
            ''', (
                ticker,
                start_timestamp,
                end_timestamp
            ))
            
            conn.commit()

    def get_ticker_data(self, ticker: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene los datos del ticker para un rango de fechas
        
        Args:
            ticker (str): Símbolo del ticker
            start_date (datetime): Fecha de inicio
            end_date (datetime): Fecha de fin
            
        Returns:
            Optional[List[Dict[str, Any]]]: Lista de datos o None si no hay datos
        """
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

    def get_stored_tickers(self) -> List[Dict[str, str]]:
        """
        Obtiene un resumen de todos los tickers almacenados y sus rangos de fechas
        
        Returns:
            List[Dict[str, str]]: Lista de tickers y sus rangos
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM ticker_ranges ORDER BY ticker')
            
            return [dict(row) for row in cursor.fetchall()]
