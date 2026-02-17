"""
Phase 8.1A - Notification Rule Engine
Automated notification system with rule-based triggers
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pymongo import MongoClient
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Collections
notification_rules_collection = db['notification_rules']
notifications_collection = db['notifications']


class NotificationRuleEngine:
    """Manages notification rules and triggers"""
    
    RULE_TYPES = [
        'event_based',      # Triggered by specific events (new booking, status change, etc.)
        'threshold_based',  # Triggered when metrics cross thresholds
        'scheduled'         # Triggered at specific times
    ]
    
    TRIGGER_EVENTS = [
        'session_created',
        'session_confirmed',
        'session_cancelled',
        'event_registered',
        'volunteer_applied',
        'contact_form_submitted',
        'blog_published',
        'threshold_exceeded'
    ]
    
    ACTION_TYPES = [
        'send_email',       # Send email (currently mocked)
        'create_alert',     # Create admin alert
        'log_event',        # Log to system
        'webhook'           # Call external webhook (future)
    ]
    
    @staticmethod
    async def create_rule(
        name: str,
        description: str,
        rule_type: str,
        trigger_event: str,
        conditions: Dict[str, Any],
        actions: List[Dict[str, Any]],
        enabled: bool = True,
        created_by: str = None
    ) -> Dict[str, Any]:
        """Create a new notification rule"""
        
        rule_id = str(uuid.uuid4())
        rule = {
            "id": rule_id,
            "name": name,
            "description": description,
            "rule_type": rule_type,
            "trigger_event": trigger_event,
            "conditions": conditions,  # e.g., {"status": "confirmed", "min_sessions": 10}
            "actions": actions,        # e.g., [{"type": "send_email", "template": "welcome"}]
            "enabled": enabled,
            "execution_count": 0,
            "last_executed": None,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        notification_rules_collection.insert_one(rule)
        return rule
    
    @staticmethod
    async def get_rules(
        rule_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get notification rules with filters"""
        
        query = {}
        if rule_type:
            query["rule_type"] = rule_type
        if enabled is not None:
            query["enabled"] = enabled
        
        total = notification_rules_collection.count_documents(query)
        rules = list(
            notification_rules_collection.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        return {
            "rules": rules,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def update_rule(
        rule_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a notification rule"""
        
        updates["updated_at"] = datetime.utcnow()
        
        result = notification_rules_collection.update_one(
            {"id": rule_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Rule {rule_id} not found")
        
        updated_rule = notification_rules_collection.find_one({"id": rule_id}, {"_id": 0})
        return updated_rule
    
    @staticmethod
    async def delete_rule(rule_id: str) -> bool:
        """Delete a notification rule"""
        
        result = notification_rules_collection.delete_one({"id": rule_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def trigger_event(
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Trigger notification rules based on an event
        Returns list of executed actions
        """
        
        # Find enabled rules that match this event
        matching_rules = list(
            notification_rules_collection.find({
                "enabled": True,
                "trigger_event": event_type
            }, {"_id": 0})
        )
        
        executed_actions = []
        
        for rule in matching_rules:
            # Check if conditions are met
            if NotificationRuleEngine._check_conditions(rule["conditions"], event_data):
                # Execute actions
                for action in rule["actions"]:
                    result = await NotificationRuleEngine._execute_action(
                        action,
                        event_data,
                        rule
                    )
                    executed_actions.append(result)
                
                # Update execution stats
                notification_rules_collection.update_one(
                    {"id": rule["id"]},
                    {
                        "$inc": {"execution_count": 1},
                        "$set": {"last_executed": datetime.utcnow()}
                    }
                )
        
        return executed_actions
    
    @staticmethod
    def _check_conditions(conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Check if event data meets rule conditions"""
        
        if not conditions:
            return True
        
        for key, expected_value in conditions.items():
            actual_value = event_data.get(key)
            
            # Handle different comparison operators
            if isinstance(expected_value, dict):
                operator = expected_value.get("operator", "eq")
                value = expected_value.get("value")
                
                if operator == "eq" and actual_value != value:
                    return False
                elif operator == "ne" and actual_value == value:
                    return False
                elif operator == "gt" and not (actual_value and actual_value > value):
                    return False
                elif operator == "gte" and not (actual_value and actual_value >= value):
                    return False
                elif operator == "lt" and not (actual_value and actual_value < value):
                    return False
                elif operator == "lte" and not (actual_value and actual_value <= value):
                    return False
                elif operator == "in" and actual_value not in value:
                    return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True
    
    @staticmethod
    async def _execute_action(
        action: Dict[str, Any],
        event_data: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a notification action"""
        
        action_type = action.get("type")
        action_id = str(uuid.uuid4())
        
        result = {
            "action_id": action_id,
            "action_type": action_type,
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "executed_at": datetime.utcnow(),
            "status": "success",
            "details": {}
        }
        
        try:
            if action_type == "send_email":
                # Mock email sending
                recipient = action.get("recipient", event_data.get("email", "admin@acube.com"))
                template = action.get("template", "default")
                
                print(f"📧 [MOCK EMAIL] Sending '{template}' to {recipient}")
                print(f"   Rule: {rule['name']}")
                print(f"   Event Data: {event_data}")
                
                result["details"] = {
                    "recipient": recipient,
                    "template": template,
                    "sent": True
                }
            
            elif action_type == "create_alert":
                # Create admin alert/notification
                alert = {
                    "id": str(uuid.uuid4()),
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "title": action.get("title", f"Alert from {rule['name']}"),
                    "message": action.get("message", str(event_data)),
                    "severity": action.get("severity", "info"),  # info, warning, error
                    "read": False,
                    "event_data": event_data,
                    "created_at": datetime.utcnow()
                }
                
                notifications_collection.insert_one(alert)
                print(f"🔔 Alert Created: {alert['title']}")
                
                result["details"] = {
                    "alert_id": alert["id"],
                    "title": alert["title"]
                }
            
            elif action_type == "log_event":
                # Log to system
                print(f"📝 [EVENT LOG] Rule: {rule['name']}")
                print(f"   Event: {event_data}")
                
                result["details"] = {
                    "logged": True,
                    "message": action.get("message", "Event logged")
                }
            
            elif action_type == "webhook":
                # Future: Call external webhook
                webhook_url = action.get("url")
                print(f"🔗 [WEBHOOK] Would call: {webhook_url}")
                print(f"   Payload: {event_data}")
                
                result["details"] = {
                    "webhook_url": webhook_url,
                    "payload_sent": True
                }
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"❌ Action execution failed: {e}")
        
        return result
    
    @staticmethod
    async def get_notifications(
        read: Optional[bool] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get admin notifications/alerts"""
        
        query = {}
        if read is not None:
            query["read"] = read
        if severity:
            query["severity"] = severity
        
        total = notifications_collection.count_documents(query)
        notifications = list(
            notifications_collection.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Get unread count
        unread_count = notifications_collection.count_documents({"read": False})
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def mark_notification_read(notification_id: str) -> bool:
        """Mark a notification as read"""
        
        result = notifications_collection.update_one(
            {"id": notification_id},
            {"$set": {"read": True}}
        )
        
        return result.matched_count > 0
    
    @staticmethod
    async def mark_all_notifications_read() -> int:
        """Mark all notifications as read"""
        
        result = notifications_collection.update_many(
            {"read": False},
            {"$set": {"read": True}}
        )
        
        return result.modified_count


# Initialize with default rules
async def initialize_default_rules():
    """Create default notification rules if they don't exist"""
    
    existing_rules = notification_rules_collection.count_documents({})
    if existing_rules > 0:
        return  # Rules already exist
    
    default_rules = [
        {
            "name": "New Session Booking Alert",
            "description": "Send alert when a new session is booked",
            "rule_type": "event_based",
            "trigger_event": "session_created",
            "conditions": {},
            "actions": [
                {
                    "type": "create_alert",
                    "title": "New Session Booking",
                    "message": "A new session has been booked",
                    "severity": "info"
                },
                {
                    "type": "send_email",
                    "recipient": "admin@acube.com",
                    "template": "new_session_notification"
                }
            ],
            "enabled": True
        },
        {
            "name": "Session Confirmed Email",
            "description": "Send confirmation email when session is confirmed",
            "rule_type": "event_based",
            "trigger_event": "session_confirmed",
            "conditions": {"status": "confirmed"},
            "actions": [
                {
                    "type": "send_email",
                    "template": "session_confirmation"
                }
            ],
            "enabled": True
        },
        {
            "name": "New Volunteer Application",
            "description": "Alert admins about new volunteer applications",
            "rule_type": "event_based",
            "trigger_event": "volunteer_applied",
            "conditions": {},
            "actions": [
                {
                    "type": "create_alert",
                    "title": "New Volunteer Application",
                    "message": "A new volunteer application has been received",
                    "severity": "info"
                }
            ],
            "enabled": True
        },
        {
            "name": "Contact Form Alert",
            "description": "Alert for new contact form submissions",
            "rule_type": "event_based",
            "trigger_event": "contact_form_submitted",
            "conditions": {},
            "actions": [
                {
                    "type": "create_alert",
                    "title": "New Contact Form",
                    "message": "New contact form submission received",
                    "severity": "info"
                },
                {
                    "type": "log_event",
                    "message": "Contact form logged"
                }
            ],
            "enabled": True
        }
    ]
    
    for rule_data in default_rules:
        await NotificationRuleEngine.create_rule(
            name=rule_data["name"],
            description=rule_data["description"],
            rule_type=rule_data["rule_type"],
            trigger_event=rule_data["trigger_event"],
            conditions=rule_data["conditions"],
            actions=rule_data["actions"],
            enabled=rule_data["enabled"],
            created_by="system"
        )
    
    print(f"✅ Initialized {len(default_rules)} default notification rules")


# Singleton instance
notification_engine = NotificationRuleEngine()
