"""Rate limiting configuration and utilities."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# ============= RATE LIMIT CONFIGURATIONS =============

# Public API endpoints - stricter limits
PUBLIC_RATE_LIMIT = "10/minute"  # 10 requests per minute
PUBLIC_BURST_LIMIT = "30/hour"   # 30 requests per hour

# Admin API endpoints - more permissive
ADMIN_RATE_LIMIT = "60/minute"    # 60 requests per minute
ADMIN_BURST_LIMIT = "1000/hour"   # 1000 requests per hour

# Authentication endpoints - very strict to prevent brute force
AUTH_RATE_LIMIT = "5/minute"      # 5 login attempts per minute
AUTH_BURST_LIMIT = "20/hour"      # 20 login attempts per hour

# File upload endpoints - moderate limits
UPLOAD_RATE_LIMIT = "10/minute"   # 10 uploads per minute
UPLOAD_BURST_LIMIT = "50/hour"    # 50 uploads per hour

# Export endpoints - conservative limits (resource-intensive)
EXPORT_RATE_LIMIT = "5/minute"    # 5 exports per minute
EXPORT_BURST_LIMIT = "20/hour"    # 20 exports per hour


# ============= HELPER FUNCTIONS =============

def get_rate_limit_key(request: Request) -> str:
    """Generate rate limit key based on IP address."""
    # In production, could use authenticated user ID for better tracking
    return get_remote_address(request)


def log_rate_limit_exceeded(request: Request, limit: str):
    """Log when rate limit is exceeded."""
    ip = get_remote_address(request)
    path = request.url.path
    logger.warning(f"Rate limit exceeded: {ip} -> {path} (limit: {limit})")


# ============= CUSTOM RATE LIMIT DECORATORS =============

def public_rate_limit():
    """Decorator for public API endpoints."""
    return limiter.limit(PUBLIC_RATE_LIMIT)


def admin_rate_limit():
    """Decorator for admin API endpoints."""
    return limiter.limit(ADMIN_RATE_LIMIT)


def auth_rate_limit():
    """Decorator for authentication endpoints."""
    return limiter.limit(AUTH_RATE_LIMIT)


def upload_rate_limit():
    """Decorator for file upload endpoints."""
    return limiter.limit(UPLOAD_RATE_LIMIT)


def export_rate_limit():
    """Decorator for export endpoints."""
    return limiter.limit(EXPORT_RATE_LIMIT)
