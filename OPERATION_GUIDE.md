# WisTrade 操作手册 - 当前系统版

**当前系统检测**: macOS, Python 3.7.4  
**更新时间**: 2026-03-08 23:51

---

## ⚠️ 当前系统限制

### 检测到的问题
- **Python版本**: 3.7.4（过低）
- **要求**: Python 3.11+（推荐）或 3.8+（最低）
- **影响**: 无法安装部分依赖（openai>=1.0.0, akshare等）

### 解决方案

#### 方案1: 升级Python（推荐）

**macOS使用Homebrew**:
```bash
# 安装Python 3.11
brew install python@3.11

# 创建新虚拟环境
python3.11 -m venv venv311
source venv311/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python -m wistrade.main
```

**或下载官方安装包**:
- 访问: https://www.python.org/downloads/
- 下载 Python 3.11+ 安装包
- 安装后重新创建虚拟环境

#### 方案2: 使用Docker（跨平台）

```bash
# 拉取镜像
docker pull python:3.11-slim

# 运行容器
docker run -it -v $(pwd):/app python:3.11-slim bash

# 在容器内
cd /app
pip install -r requirements.txt
python -m wistrade.main
```

#### 方案3: 仅测试后端功能

使用最小依赖（无GUI）：
```bash
source venv/bin/activate
pip install -r requirements-minimal.txt
python scripts/test_imports.py
```

---

## 🚀 完整启动流程（Python 3.11+）

### 步骤1: 环境准备

```bash
# 1. 检查Python版本（需要>=3.8）
python3 --version

# 2. 如果有Python 3.11+
python3.11 --version
```

### 步骤2: 创建虚拟环境

```bash
# 使用Python 3.11创建
python3.11 -m venv venv311

# 激活
source venv311/bin/activate  # macOS/Linux
# 或
venv311\Scripts\activate  # Windows
```

### 步骤3: 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装所有依赖（包含PyQt6）
pip install -r requirements.txt
```

**如果PyQt6安装失败**（服务器环境）：
```bash
# 安装最小依赖
pip install -r requirements-minimal.txt
```

### 步骤4: 配置环境

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑配置（使用任意文本编辑器）
nano .env
# 或
vim .env
# 或
open -a "Visual Studio Code" .env
```

**必需配置**:
```bash
# AI服务密钥（必需）
ZHIPUAI_API_KEY=your_zhipuai_api_key_here

# 数据库加密密码（必需，请设置强密码）
DB_ENCRYPTION_KEY=设置一个32位以上的强密码

# 安全密钥（必需）
SECRET_KEY=运行下面命令生成：
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**可选配置**:
```bash
# Tushare Token（可选）
TUSHARE_TOKEN=your_tushare_token_here
```

**获取密钥**:
1. **智谱AI**: https://open.bigmodel.cn/
   - 注册账号
   - 进入"API密钥管理"
   - 创建新密钥
   - 新用户赠送免费额度

2. **Tushare**（可选）: https://tushare.pro/
   - 注册账号
   - 进入"个人中心"
   - 获取Token

### 步骤5: 启动应用

**方式1: 使用启动脚本**
```bash
# macOS/Linux
chmod +x start.sh
./start.sh

# Windows
start.bat
```

**方式2: 直接运行**
```bash
# 确保虚拟环境已激活
source venv311/bin/activate

# 启动应用
python -m wistrade.main
```

**方式3: 测试模式（无GUI）**
```bash
# 测试模块导入
python scripts/test_imports.py

# 检查依赖
python scripts/check_dependencies.py
```

---

## 📖 应用功能指南

### 主界面布局

```
┌─────────────────────────────────────────────────┐
│ 顶部栏: Logo | 账户 | 连接状态 | 时间      │
├─────────────────────────────────────────────────┤
│ [仪表盘] [交易] [分析] [AI助手] [设置]  ← 标签页 │
│                                                 │
│              主内容区域                          │
│          (根据标签页切换)                        │
│                                                 │
├─────────────────────────────────────────────────┤
│ 底部状态栏: 状态信息 | 通知                      │
└─────────────────────────────────────────────────┘
```

### 功能模块

#### 1. 仪表盘（Dashboard）

**功能**:
- 账户概览（4个统计卡片）
  - 总资产
  - 今日盈亏
  - 持仓市值
  - 可用资金

- 持仓列表
  - 股票代码和名称
  - 持仓数量
  - 成本价和现价
  - 盈亏金额和百分比
  - 卖出按钮

**使用**:
1. 点击顶部"仪表盘"标签
2. 查看账户总览
3. 查看持仓详情
4. 点击"刷新"更新数据

#### 2. 交易（Trading）

**功能**:
- 股票搜索
- K线图查看
- 买入/卖出下单
- 订单管理
- AI策略执行

**使用**:
1. 搜索股票代码或名称
2. 查看K线图和技术指标
3. 填写买入/卖出表单
4. 确认下单
5. 在订单管理查看状态

#### 3. 分析（Analytics）

**功能**:
- 绩效指标
  - 总收益率
  - 年化收益
  - 夏普比率
  - 最大回撤
- 收益曲线
- 月度热力图
- 持仓分布
- 交易统计

**使用**:
1. 选择时间范围
2. 查看各项指标
3. 分析收益曲线
4. 导出报告

#### 4. AI助手（AI Assistant）

**功能**:
- 市场分析（AI分析当前市场）
- 选股推荐（基于偏好推荐股票）
- 策略生成（自动生成交易策略）
- 风险预警（检查持仓风险）
- 自由对话（问答式交互）

**使用**:
1. 点击快捷功能按钮
2. 或在输入框输入问题
3. 按回车或点击"发送"
4. 查看AI回复

**提示词示例**:
- "分析一下平安银行的投资价值"
- "推荐几只低估值银行股"
- "帮我生成一个稳健的交易策略"
- "我的持仓有什么风险？"

#### 5. 设置（Settings）

**左侧导航**:
- 账户管理
- AI设置
- 交易设置
- 风险控制
- 数据源
- 通知设置
- 外观设置
- 关于

**使用**:
1. 点击左侧导航项
2. 修改右侧的配置
3. 点击"保存"按钮
4. 配置立即生效

---

## ⌨️ 快捷键参考

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl+1` | 仪表盘 | 快速切换到仪表盘 |
| `Ctrl+2` | 交易 | 快速切换到交易页面 |
| `Ctrl+3` | 分析 | 快速切换到分析页面 |
| `Ctrl+4` | AI助手 | 快速切换到AI助手 |
| `Ctrl+5` | 设置 | 快速切换到设置 |
| `Ctrl+R` | 刷新数据 | 刷新当前页面数据 |
| `Ctrl+S` | 保存配置 | 保存当前配置（设置页面） |
| `F5` | 刷新行情 | 刷新实时行情数据 |
| `Esc` | 关闭弹窗 | 关闭当前弹窗或对话框 |

