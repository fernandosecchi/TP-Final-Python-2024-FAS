# TP-Final-Python-2024-FAS

Proyecto final del curso del ITBA. Año 2024.

Alumno: Fernando Secchi

## Descripción

Esta aplicación permite analizar datos históricos de acciones utilizando la API de Polygon.io. Las principales funcionalidades incluyen:

- Consulta de datos históricos de acciones por ticker y rango de fechas
- Visualización de datos en gráficos de velas (candlestick)
- Almacenamiento local de datos para consultas futuras
- Resumen estadístico de los datos (precios promedio, máximos, mínimos, volumen)

## Requisitos

- Python 3.8 o superior
- Una API key de Polygon.io (puedes obtenerla en https://polygon.io/)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/TP-Final-Python-2024-FAS.git
cd TP-Final-Python-2024-FAS
```

2. Crear y activar un entorno virtual:

```bash
conda create -n tp-final-2024-FAS python=3.8
conda activate tp-final-2024-FAS
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar la API key:
   - Renombrar el archivo `.env.example` a `.env`
   - Reemplazar `your_api_key_here` con tu API key de Polygon.io

## Uso

1. Iniciar la aplicación:

```bash
streamlit run streamlit-app/app.py
```

2. En el navegador:
   - Ingresar el símbolo del ticker (ej: AAPL, GOOGL)
   - Seleccionar el rango de fechas
   - Hacer clic en "Analizar"

## Estructura del Proyecto

```
TP-Final-Python-2024-FAS/
├── src/
│   ├── api_finanzas.py      # Cliente de la API de Polygon.io
│   ├── models/              # Modelos de datos
│   ├── services/            # Servicios de negocio
│   └── utils/               # Utilidades y validadores
├── streamlit-app/
│   ├── app.py              # Punto de entrada de la aplicación
│   ├── components/         # Componentes reutilizables
│   └── pages/             # Páginas de la aplicación
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
- Manejo de errores de red

## Instalación de las dependencias

```

pip install -r requirements.txt

```

## Cómo correr la aplicación

```

python ./src/app.py

```

### App terminal

### App Web
