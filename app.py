import streamlit as st
import requests
from datetime import datetime, timedelta
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🛢️", layout="centered")

st.title("🛢️ Lubricentro El Calvo")

# Control de sesión en Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None

if 'turno_preseleccionado' not in st.session_state:
    st.session_state['turno_preseleccionado'] = None

if 'menu_index' not in st.session_state:
    st.session_state['menu_index'] = 0

# --- FUNCIÓN PARA ENVIAR ALERTAS POR WHATSAPP A MÚLTIPLES NÚMEROS ---
def enviar_alerta_whatsapp(texto_mensaje):
    url = "https://automatizacion-evolution-api.3akfbq.easypanel.host/message/sendText/turnoslubricentro"
    
    headers = {
        "apikey": "429683C4C977415CAAFCCE10F7D57E11",
        "Content-Type": "application/json"
    }
    
    # Lista con los dos números de las administradoras
    numeros_administradoras = ["573137655289", "573122688378"]
    
    for numero in numeros_administradoras:
        payload = {
            "number": numero,
            "text": texto_mensaje,
            "delay": 1200
        }
        try:
            requests.post(url, json=payload, headers=headers)
        except Exception as e:
            print(f"Error al enviar WhatsApp al número {numero}: {e}")
# ------------------------------------------------------------------

if st.session_state['user'] is None:
    st.subheader("🔑 Acceso o Registro de Clientes")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        st.write("")
        placa_login = st.text_input("🚗 Placa del vehículo sin espacios ni caracteres especiales", key="input_login_placa").upper().strip()
        pass_login = st.text_input("🔒 Contraseña", type="password", key="input_login_pass")
        
        if st.button("Ingresar al Sistema", key="btn_login"):
            if placa_login and pass_login:
                try:
                    db = conectar_db()
                    if db:
                        cursor = db.cursor(dictionary=True)
                        cursor.execute("SELECT * FROM usuarios WHERE placa = %s AND password = %s", (placa_login, pass_login))
                        user = cursor.fetchone()
                        db.close()
                        
                        if user:
                            st.session_state['user'] = user
                            st.success("¡Acceso exitoso! Entrando...")
                            st.rerun()
                        else:
                            st.error("⚠️ Placa o contraseña incorrectas.")
                    else:
                        st.error("⚠️ Error de conexión con la base de datos.")
                except Exception as e:
                    st.error(f"⚠️ Error en el sistema: {e}")
            else:
                st.warning("⚠️ Por favor ingrese la placa y la contraseña.")
                    
    with tab2:
        st.write("")
        reg_nombre = st.text_input("Nombre completo", key="reg_nombre")
        reg_tel = st.text_input("Teléfono de contacto", key="reg_tel")
        reg_placa = st.text_input("Placa del vehículo (Sin espacios ni caracteres especiales)", key="reg_placa").upper().strip()
        reg_pass = st.text_input("Contraseña de acceso", type="password", key="reg_pass")
        
        if st.button("Registrarme y Acceder", key="btn_register"):
            if reg_placa and not reg_placa.isalnum():
                st.error("⚠️ La placa no debe contener espacios, guiones ni caracteres especiales (ej: usa ABC123 en lugar de ABC-123).")
            elif reg_nombre and reg_tel and reg_placa and reg_pass:
                try:
                    db = conectar_db()
                    if db:
                        cursor = db.cursor()
                        cursor.execute(
                            "INSERT INTO usuarios (nombre, telefono, placa, password, rol) VALUES (%s, %s, %s, %s, 'cliente')",
                            (reg_nombre, reg_tel, reg_placa, reg_pass)
                        )
                        db.commit()
                        user_id = cursor.lastrowid
                        db.close()
                        
                        st.session_state['user'] = {
                            "id": user_id, "nombre": reg_nombre, 
                            "telefono": reg_tel, "placa": reg_placa, "rol": "cliente"
                        }
                        st.success("¡Registro exitoso! Entrando...")
                        st.rerun()
                    else:
                        st.error("⚠️ No se pudo conectar a la base de datos.")
                except Exception as e:
                    st.error(f"⚠️ Error al registrar. Es posible que la placa o el teléfono ya existan. Detalle: {e}")
            else:
                st.warning("⚠️ Por favor completa todos los campos.")
