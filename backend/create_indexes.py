"""
MongoDB Indexing Script for A-Cube Platform
Creates indexes on frequently queried fields to improve performance
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_indexes():
    """Create indexes on all collections for optimal query performance"""
    
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    logger.info("Starting index creation...")
    
    try:
        # Session Bookings Collection
        logger.info("Creating indexes for session_bookings...")
        await db.session_bookings.create_index("id", unique=True)
        await db.session_bookings.create_index("status")
        await db.session_bookings.create_index([("created_at", -1)])
        await db.session_bookings.create_index("email")
        logger.info("✓ session_bookings indexes created")
        
        # Events Collection
        logger.info("Creating indexes for events...")
        await db.events.create_index("id", unique=True)
        await db.events.create_index("is_active")
        await db.events.create_index([("date", -1)])
        await db.events.create_index([("created_at", -1)])
        logger.info("✓ events indexes created")
        
        # Blogs Collection
        logger.info("Creating indexes for blogs...")
        await db.blogs.create_index("id", unique=True)
        await db.blogs.create_index("is_published")
        await db.blogs.create_index("category")
        await db.blogs.create_index("is_featured")
        await db.blogs.create_index([("created_at", -1)])
        logger.info("✓ blogs indexes created")
        
        # Careers/Jobs Collection
        logger.info("Creating indexes for careers...")
        await db.careers.create_index("id", unique=True)
        await db.careers.create_index("is_active")
        await db.careers.create_index([("created_at", -1)])
        logger.info("✓ careers indexes created")
        
        # Volunteers Collection
        logger.info("Creating indexes for volunteers...")
        await db.volunteers.create_index("id", unique=True)
        await db.volunteers.create_index("status")
        await db.volunteers.create_index([("created_at", -1)])
        await db.volunteers.create_index("email")
        logger.info("✓ volunteers indexes created")
        
        # Psychologists Collection
        logger.info("Creating indexes for psychologists...")
        await db.psychologists.create_index("id", unique=True)
        await db.psychologists.create_index("is_active")
        await db.psychologists.create_index([("created_at", -1)])
        logger.info("✓ psychologists indexes created")
        
        # Contact Forms Collection
        logger.info("Creating indexes for contact_forms...")
        await db.contact_forms.create_index("id", unique=True)
        await db.contact_forms.create_index("status")
        await db.contact_forms.create_index([("created_at", -1)])
        await db.contact_forms.create_index("email")
        logger.info("✓ contact_forms indexes created")
        
        # Admin Collection
        logger.info("Creating indexes for admins...")
        await db.admins.create_index("id", unique=True)
        await db.admins.create_index("email", unique=True)
        await db.admins.create_index("role")
        await db.admins.create_index("is_active")
        logger.info("✓ admins indexes created")
        
        # Admin Logs Collection
        logger.info("Creating indexes for admin_logs...")
        await db.admin_logs.create_index("id", unique=True)
        await db.admin_logs.create_index("admin_id")
        await db.admin_logs.create_index("admin_email")
        await db.admin_logs.create_index("action")
        await db.admin_logs.create_index("entity")
        await db.admin_logs.create_index([("timestamp", -1)])
        # Compound index for common queries
        await db.admin_logs.create_index([("admin_email", 1), ("timestamp", -1)])
        await db.admin_logs.create_index([("entity", 1), ("action", 1)])
        logger.info("✓ admin_logs indexes created")
        
        # Refresh Tokens Collection
        logger.info("Creating indexes for refresh_tokens...")
        await db.refresh_tokens.create_index("id", unique=True)
        await db.refresh_tokens.create_index("admin_id")
        await db.refresh_tokens.create_index("token")
        await db.refresh_tokens.create_index("expires_at")
        await db.refresh_tokens.create_index([("is_revoked", 1), ("expires_at", -1)])
        logger.info("✓ refresh_tokens indexes created")
        
        logger.info("\n✅ All indexes created successfully!")
        
        # List all indexes for verification
        logger.info("\n📊 Index Summary:")
        collections = [
            "session_bookings", "events", "blogs", "careers", "volunteers",
            "psychologists", "contact_forms", "admins", "admin_logs", "refresh_tokens"
        ]
        
        for collection_name in collections:
            indexes = await db[collection_name].list_indexes().to_list(None)
            logger.info(f"  {collection_name}: {len(indexes)} indexes")
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
