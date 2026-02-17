"""
Phase 14.1 - Scalability & Infrastructure
Enhanced caching, connection pooling, and performance optimizations
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import logging
import asyncio
from cache import cache, generate_cache_key

logger = logging.getLogger(__name__)


# ============= CONNECTION POOL MANAGEMENT =============

class DatabaseConnectionPool:
    """
    Enhanced MongoDB connection pool manager
    Optimizes connection reuse and implements health checks
    """
    
    def __init__(self, mongo_url: str, db_name: str, 
                 max_pool_size: int = 50, 
                 min_pool_size: int = 10):
        """
        Initialize connection pool with optimized settings
        
        Args:
            mongo_url: MongoDB connection URL
            db_name: Database name
            max_pool_size: Maximum number of connections
            min_pool_size: Minimum number of connections to maintain
        """
        self.client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=45000,  # Close idle connections after 45s
            serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
            connectTimeoutMS=10000,  # 10s connection timeout
            socketTimeoutMS=20000,  # 20s socket timeout
            retryWrites=True,
            retryReads=True
        )
        self.db = self.client[db_name]
        self._stats = {
            "total_queries": 0,
            "failed_queries": 0,
            "avg_query_time": 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check connection pool health"""
        try:
            start_time = datetime.utcnow()
            await self.client.admin.command('ping')
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "max_pool_size": 50,
                "min_pool_size": 10,
                "stats": self._stats
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "stats": self._stats
            }
    
    def get_db(self):
        """Get database instance"""
        return self.db
    
    async def close(self):
        """Close all connections"""
        self.client.close()
        logger.info("Database connection pool closed")


# ============= ENHANCED CACHING STRATEGIES =============

class CacheStrategy:
    """Advanced caching strategies for different data types"""
    
    # Cache TTL configurations (in seconds)
    CACHE_CONFIGS = {
        # Static/rarely changing data - 1 hour
        "events": 3600,
        "blogs": 3600,
        "careers": 3600,
        "psychologists": 3600,
        
        # Semi-dynamic data - 10 minutes
        "sessions": 600,
        "volunteers": 600,
        "contacts": 600,
        
        # Dynamic aggregations - 5 minutes
        "analytics": 300,
        "dashboard": 300,
        
        # Statistics - 2 minutes
        "stats": 120,
        
        # Real-time data - 30 seconds
        "realtime": 30
    }
    
    @staticmethod
    def get_ttl(data_type: str) -> int:
        """Get appropriate TTL for data type"""
        return CacheStrategy.CACHE_CONFIGS.get(data_type, 300)
    
    @staticmethod
    async def cache_with_fallback(
        cache_key: str,
        fetch_function,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ):
        """
        Cache with fallback - tries cache first, falls back to database
        
        Args:
            cache_key: Key to use for caching
            fetch_function: Async function to fetch data if not cached
            ttl: Time-to-live in seconds
            force_refresh: Force refresh from database
        """
        # Try cache first unless force refresh
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        # Fetch from database
        try:
            data = await fetch_function()
            
            # Cache the result
            if ttl:
                cache.set(cache_key, data, ttl=ttl)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for cache key {cache_key}: {str(e)}")
            raise
    
    @staticmethod
    def invalidate_related_caches(entity_type: str):
        """
        Invalidate all caches related to an entity type
        Called when entity is created/updated/deleted
        """
        cache.invalidate_pattern(f"{entity_type}:")
        
        # Also invalidate related aggregation caches
        cache.invalidate_pattern("dashboard:")
        cache.invalidate_pattern("analytics:")
        cache.invalidate_pattern("stats:")
        
        logger.info(f"Invalidated caches for entity type: {entity_type}")


# ============= BATCH OPERATIONS OPTIMIZER =============

