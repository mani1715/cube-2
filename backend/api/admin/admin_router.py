from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, List
import logging
import io
from .auth import get_current_admin
from .schemas import Admin
from .permissions import (
    require_super_admin,
    require_create_permission,
    require_update_permission,
    require_delete_permission
)
from .utils import log_admin_action, generate_csv

# Create admin router with /api/admin prefix
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])

logger = logging.getLogger(__name__)


@admin_router.get("/health")
async def admin_health_check() -> Dict[str, str]:
    """Admin API health check endpoint"""
    return {
        "status": "healthy",
        "service": "A-Cube Admin API",
        "message": "Admin endpoints are ready"
    }


@admin_router.get("/")
async def admin_root() -> Dict[str, str]:
    """Admin API root endpoint"""
    return {
        "message": "A-Cube Admin API",
        "version": "1.0.0",
        "description": "Admin management endpoints"
    }


# Protected endpoints - require authentication

@admin_router.get("/stats")
async def get_dashboard_stats(current_admin: Admin = Depends(get_current_admin)) -> Dict[str, int]:
    """Get dashboard statistics - Protected endpoint"""
    # Placeholder - will be implemented with real data later
    return {
        "total_sessions": 0,
        "total_events": 0,
        "total_blogs": 0,
        "total_psychologists": 0,
        "total_volunteers": 0,
        "total_contacts": 0,
        "total_jobs": 0
    }


@admin_router.get("/me")
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)) -> Dict[str, str]:
    """Get current admin info"""
    from .permissions import ROLE_PERMISSIONS
    
    return {
        "id": current_admin.id,
        "email": current_admin.email,
        "role": current_admin.role,
        "is_active": str(current_admin.is_active),
        "permissions": ROLE_PERMISSIONS.get(current_admin.role, [])
    }


# Placeholder endpoints for admin pages - Protected

@admin_router.get("/dashboard")
async def get_dashboard_data(current_admin: Admin = Depends(get_current_admin)) -> Dict:
    """Get dashboard analytics with real data"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from datetime import datetime, timedelta
    
    logger.info(f"Admin {current_admin.email} accessed dashboard")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Get all counts
        total_sessions = await db.session_bookings.count_documents({})
        pending_sessions = await db.session_bookings.count_documents({"status": "pending"})
        confirmed_sessions = await db.session_bookings.count_documents({"status": "confirmed"})
        
        total_events = await db.events.count_documents({})
        active_events = await db.events.count_documents({"is_active": True})
        
        total_blogs = await db.blogs.count_documents({})
        published_blogs = await db.blogs.count_documents({"is_published": True})
        
        total_psychologists = await db.psychologists.count_documents({})
        active_psychologists = await db.psychologists.count_documents({"is_active": True})
        
        total_volunteers = await db.volunteers.count_documents({})
        pending_volunteers = await db.volunteers.count_documents({"status": "pending"})
        
        total_contacts = await db.contact_forms.count_documents({})
        pending_contacts = await db.contact_forms.count_documents({"status": "pending"})
        
        total_jobs = await db.careers.count_documents({})
        active_jobs = await db.careers.count_documents({"is_active": True})
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = await db.session_bookings.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        recent_contacts = await db.contact_forms.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        
        return {
            "stats": {
                "sessions": {
                    "total": total_sessions,
                    "pending": pending_sessions,
                    "confirmed": confirmed_sessions,
                    "recent": recent_sessions
                },
                "events": {
                    "total": total_events,
                    "active": active_events
                },
                "blogs": {
                    "total": total_blogs,
                    "published": published_blogs
                },
                "psychologists": {
                    "total": total_psychologists,
                    "active": active_psychologists
                },
                "volunteers": {
                    "total": total_volunteers,
                    "pending": pending_volunteers
                },
                "contacts": {
                    "total": total_contacts,
                    "pending": pending_contacts,
                    "recent": recent_contacts
                },
                "jobs": {
                    "total": total_jobs,
                    "active": active_jobs
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")
    finally:
        client.close()


@admin_router.get("/sessions")
async def get_sessions_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    status_filter: str = None
) -> Dict:
    """Get sessions overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import SessionBooking
    
    logger.info(f"Admin {current_admin.email} accessed sessions")
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if status_filter and status_filter != "all":
            query["status"] = status_filter
        
        # Get total count
        total_count = await db.session_bookings.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch sessions with pagination
        sessions_cursor = db.session_bookings.find(query).sort("created_at", -1).skip(skip).limit(limit)
        sessions = await sessions_cursor.to_list(length=limit)
        
        # Get stats
        pending_count = await db.session_bookings.count_documents({"status": "pending"})
        confirmed_count = await db.session_bookings.count_documents({"status": "confirmed"})
        completed_count = await db.session_bookings.count_documents({"status": "completed"})
        cancelled_count = await db.session_bookings.count_documents({"status": "cancelled"})
        
        return {
            "data": sessions,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "pending": pending_count,
                "confirmed": confirmed_count,
                "completed": completed_count,
                "cancelled": cancelled_count,
                "total": total_count
            }
        }
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")
    finally:
        client.close()


