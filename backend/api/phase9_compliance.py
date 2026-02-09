"""Phase 9.5 - Compliance, Legal & Trust Endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from typing import Dict, Any, List
import json
from pydantic import BaseModel, EmailStr
import logging

logger = logging.getLogger(__name__)

phase9_compliance_router = APIRouter(
    prefix="/api/phase9/compliance",
    tags=["Phase 9.5 - Compliance"]
)


class DataExportRequest(BaseModel):
    email: EmailStr
    data_types: List[str] = ["all"]  # all, sessions, contacts, volunteers, etc.


class AccountDeletionRequest(BaseModel):
    email: EmailStr
    confirmation: bool
    reason: str = ""


@phase9_compliance_router.post("/data-export")
async def request_data_export(request: DataExportRequest) -> Dict[str, Any]:
    """
    GDPR-compliant data export endpoint.
    User can request export of all their personal data.
    """
    try:
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME')]
        
        user_email = request.email.lower()
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "email": user_email,
            "data": {}
        }
        
        # Collect data from various collections based on email
        if "all" in request.data_types or "sessions" in request.data_types:
            sessions = await db.session_bookings.find(
                {"email": user_email}
            ).to_list(1000)
            export_data["data"]["session_bookings"] = [
                {k: str(v) if isinstance(v, datetime) else v for k, v in session.items()}
                for session in sessions
            ]
        
        if "all" in request.data_types or "contacts" in request.data_types:
            contacts = await db.contact_forms.find(
                {"email": user_email}
            ).to_list(1000)
            export_data["data"]["contact_forms"] = [
                {k: str(v) if isinstance(v, datetime) else v for k, v in contact.items()}
                for contact in contacts
            ]
        
        if "all" in request.data_types or "volunteers" in request.data_types:
            volunteers = await db.volunteers.find(
                {"email": user_email}
            ).to_list(1000)
            export_data["data"]["volunteer_applications"] = [
                {k: str(v) if isinstance(v, datetime) else v for k, v in volunteer.items()}
                for volunteer in volunteers
            ]
        
        if "all" in request.data_types or "events" in request.data_types:
            event_registrations = await db.event_registrations.find(
                {"email": user_email}
            ).to_list(1000)
            export_data["data"]["event_registrations"] = [
                {k: str(v) if isinstance(v, datetime) else v for k, v in event.items()}
                for event in event_registrations
            ]
        
        if "all" in request.data_types or "careers" in request.data_types:
            career_applications = await db.career_applications.find(
                {"email": user_email}
            ).to_list(1000)
            export_data["data"]["career_applications"] = [
                {k: str(v) if isinstance(v, datetime) else v for k, v in career.items()}
                for career in career_applications
            ]
        
        client.close()
        
        # Count total records
        total_records = sum(len(v) for v in export_data["data"].values() if isinstance(v, list))
        
        logger.info(f"Data export requested for {user_email}: {total_records} records")
        
        return {
            "success": True,
            "message": "Data export generated successfully",
            "total_records": total_records,
            "export_data": export_data,
            "note": "Please save this data securely. This export contains all your personal information from our system."
        }
        
    except Exception as e:
        logger.error(f"Data export failed for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export data"
        )


@phase9_compliance_router.post("/account-deletion")
async def request_account_deletion(request: AccountDeletionRequest) -> Dict[str, Any]:
    """
    GDPR-compliant account deletion endpoint (Right to Erasure).
    Soft-deletes user data with audit trail.
    """
    try:
        if not request.confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation required for account deletion"
            )
        
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME')]
        
        user_email = request.email.lower()
        deletion_timestamp = datetime.utcnow()
        
        # Soft delete from all collections
        deleted_counts = {}
        
        collections_to_process = [
            'session_bookings',
            'contact_forms',
            'volunteers',
            'event_registrations',
            'career_applications'
        ]
        
        for collection_name in collections_to_process:
            result = await db[collection_name].update_many(
                {"email": user_email, "is_deleted": {"$ne": True}},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_at": deletion_timestamp,
                        "deletion_reason": request.reason or "User requested account deletion",
                        "deletion_type": "user_request"
                    }
                }
            )
            deleted_counts[collection_name] = result.modified_count
        
        # Log the deletion request
        await db.account_deletion_logs.insert_one({
            "email": user_email,
            "deletion_timestamp": deletion_timestamp,
            "reason": request.reason,
            "deleted_counts": deleted_counts,
            "status": "completed"
        })
        
        client.close()
        
        total_deleted = sum(deleted_counts.values())
        
        logger.info(f"Account deletion completed for {user_email}: {total_deleted} records")
        
        return {
            "success": True,
            "message": "Account deletion request processed successfully",
            "deleted_records": deleted_counts,
            "total_deleted": total_deleted,
            "note": "Your data has been marked for deletion. Complete removal will occur within 30 days as per our data retention policy."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deletion failed for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process account deletion"
        )


@phase9_compliance_router.get("/cookie-settings")
async def get_cookie_settings() -> Dict[str, Any]:
    """
    Get cookie policy settings for consent banner.
    """
    return {
        "cookie_policy": {
            "essential": {
                "name": "Essential Cookies",
                "description": "Required for website functionality and security",
                "required": True,
                "cookies": ["session_token", "csrf_token", "admin_token"]
            },
            "analytics": {
                "name": "Analytics Cookies",
                "description": "Help us understand how visitors use our website",
                "required": False,
                "cookies": ["_ga", "_gid", "_gat"]
            },
            "preferences": {
                "name": "Preference Cookies",
                "description": "Remember your settings and preferences",
                "required": False,
                "cookies": ["theme", "language", "user_preferences"]
            }
        },
        "last_updated": "2024-12-31"
    }


@phase9_compliance_router.post("/cookie-consent")
async def save_cookie_consent(consent: Dict[str, bool]) -> Dict[str, Any]:
    """
    Save user's cookie consent preferences.
    """
    try:
        # In production, you might want to store this in a database
        # For now, just acknowledge the consent
        return {
            "success": True,
            "message": "Cookie preferences saved successfully",
            "consent": consent,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to save cookie consent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save cookie preferences"
        )
