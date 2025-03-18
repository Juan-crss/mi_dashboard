import os
import pandas as pd
import plotly.express as px
import streamlit as st
from geopy.distance import geodesic
import unicodedata

# 📌 Configuración de la página
st.set_page_config(page_title="Dashboard de Operaciones", layout="wide")

# 📌 Verificar si el archivo CSV existe
file_path = "base prueba bi mid (1).csv"
if not os.path.exists(file_path):
    st.error("⚠️ El archivo CSV no se encuentra en la carpeta actual. Verifica la ruta.")
    st.stop()

# 📌 Cargar datos
try:
    df = pd.read_csv(file_path, encoding="latin1")
    st.success("✅ Archivo CSV cargado correctamente.")
except Exception as e:
    st.error(f"⚠️ Error al cargar el archivo CSV: {e}")
    st.stop()

# 📌 Estandarizar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# 📌 Verificar si existen las columnas requeridas
required_columns = {"latitud", "longitud", "nombre_cliente", "precio"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    st.error(f"⚠️ Faltan columnas en el dataset: {missing_columns}")
    st.stop()

# 📌 Eliminar valores nulos en columnas críticas
df = df.dropna(subset=["latitud", "longitud", "nombre_cliente", "precio"])

# 📌 Normalizar nombres de clientes (corrección de tildes y caracteres especiales)
def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) if unicodedata.category(c) != 'Mn')

df["nombre_cliente"] = df["nombre_cliente"].apply(normalize_text)

# 📌 Título del Dashboard
st.markdown("## 📌 **Dashboard para Equipo de Operaciones**")
st.markdown("### 🏡 Propiedades Publicadas en un Radio de 500m")

# 📌 Barra lateral para ingresar coordenadas
st.sidebar.header("📍 Introduce una Ubicación")
latitud_input = st.sidebar.number_input("Latitud", min_value=-90.0, max_value=90.0, value=4.6097, step=0.0001, format="%.4f")
longitud_input = st.sidebar.number_input("Longitud", min_value=-180.0, max_value=180.0, value=-74.0817, step=0.0001, format="%.4f")

# 📌 Función para calcular distancia Haversine
def filtrar_propiedades(lat, lon, df, radio_km=0.5):
    coord_central = (lat, lon)
    df["distancia_km"] = df.apply(lambda row: geodesic(coord_central, (row["latitud"], row["longitud"])).km, axis=1)
    return df[df["distancia_km"] <= radio_km]

# 📌 Filtrar propiedades dentro de 500m
df_filtrado = filtrar_propiedades(latitud_input, longitud_input, df)

# 📌 Mostrar el número de propiedades encontradas
st.info(f"🔎 Se encontraron **{len(df_filtrado)}** propiedades en un radio de 500m.")

# 📌 Mapa interactivo con propiedades filtradas
st.subheader("🌎 Mapa de Propiedades Cercanas")
fig = px.scatter_mapbox(df_filtrado, lat="latitud", lon="longitud", 
                        size="precio", color="precio", hover_name="nombre_cliente",
                        color_continuous_scale="Greens", zoom=15,
                        mapbox_style="carto-positron",
                        title="Propiedades en un Radio de 500m")

fig.update_layout(height=600, margin={"r":0, "t":50, "l":0, "b":0})
st.plotly_chart(fig, use_container_width=True)

# 📌 Tabla con características de las propiedades
st.subheader("📋 Listado de Propiedades Cercanas")
st.dataframe(df_filtrado[["nombre_cliente", "precio", "latitud", "longitud", "distancia_km"]])

# 📌 Pie de página
st.markdown("---")
st.markdown("📌 **Dashboard creado con Streamlit y Plotly**")
