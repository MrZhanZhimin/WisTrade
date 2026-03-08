"""
Broker abstraction layer for WisTrade

Provides unified interface for multiple Chinese securities brokers.
"""

from wistrade.brokers.base import BrokerAdapter, BrokerConfig, OrderSide, OrderType
from wistrade.brokers.qmt import QMTAdapter

__all__ = [
    "BrokerAdapter",
    "BrokerConfig",
    "OrderSide",
    "OrderType",
    "QMTAdapter",
]
