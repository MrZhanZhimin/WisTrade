"""
Tests for WisTrade core functionality
"""

import pytest
from datetime import datetime

from wistrade.brokers.base import (
    BrokerConfig,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    AccountInfo,
    Position,
    MarketData,
)
from wistrade.utils.helpers import (
    generate_order_id,
    validate_symbol,
    mask_sensitive_data,
    calculate_pnl,
)


class TestBrokerModels:
    """Test broker data models"""
    
    def test_broker_config_creation(self):
        """Test BrokerConfig model creation"""
        config = BrokerConfig(
            broker_id="zhao_shang",
            broker_name="招商证券",
            broker_type="qmt",
            enabled=True,
        )
        
        assert config.broker_id == "zhao_shang"
        assert config.broker_name == "招商证券"
        assert config.broker_type == "qmt"
        assert config.enabled is True
    
    def test_order_creation(self):
        """Test Order model creation"""
        order = Order(
            order_id="12345",
            client_order_id="client_123",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=10.50,
        )
        
        assert order.order_id == "12345"
        assert order.symbol == "000001.SZ"
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.PENDING
    
    def test_account_info_creation(self):
        """Test AccountInfo model creation"""
        account = AccountInfo(
            account_id="test_account",
            broker_id="zhao_shang",
            total_assets=100000.0,
            available_cash=50000.0,
            market_value=50000.0,
        )
        
        assert account.account_id == "test_account"
        assert account.total_assets == 100000.0
        assert account.currency == "CNY"
    
    def test_position_creation(self):
        """Test Position model creation"""
        position = Position(
            symbol="000001.SZ",
            quantity=1000,
            available_quantity=1000,
            avg_cost=10.0,
            current_price=11.0,
            market_value=11000.0,
            profit_loss=1000.0,
            profit_loss_pct=10.0,
            account_id="test_account",
        )
        
        assert position.symbol == "000001.SZ"
        assert position.quantity == 1000
        assert position.profit_loss == 1000.0
    
    def test_market_data_creation(self):
        """Test MarketData model creation"""
        data = MarketData(
            symbol="000001.SZ",
            name="平安银行",
            current_price=10.50,
            open_price=10.30,
            high_price=10.60,
            low_price=10.20,
            previous_close=10.25,
            volume=1000000,
            turnover=10500000.0,
        )
        
        assert data.symbol == "000001.SZ"
        assert data.current_price == 10.50
        assert data.volume == 1000000


class TestUtils:
    """Test utility functions"""
    
    def test_generate_order_id(self):
        """Test order ID generation"""
        order_id = generate_order_id()
        
        assert isinstance(order_id, str)
        assert len(order_id) > 0
        assert order_id.startswith("ORD-")
    
    def test_generate_order_id_uniqueness(self):
        """Test order ID uniqueness"""
        ids = [generate_order_id() for _ in range(100)]
        
        assert len(set(ids)) == 100  # All unique
    
    def test_validate_symbol_valid(self):
        """Test symbol validation with valid symbols"""
        assert validate_symbol("000001.SZ") is True
        assert validate_symbol("600000.SH") is True
        assert validate_symbol("000002") is True
    
    def test_validate_symbol_invalid(self):
        """Test symbol validation with invalid symbols"""
        assert validate_symbol("") is False
        assert validate_symbol("ABC") is False
        assert validate_symbol("123") is False
    
    def test_mask_sensitive_data(self):
        """Test sensitive data masking"""
        # Test API key masking
        masked = mask_sensitive_data("abcd1234efgh5678", show_length=4)
        assert masked == "ab***78"
        assert "***" in masked
        assert "1234" not in masked
    
    def test_calculate_pnl(self):
        """Test P&L calculation"""
        pnl = calculate_pnl(
            entry_price=10.0,
            exit_price=11.0,
            quantity=100,
        )
        
        assert pnl['profit_loss'] == 100.0
        assert pnl['profit_loss_pct'] == 10.0
    
    def test_calculate_pnl_loss(self):
        """Test P&L calculation with loss"""
        pnl = calculate_pnl(
            entry_price=10.0,
            exit_price=9.0,
            quantity=100,
        )
        
        assert pnl['profit_loss'] == -100.0
        assert pnl['profit_loss_pct'] == -10.0


class TestConfig:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        from wistrade.core.config import Config
        
        config = Config()
        app_config = config.load()
        
        assert app_config.name == "WisTrade"
        assert app_config.version == "0.1.0"
    
    def test_config_defaults(self):
        """Test configuration defaults"""
        from wistrade.core.config import Config
        
        config = Config()
        app_config = config.config
        
        assert app_config.ai.provider == "zhipuai"
        assert app_config.ai.model == "glm-4-plus"
        assert app_config.trading.risk.max_position_pct == 0.20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
