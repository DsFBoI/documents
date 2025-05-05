import mysql.connector

def store_hash_and_message_in_db(hash_value, message):
    conn = mysql.connector.connect(
        host='172.21.48.1',
        port=3306,
        user='tfg',
        password='Daniel25071005',
        database='tfg_db'
    )
    cursor = conn.cursor()

    hash_bytes = [int(hash_value[i:i+2], 16) for i in range(0, len(hash_value), 2)]
    columns = ", ".join([f"byte{i} INT" for i in range(len(hash_bytes))])
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {columns},
            message TEXT
        )
    ''')

    where_clause = " AND ".join([f"byte{i}=%s" for i in range(len(hash_bytes))])
    cursor.execute(f"SELECT 1 FROM messages WHERE {where_clause}", tuple(hash_bytes))
    if cursor.fetchone():
        print("[!] Hash already exists. Skipping insert.")
        conn.close()
        return

    values = hash_bytes + [message]
    column_names = ", ".join([f"byte{i}" for i in range(len(hash_bytes))]) + ", message"
    placeholders = ", ".join(["%s"] * len(values))

    cursor.execute(f'''
        INSERT INTO messages ({column_names}) VALUES ({placeholders})
    ''', tuple(values))

    conn.commit()
    conn.close()
    print("[✓] Hash and message inserted successfully.")
