"""
Phase 7.1 - Advanced Security & Compliance Router

This router provides endpoints for:
1. Soft delete and restore operations
2. Password rotation management
3. Mock 2FA endpoints (placeholder)
4. Approval workflows for destructive actions
5. Feature toggles
6. Admin notes on records
7. GDPR compliance (data export, purge)
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

from .schemas import (
    ApprovalRequest, ApprovalReview, FeatureToggle, FeatureToggleUpdate,
    AdminNote, PasswordChange, TwoFactorSetup, TwoFactorVerify
)
from .phase7_security import (
    SoftDeleteMixin, mask_email, mask_phone, mask_sensitive_data,
    PasswordRotationManager, TwoFactorAuth, GDPRCompliance,
    add_soft_delete_filter, prepare_entity_for_soft_delete
)
from .permissions import require_super_admin, require_admin_or_above, get_current_admin
from .utils import log_admin_action
from .auth import security
from .rate_limits import limiter, ADMIN_RATE_LIMIT

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

logger = logging.getLogger(__name__)

phase7_router = APIRouter(prefix="/api/admin/security", tags=["Phase 7 - Security"])


# ========================================
# SOFT DELETE & RESTORE ENDPOINTS
# ========================================

@phase7_router.delete("/{entity}/{entity_id}/soft-delete")
@limiter.limit(ADMIN_RATE_LIMIT)
async def soft_delete_entity(
    request: Request,
    entity: str,
    entity_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Soft delete an entity (mark as deleted without removing from database)
    """
    # Validate entity type
    valid_entities = [
        "session_bookings", "events", "event_registrations", "blogs",
        "careers", "career_applications", "volunteers", "psychologists",
        "contact_forms"
    ]
    
    if entity not in valid_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_entities)}"
        )
    
    # Get collection
    collection = db[entity]
    
    # Check if entity exists
    entity_doc = await collection.find_one({"id": entity_id, "is_deleted": False})
    if not entity_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id {entity_id} not found or already deleted"
        )
    
    # Mark as deleted
    soft_delete_data = SoftDeleteMixin.mark_as_deleted(admin["id"], admin["email"])
    await collection.update_one(
        {"id": entity_id},
        {"$set": soft_delete_data}
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="soft_delete",
        entity=entity,
        entity_id=entity_id,
        details=f"Soft deleted {entity} {entity_id}"
    )
    
    return {
        "success": True,
        "message": f"{entity} soft deleted successfully",
        "entity_id": entity_id,
        "deleted_at": soft_delete_data["deleted_at"].isoformat()
    }


@phase7_router.post("/{entity}/{entity_id}/restore")
@limiter.limit(ADMIN_RATE_LIMIT)
async def restore_entity(
    request: Request,
    entity: str,
    entity_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Restore a soft-deleted entity
    """
    # Validate entity type
    valid_entities = [
        "session_bookings", "events", "event_registrations", "blogs",
        "careers", "career_applications", "volunteers", "psychologists",
        "contact_forms"
    ]
    
    if entity not in valid_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_entities)}"
        )
    
    # Get collection
    collection = db[entity]
    
    # Check if entity exists and is deleted
    entity_doc = await collection.find_one({"id": entity_id, "is_deleted": True})
    if not entity_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id {entity_id} not found or not deleted"
        )
    
    # Restore entity
    restore_data = SoftDeleteMixin.restore_deleted()
    await collection.update_one(
        {"id": entity_id},
        {"$set": restore_data}
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="restore",
        entity=entity,
        entity_id=entity_id,
        details=f"Restored {entity} {entity_id}"
    )
    
    return {
        "success": True,
        "message": f"{entity} restored successfully",
        "entity_id": entity_id
    }


@phase7_router.get("/{entity}/deleted")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_deleted_entities(
    request: Request,
    entity: str,
    page: int = 1,
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get list of soft-deleted entities
    """
    # Validate entity type
    valid_entities = [
        "session_bookings", "events", "event_registrations", "blogs",
        "careers", "career_applications", "volunteers", "psychologists",
        "contact_forms"
    ]
    
    if entity not in valid_entities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_entities)}"
        )
    
    # Get collection
    collection = db[entity]
    
    # Calculate pagination
    skip = (page - 1) * limit
    
    # Get deleted entities
    cursor = collection.find({"is_deleted": True}).sort("deleted_at", -1).skip(skip).limit(limit)
    entities = await cursor.to_list(length=limit)
    
    # Get total count
    total = await collection.count_documents({"is_deleted": True})
    
    # Mask sensitive data
    masked_entities = [mask_sensitive_data(e) for e in entities]
    
    return {
        "data": masked_entities,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


# ========================================
# PASSWORD ROTATION ENDPOINTS
# ========================================

@phase7_router.get("/password/status")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_password_status(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Get password rotation status for current admin
    """
    password_changed_at = admin.get("password_changed_at")
    status_info = PasswordRotationManager.get_password_status(password_changed_at)
    
    return {
        "admin_email": admin["email"],
        **status_info
    }


@phase7_router.post("/password/change")
@limiter.limit("5/minute")  # Stricter rate limit for password changes
async def change_password(
    request: Request,
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Change admin password
    """
    from .auth import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as old
    if verify_password(password_data.new_password, admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    await db.admins.update_one(
        {"id": admin["id"]},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "password_changed_at": datetime.utcnow()
            }
        }
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="password_change",
        entity="admins",
        entity_id=admin["id"],
        details="Password changed successfully"
    )
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }


