"""
Phase 14 - Scalability, Backup & Infrastructure Router
API endpoints for scalability monitoring, backup management, and infrastructure
"""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import logging

from api.admin.permissions import get_current_admin, require_super_admin
from api.phase14_scalability import (
    DatabaseConnectionPool,
    CacheStrategy,
    CacheWarmer,
    BackgroundTasks as Phase14BackgroundTasks,
    PerformanceMonitor,
    performance_monitor,
    get_database_stats
)
from api.phase14_backup import BackupManager
from cache import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/phase14", tags=["Phase 14 - Scalability & Backup"])

# Get MongoDB connection from environment
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

# Initialize connection pool (will be used by dependency injection)
db_pool = DatabaseConnectionPool(mongo_url, db_name, max_pool_size=50, min_pool_size=10)

# Initialize backup manager
backup_manager = None


def get_db():
    """Dependency to get database instance"""
    return db_pool.get_db()


def get_backup_manager():
    """Dependency to get backup manager instance"""
    global backup_manager
    if backup_manager is None:
        db = db_pool.get_db()
        backup_manager = BackupManager(db)
    return backup_manager


# ============= CONNECTION POOL HEALTH =============

@router.get("/scalability/connection-pool/health")
async def check_connection_pool_health(
    admin = Depends(require_super_admin)
):
    """
    Check MongoDB connection pool health
    Returns connection statistics and health status
    """
    try:
        health = await db_pool.health_check()
        return health
    except Exception as e:
        logger.error(f"Connection pool health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check connection pool health")


# ============= CACHE MANAGEMENT =============

@router.get("/scalability/cache/stats")
async def get_cache_statistics(
    admin = Depends(require_super_admin)
):
    """
    Get detailed cache statistics
    Returns hit rate, size, and usage metrics
    """
    try:
        stats = cache.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")


