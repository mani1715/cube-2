"""Admin utility functions for logging, permissions, and exports"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
import csv
import io
from datetime import datetime
from typing import List, Dict, Any
import logging
from .schemas import AdminActivityLog, Admin

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_id: str,
    admin_email: str,
    action: str,
    entity: str,
    entity_id: str,
    details: str = ""
):
    """
    Log admin actions to admin_logs collection
    
    Args:
        admin_id: ID of the admin performing the action
        admin_email: Email of the admin
        action: Type of action (create, update, delete, status_change)
        entity: Type of entity (sessions, events, blogs, etc.)
        entity_id: ID of the entity being modified
        details: Additional details about the action
    """
    try:
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        log_entry = AdminActivityLog(
            admin_id=admin_id,
            admin_email=admin_email,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details
        )
        
        await db.admin_logs.insert_one(log_entry.dict())
        logger.info(f"Logged action: {action} on {entity} by {admin_email}")
        
        client.close()
    except Exception as e:
        logger.error(f"Failed to log admin action: {str(e)}")
        # Don't raise exception - logging failure shouldn't break main operation


def check_super_admin(admin: Admin) -> bool:
    """
    Check if admin has super_admin role
    
    Args:
        admin: Admin object
        
    Returns:
        bool: True if super_admin, False otherwise
    """
    return admin.role == "super_admin"


def generate_csv(data: List[Dict[str, Any]], fields: List[str]) -> str:
    """
    Generate CSV string from data
    
    Args:
        data: List of dictionaries containing data
        fields: List of field names to include in CSV
        
    Returns:
        str: CSV formatted string
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    
    for row in data:
        # Convert datetime objects to strings
        processed_row = {}
        for key, value in row.items():
            if isinstance(value, datetime):
                processed_row[key] = value.isoformat()
            elif isinstance(value, list):
                processed_row[key] = ', '.join(str(v) for v in value)
            else:
                processed_row[key] = value
        writer.writerow(processed_row)
    
    return output.getvalue()




def calculate_pagination(page: int, limit: int, total: int) -> dict:
    """
    Calculate pagination metadata
    
    Args:
        page: Current page number (1-indexed)
        limit: Number of items per page
        total: Total number of items
        
    Returns:
        dict: Pagination metadata
    """
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def get_skip_limit(page: int = 1, limit: int = 10) -> tuple:
    """
    Calculate skip and limit for MongoDB pagination
    
    Args:
        page: Current page number (1-indexed)
        limit: Number of items per page
        
    Returns:
        tuple: (skip, limit)
    """
    skip = (page - 1) * limit
    return skip, limit
