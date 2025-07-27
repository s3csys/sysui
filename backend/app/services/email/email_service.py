import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        if settings.EMAILS_ENABLED:
            self.config = ConnectionConfig(
                MAIL_USERNAME=settings.SMTP_USER,
                MAIL_PASSWORD=settings.SMTP_PASSWORD,
                MAIL_FROM=settings.EMAILS_FROM_EMAIL,
                MAIL_PORT=settings.SMTP_PORT,
                MAIL_SERVER=settings.SMTP_HOST,
                MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
                MAIL_TLS=settings.SMTP_TLS,
                MAIL_SSL=False,
                USE_CREDENTIALS=True,
                TEMPLATE_FOLDER=Path(settings.EMAIL_TEMPLATES_DIR)
            )
            self.fm = FastMail(self.config)
        else:
            self.fm = None
            logger.warning("Email service is disabled. Set EMAILS_ENABLED=True to enable.")
    
    async def send_email(
        self,
        email_to: List[EmailStr],
        subject: str,
        body: str,
        template_name: Optional[str] = None,
        template_body: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send an email.
        
        Args:
            email_to: List of recipient email addresses
            subject: Email subject
            body: Email body (used if template_name is None)
            template_name: Optional template name
            template_body: Optional template variables
            
        Returns:
            bool: True if email was sent, False otherwise
        """
        if not settings.EMAILS_ENABLED:
            logger.warning(f"Email not sent to {email_to}: Email service is disabled")
            return False
        
        try:
            if template_name:
                # Send email using template
                message = MessageSchema(
                    subject=subject,
                    recipients=email_to,
                    template_body=template_body or {},
                    subtype="html"
                )
                await self.fm.send_message(message, template_name=template_name)
            else:
                # Send plain email
                message = MessageSchema(
                    subject=subject,
                    recipients=email_to,
                    body=body,
                    subtype="html"
                )
                await self.fm.send_message(message)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email_to}: {str(e)}")
            return False
    
    async def send_verification_email(self, email_to: EmailStr, username: str, token: str) -> bool:
        """
        Send a verification email.
        
        Args:
            email_to: Recipient email address
            username: Username of the recipient
            token: Verification token
            
        Returns:
            bool: True if email was sent, False otherwise
        """
        subject = f"{settings.SERVER_NAME} - Verify your email"
        
        # Create verification link
        verification_link = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/verify-email?token={token}"
        
        # Use template if available, otherwise use plain text
        if Path(settings.EMAIL_TEMPLATES_DIR).exists():
            return await self.send_email(
                email_to=[email_to],
                subject=subject,
                body="",  # Not used with template
                template_name="verification.html",
                template_body={
                    "username": username,
                    "verification_link": verification_link,
                    "server_name": settings.SERVER_NAME
                }
            )
        else:
            # Plain text email
            body = f"""
            <p>Hi {username},</p>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_link}">{verification_link}</a></p>
            <p>If you didn't register for {settings.SERVER_NAME}, you can ignore this email.</p>
            """
            return await self.send_email(
                email_to=[email_to],
                subject=subject,
                body=body
            )
    
    async def send_password_reset_email(self, email_to: EmailStr, username: str, token: str) -> bool:
        """
        Send a password reset email.
        
        Args:
            email_to: Recipient email address
            username: Username of the recipient
            token: Password reset token
            
        Returns:
            bool: True if email was sent, False otherwise
        """
        subject = f"{settings.SERVER_NAME} - Password Reset"
        
        # Create reset link
        reset_link = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/reset-password?token={token}"
        
        # Use template if available, otherwise use plain text
        if Path(settings.EMAIL_TEMPLATES_DIR).exists():
            return await self.send_email(
                email_to=[email_to],
                subject=subject,
                body="",  # Not used with template
                template_name="password_reset.html",
                template_body={
                    "username": username,
                    "reset_link": reset_link,
                    "server_name": settings.SERVER_NAME
                }
            )
        else:
            # Plain text email
            body = f"""
            <p>Hi {username},</p>
            <p>You requested a password reset for your {settings.SERVER_NAME} account.</p>
            <p>Please click the link below to reset your password:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>If you didn't request a password reset, you can ignore this email.</p>
            """
            return await self.send_email(
                email_to=[email_to],
                subject=subject,
                body=body
            )


# Create a singleton instance
email_service = EmailService()