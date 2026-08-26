import streamlit as st
from database.conexion import conectar_db

st.set_page_config(page_title="Lubricentro El Calvo", page_icon="🚗", layout="centered")

# Estilos CSS para botones aptos para móviles (Touch-friendly)
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛢️ Lubricentro El Calvo - Gestion de Turnos")

# Control de sesión en Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None

if st.session_state['user'] is None:
    st.subheader("🔑 Acceso o Registro Rápido")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse (Clientes)"])
    
    with tab1:
        placa_login = st.text_input("Placa del vehículo (Ej: ABC123)").upper().strip()
        if st.button("Ingresar"):
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
                        st.error("Vehículo no encontrado. Por favor, regístrese en la pestaña de al lado.")
            else:
                st.warning("Por favor ingrese la placa.")
                    
    with tab2:
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
                        st.error(f"La placa o el teléfono ya están registrados. Error: {e}")
            else:
                st.warning("Por favor completa todos los campos.")
else:
    user = st.session_state['user']
    st.sidebar.write(f"👤 Hola, **{user['nombre']}**")
    st.sidebar.write(f"Rol: `{user['rol'].upper()}`")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['user'] = None
        st.rerun()
        
    if user['rol'] == 'administrador':
        st.header("📊 Panel de Administración")
        st.info("Aquí verás las métricas mensuales, gráficos de clientes, opción de anular o adelantar turnos.")
        
    else:
        st.header("🚗 Panel de Turnos - Cliente")
        st.write(f"Vehículo asociado (Placa): **{user['placa']}**")
        st.info("Aquí podrás agendar tu cambio de aceite, filtros o engrase y ver el estado de tus turnos.")