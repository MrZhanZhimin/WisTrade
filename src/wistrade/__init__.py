"""
WisTrade - AI-Powered Stock Trading Automation Tool

A professional desktop application for automated stock trading
with AI-driven strategy generation and multi-broker support.
"""

__version__ = "0.1.0"
__author__ = "WisTrade Team"
__email__ = "team@wistrade.com"

from wistrade.core.config import Config
from wistrade.core.logger import get_logger

__all__ = ["Config", "get_logger", "__version__"]
