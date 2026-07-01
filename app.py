import streamlit as st
import pandas as pd
import datetime

# Configuración de la página del Dashboard
st.set_page_config(page_title="Dashboard Transporte Arce Hnos", page_icon="🚚", layout="wide")

st.title("🚚 Dashboard de Control Central - Transporte Arce Hnos")
st.markdown("Actualizado automáticamente desde Google Sheets.")

# --- CARGA DE DATOS DESDE TU REPOSITORIO DE GITHUB ---
@st.cache_data(ttl=600) # Se actualiza cada 10 minutos si hay cambios
def cargar_datos(nombre_archivo):
    url = f"https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/{nombre_archivo}"
    return pd.read_csv(url)

# Intentar cargar los archivos CSV (si aún no existen, mostrará un aviso amigable)
try:
    df_vencimientos = cargar_datos("datos_vencimientos.csv")
except:
    df_vencimientos = None

try:
    df_flota = cargar_datos("datos_flota.csv")
except:
    df_flota = None


# --- DISEÑO DEL DASHBOARD EN PESTAÑAS (TABS) ---
tab1, tab2, tab3 = st.tabs(["⚠️ Vencimientos y Alertas", "🚛 Control de Flota", "👤 Personal / Choferes"])

# --- PESTAÑA 1: VENCIMIENTOS ---
with tab1:
    st.header("Control de Alertas Diario")
    if df_vencimientos is not None:
        # Métricas rápidas en tarjetas
        col1, col2, col3 = st.columns(3)
        total_docs = len(df_vencimientos)
        
        col1.metric("Total Documentos Monitoreados", total_docs)
        col2.metric("Alertas Activas hoy", "Revisar Correo") 
        
        # Buscador interactivo
        buscar = st.text_input("🔍 Buscar por Entidad o Documento:")
        if buscar:
            df_filtrado = df_vencimientos[df_vencimientos.astype(str).apply(lambda x: x.str.contains(buscar, case=False)).any(axis=1)]
        else:
            df_filtrado = df_vencimientos
            
        # Mostrar la tabla estilizada
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Esperando el archivo 'datos_vencimientos.csv' desde Google Sheets...")

# --- PESTAÑA 2: FLOTA ---
with tab2:
    st.header("Información de Camiones y Semirremolques")
    if df_flota is not None:
        st.dataframe(df_flota, use_container_width=True)
    else:
        st.info("Aquí aparecerán los datos de la flota cuando configures el archivo 'datos_flota.csv'")

# --- PESTAÑA 3: CHOFERES ---
with tab3:
    st.header("Legajos de Choferes")
    st.write("Espacio destinado para licencias, altas tempranas y vencimientos particulares.")
