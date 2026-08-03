"""
NFM-X Authentication Middleware
JWT-based authentication for API endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from datetime import datetime, timezone, timedelta
import jwt
import os

from backend.app.config import settings

logger = logging.getLogger(__name__)

# Security schemes
bearer_scheme = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for NFM-X API"""
    
    def __init__(self):
        self.secret_key = settings.secret_key or os.getenv("NFM_SECRET_KEY", "change-this-in-production")
        self.algorithm = "HS256"
        self.token_expire_minutes = 30
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
        """Get the current user from JWT token"""
        try:
            token = credentials.credentials
            payload = self.verify_token(token)
            return payload
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )


# Global instance
auth_middleware = AuthMiddleware()


# Dependency for required authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Dependency for required authentication"""
    return await auth_middleware.get_current_user(credentials)


# Dependency for optional authentication
async def get_optional_user(request: Request) -> Optional[dict]:
    """Dependency for optional authentication"""
    try:
        if request.headers.get("Authorization"):
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]
                return auth_middleware.verify_token(token)
    except Exception:
        pass
    return None