"""
Order management system for WisTrade

Handles order creation, execution, tracking, and cancellation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from wistrade.brokers.base import BrokerAdapter, Order, OrderSide, OrderStatus, OrderType
from wistrade.utils.helpers import generate_order_id

logger = logging.getLogger(__name__)


class OrderExecutor:
    """
    Order executor with retry logic and error handling
    
    Executes orders through broker adapters with:
    - Automatic retries
    - Error recovery
    - Order tracking
    """
    
    def __init__(self, broker: BrokerAdapter, max_retries: int = 3):
        """
        Initialize order executor
        
        Args:
            broker: Broker adapter instance
            max_retries: Maximum retry attempts
        """
        self.broker = broker
        self.max_retries = max_retries
        self._pending_orders: Dict[str, Order] = {}
    
    async def execute_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[float] = None,
        callback: Optional[Callable] = None,
    ) -> Order:
        """
        Execute order with retry logic
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            order_type: Market or limit
            price: Price for limit orders
            callback: Callback on order update
        
        Returns:
            Executed order
        
        Raises:
            RuntimeError: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                # Place order
                order = await self.broker.place_order(
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=price,
                )
                
                # Track pending order
                self._pending_orders[order.order_id] = order
                
                # Log order
                logger.info(
                    f"Order executed: {order.order_id} | {symbol} | "
                    f"{side.value} | {quantity} @ {price or 'market'}"
                )
                
                # Execute callback if provided
                if callback:
                    await callback(order)
                
                return order
                
            except Exception as e:
                logger.error(f"Order execution attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Order execution failed after {self.max_retries} attempts: {e}")
                
                # Wait before retry
                await asyncio.sleep(1 * (attempt + 1))
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel pending order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancelled successfully
        """
        try:
            success = await self.broker.cancel_order(order_id)
            
            if success:
                self._pending_orders.pop(order_id, None)
                logger.info(f"Order cancelled: {order_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> Order:
        """
        Get current order status
        
        Args:
            order_id: Order ID
        
        Returns:
            Updated order information
        """
        return await self.broker.get_order(order_id)


class OrderManager:
    """
    Order management system
    
    Manages order lifecycle:
    - Order creation and validation
    - Execution through broker
    - Status tracking
    - Order history
    """
    
    def __init__(self, broker: BrokerAdapter):
        """
        Initialize order manager
        
        Args:
            broker: Broker adapter for order execution
        """
        self.broker = broker
        self.executor = OrderExecutor(broker)
        self._orders: Dict[str, Order] = {}
        self._order_history: List[Order] = []
        self._callbacks: Dict[str, List[Callable]] = {}
    
    async def create_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.LIMIT,
        price: Optional[float] = None,
        strategy_id: Optional[str] = None,
    ) -> Order:
        """
        Create and validate order
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            order_type: Market or limit
            price: Price for limit orders
            strategy_id: Associated strategy ID
        
        Returns:
            Created order (not yet executed)
        """
        # Validate parameters
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("Price required for limit orders")
        
        if order_type == OrderType.LIMIT and price <= 0:
            raise ValueError("Price must be positive")
        
        # Generate order ID
        client_order_id = generate_order_id()
        
        # Create order object
        order = Order(
            order_id=client_order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # Store order
        self._orders[client_order_id] = order
        
        logger.info(
            f"Order created: {client_order_id} | {symbol} | "
            f"{side.value} | {quantity} @ {price or 'market'}"
        )
        
        return order
    
    async def submit_order(self, order: Order) -> Order:
        """
        Submit order for execution
        
        Args:
            order: Order to submit
        
        Returns:
            Executed order
        """
        # Execute order
        executed_order = await self.executor.execute_order(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            price=order.price,
        )
        
        # Update order tracking
        self._orders[executed_order.order_id] = executed_order
        self._order_history.append(executed_order)
        
        # Trigger callbacks
        await self._trigger_callbacks(executed_order.order_id, executed_order)
        
        return executed_order
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order
        
        Args:
            order_id: Order ID
        
        Returns:
            True if cancelled
        """
        success = await self.executor.cancel_order(order_id)
        
        if success:
            # Update order status
            if order_id in self._orders:
                self._orders[order_id].status = OrderStatus.CANCELLED
                self._orders[order_id].updated_at = datetime.now()
        
        return success
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID
        
        Args:
            order_id: Order ID
        
        Returns:
            Order or None
        """
        return self._orders.get(order_id)
    
    def get_active_orders(self) -> List[Order]:
        """
        Get all active orders
        
        Returns:
            List of active orders
        """
        return [
            order for order in self._orders.values()
            if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]
        ]
    
    def get_order_history(self, limit: int = 100) -> List[Order]:
        """
        Get order history
        
        Args:
            limit: Maximum orders to return
        
        Returns:
            List of historical orders
        """
        return self._order_history[-limit:]
    
    def register_callback(self, order_id: str, callback: Callable) -> None:
        """
        Register callback for order updates
        
        Args:
            order_id: Order ID
            callback: Callback function
        """
        if order_id not in self._callbacks:
            self._callbacks[order_id] = []
        
        self._callbacks[order_id].append(callback)
    
    async def _trigger_callbacks(self, order_id: str, order: Order) -> None:
        """
        Trigger registered callbacks
        
        Args:
            order_id: Order ID
            order: Updated order
        """
        callbacks = self._callbacks.get(order_id, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(order)
                else:
                    callback(order)
            except Exception as e:
                logger.error(f"Callback failed for order {order_id}: {e}")
