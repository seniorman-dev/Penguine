from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.admin_transaction import AdminTransaction
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from models.user import User





# ---------------- Get All Admin Transactions (ADMIN) ----------------
class GetAdminTransactions(Resource):
    @jwt_required()
    def get(self):
        
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "Admin user not found"}, 404
        
        #fetch the queryset
        trx_list = AdminTransaction.query.filter_by(user=user, user_id=user.id)
        
        data = []
        for trx in trx_list:
            data.clear()
            data.append(
                {
                    "id": str(trx.id),
                    "type": trx.type,  #deposit or transfer
                    "status": trx.status,
                    "currency": trx.currency,
                    "reference": trx.reference,
                    "amount": trx.amount,
                    #for transfers
                    "account_name": trx.account_name,
                    "bank_name": trx.bank_name,
                    "account_number": trx.account_number,
                    "created_at": trx.created_at.isoformat(),
                }
            )
        print(f"{data}")
            
        return {"count": len(data), "transactions": data}, 200

