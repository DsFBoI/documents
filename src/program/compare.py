import numpy as np
from PIL import Image

def compare_images_bits(image1_path, image2_path):
    """Compara bit a bit dos imágenes y muestra sus diferencias."""
    
    # Cargar imágenes
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)

    # Convertir imágenes a matrices numpy
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # Verificar que las imágenes tengan el mismo tamaño
    if img1_array.shape != img2_array.shape:
        print("Las imágenes tienen tamaños diferentes y no pueden compararse bit a bit.")
        return

    # Convertir píxeles a binario
    img1_bits = np.unpackbits(img1_array)
    img2_bits = np.unpackbits(img2_array)

    # Comparar bits
    differences = np.where(img1_bits != img2_bits)[0]  # Índices donde los bits son diferentes
    total_bits = img1_bits.size

    # Mostrar resultados
    print(f"\n\nTotal de bits en la imagen: {total_bits}")
    print(f"Total de bits diferentes: {len(differences)}")
    print(f"Porcentaje de diferencias: {len(differences) / total_bits * 100:.6f}%")

    # Mostrar los primeros 32 bits de cada imagen
    print("\nPrimeros 32 bits de la imagen original:")
    print(" ".join(map(str, img1_bits[:32])))
    print("\nPrimeros 32 bits de la imagen modificada:")
    print(" ".join(map(str, img2_bits[:32])))

    # Mostrar los últimos 32 bits de cada imagen
    print("\nÚltimos 32 bits de la imagen original:")
    print(" ".join(map(str, img1_bits[-32:])))
    print("\nÚltimos 32 bits de la imagen modificada:")
    print(" ".join(map(str, img2_bits[-32:])))

# Rutas de las imágenes
original_image_path = "./src/image/input.jpeg"   # Imagen original
modified_image_path = "./src/image/output.jpeg"  # Imagen con el hash oculto

# Comparar imágenes
compare_images_bits(original_image_path, modified_image_path)
