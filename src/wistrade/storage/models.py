"""
Data models for database storage
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AccountStatus(Enum):
    """Account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class StrategyStatus(Enum):
    """Strategy execution status"""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class User:
    """User account"""
    user_id: str
    username: str
    email: str
    phone: Optional[str] = None
    hashed_password: str = ""
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    # Additional metadata
    full_name: Optional[str] = None
    risk_level: str = "C4"  # C1-C5 risk assessment level


@dataclass
class BrokerAccount:
    """Broker account credentials"""
    account_id: str
    user_id: str
    broker_id: str  # zhao_shang, guang_da, jiang_hai
    account_name: str
    account_number: str  # Encrypted
    api_key: str  # Encrypted
    api_secret: str  # Encrypted
    status: AccountStatus = AccountStatus.ACTIVE
    is_default: bool = False
    
    # Encryption metadata
    encryption_version: int = 1
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    
    # Additional params
    qmt_path: Optional[str] = None
    extra_params: dict = field(default_factory=dict)


@dataclass
class Strategy:
    """Trading strategy"""
    strategy_id: str
    user_id: str
    account_id: str
    name: str
    description: str = ""
    
    # Strategy configuration
    strategy_type: str = "ai_generated"  # ai_generated, custom, template
    symbols: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    
    # Risk management
    max_position_pct: float = 0.20
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    
    # Status
    status: StrategyStatus = StrategyStatus.STOPPED
    
    # Performance metrics
    total_trades: int = 0
    winning_trades: int = 0
    total_return: float = 0.0
    sharpe_ratio: Optional[float] = None
    max_drawdown: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None


@dataclass
class Trade:
    """Trade execution record"""
    trade_id: str
    order_id: str
    strategy_id: Optional[str]
    account_id: str
    symbol: str
    
    # Trade details
    side: str  # BUY, SELL
    quantity: int
    price: float
    total_amount: float
    commission: float = 0.0
    tax: float = 0.0
    
    # Execution info
    execution_time: datetime = field(default_factory=datetime.now)
    execution_type: str = "market"  # market, limit
    
    # P&L (for closed positions)
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    
    # Metadata
    notes: str = ""
    tags: list = field(default_factory=list)


@dataclass
class AuditLog:
    """
    Audit log entry for compliance
    
    Retained for 5 years per regulatory requirements.
    """
    log_id: str
    user_id: str
    account_id: Optional[str]
    
    # Action details
    action: str  # LOGIN, ORDER, CANCEL, VIEW, MODIFY
    resource: str
    details: dict = field(default_factory=dict)
    
    # Security info
    ip_address: Optional[str] = None  # Masked for privacy
    user_agent: Optional[str] = None
    
    # Result
    success: bool = True
    error_message: Optional[str] = None
    
    # Compliance
    checksum: str = ""  # Tamper-evidence
    timestamp: datetime = field(default_factory=datetime.now)