# ========================================
# 2FA ENDPOINTS (MOCK)
# ========================================

@phase7_router.post("/2fa/setup")
@limiter.limit(ADMIN_RATE_LIMIT)
async def setup_2fa(
    request: Request,
    setup_data: TwoFactorSetup,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Setup 2FA for admin account (MOCK)
    """
    # Generate and send OTP
    otp = TwoFactorAuth.generate_otp(admin["email"])
    TwoFactorAuth.send_otp(admin["email"], otp)
    
    return {
        "success": True,
        "message": "[MOCK] 2FA setup initiated. OTP sent to your email.",
        "mock_otp": otp,  # Only for testing - remove in production
        "note": "This is a mock implementation. Real 2FA will be implemented in future."
    }


@phase7_router.post("/2fa/verify")
@limiter.limit(ADMIN_RATE_LIMIT)
async def verify_2fa(
    request: Request,
    verify_data: TwoFactorVerify,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Verify 2FA OTP (MOCK)
    """
    is_valid = TwoFactorAuth.verify_otp(admin["email"], verify_data.otp)
    
    if is_valid:
        # Update admin to enable 2FA
        await db.admins.update_one(
            {"id": admin["id"]},
            {"$set": {"two_factor_enabled": True}}
        )
        
        # Log action
        await log_admin_action(
            db=db,
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="2fa_enabled",
            entity="admins",
            entity_id=admin["id"],
            details="2FA enabled (mock)"
        )
        
        return {
            "success": True,
            "message": "[MOCK] 2FA enabled successfully",
            "note": "This is a mock implementation. Real 2FA will be implemented in future."
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )


@phase7_router.delete("/2fa/disable")
@limiter.limit(ADMIN_RATE_LIMIT)
async def disable_2fa(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Disable 2FA for admin account
    """
    await db.admins.update_one(
        {"id": admin["id"]},
        {"$set": {"two_factor_enabled": False}}
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="2fa_disabled",
        entity="admins",
        entity_id=admin["id"],
        details="2FA disabled"
    )
    
    return {
        "success": True,
        "message": "2FA disabled successfully"
    }


# ========================================
# APPROVAL WORKFLOW ENDPOINTS
# ========================================

@phase7_router.post("/approval/request")
@limiter.limit(ADMIN_RATE_LIMIT)
async def create_approval_request(
    request: Request,
    request_data: ApprovalRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Create an approval request for destructive actions
    """
    # Set requester info
    request_dict = request_data.dict()
    request_dict["requester_id"] = admin["id"]
    request_dict["requester_email"] = admin["email"]
    
    # Insert into database
    await db.approval_requests.insert_one(request_dict)
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="approval_request_created",
        entity="approval_requests",
        entity_id=request_dict["id"],
        details=f"Approval request for {request_data.action_type} on {request_data.entity}"
    )
    
    return {
        "success": True,
        "message": "Approval request created successfully",
        "request_id": request_dict["id"],
        "status": "pending"
    }


@phase7_router.get("/approval/requests")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_approval_requests(
    request: Request,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get approval requests (super_admin sees all, others see own)
    """
    # Build filter
    filter_query = {}
    if admin["role"] != "super_admin":
        filter_query["requester_id"] = admin["id"]
    
    if status:
        filter_query["status"] = status
    
    # Calculate pagination
    skip = (page - 1) * limit
    
    # Get requests
    cursor = db.approval_requests.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
    requests = await cursor.to_list(length=limit)
    
    # Get total count
    total = await db.approval_requests.count_documents(filter_query)
    
    return {
        "data": requests,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@phase7_router.post("/approval/requests/{request_id}/review")
@limiter.limit(ADMIN_RATE_LIMIT)
async def review_approval_request(
    request: Request,
    request_id: str,
    review_data: ApprovalReview,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_super_admin)
):
    """
    Review an approval request (super_admin only)
    """
    # Get request
    request_doc = await db.approval_requests.find_one({"id": request_id})
    if not request_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    if request_doc["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {request_doc['status']}"
        )
    
    # Update request
    await db.approval_requests.update_one(
        {"id": request_id},
        {
            "$set": {
                "status": review_data.status,
                "reviewed_at": datetime.utcnow(),
                "reviewed_by": admin["email"],
                "reviewer_comment": review_data.comment
            }
        }
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="approval_request_reviewed",
        entity="approval_requests",
        entity_id=request_id,
        details=f"Request {review_data.status}: {review_data.comment}"
    )
    
    return {
        "success": True,
        "message": f"Request {review_data.status}",
        "request_id": request_id
    }


# ========================================
# FEATURE TOGGLE ENDPOINTS
# ========================================

@phase7_router.get("/features")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_feature_toggles(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Get all feature toggles
    """
    features = await db.feature_toggles.find({}).to_list(length=100)
    return {"features": features}


@phase7_router.put("/features/{feature_name}")
@limiter.limit(ADMIN_RATE_LIMIT)
async def update_feature_toggle(
    request: Request,
    feature_name: str,
    update_data: FeatureToggleUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_super_admin)
):
    """
    Update feature toggle (super_admin only)
    """
    feature = await db.feature_toggles.find_one({"feature_name": feature_name})
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_name}' not found"
        )
    
    # Update feature
    await db.feature_toggles.update_one(
        {"feature_name": feature_name},
        {
            "$set": {
                "is_enabled": update_data.is_enabled,
                "updated_at": datetime.utcnow(),
                "updated_by": admin["email"]
            }
        }
    )
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="feature_toggle_updated",
        entity="feature_toggles",
        entity_id=feature_name,
        details=f"Feature '{feature_name}' {'enabled' if update_data.is_enabled else 'disabled'}: {update_data.reason or 'No reason provided'}"
    )
    
    return {
        "success": True,
        "message": f"Feature '{feature_name}' {'enabled' if update_data.is_enabled else 'disabled'}",
        "feature_name": feature_name
    }


