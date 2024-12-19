from datetime import datetime, date
from typing import Union, Tuple

def validate_dates(start_date: Union[str, datetime, date], 
                  end_date: Union[str, datetime, date]) -> Tuple[bool, str]:
    """
    Valida que las fechas tengan el formato correcto, que la fecha de inicio
    sea anterior a la fecha de fin y que ninguna sea futura.
    
    Args:
        start_date (Union[str, datetime]): Fecha de inicio
        end_date (Union[str, datetime]): Fecha de fin
        
    Returns:
        Tuple[bool, str]: (True, "") si las fechas son válidas, 
                         (False, mensaje_error) en caso contrario
    """
    try:
        # Convertir fechas a datetime para comparación consistente
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                try:
                    start_date = datetime.strptime(start_date, "%d/%m/%Y")
                except ValueError:
                    return False, "Formato de fecha inválido para la fecha de inicio (use DD/MM/YYYY o YYYY-MM-DD)"
        elif isinstance(start_date, date):
            start_date = datetime.combine(start_date, datetime.min.time())
                    
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                try:
                    end_date = datetime.strptime(end_date, "%d/%m/%Y")
                except ValueError:
                    return False, "Formato de fecha inválido para la fecha de fin (use DD/MM/YYYY o YYYY-MM-DD)"
        elif isinstance(end_date, date):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Verificar que ninguna fecha sea futura
        if start_date.date() > current_date.date():
            return False, f"La fecha de inicio ({start_date.strftime('%d/%m/%Y')}) no puede ser futura. La fecha actual es {current_date.strftime('%d/%m/%Y')}"
        if end_date.date() > current_date.date():
            return False, f"La fecha de fin ({end_date.strftime('%d/%m/%Y')}) no puede ser futura. La fecha actual es {current_date.strftime('%d/%m/%Y')}"
            
        # Verificar que la fecha de inicio sea anterior a la fecha de fin
        if start_date >= end_date:
            return False, "La fecha de inicio debe ser anterior a la fecha de fin"
            
        return True, ""
    except (ValueError, TypeError):
        return False, "Formato de fecha inválido"

def validate_api_response(response: dict) -> Tuple[bool, str]:
    """
    Valida la respuesta de la API.
    
    Args:
        response (dict): Respuesta de la API
        
    Returns:
        Tuple[bool, str]: (True, "") si la respuesta es válida, 
                         (False, mensaje_error) en caso contrario
    """
    if not response:
        return False, "No se recibió respuesta de la API"
    
    # Aquí puedes agregar más validaciones específicas según
    # la estructura de respuesta de tu API
    
    return True, ""
