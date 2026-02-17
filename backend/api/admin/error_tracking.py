"""Admin error tracking system"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from .auth import get_current_admin
from .schemas import Admin
from .utils import get_skip_limit, calculate_pagination

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

error_router = APIRouter(prefix="/api/admin/errors", tags=["Admin Error Tracking"])


class ErrorLog(BaseModel):
    """Error log model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error_type: str  # frontend, backend
    severity: str  # error, warning, critical
    message: str
    stack_trace: Optional[str] = None
    component: Optional[str] = None  # Component where error occurred
    url: Optional[str] = None
    user_agent: Optional[str] = None
    admin_id: Optional[str] = None
    admin_email: Optional[str] = None
    context: Optional[Dict[str, Any]] = None  # Additional context
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False


class ErrorLogCreate(BaseModel):
    """Schema for creating error log"""
    error_type: str
    severity: str
    message: str
    stack_trace: Optional[str] = None
    component: Optional[str] = None
    url: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@error_router.post("/log")
async def log_error(
    error_data: ErrorLogCreate,
    request: Request,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Log an error to the error tracking system
    
    Args:
        error_data: Error data to log
        request: FastAPI request object
        current_admin: Current authenticated admin
    
    Returns:
        Dict with error log ID
    """
    try:
        # Create error log object
        error_log = ErrorLog(
            **error_data.dict(),
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            user_agent=request.headers.get("user-agent")
        )
        
        # Store in MongoDB
        await db.admin_errors.insert_one(error_log.dict())
        
        logger.error(
            f"Error logged - Type: {error_log.error_type}, "
            f"Severity: {error_log.severity}, "
            f"Admin: {current_admin.email}, "
            f"Message: {error_log.message}"
        )
        
        return {
            "success": True,
            "error_id": error_log.id,
            "message": "Error logged successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to log error: {str(e)}")
        # Don't raise exception to prevent error logging failure from breaking the app
        return {
            "success": False,
            "message": "Failed to log error"
        }


@error_router.get("/list")
async def get_errors(
    page: int = 1,
    limit: int = 50,
    severity: Optional[str] = None,
    error_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get list of errors with filtering
    
    Args:
        page: Page number
        limit: Items per page
        severity: Filter by severity (error, warning, critical)
        error_type: Filter by error type (frontend, backend)
        resolved: Filter by resolved status
        current_admin: Current authenticated admin
    
    Returns:
        Dict with errors and pagination info
    """
    try:
        # Build query
        query = {}
        if severity:
            query["severity"] = severity
        if error_type:
            query["error_type"] = error_type
        if resolved is not None:
            query["resolved"] = resolved
        
        # Get total count
        total = await db.admin_errors.count_documents(query)
        
        # Calculate pagination
        skip, limit = get_skip_limit(page, limit)
        pagination = calculate_pagination(page, limit, total)
        
        # Fetch errors
        cursor = db.admin_errors.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
        errors = await cursor.to_list(length=limit)
        
        return {
            "data": errors,
            "pagination": pagination
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch errors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch errors")


@error_router.get("/stats")
async def get_error_stats(
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get error statistics
    
    Returns:
        Dict with error stats
    """
    try:
        total_errors = await db.admin_errors.count_documents({})
        unresolved_errors = await db.admin_errors.count_documents({"resolved": False})
        critical_errors = await db.admin_errors.count_documents({"severity": "critical", "resolved": False})
        frontend_errors = await db.admin_errors.count_documents({"error_type": "frontend", "resolved": False})
        backend_errors = await db.admin_errors.count_documents({"error_type": "backend", "resolved": False})
        
        return {
            "total": total_errors,
            "unresolved": unresolved_errors,
            "critical": critical_errors,
            "frontend": frontend_errors,
            "backend": backend_errors
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch error stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch error stats")


@error_router.patch("/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Mark an error as resolved
    
    Args:
        error_id: Error ID to resolve
        current_admin: Current authenticated admin
    
    Returns:
        Dict with success message
    """
    try:
        result = await db.admin_errors.update_one(
            {"id": error_id},
            {"$set": {"resolved": True, "resolved_by": current_admin.email, "resolved_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Error not found")
        
        logger.info(f"Error {error_id} marked as resolved by {current_admin.email}")
        
        return {
            "success": True,
            "message": "Error marked as resolved"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resolve error")


@error_router.delete("/{error_id}")
async def delete_error(
    error_id: str,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Delete an error log
    
    Args:
        error_id: Error ID to delete
        current_admin: Current authenticated admin
    
    Returns:
        Dict with success message
    """
    try:
        result = await db.admin_errors.delete_one({"id": error_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Error not found")
        
        logger.info(f"Error {error_id} deleted by {current_admin.email}")
        
        return {
            "success": True,
            "message": "Error deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete error")