@admin_router.get("/events")
async def get_events_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    is_active: bool = None
) -> Dict:
    """Get events overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from datetime import datetime
    
    logger.info(f"Admin {current_admin.email} accessed events")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get total count
        total_count = await db.events.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch events with pagination
        events_cursor = db.events.find(query).sort("date", -1).skip(skip).limit(limit)
        events = await events_cursor.to_list(length=limit)
        
        # Get stats
        total_events = await db.events.count_documents({})
        active_events = await db.events.count_documents({"is_active": True})
        inactive_events = await db.events.count_documents({"is_active": False})
        
        # Count upcoming vs past events
        now = datetime.utcnow()
        upcoming_events = await db.events.count_documents({"date": {"$gte": now}})
        past_events = await db.events.count_documents({"date": {"$lt": now}})
        
        return {
            "data": events,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_events,
                "active": active_events,
                "inactive": inactive_events,
                "upcoming": upcoming_events,
                "past": past_events
            }
        }
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")
    finally:
        client.close()


@admin_router.get("/blogs")
async def get_blogs_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    category: str = None,
    featured: bool = None
) -> Dict:
    """Get blogs overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessed blogs")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if category:
            query["category"] = category
        if featured is not None:
            query["featured"] = featured
        
        # Get total count
        total_count = await db.blogs.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch blogs with pagination
        blogs_cursor = db.blogs.find(query).sort("date", -1).skip(skip).limit(limit)
        blogs = await blogs_cursor.to_list(length=limit)
        
        # Get stats
        total_blogs = await db.blogs.count_documents({})
        published_blogs = await db.blogs.count_documents({"is_published": True})
        draft_blogs = await db.blogs.count_documents({"is_published": False})
        featured_blogs = await db.blogs.count_documents({"featured": True})
        
        return {
            "data": blogs,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_blogs,
                "published": published_blogs,
                "draft": draft_blogs,
                "featured": featured_blogs
            }
        }
    except Exception as e:
        logger.error(f"Error fetching blogs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch blogs: {str(e)}")
    finally:
        client.close()


