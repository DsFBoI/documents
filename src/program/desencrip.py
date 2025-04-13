import jpeg_toolbox
import sqlite3

def extract_hash_from_dct(image_path, bits=128):
    """Extracts bits from DCT coefficients and converts to a hexadecimal hash string."""
    img = jpeg_toolbox.load(image_path)
    stego = img['coef_arrays'][0][::8, ::8].flatten()

    message_bits = [int(coef) % 2 for coef in stego[:bits]]
    bin_str = ''.join(map(str, message_bits))

    extracted_hash = hex(int(bin_str, 2))[2:].zfill(32)
    print(f"Hash extraído: {extracted_hash}")
    return extracted_hash

def search_match_with_byte_tolerance(extracted_hash):
    """Searches DB using 2-character hex pairs (1 byte), each with ±8 tolerance."""
    conn = sqlite3.connect('steganography.db')
    cursor = conn.cursor()

    # Convert hash to 2-character chunks
    byte_chunks = [int(extracted_hash[i:i+2], 16) for i in range(0, len(extracted_hash), 2)]

    query_conditions = []
    query_values = []

    for i, byte in enumerate(byte_chunks):
        min_val = max(0, byte - 8)
        max_val = min(255, byte + 8)
        query_conditions.append(f"byte{i} BETWEEN ? AND ?")
        query_values.extend([min_val, max_val])

    query_string = f"SELECT message FROM messages WHERE {' AND '.join(query_conditions)}"

    cursor.execute(query_string, query_values)
    result = cursor.fetchone()
    conn.close()

    if result:
        print(f"Mensaje encontrado: {result[0]}")
    else:
        print("No se encontró un mensaje con este hash.")

def descifrar():
    output_image = "./src/image/output.jpeg"
    extracted_hash = extract_hash_from_dct(output_image)
    search_match_with_byte_tolerance(extracted_hash)

if __name__ == "__main__":
    descifrar()
