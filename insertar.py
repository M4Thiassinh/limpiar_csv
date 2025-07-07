import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Configura tu conexión
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '31032003',  # ← Cambia esto
    'database': 'educacion_censo',
    'charset': 'utf8mb4'
}

# Ruta a la carpeta con los CSV
csv_folder = r'C:/Users/matyr/OneDrive/Escritorio/Universidad/lX Semestre/Sistemas de Gestión/Trabajo 2/limpiar_csv/csv'

def insert_csv_to_mysql(file_path, table_name, connection):
    try:
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        df = df.dropna(how='all')

        cursor = connection.cursor()
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        for row in df.itertuples(index=False, name=None):
            try:
                cursor.execute(insert_query, row)
            except Error as e:
                print(f"⚠️ Error insertando fila en {table_name}: {e}")

        connection.commit()
        print(f"✅ Insertado: {table_name} desde {os.path.basename(file_path)}")

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")

try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("🔌 Conectado a la base de datos.")

        for file in os.listdir(csv_folder):
            if file.endswith('.csv'):
                table = os.path.splitext(file)[0]
                path = os.path.join(csv_folder, file)
                insert_csv_to_mysql(path, table, conn)

        conn.close()
        print("🔒 Conexión cerrada.")

except Error as e:
    print(f"❌ Error de conexión a MySQL: {e}")
