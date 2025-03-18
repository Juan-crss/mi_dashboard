import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

# Verificar si el archivo CSV existe
file_path = "base prueba bi mid (1).csv"
if not os.path.exists(file_path):
    st.error("⚠️ El archivo CSV no se encuentra en la carpeta actual. Verifica la ruta del archivo.")
    st.stop()

# Cargar datos
try:
    df = pd.read_csv(file_path, encoding="latin1")
    st.success("✅ Archivo CSV cargado correctamente.")
except Exception as e:
    st.error(f"⚠️ Error al cargar el archivo CSV: {e}")
    st.stop()

# Estandarizar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# Verificar si existen las columnas requeridas
required_columns = {"nombre_cliente", "precio", "latitud", "longitud"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    st.error(f"⚠️ Faltan las siguientes columnas en el dataset: {missing_columns}")
    st.stop()

# Eliminar valores nulos en columnas críticas
df = df.dropna(subset=["nombre_cliente", "precio", "latitud", "longitud"])

# Corregir problemas de codificación en nombres de clientes
df["nombre_cliente"] = df["nombre_cliente"].apply(lambda x: x.encode('latin1').decode('utf-8') if isinstance(x, str) else x)

# Título del Dashboard
st.markdown("## 📊 **Dashboard de Precios de Venta**")
st.markdown("### 📍 Análisis por Cliente y Zona Geográfica")

# Barra lateral para filtros
st.sidebar.header("🔍 Filtros")
clientes = sorted(df["nombre_cliente"].unique().tolist())
clientes_seleccionados = st.sidebar.multiselect("Selecciona uno o varios Clientes:", clientes)

# Filtrar datos por clientes seleccionados
df_cliente = df if not clientes_seleccionados else df[df["nombre_cliente"].isin(clientes_seleccionados)]

# Gráfico de precios por cliente (ordenado de mayor a menor precio promedio)
df_agg = df_cliente.groupby("nombre_cliente", as_index=False)["precio"].mean()
df_agg = df_agg.sort_values(by="precio", ascending=False)

st.subheader("💰 Precio Promedio de Venta por Cliente")
fig1 = px.bar(df_agg, x="nombre_cliente", y="precio",
              title="Precio Promedio de Venta por Cliente",
              labels={"precio": "Precio Promedio ($)", "nombre_cliente": "Cliente"},
              color="precio",
              color_continuous_scale="Blues",
              template="plotly_white")

fig1.update_layout(xaxis_title="", yaxis_title="Precio Promedio ($)", height=400)
st.plotly_chart(fig1, use_container_width=True)

# Filtrar datos de Colombia y aplicar filtro de cliente
df_colombia = df_cliente[(df_cliente["latitud"].between(-4.5, 13.5)) & (df_cliente["longitud"].between(-81.7, -66.8))]

# Reducir puntos en el mapa si hay demasiados datos
if len(df_colombia) > 5000:
    df_colombia = df_colombia.sample(5000, random_state=42)

# Mapa de calor de precios en Colombia
st.subheader("🌎 Mapa de Precios por Zona en Colombia")
fig2 = px.scatter_mapbox(df_colombia, lat="latitud", lon="longitud", size="precio",
                         color="precio", hover_name="nombre_cliente",
                         color_continuous_scale="Blues",
                         mapbox_style="carto-darkmatter", zoom=5,
                         title="Mapa de Precios por Zona en Colombia")

fig2.update_layout(height=600, margin={"r":0, "t":50, "l":0, "b":0})
st.plotly_chart(fig2, use_container_width=True)

# Pie de página
st.markdown("---")
st.markdown("📌 **Presentación ejecutiva generada con Streamlit y Plotly**")