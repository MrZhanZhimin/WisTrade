"""
User authentication and authorization module
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from pydantic import BaseModel, EmailStr, validator

from wistrade.storage.database import EncryptedDatabase
from wistrade.storage.models import User
from wistrade.core.logger import get_logger

logger = get_logger(__name__)


class UserRegistration(BaseModel):
    """User registration data"""
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login credentials"""
    username: str
    password: str


class SessionToken(BaseModel):
    """Session token data"""
    token: str
    user_id: str
    username: str
    expires_at: datetime
    created_at: datetime = datetime.now()


class AuthManager:
    """
    Authentication manager for user accounts
    
    Handles user registration, login, session management.
    """
    
    def __init__(self, db: EncryptedDatabase):
        """
        Initialize authentication manager
        
        Args:
            db: Encrypted database instance
        """
        self.db = db
        self._sessions: dict = {}  # In-memory session cache (can be Redis in production)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)  # OWASP recommendation
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
        
        Returns:
            True if password matches
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Generate secure session token
        
        Returns:
            Random session token
        """
        return secrets.token_urlsafe(32)
    
    def register_user(self, registration: UserRegistration) -> User:
        """
        Register new user
        
        Args:
            registration: User registration data
        
        Returns:
            Created user object
        
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        existing = self.db.get_user_by_username(registration.username)
        if existing:
            raise ValueError(f"Username '{registration.username}' already exists")
        
        # Hash password
        hashed_password = self.hash_password(registration.password)
        
        # Generate user ID
        user_id = f"user_{secrets.token_hex(8)}"
        
        # Create user object
        user = User(
            user_id=user_id,
            username=registration.username,
            email=registration.email,
            phone=registration.phone,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            full_name=registration.full_name,
            risk_level="C4",  # Default risk level
        )
        
        # Save to database
        success = self.db.create_user(user)
        if not success:
            raise RuntimeError("Failed to create user in database")
        
        logger.info(
            "user_registered",
            user_id=user_id,
            username=registration.username,
            email=registration.email,
        )
        
        return user
    
    def login(self, credentials: UserLogin) -> SessionToken:
        """
        Authenticate user and create session
        
        Args:
            credentials: Login credentials
        
        Returns:
            Session token
        
        Raises:
            ValueError: If authentication fails
        """
        # Get user by username
        user = self.db.get_user_by_username(credentials.username)
        if not user:
            raise ValueError("Invalid username or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Verify password
        if not self.verify_password(credentials.password, user.hashed_password):
            logger.warning(
                "login_failed_invalid_password",
                username=credentials.username,
            )
            raise ValueError("Invalid username or password")
        
        # Generate session token
        token = self.generate_session_token()
        expires_at = datetime.now() + timedelta(hours=24)  # 24-hour session
        
        # Create session
        session = SessionToken(
            token=token,
            user_id=user.user_id,
            username=user.username,
            expires_at=expires_at,
        )
        
        # Store session in cache
        self._sessions[token] = session
        
        # Update last login time
        # TODO: Update database with last_login timestamp
        
        logger.info(
            "user_logged_in",
            user_id=user.user_id,
            username=user.username,
        )
        
        return session
    
    def logout(self, token: str) -> bool:
        """
        Logout user and invalidate session
        
        Args:
            token: Session token
        
        Returns:
            True if logout successful
        """
        if token in self._sessions:
            session = self._sessions.pop(token)
            logger.info(
                "user_logged_out",
                user_id=session.user_id,
                username=session.username,
            )
            return True
        
        return False
    
    def validate_session(self, token: str) -> Optional[SessionToken]:
        """
        Validate session token
        
        Args:
            token: Session token
        
        Returns:
            Session token data if valid, None otherwise
        """
        session = self._sessions.get(token)
        
        if not session:
            return None
        
        # Check expiration
        if datetime.now() > session.expires_at:
            self._sessions.pop(token, None)
            return None
        
        return session
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User object or None
        """
        return self.db.get_user(user_id)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from cache
        
        Returns:
            Number of sessions removed
        """
        now = datetime.now()
        expired = [
            token for token, session in self._sessions.items()
            if now > session.expires_at
        ]
        
        for token in expired:
            self._sessions.pop(token, None)
        
        if expired:
            logger.info("sessions_cleaned", count=len(expired))
        
        return len(expired)