else:
    user = st.session_state['user']
    st.sidebar.write(f"👤 Hola, **{user['nombre']}**")
    st.sidebar.write(f"Vehículo: `{user['placa']}`")
    st.sidebar.write(f"Rol: `{user['rol'].upper()}`")
    
    if st.sidebar.button("Cerrar Sesión", key="btn_logout"):
        st.session_state['user'] = None
        st.rerun()
        
    if user['rol'] == 'administrador':
        st.header("📊 Panel de Administración")
        st.info("Aquí verás las métricas mensuales, gráficos de clientes, opción de anular o adelantar turnos.")
        
    else:
        st.header("🚗 Panel de Turnos - Cliente")
        st.success(f"Bienvenido **{user['nombre']}** Vehículo: **{user['placa']}**")
        
        menu_opciones = ["📅 Calendario Semanal y Disponibilidad", "➕ Agendar Turno Nuevo", "⚙️ Gestionar mis Turnos"]
        
        menu_cliente = st.radio("¿Qué deseas hacer?", menu_opciones, index=st.session_state['menu_index'], horizontal=True)
        
        if menu_cliente == menu_opciones[0]:
            st.session_state['menu_index'] = 0
        elif menu_cliente == menu_opciones[1]:
            st.session_state['menu_index'] = 1
        elif menu_cliente == menu_opciones[2]:
            st.session_state['menu_index'] = 2
        
        st.write("---")
        
        if menu_cliente == "📅 Calendario Semanal y Disponibilidad":
            st.subheader("🗓️ Estado de Turnos (Lunes a Sábado) - Haz clic en un horario libre para agendar")
            
            hoy = datetime.today().date()
            db = conectar_db()
            turnos_ocupados = []
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT fecha_hora_turno FROM turnos WHERE estado != 'cancelado'")
                turnos_ocupados = [str(t['fecha_hora_turno']) for t in cursor.fetchall()]
                db.close()
                
            dias_es = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            meses_es = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
                'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
                'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
                
            horas_atencion_24 = [f"{h:02d}:00:00" for h in range(8, 18)]
            
            dias_mostrados = 0
            dia_offset = 0
            
            while dias_mostrados < 6:
                dia_actual = hoy + timedelta(days=dia_offset)
                dia_offset += 1
                
                if dia_actual.weekday() == 6:
                    continue
                
                dias_mostrados += 1
                nombre_dia_en = dia_actual.strftime('%A')
                nombre_mes_en = dia_actual.strftime('%B')
                
                dia_espanol = dias_es.get(nombre_dia_en, nombre_dia_en)
                mes_espanol = meses_es.get(nombre_mes_en, nombre_mes_en)
                
                st.markdown(f"**📅 {dia_espanol} {dia_actual.day} de {mes_espanol}**")
                
                for row_start in range(0, len(horas_atencion_24), 4):
                    chunk_horas = horas_atencion_24[row_start:row_start+4]
                    cols = st.columns(len(chunk_horas))
                    
                    for idx, hora in enumerate(chunk_horas):
                        slot_datetime_str = f"{dia_actual} {hora}"
                        is_ocupado = any(slot_datetime_str in t for t in turnos_ocupados)
                        
                        hora_obj = datetime.strptime(hora, "%H:%M:%S")
                        hora_12h = hora_obj.strftime("%I:%M %p")
                        
                        with cols[idx]:
                            if is_ocupado:
                                st.error(f"🔴 {hora_12h}\nOcupado")
                            else:
                                btn_key = f"btn_slot_{dia_actual}_{hora}"
                                if st.button(f"🟢 {hora_12h}\nLibre", key=btn_key):
                                    st.session_state['turno_preseleccionado'] = {
                                        "fecha": dia_actual,
                                        "hora": hora
                                    }
                                    st.session_state['menu_index'] = 1
                                    st.rerun()
                st.write("")

        elif menu_cliente == "➕ Agendar Turno Nuevo":
            st.subheader("📝 Registrar un Nuevo Turno")
            
            db = conectar_db()
            servicios_dict = {}
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT id, nombre_servicio FROM servicios")
                servicios = cursor.fetchall()
                servicios_dict = {s['nombre_servicio']: s['id'] for s in servicios}
                db.close()
            
            if servicios_dict:
                servicios_seleccionados = st.multiselect("Seleccione uno o varios servicios", list(servicios_dict.keys()), key="sel_servicios_multi")
                
                pre_fecha = datetime.today()
                pre_hora_str = None
                
                if st.session_state['turno_preseleccionado']:
                    pre_fecha = st.session_state['turno_preseleccionado']['fecha']
                    pre_hora_str = st.session_state['turno_preseleccionado']['hora']
                
                fecha_turno = st.date_input("Fecha para el turno", value=pre_fecha, min_value=datetime.today(), key="sel_fecha")
                
                if fecha_turno.weekday() == 6:
                    st.error("⚠️ El lubricentro no labora los domingos. Por favor elija de lunes a sábado.")
                
                horas_ocupadas_fecha = []
                try:
                    db_occ = conectar_db()
                    if db_occ:
                        cur_occ = db_occ.cursor(dictionary=True)
                        cur_occ.execute(
                            "SELECT fecha_hora_turno FROM turnos WHERE DATE(fecha_hora_turno) = %s AND estado != 'cancelado'", 
                            (str(fecha_turno),)
                        )
                        turnos_fecha = cur_occ.fetchall()
                        db_occ.close()
                        
                        for t in turnos_fecha:
                            val = t['fecha_hora_turno']
                            if isinstance(val, datetime):
                                hora_formato = val.strftime("%H:%M:%S")
                            else:
                                val_str = str(val)
                                hora_formato = val_str.split(" ")[1] if " " in val_str else val_str
                                if len(hora_formato) == 5:
                                    hora_formato += ":00"
                            horas_ocupadas_fecha.append(hora_formato)
                except Exception as e:
                    pass
                
                todas_horas_24 = [f"{h:02d}:00:00" for h in range(8, 18)]
                horas_disponibles_24 = [h for h in todas_horas_24 if h not in horas_ocupadas_fecha]
                
                if horas_disponibles_24:
                    horas_12h_labels = [datetime.strptime(h, "%H:%M:%S").strftime("%I:%M %p") for h in horas_disponibles_24]
                    
                    pre_hora_index = 0
                    if pre_hora_str and pre_hora_str in horas_disponibles_24:
                        pre_hora_index = horas_disponibles_24.index(pre_hora_str)
                    
                    hora_seleccionada_label = st.selectbox("Hora disponible", horas_12h_labels, index=pre_hora_index, key="sel_hora")
                    idx_sel = horas_12h_labels.index(hora_seleccionada_label)
                    hora_turno = horas_disponibles_24[idx_sel]
                else:
                    st.warning("⚠️ No hay horarios disponibles para esta fecha. Por favor selecciona otro día.")
                    hora_turno = None
                
                observaciones = st.text_area("Observaciones adicionales", placeholder="Ej: Cambiar también filtro de caja...", key="sel_obs")
                
                if st.button("Confirmar y Agendar Turno", key="btn_agendar"):
                    if fecha_turno.weekday() == 6:
                        st.error("No se puede agendar un domingo.")
                    elif not servicios_seleccionados:
                        st.warning("⚠️ Por favor seleccione al menos un servicio.")
                    elif not hora_turno:
                        st.warning("⚠️ Selecciona una hora válida.")
                    else:
                        fecha_hora_completa = f"{fecha_turno} {hora_turno}"
                        try:
                            db = conectar_db()
                            if db:
                                cursor = db.cursor(dictionary=True)
                                
                                cursor.execute(
                                    "SELECT id FROM turnos WHERE fecha_hora_turno = %s AND estado != 'cancelado'", 
                                    (fecha_hora_completa,)
                                )
                                turno_existente = cursor.fetchone()
                                
                                if turno_existente:
                                    st.error("⚠️ Este horario acaba de ser ocupado por otro usuario. Por favor selecciona otro.")
                                    db.close()
                                else:
                                    cursor_insert = db.cursor()
                                    cursor_insert.execute(
                                        """INSERT INTO turnos (usuario_id, vehiculo_id, servicio_id, fecha_hora_turno, estado, observaciones) 
                                           VALUES (%s, %s, %s, %s, 'pendiente', %s)""",
                                        (user['id'], user['id'], servicios_dict[servicios_seleccionados[0]], fecha_hora_completa, observaciones)
                                    )
                                    turno_id = cursor_insert.lastrowid
                                    
                                    for serv_nombre in servicios_seleccionados:
                                        serv_id = servicios_dict[serv_nombre]
                                        cursor_insert.execute(
                                            "INSERT INTO turno_servicios (turno_id, servicio_id) VALUES (%s, %s)",
                                            (turno_id, serv_id)
                                        )
                                    
                                    db.commit()
                                    db.close()
                                    
                                    # --- ENVÍO DE ALERTA A WHATSAPP DE LA ADMINISTRADORA ---
                                    nombres_servicios_str = ", ".join(servicios_seleccionados)
                                    mensaje_whatsapp = f"""🚨 *Turno Solicitado*
ID Turno: #{turno_id}
Servicios a rea: {nombres_servicios_str}
Fecha y Hora: {fecha_hora_completa}
Estado: 🟡 PENDIENTE
Observaciones: {observaciones if observaciones else 'Ninguna'}"""
                                    enviar_alerta_whatsapp(mensaje_whatsapp)
                                    # -----------------------------------------------------
                                    
                                    st.session_state['turno_preseleccionado'] = None
                                    st.success("✅ ¡Turno agendado con éxito!")
                                    
                                    st.session_state['menu_index'] = 0
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar el turno: {e}")
            else:
                st.warning("⚠️ No hay servicios configurados en la base de datos.")

        elif menu_cliente == "⚙️ Gestionar mis Turnos":
            st.subheader("📋 Mis Turnos")
            
            try:
                db = conectar_db()
                if db:
                    cursor = db.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT t.id, 
                               GROUP_CONCAT(s.nombre_servicio SEPARATOR ', ') as nombres_servicios, 
                               t.fecha_hora_turno, 
                               t.estado, 
                               t.observaciones 
                        FROM turnos t
                        JOIN turno_servicios ts ON t.id = ts.turno_id
                        JOIN servicios s ON ts.servicio_id = s.id
                        WHERE t.usuario_id = %s
                        GROUP BY t.id, t.fecha_hora_turno, t.estado, t.observaciones
                        ORDER BY t.fecha_hora_turno DESC
                    """, (user['id'],))
                    mis_turnos = cursor.fetchall()
                    db.close()
                    
                    if mis_turnos:
                        for turno in mis_turnos:
                            estado_color = "🟡" if turno['estado'] == 'pendiente' else "🔵" if turno['estado'] == 'en_proceso' else "🟢" if turno['estado'] == 'finalizado' else "🔴"
                            
                            with st.container():
                                st.markdown(f"""
                                * **ID Turno:** #{turno['id']}
                                * **Servicios:** {turno['nombres_servicios']}
                                * **Fecha y Hora:** {turno['fecha_hora_turno']}
                                * **Estado:** {estado_color} `{turno['estado'].upper()}`
                                * **Observaciones:** {turno['observaciones'] if turno['observaciones'] else 'Ninguna'}
                                """)
                                
                                if st.button(f"🗑️ Anular y Eliminar Turno #{turno['id']}", key=f"del_{turno['id']}"):
                                    try:
                                        db_del = conectar_db()
                                        if db_del:
                                            cur_del = db_del.cursor()
                                            cur_del.execute("DELETE FROM turno_servicios WHERE turno_id = %s", (turno['id'],))
                                            cur_del.execute("DELETE FROM turnos WHERE id = %s", (turno['id'],))
                                            db_del.commit()
                                            db_del.close()
                                            
                                            # --- ENVÍO DE ALERTA DE ANULACIÓN A WHATSAPP ---
                                            mensaje_anulacion = f"""❌ *Turno Cancelado o Eliminado*
ID Turno: #{turno['id']}
Servicios: {turno['nombres_servicios']}
Fecha y Hora: {turno['fecha_hora_turno']}
Estado: 🔴 CANCELADO"""
                                            enviar_alerta_whatsapp(mensaje_anulacion)
                                            # ---------------------------------------------
                                            
                                            st.success(f"Turno #{turno['id']} eliminado con éxito.")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al eliminar: {e}")
                                
                                st.markdown("-----------------------------------")
                    else:
                        st.info("No tienes turnos separados en este momento.")
            except Exception as e:
                st.error(f"Error al cargar los turnos: {e}")