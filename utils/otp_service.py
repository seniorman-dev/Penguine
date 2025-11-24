import random, string
from datetime import datetime, timedelta, timezone


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def otp_expiry_time(minutes: int = 10) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
