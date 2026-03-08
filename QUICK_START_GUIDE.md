# WisTrade 快速启动指南

**当前时间**: 2026-03-08  
**版本**: v0.1.0

---

## 🚀 快速启动步骤

### 第一步：环境准备

**检查Python版本**：
```bash
python3 --version
```

**要求**：
- ✅ Python 3.11+ （推荐）
- ⚠️ Python 3.8+ （最低）
- ❌ Python 3.7 及以下（不支持）

---

### 第二步：创建虚拟环境

**如果使用 Python 3.11+**：
```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

**如果使用 Python 3.8+**：
```bash
python3.10 -m venv venv  # 或 python3.9
source venv/bin/activate
```

---

### 第三步：安装依赖

**完整安装（包含GUI）**：
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**最小安装（仅后端，无GUI）**：
```bash
pip install -r requirements-minimal.txt
```

---

### 第四步：配置环境变量

**1. 复制配置模板**：
```bash
cp .env.example .env
```

**2. 编辑 `.env` 文件**，填入以下必需信息：

```bash
# AI服务密钥（必需）
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# 数据库加密密码（必需）
DB_ENCRYPTION_KEY=请设置一个32位以上的强密码

# 安全密钥（必需）
SECRET_KEY=请运行以下命令生成：
# python -c "import secrets; print(secrets.token_urlsafe(32))"

# 数据源Token（可选）
TUSHARE_TOKEN=your_tushare_token_here
```

**获取密钥**：
- **智谱AI**: https://open.bigmodel.cn/ （新用户送免费额度）
- **Tushare**: https://tushare.pro/ （可选，免费版有积分限制）

---

### 第五步：启动应用

**方式1：使用启动脚本（推荐）**
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

**方式2：直接运行**
```bash
python -m wistrade.main
```

**方式3：测试后端（无GUI）**
```bash
python scripts/test_imports.py
```

---

## 📖 功能说明

### 主要功能

1. **仪表盘**
   - 账户概览（总资产、持仓市值、可用资金）
   - 持仓列表（股票、数量、成本、现价、盈亏）
   - 实时行情（自选股价格和涨跌幅）
   - 资产曲线（30天资产变化趋势）

2. **交易**
   - 股票搜索和选择
   - K线图查看（日K、周K、月K）
   - 买入/卖出下单
   - 订单管理（当前委托、成交记录）
   - AI策略推荐

3. **分析**
   - 绩效指标（收益率、夏普比率、最大回撤）
   - 收益曲线（策略 vs 基准对比）
   - 月度热力图
   - 持仓分布
   - 交易统计

4. **AI助手**
   - 市场分析（AI分析当前市场）
   - 选股推荐（基于偏好的股票推荐）
   - 策略生成（自动生成交易策略）
   - 风险预警（检查持仓风险）
   - 自由对话（问答式交互）

5. **设置**
   - 账户管理（券商配置）
   - AI设置（模型、参数）
   - 交易设置（订单类型、超时）
   - 风险控制（仓位限制、止损止盈）
   - 数据源（AkShare/Tushare切换）
   - 通知设置
   - 外观设置

---

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+1` | 仪表盘 |
| `Ctrl+2` | 交易页面 |
| `Ctrl+3` | 分析页面 |
| `Ctrl+4` | AI助手 |
| `Ctrl+5` | 设置 |
| `Ctrl+R` | 刷新数据 |
| `Ctrl+S` | 保存配置 |
| `F5` | 刷新行情 |
| `Esc` | 关闭弹窗 |

---

## 🔧 配置说明

### 主要配置文件

1. **`.env`** - 环境变量（API密钥等）
2. **`config/settings.yaml`** - 应用配置
3. **`logs/wistrade.log`** - 运行日志

### 重要配置项

#### AI配置
```yaml
ai:
  provider: "zhipuai"
  model: "glm-4-plus"  # 推荐使用Plus版本
  temperature: 0.7     # 创造性 (0-1)
  max_tokens: 4000     # 最大生成长度
```

