import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, EmailStr
import secrets
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import redis
from enum import Enum
import asyncio
import aioredis

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str
    role: UserRole = UserRole.USER
    is_active: bool = True

class UserCreate(UserBase):
    """User creation model."""
    password: str

class User(UserBase):
    """User model with ID."""
    id: int
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    """Token data model."""
    user_id: int
    username: str
    role: UserRole
    token_type: TokenType
    exp: datetime

class AuthConfig(BaseModel):
    """Authentication configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 15
    redis_url: Optional[str] = None
    min_password_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

class AuthService:
    """Advanced authentication service with security features."""
    
    def __init__(self, config: AuthConfig, db_session: Session):
        """Initialize auth service."""
        self.config = config
        self.db = db_session
        self._redis_client: Optional[redis.Redis] = None
        self._async_redis_client: Optional[aioredis.Redis] = None
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self._initialize_redis()

    def _initialize_redis(self) -> None:
        """Initialize Redis connection for token blacklisting and rate limiting."""
        if self.config.redis_url:
            try:
                self._redis_client = redis.from_url(self.config.redis_url)
                logger.info("Redis initialized for auth service")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")

    async def _initialize_async_redis(self) -> None:
        """Initialize async Redis connection."""
        if self.config.redis_url:
            try:
                self._async_redis_client = await aioredis.from_url(self.config.redis_url)
                logger.info("Async Redis initialized for auth service")
            except Exception as e:
                logger.error(f"Failed to initialize async Redis: {e}")

    def _hash_password(self, password: str) -> bytes:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def verify_password(self, plain_password: str, hashed_password: bytes) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password)

    def create_token(self, user: User, token_type: TokenType) -> str:
        """Create JWT token for user."""
        expires_delta = (
            timedelta(minutes=self.config.access_token_expire_minutes)
            if token_type == TokenType.ACCESS
            else timedelta(days=self.config.refresh_token_expire_days)
        )
        
        expire = datetime.utcnow() + expires_delta
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "type": token_type,
            "exp": expire
        }
        
        token = jwt.encode(
            token_data,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )
        
        return token

    async def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )
            
            # Check if token is blacklisted
            if await self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=401,
                    detail="Token has been revoked"
                )
            
            return TokenData(
                user_id=int(payload["sub"]),
                username=payload["username"],
                role=UserRole(payload["role"]),
                token_type=TokenType(payload["type"]),
                exp=datetime.fromtimestamp(payload["exp"])
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate token"
            )

    async def blacklist_token(self, token: str, expire_in: int) -> None:
        """Add token to blacklist."""
        if self._async_redis_client:
            await self._async_redis_client.setex(
                f"blacklist:{token}",
                expire_in,
                "1"
            )

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        if self._async_redis_client:
            return bool(await self._async_redis_client.get(f"blacklist:{token}"))
        return False

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user and manage login attempts."""
        # Check login attempts
        attempts_key = f"login_attempts:{username}"
        
        if self._redis_client:
            attempts = int(self._redis_client.get(attempts_key) or 0)
            if attempts >= self.config.max_login_attempts:
                raise HTTPException(
                    status_code=429,
                    detail="Too many login attempts. Try again later."
                )
        
        # Get user from database
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user or not self.verify_password(password, user.password):
            # Increment failed attempts
            if self._redis_client:
                self._redis_client.incr(attempts_key)
                self._redis_client.expire(
                    attempts_key,
                    self.config.lockout_duration_minutes * 60
                )
            return None
        
        # Reset login attempts on successful login
        if self._redis_client:
            self._redis_client.delete(attempts_key)
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user

    def create_user(self, user_data: UserCreate) -> User:
        """Create new user with password validation."""
        # Validate password strength
        if len(user_data.password) < self.config.min_password_length:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {self.config.min_password_length} characters"
            )
        
        # Check if user exists
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = self._hash_password(user_data.password)
        user = User(
            **user_data.dict(exclude={'password'}),
            password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    async def get_current_user(
        self,
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))
    ) -> User:
        """Get current user from token."""
        token_data = await self.verify_token(token)
        user = self.db.query(User).filter(User.id == token_data.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail="User is inactive"
            )
        
        return user

    def generate_password_reset_token(self, email: str) -> str:
        """Generate password reset token."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        token = secrets.token_urlsafe(32)
        expire = datetime.utcnow() + timedelta(
            minutes=self.config.password_reset_token_expire_minutes
        )
        
        if self._redis_client:
            self._redis_client.setex(
                f"reset_token:{token}",
                self.config.password_reset_token_expire_minutes * 60,
                str(user.id)
            )
        
        return token

    async def reset_password(
        self,
        token: str,
        new_password: str
    ) -> bool:
        """Reset user password using reset token."""
        if not self._redis_client:
            raise HTTPException(
                status_code=500,
                detail="Password reset service unavailable"
            )
        
        user_id = self._redis_client.get(f"reset_token:{token}")
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token"
            )
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Update password
        user.password = self._hash_password(new_password)
        self.db.commit()
        
        # Delete reset token
        self._redis_client.delete(f"reset_token:{token}")
        
        return True

    def require_role(self, required_role: UserRole):
        """Decorator to require specific role for access."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                user = await self.get_current_user()
                if user.role != required_role:
                    raise HTTPException(
                        status_code=403,
                        detail="Insufficient permissions"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def __del__(self):
        """Cleanup Redis connections."""
        if self._redis_client:
            self._redis_client.close()
        if self._async_redis_client:
            asyncio.create_task(self._async_redis_client.close())