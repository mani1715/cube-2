"""
Phase 15 - Push Notification Foundation
Backend infrastructure for push notifications (disabled by default, admin toggle)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

def get_db():
    """Get database instance"""
    return db

# ========================================
# Push Notification Subscription Manager
# ========================================

class PushSubscriptionManager:
    """Manage push notification subscriptions"""
    
    @staticmethod
    def save_subscription(user_id: str, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a push notification subscription
        
        Args:
            user_id: User identifier
            subscription: Web Push subscription object
        
        Returns:
            Saved subscription document
        """
        db = get_db()
        
        subscription_doc = {
            "user_id": user_id,
            "endpoint": subscription.get("endpoint"),
            "keys": subscription.get("keys", {}),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "platform": subscription.get("platform", "web"),
            "browser": subscription.get("browser", "unknown"),
        }
        
        # Check if subscription already exists
        existing = db.push_subscriptions.find_one({
            "user_id": user_id,
            "endpoint": subscription.get("endpoint")
        })
        
        if existing:
            # Update existing subscription
            db.push_subscriptions.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "keys": subscription.get("keys", {}),
                        "is_active": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return {**existing, **subscription_doc}
        
        # Insert new subscription
        result = db.push_subscriptions.insert_one(subscription_doc)
        subscription_doc["_id"] = result.inserted_id
        
        return subscription_doc
    
    @staticmethod
    def get_user_subscriptions(user_id: str) -> List[Dict[str, Any]]:
        """Get all active subscriptions for a user"""
        db = get_db()
        
        subscriptions = list(db.push_subscriptions.find({
            "user_id": user_id,
            "is_active": True
        }).sort("created_at", DESCENDING))
        
        # Convert ObjectId to string
        for sub in subscriptions:
            sub["_id"] = str(sub["_id"])
        
        return subscriptions
    
    @staticmethod
    def remove_subscription(user_id: str, endpoint: str) -> bool:
        """Remove a push notification subscription"""
        db = get_db()
        
        result = db.push_subscriptions.update_one(
            {"user_id": user_id, "endpoint": endpoint},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_all_active_subscriptions() -> List[Dict[str, Any]]:
        """Get all active subscriptions (for admin use)"""
        db = get_db()
        
        subscriptions = list(db.push_subscriptions.find({
            "is_active": True
        }).sort("created_at", DESCENDING))
        
        # Convert ObjectId to string
        for sub in subscriptions:
            sub["_id"] = str(sub["_id"])
        
        return subscriptions


# ========================================
# Push Notification Preferences
# ========================================

class NotificationPreferences:
    """Manage user notification preferences"""
    
    @staticmethod
    def get_preferences(user_id: str) -> Dict[str, Any]:
        """Get notification preferences for a user"""
        db = get_db()
        
        prefs = db.notification_preferences.find_one({"user_id": user_id})
        
        if not prefs:
            # Return default preferences
            return {
                "user_id": user_id,
                "push_enabled": False,  # Disabled by default
                "notifications": {
                    "session_reminders": True,
                    "event_updates": True,
                    "blog_updates": False,
                    "promotional": False,
                    "system_alerts": True
                },
                "quiet_hours": {
                    "enabled": False,
                    "start": "22:00",
                    "end": "08:00"
                }
            }
        
        prefs["_id"] = str(prefs["_id"])
        return prefs
    
    @staticmethod
    def update_preferences(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification preferences"""
        db = get_db()
        
        prefs_doc = {
            "user_id": user_id,
            "push_enabled": preferences.get("push_enabled", False),
            "notifications": preferences.get("notifications", {}),
            "quiet_hours": preferences.get("quiet_hours", {}),
            "updated_at": datetime.utcnow()
        }
        
        result = db.notification_preferences.update_one(
            {"user_id": user_id},
            {"$set": prefs_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )
        
        return NotificationPreferences.get_preferences(user_id)


# ========================================
# Push Notification Queue
# ========================================

class PushNotificationQueue:
    """Queue for push notifications"""
    
    @staticmethod
    def queue_notification(
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Queue a push notification for sending
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            title: Notification title
            body: Notification body
            data: Additional data payload
            priority: Priority (low, normal, high, urgent)
        
        Returns:
            Queued notification document
        """
        db = get_db()
        
        notification_doc = {
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "body": body,
            "data": data or {},
            "priority": priority,
            "status": "queued",
            "attempts": 0,
            "max_attempts": 3,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sent_at": None,
            "error": None
        }
        
        result = db.push_notification_queue.insert_one(notification_doc)
        notification_doc["_id"] = str(result.inserted_id)
        
        return notification_doc
    
    @staticmethod
    def get_pending_notifications(limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending notifications to send"""
        db = get_db()
        
        notifications = list(db.push_notification_queue.find({
            "status": "queued",
            "attempts": {"$lt": 3}
        }).sort("priority", DESCENDING).limit(limit))
        
        for notif in notifications:
            notif["_id"] = str(notif["_id"])
        
        return notifications
    
    @staticmethod
    def mark_as_sent(notification_id: str) -> bool:
        """Mark notification as sent"""
        db = get_db()
        
        result = db.push_notification_queue.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def mark_as_failed(notification_id: str, error: str) -> bool:
        """Mark notification as failed"""
        db = get_db()
        
        result = db.push_notification_queue.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "status": "failed",
                    "error": error,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"attempts": 1}
            }
        )
        
        return result.modified_count > 0


# ========================================
# Admin Feature Toggle
# ========================================

def get_push_notification_status() -> Dict[str, Any]:
    """Get push notification feature status"""
    db = get_db()
    
    # Check feature toggle
    feature_toggle = db.feature_toggles.find_one({"name": "push_notifications"})
    
    if not feature_toggle:
        # Create default toggle (disabled)
        feature_toggle = {
            "name": "push_notifications",
            "enabled": False,
            "description": "Enable push notifications for users",
            "category": "engagement",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        db.feature_toggles.insert_one(feature_toggle)
    
    # Get statistics
    total_subscriptions = db.push_subscriptions.count_documents({"is_active": True})
    total_users_opted_in = db.notification_preferences.count_documents({"push_enabled": True})
    queued_notifications = db.push_notification_queue.count_documents({"status": "queued"})
    
    return {
        "enabled": feature_toggle.get("enabled", False),
        "statistics": {
            "total_subscriptions": total_subscriptions,
            "users_opted_in": total_users_opted_in,
            "queued_notifications": queued_notifications
        },
        "description": feature_toggle.get("description"),
        "last_updated": feature_toggle.get("updated_at")
    }


def toggle_push_notifications(enabled: bool) -> Dict[str, Any]:
    """Enable or disable push notifications feature"""
    db = get_db()
    
    result = db.feature_toggles.update_one(
        {"name": "push_notifications"},
        {
            "$set": {
                "enabled": enabled,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "name": "push_notifications",
                "description": "Enable push notifications for users",
                "category": "engagement",
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    return get_push_notification_status()


# ========================================
# Utility Functions
# ========================================

def get_push_notification_stats() -> Dict[str, Any]:
    """Get comprehensive push notification statistics"""
    db = get_db()
    
    # Subscription statistics
    total_subscriptions = db.push_subscriptions.count_documents({"is_active": True})
    subscriptions_by_platform = list(db.push_subscriptions.aggregate([
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]))
    
    # Preference statistics
    total_users_with_prefs = db.notification_preferences.count_documents({})
    users_opted_in = db.notification_preferences.count_documents({"push_enabled": True})
    
    # Queue statistics
    queued = db.push_notification_queue.count_documents({"status": "queued"})
    sent = db.push_notification_queue.count_documents({"status": "sent"})
    failed = db.push_notification_queue.count_documents({"status": "failed"})
    
    return {
        "subscriptions": {
            "total": total_subscriptions,
            "by_platform": [
                {"platform": item["_id"], "count": item["count"]}
                for item in subscriptions_by_platform
            ]
        },
        "preferences": {
            "total_users": total_users_with_prefs,
            "opted_in": users_opted_in,
            "opt_in_rate": round((users_opted_in / total_users_with_prefs * 100), 2) if total_users_with_prefs > 0 else 0
        },
        "queue": {
            "queued": queued,
            "sent": sent,
            "failed": failed,
            "total": queued + sent + failed
        }
    }
