"""
Phase 14.4 - Communication Enhancements
Email templates, enhanced email queue, email tracking, and notification preferences
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import logging
import os
import uuid
import re

from api.admin.permissions import get_current_admin, require_admin_or_above, require_super_admin

logger = logging.getLogger(__name__)

# Get MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


# ============= PYDANTIC MODELS =============

class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    category: str  # 'transactional', 'marketing', 'notification', 'system'
    variables: Optional[List[str]] = []  # e.g., ['user_name', 'booking_id']
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class SendEmailRequest(BaseModel):
    template_id: str
    recipient: EmailStr
    variables: Dict[str, Any] = {}
    priority: str = "normal"  # 'low', 'normal', 'high', 'urgent'


class BatchEmailRequest(BaseModel):
    template_id: str
    recipients: List[EmailStr]
    variables: Dict[str, Any] = {}
    priority: str = "normal"


class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    marketing_emails: bool = True
    session_reminders: bool = True
    event_notifications: bool = True
    blog_updates: bool = False
    newsletter: bool = False
    sms_enabled: bool = False  # Future-ready


# ============= UTILITY FUNCTIONS =============

def render_template(template_body: str, variables: Dict[str, Any]) -> str:
    """
    Render email template with variables
    Replace {{variable_name}} with actual values
    """
    rendered = template_body
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(value))
    return rendered


async def create_email_template(template_data: EmailTemplateCreate, admin_id: str) -> str:
    """Create a new email template"""
    try:
        template_id = str(uuid.uuid4())
        
        template = {
            "id": template_id,
            "name": template_data.name,
            "subject": template_data.subject,
            "body": template_data.body,
            "category": template_data.category,
            "variables": template_data.variables or [],
            "is_active": template_data.is_active,
            "created_by": admin_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.email_templates.insert_one(template)
        logger.info(f"Email template created: {template_id}")
        return template_id
    except Exception as e:
        logger.error(f"Error creating email template: {str(e)}")
        raise


async def queue_email(
    recipient: str,
    subject: str,
    body: str,
    template_id: Optional[str] = None,
    priority: str = "normal",
    metadata: Optional[Dict] = None
) -> str:
    """
    Add email to queue for sending
    Returns email_id
    """
    try:
        email_id = str(uuid.uuid4())
        
        # Determine send_after based on priority
        send_after = datetime.utcnow()
        if priority == "urgent":
            send_after = datetime.utcnow()
        elif priority == "high":
            send_after = datetime.utcnow() + timedelta(minutes=1)
        elif priority == "normal":
            send_after = datetime.utcnow() + timedelta(minutes=5)
        else:  # low
            send_after = datetime.utcnow() + timedelta(minutes=15)
        
        email = {
            "id": email_id,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "template_id": template_id,
            "priority": priority,
            "status": "queued",  # 'queued', 'sending', 'sent', 'failed', 'bounced'
            "retry_count": 0,
            "max_retries": 3,
            "send_after": send_after,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.email_queue.insert_one(email)
        logger.info(f"Email queued: {email_id} to {recipient}")
        return email_id
    except Exception as e:
        logger.error(f"Error queueing email: {str(e)}")
        raise


async def track_email_event(
    email_id: str,
    event_type: str,  # 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'failed'
    metadata: Optional[Dict] = None
):
    """Track email delivery events"""
    try:
        event = {
            "email_id": email_id,
            "event_type": event_type,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }
        
        await db.email_tracking.insert_one(event)
        
        # Update email status in queue
        if event_type in ["sent", "delivered", "failed", "bounced"]:
            await db.email_queue.update_one(
                {"id": email_id},
                {"$set": {"status": event_type, "updated_at": datetime.utcnow()}}
            )
        
        logger.info(f"Email event tracked: {event_type} for {email_id}")
    except Exception as e:
        logger.error(f"Error tracking email event: {str(e)}")


async def send_email_with_template(
    template_id: str,
    recipient: str,
    variables: Dict[str, Any],
    priority: str = "normal"
) -> str:
    """
    Send email using template
    Returns email_id
    """
    try:
        # Get template
        template = await db.email_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Email template not found")
        
        if not template.get("is_active"):
            raise HTTPException(status_code=400, detail="Email template is inactive")
        
        # Render template
        subject = render_template(template["subject"], variables)
        body = render_template(template["body"], variables)
        
        # Queue email
        email_id = await queue_email(
            recipient=recipient,
            subject=subject,
            body=body,
            template_id=template_id,
            priority=priority,
            metadata={"variables": variables}
        )
        
        # Track as queued
        await track_email_event(email_id, "queued")
        
        # Mock sending (in production, this would trigger actual email sending)
        logger.info(f"Mock email sent to {recipient} with template {template_id}")
        
        # Track as sent (mock)
        await track_email_event(email_id, "sent")
        
        # Add to notification history
        await db.notification_history.insert_one({
            "id": str(uuid.uuid4()),
            "recipient": recipient,
            "notification_type": "email",
            "template_id": template_id,
            "email_id": email_id,
            "subject": subject,
            "status": "sent",
            "created_at": datetime.utcnow()
        })
        
        return email_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email with template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_user_notification_preferences(user_id: str) -> Dict[str, Any]:
    """Get user notification preferences"""
    try:
        prefs = await db.notification_preferences.find_one({"user_id": user_id})
        
        if not prefs:
            # Return default preferences
            return {
                "user_id": user_id,
                "email_enabled": True,
                "marketing_emails": True,
                "session_reminders": True,
                "event_notifications": True,
                "blog_updates": False,
                "newsletter": False,
                "sms_enabled": False
            }
        
        return {
            "user_id": prefs.get("user_id"),
            "email_enabled": prefs.get("email_enabled", True),
            "marketing_emails": prefs.get("marketing_emails", True),
            "session_reminders": prefs.get("session_reminders", True),
            "event_notifications": prefs.get("event_notifications", True),
            "blog_updates": prefs.get("blog_updates", False),
            "newsletter": prefs.get("newsletter", False),
            "sms_enabled": prefs.get("sms_enabled", False)
        }
    except Exception as e:
        logger.error(f"Error getting notification preferences: {str(e)}")
        raise


async def update_notification_preferences(user_id: str, preferences: NotificationPreferences):
    """Update user notification preferences"""
    try:
        prefs_data = {
            "user_id": user_id,
            "email_enabled": preferences.email_enabled,
            "marketing_emails": preferences.marketing_emails,
            "session_reminders": preferences.session_reminders,
            "event_notifications": preferences.event_notifications,
            "blog_updates": preferences.blog_updates,
            "newsletter": preferences.newsletter,
            "sms_enabled": preferences.sms_enabled,
            "updated_at": datetime.utcnow()
        }
        
        # Upsert preferences
        await db.notification_preferences.update_one(
            {"user_id": user_id},
            {"$set": prefs_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )
        
        logger.info(f"Notification preferences updated for user {user_id}")
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        raise


# ============= API ROUTER =============

router = APIRouter(prefix="/api/phase14/communication", tags=["Phase 14.4 - Communication"])


# ============= EMAIL TEMPLATES =============

@router.post("/templates")
async def create_template(
    template: EmailTemplateCreate,
    admin = Depends(require_admin_or_above)
):
    """Create a new email template"""
    try:
        template_id = await create_email_template(template, admin["id"])
        return {
            "success": True,
            "template_id": template_id,
            "message": "Email template created successfully"
        }
    except Exception as e:
        logger.error(f"Error in create_template endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin = Depends(require_admin_or_above)
):
    """List all email templates"""
    try:
        query = {}
        if category:
            query["category"] = category
        if is_active is not None:
            query["is_active"] = is_active
        
        templates = await db.email_templates.find(query).sort("created_at", -1).to_list(length=100)
        
        template_list = []
        for template in templates:
            template_list.append({
                "id": template.get("id"),
                "name": template.get("name"),
                "subject": template.get("subject"),
                "category": template.get("category"),
                "variables": template.get("variables", []),
                "is_active": template.get("is_active"),
                "created_at": template.get("created_at").isoformat() if template.get("created_at") else None,
                "updated_at": template.get("updated_at").isoformat() if template.get("updated_at") else None
            })
        
        return {
            "total": len(template_list),
            "templates": template_list
        }
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    admin = Depends(require_admin_or_above)
):
    """Get a specific email template"""
    try:
        template = await db.email_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "id": template.get("id"),
            "name": template.get("name"),
            "subject": template.get("subject"),
            "body": template.get("body"),
            "category": template.get("category"),
            "variables": template.get("variables", []),
            "is_active": template.get("is_active"),
            "created_by": template.get("created_by"),
            "created_at": template.get("created_at").isoformat() if template.get("created_at") else None,
            "updated_at": template.get("updated_at").isoformat() if template.get("updated_at") else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template_update: EmailTemplateUpdate,
    admin = Depends(require_admin_or_above)
):
    """Update an email template"""
    try:
        # Check if template exists
        existing = await db.email_templates.find_one({"id": template_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        if template_update.name is not None:
            update_data["name"] = template_update.name
        if template_update.subject is not None:
            update_data["subject"] = template_update.subject
        if template_update.body is not None:
            update_data["body"] = template_update.body
        if template_update.category is not None:
            update_data["category"] = template_update.category
        if template_update.variables is not None:
            update_data["variables"] = template_update.variables
        if template_update.is_active is not None:
            update_data["is_active"] = template_update.is_active
        
        await db.email_templates.update_one(
            {"id": template_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "template_id": template_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    admin = Depends(require_super_admin)
):
    """Delete an email template"""
    try:
        result = await db.email_templates.delete_one({"id": template_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "message": "Template deleted successfully",
            "template_id": template_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= EMAIL SENDING =============

@router.post("/send-email")
async def send_email(
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
    admin = Depends(require_admin_or_above)
):
    """Send email using template"""
    try:
        email_id = await send_email_with_template(
            template_id=request.template_id,
            recipient=request.recipient,
            variables=request.variables,
            priority=request.priority
        )
        
        return {
            "success": True,
            "email_id": email_id,
            "recipient": request.recipient,
            "message": "Email queued for sending"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-send")
async def batch_send_emails(
    request: BatchEmailRequest,
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin)
):
    """Send batch emails to multiple recipients"""
    try:
        email_ids = []
        
        for recipient in request.recipients:
            email_id = await send_email_with_template(
                template_id=request.template_id,
                recipient=recipient,
                variables=request.variables,
                priority=request.priority
            )
            email_ids.append(email_id)
        
        return {
            "success": True,
            "total_recipients": len(request.recipients),
            "email_ids": email_ids,
            "message": f"Batch emails queued for {len(request.recipients)} recipients"
        }
    except Exception as e:
        logger.error(f"Error in batch send: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= EMAIL QUEUE =============

@router.get("/email-queue")
async def get_email_queue(
    status: Optional[str] = None,
    limit: int = 50,
    admin = Depends(require_admin_or_above)
):
    """View email queue"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        emails = await db.email_queue.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        email_list = []
        for email in emails:
            email_list.append({
                "id": email.get("id"),
                "recipient": email.get("recipient"),
                "subject": email.get("subject"),
                "priority": email.get("priority"),
                "status": email.get("status"),
                "retry_count": email.get("retry_count"),
                "send_after": email.get("send_after").isoformat() if email.get("send_after") else None,
                "created_at": email.get("created_at").isoformat() if email.get("created_at") else None
            })
        
        return {
            "total": len(email_list),
            "emails": email_list
        }
    except Exception as e:
        logger.error(f"Error getting email queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= EMAIL TRACKING =============

@router.get("/tracking/{email_id}")
async def get_email_tracking(
    email_id: str,
    admin = Depends(require_admin_or_above)
):
    """Get tracking data for an email"""
    try:
        # Get email from queue
        email = await db.email_queue.find_one({"id": email_id})
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get all tracking events
        events = await db.email_tracking.find({"email_id": email_id}).sort("timestamp", 1).to_list(length=100)
        
        event_list = []
        for event in events:
            event_list.append({
                "event_type": event.get("event_type"),
                "timestamp": event.get("timestamp").isoformat() if event.get("timestamp") else None,
                "metadata": event.get("metadata")
            })
        
        return {
            "email_id": email_id,
            "recipient": email.get("recipient"),
            "subject": email.get("subject"),
            "status": email.get("status"),
            "events": event_list,
            "total_events": len(event_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= NOTIFICATION PREFERENCES =============

@router.get("/preferences/{user_id}")
async def get_preferences(
    user_id: str,
    admin = Depends(require_admin_or_above)
):
    """Get user notification preferences"""
    try:
        prefs = await get_user_notification_preferences(user_id)
        return prefs
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences/{user_id}")
async def set_preferences(
    user_id: str,
    preferences: NotificationPreferences,
    admin = Depends(require_admin_or_above)
):
    """Set user notification preferences"""
    try:
        await update_notification_preferences(user_id, preferences)
        return {
            "success": True,
            "user_id": user_id,
            "message": "Notification preferences updated successfully"
        }
    except Exception as e:
        logger.error(f"Error setting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= NOTIFICATION HISTORY =============

@router.get("/history/{user_id}")
async def get_notification_history(
    user_id: str,
    limit: int = 50,
    admin = Depends(require_admin_or_above)
):
    """Get notification history for a user"""
    try:
        # Get user to find their email
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = user.get("email")
        
        # Get notification history
        notifications = await db.notification_history.find({
            "recipient": user_email
        }).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        notification_list = []
        for notif in notifications:
            notification_list.append({
                "id": notif.get("id"),
                "notification_type": notif.get("notification_type"),
                "subject": notif.get("subject"),
                "status": notif.get("status"),
                "created_at": notif.get("created_at").isoformat() if notif.get("created_at") else None
            })
        
        return {
            "user_id": user_id,
            "total": len(notification_list),
            "notifications": notification_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= SYSTEM TEMPLATES INITIALIZATION =============

async def initialize_default_templates():
    """Initialize default email templates"""
    try:
        existing_count = await db.email_templates.count_documents({})
        if existing_count > 0:
            logger.info(f"Email templates already exist ({existing_count}), skipping initialization")
            return
        
        default_templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "Welcome Email",
                "subject": "Welcome to A-Cube Mental Health Platform, {{user_name}}!",
                "body": """
Dear {{user_name}},

Welcome to A-Cube! We're thrilled to have you join our mental health community.

Our platform offers:
- Professional therapy sessions
- Community events and workshops
- Educational blog content
- Supportive resources

Get started by exploring our services at {{platform_url}}.

Best regards,
The A-Cube Team
                """,
                "category": "transactional",
                "variables": ["user_name", "platform_url"],
                "is_active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Session Confirmation",
                "subject": "Your therapy session is confirmed - {{session_date}}",
                "body": """
Hi {{user_name}},

Your therapy session has been confirmed!

Session Details:
- Date: {{session_date}}
- Time: {{session_time}}
- Psychologist: {{psychologist_name}}
- Session ID: {{session_id}}

Please arrive 5 minutes early. If you need to reschedule, please contact us at least 24 hours in advance.

Take care,
A-Cube Team
                """,
                "category": "transactional",
                "variables": ["user_name", "session_date", "session_time", "psychologist_name", "session_id"],
                "is_active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Event Registration",
                "subject": "You're registered for {{event_name}}",
                "body": """
Hello {{user_name}},

Thank you for registering for our event!

Event: {{event_name}}
Date: {{event_date}}
Time: {{event_time}}
Location: {{event_location}}

We look forward to seeing you there!

Best,
A-Cube Events Team
                """,
                "category": "transactional",
                "variables": ["user_name", "event_name", "event_date", "event_time", "event_location"],
                "is_active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Re-engagement Email",
                "subject": "We miss you at A-Cube, {{user_name}}",
                "body": """
Hi {{user_name}},

We noticed you haven't been active recently, and we wanted to reach out!

Here's what's new:
- New blog posts about {{trending_topic}}
- Upcoming events you might enjoy
- Special offers on therapy sessions

Come back and continue your mental wellness journey with us.

Visit us: {{platform_url}}

Warm regards,
A-Cube Team
                """,
                "category": "marketing",
                "variables": ["user_name", "trending_topic", "platform_url"],
                "is_active": True,
                "created_by": "system",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await db.email_templates.insert_many(default_templates)
        logger.info(f"Initialized {len(default_templates)} default email templates")
    except Exception as e:
        logger.error(f"Error initializing default templates: {str(e)}")
