from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from models.user import User
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from utils.api_key import generate_api_key





# ---------------- Get All Users i.e Merchants (ADMIN) ----------------
class GetUsers(Resource):
    @jwt_required()
    def get(self):
        users = User.query.all()
        ''''data = [
            {
                "id": str(user.id),
                "email": user.email,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]'''
        
        data = []
        for user in users:
            if user.type == "merchant":
                
                data.clear()
                data.append(
                    {
                        "id": str(user.id),
                        "full_name": user.full_name,
                        "email": user.email,
                        "avatar": user.avatar,
                        "otp": user.otp,
                        "api_key": user.api_key,
                        "is_suspended": user.is_suspended,
                        "cac": user.cac,
                        "business_name": user.business_name,
                        "is_verified": user.is_verified,
                        "type": user.type,
                        "created_at": user.created_at.isoformat(),
                    }
                )
        print(f"{data}")
            
        return {"count": len(data), "users": data}, 200


# ---------------- Get User by ID ----------------
class GetUserById(Resource):
    @jwt_required()
    def get(self, user_id: str):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        return {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "avatar": user.avatar,
            "api_key": user.api_key,
            "is_suspended": user.is_suspended,
            "cac": user.cac,
            "business_name": user.business_name,
            "otp": user.otp,
            "type": user.type,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
        }, 200


# ---------------- Update User Info ----------------
class UpdateUser(Resource):
    @jwt_required()
    def patch(self, user_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument("full_name")
        parser.add_argument("avatar")
        parser.add_argument("cac")
        parser.add_argument("business_name")
        data = parser.parse_args()

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            # Only owner or admin can update (for now: match email from JWT)
            current_email = get_jwt_identity()
            if user.email != current_email:
                return {"message": "Permission denied!"}, 403

            if data.get("full_name"):
                user.full_name = data["full_name"]
            if data.get("avatar"):
                user.avatar = data["avatar"]
            if data.get("cac"):
                user.cac = data["cac"]
            if data.get("business_name"):
                user.business_name = data["business_name"]

            db.session.commit()
            return {"message": "User profile updated successfully"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "User profile update failed", "error": str(e)}, 500
        

class GenerateUserApiKey(Resource):
    
    @jwt_required()
    def get(self, user_id: str):

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
            user.api_key = generate_api_key()
            db.session.commit()
            return {"message": "User API Key generated successfully.", "api_key": user.api_key}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Failed to generate user API key!", "error": str(e)}, 500
        

class ChangeUserPassword(Resource):
    @jwt_required()
    def put(self, user_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument("old_password")
        parser.add_argument("new_password")
        
        data = parser.parse_args()

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
            #fetch user password hash and check if it matches
            if not user.check_password(password=data['old_password']):
                return {"message": "Invalid old password!"}, 400
            user.set_password(password=data["password"])
            db.session.commit()
            return {"message": "User password updated successfully"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "User password update failed", "error": str(e)}, 500


# ---------------- Delete User BY ID (ADMIN)----------------
class DeleteUser(Resource):
    @jwt_required()
    def delete(self, user_id: str):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404

            '''current_email = get_jwt_identity()
            if user.email != current_email:
                return {"message": "Permission denied"}, 403'''

            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Deletion failed", "error": str(e)}, 500
