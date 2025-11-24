import uuid
from datetime import datetime, timezone
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint




class Bank(db.Model):
    
    __tablename__ = "banks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=False)
    bank_code = Column(String(20), nullable=False)
    recipient_code = Column(String(40), nullable=False)
    name = Column(String(100), nullable=False)
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship (One-To-Many)
    user = db.relationship("User", backref=db.backref("banks", lazy=True, uselist=True))
    
    __table_args__ = (
        UniqueConstraint("user_id", "account_number", "bank_code", name="unique_user_bank_account"),
    )
    
    def __str__(self):
        return f"{self.id} --> {self.name} {self.account_name} {self.recipient_code}"
