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
    message = "cuando el grajo vuela bajo hace un frio del carajo 123"

    # Generar hash de 128 bits del mensaje
    hash_128 = generate_hash(message, bits=128)
    print(f"Hash generado (128 bits): {hash_128}")

    # Guardar hash y mensaje en la base de datos
    store_hash_and_message_in_db(hash_128, message)

    # Convertir hash a bits
    hash_bits = hash_to_bits(hash_128)
    print(f"bitshash: {hash_bits}")

    # Cargar imagen JPEG
    img = jpeg_toolbox.load(input_image)

    # Obtener tabla de cuantificación real de la imagen
    quant_table = img['quant_tables'][0]

    # Multiplicar coeficientes por la tabla de cuantificación
    coef_array = img['coef_arrays'][0].copy()
    for i in range(0, coef_array.shape[0], 8):
        for j in range(0, coef_array.shape[1], 8):
            block = coef_array[i:i+8, j:j+8]
            if block.shape == (8, 8):
                coef_array[i:i+8, j:j+8] = block * quant_table

    # Seleccionar bloques 8x8 del canal Y modificados
    cover = coef_array[::8, ::8]
    shape = cover.shape
    cover = cover.flatten()
    stego = cover.copy()

    # Incrustar los bits en los LSB de los coeficientes DCT
    for i in range(len(hash_bits)):
        if cover[i] % 2 != hash_bits[i]:
            stego[i] = cover[i] + random.choice([-7, 7])

    # Restaurar los valores en coef_array
    coef_array[::8, ::8] = stego.reshape(shape)

    # Dividir por la tabla de cuantificación (restauración final)
    for i in range(0, coef_array.shape[0], 8):
        for j in range(0, coef_array.shape[1], 8):
            block = coef_array[i:i+8, j:j+8]
            if block.shape == (8, 8):
                coef_array[i:i+8, j:j+8] = block // quant_table  # División entera

    # Guardar en imagen final
    img['coef_arrays'][0] = coef_array
    jpeg_toolbox.save(img, output_image)
    print("Hash oculto y guardado en 'output.jpeg'.")

if __name__ == "__main__":
    cifrar()
