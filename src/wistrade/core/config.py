"""
Configuration management for WisTrade
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AIConfig(BaseModel):
    """AI service configuration"""

    provider: str = "zhipuai"
    model: str = "glm-4-plus"
    api_key_env: str = "ZHIPUAI_API_KEY"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    retry_attempts: int = 3


class BrokerConfig(BaseModel):
    """Individual broker configuration"""

    name: str
    type: str = "qmt"
    enabled: bool = True
    qmt_path: str = ""
    account_min_assets: int = 100000


class RiskConfig(BaseModel):
    """Risk management configuration"""

    max_position_pct: float = 0.20
    max_daily_loss_pct: float = 0.05
    max_sector_exposure_pct: float = 0.40
    max_orders_per_second: int = 40
    max_orders_per_day: int = 3000
    enable_auto_stop_loss: bool = True
    enable_auto_take_profit: bool = True


class TradingConfig(BaseModel):
    """Trading engine configuration"""

    default_order_type: str = "limit"
    order_timeout: int = 30
    risk: RiskConfig = Field(default_factory=RiskConfig)


class DatabaseConfig(BaseModel):
    """Database configuration"""

    type: str = "sqlite"
    path: str = "data/wistrade.db"
    encryption_enabled: bool = True
    pool_size: int = 10
    pool_timeout: int = 30


class AppConfig(BaseModel):
    """Application configuration"""

    name: str = "WisTrade"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    ai: AIConfig = Field(default_factory=AIConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    brokers: Dict[str, BrokerConfig] = Field(default_factory=dict)


class Config:
    """
    Configuration manager for WisTrade
    
    Loads configuration from YAML file and environment variables.
    Provides type-safe access to configuration values.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        self._config_path = config_path or self._find_config_file()
        self._config: Optional[AppConfig] = None
        self._raw_config: Dict[str, Any] = {}

    def _find_config_file(self) -> str:
        """Find configuration file in standard locations"""
        search_paths = [
            Path.cwd() / "config" / "settings.yaml",
            Path.cwd() / "settings.yaml",
            Path.home() / ".wistrade" / "settings.yaml",
            Path(__file__).parent.parent.parent.parent / "config" / "settings.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return str(path)

        # Return default path even if it doesn't exist
        return str(search_paths[0])

    def load(self) -> AppConfig:
        """
        Load configuration from YAML file
        
        Returns:
            AppConfig: Loaded configuration object
        """
        if self._config is not None:
            return self._config

        # Load YAML file
        config_file = Path(self._config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self._raw_config = yaml.safe_load(f) or {}
        else:
            # Use defaults if no config file found
            self._raw_config = {}

        # Parse into typed config
        app_config = self._raw_config.get("app", {})
        self._config = AppConfig(**app_config)

        return self._config

    @property
    def config(self) -> AppConfig:
        """Get loaded configuration"""
        if self._config is None:
            self.load()
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key
        
        Args:
            key: Dot-notation key (e.g., "ai.model")
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._raw_config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable value
        
        Args:
            key: Environment variable name
            default: Default value if not set
        
        Returns:
            Environment variable value
        """
        return os.environ.get(key, default)

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service
        
        Args:
            service: Service name (e.g., "zhipuai", "tushare")
        
        Returns:
            API key or None
        """
        env_var = f"{service.upper()}_API_KEY"
        return self.get_env(env_var)

    def reload(self) -> AppConfig:
        """
        Reload configuration from file
        
        Returns:
            Reloaded configuration object
        """
        self._config = None
        return self.load()


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get global configuration instance
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
        _config.load()
    return _config