---

## 🔧 高级配置

### 配置文件位置

```
config/
├── settings.yaml      # 主配置文件
└── logging.yaml       # 日志配置（可选）

.env                   # 环境变量
```

### 主要配置项

#### AI配置
```yaml
ai:
  provider: "zhipuai"
  model: "glm-4-plus"  # glm-4, glm-4-plus, glm-4-flash
  temperature: 0.7     # 0-1，越大越有创造性
  max_tokens: 4000     # 最大生成长度
  timeout: 60          # 超时时间（秒）
  
  agent:
    max_iterations: 10
    enable_reflection: true
    reasoning_pattern: "react"
```

#### 交易配置
```yaml
trading:
  default_order_type: "limit"  # limit | market
  order_timeout: 30
  
  risk:
    max_position_pct: 0.20      # 单股最大仓位
    max_daily_loss_pct: 0.05    # 日最大亏损
    max_sector_exposure_pct: 0.40  # 单板块最大敞口
    max_orders_per_second: 40   # 每秒最大订单
    max_orders_per_day: 3000    # 每日最大订单
    enable_auto_stop_loss: true
    enable_auto_take_profit: true
```

#### 数据源配置
```yaml
market_data:
  providers:
    - "akshare"   # 免费数据源
    - "tushare"   # 付费数据源
  
  cache:
    enabled: true
    max_age_hours: 6
    max_size_mb: 500
```

#### UI配置
```yaml
ui:
  theme: "dark"  # dark | light
  language: "zh_CN"  # zh_CN | en_US
  window:
    width: 1600
    height: 900
    maximized_on_start: true
```

---

## 🐛 故障排查

### 常见错误

#### 错误1: "ModuleNotFoundError: No module named 'PyQt6'"
**原因**: PyQt6未安装或Python版本过低  
**解决**:
```bash
# 检查Python版本
python --version  # 需要 >= 3.8

# 安装PyQt6
pip install PyQt6 pyqtgraph
```

#### 错误2: "No module named 'wistrade'"
**原因**: 未在项目根目录或未安装包  
**解决**:
```bash
# 确保在项目根目录
cd /path/to/WisTrade

# 或安装为包
pip install -e .
```

#### 错误3: "AI服务无响应"
**检查清单**:
1. `.env`中`ZHIPUAI_API_KEY`是否设置
2. API密钥是否有效（登录智谱AI查看）
3. 网络是否可访问 https://open.bigmodel.cn/
4. 查看日志: `tail -f logs/wistrade.log`

#### 错误4: "无法连接券商"
**检查清单**:
1. QMT客户端是否启动
2. 账户ID是否正确
3. 是否开通API权限
4. QMT路径是否正确配置

#### 错误5: "行情数据获取失败"
**解决**:
```bash
# 检查网络
ping baidu.com

# 清除缓存
rm -rf data/cache/*

# 检查AkShare
python -c "import akshare as ak; print(ak.stock_zh_a_spot_em())"
```

### 日志查看

```bash
# 实时查看日志
tail -f logs/wistrade.log

# 查看错误
grep ERROR logs/wistrade.log

# 查看最近100行
tail -100 logs/wistrade.log
```

---

## 📞 获取帮助

### 在线资源
- **GitHub Issues**: https://github.com/MrZhanZhimin/WisTrade/issues
- **项目文档**: 查看 `docs/` 目录
- **完整手册**: `docs/USER_MANUAL.md`

### 报告问题
在GitHub Issues中提供：
1. 错误信息（完整堆栈跟踪）
2. 操作步骤
3. 系统信息（OS、Python版本）
4. 日志片段

---

## ⚠️ 重要提示

### 风险声明
**本工具仅供教育和研究使用，不构成投资建议。**

- 股票交易存在重大风险
- 过往业绩不代表未来表现
- 请充分了解风险后使用
- 建议从小额资金开始测试

### 合规要求
- 确保遵守当地证券法规
- 需要开通券商API权限
- 保留交易记录5年以上
- 如有疑问咨询专业顾问

---

## 🎯 快速测试流程

```bash
# 1. 升级Python到3.11+（如果需要）
brew install python@3.11

# 2. 创建虚拟环境
python3.11 -m venv venv311
source venv311/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑.env，填入ZHIPUAI_API_KEY和DB_ENCRYPTION_KEY

# 5. 启动应用
python -m wistrade.main

# 6. 验证功能
# - 查看仪表盘数据
# - 测试AI对话
# - 查看设置页面
```

---

**祝您使用愉快！如有问题请查看日志或提交Issue。**

*WisTrade Team © 2024*
