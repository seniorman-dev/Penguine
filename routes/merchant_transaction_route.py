from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from models.merchant_transactions import MerchantTransaction
from models.user import User
from utils.paystack_transfer_functions import resolve_account, send_funds



# ---------------- Get All CUSTOMERS Transactions (Merchant) ----------------
class GetMerchantCustomerTransactions(Resource):
    @jwt_required()
    def get(self):
        
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "Merchant user not found"}, 404
        
        #fetch the queryset i.e every customer making escrow payments must be linked to the authenticated merchant
        trx_list = MerchantTransaction.query.filter_by(user=user, user_id=user.id)
        
        data = []
        for trx in trx_list:
            data.clear()
            data.append(
                {
                    "id": str(trx.id),
                    "status": trx.status,  #pending, in-escrow, cancelled, completed
                    "currency": trx.currency,
                    "escrow_code": trx.escrow_code,
                    "reference": trx.reference,
                    "amount": trx.amount,
                    
                    #
                    "merchant_percentage": trx.merchant_percentage,
                    "expected_profit": trx.expected_profit,
                    "customer_name": trx.customer_name,
                    "customer_email": trx.customer_email,
                    "merchant_name": trx.merchant_name,
                    "merchant_email": trx.merchant_email,
                    "webhook_url": trx.webhook_url,
                    "platform": trx.platform,
                    "items": trx.items,
                    "settlement_account": trx.settlement_account,
                    "created_at": trx.created_at.isoformat(),
                }
            )
        print(f"{data}")
            
        return {"count": len(data), "transactions": data}, 200



class ResolveAccount(Resource):
    @jwt_required()
    def get(self, account_number: str, bank_code: str):
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404
        
        result: dict = resolve_account(account_number=account_number, bank_code=bank_code)
        if result.get("status"):
            return result, 200
        return result, 400
    
    
class WithdrawFunds(Resource):
    @jwt_required()
    def post(self,):
        parser = reqparse.RequestParser()
        parser.add_argument("recipient_code", type=str, required=True, help="Recipient code is required")
        parser.add_argument("reference", type=str, required=True, help="Transaction reference is required")
        parser.add_argument("reason", type=str, required=True, help="Reason is required")
        parser.add_argument("amount", type=int, required=True, help="Amount is required")

        data = parser.parse_args()
        
        try:
            # ✅ Atomic transaction
            with db.session.begin():
                email = get_jwt_identity()
                user = User.query.filter_by(email=email).first()
                if not user:
                    return {"message": "User not found"}, 404
                
                result: dict = send_funds(
                    amount=int(data["amount"]),
                    recipient_code=data["recipient_code"],
                    reference=data["reference"],
                    reason=data["reason"]
                )
                #save to user transaction history (coming soon)
                if result.get("status"):
                    return result, 200
                return result, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Failed to process withdrawal", "error": str(e)}, 500
        
    