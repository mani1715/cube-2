"""
PHASE 12.3 - User Authentication & Account Management
Separate from admin authentication - for public users
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from passlib.context import CryptContext
import jwt

# Logger setup
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client[DB_NAME]

# JWT Configuration
JWT_SECRET_USER = os.environ.get("JWT_SECRET_USER", "supersecret_user_jwt_key_change_in_production")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
USER_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("USER_ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours
USER_REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("USER_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Router
phase12_users_router = APIRouter(prefix="/api/phase12/users", tags=["Phase 12 - User Auth"])

# Pydantic Models
class UserSignupRequest(BaseModel):
    """User signup request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=2)
    phone: Optional[str] = None


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    name: Optional[str] = None
    phone: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str = Field(..., min_length=8)


# ==================== UTILITY FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=USER_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_USER, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=USER_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_USER, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_USER, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Fetch user from database
    user = db.users.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    return user


# ==================== AUTHENTICATION ENDPOINTS ====================

@phase12_users_router.post("/signup")
async def user_signup(signup_request: UserSignupRequest):
    """
    Register a new user account
    """
    try:
        # Check if email already exists
        existing_user = db.users.find_one({"email": signup_request.email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(signup_request.password)
        
        user = {
            "user_id": user_id,
            "email": signup_request.email.lower(),
            "password": hashed_password,
            "name": signup_request.name,
            "phone": signup_request.phone,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        db.users.insert_one(user)
        
        # Create tokens
        access_token = create_access_token(data={"user_id": user_id, "email": signup_request.email.lower()})
        refresh_token = create_refresh_token(data={"user_id": user_id})
        
        # Store refresh token
        db.user_refresh_tokens.insert_one({
            "token_id": str(uuid.uuid4()),
            "user_id": user_id,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=USER_REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        })
        
        logger.info(f"New user registered: {signup_request.email}")
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != "password"}
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed"
        )


@phase12_users_router.post("/login")
async def user_login(login_request: UserLoginRequest):
    """
    Login user and return access token
    """
    try:
        # Find user
        user = db.users.find_one({"email": login_request.email.lower()})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_request.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create tokens
        access_token = create_access_token(data={"user_id": user["user_id"], "email": user["email"]})
        refresh_token = create_refresh_token(data={"user_id": user["user_id"]})
        
        # Store refresh token
        db.user_refresh_tokens.insert_one({
            "token_id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=USER_REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        })
        
        # Update last login
        db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": datetime.utcnow().isoformat()}}
        )
        
        logger.info(f"User logged in: {login_request.email}")
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k not in ["password", "_id"]}
        
        return {
            "success": True,
            "message": "Login successful",
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@phase12_users_router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("user_id")
        
        # Verify refresh token exists in database
        token_doc = db.user_refresh_tokens.find_one({
            "user_id": user_id,
            "refresh_token": refresh_token
        })
        
        if not token_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.users.find_one({"user_id": user_id}, {"_id": 0})
        
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"user_id": user_id, "email": user["email"]})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@phase12_users_router.post("/logout")
async def user_logout(
    refresh_token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user by revoking refresh token
    """
    try:
        # Delete refresh token
        db.user_refresh_tokens.delete_one({
            "user_id": current_user["user_id"],
            "refresh_token": refresh_token
        })
        
        logger.info(f"User logged out: {current_user['email']}")
        
        return {
            "success": True,
            "message": "Logout successful"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# ==================== USER PROFILE ENDPOINTS ====================

@phase12_users_router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    return {
        "success": True,
        "user": current_user
    }


@phase12_users_router.put("/profile")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile
    """
    try:
        update_data = {}
        if profile_update.name:
            update_data["name"] = profile_update.name
        if profile_update.phone is not None:
            update_data["phone"] = profile_update.phone
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            db.users.update_one(
                {"user_id": current_user["user_id"]},
                {"$set": update_data}
            )
            
            # Fetch updated user
            updated_user = db.users.find_one(
                {"user_id": current_user["user_id"]},
                {"_id": 0, "password": 0}
            )
            
            return {
                "success": True,
                "message": "Profile updated successfully",
                "user": updated_user
            }
        
        return {
            "success": True,
            "message": "No changes made",
            "user": current_user
        }
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@phase12_users_router.post("/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    """
    try:
        # Get user with password
        user = db.users.find_one({"user_id": current_user["user_id"]})
        
        # Verify old password
        if not verify_password(password_change.old_password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = hash_password(password_change.new_password)
        
        # Update password
        db.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "password": new_hashed_password,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Revoke all refresh tokens for security
        db.user_refresh_tokens.delete_many({"user_id": current_user["user_id"]})
        
        logger.info(f"Password changed for user: {current_user['email']}")
        
        return {
            "success": True,
            "message": "Password changed successfully. Please login again."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@phase12_users_router.delete("/account")
async def delete_user_account(
    password: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete user account (soft delete)
    """
    try:
        # Get user with password
        user = db.users.find_one({"user_id": current_user["user_id"]})
        
        # Verify password
        if not verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )
        
        # Soft delete - mark as inactive
        db.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "is_active": False,
                    "deleted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Revoke all refresh tokens
        db.user_refresh_tokens.delete_many({"user_id": current_user["user_id"]})
        
        logger.info(f"Account deleted for user: {current_user['email']}")
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )
