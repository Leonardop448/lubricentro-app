import os
import streamlit as st
import mysql.connector
from mysql.connector import Error

def conectar_db():
    try:
        host = os.getenv("DB_HOST")
        database = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        port = int(os.getenv("DB_PORT", 3306))
        
        # Validación rápida para ver qué variable llega vacía si ocurre un error
        if not all([host, database, user, password]):
            st.error(f"Faltan variables: HOST={host}, DB={database}, USER={user}, PASS={'Configurada' if password else 'Vacía'}")

        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error detallado de MySQL: {e}")
        return None