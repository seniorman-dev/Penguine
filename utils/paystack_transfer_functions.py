import os
from flask import Response
import requests







def fetch_banks() -> dict:
    """
    FETCH LIST OF BANKS FROM PAYSTACK API
    """
    
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')

    if not PAYSTACK_LIVE_SECRET_KEY:
        raise ValueError({"message": "Missing PAYSTACK_SECRET_KEY environment variable"})
    
    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data: dict = response.json()
    if data.get("status"): 
        print("JSON DATA", data)
        return data
    else:
        return {"status": False, "message": data.get("message", "Failed to fetch commercial banks"), "error": f"{response.text}"},





def resolve_account(account_number: str, bank_code: str) -> dict:
    """
    RESOLVE USER BANK ACCOUNT DETAILS VIA PAYSTACK API
    """
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')

    if not PAYSTACK_LIVE_SECRET_KEY:
        raise ValueError({"message": "Missing PAYSTACK_SECRET_KEY environment variable"})
    
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url,headers=headers)
    response.raise_for_status()
    data: dict = response.json()
    if data.get("status"):  
        print("JSON DATA", data)
        return data
    else:
        return {"status": False, "message": data.get("message", "Failed to resolve user bank account"), "error": f"{response.text}"},
    




def create_transfer_recipient(account_name: str, account_number: str, bank_code: str) -> dict:
    
    """
    Create a transfer recipient from a given bank account detail.
    """
    
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')

    if not PAYSTACK_LIVE_SECRET_KEY:
        raise ValueError({"message": "Missing PAYSTACK_SECRET_KEY environment variable"})

    url = "https://api.paystack.co/transferrecipient"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = { 
       "type": "nuban",
       "name": account_name,
       "account_number": account_number,
       "bank_code": bank_code,
       "currency": "NGN"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data: dict = response.json()

        if data.get("status"):
            '''return {
                "status": True,
                "message": data["message"],
                "data": data["data"],
            }'''
            print(data)
            return data
        else:
            return {"status": False, "message": data.get("message", "Failed to creat transfer recipient info")}
        
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}






def initiate_transfer(amount: int, recipient_code: str, reference: str, reason: str) -> dict:
    
    """
    Initiate Transfer Request with a given recipient.
    """
    
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')

    if not PAYSTACK_LIVE_SECRET_KEY:
        raise ValueError({"message": "Missing PAYSTACK_SECRET_KEY environment variable"})

    url = "https://api.paystack.co/transfer"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = { 
       "source": "balance",
       "amount": amount,
       "recipient": recipient_code, #"RCP_gd9vgag7n5lr5ix",
       "reference": reference,
       "reason": reason, #"Release Escrow Funds"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data: dict = response.json()

        if data.get("status"):
            '''return {
                "status": True,
                "message": data["message"],
                "data": data["data"],
            }'''
            print(data)
            return data
        else:
            return {"status": False, "message": data.get("message", "Failed to initialize tranfer request")}
        
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}
    
    
    
    
    
def finalize_transfer(code: str, otp: str) -> dict:
    
    """
    Finalize Transfer Request with the transfer code and transfer otp.
    """
    
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')
    
    """Deduct money from penguine escrow services wallet and credit actual bank account of the merchant customer or the merchant himself"""
    if code is None:
        raise ValueError({"message": "Transfer code can't be empty"})
    elif otp is None:
        raise ValueError({"message": "Transfer otp or status can't be empty"})
    else:
        url = "https://api.paystack.co/transfer/finalize_transfer"
            
        headers = {
            "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = { 
            "transfer_code": code, 
            "status": otp
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data: dict = response.json()
        if data.get("status"):
            print(data)
            return data
        else:
            return {"status": False, "message": data.get("message", "Failed to finalize tranfer request"), "error": f"{response.text}"},
        
        
        
def send_funds(
    amount: int, 
    recipient_code: str, 
    reference: str,
    reason: str
    )-> dict:
    
        """
        Leverages the (finalize transfer endpoint) to send the money to recipient
        """
        
        PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY", 'nil')
        
        if amount <= 0:
            raise ValueError({"message": "Transfer amount must be positive or greater than 0"})
        
        url = "https://api.paystack.co/transfer"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "source": "balance",
            "amount": amount,  #int(amount * 100),  # Paystack expects amount in kobo
            "recipient": recipient_code,
            "reference": reference,
            "reason": reason,
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data: dict = response.json()
        if data.get("status"):
            print(data)      
            #call the finalize transfer api
            finalize_transfer(
                code=data['transfer_code'],
                otp=data['status']
            )
            return data
        else:
            return {"status": False, "message": data.get("message", "Failed to send funds to recipient"), "error": f"{response.text}"},      
        
    