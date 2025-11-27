from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.bank import Bank
from models.merchant_transactions import MerchantTransaction
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
from models.wallet import Wallet
from utils.checkout_url import generate_paystack_checkout_link
from utils.email_service import async_send_global_email
from utils.paystack_transfer_functions import send_funds








#PUBLIC ENDPOINT 
class ApplyEscrowCode(Resource):
    
    def post(self,):
        parser = reqparse.RequestParser()
        parser.add_argument("api_key", required=True)
        parser.add_argument("escrow_code", required=True)
        data: dict = parser.parse_args()
        
        try:
            # ✅ Atomic transaction
            with db.session.begin():
                
                #1. check if the merchant with the provided API Key exists
                user = User.query.filter_by(api_key=data["api_key"]).first()
                if not user:
                   return {"message": "Merchant not found"}, 404
        
                #2. check if the transaction exists
                transaction = MerchantTransaction.query.filter_by(
                    user=user, 
                    user_id=user.id, 
                    escrow_code=data["escrow_code"]
                ).first()
                if not transaction:
                   return {"message": "Transaction not found"}, 404
               
                #3. send the funds to the settle account json of the transaction, i.e call the paystack transfer API
                #to send a post request of withdrawal or money transfer to the settlement account details of the transaction object
                trx_data: dict = transaction.settlement_account
                send_funds(
                    amount=int(transaction.amount) if transaction.merchant_percentage == 0.0 else int(transaction.amount-transaction.expected_profit),
                    recipient_code=trx_data["recipient_code"],
                    reference=transaction.reference,
                    reason="Release escrow funds."
                )
                
                
                #4. credit the wallet of the merchant his expected profit (assuming he set a merchant percentage when initializing the transaction)
                wallet = Wallet.query.filter_by(user=user, user_id=user.id).first()
                wallet.profit_balance += transaction.expected_profit
                
                #update transaction status of the merchant customer to "completed"
                transaction.status = "completed"
                
                #save to db
                db.session.commit()
            
            # ✅ Only send email *after* successful commit
            async_send_global_email(
                sender="noreply@penguine.ng",
                recipient=user.email, #transaction.merchant_email
                subject=f"Payment Completed!",
                content=f"Hello {transaction.merchant_name}, your customer with the name {transaction.customer_name} has just completed an escrow transaction of NGN{transaction.amount} and your expected profit is {transaction.expected_profit}.\nAvailable wallet balance is NGN{wallet.profit_balance}"
            )
            
            return {"message": "Payment completed successfully.\nAmount has been deposited to settlement account."}, 200
                
                
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Payment processing failed.", "error": str(e)}, 500
        


#PUBLIC ENDPOINT
class StartEscrowTransaction(Resource):
    
    def post(self,):
        
        parser = reqparse.RequestParser()
        parser.add_argument("api_key", required=True)
        parser.add_argument("customer_name", required=True,)
        parser.add_argument("customer_email", required=True)
        parser.add_argument("merchant_name", required=True)
        parser.add_argument("merchant_email", required=True)
        parser.add_argument("amount", required=True)
        parser.add_argument("external_reference", required=True)
        parser.add_argument("merchant_percentage")
        parser.add_argument("webhook_url", required=True)
        parser.add_argument("platform", required=True)
        parser.add_argument("items", required=True)  #list of json
        parser.add_argument("settlement_account", required=True) #json below
        
        '''
        {
            "recipient_code": "RCP_2345555",
            "bank_code": "044",
            "bank_name": "Kuda MFB
        }
        '''

        data: dict = parser.parse_args()
        
        
        try:
            # Atomic transaction
            with db.session.begin():
                #1. check if the merchant with the provided API Key exists
                user = User.query.filter_by(api_key=data["api_key"]).first()
                if not user:
                    return {"message": "Merchant not found"}, 404
                
                #----------Calculate the expected profit of the merchant given the merchant percentage------------#
                expected_profit: float = data.get('merchant_percentage', 0.0) * data.get('amount', 0.0)
                
                #2. save all the customer credentials to the transaction (i.e create a transaction for the merchant's customer)
                transaction = MerchantTransaction(
                    user=user,
                    user_id=user.id,
                    status="pending",
                    customer_name=data['customer_name'],
                    customer_email=data['customer_email'],
                    merchant_name=data['merchant_name'],
                    merchant_email=data['merchant_email'],
                    amount=str(data['amount']),
                    merchant_percentage=data.get('merchant_percentage', 0.0),
                    expected_profit=expected_profit,
                    webhook_url=data['webhook_url'],
                    platform=data['platform'],
                    items=data['items'],
                    settlement_account=data['settlement_account'],
                    external_reference=data['external_reference']
                )
                
                #3. generate a Paystack url link (i.e call a helper function that does that)
                result: dict = generate_paystack_checkout_link(
                    email=data['customer_email'], 
                    amount=data['amount'], 
                    #reference=transaction.reference, 
                    #callback_url="https://api.penguine.onrender.com/penguine/webhook", (to be configured in my Paystack merchant dashboard)
                )
                
                #save to db
                db.session.add(transaction)
                db.session.commit()
                
                #4. return a response with the checkout link/url connected to the above transaction created
                return {"message": "Escrow transaction started successfully", "reference": transaction.reference, "checkout_url": result.get("checkout_url", "")}, 201
                
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Failed to start or initialize escrow transaction.", "error": str(e)}, 500
        
        
        
