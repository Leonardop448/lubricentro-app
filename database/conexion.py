import os
import mysql.connector
from mysql.connector import Error

def conectar_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "automatizacion_basedatosn8n"),
            database=os.getenv("DB_NAME", "turnoselcalvo"),
            user=os.getenv("DB_USER", "mysql"),
            password=os.getenv("DB_PASS", "ddo93fn4bx373syjhp5c"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None