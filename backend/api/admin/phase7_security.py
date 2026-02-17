"""
Phase 7.1 - Advanced Security & Compliance Module

This module provides:
1. Soft delete functionality for all entities
2. Password rotation enforcement
3. Mock 2FA structure (placeholder for future)
4. Sensitive field masking utilities
5. GDPR compliance helpers
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)


# ========================================
# SOFT DELETE UTILITIES
# ========================================

class SoftDeleteMixin:
    """Mixin to add soft delete fields to any model"""
    
    @staticmethod
    def get_soft_delete_fields() -> Dict[str, Any]:
        """Returns fields needed for soft delete"""
        return {
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None
        }
    
    @staticmethod
    def mark_as_deleted(admin_id: str, admin_email: str) -> Dict[str, Any]:
        """Returns update fields to mark record as deleted"""
        return {
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "deleted_by": admin_email
        }
    
    @staticmethod
    def restore_deleted() -> Dict[str, Any]:
        """Returns update fields to restore a deleted record"""
        return {
            "is_deleted": False,
            "deleted_at": None,
            "deleted_by": None
        }


# ========================================
# SENSITIVE FIELD MASKING
# ========================================

def mask_email(email: str) -> str:
    """
    Mask email address for privacy
    Example: john.doe@example.com -> j***e@e****e.com
    """
    if not email or '@' not in email:
        return email
    
    try:
        local, domain = email.split('@')
        domain_parts = domain.split('.')
        
        # Mask local part
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        # Mask domain
        if len(domain_parts[0]) <= 2:
            masked_domain = domain_parts[0][0] + '*'
        else:
            masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 2) + domain_parts[0][-1]
        
        return f"{masked_local}@{masked_domain}.{domain_parts[-1]}"
    except Exception as e:
        logger.error(f"Error masking email: {e}")
        return "***@***.com"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy
    Example: +1234567890 -> +123****890
    """
    if not phone:
        return phone
    
    try:
        # Remove non-digit characters for processing
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) <= 6:
            return '*' * len(digits)
        
        # Show first 3 and last 3 digits
        return phone[:3] + '*' * (len(digits) - 6) + phone[-3:]
    except Exception as e:
        logger.error(f"Error masking phone: {e}")
        return "***-***-****"


def mask_ip(ip: str) -> str:
    """
    Mask IP address for privacy
    Example: 192.168.1.100 -> 192.168.*.***
    """
    if not ip:
        return ip
    
    try:
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.***"
        return "***.***.***"
    except Exception as e:
        logger.error(f"Error masking IP: {e}")
        return "***.***.***.***"


def mask_sensitive_data(data: Dict[str, Any], fields_to_mask: List[str] = None) -> Dict[str, Any]:
    """
    Mask sensitive fields in a dictionary
    
    Args:
        data: Dictionary containing data to mask
        fields_to_mask: List of field names to mask (defaults to common sensitive fields)
    
    Returns:
        Dictionary with masked fields
    """
    if fields_to_mask is None:
        fields_to_mask = ['email', 'phone', 'ip', 'ip_address']
    
    masked_data = data.copy()
    
    for field in fields_to_mask:
        if field in masked_data and masked_data[field]:
            if 'email' in field.lower():
                masked_data[field] = mask_email(str(masked_data[field]))
            elif 'phone' in field.lower():
                masked_data[field] = mask_phone(str(masked_data[field]))
            elif 'ip' in field.lower():
                masked_data[field] = mask_ip(str(masked_data[field]))
    
    return masked_data


# ========================================
# PASSWORD ROTATION
# ========================================

class PasswordRotationManager:
    """Manages password rotation policies"""
    
    # Password rotation settings
    PASSWORD_ROTATION_DAYS = 90  # Force password change after 90 days
    PASSWORD_WARNING_DAYS = 14   # Warn user 14 days before expiry
    
    @staticmethod
    def is_password_expired(password_changed_at: Optional[datetime]) -> bool:
        """Check if password has expired"""
        if not password_changed_at:
            return False
        
        expiry_date = password_changed_at + timedelta(days=PasswordRotationManager.PASSWORD_ROTATION_DAYS)
        return datetime.utcnow() > expiry_date
    
    @staticmethod
    def days_until_expiry(password_changed_at: Optional[datetime]) -> int:
        """Calculate days until password expires"""
        if not password_changed_at:
            return PasswordRotationManager.PASSWORD_ROTATION_DAYS
        
        expiry_date = password_changed_at + timedelta(days=PasswordRotationManager.PASSWORD_ROTATION_DAYS)
        days_left = (expiry_date - datetime.utcnow()).days
        return max(0, days_left)
    
    @staticmethod
    def needs_warning(password_changed_at: Optional[datetime]) -> bool:
        """Check if user should be warned about password expiry"""
        if not password_changed_at:
            return False
        
        days_left = PasswordRotationManager.days_until_expiry(password_changed_at)
        return 0 < days_left <= PasswordRotationManager.PASSWORD_WARNING_DAYS
    
    @staticmethod
    def get_password_status(password_changed_at: Optional[datetime]) -> Dict[str, Any]:
        """Get comprehensive password status"""
        if not password_changed_at:
            password_changed_at = datetime.utcnow()
        
        is_expired = PasswordRotationManager.is_password_expired(password_changed_at)
        days_left = PasswordRotationManager.days_until_expiry(password_changed_at)
        needs_warning = PasswordRotationManager.needs_warning(password_changed_at)
        
        return {
            "is_expired": is_expired,
            "days_until_expiry": days_left,
            "needs_warning": needs_warning,
            "password_age_days": (datetime.utcnow() - password_changed_at).days,
            "last_changed": password_changed_at.isoformat()
        }


