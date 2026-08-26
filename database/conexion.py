import os
import mysql.connector
from mysql.connector import Error

def conectar_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "automatizacion_basedatosn8n"),
            database="turnoselcalvo",  # <- Forzamos explícitamente tu base de datos
            user="root",               # <- Usamos el usuario con permisos globales
            password=os.getenv("DB_PASS", "w6o23fph7omww3no34r"),  # <- Contraseña raíz de tu panel
            port=int(os.getenv("DB_PORT", 3306))
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None