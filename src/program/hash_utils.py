import hashlib
def generate_hash(message, bits=256):
    """Generates a SHA-256 hash of the message.  
    Optionally returns a truncated 128-bit hash if specified.
    """
    if not isinstance(message, str):
        raise ValueError("Message must be a string")

    full_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()

    if bits == 128:
        return full_hash[:32]  # First 128 bits (32 hex characters)
    return full_hash  # Default full 256-bit hash


def compare_hashes(hash1, hash2):
    """Compara dos hashes y devuelve el porcentaje de similitud."""
    hash1_bin = bin(int(hash1, 16))[2:].zfill(256)
    hash2_bin = bin(int(hash2, 16))[2:].zfill(256)


    differences = sum([1 for i in range(len(hash1_bin)) if hash1_bin[i] != hash2_bin[i]])

   
    similarity_percentage = (1 - differences / len(hash1_bin)) * 100
    return similarity_percentage