# ========================================
# 2FA PLACEHOLDER (MOCK)
# ========================================

class TwoFactorAuth:
    """Mock 2FA system - placeholder for future implementation"""
    
    @staticmethod
    def generate_otp(email: str) -> str:
        """Generate OTP code (MOCKED)"""
        # In production, this would generate a real OTP
        logger.info(f"[MOCK 2FA] Generated OTP for {email}: 123456")
        return "123456"
    
    @staticmethod
    def send_otp(email: str, otp: str) -> bool:
        """Send OTP to email (MOCKED)"""
        # In production, this would send actual email
        logger.info(f"[MOCK 2FA] Sending OTP to {email}: {otp}")
        return True
    
    @staticmethod
    def verify_otp(email: str, otp: str) -> bool:
        """Verify OTP (MOCKED - always returns True for now)"""
        # In production, this would verify against stored OTP
        logger.info(f"[MOCK 2FA] Verifying OTP for {email}: {otp}")
        return True  # Mock always succeeds
    
    @staticmethod
    def is_enabled(admin_data: Dict[str, Any]) -> bool:
        """Check if 2FA is enabled for admin"""
        return admin_data.get("two_factor_enabled", False)


# ========================================
# GDPR COMPLIANCE
# ========================================

class GDPRCompliance:
    """GDPR compliance utilities"""
    
    # Data retention periods (in days)
    RETENTION_PERIODS = {
        "session_bookings": 730,      # 2 years
        "events": 1095,                # 3 years
        "event_registrations": 730,    # 2 years
        "blogs": None,                 # Keep forever
        "careers": 1095,               # 3 years
        "career_applications": 730,    # 2 years
        "volunteers": 730,             # 2 years
        "psychologists": 1825,         # 5 years
        "contact_forms": 365,          # 1 year
        "admin_logs": 2555,            # 7 years (audit requirement)
        "admins": None,                # Keep forever
    }
    
    @staticmethod
    def should_purge(entity: str, deleted_at: Optional[datetime]) -> bool:
        """
        Check if a soft-deleted record should be permanently purged
        
        Args:
            entity: Entity type (e.g., "session_bookings")
            deleted_at: When the record was soft-deleted
        
        Returns:
            True if record should be purged, False otherwise
        """
        if not deleted_at:
            return False
        
        retention_days = GDPRCompliance.RETENTION_PERIODS.get(entity)
        
        # If no retention period, keep forever
        if retention_days is None:
            return False
        
        # Check if retention period has passed
        purge_date = deleted_at + timedelta(days=retention_days)
        return datetime.utcnow() > purge_date
    
    @staticmethod
    def get_retention_info(entity: str) -> Dict[str, Any]:
        """Get retention policy information for an entity"""
        retention_days = GDPRCompliance.RETENTION_PERIODS.get(entity)
        
        return {
            "entity": entity,
            "retention_days": retention_days,
            "retention_policy": "permanent" if retention_days is None else f"{retention_days} days",
            "description": GDPRCompliance._get_retention_description(retention_days)
        }
    
    @staticmethod
    def _get_retention_description(days: Optional[int]) -> str:
        """Get human-readable retention description"""
        if days is None:
            return "Data retained permanently"
        elif days < 365:
            return f"Data retained for {days} days"
        else:
            years = days / 365
            return f"Data retained for {years:.1f} years"
    
    @staticmethod
    def export_user_data(db, entity: str, user_identifier: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Export all data for a specific user (GDPR data portability)
        
        Args:
            db: Database connection
            entity: Entity type
            user_identifier: Dictionary with user identifier (e.g., {"email": "user@example.com"})
        
        Returns:
            List of all records for the user
        """
        # This is a placeholder - actual implementation would query database
        logger.info(f"[GDPR] Exporting data for entity '{entity}' with identifier {user_identifier}")
        return []


# ========================================
# ENTITY FILTERING FOR SOFT DELETE
# ========================================

def add_soft_delete_filter(query: Dict[str, Any], include_deleted: bool = False) -> Dict[str, Any]:
    """
    Add soft delete filter to a query
    
    Args:
        query: Existing query filter
        include_deleted: If True, don't filter deleted records
    
    Returns:
        Updated query with soft delete filter
    """
    if not include_deleted:
        query["is_deleted"] = False
    
    return query


def prepare_entity_for_soft_delete(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add soft delete fields when creating a new entity
    
    Args:
        entity_data: Entity data dictionary
    
    Returns:
        Entity data with soft delete fields added
    """
    soft_delete_fields = SoftDeleteMixin.get_soft_delete_fields()
    return {**entity_data, **soft_delete_fields}
