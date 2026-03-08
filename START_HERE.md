# WisTrade 启动说明

## 当前状态

✅ **项目已完成开发**  
⚠️ **需要Python 3.11+环境才能运行**

---

## 快速开始

### 1️⃣ 检查Python版本

```bash
python3 --version
```

**如果版本 < 3.8**，请先升级Python：

**macOS**:
```bash
brew install python@3.11
```

**Windows**: 从 https://www.python.org/downloads/ 下载

**Linux**:
```bash
sudo apt install python3.11  # Ubuntu/Debian
```

---

### 2️⃣ 创建虚拟环境

```bash
# 使用Python 3.11+
python3.11 -m venv venv311

# 激活
source venv311/bin/activate  # macOS/Linux
# 或
venv311\Scripts\activate  # Windows
```

---

### 3️⃣ 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4️⃣ 配置环境

```bash
cp .env.example .env
```

**编辑 `.env`**，填入必需信息：

```bash
# 必需：AI密钥
ZHIPUAI_API_KEY=your_key_here

# 必需：数据库密码（设置一个强密码）
DB_ENCRYPTION_KEY=your_strong_password_here

# 必需：安全密钥（运行命令生成）
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**获取AI密钥**: https://open.bigmodel.cn/ （新用户送免费额度）

---

### 5️⃣ 启动应用

```bash
python -m wistrade.main
```

或使用脚本：

```bash
./start.sh  # macOS/Linux
start.bat   # Windows
```

---

## 文档说明

- **`OPERATION_GUIDE.md`** - 详细操作手册（功能说明、配置、故障排查）
- **`docs/USER_MANUAL.md`** - 完整用户手册
- **`PROJECT_COMPLETION_REPORT.md`** - 项目完成报告
- **`README.md`** - 项目介绍

---

## 遇到问题？

1. **查看日志**: `tail -f logs/wistrade.log`
2. **检查配置**: 确保 `.env` 文件已正确配置
3. **提交Issue**: https://github.com/MrZhanZhimin/WisTrade/issues

---

**当前系统**: macOS, Python 3.7.4  
**建议**: 升级到Python 3.11+以获得最佳体验

---

*WisTrade v0.1.0 - AI智能交易平台*
