from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Any, Optional
import uuid


class AdminLogin(BaseModel):
    """Schema for admin login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class AdminToken(BaseModel):
    """Schema for admin token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 480  # minutes


class Admin(BaseModel):
    """Admin user model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    role: str = "admin"  # super_admin, admin, or viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_login: datetime = Field(default_factory=datetime.utcnow)
    # Phase 7.1 - Security enhancements
    password_changed_at: datetime = Field(default_factory=datetime.utcnow)
    two_factor_enabled: bool = False
    two_factor_secret: str = ""  # For future TOTP implementation


class AdminCreate(BaseModel):
    """Schema for creating an admin"""
    email: EmailStr
    password: str = Field(..., min_length=8)


# Admin Activity Log Model
class AdminActivityLog(BaseModel):
    """Schema for admin activity logging"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    admin_email: str
    action: str  # create, update, delete, status_change, login, logout
    entity: str  # sessions, events, blogs, etc.
    entity_id: str = ""
    details: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Refresh Token Model
class RefreshToken(BaseModel):
    """Schema for refresh token storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_revoked: bool = False


# Pagination Response Model
class PaginatedResponse(BaseModel):
    """Schema for paginated API responses"""
    data: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int


# ========================================
# PHASE 7.1 - ADVANCED SECURITY SCHEMAS
# ========================================

# Approval Workflow Schemas
class ApprovalRequest(BaseModel):
    """Schema for admin action approval requests"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str
    requester_email: str
    action_type: str  # delete, bulk_delete, purge, restore
    entity: str  # sessions, events, blogs, etc.
    entity_ids: List[str]
    reason: str = Field(..., max_length=500)
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewer_comment: Optional[str] = None


class ApprovalReview(BaseModel):
    """Schema for reviewing approval requests"""
    status: str  # approved or rejected
    comment: str = Field(..., max_length=500)


# Feature Toggle Schemas
class FeatureToggle(BaseModel):
    """Schema for feature flags"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    feature_name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    is_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str = ""


class FeatureToggleUpdate(BaseModel):
    """Schema for updating feature toggle"""
    is_enabled: bool
    reason: Optional[str] = Field(None, max_length=200)


# Admin Notes Schema
class AdminNote(BaseModel):
    """Schema for admin notes on records"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity: str  # sessions, events, blogs, etc.
    entity_id: str
    admin_id: str
    admin_email: str
    note: str = Field(..., max_length=2000)
    is_internal: bool = True  # Internal notes not visible to users
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Password Change Schema
class PasswordChange(BaseModel):
    """Schema for password change requests"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


# 2FA Schemas (Mock)
class TwoFactorSetup(BaseModel):
    """Schema for 2FA setup"""
    email: EmailStr


class TwoFactorVerify(BaseModel):
    """Schema for 2FA verification"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

