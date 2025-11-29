from flask_mail import Message
# use mail from extensions, NOT from app
from extensions import mail  
import threading
from flask import copy_current_request_context
#import resend




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
        send_email(sender=sender, recipient=recipient, subject=subject, content=content)

    thread = threading.Thread(target=_send)
    thread.start()
    
    

def brevo_mail(sender: str, recipient: str, subject: str,  content: str) -> dict:
    '''msg = Message(
        subject='Test from Flask + Brevo',
        recipients=['recipient@example.com'],
        body='Hello! This email is sent via Brevo SMTP.'
    )'''
    
    msg = Message(subject=subject, body=content, recipients=[recipient],sender=sender)
    
    try:
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Error sending mail with Brevo: {str(e)}'#