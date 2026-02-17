"""
Phase 15 - Push Notification Routes
API endpoints for push notification foundation (disabled by default)
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from .admin.permissions import require_super_admin, get_current_admin
from .phase15_push_notifications import (
    PushSubscriptionManager,
    NotificationPreferences,
    PushNotificationQueue,
    get_push_notification_status,
    toggle_push_notifications,
    get_push_notification_stats
)

router = APIRouter(prefix="/api/phase15/push", tags=["Phase 15 - Push Notifications"])


# ========================================
# Request/Response Models
# ========================================

class PushSubscriptionRequest(BaseModel):
    """Push notification subscription request"""
    user_id: str = Field(..., description="User identifier")
    endpoint: str = Field(..., description="Push subscription endpoint")
    keys: Dict[str, str] = Field(..., description="Subscription keys (p256dh, auth)")
    platform: Optional[str] = Field(default="web", description="Platform (web, mobile)")
    browser: Optional[str] = Field(default="unknown", description="Browser name")


class NotificationPreferencesRequest(BaseModel):
    """Notification preferences update request"""
    push_enabled: bool = Field(..., description="Enable push notifications")
    notifications: Dict[str, bool] = Field(..., description="Notification type preferences")
    quiet_hours: Optional[Dict[str, Any]] = Field(default=None, description="Quiet hours configuration")


class QueueNotificationRequest(BaseModel):
    """Queue notification request"""
    user_id: str = Field(..., description="Target user ID")
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title", max_length=100)
    body: str = Field(..., description="Notification body", max_length=500)
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data payload")
    priority: str = Field(default="normal", description="Priority (low, normal, high, urgent)")


class FeatureToggleRequest(BaseModel):
    """Feature toggle request"""
    enabled: bool = Field(..., description="Enable or disable feature")


# ========================================
# Public Endpoints (User-facing)
# ========================================

@router.post("/subscribe", status_code=201)
async def subscribe_to_push(
    subscription: PushSubscriptionRequest
) -> Dict[str, Any]:
    """
    Subscribe to push notifications
    
    Users can opt-in to receive push notifications by providing their subscription details.
    """
    try:
        # Check if push notifications are enabled
        status = get_push_notification_status()
        if not status["enabled"]:
            raise HTTPException(
                status_code=403,
                detail="Push notifications are currently disabled by administrators"
            )
        
        # Save subscription
        result = PushSubscriptionManager.save_subscription(
            user_id=subscription.user_id,
            subscription=subscription.dict()
        )
        
        return {
            "success": True,
            "message": "Successfully subscribed to push notifications",
            "subscription": {
                "user_id": result["user_id"],
                "endpoint": result["endpoint"],
                "created_at": result["created_at"].isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")


@router.delete("/unsubscribe")
async def unsubscribe_from_push(
    user_id: str,
    endpoint: str
) -> Dict[str, Any]:
    """
    Unsubscribe from push notifications
    
    Users can opt-out of push notifications.
    """
    try:
        success = PushSubscriptionManager.remove_subscription(user_id, endpoint)
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {
            "success": True,
            "message": "Successfully unsubscribed from push notifications"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(e)}")


@router.get("/subscriptions/{user_id}")
async def get_user_subscriptions(user_id: str) -> Dict[str, Any]:
    """
    Get all active push subscriptions for a user
    """
    try:
        subscriptions = PushSubscriptionManager.get_user_subscriptions(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "total": len(subscriptions),
            "subscriptions": subscriptions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscriptions: {str(e)}")


@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get notification preferences for a user
    """
    try:
        preferences = NotificationPreferences.get_preferences(user_id)
        
        return {
            "success": True,
            "preferences": preferences
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")


@router.put("/preferences/{user_id}")
async def update_notification_preferences(
    user_id: str,
    preferences: NotificationPreferencesRequest
) -> Dict[str, Any]:
    """
    Update notification preferences
    
    Users can customize which types of notifications they want to receive.
    """
    try:
        updated_prefs = NotificationPreferences.update_preferences(
            user_id=user_id,
            preferences=preferences.dict()
        )
        
        return {
            "success": True,
            "message": "Preferences updated successfully",
            "preferences": updated_prefs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/status")
async def get_push_status() -> Dict[str, Any]:
    """
    Get push notification feature status (public)
    
    Check if push notifications are enabled and available.
    """
    try:
        status = get_push_notification_status()
        
        return {
            "success": True,
            "push_notifications_enabled": status["enabled"],
            "description": status.get("description", "Push notifications for real-time updates")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# ========================================
# Admin Endpoints (Protected)
# ========================================

@router.get("/admin/status", dependencies=[Depends(require_super_admin)])
async def admin_get_push_status(
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get detailed push notification status (Admin only)
    
    Includes statistics and configuration details.
    """
    try:
        status = get_push_notification_status()
        
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/admin/toggle", dependencies=[Depends(require_super_admin)])
async def admin_toggle_push_notifications(
    toggle: FeatureToggleRequest,
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Enable or disable push notifications (Admin only)
    
    Super admin can toggle push notifications feature on/off.
    """
    try:
        status = toggle_push_notifications(enabled=toggle.enabled)
        
        return {
            "success": True,
            "message": f"Push notifications {'enabled' if toggle.enabled else 'disabled'} successfully",
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle: {str(e)}")


@router.get("/admin/statistics", dependencies=[Depends(require_super_admin)])
async def admin_get_push_statistics(
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get comprehensive push notification statistics (Admin only)
    
    Includes subscription counts, preference stats, and queue statistics.
    """
    try:
        stats = get_push_notification_stats()
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/admin/subscriptions", dependencies=[Depends(require_super_admin)])
async def admin_get_all_subscriptions(
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get all active push subscriptions (Admin only)
    
    View all subscribed users for management purposes.
    """
    try:
        subscriptions = PushSubscriptionManager.get_all_active_subscriptions()
        
        return {
            "success": True,
            "total": len(subscriptions),
            "subscriptions": subscriptions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscriptions: {str(e)}")


@router.post("/admin/queue", dependencies=[Depends(require_super_admin)])
async def admin_queue_notification(
    notification: QueueNotificationRequest,
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Queue a push notification for sending (Admin only)
    
    Admins can send targeted notifications to specific users.
    """
    try:
        # Check if push notifications are enabled
        status = get_push_notification_status()
        if not status["enabled"]:
            raise HTTPException(
                status_code=403,
                detail="Push notifications are currently disabled"
            )
        
        # Queue notification
        queued = PushNotificationQueue.queue_notification(
            user_id=notification.user_id,
            notification_type=notification.notification_type,
            title=notification.title,
            body=notification.body,
            data=notification.data,
            priority=notification.priority
        )
        
        return {
            "success": True,
            "message": "Notification queued successfully",
            "notification": queued
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue notification: {str(e)}")


@router.get("/admin/queue/pending", dependencies=[Depends(require_super_admin)])
async def admin_get_pending_notifications(
    limit: int = 100,
    admin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get pending notifications in queue (Admin only)
    
    View notifications waiting to be sent.
    """
    try:
        notifications = PushNotificationQueue.get_pending_notifications(limit=limit)
        
        return {
            "success": True,
            "total": len(notifications),
            "notifications": notifications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")
