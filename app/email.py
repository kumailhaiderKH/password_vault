from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import settings

def send_verification_email(email: str, token:str):
    verification_link = f"http://localhost:8000/users/verify/{token}"
    message = Mail(
        from_email = settings.sender_email,
        to_emails = email,
        subject = "Verify your email",
        html_content=f"""
            <h2>Welcome to Password Vault!</h2>
            <p>Click the link below to verify your email:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
        """
    )
    sg = SendGridAPIClient(settings.sendgrid_api_key)
    sg.send(message)

