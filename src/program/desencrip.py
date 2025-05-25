import jpeg_toolbox
import sqlite3

import mysql.connector
from hash_utils import compare_hashes


def extract_hash_from_dct(image_path, bits: int = 128, reference_hash: str = None):
    """Extrae bits de los coeficientes [0,0] de bloques 8x8 con validación paso a paso basada en los 6 siguientes valores posibles."""
    img = jpeg_toolbox.load(image_path)

    print("\n[1] Imagen cargada correctamente.")

    quant_table = img['quant_tables'][0]
    print("[2] Tabla de cuantificación obtenida:")
    print(quant_table)

    quant_00 = quant_table[0, 0]
    print(f"[3] Valor de cuantificación para [0,0]: {quant_00}")

    coef_array = img['coef_arrays'][0].copy()
    print("[4] Dimensiones del array de coeficientes:", coef_array.shape)

    hex_chars = []
    print("\n[5] Explorando bloques 8x8 con validación de coincidencia binaria de 4 bits")
    char_index = 0
    for i in range(0, coef_array.shape[0], 8):
        for j in range(0, coef_array.shape[1], 8):
            if len(hex_chars) * 4 >= bits:
                break

            block = coef_array[i:i+8, j:j+8]
            if block.shape != (8, 8):
                continue

            coef = int(block[0, 0])
            base_val = coef * quant_00

            found_match = False
            bin_val = bin(abs(base_val))[2:].zfill(12)
            last_4_bits = bin_val[-4:]
            hex_char_ant = f"{int(last_4_bits, 2):x}"
            
            for offset in range(6):
                test_val = base_val + offset
                bin_val = bin(abs(test_val))[2:].zfill(12)
                last_4_bits = bin_val[-4:]
                hex_char = f"{int(last_4_bits, 2):x}"

                if reference_hash and char_index < len(reference_hash) and hex_char == reference_hash[char_index]:
                    hex_chars.append(hex_char)
                    print(f"Block ({i},{j}) coef={coef}, test_val={test_val}, bin={bin_val}, 4 bits: {last_4_bits} → hex imagen: {hex_char_ant}, esperado: {reference_hash[char_index]} (match)")
                    char_index += 1
                    found_match = True
                    break

            if not found_match:
                print(f"[!] No se encontró coincidencia para el carácter {char_index} ({reference_hash[char_index]}) en el bloque ({i},{j})")
                return ''  # solo el primer valor válido de los siguientes 6

    hex_str = ''.join(hex_chars)[:32]  # 32 hex dígitos para 128 bits
    print(f"\n[6] Hash hexadecimal reconstruido: {hex_str}")
    return hex_str



def search_match_with_byte_tolerance(extracted_hash):
    import os

    conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

    cursor = conn.cursor()

    byte_chunks = [int(extracted_hash[i:i+2], 16) for i in range(0, len(extracted_hash), 2)]

    if not byte_chunks:
        print("[!] No hash reconstructed. Aborting search.")
        return

    columns = ', '.join([f'byte{i}' for i in range(len(byte_chunks))])
    query = f"SELECT {columns}, message FROM messages"
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("[!] Database has no messages to compare.")
        return

    best_match = None
    best_hash = None
    highest_similarity = -1

    for row in rows:
        db_bytes = row[:-1]
        db_message = row[-1]
        db_hash = ''.join(f"{b:02x}" for b in db_bytes)
        similarity = compare_hashes(extracted_hash, db_hash)
        print(f"Similarity with {db_hash}: {similarity:.2f}%")

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = db_message
            best_hash = db_hash

    print("Best match found:")
    print(f"DB Hash: {best_hash}")
    print(f"Message: {best_match}")
    print(f"Similarity: {highest_similarity:.2f}%")


def descifrar():
    conn = mysql.connector.connect(
        host='172.21.48.1',
        port=3306,
        user='tfg',
        password='Daniel25071005',
        database='tfg_db'
    )
    cursor = conn.cursor()

    # Get latest messages
    cursor.execute("SELECT " + ", ".join([f"byte{i}" for i in range(16)]) + ", message FROM messages ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[!] No messages in database.")
        return

    output_image = "./src/image/output.jpeg"
    for row in rows:
        reference_hash = ''.join(f"{b:02x}" for b in row[:-1])
        print(f"[DEBUG] Trying reference hash: {reference_hash}")
        extracted_hash = extract_hash_from_dct(output_image, reference_hash=reference_hash)
        if extracted_hash:
            search_match_with_byte_tolerance(extracted_hash)
            break
        else:
            print("[!] Failed with this reference hash. Trying next...")
    search_match_with_byte_tolerance(extracted_hash)


if __name__ == "__main__":
    descifrar()
