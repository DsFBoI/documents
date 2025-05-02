import sqlite3

def store_hash_and_message_in_db(hash_value, message):
    """Guarda el hash y el mensaje en la base de datos evitando duplicados."""
    conn = sqlite3.connect('steganography.db')
    cursor = conn.cursor()

    # Convertir hash a bytes
    hash_bytes = [int(hash_value[i:i+2], 16) for i in range(0, len(hash_value), 2)]

    # Crear tabla si no existe
    columns = ", ".join([f"byte{i} INTEGER" for i in range(len(hash_bytes))])
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns},
            message TEXT
        )
    ''')

    # Verificar si ya existe el mismo hash
    where_clause = " AND ".join([f"byte{i}=?" for i in range(len(hash_bytes))])
    cursor.execute(f"SELECT 1 FROM messages WHERE {where_clause}", hash_bytes)
    if cursor.fetchone():
        print("[!] Hash ya existe en la base de datos. No se insertó duplicado.")
        conn.close()
        return

    # Insertar nuevo hash y mensaje
    values = hash_bytes + [message]
    placeholders = ", ".join(["?"] * len(values))
    column_names = ", ".join([f"byte{i}" for i in range(len(hash_bytes))]) + ", message"

    cursor.execute(f'''
        INSERT INTO messages ({column_names}) VALUES ({placeholders})
    ''', values)

    conn.commit()
    conn.close()
    print("[✓] Hash y mensaje insertados correctamente.")
