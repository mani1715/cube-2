"""
Phase 8.1B - Basic Analytics Dashboard
Session & event trends, blog engagement, volunteer stats, CSV exports
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pymongo import MongoClient
import csv
import io

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Collections
sessions_collection = db['session_bookings']
events_collection = db['events']
blogs_collection = db['blogs']
volunteers_collection = db['volunteers']
contacts_collection = db['contact_forms']


class AnalyticsEngine:
    """Provides basic analytics and insights"""
    
    @staticmethod
    async def get_session_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get session booking analytics
        
        Returns:
            - Total sessions
            - Sessions by status
            - Sessions by time period
            - Popular session types
        """
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Total sessions
        total_sessions = sessions_collection.count_documents(query)
        
        # Sessions by status
        status_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        status_breakdown = list(sessions_collection.aggregate(status_pipeline))
        
        # Sessions over time (daily)
        time_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        sessions_over_time = list(sessions_collection.aggregate(time_pipeline))
        
        # Average sessions per day
        days_in_range = (end_date - start_date).days + 1
        avg_sessions_per_day = total_sessions / days_in_range if days_in_range > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "avg_sessions_per_day": round(avg_sessions_per_day, 2),
            "status_breakdown": status_breakdown,
            "sessions_over_time": sessions_over_time,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days_in_range
            }
        }
    
    @staticmethod
    async def get_event_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get event analytics
        
        Returns:
            - Total events
            - Events by status
            - Total registrations
            - Popular events
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Total events
        total_events = events_collection.count_documents(query)
        
        # Active events (status = active)
        active_events = events_collection.count_documents({
            **query,
            "status": "active"
        })
        
        # Total registrations
        registration_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "total_registrations": {"$sum": "$registrations"}
            }}
        ]
        registration_result = list(events_collection.aggregate(registration_pipeline))
        total_registrations = registration_result[0]["total_registrations"] if registration_result else 0
        
        # Top events by registrations
        top_events_pipeline = [
            {"$match": query},
            {"$sort": {"registrations": -1}},
            {"$limit": 5},
            {"$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "registrations": 1,
                "max_attendees": 1
            }}
        ]
        top_events = list(events_collection.aggregate(top_events_pipeline))
        
        return {
            "total_events": total_events,
            "active_events": active_events,
            "total_registrations": total_registrations,
            "avg_registrations_per_event": round(total_registrations / total_events, 2) if total_events > 0 else 0,
            "top_events": top_events,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_blog_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get blog engagement analytics
        
        Returns:
            - Total blogs
            - Blogs by status
            - Blogs by category
            - Featured blogs
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Total blogs
        total_blogs = blogs_collection.count_documents(query)
        
        # Published blogs
        published_blogs = blogs_collection.count_documents({
            **query,
            "status": "published"
        })
        
        # Featured blogs
        featured_blogs = blogs_collection.count_documents({
            **query,
            "is_featured": True
        })
        
        # Blogs by category
        category_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        category_breakdown = list(blogs_collection.aggregate(category_pipeline))
        
        # Recent blogs
        recent_blogs_pipeline = [
            {"$match": query},
            {"$sort": {"created_at": -1}},
            {"$limit": 5},
            {"$project": {
                "_id": 0,
                "id": 1,
                "title": 1,
                "category": 1,
                "status": 1,
                "created_at": 1
            }}
        ]
        recent_blogs = list(blogs_collection.aggregate(recent_blogs_pipeline))
        
        return {
            "total_blogs": total_blogs,
            "published_blogs": published_blogs,
            "featured_blogs": featured_blogs,
            "category_breakdown": category_breakdown,
            "recent_blogs": recent_blogs,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_volunteer_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get volunteer application analytics
        
        Returns:
            - Total applications
            - Applications by status
            - Applications over time
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Total applications
        total_applications = volunteers_collection.count_documents(query)
        
        # Applications by status
        status_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        status_breakdown = list(volunteers_collection.aggregate(status_pipeline))
        
        # Applications over time
        time_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        applications_over_time = list(volunteers_collection.aggregate(time_pipeline))
        
        return {
            "total_applications": total_applications,
            "status_breakdown": status_breakdown,
            "applications_over_time": applications_over_time,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_contact_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get contact form analytics
        
        Returns:
            - Total contacts
            - Contacts by status
            - Response rate
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Total contacts
        total_contacts = contacts_collection.count_documents(query)
        
        # Contacts by status
        status_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        status_breakdown = list(contacts_collection.aggregate(status_pipeline))
        
        # Resolved contacts
        resolved_contacts = contacts_collection.count_documents({
            **query,
            "status": "resolved"
        })
        
        # Response rate
        response_rate = (resolved_contacts / total_contacts * 100) if total_contacts > 0 else 0
        
        return {
            "total_contacts": total_contacts,
            "resolved_contacts": resolved_contacts,
            "response_rate": round(response_rate, 2),
            "status_breakdown": status_breakdown,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def get_dashboard_overview(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get complete dashboard overview with key metrics
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get all analytics
        session_stats = await AnalyticsEngine.get_session_analytics(start_date, end_date)
        event_stats = await AnalyticsEngine.get_event_analytics(start_date, end_date)
        blog_stats = await AnalyticsEngine.get_blog_analytics(start_date, end_date)
        volunteer_stats = await AnalyticsEngine.get_volunteer_analytics(start_date, end_date)
        contact_stats = await AnalyticsEngine.get_contact_analytics(start_date, end_date)
        
        return {
            "overview": {
                "total_sessions": session_stats["total_sessions"],
                "total_events": event_stats["total_events"],
                "total_blogs": blog_stats["total_blogs"],
                "total_volunteers": volunteer_stats["total_applications"],
                "total_contacts": contact_stats["total_contacts"]
            },
            "sessions": session_stats,
            "events": event_stats,
            "blogs": blog_stats,
            "volunteers": volunteer_stats,
            "contacts": contact_stats,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    async def export_analytics_csv(
        data_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Export analytics data to CSV format
        
        Args:
            data_type: Type of data to export (sessions, events, blogs, volunteers, contacts)
            start_date: Start date for data
            end_date: End date for data
        
        Returns:
            CSV string
        """
        
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Select collection and fields based on data type
        collection_map = {
            "sessions": (sessions_collection, ["id", "name", "email", "phone", "session_type", "status", "created_at"]),
            "events": (events_collection, ["id", "title", "description", "date", "location", "registrations", "status", "created_at"]),
            "blogs": (blogs_collection, ["id", "title", "category", "author", "status", "is_featured", "created_at"]),
            "volunteers": (volunteers_collection, ["id", "name", "email", "phone", "availability", "status", "created_at"]),
            "contacts": (contacts_collection, ["id", "name", "email", "phone", "subject", "message", "status", "created_at"])
        }
        
        if data_type not in collection_map:
            raise ValueError(f"Invalid data type: {data_type}")
        
        collection, fields = collection_map[data_type]
        
        # Fetch data
        data = list(collection.find(query, {"_id": 0}).sort("created_at", -1))
        
        # Convert to CSV
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for item in data:
                # Convert datetime to string
                if "created_at" in item and isinstance(item["created_at"], datetime):
                    item["created_at"] = item["created_at"].isoformat()
                if "date" in item and isinstance(item["date"], datetime):
                    item["date"] = item["date"].isoformat()
                
                # Only write fields that exist
                row = {k: item.get(k, "") for k in fields}
                writer.writerow(row)
        
        return output.getvalue()


# Singleton instance
analytics_engine = AnalyticsEngine()
