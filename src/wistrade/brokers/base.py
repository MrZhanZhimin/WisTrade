"""
Base broker adapter interface and data models
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class OrderSide(Enum):
    """Order side (buy/sell)"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Order execution status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class BrokerConfig:
    """Broker configuration"""
    broker_id: str
    broker_name: str
    broker_type: str = "qmt"
    enabled: bool = True
    account_min_assets: float = 100000.0
    api_endpoint: Optional[str] = None
    qmt_path: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccountInfo:
    """Trading account information"""
    account_id: str
    broker_id: str
    total_assets: float
    available_cash: float
    market_value: float
    margin_used: float = 0.0
    currency: str = "CNY"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Position:
    """Stock position"""
    symbol: str
    quantity: int
    available_quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_pct: float
    account_id: str


@dataclass
class Order:
    """Trading order"""
    order_id: str
    client_order_id: Optional[str]
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float]  # None for market orders
    filled_quantity: int = 0
    filled_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    account_id: str = ""
    error_message: Optional[str] = None


@dataclass
class MarketData:
    """Real-time market data"""
    symbol: str
    name: str
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    previous_close: float
    volume: int
    turnover: float
    timestamp: datetime = field(default_factory=datetime.now)
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_volume: Optional[int] = None
    ask_volume: Optional[int] = None


@dataclass
class KLine:
    """K-line (candlestick) data"""
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    turnover: float
    interval: str  # 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M


class BrokerAdapter(ABC):
    """
    Abstract base class for broker adapters
    
    Defines the unified interface for trading operations across
    different Chinese securities brokers.
    """
    
    def __init__(self, config: BrokerConfig):
        """
        Initialize broker adapter
        
        Args:
            config: Broker configuration
        """
        self.config = config
        self._connected = False
        self._account_id: Optional[str] = None
    
    @abstractmethod
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Connect to broker with credentials
        
        Args:
            credentials: Authentication credentials (api_key, api_secret, etc.)
        
        Returns:
            True if connection successful
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from broker
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to broker
        
        Returns:
            True if connected
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> AccountInfo:
        """
        Get account information
        
        Returns:
            Account information
        
        Raises:
            ConnectionError: If not connected
        """
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """
        Get all positions
        
        Returns:
            List of positions
        """
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None,
    ) -> Order:
        """
        Place a trading order
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            order_type: Market, limit, etc.
            quantity: Number of shares
            price: Price for limit orders
        
        Returns:
            Order object
        
        Raises:
            ValueError: Invalid order parameters
            ConnectionError: If not connected
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancelled successfully
        """
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str) -> Order:
        """
        Get order details
        
        Args:
            order_id: Order ID
        
        Returns:
            Order details
        """
        pass
    
    @abstractmethod
    async def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None,
    ) -> List[Order]:
        """
        Get orders with optional filters
        
        Args:
            symbol: Filter by symbol (optional)
            status: Filter by status (optional)
        
        Returns:
            List of orders
        """
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> MarketData:
        """
        Get real-time market data for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Market data
        """
        pass
    
    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KLine]:
        """
        Get historical K-line data
        
        Args:
            symbol: Stock symbol
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M)
            start_time: Start time (optional)
            end_time: End time (optional)
            limit: Maximum number of candles
        
        Returns:
            List of K-line data
        """
        pass
    
    @abstractmethod
    async def subscribe_market_data(
        self,
        symbols: List[str],
        callback: Any,
    ) -> bool:
        """
        Subscribe to real-time market data updates
        
        Args:
            symbols: List of symbols to subscribe
            callback: Callback function for data updates
        
        Returns:
            True if subscription successful
        """
        pass
    
    @abstractmethod
    async def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """
        Unsubscribe from market data updates
        
        Args:
            symbols: List of symbols to unsubscribe
        
        Returns:
            True if unsubscription successful
        """
        pass
    
    def get_broker_id(self) -> str:
        """Get broker identifier"""
        return self.config.broker_id
    
    def get_broker_name(self) -> str:
        """Get broker display name"""
        return self.config.broker_name
    
    def is_enabled(self) -> bool:
        """Check if broker is enabled"""
        return self.config.enabled
