from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from models.merchant_transactions import MerchantTransaction
from models.user import User



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

