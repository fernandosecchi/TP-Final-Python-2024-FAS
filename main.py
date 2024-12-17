import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    """
    Punto de entrada principal de la aplicación.
    Configura el entorno y lanza la aplicación Streamlit.
    """
    try:
        # Carga variables de entorno
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

        # Directorio raíz del proyecto
        root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Asegurar que src sea reconocible para importaciones
        os.environ["PYTHONPATH"] = root_dir
        
        # Ruta a la aplicación Streamlit
        streamlit_app_path = os.path.join(root_dir, "streamlit_app", "app.py")
        
        print("Iniciando la aplicación Streamlit...")
        # Usar subprocess.run en lugar de os.system para mejor manejo de errores
        subprocess.run(["streamlit", "run", streamlit_app_path], check=True)
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo .env o la aplicación Streamlit")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar la aplicación Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAplicación terminada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
