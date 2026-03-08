#!/bin/bash

# WisTrade 快速启动脚本 (Linux/macOS)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                 WisTrade 启动脚本                          ║"
echo "║            AI-Powered Stock Trading Tool                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source venv/bin/activate

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo -e "${RED}✗ Python版本过低: $PYTHON_VERSION (需要 >= 3.11)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"

# 检查依赖
echo -e "${BLUE}检查依赖...${NC}"
if ! python -c "import PyQt6" 2>/dev/null; then
    echo -e "${YELLOW}检测到缺失依赖，正在安装...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ 依赖已安装${NC}"
else
    echo -e "${GREEN}✓ 依赖完整${NC}"
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}未找到.env文件，从模板创建...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env已创建${NC}"
    echo -e "${YELLOW}⚠ 请编辑.env文件，填入您的API密钥${NC}"
    echo -e "${YELLOW}  - ZHIPUAI_API_KEY (必需)"
    echo -e "${YELLOW}  - DB_ENCRYPTION_KEY (必需)"
    echo -e "${YELLOW}  - TUSHARE_TOKEN (可选)${NC}"
    read -p "按Enter键继续..."
fi

# 创建必要目录
mkdir -p logs data config

# 启动应用
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              正在启动 WisTrade...                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

python -m wistrade.main

# 退出状态
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ WisTrade已正常退出${NC}"
else
    echo -e "${RED}✗ WisTrade异常退出 (退出码: $exit_code)${NC}"
fi

exit $exit_code
