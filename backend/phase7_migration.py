"""
Phase 7.1 Migration Script

This script adds soft delete fields and security enhancements to the database:
1. Add soft delete fields (is_deleted, deleted_at, deleted_by) to all collections
2. Add password rotation fields to admin users
3. Add 2FA fields to admin users
4. Create feature toggles collection
5. Create approval requests collection
6. Create admin notes collection
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


async def add_soft_delete_fields():
    """Add soft delete fields to all entity collections"""
    collections = [
        "session_bookings",
        "events",
        "event_registrations",
        "blogs",
        "careers",
        "career_applications",
        "volunteers",
        "psychologists",
        "contact_forms"
    ]
    
    print("\n📦 Adding soft delete fields to collections...")
    
    for collection_name in collections:
        collection = db[collection_name]
        
        # Add soft delete fields to documents that don't have them
        result = await collection.update_many(
            {"is_deleted": {"$exists": False}},
            {
                "$set": {
                    "is_deleted": False,
                    "deleted_at": None,
                    "deleted_by": None
                }
            }
        )
        
        print(f"  ✅ {collection_name}: Updated {result.modified_count} documents")
    
    print("✅ Soft delete fields added successfully!\n")


async def update_admin_security_fields():
    """Add password rotation and 2FA fields to admin users"""
    print("🔐 Adding security fields to admin users...")
    
    # Add password_changed_at, two_factor_enabled, two_factor_secret to admins
    result = await db.admins.update_many(
        {"password_changed_at": {"$exists": False}},
        {
            "$set": {
                "password_changed_at": datetime.utcnow(),
                "two_factor_enabled": False,
                "two_factor_secret": ""
            }
        }
    )
    
    print(f"  ✅ Updated {result.modified_count} admin accounts with security fields")
    print("✅ Admin security fields added successfully!\n")


async def create_feature_toggles():
    """Create default feature toggles"""
    print("🎛️  Creating default feature toggles...")
    
    default_features = [
        {
            "id": "feat-session-booking",
            "feature_name": "session_booking",
            "description": "Enable/disable session booking functionality",
            "is_enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-event-registration",
            "feature_name": "event_registration",
            "description": "Enable/disable event registration functionality",
            "is_enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-volunteer-application",
            "feature_name": "volunteer_application",
            "description": "Enable/disable volunteer application functionality",
            "is_enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-contact-form",
            "feature_name": "contact_form",
            "description": "Enable/disable contact form functionality",
            "is_enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-career-applications",
            "feature_name": "career_applications",
            "description": "Enable/disable career application functionality",
            "is_enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-blog-comments",
            "feature_name": "blog_comments",
            "description": "Enable/disable blog comments (future feature)",
            "is_enabled": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-payment-processing",
            "feature_name": "payment_processing",
            "description": "Enable/disable payment processing",
            "is_enabled": False,  # Currently mock
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        },
        {
            "id": "feat-2fa-enforcement",
            "feature_name": "2fa_enforcement",
            "description": "Require 2FA for all admin users",
            "is_enabled": False,  # Mock for now
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "updated_by": "system"
        }
    ]
    
    # Insert feature toggles if they don't exist
    for feature in default_features:
        existing = await db.feature_toggles.find_one({"feature_name": feature["feature_name"]})
        if not existing:
            await db.feature_toggles.insert_one(feature)
            print(f"  ✅ Created feature toggle: {feature['feature_name']}")
        else:
            print(f"  ⏭️  Feature toggle already exists: {feature['feature_name']}")
    
    print("✅ Feature toggles created successfully!\n")


async def create_indexes_for_new_collections():
    """Create indexes for new Phase 7 collections"""
    print("📊 Creating indexes for Phase 7 collections...")
    
    # Approval requests indexes
    await db.approval_requests.create_index("id", unique=True)
    await db.approval_requests.create_index("requester_id")
    await db.approval_requests.create_index("status")
    await db.approval_requests.create_index("created_at")
    print("  ✅ Indexes created for approval_requests")
    
    # Feature toggles indexes
    await db.feature_toggles.create_index("feature_name", unique=True)
    await db.feature_toggles.create_index("is_enabled")
    print("  ✅ Indexes created for feature_toggles")
    
    # Admin notes indexes
    await db.admin_notes.create_index("id", unique=True)
    await db.admin_notes.create_index([("entity", 1), ("entity_id", 1)])
    await db.admin_notes.create_index("admin_id")
    await db.admin_notes.create_index("created_at")
    print("  ✅ Indexes created for admin_notes")
    
    # Add indexes for soft delete filtering
    collections = [
        "session_bookings", "events", "event_registrations", "blogs",
        "careers", "career_applications", "volunteers", "psychologists",
        "contact_forms"
    ]
    
    for collection_name in collections:
        await db[collection_name].create_index("is_deleted")
        await db[collection_name].create_index("deleted_at")
    
    print("  ✅ Soft delete indexes created for all collections")
    print("✅ All Phase 7 indexes created successfully!\n")


async def run_migration():
    """Run all migration steps"""
    print("\n" + "="*60)
    print("🚀 PHASE 7.1 MIGRATION STARTING")
    print("="*60 + "\n")
    
    try:
        # Step 1: Add soft delete fields
        await add_soft_delete_fields()
        
        # Step 2: Update admin security fields
        await update_admin_security_fields()
        
        # Step 3: Create feature toggles
        await create_feature_toggles()
        
        # Step 4: Create indexes
        await create_indexes_for_new_collections()
        
        print("\n" + "="*60)
        print("✅ PHASE 7.1 MIGRATION COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
        print("📋 Summary:")
        print("  ✅ Soft delete fields added to all collections")
        print("  ✅ Admin security fields (password rotation, 2FA) added")
        print("  ✅ Feature toggles created")
        print("  ✅ Indexes created for new collections")
        print("\n🎉 Your A-Cube platform is now Phase 7.1 ready!\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
