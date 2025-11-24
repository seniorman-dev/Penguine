from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.bank import Bank
from models.user import User
from sqlalchemy.exc import SQLAlchemyError
from models.wallet import Wallet






class GetUserWallet(Resource):
    @jwt_required()
    def get(self):
        
        #Internal check if the user sending the request is valid
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404
        
        wallet = Wallet.query.filter_by(user_id=user.id).first()
        
        return {
            "id": str(wallet.id),
            "profit_balance": wallet.profit_balance,
            "type": wallet.type,
            "currency": wallet.currency,
            "is_frozen": wallet.is_frozen,
            "total_escrowed_funds": wallet.total_escrowed_funds,
            "created_at": wallet.created_at.isoformat(),
        }, 200

