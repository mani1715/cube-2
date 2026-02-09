"""Seed default admin user"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def seed_default_admin():
    """Create default admin if not exists"""
    default_email = "admin@acube.com"
    default_password = "Admin@2025!"
    
    # Check if admin already exists
    existing_admin = await db.admins.find_one({"email": default_email})
    
    if existing_admin:
        print(f"Admin {default_email} already exists. Skipping seed.")
        return
    
    # Create new admin
    hashed_password = hash_password(default_password)
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": default_email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.admins.insert_one(admin_data)
    print(f"✅ Default admin created successfully!")
    print(f"   Email: {default_email}")
    print(f"   Password: {default_password}")
    print(f"   Please change the password after first login.")


if __name__ == "__main__":
    asyncio.run(seed_default_admin())
    client.close()
