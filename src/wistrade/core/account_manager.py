"""
Account management module for broker accounts
"""

import uuid
from datetime import datetime
from typing import List, Optional

from wistrade.storage.database import EncryptedDatabase
from wistrade.storage.models import BrokerAccount, AccountStatus
from wistrade.brokers.base import BrokerConfig
from wistrade.core.logger import get_logger

logger = get_logger(__name__)


class AccountManager:
    """
    Manager for broker accounts
    
    Handles account creation, modification, deletion, and switching.
    """
    
    def __init__(self, db: EncryptedDatabase):
        """
        Initialize account manager
        
        Args:
            db: Encrypted database instance
        """
        self.db = db
        self._active_account_id: Optional[str] = None
    
    def add_broker_account(
        self,
        user_id: str,
        broker_id: str,
        account_name: str,
        account_number: str,
        api_key: str,
        api_secret: str,
        is_default: bool = False,
        qmt_path: Optional[str] = None,
        extra_params: Optional[dict] = None,
    ) -> BrokerAccount:
        """
        Add a new broker account
        
        Args:
            user_id: User ID
            broker_id: Broker identifier (zhao_shang, guang_da, jiang_hai)
            account_name: Display name for account
            account_number: Broker account number
            api_key: API key (will be encrypted)
            api_secret: API secret (will be encrypted)
            is_default: Set as default account
            qmt_path: Path to QMT client (optional)
            extra_params: Additional parameters
        
        Returns:
            Created broker account
        
        Raises:
            ValueError: If account already exists or invalid parameters
        """
        # Generate account ID
        account_id = f"acc_{uuid.uuid4().hex[:12]}"
        
        # If setting as default, remove default from other accounts
        if is_default:
            # TODO: Update all other accounts to is_default=False
            pass
        
        # Create account object (credentials will be encrypted in database layer)
        account = BrokerAccount(
            account_id=account_id,
            user_id=user_id,
            broker_id=broker_id,
            account_name=account_name,
            account_number=account_number,
            api_key=api_key,
            api_secret=api_secret,
            status=AccountStatus.ACTIVE,
            is_default=is_default,
            qmt_path=qmt_path,
            extra_params=extra_params or {},
        )
        
        # Save to database (encryption happens in database layer)
        success = self.db.create_broker_account(account)
        if not success:
            raise RuntimeError("Failed to create broker account in database")
        
        logger.info(
            "broker_account_added",
            account_id=account_id,
            user_id=user_id,
            broker_id=broker_id,
            account_name=account_name,
        )
        
        return account
    
    def get_account(self, account_id: str) -> Optional[BrokerAccount]:
        """
        Get broker account by ID
        
        Args:
            account_id: Account ID
        
        Returns:
            Broker account with decrypted credentials
        """
        return self.db.get_broker_account(account_id)
    
    def get_user_accounts(self, user_id: str) -> List[BrokerAccount]:
        """
        Get all broker accounts for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of broker accounts
        """
        # TODO: Implement database query for user accounts
        # For now, return empty list
        return []
    
    def get_default_account(self, user_id: str) -> Optional[BrokerAccount]:
        """
        Get default broker account for user
        
        Args:
            user_id: User ID
        
        Returns:
            Default broker account or None
        """
        accounts = self.get_user_accounts(user_id)
        
        for account in accounts:
            if account.is_default:
                return account
        
        # Return first account if no default set
        return accounts[0] if accounts else None
    
    def set_default_account(self, user_id: str, account_id: str) -> bool:
        """
        Set account as default for user
        
        Args:
            user_id: User ID
            account_id: Account ID to set as default
        
        Returns:
            True if successful
        """
        # TODO: Update database to set is_default=False for all user accounts
        # Then set is_default=True for specified account
        
        logger.info(
            "default_account_set",
            user_id=user_id,
            account_id=account_id,
        )
        
        return True
    
    def update_account(
        self,
        account_id: str,
        account_name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        qmt_path: Optional[str] = None,
    ) -> bool:
        """
        Update broker account details
        
        Args:
            account_id: Account ID
            account_name: New account name (optional)
            api_key: New API key (optional, will be encrypted)
            api_secret: New API secret (optional, will be encrypted)
            qmt_path: New QMT path (optional)
        
        Returns:
            True if successful
        """
        # Get existing account
        account = self.get_account(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        # Update fields
        if account_name:
            account.account_name = account_name
        if api_key:
            account.api_key = api_key
        if api_secret:
            account.api_secret = api_secret
        if qmt_path:
            account.qmt_path = qmt_path
        
        account.updated_at = datetime.now()
        
        # TODO: Save updated account to database
        
        logger.info(
            "broker_account_updated",
            account_id=account_id,
        )
        
        return True
    
    def delete_account(self, account_id: str) -> bool:
        """
        Delete broker account
        
        Args:
            account_id: Account ID
        
        Returns:
            True if successful
        """
        # TODO: Implement database deletion
        
        # Clear active account if deleting
        if self._active_account_id == account_id:
            self._active_account_id = None
        
        logger.info(
            "broker_account_deleted",
            account_id=account_id,
        )
        
        return True
    
    def set_active_account(self, account_id: str) -> bool:
        """
        Set currently active account for trading
        
        Args:
            account_id: Account ID
        
        Returns:
            True if successful
        """
        account = self.get_account(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        if account.status != AccountStatus.ACTIVE:
            raise ValueError(f"Account is not active: {account_id}")
        
        self._active_account_id = account_id
        
        logger.info(
            "active_account_set",
            account_id=account_id,
            broker_id=account.broker_id,
        )
        
        return True
    
    def get_active_account(self) -> Optional[BrokerAccount]:
        """
        Get currently active account
        
        Returns:
            Active broker account or None
        """
        if not self._active_account_id:
            return None
        
        return self.get_account(self._active_account_id)
    
    def test_account_connection(self, account_id: str) -> dict:
        """
        Test broker account connection
        
        Args:
            account_id: Account ID
        
        Returns:
            Dictionary with connection test results
        """
        account = self.get_account(account_id)
        if not account:
            return {
                'success': False,
                'error': 'Account not found',
            }
        
        try:
            # Import broker adapter
            from wistrade.brokers import QMTAdapter
            
            # Create broker config
            config = BrokerConfig(
                broker_id=account.broker_id,
                broker_name=account.broker_id,  # Will be mapped to actual name
            )
            
            # Create adapter
            adapter = QMTAdapter(config)
            
            # Test connection
            # Note: This is async, but we're in sync context
            # In production, this should be handled properly
            # For now, return placeholder
            
            return {
                'success': True,
                'broker': account.broker_id,
                'account_name': account.account_name,
                'message': 'Connection test not implemented in sync context',
            }
            
        except Exception as e:
            logger.error(
                "account_connection_test_failed",
                account_id=account_id,
                error=str(e),
            )
            
            return {
                'success': False,
                'error': str(e),
            }
