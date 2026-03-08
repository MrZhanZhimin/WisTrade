"""
QMT (Quantitative Market Trading) broker adapter

Implements broker adapter for QMT platform used by 招商证券, 光大证券, etc.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from wistrade.brokers.base import (
    AccountInfo,
    BrokerAdapter,
    BrokerConfig,
    KLine,
    MarketData,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)

logger = logging.getLogger(__name__)


class QMTAdapter(BrokerAdapter):
    """
    QMT broker adapter implementation
    
    Supports brokers that use the QMT platform:
    - 招商证券 (China Merchants Securities)
    - 光大证券 (Everbright Securities)
    - Other QMT-compatible brokers
    """
    
    def __init__(self, config: BrokerConfig):
        """
        Initialize QMT adapter
        
        Args:
            config: Broker configuration
        """
        super().__init__(config)
        self._qmt_client: Optional[Any] = None
        self._market_data_callback: Optional[Callable] = None
        self._subscribed_symbols: List[str] = []
    
    async def connect(self, credentials: Dict[str, str]) -> bool:
        """
        Connect to QMT broker
        
        Args:
            credentials: Should contain 'account_id' and optional 'qmt_path'
        
        Returns:
            True if connection successful
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Import QMT client (xtquant or easyxt)
            try:
                from xtquant import xtdata, xttrade
                
                logger.info("Using xtquant for QMT connection")
                self._qmt_client = {
                    'data': xtdata,
                    'trade': xttrade,
                    'type': 'xtquant'
                }
            except ImportError:
                try:
                    import easyxt as xt
                    
                    logger.info("Using easyxt for QMT connection")
                    self._qmt_client = {
                        'data': xt,
                        'trade': xt,
                        'type': 'easyxt'
                    }
                except ImportError:
                    raise ConnectionError(
                        "Neither xtquant nor easyxt found. "
                        "Please install: pip install xtquant or pip install easyxt"
                    )
            
            # Set account ID
            self._account_id = credentials.get('account_id')
            if not self._account_id:
                raise ValueError("account_id is required in credentials")
            
            # Configure QMT path if provided
            qmt_path = credentials.get('qmt_path') or self.config.qmt_path
            if qmt_path:
                # Set QMT client path for xtquant
                if self._qmt_client['type'] == 'xtquant':
                    import os
                    os.environ['QMT_PATH'] = qmt_path
            
            # Test connection by getting account info
            account_info = await self.get_account_info()
            
            self._connected = True
            logger.info(
                f"Connected to QMT broker: {self.config.broker_name} "
                f"(Account: {self._account_id})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to QMT broker: {e}")
            self._connected = False
            raise ConnectionError(f"QMT connection failed: {e}")
    
    async def disconnect(self) -> bool:
        """
        Disconnect from QMT broker
        
        Returns:
            True if disconnection successful
        """
        try:
            if self._subscribed_symbols:
                await self.unsubscribe_market_data(self._subscribed_symbols)
            
            self._qmt_client = None
            self._connected = False
            self._account_id = None
            
            logger.info(f"Disconnected from QMT broker: {self.config.broker_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from QMT: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Check if connected to broker"""
        return self._connected and self._qmt_client is not None
    
    async def get_account_info(self) -> AccountInfo:
        """
        Get account information from QMT
        
        Returns:
            Account information
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            # Get account asset information
            if self._qmt_client['type'] == 'xtquant':
                asset = self._qmt_client['trade'].get_account_asset(self._account_id)
                
                return AccountInfo(
                    account_id=self._account_id,
                    broker_id=self.config.broker_id,
                    total_assets=asset.total_asset,
                    available_cash=asset.cash,
                    market_value=asset.market_value,
                    margin_used=getattr(asset, 'margin_used', 0.0),
                    currency="CNY",
                    last_updated=datetime.now(),
                )
            else:  # easyxt
                account = self._qmt_client['trade'].get_account()
                
                return AccountInfo(
                    account_id=self._account_id,
                    broker_id=self.config.broker_id,
                    total_assets=account.total_asset,
                    available_cash=account.available_cash,
                    market_value=account.market_value,
                    margin_used=0.0,
                    currency="CNY",
                    last_updated=datetime.now(),
                )
                
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            raise
    
    async def get_positions(self) -> List[Position]:
        """
        Get all positions from QMT
        
        Returns:
            List of positions
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            positions = []
            
            if self._qmt_client['type'] == 'xtquant':
                qmt_positions = self._qmt_client['trade'].get_stock_position(self._account_id)
                
                for pos in qmt_positions:
                    # Get current price
                    market_data = await self.get_market_data(pos.stock_code)
                    current_price = market_data.current_price
                    
                    market_value = pos.volume * current_price
                    profit_loss = market_value - (pos.volume * pos.open_price)
                    profit_loss_pct = (profit_loss / (pos.volume * pos.open_price)) * 100 if pos.open_price > 0 else 0
                    
                    positions.append(Position(
                        symbol=pos.stock_code,
                        quantity=pos.volume,
                        available_quantity=pos.can_use_volume,
                        avg_cost=pos.open_price,
                        current_price=current_price,
                        market_value=market_value,
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        account_id=self._account_id,
                    ))
            else:  # easyxt
                qmt_positions = self._qmt_client['trade'].get_positions()
                
                for pos in qmt_positions:
                    positions.append(Position(
                        symbol=pos.symbol,
                        quantity=pos.quantity,
                        available_quantity=pos.available,
                        avg_cost=pos.avg_cost,
                        current_price=pos.current_price,
                        market_value=pos.market_value,
                        profit_loss=pos.profit_loss,
                        profit_loss_pct=pos.profit_loss_pct,
                        account_id=self._account_id,
                    ))
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None,
    ) -> Order:
        """
        Place a trading order via QMT
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            order_type: Market, limit, etc.
            quantity: Number of shares
            price: Price for limit orders
        
        Returns:
            Order object
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            # Map order type to QMT order type
            order_type_map = {
                OrderType.MARKET: 43,  # 市价单
                OrderType.LIMIT: 23,   # 限价单
            }
            
            qmt_order_type = order_type_map.get(order_type, 23)
            
            # Place order
            if self._qmt_client['type'] == 'xtquant':
                order_id = self._qmt_client['trade'].order_stock(
                    account=self._account_id,
                    stock_code=symbol,
                    order_type=2 if side == OrderSide.BUY else 1,  # 2=买入, 1=卖出
                    order_volume=quantity,
                    price_type=qmt_order_type,
                    price=price or 0,
                )
            else:  # easyxt
                order_id = self._qmt_client['trade'].place_order(
                    symbol=symbol,
                    side=side.value,
                    quantity=quantity,
                    price=price,
                    order_type=order_type.value,
                )
            
            # Create order object
            order = Order(
                order_id=str(order_id),
                client_order_id=None,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                filled_quantity=0,
                filled_price=None,
                status=OrderStatus.SUBMITTED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                account_id=self._account_id,
            )
            
            logger.info(
                f"Order placed: {order_id} | {symbol} | {side.value} | "
                f"{quantity} @ {price or 'market'}"
            )
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order via QMT
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if cancelled successfully
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            if self._qmt_client['type'] == 'xtquant':
                result = self._qmt_client['trade'].cancel_order(
                    self._account_id,
                    order_id,
                )
            else:  # easyxt
                result = self._qmt_client['trade'].cancel_order(order_id)
            
            logger.info(f"Order cancelled: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order(self, order_id: str) -> Order:
        """Get order details"""
        orders = await self.get_orders()
        for order in orders:
            if order.order_id == order_id:
                return order
        raise ValueError(f"Order not found: {order_id}")
    
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
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            orders = []
            
            if self._qmt_client['type'] == 'xtquant':
                qmt_orders = self._qmt_client['trade'].get_stock_orders(self._account_id)
                
                for ord in qmt_orders:
                    # Filter by symbol if provided
                    if symbol and ord.stock_code != symbol:
                        continue
                    
                    # Map status
                    status_map = {
                        48: OrderStatus.SUBMITTED,
                        49: OrderStatus.PARTIAL_FILLED,
                        50: OrderStatus.FILLED,
                        51: OrderStatus.CANCELLED,
                    }
                    order_status = status_map.get(ord.order_status, OrderStatus.PENDING)
                    
                    # Filter by status if provided
                    if status and order_status != status:
                        continue
                    
                    orders.append(Order(
                        order_id=str(ord.order_id),
                        client_order_id=None,
                        symbol=ord.stock_code,
                        side=OrderSide.BUY if ord.order_type == 2 else OrderSide.SELL,
                        order_type=OrderType.LIMIT if ord.price_type == 23 else OrderType.MARKET,
                        quantity=ord.order_volume,
                        price=ord.price,
                        filled_quantity=ord.traded_volume,
                        filled_price=ord.traded_price,
                        status=order_status,
                        created_at=datetime.fromtimestamp(ord.order_time / 1000),
                        updated_at=datetime.now(),
                        account_id=self._account_id,
                    ))
            
            return orders
            
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            raise
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """
        Get real-time market data from QMT
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Market data
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            if self._qmt_client['type'] == 'xtquant':
                # Get full tick data
                tick = self._qmt_client['data'].get_full_tick([symbol])[0]
                
                return MarketData(
                    symbol=symbol,
                    name="",  # Will be fetched separately if needed
                    current_price=tick.lastPrice,
                    open_price=tick.open,
                    high_price=tick.high,
                    low_price=tick.low,
                    previous_close=tick.lastClose,
                    volume=tick.volume,
                    turnover=tick.amount,
                    timestamp=datetime.now(),
                    bid_price=tick.bidPrice[0] if tick.bidPrice else None,
                    ask_price=tick.askPrice[0] if tick.askPrice else None,
                    bid_volume=tick.bidVol[0] if tick.bidVol else None,
                    ask_volume=tick.askVol[0] if tick.askVol else None,
                )
            else:  # easyxt
                data = self._qmt_client['data'].get_quote(symbol)
                
                return MarketData(
                    symbol=symbol,
                    name=data.name,
                    current_price=data.current,
                    open_price=data.open,
                    high_price=data.high,
                    low_price=data.low,
                    previous_close=data.previous_close,
                    volume=data.volume,
                    turnover=data.turnover,
                    timestamp=datetime.now(),
                    bid_price=data.bid,
                    ask_price=data.ask,
                )
                
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            raise
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KLine]:
        """
        Get historical K-line data from QMT
        
        Args:
            symbol: Stock symbol
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M)
            start_time: Start time (optional)
            end_time: End time (optional)
            limit: Maximum number of candles
        
        Returns:
            List of K-line data
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            klines = []
            
            # Map interval to QMT period
            period_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '1d': '1d',
                '1w': '1w',
                '1M': '1mon',
            }
            period = period_map.get(interval, '1d')
            
            if self._qmt_client['type'] == 'xtquant':
                # Download historical data
                df = self._qmt_client['data'].get_market_data(
                    field_list=[],
                    stock_list=[symbol],
                    period=period,
                    start_time=start_time.strftime('%Y%m%d') if start_time else '',
                    end_time=end_time.strftime('%Y%m%d') if end_time else '',
                    count=limit,
                )
                
                if not df.empty:
                    for idx, row in df.iterrows():
                        klines.append(KLine(
                            symbol=symbol,
                            timestamp=idx.to_pydatetime(),
                            open_price=row['open'],
                            high_price=row['high'],
                            low_price=row['low'],
                            close_price=row['close'],
                            volume=int(row['volume']),
                            turnover=row['amount'],
                            interval=interval,
                        ))
            
            return klines
            
        except Exception as e:
            logger.error(f"Failed to get K-lines for {symbol}: {e}")
            raise
    
    async def subscribe_market_data(
        self,
        symbols: List[str],
        callback: Callable,
    ) -> bool:
        """
        Subscribe to real-time market data updates
        
        Args:
            symbols: List of symbols to subscribe
            callback: Callback function for data updates
        
        Returns:
            True if subscription successful
        """
        if not await self.is_connected():
            raise ConnectionError("Not connected to QMT broker")
        
        try:
            self._market_data_callback = callback
            
            if self._qmt_client['type'] == 'xtquant':
                # Subscribe to market data
                self._qmt_client['data'].subscribe_quote(
                    stock_code_list=symbols,
                    callback=self._on_market_data_update,
                )
            
            self._subscribed_symbols.extend(symbols)
            logger.info(f"Subscribed to market data: {symbols}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to market data: {e}")
            return False
    
    async def unsubscribe_market_data(self, symbols: List[str]) -> bool:
        """
        Unsubscribe from market data updates
        
        Args:
            symbols: List of symbols to unsubscribe
        
        Returns:
            True if unsubscription successful
        """
        try:
            if self._qmt_client and self._qmt_client['type'] == 'xtquant':
                self._qmt_client['data'].unsubscribe_quote(symbols)
            
            # Remove from subscribed list
            self._subscribed_symbols = [
                s for s in self._subscribed_symbols if s not in symbols
            ]
            
            logger.info(f"Unsubscribed from market data: {symbols}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from market data: {e}")
            return False
    
    def _on_market_data_update(self, data: Any) -> None:
        """
        Internal callback for QMT market data updates
        
        Args:
            data: Market data from QMT
        """
        try:
            if self._market_data_callback:
                # Convert to MarketData and call user callback
                market_data = MarketData(
                    symbol=data.stock_code,
                    name="",
                    current_price=data.lastPrice,
                    open_price=data.open,
                    high_price=data.high,
                    low_price=data.low,
                    previous_close=data.lastClose,
                    volume=data.volume,
                    turnover=data.amount,
                    timestamp=datetime.now(),
                )
                
                # Call async callback in event loop
                if asyncio.iscoroutinefunction(self._market_data_callback):
                    asyncio.create_task(self._market_data_callback(market_data))
                else:
                    self._market_data_callback(market_data)
                    
        except Exception as e:
            logger.error(f"Error in market data callback: {e}")
