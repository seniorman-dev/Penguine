import uuid
from datetime import datetime, timezone
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey




class Wallet(db.Model):
    
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    profit_balance = Column(Float(400), default=0.00)
    total_escrowed_funds = Column(Float(1000), default=0.00)
    type = Column(String(10), default="merchant")  #admin
    currency = Column(String(5), default="NGN")
    is_frozen = Column(Boolean(create_constraint=False), default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship (One-To-One)
    user = db.relationship("User", backref=db.backref("wallets", lazy=True, uselist=False))
    
    def __str__(self):
        return f"{self.id} --> {self.profit_balance} {self.total_escrowed_funds} {self.type}"
