import streamlit as st
from datetime import datetime, timedelta
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🛢️", layout="centered")

st.title("🛢️ Lubricentro El Calvo")

# Control de sesión en Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    st.subheader("🔑 Acceso o Registro de Clientes")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        st.write("")
        placa_login = st.text_input("🚗 Placa del vehículo", key="input_login_placa").upper().strip()
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
                        # Registramos directamente al usuario (la placa y teléfono quedan unicos en esta tabla)
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
        st.success(f"Bienvenido. Vehículo asociado: **{user['placa']}**")
        
        menu_cliente = st.radio("¿Qué deseas hacer?", ["📅 Calendario Semanal y Disponibilidad", "➕ Agendar Turno Nuevo", "⚙️ Gestionar mis Turnos"], horizontal=True)
        
        st.write("---")
        
        if menu_cliente == "📅 Calendario Semanal y Disponibilidad":
            st.subheader("🗓️ Estado de Turnos (Lunes a Sábado)")
            
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
                
            horas_atencion = [f"{h:02d}:00:00" for h in range(8, 18)]
            
            dias_mostrados = 0
            dia_offset = 0
            
            while dias_mostrados < 6:
                dia_actual = hoy + timedelta(days=dia_offset)
                dia_offset += 1
                
                if dia_actual.weekday() == 6:  # Omitir domingos
                    continue
                
                dias_mostrados += 1
                nombre_dia_en = dia_actual.strftime('%A')
                nombre_mes_en = dia_actual.strftime('%B')
                
                dia_espanol = dias_es.get(nombre_dia_en, nombre_dia_en)
                mes_espanol = meses_es.get(nombre_mes_en, nombre_mes_en)
                
                st.markdown(f"**📅 {dia_espanol} {dia_actual.day} de {mes_espanol}**")
                
                for row_start in range(0, len(horas_atencion), 4):
                    chunk_horas = horas_atencion[row_start:row_start+4]
                    cols = st.columns(len(chunk_horas))
                    
                    for idx, hora in enumerate(chunk_horas):
                        slot_datetime_str = f"{dia_actual} {hora}"
                        is_ocupado = any(slot_datetime_str in t for t in turnos_ocupados)
                        
                        with cols[idx]:
                            hora_corta = hora[:5]
                            if is_ocupado:
                                st.error(f"🔴 {hora_corta}\nOcupado")
                            else:
                                st.success(f"🟢 {hora_corta}\nLibre")
                st.write("")

        elif menu_cliente == "➕ Agendar Turno Nuevo":
            st.subheader("📝 Registrar un Nuevo Turno (Múltiples Servicios)")
            
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
                
                fecha_turno = st.date_input("Fecha para el turno", min_value=datetime.today(), key="sel_fecha")
                
                if fecha_turno.weekday() == 6:
                    st.error("⚠️ El lubricentro no labora los domingos. Por favor elija de lunes a sábado.")
                
                horas_disponibles_str = [f"{h:02d}:00:00" for h in range(8, 18)]
                hora_turno = st.selectbox("Hora disponible", horas_disponibles_str, key="sel_hora")
                
                observaciones = st.text_area("Observaciones adicionales", placeholder="Ej: Aceite semisintético...", key="sel_obs")
                
                if st.button("Confirmar y Agendar Turno", key="btn_agendar"):
                    if fecha_turno.weekday() == 6:
                        st.error("No se puede agendar un domingo.")
                    elif not servicios_seleccionados:
                        st.warning("⚠️ Por favor seleccione al menos un servicio.")
                    else:
                        fecha_hora_completa = f"{fecha_turno} {hora_turno}"
                        try:
                            db = conectar_db()
                            if db:
                                cursor = db.cursor()
                                
                                # Insertamos los turnos usando el ID del usuario y asignando 0 o el mismo user_id en vehiculo_id si la tabla turnos lo pide
                                for serv_nombre in servicios_seleccionados:
                                    serv_id = servicios_dict[serv_nombre]
                                    cursor.execute(
                                        """INSERT INTO turnos (usuario_id, vehiculo_id, servicio_id, fecha_hora_turno, estado, observaciones) 
                                           VALUES (%s, %s, %s, %s, 'pendiente', %s)""",
                                        (user['id'], user['id'], serv_id, fecha_hora_completa, observaciones)
                                    )
                                db.commit()
                                db.close()
                                st.success("✅ ¡Turno(s) agendado(s) con éxito!")
                        except Exception as e:
                            st.error(f"Error al guardar el turno: {e}")
            else:
                st.warning("⚠️ No hay servicios configurados en la base de datos.")

        elif menu_cliente == "⚙️ Gestionar mis Turnos":
            st.subheader("📋 Mis Turnos Separados")
            try:
                db = conectar_db()
                if db:
                    cursor = db.cursor(dictionary=True)
                    cursor.execute("""
                        SELECT t.id, s.nombre_servicio, t.fecha_hora_turno, t.estado, t.observaciones 
                        FROM turnos t
                        JOIN servicios s ON t.servicio_id = s.id
                        WHERE t.usuario_id = %s
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
                                * **Servicio:** {turno['nombre_servicio']}
                                * **Fecha y Hora:** {turno['fecha_hora_turno']}
                                * **Estado:** {estado_color} `{turno['estado'].upper()}`
                                * **Observaciones:** {turno['observaciones'] if turno['observaciones'] else 'Ninguna'}
                                -----------------------------------
                                """)
                    else:
                        st.info("No tienes turnos separados en este momento.")
            except Exception as e:
                st.error(f"Error al cargar los turnos: {e}")