"""
Phase 14.5 - Engagement & Retention System
User activity tracking, engagement metrics, retention analytics, and re-engagement campaigns
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import os

from api.admin.permissions import get_current_admin, require_admin_or_above

logger = logging.getLogger(__name__)

# Get MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


# ============= PYDANTIC MODELS =============

class ActivityTrackRequest(BaseModel):
    user_id: str
    activity_type: str  # 'login', 'session_booking', 'event_registration', 'blog_view', etc.
    entity_type: Optional[str] = None  # 'session', 'event', 'blog', etc.
    entity_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReEngagementCampaignRequest(BaseModel):
    days_inactive: int = 30
    campaign_type: str = "general"  # 'general', 'session_reminder', 'event_promotion'
    dry_run: bool = False


# ============= UTILITY FUNCTIONS =============

async def track_user_activity(
    user_id: str,
    activity_type: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """Track user activity in the database"""
    try:
        activity = {
            "user_id": user_id,
            "activity_type": activity_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await db.user_activities.insert_one(activity)
        logger.info(f"Activity tracked: {activity_type} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error tracking activity: {str(e)}")
        return False


async def calculate_engagement_score(user_id: str, days: int = 30) -> float:
    """
    Calculate engagement score (0-100) based on user activity
    Factors: login frequency, session bookings, event registrations, blog views
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get activity counts
        activities = await db.user_activities.find({
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }).to_list(length=1000)
        
        if not activities:
            return 0.0
        
        # Weight different activity types
        activity_weights = {
            "login": 1.0,
            "session_booking": 5.0,
            "event_registration": 4.0,
            "blog_view": 2.0,
            "volunteer_application": 3.0,
            "contact_form": 2.0,
            "profile_update": 1.5
        }
        
        # Calculate weighted score
        total_score = 0.0
        for activity in activities:
            activity_type = activity.get("activity_type", "")
            weight = activity_weights.get(activity_type, 1.0)
            total_score += weight
        
        # Normalize to 0-100 scale (assuming max ~100 activities = 100 score)
        engagement_score = min(100.0, (total_score / 100) * 100)
        
        return round(engagement_score, 2)
    except Exception as e:
        logger.error(f"Error calculating engagement score: {str(e)}")
        return 0.0


async def analyze_retention_cohorts(months: int = 6) -> Dict[str, Any]:
    """
    Analyze user retention using cohort analysis
    Returns retention rates for each cohort
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
        
        # Get all users who registered since cutoff
        users = await db.users.find({
            "created_at": {"$gte": cutoff_date}
        }).to_list(length=10000)
        
        if not users:
            return {
                "cohorts": [],
                "total_users": 0,
                "message": "No users found in the specified period"
            }
        
        # Group users by registration month
        cohorts = {}
        for user in users:
            user_id = user.get("id")
            registration_date = user.get("created_at")
            if not registration_date:
                continue
            
            # Cohort key: YYYY-MM
            cohort_key = registration_date.strftime("%Y-%m")
            
            if cohort_key not in cohorts:
                cohorts[cohort_key] = {
                    "cohort_month": cohort_key,
                    "total_users": 0,
                    "active_users": 0,
                    "retention_rate": 0.0
                }
            
            cohorts[cohort_key]["total_users"] += 1
            
            # Check if user was active in last 30 days
            last_activity = await db.user_activities.find_one({
                "user_id": user_id
            }, sort=[("created_at", -1)])
            
            if last_activity:
                last_active_date = last_activity.get("created_at")
                if last_active_date and (datetime.utcnow() - last_active_date).days <= 30:
                    cohorts[cohort_key]["active_users"] += 1
        
        # Calculate retention rates
        cohort_list = []
        for cohort_key, cohort_data in sorted(cohorts.items()):
            total = cohort_data["total_users"]
            active = cohort_data["active_users"]
            retention_rate = (active / total * 100) if total > 0 else 0.0
            
            cohort_list.append({
                "cohort_month": cohort_key,
                "total_users": total,
                "active_users": active,
                "churned_users": total - active,
                "retention_rate": round(retention_rate, 2)
            })
        
        # Calculate overall retention
        total_all_users = sum(c["total_users"] for c in cohort_list)
        total_active = sum(c["active_users"] for c in cohort_list)
        overall_retention = (total_active / total_all_users * 100) if total_all_users > 0 else 0.0
        
        return {
            "cohorts": cohort_list,
            "total_users": total_all_users,
            "total_active": total_active,
            "total_churned": total_all_users - total_active,
            "overall_retention_rate": round(overall_retention, 2),
            "analysis_period_months": months
        }
    except Exception as e:
        logger.error(f"Error analyzing retention cohorts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retention analysis failed: {str(e)}")


async def identify_at_risk_users(inactivity_days: int = 14) -> List[Dict[str, Any]]:
    """
    Identify users at risk of churning based on inactivity
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=inactivity_days)
        
        # Get all users
        all_users = await db.users.find({}).to_list(length=10000)
        
        at_risk_users = []
        
        for user in all_users:
            user_id = user.get("id")
            
            # Get last activity
            last_activity = await db.user_activities.find_one({
                "user_id": user_id
            }, sort=[("created_at", -1)])
            
            if not last_activity:
                # User has never been active - high risk
                at_risk_users.append({
                    "user_id": user_id,
                    "email": user.get("email"),
                    "name": user.get("name"),
                    "last_activity": None,
                    "days_inactive": "Never active",
                    "risk_level": "high",
                    "registered_at": user.get("created_at")
                })
            else:
                last_active_date = last_activity.get("created_at")
                if last_active_date:
                    days_inactive = (datetime.utcnow() - last_active_date).days
                    
                    if days_inactive >= inactivity_days:
                        # Determine risk level
                        if days_inactive >= 60:
                            risk_level = "critical"
                        elif days_inactive >= 30:
                            risk_level = "high"
                        else:
                            risk_level = "medium"
                        
                        at_risk_users.append({
                            "user_id": user_id,
                            "email": user.get("email"),
                            "name": user.get("name"),
                            "last_activity": last_active_date.isoformat(),
                            "last_activity_type": last_activity.get("activity_type"),
                            "days_inactive": days_inactive,
                            "risk_level": risk_level,
                            "registered_at": user.get("created_at")
                        })
        
        # Sort by days inactive (descending)
        at_risk_users.sort(key=lambda x: x.get("days_inactive", 0) if isinstance(x.get("days_inactive"), int) else 0, reverse=True)
        
        return at_risk_users
    except Exception as e:
        logger.error(f"Error identifying at-risk users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to identify at-risk users: {str(e)}")


