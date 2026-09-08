import secrets
import hashlib
import smtplib
import os
from datetime import datetime , timezone,timedelta
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
def create_hash_token():
    token=secrets.token_urlsafe(32)
    hash_token=hashlib.sha256(
        token.encode()
    ).hexdigest()
    expires_at=datetime.now(timezone.utc)+timedelta(minutes=10)
    return token,hash_token,expires_at
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
def send_verification_email(email: str , token: str):
    server=smtplib.SMTP(SMTP_HOST,SMTP_PORT)
    server.starttls()
    server.login(EMAIL,PASSWORD)
    message=EmailMessage()
    message["From"]=EMAIL
    message["To"]=email
    message["Subject"]="Verify your email"
    verify_url=f"http://localhost:8000/users/verify-email?token={token}"
    message.set_content(f'''Please verify your email by clicking this link:
      {verify_url}''')
    server.send_message(message)
    server.quit()
def send_password_reset_email(email,token):
    server=smtplib.SMTP(SMTP_HOST,SMTP_PORT)
    server.starttls()
    server.login(EMAIL,PASSWORD)
    message=EmailMessage()
    message["From"]=EMAIL
    message["To"]=email
    message["Subject"]="Reset Password"
    reset_url=f"http://localhost:8000/users/reset-password?token={token}"
    message.set_content(f'''Please reset password by clicking this link:
        {reset_url}''')
    server.send_message(message)
    server.quit()