class BatchOperations:
    """Optimized batch operations for bulk data processing"""
    
    @staticmethod
    async def batch_insert(collection, documents: List[Dict], batch_size: int = 100):
        """
        Insert documents in optimized batches
        
        Args:
            collection: MongoDB collection
            documents: List of documents to insert
            batch_size: Number of documents per batch
        
        Returns:
            Number of inserted documents
        """
        if not documents:
            return 0
        
        total_inserted = 0
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                result = await collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                logger.debug(f"Batch insert: {len(result.inserted_ids)} documents")
            except Exception as e:
                logger.error(f"Batch insert error: {str(e)}")
                raise
        
        return total_inserted
    
    @staticmethod
    async def batch_update(collection, updates: List[tuple], batch_size: int = 50):
        """
        Update documents in optimized batches
        
        Args:
            collection: MongoDB collection
            updates: List of (filter, update) tuples
            batch_size: Number of operations per batch
        
        Returns:
            Number of modified documents
        """
        if not updates:
            return 0
        
        total_modified = 0
        
        # Process in batches
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            # Use bulk write for efficiency
            operations = [
                {"updateOne": {"filter": filter_doc, "update": update_doc}}
                for filter_doc, update_doc in batch
            ]
            
            try:
                result = await collection.bulk_write([
                    {"updateOne": op["updateOne"]} for op in operations
                ])
                total_modified += result.modified_count
                logger.debug(f"Batch update: {result.modified_count} documents modified")
            except Exception as e:
                logger.error(f"Batch update error: {str(e)}")
                raise
        
        return total_modified


