
# Importo este módulo para poder usar expresiones regulares y verifdicar el ticker
import re
# Importo desde utils las fechas
from utils import validar_fechas

# Creo una clase para la aplicación
class TickerApp:
    def __init__(self):
        self.ticker = ""
        self.fecha_inicio = ""
        self.fecha_fin = ""

    def solicitar_ticker(self):
        self.ticker = input("Ingrese ticker a pedir: ")
        if not self.validar_ticker(self.ticker):
            print("Ticker inválido. Asegúrese de que tenga entre 1 y 5 letras mayúsculas.")
            return False
        return True

    def validar_ticker(self, ticker):
        # Verificar que no esté vacío
        if not ticker:
            return False
        # Verificar longitud (1 a 5 caracteres) y que solo contenga letras mayúsculas
        if 1 <= len(ticker) <= 5 and re.match("^[A-Z]+$", ticker):
            return True
        return False

    def solicitar_fechas(self):
        self.fecha_inicio = input("Ingrese fecha de inicio (YYYY/MM/DD): ")
        self.fecha_fin = input("Ingrese fecha de fin (YYYY/MM/DD): ")
        # Validar las fechas usando la función de utils
        if not validar_fechas(self.fecha_inicio, self.fecha_fin):
            print("Fechas inválidas. Asegúrese de que la fecha de inicio sea anterior a la fecha de fin y que estén en el formato correcto.")
            return False
        return True

    

    def mostrar_datos(self):
        print(f"Ticker solicitado: {self.ticker}")
        print(f"Fecha de inicio: {self.fecha_inicio}")
        print(f"Fecha de fin: {self.fecha_fin}")

    def verificar_datos(self):
        if self.fecha_inicio and self.fecha_fin:
            print("Los datos se han ingresado correctamente.")
        else:
            print("Por favor, complete todos los campos.")

    def ejecutar(self):
        if self.solicitar_ticker():
            self.solicitar_fechas()
            self.mostrar_datos()
            self.verificar_datos()

# Crear una instancia de la aplicación y ejecutarla
if __name__ == "__main__":
    app = TickerApp()
    app.ejecutar()