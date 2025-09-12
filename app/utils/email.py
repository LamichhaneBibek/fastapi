# app/services/email_service.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import CONFIG

logger = logging.getLogger(__name__)

def send_email(to: str, subject: str, body: str, html_body: str = ""):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = CONFIG.SMTP_USER
        msg['To'] = to

        # Add text version
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)

        # Add HTML version if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

        with smtplib.SMTP(CONFIG.SMTP_HOST, CONFIG.SMTP_PORT) as server:
            server.starttls()
            server.login(CONFIG.SMTP_USER, CONFIG.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to}")

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        raise

def send_verification_email(to_email: str, token: str):
    """Send email verification link"""
    verify_link = f"{CONFIG.FRONTEND_URL}/api/auth/verify-email?token={token}"
    subject = "Verify Your Email Address"

    # Text version
    text_body = f"""
    Welcome! Please verify your email address.

    Click the link below to verify your email:
    {verify_link}

    This link will expire in 24 hours.

    If you didn't create an account, please ignore this email.
    """

    # HTML version for better presentation
    html_body = f"""
    <html>
    <body>
        <h2>Welcome! Please verify your email address</h2>
        <p>Thank you for creating an account. To complete your registration, please click the button below:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_link}"
               style="background-color: #007bff; color: white; padding: 12px 30px;
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email Address
            </a>
        </div>

        <p>Or copy and paste this link into your browser:</p>
        <p><a href="{verify_link}">{verify_link}</a></p>

        <p><small>This link will expire in 24 hours.</small></p>
        <p><small>If you didn't create an account, please ignore this email.</small></p>
    </body>
    </html>
    """

    send_email(to_email, subject, text_body, html_body)
