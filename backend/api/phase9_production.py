"""Phase 9.1 - Production Launch & Deployment Endpoints"""
from fastapi import APIRouter, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
try:
    import pkg_resources
except ImportError:
    # pkg_resources is part of setuptools
    from importlib import metadata as pkg_resources

logger = logging.getLogger(__name__)

phase9_prod_router = APIRouter(
    prefix="/api/phase9/production",
    tags=["Phase 9.1 - Production"]
)


@phase9_prod_router.get("/health")
async def health_check_detailed() -> Dict[str, Any]:
    """
    Detailed health check endpoint for production monitoring.
    Returns comprehensive system status.
    """
    try:
        # MongoDB connection
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db_name = os.environ.get('DB_NAME')
        db = client[db_name]
        
        # Test MongoDB connection
        try:
            await db.command('ping')
            db_status = "healthy"
            db_message = "MongoDB connection successful"
        except Exception as e:
            db_status = "unhealthy"
            db_message = f"MongoDB connection failed: {str(e)}"
        finally:
            client.close()
        
        # System info
        health_data = {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "A-Cube Mental Health Platform",
            "version": "1.0.0",
            "environment": os.environ.get('ENVIRONMENT', 'production'),
            "components": {
                "api": {
                    "status": "healthy",
                    "message": "API is operational"
                },
                "database": {
                    "status": db_status,
                    "message": db_message,
                    "type": "MongoDB"
                }
            },
            "system": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform
            }
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@phase9_prod_router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe for Kubernetes/container orchestration.
    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check MongoDB connection
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db_name = os.environ.get('DB_NAME')
        db = client[db_name]
        
        await db.command('ping')
        client.close()
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@phase9_prod_router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe for Kubernetes/container orchestration.
    Returns 200 if service is alive.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@phase9_prod_router.get("/environment")
async def environment_info() -> Dict[str, Any]:
    """
    Get environment configuration info (non-sensitive data only).
    """
    return {
        "environment": os.environ.get('ENVIRONMENT', 'production'),
        "database_configured": bool(os.environ.get('MONGO_URL')),
        "cors_origins": os.environ.get('CORS_ORIGINS', '*'),
        "features": {
            "ai_enabled": bool(os.environ.get('EMERGENT_LLM_KEY')),
            "rate_limiting": True,
            "background_jobs": True,
            "audit_logging": True
        }
    }


@phase9_prod_router.get("/metrics")
async def basic_metrics() -> Dict[str, Any]:
    """
    Basic application metrics for monitoring.
    """
    try:
        mongo_url = os.environ.get('MONGO_URL')
        client = AsyncIOMotorClient(mongo_url)
        db_name = os.environ.get('DB_NAME')
        db = client[db_name]
        
        # Get collection counts
        collections_stats = {}
        collections = ['session_bookings', 'events', 'blogs', 'careers', 
                      'volunteers', 'psychologists', 'contact_forms', 'admins']
        
        for collection in collections:
            try:
                count = await db[collection].count_documents({})
                collections_stats[collection] = count
            except:
                collections_stats[collection] = 0
        
        client.close()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "collections": collections_stats,
            "uptime": "healthy"
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect metrics"
        )
