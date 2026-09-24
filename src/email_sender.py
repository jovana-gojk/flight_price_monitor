import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
recipient_1 = os.getenv("EMAIL_RECIPIENT_1")
recipient_2 = os.getenv("EMAIL_RECIPIENT_2")


def send_email(body, recipient):
    message = EmailMessage()

    message['Subject'] = 'Flight Price Alert'
    message['From'] = email_address
    message['To'] = recipient
    message.set_content(body)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(message)
