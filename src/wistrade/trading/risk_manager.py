"""
Risk management system for WisTrade

Implements multi-layer risk controls for trading safety.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from wistrade.brokers.base import Order, OrderSide
from wistrade.storage.models import BrokerAccount

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    # Position limits
    max_position_pct: float = 20.0  # Max % of portfolio per stock
    max_sector_exposure_pct: float = 40.0  # Max % in single sector
    
    # Loss limits
    max_daily_loss_pct: float = 5.0  # Max daily loss %
    max_weekly_loss_pct: float = 10.0  # Max weekly loss %
    max_monthly_loss_pct: float = 15.0  # Max monthly loss %
    
    # Order limits
    max_order_value: float = 100000.0  # Max single order value
    max_orders_per_day: int = 50  # Max orders per day
    max_orders_per_hour: int = 20  # Max orders per hour
    max_order_rate: int = 10  # Max orders per minute
    
    # Leverage limits
    max_leverage: float = 1.0  # No margin for retail
    
    # Drawdown limits
    max_drawdown_pct: float = 20.0  # Max portfolio drawdown
    
    # Concentration limits
    max_single_stock_pct: float = 30.0  # Max % in single stock
    min_cash_reserve_pct: float = 10.0  # Min cash reserve


@dataclass
class RiskMetrics:
    """Current risk metrics"""
    current_drawdown_pct: float = 0.0
    daily_pnl_pct: float = 0.0
    weekly_pnl_pct: float = 0.0
    monthly_pnl_pct: float = 0.0
    orders_today: int = 0
    orders_this_hour: int = 0
    largest_position_pct: float = 0.0
    sector_concentration: Dict[str, float] = field(default_factory=dict)
    leverage_ratio: float = 1.0
    cash_reserve_pct: float = 100.0
    risk_level: RiskLevel = RiskLevel.LOW


class RiskManager:
    """
    Multi-layer risk management system
    
    Implements risk controls at:
    1. Order level - position size, order value
    2. Portfolio level - concentration, correlation
    3. Account level - drawdown, daily loss
    4. System level - order rate, circuit breakers
    """
    
    def __init__(
        self,
        account: BrokerAccount,
        limits: Optional[RiskLimits] = None,
    ):
        """
        Initialize risk manager
        
        Args:
            account: Trading account
            limits: Risk limits configuration
        """
        self.account = account
        self.limits = limits or RiskLimits()
        self.metrics = RiskMetrics()
        
        # Order tracking
        self._order_times: List[datetime] = []
        self._daily_orders: Dict[str, int] = {}
        
        # P&L tracking
        self._daily_pnl: Dict[str, float] = {}
        self._peak_value: Optional[float] = None
        
        logger.info(f"Risk manager initialized for account {account.account_id}")
    
    def validate_order(self, order: Order, portfolio_value: float) -> tuple[bool, List[str]]:
        """
        Validate order against risk limits
        
        Args:
            order: Order to validate
            portfolio_value: Current portfolio value
        
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # Check order value
        order_value = order.quantity * (order.price or 0)
        if order_value > self.limits.max_order_value:
            violations.append(
                f"Order value {order_value} exceeds max {self.limits.max_order_value}"
            )
        
        # Check position size
        position_pct = (order_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        if position_pct > self.limits.max_position_pct:
            violations.append(
                f"Position size {position_pct:.1f}% exceeds max {self.limits.max_position_pct}%"
            )
        
        # Check order rate
        recent_orders = self._get_recent_order_count(minutes=1)
        if recent_orders >= self.limits.max_order_rate:
            violations.append(
                f"Order rate {recent_orders}/min exceeds max {self.limits.max_order_rate}/min"
            )
        
        # Check daily order limit
        if self.metrics.orders_today >= self.limits.max_orders_per_day:
            violations.append(
                f"Daily order limit reached ({self.limits.max_orders_per_day})"
            )
        
        # Check hourly order limit
        if self.metrics.orders_this_hour >= self.limits.max_orders_per_hour:
            violations.append(
                f"Hourly order limit reached ({self.limits.max_orders_per_hour})"
            )
        
        # Check if trading should be halted
        if self._should_halt_trading():
            violations.append("Trading halted due to risk limits")
        
        is_valid = len(violations) == 0
        
        if not is_valid:
            logger.warning(f"Order validation failed: {violations}")
        
        return is_valid, violations
    
    def record_order(self, order: Order) -> None:
        """
        Record order execution for risk tracking
        
        Args:
            order: Executed order
        """
        now = datetime.now()
        
        # Track order time for rate limiting
        self._order_times.append(now)
        
        # Update daily orders
        date_key = now.strftime('%Y-%m-%d')
        self._daily_orders[date_key] = self._daily_orders.get(date_key, 0) + 1
        
        # Update metrics
        self.metrics.orders_today = self._daily_orders.get(date_key, 0)
        
        logger.debug(f"Order recorded: {order.order_id}")
    
    def update_pnl(self, daily_pnl: float, portfolio_value: float) -> None:
        """
        Update P&L tracking
        
        Args:
            daily_pnl: Today's P&L
            portfolio_value: Current portfolio value
        """
        # Update peak value
        if self._peak_value is None or portfolio_value > self._peak_value:
            self._peak_value = portfolio_value
        
        # Calculate drawdown
        if self._peak_value and self._peak_value > 0:
            self.metrics.current_drawdown_pct = (
                (self._peak_value - portfolio_value) / self._peak_value * 100
            )
        
        # Update daily P&L
        date_key = datetime.now().strftime('%Y-%m-%d')
        self._daily_pnl[date_key] = daily_pnl
        
        # Calculate daily P&L %
        # Note: This is simplified - would need initial portfolio value for accurate %
        self.metrics.daily_pnl_pct = daily_pnl / portfolio_value * 100 if portfolio_value > 0 else 0
        
        # Update risk level
        self._update_risk_level()
        
        logger.debug(
            f"P&L updated: daily={self.metrics.daily_pnl_pct:.2f}%, "
            f"drawdown={self.metrics.current_drawdown_pct:.2f}%"
        )
    
    def _should_halt_trading(self) -> bool:
        """
        Check if trading should be halted
        
        Returns:
            True if trading should halt
        """
        # Halt if daily loss exceeded
        if abs(self.metrics.daily_pnl_pct) > self.limits.max_daily_loss_pct:
            logger.critical("Trading halted: Daily loss limit exceeded")
            return True
        
        # Halt if max drawdown exceeded
        if self.metrics.current_drawdown_pct > self.limits.max_drawdown_pct:
            logger.critical("Trading halted: Max drawdown exceeded")
            return True
        
        return False
    
    def _get_recent_order_count(self, minutes: int = 1) -> int:
        """
        Get count of recent orders
        
        Args:
            minutes: Time window in minutes
        
        Returns:
            Number of orders in time window
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return sum(1 for t in self._order_times if t > cutoff)
    
    def _update_risk_level(self) -> None:
        """Update overall risk level based on metrics"""
        
        # Determine risk level
        if self.metrics.current_drawdown_pct > self.limits.max_drawdown_pct * 0.8:
            self.metrics.risk_level = RiskLevel.CRITICAL
        elif abs(self.metrics.daily_pnl_pct) > self.limits.max_daily_loss_pct * 0.8:
            self.metrics.risk_level = RiskLevel.HIGH
        elif self.metrics.current_drawdown_pct > self.limits.max_drawdown_pct * 0.5:
            self.metrics.risk_level = RiskLevel.MEDIUM
        else:
            self.metrics.risk_level = RiskLevel.LOW
    
    def get_risk_report(self) -> Dict[str, Any]:
        """
        Get comprehensive risk report
        
        Returns:
            Risk metrics and status
        """
        return {
            'risk_level': self.metrics.risk_level.value,
            'current_drawdown_pct': self.metrics.current_drawdown_pct,
            'daily_pnl_pct': self.metrics.daily_pnl_pct,
            'orders_today': self.metrics.orders_today,
            'orders_this_hour': self.metrics.orders_this_hour,
            'order_rate_per_min': self._get_recent_order_count(1),
            'limits': {
                'max_position_pct': self.limits.max_position_pct,
                'max_daily_loss_pct': self.limits.max_daily_loss_pct,
                'max_drawdown_pct': self.limits.max_drawdown_pct,
                'max_orders_per_day': self.limits.max_orders_per_day,
            },
            'trading_halted': self._should_halt_trading(),
        }
    
    def cleanup_old_records(self, days: int = 30) -> None:
        """
        Clean up old tracking records
        
        Args:
            days: Days to keep
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Clean order times
        self._order_times = [t for t in self._order_times if t > cutoff]
        
        # Clean daily orders
        cutoff_date = cutoff.strftime('%Y-%m-%d')
        self._daily_orders = {
            k: v for k, v in self._daily_orders.items()
            if k > cutoff_date
        }
        
        # Clean daily P&L
        self._daily_pnl = {
            k: v for k, v in self._daily_pnl.items()
            if k > cutoff_date
        }
        
        logger.debug("Old risk records cleaned up")
