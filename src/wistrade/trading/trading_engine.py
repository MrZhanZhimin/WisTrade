"""
Main trading engine coordinating all trading activities

Integrates order management, risk management, and strategy execution.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from wistrade.brokers.base import BrokerAdapter, Order, OrderSide, OrderType
from wistrade.trading.order_manager import OrderManager
from wistrade.trading.risk_manager import RiskManager, RiskLimits
from wistrade.trading.backtest_engine import BacktestEngine
from wistrade.ai.strategy_generator import TradingStrategy
from wistrade.storage.models import BrokerAccount
from wistrade.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TradingSession:
    """Active trading session"""
    session_id: str
    account_id: str
    strategy: TradingStrategy
    started_at: datetime
    status: str  # running, paused, stopped
    orders_executed: int = 0
    total_pnl: float = 0.0


class TradingEngine:
    """
    Main trading engine
    
    Coordinates:
    - Order management
    - Risk management
    - Strategy execution
    - Multi-account trading
    """
    
    def __init__(
        self,
        broker: BrokerAdapter,
        account: BrokerAccount,
        risk_limits: Optional[RiskLimits] = None,
    ):
        """
        Initialize trading engine
        
        Args:
            broker: Broker adapter instance
            account: Trading account
            risk_limits: Risk limit configuration
        """
        self.broker = broker
        self.account = account
        
        # Initialize components
        self.order_manager = OrderManager(broker)
        self.risk_manager = RiskManager(account, risk_limits)
        self.backtest_engine = BacktestEngine()
        
        # Trading state
        self.active_sessions: Dict[str, TradingSession] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        logger.info(
            f"Trading engine initialized: account={account.account_id}, "
            f"broker={account.broker_id}"
        )
    
    async def start_strategy(
        self,
        strategy: TradingStrategy,
        paper_trading: bool = True,
    ) -> str:
        """
        Start automated trading with strategy
        
        Args:
            strategy: Trading strategy to execute
            paper_trading: Use paper trading mode
        
        Returns:
            Session ID
        """
        import uuid
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create trading session
        session = TradingSession(
            session_id=session_id,
            account_id=self.account.account_id,
            strategy=strategy,
            started_at=datetime.now(),
            status="running",
        )
        
        self.active_sessions[session_id] = session
        
        # Start trading loop
        task = asyncio.create_task(
            self._trading_loop(session, paper_trading)
        )
        self._tasks.append(task)
        
        logger.info(
            f"Strategy started: session={session_id}, "
            f"strategy={strategy.name}, paper={paper_trading}"
        )
        
        return session_id
    
    async def stop_strategy(self, session_id: str) -> bool:
        """
        Stop trading session
        
        Args:
            session_id: Session ID to stop
        
        Returns:
            True if stopped successfully
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        session = self.active_sessions[session_id]
        session.status = "stopped"
        
        logger.info(
            f"Strategy stopped: session={session_id}, "
            f"orders={session.orders_executed}, pnl={session.total_pnl}"
        )
        
        return True
    
    async def pause_strategy(self, session_id: str) -> bool:
        """
        Pause trading session
        
        Args:
            session_id: Session ID to pause
        
        Returns:
            True if paused successfully
        """
        if session_id not in self.active_sessions:
            return False
        
        self.active_sessions[session_id].status = "paused"
        logger.info(f"Strategy paused: session={session_id}")
        
        return True
    
    async def resume_strategy(self, session_id: str) -> bool:
        """
        Resume paused session
        
        Args:
            session_id: Session ID to resume
        
        Returns:
            True if resumed successfully
        """
        if session_id not in self.active_sessions:
            return False
        
        self.active_sessions[session_id].status = "running"
        logger.info(f"Strategy resumed: session={session_id}")
        
        return True
    
    async def execute_manual_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[float] = None,
    ) -> Order:
        """
        Execute manual trading order
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            order_type: Market or limit
            price: Price for limit orders
        
        Returns:
            Executed order
        """
        # Create order
        order = await self.order_manager.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
        )
        
        # Validate with risk manager
        # TODO: Get actual portfolio value
        portfolio_value = 100000.0  # Placeholder
        
        is_valid, violations = self.risk_manager.validate_order(order, portfolio_value)
        
        if not is_valid:
            raise ValueError(f"Order violates risk limits: {violations}")
        
        # Execute order
        executed_order = await self.order_manager.submit_order(order)
        
        # Record for risk tracking
        self.risk_manager.record_order(executed_order)
        
        logger.info(
            f"Manual order executed: {executed_order.order_id} | "
            f"{symbol} | {side.value} | {quantity} @ {price or 'market'}"
        )
        
        return executed_order
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """
        Get current portfolio status
        
        Returns:
            Portfolio information
        """
        # Get account info from broker
        account_info = await self.broker.get_account_info()
        
        # Get positions
        positions = await self.broker.get_positions()
        
        # Get risk report
        risk_report = self.risk_manager.get_risk_report()
        
        # Get active orders
        active_orders = self.order_manager.get_active_orders()
        
        return {
            'account': {
                'total_assets': account_info.total_assets,
                'available_cash': account_info.available_cash,
                'market_value': account_info.market_value,
            },
            'positions': [
                {
                    'symbol': p.symbol,
                    'quantity': p.quantity,
                    'avg_cost': p.avg_cost,
                    'current_price': p.current_price,
                    'profit_loss': p.profit_loss,
                    'profit_loss_pct': p.profit_loss_pct,
                }
                for p in positions
            ],
            'active_orders': [
                {
                    'order_id': o.order_id,
                    'symbol': o.symbol,
                    'side': o.side.value,
                    'quantity': o.quantity,
                    'price': o.price,
                    'status': o.status.value,
                }
                for o in active_orders
            ],
            'risk': risk_report,
            'active_strategies': len(self.active_sessions),
        }
    
    async def _trading_loop(
        self,
        session: TradingSession,
        paper_trading: bool,
    ) -> None:
        """
        Main trading loop for automated strategy execution
        
        Args:
            session: Trading session
            paper_trading: Use paper trading mode
        """
        logger.info(f"Trading loop started: session={session.session_id}")
        
        try:
            while session.status == "running":
                # Execute strategy logic
                # TODO: Implement actual strategy execution
                # This is a placeholder for the strategy execution logic
                
                # Get market data
                # Analyze with strategy
                # Generate signals
                # Validate with risk manager
                # Execute orders
                
                # Sleep before next iteration
                await asyncio.sleep(60)  # Check every minute
                
        except asyncio.CancelledError:
            logger.info(f"Trading loop cancelled: session={session.session_id}")
            
        except Exception as e:
            logger.error(f"Trading loop error: {e}")
            session.status = "stopped"
    
    async def shutdown(self) -> None:
        """
        Shutdown trading engine
        
        Cancels all active sessions and tasks
        """
        logger.info("Shutting down trading engine")
        
        # Stop all sessions
        for session_id in list(self.active_sessions.keys()):
            await self.stop_strategy(session_id)
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        logger.info("Trading engine shutdown complete")
