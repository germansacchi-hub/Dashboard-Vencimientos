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

# =========================================================
# PESTAÑA 2: GESTIÓN DE MANTENIMIENTO (CON FILTROS AVANZADOS)
# =========================================================
with tab2:
    st.header("🔧 Gestión de Mantenimiento")
    
    url_mantenimiento = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_mantenimiento.csv?nocache=' + str(pd.Timestamp.now().timestamp())
    
    try:
        df_mantenimiento = pd.read_csv(url_mantenimiento)
    except Exception as e:
        df_mantenimiento = pd.DataFrame()

    col_tabla, col_form = st.columns([2, 1])
    
    with col_tabla:
        st.subheader("📋 Historial y Estado Actual")
        
        if not df_mantenimiento.empty:
            # FILTROS AVANZADOS POR SELECCIÓN ÚNICA
            st.markdown("##### 🔍 Filtrar datos")
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                # Extrae los tipos únicos y añade opción "Todos"
                lista_tipos = ["Todos"] + sorted(df_mantenimiento['Tipo'].dropna().unique().tolist())
                tipo_seleccionado = st.selectbox("Seleccionar 1 Tipo/Entidad:", lista_tipos)
                
            with col_f2:
                # Extrae los vehículos únicos y añade opción "Todos"
                lista_veh = ["Todos"] + sorted(df_mantenimiento['Veh/Maq'].dropna().unique().tolist())
                veh_seleccionado = st.selectbox("Seleccionar 1 Vehículo/Maquinaria:", lista_veh)
            
            # Aplicar filtros al DataFrame original
            df_mantenimiento_filtrado = df_mantenimiento.copy()
            if tipo_seleccionado != "Todos":
                df_mantenimiento_filtrado = df_mantenimiento_filtrado[df_mantenimiento_filtrado['Tipo'] == tipo_seleccionado]
            if veh_seleccionado != "Todos":
                df_mantenimiento_filtrado = df_mantenimiento_filtrado[df_mantenimiento_filtrado['Veh/Maq'] == veh_seleccionado]
                
            # Desplegar la tabla filtrada
            st.dataframe(df_mantenimiento_filtrado, use_container_width=True)
        else:
            st.info("La tabla está vacía o no se encuentra el archivo en GitHub.")

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
                datos_a_enviar = {"tipo": tipo, "vehiculo": vehiculo, "plan": plan, "tarea": tarea, "estado": estado}
                url_webhook = st.secrets["APPS_SCRIPT_WEBAPP_URL"]
                
                with st.spinner("Enviando a Google Sheets..."):
                    respuesta = requests.post(url_webhook, json=datos_a_enviar)
                    if respuesta.status_code == 200:
                        st.success("✅ ¡Guardado con éxito!")
                        st.info("🔄 Refresca la página en un minuto para ver los cambios.")
                    else:
                        st.error("❌ Hubo un problema al enviar los datos.")


