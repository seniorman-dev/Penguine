from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.bank import Bank
from models.user import User
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.paystack_transfer_functions import fetch_banks, resolve_account





class AddBank(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("recipient_code", required=True)
        parser.add_argument("bank_code", required=True)
        parser.add_argument("bank_name", required=True)
        parser.add_argument("account_number", required=True)
        parser.add_argument("account_name", required=True)
        data = parser.parse_args()

        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        # Check for duplicates
        existing_bank = Bank.query.filter_by(
            user_id=user.id,
            account_number=data["account_number"],
            account_name=data["account_name"],
            bank_name=data["bank_name"],
            bank_code=data["bank_code"],
            recipient_code=data["recipient_code"]
        ).first()
        if existing_bank:
            return {"message": "Bank account already added"}, 400

        try:
            bank = Bank(
                user_id=user.id,
                recipient_code=data["recipient_code"],
                bank_code=data["bank_code"],
                name=data["bank_name"],
                account_number=data["account_number"],
                account_name=data["account_name"],
            )
            db.session.add(bank)
            db.session.commit()
            return {"message": "Bank added successfully"}, 201

        except IntegrityError:
            db.session.rollback()
            return {"message": "Bank account already exists"}, 400
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Error adding bank", "error": str(e)}, 500



class GetBanks(Resource):
    @jwt_required()
    def get(self):
        #Internal check if the user sending the request is valid
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        banks = [
            {
                "id": str(bank.id),
                "name": bank.name,
                "recipient_code": bank.recipient_code,
                "bank_code": bank.bank_code,
                "account_number": bank.account_number,
                "account_name": bank.account_name,
                "created_at": bank.created_at.isoformat(),
            }
            for bank in user.banks
        ]

        return {"count": len(banks), "banks": banks}, 200
    
    
class GetPaystackBanks(Resource):
    def get(self):
        result: dict = fetch_banks()
        if result.get("status"):
            return result, 200
        return result, 400


class UpdateBank(Resource):
    @jwt_required()
    def put(self, bank_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument("recipient_code", required=True)
        parser.add_argument("bank_code", required=True)
        parser.add_argument("bank_name")
        parser.add_argument("account_number")
        parser.add_argument("account_name")
        data = parser.parse_args()
        
        #Internal check if the user sending the request is valid
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        bank = Bank.query.filter_by(id=bank_id, user_id=user.id).first()
        if not bank:
            return {"message": "Bank not found"}, 404
        
        if data.get("recipient_code"):
            bank.recipient_code = data["recipient_code"]
        if data.get("bank_code"):
            bank.bank_code = data["bank_code"]
        if data.get("bank_name"):
            bank.name = data["bank_name"]
        if data.get("account_number"):
            bank.account_number = data["account_number"]
        if data.get("account_name"):
            bank.account_name = data["account_name"]

        try:
            db.session.commit()
            return {"message": "Bank updated successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Update failed", "error": str(e)}, 500


class DeleteBank(Resource):
    @jwt_required()
    def delete(self, bank_id: str):
        
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        bank = Bank.query.filter_by(id=bank_id, user_id=user.id).first()
        if not bank:
            return {"message": "Bank not found"}, 404

        try:
            db.session.delete(bank)
            db.session.commit()
            return {"message": "Bank deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Delete failed", "error": str(e)}, 500


