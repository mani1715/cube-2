"""
PHASE 12.4 - User Dashboard & Engagement Features
Includes user sessions, events, payments, saved blogs, and engagement tracking
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from api.phase12_users import get_current_user

# Logger setup
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client[DB_NAME]

# Router
phase12_dashboard_router = APIRouter(prefix="/api/phase12/dashboard", tags=["Phase 12 - User Dashboard"])

# Pydantic Models
class SaveBlogRequest(BaseModel):
    """Request to save/bookmark a blog"""
    blog_id: str


class BlogLikeRequest(BaseModel):
    """Request to like a blog"""
    blog_id: str


# ==================== DASHBOARD OVERVIEW ====================

@phase12_dashboard_router.get("/overview")
async def get_dashboard_overview(current_user: dict = Depends(get_current_user)):
    """
    Get dashboard overview with all user statistics
    """
    try:
        user_id = current_user["user_id"]
        
        # Count user's sessions
        total_sessions = db.session_bookings.count_documents({"user_id": user_id})
        upcoming_sessions = db.session_bookings.count_documents({
            "user_id": user_id,
            "status": "confirmed"
        })
        
        # Count user's events
        total_events = db.event_registrations.count_documents({"user_id": user_id})
        
        # Count user's payments
        total_payments = db.transactions.count_documents({
            "user_email": current_user.get("email"),
            "status": "success"
        })
        
        # Calculate total spent
        pipeline = [
            {
                "$match": {
                    "user_email": current_user.get("email"),
                    "status": "success"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_spent": {"$sum": "$amount"}
                }
            }
        ]
        spent_result = list(db.transactions.aggregate(pipeline))
        total_spent = spent_result[0]["total_spent"] if spent_result else 0
        
        # Count saved blogs
        saved_blogs_count = db.saved_blogs.count_documents({"user_id": user_id})
        
        # Count liked blogs
        liked_blogs_count = db.blog_likes.count_documents({"user_id": user_id})
        
        return {
            "success": True,
            "overview": {
                "total_sessions": total_sessions,
                "upcoming_sessions": upcoming_sessions,
                "total_events": total_events,
                "total_payments": total_payments,
                "total_spent": total_spent,
                "saved_blogs": saved_blogs_count,
                "liked_blogs": liked_blogs_count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard overview")


# ==================== MY SESSIONS ====================

@phase12_dashboard_router.get("/sessions")
async def get_user_sessions(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all sessions booked by the current user
    """
    try:
        query = {"user_id": current_user["user_id"]}
        if status:
            query["status"] = status
        
        sessions = list(
            db.session_bookings.find(query, {"_id": 0})
            .sort("created_at", -1)
        )
        
        return {
            "success": True,
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")


@phase12_dashboard_router.get("/sessions/{session_id}")
async def get_user_session_details(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific session
    """
    try:
        session = db.session_bookings.find_one(
            {"id": session_id, "user_id": current_user["user_id"]},
            {"_id": 0}
        )
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": session
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch session details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch session details")


# ==================== MY EVENTS ====================

@phase12_dashboard_router.get("/events")
async def get_user_events(current_user: dict = Depends(get_current_user)):
    """
    Get all events registered by the current user
    """
    try:
        # Get event registrations
        registrations = list(
            db.event_registrations.find(
                {"user_id": current_user["user_id"]},
                {"_id": 0}
            ).sort("created_at", -1)
        )
        
        # Fetch full event details for each registration
        events_with_details = []
        for reg in registrations:
            event = db.events.find_one({"id": reg["event_id"]}, {"_id": 0})
            if event:
                events_with_details.append({
                    "registration": reg,
                    "event": event
                })
        
        return {
            "success": True,
            "events": events_with_details,
            "total": len(events_with_details)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch user events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")


# ==================== MY PAYMENTS ====================

@phase12_dashboard_router.get("/payments")
async def get_user_payments(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all payment transactions by the current user
    """
    try:
        query = {"user_email": current_user.get("email")}
        if status:
            query["status"] = status
        
        payments = list(
            db.transactions.find(query, {"_id": 0})
            .sort("created_at", -1)
        )
        
        return {
            "success": True,
            "payments": payments,
            "total": len(payments)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch user payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payments")


@phase12_dashboard_router.get("/payments/{transaction_id}")
async def get_payment_details(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific payment transaction
    """
    try:
        payment = db.transactions.find_one(
            {"transaction_id": transaction_id, "user_email": current_user.get("email")},
            {"_id": 0}
        )
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "success": True,
            "payment": payment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch payment details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment details")


# ==================== SAVED BLOGS ====================

@phase12_dashboard_router.post("/blogs/save")
async def save_blog(
    save_request: SaveBlogRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Save/bookmark a blog article
    """
    try:
        # Check if blog exists
        blog = db.blogs.find_one({"id": save_request.blog_id})
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        # Check if already saved
        existing = db.saved_blogs.find_one({
            "user_id": current_user["user_id"],
            "blog_id": save_request.blog_id
        })
        
        if existing:
            return {
                "success": True,
                "message": "Blog already saved",
                "is_saved": True
            }
        
        # Save blog
        db.saved_blogs.insert_one({
            "user_id": current_user["user_id"],
            "blog_id": save_request.blog_id,
            "saved_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Blog {save_request.blog_id} saved by user {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Blog saved successfully",
            "is_saved": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save blog")


@phase12_dashboard_router.delete("/blogs/save/{blog_id}")
async def unsave_blog(
    blog_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a blog from saved/bookmarked list
    """
    try:
        result = db.saved_blogs.delete_one({
            "user_id": current_user["user_id"],
            "blog_id": blog_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Saved blog not found")
        
        logger.info(f"Blog {blog_id} unsaved by user {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Blog removed from saved list",
            "is_saved": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsave blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unsave blog")


@phase12_dashboard_router.get("/blogs/saved")
async def get_saved_blogs(current_user: dict = Depends(get_current_user)):
    """
    Get all saved/bookmarked blogs for the current user
    """
    try:
        # Get saved blog IDs
        saved = list(
            db.saved_blogs.find(
                {"user_id": current_user["user_id"]},
                {"_id": 0}
            ).sort("saved_at", -1)
        )
        
        # Fetch full blog details
        blogs = []
        for item in saved:
            blog = db.blogs.find_one({"id": item["blog_id"]}, {"_id": 0})
            if blog:
                blogs.append({
                    "saved_at": item["saved_at"],
                    "blog": blog
                })
        
        return {
            "success": True,
            "saved_blogs": blogs,
            "total": len(blogs)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch saved blogs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch saved blogs")


@phase12_dashboard_router.get("/blogs/is-saved/{blog_id}")
async def check_blog_saved(
    blog_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check if a blog is saved by the current user
    """
    try:
        saved = db.saved_blogs.find_one({
            "user_id": current_user["user_id"],
            "blog_id": blog_id
        })
        
        return {
            "success": True,
            "is_saved": bool(saved)
        }
        
    except Exception as e:
        logger.error(f"Failed to check blog saved status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check saved status")


# ==================== BLOG LIKES ====================

@phase12_dashboard_router.post("/blogs/like")
async def like_blog(
    like_request: BlogLikeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Like a blog article
    """
    try:
        # Check if blog exists
        blog = db.blogs.find_one({"id": like_request.blog_id})
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        # Check if already liked
        existing = db.blog_likes.find_one({
            "user_id": current_user["user_id"],
            "blog_id": like_request.blog_id
        })
        
        if existing:
            return {
                "success": True,
                "message": "Blog already liked",
                "is_liked": True
            }
        
        # Like blog
        db.blog_likes.insert_one({
            "user_id": current_user["user_id"],
            "blog_id": like_request.blog_id,
            "liked_at": datetime.utcnow().isoformat()
        })
        
        # Increment like count on blog
        db.blogs.update_one(
            {"id": like_request.blog_id},
            {"$inc": {"likes": 1}}
        )
        
        logger.info(f"Blog {like_request.blog_id} liked by user {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Blog liked successfully",
            "is_liked": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to like blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like blog")


@phase12_dashboard_router.delete("/blogs/like/{blog_id}")
async def unlike_blog(
    blog_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove like from a blog article
    """
    try:
        result = db.blog_likes.delete_one({
            "user_id": current_user["user_id"],
            "blog_id": blog_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Like not found")
        
        # Decrement like count on blog
        db.blogs.update_one(
            {"id": blog_id},
            {"$inc": {"likes": -1}}
        )
        
        logger.info(f"Blog {blog_id} unliked by user {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Blog unliked successfully",
            "is_liked": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unlike blog: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unlike blog")


@phase12_dashboard_router.get("/blogs/is-liked/{blog_id}")
async def check_blog_liked(
    blog_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check if a blog is liked by the current user
    """
    try:
        liked = db.blog_likes.find_one({
            "user_id": current_user["user_id"],
            "blog_id": blog_id
        })
        
        return {
            "success": True,
            "is_liked": bool(liked)
        }
        
    except Exception as e:
        logger.error(f"Failed to check blog liked status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check liked status")


# ==================== BLOG ENGAGEMENT STATISTICS ====================

@phase12_dashboard_router.get("/blogs/{blog_id}/stats")
async def get_blog_engagement_stats(blog_id: str):
    """
    Get engagement statistics for a blog (public endpoint)
    """
    try:
        # Check if blog exists
        blog = db.blogs.find_one({"id": blog_id})
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        # Count saves
        saves_count = db.saved_blogs.count_documents({"blog_id": blog_id})
        
        # Count likes
        likes_count = db.blog_likes.count_documents({"blog_id": blog_id})
        
        return {
            "success": True,
            "blog_id": blog_id,
            "engagement": {
                "likes": likes_count,
                "saves": saves_count,
                "views": blog.get("views", 0)  # Assuming views are tracked
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch blog stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch blog stats")
