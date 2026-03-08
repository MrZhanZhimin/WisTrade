# WisTrade - AI-Powered Stock Trading Automation Tool

<div align="center">

![WisTrade Logo](docs/logo.png)

**智策AI交易大师 - Professional AI-Powered Stock Trading Automation**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[English](#english) | [简体中文](#简体中文)

</div>

---

## English

### Overview

**WisTrade** is a professional desktop AI-powered stock trading automation tool designed for Chinese retail investors. It provides intelligent stock selection, automated strategy generation, and fully autonomous trading across multiple broker accounts.

### Key Features

#### 🤖 AI-Powered Trading
- **GLM-4.7 Integration**: Advanced AI model for market analysis and strategy generation
- **Automatic Stock Selection**: AI-driven screening based on account permissions and available funds
- **Strategy Generation**: Automated quantitative strategy creation with risk management
- **Continuous Optimization**: Real-time strategy refinement based on trading performance

#### 💹 Multi-Broker Support
- **Seamless Broker Switching**: Support for 招商证券 (China Merchants), 光大证券 (Everbright), 江海证券
- **QMT Integration**: Unified interface via QMT/miniQMT platform
- **Multi-Account Management**: Simultaneous trading across multiple accounts
- **API Abstraction**: Easy extension to additional brokers

#### 📊 Real-Time Market Data
- **Multiple Data Sources**: AkShare, Tushare integration
- **Live Updates**: Real-time price feeds, K-line data, technical indicators
- **Historical Analysis**: Comprehensive historical data for backtesting
- **Market Scanning**: Automated market opportunity detection

#### 🎯 Automated Trading
- **24/7 Automation**: Fully autonomous trading without manual intervention
- **Risk Management**: Built-in position limits, stop-loss, take-profit
- **Order Management**: Smart order execution with real-time monitoring
- **Strategy Backtesting**: Validate strategies before deployment

#### 📈 Analytics & Reporting
- **Performance Metrics**: Win rate, ROI, Sharpe ratio, max drawdown
- **Visual Reports**: Charts and graphs for trading performance
- **Account Analysis**: Per-account performance breakdown
- **Export Options**: Excel and PDF report generation

#### ⚖️ Compliance & Security
- **Regulatory Compliance**: Adheres to Chinese securities regulations
- **Data Retention**: 5-year audit trail for trading logs
- **Encrypted Storage**: AES-256 encryption for credentials
- **Risk Controls**: Daily loss limits, position limits, rate limiting

### Technology Stack

- **Language**: Python 3.11+
- **GUI Framework**: PyQt6
- **AI Model**: GLM-4.7 (Zhipu AI)
- **Broker Integration**: QMT/miniQMT (XtQuant)
- **Database**: SQLite with SQLCipher encryption
- **Market Data**: AkShare, Tushare
- **Packaging**: PyInstaller

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DESKTOP UI LAYER                        │
│              PyQt6 + Real-time Charts                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   APPLICATION CORE                          │
│   Account Manager │ Risk Manager │ Notification Engine       │
└────┬───────────────┬─────────────┬──────────────────────────┘
     │               │             │
┌────▼────┐    ┌─────▼──────┐ ┌───▼────────┐
│AI Core  │    │Trading     │ │Data Layer  │
│(GLM-4.7)│    │Engine      │ │            │
└────┬────┘    └─────┬──────┘ └───┬────────┘
     │               │             │
     └───────────────┼─────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│              BROKER ABSTRACTION LAYER                       │
│        QMTAdapter │ BrokerAdapter Interface                 │
└─────────────────────────────────────────────────────────────┘
```

### Installation

#### Prerequisites
- Python 3.11 or higher
- QMT client (from your broker)
- Broker account with API access enabled

#### Quick Start

```bash
# Clone repository
git clone https://github.com/MrZhanZhimin/WisTrade.git
cd WisTrade

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and broker credentials

# Run application
python -m wistrade.main
```

#### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests

# Type checking
mypy src
```

### Configuration

1. **API Keys**: Set environment variables
   ```bash
   export ZHIPUAI_API_KEY="your_key_here"
   export TUSHARE_TOKEN="your_token_here"
   ```

2. **Broker Setup**: Configure in `config/settings.yaml`
   ```yaml
   brokers:
     default: "zhao_shang"
     zhao_shang:
       enabled: true
       qmt_path: "/path/to/qmt"
   ```

3. **Risk Parameters**: Adjust in `config/settings.yaml`
   ```yaml
   trading:
     risk:
       max_position_pct: 0.20
       max_daily_loss_pct: 0.05
   ```

### Usage

#### Starting the Application

```bash
python -m wistrade.main
```

#### Running Backtests

```bash
python -m wistrade.cli.backtest --strategy momentum --days 90
```

### Safety & Compliance

⚠️ **IMPORTANT DISCLAIMERS**

1. **Not Investment Advice**: This tool is for educational and research purposes only
2. **Trading Risks**: Stock trading involves substantial risk of loss
3. **Regulatory Compliance**: Ensure compliance with local securities regulations
4. **API Requirements**: Requires broker API access (may need minimum account balance)
5. **No Guarantees**: Past performance does not guarantee future results

**Risk Management**:
- Daily loss limits (default: 5%)
- Position size limits (default: 20% per stock)
- Order rate limits (avoid HFT classification)
- Mandatory stop-loss and take-profit

### Development Roadmap

- [x] Core architecture design
- [ ] Broker abstraction layer
- [ ] AI integration (GLM-4.7)
- [ ] Trading engine
- [ ] Desktop UI
- [ ] Backtesting system
- [ ] Analytics & reporting
- [ ] Multi-account management
- [ ] Strategy marketplace

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/MrZhanZhimin/WisTrade/issues)
- 💬 [Discussions](https://github.com/MrZhanZhimin/WisTrade/discussions)

---

## 简体中文

### 概述

**智策AI交易大师 (WisTrade)** 是一款专业的桌面端AI智能炒股自动化工具，专为国内散户投资者设计。提供智能选股、自动化策略生成、多账户全自主交易等功能。

### 核心特性

#### 🤖 AI智能交易
- **GLM-4.7集成**：先进的AI模型进行市场分析和策略生成
- **自动选股**：基于账户权限和可用资金的AI驱动筛选
- **策略生成**：自动生成量化策略，内置风险管理
- **持续优化**：基于交易表现的实时策略优化

#### 💹 多券商支持
- **无缝切换**：支持招商证券、光大证券、江海证券
- **QMT集成**：通过QMT/miniQMT平台统一接口
- **多账户管理**：同时管理多个账户的交易
- **API抽象**：易于扩展到其他券商

#### 📊 实时行情数据
- **多数据源**：集成AkShare、Tushare
- **实时更新**：实时价格、K线数据、技术指标
- **历史分析**：全面的历史数据用于回测
- **市场扫描**：自动检测市场机会

#### 🎯 自动化交易
- **7x24自动化**：完全自主交易，无需人工干预
- **风险管理**：内置仓位限制、止损、止盈
- **订单管理**：智能订单执行，实时监控
- **策略回测**：部署前验证策略

#### 📈 分析与报告
- **性能指标**：胜率、收益率、夏普比率、最大回撤
- **可视化报告**：交易表现图表
- **账户分析**：每个账户的绩效分析
- **导出选项**：Excel和PDF报告生成

#### ⚖️ 合规与安全
- **监管合规**：遵循中国证券法规
- **数据留存**：5年交易日志审计追踪
- **加密存储**：AES-256凭证加密
- **风险控制**：每日亏损限制、仓位限制、频率限制

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/MrZhanZhimin/WisTrade.git
cd WisTrade

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥和券商凭证

# 运行应用
python -m wistrade.main
```

### 风险提示

⚠️ **重要声明**

1. **非投资建议**：本工具仅供教育和研究使用
2. **交易风险**：股票交易存在重大损失风险
3. **合规要求**：请确保遵守当地证券法规
4. **API要求**：需要券商API权限（可能需要最低账户余额）
5. **无收益保证**：过往业绩不代表未来表现

### 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">

**Built with ❤️ by WisTrade Team**

</div>
