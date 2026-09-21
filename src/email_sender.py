import smtplib

from email.message import EmailMessage
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL

message = EmailMessage()

message['Subject'] = 'Flight Price Alert'
message['From'] = EMAIL_ADDRESS
message['To'] = RECIPIENT_EMAIL


def send_email(body):
    message.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)
