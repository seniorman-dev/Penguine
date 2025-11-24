import uuid
from datetime import datetime, timezone
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from utils.escrow_code import generate_escrow_code




class AdminTransaction(db.Model):
    
    __tablename__ = "admin_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=False)
    type = Column(String(20), nullable=False)  #deposit, transfer,
    status = Column(String(20), nullable=False)  #pending completed
    currency = Column(String(5), default="NGN")
    reference = Column(String(150), nullable=True)  #populate with paystack reference
    amount = Column(Float(400), nullable=False)
    
    #for transfers
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship (One-To-Many)
    user = db.relationship("User", backref=db.backref("admin_transactions", lazy=True, uselist=True))
    
    def __str__(self):
        return f"{self.id} --> {self.name} {self.account_name} {self.recipient_code}"
