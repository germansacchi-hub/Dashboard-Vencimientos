import streamlit as st
import pandas as pd
import requests

st.set_page_config(layout="wide", page_title="Dashboard Transporte Arce")

# --- CONFIGURACIÓN DE URLS DESDE GITHUB (CON ANTI-CACHÉ NATIVO) ---
nocache = "?nocache=" + str(pd.Timestamp.now().timestamp())
URL_VENCIMIENTOS = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_vencimientos.csv' + nocache
URL_MANTENIMIENTO = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_mantenimiento.csv' + nocache
URL_CHOFERES = 'https://raw.githubusercontent.com/germansacchi-hub/Dashboard-Vencimientos/main/datos_choferes.csv' + nocache

WEBHOOK_URL = st.secrets["APPS_SCRIPT_WEBAPP_URL"]

# Carga segura de datos
try: df_vencimientos = pd.read_csv(URL_VENCIMIENTOS)
except: df_vencimientos = pd.DataFrame()

try: df_mantenimiento = pd.read_csv(URL_MANTENIMIENTO)
except: df_mantenimiento = pd.DataFrame()

try: df_choferes = pd.read_csv(URL_CHOFERES)
except: df_choferes = pd.DataFrame()


# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📋 Vencimientos y Alertas", "🔧 Gestión de Mantenimiento", "👷‍♂️ Personal / Choferes"])


# =========================================================
# PESTAÑA 1: VENCIMIENTOS Y ALERTAS (CON MODIFICADOR DIRECTO)
# =========================================================
with tab1:
    st.header("Control de Alertas y Vencimientos Flota")
    
    col_tabla_v, col_form_v = st.columns([2, 1])
    
    with col_tabla_v:
        st.subheader("📋 Tabla General de Vencimientos")
        if not df_vencimientos.empty:
            buscador_patente = st.text_input("🔍 Buscar por Patente (Entidad):")
            if buscador_patente:
                df_v_filtrado = df_vencimientos[df_vencimientos.astype(str).apply(lambda x: x.str.contains(buscador_patente, case=False)).any(axis=1)]
                st.dataframe(df_v_filtrado, use_container_width=True)
            else:
                st.dataframe(df_vencimientos, use_container_width=True)
        else:
            st.info("No hay datos de vencimientos en GitHub.")
            
    with col_form_v:
        st.subheader("✏️ Modificar / Agregar Vencimiento")
        with st.form("form_vencimientos", clear_on_submit=True):
            patente_v = st.text_input("Patente (Entidad a buscar/crear)").upper()
            documento_v = st.text_input("Documento (Ej: RTO, Seguro, Ruta)")
            f_alerta_v = st.date_input("Fecha de Alerta").strftime('%d/%m/%Y')
            f_venc_v = st.date_input("Fecha de Vencimiento").strftime('%d/%m/%Y')
            
            btn_guardar_v = st.form_submit_button("💾 Guardar en Google Sheets")
            
            if btn_guardar_v:
                if not patente_v:
                    st.error("La patente es obligatoria.")
                else:
                    datos_v = {"documento": documento_v, "fecha_alerta": f_alerta_v, "fecha_vencimiento": f_venc_v}
                    payload_v = {"action": "editar", "sheet": "Vencimientos", "patente": patente_v, "datos": datos_v}
                    with st.spinner("Sincronizando..."):
                        res = requests.post(WEBHOOK_URL, json=payload_v)
                        if res.status_code == 200:
                            st.success("✅ Actualizado en Google Sheets e Historial.")
                            st.info("🔄 Refresca el navegador en un momento para ver los cambios.")
                        else: st.error("❌ Error en la conexión.")


