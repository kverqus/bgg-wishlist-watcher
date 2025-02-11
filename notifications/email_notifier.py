import smtplib
import os

from email.mime.text import MIMEText
from .base import NotificationBase

class EmailNotifier(NotificationBase):
    def send(self, title, message):
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'your_email@gmail.com')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_email_password') # App password if using gmail
        TO_EMAIL = os.getenv('TO_EMAIL', 'recipient@example.com')

        msg = MIMEText(message)
        msg['Subject'] = title
        msg['From'] = EMAIL_USERNAME
        msg['To'] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, TO_EMAIL, msg.as_string())
