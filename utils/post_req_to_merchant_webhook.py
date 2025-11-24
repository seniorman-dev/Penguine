import os
import requests




def post_to_webhook(
    webhook_url: str, 
    reference: str, 
    externl_reference: str,
    reason: str,
    status: str,
    amount: str,
    event_type: str,
    customer_email: str,
    created_at: str,
    ) -> dict:

    headers = {
        "Content-Type": "application/json"
    }
    payload: dict = {
        "status": status,
        "event_type": event_type,
        "amount": amount, 
        "reference": reference,
        "external_reference": externl_reference,
        "reason": reason,
        "customer_email": customer_email,
        "created_at": created_at
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        '''response.raise_for_status()
        data: dict = response.json()'''
        
        if response.status_code == 200:
            print(f"penguine-escrow successful payment data: {payload}")
            return payload
        else:
            return {"status": False, "message": "Couln't send payment information to the provided webhook url!"}
        
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}

