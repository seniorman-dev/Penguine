import os
import uuid
from datetime import datetime, timezone
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, ARRAY, JSON
from utils.escrow_code import generate_escrow_code
from utils.db_helpers import adaptive_array_or_json
from utils.transfer_reference import generate_transfer_reference





class MerchantTransaction(db.Model):
    
    __tablename__ = "merchant_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=False)
    
    #pending, failed, reversed, in-dispute, in-escrow, cancelled, completed. (only merchant admin can set status to cancelled)
    status = Column(String(20), nullable=False) 
    escrow_code = Column(String(50), nullable=True,)
    currency = Column(String(5), default="NGN")
    
    
    ###################################
    merchant_name = Column(String(250), nullable=False)
    merchant_email = Column(String(250), nullable=False)
    reference = Column(String(150), nullable=False, default=f"{generate_transfer_reference()}")
    external_reference = Column(String(300), nullable=True)
    amount = Column(Float(400), nullable=False)
    
    merchant_percentage = Column(Float(8), default=0.0)
    expected_profit = Column(Float(400), default=0.0)
    customer_name = Column(String(150), nullable=False)
    customer_email = Column(String(150), nullable=False)
    webhook_url = Column(String(250), nullable=False)
    platform = Column(String(250), nullable=False)  #e.g TheBroomApp, Aizen, Penguine, Pika, Kuda
    settlement_account = Column(JSON(), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Use ARRAY if PostgreSQL, JSON if SQLite
    items = Column(adaptive_array_or_json(), nullable=False)

    # Relationship (One-To-Many)
    user = db.relationship("User", backref=db.backref("merchant_transactions", lazy=True, uselist=True))
    
    
    def __str__(self):
        return f"{self.id} --> {self.status} {self.reference} {self.amount}"
    
    
    def __repr__(self):
        return f"<Transaction {self.reference}>"