# ========================================
# ADMIN NOTES ENDPOINTS
# ========================================

@phase7_router.post("/notes")
@limiter.limit(ADMIN_RATE_LIMIT)
async def create_admin_note(
    request: Request,
    note_data: AdminNote,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Create an internal admin note on a record
    """
    note_dict = note_data.dict()
    note_dict["admin_id"] = admin["id"]
    note_dict["admin_email"] = admin["email"]
    
    await db.admin_notes.insert_one(note_dict)
    
    return {
        "success": True,
        "message": "Note created successfully",
        "note_id": note_dict["id"]
    }


@phase7_router.get("/notes/{entity}/{entity_id}")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_admin_notes(
    request: Request,
    entity: str,
    entity_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get all admin notes for a specific record
    """
    notes = await db.admin_notes.find({
        "entity": entity,
        "entity_id": entity_id
    }).sort("created_at", -1).to_list(length=100)
    
    return {"notes": notes}


# ========================================
# GDPR COMPLIANCE ENDPOINTS
# ========================================

@phase7_router.get("/gdpr/retention-policy")
@limiter.limit(ADMIN_RATE_LIMIT)
async def get_retention_policies(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(get_current_admin)
):
    """
    Get data retention policies for all entities
    """
    entities = [
        "session_bookings", "events", "event_registrations", "blogs",
        "careers", "career_applications", "volunteers", "psychologists",
        "contact_forms", "admin_logs", "admins"
    ]
    
    policies = [GDPRCompliance.get_retention_info(entity) for entity in entities]
    
    return {"retention_policies": policies}


@phase7_router.delete("/gdpr/{entity}/{entity_id}/purge")
@limiter.limit("5/minute")  # Stricter limit for destructive actions
async def purge_entity(
    request: Request,
    entity: str,
    entity_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    admin: dict = Depends(require_super_admin)
):
    """
    Permanently delete (purge) a soft-deleted entity (super_admin only)
    GDPR compliance: Right to erasure
    """
    # Get collection
    collection = db[entity]
    
    # Check if entity is soft-deleted
    entity_doc = await collection.find_one({"id": entity_id, "is_deleted": True})
    if not entity_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id {entity_id} not found or not soft-deleted"
        )
    
    # Check if retention period allows purging
    deleted_at = entity_doc.get("deleted_at")
    if not GDPRCompliance.should_purge(entity, deleted_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Retention period not met for {entity}. Cannot purge yet."
        )
    
    # Permanently delete
    await collection.delete_one({"id": entity_id})
    
    # Log action
    await log_admin_action(
        db=db,
        admin_id=admin["id"],
        admin_email=admin["email"],
        action="purge",
        entity=entity,
        entity_id=entity_id,
        details=f"Permanently deleted {entity} {entity_id} (GDPR compliance)"
    )
    
    return {
        "success": True,
        "message": f"{entity} permanently deleted (purged)",
        "entity_id": entity_id
    }
