# utils/db_helpers.py
import os
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import JSON, String

def adaptive_array_or_json():
    db_url = os.getenv("DATABASE_URL", "")
    return ARRAY(String) if "postgres" in db_url else JSON