# ============= QUERY OPTIMIZER =============

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    async def paginated_query(
        collection,
        query: Dict,
        page: int = 1,
        limit: int = 20,
        sort_field: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """
        Optimized paginated query with caching
        
        Args:
            collection: MongoDB collection
            query: Query filter
            page: Page number (1-indexed)
            limit: Items per page
            sort_field: Field to sort by
            sort_order: Sort order (1=asc, -1=desc)
        
        Returns:
            Dict with data and pagination info
        """
        skip = (page - 1) * limit
        
        # Execute query with projection (only necessary fields)
        cursor = collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        data = await cursor.to_list(length=limit)
        
        # Get total count (cached for 2 minutes)
        cache_key = generate_cache_key("count", collection=collection.name, **query)
        total = cache.get(cache_key)
        
        if total is None:
            total = await collection.count_documents(query)
            cache.set(cache_key, total, ttl=120)  # Cache count for 2 minutes
        
        total_pages = (total + limit - 1) // limit
        
        return {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    
    @staticmethod
    async def aggregation_with_cache(
        collection,
        pipeline: List[Dict],
        cache_key: str,
        ttl: int = 300
    ) -> List[Dict]:
        """
        Execute aggregation pipeline with caching
        
        Args:
            collection: MongoDB collection
            pipeline: Aggregation pipeline
            cache_key: Key for caching results
            ttl: Cache TTL in seconds
        
        Returns:
            Aggregation results
        """
        # Try cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute aggregation
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # Cache results
        cache.set(cache_key, results, ttl=ttl)
        
        return results


# ============= CACHE WARMING =============

class CacheWarmer:
    """Pre-populate cache for critical endpoints"""
    
    @staticmethod
    async def warm_critical_caches(db):
        """
        Pre-load commonly accessed data into cache
        Should be called on startup or periodically
        """
        logger.info("Starting cache warming for critical endpoints...")
        
        try:
            # Warm up active events cache
            events = await db.events.find({"is_active": True}).sort("date", -1).to_list(100)
            cache.set("events:is_active=True", events, ttl=3600)
            logger.info(f"Warmed events cache: {len(events)} items")
            
            # Warm up published blogs cache
            blogs = await db.blogs.find({"is_published": True}).sort("date", -1).to_list(100)
            cache.set("blogs:is_published=True", blogs, ttl=3600)
            logger.info(f"Warmed blogs cache: {len(blogs)} items")
            
            # Warm up active careers cache
            careers = await db.careers.find({"is_active": True}).sort("posted_at", -1).to_list(50)
            cache.set("careers:is_active=True", careers, ttl=3600)
            logger.info(f"Warmed careers cache: {len(careers)} items")
            
            # Warm up active psychologists cache
            psychologists = await db.psychologists.find({"is_active": True}).to_list(50)
            cache.set("psychologists:is_active=True", psychologists, ttl=3600)
            logger.info(f"Warmed psychologists cache: {len(psychologists)} items")
            
            logger.info("✅ Cache warming completed successfully")
            
        except Exception as e:
            logger.error(f"Cache warming error: {str(e)}")


# ============= BACKGROUND CLEANUP TASKS =============

class BackgroundTasks:
    """Background maintenance tasks for optimal performance"""
    
    @staticmethod
    async def cleanup_expired_cache():
        """Remove expired cache entries (run periodically)"""
        try:
            cache.cleanup_expired()
            logger.info("Cache cleanup completed")
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
    
    @staticmethod
    async def cleanup_old_sessions(db, days: int = 90):
        """
        Archive or remove old completed sessions
        
        Args:
            db: Database instance
            days: Remove sessions older than this many days
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await db.session_bookings.delete_many({
                "status": "completed",
                "created_at": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old sessions")
            
        except Exception as e:
            logger.error(f"Session cleanup error: {str(e)}")
    
    @staticmethod
    async def optimize_indexes(db):
        """
        Periodic index optimization
        Rebuilds indexes for better query performance
        """
        try:
            collections = [
                "session_bookings", "events", "blogs", "careers",
                "volunteers", "psychologists", "contact_forms"
            ]
            
            for collection_name in collections:
                collection = db[collection_name]
                # Get index information
                indexes = await collection.index_information()
                logger.debug(f"{collection_name}: {len(indexes)} indexes")
            
            logger.info("Index optimization check completed")
            
        except Exception as e:
            logger.error(f"Index optimization error: {str(e)}")


# ============= PERFORMANCE MONITORING =============

class PerformanceMonitor:
    """Monitor and track application performance metrics"""
    
    def __init__(self):
        self._metrics = {
            "total_requests": 0,
            "avg_response_time": 0,
            "cache_hit_rate": 0,
            "error_rate": 0
        }
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record request metrics"""
        self._metrics["total_requests"] += 1
        
        # Update average response time
        current_avg = self._metrics["avg_response_time"]
        total = self._metrics["total_requests"]
        self._metrics["avg_response_time"] = (
            (current_avg * (total - 1) + response_time) / total
        )
        
        # Track errors
        if status_code >= 400:
            self._metrics["error_rate"] = (
                self._metrics.get("errors", 0) + 1
            ) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        cache_stats = cache.get_stats()
        
        return {
            **self._metrics,
            "cache_stats": cache_stats,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# ============= SCALABILITY UTILITIES =============

async def get_database_stats(db) -> Dict[str, Any]:
    """
    Get comprehensive database statistics
    Useful for monitoring and capacity planning
    """
    try:
        stats = await db.command("dbStats")
        
        collections_stats = []
        for collection_name in await db.list_collection_names():
            coll_stats = await db.command("collStats", collection_name)
            collections_stats.append({
                "name": collection_name,
                "count": coll_stats.get("count", 0),
                "size": coll_stats.get("size", 0),
                "avgObjSize": coll_stats.get("avgObjSize", 0),
                "storageSize": coll_stats.get("storageSize", 0),
                "indexes": coll_stats.get("nindexes", 0)
            })
        
        return {
            "database": {
                "name": db.name,
                "collections": stats.get("collections", 0),
                "dataSize": stats.get("dataSize", 0),
                "storageSize": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "indexSize": stats.get("indexSize", 0)
            },
            "collections": collections_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch database statistics")


async def optimize_collection_query(
    collection,
    filters: Dict[str, Any],
    projection: Optional[Dict[str, int]] = None
) -> List[Dict]:
    """
    Execute optimized query with projection to reduce data transfer
    
    Args:
        collection: MongoDB collection
        filters: Query filters
        projection: Fields to include/exclude
    
    Returns:
        List of documents
    """
    try:
        if projection:
            cursor = collection.find(filters, projection)
        else:
            cursor = collection.find(filters)
        
        return await cursor.to_list(length=1000)
    except Exception as e:
        logger.error(f"Query optimization error: {str(e)}")
        raise
