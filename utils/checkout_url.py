import os
import requests





def generate_paystack_checkout_link(email: str, amount: str, callback_url: str = None) -> dict:
    
    """
    Generate a Paystack checkout payment link.

    Args:
        email (str): Customer's email address.
        amount (float): Payment amount in Naira.
        callback_url (str, optional): URL to redirect to after payment.

    Returns:
        dict: Response containing Paystack's checkout URL or error details.
    """
    
    PAYSTACK_LIVE_SECRET_KEY = os.getenv("PAYSTACK_LIVE_SECRET_KEY")

    if not PAYSTACK_LIVE_SECRET_KEY:
        raise ValueError({"message": "Missing PAYSTACK_SECRET_KEY environment variable"})

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_LIVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount, #int(amount * 100),  # Paystack expects amount in kobo
        #"reference": reference,
    }

    if callback_url:
        payload["callback_url"] = callback_url

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data: dict = response.json()

        if data.get("status"):
            return {
                "status": True,
                "checkout_url": data["data"]["authorization_url"],
                "access_code": data["data"]["access_code"],
            }
        else:
            return {"status": False, "message": data.get("message", "Failed to initialize transaction")}
        
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}

