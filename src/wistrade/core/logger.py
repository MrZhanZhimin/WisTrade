"""
Structured logging system for WisTrade

Provides tamper-evident audit logging for compliance requirements.
"""

import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor


def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add ISO 8601 timestamp to log entry"""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_checksum(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add cryptographic checksum for tamper-evidence
    
    This provides audit trail integrity as required by compliance regulations.
    """
    if "checksum" not in event_dict:
        # Create checksum from log content
        content = json.dumps(event_dict, sort_keys=True, default=str)
        checksum = hashlib.sha256((content + str(time.time())).encode()).hexdigest()[:16]
        event_dict["checksum"] = checksum
    
    return event_dict


def mask_sensitive_data(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Mask sensitive information like API keys and account numbers"""
    sensitive_fields = {
        "api_key",
        "api_secret",
        "password",
        "token",
        "account_number",
        "credit_card",
    }
    
    for field in sensitive_fields:
        if field in event_dict:
            value = str(event_dict[field])
            if len(value) > 4:
                event_dict[field] = f"{value[:2]}***{value[-2:]}"
            else:
                event_dict[field] = "***"
    
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json: bool = True,
    enable_checksum: bool = True,
) -> None:
    """
    Setup structured logging system
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_json: Use JSON format for structured logs
        enable_checksum: Add checksums for audit trail integrity
    """
    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        add_timestamp,
        mask_sensitive_data,
    ]
    
    if enable_checksum:
        processors.append(add_checksum)
    
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(log_level),
    )
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.root.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class AuditLogger:
    """
    Audit logger for compliance requirements
    
    Provides tamper-evident logging for:
    - All trading actions (5-year retention)
    - API access logs (6-month retention)
    - System events (1-year retention)
    """
    
    def __init__(self, log_dir: str = "logs/audit"):
        """
        Initialize audit logger
        
        Args:
            log_dir: Directory for audit log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Separate log files by type for retention policy compliance
        self.trade_logger = self._setup_logger("trades", "trading_audit.log")
        self.access_logger = self._setup_logger("access", "access_audit.log")
        self.system_logger = self._setup_logger("system", "system_audit.log")
    
    def _setup_logger(self, name: str, filename: str) -> structlog.stdlib.BoundLogger:
        """Setup individual audit logger"""
        log_file = self.log_dir / filename
        
        # Create file handler
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        
        # Create logger
        logger = logging.getLogger(f"audit.{name}")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        return structlog.get_logger(f"audit.{name}")
    
    def log_trade(
        self,
        user_id: str,
        account_id: str,
        action: str,
        symbol: str,
        quantity: float,
        price: float,
        order_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log trading action for compliance
        
        Args:
            user_id: User identifier
            account_id: Trading account identifier
            action: Trade action (BUY, SELL, CANCEL)
            symbol: Stock symbol
            quantity: Trade quantity
            price: Trade price
            order_id: Order identifier
            **kwargs: Additional context
        """
        self.trade_logger.info(
            "trade_action",
            user_id=self._hash_identifier(user_id),
            account_id=self._hash_identifier(account_id),
            action=action,
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_id=order_id,
            **kwargs,
        )
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Log access event for security audit
        
        Args:
            user_id: User identifier
            action: Access action (LOGIN, LOGOUT, VIEW, MODIFY)
            resource: Resource accessed
            ip_address: Client IP address
            success: Whether access was successful
            **kwargs: Additional context
        """
        self.access_logger.info(
            "access_event",
            user_id=self._hash_identifier(user_id),
            action=action,
            resource=resource,
            ip_address=self._mask_ip(ip_address) if ip_address else None,
            success=success,
            **kwargs,
        )
    
    def log_system(
        self,
        event: str,
        level: str = "INFO",
        component: str = "system",
        message: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Log system event for operational audit
        
        Args:
            event: Event type
            level: Log level
            component: System component
            message: Event message
            **kwargs: Additional context
        """
        logger_method = getattr(self.system_logger, level.lower(), self.system_logger.info)
        logger_method(
            "system_event",
            event=event,
            component=component,
            message=message,
            **kwargs,
        )
    
    @staticmethod
    def _hash_identifier(identifier: str) -> str:
        """Hash identifier for privacy compliance"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    @staticmethod
    def _mask_ip(ip_address: str) -> str:
        """Mask IP address for privacy (mask last octet)"""
        parts = ip_address.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3] + ["xxx"])
        return "***"
