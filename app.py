import streamlit as st
from datetime import datetime, timedelta
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🛢️", layout="centered")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        background-image: radial-gradient(circle at 50% 50%, #222222 0%, #111111 100%);
    }
    .main .block-container {
        background-color: #1e1e1e;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
        max-width: 750px;
        margin-top: 2rem;
    }
    h1, h2, h3, p, label, span {
        color: #ffffff !important;
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
    input, select, textarea {
        border-radius: 8px !important;
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    .slot-libre {
        background-color: rgba(46, 204, 113, 0.2);
        border: 1px solid #2ecc71;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 5px;
    }
    .slot-ocupado {
        background-color: rgba(231, 76, 60, 0.2);
        border: 1px solid #e74c3c;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛢️ Lubricentro El Calvo")

# Control de sesión en Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    st.subheader("🔑 Acceso o Registro")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse (Clientes)"])
    
    with tab1:
        st.write("")
        placa_login = st.text_input("🚗 Ingrese la Placa de su vehículo (Ej: ABC123)").upper().strip()
        if st.button("Ingresar al Sistema"):
            if placa_login:
                db = conectar_db()
                if db:
                    cursor = db.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM usuarios WHERE placa = %s", (placa_login,))
                    user = cursor.fetchone()
                    db.close()
                    if user:
                        st.session_state['user'] = user
                        st.rerun()
                    else:
                        st.error("⚠️ Vehículo no encontrado. Regístrese en la pestaña de al lado.")
            else:
                st.warning("⚠️ Por favor ingrese la placa.")
                    
    with tab2:
        st.write("")
        reg_nombre = st.text_input("Nombre completo")
        reg_tel = st.text_input("Teléfono de contacto")
        reg_placa = st.text_input("Placa del vehículo (Será tu usuario)").upper().strip()
        if st.button("Registrarme y Acceder"):
            if reg_nombre and reg_tel and reg_placa:
                db = conectar_db()
                if db:
                    try:
                        cursor = db.cursor()
                        cursor.execute(
                            "INSERT INTO usuarios (nombre, telefono, placa, rol) VALUES (%s, %s, %s, 'cliente')",
                            (reg_nombre, reg_tel, reg_placa)
                        )
                        db.commit()
                        user_id = cursor.lastrowid
                        db.close()
                        
                        st.session_state['user'] = {
                            "id": user_id, "nombre": reg_nombre, 
                            "telefono": reg_tel, "placa": reg_placa, "rol": "cliente"
                        }
                        st.success("¡Registro exitoso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ La placa o el teléfono ya están registrados. Detalle: {e}")
            else:
                st.warning("⚠️ Por favor completa todos los campos.")
else:
    user = st.session_state['user']
    st.sidebar.write(f"👤 Hola, **{user['nombre']}**")
    st.sidebar.write(f"Vehículo: `{user['placa']}`")
    st.sidebar.write(f"Rol: `{user['rol'].upper()}`")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['user'] = None
        st.rerun()
        
    if user['rol'] == 'administrador':
        st.header("📊 Panel de Administración")
        st.info("Aquí verás las métricas mensuales, gráficos de clientes, opción de anular o adelantar turnos.")
        
    else:
        st.header("🚗 Panel de Turnos - Cliente")
        st.success(f"Bienvenido. Vehículo asociado: **{user['placa']}**")
        
        # Opciones principales del cliente solicitadas
        menu_cliente = st.radio("¿Qué deseas hacer?", ["📅 Calendario Semanal y Disponibilidad", "➕ Agendar Turno Nuevo", "⚙️ Gestionar mis Turnos"], horizontal=True)
        
        st.write("---")
        
        if menu_cliente == "📅 Calendario Semanal y Disponibilidad":
            st.subheader("🗓️ Estado de Turnos de la Semana (Verde: Libre | Rojo: Ocupado)")
            
            # Mostrar los próximos 7 días
            hoy = datetime.today().date()
            db = conectar_db()
            turnos_ocupados = []
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT fecha_hora_turno FROM turnos WHERE estado != 'cancelado'")
                turnos_ocupados = [t['fecha_hora_turno'].strftime('%Y-%m-%d %H:%M') for t in cursor.fetchall()]
                db.close()
                
            # Horarios de atención simulados del lubricentro (Ej: 8:00 AM a 4:00 PM)
            horas_atencion = ["08:00", "10:00", "14:00", "16:00"]
            
            for i in range(5): # Mostrar 5 días hábiles
                dia_actual = hoy + timedelta(days=i)
                st.markdown(f"**📅 Día: {dia_actual.strftime('%A %d de %B')}**")
                
                cols = st.columns(len(horas_atencion))
                for idx, hora in enumerate(horas_atencion):
                    fecha_str = f"{dia_actual} {hora}:00"
                    # Verificamos si la fecha y hora exacta está ocupada
                    slot_key = f"{dia_actual} {hora}"
                    
                    # Comprobación simple en base a la lista de ocupados
                    is_ocupado = any(slot_key in t for t in turnos_ocupados)
                    
                    with cols[idx]:
                        if is_ocupado:
                            st.markdown(f"<div class='slot-ocupado'>🔴 <b>{hora}</b><br>Ocupado</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='slot-libre'>🟢 <b>{hora}</b><br>Disponible</div>", unsafe_allow_html=True)
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
                servicio_seleccionado = st.selectbox("Seleccione el Servicio", list(servicios_dict.keys()))
                servicio_id = servicios_dict[servicio_seleccionado]
                
                fecha_turno = st.date_input("Fecha para el turno", min_value=datetime.today())
                hora_turno = st.selectbox("Hora disponible", ["08:00:00", "10:00:00", "14:00:00", "16:00:00"])
                
                observaciones = st.text_area("Observaciones adicionales", placeholder="Ej: Aceite semisintético...")
                
                if st.button("Confirmar y Agendar Turno"):
                    fecha_hora_completa = f"{fecha_turno} {hora_turno}"
                    db = conectar_db()
                    if db:
                        try:
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
                            st.error(f"Error al guardar el turno (Es posible que ese horario ya esté tomado): {e}")
            else:
                st.warning("No hay servicios configurados.")

        elif menu_cliente == "⚙️ Gestionar mis Turnos":
            st.subheader("📋 Mis Turnos Separados")
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