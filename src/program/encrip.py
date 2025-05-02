import jpeg_toolbox
import random
import numpy as np
from hash_utils import generate_hash
from db_utils import store_hash_and_message_in_db

def hash_to_bits(hash_hex):
    """Convierte un hash hexadecimal en una lista de bits."""
    return [int(b) for b in bin(int(hash_hex, 16))[2:].zfill(128)]

def cifrar():
    input_image = './src/image/input.jpeg'
    output_image = './src/image/output.jpeg'
    message = "hola que tal estas"

    # [1] Generar hash de 128 bits del mensaje
    hash_128 = generate_hash(message, bits=128)
    print(f"[1] Hash generado (128 bits): {hash_128}")

    # [2] Guardar hash y mensaje en la base de datos
    store_hash_and_message_in_db(hash_128, message)

    # [3] Convertir hash a bits
    hash_bits = hash_to_bits(hash_128)
    print(f"[3] Hash en bits: {hash_bits}\n")

    # [4] Cargar imagen JPEG
    img = jpeg_toolbox.load(input_image)
    print("[4] Imagen cargada correctamente")

    # [5] Obtener tabla de cuantificación y coeficientes
    quant_table = img['quant_tables'][0]
    quant_00 = quant_table[0, 0]
    coef_array = img['coef_arrays'][0].copy()
    print("[5] Tabla de cuantificación obtenida y coeficientes copiados")

    # [6] Incrustar los bits del hash (4 bits por bloque)
    bit_idx = 0
    for i in range(0, coef_array.shape[0], 8):
        for j in range(0, coef_array.shape[1], 8):
            if bit_idx >= len(hash_bits):
                break

            block = coef_array[i:i+8, j:j+8]
            if block.shape != (8, 8):
                continue

            original_coef = int(block[0, 0])
            quantized = original_coef * quant_00
            is_negative = quantized < 0
            bin_value = list(bin(abs(quantized))[2:].zfill(12))

            bits_to_embed = hash_bits[bit_idx:bit_idx+4]
            old_bits = bin_value[-4:]
            for k in range(4):
                if bit_idx + k < len(hash_bits):
                    bin_value[-4 + k] = str(bits_to_embed[k])
            bit_idx += 4

            new_value = int(''.join(bin_value), 2)
            if is_negative:
                new_value = -new_value

            new_coef = new_value // quant_00
            block[0, 0] = new_coef
            coef_array[i:i+8, j:j+8] = block

            print(f"[6] Block ({i},{j})")
            print(f"     Original coef: {original_coef}, Quantized: {quantized}")
            print(f"     Binario antes: {''.join(old_bits)}, después: {''.join(bin_value[-4:])}")
            print(f"     Nuevo valor: {new_value}, Nuevo coef: {new_coef}\n")

    # [7] Guardar coeficientes modificados en la imagen
    img['coef_arrays'][0] = coef_array
    jpeg_toolbox.save(img, output_image)
    print("[7] Hash oculto y guardado en 'output.jpeg'.")

if __name__ == "__main__":
    cifrar()