@router.post("/scalability/cache/warm")
async def warm_cache(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Trigger cache warming for critical endpoints
    Pre-populates cache with frequently accessed data
    """
    try:
        # Run cache warming in background
        background_tasks.add_task(CacheWarmer.warm_critical_caches, db)
        
        return {
            "message": "Cache warming initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Cache warming error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate cache warming")


@router.post("/scalability/cache/clear/{entity_type}")
async def clear_entity_cache(
    entity_type: str,
    admin = Depends(require_super_admin)
):
    """
    Clear cache for specific entity type
    Useful after bulk updates or data imports
    """
    try:
        CacheStrategy.invalidate_related_caches(entity_type)
        
        return {
            "message": f"Cache cleared for entity type: {entity_type}",
            "entity_type": entity_type
        }
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.delete("/scalability/cache/cleanup")
async def cleanup_expired_cache(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin)
):
    """
    Remove expired cache entries
    Frees up memory from stale cached data
    """
    try:
        # Run cleanup in background
        background_tasks.add_task(Phase14BackgroundTasks.cleanup_expired_cache)
        
        return {
            "message": "Cache cleanup initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Cache cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup cache")


# ============= DATABASE OPTIMIZATION =============

@router.get("/scalability/database/stats")
async def get_database_statistics(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get comprehensive database statistics
    Returns size, collection stats, and index information
    """
    try:
        stats = await get_database_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Database stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get database statistics")


@router.post("/scalability/database/cleanup-sessions")
async def cleanup_old_sessions(
    background_tasks: BackgroundTasks,
    days: int = 90,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Cleanup old completed sessions
    Removes sessions older than specified days
    """
    try:
        if days < 30:
            raise HTTPException(status_code=400, detail="Days must be at least 30")
        
        # Run cleanup in background
        background_tasks.add_task(
            Phase14BackgroundTasks.cleanup_old_sessions,
            db,
            days
        )
        
        return {
            "message": f"Session cleanup initiated (older than {days} days)",
            "days": days,
            "status": "in_progress"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup sessions")


@router.post("/scalability/database/optimize-indexes")
async def optimize_database_indexes(
    background_tasks: BackgroundTasks,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Optimize database indexes
    Checks and optimizes indexes for better query performance
    """
    try:
        # Run optimization in background
        background_tasks.add_task(Phase14BackgroundTasks.optimize_indexes, db)
        
        return {
            "message": "Index optimization initiated",
            "status": "in_progress"
        }
    except Exception as e:
        logger.error(f"Index optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize indexes")


# ============= PERFORMANCE MONITORING =============

@router.get("/scalability/performance/metrics")
async def get_performance_metrics(
    admin = Depends(require_super_admin)
):
    """
    Get application performance metrics
    Returns request stats, response times, and error rates
    """
    try:
        metrics = performance_monitor.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Performance metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


# ============= SCALABILITY OVERVIEW =============

@router.get("/scalability/overview")
async def get_scalability_overview(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get comprehensive scalability overview
    Combines cache, database, and performance metrics
    """
    try:
        # Get all metrics
        cache_stats = cache.get_stats()
        db_health = await db_pool.health_check()
        performance_metrics = performance_monitor.get_metrics()
        
        return {
            "connection_pool": {
                "status": db_health.get("status"),
                "response_time_ms": db_health.get("response_time_ms"),
                "max_pool_size": 50,
                "min_pool_size": 10
            },
            "cache": {
                "hit_rate": cache_stats.get("hit_rate", 0),
                "total_entries": cache_stats.get("cache_size", 0),
                "total_requests": cache_stats.get("total_requests", 0)
            },
            "performance": {
                "total_requests": performance_metrics.get("total_requests", 0),
                "avg_response_time": round(performance_metrics.get("avg_response_time", 0), 3),
                "error_rate": round(performance_metrics.get("error_rate", 0) * 100, 2)
            },
            "optimizations_enabled": [
                "Connection Pooling (10-50 connections)",
                "In-Memory Caching with TTL",
                "GZip Compression (>500 bytes)",
                "Query Result Caching",
                "Batch Operations Support",
                "Background Task Processing"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Scalability overview error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scalability overview")


# ============= SCALABILITY CONFIGURATION =============

@router.get("/scalability/config")
async def get_scalability_configuration(
    admin = Depends(require_super_admin)
):
    """
    Get current scalability configuration
    Shows cache TTLs, pool sizes, and optimization settings
    """
    try:
        return {
            "connection_pool": {
                "max_pool_size": 50,
                "min_pool_size": 10,
                "max_idle_time_ms": 45000,
                "server_selection_timeout_ms": 5000,
                "connection_timeout_ms": 10000,
                "socket_timeout_ms": 20000
            },
            "cache_ttl_seconds": {
                "events": CacheStrategy.CACHE_CONFIGS.get("events", 3600),
                "blogs": CacheStrategy.CACHE_CONFIGS.get("blogs", 3600),
                "careers": CacheStrategy.CACHE_CONFIGS.get("careers", 3600),
                "psychologists": CacheStrategy.CACHE_CONFIGS.get("psychologists", 3600),
                "sessions": CacheStrategy.CACHE_CONFIGS.get("sessions", 600),
                "volunteers": CacheStrategy.CACHE_CONFIGS.get("volunteers", 600),
                "analytics": CacheStrategy.CACHE_CONFIGS.get("analytics", 300),
                "dashboard": CacheStrategy.CACHE_CONFIGS.get("dashboard", 300),
                "stats": CacheStrategy.CACHE_CONFIGS.get("stats", 120)
            },
            "compression": {
                "enabled": True,
                "minimum_size_bytes": 500,
                "algorithm": "gzip"
            },
            "batch_operations": {
                "insert_batch_size": 100,
                "update_batch_size": 50
            },
            "background_tasks": {
                "enabled": True,
                "cache_cleanup_enabled": True,
                "session_cleanup_days": 90
            }
        }
    except Exception as e:
        logger.error(f"Config fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


# ============= HEALTH CHECK =============

@router.get("/scalability/health")
async def scalability_health_check(
    db = Depends(get_db)
):
    """
    Comprehensive health check for scalability components
    Public endpoint for monitoring tools
    """
    try:
        health_status = {
            "status": "healthy",
            "components": {}
        }
        
        # Check database connection
        try:
            db_health = await db_pool.health_check()
            health_status["components"]["database"] = {
                "status": db_health.get("status"),
                "response_time_ms": db_health.get("response_time_ms")
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Check cache
        try:
            cache_stats = cache.get_stats()
            health_status["components"]["cache"] = {
                "status": "healthy",
                "size": cache_stats.get("cache_size", 0),
                "hit_rate": cache_stats.get("hit_rate", 0)
            }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        health_status["timestamp"] = datetime.utcnow().isoformat()
        
        return health_status
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# PHASE 14.2 - BACKUP & DISASTER RECOVERY
# ============================================================================

@router.post("/backup/create")
async def create_database_backup(
    background_tasks: BackgroundTasks,
    backup_type: str = "manual",
    collections: Optional[List[str]] = None,
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Create a complete database backup
    
    - **backup_type**: Type of backup (manual, scheduled, pre-migration)
    - **collections**: Optional list of specific collections to backup
    
    Returns backup metadata including backup ID and size
    """
    try:
        # Run backup in background for large databases
        result = await backup_mgr.create_backup(
            backup_type=backup_type,
            include_collections=collections
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Backup failed"))
        
        logger.info(f"Backup created successfully: {result.get('backup_id')}")
        
        return {
            "message": "Backup created successfully",
            "backup": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")


@router.get("/backup/list")
async def list_all_backups(
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    List all available database backups
    
    Returns list of backups with metadata, sorted by date (newest first)
    """
    try:
        backups = await backup_mgr.list_backups()
        
        return {
            "total_backups": len(backups),
            "backups": backups
        }
    
    except Exception as e:
        logger.error(f"List backups error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


@router.get("/backup/{backup_id}")
async def get_backup_details(
    backup_id: str,
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Get detailed information about a specific backup
    
    Returns backup metadata, file listing, and collection details
    """
    try:
        details = await backup_mgr.get_backup_details(backup_id)
        
        if details is None:
            raise HTTPException(status_code=404, detail=f"Backup '{backup_id}' not found")
        
        return details
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get backup details error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get backup details: {str(e)}")


@router.post("/backup/{backup_id}/restore")
async def restore_database_backup(
    backup_id: str,
    collections: Optional[List[str]] = None,
    mode: str = "replace",
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Restore database from a backup
    
    - **backup_id**: ID of backup to restore
    - **collections**: Optional list of specific collections to restore
    - **mode**: Restore mode
        - `replace`: Drop existing data and restore (default)
        - `merge`: Keep existing data, add backup data
        - `preview`: Preview what would be restored without actually restoring
    
    ⚠️ **Warning**: `replace` mode will delete existing data!
    """
    try:
        if mode not in ["replace", "merge", "preview"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid mode. Must be 'replace', 'merge', or 'preview'"
            )
        
        result = await backup_mgr.restore_backup(
            backup_id=backup_id,
            collections=collections,
            mode=mode
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Restore failed"))
        
        message = "Restore preview completed" if mode == "preview" else "Database restored successfully"
        
        logger.info(f"Restore completed: {backup_id} (mode: {mode})")
        
        return {
            "message": message,
            "restore_results": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restore error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")


@router.delete("/backup/{backup_id}")
async def delete_backup(
    backup_id: str,
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Delete a specific backup
    
    Permanently removes backup files from the system
    """
    try:
        result = await backup_mgr.delete_backup(backup_id)
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Deletion failed"))
        
        logger.info(f"Backup deleted: {backup_id}")
        
        return {
            "message": f"Backup '{backup_id}' deleted successfully",
            "result": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete backup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete backup: {str(e)}")


@router.post("/backup/cleanup")
async def cleanup_old_backups(
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Clean up old backups based on retention policy
    
    - Deletes backups older than 30 days
    - Enforces maximum of 30 backups
    
    Returns list of deleted backups
    """
    try:
        result = await backup_mgr.cleanup_old_backups()
        
        return {
            "message": "Backup cleanup completed",
            "deleted_count": result.get("deleted_count", 0),
            "deleted_backups": result.get("deleted_backups", [])
        }
    
    except Exception as e:
        logger.error(f"Backup cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup backups: {str(e)}")


@router.get("/backup/statistics")
async def get_backup_statistics(
    admin = Depends(require_super_admin),
    backup_mgr = Depends(get_backup_manager)
):
    """
    Get backup system statistics
    
    Returns total number of backups, storage usage, and configuration
    """
    try:
        stats = backup_mgr.get_backup_statistics()
        
        return stats
    
    except Exception as e:
        logger.error(f"Backup statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get backup statistics: {str(e)}")


# ============================================================================
# PHASE 14.6 - ADMIN POWER TOOLS
# ============================================================================

from api.phase14_power_tools import (
    AdvancedSearchFilter,
    BulkDataExporter,
    DataValidator,
    QuickActions
)


@router.post("/power-tools/advanced-search/{collection}")
async def advanced_search(
    collection: str,
    filters: Dict[str, Any],
    page: int = 1,
    limit: int = 50,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Advanced search with complex filters
    
    Supports:
    - Text search across multiple fields
    - Date range filtering
    - Status filters
    - Custom field filters
    - Pagination
    """
    try:
        if collection not in await db.list_collection_names():
            raise HTTPException(status_code=404, detail=f"Collection '{collection}' not found")
        
        coll = db[collection]
        
        # Build query from filters
        query = AdvancedSearchFilter.build_query(filters)
        
        # Get total count
        total = await coll.count_documents(query)
        
        # Apply pagination
        skip = (page - 1) * limit
        results = await coll.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        return {
            "collection": collection,
            "filters_applied": filters,
            "results": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/power-tools/bulk-export/{collection}")
async def bulk_export_data(
    collection: str,
    format: str = "csv",
    filters: Optional[Dict[str, Any]] = None,
    fields: Optional[List[str]] = None,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Bulk export data from collection
    
    - **collection**: Name of collection to export
    - **format**: Export format (csv or json)
    - **filters**: Optional filters to apply
    - **fields**: Optional list of fields to include (CSV only)
    """
    try:
        if collection not in await db.list_collection_names():
            raise HTTPException(status_code=404, detail=f"Collection '{collection}' not found")
        
        coll = db[collection]
        
        # Build query
        query = AdvancedSearchFilter.build_query(filters or {})
        
        # Fetch data
        data = await coll.find(query).to_list(length=None)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found to export")
        
        # Default fields if not specified
        if fields is None and format == "csv":
            # Get all unique keys from first few documents
            fields = list(set().union(*[doc.keys() for doc in data[:10]]))
            # Remove MongoDB internal fields
            fields = [f for f in fields if f not in ["_id", "password", "password_hash"]]
        
        # Export based on format
        if format == "csv":
            return await BulkDataExporter.export_to_csv(data, fields)
        elif format == "json":
            return await BulkDataExporter.export_to_json(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'json'")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/power-tools/validate/{collection}")
async def validate_collection_data(
    collection: str,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Validate data integrity in a collection
    
    Checks for:
    - Missing required fields
    - Invalid email formats
    - Invalid date types
    - Duplicate entries
    """
    try:
        if collection not in await db.list_collection_names():
            raise HTTPException(status_code=404, detail=f"Collection '{collection}' not found")
        
        validation_results = await DataValidator.validate_collection(db, collection)
        
        return validation_results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/power-tools/fix-issues/{collection}")
async def fix_data_issues(
    collection: str,
    issue_type: str,
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Automatically fix common data issues
    
    - **issue_type**: Type of issue to fix
        - `missing_timestamps`: Add created_at to documents missing it
        - `normalize_status`: Standardize status values to lowercase
        - `remove_deleted`: Permanently delete soft-deleted records older than 90 days
    """
    try:
        if collection not in await db.list_collection_names():
            raise HTTPException(status_code=404, detail=f"Collection '{collection}' not found")
        
        if issue_type not in ["missing_timestamps", "normalize_status", "remove_deleted"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid issue_type. Must be 'missing_timestamps', 'normalize_status', or 'remove_deleted'"
            )
        
        result = await DataValidator.fix_common_issues(db, collection, issue_type)
        
        return {
            "message": f"Fixed {result['fixed_count']} issues",
            "details": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fix issues error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fix issues: {str(e)}")


@router.get("/power-tools/dashboard")
async def get_admin_dashboard(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get comprehensive admin dashboard
    
    Returns:
    - Quick statistics for all collections
    - Pending actions requiring attention
    - Recent activity summary
    """
    try:
        stats = await QuickActions.get_dashboard_stats(db)
        pending = await QuickActions.get_pending_actions(db)
        
        return {
            "statistics": stats,
            "pending_actions": pending,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")


@router.get("/power-tools/pending-actions")
async def get_pending_actions_list(
    admin = Depends(require_super_admin),
    db = Depends(get_db)
):
    """
    Get list of items requiring admin attention
    
    Returns counts of:
    - Pending session bookings
    - Pending volunteer applications
    - Unread contact forms
    - Pending approval requests
    """
    try:
        pending = await QuickActions.get_pending_actions(db)
        
        return pending
    
    except Exception as e:
        logger.error(f"Pending actions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending actions: {str(e)}")