# =========================================================
# PESTAÑA 2: GESTIÓN DE MANTENIMIENTO
# =========================================================
with tab2:
    st.header("🔧 Gestión de Mantenimiento")
    col_tabla_m, col_form_m = st.columns([2, 1])
    
    with col_tabla_m:
        st.subheader("📋 Historial y Estado Actual")
        if not df_mantenimiento.empty:
            st.markdown("##### 🔍 Filtrar datos")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                lista_tipos = ["Todos"] + sorted(df_mantenimiento['Tipo'].dropna().unique().tolist())
                tipo_seleccionado = st.selectbox("Seleccionar 1 Tipo/Entidad:", lista_tipos)
            with col_f2:
                lista_veh = ["Todos"] + sorted(df_mantenimiento['Veh/Maq'].dropna().unique().tolist())
                veh_seleccionado = st.selectbox("Seleccionar 1 Vehículo/Maquinaria:", lista_veh)
            
            df_m_filtrado = df_mantenimiento.copy()
            if tipo_seleccionado != "Todos": df_m_filtrado = df_m_filtrado[df_m_filtrado['Tipo'] == tipo_seleccionado]
            if veh_seleccionado != "Todos": df_m_filtrado = df_m_filtrado[df_m_filtrado['Veh/Maq'] == veh_seleccionado]
            st.dataframe(df_m_filtrado, use_container_width=True)
        else:
            st.info("La tabla de mantenimientos está vacía.")

    with col_form_m:
        st.subheader("✏️ Registrar Nuevo Mantenimiento")
        with st.form("form_mantenimiento", clear_on_submit=True):
            tipo = st.text_input("Tipo")
            vehiculo = st.text_input("Veh/Maq")
            plan = st.text_input("Plan")
            tarea = st.text_input("Tarea/Documento")
            estado = st.selectbox("Estado", ["Pendiente", "En proceso", "Finalizado"])
            btn_guardar = st.form_submit_button("💾 Guardar Mantenimiento")
            
            if btn_guardar:
                datos_m = {"tipo": tipo, "vehiculo": vehiculo, "plan": plan, "tarea": tarea, "estado": estado}
                with st.spinner("Enviando..."):
                    res = requests.post(WEBHOOK_URL, json=datos_m)
                    if res.status_code == 200: st.success("✅ Guardado con éxito.")
                    else: st.error("❌ Error al guardar.")


