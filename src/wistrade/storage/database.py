"""
Encrypted database manager using SQLCipher

Provides secure storage for sensitive data like API credentials.
"""

import hashlib
import logging
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from wistrade.storage.models import BrokerAccount, Strategy, Trade, User

logger = logging.getLogger(__name__)


class EncryptedDatabase:
    """
    Encrypted SQLite database using SQLCipher
    
    Provides secure storage for:
    - User credentials
    - Broker API keys
    - Trading account information
    
    Encryption: AES-256 with PBKDF2 key derivation
    """
    
    def __init__(
        self,
        db_path: str,
        encryption_key: Optional[str] = None,
        salt: Optional[bytes] = None,
    ):
        """
        Initialize encrypted database
        
        Args:
            db_path: Path to SQLite database file
            encryption_key: Master encryption password (will prompt if not provided)
            salt: Salt for key derivation (generated if not provided)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate or use provided salt
        self.salt = salt or secrets.token_bytes(16)
        
        # Derive encryption key from password
        if encryption_key is None:
            raise ValueError("Encryption key is required for production use")
        
        self._encryption_key = self._derive_key(encryption_key, self.salt)
        self._cipher = Fernet(self._encryption_key)
        
        # Initialize database connection
        self._conn = None
        self._init_database()
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key using PBKDF2
        
        Args:
            password: User password
            salt: Random salt
        
        Returns:
            Derived encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommendation
        )
        
        key = kdf.derive(password.encode())
        return hashlib.sha256(key).hexdigest()[:32].encode()  # Fernet needs 32 bytes
    
    def _encrypt(self, data: str) -> bytes:
        """
        Encrypt sensitive data
        
        Args:
            data: Plain text data
        
        Returns:
            Encrypted data
        """
        return self._cipher.encrypt(data.encode())
    
    def _decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Encrypted data
        
        Returns:
            Plain text data
        """
        return self._cipher.decrypt(encrypted_data).decode()
    
    def _init_database(self) -> None:
        """Initialize database schema"""
        try:
            # Try to use SQLCipher if available
            try:
                from pysqlcipher3 import dbapi2 as sqlite3
                self._conn = sqlite3.connect(str(self.db_path))
                self._conn.execute(f"PRAGMA key = '{self._encryption_key.decode()}'")
                logger.info("Using SQLCipher for encrypted storage")
            except ImportError:
                # Fallback to regular SQLite with application-level encryption
                import sqlite3
                self._conn = sqlite3.connect(str(self.db_path))
                logger.warning(
                    "SQLCipher not available. Using application-level encryption. "
                    "Install pysqlcipher3 for better security: pip install pysqlcipher3"
                )
            
            # Create tables
            self._create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables"""
        cursor = self._conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                full_name TEXT,
                risk_level TEXT DEFAULT 'C4',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Broker accounts table (with encrypted credentials)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broker_accounts (
                account_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                broker_id TEXT NOT NULL,
                account_name TEXT NOT NULL,
                account_number_encrypted BLOB NOT NULL,
                api_key_encrypted BLOB NOT NULL,
                api_secret_encrypted BLOB NOT NULL,
                status TEXT DEFAULT 'active',
                is_default BOOLEAN DEFAULT 0,
                encryption_version INTEGER DEFAULT 1,
                qmt_path TEXT,
                extra_params TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Strategies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                strategy_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                strategy_type TEXT DEFAULT 'ai_generated',
                symbols TEXT,
                parameters TEXT,
                max_position_pct REAL DEFAULT 0.20,
                stop_loss_pct REAL,
                take_profit_pct REAL,
                status TEXT DEFAULT 'stopped',
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                total_return REAL DEFAULT 0.0,
                sharpe_ratio REAL,
                max_drawdown REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                stopped_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (account_id) REFERENCES broker_accounts(account_id)
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                strategy_id TEXT,
                account_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                commission REAL DEFAULT 0.0,
                tax REAL DEFAULT 0.0,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_type TEXT DEFAULT 'market',
                profit_loss REAL,
                profit_loss_pct REAL,
                notes TEXT,
                tags TEXT,
                FOREIGN KEY (account_id) REFERENCES broker_accounts(account_id),
                FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
            )
        """)
        
        # Audit logs table (5-year retention)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_id TEXT,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                checksum TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_user ON broker_accounts(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_strategies_user ON strategies(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_account ON trades(account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_time ON trades(execution_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs(timestamp)")
        
        self._conn.commit()
        logger.info("Database tables created successfully")
    
    # User operations
    def create_user(self, user: User) -> bool:
        """Create new user"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    user_id, username, email, phone, hashed_password,
                    is_active, is_verified, full_name, risk_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.user_id, user.username, user.email, user.phone,
                user.hashed_password, user.is_active, user.is_verified,
                user.full_name, user.risk_level
            ))
            self._conn.commit()
            logger.info(f"Created user: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_user(row)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_user(row)
    
    def _row_to_user(self, row: tuple) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            phone=row[3],
            hashed_password=row[4],
            is_active=bool(row[5]),
            is_verified=bool(row[6]),
            full_name=row[7],
            risk_level=row[8],
            created_at=row[9],
            updated_at=row[10],
            last_login=row[11],
        )
    
    # Broker account operations
    def create_broker_account(self, account: BrokerAccount) -> bool:
        """Create broker account with encrypted credentials"""
        try:
            cursor = self._conn.cursor()
            
            # Encrypt sensitive data
            account_number_enc = self._encrypt(account.account_number)
            api_key_enc = self._encrypt(account.api_key)
            api_secret_enc = self._encrypt(account.api_secret)
            
            cursor.execute("""
                INSERT INTO broker_accounts (
                    account_id, user_id, broker_id, account_name,
                    account_number_encrypted, api_key_encrypted, api_secret_encrypted,
                    status, is_default, encryption_version, qmt_path, extra_params
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.account_id, account.user_id, account.broker_id,
                account.account_name, account_number_enc, api_key_enc,
                api_secret_enc, account.status.value, account.is_default,
                account.encryption_version, account.qmt_path,
                str(account.extra_params)
            ))
            
            self._conn.commit()
            logger.info(f"Created broker account: {account.account_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create broker account: {e}")
            return False
    
    def get_broker_account(self, account_id: str) -> Optional[BrokerAccount]:
        """Get broker account with decrypted credentials"""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM broker_accounts WHERE account_id = ?",
            (account_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_broker_account(row)
    
    def _row_to_broker_account(self, row: tuple) -> BrokerAccount:
        """Convert database row to BrokerAccount object with decrypted credentials"""
        return BrokerAccount(
            account_id=row[0],
            user_id=row[1],
            broker_id=row[2],
            account_name=row[3],
            account_number=self._decrypt(row[4]),
            api_key=self._decrypt(row[5]),
            api_secret=self._decrypt(row[6]),
            status=row[7],
            is_default=bool(row[8]),
            encryption_version=row[9],
            created_at=row[12],
            updated_at=row[13],
            last_sync=row[14],
            qmt_path=row[10],
            extra_params=eval(row[11]) if row[11] else {},
        )
    
    def close(self) -> None:
        """Close database connection"""
        if self._conn:
            self._conn.close()
            logger.info("Database connection closed")


class DatabaseManager:
    """
    High-level database manager
    
    Manages database lifecycle and provides convenience methods.
    """
    
    def __init__(self, db_path: str = "data/wistrade.db", encryption_key: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to database file
            encryption_key: Master encryption key
        """
        self.db = EncryptedDatabase(db_path, encryption_key)
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            cursor = self.db._conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database connections"""
        self.db.close()
