import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from branca.colormap import linear
import leafmap
import zipfile
import os

# Para datos vectoriales
import geopandas as gpd

# Para datos raster
import rasterio

# Para gráficos
import matplotlib.pyplot as plt

# Para crear rampas de colores
from matplotlib.colors import LinearSegmentedColormap

# Para álgebra lineal
import numpy as np

# Para descargar archivos
import requests
import zipfile
# URLs de los datos
df_data = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/merged_data.csv'
df_transporte = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/transporte_aereo.csv'
df_pib = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/pib.csv'
df_partidas = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/partidas_vuelos.csv'
URL_DATOS_PAISES = 'datos/paises.gpkg'

# Título de la app
st.title("Transporte de viajes aéreos")

# Función para cargar los datos con caché
@st.cache_data
def cargar_datos(url):
    try:
        datos = pd.read_csv(url)
        return datos
    except Exception as e:
        st.error(f"Error al cargar los datos desde {url}: {e}")
        return None

#Función para cargar los datos de los países

@st.cache_data
def cargar_datos_paises():
    paises = gpd.read_file(URL_DATOS_PAISES)
    return paises

# Cargar los datos desde las URLs
datos = cargar_datos(df_data)
datos_pib = cargar_datos(df_pib)
datos_transporte = cargar_datos(df_transporte)
datos_partidas = cargar_datos(df_partidas)

# Validar que los datos se hayan cargado correctamente
if datos is None or datos_pib is None or datos_transporte is None or datos_partidas is None:
    st.stop()

# Renombrar columnas en `datos`
columnas_espaniol = {
    'SOVEREIGNT': 'País',
    'SOV_A3': 'Código ISO',
    'TYPE': 'Tipo',
    'LABEL_X': 'Coordenada x',
    'LABEL_Y': 'Coordenada y'
}
datos = datos.rename(columns=columnas_espaniol)

# Seleccionar columnas relevantes
columnas = ['País', 'Código ISO', 'Tipo', 'Coordenada x', 'Coordenada y']
datos = datos[columnas]

# Obtener la lista de países únicos
lista_paises = datos['País'].unique().tolist()
lista_paises.sort()

# Añadir la opción "Todos" al inicio de la lista
opciones_paises = ['Todos'] + lista_paises

# Crear el selectbox en la barra lateral
pais_seleccionado = st.sidebar.selectbox(
    'Selecciona un país',
    opciones_paises
)


# ----- Filtrar datos según la selección -----

if pais_seleccionado != 'Todos':
    # Filtrar los datos para el país seleccionado
    datos_filtrados = datos[datos['País'] == pais_seleccionado]
    # Obtener el Código ISO del país seleccionado
    codigo_iso_seleccionado = datos_filtrados['Código ISO'].iloc[0]
else:
    # No aplicar filtro
    datos_filtrados = datos.copy()
    codigo_iso_seleccionado = None


# Mostrar tabla de datos cargados
st.subheader("Datos de Interés")
st.dataframe(datos, hide_index=True)

# Crear gráfico de PIB global
if 'pais' in datos_transporte.columns:
    # Transformar datos de transporte a formato largo
    df_transporte_melted = datos_transporte.melt(id_vars=['pais'], var_name='Year', value_name='GDP')

    # Limpiar datos de transporte
    df_cleaned_t = df_transporte_melted.dropna(subset=['GDP'])
    df_cleaned_t['GDP'] = pd.to_numeric(df_cleaned_t['GDP'], errors='coerce')

    # Agrupar datos de transporte por año
    df_global_t = df_cleaned_t.groupby('Year')['GDP'].sum().reset_index()
    df_global_t['pais'] = 'Mundo'

    # Crear gráfico de línea para el transporte aéreo
    fig_transporte = px.line(
        df_global_t,
        x='Year',
        y='GDP',
        title='Transporte aéreo, pasajeros transportados',
        labels={'GDP': 'Pasajeros Transportados', 'Year': 'Año'}
    )

    # Mostrar el gráfico en Streamlit
    st.subheader('Transporte aéreo: pasajeros transportados a lo largo del tiempo')
    st.plotly_chart(fig_transporte)
else:
    st.error("Los datos de transporte no tienen la columna 'pais'. Verifica el archivo.")

# MAPA



# Definir el mapa base
mapa = None  # Inicializa la variable 'mapa'

# Si se ha seleccionado un país específico, se crea el mapa con un centro ajustado
if pais_seleccionado != 'Todos':
    mapa = folium.Map(location=[0, 0], zoom_start=2)  # Mapa por defecto centrado
else:
    mapa = folium.Map(location=[0, 0], zoom_start=2)  # Crear un mapa por defecto

# Mostrar el mapa
st.subheader('Mapa de casos totales por país')

# Mostrar el mapa en la interfaz de Streamlit
folium_static(mapa)

# Cargar los datos CSV
file_path = 'https://raw.githubusercontent.com/chrismse19/proyecto_progra/refs/heads/main/merged_data.csv'
merged_data = pd.read_csv(file_path)