# =========================================================
# PESTAÑA 3: GESTIÓN DE CHOFERES (CON FILTROS Y SEMÁFORO)
# =========================================================
with tab3:
    st.header("👷‍♂️ Gestión de Choferes y Personal")
    
    url_choferes = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_choferes.csv?nocache=' + str(pd.Timestamp.now().timestamp())
    
    try:
        df_choferes = pd.read_csv(url_choferes)
    except Exception as e:
        df_choferes = pd.DataFrame()

    col_tabla_ch, col_form_ch = st.columns([2, 1])
    
    with col_tabla_ch:
        st.subheader("📋 Registro de Personal")
        
        if not df_choferes.empty:
            # FILTROS AVANZADOS POR SELECCIÓN ÚNICA
            st.markdown("##### 🔍 Filtrar datos")
            col_ch1, col_ch2 = st.columns(2)
            
            with col_ch1:
                lista_entidades = ["Todos"] + sorted(df_choferes['Entidad'].dropna().unique().tolist())
                entidad_sel = st.selectbox("Seleccionar 1 Entidad/Chofer:", lista_entidades)
                
            with col_ch2:
                lista_docs = ["Todos"] + sorted(df_choferes['Documento'].dropna().unique().tolist())
                doc_sel = st.selectbox("Seleccionar 1 Documento:", lista_docs)
            
            # Aplicar filtros
            df_choferes_filtrado = df_choferes.copy()
            if entidad_sel != "Todos":
                df_choferes_filtrado = df_choferes_filtrado[df_choferes_filtrado['Entidad'] == entidad_sel]
            if doc_sel != "Todos":
                df_choferes_filtrado = df_choferes_filtrado[df_choferes_filtrado['Documento'] == doc_sel]
                
            st.dataframe(df_choferes_filtrado, use_container_width=True)
            
            # -------------------------------------------------------------
            # CUADRO DE PRÓXIMOS VENCIMIENTOS (SEMÁFORO DE COLORES)
            # -------------------------------------------------------------
            st.markdown("---")
            st.subheader("🕓 Panel de Próximos Vencimientos")
            st.write("Control visual de urgencia según la proximidad de la fecha:")
            
            # Procesamos las fechas para calcular los días restantes
            df_alertas = df_choferes.copy()
            
            # CORRECCIÓN AQUÍ: '%d/%m/%Y' en lugar del error '%yyyy'
            # También agregamos dayfirst=True por si acaso
            df_alertas['Fecha vencimiento'] = pd.to_datetime(df_alertas['Fecha vencimiento'], format='%d/%m/%Y', errors='coerce')
            
            hoy = pd.Timestamp.now().normalize()
            
            # Verificamos si hay fechas válidas antes de intentar dibujarlas
            fechas_validas = df_alertas.dropna(subset=['Fecha vencimiento'])
            
            if fechas_validas.empty:
                st.warning("No se encontraron fechas de vencimiento válidas para mostrar las alertas. Verifica que la columna se llame 'Fecha vencimiento'.")
            else:
                # Recorremos fila por fila para armar las cajas de alertas de color
                for index, row in fechas_validas.iterrows():
                    fecha_venc = row['Fecha vencimiento']
                    dias_restantes = (fecha_venc - hoy).days
                    fecha_formateada = fecha_venc.strftime('%d/%m/%Y')
                    
                    # Definición de tonos de color según días restantes
                    if dias_restantes <= 0:
                        color_bg = "#d9534f" # Rojo Oscuro / Alerta Máxima
                        texto_alerta = f"🔴 VENCIDO (Hace {abs(dias_restantes)} días) o Vence Hoy"
                    elif dias_restantes <= 10:
                        color_bg = "#f0ad4e" # Naranja / Crítico
                        texto_alerta = f"🟠 CRÍTICO (Faltan {dias_restantes} días)"
                    elif dias_restantes <= 30:
                        color_bg = "#ffd700" # Amarillo / Advertencia
                        texto_alerta = f"🟡 ADVERTENCIA (Faltan {dias_restantes} días)"
                    elif dias_restantes <= 60:
                        color_bg = "#90ee90" # Verde Claro / Seguro
                        texto_alerta = f"🟢 CONTROLADO (Faltan {dias_restantes} días)"
                    else:
                        color_bg = "#228b22" # Verde Oscuro / Excelente
                        texto_alerta = f"🟢 VIGENTE (Faltan {dias_restantes} días)"
                    
                    # Estilo de letra (Blanco para fondos oscuros, Negro para claros)
                    text_color = "#000000" if dias_restantes > 10 and dias_restantes <= 60 else "#ffffff"
                    
                    # Diseñamos un cuadro de alerta HTML interactivo en Streamlit
                    html_card = f"""
                    <div style="background-color:{color_bg}; padding:12px; border-radius:6px; margin-bottom:8px; color:{text_color}; font-family:Arial, sans-serif;">
                        <strong style="font-size:16px;">{row['Entidad']}</strong> — Documento: <u>{row['Documento']}</u> <br>
                        <strong>Vence el:</strong> {fecha_formateada} | <span style="font-weight:bold;">{texto_alerta}</span> <br>
                        <small>Obs: {row['Observaciones'] if pd.notna(row['Observaciones']) else 'Sin observaciones'}</small>
                    </div>
                    """
                    st.markdown(html_card, unsafe_convert_html=True)
