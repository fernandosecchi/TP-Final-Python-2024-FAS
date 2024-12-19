# TP-Final-Python-2024-FAS

Proyecto final del curso del ITBA. Año 2024.

Alumno: Fernando Secchi

## Descripción

Esta aplicación permite analizar datos históricos de acciones utilizando la API de Polygon.io. Las principales funcionalidades incluyen:

- Consulta de datos históricos de acciones por ticker y rango de fechas
- Visualización de datos en gráficos de velas (candlestick) y líneas
- Almacenamiento local de datos para consultas futuras
- Resumen estadístico de los datos (precios promedio, máximos, mínimos, volumen)
- Sistema de gestión y mantenimiento de datos históricos
- Interfaz multi-página con navegación intuitiva

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

## Captura de Pantalla

### Página Principal (Nueva Consulta)
En esta vista, los usuarios pueden ingresar un símbolo de ticker (por ejemplo, AAPL) y seleccionar un rango de fechas para analizar los datos históricos de la acción.

### Historial de Consultas
La vista de historial muestra todas las consultas realizadas, permitiendo filtrar por ticker y ver estadísticas globales de las consultas realizadas.

### Mantenimiento de Base de Datos
En la sección de mantenimiento, se puede ver un resumen de los datos almacenados, incluyendo el total de tickers, rangos y datos en la base de datos local.

<video src="video/video.webm" controls>
Tu navegador no soporta la reproducción de este video.
</video>


## Características Principales

### 1. Página Principal (Nueva Consulta)
- Búsqueda de datos por símbolo de ticker
- Selector de rango de fechas personalizado
- Visualización de gráficos de velas (candlestick)
- Resumen estadístico detallado
- Indicador de fuente de datos (API o base de datos local)
- Manejo de errores y validaciones en tiempo real

### 2. Historial de Consultas
- Visualización de todas las consultas realizadas
- Filtrado por ticker
- Estadísticas globales de consultas
- Detalles específicos por ticker y período

### 3. Mantenimiento de Base de Datos
- Resumen general de datos almacenados
- Gestión de datos por ticker
- Funcionalidad de eliminación de datos
- Estadísticas de almacenamiento

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
│       ├── exceptions.py    # Manejo de excepciones personalizado
│       └── validators.py    # Validadores de datos
├── streamlit_app/
│   ├── app.py              # Aplicación Streamlit principal
│   ├── components/         # Componentes reutilizables
│   │   ├── date_selector.py
│   │   └── ticker_input.py
│   └── views/             # Vistas de la aplicación
│       ├── home_view.py
│       ├── historical_view.py
│       └── maintenance_view.py
├── main.py                # Punto de entrada principal
├── .env                   # Configuración de variables de entorno
└── requirements.txt       # Dependencias del proyecto
```

## Características Técnicas

- Arquitectura modular y escalable
- Sistema de caché local para optimizar consultas
- Manejo robusto de errores y excepciones
- Validación de datos en múltiples niveles
- Interfaz responsiva y amigable
- Visualizaciones interactivas de datos
- Sistema de almacenamiento persistente
- Gestión eficiente de recursos de API

## Extras Implementados

- Sistema multi-página con navegación intuitiva
- Visualización avanzada con gráficos de velas y líneas
- Almacenamiento local inteligente para consultas rápidas
- Sistema de caché para optimizar el uso de la API
- Resumen estadístico detallado de datos
- Manejo avanzado de errores y validaciones
- Interfaz de usuario moderna y responsiva
- Sistema de mantenimiento de datos integrado
- Estructura modular y organizada del proyecto

## Desarrollo

El proyecto está estructurado de manera modular, siguiendo las mejores prácticas de Python:

- `main.py`: Punto de entrada principal que configura el entorno y lanza la aplicación
- `src/`: Contiene la lógica de negocio y acceso a datos
- `streamlit_app/`: Contiene la interfaz de usuario y componentes visuales
- Separación clara de responsabilidades entre capas
- Código documentado y mantenible
