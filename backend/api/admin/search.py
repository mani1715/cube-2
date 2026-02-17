"""Global search functionality for admin panel"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

from .auth import get_current_admin
from .schemas import Admin
from .permissions import ROLE_PERMISSIONS

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

search_router = APIRouter(prefix="/api/admin/search", tags=["Admin Search"])


@search_router.get("/global")
async def global_search(
    q: str,
    limit: int = 20,
    current_admin: Admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Global search across multiple entities
    
    Args:
        q: Search query string
        limit: Maximum results per entity (default 20)
        current_admin: Current authenticated admin
    
    Returns:
        Dict with search results grouped by entity type
    """
    if not q or len(q.strip()) < 2:
        return {
            "query": q,
            "results": {},
            "total": 0
        }
    
    search_term = q.strip()
    results = {}
    total_count = 0
    
    # Get admin permissions
    permissions = ROLE_PERMISSIONS.get(current_admin.role, [])
    can_read = "read" in permissions
    
    if not can_read:
        raise HTTPException(status_code=403, detail="Read permission required for search")
    
    try:
        # Search sessions
        sessions_results = await db.session_bookings.find({
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"phone": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if sessions_results:
            results["sessions"] = sessions_results
            total_count += len(sessions_results)
        
        # Search events
        events_results = await db.events.find({
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"event_type": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if events_results:
            results["events"] = events_results
            total_count += len(events_results)
        
        # Search blogs
        blogs_results = await db.blogs.find({
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"excerpt": {"$regex": search_term, "$options": "i"}},
                {"author": {"$regex": search_term, "$options": "i"}},
                {"category": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if blogs_results:
            results["blogs"] = blogs_results
            total_count += len(blogs_results)
        
        # Search psychologists
        psychologists_results = await db.psychologists.find({
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"bio": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if psychologists_results:
            results["psychologists"] = psychologists_results
            total_count += len(psychologists_results)
        
        # Search volunteers
        volunteers_results = await db.volunteers.find({
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"interest_area": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if volunteers_results:
            results["volunteers"] = volunteers_results
            total_count += len(volunteers_results)
        
        # Search jobs/careers
        jobs_results = await db.careers.find({
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"department": {"$regex": search_term, "$options": "i"}},
                {"location": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if jobs_results:
            results["jobs"] = jobs_results
            total_count += len(jobs_results)
        
        # Search contacts
        contacts_results = await db.contact_forms.find({
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"subject": {"$regex": search_term, "$options": "i"}},
                {"message": {"$regex": search_term, "$options": "i"}}
            ]
        }, {"_id": 0}).limit(limit).to_list(length=limit)
        
        if contacts_results:
            results["contacts"] = contacts_results
            total_count += len(contacts_results)
        
        logger.info(f"Admin {current_admin.email} searched for '{search_term}' - found {total_count} results")
        
        return {
            "query": search_term,
            "results": results,
            "total": total_count
        }
    
    except Exception as e:
        logger.error(f"Global search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
