import numpy as np
from PIL import Image

def hide_hash_in_image(image_array, hash_bits):
    """Embeds the hash into the least significant bits (LSB) of the image."""
    data_len = len(hash_bits)
    idx = 0

    for i in range(image_array.shape[0]):
        for j in range(image_array.shape[1]):
            for k in range(image_array.shape[2]):  # Iterate over RGB channels
                if idx < data_len:
                    pixel_value = image_array[i, j, k]
                    image_array[i, j, k] = (pixel_value & 0xFE) | int(hash_bits[idx])  # Modify LSB
                    idx += 1
                else:
                    break
            if idx >= data_len:
                break
        if idx >= data_len:
            break

    return image_array

def extract_hash_from_image(image_array, hash_len):
    """Extracts the hidden binary hash from the least significant bits (LSB) of the image."""
    extracted_bits = []
    idx = 0

    for i in range(image_array.shape[0]):
        for j in range(image_array.shape[1]):
            for k in range(image_array.shape[2]):
                if idx < hash_len:
                    extracted_bits.append(str(image_array[i, j, k] & 1))  # Extract LSB
                    idx += 1
                else:
                    break
            if idx >= hash_len:
                break
        if idx >= hash_len:
            break

    extracted_bits_str = ''.join(extracted_bits)
    print(f"Primeros 32 bits extraidos: {extracted_bits_str[:32]}")
    print(f"Últimos 32 bits extraidos: {extracted_bits_str[-32:]}")
    print(f"Total de bits extraídos: {len(extracted_bits_str)}")

    return extracted_bits_str

# Function to save the image with the hidden hash
def save_image(image_array, output_path):
    """Saves the image with the hash hidden."""
    image = Image.fromarray(image_array)
    image.save(output_path)
