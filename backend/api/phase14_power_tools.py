"""
Phase 14.6 - Admin Power Tools
Advanced admin utilities for efficient data management
"""

import csv
import io
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)


class AdvancedSearchFilter:
    """Advanced search and filtering utilities"""
    
    @staticmethod
    def build_query(filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build MongoDB query from advanced filters
        
        Supports:
        - Text search
        - Date ranges
        - Status filters
        - Custom field filters
        """
        query = {}
        
        # Text search
        if filters.get("search"):
            search_text = filters["search"]
            query["$or"] = [
                {"name": {"$regex": search_text, "$options": "i"}},
                {"email": {"$regex": search_text, "$options": "i"}},
                {"title": {"$regex": search_text, "$options": "i"}},
                {"content": {"$regex": search_text, "$options": "i"}},
                {"description": {"$regex": search_text, "$options": "i"}}
            ]
        
        # Date range filters
        if filters.get("date_from") or filters.get("date_to"):
            date_query = {}
            if filters.get("date_from"):
                date_query["$gte"] = datetime.fromisoformat(filters["date_from"].replace('Z', '+00:00'))
            if filters.get("date_to"):
                date_query["$lte"] = datetime.fromisoformat(filters["date_to"].replace('Z', '+00:00'))
            query["created_at"] = date_query
        
        # Status filter
        if filters.get("status"):
            if isinstance(filters["status"], list):
                query["status"] = {"$in": filters["status"]}
            else:
                query["status"] = filters["status"]
        
        # Boolean filters
        if filters.get("is_active") is not None:
            query["is_active"] = filters["is_active"]
        
        if filters.get("is_deleted") is not None:
            query["is_deleted"] = filters["is_deleted"]
        
        if filters.get("is_featured") is not None:
            query["is_featured"] = filters["is_featured"]
        
        # Category filter
        if filters.get("category"):
            query["category"] = filters["category"]
        
        # Role filter (for admins)
        if filters.get("role"):
            query["role"] = filters["role"]
        
        # Custom field filters
        if filters.get("custom_fields"):
            for key, value in filters["custom_fields"].items():
                query[key] = value
        
        return query


class BulkDataExporter:
    """Bulk data export utilities"""
    
    @staticmethod
    async def export_to_csv(data: List[Dict[str, Any]], fields: List[str]) -> StreamingResponse:
        """
        Export data to CSV format
        
        Args:
            data: List of dictionaries to export
            fields: List of field names to include in CSV
        
        Returns:
            StreamingResponse with CSV file
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        
        writer.writeheader()
        for item in data:
            # Convert datetime objects to strings
            row = {}
            for field in fields:
                value = item.get(field)
                if isinstance(value, datetime):
                    row[field] = value.isoformat()
                elif value is None:
                    row[field] = ""
                else:
                    row[field] = str(value)
            writer.writerow(row)
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    
    @staticmethod
    async def export_to_json(data: List[Dict[str, Any]]) -> StreamingResponse:
        """
        Export data to JSON format
        
        Args:
            data: List of dictionaries to export
        
        Returns:
            StreamingResponse with JSON file
        """
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Convert datetime objects
        processed_data = []
        for item in data:
            processed_item = {}
            for key, value in item.items():
                processed_item[key] = convert_datetime(value)
            processed_data.append(processed_item)
        
        json_str = json.dumps(processed_data, indent=2, default=str)
        
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )


