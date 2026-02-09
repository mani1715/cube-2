"""Bulk operations for admin panel"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from datetime import datetime

from .auth import get_current_admin
from .schemas import Admin
from .permissions import require_delete_permission, require_admin_or_above
from .utils import log_admin_action
from .rate_limits import limiter, ADMIN_RATE_LIMIT, EXPORT_RATE_LIMIT
from .background_tasks import AuditExportService, BulkOperationsService

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

bulk_router = APIRouter(prefix="/api/admin/bulk", tags=["Admin Bulk Operations"])


# Collection mapping for different entities
ENTITY_COLLECTIONS = {
    "sessions": "session_bookings",
    "events": "events",
    "blogs": "blogs",
    "psychologists": "psychologists",
    "volunteers": "volunteers",
    "jobs": "careers",
    "contacts": "contact_forms"
}


@bulk_router.post("/delete")
@limiter.limit(ADMIN_RATE_LIMIT)
async def bulk_delete(
    request: Request,
    entity: str,
    ids: List[str],
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(require_delete_permission)
) -> Dict[str, Any]:
    """
    Bulk delete items from specified entity (background processing for large operations)
    
    Args:
        entity: Entity type (sessions, events, blogs, etc.)
        ids: List of IDs to delete
        current_admin: Current authenticated admin
    
    Returns:
        Dict with deletion results
    """
    if entity not in ENTITY_COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity}")
    
    collection_name = ENTITY_COLLECTIONS[entity]
    
    # If large bulk operation, process in background
    if len(ids) > 100:
        background_tasks.add_task(
            BulkOperationsService.bulk_delete,
            collection=collection_name,
            ids=ids,
            admin_email=current_admin.email
        )
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="bulk_delete_started",
            entity=entity,
            entity_id=",".join(ids[:5]),
            details=f"Started background bulk delete for {len(ids)} {entity} items"
        )
        
        logger.info(f"Admin {current_admin.email} started background bulk delete for {len(ids)} {entity} items")
        
        return {
            "success": True,
            "processing": "background",
            "count": len(ids),
            "entity": entity,
            "message": f"Bulk delete of {len(ids)} items started in background. You will receive an email when complete."
        }
    
    # For smaller operations, process immediately
    collection = db[collection_name]
    
    try:
        # Perform bulk delete
        result = await collection.delete_many({"id": {"$in": ids}})
        deleted_count = result.deleted_count
        
        # Log the bulk delete action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="bulk_delete",
            entity=entity,
            entity_id=",".join(ids[:5]),  # Log first 5 IDs
            details=f"Bulk deleted {deleted_count} {entity} items"
        )
        
        logger.info(f"Admin {current_admin.email} bulk deleted {deleted_count} {entity} items")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "requested_count": len(ids),
            "entity": entity,
            "message": f"Successfully deleted {deleted_count} items"
        }
    
    except Exception as e:
        logger.error(f"Bulk delete failed for {entity}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")


@bulk_router.get("/export/{entity}")
@limiter.limit(EXPORT_RATE_LIMIT)
async def bulk_export(
    request: Request,
    entity: str,
    format: str = "csv",
    status: str = None,
    page: int = 1,
    limit: int = 1000,
    current_admin: Admin = Depends(require_admin_or_above)
) -> Dict[str, Any]:
    """
    Export data for specified entity
    
    Args:
        entity: Entity type (sessions, events, blogs, etc.)
        format: Export format (csv or excel)
        status: Optional status filter
        page: Page number
        limit: Items per page (max 1000)
        current_admin: Current authenticated admin
    
    Returns:
        Dict with export data
    """
    if entity not in ENTITY_COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity}")
    
    if format not in ["csv", "excel"]:
        raise HTTPException(status_code=400, detail="Format must be 'csv' or 'excel'")
    
    collection_name = ENTITY_COLLECTIONS[entity]
    collection = db[collection_name]
    
    try:
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        # Fetch data with limit
        skip = (page - 1) * limit
        cursor = collection.find(query, {"_id": 0}).skip(skip).limit(limit)
        data = await cursor.to_list(length=limit)
        
        # Log export action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="export",
            entity=entity,
            entity_id="bulk",
            details=f"Exported {len(data)} {entity} items as {format}"
        )
        
        logger.info(f"Admin {current_admin.email} exported {len(data)} {entity} items")
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "entity": entity,
            "format": format
        }
    
    except Exception as e:
        logger.error(f"Export failed for {entity}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@bulk_router.post("/export/audit-logs")
@limiter.limit(EXPORT_RATE_LIMIT)
async def export_audit_logs(
    request: Request,
    background_tasks: BackgroundTasks,
    filters: Dict[str, Any] = None,
    current_admin: Admin = Depends(require_admin_or_above)
) -> Dict[str, str]:
    """
    Export audit logs to CSV (background processing)
    
    Args:
        filters: Optional filters (admin_email, action, entity, date_range)
        current_admin: Current authenticated admin
    
    Returns:
        Dict with job status
    """
    try:
        # Start background export task
        background_tasks.add_task(
            AuditExportService.export_audit_logs,
            admin_email=current_admin.email,
            filters=filters or {}
        )
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="audit_export_started",
            entity="audit_logs",
            entity_id="bulk",
            details="Started background audit log export"
        )
        
        logger.info(f"Admin {current_admin.email} started audit log export in background")
        
        return {
            "success": True,
            "message": "Audit log export started in background. You will receive an email with the file when complete.",
            "processing": "background"
        }
    
    except Exception as e:
        logger.error(f"Failed to start audit export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start export: {str(e)}")


@bulk_router.post("/status-update")
@limiter.limit(ADMIN_RATE_LIMIT)
async def bulk_status_update(
    request: Request,
    entity: str,
    ids: List[str],
    new_status: str,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(require_admin_or_above)
) -> Dict[str, Any]:
    """
    Bulk update status for multiple items (background processing for large operations)
    
    Args:
        entity: Entity type (sessions, volunteers, contacts, etc.)
        ids: List of IDs to update
        new_status: New status value
        current_admin: Current authenticated admin
    
    Returns:
        Dict with update results
    """
    if entity not in ENTITY_COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity}")
    
    collection_name = ENTITY_COLLECTIONS[entity]
    
    # If large bulk operation, process in background
    if len(ids) > 100:
        background_tasks.add_task(
            BulkOperationsService.bulk_status_update,
            collection=collection_name,
            ids=ids,
            new_status=new_status,
            admin_email=current_admin.email
        )
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="bulk_status_update_started",
            entity=entity,
            entity_id=",".join(ids[:5]),
            details=f"Started background status update for {len(ids)} {entity} items to '{new_status}'"
        )
        
        logger.info(f"Admin {current_admin.email} started background status update for {len(ids)} {entity} items")
        
        return {
            "success": True,
            "processing": "background",
            "count": len(ids),
            "entity": entity,
            "new_status": new_status,
            "message": f"Status update of {len(ids)} items started in background. You will receive an email when complete."
        }
    
    # For smaller operations, process immediately
    collection = db[collection_name]
    
    try:
        # Perform bulk status update
        result = await collection.update_many(
            {"id": {"$in": ids}},
            {"$set": {"status": new_status}}
        )
        updated_count = result.modified_count
        
        # Log the bulk update action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="bulk_status_update",
            entity=entity,
            entity_id=",".join(ids[:5]),
            details=f"Bulk updated status for {updated_count} {entity} items to '{new_status}'"
        )
        
        logger.info(f"Admin {current_admin.email} bulk updated {updated_count} {entity} items")
        
        return {
            "success": True,
            "updated_count": updated_count,
            "requested_count": len(ids),
            "entity": entity,
            "new_status": new_status,
            "message": f"Successfully updated {updated_count} items"
        }
    
    except Exception as e:
        logger.error(f"Bulk status update failed for {entity}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk status update failed: {str(e)}")