# =========================================================
# PESTAÑA 3: GESTIÓN DE CHOFERES (ALERTAS ORDENADAS Y REUBICACIÓN)
# =========================================================
with tab3:
    st.header("👷‍♂️ Gestión de Choferes y Personal")
    
    # Fijamos una estructura de 2 columnas limpias arriba para asegurar el formulario a la derecha
    col_tabla_ch, col_form_ch = st.columns([1.8, 1.2])
    
    with col_tabla_ch:
        st.subheader("📋 Registro de Personal")
        if not df_choferes.empty:
            st.markdown("##### 🔍 Filtrar datos")
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                lista_entidades = ["Todos"] + sorted(df_choferes['Entidad'].dropna().unique().tolist())
                entidad_sel = st.selectbox("Seleccionar 1 Entidad/Chofer:", lista_entidades)
            with col_ch2:
                lista_docs = ["Todos"] + sorted(df_choferes['Documento'].dropna().unique().tolist())
                doc_sel = st.selectbox("Seleccionar 1 Documento:", lista_docs)
            
            df_choferes_filtrado = df_choferes.copy()
            if entidad_sel != "Todos": df_choferes_filtrado = df_choferes_filtrado[df_choferes_filtrado['Entidad'] == entidad_sel]
            if doc_sel != "Todos": df_choferes_filtrado = df_choferes_filtrado[df_choferes_filtrado['Documento'] == doc_sel]
            st.dataframe(df_choferes_filtrado, use_container_width=True)
        else:
            st.info("No hay registros en la tabla de Choferes.")

    with col_form_ch:
        st.subheader("✏️ Registrar Personal")
        with st.form("form_choferes", clear_on_submit=True):
            entidad = st.text_input("Entidad (Nombre Chofer)")
            documento = st.text_input("Documento (Trámite/Carnet)")
            fecha_alerta = st.date_input("Fecha de Alerta").strftime('%d/%m/%Y')
            fecha_vencimiento = st.date_input("Fecha de Vencimiento").strftime('%d/%m/%Y')
            vencido = st.selectbox("¿Vencido actualmente?", ["NO", "SI"])
            observaciones = st.text_area("Observaciones")
            estado_entidad = st.selectbox("Estado Entidad", ["Activo", "Baja Provisional", "Inactivo"])
            
            btn_guardar_ch = st.form_submit_button("💾 Guardar en Choferes")
            
            if btn_guardar_ch:
                datos_ch = {"entidad": entidad, "id_documento": documento, "fecha_alerta": fecha_alerta, "fecha_vencimiento": fecha_vencimiento, "vencido": vencido, "observaciones": observaciones, "estado_entidad": estado_entidad}
                with st.spinner("Guardando chofer..."):
                    res = requests.post(WEBHOOK_URL, json=datos_ch)
                    if res.status_code == 200: st.success("✅ Chofer guardado con éxito.")
                    else: st.error("❌ Error en el envío.")

    # -------------------------------------------------------------
    # CUADRO DE PRÓXIMOS VENCIMIENTOS - ORDENADO POR PROXIMIDAD (Bajo las columnas)
    # -------------------------------------------------------------
    st.markdown("---")
    st.subheader("🕓 Panel de Próximos Vencimientos (Ordenado por Urgencia)")
    st.write("Control visual ordenado cronológicamente (Vencidos y críticos primero):")
    
    if not df_choferes.empty:
        df_alertas = df_choferes.copy()
        # Convertimos de forma segura a fecha nativa de Python
        df_alertas['Fecha vencimiento_dt'] = pd.to_datetime(df_alertas['Fecha vencimiento'], format='%d/%m/%Y', errors='coerce')
        
        hoy = pd.Timestamp.now().normalize()
        
        # Calculamos la columna de días restantes para poder ORDENAR por ella
        df_alertas['Dias_Restantes'] = (df_alertas['Fecha vencimiento_dt'] - hoy).dt.days
        
        # 🔥 CLAVE: Ordenamos el dataframe de menor a mayor cantidad de días restantes
        df_alertas_ordenado = df_alertas.dropna(subset=['Dias_Restantes']).sort_values(by='Dias_Restantes', ascending=True)
        
        if df_alertas_ordenado.empty:
            st.warning("No se encontraron fechas válidas para armar el panel.")
        else:
            for index, row in df_alertas_ordenado.iterrows():
                dias_restantes = int(row['Dias_Restantes'])
                fecha_formateada = row['Fecha vencimiento']
                
                # Definición de colores según urgencia
                if dias_restantes <= 0:
                    color_bg = "#d9534f" # Rojo Oscuro
                    texto_alerta = f"🔴 VENCIDO (Hace {abs(dias_restantes)} días) o Vence Hoy"
                elif dias_restantes <= 10:
                    color_bg = "#f0ad4e" # Naranja / Crítico
                    texto_alerta = f"🟠 CRÍTICO (Faltan {dias_restantes} days)"
                elif dias_restantes <= 30:
                    color_bg = "#ffd700" # Amarillo
                    texto_alerta = f"🟡 ADVERTENCIA (Faltan {dias_restantes} días)"
                elif dias_restantes <= 60:
                    color_bg = "#90ee90" # Verde Claro
                    texto_alerta = f"🟢 CONTROLADO (Faltan {dias_restantes} días)"
                else:
                    color_bg = "#228b22" # Verde Oscuro
                    texto_alerta = f"🟢 VIGENTE (Faltan {dias_restantes} días)"
                
                text_color = "#000000" if 10 < dias_restantes <= 60 else "#ffffff"
                
                html_card = f"""
                <div style="background-color:{color_bg}; padding:12px; border-radius:6px; margin-bottom:8px; color:{text_color}; font-family:Arial, sans-serif;">
                    <strong style="font-size:16px;">{row['Entidad']}</strong> — Documento: <u>{row['Documento']}</u> <br>
                    <strong>Vence el:</strong> {fecha_formateada} | <span style="font-weight:bold;">{texto_alerta}</span> <br>
                    <small>Obs: {row['Observaciones'] if pd.notna(row['Observaciones']) else 'Sin observaciones'}</small>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
    else:
        st.info("Sin registros cargados para calcular proximidades.")
