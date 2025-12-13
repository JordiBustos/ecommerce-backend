from typing import List
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


# Configure email connection
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class EmailService:
    """
    Email service for sending emails using fastapi-mail.
    
    Make sure to configure SMTP settings in .env:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASSWORD
    - EMAILS_FROM_EMAIL
    """
    
    @staticmethod
    async def send_verification_email(email: str, token: str, base_url: str) -> None:
        """
        Send verification email to newsletter subscriber
        
        Args:
            email: Recipient email address
            token: Verification token
            base_url: Base URL of the application (e.g., http://localhost:8001)
        """
        verification_link = f"{base_url}/api/v1/newsletter/verify?token={token}"
        
        logger.info(f"[EMAIL] Sending verification email to {email}")
        
        # If SMTP is not configured, fall back to console logging
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning("SMTP not configured. Logging email to console instead.")
            print(f"\n{'='*80}")
            print(f"NEWSLETTER VERIFICATION EMAIL")
            print(f"{'='*80}")
            print(f"To: {email}")
            print(f"Subject: Confirm your newsletter subscription")
            print(f"\nHi there!")
            print(f"\nThank you for subscribing to our newsletter!")
            print(f"\nPlease confirm your subscription by clicking the link below:")
            print(f"\n{verification_link}")
            print(f"\nIf you didn't request this, please ignore this email.")
            print(f"{'='*80}\n")
            return
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 20px 0;
                    background-color: #4CAF50;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Our Newsletter!</h1>
                </div>
                <div class="content">
                    <h2>Hi there!</h2>
                    <p>Thank you for subscribing to our newsletter. We're excited to have you with us!</p>
                    <p>To complete your subscription, please confirm your email address by clicking the button below:</p>
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Confirm Subscription</a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{verification_link}</p>
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        If you didn't request this subscription, please ignore this email.
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 E-Commerce Store. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            message = MessageSchema(
                subject="Confirm your newsletter subscription",
                recipients=[email],
                body=html_body,
                subtype=MessageType.html
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"[EMAIL] Verification email successfully sent to {email}")
            
        except Exception as e:
            logger.error(f"[EMAIL] Failed to send verification email to {email}: {str(e)}")
            # Don't raise exception - we don't want to fail the subscription process
            # Just log the error and the user can retry
            print(f"\nError sending email: {str(e)}")
            print(f"Verification link (for testing): {verification_link}\n")

    @staticmethod
    async def send_welcome_email(email: str) -> None:
        """Send welcome email after successful verification"""
        logger.info(f"[EMAIL] Sending welcome email to {email}")
        
        # If SMTP is not configured, fall back to console logging
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning("SMTP not configured. Logging email to console instead.")
            print(f"\n{'='*80}")
            print(f"NEWSLETTER WELCOME EMAIL")
            print(f"{'='*80}")
            print(f"To: {email}")
            print(f"Subject: Welcome to our newsletter!")
            print(f"\nWelcome!")
            print(f"\nYour subscription has been confirmed.")
            print(f"You'll now receive our latest updates and offers.")
            print(f"{'='*80}\n")
            return
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome!</h1>
                </div>
                <div class="content">
                    <h2>Thank you for confirming your subscription!</h2>
                    <p>Your email address has been successfully verified.</p>
                    <p>You'll now receive our latest updates, exclusive offers, and news about our products.</p>
                    <p>Stay tuned for exciting content!</p>
                    <p style="margin-top: 30px;">
                        <strong>Best regards,</strong><br>
                        The E-Commerce Team
                    </p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 E-Commerce Store. All rights reserved.</p>
                    <p><a href="http://localhost:8001/api/v1/newsletter/unsubscribe?email={email}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            message = MessageSchema(
                subject="Welcome to our newsletter! 🎉",
                recipients=[email],
                body=html_body,
                subtype=MessageType.html
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"[EMAIL] Welcome email successfully sent to {email}")
            
        except Exception as e:
            logger.error(f"[EMAIL] Failed to send welcome email to {email}: {str(e)}")
            print(f"\nError sending welcome email: {str(e)}\n")
