import streamlit as st
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🛢️", layout="centered")

# --- ESTILOS CSS PERSONALIZADOS (Fondo, Tarjetas y Móvil) ---
st.markdown("""
    <style>
    /* Fondo oscuro industrial moderno y elegante */
    .stApp {
        background-color: #121212;
        background-image: radial-gradient(circle at 50% 50%, #222222 0%, #111111 100%);
    }

    /* Contenedor central tipo tarjeta flotante */
    .main .block-container {
        background-color: #1e1e1e;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
        max-width: 600px;
        margin-top: 3rem;
    }

    /* Textos claros */
    h1, h2, h3, p, label, span {
        color: #ffffff !important;
    }

    /* Botones grandes y touch-friendly para celulares */
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

    /* Inputs estilizados */
    input {
        border-radius: 8px !important;
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛢️ Lubricentro El Calvo")
st.subheader("Gestión Rápida de Turnos y Servicios")

# Control de sesión en Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    st.markdown("### 🔑 Acceso o Registro")
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
        st.info("Próximo paso: Aquí programaremos el agendamiento para Cambio de Aceite, Filtros y Engrasado.")