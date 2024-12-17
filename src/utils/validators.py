from datetime import datetime
from typing import Union, Tuple

def validate_dates(start_date: Union[str, datetime], 
                  end_date: Union[str, datetime]) -> bool:
    """
    Valida que las fechas tengan el formato correcto y que la fecha de inicio
    sea anterior a la fecha de fin.
    
    Args:
        start_date (Union[str, datetime]): Fecha de inicio
        end_date (Union[str, datetime]): Fecha de fin
        
    Returns:
        bool: True si las fechas son válidas, False en caso contrario
    """
    try:
        # Si las fechas son strings, convertirlas a datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
        # Verificar que la fecha de inicio sea anterior a la fecha de fin
        return start_date < end_date
    except (ValueError, TypeError):
        return False

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
