from flask_mail import Message
# use mail from extensions, NOT from app
from extensions import mail  
import threading
from flask import copy_current_request_context
#import resend
import requests
import os



def send_otp_email(sender: str, recipient: str, otp: str):
    msg = Message(subject="Your Verification Code", recipients=[recipient],sender=sender)
    msg.body = f"Your OTP is {otp}.\nIt expires in 10 minutes."
    mail.send(msg)

def async_send_otp_email(sender: str, recipient: str, otp: str):
    @copy_current_request_context
    def _send():
        send_otp_email(sender=sender, recipient=recipient, otp=otp)

    thread = threading.Thread(target=_send)
    thread.start()



#----------------SEND GLOBAL EMAILS-------------------#
def send_email(sender: str, recipient: str, subject: str,  content: str):
    msg = Message(subject=subject, body=content, recipients=[recipient],sender=sender)
    mail.send(msg)
    
    
    

def async_send_global_email(sender: str, recipient: str, subject: str,  content: str):
    @copy_current_request_context
    def _send():
        send_brevo_email(sender=sender, recipient=recipient, subject=subject, content=content)
        #send_email(sender=sender, recipient=recipient, subject=subject, content=content)

    thread = threading.Thread(target=_send)
    thread.start()
    
    

'''def brevo_mail(sender: str, recipient: str, subject: str,  content: str) -> str:
    
    msg = Message(subject=subject, body=content, recipients=[recipient],sender=sender)
    
    try:
        mail.send(msg)
        print('Email sent successfully!')
        return 'Email sent successfully!'
    except Exception as e:
        print(f'Error sending mail with Brevo: {str(e)}')
        return f'Error sending mail with Brevo: {str(e)}'''
    
    



def send_brevo_email(recipient: str, subject: str, content: str, sender: str, sender_name: str = "Your App"):
    """Send email via Brevo API"""
    
    url = "https://api.brevo.com/v3/emailCampaigns"
    
    headers = {
        "api-key": "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",
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"name": sender_name, "email": sender},
        "to": [{"email": recipient}],
        "subject": subject,
        "htmlContent": content
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        print(f"Email sent!: {response.json()}")  #response.json().get('messageId')
        return True
    else:
        print(f"Error: {response.json()}")
        return False
