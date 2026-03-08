"""
Backtest engine for strategy validation

Simulates trading strategies on historical data with realistic costs.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from wistrade.brokers.base import KLine, Order, OrderSide, OrderType
from wistrade.ai.strategy_generator import TradingStrategy
from wistrade.utils.helpers import calculate_sharpe_ratio, calculate_max_drawdown, calculate_win_rate

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    """Backtest trade record"""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    side: OrderSide
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    profit_loss: float
    profit_loss_pct: float
    commission: float


@dataclass
class BacktestResult:
    """Backtest results summary"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # Performance metrics
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    
    # Trade statistics
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_holding_time: float  # hours
    
    # Risk metrics
    volatility: float
    var_95: float  # Value at Risk 95%
    
    # Detailed data
    trades: List[BacktestTrade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)


class BacktestEngine:
    """
    Strategy backtest engine
    
    Features:
    - Realistic slippage simulation
    - Commission fee calculation
    - Position tracking
    - Performance metrics
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,  # 0.03% typical
        slippage_bps: float = 5.0,  # 0.05% slippage
        stamp_duty: float = 0.001,  # 0.1% stamp duty (sell only)
    ):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            commission_rate: Commission fee rate
            slippage_bps: Slippage in basis points
            stamp_duty: Stamp duty rate (China market)
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_bps = slippage_bps
        self.stamp_duty = stamp_duty
        
        # Portfolio state
        self.cash = initial_capital
        self.positions: Dict[str, int] = {}  # symbol -> quantity
        self.equity_curve: List[float] = []
        
        # Trade tracking
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, BacktestTrade] = {}
        
        logger.info(
            f"Backtest engine initialized: capital={initial_capital}, "
            f"commission={commission_rate*100}%, slippage={slippage_bps}bps"
        )
    
    async def run_backtest(
        self,
        strategy: TradingStrategy,
        historical_data: Dict[str, List[KLine]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> BacktestResult:
        """
        Run backtest for strategy
        
        Args:
            strategy: Trading strategy to test
            historical_data: Historical K-line data by symbol
            start_date: Backtest start date
            end_date: Backtest end date
        
        Returns:
            Backtest results
        """
        logger.info(f"Starting backtest: {strategy.name}")
        
        # Reset state
        self._reset()
        
        # Get date range
        if not start_date or not end_date:
            # Infer from data
            all_dates = []
            for klines in historical_data.values():
                all_dates.extend([k.timestamp for k in klines])
            
            if all_dates:
                start_date = start_date or min(all_dates)
                end_date = end_date or max(all_dates)
        
        # Convert to DataFrame for easier processing
        data_frames = {}
        for symbol, klines in historical_data.items():
            df = pd.DataFrame([
                {
                    'timestamp': k.timestamp,
                    'open': k.open_price,
                    'high': k.high_price,
                    'low': k.low_price,
                    'close': k.close_price,
                    'volume': k.volume,
                }
                for k in klines
            ])
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            data_frames[symbol] = df
        
        # Run simulation
        current_date = start_date
        while current_date <= end_date:
            # Check each symbol
            for symbol in strategy.symbols:
                if symbol not in data_frames:
                    continue
                
                df = data_frames[symbol]
                
                # Get current day's data
                day_data = df[df.index.date == current_date.date()]
                
                if day_data.empty:
                    continue
                
                # Simple strategy simulation
                # In production, this would use actual strategy logic
                await self._simulate_strategy_day(symbol, day_data, strategy)
            
            # Update equity curve
            portfolio_value = self._calculate_portfolio_value(data_frames, current_date)
            self.equity_curve.append(portfolio_value)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Calculate results
        result = self._calculate_results(strategy.name, start_date, end_date)
        
        logger.info(
            f"Backtest complete: return={result.total_return_pct:.2f}%, "
            f"sharpe={result.sharpe_ratio:.2f}, max_dd={result.max_drawdown_pct:.2f}%"
        )
        
        return result
    
    async def _simulate_strategy_day(
        self,
        symbol: str,
        day_data: pd.DataFrame,
        strategy: TradingStrategy,
    ) -> None:
        """
        Simulate strategy for a single day
        
        Args:
            symbol: Stock symbol
            day_data: Day's OHLCV data
            strategy: Trading strategy
        """
        # Get current position
        position = self.positions.get(symbol, 0)
        
        # Simple entry/exit logic (placeholder)
        # In production, this would use strategy.entry_conditions and exit_conditions
        
        # Example: Buy on open if no position
        if position == 0:
            open_price = day_data.iloc[0]['open']
            quantity = int(self.cash * 0.2 / open_price)  # Use 20% of cash
            
            if quantity > 0:
                # Apply slippage
                fill_price = open_price * (1 + self.slippage_bps / 10000)
                
                # Calculate costs
                trade_value = fill_price * quantity
                commission = trade_value * self.commission_rate
                
                # Execute buy
                if trade_value + commission <= self.cash:
                    self.cash -= (trade_value + commission)
                    self.positions[symbol] = quantity
                    
                    # Record trade
                    trade = BacktestTrade(
                        entry_time=day_data.index[0],
                        exit_time=None,
                        symbol=symbol,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        entry_price=fill_price,
                        exit_price=None,
                        profit_loss=0.0,
                        profit_loss_pct=0.0,
                        commission=commission,
                    )
                    self.open_positions[symbol] = trade
        
        # Example: Sell if have position and stop-loss/take-profit hit
        elif position > 0 and symbol in self.open_positions:
            trade = self.open_positions[symbol]
            close_price = day_data.iloc[-1]['close']
            
            # Check exit conditions
            pnl_pct = (close_price - trade.entry_price) / trade.entry_price * 100
            
            should_exit = False
            exit_reason = ""
            
            # Stop loss
            if strategy.stop_loss_pct and pnl_pct <= -strategy.stop_loss_pct:
                should_exit = True
                exit_reason = "Stop loss"
            
            # Take profit
            if strategy.take_profit_pct and pnl_pct >= strategy.take_profit_pct:
                should_exit = True
                exit_reason = "Take profit"
            
            # Exit position
            if should_exit:
                # Apply slippage
                fill_price = close_price * (1 - self.slippage_bps / 10000)
                
                # Calculate costs
                trade_value = fill_price * position
                commission = trade_value * self.commission_rate
                stamp_duty_cost = trade_value * self.stamp_duty
                
                # Execute sell
                self.cash += (trade_value - commission - stamp_duty_cost)
                
                # Update trade record
                trade.exit_time = day_data.index[-1]
                trade.exit_price = fill_price
                trade.profit_loss = (fill_price - trade.entry_price) * position
                trade.profit_loss_pct = pnl_pct
                trade.commission += commission + stamp_duty_cost
                
                # Move to completed trades
                self.trades.append(trade)
                del self.open_positions[symbol]
                del self.positions[symbol]
    
    def _calculate_portfolio_value(
        self,
        data_frames: Dict[str, pd.DataFrame],
        date: datetime,
    ) -> float:
        """
        Calculate total portfolio value
        
        Args:
            data_frames: Historical data
            date: Current date
        
        Returns:
            Total portfolio value
        """
        total = self.cash
        
        for symbol, quantity in self.positions.items():
            if symbol in data_frames:
                df = data_frames[symbol]
                day_data = df[df.index.date == date.date()]
                
                if not day_data.empty:
                    price = day_data.iloc[-1]['close']
                    total += price * quantity
        
        return total
    
    def _reset(self) -> None:
        """Reset backtest state"""
        self.cash = self.initial_capital
        self.positions = {}
        self.equity_curve = []
        self.trades = []
        self.open_positions = {}
    
    def _calculate_results(
        self,
        strategy_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> BacktestResult:
        """
        Calculate backtest results
        
        Args:
            strategy_name: Strategy name
            start_date: Start date
            end_date: End date
        
        Returns:
            Backtest results
        """
        final_capital = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Calculate daily returns
        daily_returns = []
        if len(self.equity_curve) > 1:
            for i in range(1, len(self.equity_curve)):
                daily_return = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
                daily_returns.append(daily_return)
        
        # Performance metrics
        sharpe = calculate_sharpe_ratio(daily_returns) if daily_returns else 0.0
        max_dd = calculate_max_drawdown(self.equity_curve) if self.equity_curve else 0.0
        max_dd_pct = abs(max_dd) * 100
        
        # Trade statistics
        win_rate_data = calculate_win_rate([{'profit_loss': t.profit_loss} for t in self.trades])
        
        # Calculate averages
        winning_trades = [t for t in self.trades if t.profit_loss > 0]
        losing_trades = [t for t in self.trades if t.profit_loss < 0]
        
        avg_win = sum(t.profit_loss for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        largest_win = max((t.profit_loss for t in winning_trades), default=0)
        largest_loss = min((t.profit_loss for t in losing_trades), default=0)
        
        # Average holding time
        holding_times = []
        for trade in self.trades:
            if trade.exit_time and trade.entry_time:
                hours = (trade.exit_time - trade.entry_time).total_seconds() / 3600
                holding_times.append(hours)
        
        avg_holding_time = sum(holding_times) / len(holding_times) if holding_times else 0
        
        # Volatility
        import numpy as np
        volatility = float(np.std(daily_returns) * np.sqrt(252)) if daily_returns else 0.0
        
        # VaR 95%
        var_95 = 0.0
        if daily_returns:
            sorted_returns = sorted(daily_returns)
            var_index = int(len(sorted_returns) * 0.05)
            var_95 = sorted_returns[var_index] if var_index < len(sorted_returns) else sorted_returns[0]
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            sharpe_ratio=sharpe,
            max_drawdown=abs(max_dd),
            max_drawdown_pct=max_dd_pct,
            win_rate=win_rate_data['win_rate'],
            profit_factor=win_rate_data['profit_factor'],
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            avg_holding_time=avg_holding_time,
            volatility=volatility,
            var_95=var_95,
            trades=self.trades,
            equity_curve=self.equity_curve,
            daily_returns=daily_returns,
        )
