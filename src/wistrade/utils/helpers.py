"""
Helper functions for WisTrade
"""

import hashlib
import re
import uuid
from datetime import datetime
from typing import Optional


def generate_order_id() -> str:
    """
    Generate unique order ID
    
    Returns:
        UUID-based order ID
    """
    return str(uuid.uuid4())


def calculate_pnl(
    entry_price: float,
    exit_price: float,
    quantity: int,
    side: str = "BUY",
    commission: float = 0.0,
) -> dict:
    """
    Calculate profit/loss for a trade
    
    Args:
        entry_price: Entry price per share
        exit_price: Exit price per share
        quantity: Number of shares
        side: BUY or SELL
        commission: Total commission fees
    
    Returns:
        Dictionary with P&L metrics
    """
    if side.upper() == "BUY":
        # Long position
        gross_pnl = (exit_price - entry_price) * quantity
    else:
        # Short position
        gross_pnl = (entry_price - exit_price) * quantity
    
    net_pnl = gross_pnl - commission
    pnl_pct = (net_pnl / (entry_price * quantity)) * 100 if entry_price > 0 else 0
    
    return {
        'gross_pnl': gross_pnl,
        'net_pnl': net_pnl,
        'pnl_pct': pnl_pct,
        'total_cost': entry_price * quantity + commission,
        'total_value': exit_price * quantity,
    }


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
    
    Returns:
        True if valid
    """
    # Chinese A-share format: 6 digits, optionally with .SZ or .SH suffix
    pattern = r'^\d{6}(\.(SZ|SH|BJ))?$'
    return bool(re.match(pattern, symbol))


def mask_sensitive_data(data: str, show_length: int = 4) -> str:
    """
    Mask sensitive data for logging/display
    
    Args:
        data: Sensitive data string
        show_length: Number of characters to show at start and end
    
    Returns:
        Masked string
    
    Example:
        mask_sensitive_data("1234567890", 2) -> "12******90"
    """
    if len(data) <= show_length * 2:
        return "*" * len(data)
    
    return data[:show_length] + "*" * (len(data) - show_length * 2) + data[-show_length:]


def format_currency(amount: float, currency: str = "CNY") -> str:
    """
    Format currency amount with proper formatting
    
    Args:
        amount: Amount to format
        currency: Currency code
    
    Returns:
        Formatted currency string
    """
    if currency == "CNY":
        return f"¥{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_sharpe_ratio(
    returns: list,
    risk_free_rate: float = 0.03,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate Sharpe ratio for strategy performance
    
    Args:
        returns: List of period returns (as decimals)
        risk_free_rate: Annual risk-free rate (default 3%)
        periods_per_year: Number of periods in a year (252 for daily)
    
    Returns:
        Sharpe ratio
    """
    if not returns:
        return 0.0
    
    import numpy as np
    
    returns_array = np.array(returns)
    excess_returns = returns_array - (risk_free_rate / periods_per_year)
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)
    return float(sharpe)


def calculate_max_drawdown(equity_curve: list) -> float:
    """
    Calculate maximum drawdown from equity curve
    
    Args:
        equity_curve: List of portfolio values over time
    
    Returns:
        Maximum drawdown as decimal (e.g., -0.20 for 20% drawdown)
    """
    if not equity_curve:
        return 0.0
    
    import numpy as np
    
    equity_array = np.array(equity_curve)
    peak = np.maximum.accumulate(equity_array)
    drawdown = (equity_array - peak) / peak
    
    return float(np.min(drawdown))


def calculate_win_rate(trades: list) -> dict:
    """
    Calculate win rate and related metrics
    
    Args:
        trades: List of trade dictionaries with 'profit_loss' key
    
    Returns:
        Dictionary with win rate metrics
    """
    if not trades:
        return {
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0,
        }
    
    winning = [t for t in trades if t.get('profit_loss', 0) > 0]
    losing = [t for t in trades if t.get('profit_loss', 0) < 0]
    
    total_trades = len(trades)
    winning_trades = len(winning)
    losing_trades = len(losing)
    
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    avg_win = sum(t['profit_loss'] for t in winning) / winning_trades if winning_trades > 0 else 0
    avg_loss = sum(t['profit_loss'] for t in losing) / losing_trades if losing_trades > 0 else 0
    
    total_wins = sum(t['profit_loss'] for t in winning)
    total_losses = abs(sum(t['profit_loss'] for t in losing))
    profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
    
    return {
        'win_rate': win_rate,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
    }


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """
    Hash data using specified algorithm
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (sha256, sha512, md5)
    
    Returns:
        Hex digest of hash
    """
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def timestamp_to_datetime(timestamp: int, unit: str = "ms") -> datetime:
    """
    Convert timestamp to datetime
    
    Args:
        timestamp: Unix timestamp
        unit: Unit of timestamp (ms, s)
    
    Returns:
        Datetime object
    """
    if unit == "ms":
        timestamp = timestamp / 1000
    
    return datetime.fromtimestamp(timestamp)
