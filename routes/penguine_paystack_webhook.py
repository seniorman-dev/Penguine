'''
    #Typical event data that Paystack will send to this webhook
    {
       "event": "transfer.success",  #transfer.failed, transfer.reversed,
       "data": {
            "amount": 100000,
            "createdAt": "2025-08-04T10:32:40.000Z",
            "currency": "NGN",
            "domain": "test",
            "failures": null,
            "id": 860703114,
            "integration": {
               "id": 463433,
               "is_live": true,
               "business_name": "Paystack Demo",
               "logo_path": "https://public-files-paystack-prod.s3.eu-west-1.amazonaws.com/integration-logos/hpyxo8n1c7du6gxup7h6.png"
            },
            "reason": "Bonus for the week",
            "reference": "acv_9ee55786-2323-4760-98e2-6380c9cb3f68",
            "source": "balance",
            "source_details": null,
            "status": "success",
            "titan_code": null,
            "transfer_code": "TRF_v5tip3zx8nna9o78",
            "transferred_at": null,
            "updatedAt": "2025-08-04T10:32:40.000Z",
            "recipient": {
              "active": true,
              "createdAt": "2023-07-11T15:42:27.000Z",
              "currency": "NGN",
              "description": "",
              "domain": "test",
              "email": null,
              "id": 56824902,
              "integration": 463433,
              "metadata": null,
              "name": "Jekanmo Padie",
              "recipient_code": "RCP_gd9vgag7n5lr5ix",
              "type": "nuban",
              "updatedAt": "2023-07-11T15:42:27.000Z",
              "is_deleted": false,
              "details": {
                  "authorization_code": null,
                  "account_number": "9876543210",
                  "account_name": null,
                  "bank_code": "044",
                  "bank_name": "Access Bank"
                }
            },
            "session": {
               "provider": null,
               "id": null
            },
            "fee_charged": 0,
            "gateway_response": null
        }
    }

    '''

from flask_restful import Resource
from extensions import db
from flask import request
import os
import hmac
import hashlib
from models.merchant_transactions import MerchantTransaction
from utils.escrow_code import generate_escrow_code
from utils.post_req_to_merchant_webhook import post_to_webhook








class PenguinePaystackWebhook(Resource):
    
    def post(self):
        PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", "nil")

        # Get Paystack signature from headers
        paystack_signature = request.headers.get("x-paystack-signature")
        payload = request.get_data()  # raw bytes

        # Check if signature exists
        if paystack_signature is None:
            return {"message": "Missing Paystack signature"}, 400

        # 2Compute HMAC signature
        computed_signature = hmac.new(
            key=PAYSTACK_SECRET_KEY.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()

        # Compare signatures safely
        if not hmac.compare_digest(computed_signature, paystack_signature):
            return {"message": "Invalid signature"}, 400

        # Parse JSON payload
        event = request.get_json(force=True) or {}
        event_type = event.get("event")
        data: dict = event.get("data", {})

        # send all these (including the event_type) to the merchant webhook #
        reference = data.get("reference")
        reason = data.get("reason")
        created_at = data.get("createdAt")
        status = data.get("status")
        amount = data.get("amount")
        recipient: dict = data.get("recipient", {})
        customer_email = recipient.get("email")
        #----------------Info------------------#

        # Check essential fields before DB operations
        if not all([reference, amount, customer_email]):
            return {"message": "Missing required transaction data"}, 400

        # Handle events
        customer_transaction = MerchantTransaction.query.filter_by(
            amount=amount,
            reference=reference,
            customer_email=customer_email
        ).first()

        if not customer_transaction:
            return {"message": "Transaction not found"}, 404

        if event_type == "transfer.success":
            customer_transaction.escrow_code = generate_escrow_code()
            customer_transaction.status = "in-escrow"
            db.session.commit()
            print(f"Transfer succeeded for {customer_email}: {amount}, ref: {reference}")
            
            # TODO
            #I will leverage the webhoook of the transaction (customer_transaction.webhook_url) then send events to it.
            #i.e write a post request to it.
            post_to_webhook(
                externl_reference=customer_transaction.external_reference,
                webhook_url=customer_transaction.webhook_url,
                reference=reference,
                reason=reason,
                status=status,
                amount=amount,
                event_type=event_type,
                customer_email=customer_email,
                created_at=created_at
            )

        elif event_type == "transfer.failed":
            customer_transaction.status = "failed"
            db.session.commit()
            print(f"Transfer failed for {customer_email}, ref: {reference}")
            post_to_webhook(
                webhook_url=customer_transaction.webhook_url,
                externl_reference=customer_transaction.external_reference,
                reference=reference,
                reason=reason,
                status=status,
                amount=amount,
                event_type=event_type,
                customer_email=customer_email,
                created_at=created_at
            )

        elif event_type == "transfer.reversed":
            customer_transaction.status = "reversed"
            db.session.commit()
            print(f"Transfer reversed for {customer_email}, ref: {reference}")
            post_to_webhook(
                webhook_url=customer_transaction.webhook_url,
                externl_reference=customer_transaction.external_reference,
                reference=reference,
                reason=reason,
                status=status,
                amount=amount,
                event_type=event_type,
                customer_email=customer_email,
                created_at=created_at
            )

        else:
            print(f"Unhandled event type: {event_type}")

        # Always acknowledge Paystack immediately
        return {"status": "success"}, 200