@admin_router.get("/psychologists")
async def get_psychologists_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    is_active: bool = None
) -> Dict:
    """Get psychologists overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessed psychologists")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get total count
        total_count = await db.psychologists.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch psychologists with pagination
        psychologists_cursor = db.psychologists.find(query).sort("created_at", -1).skip(skip).limit(limit)
        psychologists = await psychologists_cursor.to_list(length=limit)
        
        # Get stats
        total_psychologists = await db.psychologists.count_documents({})
        active_psychologists = await db.psychologists.count_documents({"is_active": True})
        inactive_psychologists = await db.psychologists.count_documents({"is_active": False})
        
        return {
            "data": psychologists,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_psychologists,
                "active": active_psychologists,
                "inactive": inactive_psychologists
            }
        }
    except Exception as e:
        logger.error(f"Error fetching psychologists: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch psychologists: {str(e)}")
    finally:
        client.close()


@admin_router.get("/volunteers")
async def get_volunteers_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    status: str = None
) -> Dict:
    """Get volunteers overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessed volunteers")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if status and status != "all":
            query["status"] = status
        
        # Get total count
        total_count = await db.volunteers.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch volunteers with pagination
        volunteers_cursor = db.volunteers.find(query).sort("created_at", -1).skip(skip).limit(limit)
        volunteers = await volunteers_cursor.to_list(length=limit)
        
        # Get stats
        total_volunteers = await db.volunteers.count_documents({})
        pending_volunteers = await db.volunteers.count_documents({"status": "pending"})
        approved_volunteers = await db.volunteers.count_documents({"status": "approved"})
        rejected_volunteers = await db.volunteers.count_documents({"status": "rejected"})
        
        return {
            "data": volunteers,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_volunteers,
                "pending": pending_volunteers,
                "approved": approved_volunteers,
                "rejected": rejected_volunteers
            }
        }
    except Exception as e:
        logger.error(f"Error fetching volunteers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch volunteers: {str(e)}")
    finally:
        client.close()



# ============= GLOBAL SEARCH ENDPOINT =============
@admin_router.get("/search")
async def global_search(q: str, current_admin: Admin = Depends(get_current_admin)) -> Dict:
    """
    Global search across sessions, events, blogs, and contacts
    Case-insensitive keyword search
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    import re
    
    logger.info(f"Admin {current_admin.email} searching for: {q}")
    
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create case-insensitive regex pattern
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        
        # Search sessions (by name, email, phone)
        sessions = await db.session_bookings.find({
            "$or": [
                {"full_name": {"$regex": pattern}},
                {"email": {"$regex": pattern}},
                {"phone": {"$regex": pattern}}
            ]
        }).limit(10).to_list(10)
        
        # Search events (by title, description)
        events = await db.events.find({
            "$or": [
                {"title": {"$regex": pattern}},
                {"description": {"$regex": pattern}}
            ]
        }).limit(10).to_list(10)
        
        # Search blogs (by title, content, author)
        blogs = await db.blogs.find({
            "$or": [
                {"title": {"$regex": pattern}},
                {"content": {"$regex": pattern}},
                {"author": {"$regex": pattern}}
            ]
        }).limit(10).to_list(10)
        
        # Search contacts (by name, email, subject)
        contacts = await db.contact_forms.find({
            "$or": [
                {"full_name": {"$regex": pattern}},
                {"email": {"$regex": pattern}},
                {"subject": {"$regex": pattern}}
            ]
        }).limit(10).to_list(10)
        
        return {
            "query": q,
            "results": {
                "sessions": {
                    "count": len(sessions),
                    "data": sessions
                },
                "events": {
                    "count": len(events),
                    "data": events
                },
                "blogs": {
                    "count": len(blogs),
                    "data": blogs
                },
                "contacts": {
                    "count": len(contacts),
                    "data": contacts
                }
            },
            "total_results": len(sessions) + len(events) + len(blogs) + len(contacts)
        }
    except Exception as e:
        logger.error(f"Error in global search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    finally:
        client.close()


# ============= ADMIN ACTIVITY LOGS ENDPOINT =============
@admin_router.get("/logs")
async def get_activity_logs(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50
) -> Dict:
    """
    Get admin activity logs with pagination
    Read-only endpoint for audit trail
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessing activity logs")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Get total count
        total_count = await db.admin_logs.count_documents({})
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch logs sorted by timestamp (newest first)
        logs_cursor = db.admin_logs.find({}).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await logs_cursor.to_list(length=limit)
        
        return {
            "data": logs,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            }
        }
    except Exception as e:
        logger.error(f"Error fetching activity logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")
    finally:
        client.close()


