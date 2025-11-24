import random
import string

def generate_escrow_code(prefix="PGN-Escrow", length=25) -> str:
    # Characters allowed in Google API keys
    chars = string.ascii_letters + string.digits + "-_"

    # Subtract prefix length to keep total consistent
    key_body = ''.join(random.choices(chars, k=length - len(prefix)))

    return prefix + key_body

