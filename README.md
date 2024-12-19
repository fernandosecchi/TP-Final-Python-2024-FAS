# TP-Final-Python-2024-FAS

Proyecto final del curso del ITBA. Año 2024.

Alumno: Fernando Secchi

## Descripción

Esta aplicación permite analizar datos históricos de acciones utilizando la API de Polygon.io. Las principales funcionalidades incluyen:

- Consulta de datos históricos de acciones por ticker y rango de fechas
- Visualización de datos en gráficos de velas (candlestick)
- Almacenamiento local de datos para consultas futuras
- Resumen estadístico de los datos (precios promedio, máximos, mínimos, volumen)

## Requisitos del Sistema

### Python

- Versión: Python 3.10.13
- Se recomienda usar esta versión específica para evitar problemas de compatibilidad

### Dependencias Principales

- pandas==2.2.3: Para el manejo y análisis de datos
- plotly==5.20.0: Para la visualización de gráficos interactivos
- python-dotenv==1.0.1: Para la gestión de variables de entorno
- requests==2.31.0: Para realizar llamadas a la API
- streamlit==1.40.2: Para la interfaz web

### API Key

- Una API key de Polygon.io (puedes obtenerla en https://polygon.io/)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/TP-Final-Python-2024-FAS.git
cd TP-Final-Python-2024-FAS
```

2. Crear y activar un entorno virtual:

```bash
# Usando conda
conda create -n tp-final-2024-FAS python=3.10.13
conda activate tp-final-2024-FAS

# O usando venv (alternativa)
python -m venv venv
source venv/bin/activate  # En Linux/Mac
.\venv\Scripts\activate   # En Windows
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar la API key:
   - Renombrar el archivo `.env.example` a `.env`
   - Reemplazar `your_api_key_here` con tu API key de Polygon.io

## Uso

Para iniciar la aplicación, simplemente ejecuta:

```bash
python main.py
```

Esto iniciará la aplicación Streamlit y abrirá automáticamente tu navegador predeterminado. Si no se abre automáticamente, puedes acceder a la aplicación en:

- URL Local: http://localhost:8501

En la interfaz web:

1. Ingresa el símbolo del ticker (ej: AAPL, GOOGL)
2. Selecciona el rango de fechas
3. Haz clic en "Analizar"

## Estructura del Proyecto

```
TP-Final-Python-2024-FAS/
├── src/
│   ├── api/
│   │   └── api_finanzas.py    # Cliente de la API de Polygon.io
│   ├── models/                # Modelos de datos
│   │   └── ticker_model.py
│   ├── services/             # Servicios de negocio
│   │   └── ticker_service.py
│   └── utils/               # Utilidades y validadores
│       └── validators.py
├── streamlit_app/
│   ├── app.py              # Aplicación Streamlit
│   ├── components/         # Componentes reutilizables
│   │   ├── date_selector.py
│   │   └── ticker_input.py
│   └── pages/             # Páginas de la aplicación
│       └── home.py
├── main.py                # Punto de entrada principal
├── .env                   # Configuración de variables de entorno
└── requirements.txt       # Dependencias del proyecto
```

## Características

- Interfaz web intuitiva con Streamlit
- Gráficos interactivos con Plotly
- Almacenamiento local en SQLite
- Manejo de errores y validaciones
- Visualización de datos históricos

## Extras Implementados

- Visualización avanzada con gráficos de velas
- Almacenamiento local para consultas rápidas
- Resumen estadístico de datos
- Manejo de errores de red y validaciones
- Punto de entrada unificado (main.py) con manejo de errores
- Estructura modular y organizada del proyecto

## Desarrollo

El proyecto está estructurado de manera modular, siguiendo las mejores prácticas de Python:

- `main.py`: Punto de entrada principal que configura el entorno y lanza la aplicación
- `src/`: Contiene la lógica de negocio y acceso a datos
- `streamlit_app/`: Contiene la interfaz de usuario y componentes visuales