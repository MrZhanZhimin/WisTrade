"""
Unit tests for user authentication
"""

import pytest
from datetime import datetime

from wistrade.core.auth import AuthManager, UserRegistration, UserLogin
from wistrade.storage.database import EncryptedDatabase


class TestAuthManager:
    """Test authentication manager"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database for testing"""
        db_path = tmp_path / "test.db"
        return EncryptedDatabase(
            db_path=str(db_path),
            encryption_key="test_encryption_key_for_testing_only"
        )
    
    @pytest.fixture
    def auth_manager(self, db):
        """Create authentication manager"""
        return AuthManager(db)
    
    def test_password_hashing(self, auth_manager):
        """Test password hashing"""
        password = "TestPassword123"
        hashed = auth_manager.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith('$2b$')  # bcrypt prefix
    
    def test_password_verification(self, auth_manager):
        """Test password verification"""
        password = "TestPassword123"
        hashed = auth_manager.hash_password(password)
        
        assert auth_manager.verify_password(password, hashed) is True
        assert auth_manager.verify_password("WrongPassword", hashed) is False
    
    def test_session_token_generation(self, auth_manager):
        """Test session token generation"""
        token1 = auth_manager.generate_session_token()
        token2 = auth_manager.generate_session_token()
        
        assert len(token1) > 0
        assert token1 != token2  # Should be unique
    
    def test_user_registration(self, auth_manager):
        """Test user registration"""
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            phone="13800138000",
        )
        
        user = auth_manager.register_user(registration)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_user_registration_duplicate_username(self, auth_manager):
        """Test registration with duplicate username"""
        registration = UserRegistration(
            username="testuser",
            email="test1@example.com",
            password="TestPassword123",
        )
        
        auth_manager.register_user(registration)
        
        # Try to register with same username
        registration2 = UserRegistration(
            username="testuser",
            email="test2@example.com",
            password="TestPassword456",
        )
        
        with pytest.raises(ValueError, match="already exists"):
            auth_manager.register_user(registration2)
    
    def test_user_login_success(self, auth_manager):
        """Test successful user login"""
        # Register user first
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )
        auth_manager.register_user(registration)
        
        # Login
        credentials = UserLogin(
            username="testuser",
            password="TestPassword123",
        )
        
        session = auth_manager.login(credentials)
        
        assert session.token is not None
        assert session.username == "testuser"
        assert session.expires_at > datetime.now()
    
    def test_user_login_wrong_password(self, auth_manager):
        """Test login with wrong password"""
        # Register user
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )
        auth_manager.register_user(registration)
        
        # Try to login with wrong password
        credentials = UserLogin(
            username="testuser",
            password="WrongPassword123",
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_manager.login(credentials)
    
    def test_user_login_nonexistent_user(self, auth_manager):
        """Test login with nonexistent user"""
        credentials = UserLogin(
            username="nonexistent",
            password="TestPassword123",
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_manager.login(credentials)
    
    def test_session_validation(self, auth_manager):
        """Test session validation"""
        # Register and login
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )
        auth_manager.register_user(registration)
        
        credentials = UserLogin(
            username="testuser",
            password="TestPassword123",
        )
        session = auth_manager.login(credentials)
        
        # Validate session
        validated = auth_manager.validate_session(session.token)
        
        assert validated is not None
        assert validated.user_id == session.user_id
    
    def test_session_logout(self, auth_manager):
        """Test session logout"""
        # Register and login
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )
        auth_manager.register_user(registration)
        
        credentials = UserLogin(
            username="testuser",
            password="TestPassword123",
        )
        session = auth_manager.login(credentials)
        
        # Logout
        auth_manager.logout(session.token)
        
        # Try to validate session - should fail
        validated = auth_manager.validate_session(session.token)
        
        assert validated is None


class TestUserRegistration:
    """Test user registration validation"""
    
    def test_valid_registration(self):
        """Test valid registration data"""
        registration = UserRegistration(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )
        
        assert registration.username == "testuser"
        assert registration.email == "test@example.com"
    
    def test_invalid_username_too_short(self):
        """Test username too short"""
        with pytest.raises(ValueError, match="3 and 50 characters"):
            UserRegistration(
                username="ab",
                email="test@example.com",
                password="TestPassword123",
            )
    
    def test_invalid_username_non_alphanumeric(self):
        """Test username with special characters"""
        with pytest.raises(ValueError, match="letters and numbers"):
            UserRegistration(
                username="test-user",
                email="test@example.com",
                password="TestPassword123",
            )
    
    def test_invalid_password_too_short(self):
        """Test password too short"""
        with pytest.raises(ValueError, match="at least 8 characters"):
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="Pass1",
            )
    
    def test_invalid_password_no_uppercase(self):
        """Test password without uppercase"""
        with pytest.raises(ValueError, match="uppercase letter"):
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="testpassword123",
            )
    
    def test_invalid_password_no_lowercase(self):
        """Test password without lowercase"""
        with pytest.raises(ValueError, match="lowercase letter"):
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="TESTPASSWORD123",
            )
    
    def test_invalid_password_no_digit(self):
        """Test password without digit"""
        with pytest.raises(ValueError, match="at least one digit"):
            UserRegistration(
                username="testuser",
                email="test@example.com",
                password="TestPassword",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
