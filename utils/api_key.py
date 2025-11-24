import random
import string

def generate_api_key(prefix="Pgn", length=39) -> str:
    """
    Generates a Google Cloud-style API key but for Penguine.
    Example: PgnaSyA7oU-b0rQz1Ogu1LzX8PpZCmhf1e3V6s
    """
    # Characters allowed in Google API keys
    chars = string.ascii_letters + string.digits + "-_"

    # Subtract prefix length to keep total consistent
    key_body = ''.join(random.choices(chars, k=length - len(prefix)))

    return prefix + key_body
