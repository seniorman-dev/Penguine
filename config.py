import os
from datetime import timedelta
from dotenv import load_dotenv








#load_dotenv()

class Config:
    
    # General Flask config
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    # Token expiry settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_ACCESS_EXPIRES_DAYS", 1)))  # default 7 days
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", 7)))  # default 30 days

    # Mail settings
    MAIL_SERVER = os.getenv("EMAIL_HOST")
    MAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("EMAIL_HOST_USER")
    MAIL_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