# ============= CSV EXPORT ENDPOINTS =============
@admin_router.get("/export/sessions")
async def export_sessions_csv(current_admin: Admin = Depends(get_current_admin)):
    """Export all sessions to CSV"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} exporting sessions to CSV")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Fetch all sessions
        sessions = await db.session_bookings.find({}).to_list(1000)
        
        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found to export")
        
        # Define CSV fields
        fields = [
            'id', 'full_name', 'email', 'phone', 'age', 'gender',
            'therapy_type', 'preferred_time', 'status', 'created_at'
        ]
        
        # Generate CSV
        csv_content = generate_csv(sessions, fields)
        
        # Log the export action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="export",
            entity="sessions",
            entity_id="bulk",
            details=f"Exported {len(sessions)} sessions to CSV"
        )
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sessions_export.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        client.close()


@admin_router.get("/export/volunteers")
async def export_volunteers_csv(current_admin: Admin = Depends(get_current_admin)):
    """Export all volunteers to CSV"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} exporting volunteers to CSV")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Fetch all volunteers
        volunteers = await db.volunteers.find({}).to_list(1000)
        
        if not volunteers:
            raise HTTPException(status_code=404, detail="No volunteers found to export")
        
        # Define CSV fields
        fields = [
            'id', 'full_name', 'email', 'phone', 'interest_area',
            'availability', 'status', 'created_at'
        ]
        
        # Generate CSV
        csv_content = generate_csv(volunteers, fields)
        
        # Log the export action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="export",
            entity="volunteers",
            entity_id="bulk",
            details=f"Exported {len(volunteers)} volunteers to CSV"
        )
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=volunteers_export.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting volunteers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        client.close()


@admin_router.get("/export/contacts")
async def export_contacts_csv(current_admin: Admin = Depends(get_current_admin)):
    """Export all contacts to CSV"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} exporting contacts to CSV")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Fetch all contacts
        contacts = await db.contact_forms.find({}).to_list(1000)
        
        if not contacts:
            raise HTTPException(status_code=404, detail="No contacts found to export")
        
        # Define CSV fields
        fields = [
            'id', 'full_name', 'email', 'subject', 'message', 'status', 'created_at'
        ]
        
        # Generate CSV
        csv_content = generate_csv(contacts, fields)
        
        # Log the export action
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="export",
            entity="contacts",
            entity_id="bulk",
            details=f"Exported {len(contacts)} contacts to CSV"
        )
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=contacts_export.csv"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        client.close()


@admin_router.get("/jobs")
async def get_jobs_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    is_active: bool = None
) -> Dict:
    """Get jobs overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessed jobs")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get total count
        total_count = await db.careers.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch jobs with pagination
        jobs_cursor = db.careers.find(query).sort("posted_date", -1).skip(skip).limit(limit)
        jobs = await jobs_cursor.to_list(length=limit)
        
        # Get stats
        total_jobs = await db.careers.count_documents({})
        active_jobs = await db.careers.count_documents({"is_active": True})
        inactive_jobs = await db.careers.count_documents({"is_active": False})
        
        # Count applications (if career_applications collection exists)
        total_applications = await db.career_applications.count_documents({})
        
        return {
            "data": jobs,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_jobs,
                "active": active_jobs,
                "inactive": inactive_jobs,
                "applications": total_applications
            }
        }
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")
    finally:
        client.close()


