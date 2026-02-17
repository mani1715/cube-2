"""Admin permission middleware"""
from fastapi import HTTPException, Depends
from typing import List
from .auth import get_current_admin
from .schemas import Admin
from .utils import check_super_admin


# Permission levels for different roles
ROLE_PERMISSIONS = {
    "super_admin": ["read", "create", "update", "delete", "admin"],
    "admin": ["read", "create", "update"],
    "viewer": ["read"]
}


def check_permission(admin: Admin, required_permissions: List[str]) -> bool:
    """
    Check if admin has required permissions
    
    Args:
        admin: Admin object
        required_permissions: List of required permissions
        
    Returns:
        bool: True if admin has all required permissions
    """
    admin_permissions = ROLE_PERMISSIONS.get(admin.role, [])
    return all(perm in admin_permissions for perm in required_permissions)


async def require_super_admin(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """
    Dependency to require super_admin role
    
    Raises:
        HTTPException: 403 if user is not super_admin
    """
    if not check_super_admin(current_admin):
        raise HTTPException(
            status_code=403,
            detail="Super admin privileges required"
        )
    return current_admin


async def require_admin_or_above(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """
    Dependency to require admin or super_admin role
    
    Raises:
        HTTPException: 403 if user is viewer
    """
    if current_admin.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_admin


async def require_create_permission(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """
    Dependency to require create permission
    
    Raises:
        HTTPException: 403 if user doesn't have create permission
    """
    if not check_permission(current_admin, ["create"]):
        raise HTTPException(
            status_code=403,
            detail="Create permission required"
        )
    return current_admin


async def require_update_permission(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """
    Dependency to require update permission
    
    Raises:
        HTTPException: 403 if user doesn't have update permission
    """
    if not check_permission(current_admin, ["update"]):
        raise HTTPException(
            status_code=403,
            detail="Update permission required"
        )
    return current_admin


async def require_delete_permission(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """
    Dependency to require delete permission
    
    Raises:
        HTTPException: 403 if user doesn't have delete permission
    """
    if not check_permission(current_admin, ["delete"]):
        raise HTTPException(
            status_code=403,
            detail="Delete permission required"
        )
    return current_admin

