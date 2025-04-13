import sqlite3

def store_hash_and_message_in_db(hash_value, message):
    """Stores each *2-hex-character* group (i.e., 8 bits) as an integer in the database."""
    conn = sqlite3.connect('steganography.db')
    cursor = conn.cursor()

    # Convert hash into byte pairs (2 hex chars = 1 byte)
    hash_bytes = [int(hash_value[i:i+2], 16) for i in range(0, len(hash_value), 2)]

    # Define table columns
    columns = ", ".join([f"byte{i} INTEGER" for i in range(len(hash_bytes))])
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns},
            message TEXT
        )
    ''')

    # Prepare values and insert
    values = hash_bytes + [message]
    placeholders = ", ".join(["?" for _ in values])
    column_names = ", ".join([f"byte{i}" for i in range(len(hash_bytes))]) + ", message"

    cursor.execute(f'''
        INSERT INTO messages ({column_names}) VALUES ({placeholders})
    ''', values)

    conn.commit()
    conn.close()