#### 风险控制
```yaml
trading:
  risk:
    max_position_pct: 0.20      # 单股最大仓位20%
    max_daily_loss_pct: 0.05    # 日最大亏损5%
    enable_auto_stop_loss: true  # 自动止损
    enable_auto_take_profit: true  # 自动止盈
```

#### 数据源
```yaml
market_data:
  providers:
    - "akshare"  # 免费
    - "tushare"  # 需要Token
```

---

## 🐛 常见问题

### Q1: 提示"Python版本过低"
**解决**: 升级到Python 3.8+或3.11+
```bash
# macOS使用Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Windows从python.org下载安装
```

### Q2: 无法安装PyQt6
**原因**: 缺少Qt环境或Python版本过低
**解决**: 
- 确保Python 3.8+
- 在有GUI的环境安装
- macOS: `brew install qt`
- Linux: `sudo apt install qt6-base-dev`

### Q3: 提示"缺少依赖"
**解决**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Q4: AI功能无响应
**检查**:
1. `.env`文件中是否配置了`ZHIPUAI_API_KEY`
2. API密钥是否有效
3. 网络是否可访问智谱AI
4. 查看日志: `logs/wistrade.log`

### Q5: 无法连接券商
**检查**:
1. QMT客户端是否已启动
2. 账户ID是否正确
3. 是否开通API权限
4. 网络连接是否正常

---

## ⚠️ 风险提示

### 重要声明

**本工具仅供教育和研究使用，不构成投资建议。**

### 风险须知

1. **市场风险**: 股票价格波动可能导致损失
2. **流动性风险**: 可能无法及时卖出股票
3. **系统风险**: 技术故障可能导致交易失败
4. **策略风险**: AI策略可能判断失误

### 使用建议

✅ 充分了解风险后再使用  
✅ 从小额资金开始测试  
✅ 定期检查账户和策略  
✅ 设置合理的止损止盈  
✅ 不要投入超过承受能力的资金  

### 禁止事项

❌ 不要使用借贷资金交易  
❌ 不要忽视风险警告  
❌ 不要盲目信任AI推荐  
❌ 不要在无人看管时长时间运行  
❌ 不要违反当地证券法规  

---

## 📞 技术支持

### 获取帮助

- **GitHub Issues**: https://github.com/MrZhanZhimin/WisTrade/issues
- **GitHub Discussions**: https://github.com/MrZhanZhimin/WisTrade/discussions
- **项目文档**: `docs/` 目录
- **用户手册**: `docs/USER_MANUAL.md`

### 查看日志

**日志位置**: `logs/wistrade.log`

**查看最新日志**：
```bash
tail -f logs/wistrade.log
```

**搜索错误**：
```bash
grep ERROR logs/wistrade.log
```

---

## 📊 项目结构

```
WisTrade/
├── src/wistrade/          # 源代码
│   ├── ui/                # 用户界面
│   ├── ai/                # AI服务
│   ├── brokers/           # 券商接口
│   ├── trading/           # 交易引擎
│   ├── data/              # 数据服务
│   ├── storage/           # 存储系统
│   └── core/              # 核心功能
├── config/                # 配置文件
├── docs/                  # 文档
├── tests/                 # 测试
├── scripts/               # 脚本
├── logs/                  # 日志
├── data/                  # 数据
├── .env                   # 环境变量
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明
```

---

## ✅ 验证安装

运行以下命令验证安装是否成功：

```bash
# 1. 检查Python版本
python3 --version  # 应该 >= 3.8

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 测试导入
python scripts/test_imports.py

# 4. 检查依赖
python scripts/check_dependencies.py

# 5. 启动应用
python -m wistrade.main
```

---

## 🎉 开始使用

一切准备就绪后：

1. **配置账户**: 在设置页面添加券商账户
2. **配置AI**: 填入智谱AI密钥
3. **查看行情**: 在仪表盘查看持仓和行情
4. **AI分析**: 使用AI助手进行市场分析
5. **开始交易**: 在交易页面下单

---

**祝您使用愉快！**

*WisTrade Team © 2024*
