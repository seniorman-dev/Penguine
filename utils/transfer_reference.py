import uuid




def generate_transfer_reference() -> str:
    """
    Generate a unique transfer reference using UUID v4.
    Example: 'trans_3f4a7b24-2e43-4bda-b07a-3f7b312ce9b8'
    """
    return f"{uuid.uuid4()}"