async def get_user_lifecycle_data(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive lifecycle data for a user
    """
    try:
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all activities
        activities = await db.user_activities.find({
            "user_id": user_id
        }).sort("created_at", -1).to_list(length=1000)
        
        # Calculate metrics
        registration_date = user.get("created_at")
        days_since_registration = (datetime.utcnow() - registration_date).days if registration_date else 0
        
        last_activity = activities[0] if activities else None
        last_active_date = last_activity.get("created_at") if last_activity else None
        days_since_last_activity = (datetime.utcnow() - last_active_date).days if last_active_date else None
        
        # Activity breakdown
        activity_breakdown = {}
        for activity in activities:
            activity_type = activity.get("activity_type", "unknown")
            activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
        
        # Engagement score
        engagement_score = await calculate_engagement_score(user_id, days=30)
        
        # User status
        if not last_active_date:
            user_status = "never_active"
        elif days_since_last_activity > 60:
            user_status = "churned"
        elif days_since_last_activity > 30:
            user_status = "at_risk"
        elif days_since_last_activity > 14:
            user_status = "declining"
        else:
            user_status = "active"
        
        return {
            "user_id": user_id,
            "email": user.get("email"),
            "name": user.get("name"),
            "registration_date": registration_date.isoformat() if registration_date else None,
            "days_since_registration": days_since_registration,
            "last_activity_date": last_active_date.isoformat() if last_active_date else None,
            "days_since_last_activity": days_since_last_activity,
            "total_activities": len(activities),
            "activity_breakdown": activity_breakdown,
            "engagement_score": engagement_score,
            "user_status": user_status,
            "recent_activities": [
                {
                    "activity_type": a.get("activity_type"),
                    "entity_type": a.get("entity_type"),
                    "timestamp": a.get("created_at").isoformat()
                }
                for a in activities[:10]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user lifecycle data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get lifecycle data: {str(e)}")


# ============= API ROUTER =============

router = APIRouter(prefix="/api/phase14/engagement", tags=["Phase 14.5 - Engagement & Retention"])


@router.post("/track-activity")
async def track_activity(
    request: ActivityTrackRequest,
    admin = Depends(require_admin_or_above)
):
    """
    Track user activity
    Records user actions for engagement analysis
    """
    try:
        success = await track_user_activity(
            user_id=request.user_id,
            activity_type=request.activity_type,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            metadata=request.metadata
        )
        
        if success:
            return {
                "success": True,
                "message": "Activity tracked successfully",
                "activity_type": request.activity_type,
                "user_id": request.user_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to track activity")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in track_activity endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    limit: int = 50,
    admin = Depends(require_admin_or_above)
):
    """
    Get activity history for a specific user
    """
    try:
        activities = await db.user_activities.find({
            "user_id": user_id
        }).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "activity_type": activity.get("activity_type"),
                "entity_type": activity.get("entity_type"),
                "entity_id": activity.get("entity_id"),
                "metadata": activity.get("metadata"),
                "timestamp": activity.get("created_at").isoformat() if activity.get("created_at") else None
            })
        
        return {
            "user_id": user_id,
            "total_activities": len(activity_list),
            "activities": activity_list
        }
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_engagement_metrics(
    days: int = 30,
    admin = Depends(require_admin_or_above)
):
    """
    Get overall engagement metrics
    Returns DAU, WAU, MAU, average engagement scores
    """
    try:
        now = datetime.utcnow()
        
        # Daily Active Users (last 24 hours)
        day_ago = now - timedelta(days=1)
        dau_activities = await db.user_activities.distinct("user_id", {
            "created_at": {"$gte": day_ago}
        })
        dau = len(dau_activities)
        
        # Weekly Active Users (last 7 days)
        week_ago = now - timedelta(days=7)
        wau_activities = await db.user_activities.distinct("user_id", {
            "created_at": {"$gte": week_ago}
        })
        wau = len(wau_activities)
        
        # Monthly Active Users (last 30 days)
        month_ago = now - timedelta(days=30)
        mau_activities = await db.user_activities.distinct("user_id", {
            "created_at": {"$gte": month_ago}
        })
        mau = len(mau_activities)
        
        # Total registered users
        total_users = await db.users.count_documents({})
        
        # Activity breakdown
        activity_counts = await db.user_activities.aggregate([
            {"$match": {"created_at": {"$gte": month_ago}}},
            {"$group": {
                "_id": "$activity_type",
                "count": {"$sum": 1}
            }}
        ]).to_list(length=100)
        
        activity_breakdown = {item["_id"]: item["count"] for item in activity_counts}
        
        return {
            "period_days": days,
            "daily_active_users": dau,
            "weekly_active_users": wau,
            "monthly_active_users": mau,
            "total_registered_users": total_users,
            "engagement_rate": round((mau / total_users * 100) if total_users > 0 else 0, 2),
            "activity_breakdown": activity_breakdown,
            "stickiness_ratio": round((dau / mau) if mau > 0 else 0, 3),
            "timestamp": now.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-analysis")
async def retention_analysis(
    months: int = 6,
    admin = Depends(require_admin_or_above)
):
    """
    Perform retention cohort analysis
    Returns retention rates by registration cohort
    """
    return await analyze_retention_cohorts(months)


@router.get("/churn-prediction")
async def churn_prediction(
    inactivity_days: int = 14,
    admin = Depends(require_admin_or_above)
):
    """
    Identify users at risk of churning
    Returns list of inactive users
    """
    try:
        at_risk_users = await identify_at_risk_users(inactivity_days)
        
        # Categorize by risk level
        critical_risk = [u for u in at_risk_users if u.get("risk_level") == "critical"]
        high_risk = [u for u in at_risk_users if u.get("risk_level") == "high"]
        medium_risk = [u for u in at_risk_users if u.get("risk_level") == "medium"]
        
        return {
            "total_at_risk": len(at_risk_users),
            "critical_risk_count": len(critical_risk),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "users": at_risk_users[:100],  # Return first 100
            "inactivity_threshold_days": inactivity_days,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in churn prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lifecycle/{user_id}")
async def user_lifecycle(
    user_id: str,
    admin = Depends(require_admin_or_above)
):
    """
    Get comprehensive lifecycle data for a user
    """
    return await get_user_lifecycle_data(user_id)


@router.post("/campaigns/trigger")
async def trigger_reengagement_campaign(
    request: ReEngagementCampaignRequest,
    background_tasks: BackgroundTasks,
    admin = Depends(require_admin_or_above)
):
    """
    Trigger re-engagement campaign for inactive users
    """
    try:
        # Get inactive users
        at_risk_users = await identify_at_risk_users(request.days_inactive)
        
        if request.dry_run:
            return {
                "dry_run": True,
                "target_users": len(at_risk_users),
                "campaign_type": request.campaign_type,
                "message": "No emails sent (dry run mode)",
                "users_preview": at_risk_users[:10]
            }
        
        # In production, this would trigger actual emails
        # For now, we'll just log it
        triggered_count = 0
        for user in at_risk_users:
            logger.info(f"Re-engagement email would be sent to: {user.get('email')} (Campaign: {request.campaign_type})")
            triggered_count += 1
        
        return {
            "success": True,
            "campaign_type": request.campaign_type,
            "emails_triggered": triggered_count,
            "target_users": len(at_risk_users),
            "message": f"Re-engagement campaign triggered for {triggered_count} users"
        }
    except Exception as e:
        logger.error(f"Error triggering re-engagement campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inactive-users")
async def get_inactive_users(
    days: int = 30,
    limit: int = 100,
    admin = Depends(require_admin_or_above)
):
    """
    Get list of inactive users
    """
    try:
        at_risk_users = await identify_at_risk_users(days)
        
        return {
            "total_inactive": len(at_risk_users),
            "inactivity_threshold_days": days,
            "users": at_risk_users[:limit],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting inactive users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