#PUBLIC ENDPOINT       
# ---------------- Get Escrow code by transaction Reference ----------------
# (to be called by merchant after their customer has made payment via the checkout link so as to reveal the escrow code.)
class GetEscrowCodeByReference(Resource):
    
    def get(self, reference: str, api_key: str):
        try:
            # ✅ Atomic transaction
            with db.session.begin():
                #1. check if the merchant with the provided API Key exists
                user = User.query.filter_by(api_key=api_key).first()
                if not user:
                    return {"message": "Merchant not found"}, 404
                
                #2. fetch the transaction that fulfills the query or filter conditions
                transaction = MerchantTransaction.query.filter_by(
                    user=user,
                    user_id=user.id,
                    reference=reference
                ).first()
                
                #3. check if the transaction exists
                if not transaction:
                    return {"message": "Transaction not found"}, 404
                
                return {"message": "Transaction Escrow code retrieved successfully.", "refernce": transaction.reference, "escrow_code": transaction.escrow_code}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Failed to fetch escrow code via transaction reference", "error": str(e)}, 500
        
        
#PUBLIC ENDPOINT       
# ---------------- Get Transaction and Trigeer Dispute ----------------
class TriggerDispute(Resource):
    
    def post(self,):
        parser = reqparse.RequestParser()
        parser.add_argument("api_key", required=True)
        parser.add_argument("escrow_code", required=True,)
        parser.add_argument("reason", required=True,)
        
        data: dict = parser.parse_args()
        try:
            # Atomic transaction
            with db.session.begin():
                #1. check if the merchant with the provided API Key exists
                user = User.query.filter_by(api_key=data["api_key"]).first()
                if not user:
                    return {"message": "Merchant not found"}, 404
                
                #2. fetch the transaction that fulfills the query or filter conditions
                transaction = MerchantTransaction.query.filter_by(
                    user=user,
                    user_id=user.id,
                    escrow_code=data["escrow_code"]
                ).first()
                
                #3. check if the transaction exists
                if not transaction:
                    return {"message": "Transaction not found"}, 404
                
                transaction.status = "in-dispute"
                
                #update the transaction with reason ""
                transaction.dispute_reason = data["reason"]
                db.session.commit()
                
                #send email to the merchant and the customer
                #merchant
                async_send_global_email(
                    sender="noreply@penguine.ng",
                    recipient=transaction.merchant_email,
                    subject="Transaction Dispute Activated",
                    content=f"Hi {transaction.merchant_name}, a transaction with the id: {transaction.id} and escrow_code: {transaction.escrow_code} just activated dispute.\nNext up, you need to follow up on the dispute resolution of this transaction in your dashboard"
                )
                #customer
                async_send_global_email(
                    sender="noreply@penguine.ng",
                    recipient=transaction.customer_email,
                    subject="Transaction Dispute Activated",
                    content=f"Hi {transaction.customer_name}, a transaction with the id: {transaction.id} and escrow_code: {transaction.escrow_code} just activated dispute.\nNext up, {transaction.merchant_name}  will follow up on the dispute resolution of this transaction to ensure proper settlement of dispute"
                )
                
                return {"message": "Transaction set to 'in-dispute' successfullyy", "status": transaction.status, "escrow_code": transaction.escrow_code, "reason":  transaction.dispute_reason}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Failed to trigger dispute", "error": str(e)}, 500