@admin_router.patch("/sessions/{session_id}/status")
async def update_session_status(
    session_id: str,
    status: str,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update session booking status (admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating session {session_id} to status {status}")
    
    # Validate status
    valid_statuses = ["pending", "confirmed", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Update the session status
        result = await db.session_bookings.update_one(
            {"id": session_id},
            {"$set": {"status": status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Log the status change
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="status_change",
            entity="sessions",
            entity_id=session_id,
            details=f"Changed status to {status}"
        )
        
        logger.info(f"Session {session_id} status updated to {status}")
        return {
            "message": "Status updated successfully",
            "session_id": session_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
    finally:
        client.close()


@admin_router.get("/contacts")
async def get_contacts_overview(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 10,
    status: str = None
) -> Dict:
    """Get contacts overview with pagination and filtering"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} accessed contacts")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query
        query = {}
        if status and status != "all":
            query["status"] = status
        
        # Get total count
        total_count = await db.contact_forms.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Fetch contacts with pagination
        contacts_cursor = db.contact_forms.find(query).sort("created_at", -1).skip(skip).limit(limit)
        contacts = await contacts_cursor.to_list(length=limit)
        
        # Get stats
        total_contacts = await db.contact_forms.count_documents({})
        pending_contacts = await db.contact_forms.count_documents({"status": "pending"})
        read_contacts = await db.contact_forms.count_documents({"status": "read"})
        responded_contacts = await db.contact_forms.count_documents({"status": "responded"})
        
        return {
            "data": contacts,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": (total_count + limit - 1) // limit
            },
            "stats": {
                "total": total_contacts,
                "pending": pending_contacts,
                "read": read_contacts,
                "responded": responded_contacts
            }
        }
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch contacts: {str(e)}")
    finally:
        client.close()


@admin_router.get("/settings")
async def get_settings(current_admin: Admin = Depends(require_super_admin)) -> Dict:
    """Get admin settings - Super admin only"""
    logger.info(f"Super admin {current_admin.email} accessed settings")
    return {
        "message": "Settings data",
        "admin": {
            "email": current_admin.email,
            "id": current_admin.id,
            "role": current_admin.role
        }
    }



# ============= STATUS UPDATE ENDPOINTS =============
@admin_router.patch("/volunteers/{volunteer_id}/status")
async def update_volunteer_status(
    volunteer_id: str,
    status: str,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update volunteer application status (admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating volunteer {volunteer_id} to status {status}")
    
    # Validate status
    valid_statuses = ["pending", "approved", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.volunteers.update_one(
            {"id": volunteer_id},
            {"$set": {"status": status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Volunteer not found")
        
        # Log the status change
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="status_change",
            entity="volunteers",
            entity_id=volunteer_id,
            details=f"Changed status to {status}"
        )
        
        return {
            "message": "Status updated successfully",
            "volunteer_id": volunteer_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating volunteer status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
    finally:
        client.close()


@admin_router.patch("/contacts/{contact_id}/status")
async def update_contact_status(
    contact_id: str,
    status: str,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update contact form status (admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating contact {contact_id} to status {status}")
    
    # Validate status
    valid_statuses = ["pending", "read", "responded"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.contact_forms.update_one(
            {"id": contact_id},
            {"$set": {"status": status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Log the status change
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="status_change",
            entity="contacts",
            entity_id=contact_id,
            details=f"Changed status to {status}"
        )
        
        return {
            "message": "Status updated successfully",
            "contact_id": contact_id,
            "new_status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
    finally:
        client.close()


# ============= DELETE ENDPOINTS (SUPER ADMIN ONLY) =============
@admin_router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a session booking (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting session {session_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.session_bookings.delete_one({"id": session_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Log the deletion
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="sessions",
            entity_id=session_id,
            details="Session booking deleted"
        )
        
        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/events/{event_id}")
async def delete_event(
    event_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete an event (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting event {event_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.events.delete_one({"id": event_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="events",
            entity_id=event_id,
            details="Event deleted"
        )
        
        return {"message": "Event deleted successfully", "event_id": event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/blogs/{blog_id}")
async def delete_blog(
    blog_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a blog post (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting blog {blog_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.blogs.delete_one({"id": blog_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="blogs",
            entity_id=blog_id,
            details="Blog post deleted"
        )
        
        return {"message": "Blog deleted successfully", "blog_id": blog_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete blog: {str(e)}")
    finally:
        client.close()



# ============= FILE UPLOAD ENDPOINT =============
@admin_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload a file (images for profiles, events, blogs)"""
    import os
    import shutil
    from pathlib import Path
    
    logger.info(f"Admin {current_admin.email} uploading file: {file.filename}")
    
    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("/app/backend/static/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return URL path
        file_url = f"/static/uploads/{unique_filename}"
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="upload",
            entity="files",
            entity_id=unique_filename,
            details=f"Uploaded file: {file.filename}"
        )
        
        return {
            "filename": unique_filename,
            "url": file_url,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


# ============= SESSIONS CREATE & UPDATE ENDPOINTS =============
@admin_router.post("/sessions")
async def create_session(
    session_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Create a new session booking"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import SessionBooking
    
    logger.info(f"Admin {current_admin.email} creating new session")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create session object with auto-generated ID and timestamp
        session = SessionBooking(**session_data)
        
        # Insert into database
        await db.session_bookings.insert_one(session.dict())
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="create",
            entity="sessions",
            entity_id=session.id,
            details=f"Created session for {session.full_name}"
        )
        
        return {"message": "Session created successfully", "session": session.dict()}
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
    finally:
        client.close()


@admin_router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    session_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a session booking"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating session {session_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and created_at from update data if present
        update_data = {k: v for k, v in session_data.items() if k not in ['id', 'created_at']}
        
        result = await db.session_bookings.update_one(
            {"id": session_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="sessions",
            entity_id=session_id,
            details="Session updated"
        )
        
        return {"message": "Session updated successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")
    finally:
        client.close()


# ============= EVENTS CREATE & UPDATE ENDPOINTS =============
@admin_router.post("/events")
async def create_event(
    event_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Create a new event"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import Event
    
    logger.info(f"Admin {current_admin.email} creating new event")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create event object
        event = Event(**event_data)
        
        # Insert into database
        await db.events.insert_one(event.dict())
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="create",
            entity="events",
            entity_id=event.id,
            details=f"Created event: {event.title}"
        )
        
        return {"message": "Event created successfully", "event": event.dict()}
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")
    finally:
        client.close()


@admin_router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    event_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update an event"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating event {event_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and created_at from update data
        update_data = {k: v for k, v in event_data.items() if k not in ['id', 'created_at']}
        
        result = await db.events.update_one(
            {"id": event_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="events",
            entity_id=event_id,
            details="Event updated"
        )
        
        return {"message": "Event updated successfully", "event_id": event_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")
    finally:
        client.close()


# ============= BLOGS CREATE & UPDATE ENDPOINTS =============
@admin_router.post("/blogs")
async def create_blog(
    blog_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Create a new blog post"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import Blog
    
    logger.info(f"Admin {current_admin.email} creating new blog")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create blog object
        blog = Blog(**blog_data)
        
        # Insert into database
        await db.blogs.insert_one(blog.dict())
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="create",
            entity="blogs",
            entity_id=blog.id,
            details=f"Created blog: {blog.title}"
        )
        
        return {"message": "Blog created successfully", "blog": blog.dict()}
    except Exception as e:
        logger.error(f"Error creating blog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create blog: {str(e)}")
    finally:
        client.close()


@admin_router.put("/blogs/{blog_id}")
async def update_blog(
    blog_id: str,
    blog_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a blog post"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating blog {blog_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and date from update data
        update_data = {k: v for k, v in blog_data.items() if k not in ['id', 'date']}
        
        result = await db.blogs.update_one(
            {"id": blog_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="blogs",
            entity_id=blog_id,
            details="Blog updated"
        )
        
        return {"message": "Blog updated successfully", "blog_id": blog_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update blog: {str(e)}")
    finally:
        client.close()


# ============= PSYCHOLOGISTS CREATE & UPDATE ENDPOINTS =============
@admin_router.post("/psychologists")
async def create_psychologist(
    psychologist_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Create a new psychologist profile"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import Psychologist
    
    logger.info(f"Admin {current_admin.email} creating new psychologist")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create psychologist object
        psychologist = Psychologist(**psychologist_data)
        
        # Insert into database
        await db.psychologists.insert_one(psychologist.dict())
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="create",
            entity="psychologists",
            entity_id=psychologist.id,
            details=f"Created psychologist: {psychologist.full_name}"
        )
        
        return {"message": "Psychologist created successfully", "psychologist": psychologist.dict()}
    except Exception as e:
        logger.error(f"Error creating psychologist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create psychologist: {str(e)}")
    finally:
        client.close()


@admin_router.put("/psychologists/{psychologist_id}")
async def update_psychologist(
    psychologist_id: str,
    psychologist_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a psychologist profile"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating psychologist {psychologist_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and created_at from update data
        update_data = {k: v for k, v in psychologist_data.items() if k not in ['id', 'created_at']}
        
        result = await db.psychologists.update_one(
            {"id": psychologist_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Psychologist not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="psychologists",
            entity_id=psychologist_id,
            details="Psychologist profile updated"
        )
        
        return {"message": "Psychologist updated successfully", "psychologist_id": psychologist_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating psychologist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update psychologist: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/psychologists/{psychologist_id}")
async def delete_psychologist(
    psychologist_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a psychologist (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting psychologist {psychologist_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.psychologists.delete_one({"id": psychologist_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Psychologist not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="psychologists",
            entity_id=psychologist_id,
            details="Psychologist deleted"
        )
        
        return {"message": "Psychologist deleted successfully", "psychologist_id": psychologist_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting psychologist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete psychologist: {str(e)}")
    finally:
        client.close()


# ============= JOBS (CAREERS) CREATE & UPDATE ENDPOINTS =============
@admin_router.post("/jobs")
async def create_job(
    job_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Create a new job posting"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from models import Career
    
    logger.info(f"Admin {current_admin.email} creating new job")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Create job object
        job = Career(**job_data)
        
        # Insert into database
        await db.careers.insert_one(job.dict())
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="create",
            entity="jobs",
            entity_id=job.id,
            details=f"Created job: {job.title}"
        )
        
        return {"message": "Job created successfully", "job": job.dict()}
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
    finally:
        client.close()


@admin_router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    job_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a job posting"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating job {job_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and posted_at from update data
        update_data = {k: v for k, v in job_data.items() if k not in ['id', 'posted_at']}
        
        result = await db.careers.update_one(
            {"id": job_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="jobs",
            entity_id=job_id,
            details="Job updated"
        )
        
        return {"message": "Job updated successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a job posting (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting job {job_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.careers.delete_one({"id": job_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="jobs",
            entity_id=job_id,
            details="Job deleted"
        )
        
        return {"message": "Job deleted successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")
    finally:
        client.close()


# ============= VOLUNTEERS UPDATE ENDPOINT =============
@admin_router.put("/volunteers/{volunteer_id}")
async def update_volunteer(
    volunteer_id: str,
    volunteer_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a volunteer application"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating volunteer {volunteer_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and created_at from update data
        update_data = {k: v for k, v in volunteer_data.items() if k not in ['id', 'created_at']}
        
        result = await db.volunteers.update_one(
            {"id": volunteer_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Volunteer not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="volunteers",
            entity_id=volunteer_id,
            details="Volunteer application updated"
        )
        
        return {"message": "Volunteer updated successfully", "volunteer_id": volunteer_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating volunteer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update volunteer: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/volunteers/{volunteer_id}")
async def delete_volunteer(
    volunteer_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a volunteer application (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting volunteer {volunteer_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.volunteers.delete_one({"id": volunteer_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Volunteer not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="volunteers",
            entity_id=volunteer_id,
            details="Volunteer application deleted"
        )
        
        return {"message": "Volunteer deleted successfully", "volunteer_id": volunteer_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting volunteer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete volunteer: {str(e)}")
    finally:
        client.close()


# ============= CONTACTS UPDATE ENDPOINT =============
@admin_router.put("/contacts/{contact_id}")
async def update_contact(
    contact_id: str,
    contact_data: dict,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """Update a contact form submission"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Admin {current_admin.email} updating contact {contact_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Remove id and created_at from update data
        update_data = {k: v for k, v in contact_data.items() if k not in ['id', 'created_at']}
        
        result = await db.contact_forms.update_one(
            {"id": contact_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="contacts",
            entity_id=contact_id,
            details="Contact form updated"
        )
        
        return {"message": "Contact updated successfully", "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update contact: {str(e)}")
    finally:
        client.close()


@admin_router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: str,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Delete a contact form submission (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} deleting contact {contact_id}")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        result = await db.contact_forms.delete_one({"id": contact_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="delete",
            entity="contacts",
            entity_id=contact_id,
            details="Contact form deleted"
        )
        
        return {"message": "Contact deleted successfully", "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete contact: {str(e)}")
    finally:
        client.close()


# ============= SETTINGS UPDATE ENDPOINT =============
@admin_router.put("/settings")
async def update_settings(
    settings_data: dict,
    current_admin: Admin = Depends(require_super_admin)
) -> Dict:
    """Update system settings (super admin only)"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    logger.info(f"Super admin {current_admin.email} updating settings")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Store or update settings document
        result = await db.settings.update_one(
            {"_id": "system_settings"},
            {"$set": settings_data},
            upsert=True
        )
        
        await log_admin_action(
            admin_id=current_admin.id,
            admin_email=current_admin.email,
            action="update",
            entity="settings",
            entity_id="system_settings",
            details="System settings updated"
        )
        
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
    finally:
        client.close()



# ============= AUDIT LOG ENDPOINTS =============

@admin_router.get("/audit-logs")
async def get_audit_logs(
    current_admin: Admin = Depends(get_current_admin),
    page: int = 1,
    limit: int = 50,
    action: str = None,
    entity: str = None,
    admin_email: str = None
) -> Dict:
    """
    Get audit logs with pagination and filtering
    All roles can view audit logs
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from .utils import calculate_pagination, get_skip_limit
    
    logger.info(f"Admin {current_admin.email} accessing audit logs")
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Build query filter
        query = {}
        if action:
            query["action"] = action
        if entity:
            query["entity"] = entity
        if admin_email:
            query["admin_email"] = admin_email
        
        # Get total count
        total = await db.admin_logs.count_documents(query)
        
        # Calculate pagination
        skip, limit = get_skip_limit(page, limit)
        pagination = calculate_pagination(page, limit, total)
        
        # Fetch logs with pagination
        logs = await db.admin_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
        
        # Format logs for response
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": log.get("id"),
                "admin_email": log.get("admin_email"),
                "action": log.get("action"),
                "entity": log.get("entity"),
                "entity_id": log.get("entity_id", ""),
                "details": log.get("details", ""),
                "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else None
            })
        
        return {
            "data": formatted_logs,
            "pagination": pagination
        }
    except Exception as e:
        logger.error(f"Error fetching audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")
    finally:
        client.close()


@admin_router.get("/audit-logs/stats")
async def get_audit_stats(
    current_admin: Admin = Depends(get_current_admin)
) -> Dict:
    """
    Get audit log statistics
    Available to all admin roles
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from datetime import datetime, timedelta
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Get stats for last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        total_actions = await db.admin_logs.count_documents({})
        recent_actions = await db.admin_logs.count_documents({
            "timestamp": {"$gte": seven_days_ago}
        })
        
        # Count by action type
        actions_pipeline = [
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        actions_by_type = await db.admin_logs.aggregate(actions_pipeline).to_list(100)
        
        # Count by entity
        entities_pipeline = [
            {"$group": {"_id": "$entity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        actions_by_entity = await db.admin_logs.aggregate(entities_pipeline).to_list(100)
        
        # Most active admins
        admins_pipeline = [
            {"$group": {"_id": "$admin_email", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        active_admins = await db.admin_logs.aggregate(admins_pipeline).to_list(5)
        
        return {
            "total_actions": total_actions,
            "recent_actions": recent_actions,
            "actions_by_type": [{"action": item["_id"], "count": item["count"]} for item in actions_by_type],
            "actions_by_entity": [{"entity": item["_id"], "count": item["count"]} for item in actions_by_entity],
            "active_admins": [{"email": item["_id"], "count": item["count"]} for item in active_admins]
        }
    except Exception as e:
        logger.error(f"Error fetching audit stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit stats: {str(e)}")
    finally:
        client.close()

