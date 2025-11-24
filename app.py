





'''
   Why this works:

   All extensions (db, jwt, mail, api) are initialized before importing routes.

   routes.auth_routes is imported inside the function, so circular imports are avoided.

   Everything stays in a single file, but with proper order of initialization.
'''

from flask import Flask
from flask_restful import Api
from config import Config
from extensions import db, jwt, mail, migrate   # includes migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)

    # Import routes AFTER extensions initialize to avoid circular imports
    from routes.auth_routes import (
        Register, VerifyOTP, Login, ForgotPassword, ResetPassword, DeleteAccount
    )
    
    from routes.user_routes import (
        GenerateUserApiKey,
        GetUsers, 
        GetUserById, 
        UpdateUser, 
        DeleteUser,
    )

    from routes.bank_routes import (
        AddBank, 
        GetBanks, 
        UpdateBank, 
        DeleteBank,
    )
    
    from routes.wallet_routes import GetUserWallet
    from routes.merchant_transaction_route import GetMerchantCustomerTransactions
    from routes.admin_transactions_route import GetAdminTransactions
    from routes.penguine_paystack_webhook import PenguinePaystackWebhook
    from routes.escrow_routes import (
        GetEscrowCodeByReference,
        ApplyEscrowCode,
        StartEscrowTransaction,
        WithdrawToBank
    )

    # -------- AUTH ROUTES --------
    api.add_resource(Register, "/auth/register")
    api.add_resource(VerifyOTP, "/auth/verify-otp")
    api.add_resource(Login, "/auth/login")
    api.add_resource(ForgotPassword, "/auth/forgot-password")
    api.add_resource(ResetPassword, "/auth/reset-password")
    api.add_resource(DeleteAccount, "/auth/delete")

    # -------- USER ROUTES --------
    api.add_resource(GenerateUserApiKey, "/users/generate-api-key/<uuid:user_id>")
    api.add_resource(GetUsers, "/users")
    api.add_resource(GetUserById, "/users/<uuid:user_id>")
    api.add_resource(UpdateUser, "/users/update/<uuid:user_id>")
    api.add_resource(DeleteUser, "/users/delete/<uuid:user_id>")

    # -------- USER BANK ROUTES --------
    api.add_resource(AddBank, "/banks/add")
    api.add_resource(GetBanks, "/banks")
    api.add_resource(UpdateBank, "/banks/update/<uuid:bank_id>")
    api.add_resource(DeleteBank, "/banks/delete/<uuid:bank_id>")

    # -------- WALLET ROUTE --------
    api.add_resource(GetUserWallet, "/wallet")

    # -------- MERCHANT ROUTES --------
    api.add_resource(GetMerchantCustomerTransactions, "/transactions/merchant-customers")

    # -------- ADMIN ROUTES --------
    api.add_resource(GetAdminTransactions, "/transactions/admin")

    # -------- PAYSTACK WEBHOOK --------
    api.add_resource(PenguinePaystackWebhook, "/penguine/webhook")

    # -------- WITHDRAW TO BANK --------
    api.add_resource(WithdrawToBank, "/withdraw-funds")

    # -------- PUBLIC ENDPOINTS --------
    api.add_resource(GetEscrowCodeByReference, "/get-escrow-code/<string:api_key>/<string:reference>")
    api.add_resource(ApplyEscrowCode, "/apply-escrow-code")
    api.add_resource(StartEscrowTransaction, "/start-escrow-transaction")

    return app


# ====================== IMPORTANT FOR RENDER / GUNICORN ======================
# This MUST exist so Gunicorn finds the Flask app when it loads "app:app"
app = create_app()
# ============================================================================


# Local development entry point
if __name__ == "__main__":
    app.run(debug=True)
