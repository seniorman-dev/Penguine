import uuid
from datetime import datetime, timezone, timedelta
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime






class User(db.Model):
    
    #declare the table name in the SQL DB
    __tablename__ = "users"
    
    # ✅ auto-generate UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    full_name = Column(String(500), nullable=True)
    email = Column(String(120), unique=True, nullable=False)
    avatar = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    otp = Column(String(6), nullable=True)
    otp_expires = Column(DateTime)
    
    #PENGUINE USER  (merchant) OR (ceo, front-desk)
    type = Column(String(250), default="merchant", nullable=True)  
    
    #MERCHANT
    cac = Column(String(250), nullable=True)
    business_name = Column(String(500), nullable=True)
    api_key = Column(String(300), nullable=True,)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __str__(self):
        return f"{self.id} --> {self.full_name} {self.email}"

