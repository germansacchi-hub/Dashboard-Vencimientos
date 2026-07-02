import requests
import streamlit as st
import pandas as pd
import datetime

# Configuración de la página del Dashboard
st.set_page_config(page_title="Dashboard Transporte Arce Hnos", page_icon="🚚", layout="wide")

st.title("🚚 Dashboard de Control Central - Transporte Arce Hnos")
st.markdown("Actualizado automáticamente desde Google Sheets.")

# --- CARGA DE DATOS DESDE TU REPOSITORIO DE GITHUB ---
@st.cache_data(ttl=60) # Se limpia rápido para pruebas
def cargar_datos(nombre_archivo):
    url = f"https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/{nombre_archivo}"
    # Leemos especificando que use codificación UTF-8 estándar
    return pd.read_csv(url)

# Intentar cargar el archivo CSV
try:
    df_vencimientos = cargar_datos("datos_vencimientos.csv")
except Exception as e:
    df_vencimientos = None
    st.error(f"Error al cargar el archivo: {e}")

# --- DISEÑO DEL DASHBOARD EN PESTAÑAS (TABS) ---
tab1, tab2, tab3 = st.tabs(["⚠️ Vencimientos y Alertas", "🚛 Control de Flota", "👤 Personal / Choferes"])

# --- PESTAÑA 1: VENCIMIENTOS ---
with tab1:
    st.header("Control de Alertas Diario (RTO)")
    if df_vencimientos is not None:
        # Métricas rápidas en tarjetas
        col1, col2 = st.columns(2)
        total_docs = len(df_vencimientos)
        col1.metric("Total Patentes/Unidades Monitoreadas", total_docs)
        
        # Buscador interactivo
        buscar = st.text_input("🔍 Buscar por Patente (Entidad) o Documento:")
        if buscar:
            df_filtrado = df_vencimientos[df_vencimientos.astype(str).apply(lambda x: x.str.contains(buscar, case=False)).any(axis=1)]
        else:
            df_filtrado = df_vencimientos
            
        # Mostrar la tabla estilizada con tus datos reales
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Esperando el archivo 'datos_vencimientos.csv' desde Google Sheets...")

# --- PESTAÑA 2: FLOTA ---
with tab2:
    st.header("🔧 Gestión de Mantenimiento")
    
    # 1. URL de tu nuevo archivo en GitHub (con el truco anti-caché para leer en tiempo real)
    url_mantenimiento = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_mantenimiento.csv?nocache=' + str(pd.Timestamp.now().timestamp())
    
    # Intentamos leer el archivo de GitHub
    try:
        df_mantenimiento = pd.read_csv(url_mantenimiento)
    except Exception as e:
        df_mantenimiento = pd.DataFrame()

    # 2. Dividimos la pantalla: Izquierda (Tabla) y Derecha (Formulario)
    col_tabla, col_form = st.columns([2, 1])
    
    # --- LADO IZQUIERDO: VER LOS DATOS ---
    with col_tabla:
        st.subheader("📋 Historial y Estado Actual")
        
        if not df_mantenimiento.empty:
            st.dataframe(df_mantenimiento, use_container_width=True)
        else:
            st.info("La tabla está vacía. ¡Agrega tu primer mantenimiento a la derecha!")

    # --- LADO DERECHO: FORMULARIO ---
    with col_form:
        st.subheader("✏️ Registrar Nuevo")
        
        with st.form("form_mantenimiento", clear_on_submit=True):
            tipo = st.text_input("Tipo")
            vehiculo = st.text_input("Veh/Maq")
            plan = st.text_input("Plan")
            tarea = st.text_input("Tarea/Documento")
            estado = st.selectbox("Estado", ["Pendiente", "En proceso", "Finalizado"])
            
            btn_guardar = st.form_submit_button("💾 Guardar Mantenimiento")
            
            if btn_guardar:
                datos_a_enviar = {
                    "tipo": tipo,
                    "vehiculo": vehiculo,
                    "plan": plan,
                    "tarea": tarea,
                    "estado": estado
                }
                
                url_webhook = st.secrets["APPS_SCRIPT_WEBAPP_URL"]
                
                with st.spinner("Enviando a Google Sheets y actualizando..."):
                    respuesta = requests.post(url_webhook, json=datos_a_enviar)
                    
                    if respuesta.status_code == 200:
                        st.success("✅ ¡Guardado con éxito!")
                        st.info("🔄 Refresca la página web en un momento para ver la tabla actualizada.")
                    else:
                        st.error("❌ Hubo un problema al enviar los datos.")
