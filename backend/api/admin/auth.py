from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

from .schemas import AdminLogin, AdminToken, Admin, RefreshToken
from .rate_limits import limiter, AUTH_RATE_LIMIT

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'acube-admin-secret-key-change-in-production-2025')
REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY', 'acube-admin-refresh-secret-key-change-in-production-2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/admin/auth", tags=["Admin Auth"])


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def store_refresh_token(admin_id: str, token: str) -> None:
    """Store refresh token in database"""
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        admin_id=admin_id,
        token=token,
        expires_at=expires_at
    )
    await db.refresh_tokens.insert_one(refresh_token.dict())


async def verify_refresh_token(token: str) -> Optional[str]:
    """Verify refresh token and return admin email"""
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        
        # Check if token is in database and not revoked
        token_doc = await db.refresh_tokens.find_one({
            "token": token,
            "is_revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not token_doc:
            return None
        
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


async def revoke_refresh_token(token: str) -> bool:
    """Revoke a refresh token"""
    result = await db.refresh_tokens.update_one(
        {"token": token},
        {"$set": {"is_revoked": True}}
    )
    return result.modified_count > 0


async def get_admin_by_email(email: str) -> Optional[Admin]:
    """Get admin by email from database"""
    admin_data = await db.admins.find_one({"email": email})
    if admin_data:
        return Admin(**admin_data)
    return None


async def authenticate_admin(email: str, password: str) -> Optional[Admin]:
    """Authenticate admin user"""
    admin = await get_admin_by_email(email)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin


# Dependency to get current admin from JWT token
async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Admin:
    """Validate JWT token and return current admin"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = await get_admin_by_email(email)
    if admin is None:
        raise credentials_exception
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    return admin


# Refresh token endpoint
@auth_router.post("/refresh", response_model=AdminToken)
@limiter.limit(AUTH_RATE_LIMIT)
async def refresh_access_token(request: Request, refresh_token: str):
    """Refresh access token using refresh token"""
    email = await verify_refresh_token(refresh_token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = await get_admin_by_email(email)
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email, "role": admin.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Access token refreshed for: {admin.email}")
    
    return AdminToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
    )


# Logout endpoint
@auth_router.post("/logout")
async def admin_logout(
    refresh_token: str,
    admin: Admin = Depends(get_current_admin)
):
    """Admin logout endpoint - revokes refresh token"""
    await revoke_refresh_token(refresh_token)
    
    # Log logout action
    from .utils import log_admin_action
    await log_admin_action(
        admin_id=admin.id,
        admin_email=admin.email,
        action="logout",
        entity="auth",
        entity_id=admin.id,
        details="Admin logged out"
    )
    
    logger.info(f"Admin logged out: {admin.email}")
    
    return {"message": "Logged out successfully"}


# Login endpoint
@auth_router.post("/login", response_model=AdminToken)
@limiter.limit(AUTH_RATE_LIMIT)
async def admin_login(request: Request, login_data: AdminLogin):
    """Admin login endpoint"""
    admin = await authenticate_admin(login_data.email, login_data.password)
    
    if not admin:
        logger.warning(f"Failed login attempt for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email, "role": admin.role}, 
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data={"sub": admin.email})
    
    # Store refresh token in database
    await store_refresh_token(admin.id, refresh_token)
    
    # Update last login time
    await db.admins.update_one(
        {"id": admin.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Log login action
    from .utils import log_admin_action
    await log_admin_action(
        admin_id=admin.id,
        admin_email=admin.email,
        action="login",
        entity="auth",
        entity_id=admin.id,
        details="Admin logged in successfully"
    )
    
    logger.info(f"Admin logged in successfully: {admin.email}")
    
    return AdminToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
    )


# Verify token endpoint (for frontend to check if token is still valid)
@auth_router.get("/verify")
async def verify_token(admin: Admin = Depends(get_current_admin)):
    """Verify if the current token is valid"""
    return {
        "valid": True,
        "email": admin.email,
        "id": admin.id
    }
