import streamlit as st
from datetime import datetime, timedelta
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🛢️", layout="centered")

# --- ESTILOS CSS DEFINITIVOS (Todo oscuro y legible) ---
st.markdown("""
    <style>
    /* Fondo general de toda la aplicación */
    .stApp {
        background-color: #121212 !important;
    }
    
    /* Contenedor central */
    .main .block-container {
        background-color: #1e1e1e !important;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff !important;
        max-width: 800px;
        margin-top: 2rem;
    }

    /* Forzar texto blanco en toda la app */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #ffffff !important;
    }
    
    /* BARRA LATERAL OSCURA Y LIMPIA */
    [data-testid="stSidebar"] {
        background-color: #181818 !important;
        border-right: 1px solid #333 !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Cajas de texto, contenedores y elementos de Streamlit */
    div[data-baseweb="select"] > div, input, textarea {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.2em;
        font-weight: bold;
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #ff2424;
        color: white;
    }

    .slot-libre {
        background-color: rgba(46, 204, 113, 0.25);
        border: 1px solid #2ecc71;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 5px;
        font-size: 0.9rem;
    }
    .slot-ocupado {
        background-color: rgba(231, 76, 60, 0.25);
        border: 1px solid #e74c3c;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 5px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

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
        reg_placa = st.text_input("Placa del vehículo (Será tu usuario)", key="reg_placa").upper().strip()
        reg_pass = st.text_input("Contraseña de acceso", type="password", key="reg_pass")
        
        if st.button("Registrarme y Acceder", key="btn_register"):
            if reg_nombre and reg_tel and reg_placa and reg_pass:
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
    st.sidebar.write(f"Vehículo: {user['placa']}")
    st.sidebar.write(f"Rol: {user['rol'].upper()}")
    
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
            st.subheader("🗓️ Estado de Turnos de la Semana (Verde: Libre | Rojo: Ocupado)")
            
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
            
            for i in range(5):
                dia_actual = hoy + timedelta(days=i)
                nombre_dia_en = dia_actual.strftime('%A')
                nombre_mes_en = dia_actual.strftime('%B')
                
                dia_espanol = dias_es.get(nombre_dia_en, nombre_dia_en)
                mes_espanol = meses_es.get(nombre_mes_en, nombre_mes_en)
                
                st.markdown(f"**📅 Día: {dia_espanol} {dia_actual.day} de {mes_espanol}**")
                
                for row_start in range(0, len(horas_atencion), 4):
                    chunk_horas = horas_atencion[row_start:row_start+4]
                    cols = st.columns(len(chunk_horas))
                    
                    for idx, hora in enumerate(chunk_horas):
                        slot_datetime_str = f"{dia_actual} {hora}"
                        is_ocupado = any(slot_datetime_str in t for t in turnos_ocupados)
                        
                        with cols[idx]:
                            hora_corta = hora[:5]
                            if is_ocupado:
                                st.markdown(f"<div class='slot-ocupado'>🔴 <b>{hora_corta}</b><br>Ocupado</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='slot-libre'>🟢 <b>{hora_corta}</b><br>Disponible</div>", unsafe_allow_html=True)
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
                servicio_seleccionado = st.selectbox("Seleccione el Servicio", list(servicios_dict.keys()), key="sel_serv")
                servicio_id = servicios_dict[servicio_seleccionado]
                
                fecha_turno = st.date_input("Fecha para el turno", min_value=datetime.today(), key="sel_fecha")
                
                horas_disponibles_str = [f"{h:02d}:00:00" for h in range(8, 18)]
                hora_turno = st.selectbox("Hora disponible", horas_disponibles_str, key="sel_hora")
                
                observaciones = st.text_area("Observaciones adicionales", placeholder="Ej: Aceite semisintético...", key="sel_obs")
                
                if st.button("Confirmar y Agendar Turno", key="btn_agendar"):
                    fecha_hora_completa = f"{fecha_turno} {hora_turno}"
                    try:
                        db = conectar_db()
                        if db:
                            cursor = db.cursor()
                            cursor.execute(
                                """INSERT INTO turnos (usuario_id, vehiculo_id, servicio_id, fecha_hora_turno, estado, observaciones) 
                                   VALUES (%s, %s, %s, %s, 'pendiente', %s)""",
                                (user['id'], user['id'], servicio_id, fecha_hora_completa, observaciones)
                            )
                            db.commit()
                            db.close()
                            st.success("✅ ¡Turno agendado con éxito!")
                    except Exception as e:
                        st.error(f"Error al guardar el turno (Es posible que ya exista una reserva a esa hora): {e}")
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