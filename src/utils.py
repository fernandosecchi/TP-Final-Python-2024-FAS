# Acá puedo poner las utilidades más conocidas
# Importo este módulo para poder validar las fechas
from datetime import datetime

def validar_fechas(self):
        try:
            # Intentar convertir las fechas a objetos datetime
            fecha_inicio_dt = datetime.strptime(self.fecha_inicio, "%Y/%m/%d")
            fecha_fin_dt = datetime.strptime(self.fecha_fin, "%Y/%m/%d")
            # Verificar que la fecha de inicio sea anterior a la fecha de fin
            if fecha_inicio_dt < fecha_fin_dt:
                return True
            else:
                print("La fecha de inicio debe ser anterior a la fecha de fin.")
                return False
        except ValueError:
            print("Formato de fecha inválido. Asegúrese de usar el formato YYYY/MM/DD.")
            return False
        
