# =========================
# IMPORTAR LIBRERÍAS
# =========================
import streamlit as st
import pandas as pd
import unicodedata
import plotly.express as px

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(page_title="Dashboard Servicios", layout="wide")

st.title("📊 Dashboard de Servicios Técnicos")

# =========================
# CARGAR DATOS
# =========================
@st.cache_data
def cargar_datos():
    df = pd.read_excel("Asignacion de Ingenieros.xlsx")
    return df

df = cargar_datos()

# =========================
# LIMPIEZA DE COLUMNAS
# =========================
df.columns = (
    df.columns
    .str.lower()
    .str.strip()
    .str.replace(' ', '_')
)

# =========================
# FUNCIÓN PARA QUITAR ACENTOS
# =========================
def quitar_acento(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    )

df['nombre'] = df['nombre'].apply(quitar_acento).str.title()
df['tipo_de_servicio'] = df['tipo_de_servicio'].apply(quitar_acento).str.upper()
df['cliente'] = df['cliente'].apply(quitar_acento).str.upper()

df['serie_del_equipo'] = df['serie_del_equipo'].astype(str).str.upper()
df['parte'] = df['parte'].astype(str).str.upper()

# =========================
# SEMANA ISO
# =========================
df['fecha'] = pd.to_datetime(df['fecha'])
df['semana'] = df['fecha'].dt.isocalendar().week

# =========================
# FILTRAR SERVICIOS VÁLIDOS
# =========================
servicios_validos = ['PREVENTIVO','CORRECTIVO','CAPACITACION','EVALUACION','SUMINISTRO','INSTALACION']

df_IS = df[df['tipo_de_servicio'].isin(servicios_validos)]
df_ISO = df_IS[df_IS['asignacion'] == 1]

# =========================
# SIDEBAR FILTROS
# =========================
st.sidebar.header("Filtros")

ingeniero = st.sidebar.selectbox(
    "👷 Ingeniero",
    sorted(df_ISO['nombre'].unique())
)

servicio = st.sidebar.selectbox(
    "🛠 Tipo de Servicio",
    servicios_validos
)

# =========================
# FILTRAR DATOS
# =========================
df_filtrado = df_ISO[
    (df_ISO['nombre'] == ingeniero) &
    (df_ISO['tipo_de_servicio'] == servicio)
].copy()

df_filtrado['fecha'] = df_filtrado['fecha'].dt.strftime('%d-%m-%Y')
df_filtrado=df_filtrado.drop(['nombre','tipo_de_servicio','asignacion'],axis=1)

st.subheader("📋 Servicios Encontrados")
st.dataframe(df_filtrado.drop(['semana'], axis=1))

# =========================
# GRÁFICA GENERAL
# =========================
df_group = (
    df_ISO
    .groupby(['nombre','tipo_de_servicio'])['serie_del_equipo']
    .count()
    .reset_index(name='conteo')
)

fig = px.bar(
    df_group,
    x='nombre',
    y='conteo',
    color='tipo_de_servicio',
    barmode='group',
    title='Servicios por Ingeniero',
    labels={
        'nombre':'Ingeniero',
        'conteo':'Cantidad de Servicios',
        'tipo_de_servicio':'Tipo de Servicio'
    }
)

st.plotly_chart(fig, use_container_width=True)
