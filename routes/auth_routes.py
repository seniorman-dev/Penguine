
import os
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timezone
from extensions import db  # use db from extensions
from models.user import User
from models.wallet import Wallet
from utils.api_key import generate_api_key
from utils.otp_service import generate_otp, otp_expiry_time
from utils.email_service import async_send_global_email, resend_email
from sqlalchemy.exc import SQLAlchemyError




# ---------------- Register -----------------

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("full_name", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        
        #MERCHANT DETAILS
        parser.add_argument("cac")
        parser.add_argument("business_name")
        
        #PENGUINE ADMIN
        parser.add_argument("type")
        
        data: dict = parser.parse_args()
        
        try:
        
            with db.session.begin(): 
                if User.query.filter_by(email=data["email"]).first():
                    return {"message": "Email already registered"}, 400

                otp = generate_otp()
                user = User(email=data["email"])
                user.set_password(data["password"])
                user.otp = otp
                user.otp_expires = otp_expiry_time()
    
                # MERCHANT DETAILS
                user.full_name = data["full_name"]
                user.cac = data.get('cac')
                user.business_name = data.get('business_name')
                user.api_key = generate_api_key()
    
                # ADMIN
                user.type = data.get('type') or "merchant"
                db.session.add(user)
    
                # Create wallet using relationship only (no user_id needed)
                wallet_type = "merchant" if user.type == "merchant" else "admin"
                wallet = Wallet(user=user, type=wallet_type)
                db.session.add(wallet)

                # No need to commit manually here; session.begin() will commit on exit

                token = create_access_token(identity=user.email)
                
                # Only send email *after* successful commit
                # Send OTP email after successful commit
                async_send_global_email(sender=os.getenv("DEFAULT_FROM_EMAIL"), recipient=user.email,subject="Your Verification Code", content=f"Your OTP is {otp}.\nIt expires in 10 minutes.")

                return {
                   "access_token": token,
                   "message": "User registered successfully.\nPlease verify OTP sent to your email."
                }, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Registration failed.", "error": str(e)}, 500


# ---------------- Verify OTP ----------------
class VerifyOTP(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        parser.add_argument("otp", required=True)
        data = parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"message": "User not found"}, 404

        if user.otp != data["otp"]:
            return {"message": "Invalid OTP"}, 400

        if datetime.utcnow() > user.otp_expires:
            return {"message": "OTP expired"}, 400

        user.is_verified = True
        user.otp = None
        db.session.commit()

        return {"message": "Email verified successfully"}, 200

# ---------------- Login -----------------
class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        data = parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"message": "User not found"}, 404
        
        if not user.check_password(data["password"]):
            return {"message": "Invalid login credentials"}, 400

        if not user.is_verified:
            return {"message": "Email not verified"}, 403

        token = create_access_token(identity=user.email)
        return {"access_token": token, "message": "User logged in successfully"}, 200

# ---------------- Forgot Password ----------------
class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        data = parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"message": "User not found"}, 404

        otp = generate_otp()
        user.otp = otp
        user.otp_expires = otp_expiry_time()
        db.session.commit()

        async_send_global_email(sender=os.getenv("DEFAULT_FROM_EMAIL"), recipient=user.email,subject="Your Verification Code", content=f"Your OTP is {otp}.\nIt expires in 10 minutes.")
        return {"message": "OTP sent to your email for password reset"}, 200

# ---------------- Reset Password ----------------
class ResetPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True)
        parser.add_argument("otp", required=True)
        parser.add_argument("new_password", required=True)
        data = parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"message": "User not found"}, 404
        if user.otp != data["otp"]:
            return {"message": "Invalid OTP"}, 400

        if datetime.utcnow() > user.otp_expires:
            return {"message": "OTP expired"}, 400

        user.set_password(data["new_password"])
        user.otp = None
        db.session.commit()

        return {"message": "Password reset successful"}, 200

# ---------------- Delete Account ----------------
class DeleteAccount(Resource):
    @jwt_required()
    def delete(self):
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        db.session.delete(instance=user)
        db.session.commit()
        async_send_global_email(sender=os.getenv("DEFAULT_FROM_EMAIL"), recipient=user.email,subject="Your Account Has Been Deleted", content=f"Hi {user.full_name}, you ochestrated the deletion of your account and as such, your details has been wiped off completely from our system.")
        return {"message": "Account deleted successfully"}, 200
