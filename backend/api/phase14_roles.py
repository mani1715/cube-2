"""
Phase 14.3 - Role Expansion
Extended admin roles with granular permissions
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import logging
import os

from api.admin.permissions import get_current_admin, require_super_admin
from api.admin.utils import log_admin_action

logger = logging.getLogger(__name__)

# Get MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


# ============= EXTENDED ROLE DEFINITIONS =============

# Original roles: super_admin, admin, viewer
# New roles: content_manager, moderator, analyst

ROLE_PERMISSIONS = {
    "super_admin": {
        "description": "Full system access with all permissions",
        "permissions": ["*"],  # All permissions
        "level": 100
    },
    "admin": {
        "description": "Administrative access with most permissions",
        "permissions": [
            "view_all", "manage_sessions", "manage_events", "manage_blogs",
            "manage_volunteers", "manage_contacts", "view_analytics",
            "manage_admins", "view_audit_logs"
        ],
        "level": 80
    },
    "content_manager": {
        "description": "Can create, edit, and publish content (blogs, events)",
        "permissions": [
            "view_all", "create_blog", "edit_blog", "delete_blog", "publish_blog",
            "create_event", "edit_event", "delete_event", "publish_event",
            "manage_psychologists", "view_analytics"
        ],
        "level": 60
    },
    "moderator": {
        "description": "Can review and approve user submissions",
        "permissions": [
            "view_all", "review_volunteers", "approve_volunteers",
            "review_contacts", "respond_contacts", "manage_sessions",
            "view_audit_logs"
        ],
        "level": 50
    },
    "analyst": {
        "description": "Read-only access to analytics and reports",
        "permissions": [
            "view_all", "view_analytics", "view_reports", "export_data",
            "view_audit_logs"
        ],
        "level": 40
    },
    "viewer": {
        "description": "Read-only access to basic information",
        "permissions": ["view_all"],
        "level": 20
    }
}


# Detailed permission descriptions
PERMISSION_DESCRIPTIONS = {
    "*": "All permissions (super admin only)",
    "view_all": "View all data across the platform",
    "manage_sessions": "Create, edit, delete therapy sessions",
    "manage_events": "Manage all events",
    "manage_blogs": "Full blog management",
    "create_blog": "Create new blog posts",
    "edit_blog": "Edit existing blog posts",
    "delete_blog": "Delete blog posts",
    "publish_blog": "Publish/unpublish blog posts",
    "create_event": "Create new events",
    "edit_event": "Edit existing events",
    "delete_event": "Delete events",
    "publish_event": "Publish/unpublish events",
    "manage_psychologists": "Manage psychologist profiles",
    "manage_volunteers": "Manage volunteer applications",
    "review_volunteers": "Review volunteer applications",
    "approve_volunteers": "Approve/reject volunteers",
    "manage_contacts": "Manage contact form submissions",
    "review_contacts": "Review contact forms",
    "respond_contacts": "Respond to contact forms",
    "view_analytics": "View analytics and metrics",
    "view_reports": "View generated reports",
    "export_data": "Export data to CSV/JSON",
    "manage_admins": "Create, edit, delete admin users",
    "view_audit_logs": "View audit logs and activity history"
}


# ============= PYDANTIC MODELS =============

class RoleAssignmentRequest(BaseModel):
    role: str
    reason: Optional[str] = None


# ============= UTILITY FUNCTIONS =============

def check_permission(admin_role: str, required_permission: str) -> bool:
    """
    Check if admin role has required permission
    """
    if admin_role not in ROLE_PERMISSIONS:
        return False
    
    role_perms = ROLE_PERMISSIONS[admin_role]["permissions"]
    
    # Super admin has all permissions
    if "*" in role_perms:
        return True
    
    return required_permission in role_perms


def get_role_level(role: str) -> int:
    """Get numeric level of role for comparison"""
    return ROLE_PERMISSIONS.get(role, {}).get("level", 0)


def can_assign_role(assigner_role: str, target_role: str) -> bool:
    """
    Check if assigner can assign target role
    Rule: Can only assign roles with lower or equal level
    """
    assigner_level = get_role_level(assigner_role)
    target_level = get_role_level(target_role)
    
    return assigner_level >= target_level


async def get_admin_effective_permissions(admin_id: str) -> List[str]:
    """
    Get effective permissions for an admin based on their role
    """
    try:
        admin = await db.admins.find_one({"id": admin_id})
        if not admin:
            return []
        
        role = admin.get("role", "viewer")
        
        if role not in ROLE_PERMISSIONS:
            return []
        
        permissions = ROLE_PERMISSIONS[role]["permissions"]
        
        # If has wildcard, return all possible permissions
        if "*" in permissions:
            return list(PERMISSION_DESCRIPTIONS.keys())
        
        return permissions
    except Exception as e:
        logger.error(f"Error getting admin permissions: {str(e)}")
        return []


# ============= API ROUTER =============

router = APIRouter(prefix="/api/phase14/roles", tags=["Phase 14.3 - Role Expansion"])


@router.get("")
async def list_roles(
    admin = Depends(get_current_admin)
):
    """
    List all available roles with their permissions
    """
    try:
        roles_list = []
        
        for role_name, role_data in ROLE_PERMISSIONS.items():
            roles_list.append({
                "role": role_name,
                "description": role_data["description"],
                "level": role_data["level"],
                "permissions": role_data["permissions"],
                "can_assign": can_assign_role(admin["role"], role_name)
            })
        
        # Sort by level descending
        roles_list.sort(key=lambda x: x["level"], reverse=True)
        
        return {
            "total_roles": len(roles_list),
            "roles": roles_list,
            "current_admin_role": admin["role"]
        }
    except Exception as e:
        logger.error(f"Error listing roles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{role}/permissions")
async def get_role_permissions(
    role: str,
    admin = Depends(get_current_admin)
):
    """
    Get detailed permissions for a specific role
    """
    try:
        if role not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=404, detail=f"Role '{role}' not found")
        
        role_data = ROLE_PERMISSIONS[role]
        permissions = role_data["permissions"]
        
        # Build detailed permission list
        permission_details = []
        if "*" in permissions:
            # Super admin - all permissions
            for perm, desc in PERMISSION_DESCRIPTIONS.items():
                permission_details.append({
                    "permission": perm,
                    "description": desc
                })
        else:
            for perm in permissions:
                permission_details.append({
                    "permission": perm,
                    "description": PERMISSION_DESCRIPTIONS.get(perm, "No description available")
                })
        
        return {
            "role": role,
            "description": role_data["description"],
            "level": role_data["level"],
            "permissions": permission_details,
            "total_permissions": len(permission_details)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/{admin_id}/assign-role")
async def assign_role_to_admin(
    admin_id: str,
    request: RoleAssignmentRequest,
    current_admin = Depends(require_super_admin)
):
    """
    Assign a role to an admin user
    Only super_admins or admins with higher level can assign roles
    """
    try:
        # Validate role
        if request.role not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid role: {request.role}")
        
        # Check if target admin exists
        target_admin = await db.admins.find_one({"id": admin_id})
        if not target_admin:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Check if current admin can assign this role
        if not can_assign_role(current_admin["role"], request.role):
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to assign role '{request.role}'"
            )
        
        # Update admin role
        old_role = target_admin.get("role", "viewer")
        
        await db.admins.update_one(
            {"id": admin_id},
            {
                "$set": {
                    "role": request.role,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log admin action
        await log_admin_action(
            admin_id=current_admin["id"],
            admin_email=current_admin["email"],
            action="assign_role",
            entity="admin",
            entity_id=admin_id,
            details={
                "target_admin_email": target_admin.get("email"),
                "old_role": old_role,
                "new_role": request.role,
                "reason": request.reason
            },
            db=db
        )
        
        logger.info(f"Role assigned: {request.role} to admin {admin_id} by {current_admin['email']}")
        
        return {
            "success": True,
            "admin_id": admin_id,
            "old_role": old_role,
            "new_role": request.role,
            "message": f"Role successfully changed from '{old_role}' to '{request.role}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/{admin_id}/permissions")
async def get_admin_permissions(
    admin_id: str,
    admin = Depends(get_current_admin)
):
    """
    Get effective permissions for a specific admin
    """
    try:
        # Check if requesting own permissions or if has permission to view others
        if admin_id != admin["id"] and not check_permission(admin["role"], "view_audit_logs"):
            raise HTTPException(status_code=403, detail="You can only view your own permissions")
        
        permissions = await get_admin_effective_permissions(admin_id)
        
        # Get admin details
        target_admin = await db.admins.find_one({"id": admin_id})
        if not target_admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        role = target_admin.get("role", "viewer")
        role_data = ROLE_PERMISSIONS.get(role, {})
        
        # Build detailed permission list
        permission_details = []
        for perm in permissions:
            permission_details.append({
                "permission": perm,
                "description": PERMISSION_DESCRIPTIONS.get(perm, "No description"),
                "granted": True
            })
        
        return {
            "admin_id": admin_id,
            "email": target_admin.get("email"),
            "role": role,
            "role_description": role_data.get("description", ""),
            "role_level": role_data.get("level", 0),
            "permissions": permission_details,
            "total_permissions": len(permission_details),
            "is_super_admin": role == "super_admin"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix")
async def get_permission_matrix(
    admin = Depends(get_current_admin)
):
    """
    Get complete permission matrix showing all roles and their permissions
    """
    try:
        matrix = []
        
        # Get all unique permissions
        all_permissions = set()
        for role_data in ROLE_PERMISSIONS.values():
            if "*" in role_data["permissions"]:
                all_permissions.update(PERMISSION_DESCRIPTIONS.keys())
            else:
                all_permissions.update(role_data["permissions"])
        
        # Remove wildcard from display
        all_permissions.discard("*")
        all_permissions = sorted(all_permissions)
        
        # Build matrix
        for role_name, role_data in ROLE_PERMISSIONS.items():
            role_perms = role_data["permissions"]
            has_wildcard = "*" in role_perms
            
            permission_status = {}
            for perm in all_permissions:
                if has_wildcard or perm in role_perms:
                    permission_status[perm] = True
                else:
                    permission_status[perm] = False
            
            matrix.append({
                "role": role_name,
                "description": role_data["description"],
                "level": role_data["level"],
                "permission_status": permission_status
            })
        
        # Sort by level
        matrix.sort(key=lambda x: x["level"], reverse=True)
        
        return {
            "roles": matrix,
            "all_permissions": [
                {
                    "permission": perm,
                    "description": PERMISSION_DESCRIPTIONS.get(perm, "")
                }
                for perm in all_permissions
            ],
            "total_roles": len(matrix),
            "total_permissions": len(all_permissions)
        }
    except Exception as e:
        logger.error(f"Error getting permission matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_role_statistics(
    admin = Depends(require_super_admin)
):
    """
    Get statistics about role distribution among admins
    """
    try:
        # Get all admins
        admins = await db.admins.find({}).to_list(length=1000)
        
        # Count by role
        role_counts = {}
        for role_name in ROLE_PERMISSIONS.keys():
            role_counts[role_name] = 0
        
        for admin_user in admins:
            role = admin_user.get("role", "viewer")
            if role in role_counts:
                role_counts[role] += 1
        
        # Build statistics
        role_stats = []
        for role_name, count in role_counts.items():
            role_data = ROLE_PERMISSIONS[role_name]
            role_stats.append({
                "role": role_name,
                "description": role_data["description"],
                "level": role_data["level"],
                "admin_count": count,
                "percentage": round((count / len(admins) * 100) if admins else 0, 2)
            })
        
        # Sort by level
        role_stats.sort(key=lambda x: x["level"], reverse=True)
        
        return {
            "total_admins": len(admins),
            "role_distribution": role_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting role statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= PERMISSION CHECKING UTILITY =============

async def require_permission(permission: str):
    """
    Dependency to check if admin has specific permission
    Usage: admin = Depends(require_permission("create_blog"))
    """
    async def permission_checker(admin = Depends(get_current_admin)):
        if not check_permission(admin["role"], permission):
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission: {permission}"
            )
        return admin
    return permission_checker
