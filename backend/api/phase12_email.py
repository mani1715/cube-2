"""
PHASE 12.2 - Email Notification System with Resend
Replaces mocked emails with real email delivery
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import resend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

# Logger setup
logger = logging.getLogger(__name__)

# Email configuration
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@acube.com")

# Configure Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend email service configured")
else:
    logger.warning("Resend API key not configured - emails will be mocked")

# Router
phase12_email_router = APIRouter(prefix="/api/phase12/emails", tags=["Phase 12 - Emails"])

# Pydantic Models
class EmailRequest(BaseModel):
    """Generic email request"""
    recipient_email: EmailStr
    subject: str
    html_content: str


# ==================== EMAIL UTILITY FUNCTIONS ====================

async def send_email_async(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email using Resend API (async, non-blocking)
    """
    if not RESEND_API_KEY:
        logger.warning(f"MOCK EMAIL: To={to_email}, Subject={subject}")
        return {
            "status": "mocked",
            "message": "Email service not configured - email was mocked",
            "email_id": "mock_" + str(datetime.utcnow().timestamp())
        }
    
    try:
        params = {
            "from": from_email or SENDER_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        
        logger.info(f"Email sent successfully to {to_email}")
        
        return {
            "status": "success",
            "message": f"Email sent to {to_email}",
            "email_id": email.get("id")
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {
            "status": "failed",
            "message": str(e),
            "email_id": None
        }


# ==================== EMAIL TEMPLATES ====================

def create_session_confirmation_email(
    user_name: str,
    session_date: str,
    session_time: str,
    psychologist_name: str
) -> str:
    """Create HTML email for session booking confirmation"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 30px;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Session Confirmed</h1>
                <p>Your therapy session has been booked</p>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>Your therapy session has been successfully confirmed. We're here to support your mental health journey.</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0;">Session Details</h3>
                    <p><strong>Date:</strong> {session_date}</p>
                    <p><strong>Time:</strong> {session_time}</p>
                    <p><strong>Psychologist:</strong> {psychologist_name}</p>
                </div>
                
                <p>Please arrive 5 minutes early for your session. If you need to reschedule, please contact us at least 24 hours in advance.</p>
                
                <p>Best regards,<br>The A-Cube Mental Health Team</p>
            </div>
            <div class="footer">
                <p>© 2026 A-Cube Mental Health Platform. All rights reserved.</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """


def create_event_registration_email(
    user_name: str,
    event_name: str,
    event_date: str,
    event_time: str,
    event_location: str
) -> str:
    """Create HTML email for event registration confirmation"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .info-box {{
                background: #f8f9fa;
                border-left: 4px solid #f5576c;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Event Registration Confirmed</h1>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>You're all set! Your registration for the following event has been confirmed.</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0;">Event Details</h3>
                    <p><strong>Event:</strong> {event_name}</p>
                    <p><strong>Date:</strong> {event_date}</p>
                    <p><strong>Time:</strong> {event_time}</p>
                    <p><strong>Location:</strong> {event_location}</p>
                </div>
                
                <p>We look forward to seeing you there!</p>
                
                <p>Warm regards,<br>The A-Cube Events Team</p>
            </div>
            <div class="footer">
                <p>© 2026 A-Cube Mental Health Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def create_contact_acknowledgment_email(user_name: str, message_preview: str) -> str:
    """Create HTML email for contact form acknowledgment"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✉️ Message Received</h1>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>Thank you for reaching out to A-Cube Mental Health Platform. We have received your message and our team will get back to you within 24-48 hours.</p>
                
                <p><strong>Your message:</strong><br>"{message_preview}"</p>
                
                <p>If your matter is urgent, please call us directly at our helpline.</p>
                
                <p>Best regards,<br>The A-Cube Support Team</p>
            </div>
            <div class="footer">
                <p>© 2026 A-Cube Mental Health Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def create_payment_success_email(
    user_name: str,
    item_name: str,
    amount: float,
    transaction_id: str
) -> str:
    """Create HTML email for payment success confirmation"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .info-box {{
                background: #f8f9fa;
                border: 2px solid #38ef7d;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Payment Successful</h1>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>Your payment has been processed successfully. Thank you for your purchase!</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0;">Transaction Details</h3>
                    <p><strong>Item:</strong> {item_name}</p>
                    <p><strong>Amount Paid:</strong> ₹{amount:.2f}</p>
                    <p><strong>Transaction ID:</strong> {transaction_id}</p>
                    <p><strong>Date:</strong> {datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC")}</p>
                </div>
                
                <p>You can access your purchase from your dashboard. A receipt has been sent to your email.</p>
                
                <p>Thank you for choosing A-Cube Mental Health Platform!</p>
                
                <p>Best regards,<br>The A-Cube Team</p>
            </div>
            <div class="footer">
                <p>© 2026 A-Cube Mental Health Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def create_welcome_email(user_name: str) -> str:
    """Create HTML email for new user welcome"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .feature {{
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
                background: #f8f9fa;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌟 Welcome to A-Cube!</h1>
                <p>Your mental wellness journey starts here</p>
            </div>
            <div class="content">
                <p>Dear {user_name},</p>
                <p>Welcome to A-Cube Mental Health Platform! We're thrilled to have you join our community dedicated to mental wellness and personal growth.</p>
                
                <h3>What you can do:</h3>
                <div class="feature">
                    <strong>📅 Book Therapy Sessions</strong><br>
                    Connect with licensed psychologists
                </div>
                <div class="feature">
                    <strong>🎯 Attend Events</strong><br>
                    Join workshops and support groups
                </div>
                <div class="feature">
                    <strong>📚 Read Resources</strong><br>
                    Access mental health articles and guides
                </div>
                <div class="feature">
                    <strong>💼 Track Your Journey</strong><br>
                    Manage your sessions and progress
                </div>
                
                <p>If you have any questions, our support team is here to help!</p>
                
                <p>Warm regards,<br>The A-Cube Team</p>
            </div>
            <div class="footer">
                <p>© 2026 A-Cube Mental Health Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


# ==================== EMAIL SERVICE ENDPOINTS ====================

@phase12_email_router.post("/send")
async def send_generic_email(email_request: EmailRequest):
    """
    Send a generic email (for testing or custom use)
    """
    result = await send_email_async(
        to_email=email_request.recipient_email,
        subject=email_request.subject,
        html_content=email_request.html_content
    )
    
    return result


@phase12_email_router.get("/status")
async def get_email_service_status():
    """
    Check email service configuration status
    """
    return {
        "configured": bool(RESEND_API_KEY),
        "provider": "Resend" if RESEND_API_KEY else "Mocked",
        "sender_email": SENDER_EMAIL,
        "message": "Email service is configured" if RESEND_API_KEY else "Email service not configured - using mock mode"
    }
