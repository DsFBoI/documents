import jpeg_toolbox
import random
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

    # Seleccionar coeficientes de bloques 8x8 del canal Y
    cover = img['coef_arrays'][0][::8, ::8]
    shape = cover.shape
    cover = cover.flatten()
    stego = cover.copy()

    # Incrustar los bits en los LSB de los coeficientes DCT
    for i in range(len(hash_bits)):
        if cover[i] % 2 != hash_bits[i]:
            stego[i] = cover[i] + random.choice([-7, 7])

    # Reconstruir y guardar imagen
    img['coef_arrays'][0][::8, ::8] = stego.reshape(shape)
    jpeg_toolbox.save(img, output_image)
    print("Hash oculto y guardado en 'output.jpeg'.")

if __name__ == "__main__":
    cifrar()