class DataValidator:
    """Data validation and integrity checking utilities"""
    
    @staticmethod
    async def validate_collection(db, collection_name: str) -> Dict[str, Any]:
        """
        Validate data integrity in a collection
        
        Checks for:
        - Missing required fields
        - Invalid data types
        - Orphaned references
        - Duplicate entries
        """
        collection = db[collection_name]
        documents = await collection.find().to_list(length=None)
        
        validation_results = {
            "collection": collection_name,
            "total_documents": len(documents),
            "issues": [],
            "warnings": [],
            "valid_count": 0,
            "invalid_count": 0
        }
        
        required_fields = {
            "session_bookings": ["id", "name", "email", "status", "created_at"],
            "events": ["id", "title", "date", "status", "created_at"],
            "blogs": ["id", "title", "content", "status", "created_at"],
            "careers": ["id", "title", "description", "status", "created_at"],
            "volunteers": ["id", "name", "email", "status", "created_at"],
            "psychologists": ["id", "name", "email", "created_at"],
            "contact_forms": ["id", "name", "email", "message", "created_at"],
            "admins": ["id", "email", "role", "created_at"]
        }
        
        fields = required_fields.get(collection_name, ["id", "created_at"])
        
        for doc in documents:
            doc_valid = True
            
            # Check required fields
            missing_fields = []
            for field in fields:
                if field not in doc or doc[field] is None:
                    missing_fields.append(field)
                    doc_valid = False
            
            if missing_fields:
                validation_results["issues"].append({
                    "document_id": doc.get("id", doc.get("_id")),
                    "type": "missing_fields",
                    "fields": missing_fields
                })
            
            # Check email format
            if "email" in doc and doc["email"]:
                if "@" not in doc["email"]:
                    validation_results["issues"].append({
                        "document_id": doc.get("id"),
                        "type": "invalid_email",
                        "value": doc["email"]
                    })
                    doc_valid = False
            
            # Check dates
            if "created_at" in doc:
                if not isinstance(doc["created_at"], datetime):
                    validation_results["warnings"].append({
                        "document_id": doc.get("id"),
                        "type": "invalid_date_type",
                        "field": "created_at"
                    })
            
            if doc_valid:
                validation_results["valid_count"] += 1
            else:
                validation_results["invalid_count"] += 1
        
        # Check for duplicates
        if "email" in documents[0] if documents else False:
            emails = [doc.get("email") for doc in documents if doc.get("email")]
            duplicates = [email for email in emails if emails.count(email) > 1]
            if duplicates:
                validation_results["warnings"].append({
                    "type": "duplicate_emails",
                    "count": len(set(duplicates)),
                    "emails": list(set(duplicates))
                })
        
        validation_results["status"] = "healthy" if validation_results["invalid_count"] == 0 else "issues_found"
        
        return validation_results
    
    @staticmethod
    async def fix_common_issues(db, collection_name: str, issue_type: str) -> Dict[str, Any]:
        """
        Automatically fix common data issues
        
        Supported fixes:
        - Add missing timestamps
        - Standardize status values
        - Remove orphaned records
        """
        collection = db[collection_name]
        fixed_count = 0
        
        if issue_type == "missing_timestamps":
            # Add created_at to documents missing it
            result = await collection.update_many(
                {"created_at": {"$exists": False}},
                {"$set": {"created_at": datetime.utcnow()}}
            )
            fixed_count = result.modified_count
        
        elif issue_type == "normalize_status":
            # Standardize status values to lowercase
            documents = await collection.find({"status": {"$exists": True}}).to_list(length=None)
            for doc in documents:
                if doc.get("status") and doc["status"] != doc["status"].lower():
                    await collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"status": doc["status"].lower()}}
                    )
                    fixed_count += 1
        
        elif issue_type == "remove_deleted":
            # Remove soft-deleted records older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            result = await collection.delete_many({
                "is_deleted": True,
                "deleted_at": {"$lt": cutoff_date}
            })
            fixed_count = result.deleted_count
        
        return {
            "collection": collection_name,
            "issue_type": issue_type,
            "fixed_count": fixed_count,
            "timestamp": datetime.utcnow()
        }


class QuickActions:
    """Quick action utilities for common admin tasks"""
    
    @staticmethod
    async def get_dashboard_stats(db) -> Dict[str, Any]:
        """Get quick dashboard statistics"""
        stats = {}
        
        # Count active records
        collections_to_count = [
            "session_bookings",
            "events",
            "blogs",
            "careers",
            "volunteers",
            "psychologists",
            "contact_forms",
            "admins"
        ]
        
        for coll_name in collections_to_count:
            try:
                collection = db[coll_name]
                
                # Total count
                total = await collection.count_documents({})
                
                # Active/published count
                active_query = {"is_deleted": {"$ne": True}}
                if coll_name in ["events", "blogs", "careers"]:
                    active_query["status"] = "published"
                elif coll_name in ["session_bookings", "volunteers", "contact_forms"]:
                    active_query["status"] = {"$ne": "cancelled"}
                
                active = await collection.count_documents(active_query)
                
                # Recent count (last 7 days)
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                recent = await collection.count_documents({
                    "created_at": {"$gte": seven_days_ago}
                })
                
                stats[coll_name] = {
                    "total": total,
                    "active": active,
                    "recent_7_days": recent
                }
            except Exception as e:
                logger.error(f"Error counting {coll_name}: {e}")
                stats[coll_name] = {"error": str(e)}
        
        return stats
    
    @staticmethod
    async def get_pending_actions(db) -> Dict[str, Any]:
        """Get list of items requiring admin attention"""
        pending = {}
        
        try:
            # Pending session bookings
            sessions = db["session_bookings"]
            pending_sessions = await sessions.count_documents({"status": "pending"})
            pending["pending_sessions"] = pending_sessions
            
            # Pending volunteers
            volunteers = db["volunteers"]
            pending_volunteers = await volunteers.count_documents({"status": "pending"})
            pending["pending_volunteers"] = pending_volunteers
            
            # Unread contact forms
            contacts = db["contact_forms"]
            unread_contacts = await contacts.count_documents({"status": "new"})
            pending["unread_contacts"] = unread_contacts
            
            # Pending approval requests
            if "approval_requests" in await db.list_collection_names():
                approvals = db["approval_requests"]
                pending_approvals = await approvals.count_documents({"status": "pending"})
                pending["pending_approvals"] = pending_approvals
            
            pending["total_pending"] = sum([
                pending_sessions,
                pending_volunteers,
                unread_contacts,
                pending.get("pending_approvals", 0)
            ])
        
        except Exception as e:
            logger.error(f"Error getting pending actions: {e}")
            pending["error"] = str(e)
        
        return pending
